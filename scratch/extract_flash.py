import re
import json

with open('scratch/esp32_full_flash.bin', 'rb') as f:
    data = f.read()

# Match JSON starting with {"device":"carrier-c6-01" up to }
pattern = re.compile(rb'\{"device":"carrier-c6-01"[^\r\n\}]*\}')
matches = pattern.findall(data)
print(f"Total raw matches: {len(matches)}")

valid_packets = []
seen = set()
for m in matches:
    try:
        text = m.decode('utf-8', errors='ignore')
        j = json.loads(text)
        ts = j.get('timestamp_str')
        if ts and ts != "2026-10-01 00:00:00":
            key = (ts, str(j.get('lat')), str(j.get('g_force')))
            if key not in seen:
                seen.add(key)
                valid_packets.append(j)
    except Exception:
        pass

print(f"Total unique valid packets: {len(valid_packets)}")

from collections import Counter
ts_counter = Counter()
for m in matches:
    try:
        text = m.decode('utf-8', errors='ignore')
        j = json.loads(text)
        ts = j.get('timestamp_str', '')
        if '2026-10-03' in ts:
            ts_counter[ts[:14]] += 1
        elif '2026-10' in ts:
            ts_counter[ts[:10]] += 1
    except Exception:
        pass

print("Timestamps on Flash:")
for k, v in sorted(ts_counter.items()):
    print(f"  {k}: {v}")

