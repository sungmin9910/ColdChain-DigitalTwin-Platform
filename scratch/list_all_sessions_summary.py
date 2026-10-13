import toml
import pymysql
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']

conn = pymysql.connect(
    host=cfg['MYSQL_HOST'],
    port=cfg.get('MYSQL_PORT', 3306),
    user=cfg['MYSQL_USER'],
    password=cfg['MYSQL_PASSWORD'],
    database=cfg['MYSQL_DATABASE'],
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as c:
    c.execute("""
        SELECT 
            run_id, 
            COUNT(*) as total_cnt,
            SUM(CASE WHEN lat != 0.0 AND lng != 0.0 THEN 1 ELSE 0 END) as valid_gps,
            MIN(timestamp_str) as start_ts,
            MAX(timestamp_str) as end_ts,
            MAX(speed) as max_spd,
            MIN(temperature) as min_t,
            MAX(temperature) as max_t,
            MIN(id) as min_id,
            MAX(id) as max_id
        FROM sensor_data
        GROUP BY run_id
        ORDER BY min_id ASC
    """)
    rows = c.fetchall()

print("=" * 100)
print(f"{'Run ID':<32} | {'Total':<6} | {'GPS':<5} | {'MaxSpd':<6} | {'Period':<35}")
print("=" * 100)
for r in rows:
    p = f"{str(r['start_ts'])[:16]} ~ {str(r['end_ts'])[:16]}"
    print(f"{str(r['run_id']):<32} | {r['total_cnt']:<6} | {r['valid_gps']:<5} | {float(r['max_spd'] or 0):<6.1f} | {p}")
print("=" * 100)

conn.close()
