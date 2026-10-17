import toml
import pymysql
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

with conn.cursor() as cur:
    cur.execute("""
        SELECT run_id, count(*) as cnt, min(id) as min_id, max(id) as max_id, 
               min(timestamp_str) as min_ts, max(timestamp_str) as max_ts 
        FROM sensor_data 
        GROUP BY run_id 
        ORDER BY min_id ASC
    """)
    rows = cur.fetchall()
    print("=== All Session Groups in sensor_data ===")
    for r in rows:
        print(f"Session: {r['run_id']:<35} | Count: {r['cnt']:<5} | IDs: {r['min_id']}~{r['max_id']} | Time: {r['min_ts']} ~ {r['max_ts']}")

conn.close()
