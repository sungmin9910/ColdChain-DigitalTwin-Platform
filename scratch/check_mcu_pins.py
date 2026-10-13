import re

pcb_file = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect J_MCU_R and J_MCU_L with their global pad coordinates
for part in text.split('(footprint '):
    if 'J_MCU_R' in part or 'J_MCU_L' in part:
        ref = re.search(r'Reference" "([^"]+)"', part).group(1)
        at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', part).groups()
        print(f"\n{ref} at base {at}:")
        pads = re.findall(r'\(pad\s+"(\d+)".*?\(at\s+([-\d.]+)\s+([-\d.]+).*?\(net\s+\d+\s+"([^"]*)"\)', part, re.DOTALL)
        for p, x, y, net in pads:
            gy = float(at[1]) + float(y)
            gx = float(at[0]) + float(x)
            print(f"  Pad {p}: local=({x},{y}), global=({gx:.2f}, {gy:.2f}) -> Net '{net}'")
