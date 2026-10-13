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

with conn.cursor() as c:
    c.execute("""
        SELECT 
            run_id,
            COUNT(*) as cnt,
            SUM(CASE WHEN lat != 0.0 AND lng != 0.0 THEN 1 ELSE 0 END) as valid_gps,
            MIN(created_at) as min_time,
            MAX(created_at) as max_time
        FROM sensor_data
        WHERE run_id IS NOT NULL
        GROUP BY run_id
        ORDER BY MAX(id) DESC
        LIMIT 20
    """)
    rows = c.fetchall()
    print("=== 최신 20개 세션 목록 ===")
    for idx, r in enumerate(rows, 1):
        vg = int(r['valid_gps'] or 0)
        cnt = int(r['cnt'])
        st = r['min_time'] + timedelta(hours=9) if r['min_time'] else None
        et = r['max_time'] + timedelta(hours=9) if r['max_time'] else None
        st_s = st.strftime('%m-%d %H:%M') if st else 'N/A'
        et_s = et.strftime('%H:%M') if et else 'N/A'
        print(f"[{idx:>2d}] {str(r['run_id']):<30s} | {cnt:>4d}건 (유효GPS:{vg:>4d}) | {st_s} ~ {et_s}")

conn.close()
