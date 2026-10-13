import toml
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']
conn = pymysql.connect(host=cfg['MYSQL_HOST'], port=cfg.get('MYSQL_PORT', 3306), user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'], cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT run_id, COUNT(*) as cnt 
        FROM sensor_data 
        WHERE run_id IS NOT NULL 
        GROUP BY run_id 
        HAVING COUNT(*) >= 10 
        ORDER BY MAX(id) DESC
    """)
    rows = cursor.fetchall()
    print("=" * 60)
    print("🎯 [대시보드 세션 드롭다운에 노출될 최종 목록]")
    print("=" * 60)
    print(" 0. 실시간 주행 (현재 실험)")
    for idx, r in enumerate(rows, 1):
        tag = ""
        rid = r['run_id']
        if "departure" in rid:
            tag = "🌟 [오늘 아침 갈 때: 전주->대전 89km]"
        elif "return" in rid:
            tag = "🌟 [오늘 낮 올 때: 대전->전주 85km]"
        elif "1001" in rid:
            tag = "🧪 [어제 10/01 테스트 데이터]"
        else:
            tag = "📦 [과거 데이터]"
        print(f" {idx:>2d}. {rid:<32s} ({r['cnt']:>5,d}건) {tag}")
    print("=" * 60)

conn.close()
