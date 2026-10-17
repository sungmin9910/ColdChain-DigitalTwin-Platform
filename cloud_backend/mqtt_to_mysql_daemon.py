import json
import time
import os
import sys
from datetime import datetime, timezone, timedelta
import queue
import threading
import paho.mqtt.client as mqtt
import pymysql

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ----------------------------------------------------------------
# 1. 설정 (환경변수 우선, secrets.toml / 기본값 폴백)
# ----------------------------------------------------------------
MYSQL_HOST = os.environ.get("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "lab225")

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
        ts_str = str(payload.get('timestamp_str') or get_kst_now().strftime("%Y-%m-%d %H:%M:%S"))

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
                if len(ts_str) >= 16 and not ts_str.startswith("2026-10-01") and not ts_str.startswith("00:00"):
                    dt_part = ts_str[:16].replace(" ", "_").replace(":", "시") + "분"
                    new_run = f"{self.truck_id}_주행_{dt_part}"
                else:
                    new_run = f"{self.truck_id}_주행_{get_kst_now().strftime('%Y-%m-%d_%H시%M분')}"
                self.active_run_id = new_run
                self.trip_started = True
                print(f"[{self.truck_id}] [START] 새 주행 세션 자동 시작: '{new_run}' (출발시각: {ts_str})", flush=True)

        # 터널 보정
        is_in_tunnel = False
        if not gps_is_valid and self.trip_started and self.last_valid_gps != (0.0, 0.0):
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
            final_status = "대기 [실내]"
        else:
            final_status = f"정상 {loc_tag}"[:48]

        # DB 저장 조건 판정 (스마트 필터링)
        # 1) 충격 및 급변 이상치는 실내외 무관하게 100% 무조건 즉시 저장!
        # 2) 주행 중(trip_started)에는 5초 주기 정주기 저장!
        # 3) 실내 단순 대기는 DB 낭비 방지를 위해 저장 생략
        should_save = False
        if is_anomaly:
            should_save = True
        elif self.trip_started:
            if now_ts - self.last_db_save_time >= 5.0:
                should_save = True

        if should_save:
            self.last_db_save_time = now_ts
            run_id_val = self.active_run_id or f"{self.truck_id}_기록_{get_kst_now().strftime('%Y-%m-%d_%H시%M분')}"
            
            # UTC created_at 계산
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
# 3. 비동기 DB 작업자 (Queue Worker with Auto-Reconnect)
# ----------------------------------------------------------------
db_queue = queue.Queue(maxsize=10000)

def db_worker_thread():
    print("[DB Worker] MySQL 저장 백그라운드 스레드 시작", flush=True)
    conn = None

    def get_conn():
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            autocommit=True
        )

    while True:
        record = db_queue.get()
        if record is None:
            break

        # 연결 검증 및 자동 재연결
        retry = 0
        while retry < 3:
            try:
                if conn is None:
                    conn = get_conn()
                else:
                    conn.ping(reconnect=True)

                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO sensor_data 
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
                    cur.execute(sql, val)
                
                print(f"  [DB INSERT] [{record['device']}] run='{record['run_id']}' ts={record['timestamp_str']} spd={record['speed']:.1f} g={record['g_force']:.2f}G ({record['status']})", flush=True)
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
        # 1호차 ~ 4호차 토픽 일괄 구독
        for topic in TRUCK_MAPPING.keys():
            client.subscribe(topic)
            print(f"  + Subscribed: {topic}", flush=True)
        print(f" [DAEMON READY] 24/7 실시간 자동 수신 및 DB 적재 대기 중...\n", flush=True)
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
    print(f" ColdChain DigitalTwin Cloud Backend Daemon v1.0 ")
    print(f" Target MySQL: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE} ")
    print(f" Target HiveMQ: {MQTT_BROKER}:{MQTT_PORT} ")
    print(f" Monitored Fleet: 1호차 ~ 4호차 전체 (truck01 ~ truck04) ")
    print(f"=======================================================\n", flush=True)

    # DB 워커 스레드 시작
    t = threading.Thread(target=db_worker_thread, daemon=True)
    t.start()

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
