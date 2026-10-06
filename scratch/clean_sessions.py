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

try:
    with conn.cursor() as cursor:
        # 1. 21:25분경 테스트 2건 정리 (id 3960, 3961)
        cursor.execute("DELETE FROM sensor_data WHERE id IN (3960, 3961)")
        print(f"Deleted {cursor.rowcount} test dummy records (21:25).")

        # 2. 21:48:51 1건 더미 정리 (id 3967)
        cursor.execute("DELETE FROM sensor_data WHERE id = 3967")
        print(f"Deleted {cursor.rowcount} dummy record (21:48).")

        # 3. 냉장고 실험 세션 단일 통합 (id 3962~3966, 3968~4147 등 오늘 21:47 이후 냉장고 데이터)
        # '냉장고 온도 체크'와 '주행_2026-10-06_22시30분'을 'run_20261006_214737_fridge'로 통합!
        fridge_run_id = "run_20261006_214737_fridge"
        cursor.execute("""
            UPDATE sensor_data 
            SET run_id = %s 
            WHERE run_id IN ('냉장고 온도 체크', '주행_2026-10-06_22시30분')
               OR (timestamp_str >= '2026-10-06 21:47:30' AND id >= 3962)
        """, (fridge_run_id,))
        print(f"Updated {cursor.rowcount} records to unified fridge session: '{fridge_run_id}'.")

        # 4. 10월 4일 1건짜리 쓰레기 파편 정리 (run_id: '주행_2026-10-04_15시37분' -> 10-01 00:00:00 더미)
        cursor.execute("DELETE FROM sensor_data WHERE run_id = '주행_2026-10-04_15시37분'")
        print(f"Deleted {cursor.rowcount} corrupt dummy records from 10-04.")

        # 5. 10월 4일 12시 주행 파편들(4건, 11건, 30건, 207건)을 대표 세션 하나로 통합
        cursor.execute("""
            UPDATE sensor_data
            SET run_id = 'run_20261004_124656_driving'
            WHERE run_id IN ('주행_2026-10-04_12시46분', '주행_2026-10-04_12시47분', '주행_2026-10-04_12시48분', '주행_2026-10-04_12시53분', '주행_2026-10-04_12시58분')
        """)
        print(f"Unified {cursor.rowcount} fragmented records of 10-04 12:00 into 'run_20261004_124656_driving'.")

        conn.commit()

        # 6. 최종 정리된 세션 목록 확인
        cursor.execute("""
            SELECT run_id, COUNT(*) as cnt, MIN(timestamp_str) as start_ts, MAX(timestamp_str) as end_ts
            FROM sensor_data
            GROUP BY run_id
            ORDER BY MAX(id) DESC
        """)
        cleaned = cursor.fetchall()
        print("\n=== Cleaned Sessions in DB ===")
        for c in cleaned:
            print(f"run_id: '{c['run_id']}' | {c['cnt']}건 | {c['start_ts']} ~ {c['end_ts']}")

finally:
    conn.close()
