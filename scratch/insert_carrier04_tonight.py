import json
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load today's 395 records
with open('scratch/carrier_dump_20261018.jsonl', 'r', encoding='utf-8') as f:
    all_recs = [json.loads(line) for line in f]

today_recs = [r for r in all_recs if r.get('timestamp_str', '').startswith('2026-10-18')]
print(f"Loaded {len(today_recs)} records for 2026-10-18 from LittleFS dump.")

target_run_id = "truck04_주행_2026-10-18_20시24분"
target_device = "carrier-c6-04"

# 2. Connect to RDS MySQL
conn = pymysql.connect(
    host='labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com',
    port=3306,
    user='admin',
    password='12345678',
    database='lab225',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # Check existing fragmented records
        cursor.execute("""
            SELECT id, run_id, timestamp_str, device, speed, lat, lng 
            FROM sensor_data 
            WHERE device = %s AND timestamp_str >= '2026-10-18 20:00:00'
        """, (target_device,))
        old_rows = cursor.fetchall()
        print(f"Found {len(old_rows)} fragmented rows in DB from tonight.")
        
        # Backup old rows
        with open('scratch/backup_tonight_fragments.json', 'w', encoding='utf-8') as f:
            json.dump(old_rows, f, ensure_ascii=False, indent=2, default=str)
        print("Backed up old fragments to scratch/backup_tonight_fragments.json")

        # Delete old fragmented rows
        if old_rows:
            cursor.execute("""
                DELETE FROM sensor_data 
                WHERE device = %s AND timestamp_str >= '2026-10-18 20:00:00'
            """, (target_device,))
            print(f"Deleted {cursor.rowcount} old fragmented rows.")

        # Insert clean 395 records
        insert_sql = """
            INSERT INTO sensor_data 
            (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """

        inserted_count = 0
        for r in today_recs:
            status_val = r.get('status', '정상')
            if not status_val or '' in status_val:
                lat = float(r.get('lat', 0.0))
                lng = float(r.get('lng', 0.0))
                if lat != 0.0 and lng != 0.0:
                    status_val = f"정상 [GPS {r.get('sats', 0)}]"
                else:
                    status_val = "대기 [실내]"

            val = (
                target_device,
                r.get('timestamp_str', ''),
                float(r.get('temperature', 0.0)),
                float(r.get('humidity', 0.0)),
                float(r.get('lux', 0.0)),
                float(r.get('g_force', 1.0)),
                float(r.get('speed', 0.0)),
                float(r.get('lat', 0.0)),
                float(r.get('lng', 0.0)),
                status_val,
                target_run_id
            )
            cursor.execute(insert_sql, val)
            inserted_count += 1

        conn.commit()
        print(f"Successfully inserted {inserted_count} clean records with run_id='{target_run_id}'!")

        # Verify
        cursor.execute("""
            SELECT run_id, COUNT(*) as cnt, MIN(timestamp_str) as min_ts, MAX(timestamp_str) as max_ts, MAX(speed) as max_spd
            FROM sensor_data 
            WHERE run_id = %s
            GROUP BY run_id
        """, (target_run_id,))
        verify_row = cursor.fetchone()
        print(f"Verification result: {verify_row}")

finally:
    conn.close()
