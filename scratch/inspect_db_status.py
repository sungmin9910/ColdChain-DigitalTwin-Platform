import toml
import pymysql
import os

sec_path = r'Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml'
sec = toml.load(sec_path)
db_cfg = sec['MySQL']

conn = pymysql.connect(
    host=db_cfg['MYSQL_HOST'],
    port=db_cfg.get('MYSQL_PORT', 3306),
    user=db_cfg['MYSQL_USER'],
    password=db_cfg['MYSQL_PASSWORD'],
    database=db_cfg['MYSQL_DATABASE'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

print('=== DB Connection Success ===')
with conn.cursor() as cur:
    # 1. Tables list
    cur.execute('SHOW TABLES')
    tables = cur.fetchall()
    print('Tables in DB:', [list(t.values())[0] for t in tables])
    
    # 2. Total count in sensor_data
    cur.execute('SELECT COUNT(*) as cnt FROM sensor_data')
    total_cnt = cur.fetchone()['cnt']
    print(f'Total records in sensor_data: {total_cnt}')
    
    # 3. Records by device
    cur.execute('SELECT device, COUNT(*) as cnt, MIN(created_at) as min_t, MAX(created_at) as max_t FROM sensor_data GROUP BY device')
    dev_rows = cur.fetchall()
    print('\n--- Records by Device ---')
    for r in dev_rows:
        print(f"  Device: {r['device']} | Count: {r['cnt']} | {r['min_t']} ~ {r['max_t']}")
        
    # 4. Records by run_id (top 30 latest)
    cur.execute('''
        SELECT run_id, device, COUNT(*) as cnt, 
               MIN(timestamp_str) as start_ts, MAX(timestamp_str) as end_ts,
               MIN(created_at) as start_created, MAX(created_at) as end_created,
               ROUND(MIN(temperature),1) as min_temp, ROUND(MAX(temperature),1) as max_temp,
               ROUND(MIN(humidity),1) as min_humi, ROUND(MAX(humidity),1) as max_humi,
               ROUND(MAX(g_force),2) as max_g,
               COUNT(CASE WHEN lat != 0 AND lat IS NOT NULL THEN 1 END) as gps_cnt
        FROM sensor_data 
        GROUP BY run_id, device 
        ORDER BY start_created DESC 
        LIMIT 30
    ''')
    runs = cur.fetchall()
    print('\n--- Recent 30 Sessions (run_id) ---')
    for r in runs:
        print(f"  [{r['run_id']}] dev={r['device']} | cnt={r['cnt']:4d} (GPS:{r['gps_cnt']:4d}) | created: {r['start_created']} ~ {r['end_created']} | temp:{r['min_temp']}~{r['max_temp']}C | humi:{r['min_humi']}~{r['max_humi']}% | maxG:{r['max_g']}G")

    # 5. Check today's records (2026-10-12)
    cur.execute('''
        SELECT COUNT(*) as cnt, 
               MIN(created_at) as min_t, MAX(created_at) as max_t,
               COUNT(DISTINCT run_id) as run_cnt,
               COUNT(DISTINCT device) as dev_cnt
        FROM sensor_data 
        WHERE created_at >= '2026-10-12 00:00:00'
    ''')
    today_stat = cur.fetchone()
    print(f"\n--- Today's Statistics (2026-10-12) ---")
    print(f"  Total records today: {today_stat['cnt']} | Runs: {today_stat['run_cnt']} | Devices: {today_stat['dev_cnt']} | Range: {today_stat['min_t']} ~ {today_stat['max_t']}")

    # 6. Today records breakdown by run_id
    cur.execute('''
        SELECT run_id, device, COUNT(*) as cnt,
               MIN(created_at) as min_t, MAX(created_at) as max_t,
               ROUND(MIN(temperature),1) as min_t_val, ROUND(MAX(temperature),1) as max_t_val,
               ROUND(MIN(humidity),1) as min_h_val, ROUND(MAX(humidity),1) as max_h_val,
               COUNT(CASE WHEN lat != 0 AND lat IS NOT NULL THEN 1 END) as gps_cnt,
               COUNT(CASE WHEN status LIKE '%대기%' OR status LIKE '%실내%' THEN 1 END) as wait_cnt
        FROM sensor_data
        WHERE created_at >= '2026-10-12 00:00:00'
        GROUP BY run_id, device
        ORDER BY min_t DESC
    ''')
    today_runs = cur.fetchall()
    print(f"\n--- Today's Run breakdown ---")
    for r in today_runs:
        print(f"  run_id='{r['run_id']}' | dev={r['device']} | cnt={r['cnt']} | GPS={r['gps_cnt']} | wait={r['wait_cnt']} | {r['min_t']}~{r['max_t']} | temp:{r['min_t_val']}~{r['max_t_val']} | humi:{r['min_h_val']}~{r['max_h_val']}")
