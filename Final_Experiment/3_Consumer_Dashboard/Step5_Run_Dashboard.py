import streamlit as st
import pymysql
import pandas as pd
import os
from datetime import datetime, timedelta, timezone
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
        font-family: 'Noto Sans KR', sans-serif !important;
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
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(46, 204, 113, 0.12);
        border-color: #2ecc71;
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
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        margin-bottom: 30px;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
    }
    
    @media (max-width: 992px) {
        .farmer-card {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 480px) {
        .farmer-card {
            grid-template-columns: 1fr;
        }
    }

    .farmer-info-item {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .farmer-label {
        font-size: 0.85rem;
        color: #86868b;
        margin-bottom: 2px;
    }

    .farmer-value {
        font-size: 1.05rem;
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
    .timeline-container {
        padding-left: 10px;
        margin-top: 15px;
    }

    .timeline-item {
        border-left: 3px solid #2ecc71;
        padding-left: 20px;
        margin-bottom: 25px;
        position: relative;
        color: #1d1d1f;
    }

    .timeline-item::before {
        content: '';
        position: absolute;
        width: 14px;
        height: 14px;
        background-color: #2ecc71;
        border: 3px solid #ffffff;
        box-shadow: 0 0 0 2px #2ecc71;
        border-radius: 50%;
        left: -9px;
        top: 5px;
    }
    
    /* 대기 중인 타임라인 스타일 */
    .timeline-item.pending-stage {
        border-left: 3px dashed #d1d1d6 !important;
        opacity: 0.55;
    }
    
    .timeline-item.pending-stage::before {
        background-color: #d1d1d6 !important;
        box-shadow: 0 0 0 2px #d1d1d6 !important;
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
    
    /* 탭 스타일 대폭 향상 (iOS 세그먼트 스타일) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #f1f2f6;
        padding: 5px;
        border-radius: 25px;
        border: none;
        margin-bottom: 25px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #515154 !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        transition: all 0.25s ease !important;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #2ecc71 !important;
        background-color: rgba(46, 204, 113, 0.05) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffffff !important;
        color: #2ecc71 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* 탭 하단의 기본 라인 제거 */
    .stTabs [data-baseweb="tab-highlight-bar"] {
        display: none !important;
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
    
    # 한국 시간대(KST, UTC+9) 설정
    kst = timezone(timedelta(hours=9))
    
    # 타입 처리 (문자열인 경우 파싱)
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except:
            return ""
    
    # date 객체인 경우 datetime으로 변환
    if type(timestamp).__name__ == 'date':
        timestamp = datetime.combine(timestamp, datetime.min.time())
    
    # timestamp가 naive인 경우 KST로 간주 (DB 데이터 특성상)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=kst)
    
    # 현재 시간을 KST로 가져옴
    now = datetime.now(kst)
    
    diff = now - timestamp
    total_seconds = int(diff.total_seconds())
    
    if total_seconds < 60:
        return "방금 전"
    
    if total_seconds < 3600:
        return f"{total_seconds // 60}분 전"
    
    if total_seconds < 86400:
        return f"{total_seconds // 3600}시간 전"
    
    return f"{diff.days}일 전"

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

def get_fruit_image_path(fruit_type):
    fruit_type_lower = fruit_type.lower()
    mapping = {
        "사과": "apple",
        "apple": "apple",
        "참외": "koreanmelon",
        "melon": "koreanmelon",
        "복숭아": "peach",
        "peach": "peach",
        "배": "pear",
        "pear": "pear",
        "귤": "tangerine",
        "감귤": "tangerine",
        "tangerine": "tangerine",
        "orange": "tangerine"
    }
    fruit_key = None
    for k, v in mapping.items():
        if k in fruit_type_lower:
            fruit_key = v
            break
            
    if not fruit_key:
        return None
        
    for suffix in ["2", "3", "4", ""]:
        filename = f"{fruit_key}{suffix}.png"
        path = os.path.join(os.path.dirname(__file__), "static", filename)
        if os.path.exists(path):
            return path
    return None

# --- 메인 화면 렌더링 ---
st.markdown(f'<h1 class="hero-title">🍏 {fruit_type} 안심 이력</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; color:#515154; margin-top:-5px; font-weight: 500;">블록체인 기반의 먹거리 안심 정보 서비스</p>', unsafe_allow_html=True)

# 새로고침 버튼 (텍스트 줄바꿈 방지를 위해 너비 넓게 확보)
col_l, col_btn, col_r = st.columns([1.2, 1.6, 1.2])
with col_btn:
    if st.button("🔄 실시간 정보 갱신", use_container_width=True):
        st.rerun()

st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

# 탭 생성
tab1, tab2, tab3 = st.tabs(["✨ 안심 요약", "🚚 생산·유통 이력", "📍 이동 경로"])

with tab1:
    # 과일 이미지 표시 (있는 경우)
    fruit_img_path = get_fruit_image_path(fruit_type)
    if fruit_img_path:
        col_img_l, col_img, col_img_r = st.columns([1, 1.2, 1])
        with col_img:
            st.image(fruit_img_path, use_container_width=True)
            
    st.markdown(f'<h2 style="text-align:center; font-weight:800; color:#1d1d1f; margin-bottom:5px;">🍎 Premium {fruit_type}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; font-size:1rem; color:#666; margin-bottom:25px;">원산지에서 식탁까지 온 정직한 과정을 투명하게 검증받은 최상의 {fruit_type}입니다.</p>', unsafe_allow_html=True)

    # 해당 등급 수량 추출 및 포맷
    grade_qty = latest.get("Qt", "미등록")
    if grade_qty != "미등록":
        grade_qty_display = f"{grade_qty} 박스"
    else:
        grade_qty_display = "수량 미등록"

    # 핵심 정보 카드 (4열)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="info-card" style="min-height: 85px;"><small style="color:#666; font-size:0.8rem;">원산지</small><br><b style="font-size:1.05rem; display:block; margin-top:2px;">{origin}</b></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="info-card" style="min-height: 85px;"><small style="color:#666; font-size:0.8rem;">품종</small><br><b style="font-size:1.05rem; display:block; margin-top:2px;">{variety}</b></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="info-card" style="min-height: 85px;">
            <small style="color:#666; font-size:0.8rem;">선별 등급</small><br>
            <b style="color:#2ecc71; font-size:1.25rem; display:block; margin: 1px 0;">{display_grade}</b>
            <span style="color:#8e8e93; font-size:0.75rem; font-weight:500;">수량: {grade_qty_display}</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="info-card" style="min-height: 85px;"><small style="color:#666; font-size:0.8rem;">재배 방식</small><br><b style="font-size:1.05rem; display:block; margin-top:2px;">{latest.get("Mt", "자연재배")}</b></div>', unsafe_allow_html=True)

    # 수확 일자 포맷팅
    harvest_date = latest.get("HD", "미등록")
    if isinstance(harvest_date, str) and len(harvest_date) > 10:
        harvest_date = harvest_date[:10]
    elif hasattr(harvest_date, 'strftime'):
        harvest_date = harvest_date.strftime('%Y-%m-%d')
    else:
        harvest_date = str(harvest_date)

    # 농가 정보 (Farmer Info) 리디자인
    st.markdown("<h3 style='font-size:1.3rem; font-weight:700; margin-top:20px;'>👨‍🌾 생산자 및 수확 정보</h3>", unsafe_allow_html=True)
    farmer_id_display = latest.get("FmID", "미등록")
    farmer_contact = mask_contact(latest.get("Ct", ""))
    producer_name = latest.get("Rp", "미등록")
    
    st.markdown(f"""
    <div class="farmer-card">
        <div class="farmer-info-item">
            <div style="font-size: 1.8rem;">👨‍🌾</div>
            <div>
                <div class="farmer-label">생산자</div>
                <div class="farmer-value">{producer_name}</div>
            </div>
        </div>
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
        <div class="farmer-info-item">
            <div style="font-size: 1.8rem;">📅</div>
            <div>
                <div class="farmer-label">수확 일자</div>
                <div class="farmer-value">{harvest_date}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("✨ 이 과일은 투명하고 안전한 블록체인 관리 시스템을 통해 검증되었습니다. 안심하고 즐거운 시간 되세요!")

with tab2:
    st.markdown("<h3 style='font-size:1.3rem; font-weight:700; margin-bottom:15px;'>🚚 콜드체인 타임라인</h3>", unsafe_allow_html=True)
    
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

    # 완료된 단계와 미완료된 단계를 구분하여 렌더링
    completed_stages = {r.get("Lo"): r for r in records}
    timeline_order = ["A00", "A10", "A11", "A12", "A13", "A14", "A15"]
    
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    for code in timeline_order:
        title, default_desc, time_col = stage_names[code]
        if code in completed_stages:
            row = completed_stages[code]
            stage_time = row.get(time_col)
            elapsed = format_elapsed_time(stage_time)
            
            st.markdown(f"""
            <div class="timeline-item active-stage">
                <span style="font-weight:700; font-size:1.1rem; color:#1d1d1f;">{title}</span>
                <span class="elapsed-tag">{elapsed}</span>
                <p style="color:#515154; margin-top:5px; font-size:0.9rem; font-weight:400; margin-bottom:5px;">{default_desc}</p>
                <small style="color:#86868b; font-size:0.8rem;">⏰ 처리 시간: {stage_time if stage_time else ""}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # A00 단계 추가 정보 표시 생략 (수확일자가 타임라인 메인 시간에 표기되므로)
            pass

            # A14 단계일 때 추가 센서 정보 표시
            if code == "A14" and row.get("Tp") is not None:
                try:
                    tp_val = f"{float(row.get('Tp')):.1f}"
                except (ValueError, TypeError):
                    tp_val = str(row.get('Tp'))
                
                try:
                    hm_val = f"{float(row.get('Hm')):.1f}"
                except (ValueError, TypeError):
                    hm_val = str(row.get('Hm'))
                st.markdown(f"""
                <div style="background-color: #f1fcf4; border-radius: 8px; padding: 12px 18px; border: 1px solid #d4edda; margin: -15px 0 20px 20px; display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.3rem;">❄️</span>
                        <span style="font-weight: 700; color: #155724; font-size: 0.95rem;">저장고 실시간 온습도</span>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <div style="background: white; padding: 4px 10px; border-radius: 6px; border: 1px solid #c3e6cb; min-width: 80px; text-align: center;">
                            <small style="color: #666; font-size: 0.7rem; display: block; margin-bottom: 2px;">온도</small>
                            <b style="color: #27ae60; font-size: 1rem;">{tp_val}°C</b>
                        </div>
                        <div style="background: white; padding: 4px 10px; border-radius: 6px; border: 1px solid #c3e6cb; min-width: 80px; text-align: center;">
                            <small style="color: #666; font-size: 0.7rem; display: block; margin-bottom: 2px;">습도</small>
                            <b style="color: #2980b9; font-size: 1rem;">{hm_val}%</b>
                        </div>
                    </div>
                    <span style="color: #2ecc71; font-size: 0.85rem; font-weight: 600; margin-left: auto;">🟢 최적 상태 유지 중</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="timeline-item pending-stage">
                <span style="font-weight:700; font-size:1.1rem; color:#8e8e93;">{title}</span>
                <span style="background-color: #f2f2f7; color: #8e8e93 !important; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; margin-left: 10px;">준비 중</span>
                <p style="color:#a1a1a6; margin-top:5px; font-size:0.9rem; font-weight:400; margin-bottom:5px;">아직 해당 단계에 도달하지 않았습니다.</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("<h3 style='font-size:1.3rem; font-weight:700; margin-bottom:10px;'>📍 실시간 이동 경로</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#515154; font-size:0.9rem; margin-bottom:20px;'>스마트 QR 스캔 및 GPS 트래커를 통해 수집된 과일의 실시간 지리정보 경로입니다.</p>", unsafe_allow_html=True)
    
    # 4. GPS 이동 경로 수집
    map_data = []

    # 원산지 좌표 기본값 설정
    ac_code = str(latest.get("AC", ""))
    origin_lat, origin_lon = None, None
    origin_coords = {
        "55630": (35.647, 127.521),
        "55631": (35.617, 127.422),
        "55632": (35.539, 127.553),
        "55633": (35.727, 127.585),
        "55634": (35.707, 127.481),
        "55635": (35.696, 127.575)
    }
    if ac_code in origin_coords:
        origin_lat, origin_lon = origin_coords[ac_code]

    # A00 단계는 원산지 좌표로 채움
    if origin_lat and origin_lon:
        map_data.append({
            "단계": "🌱 농장 수확",
            "latitude": origin_lat,
            "longitude": origin_lon,
            "시간": latest.get("HD", "")
        })

    # 나머지 단계 중 GPS 좌표가 있는 데이터 추가
    for r in records:
        stage_code = r.get("Lo")
        if stage_code == "A00":
            continue
        lat = r.get("Lat")
        lon = r.get("lon")
        if lat is not None and lon is not None:
            try:
                lat = float(lat)
                lon = float(lon)
                if lat != 0.0 and lon != 0.0 and abs(lat) > 1.0:
                    stage_name = stage_names.get(stage_code, (stage_code, "", ""))[0]
                    time_col = stage_names.get(stage_code, ("", "", ""))[2]
                    stage_time = r.get(time_col, "")
                    map_data.append({
                        "단계": stage_name,
                        "latitude": lat,
                        "longitude": lon,
                        "시간": stage_time
                    })
            except:
                pass

    if map_data:
        df_map = pd.DataFrame(map_data)
        st.map(df_map)
        
        st.markdown("<h4 style='font-size:1.15rem; font-weight:700; margin-top:25px; margin-bottom:10px;'>📋 지리 좌표 경로 목록</h4>", unsafe_allow_html=True)
        display_df = df_map[["단계", "시간", "latitude", "longitude"]].copy()
        display_df.columns = ["유통 단계", "처리 일시", "위도 (Latitude)", "경도 (Longitude)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 이동 경로 정보(GPS)가 존재하지 않습니다.")
