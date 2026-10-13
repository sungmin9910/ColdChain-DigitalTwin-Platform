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

print("=" * 75)
print("  대시보드 세션 선택 목록 전체(run_id) 정체 및 내역 분석")
print("=" * 75)

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
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp
        FROM sensor_data
        WHERE run_id IS NOT NULL
        GROUP BY run_id
        ORDER BY MAX(id) DESC
    """)
    rows = c.fetchall()

    for idx, r in enumerate(rows, 1):
        vg = int(r['valid_gps'] or 0)
        cnt = int(r['cnt'])
        s_time = r['min_time'] + timedelta(hours=9) if r['min_time'] else None
        e_time = r['max_time'] + timedelta(hours=9) if r['max_time'] else None
        s_str = s_time.strftime('%Y-%m-%d %H:%M') if s_time else 'N/A'
        e_str = e_time.strftime('%H:%M') if e_time else 'N/A'
        
        # 정체 판별
        tag = ""
        rid = str(r['run_id'])
        if rid == "run_20261002_080002_departure":
            tag = "🌟 [오늘 아침 갈 때] 전주 -> 대전 (복원 완료)"
        elif rid == "run_20261002_012518":
            tag = "🌟 [오늘 낮 올 때] 대전 -> 전주 (메인 주행)"
        elif "20261002" in rid:
            tag = "⚠️ [오늘 주행 중 생성된 임시/분기 세션]"
        elif "20261001" in rid:
            tag = "🧪 [어제 10/01 센서/GPS 실내외 테스트 데이터]"
        elif "korea_30km_test" in rid:
            tag = "📦 [과거 30km 시뮬레이션/테스트 데이터]"
        elif "today_test" in rid:
            tag = "📦 [과거 기본값 today_test 세션]"
        elif "202607" in rid or "202608" in rid:
            tag = "📦 [과거 7~8월 프로토타입 개발/테스트 데이터]"
        else:
            tag = "📦 [기타 테스트 세션]"

        print(f"[{idx:>2d}] 세션명: {rid}")
        print(f"     분류: {tag}")
        print(f"     건수: {cnt:>4d}건 (GPS유효: {vg:>4d}건) | 일시(KST): {s_str} ~ {e_str}")
        print(f"     위치: ({r['min_lat']:.4f}~{r['max_lat']:.4f}, {r['min_lng']:.4f}~{r['max_lng']:.4f}) | 최고속도: {float(r['max_speed'] or 0):.1f}km/h")
        print("-" * 75)

conn.close()
