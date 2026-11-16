import os
import sys
import io
import json
import time
import base64
import hashlib
import random
import asyncio
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, urlparse, parse_qs

import pymysql
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image
import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from cloud_backend.db_v2.bridge_sync import sync_v1_delta_to_v2, make_sha256, parse_dt_safe

# =====================================================================
# 1. 환경 설정 (정규화 DB lab225_v2 메인 + 물리 스캐너 lab225 브릿지 호환)
# =====================================================================
DB_HOST = os.getenv("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
DB_FALLBACK_HOST = "15.165.68.30"
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))
DB_USER = os.getenv("MYSQL_USER", "admin")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "12345678")
DB_NAME = os.getenv("MYSQL_V2_DATABASE", "lab225_v2")
DB_V1_NAME = os.getenv("MYSQL_DATABASE", "lab225")

MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

STREAMLIT_CONSUMER_URL = "https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/"

STEP1_IMG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "1_PC_QR_Generators"))
PORTAL_QR_OUT_DIR = os.path.join(BASE_DIR, "generated_qr")
os.makedirs(PORTAL_QR_OUT_DIR, exist_ok=True)

KST = timezone(timedelta(hours=9))


def get_kst_now():
    return datetime.now(KST)


def get_db_connection(db_name: str = None):
    target_db = db_name or DB_NAME
    try:
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=target_db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=8,
            autocommit=True,
        )
    except Exception:
        return pymysql.connect(
            host=DB_FALLBACK_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=target_db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=8,
            autocommit=True,
        )


TRUCK_OPTIONS = {
    "truck01": {"name": "1호차 (truck01 / carrier-c6-01)", "topic": "coldchain/truck01/sensor", "device_id": "carrier-c6-01"},
    "truck02": {"name": "2호차 (truck02 / carrier-c6-02)", "topic": "coldchain/truck02/sensor", "device_id": "carrier-c6-02"},
    "truck03": {"name": "3호차 (truck03 / carrier-c6-03)", "topic": "coldchain/truck03/sensor", "device_id": "carrier-c6-03"},
    "truck04": {"name": "4호차 (truck04 / carrier-c6-04)", "topic": "coldchain/truck04/sensor", "device_id": "carrier-c6-04"},
}

FRUIT_IMAGES_FARM = {
    "Apples": "apple.png",
    "Pears": "pear.png",
    "Peaches": "peach.png",
    "Tangerines": "tangerine.png",
    "Melons": "koreanmelon.png",
}

FRUIT_IMAGES_GRADE = {
    "Apples": ["apple4.png", "apple3.png", "apple2.png"],
    "Pears": ["pear4.png", "pear3.png", "pear2.png"],
    "Peaches": ["peach4.png", "peach3.png", "peach2.png"],
    "Tangerines": ["tangerine4.png", "tangerine3.png", "tangerine2.png"],
    "Melons": ["koreanmelon4.png", "koreanmelon3.png", "koreanmelon2.png"],
}

ROLE_PINS = {
    "0000": {"role": "admin", "name": "통합 관리자 (마스터)", "tabs": ["consumer", "farm", "apc", "control"]},
    "1111": {"role": "farm", "name": "농가 출하 담당자", "tabs": ["consumer", "farm"]},
    "2222": {"role": "apc", "name": "APC 선별 작업자", "tabs": ["consumer", "apc"]},
    "3333": {"role": "control", "name": "콜드체인 관제사", "tabs": ["consumer", "control"]},
}

# =====================================================================
# 2. FastAPI 앱 및 실시간 MQTT ➔ WebSocket 브로드캐스터
# =====================================================================
app = FastAPI(title="ColdChain DigitalTwin Unified Portal v2 (Normalized DB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ws_clients = set()
latest_packets = {}
main_event_loop = None


def broadcast_mqtt_packet(payload: dict):
    if main_event_loop is None or not ws_clients:
        return
    msg_str = json.dumps({"type": "telemetry", "data": payload}, ensure_ascii=False)
    for ws in list(ws_clients):
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(msg_str), main_event_loop)
        except Exception:
            ws_clients.discard(ws)


def on_mqtt_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        for tinfo in TRUCK_OPTIONS.values():
            client.subscribe(tinfo["topic"])
        print("[FastAPI MQTT] Connected & Subscribed to all vehicle topics", flush=True)


def on_mqtt_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        payload["topic"] = msg.topic
        ts_val = payload.get("timestamp_str", "")
        if ts_val and ts_val != "00:00:00" and not str(ts_val).startswith("00:00"):
            payload["timestamp"] = str(ts_val)
        else:
            payload["timestamp"] = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")

        for k in ["temperature", "humidity", "lux", "g_force", "speed", "lat", "lng"]:
            if k in payload:
                try:
                    payload[k] = float(payload[k])
                except Exception:
                    pass
        dev = payload.get("device", "carrier-c6-01")
        latest_packets[dev] = payload
        broadcast_mqtt_packet(payload)
    except Exception as e:
        print(f"[FastAPI MQTT Error] {e}", flush=True)


