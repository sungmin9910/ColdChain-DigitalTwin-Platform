import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd
import time
from datetime import datetime
import queue
import pydeck as pdk
import pymysql

# ----------------------------------------------------------------
# 1. 설정 및 공유 자원 초기화
# ----------------------------------------------------------------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "coldchain/truck01/sensor"

st.set_page_config(
    page_title="Cold Chain Premium Monitor",
    page_icon="🚚",
    layout="wide",
)

# 다크 모드와 라이트 모드 모두 어울리는 세련된 디자인 적용
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #00d4ff;
    }
    [data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: bold;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
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
    st.header("⚙️ 컨트롤 패널")
    st.markdown("새로운 주행/테스트를 시작할 때 데이터를 초기화하세요.")
    if st.button("🔄 새 테스트 시작 (모든 데이터 초기화)", type="primary", use_container_width=True):
        # 1. DB 비우기
        conn = get_mysql_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE sensor_data")
                conn.commit()
            except Exception as e:
                st.error(f"DB 초기화 실패: {e}")
            finally:
                conn.close()
        
        # 2. 메모리 비우기
        data_history.clear()
        with msg_queue.mutex:
            msg_queue.queue.clear()
            
        st.success("데이터가 완전히 초기화되었습니다! 🚀")
        time.sleep(1)
        st.rerun()

st.title("🚚 프리미엄 콜드체인 통합 관제")
st.markdown(f"**실시간 수신 중...** (Topic: `{MQTT_TOPIC}`)")

# 상단 5대 지표 레이아웃
m1, m2, m3, m4, m5 = st.columns(5)
temp_metric = m1.empty()
humi_metric = m2.empty()
lux_metric = m3.empty()
gforce_metric = m4.empty()
speed_metric = m5.empty()

st.markdown("---")

col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("📍 차량 위치 및 이동 경로")
    map_container = st.empty()
    
    st.subheader("📉 충격량(G) 및 속도(km/h) 추이")
    gforce_chart = st.empty()

with col_right:
    st.subheader("💡 실시간 조도 변화 (Lux)")
    lux_chart = st.empty()

    st.subheader("🌡️ 온도/습도 변화")
    env_chart = st.empty()
    
    st.subheader("📋 실시간 로그")
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
        temp_metric.metric("온도", f"{latest.get('temperature', 0):.1f} °C")
        humi_metric.metric("습도", f"{latest.get('humidity', 0):.1f} %")
        lux_metric.metric("조도", f"{latest.get('lux', 0):.0f} lx")
        gforce_metric.metric("충격량", f"{latest.get('g_force', 0):.2f} G")
        speed_metric.metric("현재 속도", f"{latest.get('speed', 0):.1f} km/h")
        
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

            # 1. 이동 경로 레이어 (무채색으로 변경하여 이벤트를 돋보이게 함)
            path_layer = pdk.Layer(
                "PathLayer",
                data=[{"path": df_gps[['lng', 'lat']].values.tolist()}],
                get_path="path",
                get_color=[150, 150, 150, 150], 
                width_min_pixels=3,
            )

            # 2. 충격 지점 (강한 충격 > 2.0G) - 빨간색 (반지름 45)
            shock_df = df_gps[df_gps['g_force'] > 2.0].copy()
            shock_df['event_type'] = "🚨 강한 충격"
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

            # 3. 조도 급변 지점 (Delta > 300 lx) - 노란색 (반지름 35)
            light_df = df_gps[df_gps['lux_diff'] > 300].copy()
            light_df['event_type'] = "💡 조도 급변"
            light_df['icon'] = "💡"
            light_layer = pdk.Layer(
                "ScatterplotLayer",
                data=light_df,
                get_position="[lng, lat]",
                get_fill_color=[255, 255, 0, 80],
                get_line_color=[255, 255, 0, 255],
                stroked=True,
                get_radius=35,
                pickable=True,
            )

            # 4. 온도 급변 지점 (Delta > 1.5°C) - 주황색 (반지름 25)
            temp_df = df_gps[df_gps['temp_diff'] > 1.5].copy()
            temp_df['event_type'] = "🌡️ 온도 급변"
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
            humi_df['event_type'] = "💧 습도 급변"
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

            # 모든 이벤트 데이터를 합쳐서 텍스트 아이콘 레이어 생성
            all_events = pd.concat([shock_df, light_df, temp_df, humi_df]).drop_duplicates(subset=['timestamp', 'icon']) if not (shock_df.empty and light_df.empty and temp_df.empty and humi_df.empty) else pd.DataFrame()

            icon_layer = pdk.Layer(
                "TextLayer",
                data=all_events,
                get_position="[lng, lat]",
                get_text="icon",
                get_size=20,
                get_alignment_baseline="'center'",
            )

            map_container.pydeck_chart(pdk.Deck(
                layers=[path_layer, shock_layer, light_layer, temp_layer, humi_layer, icon_layer],
                initial_view_state=view_state,
                tooltip={"text": "{event_type}\n시간: {timestamp}\n온도: {temperature}°C\n습도: {humidity}%\n충격: {g_force}G\n조도: {lux}lx"}
            ))
        else:
            map_container.info("GPS 수신 대기 중 (이동 경로를 표시하려면 위경도 데이터가 필요합니다)...")

        # 데이터프레임 변환
        df = pd.DataFrame(data_history).set_index('timestamp')
        
        # 최적화: 차트는 최근 100개의 데이터(약 100초)만 그려서 브라우저 렉 방지
        df_chart = df.tail(100)
        
        # 그래프들
        if 'temperature' in df_chart.columns and 'humidity' in df_chart.columns:
            env_chart.line_chart(df_chart[['temperature', 'humidity']])
        elif 'temperature' in df_chart.columns:
            env_chart.line_chart(df_chart['temperature'])
        elif 'humidity' in df_chart.columns:
            env_chart.line_chart(df_chart['humidity'])
        
        if 'lux' in df_chart.columns:
            lux_chart.area_chart(df_chart['lux'], color="#FFD700") # 금색 영역 차트
            
        if 'g_force' in df_chart.columns and 'speed' in df_chart.columns:
            gforce_chart.line_chart(df_chart[['g_force', 'speed']])
        elif 'g_force' in df_chart.columns:
            gforce_chart.line_chart(df_chart['g_force'])
        elif 'speed' in df_chart.columns:
            gforce_chart.line_chart(df_chart['speed'])

        # 로그
        log_container.dataframe(df.iloc[::-1].head(10), width="stretch")

    # 최적화: 1초 -> 2초 딜레이로 변경하여 클라우드 서버 부하 감소
    time.sleep(2)
