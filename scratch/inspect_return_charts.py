import pymysql
import pandas as pd
import toml

secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']

conn = pymysql.connect(
    host=cfg['MYSQL_HOST'],
    user=cfg['MYSQL_USER'],
    password=cfg['MYSQL_PASSWORD'],
    database=cfg['MYSQL_DATABASE'],
    port=cfg.get('MYSQL_PORT', 3306),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SELECT id, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng FROM sensor_data WHERE run_id = 'run_20261002_103710_return' ORDER BY id ASC")
    rows = cur.fetchall()

df = pd.DataFrame(rows)
print(f"Total rows: {len(df)}")
print("\nFirst 10 rows:")
print(df[['id', 'timestamp_str', 'created_at', 'temperature', 'humidity', 'speed', 'g_force', 'lat', 'lng']].head(10))

print("\nLast 10 rows:")
print(df[['id', 'timestamp_str', 'created_at', 'temperature', 'humidity', 'speed', 'g_force', 'lat', 'lng']].tail(10))

# Check how many rows have speed > 0 or g_force > 1.2
print("\nSpeed distribution:")
print(df['speed'].describe())

print("\nG-force distribution:")
print(df['g_force'].describe())

# Check timestamps in load_run_data
# In Step4_Run_Coldchain_v2.py:
# ts = item.get("timestamp_str")
# if not ts or ts == "00:00:00" or str(ts).startswith("00:00"):
#     ts = str(created_at)
# Let's inspect timestamp values and chart x-axis!
print("\nTimestamps head 10 and tail 10:")
print(df['timestamp_str'].head(10).tolist())
print(df['timestamp_str'].tail(10).tolist())
