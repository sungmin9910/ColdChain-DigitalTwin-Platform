import re

pcb_file = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's check tracks connected to J_GPS
# J_GPS pads:
# Pad 1: (102.33, 109.5) -> Net 2 (3V3)
# Pad 2: (104.87, 109.5) -> Net 1 (GND)
# Pad 3: (107.41, 109.5) -> Net 8 (GPS_TX)
# Pad 4: (109.95, 109.5) -> Net 7 (GPS_RX)
# Pad 5: (112.49, 109.5) -> No Net

# Let's find tracks connected to net 8 and net 7
print("=== TRACKS FOR NET 8 (GPS_TX) ===")
for line in text.splitlines():
    if '(net 8)' in line or 'GPS_TX' in line:
        print(line)

print("\n=== TRACKS FOR NET 7 (GPS_RX) ===")
for line in text.splitlines():
    if '(net 7)' in line or 'GPS_RX' in line:
        print(line)
