import json
import math
import time
import os
import sys
from datetime import datetime, timezone, timedelta
import queue
import threading
import paho.mqtt.client as mqtt
import pymysql

# db_v2 실시간 증분 브릿지 모듈 임포트
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from db_v2.bridge_sync import upsert_sensor_packet_v2, sync_v1_delta_to_v2

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ----------------------------------------------------------------
# 1. 설정 (환경변수 우선, 기본값 폴백 - Dual-Write 지원)
# ----------------------------------------------------------------
MYSQL_HOST = os.environ.get("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "lab225")          # 기존 v1 호환 보존용 DB
MYSQL_V2_DATABASE = os.environ.get("MYSQL_V2_DATABASE", "lab225_v2") # 신규 v2 정규화 메인 DB

MQTT_BROKER = os.environ.get("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))

# 차량별 토픽 및 식별자 매핑 (1호차 ~ 4호차)
TRUCK_MAPPING = {
    "coldchain/truck01/sensor": {"truck_id": "truck01", "device_id": "carrier-c6-01"},
    "coldchain/truck02/sensor": {"truck_id": "truck02", "device_id": "carrier-c6-02"},
    "coldchain/truck03/sensor": {"truck_id": "truck03", "device_id": "carrier-c6-03"},
    "coldchain/truck04/sensor": {"truck_id": "truck04", "device_id": "carrier-c6-04"},
}

# 항온항습 챔버 교정 전용 토픽 (실제 운영 테이블과 완전 분리 -> lab225_v2.chamber_calibration_logs)
CHAMBER_TOPIC = "coldchain/chamber/+"
CHAMBER_TABLE = "chamber_calibration_logs"

KST = timezone(timedelta(hours=9))

def get_kst_now():
    return datetime.now(KST)

# ----------------------------------------------------------------
# 2. 차량별 독립 세션 트래커 (세션 분할 방지 + 시각 역전/IMU 폭주 방어)
# ----------------------------------------------------------------
DRIVE_IDLE_TIMEOUT_S = 900.0      # 주행 일시 정차/신호대기/음영 허용 (15분)
SESSION_RESUME_GAP_S = 1800.0     # 데몬 재시작·자정 경과 시 연속 실험 이어받기 (30분)

def _calc_distance_m(lat1, lng1, lat2, lng2):
    dlat = (lat2 - lat1) * 111320.0
    dlng = (lng2 - lng1) * 111320.0 * math.cos(math.radians(lat1))
    return math.hypot(dlat, dlng)


class VehicleSessionTracker:
    def __init__(self, truck_id, device_id):
        self.truck_id = truck_id
        self.device_id = device_id
        self.active_run_id = None
        self.active_storage_run_id = None
        self.trip_started = False
        self.last_driving_time = 0.0
        self.last_packet_time = 0.0
        self.standby_count = 0
        self.last_valid_gps = (0.0, 0.0)
        self.gps_anchor = None
        self.moving_streak = 0
        self.last_db_save_time = 0.0
        self.last_storage_save_time = 0.0
        self.last_db_packet_epoch = 0.0
        self.last_accepted_dt = None
        self.prev_lux = None
        self.prev_temp = None
        self.shock_storm_streak = 0
        self.last_shock_ts = 0.0

    def restore_from_db(self, run_row):
        """데몬 재시작 시 최근 30분 내 활성 세션을 그대로 이어받아 불필요한 세션 분할을 차단"""
        if not run_row:
            return
        run_id = run_row.get("run_id")
        run_type = run_row.get("run_type")
        ended_at = run_row.get("ended_at")
        if not run_id or not ended_at:
            return
        now_kst_naive = get_kst_now().replace(tzinfo=None)
        if isinstance(ended_at, str):
            try:
                ended_at = datetime.strptime(ended_at[:19], "%Y-%m-%d %H:%M:%S")
            except Exception:
                return
        gap_s = (now_kst_naive - ended_at).total_seconds()
        if gap_s > SESSION_RESUME_GAP_S or gap_s < -300:
            return

        now_ts = time.time()
        self.last_packet_time = now_ts - max(0.0, gap_s)
        self.last_accepted_dt = ended_at
        if run_type == "FIELD_DRIVE":
            self.active_run_id = run_id
            self.trip_started = True
            self.last_driving_time = self.last_packet_time
            if run_row.get("last_lat") and run_row.get("last_lng"):
                self.last_valid_gps = (float(run_row["last_lat"]), float(run_row["last_lng"]))
            print(f"[{self.truck_id}] [RESUME] 활성 주행 세션 이어받기: '{run_id}' (종료 경과 {int(gap_s)}초)", flush=True)
        elif run_type == "STORAGE":
            self.active_storage_run_id = run_id
            print(f"[{self.truck_id}] [RESUME] 활성 보관 세션 이어받기: '{run_id}' (종료 경과 {int(gap_s)}초)", flush=True)

    def process_packet(self, payload):
        now_ts = time.time()
        now_kst_naive = get_kst_now().replace(tzinfo=None)
        pkt_gap_s = (now_ts - self.last_packet_time) if self.last_packet_time > 0 else 0.0
        self.last_packet_time = now_ts

        g_force = float(payload.get('g_force', 1.0))
        lux = float(payload.get('lux', 0.0))
        temp = float(payload.get('temperature', 0.0))
        humi = float(payload.get('humidity', 0.0))
        speed = float(payload.get('speed', 0.0))
        lat = float(payload.get('lat', 0.0))
        lng = float(payload.get('lng', 0.0))
        sats = int(payload.get('sats', 0))
        status_str = str(payload.get('status', ''))

        # 미동기화 시각 및 실내 GPS 시계 되감김(Time-Rewind) 서버 측 방어
        raw_ts = str(payload.get('timestamp_str') or '').strip()
        parsed_dt = None
        if len(raw_ts) >= 19 and not raw_ts.startswith("00:00") and not raw_ts.startswith("2026-10-01 00:00"):
            try:
                parsed_dt = datetime.strptime(raw_ts[:19], "%Y-%m-%d %H:%M:%S")
            except Exception:
                parsed_dt = None

        # 오프라인 LittleFS 고속 백필(< 0.4s 간격 연속 도착)이 아닌 실시간 수신 시 시계 역전/이탈 자동 보정
        is_fast_backfill = (0.0 < pkt_gap_s < 0.45)
        if parsed_dt is None:
            parsed_dt = now_kst_naive
        elif not is_fast_backfill:
            drift_s = (parsed_dt - now_kst_naive).total_seconds()
            rewound = (self.last_accepted_dt is not None) and ((parsed_dt - self.last_accepted_dt).total_seconds() < -5.0)
            if abs(drift_s) > 120.0 or rewound:
                parsed_dt = now_kst_naive

        self.last_accepted_dt = parsed_dt
        ts_str = parsed_dt.strftime("%Y-%m-%d %H:%M:%S")

        # 이상 이벤트 감지 (충격, 조도 급변, 온도 급변) + MPU6050 고장 연속 폭주 스로틀
        lux_diff = 0.0 if self.prev_lux is None else (lux - self.prev_lux)
        temp_diff = 0.0 if self.prev_temp is None else (temp - self.prev_temp)
        self.prev_lux = lux
        self.prev_temp = temp

        is_shock = (g_force >= 1.8)
        if is_shock:
            if (now_ts - self.last_shock_ts) <= 10.0:
                self.shock_storm_streak += 1
            else:
                self.shock_storm_streak = 1
            self.last_shock_ts = now_ts
        elif (now_ts - self.last_shock_ts) > 15.0:
            self.shock_storm_streak = 0

        # 연속 5회 이상 충격 폭주(센서 이상) 시 즉시 적재 우회를 끄고 정상 주기로 스로틀링
        shock_throttled = (self.shock_storm_streak >= 5)
        is_anomaly = (is_shock and not shock_throttled) or (abs(lux_diff) >= 300.0) or (abs(temp_diff) >= 2.0)

        # GPS 유효성 및 실이동 판정 (실내/냉장고 멀티패스 정지 GPS가 주행 세션으로 오분류·분할되는 것 차단)
        is_indoor_reported = ("대기" in status_str) or ("실내" in status_str) or ("보관" in status_str)
        gps_is_valid = (lat != 0.0 and lng != 0.0 and abs(lat) > 1.0 and not is_indoor_reported)

        disp_m = 0.0
        if gps_is_valid:
            if self.gps_anchor is None:
                self.gps_anchor = (lat, lng)
            disp_m = _calc_distance_m(self.gps_anchor[0], self.gps_anchor[1], lat, lng)
            if speed >= 4.0 and speed <= 180.0:
                self.moving_streak += 1
            else:
                self.moving_streak = 0
        else:
            self.moving_streak = 0

        is_real_moving = gps_is_valid and (self.moving_streak >= 3 or (disp_m >= 50.0 and sats >= 4))

        # 오랜 공백(15분 초과) 후 실내 보관 패킷이 들어오면 이전 주행 세션을 깔끔히 종료 (과거 GPS 덮어쓰기 차단)
        if self.trip_started and is_indoor_reported and pkt_gap_s >= DRIVE_IDLE_TIMEOUT_S:
            self.trip_started = False
            self.active_run_id = None
            self.last_valid_gps = (0.0, 0.0)
            self.gps_anchor = None
            self.standby_count = 0
            print(f"[{self.truck_id}] [STOP] {int(pkt_gap_s)}초 공백 후 실내 보관 전환 -> 이전 주행 세션 종료", flush=True)

        # 주행 상태 판정 및 래치
        if is_real_moving or (self.trip_started and gps_is_valid):
            self.last_driving_time = now_ts
            self.standby_count = 0
            if gps_is_valid:
                self.last_valid_gps = (lat, lng)
        else:
            self.standby_count += 1

        # 15분(900초) 이상 정지/실내 유지 시 주행 종료 처리 (일시 정차·신호대기로 세션 쪼개짐 방지)
        if self.trip_started:
            if self.standby_count >= 180 and (now_ts - self.last_driving_time > DRIVE_IDLE_TIMEOUT_S):
                self.trip_started = False
                self.active_run_id = None
                self.last_valid_gps = (0.0, 0.0)
                self.gps_anchor = None
                print(f"[{self.truck_id}] [STOP] 15분 이상 정지 감지 -> 주행 세션 자동 종료 및 보관 복귀", flush=True)

        # 신규 주행 시작 감지 (실제 이동이 확인될 때만 FIELD_DRIVE 세션 생성)
        was_stopped = not self.trip_started
        if is_real_moving and not is_indoor_reported:
            if was_stopped or self.active_run_id is None:
                dt_part = ts_str[:16].replace(" ", "_").replace(":", "시") + "분"
                new_run = f"{self.truck_id}_주행_{dt_part}"
                self.active_run_id = new_run
                self.trip_started = True
                self.active_storage_run_id = None
                print(f"[{self.truck_id}] [START] 새 주행 세션 자동 시작: '{new_run}' (출발시각: {ts_str}, spd={speed:.1f}, disp={disp_m:.0f}m)", flush=True)

        # 터널 보정 (실내 보관 패킷에는 과거 주행 좌표를 절대 덮어쓰지 않음)
        is_in_tunnel = False
        if not self.trip_started or is_indoor_reported:
            if is_indoor_reported:
                lat, lng, speed = 0.0, 0.0, 0.0
        elif not gps_is_valid and self.last_valid_gps != (0.0, 0.0):
            lat, lng = self.last_valid_gps
            is_in_tunnel = True

        # 상태 문자열 간결화
        if not self.trip_started or is_indoor_reported:
            loc_tag = "[대기]"
        elif is_in_tunnel:
            loc_tag = "[터널]"
        elif gps_is_valid:
            loc_tag = f"[GPS {sats}]"
        else:
            loc_tag = "[대기]"

        if is_shock:
            final_status = f"충격({g_force:.1f}G) {loc_tag}"[:48]
        elif is_anomaly:
            final_status = f"이상감지 {loc_tag}"[:48]
        elif loc_tag == "[대기]":
            final_status = "보관 [실내]" if "보관" in status_str else "대기 [실내]"
        else:
            final_status = f"정상 {loc_tag}"[:48]

        # DB 저장 조건 판정 (스마트 필터링: 주행 5초 + 창고/냉장고 실내 보관 30초 + 이상 이벤트 즉시)
        pkt_epoch = parsed_dt.timestamp()
        should_save = False
        is_storage_save = False
        if is_anomaly:
            should_save = True
        elif self.trip_started and not is_indoor_reported:
            if (now_ts - self.last_db_save_time >= 5.0) or (
                self.last_db_packet_epoch > 0 and abs(pkt_epoch - self.last_db_packet_epoch) >= 4.5
            ):
                should_save = True
        else:
            # 창고/냉장고 실내 보관 중 30초 주기로 온습도·조도를 단일 보관 세션에 연속 적재
            if (now_ts - self.last_storage_save_time >= 30.0) or (self.last_storage_save_time == 0.0):
                should_save = True
                is_storage_save = True

        if should_save:
            if is_storage_save:
                self.last_storage_save_time = now_ts
                if not is_shock and not is_anomaly:
                    final_status = "보관 [실내]"
            else:
                self.last_db_save_time = now_ts
            self.last_db_packet_epoch = pkt_epoch

            if self.trip_started and self.active_run_id and not is_indoor_reported:
                run_id_val = self.active_run_id
            else:
                # 연속 보관 실험은 자정(00:00)을 넘겨도 분할하지 않고 동일 run_id 유지 (30분 이상 끊긴 뒤 새 실험 시에만 일자 갱신)
                if not self.active_storage_run_id or pkt_gap_s > SESSION_RESUME_GAP_S:
                    self.active_storage_run_id = f"{self.truck_id}_보관_{ts_str[:10]}"
                run_id_val = self.active_storage_run_id

            try:
                dt_utc = parsed_dt - timedelta(hours=9)
                created_at_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                created_at_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            db_record = {
                "device": self.device_id,
                "timestamp_str": ts_str,
                "temperature": temp,
                "humidity": humi,
                "lux": lux,
                "g_force": g_force,
                "speed": speed,
                "lat": lat,
                "lng": lng,
                "status": final_status,
                "run_id": run_id_val,
                "created_at": created_at_str
            }
            return db_record

        return None

# ----------------------------------------------------------------
# 3. 비동기 Dual-Write DB 작업자 + ESP32 QR 스캐너 증분 브릿지 워커
# ----------------------------------------------------------------
db_queue = queue.Queue(maxsize=10000)

def get_db_conn(db_name=MYSQL_DATABASE):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        autocommit=True
    )

def ensure_chamber_table(cur, dst_db=MYSQL_V2_DATABASE):
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS `{dst_db}`.`{CHAMBER_TABLE}` (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            session_date DATE NOT NULL,
            device_id VARCHAR(32) NOT NULL,
            mac VARCHAR(24) DEFAULT NULL,
            timestamp_kst VARCHAR(32) NOT NULL,
            epoch_s BIGINT DEFAULT 0,
            uptime_ms BIGINT DEFAULT 0,
            temperature DOUBLE NOT NULL,
            humidity DOUBLE NOT NULL,
            lux DOUBLE DEFAULT 0.0,
            g_force DOUBLE DEFAULT 1.0,
            rssi INT DEFAULT -127,
            created_at DATETIME NOT NULL,
            UNIQUE KEY uk_dev_ts_up (device_id, timestamp_kst, uptime_ms),
            KEY idx_session_dev (session_date, device_id),
            KEY idx_dev_ts (device_id, timestamp_kst)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

def db_worker_thread():
    print(f"[DB Worker] Dual-Write 스레드 시작 ({MYSQL_DATABASE} + {MYSQL_V2_DATABASE})", flush=True)
    conn = None
    chamber_table_ready = False

    while True:
        record = db_queue.get()
        if record is None:
            break

        retry = 0
        while retry < 3:
            try:
                if conn is None:
                    conn = get_db_conn(MYSQL_DATABASE)
                else:
                    conn.ping(reconnect=True)

                with conn.cursor() as cur:
                    if record.get("_kind") == "chamber_cal":
                        if not chamber_table_ready:
                            ensure_chamber_table(cur, MYSQL_V2_DATABASE)
                            chamber_table_ready = True
                        cur.execute(
                            f"""
                            INSERT IGNORE INTO `{MYSQL_V2_DATABASE}`.`{CHAMBER_TABLE}`
                            (session_date, device_id, mac, timestamp_kst, epoch_s, uptime_ms,
                             temperature, humidity, lux, g_force, rssi, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                record["session_date"],
                                record["device_id"],
                                record["mac"],
                                record["timestamp_kst"],
                                record["epoch_s"],
                                record["uptime_ms"],
                                record["temperature"],
                                record["humidity"],
                                record["lux"],
                                record["g_force"],
                                record["rssi"],
                                record["created_at"],
                            ),
                        )
                        print(
                            f"  [CHAMBER INSERT] [{record['device_id']}] ts={record['timestamp_kst']} "
                            f"T={record['temperature']:.3f}C RH={record['humidity']:.3f}% -> {MYSQL_V2_DATABASE}.{CHAMBER_TABLE}",
                            flush=True,
                        )
                        break

                    # 1) 기존 v1 DB (lab225.sensor_data) 호환 적재 (무손실 롤백 안전망 유지)
                    sql_v1 = f"""
                    INSERT INTO `{MYSQL_DATABASE}`.`sensor_data`
                    (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        record["device"],
                        record["timestamp_str"],
                        record["temperature"],
                        record["humidity"],
                        record["lux"],
                        record["g_force"],
                        record["speed"],
                        record["lat"],
                        record["lng"],
                        record["status"],
                        record["run_id"],
                        record["created_at"]
                    )
                    cur.execute(sql_v1, val)
                    inserted_v1_id = cur.lastrowid

                    # 2) 신규 정규화 v2 DB (lab225_v2.transport_runs + sensor_telemetry) 동시 적재
                    upsert_sensor_packet_v2(cur, record, dst_db=MYSQL_V2_DATABASE)
                    if inserted_v1_id:
                        cur.execute(
                            f"""
                            INSERT INTO `{MYSQL_V2_DATABASE}`.`_sync_watermark` (source_table, last_id)
                            VALUES ('sensor_data', %s)
                            ON DUPLICATE KEY UPDATE last_id = GREATEST(last_id, VALUES(last_id))
                            """,
                            (inserted_v1_id,),
                        )

                print(f"  [DUAL INSERT] [{record['device']}] run='{record['run_id']}' ts={record['timestamp_str']} spd={record['speed']:.1f} g={record['g_force']:.2f}G ({record['status']})", flush=True)
                break
            except Exception as e:
                retry += 1
                print(f"  [DB ERROR {retry}/3] {e}", flush=True)
                time.sleep(2)
                try:
                    if conn:
                        conn.close()
                except Exception:
                    pass
                conn = None

        db_queue.task_done()

def qr_bridge_worker_thread():
    """물리 ESP32 스마트 스캐너가 `lab225.qr`에 INSERT한 신규 스캔 데이터를 3초 주기로 `lab225_v2`에 자동 분배 동기화"""
    print(f"[QR Bridge] 실시간 스캐너 브릿지 워커 시작 ({MYSQL_DATABASE}.qr -> {MYSQL_V2_DATABASE})", flush=True)
    b_conn = None
    while True:
        try:
            if b_conn is None:
                b_conn = get_db_conn(MYSQL_V2_DATABASE)
            else:
                b_conn.ping(reconnect=True)

            res = sync_v1_delta_to_v2(b_conn, src_db=MYSQL_DATABASE, dst_db=MYSQL_V2_DATABASE)
            if res.get("synced_qr") or res.get("synced_sensors"):
                print(f"  [BRIDGE SYNC] 신규 스캔 {res['synced_qr']}건 / 센서 {res['synced_sensors']}건 -> `{MYSQL_V2_DATABASE}` 정규화 반영 완료", flush=True)
        except Exception as e:
            print(f"  [BRIDGE WARN] {e}", flush=True)
            try:
                if b_conn:
                    b_conn.close()
            except Exception:
                pass
            b_conn = None
        time.sleep(3.0)

# ----------------------------------------------------------------
# 4. MQTT 클라이언트 콜백
# ----------------------------------------------------------------
trackers = {
    tinfo["truck_id"]: VehicleSessionTracker(tinfo["truck_id"], tinfo["device_id"])
    for tinfo in TRUCK_MAPPING.values()
}

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"\n=======================================================", flush=True)
        print(f" [HiveMQ Connect OK] {MQTT_BROKER}:{MQTT_PORT}", flush=True)
        print(f"=======================================================", flush=True)
        for topic in TRUCK_MAPPING.keys():
            client.subscribe(topic)
            print(f"  + Subscribed: {topic}", flush=True)
        client.subscribe(CHAMBER_TOPIC)
        print(f"  + Subscribed: {CHAMBER_TOPIC} (전용 테이블: {MYSQL_V2_DATABASE}.{CHAMBER_TABLE})", flush=True)
        print(f" [DAEMON READY] 24/7 Dual-Write ({MYSQL_DATABASE} + {MYSQL_V2_DATABASE}) 대기 중...\n", flush=True)
    else:
        print(f" [HiveMQ Connect FAIL] rc={rc}", flush=True)

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload_str = msg.payload.decode('utf-8', errors='replace').strip()
        data = json.loads(payload_str)

        # 챔버 교정 전용 토픽은 운영 테이블과 완전 분리하여 5초 원본 전량 저장
        if topic.startswith("coldchain/chamber/"):
            raw_ts = str(data.get("timestamp_str") or "").strip()
            if len(raw_ts) >= 19 and not raw_ts.startswith("00:00"):
                ts_kst = raw_ts[:19]
            else:
                ts_kst = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                dt_utc = datetime.strptime(ts_kst, "%Y-%m-%d %H:%M:%S") - timedelta(hours=9)
                created_at_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                created_at_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            db_queue.put({
                "_kind": "chamber_cal",
                "session_date": ts_kst[:10],
                "device_id": str(data.get("device") or topic.split("/")[-1]),
                "mac": str(data.get("mac") or ""),
                "timestamp_kst": ts_kst,
                "epoch_s": int(data.get("epoch_s") or 0),
                "uptime_ms": int(data.get("uptime_ms") or 0),
                "temperature": float(data.get("temperature", 0.0)),
                "humidity": float(data.get("humidity", 0.0)),
                "lux": float(data.get("lux", 0.0)),
                "g_force": float(data.get("g_force", 1.0)),
                "rssi": int(data.get("rssi", -127)),
                "created_at": created_at_str,
            })
            return

        mapping = TRUCK_MAPPING.get(topic)
        if not mapping:
            for t, info in TRUCK_MAPPING.items():
                if info["device_id"] == data.get("device"):
                    mapping = info
                    break
        if not mapping:
            return

        truck_id = mapping["truck_id"]
        tracker = trackers.get(truck_id)
        if tracker:
            db_record = tracker.process_packet(data)
            if db_record:
                db_queue.put(db_record)

    except Exception as e:
        print(f" [MQTT Parse Error] {e}", flush=True)

def on_disconnect(client, userdata, rc, properties=None):
    print(f" [HiveMQ Disconnect] rc={rc} (reconnecting...)", flush=True)

# ----------------------------------------------------------------
# 5. 메인 루프
# ----------------------------------------------------------------
def restore_active_sessions_on_startup():
    """데몬 시작/재시작 시 최근 30분 내 활성 세션을 DB에서 복원하여 세션 분할을 방지"""
    try:
        conn = get_db_conn(MYSQL_V2_DATABASE)
        try:
            with conn.cursor() as cur:
                for truck_id, tracker in trackers.items():
                    cur.execute(
                        f"""
                        SELECT tr.run_id, tr.run_type, tr.ended_at,
                               (SELECT st.lat FROM `{MYSQL_V2_DATABASE}`.`sensor_telemetry` st
                                WHERE st.run_id = tr.run_id AND st.lat != 0 AND st.lng != 0
                                ORDER BY st.measured_at DESC LIMIT 1) AS last_lat,
                               (SELECT st.lng FROM `{MYSQL_V2_DATABASE}`.`sensor_telemetry` st
                                WHERE st.run_id = tr.run_id AND st.lat != 0 AND st.lng != 0
                                ORDER BY st.measured_at DESC LIMIT 1) AS last_lng
                        FROM `{MYSQL_V2_DATABASE}`.`transport_runs` tr
                        WHERE tr.device_id = %s
                          AND tr.run_type IN ('FIELD_DRIVE', 'STORAGE')
                        ORDER BY tr.ended_at DESC
                        LIMIT 1
                        """,
                        (tracker.device_id,),
                    )
                    row = cur.fetchone()
                    if row:
                        tracker.restore_from_db(row)
        finally:
            conn.close()
    except Exception as e:
        print(f" [Startup Resume Warn] {e}", flush=True)


def main():
    print(f"\n=======================================================")
    print(f" ColdChain DigitalTwin Cloud Backend Daemon v2.1 (Anti-Split) ")
    print(f" Target MySQL: {MYSQL_HOST}:{MYSQL_PORT} -> [{MYSQL_DATABASE} & {MYSQL_V2_DATABASE}] ")
    print(f" Target HiveMQ: {MQTT_BROKER}:{MQTT_PORT} ")
    print(f" Monitored Fleet: 1호차 ~ 4호차 전체 (truck01 ~ truck04) ")
    print(f"=======================================================\n", flush=True)

    restore_active_sessions_on_startup()

    t_db = threading.Thread(target=db_worker_thread, daemon=True)
    t_db.start()

    t_br = threading.Thread(target=qr_bridge_worker_thread, daemon=True)
    t_br.start()

    try:
        from paho.mqtt.client import CallbackAPIVersion
        client = mqtt.Client(CallbackAPIVersion.VERSION1, transport="tcp")
    except Exception:
        client = mqtt.Client(transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_forever()
        except KeyboardInterrupt:
            print("\nExiting daemon safely...", flush=True)
            db_queue.put(None)
            break
        except Exception as e:
            print(f" [Main Loop Retry] {e}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
