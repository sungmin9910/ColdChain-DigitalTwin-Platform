"""
ColdChain DigitalTwin Platform - Real-Time Incremental V1 <-> V2/V3 Bridge Engine
-------------------------------------------------------------------------------
AWS RDS의 SUPER 권한 제약(log_bin_trust_function_creators=0)에 구애받지 않고,
물리 ESP32 스마트 QR 스캐너(`lab225.qr` INSERT) 및 수집 데몬(`lab225.sensor_data` INSERT)이
기록한 신규 행(id > watermark)만 초고속으로 `lab225_v2` 정규화 테이블로 실시간 분해·조인 동기화합니다.

지원 프로토콜:
- v3 (신규 16자리 LotID + A00 ~ D10 분기 공정 + 3구간 운송 + 실내 창고 STORAGE 세션)
- v2 (레거시 FmID + A00 ~ A16 직선 공정 + 2구간 운송 100% 하위 호환)
"""

import hashlib
import json
import os
import sys
from datetime import datetime, date, timedelta, timezone
from urllib.parse import unquote_plus

_CB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _CB_ROOT not in sys.path:
    sys.path.insert(0, _CB_ROOT)

from supply_chain_spec import (
    get_crop_code,
    is_v3_lot_id,
    is_v4_lot_id,
    is_modern_lot_id,
    parse_lot_id,
    parse_lot_id_16,
    detect_protocol_version,
    V2_ONLY_STAGES,
)

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
    if "[실내]" in s or "[대기]" in s or "[보관]" in s:
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


def parse_sensor_status_safe(raw_status, lat, lng, g_force):
    return parse_sensor_codes(raw_status, lat, lng, g_force)


def normalize_pkg_grade(val) -> tuple[str, str]:
    """스캔된 등급 문자열(A/B/C 또는 상/중/하)을 정규화 코드('A','B','C')와 한글 라벨('상','중','하')로 변환"""
    s = unquote_plus(str(val or "A")).strip().upper()
    if s in ("B", "중", "M", "MEDIUM"):
        return "B", "중"
    if s in ("C", "하", "L", "LOW"):
        return "C", "하"
    return "A", "상"


def refresh_run_stats_v2(cur, run_id: str, dst_db: str = "lab225_v2"):
    """`sensor_telemetry` 실제 적재 행 기준으로 `transport_runs` 집계 통계를 오차 없이 재계산"""
    if not run_id:
        return
    cur.execute(
        f"""
        UPDATE `{dst_db}`.`transport_runs` tr
        JOIN (
            SELECT run_id,
                   MIN(measured_at) AS min_m,
                   MAX(measured_at) AS max_m,
                   COUNT(*) AS pkt_cnt,
                   SUM(CASE WHEN gps_state IN ('FIX', 'TUNNEL') AND lat != 0 AND lng != 0 THEN 1 ELSE 0 END) AS v_gps_cnt,
                   ROUND(MIN(temperature), 2) AS min_t,
                   ROUND(MAX(temperature), 2) AS max_t,
                   ROUND(AVG(temperature), 2) AS avg_t,
                   ROUND(MAX(g_force), 2) AS max_g,
                   ROUND(MAX(speed), 1) AS max_spd,
                   SUM(CASE WHEN event_type = 'SHOCK' OR g_force >= 1.8 THEN 1 ELSE 0 END) AS shk_cnt
            FROM `{dst_db}`.`sensor_telemetry`
            WHERE run_id = %s
            GROUP BY run_id
        ) agg ON tr.run_id = agg.run_id
        SET tr.started_at = agg.min_m,
            tr.ended_at = agg.max_m,
            tr.packet_cnt = agg.pkt_cnt,
            tr.valid_gps_cnt = agg.v_gps_cnt,
            tr.min_temp = agg.min_t,
            tr.max_temp = agg.max_t,
            tr.avg_temp = agg.avg_t,
            tr.max_g_force = agg.max_g,
            tr.max_speed = agg.max_spd,
            tr.shock_cnt = agg.shk_cnt,
            tr.run_type = IF(tr.run_type = 'NOISE' AND agg.v_gps_cnt > 0, 'FIELD_DRIVE', tr.run_type)
        """,
        (run_id,),
    )


def _match_drive_segment(cur, dst_db: str, dev: str, win_s: str, win_e: str, prefer_latest: bool = False):
    order_clause = "MAX(measured_at) DESC, cnt DESC" if prefer_latest else "cnt DESC, MAX(measured_at) DESC"
    match = None
    if dev:
        cur.execute(
            f"""
            SELECT run_id, device_id, MIN(measured_at) AS min_t, COUNT(*) AS cnt,
                   AVG(temperature) AS avg_t, MAX(g_force) AS max_g
            FROM `{dst_db}`.`sensor_telemetry`
            WHERE device_id = %s AND gps_state != 'INDOOR' AND lat != 0 AND lng != 0
              AND measured_at >= %s AND measured_at <= %s
            GROUP BY run_id, device_id ORDER BY {order_clause} LIMIT 1
            """,
            (dev, win_s, win_e),
        )
        match = cur.fetchone()
    if not match:
        order_clause_st = "MAX(st.measured_at) DESC, cnt DESC" if prefer_latest else "cnt DESC, MAX(st.measured_at) DESC"
        cur.execute(
            f"""
            SELECT st.run_id, st.device_id, MIN(st.measured_at) AS min_t, COUNT(*) AS cnt,
                   AVG(st.temperature) AS avg_t, MAX(st.g_force) AS max_g
            FROM `{dst_db}`.`sensor_telemetry` st
            JOIN `{dst_db}`.`transport_runs` tr ON st.run_id = tr.run_id
            WHERE tr.run_type = 'FIELD_DRIVE' AND st.gps_state != 'INDOOR' AND st.lat != 0 AND st.lng != 0
              AND st.measured_at >= %s AND st.measured_at <= %s
            GROUP BY st.run_id, st.device_id ORDER BY {order_clause_st} LIMIT 1
            """,
            (win_s, win_e),
        )
        match = cur.fetchone()
    return match


