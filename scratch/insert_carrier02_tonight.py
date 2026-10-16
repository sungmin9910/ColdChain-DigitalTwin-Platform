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

session_id = "truck02_주행_2026-10-16_21시13분"

with open('scratch/carrier02_clean_dump.jsonl', 'r', encoding='utf-8') as f:
    recs = [json.loads(l) for l in f if l.strip()]

tonight = [r for r in recs if r.get('timestamp_str', '') >= '2026-10-16 21:13:00']
print(f"Total tonight records to insert: {len(tonight)}")

try:
    with conn.cursor() as cur:
        # 1) Clean up any partial/broken records from tonight
        cur.execute("DELETE FROM sensor_data WHERE device = 'carrier-c6-02' AND timestamp_str >= '2026-10-16 21:00:00'")
        print(f"Cleaned up {cur.rowcount} previous records from 21:00:00 onwards.")
        
        # 2) Insert all tonight records
        sql = """
        INSERT INTO sensor_data 
        (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        insert_data = []
        for r in tonight:
            ts_str = r.get('timestamp_str')
            # Calculate UTC created_at from KST timestamp_str
            try:
                dt_kst = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                dt_utc = dt_kst - timedelta(hours=9)
                created_at_val = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                created_at_val = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

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
                session_id,
                created_at_val
            )
            insert_data.append(val)
            
        cur.executemany(sql, insert_data)
        conn.commit()
        print(f"Successfully inserted {len(insert_data)} rows into sensor_data with run_id='{session_id}'!")
        
        # 3) Verify the session in DB
        cur.execute("""
            SELECT run_id, count(*) as cnt, min(timestamp_str) as t_start, max(timestamp_str) as t_end, 
                   max(speed) as max_spd, max(g_force) as max_g, count(case when lat > 0 then 1 end) as gps_cnt
            FROM sensor_data
            WHERE run_id = %s
            GROUP BY run_id
        """, (session_id,))
        summary = cur.fetchone()
        print("DB Summary:", summary)
        
finally:
    conn.close()
