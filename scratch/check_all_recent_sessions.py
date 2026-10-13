import toml
import pymysql
import sys
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

print("=" * 80)
print("  2026-10-01 ~ 2026-10-02 전체 실험 세션 상세 조회")
print("=" * 80)

with conn.cursor() as c:
    c.execute("""
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
            AVG(speed) as avg_speed,
            MAX(g_force) as max_shock
        FROM sensor_data
        WHERE created_at >= '2026-09-30 00:00:00'
        GROUP BY run_id
        ORDER BY min_utc ASC
    """)
    rows = c.fetchall()
    
    for r in rows:
        sk = r['min_utc'] + timedelta(hours=9) if r['min_utc'] else None
        ek = r['max_utc'] + timedelta(hours=9) if r['max_utc'] else None
        s_str = sk.strftime('%Y-%m-%d %H:%M:%S') if sk else 'N/A'
        e_str = ek.strftime('%Y-%m-%d %H:%M:%S') if ek else 'N/A'
        valid = int(r['valid_gps'] or 0)
        cnt = int(r['cnt'])
        
        print(f"세션: {str(r['run_id']):<24s}")
        print(f"  • 건수: {cnt}건 (GPS 유효: {valid}건 / 비율: {valid/cnt*100:.1f}%)")
        print(f"  • KST: {s_str} ~ {e_str}")
        print(f"  • GPS: ({r['min_lat']:.4f} ~ {r['max_lat']:.4f}, {r['min_lng']:.4f} ~ {r['max_lng']:.4f})")
        print(f"  • 속도: 최고 {float(r['max_speed'] or 0):.1f} km/h | 평균 {float(r['avg_speed'] or 0):.1f} km/h | 최대충격: {float(r['max_shock'] or 0):.2f}G")
        print("-" * 80)

conn.close()
