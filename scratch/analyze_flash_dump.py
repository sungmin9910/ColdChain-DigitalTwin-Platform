import json
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

records = []
with open('scratch/flash_dump_20261002.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            records.append(json.loads(line))
        except Exception as e:
            pass

print("=" * 70)
print(f"  플래시 메모리 덤프 데이터 분석 (총 {len(records):,d} 건)")
print("=" * 70)

df = pd.DataFrame(records)
# 숫자형 변환
for col in ['temperature', 'humidity', 'lux', 'g_force', 'lat', 'lng', 'speed', 'sats']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['dt'] = pd.to_datetime(df['timestamp_str'], errors='coerce')
valid_dt = df.dropna(subset=['dt']).sort_values(by='dt')

print(f"• 전체 파싱 성공: {len(df):,d} 건")
print(f"• 타임스탬프 유효: {len(valid_dt):,d} 건")
if not valid_dt.empty:
    print(f"• 기록 시작 시각: {valid_dt['dt'].iloc[0]}")
    print(f"• 기록 종료 시각: {valid_dt['dt'].iloc[-1]}")
    
# GPS 유효 데이터
valid_gps = df[(df['lat'] != 0.0) & (df['lng'] != 0.0)]
print(f"• GPS Fix 유효 데이터: {len(valid_gps):,d} 건 ({len(valid_gps)/len(df)*100:.1f}%)")

# 시간대별(시간 단위) 데이터 분포
if not valid_dt.empty:
    print("\n⏰ 시간대별(KST) 기록 건수 분포:")
    valid_dt['hour'] = valid_dt['dt'].dt.floor('h')
    hourly = valid_dt.groupby('hour').agg(
        total=('dt', 'count'),
        gps_valid=('lat', lambda x: ((x != 0.0) & (df.loc[x.index, 'lng'] != 0.0)).sum()),
        min_temp=('temperature', 'min'),
        max_temp=('temperature', 'max'),
        max_spd=('speed', 'max')
    )
    for h, r in hourly.iterrows():
        tot = int(r['total'])
        gv = int(r['gps_valid'])
        print(f"  - [{h.strftime('%Y-%m-%d %H시')}] 총 {tot:>4d}건 (GPS유효: {gv:>4d}건) | 기온: {r['min_temp']:.1f}~{r['max_temp']:.1f}°C | 최고속도: {r['max_spd']:.1f}km/h")

# 갈 때 구간 (08:00 ~ 10:00) 분석
depart_flash = valid_dt[(valid_dt['dt'] >= '2026-10-02 08:00:00') & (valid_dt['dt'] <= '2026-10-02 10:00:00')]
print("\n" + "=" * 70)
print(f"🔍 [핵심 확인] 갈 때 (08:00 ~ 10:00 KST) 플래시 메모리 데이터:")
print(f"• 플래시 메모리 내 보존 건수: {len(depart_flash)} 건")
depart_gps = depart_flash[(depart_flash['lat'] != 0.0) & (depart_flash['lng'] != 0.0)]
print(f"• GPS 유효 건수: {len(depart_gps)} 건")
if not depart_flash.empty:
    print(f"• 시간 범위: {depart_flash['dt'].min()} ~ {depart_flash['dt'].max()}")
    print(f"• 좌표 범위: lat({depart_gps['lat'].min():.4f} ~ {depart_gps['lat'].max():.4f}), lng({depart_gps['lng'].min():.4f} ~ {depart_gps['lng'].max():.4f})")
    print(f"• 최고 속도: {depart_gps['speed'].max():.1f} km/h")
