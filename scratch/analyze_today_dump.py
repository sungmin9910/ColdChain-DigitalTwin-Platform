import json

with open("scratch/dump_20261006_evening.jsonl", "r", encoding="utf-8") as f:
    records = [json.loads(line) for line in f if line.strip()]

today_records = [r for r in records if str(r.get('timestamp_str', '')).startswith('2026-10-06')]

print(f"Total today records: {len(today_records)}")
print(f"Start TS: {today_records[0].get('timestamp_str')}")
print(f"End TS:   {today_records[-1].get('timestamp_str')}")

# 구간별 요약
speeds = [float(r.get('speed', 0.0)) for r in today_records]
lats = [float(r.get('lat', 0.0)) for r in today_records if float(r.get('lat', 0.0)) > 0]
lngs = [float(r.get('lng', 0.0)) for r in today_records if float(r.get('lng', 0.0)) > 0]

print(f"Max Speed: {max(speeds)} km/h")
print(f"Valid GPS points: {len(lats)} / {len(today_records)}")
print(f"Start Point: Lat {lats[0]:.6f}, Lng {lngs[0]:.6f}")
print(f"End Point:   Lat {lats[-1]:.6f}, Lng {lngs[-1]:.6f}")

# 20:49 이후 몇 건인지 확인
after_49 = [r for r in today_records if r.get('timestamp_str') > '2026-10-06 20:49:11']
print(f"Records after 20:49:11 (missing in DB): {len(after_49)} records")
