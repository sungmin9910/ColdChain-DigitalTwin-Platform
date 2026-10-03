import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd
import time
from datetime import datetime, timezone, timedelta
import queue
import pydeck as pdk
import pymysql
import altair as alt

# 한국 표준시 (KST, UTC+9) 설정
KST = timezone(timedelta(hours=9))

def get_kst_now():
    return datetime.now(KST)

def generate_run_id():
    now_kst = get_kst_now()
    return f"주행_{now_kst.strftime('%Y-%m-%d_%H시%M분')}"

# ----------------------------------------------------------------
# 1. 설정 및 공유 자원 초기화
# ----------------------------------------------------------------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "coldchain/truck01/sensor"

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
if 'run_id' not in st.session_state:
    st.session_state.run_id = generate_run_id()

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
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
        client.subscribe(MQTT_TOPIC)
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
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
        print(f"Error parsing message: {e}")

@st.cache_resource
def start_mqtt_client():
    try:
        from paho.mqtt.client import CallbackAPIVersion
        client = mqtt.Client(CallbackAPIVersion.VERSION1)
    except:
        client = mqtt.Client()
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client

mqtt_client = start_mqtt_client()

# ----------------------------------------------------------------
# 3. UI 구성
# ----------------------------------------------------------------

# DB에서 고유 run_id 목록 가져오기
run_ids = ["실시간 주행 (현재 실험)"]
conn = get_mysql_connection()
if conn:
    try:
        with conn.cursor() as cursor:
            # 1건 이상 기록된 모든 주행 세션을 최신순으로 가져오기
            cursor.execute("""
                SELECT run_id 
                FROM sensor_data 
                WHERE run_id IS NOT NULL 
                GROUP BY run_id 
                HAVING COUNT(*) >= 1 
                ORDER BY MAX(id) DESC
            """)
            rows = cursor.fetchall()
            for r in rows:
                val = r["run_id"]
                if val not in run_ids:
                    run_ids.append(val)
    except Exception as e:
        print(f"run_ids 로드 에러: {e}")
    finally:
        conn.close()

with st.sidebar:
    st.markdown(f"### {LANG_DICT[st.session_state.lang]['sidebar_title']}")
    st.caption(LANG_DICT[st.session_state.lang]['sidebar_desc'])
    
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
    
    # [2] 실험 세션 및 주행 데이터 선택
    def format_session_label(session_id):
        if session_id == "실시간 주행 (현재 실험)":
            return "🟢 실시간 주행 (현재 실험)"
        elif "20261003" in session_id or "2026-10-03" in session_id:
            if "1834" in session_id or "18" in session_id:
                return f"🚗 [10-03 저녁 주행] {session_id}"
            return f"🚗 [10-03 실험] {session_id}"
        elif "departure" in session_id:
            return "🚗 [10-02 출발] 전주 ➔ 대전 (89km, 1,356건)"
        elif "return" in session_id:
            return "🚗 [10-02 복귀] 대전 ➔ 전주 (85km, 478건)"
        elif "065739" in session_id:
            return "🧪 [10-01 야외] 전북대 캠퍼스 GPS 검증 (157건)"
        elif "30km" in session_id:
            return "📦 [07-15 모의] 30km 시뮬레이션 주행 (181건)"
        else:
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
        
        # 버튼 텍스트 잘림 해결 (풀위드 1열 배치)
        if st.button("🚀 새 실험 세션 시작 (화면 리셋)" if st.session_state.lang == 'KO' else "🚀 Start New Session", type="primary", use_container_width=True):
            if new_run_input.strip():
                st.session_state.run_id = new_run_input.strip()
            else:
                st.session_state.run_id = generate_run_id()
            
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

# Row 2: 충격량/속도 차트 및 온습도 차트
col1_row2, col2_row2 = st.columns(2)

with col1_row2:
    st.markdown(f"<h3 style='text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 10px; margin-top: 20px;'>{LANG_DICT[st.session_state.lang]['chart_g_speed']}</h3>", unsafe_allow_html=True)
    gforce_chart = st.empty()

