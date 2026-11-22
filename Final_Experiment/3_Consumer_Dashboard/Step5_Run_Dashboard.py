import streamlit as st
import pymysql
import pandas as pd
import pydeck as pdk
import math
import os
import qrcode
import io
from PIL import Image
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import sys

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from cloud_backend.db_v2.bridge_sync import sync_v1_delta_to_v2, make_sha256
from cloud_backend.supply_chain_spec import (
    get_crop_code,
    normalize_area_code,
    normalize_fmid_2digit,
    build_lot_id_16,
    is_v3_lot_id,
    detect_protocol_version,
)

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
        'origin_55517': "전북 무주군 (무주읍)",
        'origin_55518': "전북 무주군 (무주읍)",
        'origin_55549': "전북 무주군 (설천면)",
        'origin_55527': "전북 무주군 (적상면)",
        'origin_55540': "전북 무주군 (안성면)",
        'origin_55559': "전북 무주군 (무풍면)",
        'origin_55434': "전북 진안군 (진안읍)",
        'origin_55435': "전북 진안군 (진안읍)",
        'origin_55451': "전북 진안군 (마령면)",
        'origin_55455': "전북 진안군 (백운면)",
        'origin_55459': "전북 진안군 (성수면)",
        'origin_55416': "전북 진안군 (부귀면)",
        'origin_default': "대한민국",
        'stage_A00_title': "🌱 농가 수확 (A00)",
        'stage_A00_desc': "산지 농가에서 수확하고 16자리 고유 코드 기반 안심 QR을 발급했습니다.",
        'stage_A01_title': "🏡 농가 창고 보관 (A01)",
        'stage_A01_desc': "수확 직후 농가 저온창고에서 예냉 및 신선 보관을 거쳤습니다.",
        'stage_A02_title': "🚜 농가 출하 (A02)",
        'stage_A02_desc': "산지유통센터(APC)를 향해 1구간 운송을 시작했습니다.",
        'stage_B10_title': "🏢 APC 입고 (B10)",
        'stage_B10_desc': "산지유통센터(APC)에 신선한 상태로 입고되었습니다.",
        'stage_B12_PRE_title': "❄️ APC 창고 · 선별 전 (B12)",
        'stage_B12_PRE_desc': "선별 전 APC 저온창고에서 최적 온습도로 원물을 보관했습니다.",
        'stage_B11_title': "🔍 APC 선별 · 유색QR 변경 (B11)",
        'stage_B11_desc': "크기와 당도, 품질을 엄격하게 선별하고 등급별 유색 QR로 교체했습니다.",
        'stage_B12_POST_title': "❄️ APC 창고 · 선별 후 (B12)",
        'stage_B12_POST_desc': "등급 선별 후 출하 전까지 APC 저온창고에 안전하게 보관했습니다.",
        'stage_B13_title': "🚛 APC 출하 (B13)",
        'stage_B13_desc': "APC에서 유통 창고를 향해 2구간 냉장 운송을 시작했습니다.",
        'stage_C10_title': "🏬 유통 창고 저장 (C10)",
        'stage_C10_desc': "유통 물류센터 저온창고에 도착하여 신선하게 보관 중입니다.",
        'stage_C11_title': "🚚 유통 출하 · 판매처 출발 (C11)",
        'stage_C11_desc': "유통 창고에서 판매처를 향해 3구간 냉장 배송을 출발했습니다.",
        'stage_D10_title': "🏪 판매처 도착 (D10)",
        'stage_D10_desc': "전 구간 콜드체인 안전 운송을 마치고 판매처에 신선하게 도착했습니다!",
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
        'stage_A16_title': "🏪 판매처 도착",
        'stage_A16_desc': "콜드체인 안전 운송을 마치고 판매처에 신선하게 도착했습니다!",
        'route_leg1': "🌱 농가 → APC 운송 (1구간)",
        'route_leg2': "🚛 APC → 유통창고 운송 (2구간)",
        'route_leg2_legacy': "🚛 APC → 판매처 냉장운송 (2구간)",
        'route_leg3': "🚚 유통창고 → 판매처 배송 (3구간)",
        'route_apc_hub': "🏢 APC 공정 (B10~B13)",
        'route_apc_hub_legacy': "🏢 APC 품질공정 (A10~A15)",
        'route_dist_hub': "🏬 유통 창고 (C10~C11)",
        'route_in_transit': "🚚 실시간 배송 중",
        'route_telemetry_title': "❄️ 운송 구간 실시간 콜드체인 검증",
        'route_avg_temp': "운송 평균 온도",
        'route_max_g': "최대 충격량",
        'route_gps_pts': "실측 도로 궤적",
        'route_pts_unit': "{}개 지점",
        'route_safe_badge': "🟢 전 구간 안전 운송",
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
        'origin_55517': "Muju-eup, Muju-gun, Jeonbuk",
        'origin_55518': "Muju-eup, Muju-gun, Jeonbuk",
        'origin_55549': "Seolcheon-myeon, Muju-gun, Jeonbuk",
        'origin_55527': "Jeoksang-myeon, Muju-gun, Jeonbuk",
        'origin_55540': "Anseong-myeon, Muju-gun, Jeonbuk",
        'origin_55559': "Mupung-myeon, Muju-gun, Jeonbuk",
        'origin_55434': "Jinan-eup, Jinan-gun, Jeonbuk",
        'origin_55435': "Jinan-eup, Jinan-gun, Jeonbuk",
        'origin_55451': "Maryeong-myeon, Jinan-gun, Jeonbuk",
        'origin_55455': "Baegun-myeon, Jinan-gun, Jeonbuk",
        'origin_55459': "Seongsu-myeon, Jinan-gun, Jeonbuk",
        'origin_55416': "Bugwi-myeon, Jinan-gun, Jeonbuk",
        'origin_default': "Republic of Korea",
        'stage_A00_title': "🌱 Farm Harvest (A00)",
        'stage_A00_desc': "Harvested at the farm and issued a 16-digit traceable raw QR code.",
        'stage_A01_title': "🏡 Farm Storage (A01)",
        'stage_A01_desc': "Pre-cooled and stored fresh at the farm's cold storage facility.",
        'stage_A02_title': "🚜 Farm Dispatch (A02)",
        'stage_A02_desc': "Departed from the farm toward the APC center (Leg 1 transport).",
        'stage_B10_title': "🏢 APC Receiving (B10)",
        'stage_B10_desc': "Arrived fresh at the APC center from the farm.",
        'stage_B12_PRE_title': "❄️ APC Storage · Pre-Sort (B12)",
        'stage_B12_PRE_desc': "Stored under optimal temperature & humidity in APC storage prior to sorting.",
        'stage_B11_title': "🔍 APC Sorting & Colored QR (B11)",
        'stage_B11_desc': "Strictly graded and upgraded to color-coded grade QR labels.",
        'stage_B12_POST_title': "❄️ APC Storage · Post-Sort (B12)",
        'stage_B12_POST_desc': "Stored under cold-chain control in APC storage after grading.",
        'stage_B13_title': "🚛 APC Dispatch (B13)",
        'stage_B13_desc': "Departed from APC toward the distribution warehouse (Leg 2 transport).",
        'stage_C10_title': "🏬 Distribution Storage (C10)",
        'stage_C10_desc': "Arrived and stored safely in the distribution center cold warehouse.",
        'stage_C11_title': "🚚 Distribution Dispatch (C11)",
        'stage_C11_desc': "Dispatched from distribution warehouse to the retail store (Leg 3 transport).",
        'stage_D10_title': "🏪 Retail Arrival (D10)",
        'stage_D10_desc': "Safely arrived at the retail store via verified end-to-end cold-chain!",
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
        'stage_A16_title': "🏪 Retail Arrival",
        'stage_A16_desc': "Safely arrived at the retail store via cold-chain transport!",
        'route_leg1': "🌱 Farm → APC (Leg 1)",
        'route_leg2': "🚛 APC → Dist. Warehouse (Leg 2)",
        'route_leg2_legacy': "🚛 APC → Retail Cold-Chain (Leg 2)",
        'route_leg3': "🚚 Dist. → Retail Store (Leg 3)",
        'route_apc_hub': "🏢 APC Center (B10~B13)",
        'route_apc_hub_legacy': "🏢 APC Quality Hub (A10~A15)",
        'route_dist_hub': "🏬 Distribution Hub (C10~C11)",
        'route_in_transit': "🚚 Live In-Transit",
        'route_telemetry_title': "❄️ Transport Cold-Chain Telemetry",
        'route_avg_temp': "Avg Transport Temp",
        'route_max_g': "Peak Impact",
        'route_gps_pts': "Road GPS Track",
        'route_pts_unit': "{} pts",
        'route_safe_badge': "🟢 Verified Safe Route",
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

