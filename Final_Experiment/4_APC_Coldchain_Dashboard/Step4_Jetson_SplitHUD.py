import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt
import paho.mqtt.client as mqtt
import json
import time
import queue
from datetime import datetime, timezone, timedelta
import pymysql

# ----------------------------------------------------------------
# 1. 페이지 환경설정 및 차량용 다크모드 고대비 CSS
# ----------------------------------------------------------------
st.set_page_config(
    page_title="ColdChain Jetson HUD",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 차량용 소형 스크린(7~10인치) 맞춤형 No-Scroll 고대비 스타일링
st.markdown("""
<style>
    /* 전체 여백 극소화 (스크롤 방지) */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }
    header, footer { visibility: hidden !important; height: 0px !important; }
    
    /* 배경 다크 테마 */
    .stApp {
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
    }

    /* 상단 슬림바 버튼 스타일링 */
    div[data-testid="stButton"] button {
        border-radius: 12px !important;
        padding: 8px 14px !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        transition: all 0.2s ease-in-out !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        width: 100% !important;
    }
    div[data-testid="stButton"] button:hover {
        border-color: #00d4ff !important;
        color: #00d4ff !important;
        background: rgba(0, 212, 255, 0.1) !important;
    }

    /* 활성화된 1번/2번 슬롯 버튼 강조 스타일 */
    .slot-active-1 {
        border: 2px solid #00e5ff !important;
        background: rgba(0, 229, 255, 0.18) !important;
        color: #00e5ff !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.4) !important;
    }
    .slot-active-2 {
        border: 2px solid #ffaa00 !important;
        background: rgba(255, 170, 0, 0.18) !important;
        color: #ffaa00 !important;
        box-shadow: 0 0 12px rgba(255, 170, 0, 0.4) !important;
    }

    /* 패널 카드 컨테이너 */
    .hud-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. 글로벌 상태 및 2-슬롯 선택 관리 로직
# ----------------------------------------------------------------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "coldchain/telemetry"

def get_kst_now():
    return datetime.now(timezone(timedelta(hours=9)))

def generate_run_id():
    return f"주행_{get_kst_now().strftime('%Y-%m-%d_%H시%M분')}"

if 'run_id' not in st.session_state:
    st.session_state.run_id = generate_run_id()

# 기본 선택: [1번: 지도, 2번: 충격량·속도]
if 'selected_views' not in st.session_state:
    st.session_state.selected_views = ['map', 'gforce']

if 'trip_started' not in st.session_state:
    st.session_state.trip_started = False

if 'last_valid_gps' not in st.session_state:
    st.session_state.last_valid_gps = (0.0, 0.0)

# 뷰 토글 함수 (최대 2개 유지, FIFO 슬라이딩 교체)
def toggle_view(view_key):
    cur = st.session_state.selected_views
    if view_key in cur:
        # 이미 선택된 상태에서 클릭 시 (2개 선택 중일 때만 해제 허용, 1개는 유지)
        if len(cur) > 1:
            cur.remove(view_key)
    else:
        # 새로운 뷰 선택 시
        if len(cur) < 2:
            cur.append(view_key)
        else:
            # 2개가 이미 찼으면 가장 오래된 1번을 밀어내고 새 뷰 추가
            cur.pop(0)
            cur.append(view_key)
    st.session_state.selected_views = cur

# ----------------------------------------------------------------
# 3. AWS RDS MySQL 연동
# ----------------------------------------------------------------
def get_mysql_connection():
    try:
        if "MySQL" in st.secrets:
            return pymysql.connect(
                host=st.secrets["MySQL"]["MYSQL_HOST"],
                port=st.secrets["MySQL"].get("MYSQL_PORT", 3306),
                user=st.secrets["MySQL"]["MYSQL_USER"],
                password=st.secrets["MySQL"]["MYSQL_PASSWORD"],
                database=st.secrets["MySQL"]["MYSQL_DATABASE"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
    except Exception as e:
        print(f"MySQL 연결 실패: {e}")
    return None

def save_to_mysql(msg_dict, run_id):
    conn = get_mysql_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET time_zone = '+09:00'")
            sql = """
            INSERT INTO sensor_data 
            (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            val = (
                msg_dict.get("device", "carrier-c6-01"),
                msg_dict.get("timestamp", ""),
                float(msg_dict.get("temperature", 0.0)),
                float(msg_dict.get("humidity", 0.0)),
                float(msg_dict.get("lux", 0.0)),
                float(msg_dict.get("g_force", 1.0)),
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

# ----------------------------------------------------------------
# 4. 실시간 MQTT 파이프라인
# ----------------------------------------------------------------
@st.cache_resource
def get_msg_queue():
    return queue.Queue()

@st.cache_resource
def get_data_history():
    return []

msg_queue = get_msg_queue()
data_history = get_data_history()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(MQTT_TOPIC)
        print("Connected to EMQX Broker!")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        ts_val = payload.get('timestamp_str', '')
        if ts_val and ts_val != "00:00:00" and not str(ts_val).startswith("00:00"):
            payload['timestamp'] = str(ts_val)
        else:
            payload['timestamp'] = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")

        for key in ['temperature', 'humidity', 'lux', 'g_force', 'speed', 'lat', 'lng']:
            if key in payload:
                try:
                    payload[key] = float(payload[key])
                except:
                    pass
        msg_queue.put(payload)
    except Exception as e:
        print(f"MQTT 파싱 에러: {e}")

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
# 5. UI 모듈 렌더링 함수들 (지도, 충격량, 온습도, 조도)
# ----------------------------------------------------------------

# 기본 컬럼 정의
DEFAULT_COLS = ['timestamp', 'lat', 'lng', 'speed', 'g_force', 'temperature', 'humidity', 'lux', 'status', 'device', 'run_id']

@st.cache_data(ttl=60)
def load_recent_session():
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT run_id FROM sensor_data WHERE run_id IS NOT NULL ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    last_run = row['run_id']
                    cursor.execute("SELECT * FROM sensor_data WHERE run_id = %s ORDER BY id ASC LIMIT 500", (last_run,))
                    records = cursor.fetchall()
                    history = []
                    for item in records:
                        history.append({
                            "device": item.get("device", "carrier-c6-01"),
                            "timestamp": str(item.get("timestamp_str") or item.get("created_at")),
                            "temperature": float(item.get("temperature", 0.0) or 0.0),
                            "humidity": float(item.get("humidity", 0.0) or 0.0),
                            "lux": float(item.get("lux", 0.0) or 0.0),
                            "g_force": float(item.get("g_force", 1.0) or 1.0),
                            "speed": float(item.get("speed", 0.0) or 0.0),
                            "lat": float(item.get("lat", 0.0) or 0.0),
                            "lng": float(item.get("lng", 0.0) or 0.0),
                            "status": item.get("status", ""),
                            "run_id": last_run
                        })
                    return history, last_run
        except Exception as e:
            print(f"DB 초기 로드 에러: {e}")
        finally:
            conn.close()
    return [], generate_run_id()

if len(data_history) == 0:
    cached_records, last_run = load_recent_session()
    if cached_records:
        data_history.extend(cached_records)
        st.session_state.run_id = last_run

# [모듈 1] 📍 실시간 GPS 궤적 지도
def render_map_module(df_gps, container, height=450):
    with container:
        st.markdown("<div style='font-size:16px; font-weight:800; color:#00e5ff; margin-bottom:6px;'>📍 실시간 주행 궤적 지도</div>", unsafe_allow_html=True)
        if df_gps.empty or 'lat' not in df_gps.columns or 'lng' not in df_gps.columns:
            st.info("🛰️ 위성 신호 및 센서 데이터 수신 대기 중입니다...")
            return

        valid_gps = df_gps[(df_gps['lat'] != 0) & (df_gps['lng'] != 0)]
        if valid_gps.empty:
            st.info("🛰️ 위성 신호 탐색 대기 중입니다 (야외 이동 시 궤적이 표시됩니다)")
            return

        cur_lat = valid_gps['lat'].iloc[-1]
        cur_lng = valid_gps['lng'].iloc[-1]

        view_state = pdk.ViewState(
            latitude=cur_lat,
            longitude=cur_lng,
            zoom=14,
            pitch=35
        )

        # 1. 주행 궤적 라인 (두껍고 선명한 형광 청록색)
        path_layer = pdk.Layer(
            "PathLayer",
            data=[{"path": valid_gps[['lng', 'lat']].values.tolist()}],
            get_path="path",
            get_color=[0, 229, 255, 230],
            width_min_pixels=4,
        )

        # 2. 충격 감지 지점 마커 (1.8G 이상: 빨간색 원형 핀포인트)
        shocks = valid_gps[valid_gps['g_force'] >= 1.8]
        shock_layer = pdk.Layer(
            "ScatterplotLayer",
            data=shocks,
            get_position="[lng, lat]",
            get_fill_color=[255, 50, 50, 220],
            get_radius=40,
            radius_min_pixels=6,
            pickable=True
        )

        # 3. 현재 차량 위치 마커
        current_layer = pdk.Layer(
            "ScatterplotLayer",
            data=valid_gps.iloc[[-1]],
            get_position="[lng, lat]",
            get_fill_color=[50, 255, 120, 240],
            get_radius=50,
            radius_min_pixels=8,
            stroked=True,
            get_line_color=[255, 255, 255, 255],
            line_width_min_pixels=2
        )

        st.pydeck_chart(pdk.Deck(
            layers=[path_layer, shock_layer, current_layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            tooltip={"text": "시각: {timestamp}\n충격: {g_force}G\n속도: {speed}km/h"},
            height=height
        ))

# [모듈 2] 💥 과일 충격량 & 속도 이중 Y축 차트
def render_gforce_module(df_chart, container, height=450):
    with container:
        st.markdown("<div style='font-size:16px; font-weight:800; color:#ff5555; margin-bottom:6px;'>💥 과일 충격량(G) & 속도(km/h) 이중 차트</div>", unsafe_allow_html=True)
        if df_chart.empty or 'g_force' not in df_chart.columns:
            st.info("데이터 수집 대기 중...")
            return

        df_c = df_chart.copy().tail(250)
        df_c['timestamp'] = pd.to_datetime(df_c['timestamp'], errors='coerce', format='mixed')
        df_c = df_c.dropna(subset=['timestamp'])

        # 메인 라인: 충격량 (오렌지-레드, 굵기 3.2px)
        g_line = alt.Chart(df_c).mark_line(color='#ff5252', strokeWidth=3.2).encode(
            x=alt.X('timestamp:T', axis=alt.Axis(labels=False, title=None)),
            y=alt.Y('g_force:Q', scale=alt.Scale(domain=[0.8, max(3.5, df_c['g_force'].max() + 0.3)]), title='충격량 (G-Force)')
        )

        # 2.0G 주의 기준선
        r2 = alt.Chart(pd.DataFrame({'y': [2.0]})).mark_rule(color='#ffaa00', strokeDash=[4, 4], strokeWidth=2).encode(y='y:Q')
        # 3.0G 위험 기준선
        r3 = alt.Chart(pd.DataFrame({'y': [3.0]})).mark_rule(color='#ff1744', strokeDash=[2, 2], strokeWidth=2.5).encode(y='y:Q')

        # 충격 이벤트 하이라이트 (>1.8G)
        shock_pts = alt.Chart(df_c[df_c['g_force'] >= 1.8]).mark_circle(size=90, color='#ff1744').encode(
            x='timestamp:T', y='g_force:Q',
            tooltip=['timestamp:T', 'g_force:Q', 'speed:Q']
        )

        # 보조 라인: 속도 (녹색 옅은 라인)
        speed_line = alt.Chart(df_c).mark_line(color='#00e676', strokeWidth=1.8, opacity=0.6).encode(
            x='timestamp:T',
            y=alt.Y('speed:Q', scale=alt.Scale(domain=[0, 130]), title='차량 속도 (km/h)')
        )

        chart = alt.layer(speed_line, g_line, r2, r3, shock_pts).resolve_scale(y='independent').properties(height=height)
        st.altair_chart(chart, use_container_width=True)

# [모듈 3] 🌡️ 온·습도 환경 추이 차트
def render_env_module(df_chart, container, height=450):
    with container:
        st.markdown("<div style='font-size:16px; font-weight:800; color:#38bdf8; margin-bottom:6px;'>🌡️ 차량 적재함 온·습도 추이</div>", unsafe_allow_html=True)
        if df_chart.empty or 'temperature' not in df_chart.columns:
            st.info("데이터 수집 대기 중...")
            return

        df_c = df_chart.copy().tail(250)
        df_c['timestamp'] = pd.to_datetime(df_c['timestamp'], errors='coerce', format='mixed')
        df_c = df_c.dropna(subset=['timestamp'])

        df_long = df_c.melt(id_vars=['timestamp'], value_vars=['temperature', 'humidity'], var_name='Metric', value_name='Value')
        df_long['Metric'] = df_long['Metric'].map({'temperature': '온도 (°C)', 'humidity': '습도 (%)'})

        chart = alt.Chart(df_long).mark_line(strokeWidth=3.0).encode(
            x=alt.X('timestamp:T', axis=alt.Axis(labels=False, title=None)),
            y=alt.Y('Value:Q', scale=alt.Scale(zero=False), title='온도 / 습도'),
            color=alt.Color('Metric:N', scale=alt.Scale(domain=['온도 (°C)', '습도 (%)'], range=['#f97316', '#38bdf8']), legend=alt.Legend(orient='top', title=None))
        ).properties(height=height)
        st.altair_chart(chart, use_container_width=True)

# [모듈 4] 💡 조도 센서 차트 (박스 개봉 감지)
def render_lux_module(df_chart, container, height=450):
    with container:
        st.markdown("<div style='font-size:16px; font-weight:800; color:#facc15; margin-bottom:6px;'>💡 실시간 조도(Lux) - 박스 개봉 모니터링</div>", unsafe_allow_html=True)
        if df_chart.empty or 'lux' not in df_chart.columns:
            st.info("데이터 수집 대기 중...")
            return

        df_c = df_chart.copy().tail(250)
        df_c['timestamp'] = pd.to_datetime(df_c['timestamp'], errors='coerce', format='mixed')
        df_c = df_c.dropna(subset=['timestamp'])

        chart = alt.Chart(df_c).mark_area(color='#facc15', opacity=0.4, line={'color': '#facc15', 'width': 2.5}).encode(
            x=alt.X('timestamp:T', axis=alt.Axis(labels=False, title=None)),
            y=alt.Y('lux:Q', scale=alt.Scale(zero=True), title='조도 (Lux)')
        )
        rule_open = alt.Chart(pd.DataFrame({'y': [500]})).mark_rule(color='#ef4444', strokeDash=[4, 4], strokeWidth=2).encode(y='y:Q')
        st.altair_chart((chart + rule_open).properties(height=height), use_container_width=True)

# ----------------------------------------------------------------
# 6. 상단 슬림 인터랙티브 바 및 2-슬롯 뷰포트 배치
# ----------------------------------------------------------------
header_box = st.container()
viewport_box = st.container()

# 실시간 루프
last_db_save_time = 0
last_packet_epoch = 0

while True:
    # 1) MQTT 큐 수신 및 세션 데이터 적재
    while not msg_queue.empty():
        msg = msg_queue.get()
        msg['run_id'] = st.session_state.run_id

        lat_v = float(msg.get("lat", 0.0))
        lng_v = float(msg.get("lng", 0.0))
        spd_v = float(msg.get("speed", 0.0))
        g_v = float(msg.get("g_force", 1.0))
        is_gps_valid = (lat_v != 0.0 and lng_v != 0.0)

        # 주행 래치 감지
        if is_gps_valid or spd_v > 2.5:
            st.session_state.trip_started = True
            if is_gps_valid:
                st.session_state.last_valid_gps = (lat_v, lng_v)

        # 터널 데드레커닝
        if not is_gps_valid and st.session_state.trip_started and st.session_state.last_valid_gps != (0.0, 0.0):
            msg['lat'] = st.session_state.last_valid_gps[0]
            msg['lng'] = st.session_state.last_valid_gps[1]

        data_history.append(msg)
        if len(data_history) > 3000:
            data_history.pop(0)

        # DB 주기적 저장 (5초 간격 or 1.8G 충격 시 즉시)
        now_t = time.time()
        if (now_t - last_db_save_time >= 5.0) or (g_v >= 1.8):
            save_to_mysql(msg, st.session_state.run_id)
            last_db_save_time = now_t

    # 최신 센서값 추출
    latest = data_history[-1] if len(data_history) > 0 else {}
    c_temp = latest.get('temperature', 0.0)
    c_humi = latest.get('humidity', 0.0)
    c_lux = latest.get('lux', 0.0)
    c_g = latest.get('g_force', 1.00)
    c_spd = latest.get('speed', 0.0)

    # ----------------------------------------------------------------
    # 상단 슬림바 렌더링 (클릭 가능한 4대 모듈 배지 버튼)
    # ----------------------------------------------------------------
    views = st.session_state.selected_views
    
    # 버튼 라벨에 순번(#1, #2)과 실시간 수치 표시
    def get_btn_label(key, icon, name, val_str):
        if key in views:
            slot_num = views.index(key) + 1
            return f"[{slot_num}번 {icon}] {name} ({val_str})"
        return f"{icon} {name} ({val_str})"

    lbl_map = get_btn_label('map', '📍', '지도', f"{latest.get('lat', 0.0):.2f}")
    lbl_g = get_btn_label('gforce', '💥', '충격·속도', f"{c_g:.2f}G")
    lbl_env = get_btn_label('env', '🌡️', '온·습도', f"{c_temp:.1f}°C")
    lbl_lux = get_btn_label('lux', '💡', '조도', f"{c_lux:.0f}lx")

    with header_box:
        c1, c2, c3, c4, c_stat = st.columns([2.5, 2.5, 2.5, 2.5, 2.2], gap="small")
        
        with c1:
            if st.button(lbl_map, key="btn_toggle_map", use_container_width=True):
                toggle_view('map')
                st.rerun()
        with c2:
            if st.button(lbl_g, key="btn_toggle_gforce", use_container_width=True):
                toggle_view('gforce')
                st.rerun()
        with c3:
            if st.button(lbl_env, key="btn_toggle_env", use_container_width=True):
                toggle_view('env')
                st.rerun()
        with c4:
            if st.button(lbl_lux, key="btn_toggle_lux", use_container_width=True):
                toggle_view('lux')
                st.rerun()
        with c_stat:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.08); border-radius:10px; padding:6px 10px; text-align:center; font-size:12px; line-height:1.4;">
                <span style="color:#00e676; font-weight:800;">🟢 LIVE</span> | <code>{c_spd:.0f}km/h</code><br>
                <span style="color:#94a3b8;">{get_kst_now().strftime('%H:%M:%S')}</span>
            </div>
            """, unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # 메인 뷰포트 렌더링 (1개 선택 시 100% 와이드, 2개 선택 시 50:50 분할)
    # ----------------------------------------------------------------
    if len(data_history) > 0:
        df_cur = pd.DataFrame(data_history)
    else:
        df_cur = pd.DataFrame(columns=DEFAULT_COLS)

    with viewport_box:
        if len(views) == 1:
            # 1개 모듈 전체화면 100% 모드
            c_full = st.container()
            active_key = views[0]
            if active_key == 'map':
                render_map_module(df_cur, c_full, height=520)
            elif active_key == 'gforce':
                render_gforce_module(df_cur, c_full, height=520)
            elif active_key == 'env':
                render_env_module(df_cur, c_full, height=520)
            elif active_key == 'lux':
                render_lux_module(df_cur, c_full, height=520)
        else:
            # 2개 모듈 50:50 분할 모드 (좌측: 1번, 우측: 2번)
            left_col, right_col = st.columns([1, 1], gap="medium")
            
            # 좌측 슬롯 (1번)
            k1 = views[0]
            if k1 == 'map': render_map_module(df_cur, left_col, height=460)
            elif k1 == 'gforce': render_gforce_module(df_cur, left_col, height=460)
            elif k1 == 'env': render_env_module(df_cur, left_col, height=460)
            elif k1 == 'lux': render_lux_module(df_cur, left_col, height=460)

            # 우측 슬롯 (2번)
            k2 = views[1]
            if k2 == 'map': render_map_module(df_cur, right_col, height=460)
            elif k2 == 'gforce': render_gforce_module(df_cur, right_col, height=460)
            elif k2 == 'env': render_env_module(df_cur, right_col, height=460)
            elif k2 == 'lux': render_lux_module(df_cur, right_col, height=460)

    time.sleep(1.0)
