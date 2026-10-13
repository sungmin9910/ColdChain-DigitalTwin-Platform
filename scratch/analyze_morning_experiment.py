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

print("=" * 60)
print("  2026-10-02 (오늘 아침) 주행 실험 데이터 상세 분석")
print("=" * 60)

with conn.cursor() as cursor:
    # 1. 오늘 날짜의 run_id 목록 및 집계
    cursor.execute("""
        SELECT 
            run_id,
            COUNT(*) as total_packets,
            SUM(CASE WHEN lat != 0.0 AND lng != 0.0 THEN 1 ELSE 0 END) as valid_gps_cnt,
            MIN(created_at) as min_utc,
            MAX(created_at) as max_utc,
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            AVG(temperature) as avg_temp,
            MIN(humidity) as min_hum,
            MAX(humidity) as max_hum,
            AVG(humidity) as avg_hum,
            MAX(g_force) as max_shock,
            AVG(g_force) as avg_shock,
            MAX(speed) as max_speed,
            AVG(speed) as avg_speed
        FROM sensor_data
        WHERE DATE(created_at) = '2026-10-02'
        GROUP BY run_id
        ORDER BY min_utc ASC
    """)
    runs = cursor.fetchall()
    
    print("\n[1] 오늘(2026-10-02) 수집된 실험 세션(run_id) 목록")
    print("-" * 60)
    for r in runs:
        # UTC to KST (+9 hours)
        start_kst = r['min_utc'] + timedelta(hours=9)
        end_kst = r['max_utc'] + timedelta(hours=9)
        duration_min = (r['max_utc'] - r['min_utc']).total_seconds() / 60.0
        gps_ratio = (r['valid_gps_cnt'] / r['total_packets']) * 100 if r['total_packets'] > 0 else 0
        
        total_pkts = int(r['total_packets'])
        valid_gps = int(r['valid_gps_cnt']) if r['valid_gps_cnt'] is not None else 0
        gps_ratio = (valid_gps / total_pkts) * 100 if total_pkts > 0 else 0
        
        print(f"🚗 세션명: {r['run_id']}")
        print(f"   • 시작 시각 (KST): {start_kst.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   • 종료 시각 (KST): {end_kst.strftime('%Y-%m-%d %H:%M:%S')} (총 {duration_min:.1f}분 주행)")
        print(f"   • 수집 패킷: {total_pkts}개 (GPS 유효: {valid_gps}개, 성공률: {gps_ratio:.1f}%)")
        print(f"   • 온도: {float(r['min_temp']):.1f}°C ~ {float(r['max_temp']):.1f}°C (평균: {float(r['avg_temp']):.1f}°C)")
        print(f"   • 습도: {float(r['min_hum']):.1f}% ~ {float(r['max_hum']):.1f}% (평균: {float(r['avg_hum']):.1f}%)")
        print(f"   • 충격량(G): 평균 {float(r['avg_shock']):.2f}G / 최대 {float(r['max_shock']):.2f}G")
        print(f"   • 주행속도: 평균 {float(r['avg_speed']):.1f} km/h / 최고 {float(r['max_speed']):.1f} km/h")
        print("-" * 60)

    # 2. 메인 주행 세션 (run_20261002_012518) 데이터 심층 분석
    main_run = 'run_20261002_012518'
    cursor.execute(f"""
        SELECT id, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng
        FROM sensor_data
        WHERE run_id = '{main_run}'
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)
    
    if not df.empty:
        df['kst_time'] = pd.to_datetime(df['created_at']) + pd.Timedelta(hours=9)
        valid_gps = df[(df['lat'] != 0.0) & (df['lng'] != 0.0)]
        
        print(f"\n[2] 메인 주행 세션 ('{main_run}') 심층 경로 및 품질 분석")
        print("-" * 60)
        print(f"• 전체 수집 건수: {len(df)} 건")
        print(f"• 유효 GPS 위치 수집: {len(valid_gps)} 건 ({len(valid_gps)/len(df)*100:.1f}%)")
        
        if not valid_gps.empty:
            print(f"• 위도 범위: {valid_gps['lat'].min():.6f} ~ {valid_gps['lat'].max():.6f}")
            print(f"• 경도 범위: {valid_gps['lng'].min():.6f} ~ {valid_gps['lng'].max():.6f}")
            
            # 주행 구간별 샘플링 (시작, 25%, 50%, 75%, 종료)
            print("\n  📍 주행 경로 주요 타임라인 (KST):")
            sample_indices = [0, len(valid_gps)//4, len(valid_gps)//2, (len(valid_gps)*3)//4, len(valid_gps)-1]
            for idx in sample_indices:
                pt = valid_gps.iloc[idx]
                print(f"    - [{pt['kst_time'].strftime('%H:%M:%S')}] 좌표: ({pt['lat']:.5f}, {pt['lng']:.5f}) | "
                      f"속도: {pt['speed']:4.1f}km/h | 온도: {pt['temperature']:4.1f}°C | 충격: {pt['g_force']:4.2f}G")
                
        # 충격(Shock/Vibration) 이벤트 감지 (2.0G 이상 구간)
        shocks = df[df['g_force'] >= 2.0]
        print(f"\n• 고충격(2.0G 이상) 감지 건수: {len(shocks)} 건")
        if not shocks.empty:
            for _, s in shocks.head(5).iterrows():
                print(f"    ⚠️ [{s['kst_time'].strftime('%H:%M:%S')}] 충격: {s['g_force']:.2f}G | 속도: {s['speed']:.1f}km/h | 위치: ({s['lat']:.5f}, {s['lng']:.5f})")

    # 3. gps_log 및 sensor_logs 테이블 확인
    print("\n[3] 타 테이블 오늘자 데이터 기록 확인")
    print("-" * 60)
    for tbl in ['gps_log', 'sensor_logs', 'qr']:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {tbl} WHERE DATE(created_at) = '2026-10-02'")
        res = cursor.fetchone()
        print(f"• {tbl:<15s}: 오늘 기록 {res['cnt']} 건")

conn.close()
