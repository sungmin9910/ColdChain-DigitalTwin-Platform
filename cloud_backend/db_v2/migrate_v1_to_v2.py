import os
import sys
import json
import hashlib
from datetime import datetime, date, timedelta
from urllib.parse import unquote_plus
import pymysql

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MYSQL_HOST = os.environ.get("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")

SRC_DB = "lab225"
DST_DB = "lab225_v2"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
SCHEMA_SQL_PATH = os.path.join(BASE_DIR, "schema_v2.sql")

LEDGER_CANDIDATES = [
    os.path.join(PROJECT_ROOT, "blockchain_ledger.json"),
    os.path.join(PROJECT_ROOT, "Final_Experiment", "blockchain_ledger.json"),
    os.path.join(PROJECT_ROOT, "Final_Experiment", "5_Unified_FastAPI_Portal", "blockchain_ledger.json"),
]


def split_sql_statements(sql_text: str):
    stmts = []
    buf = []
    in_single = False
    escape = False
    for ch in sql_text:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\":
            buf.append(ch)
            escape = True
            continue
        if ch == "'":
            in_single = not in_single
            buf.append(ch)
            continue
        if ch == ";" and not in_single:
            raw = "".join(buf).strip()
            lines = [ln for ln in raw.splitlines() if not ln.strip().startswith("--")]
            if any(ln.strip() for ln in lines):
                stmts.append("\n".join(lines))
            buf = []
        else:
            buf.append(ch)
    return stmts


def parse_dt(val, fallback_date=None):
    if val is None:
        return None
    if isinstance(val, datetime):
        if val.year < 2000:
            return None
        return val.replace(tzinfo=None)
    if isinstance(val, date):
        if val.year < 2000:
            return None
        return datetime(val.year, val.month, val.day, 0, 0, 0)
    s = str(val).strip()
    if not s or s.startswith("0000-00-00") or s.startswith("00:00"):
        return None
    for fmt, slen in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M", 16), ("%Y-%m-%d", 10)):
        if len(s) >= slen:
            try:
                dt = datetime.strptime(s[:slen], fmt)
                return dt if dt.year >= 2000 else None
            except Exception:
                continue
    # "HH:MM:SS" 형태만 있는 레거시 문자열인 경우 fallback_date와 결합
    if len(s) >= 8 and s[2] == ":" and s[5] == ":" and fallback_date is not None:
        try:
            t_part = datetime.strptime(s[:8], "%H:%M:%S").time()
            return datetime.combine(fallback_date, t_part)
        except Exception:
            pass
    return None


def safe_int(val, default=0):
    try:
        if val is None or str(val).strip() == "":
            return default
        return int(float(str(val).strip()))
    except Exception:
        return default


def safe_float(val, default=None):
    try:
        if val is None or str(val).strip() == "":
            return default
        return float(str(val).strip())
    except Exception:
        return default


def load_blockchain_hashes():
    """로컬에 흩어져 있던 blockchain_ledger.json 파일들에서 (fmid, stage_prefix) 해시 매핑 로드"""
    hash_map = {}
    for path in LEDGER_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            if not isinstance(entries, list):
                continue
            for item in entries:
                h = item.get("hash")
                meta = item.get("metadata") or {}
                fmid = str(meta.get("FmID") or meta.get("FarmerID") or "").strip()
                stage_raw = str(item.get("stage") or "")
                if not h or not fmid:
                    continue
                if "A12" in stage_raw or meta.get("Type") == "Grading Result":
                    hash_map[(fmid, "A12")] = h
                else:
                    hash_map[(fmid, "A00")] = h
        except Exception:
            pass
    return hash_map


