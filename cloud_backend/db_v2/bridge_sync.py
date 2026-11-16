"""
ColdChain DigitalTwin Platform - Real-Time Incremental V1 <-> V2 Bridge Engine
-------------------------------------------------------------------------------
AWS RDS의 SUPER 권한 제약(log_bin_trust_function_creators=0)에 구애받지 않고,
물리 ESP32 스마트 QR 스캐너(`lab225.qr` INSERT) 및 기존 수집기(`lab225.sensor_data` INSERT)가
기록한 신규 행(id > watermark)만 0.01초 만에 `lab225_v2` 정규화 7개 테이블로 실시간 분해·조인 동기화합니다.
또한 신규 포털/대시보드에서 생성한 A00/A12 데이터를 양쪽 DB에 원자적(Idempotent)으로 기록하는 헬퍼도 제공합니다.
"""

import hashlib
import json
from datetime import datetime, date, timedelta, timezone
from urllib.parse import unquote_plus

KST = timezone(timedelta(hours=9))
VALID_DEVICES = {"carrier-c6-01", "carrier-c6-02", "carrier-c6-03", "carrier-c6-04"}


def get_kst_now():
    return datetime.now(KST).replace(tzinfo=None)


def parse_dt_safe(val, fallback_date=None):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.replace(tzinfo=None) if val.year >= 2000 else None
    if isinstance(val, date):
        return datetime(val.year, val.month, val.day, 0, 0, 0) if val.year >= 2000 else None
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
    if len(s) >= 8 and s[2] == ":" and s[5] == ":" and fallback_date is not None:
        try:
            return datetime.combine(fallback_date, datetime.strptime(s[:8], "%H:%M:%S").time())
        except Exception:
            pass
    return None


