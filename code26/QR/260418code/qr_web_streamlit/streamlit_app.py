import streamlit as st
import pandas as pd
import pymysql
import hashlib
import json
import os
from pathlib import Path

# --- Configuration ---
FRUIT_TYPES = ['사과', '배', '복숭아', '귤', '참외']
FRUIT_ICONS = {
    '사과': '🍎',
    '배': '🍐',
    '복숭아': '🍑',
    '귤': '🍊',
    '참외': '🍈'
}
FRUIT_IMAGES = {
    '사과': 'static/Apples.png',
    'Apples': 'static/Apples.png',
    '배': 'static/Pears.png',
    'Pears': 'static/Pears.png',
    '복숭아': 'static/Peaches.png',
    'Peaches': 'static/Peaches.png',
    '귤': 'static/Tangerines.png',
    'Tangerines': 'static/Tangerines.png',
    '참외': 'static/Melons.png',
    'Melons': 'static/Melons.png'
}
FRUIT_ENCYCLOPEDIA = {
    '사과': 'https://www.nongnet.or.kr/front/M000000224/picture/view.do?pictureSn=49&codeBuNo=&codeNo=&pageIndex=1',
    '배': 'https://www.nongnet.or.kr/front/M000000224/picture/view.do?pictureSn=48&codeBuNo=&codeNo=&pageIndex=1',
    '복숭아': 'https://www.nongnet.or.kr/front/M000000224/picture/view.do?pictureSn=47&codeBuNo=&codeNo=&pageIndex=1',
    '귤': 'https://www.nongnet.or.kr/front/M000000224/picture/view.do?pictureSn=45&codeBuNo=&codeNo=&pageIndex=1',
    '참외': 'https://www.nongnet.or.kr/front/M000000224/picture/view.do?pictureSn=28&codeBuNo=&codeNo=&pageIndex=2'
}
BLOCKCHAIN_FILE = "blockchain_ledger.json"

