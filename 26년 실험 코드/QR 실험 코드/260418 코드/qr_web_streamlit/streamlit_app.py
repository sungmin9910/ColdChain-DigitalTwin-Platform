import streamlit as st
import pandas as pd
import pymysql
import hashlib
import json
import os
from pathlib import Path

# --- Configuration ---
FRUIT_TYPES = ['사과', '샤인머스켓', '복숭아', '배', '포도']
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

# --- App UI ---
st.set_page_config(page_title="QR 과일 이력 시스템", layout="wide")

st.sidebar.title("메뉴")
page = st.sidebar.radio("페이지 선택", ["대시보드", "이력 추적", "이미지 갤러리"])

if page == "대시보드":
    st.title("🍎 과일 데이터 대시보드")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_fruit = st.selectbox("과일 종류 필터", ["전체"] + FRUIT_TYPES)
    with col2:
        search_fmid = st.text_input("FmID 검색")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM qr WHERE 1=1"
            params = []
            if selected_fruit != "전체":
                query += " AND FrT = %s"
                params.append(selected_fruit)
            if search_fmid:
                query += " AND FmID LIKE %s"
                params.append(f"%{search_fmid}%")
            
            query += " ORDER BY APC_AD DESC LIMIT 100"
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            if records:
                df = pd.DataFrame(records)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("조건에 맞는 데이터가 없습니다.")
    finally:
        conn.close()

elif page == "이력 추적":
    st.title("🔍 상세 이력 추적")
    fmid_to_trace = st.text_input("추적할 FmID 입력")
    
    if fmid_to_trace:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM qr WHERE FmID = %s ORDER BY Lo ASC, APC_AD ASC", (fmid_to_trace,))
                records = cursor.fetchall()
                
                if records:
                    st.subheader(f"FmID: {fmid_to_trace} 의 유통 과정")
                    
                    # 과일 정보
                    fruit_name = records[0].get('FrT')
                    if fruit_name in FRUIT_IMAGES:
                        col_img, col_txt = st.columns([1, 3])
                        with col_img:
                            st.image(FRUIT_IMAGES[fruit_name], width=150)
                        with col_txt:
                            st.write(f"**품목:** {fruit_name}")
                            st.link_button("백과사전 보기", FRUIT_ENCYCLOPEDIA.get(fruit_name, "#"))
                    
                    # 데이터 표
                    st.table(records)
                    
                    # 무결성 검증 (단순 예시)
                    latest_record = records[-1]
                    current_hash = calculate_hash(latest_record)
                    st.info(f"현재 데이터 해시: {current_hash}")
                    
                else:
                    st.warning("해당 FmID의 기록이 없습니다.")
        finally:
            conn.close()

else: # 이미지 갤러리
    st.title("🖼️ 정적 이미지 갤러리")
    static_dir = Path("static")
    if static_dir.exists():
        images = list(static_dir.glob("*.JPG")) + list(static_dir.glob("*.png"))
        if images:
            cols = st.columns(3)
            for i, img_path in enumerate(images):
                with cols[i % 3]:
                    st.image(str(img_path), caption=img_path.name, use_container_width=True)
        else:
            st.write("이미지가 없습니다.")
    else:
        st.error("static 폴더를 찾을 수 없습니다.")
