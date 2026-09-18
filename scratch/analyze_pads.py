import re

pcb_file = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
content = open(pcb_file, encoding='utf-8').read()

fp_blocks = content.split('(footprint ')
for block in fp_blocks[1:]:
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
    if not ref_m:
        ref_m = re.search(r'\(fp_text\s+reference\s+"([^"]+)"', block)
    ref = ref_m.group(1) if ref_m else 'UNKNOWN'
    if not ref.startswith('J'):
        continue
    at_m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', block)
    fx, fy = float(at_m.group(1)), float(at_m.group(2))
    
    pad_matches = re.findall(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)', block)
    pad_coords = [(p[0], fx + float(p[1]), fy + float(p[2])) for p in pad_matches]
    print(f"=== {ref} (fp origin: {fx:.2f}, {fy:.2f}) ===")
    for pnum, px, py in pad_coords:
        print(f"  Pad {pnum}: ({px:.2f}, {py:.2f})")
