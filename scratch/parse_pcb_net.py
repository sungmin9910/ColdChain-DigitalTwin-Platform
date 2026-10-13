import json
import re

with open('3D modeling/CarrierBoard_BeetleC6_50x50/CarrierBoard_BeetleC6_50x50_EasyEDA_Source.json', 'r', encoding='utf-8') as f:
    text = f.read()

nets = set(re.findall(r'\"net\":\s*\"([^\"]+)\"', text))
print('Nets found with "net":', sorted(list(nets)))

# Find PAD definitions
pads = [line for line in text.split('PAD~') if any(k in line for k in ['SDA', 'SCL', 'I2C', '19', '20', 'GPIO'])]
print(f'Total matching pads: {len(pads)}')
for p in pads[:25]:
    parts = p.split('~')
    print('PAD:', parts[:10])
