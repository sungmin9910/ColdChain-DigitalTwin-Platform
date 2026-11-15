import os
import io
import json
import time
import base64
import hashlib
import random
import asyncio
import threading
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import pymysql
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image
import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =====================================================================
# 1. 환경 설정 및 기존 시스템(Streamlit / AWS RDS / HiveMQ) 100% 호환 설정
# =====================================================================
DB_HOST = os.getenv("MYSQL_HOST", "15.165.68.30")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))
DB_USER = os.getenv("MYSQL_USER", "admin")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "12345678")
DB_NAME = os.getenv("MYSQL_DATABASE", "lab225")

MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

STREAMLIT_CONSUMER_URL = "https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STEP1_IMG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "1_PC_QR_Generators"))
BLOCKCHAIN_FILE = os.path.join(BASE_DIR, "blockchain_ledger.json")

KST = timezone(timedelta(hours=9))

def get_kst_now():
    return datetime.now(KST)

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
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
app = FastAPI(title="ColdChain DigitalTwin Unified Portal (FastAPI)")

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
# 3. 헬퍼 함수 (블록체인 해시 & QR 이미지 Base64 생성)
# =====================================================================
def calculate_hash(data_dict: dict) -> str:
    data_str = json.dumps(data_dict, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(data_str).hexdigest()

def save_to_blockchain(data_hash: str, metadata: dict, stage: str):
    entry = {
        "timestamp": get_kst_now().strftime("%Y-%m-%d %H:%M:%S"),
        "hash": data_hash,
        "stage": stage,
        "metadata": metadata,
    }
    chain_data = []
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
                chain_data = json.load(f)
        except Exception:
            chain_data = []
    chain_data.append(entry)
    with open(BLOCKCHAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(chain_data, f, indent=2, ensure_ascii=False)

def make_qr_base64(qr_url: str, overlay_filename: str = None, rounded: bool = True) -> str:
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

    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

# =====================================================================
# 4. REST API 엔드포인트
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
def api_get_fmid_list():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT FmID, MAX(FrT) as FrT, MAX(Vt) as Vt, MAX(Lo) as latest_step, MAX(id) as max_id
                FROM qr
                WHERE FmID IS NOT NULL AND FmID != ''
                GROUP BY FmID
                ORDER BY max_id DESC
                LIMIT 30
            """)
            rows = cur.fetchall()
            return {"ok": True, "items": rows}
    finally:
        conn.close()

@app.get("/api/consumer/trace/{fmid}")
def api_get_consumer_trace(fmid: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM qr WHERE FmID = %s ORDER BY id ASC", (fmid,))
            qr_rows = cur.fetchall()
            if not qr_rows:
                raise HTTPException(status_code=404, detail=f"FmID={fmid} 이력 데이터가 존재하지 않습니다.")

            # 병합 요약 정보 및 단계별 시각 추출
            stage_time_cols = {
                "A00": "HD",
                "A10": "APC_AD",
                "A11": "APC_WD",
                "A12": "APC_RT",
                "A13": "APC_PT",
                "A14": "APC_StD",
                "A15": "APC_OP",
                "A16": "Retail_AD",
            }
            merged = {}
            step_times = {}
            for r in qr_rows:
                lo = r.get("Lo")
                for k, v in r.items():
                    if v is not None and str(v).strip() != "" and str(v) != "None":
                        merged[k] = str(v) if isinstance(v, datetime) else v
                if lo:
                    t_col = stage_time_cols.get(lo, "HD")
                    step_times[lo] = {
                        "Lo": lo,
                        "timestamp": str(r.get(t_col) or r.get("HD") or ""),
                        "lat": float(r["Lat"]) if r.get("Lat") not in (None, "", 0, "0") else None,
                        "lon": float(r["lon"]) if r.get("lon") not in (None, "", 0, "0") else None,
                    }

            # 1구간(HD ~ APC_AD) 및 2구간(APC_OP ~ Retail_AD) 주행 센서 궤적 조회
            def fetch_segment(start_t, end_t):
                if not start_t or not end_t:
                    return []
                cur.execute("""
                    SELECT timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id
                    FROM sensor_data
                    WHERE timestamp_str >= %s AND timestamp_str <= %s
                      AND lat IS NOT NULL AND lng IS NOT NULL AND lat != 0 AND lng != 0
                    ORDER BY timestamp_str ASC
                """, (str(start_t), str(end_t)))
                return list(cur.fetchall())

            t_hd = merged.get("HD")
            t_a10 = merged.get("APC_AD")
            t_a15 = merged.get("APC_OP") or merged.get("APC_StD") or merged.get("APC_PT")
            t_a16 = merged.get("Retail_AD") or "2099-12-31 23:59:59"

            leg1_pts = fetch_segment(t_hd, t_a10) if (t_hd and t_a10) else []
            leg2_pts = fetch_segment(t_a15, t_a16) if t_a15 else []

            return {
                "ok": True,
                "fmid": fmid,
                "summary": merged,
                "steps": list(step_times.values()),
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
    DD_date: str
    StD_date: str
    Mt: str = "Organic"
    HN: str = "1"
    Qt: str = "50"
    Rp: str = "GAP"
    target_mode: str = "streamlit"  # "streamlit" (현재 메인) or "fastapi" (차기 메인 전환용)
    portal_base_url: str = ""

@app.post("/api/farm/create-qr")
def api_create_farm_qr(req: FarmQRRequest):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SET time_zone = '+09:00'")
            cur.execute("SELECT DATE_FORMAT(NOW(), '%%H:%%i:%%s') as cur_time")
            srv_time = cur.fetchone()["cur_time"]
            hd_full = f"{req.HD_date} {srv_time}"

            cur.execute("""
                INSERT INTO qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                "A00", req.AC, req.FmID, req.FrT, req.Vt, req.Ct,
                hd_full, req.DD_date, req.Qt, req.Mt, req.HN, req.StD_date, req.Rp
            ))

        params = {
            "AC": req.AC, "FmID": req.FmID, "Ct": req.Ct, "FrT": req.FrT,
            "Vt": req.Vt, "HD": hd_full, "DD": req.DD_date, "StD": req.StD_date,
            "Mt": req.Mt, "HN": req.HN, "Qt": req.Qt, "Rp": req.Rp,
        }
        query_string = urlencode(params)
        if req.target_mode == "fastapi" and req.portal_base_url:
            base = req.portal_base_url.rstrip("/")
            qr_url = f"{base}/?{query_string}"
        else:
            qr_url = f"{STREAMLIT_CONSUMER_URL}/?{query_string}"

        integrity_hash = calculate_hash(params)
        save_to_blockchain(integrity_hash, {"FmID": req.FmID, "HD": hd_full}, "A00 (Farm Harvest)")

        overlay_icon = FRUIT_IMAGES_FARM.get(req.FrT, "apple.png")
        qr_b64 = make_qr_base64(qr_url, overlay_filename=overlay_icon, rounded=True)

        return {
            "ok": True,
            "fmid": req.FmID,
            "hd_full": hd_full,
            "hash": integrity_hash,
            "qr_url": qr_url,
            "qr_base64": qr_b64,
        }
    finally:
        conn.close()

