import glob
import os
import re

out = []
for p in glob.glob('**/*.kicad_pcb', recursive=True):
    out.append(f"\n============================\nPCB: {p}")
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    parts = text.split('(footprint ')
    for part in parts[1:]:
        lines = part.splitlines()
        fp_name = lines[0].strip().strip('"')
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', part)
        at_m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', part)
        ref = ref_m.group(1) if ref_m else "?"
        at = at_m.groups() if at_m else ("?", "?", "?")
        layer_m = re.search(r'\(layer\s+"([^"]+)"\)', part)
        layer = layer_m.group(1) if layer_m else "?"
        pads_count = len(re.findall(r'\(pad\s+', part))
        out.append(f"  {ref:12} ({pads_count:2} pads) at {at} layer={layer} | {fp_name}")

with open('scratch/all_pcbs.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Wrote scratch/all_pcbs.txt")
