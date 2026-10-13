import toml
import pymysql
import sys
import pandas as pd
import numpy as np
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

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT id, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng, run_id
        FROM sensor_data
        WHERE run_id = 'run_20261002_012518'
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

df = pd.DataFrame(rows)
df['kst_time'] = pd.to_datetime(df['created_at']) + pd.Timedelta(hours=9)
valid = df[(df['lat'] != 0.0) & (df['lng'] != 0.0)].copy()

# 누적 거리 계산
valid['prev_lat'] = valid['lat'].shift(1)
valid['prev_lng'] = valid['lng'].shift(1)
valid['dist_km'] = valid.apply(
    lambda r: haversine(r['prev_lat'], r['prev_lng'], r['lat'], r['lng']) if pd.notnull(r['prev_lat']) else 0.0,
    axis=1
)
# 이상치 필터링 (순간 10km 이상 점프는 제외)
valid['dist_km'] = valid['dist_km'].apply(lambda x: x if x < 5.0 else 0.0)
total_distance = valid['dist_km'].sum()

print("=" * 65)
print("  [오늘 아침 메인 주행 실험 세부 통계 (run_20261002_012518)]")
print("=" * 65)
print(f"• 세션 식별자: run_20261002_012518")
print(f"• 주행 시작 (KST): {df['kst_time'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')}")
print(f"• 주행 종료 (KST): {df['kst_time'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')}")
duration_sec = (df['kst_time'].iloc[-1] - df['kst_time'].iloc[0]).total_seconds()
print(f"• 총 주행 시간: {int(duration_sec // 3600)}시간 {int((duration_sec % 3600) // 60)}분 {int(duration_sec % 60)}초 ({duration_sec/60:.1f}분)")
print(f"• 총 누적 이동 거리: 약 {total_distance:.2f} km")
print(f"• 총 수집 패킷 수: {len(df)} 건")
print(f"• 유효 GPS 좌표 수: {len(valid)} 건 (수신 성공률: {len(valid)/len(df)*100:.2f}%)")
print(f"• 미수신(음영/터널) 패킷: {len(df) - len(valid)} 건 (오프라인/터널 구간)")

print("\n📊 1. 주행 속도(Speed) 지표")
print(f"   • 최고 속도: {valid['speed'].max():.1f} km/h")
print(f"   • 평균 주행 속도 (정차 제외 >5km/h): {valid[valid['speed'] > 5]['speed'].mean():.1f} km/h")
print(f"   • 전체 평균 속도: {valid['speed'].mean():.1f} km/h")
print(f"   • 80km/h 이상 고속 주행 패킷: {len(valid[valid['speed'] >= 80])} 건 ({len(valid[valid['speed'] >= 80])/len(valid)*100:.1f}%)")

print("\n🌡️ 2. 환경 모니터링 (온도 / 습도 / 조도)")
print(f"   • 온도 범위: {df['temperature'].min():.1f}°C ~ {df['temperature'].max():.1f}°C (평균: {df['temperature'].mean():.1f}°C)")
print(f"   • 습도 범위: {df['humidity'].min():.1f}% ~ {df['humidity'].max():.1f}% (평균: {df['humidity'].mean():.1f}%)")
print(f"   • 조도 범위: {df['lux'].min():.0f} lx ~ {df['lux'].max():.0f} lx (평균: {df['lux'].mean():.0f} lx)")

print("\n💥 3. 진동 및 물리적 충격 (G-Force)")
print(f"   • 평균 G-Force: {df['g_force'].mean():.2f} G (표준 중력 1.0G 기준 정상)")
print(f"   • 최대 충격량: {df['g_force'].max():.2f} G")
print(f"   • 위험 충격 (>= 2.0G): {len(df[df['g_force'] >= 2.0])} 건")
print(f"   • 심각 충격 (>= 3.0G): {len(df[df['g_force'] >= 3.0])} 건")
top_shocks = df.sort_values(by='g_force', ascending=False).head(5)
print("   • 최상위 충격 이벤트 Top 5:")
for _, s in top_shocks.iterrows():
    print(f"     - {s['kst_time'].strftime('%H:%M:%S')} | {s['g_force']:.2f}G | 속도: {s['speed']:4.1f}km/h | 위치: ({s['lat']:.5f}, {s['lng']:.5f})")

print("\n📍 4. 출발지, 경유지, 도착지 좌표 분석")
print(f"   • 출발 지점: ({valid['lat'].iloc[0]:.5f}, {valid['lng'].iloc[0]:.5f}) - 대전권 출발")
print(f"   • 최북단: {valid['lat'].max():.5f} / 최남단: {valid['lat'].min():.5f}")
print(f"   • 도착 지점: ({valid['lat'].iloc[-1]:.5f}, {valid['lng'].iloc[-1]:.5f}) - 전북대 전주 캠퍼스 도착")