def start_background_mqtt():
    try:
        try:
            from paho.mqtt.client import CallbackAPIVersion
            client = mqtt.Client(CallbackAPIVersion.VERSION1)
        except Exception:
            client = mqtt.Client()
        client.on_connect = on_mqtt_connect
        client.on_message = on_mqtt_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        return client
    except Exception as e:
        print(f"[FastAPI MQTT Init Warning] {e}", flush=True)
        return None


@app.on_event("startup")
async def startup_event():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()
    start_background_mqtt()


# =====================================================================
# 3. 헬퍼 함수 (QR 이미지 Base64 생성 & 운송 궤적 JOIN 로더)
# =====================================================================
def make_qr_base64(qr_url: str, overlay_filename: str = None, rounded: bool = True, save_filename: str = None) -> str:
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    if rounded:
        qr_img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer()).convert("RGBA")
    else:
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    if overlay_filename:
        overlay_path = os.path.join(STEP1_IMG_DIR, overlay_filename)
        if os.path.exists(overlay_path):
            try:
                logo_size = int(qr_img.size[0] * 0.25)
                logo = Image.open(overlay_path).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
                pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
                qr_img.paste(logo, pos, mask=logo)
            except Exception as e:
                print(f"[QR Overlay Warning] {e}")

    if save_filename:
        try:
            os.makedirs(PORTAL_QR_OUT_DIR, exist_ok=True)
            qr_img.save(os.path.join(PORTAL_QR_OUT_DIR, save_filename), format="PNG")
            if os.path.exists(STEP1_IMG_DIR):
                qr_img.save(os.path.join(STEP1_IMG_DIR, save_filename), format="PNG")
        except Exception as e:
            print(f"[QR File Save Warning] {e}")

    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def fetch_shipment_pts(cur, sh_row: dict):
    """`shipments` 레코드와 `sensor_telemetry`를 run_id + 시간 윈도우로 정밀 JOIN"""
    if not sh_row or not sh_row.get("departed_at"):
        return []
    dep_dt = sh_row["departed_at"]
    arr_dt = sh_row.get("arrived_at")
    run_id = sh_row.get("run_id")
    dev_id = sh_row.get("device_id")

    s_str = dep_dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dep_dt, "strftime") else str(dep_dt)[:19]
    e_dt = arr_dt if arr_dt else ((parse_dt_safe(dep_dt) or datetime.now()) + timedelta(hours=12))
    e_str = e_dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(e_dt, "strftime") else str(e_dt)[:19]

    select_cols = """
        DATE_FORMAT(st.measured_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS timestamp_str,
        st.temperature, st.humidity, st.lux, st.g_force, st.speed,
        st.lat, st.lng, st.raw_status AS status, st.device_id AS device, st.run_id
    """
    if run_id:
        cur.execute(
            f"""
            SELECT {select_cols}
            FROM `{DB_NAME}`.`sensor_telemetry` st
            WHERE st.run_id = %s
              AND st.gps_state != 'INDOOR' AND st.lat != 0 AND st.lng != 0
              AND st.measured_at >= %s AND st.measured_at <= %s
            ORDER BY st.measured_at ASC, st.telemetry_id ASC
            """,
            (run_id, s_str, e_str),
        )
        rows = list(cur.fetchall())
        if rows:
            return rows

    if dev_id:
        cur.execute(
            f"""
            SELECT {select_cols}
            FROM `{DB_NAME}`.`sensor_telemetry` st
            WHERE st.device_id = %s
              AND st.gps_state != 'INDOOR' AND st.lat != 0 AND st.lng != 0
              AND st.measured_at >= %s AND st.measured_at <= %s
            ORDER BY st.measured_at ASC, st.telemetry_id ASC
            """,
            (dev_id, s_str, e_str),
        )
        rows = list(cur.fetchall())
        if rows:
            return rows

    cur.execute(
        f"""
        SELECT {select_cols}
        FROM `{DB_NAME}`.`sensor_telemetry` st
        JOIN `{DB_NAME}`.`transport_runs` tr ON st.run_id = tr.run_id
        WHERE tr.run_type = 'FIELD_DRIVE'
          AND st.gps_state != 'INDOOR' AND st.lat != 0 AND st.lng != 0
          AND st.measured_at >= %s AND st.measured_at <= %s
        ORDER BY st.measured_at ASC, st.telemetry_id ASC
        """,
        (s_str, e_str),
    )
    return list(cur.fetchall())


# =====================================================================
# 4. REST API 엔드포인트 (lab225_v2 정규화 JOIN 기반)
# =====================================================================
class LoginRequest(BaseModel):
    pin: str


@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    pin = req.pin.strip()
    if pin in ROLE_PINS:
        return {"ok": True, **ROLE_PINS[pin]}
    raise HTTPException(status_code=401, detail="유효하지 않은 권한 PIN 번호입니다. (관리자: 0000, 농가: 1111, APC: 2222, 관제: 3333)")


