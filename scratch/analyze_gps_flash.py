import re
import json
from collections import Counter

with open('scratch/esp32_full_flash.bin', 'rb') as f:
    data = f.read()

pattern = re.compile(rb'\{"device":"carrier-c6-01"[^\r\n\}]*\}')
matches = pattern.findall(data)
print(f"Total JSON matches in 4MB flash: {len(matches)}")

gps_packets = []
seen = set()
for m in matches:
    try:
        j = json.loads(m.decode('utf-8', errors='ignore'))
        lat = float(j.get('lat', 0.0))
        lng = float(j.get('lng', 0.0))
        if lat > 30.0 and lng > 120.0:
            key = (j.get('timestamp_str'), lat, lng, j.get('g_force'))
            if key not in seen:
                seen.add(key)
                gps_packets.append(j)
    except Exception:
        pass

print(f"Total unique GPS packets: {len(gps_packets)}")
date_counter = Counter()
for p in gps_packets:
    ts = str(p.get('timestamp_str', ''))[:10]
    date_counter[ts] += 1

print("GPS packets grouped by timestamp date:")
for k, v in sorted(date_counter.items()):
    print(f"  {k}: {v}")

# Check 2026-10-03 GPS packets
today_gps = [p for p in gps_packets if str(p.get('timestamp_str', '')).startswith('2026-10-03')]
print(f"Total 2026-10-03 GPS packets: {len(today_gps)}")
if today_gps:
    print("First today GPS:", today_gps[0])
    print("Last today GPS:", today_gps[-1])

# Check 2026-10-01 (default time) GPS packets
uninit_gps = [p for p in gps_packets if str(p.get('timestamp_str', '')).startswith('2026-10-01')]
print(f"Total 2026-10-01 uninitialized time GPS packets: {len(uninit_gps)}")
for i, p in enumerate(uninit_gps):
    print(f"  [{i:02d}] speed: {p.get('speed', 0):>4} km/h | lat: {p.get('lat', 0):.5f}, lng: {p.get('lng', 0):.5f} | g: {p.get('g_force')} | temp: {p.get('temperature')} | sats: {p.get('sats')}")

