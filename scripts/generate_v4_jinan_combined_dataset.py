"""
ColdChain DigitalTwin Platform - Supply Chain v4 Single-Lot Multi-Destination/Multi-Truck Builder
--------------------------------------------------------------------------------------------------
설계 핵심:
  1. 1차 단일 로트(55451071411261125: 진안 마령면 55451 / 농가 071 / 홍로 사과 411 / 2026-11-25 수확 / 500상자)
  2. 농가 저장고(A02~A03) 및 APC 저장고(B04~B05) 포함, v4 13단계 전 공정 완주.
  3. APC 선별(B02) 이후 상(A)/중(B)/하(C) 등급별로 서로 다른 유통창고·판매처 목적지 및 서로 다른 호차 배정:
     - 공통 1구간 (원물 500상자): 1호차 (truck01 / carrier-c6-01) | 진안 마령면 농가 -> 함양 거점 APC
     - 상(A) 등급 (400상자)     : 2호차 (truck02 / carrier-c6-02) | 함양 APC -> 창원 광역물류센터 -> 부산 해운대 판매처
     - 중(B) 등급 (60상자)      : 3호차 (truck03 / carrier-c6-03) | 함양 APC -> 진주 물류센터     -> 김해 판매처
     - 하(C) 등급 (32상자)      : 4호차 (truck04 / carrier-c6-04) | 함양 APC -> 산청 거점창고     -> 진주 로컬 판매처
     - 결점과     (8상자)       : REJECTED (출하 제외)

데이터 출처 (100% RDS 실측 기반):
  - GPS / 속도 / 진동: lab225_v2.sensor_telemetry (run_id='truck04_주행_2026-10-20_15시27분', 1,518건)
      모든 구간이 APC 좌표(35.5510, 127.7590)에서 단절 없이 실제 고속도로/국도 궤적으로 연결됨.
      정상 콜드체인 유지 시나리오를 위해 비주행 충격 스파이크(>=1.8G, 2건)만 완화.
  - 온도 / 습도: lab225_v2.chamber_calibration_logs (2026-11-27~28 저온 1.5~3.9°C 실측 구간)
      등급/차량별 서로 다른 실측 저온 구간 적용 + 실측 습도 변동 곡선을 사과 저온 적정 RH(86~88%)로 보정.

안전 원칙:
  - 기존 실증 데이터(v2 16건, v3 1건, 기존 주행/보관 세션)는 단 1건도 수정·삭제하지 않음.
  - 오직 본 스크립트가 생성한 합성 로트(55451071411261123/24/25) 및 '%진안071%' run_id만 정리/갱신.
  - 1~4호차의 모든 기존 세션 타임스탬프와 충돌(겹침) 여부를 사전 검사하여 0건일 때만 적재.

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

# 이전 다중 로트 테스트에서 본 스크립트가 생성했던 합성 ID 정리 대상 (기존 v2/v3 실증 데이터는 절대 포함 불가)
MANAGED_SYNTH_LOT_IDS = (
    "55451071411261123",
    "55451071411261124",
    "55451071411261125",
)
MANAGED_RUN_LIKE = "%진안071%"

# 1차 단일 로트 정의 (11/25 수확 -> 농가 저온저장 -> 11/26 APC 입고·선별·저장 -> 11/27 등급별 분기 운송·도착)
LOT_SPEC = {
    "area_code": "55451",  # 전북 진안군 (마령면)
    "farmer_code": "071",
    "fruit_type": "Apples",
    "variety": "Hongro Apple",
    "crop_code": "411",
    "farmer_phone": "010-7100-5451",
    "cultivation": "GAP",
    "harvest_no": 1,
    "total_qty": 500,
    "grades": {"A": 400, "B": 60, "C": 32, "DEFECT": 8},
    "harvest_date": "2026-11-25",
    "common_schedule": {
        "A01": "2026-11-25 08:30:00",
        "A02": "2026-11-25 09:30:00",
        "A03": "2026-11-26 15:30:00",  # 약 30시간 농가 저온저장
        "leg1_start": "2026-11-26 16:00:00",  # -> B01 ~ 16:44:17
        "B02": "2026-11-26 17:30:00",  # APC 선별 및 A/B/C 유색 QR 발급
    },
    # 공통 1구간: 1호차 (truck01 / carrier-c6-01), 진안 마령면(idx 0) -> 함양 APC(idx 101)
    "leg1": {
        "device_id": "carrier-c6-01",
        "truck_prefix": "truck01",
        "slice": (0, 102),
        "run_suffix": "진안071_1구간_원물",
        "chamber": {
            "device_id": "carrier-c6-03",
            "t_start": "2026-11-27 23:25:00",
            "t_end": "2026-11-28 00:05:00",
            "target_rh": 87.6,
        },
    },
    # 선별 이후 A / B / C 등급별 서로 다른 호차 · 서로 다른 유통창고/판매처 목적지 · 서로 다른 실측 온습도 구간
    "grade_plans": {
        "A": {
            "label_ko": "상",
            "device_id": "carrier-c6-02",  # 2호차 (truck02)
            "truck_prefix": "truck02",
            "dest_desc": "창원 광역물류센터 -> 부산 해운대 판매처",
            "B03": "2026-11-26 18:00:00",
            "B04": "2026-11-26 18:20:00",
            "B05": "2026-11-27 07:30:00",
            "leg2_start": "2026-11-27 08:00:00",  # 함양 APC(101) -> 창원 광역물류센터(707)
            "leg2_slice": (101, 708),
            "leg2_suffix": "진안071_A상_2구간_창원",
            "leg3_start": "2026-11-27 14:00:00",  # 창원(707) -> 부산 해운대 판매처(1517)
            "leg3_slice": (707, 1518),
            "leg3_suffix": "진안071_A상_3구간_부산",
            "chamber": {
                "device_id": "carrier-c6-03",
                "t_start": "2026-11-27 23:45:00",
                "t_end": "2026-11-28 00:18:00",
                "target_rh": 87.2,
            },
        },
        "B": {
            "label_ko": "중",
            "device_id": "carrier-c6-03",  # 3호차 (truck03)
            "truck_prefix": "truck03",
            "dest_desc": "진주 물류센터 -> 김해 판매처",
            "B03": "2026-11-26 18:10:00",
            "B04": "2026-11-26 18:30:00",
            "B05": "2026-11-27 08:30:00",
            "leg2_start": "2026-11-27 09:00:00",  # 함양 APC(101) -> 진주 물류센터(404)
            "leg2_slice": (101, 405),
            "leg2_suffix": "진안071_B중_2구간_진주",
            "leg3_start": "2026-11-27 13:00:00",  # 진주(404) -> 김해 판매처(808)
            "leg3_slice": (404, 809),
            "leg3_suffix": "진안071_B중_3구간_김해",
            "chamber": {
                "device_id": "carrier-c6-03",
                "t_start": "2026-11-27 23:25:00",
                "t_end": "2026-11-28 00:10:00",
                "target_rh": 86.8,
            },
        },
        "C": {
            "label_ko": "하",
            "device_id": "carrier-c6-04",  # 4호차 (truck04)
            "truck_prefix": "truck04",
            "dest_desc": "산청 거점창고 -> 진주 로컬 판매처",
            "B03": "2026-11-26 18:20:00",
            "B04": "2026-11-26 18:40:00",
            "B05": "2026-11-27 09:30:00",
            "leg2_start": "2026-11-27 10:00:00",  # 함양 APC(101) -> 산청 거점창고(202)
            "leg2_slice": (101, 203),
            "leg2_suffix": "진안071_C하_2구간_산청",
            "leg3_start": "2026-11-27 12:00:00",  # 산청(202) -> 진주 로컬 판매처(404)
            "leg3_slice": (202, 405),
            "leg3_suffix": "진안071_C하_3구간_진주",
            "chamber": {
                "device_id": "carrier-c6-02",
                "t_start": "2026-11-28 00:00:01",
                "t_end": "2026-11-28 00:40:00",
                "target_rh": 86.2,
            },
        },
    },
}

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
    return [
        (round(float(r["temperature"]), 2), round(min(92.0, max(82.0, float(r["humidity"]) + rh_offset)), 1))
        for r in rows
    ]


def sanitize_normal_g_force(raw_g: float) -> float:
    g = float(raw_g or 1.0)
    return 1.32 if g >= 1.8 else round(g, 2)


def sanitize_normal_status(raw_status: str, g_val: float) -> str:
    s = str(raw_status or "")
    if "충격" in s or g_val >= 1.8:
        return "정상 [GPS FIX]"
    return s[:60] if s else "정상 [GPS FIX]"


def build_leg_packets(drive_slice: list, target_start: datetime, chamber_series: list, phase_offset: int):
    base_t = drive_slice[0]["measured_at"]
    m = len(chamber_series)
    packets = []
    seen_ts = set()
    for i, r in enumerate(drive_slice):
        new_dt = target_start + (r["measured_at"] - base_t)
        while new_dt in seen_ts:
            new_dt += timedelta(seconds=1)
        seen_ts.add(new_dt)
        temp_v, humi_v = chamber_series[(i + phase_offset) % m]
        g_v = sanitize_normal_g_force(r["g_force"])
        lux_v = round(min(float(r["lux"] or 0.0), 2.0), 1)
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


def summarize_leg(leg_no: int, device_id: str, run_id: str, pkts: list):
    return {
        "leg_no": leg_no,
        "device_id": device_id,
        "run_id": run_id,
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


def check_existing_conflicts(cur, planned_runs: list):
    """모든 기존(비합성) 세션과의 시간 충돌을 차량(device_id)별로 사전 검사"""
    cur.execute(
        """
        SELECT device_id, run_id, started_at, ended_at
        FROM transport_runs
        WHERE run_id NOT LIKE %s
          AND run_type IN ('FIELD_DRIVE', 'STORAGE')
          AND started_at IS NOT NULL AND ended_at IS NOT NULL
        """,
        (MANAGED_RUN_LIKE,),
    )
    existing_runs = list(cur.fetchall())

    conflicts = []
    for pr in planned_runs:
        ps, pe = pr["started_at"], pr["ended_at"]
        for er in existing_runs:
            if er["device_id"] != pr["device_id"]:
                continue
            es, ee = er["started_at"], er["ended_at"]
            if ps <= (ee + timedelta(minutes=5)) and pe >= (es - timedelta(minutes=5)):
                conflicts.append((pr["device_id"], pr["run_id"], ps, pe, er["run_id"], es, ee))
    return conflicts


def build_plan(cur):
    spec = LOT_SPEC
    assert sum(spec["grades"].values()) == spec["total_qty"], "Grade sum != total_qty"
    lot_id = build_lot_id_17(
        spec["area_code"],
        spec["farmer_code"],
        spec["fruit_type"],
        spec["variety"],
        spec["harvest_date"],
        crop_code=spec["crop_code"],
    )
    drive_rows = load_source_drive(cur)
    planned_runs = []

    # 1) 공통 1구간 (1호차: 진안 마령면 -> 함양 APC)
    l1_cfg = spec["leg1"]
    l1_chamber = load_chamber_slice(
        cur,
        l1_cfg["chamber"]["device_id"],
        l1_cfg["chamber"]["t_start"],
        l1_cfg["chamber"]["t_end"],
        l1_cfg["chamber"]["target_rh"],
    )
    s1, e1 = l1_cfg["slice"]
    l1_start = parse_dt(spec["common_schedule"]["leg1_start"])
    l1_pkts = build_leg_packets(drive_rows[s1:e1], l1_start, l1_chamber, phase_offset=11)
    l1_run_id = f"{l1_cfg['truck_prefix']}_주행_{l1_start.strftime('%Y-%m-%d_%H시%M분')}_{l1_cfg['run_suffix']}"
    leg1 = summarize_leg(1, l1_cfg["device_id"], l1_run_id, l1_pkts)
    planned_runs.append(leg1)

    farm_storage_env = {"A02": l1_chamber[5], "A03": l1_chamber[25]}

    # 2) 등급별(A/B/C) 서로 다른 호차 · 서로 다른 목적지 2·3구간
    grade_bundles = {}
    for g_idx, g_code in enumerate(("A", "B", "C")):
        gp = spec["grade_plans"][g_code]
        g_chamber = load_chamber_slice(
            cur,
            gp["chamber"]["device_id"],
            gp["chamber"]["t_start"],
            gp["chamber"]["t_end"],
            gp["chamber"]["target_rh"],
        )
        s2, e2 = gp["leg2_slice"]
        t2_start = parse_dt(gp["leg2_start"])
        pkts2 = build_leg_packets(drive_rows[s2:e2], t2_start, g_chamber, phase_offset=31 + g_idx * 17)
        run2_id = f"{gp['truck_prefix']}_주행_{t2_start.strftime('%Y-%m-%d_%H시%M분')}_{gp['leg2_suffix']}"
        leg2 = summarize_leg(2, gp["device_id"], run2_id, pkts2)
        planned_runs.append(leg2)

        s3, e3 = gp["leg3_slice"]
        t3_start = parse_dt(gp["leg3_start"])
        pkts3 = build_leg_packets(drive_rows[s3:e3], t3_start, g_chamber, phase_offset=73 + g_idx * 23)
        run3_id = f"{gp['truck_prefix']}_주행_{t3_start.strftime('%Y-%m-%d_%H시%M분')}_{gp['leg3_suffix']}"
        leg3 = summarize_leg(3, gp["device_id"], run3_id, pkts3)
        planned_runs.append(leg3)

        grade_bundles[g_code] = {
            "cfg": gp,
            "leg2": leg2,
            "leg3": leg3,
            "storage_env": {
                "B04": g_chamber[10 % len(g_chamber)],
                "B05": g_chamber[35 % len(g_chamber)],
                "C01": g_chamber[60 % len(g_chamber)],
            },
        }

    conflicts = check_existing_conflicts(cur, planned_runs)
    return {
        "lot_id": lot_id,
        "spec": spec,
        "leg1": leg1,
        "farm_storage_env": farm_storage_env,
        "grade_bundles": grade_bundles,
        "planned_runs": planned_runs,
        "conflicts": conflicts,
    }


def cleanup_previous_managed_synth(cur):
    """오직 본 스크립트가 이전에 생성한 합성 로트/세션만 정밀 삭제 (기존 v2/v3 및 타 세션 100% 보존)"""
    placeholders = ", ".join(["%s"] * len(MANAGED_SYNTH_LOT_IDS))
    cur.execute(
        f"SELECT lot_id, protocol_ver FROM harvest_lots WHERE lot_id IN ({placeholders})",
        MANAGED_SYNTH_LOT_IDS,
    )
    found_lots = cur.fetchall()
    for row in found_lots:
        assert row["protocol_ver"] == "v4", f"Refusing to touch non-v4 lot: {row}"

    if found_lots:
        # FK ON DELETE CASCADE로 sorted_lots, stage_events, shipments의 해당 합성 행만 함께 정리됨
        cur.execute(f"DELETE FROM harvest_lots WHERE lot_id IN ({placeholders})", MANAGED_SYNTH_LOT_IDS)
        print(f"Cleaned previous managed synthetic lots: {[r['lot_id'] for r in found_lots]}")

    cur.execute("SELECT run_id FROM transport_runs WHERE run_id LIKE %s", (MANAGED_RUN_LIKE,))
    found_runs = [r["run_id"] for r in cur.fetchall()]
    if found_runs:
        # FK ON DELETE CASCADE로 sensor_telemetry의 해당 합성 run_id 패킷만 함께 정리됨
        cur.execute("DELETE FROM transport_runs WHERE run_id LIKE %s", (MANAGED_RUN_LIKE,))
        print(f"Cleaned previous managed synthetic runs: {len(found_runs)} runs")


def apply_plan(conn, cur, plan: dict):
    # 0) 기존에 본 스크립트가 넣었던 이전 합성 데이터(1·2·3차)만 안전 정리
    cleanup_previous_managed_synth(cur)

    lot_id = plan["lot_id"]
    spec = plan["spec"]
    sch = spec["common_schedule"]
    leg1 = plan["leg1"]
    f_env = plan["farm_storage_env"]

    # 1) transport_runs + sensor_telemetry (1~4호차 총 7개 주행 세션)
    for r in plan["planned_runs"]:
        pkts = r["packets"]
        cur.execute(
            """
            INSERT INTO transport_runs
                (run_id, device_id, run_type, started_at, ended_at, packet_cnt, valid_gps_cnt,
                 min_temp, max_temp, avg_temp, max_g_force, max_speed, shock_cnt)
            VALUES (%s, %s, 'FIELD_DRIVE', %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
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

    # 2) harvest_lots (단일 1차 v4 로트)
    farm_lat, farm_lng = leg1["start_coord"]
    apc_lat, apc_lng = leg1["end_coord"]

    cur.execute(
        """
        INSERT INTO harvest_lots
            (lot_id, origin_zip, farmer_code, crop_code, fruit_type, variety,
             farmer_phone, cultivation, harvest_no, total_qty,
             harvest_date, storage_date, deliver_date,
             ag_practice, current_stage, protocol_ver, is_test, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, 'B02', 'v4', 0, %s)
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

    # 3) sorted_lots (A/B/C -> D01 완주, DEFECT -> REJECTED)
    for g_code in ("A", "B", "C", "DEFECT"):
        pkg_id = f"{lot_id}-DEF" if g_code == "DEFECT" else f"{lot_id}-{g_code}"
        cur.execute(
            """
            INSERT INTO sorted_lots
                (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                pkg_id,
                lot_id,
                g_code,
                GRADE_LABELS[g_code],
                spec["grades"][g_code],
                0 if g_code == "DEFECT" else 1,
                "REJECTED" if g_code == "DEFECT" else "D01",
                sch["B02"],
            ),
        )

    # 4) 공통 단계 stage_events (A01~B02, pkg_id=NULL) + 1구간 shipment (1호차)
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
    h_b02 = make_sha256({"lot_id": lot_id, "stage": "B02", **spec["grades"], "rt": sch["B02"]})

    for st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h in [
        ("A01", sch["A01"], farm_lat, farm_lng, None, None, h_a01),
        ("A02", sch["A02"], farm_lat, farm_lng, f_env["A02"][0], f_env["A02"][1], None),
        ("A03", sch["A03"], farm_lat, farm_lng, f_env["A03"][0], f_env["A03"][1], None),
        ("A04", fmt_dt(leg1["started_at"]), farm_lat, farm_lng, None, None, None),
        ("B01", fmt_dt(leg1["ended_at"]), apc_lat, apc_lng, None, None, None),
        ("B02", sch["B02"], apc_lat, apc_lng, None, None, h_b02),
    ]:
        cur.execute(
            """
            INSERT INTO stage_events (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi, tx_hash)
            VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s)
            """,
            (lot_id, st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h),
        )

    cur.execute(
        """
        INSERT INTO shipments
            (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status,
             gps_points_cnt, avg_temp, max_g_force)
        VALUES (1, %s, NULL, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
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

    # 5) 등급별 독립 stage_events (B03~D01) + 등급별 독립 2·3구간 shipments (2·3·4호차)
    for g_code in ("A", "B", "C"):
        pkg_id = f"{lot_id}-{g_code}"
        bundle = plan["grade_bundles"][g_code]
        gp = bundle["cfg"]
        leg2, leg3 = bundle["leg2"], bundle["leg3"]
        s_env = bundle["storage_env"]

        dist_lat, dist_lng = leg2["end_coord"]
        retail_lat, retail_lng = leg3["end_coord"]
        t_d01 = fmt_dt(leg3["ended_at"])
        h_d01 = make_sha256(
            {"lot_id": lot_id, "pkg_id": pkg_id, "stage": "D01", "device": gp["device_id"], "at": t_d01}
        )

        for st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h in [
            ("B03", gp["B03"], apc_lat, apc_lng, None, None, None),
            ("B04", gp["B04"], apc_lat, apc_lng, s_env["B04"][0], s_env["B04"][1], None),
            ("B05", gp["B05"], apc_lat, apc_lng, s_env["B05"][0], s_env["B05"][1], None),
            ("B06", fmt_dt(leg2["started_at"]), apc_lat, apc_lng, None, None, None),
            ("C01", fmt_dt(leg2["ended_at"]), dist_lat, dist_lng, s_env["C01"][0], s_env["C01"][1], None),
            ("C02", fmt_dt(leg3["started_at"]), dist_lat, dist_lng, None, None, None),
            ("D01", t_d01, retail_lat, retail_lng, None, None, h_d01),
        ]:
            cur.execute(
                """
                INSERT INTO stage_events (lot_id, pkg_id, stage_code, event_at, lat, lng, temp, humi, tx_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (lot_id, pkg_id, st_code, ev_at, lat_v, lng_v, tp_v, hm_v, tx_h),
            )

        for leg_no, leg_obj in ((2, leg2), (3, leg3)):
            cur.execute(
                """
                INSERT INTO shipments
                    (leg_no, lot_id, pkg_id, device_id, run_id, departed_at, arrived_at, status,
                     gps_points_cnt, avg_temp, max_g_force)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'ARRIVED', %s, %s, %s)
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
                SELECT leg_no, device_id, run_id, gps_points_cnt, avg_temp, max_g_force, status
                FROM shipments WHERE lot_id=%s AND (pkg_id IS NULL OR pkg_id=%s)
                ORDER BY leg_no ASC
                """,
                (lid, pkg),
            )
            sh = cur.fetchall()
            cur.execute("SELECT lat, lng FROM stage_events WHERE lot_id=%s AND pkg_id=%s AND stage_code='D01'", (lid, pkg))
            d01_pos = cur.fetchone()
            print(f"   grade {g}: stages={ev['cnt']} | D01={d01_pos}")
            for x in sh:
                print(f"     leg{x['leg_no']}: {x['device_id']} | {x['run_id']} | pts={x['gps_points_cnt']} | avgT={x['avg_temp']}C | maxG={x['max_g_force']}G")

    print("\n=== VERIFICATION: Existing v2/v3 lots & vehicle run counts ===")
    cur.execute("SELECT protocol_ver, COUNT(*) AS cnt FROM harvest_lots GROUP BY protocol_ver ORDER BY protocol_ver")
    print("  lots by protocol_ver:", cur.fetchall())
    cur.execute(
        """
        SELECT device_id, COUNT(*) AS cnt
        FROM transport_runs
        WHERE run_type IN ('FIELD_DRIVE', 'STORAGE')
        GROUP BY device_id
        ORDER BY device_id
        """
    )
    print("  FIELD_DRIVE/STORAGE runs by device:", cur.fetchall())


def main():
    parser = argparse.ArgumentParser(description="Build & load v4 1st-lot multi-destination/multi-truck dataset")
    parser.add_argument("--dry-run", action="store_true", help="Preview plan without writing to RDS")
    parser.add_argument("--apply", action="store_true", help="Apply to lab225_v2 (cleans only previous managed synth rows)")
    parser.add_argument("--verify", action="store_true", help="Verify loaded v4 dataset in lab225_v2")
    args = parser.parse_args()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if args.verify and not args.apply and not args.dry_run:
                verify_loaded(cur)
                return

            plan = build_plan(cur)
            print(f"LotID={plan['lot_id']} | 55451 진안 마령면 | FmID=071 | Hongro Apple | Qt=500 | HN=1")
            l1 = plan["leg1"]
            print(
                f"  [공통 1구간] {l1['device_id']} | {l1['run_id']} | {fmt_dt(l1['started_at'])} ~ {fmt_dt(l1['ended_at'])} "
                f"| pts={len(l1['packets'])} | avgT={l1['avg_temp']}C | maxG={l1['max_g']}G | {l1['start_coord']} -> {l1['end_coord']}"
            )
            for g_code in ("A", "B", "C"):
                b = plan["grade_bundles"][g_code]
                gp = b["cfg"]
                print(f"  [등급 {g_code}({gp['label_ko']}) | {gp['device_id']} | {gp['dest_desc']}] storage_env={b['storage_env']}")
                for lg in (b["leg2"], b["leg3"]):
                    print(
                        f"    Leg {lg['leg_no']}: {lg['run_id']} | {fmt_dt(lg['started_at'])} ~ {fmt_dt(lg['ended_at'])} "
                        f"| pts={len(lg['packets'])} | avgT={lg['avg_temp']}C | maxG={lg['max_g']}G | {lg['start_coord']} -> {lg['end_coord']}"
                    )

            if plan["conflicts"]:
                print("\n[ABORT] Timestamp conflict detected with existing runs:")
                for c in plan["conflicts"]:
                    print(" ", c)
                sys.exit(2)
            else:
                print("\n[OK] Zero timestamp conflicts across carrier-c6-01 ~ carrier-c6-04.")

            if args.apply:
                apply_plan(conn, cur, plan)
                print("\n[SUCCESS] Applied single-lot multi-destination v4 dataset to lab225_v2!")
                verify_loaded(cur)
            else:
                print("\n(Dry-run complete. Use --apply to write to lab225_v2.)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
