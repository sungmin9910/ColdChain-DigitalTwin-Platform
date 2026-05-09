import streamlit as st
import pymysql
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- 페이지 설정 ---
st.set_page_config(
    page_title="프리미엄 과일 안심 이력조회", 
    page_icon="🍏", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 커스텀 CSS (프리미엄 디자인) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;300;400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    .stApp {
        background-color: transparent;
    }

    /* 카드 스타일 */
    .info-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 20px;
    }

    /* 헤더 스타일 */
    .hero-title {
        font-weight: 900;
        font-size: 2.5rem;
        color: #1d1d1f;
        text-align: center;
        margin-bottom: 10px;
        background: -webkit-linear-gradient(#2ecc71, #27ae60);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #86868b;
        text-align: center;
        margin-bottom: 40px;
    }

    /* 타임라인 스타일 */
    .timeline-item {
        border-left: 3px solid #2ecc71;
        padding-left: 20px;
        margin-bottom: 30px;
        position: relative;
    }

    .timeline-item::before {
        content: '';
        position: absolute;
        width: 15px;
        height: 15px;
        background-color: #2ecc71;
        border-radius: 50%;
        left: -9px;
        top: 5px;
    }

    .elapsed-tag {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 10px;
    }

    /* 랜딩 페이지 전용 */
    .landing-container {
        text-align: center;
        padding: 50px 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- DB 설정 ---
DB_HOST = "15.165.68.30"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, port=DB_PORT, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- 유틸리티 함수 ---
def format_elapsed_time(timestamp):
    if not timestamp: return ""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except:
            return ""
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days}일 전"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}시간 전"
    minutes = (diff.seconds % 3600) // 60
    if minutes > 0:
        return f"{minutes}분 전"
    return "방금 전"

def get_origin_name(ac):
    origin_map = {
        "55630": "전북 장수군 (장수읍)",
        "55631": "전북 장수군 (산서면)",
        "55632": "전북 장수군 (번암면)",
        "55633": "전북 장수군 (장계면)",
        "55634": "전북 장수군 (천천면)",
        "55635": "전북 장수군 (계남면)"
    }
    return origin_map.get(str(ac), "대한민국")

# --- 로직 시작 ---
query_params = st.query_params
fm_id = query_params.get("FmID", None)
url_grade = query_params.get("grade", None)

# 1. 랜딩 페이지 (FmID가 없을 때)
if not fm_id:
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">과일의 진실된 이야기를 스캔하세요</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">고객님이 구매하신 과일이 생산지에서 식탁까지 온 정직한 과정을 투명하게 보여드립니다.</p>', unsafe_allow_html=True)
    
    # 가이드 이미지 표시
    guide_img_path = r"C:\Users\yuyub\.gemini\antigravity\brain\c2ccf74d-f504-4cfc-ad00-1767cfa1c705\consumer_qr_guide_1778287608691.png"
    if os.path.exists(guide_img_path):
        st.image(guide_img_path, use_container_width=True)
    
    st.info("💡 **방법**: 제품에 부착된 안심 QR 코드를 스마트폰 카메라로 비춰주세요.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 2. 데이터 조회
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM qr WHERE FmID = %s ORDER BY Lo ASC"
    cursor.execute(query, (fm_id,))
    records = cursor.fetchall()
    conn.close()
except Exception as e:
    st.error(f"⚠️ 데이터 시스템 연결에 문제가 발생했습니다. ({e})")
    st.stop()

if not records:
    st.error(f"❌ '{fm_id}' 번호와 일치하는 과일 이력을 찾을 수 없습니다.")
    st.stop()

# 3. 정보 구성
latest = records[-1]
fruit_type = latest.get('FrT', '과일')
variety = latest.get('Vt', '')
origin = get_origin_name(latest.get('AC'))
# DB에 등급 정보가 있을 수도 있고(A12 레코드), URL에 있을 수도 있음
db_grade = next((r.get('grade') for r in records if r.get('grade')), None)
display_grade = url_grade or db_grade or "품질 인증 완료"

# --- 메인 화면 렌더링 ---
st.markdown(f'<h1 class="hero-title">🍎 {fruit_type} 안심 이력</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="hero-subtitle">{variety} | {origin}</p>', unsafe_allow_html=True)

# 핵심 정보 카드
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="info-card" style="text-align:center;"><small>원산지</small><br><b>{origin}</b></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="info-card" style="text-align:center;"><small>선별 등급</small><br><b style="color:#2ecc71;">{display_grade}</b></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="info-card" style="text-align:center;"><small>재배 방식</small><br><b>{latest.get("Mt", "자연재배")}</b></div>', unsafe_allow_html=True)

st.divider()
st.subheader("🚚 신선 타임라인")

# 단계 설정
stage_names = {
    "A10": ("🏢 입고", "생산지에서 신선한 상태로 센터에 도착했습니다.", "APC_AD"),
    "A11": ("💦 세척", "깨끗하고 안전한 물로 세척 과정을 마쳤습니다.", "APC_WD"),
    "A12": ("🔍 선별", "크기와 당도, 품질을 엄격하게 선별했습니다.", "APC_RT"),
    "A13": ("📦 포장", "신선함을 유지할 수 있는 전용 패키지로 포장되었습니다.", "APC_PT"),
    "A14": ("❄️ 저장", "최적의 온도와 습도로 신선도를 보관 중입니다.", "APC_StD"),
    "A15": ("🚛 출하", "고객님을 만나기 위해 건강하게 출발했습니다!", "APC_OP")
}

# 기록된 단계 렌더링
for row in records:
    stage_code = row.get("Lo")
    if stage_code in stage_names:
        title, desc, time_col = stage_names[stage_code]
        stage_time = row.get(time_col)
        elapsed = format_elapsed_time(stage_time)
        
        with st.container():
            st.markdown(f"""
            <div class="timeline-item">
                <span style="font-weight:700; font-size:1.1rem;">{title}</span>
                <span class="elapsed-tag">{elapsed}</span>
                <p style="color:#666; margin-top:5px; font-size:0.9rem;">{desc}</p>
                <small style="color:#999;">{stage_time if stage_time else ""}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if stage_code == "A14" and row.get("Tp") is not None:
                st.info(f"❄️ **신선 보관 정보**: 온도 {row['Tp']}°C / 습도 {row['Hm']}% (최적 상태 유지)")

st.success("✨ 이 과일은 투명하고 안전한 관리 시스템을 통해 검증되었습니다. 안심하고 즐거운 시간 되세요!")
