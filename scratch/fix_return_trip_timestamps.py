import pymysql, toml
secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']
conn = pymysql.connect(host=cfg['MYSQL_HOST'], user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'], port=cfg.get('MYSQL_PORT', 3306), charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as cur:
    cur.execute("SELECT id, timestamp_str, created_at FROM sensor_data WHERE run_id = 'run_20261002_103710_return' AND (timestamp_str = '2026-10-01 00:00:00' OR timestamp_str LIKE '%00:00:00')")
    rows = cur.fetchall()
    print("Found rows to fix:", rows)
    
    # We update id 921, 922, 923 with their KST time (created_at + 9h)
    for r in rows:
        rid = r['id']
        # created_at is 2026-10-02 01:37:xx UTC -> 10:37:xx KST
        kst_dt = r['created_at']
        from datetime import timedelta
        new_ts = (kst_dt + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Updating id {rid} to {new_ts}")
        cur.execute("UPDATE sensor_data SET timestamp_str = %s WHERE id = %s", (new_ts, rid))
    
    conn.commit()
    print("Successfully updated database records!")