# --- DB Connection ---
def get_connection():
    cfg = st.secrets["MySQL"]
    return pymysql.connect(
        host=cfg["MYSQL_HOST"],
        user=cfg["MYSQL_USER"],
        password=cfg["MYSQL_PASSWORD"],
        database=cfg["MYSQL_DATABASE"],
        port=cfg["MYSQL_PORT"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

def calculate_hash(data_dict):
    data_str = json.dumps(data_dict, sort_keys=True, default=str).encode()
    return hashlib.sha256(data_str).hexdigest()

# --- App UI Setup ---
st.set_page_config(page_title="Fresh Fruit Traceability", layout="wide", page_icon="🍎")

# Custom CSS for card-like styling
st.markdown("""
    <style>
    .card {
        border-radius: 10px;
        padding: 20px;
        background-color: #ffffff;
        color: #000000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #dee2e6;
        border-left: 5px solid #007bff;
    }
    .card h3 {
        font-size: 1.25rem;
        color: #000000;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Flask 스타일로 변경) ---
with st.sidebar:
    st.header("🍎 과일 도감")
    
    # 세션 초기화
    if "selected_fruit" not in st.session_state:
        st.session_state.selected_fruit = "전체 보기"
    if "menu_choice" not in st.session_state:
        st.session_state.menu_choice = "📊 대시보드"

    # 과일 필터링 메뉴 (버튼 형식)
    st.subheader("카테고리")
    if st.button("전체 보기", use_container_width=True):
        st.session_state.selected_fruit = "전체 보기"
        st.session_state.menu_choice = "📊 대시보드"
        st.rerun()

    for fruit in FRUIT_TYPES:
        if st.button(f"{FRUIT_ICONS[fruit]} {fruit}", use_container_width=True):
            st.session_state.selected_fruit = fruit
            st.session_state.menu_choice = "📊 대시보드"
            st.rerun()
            
    st.divider()
    
    # 기타 메뉴
    if st.button("🔍 상세 이력 추적", use_container_width=True):
        st.session_state.menu_choice = "🔍 상세 이력 추적"
        st.rerun()
    if st.button("🏠 소비자 페이지", use_container_width=True):
        st.session_state.menu_choice = "🏠 소비자 페이지"
        st.rerun()
        
    st.divider()
    
    # 백과사전 링크
    st.subheader("📖 과일 백과사전")
    for fruit in FRUIT_TYPES:
        st.markdown(f"[{FRUIT_ICONS[fruit]} {fruit} 도감]({FRUIT_ENCYCLOPEDIA[fruit]})")

# 현재 메뉴 상태 동기화
menu = st.session_state.menu_choice

# --- Page Logic ---

if menu == "📊 대시보드":
    st.title("🍎 스마트팜 QR 스캔 데이터")
    
    # 대시보드 상단
    col_search, _ = st.columns([2, 1])
    with col_search:
        search_fmid = st.text_input("FmID 검색", placeholder="검색할 FmID를 입력하세요...")

    selected_fruit = st.session_state.selected_fruit

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM qr WHERE 1=1"
            params = []
            
            # DB의 FrT 값이 영어(Apples, Pears 등)로 되어 있는 경우를 위한 매핑
            fruit_db_mapping = {
                '사과': 'Apples',
                '배': 'Pears',
                '복숭아': 'Peaches',
                '귤': 'Tangerines',
                '참외': 'Melons'
            }
            
            if selected_fruit != "전체 보기":
                db_name = fruit_db_mapping.get(selected_fruit, selected_fruit)
                query += " AND (FrT = %s OR FrT = %s)"
                params.extend([selected_fruit, db_name])
            if search_fmid:
                query += " AND FmID LIKE %s"
                params.append(f"%{search_fmid}%")
            
            query += " ORDER BY FmID DESC, Lo ASC LIMIT 200"
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            if records:
                # FmID 기준으로 그룹화
                grouped_records = {}
                for row in records:
                    fmid = row['FmID']
                    if fmid not in grouped_records:
                        grouped_records[fmid] = []
                    grouped_records[fmid].append(row)

                # Header showing selected fruit
                if selected_fruit != "전체 보기":
                    cols = st.columns([1, 5])
                    with cols[0]:
                        if selected_fruit in FRUIT_IMAGES:
                            st.image(FRUIT_IMAGES[selected_fruit], width=80)
                    with cols[1]:
                        st.header(f"{selected_fruit} 데이터")
                        st.write(f"총 {len(grouped_records)} 건의 고유 FmID 데이터가 조회되었습니다.")
                else:
                    st.header("전체 QR 스캔 데이터")
                    st.write(f"총 {len(grouped_records)} 건의 고유 FmID 데이터가 조회되었습니다.")

                # Card-based Display (FmID 단위로 그룹화된 카드)
                for i, (fmid, fmid_records) in enumerate(grouped_records.items()):
                    latest_row = fmid_records[-1] # 마지막 단계 데이터
                    
                    # A00 -> A10 -> A15 타임라인 텍스트 생성
                    timeline_html = " ➔ ".join(
                        [f"<span style='color: {'#dc3545' if idx == len(fmid_records)-1 else '#000000'}; font-weight: {'bold' if idx == len(fmid_records)-1 else 'normal'};'>{r['Lo']}</span>" 
                         for idx, r in enumerate(fmid_records)]
                    )

                    with st.container():
                        st.markdown(f"""
                        <div class="card">
                            <h3>{latest_row['FrT']} - {latest_row['Vt']}</h3>
                            <div style="display: flex; gap: 20px;">
                                <div>
                                    <p><strong>FmID:</strong> <span style="color: blue;">{fmid}</span></p>
                                    <p><strong>공정 진행:</strong> {timeline_html}</p>
                                    <p><strong>최종 도착 시간:</strong> {latest_row['APC_AD']}</p>
                                </div>
                                <div style="border-left: 1px solid #ddd; padding-left: 20px;">
                                    <p><strong>생산지 코드:</strong> {latest_row['AC']}</p>
                                    <p><strong>최종 수량:</strong> {latest_row['Qt']} {latest_row['Mt']}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        btn_cols = st.columns([1, 1, 4])
                        if btn_cols[0].button(f"상세 이력", key=f"trace_{i}"):
                            st.session_state.trace_fmid = fmid
                            st.session_state.menu_choice = "🔍 상세 이력 추적"
                            st.rerun()
                        if btn_cols[1].button(f"소비자 뷰", key=f"consumer_{i}"):
                            st.session_state.consumer_fmid = fmid
                            st.session_state.menu_choice = "🏠 소비자 페이지"
                            st.rerun()
            else:
                st.info("조건에 맞는 데이터가 없습니다.")
    finally:
        conn.close()

elif menu == "🔍 상세 이력 추적":
    st.title("🕵️ 관리자용 상세 이력 추적")
    
    # Pre-fill if redirected from dashboard
    default_fmid = st.session_state.get("trace_fmid", "")
    fmid_to_trace = st.text_input("추적할 FmID 입력", value=default_fmid)
    
    if fmid_to_trace:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM qr WHERE FmID = %s ORDER BY Lo ASC, APC_AD ASC", (fmid_to_trace,))
                records = cursor.fetchall()
                
                if records:
                    st.subheader(f"📍 FmID: {fmid_to_trace} 유통 타임라인")
                    
                    # Status Summary
                    cols = st.columns(len(records))
                    for i, step in enumerate(records):
                        with cols[i]:
                            st.success(f"**{step['Lo']}**")
                            st.caption(f"{step['APC_AD']}")
                    
                    st.divider()
                    st.dataframe(pd.DataFrame(records), use_container_width=True)
                else:
                    st.warning("해당 FmID의 기록이 없습니다.")
        finally:
            conn.close()

elif menu == "🏠 소비자 페이지":
    st.title("👨‍👩‍👧‍👦 신선한 과일 이야기")
    
    default_fmid = st.session_state.get("consumer_fmid", "")
    fmid = st.text_input("FmID를 입력하세요", value=default_fmid)
    
    if fmid:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM qr WHERE FmID = %s ORDER BY Lo ASC, APC_AD ASC", (fmid,))
                records = cursor.fetchall()
                
                if records:
                    st.subheader(f"이 제품(FmID: {fmid})이 고객님께 오기까지의 과정입니다.")
                    
                    # Blockchain Banner (Mockup)
                    st.success("✅ **블록체인 검증 완료**: 이 제품의 정보는 블록체인 기술로 보호되며, 위변조되지 않았음이 확인되었습니다.")
                    
                    # Product Summary Card
                    with st.expander("✅ 제품 요약 정보", expanded=True):
                        cols = st.columns([1, 2])
                        fruit_name = records[0].get('FrT')
                        if fruit_name in FRUIT_IMAGES:
                            cols[0].image(FRUIT_IMAGES[fruit_name], use_container_width=True)
                        
                        with cols[1]:
                            st.write(f"### {fruit_name} ({records[0].get('Vt')})")
                            st.write(f"**농장명:** {records[0].get('FmID')}")
                            st.write(f"**수확일:** {records[0].get('HD') if records[0].get('HD') else '기록 없음'}")
                            st.write(f"**마트 도착일:** {records[-1].get('APC_AD') if records[-1].get('APC_AD') else '기록 없음'}")
                    
                    # Encyclopedia Section
                    if fruit_name in FRUIT_ENCYCLOPEDIA:
                        st.divider()
                        st.subheader(f"📖 {fruit_name} 도감 정보")
                        st.markdown(f"**{fruit_name}**에 대한 더 자세한 정보를 확인해 보세요.")
                        st.link_button(f"{fruit_name} 도감 보러가기", FRUIT_ENCYCLOPEDIA[fruit_name])
                else:
                    st.error("해당 제품에 대한 정보가 없습니다.")
        finally:
            conn.close()

else: # 이미지 갤러리
    st.title("🖼️ 정적 이미지 갤러리")
    static_dir = Path("static")
    if static_dir.exists():
        images = list(static_dir.glob("*.JPG")) + list(static_dir.glob("*.png"))
        if images:
            cols = st.columns(4)
            for i, img_path in enumerate(images):
                with cols[i % 4]:
                    st.image(str(img_path), caption=img_path.name, use_container_width=True)
        else:
            st.write("이미지가 없습니다.")
    else:
        st.error("static 폴더를 찾을 수 없습니다.")
