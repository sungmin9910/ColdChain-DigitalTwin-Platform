import json
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

KST = timezone(timedelta(hours=9))

def get_kst_now():
    return datetime.now(KST)

# ----------------------------------------------------------------
# 2. 차량별 독립 세션 트래커
# ----------------------------------------------------------------
class VehicleSessionTracker:
    def __init__(self, truck_id, device_id):
        self.truck_id = truck_id
        self.device_id = device_id
        self.active_run_id = None
        self.trip_started = False
        self.last_driving_time = 0.0
        self.last_packet_time = 0.0
        self.standby_count = 0
        self.last_valid_gps = (0.0, 0.0)
        self.last_db_save_time = 0.0
        self.last_storage_save_time = 0.0
        self.last_db_packet_epoch = 0.0
        self.prev_lux = None
        self.prev_temp = None

    def process_packet(self, payload):
        now_ts = time.time()
        g_force = float(payload.get('g_force', 1.0))
        lux = float(payload.get('lux', 0.0))
        temp = float(payload.get('temperature', 0.0))
        humi = float(payload.get('humidity', 0.0))
        speed = float(payload.get('speed', 0.0))
        lat = float(payload.get('lat', 0.0))
        lng = float(payload.get('lng', 0.0))
        sats = int(payload.get('sats', 0))
        status_str = str(payload.get('status', ''))

        # 미동기화 시각(00:00:00 또는 2026-10-01 00:00) 수신 시 서버 KST 현재 시각으로 즉시 보정
        raw_ts = str(payload.get('timestamp_str') or '').strip()
        if len(raw_ts) >= 19 and not raw_ts.startswith("00:00") and not raw_ts.startswith("2026-10-01 00:00"):
            ts_str = raw_ts[:19]
        else:
            ts_str = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")

        # 이상 이벤트 감지 (충격, 조도 급변, 온도 급변)
        lux_diff = 0.0 if self.prev_lux is None else (lux - self.prev_lux)
        temp_diff = 0.0 if self.prev_temp is None else (temp - self.prev_temp)
        self.prev_lux = lux
        self.prev_temp = temp

        is_shock = (g_force >= 1.8)
        is_anomaly = is_shock or (abs(lux_diff) >= 300.0) or (abs(temp_diff) >= 2.0)

        # GPS 유효성 판정
        gps_is_valid = (lat != 0.0 and lng != 0.0)
        is_moving = (speed > 2.0) or (gps_is_valid and speed > 0.8)

        # 주행 상태 판정 및 래치
        if is_moving or (gps_is_valid and "대기" not in status_str):
            self.last_driving_time = now_ts
            self.standby_count = 0
            if gps_is_valid:
                self.last_valid_gps = (lat, lng)
        else:
            self.standby_count += 1

        # 3분(36패킷) 이상 정지 시 주행 종료 처리
        if self.trip_started:
            if self.standby_count >= 36 and (now_ts - self.last_driving_time > 180):
                self.trip_started = False
                self.active_run_id = None
                print(f"[{self.truck_id}] [STOP] 3분 이상 정지 감지 -> 주행 세션 자동 종료 및 대기 복귀", flush=True)

        # 신규 주행 시작 감지 (세션 ID 자동 생성)
        was_stopped = not self.trip_started
        if (gps_is_valid or speed > 2.0) and "대기" not in status_str and "실내" not in status_str:
            if was_stopped or self.active_run_id is None:
                dt_part = ts_str[:16].replace(" ", "_").replace(":", "시") + "분"
                new_run = f"{self.truck_id}_주행_{dt_part}"
                self.active_run_id = new_run
                self.trip_started = True
                print(f"[{self.truck_id}] [START] 새 주행 세션 자동 시작: '{new_run}' (출발시각: {ts_str})", flush=True)

        # 터널 보정
        is_in_tunnel = False
        if not self.trip_started:
            pass
        elif not gps_is_valid and self.last_valid_gps != (0.0, 0.0):
            lat, lng = self.last_valid_gps
            is_in_tunnel = True

        # 상태 문자열 간결화
        if not self.trip_started or "대기" in status_str or "실내" in status_str:
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

        # DB 저장 조건 판정 (스마트 필터링: 주행 5초 + 창고 실내 보관 30초 + 이상 이벤트 즉시)
        pkt_epoch = None
        try:
            pkt_epoch = datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S").timestamp()
        except Exception:
            pkt_epoch = None

        should_save = False
        is_storage_save = False
        if is_anomaly:
            should_save = True
        elif self.trip_started:
            if (now_ts - self.last_db_save_time >= 5.0) or (
                pkt_epoch is not None and self.last_db_packet_epoch > 0 and abs(pkt_epoch - self.last_db_packet_epoch) >= 4.5
            ):
                should_save = True
        else:
            # 창고(A02~A03/B03~B04/C10, 레거시 A01/B12) 실내 보관 중에도 30초 주기로 온습도·조도를 DB에 적재
            if now_ts - self.last_storage_save_time >= 30.0:
                should_save = True
                is_storage_save = True

        if should_save:
            if is_storage_save:
                self.last_storage_save_time = now_ts
                final_status = "보관 [실내]"
            else:
                self.last_db_save_time = now_ts
            if pkt_epoch is not None:
                self.last_db_packet_epoch = pkt_epoch
            if self.trip_started and self.active_run_id:
                run_id_val = self.active_run_id
            elif is_storage_save or not self.trip_started:
                run_id_val = f"{self.truck_id}_보관_{ts_str[:10]}"
            else:
                run_id_val = f"{self.truck_id}_기록_{get_kst_now().strftime('%Y-%m-%d_%H시%M분')}"

            try:
                dt_kst = datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S")
                dt_utc = dt_kst - timedelta(hours=9)
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

def db_worker_thread():
    print(f"[DB Worker] Dual-Write 스레드 시작 ({MYSQL_DATABASE} + {MYSQL_V2_DATABASE})", flush=True)
    conn = None

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
        print(f" [DAEMON READY] 24/7 Dual-Write ({MYSQL_DATABASE} + {MYSQL_V2_DATABASE}) 대기 중...\n", flush=True)
    else:
        print(f" [HiveMQ Connect FAIL] rc={rc}", flush=True)

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload_str = msg.payload.decode('utf-8', errors='replace').strip()
        data = json.loads(payload_str)

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
def main():
    print(f"\n=======================================================")
    print(f" ColdChain DigitalTwin Cloud Backend Daemon v2.0 (Dual-Write) ")
    print(f" Target MySQL: {MYSQL_HOST}:{MYSQL_PORT} -> [{MYSQL_DATABASE} & {MYSQL_V2_DATABASE}] ")
    print(f" Target HiveMQ: {MQTT_BROKER}:{MQTT_PORT} ")
    print(f" Monitored Fleet: 1호차 ~ 4호차 전체 (truck01 ~ truck04) ")
    print(f"=======================================================\n", flush=True)

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