@app.get("/api/consumer/fmid-list")
def api_get_fmid_list(include_test: bool = False):
    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        with conn.cursor() as cur:
            where_sql = "" if include_test else "WHERE hl.is_test = 0"
            cur.execute(
                f"""
                SELECT hl.lot_id AS FmID,
                       hl.fruit_type AS FrT,
                       hl.variety AS Vt,
                       COALESCE(MAX(sl.current_stage), hl.current_stage) AS latest_step,
                       MAX(se.event_id) AS max_id
                FROM `{DB_NAME}`.`harvest_lots` hl
                LEFT JOIN `{DB_NAME}`.`sorted_lots` sl
                  ON hl.lot_id = sl.lot_id AND sl.grade_code = 'A'
                LEFT JOIN `{DB_NAME}`.`stage_events` se
                  ON hl.lot_id = se.lot_id
                {where_sql}
                GROUP BY hl.lot_id, hl.fruit_type, hl.variety, hl.current_stage
                ORDER BY max_id DESC
                LIMIT 30
                """
            )
            return {"ok": True, "items": list(cur.fetchall())}
    finally:
        conn.close()


@app.get("/api/consumer/trace/{fmid}")
def api_get_consumer_trace(fmid: str, grade: str = "상"):
    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{DB_NAME}`.`harvest_lots` WHERE lot_id = %s LIMIT 1", (fmid,))
            lot = cur.fetchone()
            if not lot:
                raise HTTPException(status_code=404, detail=f"FmID={fmid} 이력 데이터가 존재하지 않습니다.")

            # 등급 판별 및 sorted_lots(방법 A) JOIN
            g_upper = str(grade or "상").strip().upper()
            if g_upper in ("중", "M", "B"):
                g_idx, g_param, g_code = 1, "중", "B"
            elif g_upper in ("하", "L", "C"):
                g_idx, g_param, g_code = 2, "하", "C"
            else:
                g_idx, g_param, g_code = 0, "상", "A"

            cur.execute(f"SELECT * FROM `{DB_NAME}`.`sorted_lots` WHERE lot_id = %s", (fmid,))
            sorted_map = {r["grade_code"]: r for r in cur.fetchall()}

            effective_pkg = f"{fmid}-{g_code}"

            # 10단계 타임라인(A00·A01·A02 + A10~A16) 조회
            cur.execute(
                f"""
                SELECT stage_code, pkg_id, event_at, lat, lng, temp, humi, tx_hash
                FROM `{DB_NAME}`.`stage_events`
                WHERE lot_id = %s AND (pkg_id IS NULL OR pkg_id = %s)
                ORDER BY event_at ASC, event_id ASC
                """,
                (fmid, effective_pkg),
            )
            ev_rows = cur.fetchall()

            a_qty = sorted_map.get("A", {}).get("grade_qty")
            b_qty = sorted_map.get("B", {}).get("grade_qty")
            c_qty = sorted_map.get("C", {}).get("grade_qty")
            def_qty = sorted_map.get("DEFECT", {}).get("grade_qty")

            merged = {
                "FmID": lot["lot_id"],
                "AC": lot["origin_zip"],
                "FrT": lot["fruit_type"],
                "Vt": lot["variety"],
                "Ct": lot["farmer_phone"],
                "Mt": lot["cultivation"],
                "HN": lot["harvest_no"],
                "Qt": lot["total_qty"],
                "HD": str(lot["harvest_date"] or ""),
                "StD": str(lot["storage_date"] or ""),
                "DD": str(lot["deliver_date"] or ""),
                "AGrade": a_qty,
                "BGrade": b_qty,
                "CGrade": c_qty,
                "DefectRate": def_qty,
            }

            stage_lookup = {}
            clean_records = []
            legacy_time_key = {
                "A00": "HD",
                "A01": "Farm_StD",
                "A02": "Farm_DD",
                "A10": "APC_AD",
                "A11": "APC_WD",
                "A12": "APC_RT",
                "A13": "APC_PT",
                "A14": "APC_StD",
                "A15": "APC_OP",
                "A16": "Retail_AD",
            }
            for ev in ev_rows:
                code = ev["stage_code"]
                ev_str = ev["event_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(ev["event_at"], "strftime") else str(ev["event_at"])
                item = {
                    "Lo": code,
                    "FmID": lot["lot_id"],
                    "event_at": ev_str,
                    "Lat": ev["lat"],
                    "lon": ev["lng"],
                    "Tp": ev["temp"],
                    "Hm": ev["humi"],
                    "tx_hash": ev["tx_hash"],
                    "AGrade": a_qty,
                    "BGrade": b_qty,
                    "CGrade": c_qty,
                    "DefectRate": def_qty,
                }
                t_key = legacy_time_key.get(code)
                if t_key:
                    item[t_key] = ev_str
                    merged[t_key] = ev_str
                if ev["tp_ok"] if "tp_ok" in ev else (ev["temp"] is not None):
                    merged["Tp"] = ev["temp"]
                    merged["Hm"] = ev["humi"]
                stage_lookup[code] = item
                clean_records.append(item)

            # 1구간(leg_no=1) 및 2구간(leg_no=2) 운송 궤적 JOIN
            cur.execute(
                f"SELECT * FROM `{DB_NAME}`.`shipments` WHERE lot_id = %s AND leg_no = 1 LIMIT 1",
                (fmid,),
            )
            sh_leg1 = cur.fetchone()
            leg1_pts = fetch_shipment_pts(cur, sh_leg1) if (sh_leg1 and (sh_leg1.get("status") == "ARRIVED" or sh_leg1.get("run_id"))) else []

            cur.execute(
                f"SELECT * FROM `{DB_NAME}`.`shipments` WHERE lot_id = %s AND leg_no = 2 AND pkg_id = %s LIMIT 1",
                (fmid, effective_pkg),
            )
            sh_leg2 = cur.fetchone()
            leg2_pts = fetch_shipment_pts(cur, sh_leg2) if sh_leg2 else []

            fruit_raw = str(lot["fruit_type"] or "Apples")
            cat_key = "Apples"
            for k in FRUIT_IMAGES_GRADE.keys():
                if k.lower() in fruit_raw.lower():
                    cat_key = k
                    break

            auth_qr_url = f"{STREAMLIT_CONSUMER_URL}/?FmID={fmid}&grade={g_param}&AC={lot['origin_zip']}&FrT={fruit_raw}"
            overlay_icon = FRUIT_IMAGES_GRADE[cat_key][g_idx]
            auth_qr_b64 = make_qr_base64(auth_qr_url, overlay_filename=overlay_icon, rounded=False)

            return {
                "ok": True,
                "fmid": fmid,
                "grade": g_param,
                "summary": merged,
                "records": clean_records,
                "stage_lookup": stage_lookup,
                "auth_qr_base64": auth_qr_b64,
                "leg1_sensor_pts": leg1_pts,
                "leg2_sensor_pts": leg2_pts,
            }
    finally:
        conn.close()


class FarmQRRequest(BaseModel):
    AC: str = "55632"
    FmID: str
    Ct: str = "01012345678"
    FrT: str = "Apples"
    Vt: str = "Fuji Apple"
    HD_date: str
    StD_date: str
    DD_date: str
    Mt: str = "Organic"
    HN: str = "1"
    Qt: str = "50"
    target_mode: str = "streamlit"
    portal_base_url: str = ""


@app.post("/api/farm/create-qr")
def api_create_farm_qr(req: FarmQRRequest):
    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        lot_id = req.FmID.strip()
        with conn.cursor() as cur:
            cur.execute("SET time_zone = '+09:00'")
            cur.execute("SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') as srv_dt, DATE_FORMAT(NOW(), '%H:%i:%s') as srv_time")
            srv_info = cur.fetchone()
            srv_now_dt = datetime.strptime(srv_info["srv_dt"], "%Y-%m-%d %H:%M:%S")
            hd_full = f"{req.HD_date} {srv_info['srv_time']}"
            dt_a00 = datetime.strptime(hd_full, "%Y-%m-%d %H:%M:%S")
            if dt_a00 > srv_now_dt:
                dt_a00 = srv_now_dt - timedelta(seconds=2)
                hd_full = dt_a00.strftime("%Y-%m-%d %H:%M:%S")

            std_d = datetime.strptime(req.StD_date[:10], "%Y-%m-%d").date()
            dt_a01 = datetime(std_d.year, std_d.month, std_d.day, 9, 0, 0) if std_d > dt_a00.date() else (dt_a00 + timedelta(seconds=1))
            dt_a02 = max(srv_now_dt, dt_a01 + timedelta(seconds=1))

            # 1) 물리 ESP32 스캐너 호환용 v1 기록
            cur.execute(
                f"""
                INSERT INTO `{DB_V1_NAME}`.`qr` (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ("A00", req.AC, lot_id, req.FrT, req.Vt, req.Ct, hd_full, req.DD_date, req.Qt, req.Mt, req.HN, req.StD_date, None),
            )
            v1_id = cur.lastrowid

            # 2) v2 정규화 테이블(harvest_lots + stage_events A00·A01·A02 + shipments leg=1 오픈) 기록
            cur.execute(
                f"""
                INSERT INTO `{DB_NAME}`.`harvest_lots`
                (lot_id, origin_zip, fruit_type, variety, farmer_phone, cultivation,
                 harvest_no, total_qty, harvest_date, storage_date, deliver_date,
                 ag_practice, current_stage, is_test, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, 'A02', 0, %s)
                ON DUPLICATE KEY UPDATE
                    origin_zip=VALUES(origin_zip), fruit_type=VALUES(fruit_type), variety=VALUES(variety),
                    farmer_phone=VALUES(farmer_phone), cultivation=VALUES(cultivation), harvest_no=VALUES(harvest_no),
                    total_qty=VALUES(total_qty), harvest_date=VALUES(harvest_date), storage_date=VALUES(storage_date),
                    deliver_date=VALUES(deliver_date), current_stage='A02', is_test=0
                """,
                (lot_id, req.AC, req.FrT, req.Vt, req.Ct, req.Mt, int(req.HN), int(req.Qt), req.HD_date[:10], req.StD_date[:10], req.DD_date[:10], hd_full),
            )

            params = {
                "AC": req.AC, "FmID": lot_id, "Ct": req.Ct, "FrT": req.FrT,
                "Vt": req.Vt, "HD": hd_full, "DD": req.DD_date, "StD": req.StD_date,
                "Mt": req.Mt, "HN": req.HN, "Qt": req.Qt,
            }
            integrity_hash = make_sha256(params)

            for s_cd, s_dt, s_h in [("A00", dt_a00, integrity_hash), ("A01", dt_a01, None), ("A02", dt_a02, None)]:
                cur.execute(
                    f"""
                    INSERT INTO `{DB_NAME}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, tx_hash)
                    VALUES (%s, NULL, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE event_at=VALUES(event_at), tx_hash=COALESCE(VALUES(tx_hash), tx_hash)
                    """,
                    (lot_id, s_cd, s_dt.strftime("%Y-%m-%d %H:%M:%S"), s_h),
                )

            cur.execute(
                f"""
                INSERT INTO `{DB_NAME}`.`shipments` (leg_no, lot_id, pkg_id, departed_at, status)
                VALUES (1, %s, NULL, %s, 'IN_TRANSIT')
                ON DUPLICATE KEY UPDATE departed_at=VALUES(departed_at), status='IN_TRANSIT'
                """,
                (lot_id, dt_a02.strftime("%Y-%m-%d %H:%M:%S")),
            )

            if v1_id:
                cur.execute(
                    f"""
                    INSERT INTO `{DB_NAME}`.`_sync_watermark` (source_table, last_id)
                    VALUES ('qr', %s) ON DUPLICATE KEY UPDATE last_id=GREATEST(last_id, VALUES(last_id))
                    """,
                    (v1_id,),
                )

        query_string = urlencode(params)
        if req.target_mode == "fastapi" and req.portal_base_url:
            base = req.portal_base_url.rstrip("/")
            qr_url = f"{base}/?{query_string}"
        else:
            qr_url = f"{STREAMLIT_CONSUMER_URL}/?{query_string}"

        yymmdd = req.HD_date.replace("-", "")[2:8]
        farm_qr_filename = f"{req.AC}{lot_id}{yymmdd}_QR.png"
        overlay_icon = FRUIT_IMAGES_FARM.get(req.FrT, "apple.png")
        qr_b64 = make_qr_base64(qr_url, overlay_filename=overlay_icon, rounded=True, save_filename=farm_qr_filename)

        return {
            "ok": True,
            "fmid": lot_id,
            "hd_full": hd_full,
            "hash": integrity_hash,
            "qr_url": qr_url,
            "qr_base64": qr_b64,
            "saved_filename": farm_qr_filename,
            "saved_paths": [
                os.path.join(STEP1_IMG_DIR, farm_qr_filename),
                os.path.join(PORTAL_QR_OUT_DIR, farm_qr_filename),
            ],
        }
    finally:
        conn.close()


class ApcScanRequest(BaseModel):
    qr_data: str


@app.post("/api/apc/scan-qr")
def api_apc_scan_qr(req: ApcScanRequest):
    raw = req.qr_data.strip()
    fm_id = None
    if "?" in raw or raw.startswith("http"):
        parsed_url = urlparse(raw)
        q_params = parse_qs(parsed_url.query)
        fm_id = (q_params.get("FmID") or q_params.get("fmid") or [None])[0]
        if not fm_id:
            fm_id = parsed_url.path.rstrip("/").split("/")[-1]
    else:
        fm_id = raw

    if not fm_id:
        raise HTTPException(status_code=400, detail="QR에서 FmID를 찾을 수 없음")

    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT hl.lot_id AS FmID,
                       hl.origin_zip AS AC,
                       hl.farmer_phone AS Ct,
                       hl.fruit_type AS FrT,
                       hl.variety AS Vt,
                       hl.cultivation AS Mt,
                       hl.harvest_no AS HN,
                       hl.total_qty AS Qt,
                       hl.current_stage,
                       COALESCE(
                           DATE_FORMAT(se_a00.event_at, '%%Y-%%m-%%d %%H:%%i:%%s'),
                           DATE_FORMAT(hl.harvest_date, '%%Y-%%m-%%d')
                       ) AS HD,
                       DATE_FORMAT(hl.deliver_date, '%%Y-%%m-%%d') AS DD,
                       DATE_FORMAT(hl.storage_date, '%%Y-%%m-%%d') AS StD,
                       DATE_FORMAT(se.event_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS APC_WD
                FROM `{DB_NAME}`.`harvest_lots` hl
                JOIN `{DB_NAME}`.`stage_events` se
                  ON hl.lot_id = se.lot_id AND se.stage_code = 'A11'
                LEFT JOIN `{DB_NAME}`.`stage_events` se_a00
                  ON hl.lot_id = se_a00.lot_id AND se_a00.stage_code = 'A00'
                WHERE hl.lot_id = %s
                LIMIT 1
                """,
                (fm_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"DB에서 A11(세척 완료) 데이터를 찾을 수 없음 (FmID={fm_id}: A10 입고 및 A11 세척 단계가 먼저 완료되어야 QR 생성이 가능합니다)",
                )

            cur.execute(f"SELECT grade_code, grade_qty FROM `{DB_NAME}`.`sorted_lots` WHERE lot_id = %s", (fm_id,))
            existing_sorted = {r["grade_code"]: int(r["grade_qty"] or 0) for r in cur.fetchall()}

            total_qt = int(row.get("Qt") or 0)
            already_sorted = len(existing_sorted) > 0
            if already_sorted:
                a_val = existing_sorted.get("A", 0)
                b_val = existing_sorted.get("B", 0)
                c_val = existing_sorted.get("C", 0)
                defect_val = existing_sorted.get("DEFECT", 0)
            elif total_qt > 0:
                defect_val = random.randint(1, min(3, total_qt))
                rem_after_defect = total_qt - defect_val
                a_val = int(total_qt * random.uniform(0.78, 0.82))
                if a_val > rem_after_defect:
                    a_val = rem_after_defect
                rem_for_bc = rem_after_defect - a_val
                if rem_for_bc > 0:
                    b_val = random.randint(0, rem_for_bc)
                    c_val = rem_for_bc - b_val
                else:
                    b_val, c_val = 0, 0
                a_val = total_qt - (b_val + c_val + defect_val)
            else:
                a_val, b_val, c_val, defect_val = 0, 0, 0, 0

            qrs_preview = []
            if already_sorted:
                fruit = str(row.get("FrT") or "Apples")
                ac = str(row.get("AC") or "")
                grade_icons = FRUIT_IMAGES_GRADE.get(fruit, FRUIT_IMAGES_GRADE["Apples"])
                for idx, (g_kr, g_en, cnt) in enumerate([("상", "A", a_val), ("중", "B", b_val), ("하", "C", c_val)]):
                    q_url = f"{STREAMLIT_CONSUMER_URL}/?FmID={fm_id}&grade={g_kr}&pkg_grade={g_en}&AC={ac}&FrT={fruit}"
                    q_b64 = make_qr_base64(q_url, overlay_filename=grade_icons[idx], rounded=False)
                    qrs_preview.append({
                        "grade_en": g_en,
                        "grade_kr": g_kr,
                        "count": str(cnt),
                        "qr_url": q_url,
                        "qr_base64": q_b64,
                        "filename": f"{fm_id}_{g_en}_QR.png",
                    })

            return {
                "ok": True,
                "fmid": str(fm_id),
                "already_sorted": already_sorted,
                "row": row,
                "qrs": qrs_preview,
                "auto_grades": {
                    "AGrade": a_val,
                    "BGrade": b_val,
                    "CGrade": c_val,
                    "DefectRate": defect_val,
                    "TotalQt": total_qt,
                },
            }
    finally:
        conn.close()


@app.get("/api/apc/candidates")
def api_apc_candidates():
    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT hl.lot_id AS FmID, hl.origin_zip AS AC, hl.fruit_type AS FrT, hl.variety AS Vt,
                       hl.total_qty AS Qt,
                       DATE_FORMAT(se.event_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS APC_WD
                FROM `{DB_NAME}`.`harvest_lots` hl
                JOIN `{DB_NAME}`.`stage_events` se
                  ON hl.lot_id = se.lot_id AND se.stage_code = 'A11'
                WHERE hl.current_stage = 'A11'
                ORDER BY se.event_at DESC
                LIMIT 20
                """
            )
            return {"ok": True, "items": list(cur.fetchall())}
    finally:
        conn.close()


class ApcSortingRequest(BaseModel):
    FmID: str
    AGrade: str
    BGrade: str
    CGrade: str
    DefectRate: str
    target_mode: str = "streamlit"
    portal_base_url: str = ""


@app.post("/api/apc/create-sorting-qr")
def api_create_apc_sorting_qr(req: ApcSortingRequest):
    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        lot_id = req.FmID.strip()
        with conn.cursor() as cur:
            cur.execute("SET time_zone = '+09:00'")
            cur.execute("SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') as srv_now")
            srv_now = cur.fetchone()["srv_now"]

            cur.execute(
                f"""
                SELECT hl.*, se.lat AS a11_lat, se.lng AS a11_lng
                FROM `{DB_NAME}`.`harvest_lots` hl
                JOIN `{DB_NAME}`.`stage_events` se
                  ON hl.lot_id = se.lot_id AND se.stage_code = 'A11'
                WHERE hl.lot_id = %s
                LIMIT 1
                """,
                (lot_id,),
            )
            lot_row = cur.fetchone()
            if not lot_row:
                raise HTTPException(
                    status_code=400,
                    detail=f"DB에서 A11(세척 완료) 데이터를 찾을 수 없습니다 (FmID={lot_id}). 이전 단계(A10 입고·A11 세척)가 먼저 완료되어야 유색 QR 생성이 가능합니다.",
                )

            a_cnt = int(req.AGrade or 0)
            b_cnt = int(req.BGrade or 0)
            c_cnt = int(req.CGrade or 0)
            def_cnt = int(req.DefectRate or 0)

            # 1) 방법 A 정규화 적재: sorted_lots 4행 (A, B, C, DEFECT) + stage_events(A12)
            for p_id, g_cd, g_ko, g_q, ship, p_st in [
                (f"{lot_id}-A", "A", "상", a_cnt, 1, "A12"),
                (f"{lot_id}-B", "B", "중", b_cnt, 1, "A12"),
                (f"{lot_id}-C", "C", "하", c_cnt, 1, "A12"),
                (f"{lot_id}-DEF", "DEFECT", "결점과", def_cnt, 0, "REJECTED"),
            ]:
                cur.execute(
                    f"""
                    INSERT INTO `{DB_NAME}`.`sorted_lots`
                    (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE grade_qty=VALUES(grade_qty), sorted_at=VALUES(sorted_at)
                    """,
                    (p_id, lot_id, g_cd, g_ko, g_q, ship, p_st, srv_now),
                )

            integrity_hash = make_sha256(
                {"lot_id": lot_id, "stage": "A12", "A": a_cnt, "B": b_cnt, "C": c_cnt, "DEFECT": def_cnt, "rt": srv_now}
            )
            cur.execute(
                f"""
                INSERT INTO `{DB_NAME}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
                VALUES (%s, NULL, 'A12', %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at=VALUES(event_at), tx_hash=VALUES(tx_hash)
                """,
                (lot_id, srv_now, lot_row.get("a11_lat"), lot_row.get("a11_lng"), integrity_hash),
            )
            cur.execute(f"UPDATE `{DB_NAME}`.`harvest_lots` SET current_stage='A12' WHERE lot_id=%s", (lot_id,))

            # 2) 물리 ESP32 스캐너 호환을 위한 lab225.qr A12 기록 및 워터마크 갱신
            cur.execute(f"SELECT * FROM `{DB_V1_NAME}`.`qr` WHERE FmID=%s AND Lo='A11' ORDER BY id DESC LIMIT 1", (lot_id,))
            prev_v1 = cur.fetchone()
            if prev_v1:
                data_dict = dict(prev_v1)
                data_dict.update({
                    "Lo": "A12",
                    "AGrade": str(a_cnt),
                    "BGrade": str(b_cnt),
                    "CGrade": str(c_cnt),
                    "DefectRate": str(def_cnt),
                    "APC_RT": srv_now,
                })
                cur.execute(f"SHOW COLUMNS FROM `{DB_V1_NAME}`.`qr`")
                db_cols = {c["Field"] for c in cur.fetchall()}
                data_to_insert = {k: v for k, v in data_dict.items() if k in db_cols and k != "id"}
                cols_sql = ", ".join(data_to_insert.keys())
                placeholders_sql = ", ".join([f"%({k})s" for k in data_to_insert.keys()])
                cur.execute(f"INSERT INTO `{DB_V1_NAME}`.`qr` ({cols_sql}) VALUES ({placeholders_sql})", data_to_insert)
                v1_id = cur.lastrowid
                if v1_id:
                    cur.execute(
                        f"""
                        INSERT INTO `{DB_NAME}`.`_sync_watermark` (source_table, last_id)
                        VALUES ('qr', %s) ON DUPLICATE KEY UPDATE last_id=GREATEST(last_id, VALUES(last_id))
                        """,
                        (v1_id,),
                    )

        fruit = str(lot_row.get("fruit_type") or "Apples")
        ac = str(lot_row.get("origin_zip") or "")
        grade_icons = FRUIT_IMAGES_GRADE.get(fruit, FRUIT_IMAGES_GRADE["Apples"])

        base_url = (
            req.portal_base_url.rstrip("/")
            if (req.target_mode == "fastapi" and req.portal_base_url)
            else STREAMLIT_CONSUMER_URL
        )

        qrs = []
        saved_files = []
        for idx, (g_kr, g_en, cnt) in enumerate([
            ("상", "A", req.AGrade),
            ("중", "B", req.BGrade),
            ("하", "C", req.CGrade),
        ]):
            q_url = f"{base_url}/?FmID={lot_id}&grade={g_kr}&pkg_grade={g_en}&AC={ac}&FrT={fruit}"
            qr_filename = f"{lot_id}_{g_en}_QR.png"
            q_b64 = make_qr_base64(q_url, overlay_filename=grade_icons[idx], rounded=False, save_filename=qr_filename)
            saved_files.append(qr_filename)
            qrs.append({
                "grade_en": g_en,
                "grade_kr": g_kr,
                "count": cnt,
                "qr_url": q_url,
                "qr_base64": q_b64,
                "filename": qr_filename,
            })

        return {
            "ok": True,
            "fmid": lot_id,
            "apc_rt": srv_now,
            "hash": integrity_hash,
            "qrs": qrs,
            "saved_dir_step1": STEP1_IMG_DIR,
            "saved_dir_portal": PORTAL_QR_OUT_DIR,
            "saved_files": saved_files,
        }
    finally:
        conn.close()


@app.get("/api/control/sessions")
def api_control_sessions(truck_id: str = "truck02", include_lab: bool = False):
    truck = TRUCK_OPTIONS.get(truck_id, TRUCK_OPTIONS["truck02"])
    dev = truck["device_id"]
    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        with conn.cursor() as cur:
            type_filter = "tr.run_type IN ('FIELD_DRIVE', 'BENCH', 'MOCK')" if include_lab else "tr.run_type = 'FIELD_DRIVE'"
            cur.execute(
                f"""
                SELECT tr.run_id, tr.run_type, tr.packet_cnt AS cnt,
                       DATE_FORMAT(tr.started_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS start_ts,
                       DATE_FORMAT(tr.ended_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS end_ts,
                       tr.max_speed AS max_spd, tr.min_temp, tr.max_temp, tr.max_g_force,
                       GROUP_CONCAT(DISTINCT CONCAT('FmID#', sh.lot_id, '(', sh.leg_no, '구간)') SEPARATOR ', ') AS cargo_summary
                FROM `{DB_NAME}`.`transport_runs` tr
                LEFT JOIN `{DB_NAME}`.`shipments` sh ON tr.run_id = sh.run_id
                WHERE tr.device_id = %s AND {type_filter}
                GROUP BY tr.run_id
                ORDER BY tr.started_at DESC
                LIMIT 25
                """,
                (dev,),
            )
            return {"ok": True, "device_id": dev, "sessions": list(cur.fetchall())}
    finally:
        conn.close()


@app.get("/api/control/history")
def api_control_history(truck_id: str = "truck02", run_id: str = "live"):
    truck = TRUCK_OPTIONS.get(truck_id, TRUCK_OPTIONS["truck02"])
    dev = truck["device_id"]
    conn = get_db_connection()
    try:
        sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
        with conn.cursor() as cur:
            target_run = run_id
            if run_id == "live":
                cutoff_kst = (get_kst_now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(
                    f"""
                    SELECT run_id
                    FROM `{DB_NAME}`.`transport_runs`
                    WHERE device_id = %s
                      AND run_type = 'FIELD_DRIVE'
                      AND ended_at >= %s
                    ORDER BY ended_at DESC
                    LIMIT 1
                    """,
                    (dev, cutoff_kst),
                )
                latest = cur.fetchone()
                target_run = latest["run_id"] if latest else None

            if not target_run:
                return {"ok": True, "run_id": None, "cargo": [], "records": []}

            cur.execute(
                f"""
                SELECT st.device_id AS device,
                       DATE_FORMAT(st.measured_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS timestamp,
                       st.temperature, st.humidity, st.lux, st.g_force, st.speed,
                       st.lat, st.lng, st.raw_status AS status, st.gps_state, st.event_type, st.run_id
                FROM `{DB_NAME}`.`sensor_telemetry` st
                WHERE st.run_id = %s AND st.device_id = %s
                ORDER BY st.measured_at ASC, st.telemetry_id ASC
                """,
                (target_run, dev),
            )
            records = list(cur.fetchall())

            cur.execute(
                f"""
                SELECT sh.lot_id, sh.pkg_id, sh.leg_no, sh.status, hl.variety, hl.total_qty
                FROM `{DB_NAME}`.`shipments` sh
                JOIN `{DB_NAME}`.`harvest_lots` hl ON sh.lot_id = hl.lot_id
                WHERE sh.run_id = %s
                ORDER BY sh.leg_no ASC
                """,
                (target_run,),
            )
            cargo = list(cur.fetchall())
            return {"ok": True, "run_id": target_run, "cargo": cargo, "records": records}
    finally:
        conn.close()


@app.websocket("/ws/telemetry")
async def ws_telemetry_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_clients.add(websocket)
    try:
        for dev, pkt in latest_packets.items():
            await websocket.send_text(json.dumps({"type": "telemetry", "data": pkt}, ensure_ascii=False))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_clients.discard(websocket)
    except Exception:
        ws_clients.discard(websocket)


@app.get("/", response_class=HTMLResponse)
def serve_portal_index():
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
