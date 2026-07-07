import streamlit as st
import pymysql
import pandas as pd
import os
import qrcode
import io
from PIL import Image
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# --- 다국어 설정 (Localization) ---
LANG_DICT = {
    'KO': {
        'page_title': "프리미엄 과일 안심 이력조회",
        'landing_title': "과일의 진실된 이야기를 스캔하세요",
        'landing_subtitle': "고객님이 구매하신 과일이 생산지에서 식탁까지 온 정직한 과정을 투명하게 보여드립니다.",
        'landing_guide': "💡 **방법**: 제품에 부착된 안심 QR 코드를 스마트폰 카메라로 비춰주세요.",
        'db_error': "⚠️ 데이터 시스템 연결에 문제가 발생했습니다.",
        'no_record': "❌ '{}' 번호와 일치하는 과일 이력을 찾을 수 없습니다.",
        'title_suffix': "안심 이력",
        'subtitle': "블록체인 기반의 먹거리 안심 정보 서비스",
        'refresh_btn': "🔄 실시간 정보 갱신",
        'tab_summary': "✨ 안심 요약",
        'tab_timeline': "🚚 생산·유통 이력",
        'tab_route': "📍 이동 경로",
        'premium_fruit': "🍎 Premium {}",
        'fruit_desc': "원산지에서 식탁까지 온 정직한 과정을 투명하게 검증받은 최상의 {}입니다.",
        'origin': "원산지",
        'variety': "품종",
        'grade': "선별 등급",
        'method': "재배 방식",
        'quantity': "수량",
        'boxes': "{} 박스",
        'no_qty': "수량 미등록",
        'no_grade': "선별 전",
        'farmer_title': "🚜 농가 및 수확 정보",
        'farmer_id': "생산 농가 ID",
        'contact': "연락처 (안심번호)",
        'harvest_date': "수확 일자",
        'no_info': "정보 없음",
        'blockchain_verified': "✨ 이 과일은 투명하고 안전한 블록체인 관리 시스템을 통해 검증되었습니다. 안심하고 즐거운 시간 되세요!",
        'timeline_title': "🚚 콜드체인 타임라인",
        'route_title': "📍 실시간 이동 경로",
        'route_subtitle': "스마트 QR 스캔 및 GPS 트래커를 통해 수집된 과일의 실시간 지리정보 경로입니다.",
        'route_list': "📋 지리 좌표 경로 목록",
        'col_stage': "유통 단계",
        'col_time': "처리 일시",
        'col_lat': "위도 (Latitude)",
        'col_lon': "경도 (Longitude)",
        'no_gps': "⚠️ 이동 경로 정보(GPS)가 존재하지 않습니다.",
        'elapsed_just_now': "방금 전",
        'elapsed_min': "{}분 전",
        'elapsed_hour': "{}시간 전",
        'elapsed_day': "{}일 전",
        'stage_preparing': "준비 중",
        'stage_not_reached': "아직 해당 단계에 도달하지 않았습니다.",
        'proc_time': "⏰ 처리 시간",
        'sensor_title': "저장고 실시간 온습도",
        'temp': "온도",
        'humi': "습도",
        'optimal_state': "🟢 최적 상태 유지 중",
        'select_lang': "🌐 언어 선택 / Language",
        'origin_55630': "전북 장수군 (장수읍)",
        'origin_55631': "전북 장수군 (산서면)",
        'origin_55632': "전북 장수군 (번암면)",
        'origin_55633': "전북 장수군 (장계면)",
        'origin_55634': "전북 장수군 (천천면)",
        'origin_55635': "전북 장수군 (계남면)",
        'origin_default': "대한민국",
        'stage_A00_title': "🌱 농장 수확",
        'stage_A00_desc': "정성껏 재배한 과일을 정직하게 수확했습니다.",
        'stage_A10_title': "🏢 입고",
        'stage_A10_desc': "생산지에서 신선한 상태로 센터에 도착했습니다.",
        'stage_A11_title': "💦 세척",
        'stage_A11_desc': "깨끗하고 안전한 물로 세척 과정을 마쳤습니다.",
        'stage_A12_title': "🔍 선별",
        'stage_A12_desc': "크기와 당도, 품질을 엄격하게 선별했습니다.",
        'stage_A13_title': "📦 포장",
        'stage_A13_desc': "신선함을 유지할 수 있는 전용 패키지로 포장되었습니다.",
        'stage_A14_title': "❄️ 저장",
        'stage_A14_desc': "최적의 온도와 습도로 신선도를 보관 중입니다.",
        'stage_A15_title': "🚛 출하",
        'stage_A15_desc': "고객님을 만나기 위해 건강하게 출발했습니다!",
    },
    'EN': {
        'page_title': "Premium Fruit Traceability Inquiry",
        'landing_title': "Scan the True Story of the Fruit",
        'landing_subtitle': "We transparently show you the honest journey of your fruit from origin to table.",
        'landing_guide': "💡 **How to scan**: Focus your smartphone camera on the safe QR code attached to the product.",
        'db_error': "⚠️ Connection issues with the database system.",
        'no_record': "❌ No fruit history found matching the number '{}'.",
        'title_suffix': "Traceability",
        'subtitle': "Blockchain-based Safe Food Information Service",
        'refresh_btn': "🔄 Refresh Real-time Info",
        'tab_summary': "✨ Safe Summary",
        'tab_timeline': "🚚 Log & Timeline",
        'tab_route': "📍 Route Map",
        'premium_fruit': "🍎 Premium {}",
        'fruit_desc': "This is the premium {}, transparently verified for its honest journey from origin to table.",
        'origin': "Origin",
        'variety': "Variety",
        'grade': "Grade",
        'method': "Cultivation",
        'quantity': "Quantity",
        'boxes': "{} Box(es)",
        'no_qty': "Unregistered",
        'no_grade': "Before Sorting",
        'farmer_title': "🚜 Farm & Harvest Info",
        'farmer_id': "Farm ID",
        'contact': "Contact (Safe #)",
        'harvest_date': "Harvest Date",
        'no_info': "No Info",
        'blockchain_verified': "✨ This fruit has been verified through a transparent and secure blockchain management system. Enjoy your healthy choice!",
        'timeline_title': "🚚 Cold Chain Timeline",
        'route_title': "📍 Real-time Route Map",
        'route_subtitle': "This is the real-time geographical route of the fruit collected via smart QR scans and GPS trackers.",
        'route_list': "📋 Geographical Coordinate Route List",
        'col_stage': "Logistics Stage",
        'col_time': "Processed Time",
        'col_lat': "Latitude",
        'col_lon': "Longitude",
        'no_gps': "⚠️ No route coordinates (GPS) available.",
        'elapsed_just_now': "Just now",
        'elapsed_min': "{}m ago",
        'elapsed_hour': "{}h ago",
        'elapsed_day': "{}d ago",
        'stage_preparing': "Preparing",
        'stage_not_reached': "This stage has not been reached yet.",
        'proc_time': "⏰ Processed at",
        'sensor_title': "Real-time Storage Temp & Humidity",
        'temp': "Temperature",
        'humi': "Humidity",
        'optimal_state': "🟢 Maintaining Optimal State",
        'select_lang': "Select Language",
        'origin_55630': "Jangsu-eup, Jangsu-gun, Jeonbuk",
        'origin_55631': "Sanseo-myeon, Jangsu-gun, Jeonbuk",
        'origin_55632': "Beonam-myeon, Jangsu-gun, Jeonbuk",
        'origin_55633': "Janggye-myeon, Jangsu-gun, Jeonbuk",
        'origin_55634': "Cheoncheon-myeon, Jangsu-gun, Jeonbuk",
        'origin_55635': "Gyenam-myeon, Jangsu-gun, Jeonbuk",
        'origin_default': "Republic of Korea",
        'stage_A00_title': "🌱 Harvest",
        'stage_A00_desc': "Carefully cultivated fruit has been honestly harvested.",
        'stage_A10_title': "🏢 Receiving",
        'stage_A10_desc': "Arrived at the APC center in a fresh state from the farm.",
        'stage_A11_title': "💦 Washing",
        'stage_A11_desc': "Completed the washing process with clean and safe water.",
        'stage_A12_title': "🔍 Sorting",
        'stage_A12_desc': "Strictly sorted by size, sweetness, and quality.",
        'stage_A13_title': "📦 Packaging",
        'stage_A13_desc': "Packed in a specialized package to maintain freshness.",
        'stage_A14_title': "❄️ Storage",
        'stage_A14_desc': "Storing at optimal temperature and humidity to preserve freshness.",
        'stage_A15_title': "🚛 Shipping",
        'stage_A15_desc': "Healthy shipment has departed to meet the customer!",
    }
}

