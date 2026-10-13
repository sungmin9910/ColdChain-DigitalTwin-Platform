import toml
import pymysql
import sys

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
print("  오늘(2026-10-02) 왕복 주행 실험 세션 최종 현황 검증")
print("=" * 70)

with conn.cursor() as c:
    c.execute("""
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
        WHERE DATE(created_at) = '2026-10-02'
        GROUP BY run_id
        ORDER BY min_time ASC
    """)
    rows = c.fetchall()
    
    for r in rows:
        vg = int(r['valid_gps']) if r['valid_gps'] is not None else 0
        cnt = int(r['cnt'])
        ratio = (vg / cnt) * 100 if cnt > 0 else 0
        
        print(f"🚗 세션명: {r['run_id']}")
        print(f"   • 총 수집 패킷: {cnt:,d} 개 (GPS 유효: {vg:,d} 개, 성공률: {ratio:.1f}%)")
        print(f"   • 운행 시각: {r['min_time']} ~ {r['max_time']}")
        print(f"   • 좌표 범위: lat({r['min_lat']:.5f} ~ {r['max_lat']:.5f}), lng({r['min_lng']:.5f} ~ {r['max_lng']:.5f})")
        print(f"   • 속도 지표: 최고 {float(r['max_speed'] or 0):.1f} km/h | 평균 {float(r['avg_speed'] or 0):.1f} km/h")
        print(f"   • 온도 범위: {float(r['min_temp'] or 0):.1f}°C ~ {float(r['max_temp'] or 0):.1f}°C")
        print(f"   • 최대 충격: {float(r['max_shock'] or 0):.2f} G")
        print("-" * 70)

conn.close()
