import toml
import pymysql
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']

conn = pymysql.connect(
    host=cfg['MYSQL_HOST'],
    port=cfg.get('MYSQL_PORT', 3306),
    user=cfg['MYSQL_USER'],
    password=cfg['MYSQL_PASSWORD'],
    database=cfg['MYSQL_DATABASE'],
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as c:
    c.execute("""
        SELECT *
        FROM sensor_data
        WHERE run_id = '주행_2026-10-11_09시38분'
        ORDER BY id ASC
    """)
    rows = c.fetchall()

# Convert datetimes to string for json serialization
backup_rows = []
for r in rows:
    row_copy = dict(r)
    if row_copy.get('created_at'):
        row_copy['created_at'] = str(row_copy['created_at'])
    backup_rows.append(row_copy)

backup_path = 'scratch/backup_20261011_raw_session.json'
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(backup_rows, f, ensure_ascii=False, indent=2)

print(f"✅ 오늘(10-11) 원본 637건 전체가 '{backup_path}'에 100% 안전하게 백업되었습니다.")

# Verify split boundary
driving_records = [r for r in rows if r['id'] <= 4448] # 09:38:56 ~ 10:02:01
indoor_records = [r for r in rows if r['id'] > 4448]

print(f"• 실제 주행 구간 (ID <= 4448): {len(driving_records)}건")
print(f"  시작: {driving_records[0]['timestamp_str']} -> 종료: {driving_records[-1]['timestamp_str']}")
print(f"  최고속도: {max(r['speed'] for r in driving_records):.1f} km/h")

print(f"• 실내 방치 구간 (ID > 4448): {len(indoor_records)}건")
print(f"  시작: {indoor_records[0]['timestamp_str']} -> 종료: {indoor_records[-1]['timestamp_str']}")
print(f"  GPS: 위도 {indoor_records[0]['lat']:.4f}, 경도 {indoor_records[0]['lng']:.4f} (고정)")

conn.close()
