import toml
import pymysql
import sys
import pandas as pd
import numpy as np

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

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT id, run_id, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng
        FROM sensor_data
        WHERE created_at BETWEEN '2026-10-01 22:30:00' AND '2026-10-02 01:05:00'
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

df = pd.DataFrame(rows)
df['kst_time'] = pd.to_datetime(df['created_at']) + pd.Timedelta(hours=9)
valid = df[(df['lat'] != 0.0) & (df['lng'] != 0.0)]

print("=" * 65)
print("  갈 때 (전주 -> 대전) 주행 데이터 세부 통계")
print("=" * 65)
print(f"• 데이터 수집 구간 (KST): {df['kst_time'].iloc[0].strftime('%H:%M:%S')} ~ {df['kst_time'].iloc[-1].strftime('%H:%M:%S')}")
print(f"• 총 수집 패킷 수: {len(df)} 건")
print(f"• GPS 유효 패킷 수: {len(valid)} 건 ({len(valid)/len(df)*100:.1f}%)")
print(f"• 최고 속도: {valid['speed'].max():.1f} km/h")
print(f"• 평균 속도 (주행중): {valid[valid['speed'] > 5]['speed'].mean():.1f} km/h")
print(f"• 온도 범위: {df['temperature'].min():.1f}°C ~ {df['temperature'].max():.1f}°C (평균: {df['temperature'].mean():.1f}°C)")
print(f"• 습도 범위: {df['humidity'].min():.1f}% ~ {df['humidity'].max():.1f}% (평균: {df['humidity'].mean():.1f}%)")
print(f"• 최대 충격량: {df['g_force'].max():.2f} G (ID {df.loc[df['g_force'].idxmax()]['id']}, 시각 {df.loc[df['g_force'].idxmax()]['kst_time'].strftime('%H:%M:%S')})")
print(f"• 2.0G 이상 충격 건수: {len(df[df['g_force'] >= 2.0])} 건")

print("\n📍 출발지 ~ 도착지 확인:")
print(f"• 출발: {valid.iloc[0]['kst_time'].strftime('%H:%M:%S')} | ({valid.iloc[0]['lat']:.5f}, {valid.iloc[0]['lng']:.5f}) - 전주 전북대 인근")
print(f"• 마지막: {valid.iloc[-1]['kst_time'].strftime('%H:%M:%S')} | ({valid.iloc[-1]['lat']:.5f}, {valid.iloc[-1]['lng']:.5f}) - 대전 도착 지점")
