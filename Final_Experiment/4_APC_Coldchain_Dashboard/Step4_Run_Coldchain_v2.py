import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd
import time
import sys
from datetime import datetime, timezone, timedelta
import queue
import pydeck as pdk
import pymysql
import altair as alt

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 한국 표준시 (KST, UTC+9) 설정
KST = timezone(timedelta(hours=9))

def get_kst_now():
    return datetime.now(KST)

def generate_run_id():
    now_kst = get_kst_now()
    return f"주행_{now_kst.strftime('%Y-%m-%d_%H시%M분')}"

# 세션 분할 방지 및 브라우저 새로고침 간 활성 세션 보존용 공유 트래커
@st.cache_resource
def get_session_tracker():
    return {
        "active_run_id": None,
        "is_custom": False,
        "last_packet_epoch": 0,
        "start_ts_str": None
    }


# ----------------------------------------------------------------
# 1. 설정 및 공유 자원 초기화
# ----------------------------------------------------------------
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# 독립 관제 차량 및 단말 매핑 (개별 분리)
TRUCK_OPTIONS = {
    'truck02': {
        'name_ko': '2호차 (truck02 / carrier-c6-02) [현재 연결]',
        'name_en': 'Truck 02 (carrier-c6-02) [Connected]',
        'topic': 'coldchain/truck02/sensor',
        'device_id': 'carrier-c6-02',
    },
    'truck01': {
        'name_ko': '1호차 (truck01 / carrier-c6-01)',
        'name_en': 'Truck 01 (carrier-c6-01)',
        'topic': 'coldchain/truck01/sensor',
        'device_id': 'carrier-c6-01',
    }
}

# --- 다국어 설정 (Localization) ---
LANG_DICT = {
    'KO': {
        'page_title': "프리미엄 콜드체인 통합 관제",
        'topic_running': "**실시간 수신 중...** (Topic: `{}`)",
        'sidebar_title': "🎛️ APC 관제 & 실험 관리",
        'sidebar_desc': "차량 실시간 수송 관제 및 주행 실험 모니터링",
        'sidebar_reset_btn': "🚀 새 실험 세션 시작",
        'reset_success': "새로운 실험 세션이 시작되었습니다! 🚀",
        'reset_failed': "DB 초기화 실패: {}",
        'metric_temp': "온도",
        'metric_humi': "습도",
        'metric_lux': "조도",
        'metric_gforce': "충격량",
        'metric_speed': "현재 속도",
        'map_title': "📍 차량 위치 및 이동 경로",
        'chart_g_speed': "💥 과일 충격량(G-Force) & 차량 속도(km/h) 상관관계",
        'chart_lux': "💡 실시간 조도 변화 (Lux)",
        'chart_env': "🌡️ 온도/습도 변화",
        'log_title': "📋 실시간 로그",
        'gps_wait': "GPS 수신 대기 중 (이동 경로를 표시하려면 위경도 데이터가 필요합니다)...",
        'evt_shock': "🚨 강한 충격",
        'evt_light': "💡 조도 급변",
        'evt_temp': "🌡️ 온도 급변",
        'evt_humi': "💧 습도 급변",
        'evt_current': "🚚 현재 위치",
        'tooltip_format': "{event_type}\n시간: {timestamp}\n온도: {temperature:.1f}°C\n습도: {humidity:.1f}%\n충격: {g_force:.2f}G\n조도: {lux:.0f}lx",
        'select_lang': "🌐 언어 선택 / Language",
    },
    'EN': {
        'page_title': "Premium Cold Chain Integrated Monitoring",
        'topic_running': "**Receiving in Real-time...** (Topic: `{}`)",
        'sidebar_title': "🎛️ APC Control & Experiment",
        'sidebar_desc': "Vehicle real-time transport telemetry & test monitoring",
        'sidebar_reset_btn': "🚀 Start New Test Session",
        'reset_success': "New experiment session started! 🚀",
        'reset_failed': "Failed to reset DB: {}",
        'metric_temp': "Temperature",
        'metric_humi': "Humidity",
        'metric_lux': "Illuminance",
        'metric_gforce': "Impact (G)",
        'metric_speed': "Current Speed",
        'map_title': "📍 Vehicle Location & Route",
        'chart_g_speed': "💥 Fruit Impact (G) & Speed (km/h) Correlation",
        'chart_lux': "💡 Real-time Illuminance (Lux)",
        'chart_env': "🌡️ Temperature & Humidity Changes",
        'log_title': "📋 Real-time Logs",
        'gps_wait': "Waiting for GPS signals (coordinates are required to display the route)...",
        'evt_shock': "🚨 Hard Impact",
        'evt_light': "💡 Sudden Light Change",
        'evt_temp': "🌡️ Sudden Temp Change",
        'evt_humi': "💧 Sudden Humidity Change",
        'evt_current': "🚚 Current Location",
        'tooltip_format': "{event_type}\nTime: {timestamp}\nTemp: {temperature:.1f}°C\nHumidity: {humidity:.1f}%\nImpact: {g_force:.2f}G\nLight: {lux:.0f}lx",
        'select_lang': "Language Selection",
    }
}

if 'lang' not in st.session_state:
    st.session_state.lang = 'KO'
if 'selected_truck_id' not in st.session_state:
    st.session_state.selected_truck_id = 'truck02'
if 'conflict_alert' not in st.session_state:
    st.session_state.conflict_alert = None
if 'conflict_alert_time' not in st.session_state:
    st.session_state.conflict_alert_time = 0.0

tracker = get_session_tracker()
if 'run_id' not in st.session_state:
    if tracker['active_run_id']:
        st.session_state.run_id = tracker['active_run_id']
    else:
        st.session_state.run_id = generate_run_id()
if 'session_user_locked' not in st.session_state:
    st.session_state.session_user_locked = tracker.get('is_custom', False)


st.set_page_config(
    page_title=LANG_DICT[st.session_state.lang]['page_title'],
    page_icon="🚚",
    layout="wide",
)

