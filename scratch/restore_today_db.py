import pymysql
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')


def restore_and_unify_today_session():
    conn = pymysql.connect(
        host="labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com",
        port=3306,
        user="admin",
        password="12345678",
        database="lab225",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    unify_run_id = "run_20261006_204402_evening"
    
    with open("scratch/dump_20261006_evening.jsonl", "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    today_records = [r for r in records if str(r.get('timestamp_str', '')).startswith('2026-10-06')]
    print(f"Loaded {len(today_records)} records from flash dump for today (2026-10-06)")

    try:
        with conn.cursor() as cursor:
            # 1. 오늘 기존에 분할 저장된 28건 삭제 (ID 3573 ~ 3600)
            cursor.execute("""
                DELETE FROM sensor_data 
                WHERE id >= 3573 AND timestamp_str LIKE '2026-10-06%'
            """)
            deleted_count = cursor.rowcount
            print(f"Deleted {deleted_count} fragmented records from DB.")

            # 2. 덤프 데이터 179건을 단일 세션으로 INSERT
            # 5초 간격 또는 10초 간격? 보드 덤프 179건 전체를 넣는 것이 시계열 연속성에 최고!
            sql = """
            INSERT INTO sensor_data 
            (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            insert_rows = []
            for r in today_records:
                ts = r.get("timestamp_str", "")
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                insert_rows.append((
                    r.get("device", "carrier-c6-01"),
                    ts,
                    float(r.get("temperature", 0.0)),
                    float(r.get("humidity", 0.0)),
                    float(r.get("lux", 0.0)),
                    float(r.get("g_force", 1.0)),
                    float(r.get("speed", 0.0)),
                    float(r.get("lat", 0.0)),
                    float(r.get("lng", 0.0)),
                    r.get("status", "정상"),
                    unify_run_id,
                    dt # created_at도 실제 측정 시각으로 정확히 동기화
                ))
            
            cursor.executemany(sql, insert_rows)
            conn.commit()
            print(f"✅ Successfully inserted {len(insert_rows)} records into '{unify_run_id}'!")
            
            # 3. 검증
            cursor.execute("""
                SELECT COUNT(*) as cnt, MIN(timestamp_str) as start_ts, MAX(timestamp_str) as end_ts, 
                       MIN(lat) as min_lat, MAX(lat) as max_lat, MAX(speed) as max_spd
                FROM sensor_data
                WHERE run_id = %s
            """, (unify_run_id,))
            stat = cursor.fetchone()
            print("\n=== Restored Session Summary ===")
            print(stat)

    finally:
        conn.close()

if __name__ == "__main__":
    restore_and_unify_today_session()
