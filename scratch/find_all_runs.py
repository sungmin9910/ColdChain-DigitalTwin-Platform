import toml
import pymysql
import sys
import pandas as pd
from datetime import timedelta

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
print("  전체 세션(run_id) 및 주행 실험 이력 검색")
print("=" * 70)

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT 
            run_id,
            COUNT(*) as cnt,
            SUM(CASE WHEN lat != 0.0 AND lng != 0.0 THEN 1 ELSE 0 END) as valid_gps,
            MIN(created_at) as min_utc,
            MAX(created_at) as max_utc,
            MIN(lat) as min_lat,
            MAX(lat) as max_lat,
            MIN(lng) as min_lng,
            MAX(lng) as max_lng,
            MAX(speed) as max_speed,
            AVG(speed) as avg_speed
        FROM sensor_data
        GROUP BY run_id
        ORDER BY min_utc DESC
    """)
    runs = cursor.fetchall()
    
    print(f"총 {len(runs)}개의 run_id 발견됨:\n")
    for r in runs:
        start_kst = r['min_utc'] + timedelta(hours=9) if r['min_utc'] else None
        end_kst = r['max_utc'] + timedelta(hours=9) if r['max_utc'] else None
        s_kst_str = start_kst.strftime('%m-%d %H:%M:%S') if start_kst else 'N/A'
        e_kst_str = end_kst.strftime('%m-%d %H:%M:%S') if end_kst else 'N/A'
        valid = int(r['valid_gps']) if r['valid_gps'] else 0
        total = int(r['cnt'])
        
        print(f"• run_id: {str(r['run_id']):<24s} | {total:>4d}건 (유효GPS: {valid:>4d}건)")
        print(f"  시각: {s_kst_str} ~ {e_kst_str} (KST)")
        print(f"  좌표범위: lat({r['min_lat']:.4f} ~ {r['max_lat']:.4f}), lng({r['min_lng']:.4f} ~ {r['max_lng']:.4f})")
        print(f"  속도: 최고 {float(r['max_speed'] or 0):.1f} km/h | 평균 {float(r['avg_speed'] or 0):.1f} km/h")
        print("-" * 70)

    # 혹시 NULL run_id가 있는지 확인
    cursor.execute("""
        SELECT COUNT(*) as cnt, MIN(created_at) as min_utc, MAX(created_at) as max_utc 
        FROM sensor_data 
        WHERE run_id IS NULL OR run_id = ''
    """)
    null_run = cursor.fetchone()
    if null_run and null_run['cnt'] > 0:
        print(f"\n[주의] run_id가 없거나 빈 문자열인 레코드: {null_run['cnt']}건")
        print(f"  기간: {null_run['min_utc']} ~ {null_run['max_utc']}")

    # gps_log 테이블 확인 (혹시 다른 테이블에 저장되었는지)
    cursor.execute("""
        SELECT 
            device_id, 
            COUNT(*) as cnt, 
            MIN(recorded_at) as min_time, 
            MAX(recorded_at) as max_time,
            MIN(latitude) as min_lat,
            MAX(latitude) as max_lat
        FROM gps_log
        GROUP BY device_id
    """)
    gps_logs = cursor.fetchall()
    print("\n[gps_log 테이블]")
    for g in gps_logs:
        print(f"  • device: {g['device_id']} | {g['cnt']}건 | {g['min_time']} ~ {g['max_time']} | lat: {g['min_lat']} ~ {g['max_lat']}")

    # sensor_logs 테이블 확인
    cursor.execute("""
        SELECT 
            device_id, 
            COUNT(*) as cnt, 
            MIN(recorded_at) as min_time, 
            MAX(recorded_at) as max_time,
            MIN(latitude) as min_lat,
            MAX(latitude) as max_lat
        FROM sensor_logs
        GROUP BY device_id
    """)
    sensor_logs = cursor.fetchall()
    print("\n[sensor_logs 테이블]")
    for s in sensor_logs:
        print(f"  • device: {s['device_id']} | {s['cnt']}건 | {s['min_time']} ~ {s['max_time']} | lat: {s['min_lat']} ~ {s['max_lat']}")

conn.close()
