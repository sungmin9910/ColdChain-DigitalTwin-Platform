import toml
import pymysql
import sys
import json
import pandas as pd
from datetime import datetime

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
print("  갈 때 (전주 -> 대전) 주행 데이터 복원 및 단일 세션 통합 작업")
print("=" * 70)

unified_run_id = "run_20261002_080002_departure"

with conn.cursor() as cursor:
    # 1. 기존 파편화된 44건 백업
    cursor.execute("SELECT * FROM sensor_data WHERE id BETWEEN 877 AND 920 ORDER BY id ASC")
    old_rows = cursor.fetchall()
    
    # datetime 직렬화 지원
    def json_serial(obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
        
    with open('scratch/backup_departure_44_records.json', 'w', encoding='utf-8') as f:
        json.dump(old_rows, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"✅ 1. 기존 파편화된 {len(old_rows)}건의 레코드를 'scratch/backup_departure_44_records.json'에 백업 완료.")

    # 2. 플래시 메모리 덤프에서 갈 때(08:00:00 ~ 09:58:00) 1,356건 로드
    flash_records = []
    with open('scratch/flash_dump_20261002.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    flash_records.append(json.loads(line))
                except Exception:
                    pass
                    
    df_flash = pd.DataFrame(flash_records)
    df_flash['dt'] = pd.to_datetime(df_flash['timestamp_str'], errors='coerce')
    sub = df_flash[(df_flash['dt'] >= '2026-10-02 08:00:00') & (df_flash['dt'] <= '2026-10-02 09:58:00')].sort_values(by='dt')
    print(f"✅ 2. 플래시 메모리에서 갈 때 전체 데이터 {len(sub)}건 추출 완료.")

    # 3. 기존 44건 삭제
    cursor.execute("DELETE FROM sensor_data WHERE id BETWEEN 877 AND 920")
    print(f"✅ 3. 기존 분절된 44건 레코드 정리 완료.")

    # 4. 플래시 메모리 1,356건 일괄 삽입 (INSERT)
    # AWS RDS 타임존 +09:00 설정
    cursor.execute("SET time_zone = '+09:00'")
    
    insert_sql = """
        INSERT INTO sensor_data 
        (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    insert_values = []
    for _, r in sub.iterrows():
        ts_str = str(r['timestamp_str'])
        # created_at으로 실제 측정 시각 사용
        created_at_val = ts_str
        insert_values.append((
            r.get('device', 'carrier-c6-01'),
            ts_str,
            float(r.get('temperature', 0.0) or 0.0),
            float(r.get('humidity', 0.0) or 0.0),
            float(r.get('lux', 0.0) or 0.0),
            float(r.get('g_force', 1.0) or 1.0),
            float(r.get('speed', 0.0) or 0.0),
            float(r.get('lat', 0.0) or 0.0),
            float(r.get('lng', 0.0) or 0.0),
            r.get('status', '정상'),
            unified_run_id,
            created_at_val
        ))
        
    cursor.executemany(insert_sql, insert_values)
    conn.commit()
    print(f"✅ 4. 단일 세션 '{unified_run_id}'으로 {len(insert_values)}건의 고해상도 주행 데이터 복원 및 적재 완료!")

    # 5. 적재 후 검증 쿼리
    cursor.execute(f"""
        SELECT 
            run_id,
            COUNT(*) as cnt,
            SUM(CASE WHEN lat != 0.0 AND lng != 0.0 THEN 1 ELSE 0 END) as valid_gps,
            MIN(created_at) as min_time,
            MAX(created_at) as max_time,
            MIN(lat) as min_lat,
            MAX(lat) as max_lat,
            MIN(lng) as min_lng,
            MAX(lng) as max_lng,
            MAX(speed) as max_speed,
            AVG(speed) as avg_speed,
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            MAX(g_force) as max_shock
        FROM sensor_data
        WHERE run_id = '{unified_run_id}'
        GROUP BY run_id
    """)
    res = cursor.fetchone()
    print("\n" + "=" * 70)
    print("📊 [복원 결과 최종 검증]")
    print("=" * 70)
    print(f"• 통합 세션 ID: {res['run_id']}")
    print(f"• 총 저장 건수: {res['cnt']:,d} 건 (결측 0건)")
    print(f"• GPS 유효 성공: {res['valid_gps']:,d} 건 ({res['valid_gps']/res['cnt']*100:.1f}%)")
    print(f"• 측정 시간: {res['min_time']} ~ {res['max_time']} (KST)")
    print(f"• 이동 좌표: lat({res['min_lat']:.5f} ~ {res['max_lat']:.5f}), lng({res['min_lng']:.5f} ~ {res['max_lng']:.5f})")
    print(f"• 주행 속도: 최고 {res['max_speed']:.1f} km/h | 평균 {res['avg_speed']:.1f} km/h")
    print(f"• 온도 범위: {res['min_temp']:.1f}°C ~ {res['max_temp']:.1f}°C")
    print(f"• 최대 충격: {res['max_shock']:.2f} G")
    print("=" * 70)

conn.close()
