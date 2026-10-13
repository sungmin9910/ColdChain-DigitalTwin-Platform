import math

# Hole pitch 43x43mm, pcb_z_center = 3.0
hole_pitch = 43.0
pcb_z_center = 3.0

pts = []
for dx in [-1, 1]:
    for dz in [-1, 1]:
        x = dx * (hole_pitch / 2) # +-21.5
        z = pcb_z_center + dz * (hole_pitch / 2) # 3.0 +- 21.5 = +24.5 or -18.5
        pts.append((x, z))

print("4x PCB Hole Coordinates (X, Z):")
for p in pts:
    r = math.sqrt(p[0]**2 + p[1]**2)
    print(f"  X={p[0]:>5.1f}, Z={p[1]:>5.1f} | Radius from apple center = {r:.2f} mm")
