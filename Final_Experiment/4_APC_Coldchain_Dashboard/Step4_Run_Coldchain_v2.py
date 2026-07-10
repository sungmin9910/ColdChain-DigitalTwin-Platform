import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd
import time
from datetime import datetime
import queue
import pydeck as pdk
import pymysql
import altair as alt

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
        'sidebar_title': "⚙️ 컨트롤 패널",
        'sidebar_desc': "새로운 주행/테스트를 시작할 때 데이터를 초기화하세요.",
        'sidebar_reset_btn': "🔄 새 테스트 시작 (모든 데이터 초기화)",
        'reset_success': "데이터가 완전히 초기화되었습니다! 🚀",
        'reset_failed': "DB 초기화 실패: {}",
        'metric_temp': "온도",
        'metric_humi': "습도",
        'metric_lux': "조도",
        'metric_gforce': "충격량",
        'metric_speed': "현재 속도",
        'map_title': "📍 차량 위치 및 이동 경로",
        'chart_g_speed': "📉 충격량(G) 및 속도(km/h) 추이",
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
        'sidebar_title': "⚙️ Control Panel",
        'sidebar_desc': "Reset data when starting a new driving test.",
        'sidebar_reset_btn': "🔄 Start New Test (Reset All Data)",
        'reset_success': "Data has been completely reset! 🚀",
        'reset_failed': "Failed to reset DB: {}",
        'metric_temp': "Temperature",
        'metric_humi': "Humidity",
        'metric_lux': "Illuminance",
        'metric_gforce': "Impact (G)",
        'metric_speed': "Current Speed",
        'map_title': "📍 Vehicle Location & Route",
        'chart_g_speed': "📉 Impact (G) & Speed (km/h) Trend",
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
    st.session_state.lang = 'EN'

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
    history = []
    # 앱 시작 시 DB에서 최근 데이터 불러오기
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 100")
                items = cursor.fetchall()
            
            for item in reversed(items):
                # DB 결과를 원래 JSON 형태로 매핑
                parsed_item = {
                    "device": item.get("device"),
                    "timestamp": item.get("timestamp_str"),
                    "temperature": item.get("temperature", 0.0),
                    "humidity": item.get("humidity", 0.0),
                    "lux": item.get("lux", 0.0),
                    "g_force": item.get("g_force", 0.0),
                    "speed": item.get("speed", 0.0),
                    "lat": item.get("lat", 0.0),
                    "lng": item.get("lng", 0.0),
                    "status": item.get("status")
                }
                history.append(parsed_item)
            print(f"MySQL에서 {len(history)}개의 과거 데이터를 불러왔습니다.")
        except Exception as e:
            print(f"MySQL 데이터 로드 실패: {e}")
        finally:
            conn.close()
    return history

msg_queue = get_msg_queue()
data_history = get_data_history()

# 최근 데이터 삭제를 위한 전역 변수
last_cleanup_time = 0
CLEANUP_INTERVAL_SEC = 86400  # 하루(24시간) 마다 한 번씩 정리

def cleanup_old_data():
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # 7일 이상 지난 데이터 자동 삭제
                cursor.execute("DELETE FROM sensor_data WHERE created_at < NOW() - INTERVAL 7 DAY")
            conn.commit()
            print("오래된 데이터 정리 완료 (7일 이전 데이터 삭제)")
        except Exception as e:
            print(f"데이터 정리 에러: {e}")
        finally:
            conn.close()