with col2_row2:
    st.markdown(f"<h3 style='text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 10px; margin-top: 20px;'>{LANG_DICT[st.session_state.lang]['chart_env']}</h3>", unsafe_allow_html=True)
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

        # 최적화: 스마트 주행 감지 래치 (Smart Trip Latch & Last Known GPS)
        if 'trip_started' not in st.session_state:
            st.session_state.trip_started = False
        if 'last_valid_gps' not in st.session_state:
            st.session_state.last_valid_gps = (0.0, 0.0)

        # 보드에서 자동 주행 종료 또는 명시적 대기 상태 패킷 수신 시 주행 래치 해제
        incoming_status = str(msg.get("status", ""))
        if "대기" in incoming_status or "실내" in incoming_status:
            st.session_state.trip_started = False

        gps_lat_val = float(msg.get("lat", 0.0))
        gps_lng_val = float(msg.get("lng", 0.0))
        gps_speed_val = float(msg.get("speed", 0.0))
        gps_sats_val = int(msg.get("sats", 0))
        gps_is_valid = (gps_lat_val != 0.0 and gps_lng_val != 0.0)

        if "대기" not in incoming_status and "실내" not in incoming_status:
            if gps_is_valid:
                st.session_state.trip_started = True
                st.session_state.last_valid_gps = (gps_lat_val, gps_lng_val)
            elif gps_speed_val > 2.5:
                st.session_state.trip_started = True

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

            dev_id = latest.get('device', 'carrier-c6-01')
            ts_str = latest.get('timestamp', '-')
            
            sidebar_status_box.markdown(f"""
            <div style="background-color: rgba(0, 212, 255, 0.08); border: 1px solid rgba(0, 212, 255, 0.35); border-radius: 8px; padding: 12px; margin-bottom: 5px;">
                <div style="font-size: 13.5px; font-weight: bold; color: #00d4ff; margin-bottom: 6px;">📡 실시간 데이터 수신 상태</div>
                <div style="font-size: 12px; line-height: 1.7; color: #e0e0e0;">
                    • <b>수신 단말:</b> <code>{dev_id}</code><br>
                    • <b>GPS 상태:</b> {gps_badge}<br>
                    • <b>DB 상태:</b> {db_badge}<br>
                    • <b>최근 패킷:</b> <code>{ts_str}</code><br>
                    • <b>현재 세션 수집:</b> <b style="color:#00d4ff;">{len(display_history)}</b>건
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
            
            # 1. 온도/습도 그래프 (온도와 습도 중 사용 가능한 컬럼 추출)
            available_env = [col for col in ['temperature', 'humidity'] if col in df_chart.columns]
            if available_env:
                df_reset = df_chart.reset_index()
                df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'], errors='coerce', format='mixed')
                df_reset = df_reset.dropna(subset=['timestamp'])
                if not df_reset.empty:
                    df_long = df_reset.melt(id_vars=['timestamp'], value_vars=available_env, var_name='Metric', value_name='Value')
                    
                    # 범례 한글화 매핑 (세션 언어가 KO이면 한글로 표시)
                    if st.session_state.lang == 'KO':
                        metric_labels = {'temperature': '온도 (°C)', 'humidity': '습도 (%)'}
                        domain_list = ['온도 (°C)', '습도 (%)']
                        y_title = '온도 / 습도'
                    else:
                        metric_labels = {'temperature': 'Temperature (°C)', 'humidity': 'Humidity (%)'}
                        domain_list = ['Temperature (°C)', 'Humidity (%)']
                        y_title = 'Temp / Humi'
                    
                    df_long['Metric'] = df_long['Metric'].map(metric_labels)
                    
                    chart = alt.Chart(df_long).mark_line().encode(
                        x=alt.X('timestamp:T', axis=alt.Axis(labels=False, ticks=False), title=None),
                        y=alt.Y('Value:Q', scale=alt.Scale(zero=False), title=y_title),
                        color=alt.Color('Metric:N', 
                                        scale=alt.Scale(domain=domain_list, range=['#FF5733', '#33A2FF']),
                                        legend=alt.Legend(orient='bottom', title=None))
                    ).properties(
                        height=400
                    ).configure_axis(
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_legend(
                        labelFontSize=12,
                        titleFontSize=14
                    ).interactive(bind_y=False)
                    env_chart.altair_chart(chart, width="stretch")
            
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
                    
                    chart = alt.Chart(df_reset).mark_area().encode(
                        x=alt.X('timestamp:T', axis=alt.Axis(labels=False, ticks=False), title=None),
                        y=alt.Y('lux:Q', scale=alt.Scale(zero=False), title=y_title),
                        color=alt.Color('Metric:N', 
                                        scale=alt.Scale(domain=[metric_label], range=['#FFD700']), 
                                        legend=alt.Legend(orient='bottom', title=None))
                    ).properties(
                        height=400
                    ).configure_axis(
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_legend(
                        labelFontSize=12,
                        titleFontSize=14
                    ).interactive(bind_y=False)
                    lux_chart.altair_chart(chart, width="stretch")
                
            # 3. 충격량 및 속도 이중 Y축 (Dual-Axis) 고도화 그래프
            if 'g_force' in df_chart.columns:
                df_reset = df_chart.reset_index()
                df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'], errors='coerce', format='mixed')
                df_reset = df_reset.dropna(subset=['timestamp'])
                if not df_reset.empty:
                    is_ko = (st.session_state.lang == 'KO')
                    
                    # 1) 충격량 메인 라인 (왼쪽 Y축 - 주인공)
                    y_g_title = '충격량 (G-Force)' if is_ko else 'Impact (G-Force)'
                    gforce_line = alt.Chart(df_reset).mark_line(
                        color='#E74C3C', strokeWidth=2.2
                    ).encode(
                        x=alt.X('timestamp:T', axis=alt.Axis(labels=False, ticks=False), title=None),
                        y=alt.Y('g_force:Q', axis=alt.Axis(title=y_g_title, titleColor='#E74C3C', grid=True), scale=alt.Scale(zero=False))
                    )
                    
                    # 2) 2.0G 이상 충격 피크 포인트 강조 (빨간 점)
                    shock_pts_df = df_reset[df_reset['g_force'] >= 2.0]
                    if not shock_pts_df.empty:
                        shock_points = alt.Chart(shock_pts_df).mark_circle(
                            size=60, color='#E74C3C'
                        ).encode(
                            x=alt.X('timestamp:T'),
                            y=alt.Y('g_force:Q'),
                            tooltip=[
                                alt.Tooltip('timestamp:T', title='시간' if is_ko else 'Time'),
                                alt.Tooltip('g_force:Q', title='충격량(G)' if is_ko else 'Impact(G)', format='.2f'),
                                alt.Tooltip('speed:Q', title='당시속도(km/h)' if is_ko else 'Speed(km/h)', format='.1f')
                            ]
                        )
                    else:
                        shock_points = alt.Chart(df_reset.head(0)).mark_circle()

                    # 3) 과일 손상 위험 기준선 (2.0G 주의선, 3.0G 위험선)
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

                    # 4) 차량 속도 보조 라인 (오른쪽 Y축 - 배경)
                    if 'speed' in df_reset.columns:
                        y_spd_title = '차량 속도 (km/h)' if is_ko else 'Speed (km/h)'
                        speed_layer = alt.Chart(df_reset).mark_line(
                            color='#2ECC71', strokeWidth=1.4, opacity=0.6
                        ).encode(
                            x=alt.X('timestamp:T', axis=alt.Axis(labels=False, ticks=False), title=None),
                            y=alt.Y('speed:Q', axis=alt.Axis(title=y_spd_title, titleColor='#2ECC71', grid=False), scale=alt.Scale(zero=True))
                        )
                        combined_chart = alt.layer(speed_layer, gforce_group).resolve_scale(y='independent')
                    else:
                        combined_chart = gforce_group

                    final_g_chart = combined_chart.properties(
                        height=400
                    ).configure_axis(
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_legend(
                        labelFontSize=12,
                        titleFontSize=14
                    ).interactive(bind_y=False)
                    
                    gforce_chart.altair_chart(final_g_chart, width="stretch")
     
            # 로그 (전체 데이터를 역순으로 표시, 스크롤 가능하며 표 우측 상단 'Download as CSV' 클릭 시 전량 다운로드)
            log_container.dataframe(df.iloc[::-1], height=350, use_container_width=True)
        except Exception as chart_err:
            print(f"Chart render warning: {chart_err}")
 
    if selected_run != "실시간 주행 (현재 실험)":
        # 과거 실험 데이터는 정적 데이터이므로 한 번 렌더링 후 루프 종료 (클라우드 CPU 절약 및 UI 안정화)
        break

    # 최적화: 1초 -> 2초 딜레이로 변경하여 클라우드 서버 부하 감소
    time.sleep(2)