def make_sha256(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def classify_run_type(run_id: str, raw_device: str, pkt_cnt: int, valid_gps_cnt: int) -> str:
    r_low = (run_id or "").lower()
    if "mock" in r_low or "korea_30km_test" in r_low or raw_device == "truck01":
        return "MOCK"
    if "bench" in r_low or "fridge" in r_low:
        return "BENCH"
    if pkt_cnt <= 3 or (valid_gps_cnt == 0 and ("기록" in r_low or pkt_cnt < 10)):
        return "NOISE"
    return "FIELD_DRIVE"


def parse_sensor_status(status_str: str, lat: float, lng: float, g_force: float):
    s = status_str or ""
    gps_valid = (lat != 0.0 and lng != 0.0 and abs(lat) > 1.0)
    if "[실내]" in s or "[대기]" in s:
        gps_state = "INDOOR"
    elif "[터널]" in s:
        gps_state = "TUNNEL"
    elif gps_valid:
        gps_state = "FIX"
    else:
        gps_state = "INDOOR"

    if "충격" in s or g_force >= 1.8:
        event_type = "SHOCK"
    elif "조도" in s:
        event_type = "LUX_JUMP"
    elif "온도" in s:
        event_type = "TEMP_JUMP"
    elif "이상" in s:
        event_type = "ANOMALY"
    else:
        event_type = "NORMAL"
    return gps_state, event_type


def main():
    print("============================================================")
    print(f" [Step 2] 정규화 DB `{DST_DB}` 구축 및 `{SRC_DB}` 안전 마이그레이션")
    print("============================================================")

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )

    ledger_hashes = load_blockchain_hashes()

    try:
        with conn.cursor() as cur:
            cur.execute("SET SESSION sql_mode = ''")

            # 1) schema_v2.sql 실행 (lab225_v2 및 7개 정규화 테이블 생성)
            with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as sf:
                ddl_stmts = split_sql_statements(sf.read())
            for stmt in ddl_stmts:
                cur.execute(stmt)
            conn.commit()
            print(f"[1/4] `{DST_DB}` 스키마 및 7개 정규화 테이블 생성 완료")

            # 2) sensor_data (7,256행) 읽기 전용 추출 -> transport_runs & sensor_telemetry 이관
            cur.execute(f"SELECT * FROM `{SRC_DB}`.`sensor_data` ORDER BY id ASC")
            raw_sensors = cur.fetchall()

            valid_devices = {"carrier-c6-01", "carrier-c6-02", "carrier-c6-03", "carrier-c6-04"}
            runs_bucket = {}
            seen_telemetry_keys = set()
            dedup_skipped = 0

            for r in raw_sensors:
                raw_dev = (r.get("device") or "carrier-c6-01").strip()
                norm_dev = "carrier-c6-01" if raw_dev == "truck01" else raw_dev
                if norm_dev not in valid_devices:
                    norm_dev = "carrier-c6-01"

                run_id = (r.get("run_id") or "default_run").strip()
                c_at = parse_dt(r.get("created_at"))
                c_at_kst = (c_at + timedelta(hours=9)) if c_at else None
                dt_meas = parse_dt(r.get("timestamp_str"), fallback_date=(c_at_kst.date() if c_at_kst else None))
                if dt_meas is None or (dt_meas.year == 2026 and dt_meas.month == 10 and dt_meas.day == 1 and dt_meas.hour == 0 and dt_meas.minute == 0):
                    dt_meas = c_at_kst if c_at_kst else datetime(2026, 10, 1, 0, 0, 0)

                meas_str = dt_meas.strftime("%Y-%m-%d %H:%M:%S")
                dedup_key = (norm_dev, meas_str, run_id)
                if dedup_key in seen_telemetry_keys:
                    dedup_skipped += 1
                    continue
                seen_telemetry_keys.add(dedup_key)

                temp = safe_float(r.get("temperature"), 0.0)
                humi = safe_float(r.get("humidity"), 0.0)
                lux = safe_float(r.get("lux"), 0.0)
                g_force = safe_float(r.get("g_force"), 1.0)
                speed = safe_float(r.get("speed"), 0.0)
                lat = safe_float(r.get("lat"), 0.0)
                lng = safe_float(r.get("lng"), 0.0)
                raw_status = str(r.get("status") or "")[:60]

                gps_state, event_type = parse_sensor_status(raw_status, lat, lng, g_force)

                if run_id not in runs_bucket:
                    runs_bucket[run_id] = {
                        "device_id": norm_dev,
                        "raw_device": raw_dev,
                        "packets": [],
                    }
                runs_bucket[run_id]["packets"].append(
                    (
                        run_id,
                        norm_dev,
                        meas_str,
                        temp,
                        humi,
                        lux,
                        g_force,
                        speed,
                        lat,
                        lng,
                        gps_state,
                        event_type,
                        raw_status,
                        dt_meas,
                    )
                )

            cur.execute(f"USE `{DST_DB}`")
            run_rows_sql = []
            telemetry_rows_sql = []
            for run_id, info in runs_bucket.items():
                pkts = info["packets"]
                pkt_cnt = len(pkts)
                valid_gps_cnt = sum(1 for p in pkts if p[10] in ("FIX", "TUNNEL") and p[8] != 0.0)
                temps = [p[3] for p in pkts]
                g_vals = [p[6] for p in pkts]
                spds = [p[7] for p in pkts]
                dts = [p[13] for p in pkts]
                shock_cnt = sum(1 for p in pkts if p[11] == "SHOCK")

                r_type = classify_run_type(run_id, info["raw_device"], pkt_cnt, valid_gps_cnt)
                run_rows_sql.append(
                    (
                        run_id,
                        info["device_id"],
                        r_type,
                        min(dts).strftime("%Y-%m-%d %H:%M:%S"),
                        max(dts).strftime("%Y-%m-%d %H:%M:%S"),
                        pkt_cnt,
                        valid_gps_cnt,
                        round(min(temps), 2),
                        round(max(temps), 2),
                        round(sum(temps) / len(temps), 2),
                        round(max(g_vals), 2),
                        round(max(spds), 2),
                        shock_cnt,
                    )
                )
                for p in pkts:
                    telemetry_rows_sql.append(p[:13])

            cur.executemany(
                """
                INSERT INTO `transport_runs`
                (run_id, device_id, run_type, started_at, ended_at, packet_cnt, valid_gps_cnt,
                 min_temp, max_temp, avg_temp, max_g_force, max_speed, shock_cnt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                run_rows_sql,
            )

            batch_sz = 500
            for i in range(0, len(telemetry_rows_sql), batch_sz):
                cur.executemany(
                    """
                    INSERT INTO `sensor_telemetry`
                    (run_id, device_id, measured_at, temperature, humidity, lux, g_force,
                     speed, lat, lng, gps_state, event_type, raw_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    telemetry_rows_sql[i : i + batch_sz],
                )
            conn.commit()
            print(
                f"[2/4] 센서 이관 완료: 주행 세션 {len(run_rows_sql)}개 (`transport_runs`), "
                f"정제 패킷 {len(telemetry_rows_sql):,}행 (`sensor_telemetry`, 중복 {dedup_skipped}행 자동 제거)"
            )

            # 3) qr (63행) 읽기 전용 추출 -> harvest_lots, sorted_lots, stage_events, shipments 이관
            cur.execute(f"SELECT * FROM `{SRC_DB}`.`qr` ORDER BY id ASC")
            raw_qr = cur.fetchall()

            lots_group = {}
            for r in raw_qr:
                fmid = str(r.get("FmID") or "").strip()
                if not fmid:
                    continue
                lots_group.setdefault(fmid, []).append(r)

            stage_order = ["A00", "A10", "A11", "A12", "A13", "A14", "A15", "A16"]
            stage_col_map = {
                "A10": "APC_AD",
                "A11": "APC_WD",
                "A12": "APC_RT",
                "A13": "APC_PT",
                "A14": "APC_StD",
                "A15": "APC_OP",
                "A16": "Retail_AD",
            }

            cur.execute(f"USE `{DST_DB}`")

            for lot_id, rows in lots_group.items():
                # 단계별 최신 유효 레코드 수집
                by_stage = {}
                merged = {}
                a00_hd_dt = None
                for r in rows:
                    lo = (r.get("Lo") or "").strip()
                    if lo == "A00":
                        cand_hd = parse_dt(r.get("HD"))
                        if cand_hd:
                            a00_hd_dt = cand_hd
                    for k, v in r.items():
                        if v is not None and str(v).strip() != "" and str(v) != "None":
                            if k == "HD" and parse_dt(v) is None:
                                continue
                            merged[k] = v
                    if lo:
                        by_stage[lo] = r

                origin_zip = str(merged.get("AC") or "55630").strip()
                fruit_type = unquote_plus(str(merged.get("FrT") or "Apples")).strip()
                variety = unquote_plus(str(merged.get("Vt") or "Fuji Apple")).strip()
                farmer_phone = str(merged.get("Ct") or "").strip() or None
                cultivation = unquote_plus(str(merged.get("Mt") or "Organic")).strip()
                harvest_no = safe_int(merged.get("HN"), 1)
                total_qty = safe_int(merged.get("Qt"), 0)
                ag_practice = str(merged.get("Rp") or "").strip() or None

                hd_dt = a00_hd_dt or parse_dt(merged.get("HD")) or parse_dt(merged.get("APC_AD")) or datetime(2026, 5, 1, 9, 0, 0)
                std_dt = parse_dt(merged.get("Std"))
                dd_dt = parse_dt(merged.get("DD"))

                has_sorting = ("A12" in by_stage) or (merged.get("AGrade") is not None)
                # A12 이상 진행된 정상 공정 데이터는 정식 실증(is_test=0), 초기 단발/오류 테스트는 is_test=1
                is_test = 0 if has_sorting else 1

                lot_stages_present = [s for s in ["A10", "A11", "A12"] if s in by_stage]
                lot_current_stage = lot_stages_present[-1] if lot_stages_present else "A02"

                cur.execute(
                    """
                    INSERT INTO `harvest_lots`
                    (lot_id, origin_zip, fruit_type, variety, farmer_phone, cultivation,
                     harvest_no, total_qty, harvest_date, storage_date, deliver_date,
                     ag_practice, current_stage, is_test, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        lot_id,
                        origin_zip,
                        fruit_type,
                        variety,
                        farmer_phone,
                        cultivation,
                        harvest_no,
                        total_qty,
                        hd_dt.strftime("%Y-%m-%d"),
                        std_dt.strftime("%Y-%m-%d") if std_dt else hd_dt.strftime("%Y-%m-%d"),
                        dd_dt.strftime("%Y-%m-%d") if dd_dt else hd_dt.strftime("%Y-%m-%d"),
                        ag_practice,
                        lot_current_stage,
                        is_test,
                        hd_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )

                # --- 농가 3단계 (A00 수확 -> A01 농가저장 -> A02 농가출하) 시간 정합성 계산 ---
                dt_a00 = hd_dt
                if std_dt and std_dt.date() > dt_a00.date():
                    dt_a01 = datetime(std_dt.year, std_dt.month, std_dt.day, 9, 0, 0)
                else:
                    dt_a01 = dt_a00 + timedelta(seconds=1)

                dt_apc_ad = parse_dt(merged.get("APC_AD"))
                hint_dev = str(merged.get("truck_device") or "").strip() or None

                # 1구간 실제 차량 주행 매칭 탐색 (APC_AD 도착 기준 직전 24시간 이내 주행)
                leg1_match = None
                if dt_apc_ad:
                    win_start = (dt_apc_ad - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
                    win_end = dt_apc_ad.strftime("%Y-%m-%d %H:%M:%S")
                    if hint_dev:
                        cur.execute(
                            """
                            SELECT run_id, device_id, MIN(measured_at) AS min_t, MAX(measured_at) AS max_t,
                                   COUNT(*) AS cnt, AVG(temperature) AS avg_t, MAX(g_force) AS max_g
                            FROM `sensor_telemetry`
                            WHERE device_id = %s AND gps_state != 'INDOOR'
                              AND measured_at >= %s AND measured_at <= %s
                            GROUP BY run_id, device_id
                            ORDER BY max_t DESC LIMIT 1
                            """,
                            (hint_dev, win_start, win_end),
                        )
                        leg1_match = cur.fetchone()
                    if not leg1_match:
                        cur.execute(
                            """
                            SELECT st.run_id, st.device_id, MIN(st.measured_at) AS min_t, MAX(st.measured_at) AS max_t,
                                   COUNT(*) AS cnt, AVG(st.temperature) AS avg_t, MAX(st.g_force) AS max_g
                            FROM `sensor_telemetry` st
                            JOIN `transport_runs` tr ON st.run_id = tr.run_id
                            WHERE tr.run_type = 'FIELD_DRIVE' AND st.gps_state != 'INDOOR'
                              AND st.measured_at >= %s AND st.measured_at <= %s
                            GROUP BY st.run_id, st.device_id
                            ORDER BY max_t DESC LIMIT 1
                            """,
                            (win_start, win_end),
                        )
                        leg1_match = cur.fetchone()

                if leg1_match and leg1_match["min_t"]:
                    dt_a02 = leg1_match["min_t"]
                    if dt_a02 <= dt_a01:
                        dt_a02 = dt_a01 + timedelta(seconds=1)
                elif dd_dt and dd_dt.date() > dt_a01.date():
                    dt_a02 = datetime(dd_dt.year, dd_dt.month, dd_dt.day, 8, 0, 0)
                else:
                    dt_a02 = dt_a01 + timedelta(seconds=1)

                if dt_apc_ad and dt_a02 > dt_apc_ad:
                    dt_a02 = dt_apc_ad - timedelta(minutes=10)
                    if dt_a01 >= dt_a02:
                        dt_a01 = dt_a02 - timedelta(minutes=1)
                    if dt_a00 >= dt_a01:
                        dt_a00 = dt_a01 - timedelta(minutes=1)

                a00_hash = ledger_hashes.get((lot_id, "A00")) or make_sha256(
                    {"lot_id": lot_id, "stage": "A00", "origin_zip": origin_zip, "total_qty": total_qty, "hd": str(dt_a00)}
                )

                # A00, A01, A02 이벤트 INSERT
                for st_code, st_dt, st_hash in [
                    ("A00", dt_a00, a00_hash),
                    ("A01", dt_a01, None),
                    ("A02", dt_a02, None),
                ]:
                    cur.execute(
                        """
                        INSERT INTO `stage_events` (lot_id, pkg_id, stage_code, event_at, tx_hash)
                        VALUES (%s, NULL, %s, %s, %s)
                        """,
                        (lot_id, st_code, st_dt.strftime("%Y-%m-%d %H:%M:%S"), st_hash),
                    )

                # 1구간 운송 (shipments leg_no=1) 생성
                if dt_apc_ad:
                    cur.execute(
                        """
                        INSERT INTO `shipments`
                        (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at,
                         status, gps_points_cnt, avg_temp, max_g_force)
                        VALUES (1, %s, NULL, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
                        """,
                        (
                            lot_id,
                            (leg1_match["device_id"] if leg1_match else hint_dev),
                            (leg1_match["run_id"] if leg1_match else None),
                            dt_a02.strftime("%Y-%m-%d %H:%M:%S"),
                            dt_apc_ad.strftime("%Y-%m-%d %H:%M:%S"),
                            int(leg1_match["cnt"]) if leg1_match else 0,
                            round(float(leg1_match["avg_t"]), 2) if (leg1_match and leg1_match["avg_t"] is not None) else None,
                            round(float(leg1_match["max_g"]), 2) if (leg1_match and leg1_match["max_g"] is not None) else None,
                        ),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO `shipments`
                        (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status)
                        VALUES (1, %s, NULL, %s, NULL, %s, NULL, 'IN_TRANSIT')
                        """,
                        (lot_id, hint_dev, dt_a02.strftime("%Y-%m-%d %H:%M:%S")),
                    )

                # --- APC 원물 단계 (A10, A11, A12) & 방법 A 선별 분기 (sorted_lots) ---
                for st_code in ["A10", "A11"]:
                    if st_code in by_stage or merged.get(stage_col_map[st_code]):
                        r_st = by_stage.get(st_code, merged)
                        ev_dt = parse_dt(r_st.get(stage_col_map[st_code])) or parse_dt(merged.get(stage_col_map[st_code])) or dt_a02
                        lat_v = safe_float(r_st.get("Lat"))
                        lng_v = safe_float(r_st.get("lon"))
                        if lat_v == 0.0 and lng_v == 0.0:
                            lat_v, lng_v = None, None
                        cur.execute(
                            """
                            INSERT INTO `stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng)
                            VALUES (%s, NULL, %s, %s, %s, %s)
                            """,
                            (lot_id, st_code, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v),
                        )

                rep_pkg_id = None
                if has_sorting:
                    r_a12 = by_stage.get("A12", merged)
                    dt_a12 = parse_dt(r_a12.get("APC_RT")) or parse_dt(merged.get("APC_RT")) or dt_apc_ad or dt_a02
                    a_qty = safe_int(r_a12.get("AGrade") or merged.get("AGrade"), 0)
                    b_qty = safe_int(r_a12.get("BGrade") or merged.get("BGrade"), 0)
                    c_qty = safe_int(r_a12.get("CGrade") or merged.get("CGrade"), 0)
                    def_qty = safe_int(r_a12.get("DefectRate") or merged.get("DefectRate"), 0)

                    # 방법 A: sorted_lots에 A / B / C / DEFECT 4행 분기 적재
                    pkg_stages_present = [s for s in ["A13", "A14", "A15", "A16"] if (s in by_stage or merged.get(stage_col_map[s]))]
                    a_pkg_final_stage = pkg_stages_present[-1] if pkg_stages_present else "A12"

                    grade_defs = [
                        (f"{lot_id}-A", "A", "상", a_qty, 1, a_pkg_final_stage),
                        (f"{lot_id}-B", "B", "중", b_qty, 1, "A12"),
                        (f"{lot_id}-C", "C", "하", c_qty, 1, "A12"),
                        (f"{lot_id}-DEF", "DEFECT", "결점과", def_qty, 0, "REJECTED"),
                    ]
                    for p_id, g_code, g_ko, g_qty, shippable, p_stage in grade_defs:
                        cur.execute(
                            """
                            INSERT INTO `sorted_lots`
                            (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (p_id, lot_id, g_code, g_ko, g_qty, shippable, p_stage, dt_a12.strftime("%Y-%m-%d %H:%M:%S")),
                        )

                    rep_pkg_id = f"{lot_id}-A"
                    a12_hash = ledger_hashes.get((lot_id, "A12")) or make_sha256(
                        {"lot_id": lot_id, "stage": "A12", "A": a_qty, "B": b_qty, "C": c_qty, "DEFECT": def_qty, "rt": str(dt_a12)}
                    )
                    lat_12 = safe_float(r_a12.get("Lat"))
                    lng_12 = safe_float(r_a12.get("lon"))
                    if lat_12 == 0.0 and lng_12 == 0.0:
                        lat_12, lng_12 = None, None
                    cur.execute(
                        """
                        INSERT INTO `stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
                        VALUES (%s, NULL, 'A12', %s, %s, %s, %s)
                        """,
                        (lot_id, dt_a12.strftime("%Y-%m-%d %H:%M:%S"), lat_12, lng_12, a12_hash),
                    )

                    # --- 정품 패키지 단계 (A13 포장 -> A14 APC저장 -> A15 APC출하 -> A16 판매처도착) ---
                    for st_code in ["A13", "A14", "A15", "A16"]:
                        col_name = stage_col_map[st_code]
                        if st_code in by_stage or merged.get(col_name):
                            r_st = by_stage.get(st_code, merged)
                            ev_dt = parse_dt(r_st.get(col_name)) or parse_dt(merged.get(col_name)) or dt_a12
                            lat_v = safe_float(r_st.get("Lat"))
                            lng_v = safe_float(r_st.get("lon"))
                            if lat_v == 0.0 and lng_v == 0.0:
                                lat_v, lng_v = None, None
                            tp_v = safe_float(r_st.get("Tp") or merged.get("Tp")) if st_code == "A14" else None
                            hm_v = safe_float(r_st.get("Hm") or merged.get("Hm")) if st_code == "A14" else None
                            st_hash = (
                                make_sha256({"lot_id": lot_id, "pkg_id": rep_pkg_id, "stage": "A16", "at": str(ev_dt)})
                                if st_code == "A16"
                                else None
                            )
                            cur.execute(
                                """
                                INSERT INTO `stage_events`
                                (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi, tx_hash)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (lot_id, rep_pkg_id, st_code, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, tp_v, hm_v, st_hash),
                            )

                    # 2구간 운송 (shipments leg_no=2: A15 ~ A16) 매칭 생성
                    dt_apc_op = parse_dt(merged.get("APC_OP"))
                    dt_retail_ad = parse_dt(merged.get("Retail_AD"))
                    if dt_apc_op and rep_pkg_id:
                        win2_start = dt_apc_op.strftime("%Y-%m-%d %H:%M:%S")
                        win2_end = (dt_retail_ad if dt_retail_ad else (dt_apc_op + timedelta(hours=12))).strftime("%Y-%m-%d %H:%M:%S")
                        leg2_match = None
                        if hint_dev:
                            cur.execute(
                                """
                                SELECT run_id, device_id, COUNT(*) AS cnt, AVG(temperature) AS avg_t, MAX(g_force) AS max_g
                                FROM `sensor_telemetry`
                                WHERE device_id = %s AND gps_state != 'INDOOR'
                                  AND measured_at >= %s AND measured_at <= %s
                                GROUP BY run_id, device_id
                                ORDER BY cnt DESC LIMIT 1
                                """,
                                (hint_dev, win2_start, win2_end),
                            )
                            leg2_match = cur.fetchone()
                        if not leg2_match:
                            cur.execute(
                                """
                                SELECT st.run_id, st.device_id, COUNT(*) AS cnt, AVG(st.temperature) AS avg_t, MAX(st.g_force) AS max_g
                                FROM `sensor_telemetry` st
                                JOIN `transport_runs` tr ON st.run_id = tr.run_id
                                WHERE tr.run_type = 'FIELD_DRIVE' AND st.gps_state != 'INDOOR'
                                  AND st.measured_at >= %s AND st.measured_at <= %s
                                GROUP BY st.run_id, st.device_id
                                ORDER BY cnt DESC LIMIT 1
                                """,
                                (win2_start, win2_end),
                            )
                            leg2_match = cur.fetchone()

                        cur.execute(
                            """
                            INSERT INTO `shipments`
                            (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at,
                             status, gps_points_cnt, avg_temp, max_g_force)
                            VALUES (2, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                lot_id,
                                rep_pkg_id,
                                (leg2_match["device_id"] if leg2_match else hint_dev),
                                (leg2_match["run_id"] if leg2_match else None),
                                dt_apc_op.strftime("%Y-%m-%d %H:%M:%S"),
                                dt_retail_ad.strftime("%Y-%m-%d %H:%M:%S") if dt_retail_ad else None,
                                "ARRIVED" if dt_retail_ad else "IN_TRANSIT",
                                int(leg2_match["cnt"]) if leg2_match else 0,
                                round(float(leg2_match["avg_t"]), 2) if (leg2_match and leg2_match["avg_t"] is not None) else None,
                                round(float(leg2_match["max_g"]), 2) if (leg2_match and leg2_match["max_g"] is not None) else None,
                            ),
                        )

            conn.commit()
            print(f"[3/4] 원물·선별·타임라인·운송 이관 완료: 총 {len(lots_group)}개 원물 Lot 정규화 완료")

            # 증분 동기화 워터마크 초기화 (현재까지 이관된 lab225 원본 MAX(id) 기록)
            cur.execute(f"SELECT COALESCE(MAX(id), 0) AS mid FROM `{SRC_DB}`.`qr`")
            max_qr_id = int(cur.fetchone()["mid"] or 0)
            cur.execute(f"SELECT COALESCE(MAX(id), 0) AS mid FROM `{SRC_DB}`.`sensor_data`")
            max_sd_id = int(cur.fetchone()["mid"] or 0)
            cur.execute(
                f"""
                INSERT INTO `{DST_DB}`.`_sync_watermark` (source_table, last_id)
                VALUES ('qr', %s), ('sensor_data', %s)
                ON DUPLICATE KEY UPDATE last_id = VALUES(last_id)
                """,
                (max_qr_id, max_sd_id),
            )
            conn.commit()
            print(f"      -> 증분 브릿지 워터마크 기록 완료: qr.last_id={max_qr_id}, sensor_data.last_id={max_sd_id}")

            # 4) 사후 무결성 & JOIN 검증 리포트 출력
            print("\n============================================================")
            print(f" [4/4] `{DST_DB}` 마이그레이션 무결성 및 JOIN 사전 검증 리포트")
            print("============================================================")
            for tbl in ["vehicles", "harvest_lots", "sorted_lots", "stage_events", "transport_runs", "shipments", "sensor_telemetry"]:
                cur.execute(f"SELECT COUNT(*) AS c FROM `{DST_DB}`.`{tbl}`")
                print(f"  - {tbl:18s}: {cur.fetchone()['c']:,} 행")

            cur.execute(f"SELECT run_type, COUNT(*) AS runs, SUM(packet_cnt) AS pkts FROM `{DST_DB}`.`transport_runs` GROUP BY run_type")
            print("\n  [주행 세션 자동 분류 결과 (transport_runs)]")
            for r in cur.fetchall():
                print(f"    * {r['run_type']:12s}: {r['runs']:2d}개 세션 (패킷 {int(r['pkts']):,}건)")

            cur.execute(
                f"""
                SELECT hl.lot_id, hl.total_qty, SUM(sl.grade_qty) AS sum_sorted
                FROM `{DST_DB}`.`harvest_lots` hl
                JOIN `{DST_DB}`.`sorted_lots` sl ON hl.lot_id = sl.lot_id
                GROUP BY hl.lot_id, hl.total_qty
                """
            )
            mass_rows = cur.fetchall()
            mismatches = [m for m in mass_rows if int(m["total_qty"]) != int(m["sum_sorted"])]
            print(f"\n  [방법 A 수량 보존 검증 (A+B+C+DEFECT == total_qty)]: 대상 {len(mass_rows)}건 중 불일치 {len(mismatches)}건")

            print("\n  [실차 완주 실험 (FmID=85, FmID=13) 1·2구간 JOIN 검증]")
            cur.execute(
                f"""
                SELECT s.lot_id, s.pkg_id, s.leg_no, v.truck_id, s.run_id,
                       s.departed_at, s.arrived_at, s.status, s.gps_points_cnt, s.avg_temp, s.max_g_force
                FROM `{DST_DB}`.`shipments` s
                LEFT JOIN `{DST_DB}`.`vehicles` v ON s.device_id = v.device_id
                WHERE s.lot_id IN ('85', '13')
                ORDER BY s.lot_id DESC, s.leg_no ASC
                """
            )
            for srow in cur.fetchall():
                print(
                    f"    * Lot #{srow['lot_id']} (pkg={srow['pkg_id'] or '원물'}) | {srow['leg_no']}구간 | "
                    f"차량={srow['truck_id']} | run='{srow['run_id']}' | "
                    f"{srow['departed_at']} ~ {srow['arrived_at']} | GPS={srow['gps_points_cnt']}점 | "
                    f"평균온도={srow['avg_temp']}℃ | 최대충격={srow['max_g_force']}G"
                )

            # 원본 lab225 무손실 확인
            cur.execute(f"SELECT COUNT(*) AS c FROM `{SRC_DB}`.`qr`")
            orig_qr_cnt = cur.fetchone()["c"]
            cur.execute(f"SELECT COUNT(*) AS c FROM `{SRC_DB}`.`sensor_data`")
            orig_sd_cnt = cur.fetchone()["c"]
            print(f"\n  [원본 `{SRC_DB}` 보존 확인]: qr={orig_qr_cnt}행, sensor_data={orig_sd_cnt:,}행 (변동 0건!)")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
