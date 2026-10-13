import re
import math

pcb_path = r'3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50\CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'

with open(pcb_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Board center is at (125.0, 125.0)
# Hole coordinates in KiCad:
# (103.5, 103.5) -> (dx=-21.5, dy=-21.5)
# (146.5, 103.5) -> (dx=+21.5, dy=-21.5)
# (103.5, 146.5) -> (dx=-21.5, dy=+21.5)
# (146.5, 146.5) -> (dx=+21.5, dy=+21.5)

fps = content.split('(footprint ')
print("=== Footprints and distances to 4 mounting holes ===")
holes = {
    "H1 (Top-Left in KiCad)": (103.5, 103.5),
    "H2 (Top-Right in KiCad)": (146.5, 103.5),
    "H3 (Bottom-Left in KiCad)": (103.5, 146.5),
    "H4 (Bottom-Right in KiCad)": (146.5, 146.5)
}

for fp in fps[1:]:
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    layer_m = re.search(r'\(layer "([^"]+)"\)', fp)
    at_m = re.search(r'\(at ([\d\.\-]+) ([\d\.\-]+)', fp)
    
    if not ref_m or not at_m:
        continue
    ref = ref_m.group(1)
    layer = layer_m.group(1) if layer_m else '?'
    x = float(at_m.group(1))
    y = float(at_m.group(2))
    
    # Distance to closest hole
    min_dist = 999
    closest_h = ""
    for hname, (hx, hy) in holes.items():
        d = math.sqrt((x - hx)**2 + (y - hy)**2)
        if d < min_dist:
            min_dist = d
            closest_h = hname
            
    print(f"{ref:<12} on {layer:<6} at ({x:>6.2f}, {y:>6.2f}) -> closest {closest_h}: dist = {min_dist:.2f} mm")
