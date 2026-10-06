import pymysql
import json
from datetime import datetime

def query_today_data():
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
            # 1. run_id 별 최근 통계
            cursor.execute("""
                SELECT run_id, COUNT(*) as cnt, MIN(timestamp_str) as min_ts, MAX(timestamp_str) as max_ts, MIN(created_at) as min_created, MAX(created_at) as max_created
                FROM sensor_data
                GROUP BY run_id
                ORDER BY MAX(id) DESC
                LIMIT 10
            """)
            runs = cursor.fetchall()
            print("=== Recent Runs ===")
            for r in runs:
                print(r)
            
            # 2. 최근 50개 레코드 상세
            cursor.execute("""
                SELECT id, run_id, timestamp_str, created_at, lat, lng, speed, g_force, lux, temperature, humidity, status
                FROM sensor_data
                ORDER BY id DESC
                LIMIT 40
            """)
            recent_rows = cursor.fetchall()
            print("\n=== Recent 40 Records ===")
            for row in recent_rows:
                print(f"ID:{row['id']} | Run:{row['run_id']} | TS:{row['timestamp_str']} | Created:{row['created_at']} | Lat:{row['lat']:.4f} Lng:{row['lng']:.4f} Spd:{row['speed']} | Status:{row['status']}")

    finally:
        conn.close()

if __name__ == "__main__":
    query_today_data()
