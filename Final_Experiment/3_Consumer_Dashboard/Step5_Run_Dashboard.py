import streamlit as st
import pymysql
import pandas as pd
import os
from datetime import datetime, timedelta
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

    /* 글로벌 텍스트 색상 강제 지정 */
    html, body, [class*="css"], [data-testid="stMarkdownContainer"] {
        color: #1d1d1f !important;
    }

    .main {
        background-color: #ffffff;
    }

    .stApp {
        background-color: #ffffff;
    }

    /* 카드 스타일 (높이 균일화 및 중앙 정렬) */
    .info-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #eef0f2;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        color: #1d1d1f;
        height: 130px; /* 모든 카드 높이 통일 */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    /* 버튼 스타일 커스텀 */
    div.stButton > button {
        background-color: #f0f2f6;
        color: #1d1d1f;
        border-radius: 20px;
        border: none;
        padding: 8px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #e0e4ea;
        color: #2ecc71;
        border: none;
    }

    /* 생산자 프로필 카드 전용 스타일 */
    .farmer-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 20px 30px;
        border-left: 5px solid #2ecc71;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .farmer-info-item {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .farmer-label {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 2px;
    }

    .farmer-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1d1d1f;
    }
    .hero-title {
        font-weight: 800;
        font-size: 2.2rem;
        color: #1d1d1f !important;
        text-align: center;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        color: #515154 !important;
        font-weight: 600;
        font-size: 1.5rem; /* 품종 글씨 크기 확대 */
        text-align: center;
        margin-bottom: 30px;
    }

    /* 타임라인 스타일 */
    .timeline-item {
        border-left: 3px solid #2ecc71;
        padding-left: 20px;
        margin-bottom: 30px;
        position: relative;
        color: #1d1d1f;
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
        color: #2e7d32 !important;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 10px;
    }

    /* 알림창 텍스트 색상 보정 */
    .stAlert p {
        color: #1d1d1f !important;
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
    
    # 타입 처리 (문자열인 경우 파싱)
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except:
            return ""
    
    # date 객체인 경우 datetime으로 변환
    if type(timestamp).__name__ == 'date':
        timestamp = datetime.combine(timestamp, datetime.min.time())
    
    now = datetime.now()
    
    # [시차 보정 로직]
    # 서버 시간이 UTC이고 데이터가 KST(+9)일 경우 diff가 큰 음수가 됨
    diff = now - timestamp
    if diff.total_seconds() < -18000: # 5시간 이상 미래 시간으로 잡힌다면 시차 문제로 판단
        now = now + timedelta(hours=9)
        diff = now - timestamp

    total_seconds = int(diff.total_seconds())
    
    if total_seconds < 0: return "방금 전" 
    
    if total_seconds >= 86400: # 1일 이상
        return f"{total_seconds // 86400}일 전"
    elif total_seconds >= 3600: # 1시간 이상
        return f"{total_seconds // 3600}시간 전"
    elif total_seconds >= 60: # 1분 이상
        return f"{total_seconds // 60}분 전"
    else:
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

def mask_contact(contact):
    if not contact: return "정보 없음"
    contact = str(contact).strip()
    if len(contact) > 4:
        # 뒤에서 4자리를 ****로 변경
        return contact[:-4] + "****"
    return "****"

# --- 로직 시작 ---
query_params = st.query_params
fm_id = query_params.get("FmID", None)
url_grade = query_params.get("grade", None)

# 1. 랜딩 페이지 (FmID가 없을 때)
if not fm_id:
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title" style="background:none; -webkit-text-fill-color:initial; color:#2ecc71;">과일의 진실된 이야기를 스캔하세요</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">고객님이 구매하신 과일이 생산지에서 식탁까지 온 정직한 과정을 투명하게 보여드립니다.</p>', unsafe_allow_html=True)
    
    # 가이드 이미지 표시 (상대 경로로 수정)
    guide_img_path = os.path.join(os.path.dirname(__file__), "consumer_guide.png")
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
display_grade = url_grade or db_grade or "선별 전"

# --- 메인 화면 렌더링 ---
st.markdown(f'<h1 class="hero-title">🍎 {fruit_type} 안심 이력</h1>', unsafe_allow_html=True)

# 새로고침 버튼 (중앙 배치)
col_l, col_btn, col_r = st.columns([1, 1, 1])
with col_btn:
    if st.button("🔄 정보 새로고침", use_container_width=True):
        st.rerun()

st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

# 핵심 정보 카드 (4열로 확장)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="info-card"><small style="color:#666;">원산지</small><br><b>{origin}</b></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="info-card"><small style="color:#666;">품종</small><br><b>{variety}</b></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="info-card"><small style="color:#666;">선별 등급</small><br><b style="color:#2ecc71; font-size:1.4rem;">{display_grade}</b></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="info-card"><small style="color:#666;">재배 방식</small><br><b>{latest.get("Mt", "자연재배")}</b></div>', unsafe_allow_html=True)

# 농가 정보 (Farmer Info) 리디자인
st.markdown("### 👨‍🌾 생산자 정보")
farmer_id_display = latest.get("FmID", "미등록")
farmer_contact = mask_contact(latest.get("Ct", ""))
st.markdown(f"""
<div class="farmer-card">
    <div class="farmer-info-item">
        <div style="font-size: 1.8rem;">🆔</div>
        <div>
            <div class="farmer-label">생산 농가 ID</div>
            <div class="farmer-value">{farmer_id_display}</div>
        </div>
    </div>
    <div class="farmer-info-item">
        <div style="font-size: 1.8rem;">📞</div>
        <div>
            <div class="farmer-label">연락처 (안심번호)</div>
            <div class="farmer-value">{farmer_contact}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.subheader("🚚 과일 타임라인")

# 단계 설정 (A00 농장 단계 추가)
stage_names = {
    "A00": ("🌱 농장 수확", "정성껏 재배한 과일을 정직하게 수확했습니다.", "HD"),
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
                <span style="font-weight:700; font-size:1.1rem; color:#1d1d1f;">{title}</span>
                <span class="elapsed-tag">{elapsed}</span>
                <p style="color:#515154; margin-top:5px; font-size:0.9rem; font-weight:400;">{desc}</p>
                <small style="color:#86868b; font-size:0.8rem;">{stage_time if stage_time else ""}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if stage_code == "A14" and row.get("Tp") is not None:
                st.info(f"❄️ **신선 보관 정보**: 온도 {row['Tp']}°C / 습도 {row['Hm']}% (최적 상태 유지)")

st.success("✨ 이 과일은 투명하고 안전한 관리 시스템을 통해 검증되었습니다. 안심하고 즐거운 시간 되세요!")
