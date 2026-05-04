import streamlit as st
import pandas as pd
import pymysql
import hashlib
import json
import os
from pathlib import Path

# --- Configuration ---
FRUIT_TYPES = ['사과', '샤인머스켓', '복숭아', '배', '포도']
FRUIT_ICONS = {
    '사과': '🍎',
    '샤인머스켓': '🍇',
    '복숭아': '🍑',
    '배': '🍐',
    '포도': '🍇'
}
FRUIT_IMAGES = {
    '사과': 'static/image/사과.png',
    '샤인머스켓': 'static/image/샤인머스켓.png',
    '복숭아': 'static/image/복숭아.png',
    '배': 'static/image/배.png',
    '포도': 'static/image/포도.png'
}
FRUIT_ENCYCLOPEDIA = {
    '사과': 'https://terms.naver.com/entry.naver?docId=1107936&cid=40942&categoryId=32711',
    '샤인머스켓': 'https://terms.naver.com/entry.naver?docId=5704403&cid=40942&categoryId=32711',
    '복숭아': 'https://terms.naver.com/entry.naver?docId=1103333&cid=40942&categoryId=32711',
    '배': 'https://terms.naver.com/entry.naver?docId=1099988&cid=40942&categoryId=32711',
    '포도': 'https://terms.naver.com/entry.naver?docId=1158525&cid=40942&categoryId=32711'
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #eee;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("🍎 과일 도감")
    
    # Navigation
    menu = st.radio("이동할 페이지", ["📊 대시보드", "🔍 상세 이력 추적", "🏠 소비자 페이지", "🖼️ 이미지 갤러리"])
    
    st.divider()
    
    # Encyclopedia Links
    st.subheader("📖 과일 백과사전")
    for fruit in FRUIT_TYPES:
        cols = st.columns([1, 4])
        with cols[0]:
            st.write(FRUIT_ICONS[fruit])
        with cols[1]:
            st.markdown(f"[{fruit} 도감]({FRUIT_ENCYCLOPEDIA[fruit]})")

# --- Page Logic ---

if menu == "📊 대시보드":
    st.title("🍎 스마트팜 QR 스캔 데이터")
    
    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        selected_fruit = st.selectbox("과일 종류 필터", ["전체 보기"] + FRUIT_TYPES)
    with col_search:
        search_fmid = st.text_input("FmID 검색", placeholder="검색할 FmID를 입력하세요...")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM qr WHERE 1=1"
            params = []
            if selected_fruit != "전체 보기":
                query += " AND FrT = %s"
                params.append(selected_fruit)
            if search_fmid:
                query += " AND FmID LIKE %s"
                params.append(f"%{search_fmid}%")
            
            query += " ORDER BY APC_AD DESC LIMIT 50"
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            if records:
                # Header showing selected fruit
                if selected_fruit != "전체 보기":
                    cols = st.columns([1, 5])
                    with cols[0]:
                        st.image(FRUIT_IMAGES[selected_fruit], width=80)
                    with cols[1]:
                        st.header(f"{selected_fruit} 데이터")
                        st.write(f"총 {len(records)} 건의 데이터가 조회되었습니다.")
                else:
                    st.header("전체 QR 스캔 데이터")
                    st.write(f"총 {len(records)} 건의 최신 데이터가 조회되었습니다.")

                # Card-based Display
                for row in records:
                    with st.container():
                        st.markdown(f"""
                        <div class="card">
                            <h3>{row['FrT']} - {row['Vt']}</h3>
                            <div style="display: flex; gap: 20px;">
                                <div>
                                    <p><strong>FmID:</strong> <span style="color: blue;">{row['FmID']}</span></p>
                                    <p><strong>현재 공정:</strong> <span style="color: red; font-weight: bold;">{row['Lo']}</span></p>
                                    <p><strong>APC 도착 시간:</strong> {row['APC_AD']}</p>
                                </div>
                                <div style="border-left: 1px solid #ddd; padding-left: 20px;">
                                    <p><strong>생산지 코드:</strong> {row['AC']}</p>
                                    <p><strong>수량:</strong> {row['Qt']} {row['Mt']}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        btn_cols = st.columns([1, 1, 4])
                        if btn_cols[0].button(f"상세 이력", key=f"trace_{row['id']}"):
                            st.session_state.trace_fmid = row['FmID']
                            # Note: Switching pages in radio via state is tricky, usually we set a trigger
                            # For simplicity, we just show a message or use st.query_params
                        if btn_cols[1].button(f"소비자 뷰", key=f"consumer_{row['id']}"):
                            st.session_state.consumer_fmid = row['FmID']
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