# 다크 모드와 라이트 모드 모두 어울리는 세련된 디자인 적용
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 36px;
        color: #00d4ff;
    }
    [data-testid="stMetricLabel"] {
        font-size: 20px;
        font-weight: bold;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* 테이블 및 일반 텍스트 폰트 확대 */
    .stDataFrame td, .stDataFrame th {
        font-size: 15px !important;
    }
    /* 세그먼트 컨트롤 및 필터 버튼 중앙 정렬 및 여백 */
    [data-testid="stSegmentedControl"], [data-testid="stPills"], [data-testid="stRadio"] {
        display: flex;
        justify-content: center;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 반응형 토글 컨트롤 렌더링 헬퍼 (모든 Streamlit 버전 호환)
def render_segmented_toggle(label, options, default, key):
    if hasattr(st, "segmented_control"):
        val = st.segmented_control(label, options=options, default=default, key=key, label_visibility="collapsed")
    elif hasattr(st, "pills"):
        val = st.pills(label, options=options, default=default, key=key, label_visibility="collapsed")
    else:
        val = st.radio(label, options=options, index=options.index(default) if default in options else 0, key=key, horizontal=True, label_visibility="collapsed")
    return val or default

# AWS MySQL 설정
def get_mysql_connection():
    try:
        if "MySQL" in st.secrets:
            conn = pymysql.connect(
                host=st.secrets["MySQL"]["MYSQL_HOST"],
                port=st.secrets["MySQL"].get("MYSQL_PORT", 3306),
                user=st.secrets["MySQL"]["MYSQL_USER"],
                password=st.secrets["MySQL"]["MYSQL_PASSWORD"],
                database=st.secrets["MySQL"]["MYSQL_DATABASE"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
    except Exception as e:
        print(f"MySQL 연결 에러 (secrets.toml 확인 필요): {e}")
    return None

# DB 초기화 (테이블 없으면 자동 생성)
def init_mysql_table():
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device VARCHAR(50),
                    timestamp_str VARCHAR(50),
                    temperature FLOAT,
                    humidity FLOAT,
                    lux FLOAT,
                    g_force FLOAT,
                    speed FLOAT,
                    lat FLOAT,
                    lng FLOAT,
                    status VARCHAR(50),
                    run_id VARCHAR(100) DEFAULT 'default_run',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
            conn.commit()
        except Exception as e:
            print(f"테이블 생성 에러: {e}")
        finally:
            conn.close()

init_mysql_table()

# 데이터 공유를 위한 큐
@st.cache_resource
def get_msg_queue():
    return queue.Queue()

@st.cache_resource
def get_data_history():
    # 실시간 모드는 깨끗한 빈 상태로 시작 (과거 데이터는 드롭다운에서 선택하여 조회)
    return []

@st.cache_data(ttl=300)
def load_run_data(run_id):
    history = []
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM sensor_data WHERE run_id = %s ORDER BY id ASC", (run_id,))
                items = cursor.fetchall()
            
            for item in items:
                ts = item.get("timestamp_str")
                if not ts or ts == "00:00:00" or str(ts).startswith("00:00") or str(ts).startswith("2026-10-01 00:00"):
                    created_at = item.get("created_at")
                    if created_at:
                        ts = (created_at + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                parsed_item = {
                    "device": item.get("device"),
                    "timestamp": ts,
                    "temperature": item.get("temperature", 0.0),
                    "humidity": item.get("humidity", 0.0),
                    "lux": item.get("lux", 0.0),
                    "g_force": item.get("g_force", 0.0),
                    "speed": item.get("speed", 0.0),
                    "lat": item.get("lat", 0.0),
                    "lng": item.get("lng", 0.0),
                    "status": item.get("status"),
                    "run_id": item.get("run_id")
                }
                history.append(parsed_item)
            print(f"MySQL에서 실험 '{run_id}'의 데이터 {len(history)}개를 불러왔습니다.")
        except Exception as e:
            print(f"MySQL 데이터 로드 실패: {e}")
        finally:
            conn.close()
    return history

def save_to_mysql(msg_dict, run_id):
    conn = get_mysql_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            # AWS RDS 시간에 +09:00 적용
            cursor.execute("SET time_zone = '+09:00'")
            
            sql = """
            INSERT INTO sensor_data 
            (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            val = (
                msg_dict.get("device", "unknown"),
                msg_dict.get("timestamp", ""),
                float(msg_dict.get("temperature", 0.0)),
                float(msg_dict.get("humidity", 0.0)),
                float(msg_dict.get("lux", 0.0)),
                float(msg_dict.get("g_force", 0.0)),
                float(msg_dict.get("speed", 0.0)),
                float(msg_dict.get("lat", 0.0)),
                float(msg_dict.get("lng", 0.0)),
                msg_dict.get("status", ""),
                run_id
            )
            cursor.execute(sql, val)
        conn.commit()
    except Exception as e:
        print(f"MySQL 저장 에러: {e}")
    finally:
        conn.close()

msg_queue = get_msg_queue()
data_history = get_data_history()

# ----------------------------------------------------------------
# 2. MQTT 콜백 설정
# ----------------------------------------------------------------
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        # 단말별 전용 토픽 구독 (와일드카드 없이 각각 개별 구독)
        client.subscribe("coldchain/truck01/sensor")
        client.subscribe("coldchain/truck02/sensor")
        print("Connected to HiveMQ Broker! Subscribed to [coldchain/truck01/sensor, coldchain/truck02/sensor]", flush=True)
    else:
        print(f"Failed to connect, return code {rc}", flush=True)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        payload['topic'] = msg.topic
        print(f"[STREAMLIT MQTT on_message] topic={msg.topic}, device={payload.get('device')}", flush=True)
        
        # 보드에서 보낸 시간 정보가 있으면 사용, 없거나 비정상일 경우 현재 시간 생성
        ts_val = payload.get('timestamp_str', '')
        if ts_val and ts_val != "00:00:00" and not str(ts_val).startswith("00:00"):
            payload['timestamp'] = str(ts_val)
        else:
            payload['timestamp'] = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 데이터가 문자열로 올 경우를 대비해 숫자로 변환
        for key in ['temperature', 'humidity', 'lux', 'g_force', 'speed', 'lat', 'lng']:
            if key in payload:
                try:
                    payload[key] = float(payload[key])
                except:
                    pass
        msg_queue.put(payload)
    except Exception as e:
        print(f"Error parsing message: {e}", flush=True)

@st.cache_resource
def start_mqtt_client():
    # 1순위: WebSockets (Port 8000) - Streamlit Community Cloud 및 모든 방화벽/클라우드 완벽 호환
    try:
        try:
            from paho.mqtt.client import CallbackAPIVersion
            client = mqtt.Client(CallbackAPIVersion.VERSION1, transport="websockets")
        except Exception:
            client = mqtt.Client(transport="websockets")
        
        client.ws_set_options(path="/mqtt")
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, 8000, 60)
        client.loop_start()
        print("Connected to HiveMQ via WebSockets (Port 8000) successfully!", flush=True)
        return client
    except Exception as e:
        print(f"WebSocket Port 8000 connection failed: {e}, falling back to standard TCP 1883...", flush=True)

    # 2순위: Standard TCP (Port 1883)
    try:
        try:
            from paho.mqtt.client import CallbackAPIVersion
            client = mqtt.Client(CallbackAPIVersion.VERSION1, transport="tcp")
        except Exception:
            client = mqtt.Client(transport="tcp")
        
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_start()
        print("Connected to HiveMQ via TCP (Port 1883) successfully!", flush=True)
        return client
    except Exception as e:
        print(f"TCP Port 1883 connection failed: {e}", flush=True)
        return client

mqtt_client = start_mqtt_client()

# ----------------------------------------------------------------
# 3. UI 구성
# ----------------------------------------------------------------

# DB에서 고유 run_id 목록 및 메타데이터 가져오기
run_ids = ["실시간 주행 (현재 실험)"]
session_meta_dict = {}

conn = get_mysql_connection()
if conn:
    try:
        with conn.cursor() as cursor:
            # 3건 이상 기록된 정상 세션의 요약 메타데이터(시작/종료, 건수, 최고속도, 온습도) 조회
            # 미동기 더미 타임스탬프(2026-10-01)를 제외하여 실제 시작 시간을 정확하게 추출
            cursor.execute("""
                SELECT run_id, 
                       COUNT(*) as cnt, 
                       MIN(CASE WHEN timestamp_str NOT LIKE '2026-10-01%' AND timestamp_str != '00:00:00' AND timestamp_str IS NOT NULL THEN timestamp_str END) as start_ts, 
                       MAX(timestamp_str) as end_ts,
                       MAX(speed) as max_spd,
                       MIN(temperature) as min_temp,
                       MAX(temperature) as max_temp
                FROM sensor_data 
                WHERE run_id IS NOT NULL 
                GROUP BY run_id 
                HAVING COUNT(*) >= 3 
                ORDER BY MAX(id) DESC
            """)
            rows = cursor.fetchall()
            for r in rows:
                val = r["run_id"]
                if val not in run_ids:
                    run_ids.append(val)
                session_meta_dict[val] = r
    except Exception as e:
        print(f"run_ids 로드 에러: {e}")
    finally:
        conn.close()

with st.sidebar:
    st.markdown(f"### {LANG_DICT[st.session_state.lang]['sidebar_title']}")
    st.caption(LANG_DICT[st.session_state.lang]['sidebar_desc'])
    
    # [0] 관제 대상 차량/단말 독립 선택기
    truck_keys = list(TRUCK_OPTIONS.keys())
    truck_labels = [
        TRUCK_OPTIONS[k]['name_ko'] if st.session_state.lang == 'KO' else TRUCK_OPTIONS[k]['name_en']
        for k in truck_keys
    ]
    cur_truck_idx = truck_keys.index(st.session_state.selected_truck_id) if st.session_state.selected_truck_id in truck_keys else 0
    selected_truck_label = st.radio(
        "🚚 관제 대상 차량 (독립 단말 선택)" if st.session_state.lang == 'KO' else "🚚 Target Vehicle (Isolated)",
        truck_labels,
        index=cur_truck_idx,
        help="단말 혼선 및 데이터 충돌을 방지하기 위해 선택된 단말의 전용 토픽만 독립 수신합니다."
    )
    new_truck_id = truck_keys[truck_labels.index(selected_truck_label)]
    if new_truck_id != st.session_state.selected_truck_id:
        st.session_state.selected_truck_id = new_truck_id
        data_history.clear()
        with msg_queue.mutex:
            msg_queue.queue.clear()
        st.session_state.conflict_alert = None
        st.session_state.conflict_alert_time = 0.0
        st.rerun()

    active_truck = TRUCK_OPTIONS[st.session_state.selected_truck_id]
    MQTT_TOPIC = active_truck['topic']
    EXPECTED_DEVICE = active_truck['device_id']
    
    # [1] 실시간 통신 및 센서 상태 요약 카드 (플레이스홀더)
    sidebar_status_box = st.empty()
    sidebar_status_box.markdown("""
    <div style="background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 5px;">
        <div style="font-size: 13px; font-weight: bold; color: #aaa; margin-bottom: 6px;">📡 실시간 데이터 대기 중...</div>
        <div style="font-size: 12px; line-height: 1.6; color: #888;">
            • 센서 노드(Beetle C6) 전원을 켜시면<br>
            • 5초 주기로 데이터가 자동 갱신됩니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # [2] 지능형 동적 세션 라벨 생성기 (중복 원천 방지 & 미래 세션 100% 자동 지원)
    def format_session_label(session_id):
        if session_id == "실시간 주행 (현재 실험)":
            return "🟢 실시간 주행 (현재 실험)"
        
        meta = session_meta_dict.get(session_id)
        if meta:
            cnt = meta.get('cnt', 0)
            start_ts = str(meta.get('start_ts', ''))
            max_spd = float(meta.get('max_spd') or 0.0)
            min_temp = float(meta.get('min_temp') or 0.0)
            max_temp = float(meta.get('max_temp') or 0.0)
            
            # 날짜 및 시각 태그 생성 (MM-DD HH:MM)
            dt_tag = f"[{start_ts[5:10]} {start_ts[11:16]}]" if len(start_ts) >= 16 else ""

            # 1) 유명 핵심 기준 세션 매핑
            if "departure" in session_id:
                return f"🚗 [10-02 편도출발] 전주 ➔ 대전 (89km, {cnt:,}건)"
            elif "return" in session_id:
                return f"🚗 [10-02 편도복귀] 대전 ➔ 전주 (85km, {cnt:,}건)"
            elif "30km" in session_id:
                return f"📦 [07-15 모의주행] 30km 표준 시뮬레이션 ({cnt}건)"
            elif "065739" in session_id:
                return f"🧪 [10-01 야외검증] 캠퍼스 GPS 텔레메트리 ({cnt}건)"

            # 2) 지능형 자동 분류 (주행 vs 급랭/챔버 vs 정적실험)
            clean_name = session_id
            for pfx in ["run_", "주행_"]:
                if clean_name.startswith(pfx):
                    clean_name = clean_name[len(pfx):]
            if len(clean_name) > 20:
                clean_name = clean_name[:18] + ".."

            if "fridge" in session_id or "냉장고" in session_id or (max_temp - min_temp >= 4.0 and max_spd < 5.0):
                return f"❄️ {dt_tag} {clean_name} ({cnt}건, {max_temp:.1f}°C➔{min_temp:.1f}°C)"
            elif max_spd >= 15.0 or "주행" in session_id or "driving" in session_id:
                return f"🚗 {dt_tag} {clean_name} ({cnt}건, 최고 {max_spd:.0f}km/h)"
            else:
                return f"🧪 {dt_tag} {clean_name} ({cnt}건, {min_temp:.1f}°C)"

        return f"📂 {session_id}"

    selected_run = st.selectbox(
        "📂 조회할 세션 선택" if st.session_state.lang == 'KO' else "📂 Select Session",
        run_ids, 
        index=0,
        format_func=format_session_label,
        help="실시간 데이터를 보려면 '실시간 주행 (현재 실험)'을 선택하고, 과거 실험 데이터를 확인하려면 목록에서 선택하세요."
    )
    
    static_history = []
    if selected_run == "실시간 주행 (현재 실험)":
        # 🔴 DB 실시간 저장 제어 (기본값: 스마트 자동 - 주행/터널/충격 시 자동 기록)
        db_mode_options = [
            "🤖 스마트 자동 (주행/터널/충격 시 자동 기록)" if st.session_state.lang == 'KO' else "🤖 Smart Auto (Save on Trip & Shock)",
            "🔴 항상 저장 (수동 강제 저장)" if st.session_state.lang == 'KO' else "🔴 Always Save (Force ON)",
            "⚪ 저장 안함 (연구실 모니터링)" if st.session_state.lang == 'KO' else "⚪ Do Not Save (Lab Monitoring)"
        ]
        db_record_mode = st.radio(
            "💾 DB 저장 모드 설정" if st.session_state.lang == 'KO' else "💾 DB Recording Mode",
            db_mode_options,
            index=0,
            help="• 스마트 자동 (기본값): 야외 출발 시(GPS Fix/속도 발생) 자동으로 기록을 시작하며, 터널/지하차도에 진입하여 일시적으로 GPS가 끊기더라도 직전 위치를 유지하며 연속 기록합니다. 충격/급변 발생 시 실내외 무관하게 100% 즉시 저장됩니다.\n• 항상 저장: GPS 수신 여부와 관계없이 실시간으로 DB에 저장합니다.\n• 저장 안함: DB 저장을 완전히 차단하고 화면 모니터링만 수행합니다."
        )
        if "스마트 자동" in db_record_mode or "Smart Auto" in db_record_mode:
            st.caption("✨ **주행 감지 시 자동 기록** (터널 통과 연속 보존, 실내 대기 저장 차단)")
        elif "항상 저장" in db_record_mode or "Always Save" in db_record_mode:
            st.caption("🔴 **[수동 강제 ON]** 모든 데이터를 즉시 DB에 저장합니다.")
        else:
            st.caption("⚪ **[연구실 모드]** DB 저장이 차단된 모니터링 전용 상태입니다.")

        st.markdown(f"**🏷️ 현재 활성 세션 ID**  \n`{st.session_state.run_id}`")
        new_run_input = st.text_input(
            "새 세션 이름 (선택사항)" if st.session_state.lang == 'KO' else "New Session Name (Optional)",
            placeholder="미입력 시 현재 시간으로 자동 생성" if st.session_state.lang == 'KO' else "Auto-generated if empty"
        )
        
        lock_session = st.checkbox(
            "🔒 세션 ID 고정 (정차/신호대기 시 분할 방지)" if st.session_state.lang == 'KO' else "🔒 Lock Session ID (Prevent Split)",
            value=st.session_state.get('session_user_locked', True),
            help="체크 시 3분 이상 정차하거나 터널/음영구간을 통과해도 세션 ID가 자동으로 새로 생성되지 않고 단일 세션으로 계속 유지됩니다."
        )
        st.session_state.session_user_locked = lock_session
        
        # 버튼 텍스트 잘림 해결 (풀위드 1열 배치)
        if st.button("🚀 새 실험 세션 시작 (화면 리셋)" if st.session_state.lang == 'KO' else "🚀 Start New Session", type="primary", use_container_width=True):
            tracker = get_session_tracker()
            if new_run_input.strip():
                st.session_state.run_id = new_run_input.strip()
                tracker['active_run_id'] = new_run_input.strip()
                tracker['is_custom'] = True
                st.session_state.session_user_locked = True
            else:
                tracker['active_run_id'] = None
                tracker['is_custom'] = False
                tracker['start_ts_str'] = None
                st.session_state.run_id = generate_run_id()
                st.session_state.session_user_locked = False
            
            # 주행 세션 및 GPS 보정 리셋
            st.session_state.trip_started = False
            st.session_state.last_valid_gps = (0.0, 0.0)
            
            # 메모리 비우기
            data_history.clear()
            with msg_queue.mutex:
                msg_queue.queue.clear()
            st.success(f"새 세션 시작: {st.session_state.run_id}")
            time.sleep(0.8)
            st.rerun()
            
        if st.button("🧹 화면 차트 비우기 (Clear Display)" if st.session_state.lang == 'KO' else "🧹 Clear Screen History", use_container_width=True):
            data_history.clear()
            with msg_queue.mutex:
                msg_queue.queue.clear()
            st.info("화면의 실시간 임시 데이터가 초기화되었습니다.")
            time.sleep(0.5)
            st.rerun()
    else:
        db_record_mode = "⚪ 저장 안함"
        static_history = load_run_data(selected_run)
        
        sidebar_status_box.markdown(f"""
        <div style="background-color: rgba(255, 165, 0, 0.08); border: 1px solid rgba(255, 165, 0, 0.35); border-radius: 8px; padding: 12px; margin-bottom: 5px;">
            <div style="font-size: 13.5px; font-weight: bold; color: #ffa500; margin-bottom: 6px;">📂 과거 실험 조회 모드</div>
            <div style="font-size: 12px; line-height: 1.7; color: #e0e0e0;">
                • <b>선택 세션:</b> <code>{selected_run}</code><br>
                • <b>기록 데이터:</b> <b style="color:#ffa500;">{len(static_history)}</b>건
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"📂 과거 실험 데이터 `{selected_run}`을 조회 중입니다.")
        
        if len(static_history) > 0:
            df_export = pd.DataFrame(static_history)
            st.download_button(
                "📥 이 실험 데이터 CSV 다운로드" if st.session_state.lang == 'KO' else "📥 Download Session CSV",
                data=df_export.to_csv(index=False).encode('utf-8-sig'),
                file_name=f"{selected_run}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"btn_csv_export_{selected_run}"
            )

col_header, col_lang = st.columns([8.2, 1.8])
with col_header:
    st.markdown(f"<h1 style='text-align: left; font-size: 40px; font-weight: 800; margin-bottom: 5px;'>{LANG_DICT[st.session_state.lang]['page_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: left; font-size: 16px; margin-bottom: 20px; color: #515154;'>{LANG_DICT[st.session_state.lang]['topic_running'].format(MQTT_TOPIC)}</p>", unsafe_allow_html=True)
with col_lang:
    selected_lang_label = st.selectbox(
        "🌐 Language", 
        ["English (EN)", "한국어 (KO)"], 
        index=0 if st.session_state.lang == 'EN' else 1,
        key="lang_selector",
        label_visibility="collapsed"
    )
    lang_key = 'EN' if "English" in selected_lang_label else 'KO'
    if lang_key != st.session_state.lang:
        st.session_state.lang = lang_key
        st.rerun()

# 단말 혼선 / 충돌 경고 배너
conflict_alert_ph = st.empty()
if st.session_state.get('conflict_alert') and (time.time() - st.session_state.get('conflict_alert_time', 0) < 20):
    conflict_alert_ph.error(st.session_state['conflict_alert'])
else:
    conflict_alert_ph.empty()

# 상단 5대 지표 레이아웃
m1, m2, m3, m4, m5 = st.columns(5)
temp_metric = m1.empty()
humi_metric = m2.empty()
lux_metric = m3.empty()
gforce_metric = m4.empty()
speed_metric = m5.empty()

# Row 1: 지도 및 조도 차트
col1_row1, col2_row1 = st.columns(2)

with col1_row1:
    st.markdown(f"<h3 style='text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 10px;'>{LANG_DICT[st.session_state.lang]['map_title']}</h3>", unsafe_allow_html=True)
    map_container = st.empty()

with col2_row1:
    st.markdown(f"<h3 style='text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 10px;'>{LANG_DICT[st.session_state.lang]['chart_lux']}</h3>", unsafe_allow_html=True)
    lux_chart = st.empty()

# Row 2: 충격량/속도 차트 및 온습도 차트 (개별/통합 토글 지원)
col1_row2, col2_row2 = st.columns(2)

with col1_row2:
    st.markdown(f"<h3 style='text-align: center; font-size: 26px; font-weight: bold; margin-bottom: 6px; margin-top: 15px;'>{LANG_DICT[st.session_state.lang]['chart_g_speed']}</h3>", unsafe_allow_html=True)
    g_filter_opts = ["💥+🚗 충격량+속도", "💥 충격량만", "🚗 속도만"] if st.session_state.lang == 'KO' else ["💥+🚗 All (Dual)", "💥 Impact Only", "🚗 Speed Only"]
    render_segmented_toggle("G-Force Filter", options=g_filter_opts, default=g_filter_opts[0], key="filter_g_chart")
    gforce_chart = st.empty()

with col2_row2:
    st.markdown(f"<h3 style='text-align: center; font-size: 26px; font-weight: bold; margin-bottom: 6px; margin-top: 15px;'>{LANG_DICT[st.session_state.lang]['chart_env']}</h3>", unsafe_allow_html=True)
    env_filter_opts = ["🌡️+💧 온습도 전체", "🌡️ 온도만", "💧 습도만"] if st.session_state.lang == 'KO' else ["🌡️+💧 All (Dual)", "🌡️ Temp Only", "💧 Humi Only"]
    render_segmented_toggle("Env Filter", options=env_filter_opts, default=env_filter_opts[0], key="filter_env_chart")
    env_chart = st.empty()

st.markdown("---")
col_log_h1, col_log_h2 = st.columns([7.5, 2.5])
with col_log_h1:
    st.markdown(f"<h3 style='text-align: left; font-size: 28px; font-weight: bold; margin-bottom: 10px;'>{LANG_DICT[st.session_state.lang]['log_title']}</h3>", unsafe_allow_html=True)
with col_log_h2:
    if selected_run != "실시간 주행 (현재 실험)" and len(static_history) > 0:
        df_full_log = pd.DataFrame(static_history)
        st.download_button(
            f"📥 전체 CSV 다운로드 ({len(static_history)}건)" if st.session_state.lang == 'KO' else f"📥 Download Full CSV ({len(static_history)})",
            data=df_full_log.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"{selected_run}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"btn_log_header_dl_{selected_run}"
        )
    elif selected_run == "실시간 주행 (현재 실험)":
        if st.button("🧹 실시간 로그 비우기" if st.session_state.lang == 'KO' else "🧹 Clear Live Log", key="btn_clear_live_log", use_container_width=True):
            data_history.clear()
            with msg_queue.mutex:
                msg_queue.queue.clear()
            st.rerun()
log_container = st.empty()

# ----------------------------------------------------------------
# 4. 실시간 루프
# ----------------------------------------------------------------
last_db_save_time = 0
last_db_packet_epoch = 0

while True:
    # 1) 실시간 패킷 항시 처리 (과거 세션 조회 중에도 실시간 데이터 유실 방지)
    while not msg_queue.empty():
        msg = msg_queue.get()
        incoming_dev = str(msg.get("device", "")).strip()
        incoming_topic = str(msg.get("topic", "")).strip()
        print(f"[STREAMLIT LOOP] processing packet: dev={incoming_dev}, expected={EXPECTED_DEVICE}, topic={incoming_topic}", flush=True)

        # ⚠️ 단말 혼선 및 충돌 검출: 현재 선택된 차량/단말과 일치하지 않으면 차단 및 오류 표시
        if incoming_dev and incoming_dev != EXPECTED_DEVICE:
            st.session_state.conflict_alert = (
                f"🚨 **[단말 혼선 및 충돌 오류 감지]** 현재 대시보드는 **'{active_truck['name_ko']}'** (`{EXPECTED_DEVICE}`) 전용으로 동작 중입니다. "
                f"그러나 다른 단말인 **`{incoming_dev}`** (수신 토픽: `{incoming_topic}`)의 데이터가 유입되었습니다!\n\n"
                f"⚠️ 데이터 혼재 방지를 위해 해당 패킷을 차단했습니다. 관제하려는 보드에 맞게 사이드바에서 차량을 변경하거나 다른 보드의 전원을 확인하세요."
            )
            st.session_state.conflict_alert_time = time.time()
            continue

        if incoming_topic and incoming_topic != MQTT_TOPIC:
            st.session_state.conflict_alert = (
                f"🚨 **[토픽 불일치 오류]** 현재 설정된 토픽(`{MQTT_TOPIC}`)이 아닌 다른 토픽(`{incoming_topic}`)에서 패킷이 수신되었습니다!"
            )
            st.session_state.conflict_alert_time = time.time()
            continue

        if time.time() - st.session_state.get('conflict_alert_time', 0) > 15:
            st.session_state.conflict_alert = None

        msg['run_id'] = st.session_state.run_id
        
        # --- 다중 복합 이벤트 감지 (충격, 조도 급변, 온도 급변) ---
        g_force = float(msg.get('g_force', 1.0))
        lux = float(msg.get('lux', 0.0))
        temp = float(msg.get('temperature', 0.0))
        
        # 직전 수신 데이터 대비 변화량(Delta) 계산
        lux_diff = 0.0
        temp_diff = 0.0
        if len(data_history) > 0:
            prev_msg = data_history[-1]
            lux_diff = lux - float(prev_msg.get('lux', lux))
            temp_diff = temp - float(prev_msg.get('temperature', temp))
        
        detected_events = []
        if g_force >= 1.8:
            detected_events.append(f"충격({g_force:.1f}G)")
        if abs(lux_diff) >= 300.0:
            detected_events.append("조도급변")
        if abs(temp_diff) >= 2.0:
            detected_events.append("온도급변")
        is_anomaly = len(detected_events) > 0

        # 최적화: 스마트 주행 감지 래치 (Smart Trip Latch & Anti-Fragmentation Debounce)
        if 'trip_started' not in st.session_state:
            st.session_state.trip_started = False
        if 'last_valid_gps' not in st.session_state:
            st.session_state.last_valid_gps = (0.0, 0.0)
        if 'last_driving_time' not in st.session_state:
            st.session_state.last_driving_time = 0.0
        if 'standby_packet_count' not in st.session_state:
            st.session_state.standby_packet_count = 0

        incoming_status = str(msg.get("status", ""))
        gps_lat_val = float(msg.get("lat", 0.0))
        gps_lng_val = float(msg.get("lng", 0.0))
        gps_speed_val = float(msg.get("speed", 0.0))
        gps_sats_val = int(msg.get("sats", 0))
        gps_is_valid = (gps_lat_val != 0.0 and gps_lng_val != 0.0)

        # 주행 상태 판정 (GPS 유효 좌표 또는 2.5km/h 이상 속도 감지)
        is_actively_moving = (gps_speed_val > 2.5) or (gps_is_valid and gps_speed_val > 1.0)
        
        now_ts = time.time()
        # 패킷 타임스탬프가 유효하면 타임스탬프 기준 시간도 고려
        ts_val_str = str(msg.get("timestamp") or msg.get("timestamp_str") or "")

        if is_actively_moving or (gps_is_valid and "대기" not in incoming_status):
            st.session_state.last_driving_time = now_ts
            st.session_state.standby_packet_count = 0
            if gps_is_valid:
                st.session_state.last_valid_gps = (gps_lat_val, gps_lng_val)
        else:
            st.session_state.standby_packet_count += 1

        # 주행 종료 디바운스: 연속 36개 패킷(약 3분) 이상 완전 대기 & 속도 0km/h일 때만 종료 판정
        if st.session_state.trip_started:
            if st.session_state.standby_packet_count >= 36 and (now_ts - st.session_state.last_driving_time > 180):
                st.session_state.trip_started = False
                print(f"🛑 [주행 종료] 3분 이상 정지 감지 -> 대기 모드 복귀 (세션: {st.session_state.run_id})")

        # 신규 주행 시작 감지 (세션 분할 방지 락 적용)
        was_stopped = not st.session_state.trip_started
        now_driving = gps_is_valid or (gps_speed_val > 2.5)

        tracker = get_session_tracker()
        # 패킷 타임스탬프 기반 지능형 자동 세션 동기화 (오프라인 덤프 또는 신규 출발 시 실시간 시계 대신 데이터 시각 채택)
        if not tracker.get('is_custom', False) and len(ts_val_str) >= 16 and not ts_val_str.startswith("2026-10-01") and not ts_val_str.startswith("00:00"):
            now_epoch = time.time()
            if tracker['active_run_id'] is None or (now_epoch - tracker.get('last_packet_epoch', 0) > 1800):
                dt_part = ts_val_str[:16].replace(" ", "_").replace(":", "시") + "분"
                new_sync_id = f"주행_{dt_part}"
                tracker['active_run_id'] = new_sync_id
                tracker['start_ts_str'] = ts_val_str
                st.session_state.run_id = new_sync_id
                print(f"🚀 [패킷 기반 세션 동기화] 세션 ID 설정: '{new_sync_id}' (출발시각: {ts_val_str})")
            elif st.session_state.run_id != tracker['active_run_id']:
                st.session_state.run_id = tracker['active_run_id']
        
        tracker['last_packet_epoch'] = time.time()

        if "대기" not in incoming_status and "실내" not in incoming_status:
            if was_stopped and now_driving:
                # 🚗 실내/대기에서 완전 신규 주행 시작 감지
                user_locked = st.session_state.get('session_user_locked', False) or tracker.get('is_custom', False)
                should_create_new_session = (not user_locked) and ((now_ts - st.session_state.last_driving_time > 300) or not st.session_state.run_id)
                
                if should_create_new_session:
                    if len(ts_val_str) >= 16 and not ts_val_str.startswith("2026-10-01 00:00"):
                        dt_part = ts_val_str[:16].replace(" ", "_").replace(":", "시") + "분"
                        st.session_state.run_id = f"주행_{dt_part}"
                    else:
                        st.session_state.run_id = generate_run_id()
                    
                    tracker['active_run_id'] = st.session_state.run_id
                    # 이전 대기 화면 흔적만 안전하게 비우기
                    data_history.clear()
                    print(f"🚀 [신규 주행 세션 개시] 새 세션 '{st.session_state.run_id}' 자동 개시!")
                
                st.session_state.trip_started = True
                st.session_state.last_driving_time = now_ts
                if gps_is_valid:
                    st.session_state.last_valid_gps = (gps_lat_val, gps_lng_val)
            elif now_driving:
                st.session_state.trip_started = True
                st.session_state.last_driving_time = now_ts
                if gps_is_valid:
                    st.session_state.last_valid_gps = (gps_lat_val, gps_lng_val)

        msg['run_id'] = st.session_state.run_id

        # 터널/음영구간 통과 중일 때: 직전 유효 좌표 보정 (0,0으로 튀는 현상 방지)
        is_in_tunnel = False
        if not gps_is_valid and st.session_state.trip_started and st.session_state.last_valid_gps != (0.0, 0.0):
            msg['lat'] = st.session_state.last_valid_gps[0]
            msg['lng'] = st.session_state.last_valid_gps[1]
            is_in_tunnel = True

        # 간결하고 명확한 status 요약 생성 (이모지 제거, 50자 이내 완전 보장)
        if not st.session_state.trip_started or "대기" in incoming_status or "실내" in incoming_status:
            loc_tag = "[대기]"
        elif is_in_tunnel:
            loc_tag = "[터널]"
        elif gps_is_valid:
            loc_tag = f"[GPS {gps_sats_val}]"
        else:
            loc_tag = "[대기]"

        if is_anomaly:
            evt_summary = "/".join(detected_events)
            msg['status'] = f"{evt_summary} {loc_tag}"[:48]
        elif loc_tag == "[대기]":
            msg['status'] = "대기 [실내]"
        else:
            msg['status'] = f"정상 {loc_tag}"[:48]

        data_history.append(msg)

        # 패킷 내 실제 측정 시각 파싱 (버퍼 일괄 수신 시 시계열 보존)
        packet_epoch = None
        ts_str_val = str(msg.get('timestamp') or msg.get('timestamp_str') or '')
        if len(ts_str_val) >= 19 and not ts_str_val.startswith('2026-10-01 00:00'):
            try:
                dt = datetime.strptime(ts_str_val[:19], "%Y-%m-%d %H:%M:%S")
                packet_epoch = dt.timestamp()
            except Exception:
                packet_epoch = None

        current_time = time.time()
        time_interval_met = False
        if packet_epoch is not None and last_db_packet_epoch > 0:
            # 패킷 측정 시각 기준 9초 이상 경과 시
            if abs(packet_epoch - last_db_packet_epoch) >= 9.0:
                time_interval_met = True
        else:
            # 실시간 수신 또는 시간 파싱 불가 시 PC 시각 기준 10초
            if (current_time - last_db_save_time >= 10):
                time_interval_met = True

        should_save_to_db = False
        if "스마트 자동" in db_record_mode or "Smart Auto" in db_record_mode:
            # 1. 충격/급변 이상 징후는 터널/실내 무관하게 무조건 즉시 DB 저장!
            if is_anomaly:
                should_save_to_db = True
            # 2. 주기적 저장: GPS Fix 중이거나, 이미 주행이 시작된 상태(터널/지하차도 포함)일 때 100% 저장!
            elif (gps_is_valid or st.session_state.trip_started) and time_interval_met:
                should_save_to_db = True
        elif "항상 저장" in db_record_mode or "Always Save" in db_record_mode:
            if time_interval_met or is_anomaly:
                should_save_to_db = True
        else:
            should_save_to_db = False

        if should_save_to_db:
            save_to_mysql(msg, st.session_state.run_id)  
            last_db_save_time = current_time
            if packet_epoch is not None:
                last_db_packet_epoch = packet_epoch
        if len(data_history) > 3600:
            data_history.pop(0)

    # 2) 화면에 표시할 데이터 선택
    if selected_run == "실시간 주행 (현재 실험)":
        display_history = data_history
    else:
        display_history = static_history

    if len(display_history) > 0:
        latest = display_history[-1]
        
        # 메트릭 업데이트 (값이 없을 경우를 대비해 0.0 처리)
        temp_metric.metric(LANG_DICT[st.session_state.lang]['metric_temp'], f"{latest.get('temperature', 0):.1f} °C")
        humi_metric.metric(LANG_DICT[st.session_state.lang]['metric_humi'], f"{latest.get('humidity', 0):.1f} %")
        lux_metric.metric(LANG_DICT[st.session_state.lang]['metric_lux'], f"{latest.get('lux', 0):.0f} lx")
        gforce_metric.metric(LANG_DICT[st.session_state.lang]['metric_gforce'], f"{latest.get('g_force', 0):.2f} G")
        speed_metric.metric(LANG_DICT[st.session_state.lang]['metric_speed'], f"{latest.get('speed', 0):.1f} km/h")
        
        # 사이드바 실시간 상태 카드 업데이트 (실시간 모드일 때만 동적 갱신)
        if selected_run == "실시간 주행 (현재 실험)":
            gps_lat = latest.get('lat', 0.0)
            gps_lng = latest.get('lng', 0.0)
            gps_sats = latest.get('sats', 0)
            if gps_lat != 0.0 and gps_lng != 0.0:
                gps_badge = f"<span style='color:#00ff88; font-weight:bold;'>🟢 Fix 완료 (위성 {gps_sats}개)</span>"
            else:
                gps_badge = f"<span style='color:#ffaa00; font-weight:bold;'>🟡 위성 탐색 중 ({gps_sats}개)</span>" if gps_sats > 0 else "<span style='color:#ffaa00; font-weight:bold;'>🟡 위성 신호 탐색 중</span>"
                
            # DB 저장 상태 뱃지 판정
            if "스마트 자동" in db_record_mode or "Smart Auto" in db_record_mode:
                if gps_lat != 0.0 and gps_lng != 0.0:
                    db_badge = "<span style='color:#00ff88; font-weight:bold;'>🔴 스마트 자동 기록 중 (GPS Fix)</span>"
                elif st.session_state.get('trip_started', False):
                    db_badge = "<span style='color:#00e5ff; font-weight:bold;'>🔵 스마트 주행 기록 중 (터널/음영구간)</span>"
                else:
                    db_badge = "<span style='color:#888888; font-weight:bold;'>⚪ 자동 대기 (실내/출발전)</span>"
            elif "항상 저장" in db_record_mode or "Always Save" in db_record_mode:
                db_badge = "<span style='color:#ff4444; font-weight:bold;'>🔴 상시 강제 기록 중</span>"
            else:
                db_badge = "<span style='color:#888888; font-weight:bold;'>⚪ 기록 차단됨 (모니터링)</span>"

            dev_id = latest.get('device', EXPECTED_DEVICE)
            ts_str = latest.get('timestamp', '-')
            
            conflict_badge = ""
            if st.session_state.get('conflict_alert') and (time.time() - st.session_state.get('conflict_alert_time', 0) < 20):
                conflict_badge = "<br>• <b style='color:#ff4d4f;'>⚠️ 단말 충돌 오류 감지됨!</b>"

            sidebar_status_box.markdown(f"""
            <div style="background-color: rgba(0, 212, 255, 0.08); border: 1px solid rgba(0, 212, 255, 0.35); border-radius: 8px; padding: 12px; margin-bottom: 5px;">
                <div style="font-size: 13.5px; font-weight: bold; color: #00d4ff; margin-bottom: 6px;">📡 실시간 데이터 수신 상태</div>
                <div style="font-size: 12px; line-height: 1.7; color: #e0e0e0;">
                    • <b>관제 대상:</b> <code>{active_truck['name_ko']}</code><br>
                    • <b>수신 단말:</b> <code>{dev_id}</code><br>
                    • <b>GPS 상태:</b> {gps_badge}<br>
                    • <b>DB 상태:</b> {db_badge}<br>
                    • <b>최근 패킷:</b> <code>{ts_str}</code><br>
                    • <b>현재 세션 수집:</b> <b style="color:#00d4ff;">{len(display_history)}</b>건{conflict_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ----------------------------------------------------------------
        # 5. 고도화된 지도 시각화 (Pydeck)
        # ----------------------------------------------------------------
        df_gps = pd.DataFrame(display_history)
        # 유효한 GPS 데이터만 필터링
        df_gps = df_gps[(df_gps['lat'] != 0) & (df_gps['lng'] != 0)]
        
        if not df_gps.empty:
            # 중심점 계산
            view_state = pdk.ViewState(
                latitude=df_gps['lat'].iloc[-1],
                longitude=df_gps['lng'].iloc[-1],
                zoom=14,
                pitch=45,
            )
 
            # 변화량 계산 (급격한 변화 감지용)
            df_gps['temp_diff'] = df_gps['temperature'].diff().abs().fillna(0)
            df_gps['humi_diff'] = df_gps['humidity'].diff().abs().fillna(0)
            df_gps['lux_diff'] = df_gps['lux'].diff().abs().fillna(0)
 
            # 1. 이동 경로 레이어 (밝은 배경에서 가독성을 높이기 위해 선명한 진한 회색으로 변경 및 두께 조정)
            path_layer = pdk.Layer(
                "PathLayer",
                data=[{"path": df_gps[['lng', 'lat']].values.tolist()}],
                get_path="path",
                get_color=[70, 70, 70, 220], 
                width_min_pixels=5,
            )
 
            # 2. 충격 지점 (강한 충격 > 1.8G) - 빨간색 (반지름 45)
            shock_df = df_gps[df_gps['g_force'] > 1.8].copy()
            shock_df['event_type'] = LANG_DICT[st.session_state.lang]['evt_shock']
            shock_df['icon'] = "🚨"
            shock_layer = pdk.Layer(
                "ScatterplotLayer",
                data=shock_df,
                get_position="[lng, lat]",
                get_fill_color=[255, 0, 0, 80],
                get_line_color=[255, 0, 0, 255],
                stroked=True,
                get_radius=45,
                pickable=True,
            )
 
            # 3. 조도 급변 지점 (Delta > 300 lx) - 밝은 배경에서도 잘 보이도록 진한 골드/오렌지톤으로 변경 (반지름 35)
            light_df = df_gps[df_gps['lux_diff'] > 300].copy()
            light_df['event_type'] = LANG_DICT[st.session_state.lang]['evt_light']
            light_df['icon'] = "💡"
            light_layer = pdk.Layer(
                "ScatterplotLayer",
                data=light_df,
                get_position="[lng, lat]",
                get_fill_color=[240, 160, 0, 100],
                get_line_color=[200, 100, 0, 255],
                stroked=True,
                get_radius=35,
                pickable=True,
            )
 
            # 4. 온도 급변 지점 (Delta > 1.5°C) - 주황색 (반지름 25)
            temp_df = df_gps[df_gps['temp_diff'] > 1.5].copy()
            temp_df['event_type'] = LANG_DICT[st.session_state.lang]['evt_temp']
            temp_df['icon'] = "🌡️"
            temp_layer = pdk.Layer(
                "ScatterplotLayer",
                data=temp_df,
                get_position="[lng, lat]",
                get_fill_color=[255, 128, 0, 80],
                get_line_color=[255, 128, 0, 255],
                stroked=True,
                get_radius=25,
                pickable=True,
            )
 
            # 5. 습도 급변 지점 (Delta > 5%) - 파란색 (반지름 15)
            humi_df = df_gps[df_gps['humi_diff'] > 5.0].copy()
            humi_df['event_type'] = LANG_DICT[st.session_state.lang]['evt_humi']
            humi_df['icon'] = "💧"
            humi_layer = pdk.Layer(
                "ScatterplotLayer",
                data=humi_df,
                get_position="[lng, lat]",
                get_fill_color=[0, 128, 255, 80],
                get_line_color=[0, 128, 255, 255],
                stroked=True,
                get_radius=15,
                pickable=True,
            )
 
            # 6. 현재 위치 레이어 (마지막 수신 위치) - 파란색 원형 마커 (반지름 30)
            current_df = df_gps.iloc[[-1]].copy()
            current_df['event_type'] = LANG_DICT[st.session_state.lang]['evt_current']
            current_df['icon'] = "🚚"
            current_layer = pdk.Layer(
                "ScatterplotLayer",
                data=current_df,
                get_position="[lng, lat]",
                get_fill_color=[0, 120, 255, 200],
                get_line_color=[255, 255, 255, 255],
                stroked=True,
                get_radius=30,
                pickable=True,
            )
 
            # 모든 이벤트 데이터를 합쳐서 텍스트 아이콘 레이어 생성 (현재 위치 아이콘 포함)
            all_events = pd.concat([shock_df, light_df, temp_df, humi_df, current_df]).drop_duplicates(subset=['timestamp', 'icon']) if not (shock_df.empty and light_df.empty and temp_df.empty and humi_df.empty and current_df.empty) else pd.DataFrame()
 
            icon_layer = pdk.Layer(
                "TextLayer",
                data=all_events,
                get_position="[lng, lat]",
                get_text="icon",
                get_size=20,
                get_alignment_baseline="'center'",
            )
 
            tooltip_text = (
                "{event_type}\n시간: {timestamp}\n온도: {temperature}°C\n습도: {humidity}%\n충격: {g_force}G\n조도: {lux}lx" 
                if st.session_state.lang == 'KO' else 
                "{event_type}\nTime: {timestamp}\nTemp: {temperature}°C\nHumidity: {humidity}%\nImpact: {g_force}G\nLight: {lux}lx"
            )
 
            map_container.pydeck_chart(pdk.Deck(
                layers=[path_layer, shock_layer, light_layer, temp_layer, humi_layer, current_layer, icon_layer],
                initial_view_state=view_state,
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                tooltip={"text": tooltip_text},
                height=400
            ))
        else:
            map_container.info(LANG_DICT[st.session_state.lang]['gps_wait'])
 
        # 차트 및 로그 렌더링 (예외 발생 시에도 루프가 중단되지 않도록 보호)
        try:
            # 데이터프레임 변환
            df = pd.DataFrame(display_history).set_index('timestamp')
            df_chart = df.copy()
            
            # 1. 온도/습도 그래프 (이중 Y축 or 단독 필터 보기)
            has_temp = 'temperature' in df_chart.columns
            has_humi = 'humidity' in df_chart.columns
            if has_temp or has_humi:
                df_reset = df_chart.reset_index()
                df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'], errors='coerce', format='mixed')
                df_reset = df_reset.dropna(subset=['timestamp'])
                if not df_reset.empty:
                    is_ko = (st.session_state.lang == 'KO')
                    temp_lbl = '온도 (°C)' if is_ko else 'Temperature (°C)'
                    humi_lbl = '습도 (%)' if is_ko else 'Humidity (%)'
                    
                    df_reset['temp_label'] = temp_lbl
                    df_reset['humi_label'] = humi_lbl
                    
                    axis_x_compact = alt.Axis(
                        format='%H:%M',
                        labelAngle=0,
                        tickCount=6,
                        title=None,
                        labelFontSize=11,
                        labelColor='#888888',
                        grid=True,
                        gridDash=[2, 4],
                        gridOpacity=0.25
                    )
                    
                    # 현재 선택된 온습도 필터 확인 (전체 / 온도만 / 습도만)
                    active_env_filter = st.session_state.get('filter_env_chart') or ""
                    is_all = ("전체" in active_env_filter or "All" in active_env_filter or not active_env_filter)
                    show_temp = (is_all or "온도" in active_env_filter or "Temp" in active_env_filter) and has_temp
                    show_humi = (is_all or "습도" in active_env_filter or "Humi" in active_env_filter) and has_humi
                    is_dual = show_temp and show_humi
                    
                    tooltip_list = [
                        alt.Tooltip('timestamp:T', title='시간' if is_ko else 'Time', format='%H:%M:%S')
                    ]
                    if show_temp:
                        tooltip_list.append(alt.Tooltip('temperature:Q', title=temp_lbl, format='.2f'))
                    if show_humi:
                        tooltip_list.append(alt.Tooltip('humidity:Q', title=humi_lbl, format='.2f'))
                    
                    layers = []
                    
                    # 1) 온도 레이어 (범위: -10°C ~ +40°C)
                    if show_temp:
                        temp_line = alt.Chart(df_reset).mark_line(
                            strokeWidth=2.4
                        ).encode(
                            x=alt.X('timestamp:T', axis=axis_x_compact, title=None),
                            y=alt.Y(
                                'temperature:Q',
                                axis=alt.Axis(
                                    title=temp_lbl,
                                    titleColor='#FF5733',
                                    orient='left',
                                    grid=True
                                ),
                                scale=alt.Scale(domain=[-10, 40], clamp=True)
                            ),
                            color=alt.Color(
                                'temp_label:N',
                                scale=alt.Scale(
                                    domain=[temp_lbl, humi_lbl],
                                    range=['#FF5733', '#33A2FF']
                                ),
                                legend=alt.Legend(orient='bottom', title=None) if is_dual else None
                            ),
                            tooltip=tooltip_list
                        )
                        layers.append(temp_line)
                    
                    # 2) 습도 레이어 (범위: 0% ~ 100%)
                    if show_humi:
                        humi_orient = 'right' if is_dual else 'left'
                        humi_line = alt.Chart(df_reset).mark_line(
                            strokeWidth=2.2
                        ).encode(
                            x=alt.X('timestamp:T', axis=axis_x_compact, title=None),
                            y=alt.Y(
                                'humidity:Q',
                                axis=alt.Axis(
                                    title=humi_lbl,
                                    titleColor='#33A2FF',
                                    orient=humi_orient,
                                    grid=(not is_dual)
                                ),
                                scale=alt.Scale(domain=[0, 100], clamp=True)
                            ),
                            color=alt.Color(
                                'humi_label:N',
                                scale=alt.Scale(
                                    domain=[temp_lbl, humi_lbl],
                                    range=['#FF5733', '#33A2FF']
                                ),
                                legend=alt.Legend(orient='bottom', title=None) if is_dual else None
                            ),
                            tooltip=tooltip_list
                        )
                        layers.append(humi_line)
                    
                    if len(layers) == 2:
                        env_combined = alt.layer(layers[0], layers[1]).resolve_scale(y='independent')
                    elif len(layers) == 1:
                        env_combined = layers[0]
                    else:
                        env_combined = alt.Chart(df_reset.head(0)).mark_line()
                    
                    final_env_chart = env_combined.properties(
                        height=400
                    ).configure_axis(
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_legend(
                        labelFontSize=12,
                        titleFontSize=14
                    ).interactive(bind_y=False)
                    
                    env_chart.altair_chart(final_env_chart, use_container_width=True)
            
            # 2. 조도 그래프
            if 'lux' in df_chart.columns:
                df_reset = df_chart.reset_index()
                df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'], errors='coerce', format='mixed')
                df_reset = df_reset.dropna(subset=['timestamp'])
                if not df_reset.empty:
                    # 범례 표시를 위해 Metric 컬럼 생성
                    metric_label = '조도 (Lux)' if st.session_state.lang == 'KO' else 'Illuminance (Lux)'
                    df_reset['Metric'] = metric_label
                    y_title = '조도 (Lux)' if st.session_state.lang == 'KO' else 'Lux'
                    
                    axis_x_lux = alt.Axis(
                        format='%H:%M',
                        labelAngle=0,
                        tickCount=6,
                        title=None,
                        labelFontSize=11,
                        labelColor='#888888',
                        grid=True,
                        gridDash=[2, 4],
                        gridOpacity=0.25
                    )
                    
                    chart = alt.Chart(df_reset).mark_area().encode(
                        x=alt.X('timestamp:T', axis=axis_x_lux, title=None),
                        y=alt.Y('lux:Q', scale=alt.Scale(zero=False), title=y_title),
                        color=alt.Color('Metric:N', 
                                        scale=alt.Scale(domain=[metric_label], range=['#FFD700']), 
                                        legend=alt.Legend(orient='bottom', title=None)),
                        tooltip=[
                            alt.Tooltip('timestamp:T', title='시간' if st.session_state.lang == 'KO' else 'Time', format='%H:%M:%S'),
                            alt.Tooltip('lux:Q', title='조도(Lux)' if st.session_state.lang == 'KO' else 'Lux', format='.1f')
                        ]
                    ).properties(
                        height=400
                    ).configure_axis(
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_legend(
                        labelFontSize=12,
                        titleFontSize=14
                    ).interactive(bind_y=False)
                    lux_chart.altair_chart(chart, use_container_width=True)
                
            # 3. 충격량 및 속도 그래프 (이중 Y축 or 단독 필터 보기)
            if 'g_force' in df_chart.columns:
                df_reset = df_chart.reset_index()
                df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'], errors='coerce', format='mixed')
                df_reset = df_reset.dropna(subset=['timestamp'])
                if not df_reset.empty:
                    is_ko = (st.session_state.lang == 'KO')
                    
                    axis_x_gforce = alt.Axis(
                        format='%H:%M',
                        labelAngle=0,
                        tickCount=6,
                        title=None,
                        labelFontSize=11,
                        labelColor='#888888',
                        grid=True,
                        gridDash=[2, 4],
                        gridOpacity=0.25
                    )
                    
                    # 현재 선택된 충격/속도 필터 확인 (전체 / 충격량만 / 속도만)
                    active_g_filter = st.session_state.get('filter_g_chart') or ""
                    is_g_all = ("전체" in active_g_filter or "충격량+속도" in active_g_filter or "All" in active_g_filter or not active_g_filter)
                    show_g = (is_g_all or "충격량만" in active_g_filter or "Impact" in active_g_filter)
                    show_spd = (is_g_all or "속도만" in active_g_filter or "Speed" in active_g_filter) and ('speed' in df_reset.columns)
                    is_g_dual = show_g and show_spd
                    
                    # 1) 충격량 메인 라인 & 피크 & 기준선 그룹
                    if show_g:
                        y_g_title = '충격량 (G-Force)' if is_ko else 'Impact (G-Force)'
                        gforce_line = alt.Chart(df_reset).mark_line(
                            color='#E74C3C', strokeWidth=2.2
                        ).encode(
                            x=alt.X('timestamp:T', axis=axis_x_gforce, title=None),
                            y=alt.Y('g_force:Q', axis=alt.Axis(title=y_g_title, titleColor='#E74C3C', grid=True), scale=alt.Scale(zero=False)),
                            tooltip=[
                                alt.Tooltip('timestamp:T', title='시간' if is_ko else 'Time', format='%H:%M:%S'),
                                alt.Tooltip('g_force:Q', title='충격량(G)' if is_ko else 'Impact(G)', format='.2f'),
                                alt.Tooltip('speed:Q', title='속도(km/h)' if is_ko else 'Speed(km/h)', format='.1f')
                            ]
                        )
                        
                        # 2.0G 이상 충격 피크 포인트 강조 (빨간 점)
                        shock_pts_df = df_reset[df_reset['g_force'] >= 2.0]
                        if not shock_pts_df.empty:
                            shock_points = alt.Chart(shock_pts_df).mark_circle(
                                size=60, color='#E74C3C'
                            ).encode(
                                x=alt.X('timestamp:T'),
                                y=alt.Y('g_force:Q'),
                                tooltip=[
                                    alt.Tooltip('timestamp:T', title='시간' if is_ko else 'Time', format='%H:%M:%S'),
                                    alt.Tooltip('g_force:Q', title='충격량(G)' if is_ko else 'Impact(G)', format='.2f'),
                                    alt.Tooltip('speed:Q', title='당시속도(km/h)' if is_ko else 'Speed(km/h)', format='.1f')
                                ]
                            )
                        else:
                            shock_points = alt.Chart(df_reset.head(0)).mark_circle()

                        # 과일 손상 위험 기준선 (2.0G 주의선, 3.0G 위험선)
                        lbl_2g = '2.0G 과일 손상 주의 (요철)' if is_ko else '2.0G Fruit Damage Warning'
                        lbl_3g = '3.0G 과일 압상 위험 (Critical)' if is_ko else '3.0G Critical Impact'
                        thresh_df = pd.DataFrame([
                            {'level': 2.0, 'label': lbl_2g},
                            {'level': 3.0, 'label': lbl_3g}
                        ])
                        rules = alt.Chart(thresh_df).mark_rule(
                            strokeDash=[4, 4], strokeWidth=1.5, opacity=0.85
                        ).encode(
                            y=alt.Y('level:Q'),
                            color=alt.Color('label:N', 
                                            scale=alt.Scale(domain=[lbl_2g, lbl_3g], range=['#FFA500', '#FF0000']), 
                                            legend=alt.Legend(orient='bottom', title=None))
                        )
                        gforce_group = alt.layer(gforce_line, shock_points, rules)

                    # 2) 차량 속도 라인
                    if show_spd:
                        y_spd_title = '차량 속도 (km/h)' if is_ko else 'Speed (km/h)'
                        spd_orient = 'right' if is_g_dual else 'left'
                        speed_layer = alt.Chart(df_reset).mark_line(
                            color='#2ECC71', strokeWidth=2.2 if not is_g_dual else 1.5, opacity=1.0 if not is_g_dual else 0.7
                        ).encode(
                            x=alt.X('timestamp:T', axis=axis_x_gforce, title=None),
                            y=alt.Y('speed:Q', axis=alt.Axis(title=y_spd_title, titleColor='#2ECC71', orient=spd_orient, grid=(not is_g_dual)), scale=alt.Scale(zero=True)),
                            tooltip=[
                                alt.Tooltip('timestamp:T', title='시간' if is_ko else 'Time', format='%H:%M:%S'),
                                alt.Tooltip('speed:Q', title='속도(km/h)' if is_ko else 'Speed(km/h)', format='.1f')
                            ]
                        )

                    # 3) 차트 결합 (단독 or 이중축)
                    if is_g_dual:
                        combined_chart = alt.layer(speed_layer, gforce_group).resolve_scale(y='independent')
                    elif show_g:
                        combined_chart = gforce_group
                    elif show_spd:
                        combined_chart = speed_layer
                    else:
                        combined_chart = alt.Chart(df_reset.head(0)).mark_line()

                    final_g_chart = combined_chart.properties(
                        height=400
                    ).configure_axis(
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_legend(
                        labelFontSize=12,
                        titleFontSize=14
                    ).interactive(bind_y=False)
                    
                    gforce_chart.altair_chart(final_g_chart, use_container_width=True)
     
            # 로그 (전체 데이터를 역순으로 표시, 스크롤 가능하며 표 우측 상단 'Download as CSV' 클릭 시 전량 다운로드)
            log_container.dataframe(df.iloc[::-1], height=350, use_container_width=True)
        except Exception as chart_err:
            print(f"Chart render warning: {chart_err}")
    else:
        # 실시간 데이터 최초 수신 대기 상태 표시 (화면이 빈 상태로 남는 현상 방지)
        temp_metric.metric(LANG_DICT[st.session_state.lang]['metric_temp'], "- °C")
        humi_metric.metric(LANG_DICT[st.session_state.lang]['metric_humi'], "- %")
        lux_metric.metric(LANG_DICT[st.session_state.lang]['metric_lux'], "- lx")
        gforce_metric.metric(LANG_DICT[st.session_state.lang]['metric_gforce'], "- G")
        speed_metric.metric(LANG_DICT[st.session_state.lang]['metric_speed'], "- km/h")
        
        map_container.info("⏳ 센서 노드로부터 첫 실시간 데이터 수신 대기 중입니다 (5초 주기)..." if st.session_state.lang == 'KO' else "⏳ Waiting for initial telemetry from sensor node (5s interval)...")
        if selected_run == "실시간 주행 (현재 실험)":
            sidebar_status_box.markdown(f"""
            <div style="background-color: rgba(0, 212, 255, 0.08); border: 1px solid rgba(0, 212, 255, 0.35); border-radius: 8px; padding: 12px; margin-bottom: 5px;">
                <div style="font-size: 13.5px; font-weight: bold; color: #00d4ff; margin-bottom: 6px;">📡 실시간 데이터 수신 대기</div>
                <div style="font-size: 12px; line-height: 1.7; color: #e0e0e0;">
                    • <b>관제 대상:</b> <code>{active_truck['name_ko']}</code><br>
                    • <b>브로커:</b> <code>{MQTT_BROKER}</code><br>
                    • <b>전용 토픽:</b> <code>{MQTT_TOPIC}</code><br>
                    • <b>대상 단말:</b> <code>{EXPECTED_DEVICE}</code><br>
                    • <b>상태:</b> 🟡 센서 노드 패킷 대기 중
                </div>
            </div>
            """, unsafe_allow_html=True)
 
    if selected_run != "실시간 주행 (현재 실험)":
        # 과거 실험 데이터는 정적 데이터이므로 한 번 렌더링 후 루프 종료 (클라우드 CPU 절약 및 UI 안정화)
        break

    # 최적화: 1초 -> 2초 딜레이로 변경하여 클라우드 서버 부하 감소
    time.sleep(2)