def save_to_mysql(msg_dict):
    global last_cleanup_time
    
    # 24시간마다 한 번씩 정리 로직 실행
    current_time = time.time()
    if current_time - last_cleanup_time > CLEANUP_INTERVAL_SEC:
        cleanup_old_data()
        last_cleanup_time = current_time

    conn = get_mysql_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            # AWS RDS 시간에 +09:00 적용
            cursor.execute("SET time_zone = '+09:00'")
            
            sql = """
            INSERT INTO sensor_data 
            (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
                msg_dict.get("status", "")
            )
            cursor.execute(sql, val)
        conn.commit()
    except Exception as e:
        print(f"MySQL 저장 에러: {e}")
    finally:
        conn.close()

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
        
        # 보드에서 보낸 시간 정보가 있으면 사용, 없으면 현재 시간 생성
        if 'timestamp_str' in payload:
            payload['timestamp'] = payload['timestamp_str']
        else:
            payload['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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

with st.sidebar:
    st.header(LANG_DICT[st.session_state.lang]['sidebar_title'])
    st.markdown(LANG_DICT[st.session_state.lang]['sidebar_desc'])
    if st.button(LANG_DICT[st.session_state.lang]['sidebar_reset_btn'], type="primary", use_container_width=True):
        # 1. DB 비우기
        conn = get_mysql_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE sensor_data")
                conn.commit()
            except Exception as e:
                st.error(LANG_DICT[st.session_state.lang]['reset_failed'].format(e))
            finally:
                conn.close()
        
        # 2. 메모리 비우기
        data_history.clear()
        with msg_queue.mutex:
            msg_queue.queue.clear()
            
        st.success(LANG_DICT[st.session_state.lang]['reset_success'])
        time.sleep(1)
        st.rerun()

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
st.markdown(f"<h3 style='text-align: left; font-size: 28px; font-weight: bold; margin-bottom: 10px;'>{LANG_DICT[st.session_state.lang]['log_title']}</h3>", unsafe_allow_html=True)
log_container = st.empty()

# ----------------------------------------------------------------
# 4. 실시간 루프
# ----------------------------------------------------------------
last_db_save_time = 0

while True:
    while not msg_queue.empty():
        msg = msg_queue.get()
        data_history.append(msg)
        
        # 최적화: 10초에 한 번씩만 DB에 저장 (또는 강한 충격 발생 시 즉시 저장)
        current_time = time.time()
        if (current_time - last_db_save_time >= 10) or (msg.get('g_force', 0) > 1.8):
            save_to_mysql(msg)  
            last_db_save_time = current_time
        if len(data_history) > 3600:
            data_history.pop(0)

    if len(data_history) > 0:
        latest = data_history[-1]
        
        # 메트릭 업데이트 (값이 없을 경우를 대비해 0.0 처리)
        temp_metric.metric(LANG_DICT[st.session_state.lang]['metric_temp'], f"{latest.get('temperature', 0):.1f} °C")
        humi_metric.metric(LANG_DICT[st.session_state.lang]['metric_humi'], f"{latest.get('humidity', 0):.1f} %")
        lux_metric.metric(LANG_DICT[st.session_state.lang]['metric_lux'], f"{latest.get('lux', 0):.0f} lx")
        gforce_metric.metric(LANG_DICT[st.session_state.lang]['metric_gforce'], f"{latest.get('g_force', 0):.2f} G")
        speed_metric.metric(LANG_DICT[st.session_state.lang]['metric_speed'], f"{latest.get('speed', 0):.1f} km/h")
        
        # ----------------------------------------------------------------
        # 5. 고도화된 지도 시각화 (Pydeck)
        # ----------------------------------------------------------------
        df_gps = pd.DataFrame(data_history)
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

        # 데이터프레임 변환
        df = pd.DataFrame(data_history).set_index('timestamp')
        
        # 차트용 데이터프레임 (전체 누적 기록)
        df_chart = df.copy()
        
        # 1. 온도/습도 그래프 (온도와 습도 중 사용 가능한 컬럼 추출)
        available_env = [col for col in ['temperature', 'humidity'] if col in df_chart.columns]
        if available_env:
            df_reset = df_chart.reset_index()
            df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'])
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
            env_chart.altair_chart(chart, use_container_width=True)
        
        # 2. 조도 그래프
        if 'lux' in df_chart.columns:
            df_reset = df_chart.reset_index()
            df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'])
            
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
            lux_chart.altair_chart(chart, use_container_width=True)
            
        # 3. 충격량 및 속도 그래프
        available_g_speed = [col for col in ['g_force', 'speed'] if col in df_chart.columns]
        if available_g_speed:
            df_reset = df_chart.reset_index()
            df_reset['timestamp'] = pd.to_datetime(df_reset['timestamp'])
            df_long = df_reset.melt(id_vars=['timestamp'], value_vars=available_g_speed, var_name='Metric', value_name='Value')
            
            # 범례 한글화 매핑
            if st.session_state.lang == 'KO':
                metric_labels = {'g_force': '충격량 (G)', 'speed': '속도 (km/h)'}
                domain_list = ['충격량 (G)', '속도 (km/h)']
                y_title = '충격량 / 속도'
            else:
                metric_labels = {'g_force': 'Impact (G)', 'speed': 'Speed (km/h)'}
                domain_list = ['Impact (G)', 'Speed (km/h)']
                y_title = 'Impact / Speed'
                
            df_long['Metric'] = df_long['Metric'].map(metric_labels)
            
            chart = alt.Chart(df_long).mark_line().encode(
                x=alt.X('timestamp:T', axis=alt.Axis(labels=False, ticks=False), title=None),
                y=alt.Y('Value:Q', scale=alt.Scale(zero=False), title=y_title),
                color=alt.Color('Metric:N',
                                scale=alt.Scale(domain=domain_list, range=['#E74C3C', '#2ECC71']),
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
            gforce_chart.altair_chart(chart, use_container_width=True)

        # 로그
        log_container.dataframe(df.iloc[::-1].head(10), width="stretch")

    # 최적화: 1초 -> 2초 딜레이로 변경하여 클라우드 서버 부하 감소
    time.sleep(2)
