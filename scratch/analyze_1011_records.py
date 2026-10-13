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
        SELECT id, timestamp_str, lat, lng, speed, g_force, temperature, humidity, lux, status
        FROM sensor_data
        WHERE run_id = '주행_2026-10-11_09시38분'
        ORDER BY id ASC
    """)
    rows = c.fetchall()

df = pd.DataFrame(rows)
df['timestamp'] = pd.to_datetime(df['timestamp_str'])
print(f"Total rows: {len(df)}")
print(f"Time range: {df['timestamp'].min()} ~ {df['timestamp'].max()}")

# Driving vs stationary
driving = df[df['speed'] >= 5.0]
stationary = df[df['speed'] < 5.0]
print(f"Moving (speed >= 5 km/h): {len(driving)} records")
print(f"Stationary (speed < 5 km/h): {len(stationary)} records")

if len(driving) > 0:
    print(f"Driving time range: {driving['timestamp'].min()} ~ {driving['timestamp'].max()}")
    print(f"Driving max speed: {driving['speed'].max():.1f} km/h, avg speed: {driving['speed'].mean():.1f} km/h")
    print(f"Driving start coord: ({driving.iloc[0]['lat']}, {driving.iloc[0]['lng']})")
    print(f"Driving end coord: ({driving.iloc[-1]['lat']}, {driving.iloc[-1]['lng']})")

# Look at time intervals
print("\nTimestamp timeline distribution (hourly breakdown):")
df['hour'] = df['timestamp'].dt.hour
print(df.groupby('hour').agg(cnt=('id', 'count'), min_speed=('speed', 'min'), max_speed=('speed', 'max'), avg_speed=('speed', 'mean')))

conn.close()
