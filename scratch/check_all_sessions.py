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
        SELECT run_id, COUNT(*) as cnt, MIN(timestamp_str) as start_ts, MAX(timestamp_str) as end_ts,
               MIN(created_at) as min_created, MAX(created_at) as max_created
        FROM sensor_data 
        WHERE run_id IS NOT NULL 
        GROUP BY run_id 
        HAVING COUNT(*) >= 1 
        ORDER BY MAX(id) DESC
    """)
    rows = cursor.fetchall()

conn.close()

def format_session_label(session_id):
    if session_id == "실시간 주행 (현재 실험)":
        return "🟢 실시간 주행 (현재 실험)"
    elif "20261006" in session_id or "2026-10-06" in session_id:
        return f"🚗 [10-06 저녁 주행] 전북대 ➔ 자택 (179건, 최고 83km/h)"
    elif "20261003" in session_id or "2026-10-03" in session_id:
        if "1834" in session_id or "18" in session_id:
            return f"🚗 [10-03 저녁 주행] {session_id}"
        return f"🚗 [10-03 실험] {session_id}"
    elif "departure" in session_id:
        return "🚗 [10-02 출발] 전주 ➔ 대전 (89km, 1,356건)"
    elif "return" in session_id:
        return "🚗 [10-02 복귀] 대전 ➔ 전주 (85km, 478건)"
    elif "065739" in session_id:
        return "🧪 [10-01 야외] 전북대 캠퍼스 GPS 검증 (157건)"
    elif "30km" in session_id:
        return "📦 [07-15 모의] 30km 시뮬레이션 주행 (181건)"
    else:
        return f"📂 {session_id}"

print("=== Current All run_ids in DB ===")
for r in rows:
    raw_id = r['run_id']
    label = format_session_label(raw_id)
    print(f"RAW: '{raw_id}' ({r['cnt']}건) | TS: {r['start_ts']} ~ {r['end_ts']} | LABEL: '{label}'")
