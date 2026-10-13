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

with conn.cursor() as c:
    c.execute('SELECT run_id, COUNT(*) as cnt FROM sensor_data GROUP BY run_id ORDER BY cnt ASC')
    rows = c.fetchall()
    less_than_10 = [r for r in rows if r['cnt'] < 10]
    gte_10 = [r for r in rows if r['cnt'] >= 10]
    
    print("=== 10건 미만 세션 (삭제 대상) ===")
    for r in less_than_10:
        print(f"• {str(r['run_id']):<30s} : {r['cnt']:>2d}건")
    print(f"총 {len(less_than_10)}개 세션, 총 레코드: {sum(r['cnt'] for r in less_than_10)}건\n")
    
    print("=== 10건 이상 세션 (보존/유지 대상) ===")
    for r in gte_10:
        print(f"• {str(r['run_id']):<30s} : {r['cnt']:>4d}건")
    print(f"총 {len(gte_10)}개 세션, 총 레코드: {sum(r['cnt'] for r in gte_10)}건")

conn.close()
