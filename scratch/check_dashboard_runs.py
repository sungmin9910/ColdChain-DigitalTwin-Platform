import toml
import pymysql

sec = toml.load(r'Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')['MySQL']
conn = pymysql.connect(
    host=sec['MYSQL_HOST'],
    port=sec.get('MYSQL_PORT', 3306),
    user=sec['MYSQL_USER'],
    password=sec['MYSQL_PASSWORD'],
    database=sec['MYSQL_DATABASE'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute('''
        SELECT run_id, 
               COUNT(*) as cnt, 
               MIN(CASE WHEN timestamp_str NOT LIKE '2026-10-01%' AND timestamp_str != '00:00:00' AND timestamp_str IS NOT NULL THEN timestamp_str END) as start_ts, 
               MAX(timestamp_str) as end_ts,
               MAX(speed) as max_spd,
               MIN(temperature) as min_temp,
               MAX(temperature) as max_temp
        FROM sensor_data 
        WHERE run_id IS NOT NULL 
        GROUP BY run_id 
        HAVING COUNT(*) >= 3 
        ORDER BY MAX(id) DESC
    ''')
    rows = cur.fetchall()
    print("=== Available Dropdown Runs in Dashboard ===")
    for r in rows:
        print(f"  {r['run_id']} | cnt={r['cnt']} | start={r['start_ts']} | end={r['end_ts']} | max_spd={r['max_spd']} | temp:{r['min_temp']}~{r['max_temp']}")
