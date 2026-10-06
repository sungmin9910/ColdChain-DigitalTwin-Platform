import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host="labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com",
    port=3306,
    user="admin",
    password="12345678",
    database="lab225",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT run_id, COUNT(*) as cnt, MIN(timestamp_str) as start_ts, MAX(timestamp_str) as end_ts
        FROM sensor_data 
        WHERE run_id IS NOT NULL 
        GROUP BY run_id 
        HAVING COUNT(*) >= 3 
        ORDER BY MAX(id) DESC
    """)
    rows = cursor.fetchall()
conn.close()

def format_session_label(session_id):
    if session_id == "실시간 주행 (현재 실험)":
        return "🟢 실시간 주행 (현재 실험)"
    elif "fridge" in session_id or "냉장고" in session_id:
        return "❄️ [10-06 급랭실험] 냉장고 스텝인풋 (185건, 27°C ➔ 5.6°C)"
    elif session_id == "run_20261006_204402_evening" or "1006_evening" in session_id:
        return "🚗 [10-06 저녁주행] 전북대 ➔ 자택 (179건, 최고 83km/h)"
    elif "15시36분" in session_id or "20261004_15" in session_id:
        return "🚗 [10-04 오후주행] 전주 시내 테스트 (300건)"
    elif "124656" in session_id or "12시" in session_id or "20261004_12" in session_id:
        return "🚗 [10-04 낮주행] 전북대 ➔ 전주 시내 (283건)"
    elif "20261003_1834" in session_id:
        return "🚗 [10-03 저녁주행] 야간 주행 벤치마크 (7건)"
    elif "20261003_1800" in session_id:
        return "🧪 [10-03 센서검증] 통신 및 센서 기본점검 (3건)"
    elif "departure" in session_id:
        return "🚗 [10-02 편도출발] 전주 ➔ 대전 (89km, 1,356건)"
    elif "return" in session_id:
        return "🚗 [10-02 편도복귀] 대전 ➔ 전주 (85km, 478건)"
    elif "065739" in session_id:
        return "🧪 [10-01 야외검증] 캠퍼스 GPS 텔레메트리 (157건)"
    elif "30km" in session_id:
        return "📦 [07-15 모의주행] 30km 표준 시뮬레이션 (181건)"
    else:
        return f"📂 {session_id}"

print("=== Cleaned Sessions with New Label Function ===")
for r in rows:
    raw_id = r['run_id']
    label = format_session_label(raw_id)
    print(f"[{label}]  <--  {raw_id} ({r['cnt']}건)")
