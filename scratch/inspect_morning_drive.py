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
        SELECT id, timestamp_str, lat, lng, speed, g_force, status
        FROM sensor_data
        WHERE run_id = '주행_2026-10-11_09시38분'
        ORDER BY id ASC
    """)
    rows = c.fetchall()

df = pd.DataFrame(rows)
df['ts'] = pd.to_datetime(df['timestamp_str'])

# Find when it was actually moving along the road from south Jeonju to JBNU
# Let's inspect rows 0 to 120
for idx, r in df.iloc[:120].iterrows():
    if r['speed'] > 1.0 or r['lat'] != 35.8484:
        print(f"[{idx}] {r['ts']} | Lat:{r['lat']:.4f} Lng:{r['lng']:.4f} | Spd:{r['speed']:4.1f} | {r['status']}")

conn.close()
