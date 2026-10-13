import toml
import pymysql
import sys
import json
from datetime import datetime
import pandas as pd

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

def json_serial(obj):
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

print("=" * 80)
print("  🧹 AWS RDS sensor_data 데이터베이스 정제 및 단일화 작업")
print("=" * 80)

with conn.cursor() as c:
    # 1. 오늘(10-11) 세션의 실내 방치 레코드 (id > 4448) 삭제
    c.execute("SELECT COUNT(*) as cnt FROM sensor_data WHERE run_id = '주행_2026-10-11_09시38분' AND id > 4448")
    indoor_cnt = c.fetchone()['cnt']
    print(f"1. 오늘(10-11) 연구실 실내 방치 찌꺼기 레코드: {indoor_cnt}건")
    if indoor_cnt > 0:
        c.execute("DELETE FROM sensor_data WHERE run_id = '주행_2026-10-11_09시38분' AND id > 4448")
        print(f"   -> {indoor_cnt}건 삭제 완료! (실제 주행 77건만 남김)")

    # 2. 극소수 자잘한 테스트 찌꺼기 세션 백업 및 정리 (건수 <= 20건인 비정상 조각들)
    c.execute("""
        SELECT run_id, COUNT(*) as cnt 
        FROM sensor_data 
        GROUP BY run_id 
        HAVING COUNT(*) <= 20
    """)
    small_runs = c.fetchall()
    small_run_ids = [r['run_id'] for r in small_runs if r['run_id']]
    small_desc = [f"{r['run_id']} ({r['cnt']}건)" for r in small_runs]
    print(f"\n2. 극소수 조각 세션 (<= 20건): {small_desc}")
    
    if small_run_ids:
        placeholders = ','.join(['%s'] * len(small_run_ids))
        c.execute(f"SELECT * FROM sensor_data WHERE run_id IN ({placeholders})", tuple(small_run_ids))
        small_rows = c.fetchall()
        with open('scratch/backup_small_fragments_20261011.json', 'w', encoding='utf-8') as f:
            json.dump(small_rows, f, ensure_ascii=False, indent=2, default=json_serial)
        print(f"   -> 총 {len(small_rows)}건 백업 완료 ('scratch/backup_small_fragments_20261011.json')")
        c.execute(f"DELETE FROM sensor_data WHERE run_id IN ({placeholders})", tuple(small_run_ids))
        print(f"   -> 조각 세션 삭제 완료.")

    conn.commit()

    # 3. 최종 정제 후 남은 세션 확인
    c.execute("""
        SELECT 
            run_id, 
            COUNT(*) as total_cnt,
            SUM(CASE WHEN lat != 0.0 AND lng != 0.0 THEN 1 ELSE 0 END) as valid_gps,
            MIN(timestamp_str) as start_ts,
            MAX(timestamp_str) as end_ts,
            MAX(speed) as max_spd,
            MIN(temperature) as min_t,
            MAX(temperature) as max_t,
            MIN(id) as min_id
        FROM sensor_data
        GROUP BY run_id
        ORDER BY min_id ASC
    """)
    final_rows = c.fetchall()

print("\n" + "=" * 100)
print("🎯 [정제 완료: AWS RDS sensor_data 활성 세션 목록 (총 {}개)]".format(len(final_rows)))
print("=" * 100)
print(f"{'No':<3} | {'Run ID':<32} | {'Total':<6} | {'GPS':<5} | {'MaxSpd':<6} | {'Period':<35}")
print("-" * 100)
for idx, r in enumerate(final_rows, 1):
    p = f"{str(r['start_ts'])[:16]} ~ {str(r['end_ts'])[:16]}"
    print(f"{idx:<3} | {str(r['run_id']):<32} | {r['total_cnt']:<6} | {r['valid_gps']:<5} | {float(r['max_spd'] or 0):<6.1f} | {p}")
print("=" * 100)

conn.close()
