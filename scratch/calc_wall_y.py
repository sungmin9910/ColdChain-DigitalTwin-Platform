import math

# Extract profile from 21_apple_sensor_pod.scad
with open(r'3D_Printer_Housing\v21_Apple_Sensor_Pod_2Piece5000mAh\21_apple_sensor_pod.scad', 'r', encoding='utf-8') as f:
    text = f.read()

import re

inner_match = re.search(r'apple_inner_profile\s*=\s*\[(.*?)\];', text, re.DOTALL)
outer_match = re.search(r'apple_outer_profile\s*=\s*\[(.*?)\];', text, re.DOTALL)

def parse_profile(s):
    pairs = re.findall(r'\[\s*([\d\.\-]+)\s*,\s*([\d\.\-]+)\s*\]', s)
    return [(float(r), float(z)) for r, z in pairs]

inner_prof = parse_profile(inner_match.group(1))
outer_prof = parse_profile(outer_match.group(1))

# Interpolate R given Z
def get_r(prof, z_target):
    # prof is sorted by z
    for i in range(len(prof) - 1):
        r1, z1 = prof[i]
        r2, z2 = prof[i+1]
        if (z1 <= z_target <= z2) or (z2 <= z_target <= z1):
            if z2 == z1:
                return r1
            t = (z_target - z1) / (z2 - z1)
            return r1 + t * (r2 - r1)
    return 0.0

hole_pitch = 43.0
pcb_z_center = 3.0

holes = [
    ("Bottom-Left",  -21.5, pcb_z_center - 21.5), # -18.5
    ("Bottom-Right",  21.5, pcb_z_center - 21.5), # -18.5
    ("Top-Left",     -21.5, pcb_z_center + 21.5), # +24.5
    ("Top-Right",     21.5, pcb_z_center + 21.5), # +24.5
]

print("=== Standoff Locations and Wall Y-Positions ===")
for name, x, z in holes:
    r_in = get_r(inner_prof, z)
    r_out = get_r(outer_prof, z)
    
    # At this x, z: Y_inner = sqrt(r_in^2 - x^2), Y_outer = sqrt(r_out^2 - x^2)
    y_in = math.sqrt(max(0, r_in**2 - x**2))
    y_out = math.sqrt(max(0, r_out**2 - x**2))
    print(f"{name:<12} (X={x:>5.1f}, Z={z:>5.1f}):")
    print(f"   R_inner(Z) = {r_in:.2f} mm -> Inner Wall is at Y = +{y_in:.2f} mm")
    print(f"   R_outer(Z) = {r_out:.2f} mm -> Outer Wall is at Y = +{y_out:.2f} mm")
    print(f"   Wall thickness along Y: {y_out - y_in:.2f} mm")
    print(f"   Distance from PCB mount (Y=3.5) to Inner Wall: {y_in - 3.5:.2f} mm")
