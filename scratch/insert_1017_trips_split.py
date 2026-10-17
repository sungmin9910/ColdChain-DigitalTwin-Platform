import json
import toml
import pymysql
from datetime import datetime, timedelta
import sys

sys.stdout.reconfigure(encoding='utf-8')

sec = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')['MySQL']
conn = pymysql.connect(
    host=sec['MYSQL_HOST'],
    port=sec.get('MYSQL_PORT', 3306),
    user=sec['MYSQL_USER'],
    password=sec['MYSQL_PASSWORD'],
    database=sec['MYSQL_DATABASE'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with open('scratch/carrier02_dump_1017.jsonl', 'r', encoding='utf-8') as f:
    recs = [json.loads(l) for l in f if l.strip()]

print(f"Total dumped records: {len(recs)}")

# Split at index 198 (gap of 71.4 minutes)
trip1 = recs[:199]
trip2 = recs[199:]

session1_id = "truck02_주행_2026-10-17_13시01분"
session2_id = "truck02_주행_2026-10-17_14시29분"

print(f"Trip 1: {len(trip1)} records ({trip1[0]['timestamp_str']} ~ {trip1[-1]['timestamp_str']}) -> {session1_id}")
print(f"Trip 2: {len(trip2)} records ({trip2[0]['timestamp_str']} ~ {trip2[-1]['timestamp_str']}) -> {session2_id}")

try:
    with conn.cursor() as cur:
        # 1) Clean up any partial 10/17 records for carrier-c6-02
        cur.execute("DELETE FROM sensor_data WHERE device = 'carrier-c6-02' AND timestamp_str >= '2026-10-17 00:00:00'")
        print(f"Cleaned up {cur.rowcount} previous records from 2026-10-17.")

        sql = """
        INSERT INTO sensor_data 
        (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 2) Insert Trip 1
        data_trip1 = []
        for r in trip1:
            ts_str = r.get('timestamp_str')
            dt_kst = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            created_at_val = (dt_kst - timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
            val = (
                r.get("device", "carrier-c6-02"),
                ts_str,
                float(r.get("temperature", 0.0)),
                float(r.get("humidity", 0.0)),
                float(r.get("lux", 0.0)),
                float(r.get("g_force", 1.0)),
                float(r.get("speed", 0.0)),
                float(r.get("lat", 0.0)),
                float(r.get("lng", 0.0)),
                r.get("status", "정상"),
                session1_id,
                created_at_val
            )
            data_trip1.append(val)
        cur.executemany(sql, data_trip1)
        print(f"Successfully inserted {len(data_trip1)} rows for Trip 1 ({session1_id})!")

        # 3) Insert Trip 2
        data_trip2 = []
        for r in trip2:
            ts_str = r.get('timestamp_str')
            dt_kst = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            created_at_val = (dt_kst - timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
            val = (
                r.get("device", "carrier-c6-02"),
                ts_str,
                float(r.get("temperature", 0.0)),
                float(r.get("humidity", 0.0)),
                float(r.get("lux", 0.0)),
                float(r.get("g_force", 1.0)),
                float(r.get("speed", 0.0)),
                float(r.get("lat", 0.0)),
                float(r.get("lng", 0.0)),
                r.get("status", "정상"),
                session2_id,
                created_at_val
            )
            data_trip2.append(val)
        cur.executemany(sql, data_trip2)
        print(f"Successfully inserted {len(data_trip2)} rows for Trip 2 ({session2_id})!")

        conn.commit()

        # 4) Verify both sessions
        cur.execute("""
            SELECT run_id, count(*) as cnt, min(timestamp_str) as t_start, max(timestamp_str) as t_end,
                   max(speed) as max_spd, max(g_force) as max_g, count(case when lat > 0 then 1 end) as gps_cnt
            FROM sensor_data
            WHERE device = 'carrier-c6-02' AND timestamp_str >= '2026-10-17 00:00:00'
            GROUP BY run_id
            ORDER BY min(timestamp_str) ASC
        """)
        rows = cur.fetchall()
        print("\n=== Verified Sessions in DB ===")
        for r in rows:
            print(r)

finally:
    conn.close()
