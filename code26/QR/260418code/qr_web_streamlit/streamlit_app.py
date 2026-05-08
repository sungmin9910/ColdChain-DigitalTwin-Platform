import streamlit as st
import pymysql
import pandas as pd

import os
from dotenv import load_dotenv
load_dotenv()

# --- 페이지 설정 ---
st.set_page_config(page_title="프리미엄 과일 안심 이력조회", page_icon="🍏", layout="centered")

# --- DB 설정 (AWS RDS) ---
DB_HOST = "15.165.68.30"
DB_USER = "admin"
# .env에서 불러오거나, Streamlit Cloud 배포 시 st.secrets를 사용하도록 이중 지원
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, port=DB_PORT, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- 메인 화면 ---
st.title("🍏 프리미엄 과일 안심 이력조회")
st.markdown("고객님께서 구매하신 과일이 어떤 과정을 거쳐 식탁에 올랐는지 투명하게 공개합니다.")

# 1. QR 코드의 파라미터에서 FmID 가져오기
query_params = st.query_params
fm_id = query_params.get("FmID", None)

if not fm_id:
    st.warning("⚠️ QR 코드를 통해 접속해주세요. (URL에 FmID가 없습니다)")
    st.stop()

# 2. DB에서 이력 데이터 가져오기
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    # FmID에 해당하는 모든 이력을 시간순으로 가져옵니다
    query = "SELECT * FROM qr WHERE FmID = %s ORDER BY id ASC"
    cursor.execute(query, (fm_id,))
    records = cursor.fetchall()
    conn.close()
except Exception as e:
    st.error(f"데이터베이스 연결 오류: {e}")
    st.stop()

if not records:
    st.error(f"❌ 검색된 과일 이력(FmID: {fm_id})이 없습니다.")
    st.stop()

# 3. 과일 기본 정보 표시 (가장 최신 레코드 기준)
latest = records[-1]

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric("과일 종류", f"{latest.get('FrT', '알수없음')} ({latest.get('Vt', '')})")
    st.metric("농가 번호 (FmID)", fm_id)
with col2:
    st.metric("재배 방식", latest.get('Mt', '일반'))
    st.metric("출하 수량", f"{latest.get('Qt', '0')} 박스")

st.divider()
st.subheader("🚚 유통 타임라인")

# 4. 단계별 타임라인 그리기
stage_names = {
    "A10": ("입고 완료", "APC 센터에 과일이 안전하게 도착했습니다.", "🏢"),
    "A11": ("세척 완료", "깨끗하고 안전하게 세척되었습니다.", "💦"),
    "A12": ("선별 완료", "크기와 당도에 따라 최상품으로 선별되었습니다.", "🔍"),
    "A13": ("포장 완료", "신선도를 유지하기 위해 꼼꼼히 포장되었습니다.", "📦"),
    "A14": ("저온 저장", "최적의 온습도 환경에서 신선하게 보관되었습니다.", "❄️"),
    "A15": ("출하 완료", "고객님을 향해 신선하게 출발했습니다!", "🚛")
}

# 기록된 단계를 순서대로 표시
for row in records:
    stage_code = row.get("Lo")
    if stage_code in stage_names:
        title, desc, icon = stage_names[stage_code]
        
        # 시간 정보 추출 (각 단계별 해당 컬럼)
        time_cols = {"A10":"APC_AD", "A11":"APC_WD", "A12":"APC_RT", "A13":"APC_PT", "A14":"APC_StD", "A15":"APC_OP"}
        stage_time = row.get(time_cols.get(stage_code))
        
        with st.container():
            st.markdown(f"### {icon} {title}")
            if stage_time:
                st.caption(f"🕒 처리 시간: {stage_time}")
            st.write(desc)
            
            # A14 (저장) 단계일 경우 온습도 특별 표시
            if stage_code == "A14" and row.get("Tp") is not None and row.get("Hm") is not None:
                st.info(f"🌡️ 보관 온도: **{row['Tp']}°C**  |  💧 보관 습도: **{row['Hm']}%** (최적 신선도 유지 중)")
            
            st.markdown("---")

st.success("✨ 이 과일은 신선하고 안전하게 관리되었습니다. 안심하고 드세요!")
