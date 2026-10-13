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

print("=" * 80)
print("  오늘 아침 '갈 때' (07:30 ~ 10:30 KST) 전체 수집 레코드 타임라인")
print("=" * 80)

# UTC 기준 2026-10-01 22:30:00 ~ 2026-10-02 01:30:00
with conn.cursor() as cursor:
    cursor.execute("""
        SELECT id, run_id, timestamp_str, created_at, temperature, humidity, g_force, speed, lat, lng
        FROM sensor_data
        WHERE created_at BETWEEN '2026-10-01 22:30:00' AND '2026-10-02 01:30:00'
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

df = pd.DataFrame(rows)
if df.empty:
    print("해당 시간대에 데이터가 없습니다.")
else:
    df['kst_time'] = pd.to_datetime(df['created_at']) + pd.Timedelta(hours=9)
    print(f"• 총 수집 건수: {len(df)} 건")
    print(f"• 세션(run_id) 분포:")
    for run, g in df.groupby('run_id'):
        print(f"   - {run:<24s}: {len(g):>3d}건 (KST {g['kst_time'].min().strftime('%H:%M:%S')} ~ {g['kst_time'].max().strftime('%H:%M:%S')})")

    print("\n📍 전체 수집 패킷 타임라인:")
    for _, r in df.iterrows():
        print(f"ID {r['id']:>4d} | {r['kst_time'].strftime('%H:%M:%S')} | {r['run_id']:<22s} | "
              f"GPS:({r['lat']:.5f}, {r['lng']:.5f}) | 속도: {r['speed']:4.1f}km/h | 충격: {r['g_force']:.2f}G | 온습도: {r['temperature']:.1f}°C/{r['humidity']:.1f}%")

conn.close()