@app.get("/api/apc/candidates")
def api_apc_candidates():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM qr
                WHERE Lo IN ('A11', 'A10', 'A00') AND FmID IS NOT NULL
                ORDER BY id DESC
                LIMIT 20
            """)
            rows = cur.fetchall()
            seen = set()
            items = []
            for r in rows:
                fmid = r.get("FmID")
                if fmid and fmid not in seen:
                    seen.add(fmid)
                    for k, v in list(r.items()):
                        if isinstance(v, datetime):
                            r[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                    items.append(r)
            return {"ok": True, "items": items}
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
        with conn.cursor() as cur:
            cur.execute("SET time_zone = '+09:00'")
            cur.execute("SELECT DATE_FORMAT(NOW(), '%%Y-%%m-%%d %%H:%%i:%%s') as srv_now")
            srv_now = cur.fetchone()["srv_now"]

            cur.execute("SELECT * FROM qr WHERE FmID = %s ORDER BY id DESC LIMIT 1", (req.FmID,))
            prev_row = cur.fetchone()
            if not prev_row:
                raise HTTPException(status_code=404, detail=f"FmID={req.FmID} 원본 데이터를 찾을 수 없습니다.")

            data_dict = dict(prev_row)
            data_dict.update({
                "Lo": "A12",
                "AGrade": req.AGrade,
                "BGrade": req.BGrade,
                "CGrade": req.CGrade,
                "DefectRate": req.DefectRate,
                "APC_RT": srv_now,
            })

            cur.execute("SHOW COLUMNS FROM qr")
            db_cols = {c["Field"] for c in cur.fetchall()}
            data_to_insert = {k: v for k, v in data_dict.items() if k in db_cols and k != "id"}

            cols_sql = ", ".join(data_to_insert.keys())
            placeholders_sql = ", ".join([f"%({k})s" for k in data_to_insert.keys()])
            cur.execute(f"INSERT INTO qr ({cols_sql}) VALUES ({placeholders_sql})", data_to_insert)

        integrity_hash = calculate_hash(data_to_insert)
        save_to_blockchain(integrity_hash, {"FmID": req.FmID, "APC_RT": srv_now}, "A12 (Sorting & Grading)")

        fruit = str(prev_row.get("FrT") or "Apples")
        ac = str(prev_row.get("AC") or "")
        grade_icons = FRUIT_IMAGES_GRADE.get(fruit, FRUIT_IMAGES_GRADE["Apples"])

        base_url = (
            req.portal_base_url.rstrip("/")
            if (req.target_mode == "fastapi" and req.portal_base_url)
            else STREAMLIT_CONSUMER_URL
        )

        qrs = []
        for idx, (g_kr, g_en, cnt) in enumerate([
            ("상", "A", req.AGrade),
            ("중", "B", req.BGrade),
            ("하", "C", req.CGrade),
        ]):
            q_url = f"{base_url}/?FmID={req.FmID}&grade={g_kr}&AC={ac}&FrT={fruit}"
            q_b64 = make_qr_base64(q_url, overlay_filename=grade_icons[idx], rounded=False)
            qrs.append({
                "grade_en": g_en,
                "grade_kr": g_kr,
                "count": cnt,
                "qr_url": q_url,
                "qr_base64": q_b64,
            })

        return {
            "ok": True,
            "fmid": req.FmID,
            "apc_rt": srv_now,
            "hash": integrity_hash,
            "qrs": qrs,
        }
    finally:
        conn.close()

@app.get("/api/control/sessions")
def api_control_sessions(truck_id: str = "truck02"):
    truck = TRUCK_OPTIONS.get(truck_id, TRUCK_OPTIONS["truck02"])
    dev = truck["device_id"]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT run_id, COUNT(*) as cnt, MIN(timestamp_str) as start_ts, MAX(timestamp_str) as end_ts,
                       MAX(speed) as max_spd, MIN(temperature) as min_temp, MAX(temperature) as max_temp
                FROM sensor_data
                WHERE (device = %s OR (device = 'truck01' AND %s = 'carrier-c6-01'))
                  AND run_id IS NOT NULL
                GROUP BY run_id
                HAVING cnt >= 2
                ORDER BY MAX(id) DESC
                LIMIT 25
            """, (dev, dev))
            rows = cur.fetchall()
            return {"ok": True, "device_id": dev, "sessions": rows}
    finally:
        conn.close()