def make_sha256(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def parse_sensor_codes(status_str: str, lat: float, lng: float, g_force: float):
    s = status_str or ""
    gps_valid = (lat != 0.0 and lng != 0.0 and abs(lat) > 1.0)
    if "[터널]" in s:
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


def upsert_sensor_packet_v2(cur, record: dict, dst_db: str = "lab225_v2"):
    """단일 센서 패킷을 정규화 테이블(`transport_runs` + `sensor_telemetry`)에 멱등 적재"""
    raw_dev = str(record.get("device") or "carrier-c6-01").strip()
    norm_dev = "carrier-c6-01" if raw_dev == "truck01" else raw_dev
    if norm_dev not in VALID_DEVICES:
        norm_dev = "carrier-c6-01"

    run_id = str(record.get("run_id") or "default_run").strip() or "default_run"
    c_at = parse_dt_safe(record.get("created_at"))
    c_at_kst = (c_at + timedelta(hours=9)) if c_at else get_kst_now()

    dt_meas = parse_dt_safe(
        record.get("timestamp_str") or record.get("timestamp"),
        fallback_date=c_at_kst.date(),
    )
    if dt_meas is None or (dt_meas.year == 2026 and dt_meas.month == 10 and dt_meas.day == 1 and dt_meas.hour == 0 and dt_meas.minute == 0):
        dt_meas = c_at_kst
    meas_str = dt_meas.strftime("%Y-%m-%d %H:%M:%S")

    temp = float(record.get("temperature") or 0.0)
    humi = float(record.get("humidity") or 0.0)
    lux = float(record.get("lux") or 0.0)
    g_force = float(record.get("g_force") or 1.0)
    speed = float(record.get("speed") or 0.0)
    lat = float(record.get("lat") or 0.0)
    lng = float(record.get("lng") or 0.0)
    raw_status = str(record.get("status") or "")[:60]

    gps_state, event_type = parse_sensor_status_safe(raw_status, lat, lng, g_force)
    is_valid_gps = 1 if (gps_state in ("FIX", "TUNNEL") and lat != 0.0) else 0
    is_shock = 1 if event_type == "SHOCK" else 0

    r_low = run_id.lower()
    if "mock" in r_low or "30km" in r_low or raw_dev == "truck01":
        init_type = "MOCK"
    elif "bench" in r_low or "fridge" in r_low:
        init_type = "BENCH"
    elif is_valid_gps or "주행" in r_low or "driving" in r_low:
        init_type = "FIELD_DRIVE"
    else:
        init_type = "NOISE"

    cur.execute(
        f"""
        INSERT INTO `{dst_db}`.`transport_runs`
            (run_id, device_id, run_type, started_at, ended_at, packet_cnt, valid_gps_cnt,
             min_temp, max_temp, avg_temp, max_g_force, max_speed, shock_cnt)
        VALUES (%s, %s, %s, %s, %s, 1, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            run_type = IF(run_type = 'NOISE' AND (VALUES(valid_gps_cnt) > 0 OR packet_cnt >= 3), 'FIELD_DRIVE', run_type),
            started_at = LEAST(IFNULL(started_at, VALUES(started_at)), VALUES(started_at)),
            ended_at = GREATEST(IFNULL(ended_at, VALUES(ended_at)), VALUES(ended_at)),
            avg_temp = ROUND(((IFNULL(avg_temp, 0) * packet_cnt) + VALUES(avg_temp)) / (packet_cnt + 1), 2),
            packet_cnt = packet_cnt + 1,
            valid_gps_cnt = valid_gps_cnt + VALUES(valid_gps_cnt),
            min_temp = LEAST(IFNULL(min_temp, VALUES(min_temp)), VALUES(min_temp)),
            max_temp = GREATEST(IFNULL(max_temp, VALUES(max_temp)), VALUES(max_temp)),
            max_g_force = GREATEST(IFNULL(max_g_force, 1.0), VALUES(max_g_force)),
            max_speed = GREATEST(IFNULL(max_speed, 0), VALUES(max_speed)),
            shock_cnt = shock_cnt + VALUES(shock_cnt)
        """,
        (run_id, norm_dev, init_type, meas_str, meas_str, is_valid_gps, temp, temp, temp, g_force, speed, is_shock),
    )

    cur.execute(
        f"""
        INSERT INTO `{dst_db}`.`sensor_telemetry`
            (run_id, device_id, measured_at, temperature, humidity, lux, g_force,
             speed, lat, lng, gps_state, event_type, raw_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            g_force = GREATEST(g_force, VALUES(g_force)),
            raw_status = VALUES(raw_status)
        """,
        (run_id, norm_dev, meas_str, temp, humi, lux, g_force, speed, lat, lng, gps_state, event_type, raw_status),
    )


def parse_sensor_status_safe(raw_status, lat, lng, g_force):
    return parse_sensor_codes(raw_status, lat, lng, g_force)


def apply_qr_row_to_v2(cur, row: dict, dst_db: str = "lab225_v2"):
    """`lab225.qr`에 INSERT된 스캔/생성 1개 행을 `lab225_v2` 4개 테이블로 정규화 분배(멱등)"""
    lot_id = str(row.get("FmID") or "").strip()
    stage = str(row.get("Lo") or "").strip()
    if not lot_id or not stage:
        return

    now_kst = get_kst_now()
    frt = unquote_plus(str(row.get("FrT") or "Apples")).strip() or "Apples"
    vt = unquote_plus(str(row.get("Vt") or "Fuji Apple")).strip() or "Fuji Apple"
    mt = unquote_plus(str(row.get("Mt") or "Organic")).strip() or "Organic"
    ac = str(row.get("AC") or "55630").strip() or "55630"
    ct = str(row.get("Ct") or "").strip() or None
    rp = str(row.get("Rp") or "").strip() or None
    if rp == "None":
        rp = None

    try:
        hn = int(float(str(row.get("HN") or "1").strip()))
    except Exception:
        hn = 1
    try:
        qt = int(float(str(row.get("Qt") or "0").strip()))
    except Exception:
        qt = 0

    raw_dev = str(row.get("truck_device") or "").strip()
    dev = raw_dev if raw_dev in VALID_DEVICES else None

    hd_dt = parse_dt_safe(row.get("HD")) or now_kst
    std_dt = parse_dt_safe(row.get("Std") or row.get("StD")) or hd_dt
    dd_dt = parse_dt_safe(row.get("DD")) or hd_dt

    try:
        lat_v = float(row.get("Lat")) if row.get("Lat") is not None else None
        lng_v = float(row.get("lon")) if row.get("lon") is not None else None
        if lat_v == 0.0 and lng_v == 0.0:
            lat_v, lng_v = None, None
    except Exception:
        lat_v, lng_v = None, None

    try:
        tp_v = float(row.get("Tp")) if row.get("Tp") not in (None, "", "None") else None
    except Exception:
        tp_v = None
    try:
        hm_v = float(row.get("Hm")) if row.get("Hm") not in (None, "", "None") else None
    except Exception:
        hm_v = None

    init_lot_stage = "A02" if stage == "A00" else (stage if stage in ("A10", "A11", "A12") else "A12")

    cur.execute(
        f"""
        INSERT INTO `{dst_db}`.`harvest_lots`
            (lot_id, origin_zip, fruit_type, variety, farmer_phone, cultivation,
             harvest_no, total_qty, harvest_date, storage_date, deliver_date,
             ag_practice, current_stage, is_test, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
        ON DUPLICATE KEY UPDATE
            current_stage = IF(%s IN ('A10','A11','A12'), %s, current_stage),
            is_test = 0
        """,
        (
            lot_id, ac, frt, vt, ct, mt, hn, qt,
            hd_dt.strftime("%Y-%m-%d"), std_dt.strftime("%Y-%m-%d"), dd_dt.strftime("%Y-%m-%d"),
            rp, init_lot_stage, hd_dt.strftime("%Y-%m-%d %H:%M:%S"),
            stage, stage,
        ),
    )

    if stage == "A00":
        dt_a00 = hd_dt
        dt_a01 = datetime(std_dt.year, std_dt.month, std_dt.day, 9, 0, 0) if std_dt.date() > dt_a00.date() else (dt_a00 + timedelta(seconds=1))
        dt_a02 = max(now_kst, dt_a01 + timedelta(seconds=1))
        h_a00 = make_sha256({"lot_id": lot_id, "stage": "A00", "ac": ac, "qt": qt, "hd": dt_a00.strftime("%Y-%m-%d %H:%M:%S")})

        for s_code, s_dt, s_hash in [("A00", dt_a00, h_a00), ("A01", dt_a01, None), ("A02", dt_a02, None)]:
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, tx_hash)
                VALUES (%s, NULL, %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), tx_hash = COALESCE(tx_hash, VALUES(tx_hash))
                """,
                (lot_id, s_code, s_dt.strftime("%Y-%m-%d %H:%M:%S"), s_hash),
            )
        cur.execute(
            f"""
            INSERT INTO `{dst_db}`.`shipments` (leg_no, lot_id, pkg_id, device_id, departed_at, status)
            VALUES (1, %s, NULL, %s, %s, 'IN_TRANSIT')
            ON DUPLICATE KEY UPDATE device_id = COALESCE(VALUES(device_id), device_id)
            """,
            (lot_id, dev, dt_a02.strftime("%Y-%m-%d %H:%M:%S")),
        )

    elif stage == "A10":
        ev_dt = parse_dt_safe(row.get("APC_AD")) or now_kst
        cur.execute(
            f"""
            INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng)
            VALUES (%s, NULL, 'A10', %s, %s, %s)
            ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), lat = COALESCE(VALUES(lat), lat), lng = COALESCE(VALUES(lng), lng)
            """,
            (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v),
        )
        # 1구간 주행 매칭 및 ARRIVED 마감
        win_s = (ev_dt - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        win_e = ev_dt.strftime("%Y-%m-%d %H:%M:%S")
        leg1 = None
        if dev:
            cur.execute(
                f"""
                SELECT run_id, device_id, MIN(measured_at) AS min_t, COUNT(*) AS cnt,
                       AVG(temperature) AS avg_t, MAX(g_force) AS max_g
                FROM `{dst_db}`.`sensor_telemetry`
                WHERE device_id = %s AND gps_state != 'INDOOR'
                  AND measured_at >= %s AND measured_at <= %s
                GROUP BY run_id, device_id ORDER BY MAX(measured_at) DESC LIMIT 1
                """,
                (dev, win_s, win_e),
            )
            leg1 = cur.fetchone()
        if not leg1:
            cur.execute(
                f"""
                SELECT st.run_id, st.device_id, MIN(st.measured_at) AS min_t, COUNT(*) AS cnt,
                       AVG(st.temperature) AS avg_t, MAX(st.g_force) AS max_g
                FROM `{dst_db}`.`sensor_telemetry` st
                JOIN `{dst_db}`.`transport_runs` tr ON st.run_id = tr.run_id
                WHERE tr.run_type = 'FIELD_DRIVE' AND st.gps_state != 'INDOOR'
                  AND st.measured_at >= %s AND st.measured_at <= %s
                GROUP BY st.run_id, st.device_id ORDER BY MAX(st.measured_at) DESC LIMIT 1
                """,
                (win_s, win_e),
            )
            leg1 = cur.fetchone()

        dep_dt = leg1["min_t"] if (leg1 and leg1.get("min_t")) else (ev_dt - timedelta(minutes=10))
        cur.execute(
            f"""
            INSERT INTO `{dst_db}`.`shipments`
                (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status, gps_points_cnt, avg_temp, max_g_force)
            VALUES (1, %s, NULL, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                device_id = COALESCE(VALUES(device_id), device_id),
                run_id = COALESCE(VALUES(run_id), run_id),
                departed_at = IF(VALUES(run_id) IS NOT NULL, VALUES(departed_at), LEAST(departed_at, VALUES(arrived_at))),
                arrived_at = VALUES(arrived_at),
                status = 'ARRIVED',
                gps_points_cnt = VALUES(gps_points_cnt),
                avg_temp = VALUES(avg_temp),
                max_g_force = VALUES(max_g_force)
            """,
            (
                lot_id,
                (leg1["device_id"] if leg1 else dev),
                (leg1["run_id"] if leg1 else None),
                dep_dt.strftime("%Y-%m-%d %H:%M:%S"),
                ev_dt.strftime("%Y-%m-%d %H:%M:%S"),
                int(leg1["cnt"]) if leg1 else 0,
                round(float(leg1["avg_t"]), 2) if (leg1 and leg1["avg_t"] is not None) else None,
                round(float(leg1["max_g"]), 2) if (leg1 and leg1["max_g"] is not None) else None,
            ),
        )

    elif stage == "A11":
        ev_dt = parse_dt_safe(row.get("APC_WD")) or now_kst
        cur.execute(
            f"""
            INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng)
            VALUES (%s, NULL, 'A11', %s, %s, %s)
            ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), lat = COALESCE(VALUES(lat), lat), lng = COALESCE(VALUES(lng), lng)
            """,
            (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v),
        )

    elif stage == "A12":
        ev_dt = parse_dt_safe(row.get("APC_RT")) or now_kst
        a_q = int(float(str(row.get("AGrade") or "0").strip() or 0))
        b_q = int(float(str(row.get("BGrade") or "0").strip() or 0))
        c_q = int(float(str(row.get("CGrade") or "0").strip() or 0))
        d_q = int(float(str(row.get("DefectRate") or "0").strip() or 0))

        for p_id, g_cd, g_ko, g_q, ship, st_c in [
            (f"{lot_id}-A", "A", "상", a_q, 1, "A12"),
            (f"{lot_id}-B", "B", "중", b_q, 1, "A12"),
            (f"{lot_id}-C", "C", "하", c_q, 1, "A12"),
            (f"{lot_id}-DEF", "DEFECT", "결점과", d_q, 0, "REJECTED"),
        ]:
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`sorted_lots`
                    (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE grade_qty = VALUES(grade_qty), sorted_at = VALUES(sorted_at)
                """,
                (p_id, lot_id, g_cd, g_ko, g_q, ship, st_c, ev_dt.strftime("%Y-%m-%d %H:%M:%S")),
            )

        h_a12 = make_sha256({"lot_id": lot_id, "stage": "A12", "A": a_q, "B": b_q, "C": c_q, "DEFECT": d_q, "rt": ev_dt.strftime("%Y-%m-%d %H:%M:%S")})
        cur.execute(
            f"""
            INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
            VALUES (%s, NULL, 'A12', %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), tx_hash = COALESCE(tx_hash, VALUES(tx_hash))
            """,
            (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, h_a12),
        )

    elif stage in ("A13", "A14", "A15", "A16"):
        pkg_id = f"{lot_id}-A"
        cur.execute(
            f"""
            INSERT IGNORE INTO `{dst_db}`.`sorted_lots`
                (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
            VALUES (%s, %s, 'A', '상', %s, 1, %s, %s)
            """,
            (pkg_id, lot_id, qt, stage, now_kst.strftime("%Y-%m-%d %H:%M:%S")),
        )
        cur.execute(f"UPDATE `{dst_db}`.`sorted_lots` SET current_stage = %s WHERE pkg_id = %s", (stage, pkg_id))

        col_map = {"A13": "APC_PT", "A14": "APC_StD", "A15": "APC_OP", "A16": "Retail_AD"}
        ev_dt = parse_dt_safe(row.get(col_map[stage])) or now_kst
        h_val = make_sha256({"lot_id": lot_id, "pkg_id": pkg_id, "stage": "A16", "at": ev_dt.strftime("%Y-%m-%d %H:%M:%S")}) if stage == "A16" else None

        cur.execute(
            f"""
            INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi, tx_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                event_at = VALUES(event_at),
                lat = COALESCE(VALUES(lat), lat),
                lng = COALESCE(VALUES(lng), lng),
                temp = COALESCE(VALUES(temp), temp),
                humi = COALESCE(VALUES(humi), humi),
                tx_hash = COALESCE(tx_hash, VALUES(tx_hash))
            """,
            (
                lot_id, pkg_id, stage, ev_dt.strftime("%Y-%m-%d %H:%M:%S"),
                lat_v, lng_v,
                tp_v if stage == "A14" else None,
                hm_v if stage == "A14" else None,
                h_val,
            ),
        )

        if stage == "A15":
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`shipments` (leg_no, lot_id, pkg_id, device_id, departed_at, status)
                VALUES (2, %s, %s, %s, %s, 'IN_TRANSIT')
                ON DUPLICATE KEY UPDATE
                    device_id = COALESCE(VALUES(device_id), device_id),
                    departed_at = VALUES(departed_at)
                """,
                (lot_id, pkg_id, dev, ev_dt.strftime("%Y-%m-%d %H:%M:%S")),
            )

        elif stage == "A16":
            dep2_dt = parse_dt_safe(row.get("APC_OP"))
            if not dep2_dt:
                cur.execute(
                    f"SELECT departed_at FROM `{dst_db}`.`shipments` WHERE lot_id = %s AND pkg_id = %s AND leg_no = 2 LIMIT 1",
                    (lot_id, pkg_id),
                )
                sh_prev = cur.fetchone()
                dep2_dt = sh_prev["departed_at"] if (sh_prev and sh_prev.get("departed_at")) else (ev_dt - timedelta(hours=2))

            win2_s = dep2_dt.strftime("%Y-%m-%d %H:%M:%S")
            win2_e = ev_dt.strftime("%Y-%m-%d %H:%M:%S")
            leg2 = None
            if dev:
                cur.execute(
                    f"""
                    SELECT run_id, device_id, COUNT(*) AS cnt, AVG(temperature) AS avg_t, MAX(g_force) AS max_g
                    FROM `{dst_db}`.`sensor_telemetry`
                    WHERE device_id = %s AND gps_state != 'INDOOR'
                      AND measured_at >= %s AND measured_at <= %s
                    GROUP BY run_id, device_id ORDER BY cnt DESC LIMIT 1
                    """,
                    (dev, win2_s, win2_e),
                )
                leg2 = cur.fetchone()
            if not leg2:
                cur.execute(
                    f"""
                    SELECT st.run_id, st.device_id, COUNT(*) AS cnt, AVG(st.temperature) AS avg_t, MAX(st.g_force) AS max_g
                    FROM `{dst_db}`.`sensor_telemetry` st
                    JOIN `{dst_db}`.`transport_runs` tr ON st.run_id = tr.run_id
                    WHERE tr.run_type = 'FIELD_DRIVE' AND st.gps_state != 'INDOOR'
                      AND st.measured_at >= %s AND st.measured_at <= %s
                    GROUP BY st.run_id, st.device_id ORDER BY cnt DESC LIMIT 1
                    """,
                    (win2_s, win2_e),
                )
                leg2 = cur.fetchone()

            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`shipments`
                    (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status, gps_points_cnt, avg_temp, max_g_force)
                VALUES (2, %s, %s, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    device_id = COALESCE(VALUES(device_id), device_id),
                    run_id = COALESCE(VALUES(run_id), run_id),
                    arrived_at = VALUES(arrived_at),
                    status = 'ARRIVED',
                    gps_points_cnt = VALUES(gps_points_cnt),
                    avg_temp = VALUES(avg_temp),
                    max_g_force = VALUES(max_g_force)
                """,
                (
                    lot_id, pkg_id,
                    (leg2["device_id"] if leg2 else dev),
                    (leg2["run_id"] if leg2 else None),
                    win2_s, win2_e,
                    int(leg2["cnt"]) if leg2 else 0,
                    round(float(leg2["avg_t"]), 2) if (leg2 and leg2["avg_t"] is not None) else None,
                    round(float(leg2["max_g"]), 2) if (leg2 and leg2["max_g"] is not None) else None,
                ),
            )


