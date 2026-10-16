import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/carrier02_full_dump.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(l) for l in f if l.strip()]

tonight = [r for r in records if r.get('timestamp_str', '').startswith('2026-10-16 21:') or r.get('timestamp_str', '').startswith('2026-10-16 22:')]
print(f"Tonight records count: {len(tonight)}")

if tonight:
    temps = [float(r['temperature']) for r in tonight if float(r.get('temperature', 0)) > 0]
    humis = [float(r['humidity']) for r in tonight if float(r.get('humidity', 0)) > 0]
    luxs = [float(r['lux']) for r in tonight]
    g_forces = [float(r['g_force']) for r in tonight]
    gps_recs = [r for r in tonight if float(r.get('lat', 0)) > 0]
    speeds = [float(r['speed']) for r in gps_recs]
    
    t_start = tonight[0]['timestamp_str']
    t_end = tonight[-1]['timestamp_str']
    print(f"시작 시각: {t_start}")
    print(f"종료 시각: {t_end}")
    
    if temps:
        print(f"온도 범위: {min(temps):.2f} ℃ ~ {max(temps):.2f} ℃ (평균: {sum(temps)/len(temps):.2f} ℃)")
    if humis:
        print(f"습도 범위: {min(humis):.2f} % ~ {max(humis):.2f} % (평균: {sum(humis)/len(humis):.2f} %)")
    if luxs:
        print(f"조도 범위: {min(luxs):.1f} lx ~ {max(luxs):.1f} lx")
    if g_forces:
        print(f"최대 충격량: {max(g_forces):.2f} G")
    
    print(f"유효 GPS 수신 포인트: {len(gps_recs)} 개")
    if gps_recs:
        print(f"최고 주행 속도: {max(speeds):.1f} km/h (평균: {sum(speeds)/len(speeds):.1f} km/h)")
        print(f"출발 지점 좌표: ({gps_recs[0]['lat']}, {gps_recs[0]['lng']}) - {gps_recs[0]['timestamp_str']}")
        print(f"도착 지점 좌표: ({gps_recs[-1]['lat']}, {gps_recs[-1]['lng']}) - {gps_recs[-1]['timestamp_str']}")

    # Check shock events >= 1.8G
    shocks = [r for r in tonight if float(r.get('g_force', 1.0)) >= 1.8]
    print(f"충격(1.8G 이상) 감지 횟수: {len(shocks)} 회")
    for s in shocks:
        print(f"  - [{s['timestamp_str']}] 충격: {s['g_force']} G, 위치: ({s.get('lat')}, {s.get('lng')}), 상태: {s.get('status')}")
