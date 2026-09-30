import re

with open(r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

footprints = text.split('(footprint ')
for fp in footprints[1:]:
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', fp)
    at_match = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', fp)
    if not ref_match or not at_match:
        continue
    ref = ref_match.group(1)
    base_x = float(at_match.group(1))
    base_y = float(at_match.group(2))
    print(f"\n==========================================")
    print(f"Footprint: {ref} at base ({base_x}, {base_y})")
    print(f"==========================================")
    pads = re.findall(r'\(pad\s+"(\d+)"\s+thru_hole\s+\w+\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\).*?\(net\s+\d+\s+"([^"]*)"\)', fp, re.DOTALL)
    for p, rx, ry, rot, net in pads:
        gx = base_x + float(rx)
        gy = base_y + float(ry)
        print(f"  Pin {p:2s} -> Global (X={gx:6.2f}, Y={gy:6.2f}) | Net: '{net}'")