# 1. 언어 설정 초기화 (쿼리 매개변수 우선, 없으면 세션 상태 - 기본값 영어 EN 설정)
if 'lang' not in st.session_state:
    qp_lang = st.query_params.get("lang", "EN").upper()
    st.session_state.lang = qp_lang if qp_lang in ['KO', 'EN'] else 'EN'

# 2. 페이지 설정 호출 (가장 먼저 실행)
st.set_page_config(
    page_title=LANG_DICT[st.session_state.lang]['page_title'], 
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

    /* 앱 전체 배경화면: 프리미엄 실크 그레이-민트 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ee 100%) !important;
    }

    .main {
        background: transparent !important;
    }

    /* Streamlit 메인 콘텐트 컨테이너 스타일링 (데스크톱 플로팅 디바이스 뷰) */
    [data-testid="stAppViewBlockContainer"], [data-testid="stMainBlockContainer"] {
        background-color: #ffffff !important;
        border-radius: 24px !important;
        padding: 45px 35px !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid rgba(225, 228, 232, 0.6) !important;
        max-width: 680px !important;
        margin: 40px auto !important;
    }

    /* 모바일 브라우저 대응 (테두리 및 외부 배경 제거) */
    @media (max-width: 768px) {
        [data-testid="stAppViewBlockContainer"], [data-testid="stMainBlockContainer"] {
            border-radius: 0px !important;
            box-shadow: none !important;
            border: none !important;
            padding: 20px 15px !important;
            margin: 0px auto !important;
            max-width: 100% !important;
        }
        .stApp {
            background: #ffffff !important;
        }
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
        grid-template-columns: repeat(3, 1fr);
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
        text-align: left;
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
def format_elapsed_time(timestamp, lang='KO'):
    if not timestamp: return ""
    kst = timezone(timedelta(hours=9))
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except:
            return ""
    if type(timestamp).__name__ == 'date':
        timestamp = datetime.combine(timestamp, datetime.min.time())
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=kst)
    now = datetime.now(kst)
    diff = now - timestamp
    total_seconds = int(diff.total_seconds())
    
    if total_seconds < 60:
        return LANG_DICT[lang]['elapsed_just_now']
    if total_seconds < 3600:
        return LANG_DICT[lang]['elapsed_min'].format(total_seconds // 60)
    if total_seconds < 86400:
        return LANG_DICT[lang]['elapsed_hour'].format(total_seconds // 3600)
    return LANG_DICT[lang]['elapsed_day'].format(diff.days)

def get_origin_name(ac, lang='KO'):
    ac_str = str(ac) if ac is not None else ""
    key = f"origin_{ac_str}"
    if key in LANG_DICT[lang]:
        return LANG_DICT[lang][key]
    return LANG_DICT[lang]['origin_default']

def mask_contact(contact, lang='KO'):
    if not contact: 
        return LANG_DICT[lang]['no_info']
    contact = str(contact).strip()
    if len(contact) > 4:
        return contact[:-4] + "****"
    return "****"

# --- 다국어 데이터 번역 헬퍼 함수 ---
def normalize_grade(grade_str):
    if not grade_str:
        return "선별 전"
    grade_str = str(grade_str).strip().upper()
    if grade_str in ["상", "H", "HIGH", "A"]:
        return "상"
    elif grade_str in ["중", "M", "MEDIUM", "B"]:
        return "중"
    elif grade_str in ["하", "L", "LOW", "C"]:
        return "하"
    return grade_str

def translate_grade(grade_str, lang):
    norm = normalize_grade(grade_str)
    if norm == "상":
        return "상" if lang == 'KO' else "H"
    elif norm == "중":
        return "중" if lang == 'KO' else "M"
    elif norm == "하":
        return "하" if lang == 'KO' else "L"
    if lang == 'KO':
        return norm
    else:
        if norm == "선별 전":
            return "Before Sorting"
        return norm

def translate_fruit(fruit, lang):
    if lang == 'KO':
        return fruit
    if not fruit:
        return ""
    fruit_lower = fruit.lower()
    mapping = {
        "사과": "Apple",
        "참외": "Korean Melon",
        "복숭아": "Peach",
        "배": "Pear",
        "귤": "Tangerine",
        "감귤": "Tangerine"
    }
    for k, v in mapping.items():
        if k in fruit_lower:
            return v
    return fruit

def translate_variety(vt, lang):
    if lang == 'KO':
        return vt
    if not vt:
        return ""
    mapping = {
        "후지": "Fuji",
        "홍로": "Hongro",
        "신고": "Shingo",
        "황도": "Yellow Peach",
        "백도": "White Peach",
        "천도": "Nectarine",
        "감귤": "Tangerine",
        "조생": "Early-season"
    }
    for k, v in mapping.items():
        if k in vt:
            return v
    return vt

def translate_method(mt, lang):
    if lang == 'KO':
        return mt
    if not mt:
        return ""
    mapping = {
        "자연재배": "Natural",
        "유기농": "Organic",
        "무농약": "Pesticide-Free"
    }
    return mapping.get(mt, mt)

# --- 메인 화면 언어 선택기 (Main Screen Language Selector) ---
col_lang_left, col_lang_right = st.columns([3.8, 1.2])
with col_lang_right:
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

# --- 로직 시작 ---
query_params = st.query_params
fm_id = query_params.get("FmID", None)
url_grade = query_params.get("grade", None)

# 1. 랜딩 페이지 (FmID가 없을 때)
if not fm_id:
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 class="hero-title" style="background:none; -webkit-text-fill-color:initial; color:#2ecc71;">{LANG_DICT[st.session_state.lang]["landing_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-subtitle">{LANG_DICT[st.session_state.lang]["landing_subtitle"]}</p>', unsafe_allow_html=True)
    
    # 가이드 이미지 표시 (상대 경로로 수정)
    guide_img_path = os.path.join(os.path.dirname(__file__), "consumer_guide.png")
    if os.path.exists(guide_img_path):
        st.image(guide_img_path, use_container_width=True)
    
    st.info(LANG_DICT[st.session_state.lang]["landing_guide"])
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
    st.error(f"{LANG_DICT[st.session_state.lang]['db_error']} ({e})")
    st.stop()

if not records:
    st.error(LANG_DICT[st.session_state.lang]['no_record'].format(fm_id))
    st.stop()

# 3. 정보 구성
latest = records[-1]
fruit_type = latest.get('FrT', '과일')
variety = latest.get('Vt', '')
origin = get_origin_name(latest.get('AC'), st.session_state.lang)
# DB에 등급 정보가 있을 수도 있고(A12 레코드), URL에 있을 수도 있음
db_grade = next((r.get('grade') for r in records if r.get('grade')), None)
raw_grade = url_grade or db_grade or "선별 전"
display_grade = translate_grade(raw_grade, st.session_state.lang)

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

# --- 메인 화면 렌더링 (헤더 2열 구성: 좌측 타이틀/새로고침, 우측 정품 인증 QR) ---
col_header_left, col_header_right = st.columns([3.2, 1.2])

with col_header_left:
    fruit_type_translated = translate_fruit(fruit_type, st.session_state.lang)
    st.markdown(f'<h1 class="hero-title" style="text-align:left; margin-bottom:5px;">🍏 {fruit_type_translated} {LANG_DICT[st.session_state.lang]["title_suffix"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:left; color:#515154; margin-top:-5px; font-weight: 500; font-size: 0.95rem; margin-bottom: 15px;">{LANG_DICT[st.session_state.lang]["subtitle"]}</p>', unsafe_allow_html=True)
    
    # 새로고침 버튼을 타이틀 아래에 콤팩트하게 배치
    if st.button(LANG_DICT[st.session_state.lang]["refresh_btn"], key="top_refresh_btn"):
        st.rerun()

with col_header_right:
    # 1. 과일 카테고리 매핑 (Step3_Sorting_QR_Creator와 일치)
    fruit_images_mapping = {
        "Apples": ["apple4.png", "apple3.png", "apple2.png"],
        "Pears": ["pear4.png", "pear3.png", "pear2.png"],
        "Peaches": ["peach4.png", "peach3.png", "peach2.png"],
        "Tangerines": ["tangerine4.png", "tangerine3.png", "tangerine2.png"],
        "Melons": ["koreanmelon4.png", "koreanmelon3.png", "koreanmelon2.png"]
    }
    
    category_key = None
    for k in fruit_images_mapping.keys():
        if k.lower() in fruit_type.lower() or (k == "Apples" and "사과" in fruit_type) or (k == "Pears" and "배" in fruit_type) or (k == "Peaches" and "복숭아" in fruit_type) or (k == "Tangerines" and ("귤" in fruit_type or "감귤" in fruit_type)) or (k == "Melons" and "참외" in fruit_type):
            category_key = k
            break
            
    # 2. 등급 인덱스 매핑 (A/상=0, B/중=1, C/하=2)
    grade_idx = 0
    norm_grade = normalize_grade(raw_grade)
    if norm_grade == "상":
        grade_idx = 0
    elif norm_grade == "중":
        grade_idx = 1
    elif norm_grade == "하":
        grade_idx = 2
    else:
        grade_idx = 0
        
    qr_url = f"https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/?FmID={fm_id}&grade={display_grade}&AC={latest.get('AC', '')}&FrT={latest.get('FrT', '')}"
    
    # 3. 고해상도 및 높은 복원력(ERROR_CORRECT_H)으로 QR 생성하여 과일 로고를 중앙에 합성
    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    
    if category_key and category_key in fruit_images_mapping:
        filename = fruit_images_mapping[category_key][grade_idx]
        overlay_path = os.path.join(os.path.dirname(__file__), "static", filename)
        if os.path.exists(overlay_path):
            logo_size = int(img.size[0] * 0.25)
            logo = Image.open(overlay_path).resize((logo_size, logo_size), Image.LANCZOS).convert("RGBA")
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, mask=logo)
            
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_bytes = buf.getvalue()
    
    # 우측 상단에 정렬되도록 컨테이너와 함께 배치
    st.image(qr_bytes, use_container_width=True)

st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

# 탭 생성
tab1, tab2, tab3 = st.tabs([
    LANG_DICT[st.session_state.lang]['tab_summary'], 
    LANG_DICT[st.session_state.lang]['tab_timeline'], 
    LANG_DICT[st.session_state.lang]['tab_route']
])

with tab1:
    st.markdown(f'<h2 style="text-align:center; font-weight:800; color:#1d1d1f; margin-bottom:5px; margin-top:10px;">{LANG_DICT[st.session_state.lang]["premium_fruit"].format(fruit_type_translated)}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; font-size:1rem; color:#666; margin-bottom:25px;">{LANG_DICT[st.session_state.lang]["fruit_desc"].format(fruit_type_translated)}</p>', unsafe_allow_html=True)

    # 해당 등급의 구체적인 수량 추출 (A12 선별 단계의 AGrade, BGrade, CGrade 컬럼 참조)
    a12_record = next((r for r in records if r.get("Lo") == "A12"), None)
    grade_qty = None
    if a12_record:
        norm_grade = normalize_grade(raw_grade)
        if norm_grade == "상":
            grade_qty = a12_record.get("AGrade")
        elif norm_grade == "중":
            grade_qty = a12_record.get("BGrade")
        elif norm_grade == "하":
            grade_qty = a12_record.get("CGrade")

    if grade_qty is None or grade_qty == "":
        # 만약 A12에 구체적인 등급 수량이 없으면 전체 수량(Qt)을 백업으로 사용
        grade_qty = latest.get("Qt", "미등록")

    if grade_qty != "미등록" and grade_qty != "Unregistered" and grade_qty is not None:
        grade_qty_display = LANG_DICT[st.session_state.lang]['boxes'].format(grade_qty)
    else:
        grade_qty_display = LANG_DICT[st.session_state.lang]['no_qty']

    variety_display = translate_variety(variety, st.session_state.lang)
    method_display = translate_method(latest.get("Mt", "자연재배"), st.session_state.lang)

    # 핵심 정보 카드 (4열)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="info-card" style="min-height: 85px;"><small style="color:#666; font-size:0.8rem;">{LANG_DICT[st.session_state.lang]["origin"]}</small><br><b style="font-size:1.05rem; display:block; margin-top:2px;">{origin}</b></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="info-card" style="min-height: 85px;"><small style="color:#666; font-size:0.8rem;">{LANG_DICT[st.session_state.lang]["variety"]}</small><br><b style="font-size:1.05rem; display:block; margin-top:2px;">{variety_display}</b></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="info-card" style="min-height: 85px;">
            <small style="color:#666; font-size:0.8rem;">{LANG_DICT[st.session_state.lang]["grade"]}</small><br>
            <b style="color:#2ecc71; font-size:1.25rem; display:block; margin: 1px 0;">{display_grade}</b>
            <span style="color:#8e8e93; font-size:0.75rem; font-weight:500;">{LANG_DICT[st.session_state.lang]["quantity"]}: {grade_qty_display}</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="info-card" style="min-height: 85px;"><small style="color:#666; font-size:0.8rem;">{LANG_DICT[st.session_state.lang]["method"]}</small><br><b style="font-size:1.05rem; display:block; margin-top:2px;">{method_display}</b></div>', unsafe_allow_html=True)

    # 수확 일자 포맷팅
    harvest_date = latest.get("HD", "미등록")
    if isinstance(harvest_date, str) and len(harvest_date) > 10:
        harvest_date = harvest_date[:10]
    elif hasattr(harvest_date, 'strftime'):
        harvest_date = harvest_date.strftime('%Y-%m-%d')
    else:
        harvest_date = str(harvest_date)

    # 농가 정보 (Farmer Info) 리디자인
    st.markdown(f"<h3 style='font-size:1.3rem; font-weight:700; margin-top:20px;'>{LANG_DICT[st.session_state.lang]['farmer_title']}</h3>", unsafe_allow_html=True)
    farmer_id_display = latest.get("FmID", "미등록")
    if farmer_id_display == "미등록" or farmer_id_display == "Unregistered" or not farmer_id_display:
        farmer_id_display = LANG_DICT[st.session_state.lang]['no_qty']
    farmer_contact = mask_contact(latest.get("Ct", ""), st.session_state.lang)
    
    st.markdown(f"""
    <div class="farmer-card">
        <div class="farmer-info-item">
            <div style="font-size: 1.8rem;">🆔</div>
            <div>
                <div class="farmer-label">{LANG_DICT[st.session_state.lang]['farmer_id']}</div>
                <div class="farmer-value">{farmer_id_display}</div>
            </div>
        </div>
        <div class="farmer-info-item">
            <div style="font-size: 1.8rem;">📞</div>
            <div>
                <div class="farmer-label">{LANG_DICT[st.session_state.lang]['contact']}</div>
                <div class="farmer-value">{farmer_contact}</div>
            </div>
        </div>
        <div class="farmer-info-item">
            <div style="font-size: 1.8rem;">📅</div>
            <div>
                <div class="farmer-label">{LANG_DICT[st.session_state.lang]['harvest_date']}</div>
                <div class="farmer-value">{harvest_date}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    
    st.success(LANG_DICT[st.session_state.lang]['blockchain_verified'])

with tab2:
    st.markdown(f"<h3 style='font-size:1.3rem; font-weight:700; margin-bottom:15px;'>{LANG_DICT[st.session_state.lang]['timeline_title']}</h3>", unsafe_allow_html=True)
    
    # 단계 설정 (A00 농장 단계 추가)
    stage_names = {
        "A00": (LANG_DICT[st.session_state.lang]["stage_A00_title"], LANG_DICT[st.session_state.lang]["stage_A00_desc"], "HD"),
        "A10": (LANG_DICT[st.session_state.lang]["stage_A10_title"], LANG_DICT[st.session_state.lang]["stage_A10_desc"], "APC_AD"),
        "A11": (LANG_DICT[st.session_state.lang]["stage_A11_title"], LANG_DICT[st.session_state.lang]["stage_A11_desc"], "APC_WD"),
        "A12": (LANG_DICT[st.session_state.lang]["stage_A12_title"], LANG_DICT[st.session_state.lang]["stage_A12_desc"], "APC_RT"),
        "A13": (LANG_DICT[st.session_state.lang]["stage_A13_title"], LANG_DICT[st.session_state.lang]["stage_A13_desc"], "APC_PT"),
        "A14": (LANG_DICT[st.session_state.lang]["stage_A14_title"], LANG_DICT[st.session_state.lang]["stage_A14_desc"], "APC_StD"),
        "A15": (LANG_DICT[st.session_state.lang]["stage_A15_title"], LANG_DICT[st.session_state.lang]["stage_A15_desc"], "APC_OP")
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
            elapsed = format_elapsed_time(stage_time, st.session_state.lang)
            
            st.markdown(f"""
            <div class="timeline-item active-stage">
                <span style="font-weight:700; font-size:1.1rem; color:#1d1d1f;">{title}</span>
                <span class="elapsed-tag">{elapsed}</span>
                <p style="color:#515154; margin-top:5px; font-size:0.9rem; font-weight:400; margin-bottom:5px;">{default_desc}</p>
                <small style="color:#86868b; font-size:0.8rem;">⏰ {LANG_DICT[st.session_state.lang]['proc_time']}: {stage_time if stage_time else ""}</small>
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
                        <span style="font-weight: 700; color: #155724; font-size: 0.95rem;">{LANG_DICT[st.session_state.lang]['sensor_title']}</span>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <div style="background: white; padding: 4px 10px; border-radius: 6px; border: 1px solid #c3e6cb; min-width: 80px; text-align: center;">
                            <small style="color: #666; font-size: 0.7rem; display: block; margin-bottom: 2px;">{LANG_DICT[st.session_state.lang]['temp']}</small>
                            <b style="color: #27ae60; font-size: 1rem;">{tp_val}°C</b>
                        </div>
                        <div style="background: white; padding: 4px 10px; border-radius: 6px; border: 1px solid #c3e6cb; min-width: 80px; text-align: center;">
                            <small style="color: #666; font-size: 0.7rem; display: block; margin-bottom: 2px;">{LANG_DICT[st.session_state.lang]['humi']}</small>
                            <b style="color: #2980b9; font-size: 1rem;">{hm_val}%</b>
                        </div>
                    </div>
                    <span style="color: #2ecc71; font-size: 0.85rem; font-weight: 600; margin-left: auto;">{LANG_DICT[st.session_state.lang]['optimal_state']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="timeline-item pending-stage">
                <span style="font-weight:700; font-size:1.1rem; color:#8e8e93;">{title}</span>
                <span style="background-color: #f2f2f7; color: #8e8e93 !important; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; margin-left: 10px;">{LANG_DICT[st.session_state.lang]['stage_preparing']}</span>
                <p style="color:#a1a1a6; margin-top:5px; font-size:0.9rem; font-weight:400; margin-bottom:5px;">{LANG_DICT[st.session_state.lang]['stage_not_reached']}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown(f"<h3 style='font-size:1.3rem; font-weight:700; margin-bottom:10px;'>{LANG_DICT[st.session_state.lang]['route_title']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#515154; font-size:0.9rem; margin-bottom:20px;'>{LANG_DICT[st.session_state.lang]['route_subtitle']}</p>", unsafe_allow_html=True)
    
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
            "단계": LANG_DICT[st.session_state.lang]['stage_A00_title'],
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
        
        st.markdown(f"<h4 style='font-size:1.15rem; font-weight:700; margin-top:25px; margin-bottom:10px;'>{LANG_DICT[st.session_state.lang]['route_list']}</h4>", unsafe_allow_html=True)
        display_df = df_map[["단계", "시간", "latitude", "longitude"]].copy()
        display_df.columns = [
            LANG_DICT[st.session_state.lang]['col_stage'],
            LANG_DICT[st.session_state.lang]['col_time'],
            LANG_DICT[st.session_state.lang]['col_lat'],
            LANG_DICT[st.session_state.lang]['col_lon']
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning(LANG_DICT[st.session_state.lang]['no_gps'])
