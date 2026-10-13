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

print("Sample records around transition:")
# Check between 09:38 and 10:30
print("\n--- 09:38 ~ 10:15 (Actual Drive?) ---")
d1 = df[(df['ts'] >= '2026-10-11 09:38:00') & (df['ts'] <= '2026-10-11 10:15:00')]
print(f"Count: {len(d1)}")
print(d1[['ts', 'lat', 'lng', 'speed', 'g_force', 'status']].head(10))
print("...")
print(d1[['ts', 'lat', 'lng', 'speed', 'g_force', 'status']].tail(10))

print("\n--- 10:15 ~ 11:00 ---")
d2 = df[(df['ts'] > '2026-10-11 10:15:00') & (df['ts'] <= '2026-10-11 11:00:00')]
print(f"Count: {len(d2)}")
print(d2[['ts', 'lat', 'lng', 'speed', 'g_force', 'status']].head(5))
print(d2[['ts', 'lat', 'lng', 'speed', 'g_force', 'status']].tail(5))

print("\n--- 11:00 ~ End ---")
d3 = df[df['ts'] > '2026-10-11 11:00:00']
print(f"Count: {len(d3)}")
print(d3[['ts', 'lat', 'lng', 'speed', 'g_force', 'status']].head(5))
print(d3[['ts', 'lat', 'lng', 'speed', 'g_force', 'status']].tail(5))

# Unique locations
print("\nUnique Lat/Lng count:")
print(df.groupby(['lat', 'lng']).size().sort_values(ascending=False).head(10))

conn.close()
