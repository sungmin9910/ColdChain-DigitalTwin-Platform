import toml
import pymysql
import json
from datetime import datetime

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

backup_file = 'scratch/backup_20261012_sessions.json'

with conn.cursor() as cur:
    # 1. Backup all records for today (2026-10-12)
    cur.execute("""
        SELECT * FROM sensor_data 
        WHERE run_id IN ('주행_2026-10-12_12시08분', '주행_2026-10-12_12시09분', '주행_2026-10-12_17시06분')
           OR device = 'carrier-c6-02'
    """)
    rows = cur.fetchall()
    print(f"Backing up {len(rows)} rows to {backup_file}...")
    
    # JSON serialize datetime
    def default_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Type {type(o)} not serializable")

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2, default=default_serializer)
    print("Backup completed successfully!")

    # 2. Delete the 100% duplicate scrap session '주행_2026-10-12_12시09분' (37 records)
    cur.execute("DELETE FROM sensor_data WHERE run_id = '주행_2026-10-12_12시09분'")
    deleted_dup_cnt = cur.rowcount
    print(f"Deleted duplicate 12:09 session records: {deleted_dup_cnt} rows.")

    # 3. Relabel carrier-c6-02 records in 12:08 to 'truck02_bench_20261012'
    cur.execute("""
        UPDATE sensor_data 
        SET run_id = 'truck02_bench_20261012'
        WHERE run_id = '주행_2026-10-12_12시08분' AND device = 'carrier-c6-02'
    """)
    updated_c602_cnt = cur.rowcount
    print(f"Relabeled carrier-c6-02 records to 'truck02_bench_20261012': {updated_c602_cnt} rows.")

    # 4. Clean up 6 uninitialized sensor dropouts (temp=0.0 AND humi=0.0) from carrier-c6-01's 12:08 run
    cur.execute("""
        DELETE FROM sensor_data 
        WHERE run_id = '주행_2026-10-12_12시08분' 
          AND device = 'carrier-c6-01'
          AND temperature = 0.0 
          AND humidity = 0.0
    """)
    deleted_dropouts_cnt = cur.rowcount
    print(f"Cleaned uninitialized sensor dropouts (0,0) in 12:08: {deleted_dropouts_cnt} rows.")

    conn.commit()
    print("Database transaction committed successfully!")

conn.close()