def refresh_shipment_stats_v2(cur, dst_db: str = "lab225_v2", lot_id: str = None):
    """
    센서 패킷과 QR 스캔의 도착 순서가 엇갈려도 `shipments`의 1·2·3구간 요약 통계
    (run_id, device_id, gps_points_cnt, avg_temp, max_g_force)를 정확히 동기화합니다.
    """
    where_clause = (
        "WHERE lot_id = %s"
        if lot_id
        else "WHERE status = 'IN_TRANSIT' OR gps_points_cnt = 0 OR run_id IS NULL OR departed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    )
    params = (lot_id,) if lot_id else ()
    cur.execute(f"SELECT * FROM `{dst_db}`.`shipments` {where_clause}", params)
    sh_rows = cur.fetchall()
    for sh in sh_rows:
        sh_id = sh["shipment_id"]
        leg_no = int(sh["leg_no"])
        sh_lot_id = str(sh["lot_id"])
        dev = sh.get("device_id")
        dep_dt = parse_dt_safe(sh.get("departed_at"))
        arr_dt = parse_dt_safe(sh.get("arrived_at"))
        if not dep_dt:
            continue

        is_legacy_leg1 = (leg_no == 1 and not is_modern_lot_id(sh_lot_id))
        if is_legacy_leg1 and arr_dt:
            win_s = (arr_dt - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
            win_e = arr_dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            win_s = (dep_dt - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
            win_e = ((arr_dt + timedelta(minutes=2)) if arr_dt else (dep_dt + timedelta(hours=12))).strftime("%Y-%m-%d %H:%M:%S")

        match = _match_drive_segment(cur, dst_db, dev, win_s, win_e, prefer_latest=is_legacy_leg1)
        if match and int(match["cnt"] or 0) > 0:
            new_dep = (
                match["min_t"].strftime("%Y-%m-%d %H:%M:%S")
                if (is_legacy_leg1 and match.get("min_t"))
                else dep_dt.strftime("%Y-%m-%d %H:%M:%S")
            )
            cur.execute(
                f"""
                UPDATE `{dst_db}`.`shipments`
                SET device_id = COALESCE(%s, device_id),
                    run_id = %s,
                    departed_at = %s,
                    gps_points_cnt = %s,
                    avg_temp = %s,
                    max_g_force = %s
                WHERE shipment_id = %s
                """,
                (
                    match["device_id"],
                    match["run_id"],
                    new_dep,
                    int(match["cnt"]),
                    round(float(match["avg_t"]), 2) if match["avg_t"] is not None else None,
                    round(float(match["max_g"]), 2) if match["max_g"] is not None else None,
                    sh_id,
                ),
            )
            if is_legacy_leg1 and match.get("min_t"):
                cur.execute(
                    f"""
                    UPDATE `{dst_db}`.`stage_events`
                    SET event_at = %s
                    WHERE lot_id = %s AND stage_code = 'A02'
                    """,
                    (new_dep, sh_lot_id),
                )


def upsert_sensor_packet_v2(cur, record: dict, dst_db: str = "lab225_v2", refresh_stats: bool = True):
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
    elif "보관" in r_low or "storage" in r_low or "창고" in r_low:
        init_type = "STORAGE"
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
            run_type = IF(run_type = 'NOISE' AND VALUES(valid_gps_cnt) > 0, 'FIELD_DRIVE', run_type),
            started_at = LEAST(IFNULL(started_at, VALUES(started_at)), VALUES(started_at)),
            ended_at = GREATEST(IFNULL(ended_at, VALUES(ended_at)), VALUES(ended_at))
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
            gps_state = VALUES(gps_state),
            event_type = VALUES(event_type),
            raw_status = VALUES(raw_status)
        """,
        (run_id, norm_dev, meas_str, temp, humi, lux, g_force, speed, lat, lng, gps_state, event_type, raw_status),
    )

    if refresh_stats:
        refresh_run_stats_v2(cur, run_id, dst_db=dst_db)


def _close_shipment_leg(cur, dst_db: str, leg_no: int, lot_id: str, pkg_id, dev, arr_dt: datetime, dep_dt_hint=None):
    """운송 구간(leg_no=1,2,3)의 출발~도착 주행 궤적을 매칭하고 ARRIVED로 마감합니다."""
    dep_dt = dep_dt_hint
    if not dep_dt:
        if pkg_id:
            cur.execute(
                f"SELECT departed_at, device_id FROM `{dst_db}`.`shipments` WHERE lot_id = %s AND pkg_id = %s AND leg_no = %s LIMIT 1",
                (lot_id, pkg_id, leg_no),
            )
        else:
            cur.execute(
                f"SELECT departed_at, device_id FROM `{dst_db}`.`shipments` WHERE lot_id = %s AND pkg_id IS NULL AND leg_no = %s LIMIT 1",
                (lot_id, leg_no),
            )
        sh_prev = cur.fetchone()
        if sh_prev:
            dep_dt = parse_dt_safe(sh_prev.get("departed_at"))
            if not dev and sh_prev.get("device_id"):
                dev = sh_prev["device_id"]

    is_legacy_leg1 = (leg_no == 1 and not is_modern_lot_id(lot_id))
    if not dep_dt:
        dep_dt = arr_dt - timedelta(hours=2 if leg_no > 1 else 1)

    if is_legacy_leg1:
        win_s = (arr_dt - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        win_e = arr_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        win_s = (dep_dt - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
        win_e = (arr_dt + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")

    seg = _match_drive_segment(cur, dst_db, dev, win_s, win_e, prefer_latest=is_legacy_leg1)
    final_dep = (
        seg["min_t"].strftime("%Y-%m-%d %H:%M:%S")
        if (is_legacy_leg1 and seg and seg.get("min_t"))
        else dep_dt.strftime("%Y-%m-%d %H:%M:%S")
    )
    arr_str = arr_dt.strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        f"""
        INSERT INTO `{dst_db}`.`shipments`
            (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status, gps_points_cnt, avg_temp, max_g_force)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            device_id = COALESCE(VALUES(device_id), device_id),
            run_id = COALESCE(VALUES(run_id), run_id),
            departed_at = IF(VALUES(departed_at) IS NOT NULL, LEAST(departed_at, VALUES(arrived_at)), departed_at),
            arrived_at = VALUES(arrived_at),
            status = 'ARRIVED',
            gps_points_cnt = IF(VALUES(gps_points_cnt) > 0, VALUES(gps_points_cnt), gps_points_cnt),
            avg_temp = COALESCE(VALUES(avg_temp), avg_temp),
            max_g_force = COALESCE(VALUES(max_g_force), max_g_force)
        """,
        (
            leg_no,
            lot_id,
            pkg_id,
            (seg["device_id"] if seg else dev),
            (seg["run_id"] if seg else None),
            final_dep,
            arr_str,
            int(seg["cnt"]) if seg else 0,
            round(float(seg["avg_t"]), 2) if (seg and seg["avg_t"] is not None) else None,
            round(float(seg["max_g"]), 2) if (seg and seg["max_g"] is not None) else None,
        ),
    )
    if is_legacy_leg1 and seg and seg.get("min_t"):
        cur.execute(
            f"UPDATE `{dst_db}`.`stage_events` SET event_at = %s WHERE lot_id = %s AND stage_code = 'A02'",
            (final_dep, lot_id),
        )


def apply_qr_row_to_v2(cur, row: dict, dst_db: str = "lab225_v2"):
    """`lab225.qr`에 INSERT된 스캔/생성 1개 행을 `lab225_v2` 정규화 테이블로 분배(멱등, v3 + v2 호환)"""
    raw_lot_id = str(row.get("LotID") or "").strip()
    raw_fmid = str(row.get("FmID") or "").strip()
    lot_id = raw_lot_id if raw_lot_id else raw_fmid
    stage = str(row.get("Lo") or "").strip().upper()
    if not lot_id or not stage:
        return

    now_kst = get_kst_now()
    parsed16 = parse_lot_id_16(lot_id)
    proto_ver = detect_protocol_version(lot_id, [stage])

    frt = unquote_plus(str(row.get("FrT") or (parsed16["fruit_type"] if parsed16 else "Apples"))).strip() or "Apples"
    vt = unquote_plus(str(row.get("Vt") or "Fuji Apple")).strip() or "Fuji Apple"
    mt = unquote_plus(str(row.get("Mt") or "Organic")).strip() or "Organic"
    ac = str(row.get("AC") or (parsed16["area_code"] if parsed16 else "55630")).strip() or "55630"
    farmer_code = raw_fmid or (parsed16["farmer_code"] if parsed16 else lot_id[:10])
    crop_code = str(row.get("CropCode") or (parsed16["crop_code"] if parsed16 else get_crop_code(frt, vt))).strip()
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

    hd_dt = parse_dt_safe(row.get("HD")) or (
        parse_dt_safe(parsed16["harvest_date_iso"]) if parsed16 else now_kst
    )
    std_dt = parse_dt_safe(row.get("Farm_StD") or row.get("Std") or row.get("StD"))
    dd_dt = parse_dt_safe(row.get("Farm_DD") or row.get("DD"))

    try:
        lat_v = float(row.get("Lat")) if row.get("Lat") not in (None, "", "None") else None
        lng_v = float(row.get("lon")) if row.get("lon") not in (None, "", "None") else None
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

    raw_pkg_grade = str(row.get("pkg_grade") or "").strip()

    # 원물 마스터(harvest_lots) 진행 단계 계산
    if proto_ver == "v4":
        raw_stage_set = {"A01", "A02", "A03", "A04", "B01", "B02"}
        if stage in raw_stage_set:
            init_lot_stage = stage
            update_lot_stage = True
        else:
            init_lot_stage = "B02"
            update_lot_stage = False
    elif proto_ver == "v3":
        raw_stage_set = {"A00", "A01", "A02", "B10", "B11"}
        if stage in raw_stage_set or (stage == "B12" and not raw_pkg_grade):
            init_lot_stage = stage
            update_lot_stage = True
        else:
            init_lot_stage = "B11"
            update_lot_stage = False
    else:
        init_lot_stage = "A02" if stage == "A00" else (stage if stage in ("A10", "A11", "A12") else "A12")
        update_lot_stage = stage in ("A10", "A11", "A12")

    cur.execute(
        f"""
        INSERT INTO `{dst_db}`.`harvest_lots`
            (lot_id, origin_zip, farmer_code, crop_code, fruit_type, variety, farmer_phone, cultivation,
             harvest_no, total_qty, harvest_date, storage_date, deliver_date,
             ag_practice, current_stage, protocol_ver, is_test, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
        ON DUPLICATE KEY UPDATE
            farmer_code = COALESCE(VALUES(farmer_code), farmer_code),
            crop_code = COALESCE(VALUES(crop_code), crop_code),
            current_stage = IF(%s = 1, %s, current_stage),
            protocol_ver = IF(VALUES(protocol_ver) = 'v4', 'v4', IF(VALUES(protocol_ver) = 'v3' AND protocol_ver != 'v4', 'v3', protocol_ver)),
            is_test = 0
        """,
        (
            lot_id,
            ac,
            farmer_code,
            crop_code,
            frt,
            vt,
            ct,
            mt,
            hn,
            qt,
            hd_dt.strftime("%Y-%m-%d") if hd_dt else None,
            std_dt.strftime("%Y-%m-%d") if std_dt else None,
            dd_dt.strftime("%Y-%m-%d") if dd_dt else None,
            rp,
            init_lot_stage,
            proto_ver,
            (hd_dt or now_kst).strftime("%Y-%m-%d %H:%M:%S"),
            1 if update_lot_stage else 0,
            stage,
        ),
    )

    # =========================================================================
    # 0. v4 최신 공급망 (17자리 LotID, 3자리 FmID, A01~A04 -> B01~B05 -> C10~D10)
    # =========================================================================
    if proto_ver == "v4":
        if stage == "A01":
            # 농가 수확 (무색 QR 최초 발급)
            ev_dt = hd_dt or now_kst
            h_a01 = make_sha256({"lot_id": lot_id, "stage": "A01", "ac": ac, "fm": farmer_code, "cc": crop_code, "qt": qt, "hd": ev_dt.strftime("%Y-%m-%d")})
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
                VALUES (%s, NULL, 'A01', %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), tx_hash = COALESCE(tx_hash, VALUES(tx_hash))
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, h_a01),
            )

        elif stage == "A02":
            # 농가 저장고 들어감 (선택)
            ev_dt = parse_dt_safe(row.get("Farm_StD")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi)
                VALUES (%s, NULL, 'A02', %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    event_at = VALUES(event_at),
                    lat = COALESCE(VALUES(lat), lat),
                    lng = COALESCE(VALUES(lng), lng),
                    temp = COALESCE(VALUES(temp), temp),
                    humi = COALESCE(VALUES(humi), humi)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, tp_v, hm_v),
            )
            cur.execute(
                f"UPDATE `{dst_db}`.`harvest_lots` SET storage_date = %s, current_stage = 'A02' WHERE lot_id = %s",
                (ev_dt.strftime("%Y-%m-%d"), lot_id),
            )

        elif stage == "A03":
            # 농가 저장고 나옴 (선택)
            p_a02 = parse_dt_safe(row.get("Farm_StD"))
            if p_a02:
                cur.execute(
                    f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, NULL, 'A02', %s)",
                    (lot_id, p_a02.strftime("%Y-%m-%d %H:%M:%S")),
                )
            ev_dt = parse_dt_safe(row.get("Farm_StOut")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi)
                VALUES (%s, NULL, 'A03', %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    event_at = VALUES(event_at),
                    lat = COALESCE(VALUES(lat), lat),
                    lng = COALESCE(VALUES(lng), lng),
                    temp = COALESCE(VALUES(temp), temp),
                    humi = COALESCE(VALUES(humi), humi)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, tp_v, hm_v),
            )
            cur.execute(f"UPDATE `{dst_db}`.`harvest_lots` SET current_stage = 'A03' WHERE lot_id = %s", (lot_id,))

        elif stage == "A04":
            # 농가 출하 · APC로 출발 (1구간 운송 시작)
            for prev_cd, prev_col in (("A02", "Farm_StD"), ("A03", "Farm_StOut")):
                p_dt = parse_dt_safe(row.get(prev_col))
                if p_dt:
                    cur.execute(
                        f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, NULL, %s, %s)",
                        (lot_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                    )
            ev_dt = parse_dt_safe(row.get("Farm_DD")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng)
                VALUES (%s, NULL, 'A04', %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), lat = COALESCE(VALUES(lat), lat), lng = COALESCE(VALUES(lng), lng)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v),
            )
            cur.execute(
                f"UPDATE `{dst_db}`.`harvest_lots` SET deliver_date = %s, current_stage = 'A04' WHERE lot_id = %s",
                (ev_dt.strftime("%Y-%m-%d"), lot_id),
            )
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`shipments` (leg_no, lot_id, pkg_id, device_id, departed_at, status)
                VALUES (1, %s, NULL, %s, %s, 'IN_TRANSIT')
                ON DUPLICATE KEY UPDATE
                    device_id = COALESCE(VALUES(device_id), device_id),
                    departed_at = VALUES(departed_at)
                """,
                (lot_id, dev, ev_dt.strftime("%Y-%m-%d %H:%M:%S")),
            )

        elif stage == "B01":
            # APC 입고 (1구간 운송 ARRIVED 마감)
            for prev_cd, prev_col in (("A02", "Farm_StD"), ("A03", "Farm_StOut"), ("A04", "Farm_DD")):
                p_dt = parse_dt_safe(row.get(prev_col))
                if p_dt:
                    cur.execute(
                        f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, NULL, %s, %s)",
                        (lot_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                    )
            ev_dt = parse_dt_safe(row.get("APC_AD")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng)
                VALUES (%s, NULL, 'B01', %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), lat = COALESCE(VALUES(lat), lat), lng = COALESCE(VALUES(lng), lng)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v),
            )
            _close_shipment_leg(cur, dst_db, 1, lot_id, None, dev, ev_dt, dep_dt_hint=parse_dt_safe(row.get("Farm_DD")))

        elif stage == "B02":
            # APC 선별 (유색 QR 3종 변경 및 등급 배분)
            ev_dt = parse_dt_safe(row.get("APC_RT")) or now_kst
            a_q = int(float(str(row.get("AGrade") or "0").strip() or 0))
            b_q = int(float(str(row.get("BGrade") or "0").strip() or 0))
            c_q = int(float(str(row.get("CGrade") or "0").strip() or 0))
            d_q = int(float(str(row.get("DefectRate") or "0").strip() or 0))

            for p_id, g_cd, g_ko, g_q, ship, st_c in [
                (f"{lot_id}-A", "A", "상", a_q, 1, "B02"),
                (f"{lot_id}-B", "B", "중", b_q, 1, "B02"),
                (f"{lot_id}-C", "C", "하", c_q, 1, "B02"),
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

            h_b02 = make_sha256({"lot_id": lot_id, "stage": "B02", "A": a_q, "B": b_q, "C": c_q, "DEFECT": d_q, "rt": ev_dt.strftime("%Y-%m-%d %H:%M:%S")})
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
                VALUES (%s, NULL, 'B02', %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), tx_hash = COALESCE(tx_hash, VALUES(tx_hash))
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, h_b02),
            )

        elif stage in ("B03", "B04", "B05", "C10", "C11", "D10"):
            # 유색 QR 등급별 독립 공정 (APC 저장고 입/출고 B03/B04 -> APC 출하 B05 -> 유통 C10/C11 -> 판매처 D10)
            g_code, g_ko = normalize_pkg_grade(raw_pkg_grade or "A")
            pkg_id = f"{lot_id}-{g_code}"
            grade_col_map = {"A": "AGrade", "B": "BGrade", "C": "CGrade"}
            try:
                g_qty_val = int(float(str(row.get(grade_col_map[g_code]) or qt or 0).strip()))
            except Exception:
                g_qty_val = qt

            cur.execute(
                f"""
                INSERT IGNORE INTO `{dst_db}`.`sorted_lots`
                    (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
                VALUES (%s, %s, %s, %s, %s, 1, %s, %s)
                """,
                (pkg_id, lot_id, g_code, g_ko, g_qty_val, stage, now_kst.strftime("%Y-%m-%d %H:%M:%S")),
            )
            cur.execute(f"UPDATE `{dst_db}`.`sorted_lots` SET current_stage = %s WHERE pkg_id = %s", (stage, pkg_id))

            col_map = {
                "B03": "APC_StD",
                "B04": "APC_StOut",
                "B05": "APC_OP",
                "C10": "Dist_StD",
                "C11": "Dist_OP",
                "D10": "Retail_AD",
            }
            ev_dt = parse_dt_safe(row.get(col_map[stage])) or now_kst
            h_val = (
                make_sha256({"lot_id": lot_id, "pkg_id": pkg_id, "stage": "D10", "at": ev_dt.strftime("%Y-%m-%d %H:%M:%S")})
                if stage == "D10"
                else None
            )
            store_env = stage in ("B03", "B04", "C10")

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
                    lot_id,
                    pkg_id,
                    stage,
                    ev_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    lat_v,
                    lng_v,
                    tp_v if store_env else None,
                    hm_v if store_env else None,
                    h_val,
                ),
            )

            if stage == "B04":
                p_b03 = parse_dt_safe(row.get("APC_StD"))
                if p_b03:
                    cur.execute(
                        f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, %s, 'B03', %s)",
                        (lot_id, pkg_id, p_b03.strftime("%Y-%m-%d %H:%M:%S")),
                    )
            elif stage == "B05":
                for prev_cd, prev_col in (("B03", "APC_StD"), ("B04", "APC_StOut")):
                    p_dt = parse_dt_safe(row.get(prev_col))
                    if p_dt:
                        cur.execute(
                            f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, %s, %s, %s)",
                            (lot_id, pkg_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                        )
                # 2구간 운송 시작 (APC 출하 -> 유통 창고)
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
            elif stage == "C10":
                for prev_cd, prev_col in (("B03", "APC_StD"), ("B04", "APC_StOut"), ("B05", "APC_OP")):
                    p_dt = parse_dt_safe(row.get(prev_col))
                    if p_dt:
                        cur.execute(
                            f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, %s, %s, %s)",
                            (lot_id, pkg_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                        )
                _close_shipment_leg(cur, dst_db, 2, lot_id, pkg_id, dev, ev_dt, dep_dt_hint=parse_dt_safe(row.get("APC_OP")))
            elif stage == "C11":
                for prev_cd, prev_col in (("B05", "APC_OP"), ("C10", "Dist_StD")):
                    p_dt = parse_dt_safe(row.get(prev_col))
                    if p_dt:
                        cur.execute(
                            f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, %s, %s, %s)",
                            (lot_id, pkg_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                        )
                cur.execute(
                    f"""
                    INSERT INTO `{dst_db}`.`shipments` (leg_no, lot_id, pkg_id, device_id, departed_at, status)
                    VALUES (3, %s, %s, %s, %s, 'IN_TRANSIT')
                    ON DUPLICATE KEY UPDATE
                        device_id = COALESCE(VALUES(device_id), device_id),
                        departed_at = VALUES(departed_at)
                    """,
                    (lot_id, pkg_id, dev, ev_dt.strftime("%Y-%m-%d %H:%M:%S")),
                )
            elif stage == "D10":
                for prev_cd, prev_col in (("B05", "APC_OP"), ("C10", "Dist_StD"), ("C11", "Dist_OP")):
                    p_dt = parse_dt_safe(row.get(prev_col))
                    if p_dt:
                        cur.execute(
                            f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, %s, %s, %s)",
                            (lot_id, pkg_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                        )
                dep3_hint = parse_dt_safe(row.get("Dist_OP")) or parse_dt_safe(row.get("APC_OP"))
                _close_shipment_leg(cur, dst_db, 3, lot_id, pkg_id, dev, ev_dt, dep_dt_hint=dep3_hint)
        return

    # =========================================================================
    # A. v3 레거시 공급망 (16자리, A00 ~ D10 하위 호환 보존)
    # =========================================================================
    if proto_ver == "v3":
        if stage == "A00":
            ev_dt = hd_dt or now_kst
            h_a00 = make_sha256({"lot_id": lot_id, "stage": "A00", "ac": ac, "cc": crop_code, "qt": qt, "hd": ev_dt.strftime("%Y-%m-%d")})
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
                VALUES (%s, NULL, 'A00', %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), tx_hash = COALESCE(tx_hash, VALUES(tx_hash))
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, h_a00),
            )

        elif stage == "A01":
            # 농가 창고 (QR 스캐너 스캔, 선택 단계)
            ev_dt = parse_dt_safe(row.get("Farm_StD")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi)
                VALUES (%s, NULL, 'A01', %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    event_at = VALUES(event_at),
                    lat = COALESCE(VALUES(lat), lat),
                    lng = COALESCE(VALUES(lng), lng),
                    temp = COALESCE(VALUES(temp), temp),
                    humi = COALESCE(VALUES(humi), humi)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, tp_v, hm_v),
            )
            cur.execute(
                f"UPDATE `{dst_db}`.`harvest_lots` SET storage_date = %s, current_stage = 'A01' WHERE lot_id = %s",
                (ev_dt.strftime("%Y-%m-%d"), lot_id),
            )

        elif stage == "A02":
            # 농가 출하 (QR 스캐너 스캔 -> 1구간 운송 시작)
            ev_dt = parse_dt_safe(row.get("Farm_DD")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng)
                VALUES (%s, NULL, 'A02', %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), lat = COALESCE(VALUES(lat), lat), lng = COALESCE(VALUES(lng), lng)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v),
            )
            cur.execute(
                f"UPDATE `{dst_db}`.`harvest_lots` SET deliver_date = %s, current_stage = 'A02' WHERE lot_id = %s",
                (ev_dt.strftime("%Y-%m-%d"), lot_id),
            )
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`shipments` (leg_no, lot_id, pkg_id, device_id, departed_at, status)
                VALUES (1, %s, NULL, %s, %s, 'IN_TRANSIT')
                ON DUPLICATE KEY UPDATE
                    device_id = COALESCE(VALUES(device_id), device_id),
                    departed_at = VALUES(departed_at)
                """,
                (lot_id, dev, ev_dt.strftime("%Y-%m-%d %H:%M:%S")),
            )

        elif stage == "B10":
            # 선행 농가 스캔(A01/A02) 시각이 행에 있으면 누락 방어 보완
            for prev_cd, prev_col in (("A01", "Farm_StD"), ("A02", "Farm_DD")):
                p_dt = parse_dt_safe(row.get(prev_col))
                if p_dt:
                    cur.execute(
                        f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, NULL, %s, %s)",
                        (lot_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                    )
            # APC 입고 (1구간 운송 ARRIVED 마감)
            ev_dt = parse_dt_safe(row.get("APC_AD")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng)
                VALUES (%s, NULL, 'B10', %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), lat = COALESCE(VALUES(lat), lat), lng = COALESCE(VALUES(lng), lng)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v),
            )
            _close_shipment_leg(cur, dst_db, 1, lot_id, None, dev, ev_dt, dep_dt_hint=parse_dt_safe(row.get("Farm_DD")))

        elif stage == "B11":
            # APC 선별 (유색 QR 3종 변경 및 등급 배분)
            ev_dt = parse_dt_safe(row.get("APC_RT")) or now_kst
            a_q = int(float(str(row.get("AGrade") or "0").strip() or 0))
            b_q = int(float(str(row.get("BGrade") or "0").strip() or 0))
            c_q = int(float(str(row.get("CGrade") or "0").strip() or 0))
            d_q = int(float(str(row.get("DefectRate") or "0").strip() or 0))

            for p_id, g_cd, g_ko, g_q, ship, st_c in [
                (f"{lot_id}-A", "A", "상", a_q, 1, "B11"),
                (f"{lot_id}-B", "B", "중", b_q, 1, "B11"),
                (f"{lot_id}-C", "C", "하", c_q, 1, "B11"),
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

            h_b11 = make_sha256({"lot_id": lot_id, "stage": "B11", "A": a_q, "B": b_q, "C": c_q, "DEFECT": d_q, "rt": ev_dt.strftime("%Y-%m-%d %H:%M:%S")})
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
                VALUES (%s, NULL, 'B11', %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE event_at = VALUES(event_at), tx_hash = COALESCE(tx_hash, VALUES(tx_hash))
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, h_b11),
            )

        elif stage == "B12" and not raw_pkg_grade:
            # APC 창고 (선별 전: 무색 QR로 B10 이후 저장)
            ev_dt = parse_dt_safe(row.get("APC_StD")) or now_kst
            cur.execute(
                f"""
                INSERT INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi)
                VALUES (%s, NULL, 'B12', %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    event_at = VALUES(event_at),
                    lat = COALESCE(VALUES(lat), lat),
                    lng = COALESCE(VALUES(lng), lng),
                    temp = COALESCE(VALUES(temp), temp),
                    humi = COALESCE(VALUES(humi), humi)
                """,
                (lot_id, ev_dt.strftime("%Y-%m-%d %H:%M:%S"), lat_v, lng_v, tp_v, hm_v),
            )

        elif stage in ("B12", "B13", "C10", "C11", "D10"):
            # 유색 QR 등급별 독립 공정 (선별 후 B12 / B13 / C10 / C11 / D10)
            g_code, g_ko = normalize_pkg_grade(raw_pkg_grade or "A")
            pkg_id = f"{lot_id}-{g_code}"
            grade_col_map = {"A": "AGrade", "B": "BGrade", "C": "CGrade"}
            try:
                g_qty_val = int(float(str(row.get(grade_col_map[g_code]) or qt or 0).strip()))
            except Exception:
                g_qty_val = qt

            cur.execute(
                f"""
                INSERT IGNORE INTO `{dst_db}`.`sorted_lots`
                    (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
                VALUES (%s, %s, %s, %s, %s, 1, %s, %s)
                """,
                (pkg_id, lot_id, g_code, g_ko, g_qty_val, stage, now_kst.strftime("%Y-%m-%d %H:%M:%S")),
            )
            cur.execute(f"UPDATE `{dst_db}`.`sorted_lots` SET current_stage = %s WHERE pkg_id = %s", (stage, pkg_id))

            col_map = {
                "B12": "APC_StD",
                "B13": "APC_OP",
                "C10": "Dist_StD",
                "C11": "Dist_OP",
                "D10": "Retail_AD",
            }
            ev_dt = parse_dt_safe(row.get(col_map[stage])) or now_kst
            h_val = (
                make_sha256({"lot_id": lot_id, "pkg_id": pkg_id, "stage": "D10", "at": ev_dt.strftime("%Y-%m-%d %H:%M:%S")})
                if stage == "D10"
                else None
            )
            store_env = stage in ("B12", "C10")

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
                    lot_id,
                    pkg_id,
                    stage,
                    ev_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    lat_v,
                    lng_v,
                    tp_v if store_env else None,
                    hm_v if store_env else None,
                    h_val,
                ),
            )

            if stage == "B13":
                # 2구간 운송 시작 (APC 출하 -> 유통 창고)
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
            elif stage == "C10":
                # B13 시각(APC_OP)이 행에 포함되어 있으면 누락 방어 보완
                b13_dt = parse_dt_safe(row.get("APC_OP"))
                if b13_dt:
                    cur.execute(
                        f"""
                        INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at)
                        VALUES (%s, %s, 'B13', %s)
                        """,
                        (lot_id, pkg_id, b13_dt.strftime("%Y-%m-%d %H:%M:%S")),
                    )
                # 2구간 운송 도착 마감 (유통 창고 도착)
                _close_shipment_leg(cur, dst_db, 2, lot_id, pkg_id, dev, ev_dt, dep_dt_hint=b13_dt)
            elif stage == "C11":
                for prev_cd, prev_col in (("B13", "APC_OP"), ("C10", "Dist_StD")):
                    p_dt = parse_dt_safe(row.get(prev_col))
                    if p_dt:
                        cur.execute(
                            f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, %s, %s, %s)",
                            (lot_id, pkg_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                        )
                # 3구간 운송 시작 (유통 출하 -> 판매처 출발)
                cur.execute(
                    f"""
                    INSERT INTO `{dst_db}`.`shipments` (leg_no, lot_id, pkg_id, device_id, departed_at, status)
                    VALUES (3, %s, %s, %s, %s, 'IN_TRANSIT')
                    ON DUPLICATE KEY UPDATE
                        device_id = COALESCE(VALUES(device_id), device_id),
                        departed_at = VALUES(departed_at)
                    """,
                    (lot_id, pkg_id, dev, ev_dt.strftime("%Y-%m-%d %H:%M:%S")),
                )
            elif stage == "D10":
                for prev_cd, prev_col in (("B13", "APC_OP"), ("C10", "Dist_StD"), ("C11", "Dist_OP")):
                    p_dt = parse_dt_safe(row.get(prev_col))
                    if p_dt:
                        cur.execute(
                            f"INSERT IGNORE INTO `{dst_db}`.`stage_events` (lot_id, pkg_id, stage_code, event_at) VALUES (%s, %s, %s, %s)",
                            (lot_id, pkg_id, prev_cd, p_dt.strftime("%Y-%m-%d %H:%M:%S")),
                        )
                # 3구간 운송 도착 마감 (판매처 도착)
                dep3_hint = parse_dt_safe(row.get("Dist_OP")) or parse_dt_safe(row.get("APC_OP"))
                _close_shipment_leg(cur, dst_db, 3, lot_id, pkg_id, dev, ev_dt, dep_dt_hint=dep3_hint)
        return

    # =========================================================================
    # B. 레거시 v2 공급망 (A00 ~ A16 하위 호환 보존)
    # =========================================================================
    if stage == "A00":
        dt_a00 = datetime(hd_dt.year, hd_dt.month, hd_dt.day, 0, 0, 0)
        std_use = std_dt or hd_dt
        dd_use = dd_dt or hd_dt
        dt_a01 = datetime(std_use.year, std_use.month, std_use.day, 0, 0, 0)
        dt_a02 = datetime(dd_use.year, dd_use.month, dd_use.day, 0, 0, 0)
        h_a00 = make_sha256({"lot_id": lot_id, "stage": "A00", "ac": ac, "qt": qt, "hd": dt_a00.strftime("%Y-%m-%d")})

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
            (lot_id, dev, now_kst.strftime("%Y-%m-%d %H:%M:%S")),
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
        _close_shipment_leg(cur, dst_db, 1, lot_id, None, dev, ev_dt)

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
        g_code, g_ko = normalize_pkg_grade(row.get("pkg_grade"))
        pkg_id = f"{lot_id}-{g_code}"
        grade_col_map = {"A": "AGrade", "B": "BGrade", "C": "CGrade"}
        try:
            g_qty_val = int(float(str(row.get(grade_col_map[g_code]) or qt or 0).strip()))
        except Exception:
            g_qty_val = qt

        cur.execute(
            f"""
            INSERT IGNORE INTO `{dst_db}`.`sorted_lots`
                (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
            VALUES (%s, %s, %s, %s, %s, 1, %s, %s)
            """,
            (pkg_id, lot_id, g_code, g_ko, g_qty_val, stage, now_kst.strftime("%Y-%m-%d %H:%M:%S")),
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
            _close_shipment_leg(cur, dst_db, 2, lot_id, pkg_id, dev, ev_dt, dep_dt_hint=parse_dt_safe(row.get("APC_OP")))


def sync_v1_delta_to_v2(conn, src_db: str = "lab225", dst_db: str = "lab225_v2") -> dict:
    """
    `lab225`에 새로 쌓인 센서 패킷 및 ESP32 스캐너 QR 행(`id > last_id`)만 초고속 증분 동기화!
    """
    synced_sensors = 0
    synced_qr = 0
    touched_runs = set()
    with conn.cursor() as cur:
        cur.execute("SET SESSION sql_mode = ''")
        cur.execute(f"SELECT source_table, last_id FROM `{dst_db}`.`_sync_watermark`")
        wm = {r["source_table"]: int(r["last_id"] or 0) for r in cur.fetchall()}
        last_sd_id = wm.get("sensor_data", 0)
        last_qr_id = wm.get("qr", 0)

        # 1) 신규 센서 패킷 먼저 동기화
        cur.execute(
            f"SELECT * FROM `{src_db}`.`sensor_data` WHERE id > %s ORDER BY id ASC LIMIT 2500",
            (last_sd_id,),
        )
        new_sd_rows = cur.fetchall()
        if new_sd_rows:
            for s_row in new_sd_rows:
                upsert_sensor_packet_v2(cur, s_row, dst_db=dst_db, refresh_stats=False)
                r_id = str(s_row.get("run_id") or "default_run").strip() or "default_run"
                touched_runs.add(r_id)
            for r_id in touched_runs:
                refresh_run_stats_v2(cur, r_id, dst_db=dst_db)
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

        # 3) shipments 요약 통계 자동 보정
        if synced_sensors or synced_qr:
            refresh_shipment_stats_v2(cur, dst_db=dst_db)

    if synced_sensors or synced_qr:
        conn.commit()
    return {"synced_sensors": synced_sensors, "synced_qr": synced_qr}
