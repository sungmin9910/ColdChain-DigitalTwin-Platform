import re
from collections import Counter

with open('scratch/esp32_full_flash.bin', 'rb') as f:
    data = f.read()

matches = re.findall(rb'"timestamp_str":"([^"]+)"', data)
unique_ts = sorted(set(m.decode('utf-8', errors='ignore') for m in matches))
print(f"Total unique timestamps: {len(unique_ts)}")

today_ts = [t for t in unique_ts if t.startswith('2026-10-03')]
print(f"Today unique timestamps: {len(today_ts)}")
for t in today_ts[:15]:
    print('  ', t)
if len(today_ts) > 15:
    print('  ...')
    for t in today_ts[-15:]:
        print('  ', t)

# Check if there are timestamps starting with 2026-10-01 (default when NTP is off)
uninit_ts = [t for t in unique_ts if t.startswith('2026-10-01')]
print(f"2026-10-01 (uninitialized NTP) timestamps: {len(uninit_ts)}")