@app.get("/api/control/history")
def api_control_history(truck_id: str = "truck02", run_id: str = "live"):
    truck = TRUCK_OPTIONS.get(truck_id, TRUCK_OPTIONS["truck02"])
    dev = truck["device_id"]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            target_run = run_id
            if run_id == "live":
                cutoff_kst = (get_kst_now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    SELECT run_id, MAX(id) as last_id, COUNT(*) as cnt
                    FROM sensor_data
                    WHERE (device = %s OR (device = 'truck01' AND %s = 'carrier-c6-01'))
                      AND run_id IS NOT NULL
                      AND (timestamp_str >= %s OR created_at >= UTC_TIMESTAMP() - INTERVAL 6 HOUR)
                    GROUP BY run_id
                    HAVING cnt >= 2
                    ORDER BY last_id DESC
                    LIMIT 1
                """, (dev, dev, cutoff_kst))
                latest = cur.fetchone()
                target_run = latest["run_id"] if latest else None

            if not target_run:
                return {"ok": True, "run_id": None, "records": []}

            cur.execute("""
                SELECT device, timestamp_str as timestamp, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id
                FROM sensor_data
                WHERE run_id = %s
                  AND (device = %s OR (device = 'truck01' AND %s = 'carrier-c6-01'))
                ORDER BY id ASC
            """, (target_run, dev, dev))
            records = list(cur.fetchall())
            return {"ok": True, "run_id": target_run, "records": records}
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
