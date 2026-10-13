import toml
import pymysql
import sys

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
            MIN(id) as min_id, 
            MAX(id) as max_id, 
            COUNT(*) as cnt, 
            MIN(timestamp_str) as min_ts, 
            MAX(timestamp_str) as max_ts, 
            MIN(created_at) as min_created,
            MAX(created_at) as max_created,
            MIN(lat) as min_lat, 
            MAX(lat) as max_lat, 
            MIN(lng) as min_lng, 
            MAX(lng) as max_lng, 
            MAX(speed) as max_spd, 
            AVG(speed) as avg_spd, 
            MAX(g_force) as max_g 
        FROM sensor_data 
        WHERE run_id LIKE '%2026-10-11%'
    """)
    res = c.fetchone()
    print("2026-10-11 Session Stats:")
    for k, v in res.items():
        print(f"  {k}: {v}")

    # Check first 5 records
    c.execute("""
        SELECT id, run_id, timestamp_str, created_at, lat, lng, speed, g_force, status
        FROM sensor_data
        WHERE run_id LIKE '%2026-10-11%'
        ORDER BY id ASC LIMIT 5
    """)
    first5 = c.fetchall()
    print("\nFirst 5 records:")
    for r in first5:
        print(r)

    # Check last 5 records
    c.execute("""
        SELECT id, run_id, timestamp_str, created_at, lat, lng, speed, g_force, status
        FROM sensor_data
        WHERE run_id LIKE '%2026-10-11%'
        ORDER BY id DESC LIMIT 5
    """)
    last5 = c.fetchall()
    print("\nLast 5 records:")
    for r in last5:
        print(r)

    # Also check what other records were created on 2026-10-10 or 2026-10-11
    c.execute("""
        SELECT run_id, COUNT(*) as cnt, MIN(created_at) as min_c, MAX(created_at) as max_c
        FROM sensor_data
        WHERE created_at >= '2026-10-09 00:00:00'
        GROUP BY run_id
        ORDER BY MIN(id) DESC
    """)
    recent_runs = c.fetchall()
    print("\nAll Runs from 2026-10-09 onwards:")
    for r in recent_runs:
        print(r)

conn.close()
