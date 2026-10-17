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

try:
    with conn.cursor() as cur:
        # Check rows to delete
        cur.execute("SELECT count(*) as cnt, min(id) as min_id, max(id) as max_id FROM sensor_data WHERE id >= 6677")
        res = cur.fetchone()
        cnt = res['cnt']
        min_id = res['min_id']
        max_id = res['max_id']
        print(f"Target rows to delete (tonight's bench testing): {cnt} rows (IDs {min_id} ~ {max_id})")
        
        if cnt > 0:
            cur.execute("DELETE FROM sensor_data WHERE id >= 6677")
            conn.commit()
            print(f"Successfully deleted {cnt} test records from sensor_data.")
        else:
            print("No test records found to delete.")
            
        # Verify remaining sessions
        cur.execute("""
            SELECT run_id, count(*) as cnt, min(id) as min_id, max(id) as max_id, 
                   min(timestamp_str) as min_ts, max(timestamp_str) as max_ts 
            FROM sensor_data 
            GROUP BY run_id 
            ORDER BY min_id DESC
            LIMIT 5
        """)
        rows = cur.fetchall()
        print("\n=== Latest 5 Sessions in sensor_data after cleanup ===")
        for r in rows:
            print(f"Session: {r['run_id']:<35} | Count: {r['cnt']:<5} | IDs: {r['min_id']}~{r['max_id']} | Time: {r['min_ts']} ~ {r['max_ts']}")

finally:
    conn.close()