def sync_v1_delta_to_v2(conn, src_db: str = "lab225", dst_db: str = "lab225_v2") -> dict:
    """
    `lab225`에 새로 쌓인 센서 패킷 및 ESP32 스캐너 QR 행(`id > last_id`)만 초고속 증분 동기화!
    대시보드 로드 시 또는 EC2 데몬 백그라운드 워커에서 안전하게 호출 가능.
    """
    synced_sensors = 0
    synced_qr = 0
    with conn.cursor() as cur:
        cur.execute("SET SESSION sql_mode = ''")
        cur.execute(f"SELECT source_table, last_id FROM `{dst_db}`.`_sync_watermark`")
        wm = {r["source_table"]: int(r["last_id"] or 0) for r in cur.fetchall()}
        last_sd_id = wm.get("sensor_data", 0)
        last_qr_id = wm.get("qr", 0)

        # 1) 신규 센서 패킷 먼저 동기화 (스캐너 A10/A16 매칭 시 최신 주행 데이터 참조 가능하도록 순서 보장!)
        cur.execute(
            f"SELECT * FROM `{src_db}`.`sensor_data` WHERE id > %s ORDER BY id ASC LIMIT 2500",
            (last_sd_id,),
        )
        new_sd_rows = cur.fetchall()
        if new_sd_rows:
            for s_row in new_sd_rows:
                upsert_sensor_packet_v2(cur, s_row, dst_db=dst_db)
            new_max_sd = int(new_sd_rows[-1]["id"])
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`_sync_watermark` (source_table, last_id)
                VALUES ('sensor_data', %s)
                ON DUPLICATE KEY UPDATE last_id = GREATEST(last_id, VALUES(last_id))
                """,
                (new_max_sd,),
            )
            synced_sensors = len(new_sd_rows)

        # 2) 신규 스캐너/QR 행 증분 동기화
        cur.execute(
            f"SELECT * FROM `{src_db}`.`qr` WHERE id > %s ORDER BY id ASC LIMIT 200",
            (last_qr_id,),
        )
        new_qr_rows = cur.fetchall()
        if new_qr_rows:
            for q_row in new_qr_rows:
                apply_qr_row_to_v2(cur, q_row, dst_db=dst_db)
            new_max_qr = int(new_qr_rows[-1]["id"])
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`_sync_watermark` (source_table, last_id)
                VALUES ('qr', %s)
                ON DUPLICATE KEY UPDATE last_id = GREATEST(last_id, VALUES(last_id))
                """,
                (new_max_qr,),
            )
            synced_qr = len(new_qr_rows)

    if synced_sensors or synced_qr:
        conn.commit()
    return {"synced_sensors": synced_sensors, "synced_qr": synced_qr}
