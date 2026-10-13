import pymysql, toml, pandas as pd
secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']
conn = pymysql.connect(host=cfg['MYSQL_HOST'], user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'], port=cfg.get('MYSQL_PORT', 3306), charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as cur:
    cur.execute("SELECT id, timestamp_str FROM sensor_data WHERE run_id = 'run_20261002_103710_return' ORDER BY id ASC")
    rows = cur.fetchall()

df = pd.DataFrame(rows)
df['ts'] = pd.to_datetime(df['timestamp_str'])
print('Min time:', df['ts'].min())
print('Max time:', df['ts'].max())
print('Total duration:', df['ts'].max() - df['ts'].min())
print('First 5:', [str(t) for t in df['ts'].head(5)])
