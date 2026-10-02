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

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def analyze_session(run_id, title):
    with conn.cursor() as c:
        c.execute("""
            SELECT id, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng
            FROM sensor_data
            WHERE run_id = %s
            ORDER BY id ASC
        """, (run_id,))
        rows = c.fetchall()
        
    df = pd.DataFrame(rows)
    valid = df[(df['lat'] != 0.0) & (df['lng'] != 0.0)].copy()
    
    # 누적 주행 거리
    valid['prev_lat'] = valid['lat'].shift(1)
    valid['prev_lng'] = valid['lng'].shift(1)
    valid['dist_km'] = valid.apply(
        lambda r: haversine(r['prev_lat'], r['prev_lng'], r['lat'], r['lng']) if pd.notnull(r['prev_lat']) else 0.0,
        axis=1
    )
    valid['dist_km'] = valid['dist_km'].apply(lambda x: x if x < 5.0 else 0.0)
    total_dist = valid['dist_km'].sum()
    
    # 시간
    start_time = df['timestamp_str'].iloc[0]
    end_time = df['timestamp_str'].iloc[-1]
    
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print(f"• 세션 식별자: {run_id}")
    print(f"• 운행 시간 (KST): {start_time} ~ {end_time}")
    print(f"• 총 수집 패킷: {len(df):,d} 건 (GPS 수신율: {len(valid)/len(df)*100:.1f}%)")
    print(f"• 총 누적 주행 거리: 약 {total_dist:.2f} km")
    print(f"• 출발 위치: ({valid.iloc[0]['lat']:.5f}, {valid.iloc[0]['lng']:.5f})")
    print(f"• 도착 위치: ({valid.iloc[-1]['lat']:.5f}, {valid.iloc[-1]['lng']:.5f})")
    print(f"• 주행 속도: 최고 {valid['speed'].max():.1f} km/h | 평균(주행중): {valid[valid['speed'] > 5]['speed'].mean():.1f} km/h")
    print(f"• 환경 모니터링: 온도 {df['temperature'].min():.1f}°C ~ {df['temperature'].max():.1f}°C (평균: {df['temperature'].mean():.1f}°C) | 습도 {df['humidity'].min():.1f}% ~ {df['humidity'].max():.1f}%")
    print(f"• 충격/진동: 최대 {df['g_force'].max():.2f} G | 2.0G 이상 충격 {len(df[df['g_force'] >= 2.0])} 건")

analyze_session('run_20261002_080002_departure', '🚗 1. [갈 때] 전주 -> 대전 (복원 완료)')
analyze_session('run_20261002_012518', '🚗 2. [올 때] 대전 -> 전주')

conn.close()
