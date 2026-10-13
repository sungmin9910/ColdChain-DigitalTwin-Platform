import re

pcb_path = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find footprints
blocks = text.split('(footprint')
for b in blocks[1:]:
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', b)
    at_match = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)', b)
    if ref_match and at_match:
        ref = ref_match.group(1)
        x, y = float(at_match.group(1)), float(at_match.group(2))
        print(f"Ref: {ref:10s} at ({x:6.2f}, {y:6.2f})")
        # print pads
        pads = re.findall(r'\(pad "([^"]+)" [^\(]+\(at ([\d\.-]+) ([\d\.-]+)[^\)]*\).*?\(net \d+ "([^"]*)"\)?', b)
        for p in pads:
            px = x + float(p[1])
            py = y + float(p[2])
            print(f"   Pad {p[0]:2s}: rel({p[1]:>5s}, {p[2]:>5s}) => abs({px:6.2f}, {py:6.2f}) net: {p[3]}")
