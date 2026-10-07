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
        padding-top: 0.35rem !important;
        padding-bottom: 0.35rem !important;
        padding-left: 0.7rem !important;
        padding-right: 0.7rem !important;
        max-width: 100% !important;
    }
    header, footer { visibility: hidden !important; height: 0px !important; }
    
    /* 배경 다크 테마 */
    .stApp {
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
    }

    /* 드롭다운 셀렉트박스 스타일 (터치 최적화) */
    div[data-baseweb="select"] {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    /* 상단 슬림바 모듈 버튼 스타일 */
    div[data-testid="stButton"] button {
        border-radius: 10px !important;
        padding: 6px 10px !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        transition: all 0.15s ease-in-out !important;
        border: 2px solid rgba(255, 255, 255, 0.18) !important;
        background: rgba(255, 255, 255, 0.06) !important;
        color: #e2e8f0 !important;
        width: 100% !important;
    }
    div[data-testid="stButton"] button:hover {
        border-color: #00e5ff !important;
        color: #00e5ff !important;
        background: rgba(0, 229, 255, 0.12) !important;
    }

    /* 차트 및 맵 컨테이너 */
    .hud-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. 글로벌 상태 및 2-슬롯 선택 관리 로직
# ----------------------------------------------------------------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "coldchain/telemetry"
DEFAULT_COLS = ['timestamp', 'lat', 'lng', 'speed', 'g_force', 'temperature', 'humidity', 'lux', 'status', 'device', 'run_id']

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
    cur = list(st.session_state.selected_views)
    if view_key in cur:
        if len(cur) > 1:
            cur.remove(view_key)
    else:
        if len(cur) < 2:
            cur.append(view_key)
        else:
            cur.pop(0)
            cur.append(view_key)
    st.session_state.selected_views = cur

# ----------------------------------------------------------------
# 3. AWS RDS MySQL 연동 및 세션 관리 (기존 대시보드와 동일한 명칭 매핑)
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

# DB에서 과거 세션 목록 및 요약 통계 로드
@st.cache_data(ttl=60)
def get_all_run_ids_and_meta():
    run_list = ["실시간 주행 (현재 실험)"]
    meta_dict = {}
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT run_id, 
                           COUNT(*) as cnt, 
                           MIN(timestamp_str) as start_ts, 
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
                    if val not in run_list:
                        run_list.append(val)
                    meta_dict[val] = r
        except Exception as e:
            print(f"run_ids 로드 에러: {e}")
        finally:
            conn.close()
    return run_list, meta_dict

# 기존 대시보드와 동일한 지능형 세션 라벨 포맷터
def format_session_label(session_id):
    if session_id == "실시간 주행 (현재 실험)":
        return "🟢 실시간 주행 (현재 센서 스트리밍)"
    
    meta = session_meta_dict.get(session_id)
    if meta:
        cnt = meta.get('cnt', 0)
        start_ts = str(meta.get('start_ts', ''))
        max_spd = float(meta.get('max_spd') or 0.0)
        min_temp = float(meta.get('min_temp') or 0.0)
        max_temp = float(meta.get('max_temp') or 0.0)
        
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
        dt_tag = f"[{start_ts[5:10]} {start_ts[11:16]}]" if len(start_ts) >= 16 else ""
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

# 특정 과거 세션 데이터 로드 (캐싱)
@st.cache_data(ttl=300)
def load_session_data(target_run_id):
    history = []
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM sensor_data WHERE run_id = %s ORDER BY id ASC", (target_run_id,))
                items = cursor.fetchall()
            for item in items:
                ts = item.get("timestamp_str")
                if not ts or ts == "00:00:00" or str(ts).startswith("00:00") or str(ts).startswith("2026-10-01 00:00"):
                    created_at = item.get("created_at")
                    if created_at:
                        ts = (created_at + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history.append({
                    "device": item.get("device", "carrier-c6-01"),
                    "timestamp": str(ts),
                    "temperature": float(item.get("temperature", 0.0) or 0.0),
                    "humidity": float(item.get("humidity", 0.0) or 0.0),
                    "lux": float(item.get("lux", 0.0) or 0.0),
                    "g_force": float(item.get("g_force", 1.0) or 1.0),
                    "speed": float(item.get("speed", 0.0) or 0.0),
                    "lat": float(item.get("lat", 0.0) or 0.0),
                    "lng": float(item.get("lng", 0.0) or 0.0),
                    "status": item.get("status", ""),
                    "run_id": target_run_id
                })
        except Exception as e:
            print(f"과거 세션 로드 실패: {e}")
        finally:
            conn.close()
    return history

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

# [모듈 1] 📍 실시간 GPS 궤적 지도
def render_map_module(df_gps, container, height=450):
    with container:
        st.markdown("<div style='font-size:14px; font-weight:800; color:#00e5ff; margin-bottom:4px;'>📍 주행 궤적 지도</div>", unsafe_allow_html=True)
        if df_gps.empty or 'lat' not in df_gps.columns or 'lng' not in df_gps.columns:
            st.info("🛰️ 위성 신호 수신 대기 중입니다...")
            return

        valid_gps = df_gps[(df_gps['lat'] != 0) & (df_gps['lng'] != 0)]
        if valid_gps.empty:
            st.info("🛰️ 유효 GPS 좌표가 없습니다 (실내 대기 중이거나 위성 탐색 중)")
            return

        cur_lat = valid_gps['lat'].iloc[-1]
        cur_lng = valid_gps['lng'].iloc[-1]

        view_state = pdk.ViewState(
            latitude=cur_lat,
            longitude=cur_lng,
            zoom=13.5,
            pitch=35
        )

        # 1. 주행 궤적 라인 (형광 청록색)
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

        # 3. 현재 차량 위치 마커 (네온 그린 + 흰색 외곽선)
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
        st.markdown("<div style='font-size:14px; font-weight:800; color:#ff5555; margin-bottom:4px;'>💥 과일 충격량(G) & 주행속도(km/h)</div>", unsafe_allow_html=True)
        if df_chart.empty or 'g_force' not in df_chart.columns:
            st.info("데이터 수집 대기 중...")
            return

        df_c = df_chart.copy().tail(350)
        df_c['timestamp'] = pd.to_datetime(df_c['timestamp'], errors='coerce', format='mixed')
        df_c = df_c.dropna(subset=['timestamp'])

        g_line = alt.Chart(df_c).mark_line(color='#ff5252', strokeWidth=3.0).encode(
            x=alt.X('timestamp:T', axis=alt.Axis(labels=False, title=None)),
            y=alt.Y('g_force:Q', scale=alt.Scale(domain=[0.8, max(3.5, df_c['g_force'].max() + 0.3)]), title='충격량 (G)')
        )

        r2 = alt.Chart(pd.DataFrame({'y': [2.0]})).mark_rule(color='#ffaa00', strokeDash=[4, 4], strokeWidth=2).encode(y='y:Q')
        r3 = alt.Chart(pd.DataFrame({'y': [3.0]})).mark_rule(color='#ff1744', strokeDash=[2, 2], strokeWidth=2.5).encode(y='y:Q')

        shock_pts = alt.Chart(df_c[df_c['g_force'] >= 1.8]).mark_circle(size=80, color='#ff1744').encode(
            x='timestamp:T', y='g_force:Q',
            tooltip=['timestamp:T', 'g_force:Q', 'speed:Q']
        )

        speed_line = alt.Chart(df_c).mark_line(color='#00e676', strokeWidth=1.8, opacity=0.65).encode(
            x='timestamp:T',
            y=alt.Y('speed:Q', scale=alt.Scale(domain=[0, 130]), title='속도 (km/h)')
        )

        chart = alt.layer(speed_line, g_line, r2, r3, shock_pts).resolve_scale(y='independent').properties(height=height)
        st.altair_chart(chart, use_container_width=True)

# [모듈 3] 🌡️ 온·습도 환경 추이 차트
def render_env_module(df_chart, container, height=450):
    with container:
        st.markdown("<div style='font-size:14px; font-weight:800; color:#38bdf8; margin-bottom:4px;'>🌡️ 차량 적재함 온·습도 추이</div>", unsafe_allow_html=True)
        if df_chart.empty or 'temperature' not in df_chart.columns:
            st.info("데이터 수집 대기 중...")
            return

        df_c = df_chart.copy().tail(350)
        df_c['timestamp'] = pd.to_datetime(df_c['timestamp'], errors='coerce', format='mixed')
        df_c = df_c.dropna(subset=['timestamp'])

        df_long = df_c.melt(id_vars=['timestamp'], value_vars=['temperature', 'humidity'], var_name='Metric', value_name='Value')
        df_long['Metric'] = df_long['Metric'].map({'temperature': '온도 (°C)', 'humidity': '습도 (%)'})

        chart = alt.Chart(df_long).mark_line(strokeWidth=2.8).encode(
            x=alt.X('timestamp:T', axis=alt.Axis(labels=False, title=None)),
            y=alt.Y('Value:Q', scale=alt.Scale(zero=False), title='온도 / 습도'),
            color=alt.Color('Metric:N', scale=alt.Scale(domain=['온도 (°C)', '습도 (%)'], range=['#f97316', '#38bdf8']), legend=alt.Legend(orient='top', title=None))
        ).properties(height=height)
        st.altair_chart(chart, use_container_width=True)

# [모듈 4] 💡 조도 센서 차트 (박스 개봉 감지)
def render_lux_module(df_chart, container, height=450):
    with container:
        st.markdown("<div style='font-size:14px; font-weight:800; color:#facc15; margin-bottom:4px;'>💡 실시간 조도 (박스 개봉 감지)</div>", unsafe_allow_html=True)
        if df_chart.empty or 'lux' not in df_chart.columns:
            st.info("데이터 수집 대기 중...")
            return

        df_c = df_chart.copy().tail(350)
        df_c['timestamp'] = pd.to_datetime(df_c['timestamp'], errors='coerce', format='mixed')
        df_c = df_c.dropna(subset=['timestamp'])

        chart = alt.Chart(df_c).mark_area(color='#facc15', opacity=0.35, line={'color': '#facc15', 'width': 2.5}).encode(
            x=alt.X('timestamp:T', axis=alt.Axis(labels=False, title=None)),
            y=alt.Y('lux:Q', scale=alt.Scale(zero=True), title='조도 (Lux)')
        )
        rule_open = alt.Chart(pd.DataFrame({'y': [500]})).mark_rule(color='#ef4444', strokeDash=[4, 4], strokeWidth=2).encode(y='y:Q')
        st.altair_chart((chart + rule_open).properties(height=height), use_container_width=True)

# ----------------------------------------------------------------
# 6. 상단 컨트롤 바 (세션 선택기 + 실시간 센서 상태 요약) & 4대 모듈 버튼
# ----------------------------------------------------------------
run_options, session_meta_dict = get_all_run_ids_and_meta()

# Row 1: 세션 드롭다운 선택기 + 상태 모니터링 배지
col_sel, col_stat = st.columns([6.2, 3.8], gap="small")
with col_sel:
    selected_run = st.selectbox(
        "세션 선택",
        options=run_options,
        index=0,
        format_func=format_session_label,
        key="sb_selected_run",
        label_visibility="collapsed"
    )

status_placeholder = col_stat.empty()

# Row 2: 4대 모듈 인터랙티브 배지 버튼 (클릭 시 1~2개 뷰포트 토글)
views = st.session_state.selected_views

def get_slot_label(key, icon, name):
    if key in views:
        slot_idx = views.index(key) + 1
        return f"[{slot_idx}번 {icon}] {name}"
    return f"{icon} {name}"

b1, b2, b3, b4 = st.columns(4, gap="small")
with b1:
    if st.button(get_slot_label('map', '📍', '지도'), key="btn_jetson_map", use_container_width=True):
        toggle_view('map')
        st.rerun()
with b2:
    if st.button(get_slot_label('gforce', '💥', '충격·속도'), key="btn_jetson_gforce", use_container_width=True):
        toggle_view('gforce')
        st.rerun()
with b3:
    if st.button(get_slot_label('env', '🌡️', '온·습도'), key="btn_jetson_env", use_container_width=True):
        toggle_view('env')
        st.rerun()
with b4:
    if st.button(get_slot_label('lux', '💡', '조도'), key="btn_jetson_lux", use_container_width=True):
        toggle_view('lux')
        st.rerun()

# Row 3: 메인 뷰포트 레이아웃 준비
if len(views) == 1:
    slot1_container = st.empty()
    slot2_container = None
else:
    col_left, col_right = st.columns([1, 1], gap="medium")
    slot1_container = col_left.empty()
    slot2_container = col_right.empty()

# ----------------------------------------------------------------
# 7. 실시간 스트리밍 & 디스플레이 루프
# ----------------------------------------------------------------
last_db_save_time = 0
is_live_mode = (selected_run == "실시간 주행 (현재 실험)")

# 과거 세션 조회 시 DB 데이터 1회 사전 로드
if not is_live_mode:
    static_records = load_session_data(selected_run)
    df_static = pd.DataFrame(static_records) if len(static_records) > 0 else pd.DataFrame(columns=DEFAULT_COLS)
else:
    df_static = None

# 과거 모드일 때 정적 뷰포트 1회 렌더링
def render_active_view(view_key, df_data, container, h):
    if view_key == 'map':
        render_map_module(df_data, container, height=h)
    elif view_key == 'gforce':
        render_gforce_module(df_data, container, height=h)
    elif view_key == 'env':
        render_env_module(df_data, container, height=h)
    elif view_key == 'lux':
        render_lux_module(df_data, container, height=h)

if not is_live_mode:
    h_target = 520 if len(views) == 1 else 450
    with slot1_container.container():
        render_active_view(views[0], df_static, st.container(), h_target)
    if slot2_container is not None and len(views) > 1:
        with slot2_container.container():
            render_active_view(views[1], df_static, st.container(), h_target)

while True:
    # 1) 실시간 MQTT 수신 (과거 세션 열람 중에도 메모리 큐 유지)
    new_packet_arrived = False
    while not msg_queue.empty():
        msg = msg_queue.get()
        new_packet_arrived = True
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

        # 실시간 모드일 때만 DB 주기적 저장 (5초 간격 또는 1.8G 충격 시 즉시)
        if is_live_mode:
            now_t = time.time()
            if (now_t - last_db_save_time >= 5.0) or (g_v >= 1.8):
                save_to_mysql(msg, st.session_state.run_id)
                last_db_save_time = now_t

    # 2) 최근 실시간 센서 패킷 정보 추출
    if len(data_history) > 0:
        latest_live = data_history[-1]
        live_temp = latest_live.get('temperature', 0.0)
        live_humi = latest_live.get('humidity', 0.0)
        live_g = latest_live.get('g_force', 1.0)
        live_spd = latest_live.get('speed', 0.0)
        live_time = latest_live.get('timestamp', get_kst_now().strftime('%H:%M:%S'))[-8:]
    else:
        live_temp, live_humi, live_g, live_spd = 0.0, 0.0, 1.0, 0.0
        live_time = get_kst_now().strftime('%H:%M:%S')

    # 3) 상단 상태 모니터링 배지 갱신 (실시간 모드 vs 과거 세션 열람 모드)
    if is_live_mode:
        status_placeholder.markdown(f"""
        <div style="background:rgba(0,230,118,0.12); border:1px solid #00e676; border-radius:10px; padding:6px 12px; text-align:center;">
            <span style="color:#00e676; font-weight:800; font-size:13px;">🟢 LIVE 수신 중</span>
            <span style="color:#94a3b8; font-size:12px; margin-left:8px;">수집: <b>{len(data_history)}</b>건 | {live_time}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 과거 세션을 보고 있어도 현재 실시간 트럭 센서 값을 한눈에 확인 가능!
        status_placeholder.markdown(f"""
        <div style="background:rgba(56,189,248,0.12); border:1px solid #38bdf8; border-radius:10px; padding:3px 10px; text-align:center;">
            <div style="color:#38bdf8; font-weight:800; font-size:12px;">📁 과거 기록 ({len(df_static)}건)</div>
            <div style="color:#f1f5f9; font-size:11.5px; font-weight:700;">
                📡 실시간: <span style="color:#f97316;">{live_temp:.1f}°C</span> · <span style="color:#ff5252;">{live_g:.2f}G</span> · <span style="color:#00e676;">{live_spd:.0f}km/h</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4) 실시간 모드일 때 뷰포트 동적 갱신
    if is_live_mode:
        df_live = pd.DataFrame(data_history) if len(data_history) > 0 else pd.DataFrame(columns=DEFAULT_COLS)
        h_target = 520 if len(views) == 1 else 450
        
        with slot1_container.container():
            render_active_view(views[0], df_live, st.container(), h_target)
        if slot2_container is not None and len(views) > 1:
            with slot2_container.container():
                render_active_view(views[1], df_live, st.container(), h_target)

    # 과거 모드일 때는 CPU 절약을 위해 1.5초 대기, 실시간 모드는 1.0초 대기
    sleep_interval = 1.0 if is_live_mode else 1.5
    time.sleep(sleep_interval)