# --- DB 설정 (v2 정규화 DB 메인 + v1 스캐너 호환 브릿지) ---
DB_HOST = os.getenv("DB_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
DB_FALLBACK_HOST = "15.165.68.30"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = os.getenv("MYSQL_V2_DATABASE", "lab225_v2")
DB_V1_NAME = os.getenv("MYSQL_DATABASE", "lab225")
DB_PORT = 3306

def get_db_connection(db_name=None):
    target_db = db_name or DB_NAME
    try:
        return pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=target_db, port=DB_PORT, charset="utf8mb4",
            connect_timeout=8, cursorclass=pymysql.cursors.DictCursor
        )
    except Exception:
        return pymysql.connect(
            host=DB_FALLBACK_HOST, user=DB_USER, password=DB_PASSWORD,
            database=target_db, port=DB_PORT, charset="utf8mb4",
            connect_timeout=8, cursorclass=pymysql.cursors.DictCursor
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
    if not fruit:
        return ""
    fruit_clean = str(fruit).replace("+", " ").strip()
    fruit_lower = fruit_clean.lower()
    if lang == 'KO':
        ko_mapping = {
            "apples": "사과",
            "apple": "사과",
            "melons": "참외",
            "korean melon": "참외",
            "melon": "참외",
            "peaches": "복숭아",
            "peach": "복숭아",
            "pears": "배",
            "pear": "배",
            "tangerines": "감귤",
            "tangerine": "감귤",
        }
        for k, v in ko_mapping.items():
            if k in fruit_lower:
                return v
        return fruit_clean
    mapping = {
        "사과": "Apple",
        "apples": "Apple",
        "apple": "Apple",
        "참외": "Korean Melon",
        "복숭아": "Peach",
        "peaches": "Peach",
        "배": "Pear",
        "pears": "Pear",
        "귤": "Tangerine",
        "감귤": "Tangerine",
        "tangerines": "Tangerine",
    }
    for k, v in mapping.items():
        if k in fruit_lower:
            return v
    return fruit_clean

def translate_variety(vt, lang):
    if not vt:
        return ""
    vt_clean = str(vt).replace("+", " ").strip()
    vt_lower = vt_clean.lower()
    if lang == 'KO':
        ko_mapping = {
            "fuji apple": "후지 사과",
            "fuji": "후지",
            "hongro apple": "홍로 사과",
            "hongro": "홍로",
            "gamhong apple": "감홍 사과",
            "shingo pear": "신고 배",
            "shingo": "신고",
            "wonhwang pear": "원황 배",
            "gamcheon pear": "감천 배",
        }
        for k, v in ko_mapping.items():
            if k in vt_lower:
                return v
        return vt_clean
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
        if k in vt_clean:
            return v
    return vt_clean

def translate_method(mt, lang):
    if not mt:
        return ""
    mt_clean = str(mt).replace("+", " ").strip()
    mt_lower = mt_clean.lower()
    if lang == 'KO':
        ko_mapping = {
            "organic": "유기농",
            "conventional": "관행재배",
            "natural": "자연재배",
            "pesticide-free": "무농약",
        }
        return ko_mapping.get(mt_lower, mt_clean)
    mapping = {
        "자연재배": "Natural",
        "유기농": "Organic",
        "무농약": "Pesticide-Free",
        "관행재배": "Conventional",
    }
    return mapping.get(mt_clean, mt_clean)

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
fm_id = query_params.get("LotID", None) or query_params.get("lot_id", None) or query_params.get("FmID", None) or query_params.get("fmid", None)
url_grade = query_params.get("grade", None) or query_params.get("pkg_grade", None)

# 1. 랜딩 페이지 및 24/7 클라우드 통합 포털 (FmID가 없을 때 또는 mode=admin일 때)
if not fm_id:
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 class="hero-title" style="background:none; -webkit-text-fill-color:initial; color:#2ecc71;">{LANG_DICT[st.session_state.lang]["landing_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-subtitle">{LANG_DICT[st.session_state.lang]["landing_subtitle"]}</p>', unsafe_allow_html=True)
    
    guide_img_path = os.path.join(os.path.dirname(__file__), "consumer_guide.png")
    if os.path.exists(guide_img_path):
        st.image(guide_img_path, use_container_width=True)
    
    st.info(LANG_DICT[st.session_state.lang]["landing_guide"])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 24/7 상시 클라우드 현장 작업자/관리자 포털 (PC 전원 OFF 상태에서도 스마트폰에서 A00/B11 생성 가능) ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔐 현장 작업자 / 관리자 통합 포털 (농가 A00 16자리 QR · APC B11 유색 QR · 이력 조회)", expanded=(query_params.get("mode") == "admin")):
        import random
        import hashlib
        from urllib.parse import urlencode, urlparse, parse_qs
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

        STREAMLIT_BASE_URL = "https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/"
        STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
        FARM_ICONS = {
            "Apples": "apple.png",
            "Pears": "pear.png",
            "Peaches": "peach.png",
            "Tangerines": "tangerine.png",
            "Melons": "koreanmelon.png",
        }
        GRADE_ICONS = {
            "Apples": ["apple4.png", "apple3.png", "apple2.png"],
            "Pears": ["pear4.png", "pear3.png", "pear2.png"],
            "Peaches": ["peach4.png", "peach3.png", "peach2.png"],
            "Tangerines": ["tangerine4.png", "tangerine3.png", "tangerine2.png"],
            "Melons": ["koreanmelon4.png", "koreanmelon3.png", "koreanmelon2.png"],
        }
        VARIETY_OPTIONS = {
            "Apples": ["Fuji Apple", "Hongro Apple", "Gamhong Apple"],
            "Pears": ["Shingo Pear", "Wonhwang Pear", "Gamcheon Pear"],
            "Peaches": ["mibaegdo", "cheonjungdobaegdo", "yumyeongdo"],
            "Tangerines": ["eunju tangerine", "cheong tangerine", "mandarin"],
            "Melons": ["cham-oe", "net melon", "baegja melon"],
        }

        def _make_portal_qr_bytes(qr_url: str, icon_name: str = None, rounded: bool = True) -> bytes:
            qr_obj = qrcode.QRCode(
                version=4,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr_obj.add_data(qr_url)
            qr_obj.make(fit=True)
            if rounded:
                q_img = qr_obj.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer()).convert("RGBA")
            else:
                q_img = qr_obj.make_image(fill_color="black", back_color="white").convert("RGBA")
            if icon_name:
                ic_path = os.path.join(STATIC_DIR, icon_name)
                if os.path.exists(ic_path):
                    try:
                        l_size = int(q_img.size[0] * 0.25)
                        logo_im = Image.open(ic_path).convert("RGBA").resize((l_size, l_size), Image.LANCZOS)
                        pos = ((q_img.size[0] - logo_im.size[0]) // 2, (q_img.size[1] - logo_im.size[1]) // 2)
                        q_img.paste(logo_im, pos, mask=logo_im)
                    except Exception:
                        pass
            buf_io = io.BytesIO()
            q_img.save(buf_io, format="PNG")
            return buf_io.getvalue()

        pin_val = st.text_input("🔑 권한 PIN 번호 입력 (0000: 통합관리자 | 1111: 농가 | 2222: APC)", value="0000", type="password")
        if pin_val not in ("0000", "1111", "2222"):
            st.warning("올바른 PIN 번호(0000, 1111, 2222)를 입력하세요.")
            st.stop()

        portal_tabs = []
        if pin_val in ("0000", "1111"):
            portal_tabs.append("🌾 1. 농가 수확·16자리 무색 QR (A00)")
        if pin_val in ("0000", "2222"):
            portal_tabs.append("🏭 2. APC 선별·유색 QR 변경 (B11)")
        portal_tabs.append("🔍 3. 소비자 안심 이력 바로 조회")

        selected_ptab = st.radio("작업 모듈 선택", portal_tabs, horizontal=True)
        st.markdown("---")

        # [모듈 1] 농가 수확 무색 QR 생성 (A00 - 16자리 통합 코드)
        if selected_ptab.startswith("🌾"):
            st.subheader("🌾 농가 수확 등록 및 16자리 무색 QR 발급 (A00)")
            st.caption("AreaCode(5자리) + FmID(2자리) + aT 작물코드(3자리) + 수확날짜(6자리) = 총 16자리 고유 코드가 자동 생성됩니다. 이후 농가창고(A01)·농가출하(A02)는 QR 스캐너로 진행합니다.")
            c1, c2 = st.columns(2)
            with c1:
                f_ac_label = st.selectbox("지역 코드 5자리 (Area Code, AC)", [
                    "55630 (장수 장수읍)", "55631 (장수 산서면)", "55632 (장수 번암면)", "55633 (장수 장계면)", "55634 (장수 천천면)",
                    "55518 (무주 무주읍)", "55549 (무주 설천면)", "55527 (무주 적상면)", "55540 (무주 안성면)", "55559 (무주 무풍면)",
                    "55435 (진안 진안읍)", "55451 (진안 마령면)", "55455 (진안 백운면)", "55459 (진안 성수면)", "55416 (진안 부귀면)",
                ])
                f_ac = normalize_area_code(f_ac_label)
                f_frt = st.selectbox("과일 종류 (Fruit Type, FrT)", list(VARIETY_OPTIONS.keys()))
                f_ct = st.text_input("연락처 (Contact Info, Ct)", value="01012345678")
                f_hn = st.number_input("수확 횟수 (Harvesting No., HN)", min_value=1, max_value=99, value=1)
                f_hd = st.date_input("수확 일자 (Harvest Date, HD)", value=datetime.now(timezone(timedelta(hours=9))).date())
            with c2:
                f_fmid = st.text_input("농가 고유 번호 2자리 (Farmer ID, FmID)", value="07", max_chars=2)
                f_vt = st.selectbox("품종 (Variety, Vt)", VARIETY_OPTIONS[f_frt])
                f_mt = st.selectbox("재배 방식 (Farming Method, Mt)", ["Organic", "Pesticide-Free", "Conventional", "Natural"])
                f_qt = st.number_input("총 수확 수량 (Quantity, Qt)", min_value=1, max_value=99999, value=100)
                preview_cc = get_crop_code(f_frt, f_vt)
                preview_lot = build_lot_id_16(f_ac, f_fmid, f_frt, f_vt, f_hd, crop_code=preview_cc)
                st.info(f"🔑 **16자리 LotID 미리보기**: `{preview_lot}` (작물코드 `{preview_cc}`)")

            if st.button("🛡️ A00 DB 저장 + 16자리 무색 농가 QR 생성", use_container_width=True, type="primary"):
                try:
                    conn_p = get_db_connection()
                    sync_v1_delta_to_v2(conn_p, src_db=DB_V1_NAME, dst_db=DB_NAME)
                    cur_p = conn_p.cursor()
                    cur_p.execute("SET time_zone = '+09:00'")
                    cur_p.execute("SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') as srv_dt")
                    srv_now_str = cur_p.fetchone()["srv_dt"]
                    hd_str = f_hd.strftime("%Y-%m-%d")
                    ac5 = normalize_area_code(f_ac)
                    fm2 = normalize_fmid_2digit(f_fmid)
                    cc3 = get_crop_code(f_frt, f_vt)
                    lot_id_val = build_lot_id_16(ac5, fm2, f_frt, f_vt, hd_str, crop_code=cc3)

                    # 1) 물리 ESP32 스캐너 호환용 lab225.qr A00 기록
                    cur_p.execute(f"""
                        INSERT INTO `{DB_V1_NAME}`.`qr` (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Rp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        "A00", ac5, fm2, lot_id_val, cc3, f_frt, f_vt, f_ct.strip(),
                        srv_now_str, None, str(f_qt), f_mt, str(f_hn), None, None
                    ))
                    v1_qr_id = cur_p.lastrowid

                    # 2) lab225_v2 정규화 저장: harvest_lots(current_stage='A00', protocol_ver='v3') + stage_events(A00만 기록)
                    cur_p.execute(f"""
                        INSERT INTO `{DB_NAME}`.`harvest_lots`
                        (lot_id, origin_zip, farmer_code, crop_code, fruit_type, variety, farmer_phone, cultivation,
                         harvest_no, total_qty, harvest_date, storage_date, deliver_date,
                         ag_practice, current_stage, protocol_ver, is_test, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, NULL, NULL, 'A00', 'v3', 0, %s)
                        ON DUPLICATE KEY UPDATE
                            origin_zip=VALUES(origin_zip), farmer_code=VALUES(farmer_code), crop_code=VALUES(crop_code),
                            fruit_type=VALUES(fruit_type), variety=VALUES(variety), farmer_phone=VALUES(farmer_phone),
                            cultivation=VALUES(cultivation), harvest_no=VALUES(harvest_no), total_qty=VALUES(total_qty),
                            harvest_date=VALUES(harvest_date), protocol_ver='v3', is_test=0
                    """, (
                        lot_id_val, ac5, fm2, cc3, f_frt, f_vt, f_ct.strip(), f_mt,
                        int(f_hn), int(f_qt), hd_str, srv_now_str
                    ))

                    a00_hash = make_sha256({"lot_id": lot_id_val, "stage": "A00", "ac": ac5, "cc": cc3, "qt": int(f_qt), "hd": hd_str})
                    cur_p.execute(f"""
                        INSERT INTO `{DB_NAME}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, tx_hash)
                        VALUES (%s, NULL, 'A00', %s, %s)
                        ON DUPLICATE KEY UPDATE event_at=VALUES(event_at), tx_hash=COALESCE(VALUES(tx_hash), tx_hash)
                    """, (lot_id_val, srv_now_str, a00_hash))

                    if v1_qr_id:
                        cur_p.execute(f"""
                            INSERT INTO `{DB_NAME}`.`_sync_watermark` (source_table, last_id)
                            VALUES ('qr', %s) ON DUPLICATE KEY UPDATE last_id=GREATEST(last_id, VALUES(last_id))
                        """, (v1_qr_id,))

                    conn_p.commit()
                    conn_p.close()

                    q_params = {
                        "LotID": lot_id_val, "AC": ac5, "FmID": fm2, "CC": cc3,
                        "Ct": f_ct.strip(), "FrT": f_frt, "Vt": f_vt, "HD": hd_str,
                        "Mt": f_mt, "HN": str(f_hn), "Qt": str(f_qt),
                    }
                    farm_qr_url = f"{STREAMLIT_BASE_URL}?{urlencode(q_params)}"
                    farm_fn = f"{lot_id_val}_QR.png"
                    st.session_state["last_farm_qr"] = {
                        "bytes": _make_portal_qr_bytes(farm_qr_url, FARM_ICONS.get(f_frt, "apple.png"), rounded=True),
                        "filename": farm_fn,
                        "lot_id": lot_id_val,
                        "fmid": fm2,
                        "crop_code": cc3,
                        "hd_full": srv_now_str,
                    }
                except Exception as ex_f:
                    st.error(f"❌ 농가 QR 생성 오류: {ex_f}")

            if "last_farm_qr" in st.session_state:
                lf = st.session_state["last_farm_qr"]
                st.success(f"✅ A00 DB 저장 완료! (16자리 LotID=`{lf.get('lot_id', lf['fmid'])}`, 작물코드=`{lf.get('crop_code', '-')}` | 다음: QR 스캐너로 A01 창고 또는 A02 출하 스캔)")
                st.image(lf["bytes"], caption=f"농가 무색 원본 QR ({lf['filename']})", width=260)
                st.download_button(
                    label=f"📥 무색 QR 이미지 다운로드 ({lf['filename']})",
                    data=lf["bytes"],
                    file_name=lf["filename"],
                    mime="image/png",
                    use_container_width=True,
                )

        # [모듈 2] APC 선별 및 등급별 유색 QR 자동 생성 (B11)
        elif selected_ptab.startswith("🏭"):
            st.subheader("🏭 B11 APC 선별 및 유색 QR 변경 (무색 QR 스캔 / 16자리 LotID 입력 ➔ 난수 배분 ➔ 유색 QR 생성)")
            st.caption("DB에서 APC 입고(B10) 또는 선별 전 APC 창고(B12) 완료 로트를 확인한 뒤 난수로 A/B/C/결점 등급을 나누고 즉시 유색 QR 3종으로 변경·발급합니다.")

            apc_candidates = []
            try:
                conn_c = get_db_connection()
                sync_v1_delta_to_v2(conn_c, src_db=DB_V1_NAME, dst_db=DB_NAME)
                cur_c = conn_c.cursor()
                cur_c.execute(f"""
                    SELECT hl.lot_id AS LotID, hl.fruit_type AS FrT, hl.variety AS Vt,
                           hl.total_qty AS Qt, hl.current_stage, MAX(se.event_at) AS ready_at
                    FROM `{DB_NAME}`.`harvest_lots` hl
                    JOIN `{DB_NAME}`.`stage_events` se
                      ON hl.lot_id = se.lot_id AND se.pkg_id IS NULL AND se.stage_code IN ('B10', 'B12', 'A11')
                    WHERE hl.current_stage IN ('B10', 'B12', 'A11')
                    GROUP BY hl.lot_id, hl.fruit_type, hl.variety, hl.total_qty, hl.current_stage
                    ORDER BY ready_at DESC
                    LIMIT 25
                """)
                apc_candidates = list(cur_c.fetchall())
                conn_c.close()
            except Exception:
                pass

            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                raw_scan_in = st.text_input("👉 무색(농가) QR URL 스캔 또는 16자리 LotID 직접 입력", placeholder="예: 5563207411261122 또는 QR 스캔")
            with col_s2:
                cand_opts = ["(직접 입력 사용)"] + [f"{c['LotID']} | [{c['current_stage']}] {c.get('Vt') or c.get('FrT')} ({c.get('Qt')}박스)" for c in apc_candidates]
                sel_cand = st.selectbox("또는 B10(입고)/B12(창고) 대기 목록 선택", cand_opts)

            if st.button("⚡ B10/B12 조회 + 난수 등급 배분 + B11 유색 QR 3종 즉시 생성", use_container_width=True, type="primary"):
                target_lotid = ""
                if sel_cand != "(직접 입력 사용)":
                    target_lotid = sel_cand.split("|")[0].strip()
                else:
                    s_raw = raw_scan_in.strip()
                    if "?" in s_raw or s_raw.startswith("http"):
                        pq = parse_qs(urlparse(s_raw).query)
                        target_lotid = (pq.get("LotID") or pq.get("lot_id") or pq.get("FmID") or pq.get("fmid") or [""])[0]
                    else:
                        target_lotid = s_raw

                if not target_lotid:
                    st.error("❌ 조회할 16자리 LotID를 입력하거나 목록에서 선택해 주세요.")
                else:
                    try:
                        conn_a = get_db_connection()
                        sync_v1_delta_to_v2(conn_a, src_db=DB_V1_NAME, dst_db=DB_NAME)
                        cur_a = conn_a.cursor()
                        cur_a.execute("SET time_zone = '+09:00'")
                        cur_a.execute(f"""
                            SELECT hl.*, se.stage_code AS ready_stage, se.lat AS prev_lat, se.lng AS prev_lng
                            FROM `{DB_NAME}`.`harvest_lots` hl
                            JOIN `{DB_NAME}`.`stage_events` se
                              ON hl.lot_id = se.lot_id AND se.pkg_id IS NULL AND se.stage_code IN ('B10', 'B12', 'A11')
                            WHERE hl.lot_id = %s
                            ORDER BY FIELD(se.stage_code, 'B12', 'B10', 'A11'), se.event_at DESC
                            LIMIT 1
                        """, (target_lotid,))
                        lot_row = cur_a.fetchone()
                        if not lot_row:
                            conn_a.close()
                            st.session_state.pop("last_apc_qrs", None)
                            st.error(f"❌ DB에서 APC 입고(B10) 또는 선별 전 창고(B12) 이력을 찾을 수 없음! (LotID={target_lotid})")
                        else:
                            is_legacy_v2 = (lot_row.get("ready_stage") == "A11" and not is_v3_lot_id(target_lotid))
                            sort_stage = "A12" if is_legacy_v2 else "B11"

                            tot_qt = int(lot_row.get("total_qty") or 0)
                            if tot_qt > 0:
                                def_v = random.randint(1, min(3, tot_qt))
                                rem_d = tot_qt - def_v
                                a_v = int(tot_qt * random.uniform(0.78, 0.82))
                                if a_v > rem_d:
                                    a_v = rem_d
                                rem_bc = rem_d - a_v
                                if rem_bc > 0:
                                    b_v = random.randint(0, rem_bc)
                                    c_v = rem_bc - b_v
                                else:
                                    b_v, c_v = 0, 0
                                a_v = tot_qt - (b_v + c_v + def_v)
                            else:
                                a_v, b_v, c_v, def_v = 0, 0, 0, 0

                            cur_a.execute("SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') as srv_now")
                            srv_now = cur_a.fetchone()["srv_now"]

                            for p_id, g_cd, g_ko, g_cnt, ship, p_st in [
                                (f"{target_lotid}-A", "A", "상", a_v, 1, sort_stage),
                                (f"{target_lotid}-B", "B", "중", b_v, 1, sort_stage),
                                (f"{target_lotid}-C", "C", "하", c_v, 1, sort_stage),
                                (f"{target_lotid}-DEF", "DEFECT", "결점과", def_v, 0, "REJECTED"),
                            ]:
                                cur_a.execute(f"""
                                    INSERT INTO `{DB_NAME}`.`sorted_lots`
                                    (pkg_id, lot_id, grade_code, grade_label_ko, grade_qty, is_shippable, current_stage, sorted_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE grade_qty=VALUES(grade_qty), sorted_at=VALUES(sorted_at)
                                """, (p_id, target_lotid, g_cd, g_ko, g_cnt, ship, p_st, srv_now))

                            sort_hash = make_sha256({"lot_id": target_lotid, "stage": sort_stage, "A": a_v, "B": b_v, "C": c_v, "DEFECT": def_v, "rt": srv_now})
                            cur_a.execute(f"""
                                INSERT INTO `{DB_NAME}`.`stage_events` (lot_id, pkg_id, stage_code, event_at, lat, lng, tx_hash)
                                VALUES (%s, NULL, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE event_at=VALUES(event_at), tx_hash=VALUES(tx_hash)
                            """, (target_lotid, sort_stage, srv_now, lot_row.get("prev_lat"), lot_row.get("prev_lng"), sort_hash))

                            cur_a.execute(f"UPDATE `{DB_NAME}`.`harvest_lots` SET current_stage=%s WHERE lot_id=%s", (sort_stage, target_lotid))

                            cur_a.execute(f"""
                                SELECT * FROM `{DB_V1_NAME}`.`qr`
                                WHERE (LotID=%s OR (LotID IS NULL AND FmID=%s))
                                  AND Lo IN ('B12', 'B10', 'A11')
                                  AND (pkg_grade IS NULL OR pkg_grade = '')
                                ORDER BY id DESC LIMIT 1
                            """, (target_lotid, target_lotid))
                            v1_prev = cur_a.fetchone()
                            if v1_prev:
                                ins_dict = dict(v1_prev)
                                ins_dict.update({
                                    "Lo": sort_stage,
                                    "LotID": target_lotid if is_v3_lot_id(target_lotid) else ins_dict.get("LotID"),
                                    "AGrade": str(a_v),
                                    "BGrade": str(b_v),
                                    "CGrade": str(c_v),
                                    "DefectRate": str(def_v),
                                    "APC_RT": srv_now,
                                    "pkg_grade": None,
                                })
                                cur_a.execute(f"SHOW COLUMNS FROM `{DB_V1_NAME}`.`qr`")
                                db_cols = {c["Field"] for c in cur_a.fetchall()}
                                data_ins = {k: v for k, v in ins_dict.items() if k in db_cols and k != "id"}
                                cols_s = ", ".join(data_ins.keys())
                                ph_s = ", ".join([f"%({k})s" for k in data_ins.keys()])
                                cur_a.execute(f"INSERT INTO `{DB_V1_NAME}`.`qr` ({cols_s}) VALUES ({ph_s})", data_ins)
                                v1_ins_id = cur_a.lastrowid
                                if v1_ins_id:
                                    cur_a.execute(f"""
                                        INSERT INTO `{DB_NAME}`.`_sync_watermark` (source_table, last_id)
                                        VALUES ('qr', %s) ON DUPLICATE KEY UPDATE last_id=GREATEST(last_id, VALUES(last_id))
                                    """, (v1_ins_id,))

                            conn_a.commit()
                            conn_a.close()

                            frt_name = str(lot_row.get("fruit_type") or "Apples")
                            ac_val = str(lot_row.get("origin_zip") or "")
                            fm2_val = str(lot_row.get("farmer_code") or (target_lotid[5:7] if is_v3_lot_id(target_lotid) else target_lotid))
                            cc3_val = str(lot_row.get("crop_code") or get_crop_code(frt_name, lot_row.get("variety") or ""))
                            g_icons = GRADE_ICONS.get(frt_name, GRADE_ICONS["Apples"])
                            gen_list = []
                            for idx_g, (g_kr, g_en, g_cnt) in enumerate([("상", "A", a_v), ("중", "B", b_v), ("하", "C", c_v)]):
                                if is_legacy_v2:
                                    g_url = f"{STREAMLIT_BASE_URL}?FmID={target_lotid}&grade={g_kr}&pkg_grade={g_en}&AC={ac_val}&FrT={frt_name}"
                                else:
                                    g_url = f"{STREAMLIT_BASE_URL}?LotID={target_lotid}&FmID={fm2_val}&CC={cc3_val}&grade={g_kr}&pkg_grade={g_en}&AC={ac_val}&FrT={frt_name}"
                                g_fn = f"{target_lotid}_{g_en}_QR.png"
                                gen_list.append({
                                    "grade_en": g_en,
                                    "grade_kr": g_kr,
                                    "count": g_cnt,
                                    "filename": g_fn,
                                    "bytes": _make_portal_qr_bytes(g_url, g_icons[idx_g], rounded=False),
                                })
                            st.session_state["last_apc_qrs"] = {
                                "lot_id": target_lotid,
                                "stage": sort_stage,
                                "apc_rt": srv_now,
                                "row": lot_row,
                                "grades": (a_v, b_v, c_v, def_v, tot_qt),
                                "qrs": gen_list,
                            }
                    except Exception as ex_a:
                        st.error(f"❌ APC 선별 처리 오류: {ex_a}")

            if "last_apc_qrs" in st.session_state:
                la = st.session_state["last_apc_qrs"]
                a_v, b_v, c_v, def_v, tot_qt = la["grades"]
                st.success(f"✅ {la.get('stage', 'B11')} 선별 DB 저장 및 유색 QR 생성 완료! (LotID=`{la['lot_id']}` | 총 {tot_qt}박스 ➔ A:{a_v}, B:{b_v}, C:{c_v}, 결점:{def_v} | 시각: {la['apc_rt']})")
                q_cols = st.columns(3)
                for idx_c, q_item in enumerate(la["qrs"]):
                    with q_cols[idx_c]:
                        st.markdown(f"**{q_item['grade_en']}등급({q_item['grade_kr']}) QR — {q_item['count']}개**")
                        st.image(q_item["bytes"], use_container_width=True)
                        st.download_button(
                            label=f"📥 {q_item['filename']} 저장",
                            data=q_item["bytes"],
                            file_name=q_item["filename"],
                            mime="image/png",
                            key=f"dl_apc_{q_item['grade_en']}",
                            use_container_width=True,
                        )

        # [모듈 3] 소비자 안심 이력 바로 조회
        else:
            st.subheader("🔍 소비자 안심 이력 조회")
            q_lot = st.text_input("조회할 16자리 LotID 또는 기존 FmID", value="85")
            q_grade = st.selectbox("조회할 등급", ["상", "중", "하"])
            if st.button("🍏 해당 과일 안심 이력 열기", use_container_width=True, type="primary"):
                q_val = q_lot.strip()
                if is_v3_lot_id(q_val):
                    st.query_params["LotID"] = q_val
                else:
                    st.query_params["FmID"] = q_val
                st.query_params["grade"] = q_grade
                st.rerun()

    st.stop()

def parse_kst_dt(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val.replace(tzinfo=None)
    s = str(val).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:len(fmt) + 2].strip(), fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s[:19])
    except Exception:
        return None

def fetch_shipment_telemetry(cursor, shipment_row):
    """정규화 `shipments` 레코드(run_id + departed_at ~ arrived_at)로 `sensor_telemetry` 정밀 JOIN 조회"""
    if not shipment_row:
        return []
    dep_dt = shipment_row.get("departed_at")
    arr_dt = shipment_row.get("arrived_at")
    run_id = shipment_row.get("run_id")
    dev_id = shipment_row.get("device_id")
    if not dep_dt:
        return []

    s_str = dep_dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dep_dt, "strftime") else str(dep_dt)[:19]
    e_dt = arr_dt if arr_dt else (parse_kst_dt(dep_dt) + timedelta(hours=12))
    e_str = e_dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(e_dt, "strftime") else str(e_dt)[:19]

    if run_id:
        cursor.execute(f"""
            SELECT DATE_FORMAT(measured_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS timestamp_str,
                   lat, lng, temperature, humidity, g_force, speed, device_id AS device, run_id
            FROM `{DB_NAME}`.`sensor_telemetry`
            WHERE run_id = %s
              AND gps_state != 'INDOOR' AND lat != 0 AND lng != 0
              AND measured_at >= %s AND measured_at <= %s
            ORDER BY measured_at ASC, telemetry_id ASC
        """, (run_id, s_str, e_str))
        pts = list(cursor.fetchall())
        if pts:
            return pts

    # 실시간 배송 중(IN_TRANSIT)이어서 아직 run_id가 미확정일 때: 담당 차량 또는 활성 FIELD_DRIVE 세션 조회
    if dev_id:
        cursor.execute(f"""
            SELECT DATE_FORMAT(measured_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS timestamp_str,
                   lat, lng, temperature, humidity, g_force, speed, device_id AS device, run_id
            FROM `{DB_NAME}`.`sensor_telemetry`
            WHERE device_id = %s
              AND gps_state != 'INDOOR' AND lat != 0 AND lng != 0
              AND measured_at >= %s AND measured_at <= %s
            ORDER BY measured_at ASC, telemetry_id ASC
        """, (dev_id, s_str, e_str))
        pts = list(cursor.fetchall())
        if pts:
            return pts

    cursor.execute(f"""
        SELECT DATE_FORMAT(st.measured_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS timestamp_str,
               st.lat, st.lng, st.temperature, st.humidity, st.g_force, st.speed,
               st.device_id AS device, st.run_id
        FROM `{DB_NAME}`.`sensor_telemetry` st
        JOIN `{DB_NAME}`.`transport_runs` tr ON st.run_id = tr.run_id
        WHERE tr.run_type = 'FIELD_DRIVE'
          AND st.gps_state != 'INDOOR' AND st.lat != 0 AND st.lng != 0
          AND st.measured_at >= %s AND st.measured_at <= %s
        ORDER BY st.measured_at ASC, st.telemetry_id ASC
    """, (s_str, e_str))
    return list(cursor.fetchall())

# 2. 데이터 조회 (lab225_v2 정규화 7개 테이블 JOIN 구조, v3 + v2 하위 호환)
leg1_sensor_pts = []
leg2_sensor_pts = []
leg3_sensor_pts = []
records = []
lot_master = None
sorted_map = {}
proto_ver = "v3"
resolved_lot_id = str(fm_id).strip()
resolved_farmer_code = resolved_lot_id
resolved_crop_code = ""

try:
    conn = get_db_connection()
    # 방금 물리 스캐너로 찍은 내역이 있으면 즉시 증분 반영
    sync_v1_delta_to_v2(conn, src_db=DB_V1_NAME, dst_db=DB_NAME)
    cursor = conn.cursor()

    # (1) 농가 원물 마스터 조회 (16자리 LotID 우선, 없으면 farmer_code 최신 폴백)
    cursor.execute(f"SELECT * FROM `{DB_NAME}`.`harvest_lots` WHERE lot_id = %s LIMIT 1", (resolved_lot_id,))
    lot_master = cursor.fetchone()
    if not lot_master:
        cursor.execute(f"SELECT * FROM `{DB_NAME}`.`harvest_lots` WHERE farmer_code = %s ORDER BY created_at DESC LIMIT 1", (resolved_lot_id,))
        lot_master = cursor.fetchone()

    if lot_master:
        resolved_lot_id = lot_master["lot_id"]
        resolved_farmer_code = lot_master.get("farmer_code") or (resolved_lot_id[5:7] if is_v3_lot_id(resolved_lot_id) else resolved_lot_id)
        resolved_crop_code = lot_master.get("crop_code") or (resolved_lot_id[7:10] if is_v3_lot_id(resolved_lot_id) else get_crop_code(lot_master.get("fruit_type"), lot_master.get("variety")))

        # (2) APC 선별 결과(A / B / C / DEFECT) JOIN 조회
        cursor.execute(f"SELECT * FROM `{DB_NAME}`.`sorted_lots` WHERE lot_id = %s", (resolved_lot_id,))
        for sl in cursor.fetchall():
            sorted_map[sl["grade_code"]] = sl

        norm_g = normalize_grade(url_grade)
        target_g_code = "B" if norm_g == "중" else ("C" if norm_g == "하" else "A")
        effective_pkg_id = f"{resolved_lot_id}-{target_g_code}"

        # (3) 통합 공정 타임라인 조회
        cursor.execute(f"""
            SELECT stage_code, pkg_id, event_at, lat, lng, temp, humi, tx_hash
            FROM `{DB_NAME}`.`stage_events`
            WHERE lot_id = %s AND (pkg_id IS NULL OR pkg_id = %s)
            ORDER BY event_at ASC, event_id ASC
        """, (resolved_lot_id, effective_pkg_id))
        ev_rows = cursor.fetchall()
        proto_ver = detect_protocol_version(
            resolved_lot_id,
            [e["stage_code"] for e in ev_rows],
            explicit_ver=lot_master.get("protocol_ver"),
        )

        a_qty = sorted_map.get("A", {}).get("grade_qty")
        b_qty = sorted_map.get("B", {}).get("grade_qty")
        c_qty = sorted_map.get("C", {}).get("grade_qty")
        def_qty = sorted_map.get("DEFECT", {}).get("grade_qty")

        # (4) 1구간, 2구간, 3구간 운송 궤적 정밀 JOIN 조회
        cursor.execute(f"SELECT * FROM `{DB_NAME}`.`shipments` WHERE lot_id = %s AND leg_no = 1 LIMIT 1", (resolved_lot_id,))
        sh_leg1 = cursor.fetchone()
        if sh_leg1 and (sh_leg1.get("status") == "ARRIVED" or sh_leg1.get("run_id") or proto_ver == "v3"):
            leg1_sensor_pts = fetch_shipment_telemetry(cursor, sh_leg1)

        cursor.execute(f"SELECT * FROM `{DB_NAME}`.`shipments` WHERE lot_id = %s AND leg_no = 2 AND pkg_id = %s LIMIT 1", (resolved_lot_id, effective_pkg_id))
        sh_leg2 = cursor.fetchone()
        if sh_leg2:
            leg2_sensor_pts = fetch_shipment_telemetry(cursor, sh_leg2)

        cursor.execute(f"SELECT * FROM `{DB_NAME}`.`shipments` WHERE lot_id = %s AND leg_no = 3 AND pkg_id = %s LIMIT 1", (resolved_lot_id, effective_pkg_id))
        sh_leg3 = cursor.fetchone()
        if sh_leg3:
            leg3_sensor_pts = fetch_shipment_telemetry(cursor, sh_leg3)

        for ev in ev_rows:
            raw_cd = ev["stage_code"]
            if proto_ver == "v3" and raw_cd == "B12":
                st_cd = "B12_PRE" if not ev.get("pkg_id") else "B12_POST"
            else:
                st_cd = raw_cd

            raw_ev_str = ev["event_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(ev["event_at"], "strftime") else str(ev["event_at"])
            if proto_ver == "v2" and st_cd in ("A00", "A01"):
                ev_time_str = raw_ev_str[:10]
            elif proto_ver == "v2" and st_cd == "A02":
                if leg1_sensor_pts and leg1_sensor_pts[0].get("timestamp_str"):
                    ev_time_str = leg1_sensor_pts[0]["timestamp_str"]
                elif sh_leg1 and sh_leg1.get("run_id") and sh_leg1.get("departed_at"):
                    dep_v = sh_leg1["departed_at"]
                    ev_time_str = dep_v.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dep_v, "strftime") else str(dep_v)
                elif raw_ev_str.endswith("00:00:00"):
                    ev_time_str = raw_ev_str[:10]
                else:
                    ev_time_str = raw_ev_str
            else:
                ev_time_str = raw_ev_str[:10] if (st_cd == "A00" and raw_ev_str.endswith("00:00:00")) else raw_ev_str

            rec_item = {
                "Lo": st_cd,
                "LotID": resolved_lot_id,
                "FmID": resolved_farmer_code,
                "CropCode": resolved_crop_code,
                "AC": lot_master["origin_zip"],
                "FrT": lot_master["fruit_type"],
                "Vt": lot_master["variety"],
                "Ct": lot_master["farmer_phone"],
                "Mt": lot_master["cultivation"],
                "HN": lot_master["harvest_no"],
                "Qt": lot_master["total_qty"],
                "HD": str(lot_master["harvest_date"] or ev_time_str[:10]),
                "StD": str(lot_master["storage_date"] or ""),
                "DD": str(lot_master["deliver_date"] or ""),
                "event_at": ev_time_str,
                "Lat": ev["lat"],
                "lon": ev["lng"],
                "Tp": ev["temp"],
                "Hm": ev["humi"],
                "tx_hash": ev["tx_hash"],
                "AGrade": a_qty,
                "BGrade": b_qty,
                "CGrade": c_qty,
                "DefectRate": def_qty,
            }
            records.append(rec_item)

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
        
    if proto_ver == "v3":
        pkg_g_code = "B" if norm_grade == "중" else ("C" if norm_grade == "하" else "A")
        qr_url = f"https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/?LotID={resolved_lot_id}&FmID={resolved_farmer_code}&CC={resolved_crop_code}&grade={display_grade}&pkg_grade={pkg_g_code}&AC={latest.get('AC', '')}&FrT={latest.get('FrT', '')}"
    else:
        qr_url = f"https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/?FmID={resolved_lot_id}&grade={display_grade}&AC={latest.get('AC', '')}&FrT={latest.get('FrT', '')}"
    
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

    # 해당 등급의 구체적인 수량 추출 (v3: B11 또는 레거시 v2: A12 선별 단계 참조)
    a12_record = next((r for r in records if r.get("Lo") in ("B11", "A12")), None)
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
    farmer_id_display = resolved_lot_id if proto_ver == "v3" else latest.get("FmID", "미등록")
    if farmer_id_display == "미등록" or farmer_id_display == "Unregistered" or not farmer_id_display:
        farmer_id_display = LANG_DICT[st.session_state.lang]['no_qty']
    farmer_id_lbl = ("16자리 고유코드 (LotID)" if st.session_state.lang == "KO" else "16-Digit Lot ID") if proto_ver == "v3" else LANG_DICT[st.session_state.lang]['farmer_id']
    farmer_contact = mask_contact(latest.get("Ct", ""), st.session_state.lang)
    
    st.markdown(f"""
    <div class="farmer-card">
        <div class="farmer-info-item">
            <div style="font-size: 1.8rem;">🆔</div>
            <div>
                <div class="farmer-label">{farmer_id_lbl}</div>
                <div class="farmer-value" style="font-size:0.95rem; word-break:break-all;">{farmer_id_display}</div>
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
    
    # 단계 설정 (v3: A00~D10 분기 공정, v2 레거시: A00~A16 호환)
    stage_names = {
        "A00": (LANG_DICT[st.session_state.lang]["stage_A00_title"], LANG_DICT[st.session_state.lang]["stage_A00_desc"], "event_at"),
        "A01": (LANG_DICT[st.session_state.lang]["stage_A01_title"], LANG_DICT[st.session_state.lang]["stage_A01_desc"], "event_at"),
        "A02": (LANG_DICT[st.session_state.lang]["stage_A02_title"], LANG_DICT[st.session_state.lang]["stage_A02_desc"], "event_at"),
        "B10": (LANG_DICT[st.session_state.lang]["stage_B10_title"], LANG_DICT[st.session_state.lang]["stage_B10_desc"], "event_at"),
        "B12_PRE": (LANG_DICT[st.session_state.lang]["stage_B12_PRE_title"], LANG_DICT[st.session_state.lang]["stage_B12_PRE_desc"], "event_at"),
        "B11": (LANG_DICT[st.session_state.lang]["stage_B11_title"], LANG_DICT[st.session_state.lang]["stage_B11_desc"], "event_at"),
        "B12_POST": (LANG_DICT[st.session_state.lang]["stage_B12_POST_title"], LANG_DICT[st.session_state.lang]["stage_B12_POST_desc"], "event_at"),
        "B13": (LANG_DICT[st.session_state.lang]["stage_B13_title"], LANG_DICT[st.session_state.lang]["stage_B13_desc"], "event_at"),
        "C10": (LANG_DICT[st.session_state.lang]["stage_C10_title"], LANG_DICT[st.session_state.lang]["stage_C10_desc"], "event_at"),
        "C11": (LANG_DICT[st.session_state.lang]["stage_C11_title"], LANG_DICT[st.session_state.lang]["stage_C11_desc"], "event_at"),
        "D10": (LANG_DICT[st.session_state.lang]["stage_D10_title"], LANG_DICT[st.session_state.lang]["stage_D10_desc"], "event_at"),
        "A10": (LANG_DICT[st.session_state.lang]["stage_A10_title"], LANG_DICT[st.session_state.lang]["stage_A10_desc"], "event_at"),
        "A11": (LANG_DICT[st.session_state.lang]["stage_A11_title"], LANG_DICT[st.session_state.lang]["stage_A11_desc"], "event_at"),
        "A12": (LANG_DICT[st.session_state.lang]["stage_A12_title"], LANG_DICT[st.session_state.lang]["stage_A12_desc"], "event_at"),
        "A13": (LANG_DICT[st.session_state.lang]["stage_A13_title"], LANG_DICT[st.session_state.lang]["stage_A13_desc"], "event_at"),
        "A14": (LANG_DICT[st.session_state.lang]["stage_A14_title"], LANG_DICT[st.session_state.lang]["stage_A14_desc"], "event_at"),
        "A15": (LANG_DICT[st.session_state.lang]["stage_A15_title"], LANG_DICT[st.session_state.lang]["stage_A15_desc"], "event_at"),
        "A16": (LANG_DICT[st.session_state.lang]["stage_A16_title"], LANG_DICT[st.session_state.lang]["stage_A16_desc"], "event_at")
    }

    completed_stages = {r.get("Lo"): r for r in records}
    timeline_order = (
        ["A00", "A01", "A02", "B10", "B12_PRE", "B11", "B12_POST", "B13", "C10", "C11", "D10"]
        if proto_ver == "v3"
        else ["A00", "A01", "A02", "A10", "A11", "A12", "A13", "A14", "A15", "A16"]
    )
    optional_v3 = {"A01", "B12_PRE", "B12_POST"}
    storage_stages = {"A01", "B12_PRE", "B12_POST", "C10", "A14"}
    max_done_idx = max([i for i, c in enumerate(timeline_order) if c in completed_stages], default=-1)

    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    for idx_t, code in enumerate(timeline_order):
        if proto_ver == "v3" and code in optional_v3 and code not in completed_stages:
            if idx_t < max_done_idx:
                continue
            if code == "B12_PRE" or (code == "B12_POST" and "B11" not in completed_stages):
                continue
        title, default_desc, time_col = stage_names[code]
        if code in completed_stages:
            row = completed_stages[code]
            stage_time = row.get(time_col)
            elapsed = format_elapsed_time(stage_time, st.session_state.lang)
            
            tx_badge = (
                f' &nbsp;|&nbsp; <span style="color:#27ae60; font-weight:600;">🔗 Hash: {str(row.get("tx_hash"))[:12]}...</span>'
                if row.get("tx_hash")
                else ""
            )
            st.markdown(f"""
            <div class="timeline-item active-stage">
                <span style="font-weight:700; font-size:1.1rem; color:#1d1d1f;">{title}</span>
                <span class="elapsed-tag">{elapsed}</span>
                <p style="color:#515154; margin-top:5px; font-size:0.9rem; font-weight:400; margin-bottom:5px;">{default_desc}</p>
                <small style="color:#86868b; font-size:0.8rem;">⏰ {LANG_DICT[st.session_state.lang]['proc_time']}: {stage_time if stage_time else ""}{tx_badge}</small>
            </div>
            """, unsafe_allow_html=True)

            # 창고 단계(A01, B12, C10, A14)일 때 실시간 온습도 센서 카드 표시
            if code in storage_stages and row.get("Tp") is not None:
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
    L = LANG_DICT[st.session_state.lang]
    st.markdown(f"<h3 style='font-size:1.3rem; font-weight:700; margin-bottom:8px;'>{L['route_title']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#515154; font-size:0.9rem; margin-bottom:14px;'>{L['route_subtitle']}</p>", unsafe_allow_html=True)

    def _valid_coord(lat_v, lon_v):
        try:
            la, lo = float(lat_v), float(lon_v)
            if la != 0.0 and lo != 0.0 and abs(la) > 1.0 and abs(lo) > 1.0:
                return (la, lo)
        except Exception:
            pass
        return None

    # 1) 원산지(A00) 좌표 (실측 1구간 주행 GPS가 있으면 실제 출발 좌표를 최우선 사용하고, 없을 때만 우편번호 대표 좌표 폴백)
    ac_code = str(latest.get("AC", ""))
    origin_coords = {
        "55630": (35.6470, 127.5210),
        "55631": (35.6170, 127.4220),
        "55632": (35.5390, 127.5530),
        "55633": (35.7270, 127.5850),
        "55634": (35.7070, 127.4810),
        "55635": (35.6960, 127.5750),
        "55517": (36.0068, 127.6608),
        "55518": (36.0068, 127.6608),
        "55549": (36.0170, 127.7830),
        "55527": (35.9510, 127.6480),
        "55540": (35.8750, 127.6560),
        "55559": (35.9560, 127.8480),
        "55434": (35.7906, 127.4229),
        "55435": (35.7906, 127.4229),
        "55451": (35.7470, 127.3670),
        "55455": (35.6980, 127.4190),
        "55459": (35.6940, 127.3390),
        "55416": (35.8140, 127.3450),
    }
    if leg1_sensor_pts:
        origin_pt = (float(leg1_sensor_pts[0]["lat"]), float(leg1_sensor_pts[0]["lng"]))
    else:
        origin_pt = origin_coords.get(ac_code)

    # 2) 단계별 체크포인트 테이블 데이터 구성 & APC 거점 / 도착점 좌표 추출
    map_data = []
    if origin_pt:
        map_data.append({
            "단계": L['stage_A00_title'],
            "latitude": origin_pt[0],
            "longitude": origin_pt[1],
            "시간": str(latest.get("HD", "") or "")
        })

    apc_pts = []
    dist_pts = []
    retail_pt = None
    retail_time = ""
    last_apc_time = ""
    dist_time = ""

    for r in records:
        stage_code = r.get("Lo")
        if stage_code == "A00":
            continue
        c_pt = _valid_coord(r.get("Lat"), r.get("lon"))
        stage_name = stage_names.get(stage_code, (stage_code, "", ""))[0]
        time_col = stage_names.get(stage_code, ("", "", ""))[2]
        stage_time = str(r.get(time_col, "") or "")

        if stage_code in ("A01", "A02"):
            if c_pt and not origin_pt:
                origin_pt = c_pt
        elif stage_code in ("B10", "B11", "B12_PRE", "B12_POST", "B13", "A10", "A11", "A12", "A13", "A14", "A15"):
            if stage_time:
                last_apc_time = stage_time
            if c_pt:
                apc_pts.append(c_pt)
        elif stage_code in ("C10", "C11"):
            if stage_time:
                dist_time = stage_time
            if c_pt:
                dist_pts.append(c_pt)
        elif stage_code in ("D10", "A16"):
            retail_time = stage_time
            if c_pt:
                retail_pt = c_pt

        if c_pt:
            map_data.append({
                "단계": stage_name,
                "latitude": c_pt[0],
                "longitude": c_pt[1],
                "시간": stage_time
            })

    apc_hub_pt = apc_pts[-1] if apc_pts else None
    if not apc_hub_pt:
        if leg1_sensor_pts:
            apc_hub_pt = (float(leg1_sensor_pts[-1]["lat"]), float(leg1_sensor_pts[-1]["lng"]))
        elif leg2_sensor_pts:
            apc_hub_pt = (float(leg2_sensor_pts[0]["lat"]), float(leg2_sensor_pts[0]["lng"]))

    dist_hub_pt = dist_pts[-1] if dist_pts else None
    if proto_ver == "v3" and not dist_hub_pt:
        if leg2_sensor_pts:
            dist_hub_pt = (float(leg2_sensor_pts[-1]["lat"]), float(leg2_sensor_pts[-1]["lng"]))
        elif leg3_sensor_pts:
            dist_hub_pt = (float(leg3_sensor_pts[0]["lat"]), float(leg3_sensor_pts[0]["lng"]))

    if not retail_pt:
        if "D10" in completed_stages and leg3_sensor_pts:
            retail_pt = (float(leg3_sensor_pts[-1]["lat"]), float(leg3_sensor_pts[-1]["lng"]))
        elif "A16" in completed_stages and leg2_sensor_pts:
            retail_pt = (float(leg2_sensor_pts[-1]["lat"]), float(leg2_sensor_pts[-1]["lng"]))

    # 3) PyDeck 연속 주행 경로(1/2/3구간 PathLayer) 및 거점 마커 구성
    leg1_path = [[float(p["lng"]), float(p["lat"])] for p in leg1_sensor_pts]
    if len(leg1_path) < 2 and origin_pt and apc_hub_pt:
        leg1_path = [[origin_pt[1], origin_pt[0]], [apc_hub_pt[1], apc_hub_pt[0]]]
    elif len(leg1_path) >= 2:
        if origin_pt:
            leg1_path = [[origin_pt[1], origin_pt[0]]] + leg1_path
        if apc_hub_pt:
            leg1_path = leg1_path + [[apc_hub_pt[1], apc_hub_pt[0]]]

    leg2_end_pt = (dist_hub_pt or retail_pt) if proto_ver == "v3" else retail_pt
    leg2_path = [[float(p["lng"]), float(p["lat"])] for p in leg2_sensor_pts]
    if len(leg2_path) < 2 and apc_hub_pt and leg2_end_pt:
        leg2_path = [[apc_hub_pt[1], apc_hub_pt[0]], [leg2_end_pt[1], leg2_end_pt[0]]]
    elif len(leg2_path) >= 2:
        if apc_hub_pt:
            leg2_path = [[apc_hub_pt[1], apc_hub_pt[0]]] + leg2_path
        if leg2_end_pt:
            leg2_path = leg2_path + [[leg2_end_pt[1], leg2_end_pt[0]]]

    leg3_path = []
    if proto_ver == "v3":
        leg3_start_pt = dist_hub_pt or apc_hub_pt
        leg3_path = [[float(p["lng"]), float(p["lat"])] for p in leg3_sensor_pts]
        if len(leg3_path) < 2 and leg3_start_pt and retail_pt:
            leg3_path = [[leg3_start_pt[1], leg3_start_pt[0]], [retail_pt[1], retail_pt[0]]]
        elif len(leg3_path) >= 2:
            if leg3_start_pt:
                leg3_path = [[leg3_start_pt[1], leg3_start_pt[0]]] + leg3_path
            if retail_pt:
                leg3_path = leg3_path + [[retail_pt[1], retail_pt[0]]]

    hub_markers = []
    if origin_pt:
        hub_markers.append({
            "name": L['stage_A00_title'],
            "time": str(latest.get("HD", "") or "-"),
            "lat": origin_pt[0],
            "lng": origin_pt[1],
            "icon": "🌱",
            "fill": [46, 204, 113, 230],
        })
    if apc_hub_pt:
        hub_markers.append({
            "name": L['route_apc_hub'] if proto_ver == "v3" else L['route_apc_hub_legacy'],
            "time": last_apc_time or "-",
            "lat": apc_hub_pt[0],
            "lng": apc_hub_pt[1],
            "icon": "🏢",
            "fill": [243, 156, 18, 235],
        })
    if proto_ver == "v3" and dist_hub_pt:
        hub_markers.append({
            "name": L['route_dist_hub'],
            "time": dist_time or "-",
            "lat": dist_hub_pt[0],
            "lng": dist_hub_pt[1],
            "icon": "🏬",
            "fill": [0, 122, 255, 235],
        })
    if retail_pt:
        hub_markers.append({
            "name": L['stage_D10_title'] if proto_ver == "v3" else L['stage_A16_title'],
            "time": retail_time or "-",
            "lat": retail_pt[0],
            "lng": retail_pt[1],
            "icon": "🏪",
            "fill": [124, 58, 237, 235] if proto_ver == "v3" else [0, 122, 255, 235],
        })
    elif leg3_sensor_pts or leg2_sensor_pts:
        last_live = leg3_sensor_pts[-1] if leg3_sensor_pts else leg2_sensor_pts[-1]
        hub_markers.append({
            "name": L['route_in_transit'],
            "time": str(last_live.get("timestamp_str", "-")),
            "lat": float(last_live["lat"]),
            "lng": float(last_live["lng"]),
            "icon": "🚚",
            "fill": [0, 122, 255, 235],
        })

    all_coords = (
        [(pt[1], pt[0]) for pt in leg1_path]
        + [(pt[1], pt[0]) for pt in leg2_path]
        + [(pt[1], pt[0]) for pt in leg3_path]
        + [(m["lat"], m["lng"]) for m in hub_markers]
    )

    # 운송 구간 실시간 콜드체인 센서 요약 카드 표출
    all_sensor_pts = list(leg1_sensor_pts) + list(leg2_sensor_pts) + list(leg3_sensor_pts)
    if all_sensor_pts:
        temps = [float(p["temperature"]) for p in all_sensor_pts if p.get("temperature") is not None]
        gforces = [float(p["g_force"]) for p in all_sensor_pts if p.get("g_force") is not None]
        avg_t_str = f"{(sum(temps) / len(temps)):.1f}°C" if temps else "-"
        max_g_str = f"{max(gforces):.2f}G" if gforces else "-"
        st.markdown(f"""
        <div style="background-color:#f4f9ff; border:1px solid #cfe4ff; border-radius:12px; padding:12px 16px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:8px;">
                <span style="font-weight:700; color:#0b5394; font-size:0.95rem;">{L['route_telemetry_title']}</span>
                <span style="font-size:0.8rem; font-weight:600; color:#27ae60;">{L['route_safe_badge']}</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:8px; text-align:center;">
                <div style="background:#ffffff; border-radius:8px; padding:6px 8px; border:1px solid #e1ecf7;">
                    <small style="color:#666; font-size:0.72rem; display:block;">{L['route_avg_temp']}</small>
                    <b style="color:#0b5394; font-size:0.98rem;">{avg_t_str}</b>
                </div>
                <div style="background:#ffffff; border-radius:8px; padding:6px 8px; border:1px solid #e1ecf7;">
                    <small style="color:#666; font-size:0.72rem; display:block;">{L['route_max_g']}</small>
                    <b style="color:#27ae60; font-size:0.98rem;">{max_g_str}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if all_coords:
        leg2_lbl = L['route_leg2'] if proto_ver == "v3" else L['route_leg2_legacy']
        leg3_badge_html = (
            f"""<span style="display:inline-flex; align-items:center; gap:6px;">
                <span style="width:18px; height:4px; background:#7c3aed; border-radius:2px; display:inline-block;"></span>
                {L['route_leg3']}
            </span>"""
            if proto_ver == "v3"
            else ""
        )
        st.markdown(f"""
        <div style="display:flex; flex-wrap:wrap; gap:12px; margin-bottom:10px; font-size:0.82rem; color:#515154;">
            <span style="display:inline-flex; align-items:center; gap:6px;">
                <span style="width:18px; height:4px; background:#2ecc71; border-radius:2px; display:inline-block;"></span>
                {L['route_leg1']}
            </span>
            <span style="display:inline-flex; align-items:center; gap:6px;">
                <span style="width:18px; height:4px; background:#007aff; border-radius:2px; display:inline-block;"></span>
                {leg2_lbl}
            </span>
            {leg3_badge_html}
        </div>
        """, unsafe_allow_html=True)

        lats = [c[0] for c in all_coords]
        lons = [c[1] for c in all_coords]
        center_lat = (min(lats) + max(lats)) / 2.0
        center_lon = (min(lons) + max(lons)) / 2.0
        span = max(max(lats) - min(lats), max(lons) - min(lons))
        if span < 0.003:
            auto_zoom = 14.2
        else:
            auto_zoom = max(6.8, min(14.2, math.log2(360.0 / (span * 2.3)) - 0.4))

        deck_layers = []
        if len(leg1_path) >= 2:
            deck_layers.append(pdk.Layer(
                "PathLayer",
                data=[{"path": leg1_path, "name": L['route_leg1'], "time": "-"}],
                get_path="path",
                get_color=[46, 204, 113, 215],
                width_min_pixels=4,
                cap_rounded=True,
                joint_rounded=True,
                pickable=True,
            ))
        if len(leg2_path) >= 2:
            deck_layers.append(pdk.Layer(
                "PathLayer",
                data=[{"path": leg2_path, "name": leg2_lbl, "time": dist_time or retail_time or last_apc_time or "-"}],
                get_path="path",
                get_color=[0, 122, 255, 235],
                width_min_pixels=5,
                cap_rounded=True,
                joint_rounded=True,
                pickable=True,
            ))
        if len(leg3_path) >= 2:
            deck_layers.append(pdk.Layer(
                "PathLayer",
                data=[{"path": leg3_path, "name": L['route_leg3'], "time": retail_time or dist_time or "-"}],
                get_path="path",
                get_color=[124, 58, 237, 235],
                width_min_pixels=5,
                cap_rounded=True,
                joint_rounded=True,
                pickable=True,
            ))
        if hub_markers:
            df_hubs = pd.DataFrame(hub_markers)
            deck_layers.append(pdk.Layer(
                "ScatterplotLayer",
                data=df_hubs,
                get_position="[lng, lat]",
                get_fill_color="fill",
                get_line_color=[255, 255, 255, 255],
                line_width_min_pixels=2,
                stroked=True,
                radius_min_pixels=9,
                radius_max_pixels=16,
                pickable=True,
            ))
            deck_layers.append(pdk.Layer(
                "TextLayer",
                data=df_hubs,
                get_position="[lng, lat]",
                get_text="icon",
                get_size=22,
                get_pixel_offset=[0, -20],
                get_alignment_baseline="'center'",
            ))

        st.pydeck_chart(pdk.Deck(
            layers=deck_layers,
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=auto_zoom,
                pitch=0,
            ),
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            tooltip={"text": "{name}\n⏰ {time}"},
            height=380,
        ))

        if map_data:
            df_map = pd.DataFrame(map_data)
            with st.expander(L['route_list'], expanded=False):
                display_df = df_map[["단계", "시간", "latitude", "longitude"]].copy()
                display_df.columns = [L['col_stage'], L['col_time'], L['col_lat'], L['col_lon']]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning(L['no_gps'])
