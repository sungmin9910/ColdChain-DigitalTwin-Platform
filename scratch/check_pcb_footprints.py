import re

pcb_path = r'3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50\CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'

with open(pcb_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find board outline or center
# Split footprints
fps = content.split('(footprint ')
print("=== All Footprints on Board ===")
for fp in fps[1:]:
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    val_m = re.search(r'\(property "Value" "([^"]+)"', fp)
    layer_m = re.search(r'\(layer "([^"]+)"\)', fp)
    at_m = re.search(r'\(at ([\d\.\-]+) ([\d\.\-]+)(?: ([\d\.\-]+))?\)', fp)
    
    ref = ref_m.group(1) if ref_m else '?'
    val = val_m.group(1) if val_m else '?'
    layer = layer_m.group(1) if layer_m else '?'
    at = at_m.groups() if at_m else ('?', '?', '?')
    
    print(f"Ref: {ref:<15} Val: {val:<25} Layer: {layer:<10} At: (X={at[0]}, Y={at[1]}, rot={at[2]})")
