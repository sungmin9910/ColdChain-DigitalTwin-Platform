import re

pcb_path = r'3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText\CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'

with open(pcb_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Split footprints
fps = content.split('(footprint ')
for fp in fps[1:]:
    # extract reference
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    if not ref_m:
        continue
    ref = ref_m.group(1)
    if ref in ['J_MCU_L', 'J_MCU_R', 'J_SHT45', 'J_GY521', 'J_BH1750', 'J_GPS', 'R3', 'R4']:
        layer_m = re.search(r'\(layer "([^"]+)"\)', fp)
        at_m = re.search(r'\(at ([\d\.\-]+) ([\d\.\-]+)(?: ([\d\.\-]+))?\)', fp)
        print(f"\n=======================================================")
        print(f"Footprint: {ref} | Layer: {layer_m.group(1) if layer_m else 'unknown'} | At: {at_m.groups() if at_m else ''}")
        pads = re.findall(r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+).*?\(net\s+(\d+)\s+"([^"]+)"\)', fp)
        for p in pads:
            pad_num, ptype, shape, x, y, net_id, net_name = p
            print(f"  Pad {pad_num:>2} (dx={float(x):>5.2f}, dy={float(y):>5.2f}) -> Net: {net_name} ({net_id})")
