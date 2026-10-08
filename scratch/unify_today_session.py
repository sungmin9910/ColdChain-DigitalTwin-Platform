import os, pymysql, toml

sec = toml.load("Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml")
db_conf = sec.get("MySQL", {})
conn = pymysql.connect(
    host=db_conf["MYSQL_HOST"],
    port=db_conf.get("MYSQL_PORT", 3306),
    user=db_conf["MYSQL_USER"],
    password=db_conf["MYSQL_PASSWORD"],
    database=db_conf["MYSQL_DATABASE"],
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

TARGET_RUN_ID = "주행_2026-10-08_19시01분"

try:
    with conn.cursor() as cur:
        # Check current state of today's rows
        cur.execute("SELECT COUNT(*) as cnt, MIN(timestamp_str) as min_ts, MAX(timestamp_str) as max_ts FROM sensor_data WHERE id >= 4217 AND id <= 4360")
        stat = cur.fetchone()
        print(f"Found {stat['cnt']} rows from today: {stat['min_ts']} ~ {stat['max_ts']}")

        # 1. Update id 4218 and 4219 uninitialized timestamps (were 2026-10-01 00:00:00) to 2026-10-08 18:28:25 and 18:28:35
        cur.execute("""
            UPDATE sensor_data 
            SET timestamp_str = '2026-10-08 18:28:25' 
            WHERE id = 4218 AND timestamp_str = '2026-10-01 00:00:00'
        """)
        cur.execute("""
            UPDATE sensor_data 
            SET timestamp_str = '2026-10-08 18:28:35' 
            WHERE id = 4219 AND timestamp_str = '2026-10-01 00:00:00'
        """)
        print(f"Corrected uninitialized dummy timestamps for id 4218, 4219.")

        # 2. Unify all 144 records into TARGET_RUN_ID
        cur.execute("""
            UPDATE sensor_data 
            SET run_id = %s 
            WHERE id >= 4217 AND id <= 4360
        """, (TARGET_RUN_ID,))
        updated_count = cur.rowcount
        print(f"Updated {updated_count} records to run_id: '{TARGET_RUN_ID}'")

        conn.commit()
        print("Successfully committed DB update.")

        # Verify
        cur.execute("""
            SELECT run_id, COUNT(*) as cnt, MIN(timestamp_str) as min_ts, MAX(timestamp_str) as max_ts, MAX(speed) as max_spd
            FROM sensor_data
            WHERE run_id = %s
            GROUP BY run_id
        """, (TARGET_RUN_ID,))
        res = cur.fetchone()
        print(f"\nVerification Result:")
        print(f"  run_id: {res['run_id']}")
        print(f"  count: {res['cnt']}")
        print(f"  timestamp range: {res['min_ts']} ~ {res['max_ts']}")
        print(f"  max speed: {res['max_spd']} km/h")

finally:
    conn.close()
