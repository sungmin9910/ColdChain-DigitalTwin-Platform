import re

pcb_path = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_path, 'r', encoding='utf-8') as f:
    text = f.read()

print("=== NETS ===")
for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]+)"\)', text):
    net_id, net_name = m.groups()
    if any(k in net_name for k in ['GPS', 'RX', 'TX', '16', '17', 'UART']):
        print(f"Net {net_id}: {net_name}")

print("\n=== J_MCU_R and J_MCU_L ===")
for m in re.finditer(r'\(footprint\s+"[^"]*"\s+.*?\(property\s+"Reference"\s+"(J_MCU_[LR]|J_GPS)"\).*?\n\s*\)', text, re.DOTALL):
    fp_text = m.group(0)
    ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"\)', fp_text).group(1)
    print(f"\nFootprint {ref}:")
    pads = re.findall(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([-\d\.]+)\s+([-\d\.]+).*?\(net\s+\d+\s+"([^"]*)"\)', fp_text, re.DOTALL)
    for p, x, y, net in pads:
        print(f"  Pad {p:2s} (at {x}, {y}) -> Net '{net}'")
