import toml
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']
conn = pymysql.connect(host=cfg['MYSQL_HOST'], port=cfg.get('MYSQL_PORT', 3306), user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'], cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as c:
    c.execute("""
        SELECT 
            run_id,
            COUNT(*) as total_cnt,
            SUM(CASE WHEN lat != 0.0 AND lng != 0.0 THEN 1 ELSE 0 END) as valid_gps,
            MAX(speed) as max_speed,
            MIN(created_at) as min_time,
            MAX(created_at) as max_time
        FROM sensor_data 
        WHERE run_id IS NOT NULL 
        GROUP BY run_id 
        HAVING COUNT(*) >= 10 
        ORDER BY MAX(id) DESC
    """)
    rows = c.fetchall()
    
    print("=" * 80)
    print("  드롭다운에 남아있는 15개 세션의 실제 데이터 내용 정밀 검사")
    print("=" * 80)
    for r in rows:
        vg = int(r['valid_gps'])
        tot = int(r['total_cnt'])
        max_s = float(r['max_speed'] or 0)
        
        # 성격 분류
        desc = ""
        if "departure" in r['run_id']:
            desc = "🌟 [진짜 주행] 오늘 갈 때 (전주->대전, 89km 고속도로 완주)"
        elif "return" in r['run_id']:
            desc = "🌟 [진짜 주행] 오늘 올 때 (대전->전주, 85km 고속도로 완주)"
        elif r['run_id'] == "run_20261001_065739":
            desc = "📍 [어제 테스트] 전북대 캠퍼스 야외 GPS 수신 성공 테스트 (시속 5km)"
        elif r['run_id'] == "korea_30km_test":
            desc = "📦 [과거 데이터] 7월 30km 시뮬레이션 가상 데이터"
        elif vg == 0 and max_s == 0.0:
            desc = "❌ [가짜/실내] 위도/경도 0.0, 속도 0, 실내 책상 위에서 회로 테스트한 찌꺼기"
        else:
            desc = f"⚠️ [기타] GPS {vg}건, 속도 {max_s}km/h"
            
        print(f"• 세션: {r['run_id']:<32s}")
        print(f"  내용: {desc}")
        print(f"  건수: {tot}건 중 유효GPS: {vg}건 ({vg/tot*100:.1f}%), 최고속도: {max_s}km/h, 일시: {r['min_time']}")
        print("-" * 80)

conn.close()
