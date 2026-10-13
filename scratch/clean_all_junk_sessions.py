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

print("=" * 70)
print("  실내 0.0 및 과거 찌꺼기 세션 백업 및 완전 정리")
print("=" * 70)

def json_serial(obj):
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# 유지할 4대 핵심 세션
keep_sessions = [
    'run_20261002_080002_departure',
    'run_20261002_103710_return',
    'run_20261001_065739',
    'korea_30km_test'
]

with conn.cursor() as c:
    # 삭제 대상 조회
    format_strings = ','.join(['%s'] * len(keep_sessions))
    c.execute(f"""
        SELECT run_id, COUNT(*) as cnt 
        FROM sensor_data 
        WHERE run_id NOT IN ({format_strings}) OR run_id IS NULL 
        GROUP BY run_id
    """, tuple(keep_sessions))
    delete_targets = c.fetchall()
    
    del_ids = [r['run_id'] for r in delete_targets if r['run_id'] is not None]
    total_del_cnt = sum(r['cnt'] for r in delete_targets)
    
    print(f"• 삭제 대상 세션 ({len(del_ids)}개 세션, 총 {total_del_cnt}건):")
    for r in delete_targets:
        print(f"   - {str(r['run_id']):<30s} : {r['cnt']}건")
        
    if del_ids:
        # 백업
        del_placeholders = ','.join(['%s'] * len(del_ids))
        c.execute(f"SELECT * FROM sensor_data WHERE run_id IN ({del_placeholders})", tuple(del_ids))
        backup_data = c.fetchall()
        with open('scratch/backup_indoor_junk_sessions.json', 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=json_serial)
        print(f"✅ 총 {len(backup_data)}건의 찌꺼기 레코드를 'scratch/backup_indoor_junk_sessions.json'에 백업 완료.")
        
        # 삭제
        c.execute(f"DELETE FROM sensor_data WHERE run_id IN ({del_placeholders})", tuple(del_ids))
        # 혹시 NULL run_id도 삭제
        c.execute("DELETE FROM sensor_data WHERE run_id IS NULL OR run_id = ''")
        conn.commit()
        print(f"✅ 불필요한 찌꺼기 세션 삭제 완료.")

    # 최종 남은 세션 확인
    c.execute("""
        SELECT run_id, COUNT(*) as cnt, MIN(created_at) as min_t, MAX(created_at) as max_t 
        FROM sensor_data 
        GROUP BY run_id 
        ORDER BY MAX(id) DESC
    """)
    final_remain = c.fetchall()
    print("\n" + "=" * 70)
    print(f"🎯 [최종 유지되는 유의미한 주행 세션 목록 (총 {len(final_remain)}개)]")
    print("=" * 70)
    for idx, r in enumerate(final_remain, 1):
        print(f"[{idx}] {r['run_id']:<32s} : {r['cnt']:>5,d} 건")

conn.close()
