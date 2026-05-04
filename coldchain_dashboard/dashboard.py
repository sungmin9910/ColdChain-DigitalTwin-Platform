import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd
import time
from datetime import datetime
import queue
import pydeck as pdk

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

# 데이터 공유를 위한 큐
@st.cache_resource
def get_msg_queue():
    return queue.Queue()

@st.cache_resource
def get_data_history():
    return []

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
        payload['timestamp'] = datetime.now().strftime("%H:%M:%S")
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
while True:
    while not msg_queue.empty():
        msg = msg_queue.get()
        data_history.append(msg)
        if len(data_history) > 100:
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

            # 1. 이동 경로 레이어
            path_layer = pdk.Layer(
                "PathLayer",
                data=[{"path": df_gps[['lng', 'lat']].values.tolist()}],
                get_path="path",
                get_color=[0, 212, 255, 200], # 시안 블루
                width_min_pixels=5,
            )

            # 2. 충격 지점 레이어 (G-Force > 1.8)
            shock_df = df_gps[df_gps['g_force'] > 1.8]
            shock_layer = pdk.Layer(
                "ScatterplotLayer",
                data=shock_df,
                get_position="[lng, lat]",
                get_color=[255, 0, 0, 200], # 빨간색
                get_radius=30,
                pickable=True,
            )

            # 3. 조도 이벤트 레이어 (Lux > 500)
            light_df = df_gps[df_gps['lux'] > 500]
            light_layer = pdk.Layer(
                "ScatterplotLayer",
                data=light_df,
                get_position="[lng, lat]",
                get_color=[255, 255, 0, 150], # 노란색
                get_radius=20,
                pickable=True,
            )

            map_container.pydeck_chart(pdk.Deck(
                layers=[path_layer, shock_layer, light_layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/dark-v10",
                tooltip={"text": "상태: {status}\n충격: {g_force}G\n조도: {lux}lx"}
            ))
        else:
            map_container.info("GPS 수신 대기 중 (이동 경로를 표시하려면 위경도 데이터가 필요합니다)...")

        # 데이터프레임 변환
        df = pd.DataFrame(data_history).set_index('timestamp')
        
        # 그래프들
        if 'temperature' in df.columns and 'humidity' in df.columns:
            env_chart.line_chart(df[['temperature', 'humidity']])
        elif 'temperature' in df.columns:
            env_chart.line_chart(df['temperature'])
        elif 'humidity' in df.columns:
            env_chart.line_chart(df['humidity'])
        
        if 'lux' in df.columns:
            lux_chart.area_chart(df['lux'], color="#FFD700") # 금색 영역 차트
            
        if 'g_force' in df.columns and 'speed' in df.columns:
            gforce_chart.line_chart(df[['g_force', 'speed']])
        elif 'g_force' in df.columns:
            gforce_chart.line_chart(df['g_force'])
        elif 'speed' in df.columns:
            gforce_chart.line_chart(df['speed'])

        # 로그
        log_container.dataframe(df.iloc[::-1].head(10), width="stretch")

    time.sleep(1)
