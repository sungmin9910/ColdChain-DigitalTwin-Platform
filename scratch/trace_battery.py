import re

pcb_file = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_file, 'r', encoding='utf-8') as f:
    text = f.read()

nets = dict(re.findall(r'\(net\s+(\d+)\s+"([^"]*)"\)', text))
print("=== NETS ===")
for k, v in nets.items():
    if 'BAT' in v or 'GND' in v:
        print(f"Net {k}: {v}")

tracks = re.findall(r'\(segment\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\).*?\(net\s+(\d+)\)', text)
for t in tracks:
    net_name = nets.get(t[4], '')
    if 'BAT' in net_name:
        print(f"Track {net_name}: ({t[0]}, {t[1]}) -> ({t[2]}, {t[3]})")
