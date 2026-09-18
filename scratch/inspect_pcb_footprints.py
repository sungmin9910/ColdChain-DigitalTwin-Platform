import re

with open(r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find footprints
fp_matches = re.finditer(r'\(footprint\s+"([^"]+)".*?\n\t\)', text, re.DOTALL)
for m in fp_matches:
    fp_str = m.group(0)
    ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_str)
    ref = ref_match.group(1) if ref_match else "Unknown"
    at_match = re.search(r'\(at\s+([0-9.-]+)\s+([0-9.-]+)\)', fp_str)
    at = at_match.groups() if at_match else ()
    print(f"Ref: {ref:10} At: {at}")
    # print pads
    pads = re.findall(r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)\s+\(at\s+([0-9.-]+)\s+([0-9.-]+).*?\(net\s+(\d+)\s+"([^"]*)"\)', fp_str)
    for p in pads:
        print(f"   Pad {p[0]:2}: rel=({p[3]}, {p[4]}) net={p[5]} ({p[6]})")
