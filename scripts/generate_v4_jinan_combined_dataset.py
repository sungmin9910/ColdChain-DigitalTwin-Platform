"""
ColdChain DigitalTwin Platform - Supply Chain v4 Combined Experimental Dataset Builder
--------------------------------------------------------------------------------------
목적:
  센서 기기가 없는 상태에서 기존 AWS RDS 실측 자산(장거리 도로 주행 GPS/속도/충격 +
  항온항습 챔버 저온 실측 온습도)을 결합하여 Supply Chain v4(17자리 LotID, A01~D01 13단계,
  상/중/하 전 등급, 3구간 운송) 정상 콜드체인 실험 데이터를 비파괴적으로 생성·적재합니다.

안전 원칙:
  1. 기존 로트(v2/v3), 기존 주행/보관 세션, 진행 중인 실시간 데이터는 절대 수정·삭제하지 않음.
  2. 신규 17자리 LotID(55451071411261123/24/25)와 신규 비중복 run_id만 INSERT(멱등) 적재.
  3. carrier-c6-02(truck02)의 기존 타임스탬프(11/22, 11/25 12:11~11/26 14:58)와
     단 1초도 겹치지 않는 시간 윈도우만 사용.

데이터 출처 (100% RDS 실측 기반):
  - GPS / 속도 / 충격 / 조도: lab225_v2.sensor_telemetry
      run_id = 'truck04_주행_2026-10-20_15시27분' (1,518건, 전북 진안 인근 -> 경남 -> 부산 실주행)
      ※ 정상 콜드체인 유지 시나리오를 위해 비주행 충격 스파이크(>=1.8G, 2건)만 직전 정상값으로 완화.
  - 온도 / 습도: lab225_v2.chamber_calibration_logs
      저온 실측 구간(1.5~3.9°C, carrier-c6-02 & carrier-c6-03, 2026-11-27~28)의 실측 온도 시계열을
      그대로 사용하고, 실측 습도 변동 패턴은 사과 저온저장 적정 RH(85~89%) 중심값으로 평행 보정.

사용법:
  python scripts/generate_v4_jinan_combined_dataset.py --dry-run
  python scripts/generate_v4_jinan_combined_dataset.py --apply
  python scripts/generate_v4_jinan_combined_dataset.py --verify
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
import pymysql

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cloud_backend.db_v2.bridge_sync import make_sha256, refresh_run_stats_v2
from cloud_backend.supply_chain_spec import build_lot_id_17

DB_HOST = os.getenv("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))
DB_USER = os.getenv("MYSQL_USER", "admin")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "12345678")
DB_V2 = os.getenv("MYSQL_V2_DATABASE", "lab225_v2")

SOURCE_DRIVE_RUN_ID = "truck04_주행_2026-10-20_15시27분"
TARGET_DEVICE_ID = "carrier-c6-02"  # 관제 2호차 (truck02)

# 1,518개 실주행 포인트 3구간 분할 인덱스 (진안 -> 함양/산청 APC -> 창원/경남 유통창고 -> 부산 판매처)
# idx 0    : 35.7694, 127.3610 (전북 진안군 마령면 인근 출발)
# idx 101  : 35.5510, 127.7590 (1구간 도착 / APC 거점, 약 44분)
# idx 707  : 35.2798, 128.6250 (2구간 도착 / 유통창고 거점, 약 1시간 40분)
# idx 1517 : 35.1623, 129.1580 (3구간 도착 / 부산 판매처, 약 1시간 46분)
LEG_SLICES = [
    (1, 0, 102),      # Leg 1: idx 0..101 (102 pts)
    (2, 101, 708),    # Leg 2: idx 101..707 (607 pts, 끝점-시작점 연속 연결)
    (3, 707, 1518),   # Leg 3: idx 707..1517 (811 pts, 끝점-시작점 연속 연결)
]

# 3개 로트 정의 (진안 마령면 55451, 농가 071, 사과/홍로 411, 총 500상자, 1~3회차)
# 기존 carrier-c6-02 세션(11/22, 11/25 12:11 ~ 11/26 14:58)과 시간 중복이 전혀 없도록 배치
LOT_SPECS = [
    {
        "area_code": "55451",  # 전북 진안군 (마령면)
        "farmer_code": "071",
        "fruit_type": "Apples",
        "variety": "Hongro Apple",
        "crop_code": "411",
        "farmer_phone": "010-7100-5451",
        "cultivation": "GAP",
        "harvest_no": 1,
        "total_qty": 500,
        "grades": {"A": 395, "B": 65, "C": 30, "DEFECT": 10},
        "harvest_date": "2026-11-23",
        "chamber_profile": {
            "device_id": "carrier-c6-03",
            "t_start": "2026-11-27 23:25:00",
            "t_end": "2026-11-28 00:15:00",
            "target_rh": 87.5,
        },
        "schedule": {
            "A01": "2026-11-23 08:30:00",
            "A02": "2026-11-23 09:30:00",
            "A03": "2026-11-24 07:30:00",
            "leg1_start": "2026-11-24 08:00:00",  # -> B01 ~ 08:44:17
            "B02": "2026-11-24 09:30:00",
            "B03": "2026-11-24 10:15:00",
            "B04": "2026-11-24 10:40:00",
            "B05": "2026-11-24 16:30:00",
            "leg2_start": "2026-11-24 17:00:00",  # -> C01 ~ 18:39:41
            "leg3_start": "2026-11-25 07:00:00",  # -> D01 ~ 08:46:25 (기존 11/25 12:11 세션 이전 완료)
        },
        "run_tag": "진안071_1차",
    },
    {
        "area_code": "55451",
        "farmer_code": "071",
        "fruit_type": "Apples",
        "variety": "Hongro Apple",
        "crop_code": "411",
        "farmer_phone": "010-7100-5451",
        "cultivation": "GAP",
        "harvest_no": 2,
        "total_qty": 500,
        "grades": {"A": 405, "B": 55, "C": 30, "DEFECT": 10},
        "harvest_date": "2026-11-24",
        "chamber_profile": {
            "device_id": "carrier-c6-03",
            "t_start": "2026-11-27 23:45:00",
            "t_end": "2026-11-28 00:18:00",
            "target_rh": 86.8,
        },
        "schedule": {
            "A01": "2026-11-24 09:00:00",
            "A02": "2026-11-24 10:00:00",
            "A03": "2026-11-26 15:30:00",  # 2일 저온저장 (기존 11/25~26 14:58 세션 이후 출고)
            "leg1_start": "2026-11-26 16:00:00",  # -> B01 ~ 16:44:17
            "B02": "2026-11-26 17:20:00",
            "B03": "2026-11-26 17:55:00",
            "B04": "2026-11-26 18:20:00",
            "B05": "2026-11-27 07:30:00",
            "leg2_start": "2026-11-27 08:00:00",  # -> C01 ~ 09:39:41
            "leg3_start": "2026-11-27 14:00:00",  # -> D01 ~ 15:46:25
        },
        "run_tag": "진안071_2차",
    },
    {
        "area_code": "55451",
        "farmer_code": "071",
        "fruit_type": "Apples",
        "variety": "Hongro Apple",
        "crop_code": "411",
        "farmer_phone": "010-7100-5451",
        "cultivation": "GAP",
        "harvest_no": 3,
        "total_qty": 500,
        "grades": {"A": 400, "B": 60, "C": 32, "DEFECT": 8},
        "harvest_date": "2026-11-25",
        "chamber_profile": {
            "device_id": "carrier-c6-02",
            "t_start": "2026-11-28 00:00:01",
            "t_end": "2026-11-28 00:42:00",
            "target_rh": 86.2,
        },
        "schedule": {
            "A01": "2026-11-25 08:30:00",
            "A02": "2026-11-25 09:30:00",
            "A03": "2026-11-27 16:30:00",  # 2일 저온저장 후 출고
            "leg1_start": "2026-11-27 17:00:00",  # -> B01 ~ 17:44:17
            "B02": "2026-11-27 18:20:00",
            "B03": "2026-11-27 18:50:00",
            "B04": "2026-11-27 19:15:00",
            "B05": "2026-11-28 06:30:00",
            "leg2_start": "2026-11-28 07:00:00",  # -> C01 ~ 08:39:41
            "leg3_start": "2026-11-28 11:30:00",  # -> D01 ~ 13:16:25
        },
        "run_tag": "진안071_3차",
    },
]

GRADE_LABELS = {"A": "상", "B": "중", "C": "하", "DEFECT": "결점과"}


def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_V2,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=15,
        autocommit=False,
    )


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def load_source_drive(cur):
    cur.execute(
        """
        SELECT measured_at, speed, g_force, lux, lat, lng, gps_state, raw_status
        FROM sensor_telemetry
        WHERE run_id = %s AND gps_state != 'INDOOR' AND lat != 0 AND lng != 0
        ORDER BY measured_at ASC, telemetry_id ASC
        """,
        (SOURCE_DRIVE_RUN_ID,),
    )
    rows = list(cur.fetchall())
    if len(rows) < 1500:
        raise RuntimeError(f"Expected >=1500 rows in {SOURCE_DRIVE_RUN_ID}, got {len(rows)}")
    return rows


def load_chamber_slice(cur, device_id: str, t_start: str, t_end: str, target_rh: float):
    cur.execute(
        """
        SELECT timestamp_kst, temperature, humidity
        FROM chamber_calibration_logs
        WHERE device_id = %s AND timestamp_kst >= %s AND timestamp_kst <= %s
          AND temperature BETWEEN 0.8 AND 4.5
        ORDER BY timestamp_kst ASC, id ASC
        """,
        (device_id, t_start, t_end),
    )
    rows = list(cur.fetchall())
    if len(rows) < 50:
        raise RuntimeError(f"Chamber slice too small for {device_id} [{t_start}..{t_end}]: {len(rows)}")
    avg_rh = sum(float(r["humidity"]) for r in rows) / len(rows)
    rh_offset = target_rh - avg_rh
    series = []
    for r in rows:
        t_val = round(float(r["temperature"]), 2)
        h_val = round(min(92.0, max(82.0, float(r["humidity"]) + rh_offset)), 1)
        series.append((t_val, h_val))
    return series


def sanitize_normal_g_force(raw_g: float) -> float:
    """정상 콜드체인 유지 시나리오: 실주행 미세 진동(1.0~1.55G)은 그대로 보존, 비주행 스파이크(>=1.8G)만 완화"""
    g = float(raw_g or 1.0)
    if g >= 1.8:
        return 1.32
    return round(g, 2)


def sanitize_normal_status(raw_status: str, g_val: float) -> str:
    s = str(raw_status or "")
    if "충격" in s or g_val >= 1.8:
        return "정상 [GPS FIX]"
    return s[:60] if s else "정상 [GPS FIX]"


def build_leg_packets(drive_slice: list, target_start: datetime, chamber_series: list, phase_offset: int):
    """실주행 슬라이스의 상대 시간 간격을 유지하며 목표 시작 시각으로 이동, 챔버 저온 온습도 결합"""
    base_t = drive_slice[0]["measured_at"]
    m = len(chamber_series)
    packets = []
    seen_ts = set()
    for i, r in enumerate(drive_slice):
        delta = r["measured_at"] - base_t
        new_dt = target_start + delta
        while new_dt in seen_ts:
            new_dt += timedelta(seconds=1)
        seen_ts.add(new_dt)
        temp_v, humi_v = chamber_series[(i + phase_offset) % m]
        g_v = sanitize_normal_g_force(r["g_force"])
        lux_v = round(min(float(r["lux"] or 0.0), 2.0), 1)  # 밀폐 냉장탑차 정상 암실 유지
        packets.append(
            {
                "measured_at": new_dt,
                "temperature": temp_v,
                "humidity": humi_v,
                "lux": lux_v,
                "g_force": g_v,
                "speed": round(float(r["speed"] or 0.0), 1),
                "lat": float(r["lat"]),
                "lng": float(r["lng"]),
                "gps_state": r["gps_state"] if r["gps_state"] in ("FIX", "TUNNEL") else "FIX",
                "event_type": "NORMAL",
                "raw_status": sanitize_normal_status(r["raw_status"], g_v),
            }
        )
    return packets


def check_existing_conflicts(cur, planned_lots: list, planned_runs: list):
    """기존 데이터 보호를 위해 carrier-c6-02의 기존 타 세션과의 시간 충돌 사전 검사"""
    planned_run_ids = {r["run_id"] for r in planned_runs}
    cur.execute(
        """
        SELECT run_id, started_at, ended_at
        FROM transport_runs
        WHERE device_id = %s AND run_type IN ('FIELD_DRIVE', 'STORAGE')
          AND started_at IS NOT NULL AND ended_at IS NOT NULL
        """,
        (TARGET_DEVICE_ID,),
    )
    existing_runs = [r for r in cur.fetchall() if r["run_id"] not in planned_run_ids]

    conflicts = []
    for pr in planned_runs:
        ps, pe = pr["started_at"], pr["ended_at"]
        for er in existing_runs:
            es, ee = er["started_at"], er["ended_at"]
            # 5분 안전 여유 포함 비중첩 확인
            if ps <= (ee + timedelta(minutes=5)) and pe >= (es - timedelta(minutes=5)):
                conflicts.append((pr["run_id"], ps, pe, er["run_id"], es, ee))
    return conflicts


def build_plan(cur):
    drive_rows = load_source_drive(cur)
    planned_lots = []
    planned_runs = []

    for lot_idx, spec in enumerate(LOT_SPECS):
        assert sum(spec["grades"].values()) == spec["total_qty"], "Grade sum != total_qty"
        lot_id = build_lot_id_17(
            spec["area_code"],
            spec["farmer_code"],
            spec["fruit_type"],
            spec["variety"],
            spec["harvest_date"],
            crop_code=spec["crop_code"],
        )
        cp = spec["chamber_profile"]
        chamber_series = load_chamber_slice(cur, cp["device_id"], cp["t_start"], cp["t_end"], cp["target_rh"])

        sch = spec["schedule"]
        leg_data = {}
        for leg_no, s_idx, e_idx in LEG_SLICES:
            sl = drive_rows[s_idx:e_idx]
            t_start = parse_dt(sch[f"leg{leg_no}_start"])
            pkts = build_leg_packets(sl, t_start, chamber_series, phase_offset=leg_no * 37 + lot_idx * 19)
            run_id = f"truck02_주행_{t_start.strftime('%Y-%m-%d_%H시%M분')}_{spec['run_tag']}_{leg_no}구간"
            leg_info = {
                "leg_no": leg_no,
                "run_id": run_id,
                "device_id": TARGET_DEVICE_ID,
                "started_at": pkts[0]["measured_at"],
                "ended_at": pkts[-1]["measured_at"],
                "packets": pkts,
                "avg_temp": round(sum(p["temperature"] for p in pkts) / len(pkts), 2),
                "min_temp": round(min(p["temperature"] for p in pkts), 2),
                "max_temp": round(max(p["temperature"] for p in pkts), 2),
                "avg_humi": round(sum(p["humidity"] for p in pkts) / len(pkts), 1),
                "max_g": round(max(p["g_force"] for p in pkts), 2),
                "max_spd": round(max(p["speed"] for p in pkts), 1),
                "start_coord": (pkts[0]["lat"], pkts[0]["lng"]),
                "end_coord": (pkts[-1]["lat"], pkts[-1]["lng"]),
            }
            leg_data[leg_no] = leg_info
            planned_runs.append(leg_info)

        # 저장고 대표 온습도 (챔버 실측 저온 구간에서 직접 추출)
        storage_env = {
            "A02": chamber_series[5],
            "A03": chamber_series[25],
            "B04": chamber_series[45 % len(chamber_series)],
            "B05": chamber_series[65 % len(chamber_series)],
            "C01": chamber_series[85 % len(chamber_series)],
        }

        planned_lots.append(
            {
                "lot_id": lot_id,
                "spec": spec,
                "legs": leg_data,
                "storage_env": storage_env,
            }
        )

    conflicts = check_existing_conflicts(cur, planned_lots, planned_runs)
    return planned_lots, planned_runs, conflicts


def apply_plan(conn, cur, planned_lots, planned_runs):
    # 1) transport_runs + sensor_telemetry
    for r in planned_runs:
        pkts = r["packets"]
        cur.execute(
            """
            INSERT INTO transport_runs
                (run_id, device_id, run_type, started_at, ended_at, packet_cnt, valid_gps_cnt,
                 min_temp, max_temp, avg_temp, max_g_force, max_speed, shock_cnt)
            VALUES (%s, %s, 'FIELD_DRIVE', %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE
                started_at=VALUES(started_at), ended_at=VALUES(ended_at),
                packet_cnt=VALUES(packet_cnt), valid_gps_cnt=VALUES(valid_gps_cnt),
                min_temp=VALUES(min_temp), max_temp=VALUES(max_temp), avg_temp=VALUES(avg_temp),
                max_g_force=VALUES(max_g_force), max_speed=VALUES(max_speed), shock_cnt=0
            """,
            (
                r["run_id"],
                r["device_id"],
                fmt_dt(r["started_at"]),
                fmt_dt(r["ended_at"]),
                len(pkts),
                len(pkts),
                r["min_temp"],
                r["max_temp"],
                r["avg_temp"],
                r["max_g"],
                r["max_spd"],
            ),
        )
        cur.executemany(
            """
            INSERT INTO sensor_telemetry
                (run_id, device_id, measured_at, temperature, humidity, lux, g_force,
                 speed, lat, lng, gps_state, event_type, raw_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                temperature=VALUES(temperature), humidity=VALUES(humidity), lux=VALUES(lux),
                g_force=VALUES(g_force), speed=VALUES(speed), lat=VALUES(lat), lng=VALUES(lng),
                gps_state=VALUES(gps_state), event_type=VALUES(event_type), raw_status=VALUES(raw_status)
            """,
            [
                (
                    r["run_id"],
                    r["device_id"],
                    fmt_dt(p["measured_at"]),
                    p["temperature"],
                    p["humidity"],
                    p["lux"],
                    p["g_force"],
                    p["speed"],
                    p["lat"],
                    p["lng"],
                    p["gps_state"],
                    p["event_type"],
                    p["raw_status"],
                )
                for p in pkts
            ],
        )
        refresh_run_stats_v2(cur, r["run_id"], dst_db=DB_V2)

    # 2) harvest_lots + sorted_lots + stage_events + shipments
    for item in planned_lots:
        lot_id = item["lot_id"]
        spec = item["spec"]
        sch = spec["schedule"]
        leg1, leg2, leg3 = item["legs"][1], item["legs"][2], item["legs"][3]
        env = item["storage_env"]

        farm_lat, farm_lng = leg1["start_coord"]
        apc_lat, apc_lng = leg1["end_coord"]
        dist_lat, dist_lng = leg2["end_coord"]
        retail_lat, retail_lng = leg3["end_coord"]

        # harvest_lots
        cur.execute(
            """
            INSERT INTO harvest_lots
                (lot_id, origin_zip, farmer_code, crop_code, fruit_type, variety,
                 farmer_phone, cultivation, harvest_no, total_qty,
                 harvest_date, storage_date, deliver_date,
                 ag_practice, current_stage, protocol_ver, is_test, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, 'B02', 'v4', 0, %s)
            ON DUPLICATE KEY UPDATE
                origin_zip=VALUES(origin_zip), farmer_code=VALUES(farmer_code), crop_code=VALUES(crop_code),
                fruit_type=VALUES(fruit_type), variety=VALUES(variety), farmer_phone=VALUES(farmer_phone),
                cultivation=VALUES(cultivation), harvest_no=VALUES(harvest_no), total_qty=VALUES(total_qty),
                harvest_date=VALUES(harvest_date), storage_date=VALUES(storage_date), deliver_date=VALUES(deliver_date),
                current_stage='B02', protocol_ver='v4', is_test=0
            """,
            (
                lot_id,
                spec["area_code"],
                spec["farmer_code"],
                spec["crop_code"],
                spec["fruit_type"],
                spec["variety"],
                spec["farmer_phone"],
                spec["cultivation"],
                spec["harvest_no"],
                spec["total_qty"],
                spec["harvest_date"],
                sch["A02"][:10],
                fmt_dt(leg1["started_at"])[:10],
                sch["A01"],
            ),
        )

        # sorted_lots (A, B, C -> D01 완주, DEFECT -> REJECTED)
        for g_code in ("A", "B", "C", "DEFECT"):
            pkg_id = f"{lot_id}-DEF" if g_code == "DEFECT" else f"{lot_id}-{g_code}"
            is_ship = 0 if g_code == "DEFECT" else 1
            cur_st = "REJECTED" if g_code == "DEFECT" else "D01"
            cur.execute(
                """
                INSERT INTO sorted_lots
                    (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    grade_qty=VALUES(grade_qty), current_stage=VALUES(current_stage), sorted_at=VALUES(sorted_at)
                """,
                (pkg_id, lot_id, g_code, GRADE_LABELS[g_code], spec["grades"][g_code], is_ship, cur_st, sch["B02"]),
            )

        # 공통 단계 stage_events (pkg_id = NULL): A01 ~ B02
        h_a01 = make_sha256(
            {
                "lot_id": lot_id,
                "stage": "A01",
                "ac": spec["area_code"],
                "fm": spec["farmer_code"],
                "cc": spec["crop_code"],
                "qt": spec["total_qty"],
                "hd": spec["harvest_date"],
            }
        )
        h_b02 = make_sha256(
            {
                "lot_id": lot_id,
                "stage": "B02",
                **spec["grades"],
                "rt": sch["B02"],
            }
        )

        common_events = [
            ("A01", sch["A01"], farm_lat, farm_lng, None, None, h_a01),
            ("A02", sch["A02"], farm_lat, farm_lng, env["A02"][0], env["A02"][1], None),
            ("A03", sch["A03"], farm_lat, farm_lng, env["A03"][0], env["A03"][1], None),
            ("A04", fmt_dt(leg1["started_at"]), farm_lat, farm_lng, None, None, None),
            ("B01", fmt_dt(leg1["ended_at"]), apc_lat, apc_lng, None, None, None),
            ("B02", sch["B02"], apc_lat, apc_lng, None, None, h_b02),
        ]
        for st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h in common_events:
            cur.execute(
                """
                INSERT INTO stage_events (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi, tx_hash)
                VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    event_at=VALUES(event_at), lat=VALUES(lat), lng=VALUES(lng),
                    temp=VALUES(temp), humi=VALUES(humi), tx_hash=COALESCE(VALUES(tx_hash), tx_hash)
                """,
                (lot_id, st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h),
            )

        # 1구간 shipment (pkg_id = NULL)
        cur.execute(
            """
            INSERT INTO shipments
                (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status,
                 gps_points_cnt, avg_temp, max_g_force)
            VALUES (1, %s, NULL, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                device_id=VALUES(device_id), run_id=VALUES(run_id),
                departed_at=VALUES(departed_at), arrived_at=VALUES(arrived_at),
                status='ARRIVED', gps_points_cnt=VALUES(gps_points_cnt),
                avg_temp=VALUES(avg_temp), max_g_force=VALUES(max_g_force)
            """,
            (
                lot_id,
                leg1["device_id"],
                leg1["run_id"],
                fmt_dt(leg1["started_at"]),
                fmt_dt(leg1["ended_at"]),
                len(leg1["packets"]),
                leg1["avg_temp"],
                leg1["max_g"],
            ),
        )

        # 등급별 단계 stage_events & 2·3구간 shipments (A / B / C 모두 완주)
        for g_idx, g_code in enumerate(("A", "B", "C")):
            pkg_id = f"{lot_id}-{g_code}"
            scan_offset = timedelta(minutes=g_idx * 2)  # B03/B04/B05 등급별 순차 스캔 (2분 간격)
            t_b03 = fmt_dt(parse_dt(sch["B03"]) + scan_offset)
            t_b04 = fmt_dt(parse_dt(sch["B04"]) + scan_offset)
            t_b05 = fmt_dt(parse_dt(sch["B05"]) + scan_offset)
            t_b06 = fmt_dt(leg2["started_at"])
            t_c01 = fmt_dt(leg2["ended_at"])
            t_c02 = fmt_dt(leg3["started_at"])
            t_d01 = fmt_dt(leg3["ended_at"])

            h_d01 = make_sha256({"lot_id": lot_id, "pkg_id": pkg_id, "stage": "D01", "at": t_d01})

            grade_events = [
                ("B03", t_b03, apc_lat, apc_lng, None, None, None),
                ("B04", t_b04, apc_lat, apc_lng, env["B04"][0], env["B04"][1], None),
                ("B05", t_b05, apc_lat, apc_lng, env["B05"][0], env["B05"][1], None),
                ("B06", t_b06, apc_lat, apc_lng, None, None, None),
                ("C01", t_c01, dist_lat, dist_lng, env["C01"][0], env["C01"][1], None),
                ("C02", t_c02, dist_lat, dist_lng, None, None, None),
                ("D01", t_d01, retail_lat, retail_lng, None, None, h_d01),
            ]
            for st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h in grade_events:
                cur.execute(
                    """
                    INSERT INTO stage_events (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi, tx_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        event_at=VALUES(event_at), lat=VALUES(lat), lng=VALUES(lng),
                        temp=VALUES(temp), humi=VALUES(humi), tx_hash=COALESCE(VALUES(tx_hash), tx_hash)
                    """,
                    (lot_id, pkg_id, st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h),
                )

            # 2구간 & 3구간 shipments
            for leg_no, leg_obj in ((2, leg2), (3, leg3)):
                cur.execute(
                    """
                    INSERT INTO shipments
                        (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status,
                         gps_points_cnt, avg_temp, max_g_force)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        device_id=VALUES(device_id), run_id=VALUES(run_id),
                        departed_at=VALUES(departed_at), arrived_at=VALUES(arrived_at),
                        status='ARRIVED', gps_points_cnt=VALUES(gps_points_cnt),
                        avg_temp=VALUES(avg_temp), max_g_force=VALUES(max_g_force)
                    """,
                    (
                        leg_no,
                        lot_id,
                        pkg_id,
                        leg_obj["device_id"],
                        leg_obj["run_id"],
                        fmt_dt(leg_obj["started_at"]),
                        fmt_dt(leg_obj["ended_at"]),
                        len(leg_obj["packets"]),
                        leg_obj["avg_temp"],
                        leg_obj["max_g"],
                    ),
                )

    conn.commit()


def verify_loaded(cur):
    print("\n=== VERIFICATION: v4 Lots in lab225_v2 ===")
    cur.execute(
        """
        SELECT lot_id, origin_zip, farmer_code, crop_code, fruit_type, variety,
               harvest_no, total_qty, harvest_date, current_stage, protocol_ver, is_test
        FROM harvest_lots
        WHERE protocol_ver = 'v4'
        ORDER BY lot_id ASC
        """
    )
    lots = cur.fetchall()
    print(f"Total v4 lots: {len(lots)}")
    for l in lots:
        print(" ", l)
        lid = l["lot_id"]
        cur.execute("SELECT grade_code, grade_qty, current_stage FROM sorted_lots WHERE lot_id=%s ORDER BY grade_code", (lid,))
        print("   sorted_lots:", cur.fetchall())
        for g in ("A", "B", "C"):
            pkg = f"{lid}-{g}"
            cur.execute(
                """
                SELECT GROUP_CONCAT(stage_code ORDER BY event_at) AS stages, COUNT(*) AS cnt
                FROM stage_events WHERE lot_id=%s AND (pkg_id IS NULL OR pkg_id=%s)
                """,
                (lid, pkg),
            )
            ev = cur.fetchone()
            cur.execute(
                """
                SELECT leg_no, run_id, gps_points_cnt, avg_temp, max_g_force, status
                FROM shipments WHERE lot_id=%s AND (pkg_id IS NULL OR pkg_id=%s)
                ORDER BY leg_no ASC
                """,
                (lid, pkg),
            )
            sh = cur.fetchall()
            print(f"   grade {g}: stages={ev['cnt']} ({ev['stages']}), legs={[(x['leg_no'], x['gps_points_cnt'], x['avg_temp'], x['max_g_force']) for x in sh]}")

    print("\n=== VERIFICATION: Existing v2/v3 lots untouched ===")
    cur.execute("SELECT protocol_ver, COUNT(*) AS cnt FROM harvest_lots GROUP BY protocol_ver ORDER BY protocol_ver")
    print(" ", cur.fetchall())
    cur.execute("SELECT COUNT(*) AS cnt FROM transport_runs WHERE device_id='carrier-c6-02' AND run_type IN ('FIELD_DRIVE', 'STORAGE')")
    print("  carrier-c6-02 FIELD_DRIVE/STORAGE total runs:", cur.fetchone())


def main():
    parser = argparse.ArgumentParser(description="Build & load v4 Jinan Hongro Apple combined dataset")
    parser.add_argument("--dry-run", action="store_true", help="Preview plan without writing to RDS")
    parser.add_argument("--apply", action="store_true", help="Insert v4 combined dataset into lab225_v2")
    parser.add_argument("--verify", action="store_true", help="Verify loaded v4 dataset in lab225_v2")
    args = parser.parse_args()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if args.verify and not args.apply and not args.dry_run:
                verify_loaded(cur)
                return

            planned_lots, planned_runs, conflicts = build_plan(cur)
            print(f"Planned v4 lots: {len(planned_lots)}, planned runs: {len(planned_runs)}")
            for item in planned_lots:
                s = item["spec"]
                print(f"\nLotID={item['lot_id']} | {s['area_code']} 진안 | FmID={s['farmer_code']} | {s['variety']} | Qt={s['total_qty']} | HN={s['harvest_no']}")
                print(f"  Storage env (chamber): {item['storage_env']}")
                for leg_no in (1, 2, 3):
                    lg = item["legs"][leg_no]
                    print(
                        f"  Leg {leg_no}: {lg['run_id']} | {fmt_dt(lg['started_at'])} ~ {fmt_dt(lg['ended_at'])} "
                        f"| pts={len(lg['packets'])} | temp={lg['min_temp']}~{lg['max_temp']}C (avg {lg['avg_temp']}C) "
                        f"| maxG={lg['max_g']}G | maxSpd={lg['max_spd']}km/h"
                    )

            if conflicts:
                print("\n[ABORT] Timestamp conflict detected with existing carrier-c6-02 runs:")
                for c in conflicts:
                    print(" ", c)
                sys.exit(2)
            else:
                print("\n[OK] Zero timestamp conflicts with existing carrier-c6-02 runs.")

            if args.apply:
                apply_plan(conn, cur, planned_lots, planned_runs)
                print("\n[SUCCESS] Applied v4 combined dataset to lab225_v2!")
                verify_loaded(cur)
            else:
                print("\n(Dry-run complete. Use --apply to write to lab225_v2.)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
