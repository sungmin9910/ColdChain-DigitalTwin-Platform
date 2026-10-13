import re

pcb_path = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_path, 'r', encoding='utf-8') as f:
    text = f.read()

footprints = text.split('(footprint ')
for fp in footprints[1:]:
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', fp)
    if not ref_match:
        continue
    ref = ref_match.group(1)
    if ref in ['J_GPS', 'J_MCU_R', 'J_MCU_L']:
        print(f"\n=== {ref} ===")
        pads = fp.split('(pad ')
        for p in pads[1:]:
            pad_num = p.split()[0].replace('"', '')
            at_match = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)\)', p)
            net_match = re.search(r'\(net (\d+) "([^"]*)"\)', p)
            at_str = f"({at_match.group(1)}, {at_match.group(2)})" if at_match else "no pos"
            net_str = f"net {net_match.group(1)}: {net_match.group(2)}" if net_match else "NC"
            print(f"  Pad {pad_num:>2s}: at {at_str:<16s} {net_str}")
