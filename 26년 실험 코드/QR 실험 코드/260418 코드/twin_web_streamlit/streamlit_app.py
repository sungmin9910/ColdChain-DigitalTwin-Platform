import streamlit as st
import pandas as pd
import pymysql
import time
from datetime import datetime

# --- Configuration ---
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

st.set_page_config(page_title="디지털 트윈 모니터링", layout="wide")

st.title("🌐 디지털 트윈 실시간 모니터링")
st.markdown("창고 입고(A14) 단계의 센서 데이터를 실시간으로 조회합니다.")

# placeholder for real-time data
data_placeholder = st.empty()

def fetch_sensor_data():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Tp, Hm, APC_StD 
                FROM qr 
                WHERE Lo = 'A14' AND Tp IS NOT NULL 
                ORDER BY APC_StD DESC 
                LIMIT 20
            """)
            return cursor.fetchall()
    except Exception as e:
        st.error(f"데이터 조회 오류: {e}")
        return None
    finally:
        conn.close()

# Sidebar controls
refresh_rate = st.sidebar.slider("새로고침 간격 (초)", 1, 60, 5)
show_history = st.sidebar.checkbox("이력 데이터 보기", value=True)

while True:
    records = fetch_sensor_data()
    
    with data_placeholder.container():
        if records:
            latest = records[0]
            
            # 메트릭 표시
            col1, col2, col3 = st.columns(3)
            col1.metric("온도 (Tp)", f"{latest['Tp']} °C")
            col2.metric("습도 (Hm)", f"{latest['Hm']} %")
            col3.metric("최신 업데이트", str(latest['APC_StD']))
            
            if show_history:
                st.subheader("최근 데이터 추세")
                df = pd.DataFrame(records)
                df['APC_StD'] = pd.to_datetime(df['APC_StD'])
                
                # 차트
                st.line_chart(df.set_index('APC_StD')[['Tp', 'Hm']])
                
                st.subheader("최근 20개 데이터 내역")
                st.table(df)
        else:
            st.warning("데이터를 찾을 수 없습니다. (Lo='A14' 조건)")
            
    time.sleep(refresh_rate)
