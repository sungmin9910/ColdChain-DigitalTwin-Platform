import numpy as np

# Verify 100% 2D Zero-Overlap across Front, Back, and Projection

# Component Bounding Boxes [Xmin, Xmax, Ymin, Ymax]
components = {
    'Beetle ESP32-C6 (Top)': (114.75, 135.25, 100.0, 125.0),
    'BH1750 (Top, Right Wing)': (135.8, 149.7, 106.7, 125.2),
    'JST-PH 2.0 (Top)': (120.0, 126.0, 144.5, 149.0),
    'SW1 Slide Switch (Top)': (112.5, 119.5, 144.5, 148.5),
    'GPS ATGM336H (Bottom, Left Wing)': (100.8, 113.9, 107.5, 123.2),
    'SHT45 Qwiic (Bottom, Top-Left)': (100.5, 126.0, 125.5, 143.3),
    'GY-521 IMU (Bottom, Top-Right)': (128.5, 149.2, 125.5, 141.15),
}

# Female Header Housings (2.54mm wide)
housings = {
    'MCU Left Socket (Top)': (116.11 - 1.27, 116.11 + 1.27, 102.66 - 1.27, 120.44 + 1.27),
    'MCU Right Socket (Top)': (133.89 - 1.27, 133.89 + 1.27, 102.66 - 1.27, 120.44 + 1.27),
    'BH1750 Socket (Top)': (137.67 - 1.27, 147.83 + 1.27, 123.2 - 1.27, 123.2 + 1.27),
    'GPS Socket (Bottom)': (102.33 - 1.27, 112.49 + 1.27, 109.5 - 1.27, 109.5 + 1.27),
    'SHT45 Socket (Bottom)': (108.17 - 1.27, 118.33 + 1.27, 127.5 - 1.27, 127.5 + 1.27),
    'GY-521 Socket (Bottom)': (129.56 - 1.27, 147.34 + 1.27, 127.5 - 1.27, 127.5 + 1.27),
}

# M3 Holes
holes = [
    ('H1 (Bottom-Left)', 103.5, 103.5),
    ('H2 (Bottom-Right)', 146.5, 103.5),
    ('H3 (Top-Left)', 103.5, 146.5),
    ('H4 (Top-Right)', 146.5, 146.5),
]

print("=== 1. VERIFYING 2D PROJECTION OVERLAPS (FRONT + BACK OVERLAID) ===")
comp_overlaps = 0
c_names = list(components.keys())
for i in range(len(c_names)):
    for j in range(i + 1, len(c_names)):
        n1, n2 = c_names[i], c_names[j]
        r1, r2 = components[n1], components[n2]
        x_ov = max(0, min(r1[1], r2[1]) - max(r1[0], r2[0]))
        y_ov = max(0, min(r1[3], r2[3]) - max(r1[2], r2[2]))
        if x_ov > 0 and y_ov > 0:
            print(f"COLLISION: {n1} vs {n2} (X={x_ov:.2f}, Y={y_ov:.2f})")
            comp_overlaps += 1
        else:
            gap = max(r2[0] - r1[1], r1[0] - r2[1], r2[2] - r1[3], r1[2] - r2[3])
            print(f"PASS: {n1} vs {n2} -> 2D Gap = {gap:.2f} mm")

print(f"\nTotal Component 2D Overlaps: {comp_overlaps}")

print("\n=== 2. VERIFYING FEMALE HEADER HOUSING CLEARANCES ===")
house_overlaps = 0
h_names = list(housings.keys())
for i in range(len(h_names)):
    for j in range(i + 1, len(h_names)):
        n1, n2 = h_names[i], h_names[j]
        r1, r2 = housings[n1], housings[n2]
        x_ov = max(0, min(r1[1], r2[1]) - max(r1[0], r2[0]))
        y_ov = max(0, min(r1[3], r2[3]) - max(r1[2], r2[2]))
        if x_ov > 0 and y_ov > 0:
            print(f"SOCKET COLLISION: {n1} vs {n2}")
            house_overlaps += 1
        else:
            gap = max(r2[0] - r1[1], r1[0] - r2[1], r2[2] - r1[3], r1[2] - r2[3])
            print(f"PASS: {n1} vs {n2} -> Housing Gap = {gap:.2f} mm")

print(f"\nTotal Socket Housing Overlaps: {house_overlaps}")

print("\n=== 3. VERIFYING M3 HOLE CLEARANCES ===")
hole_conflicts = 0
for h_name, hx, hy in holes:
    for c_name, r in components.items():
        dx = max(0, r[0] - hx, hx - r[1])
        dy = max(0, r[2] - hy, hy - r[3])
        dist = np.hypot(dx, dy)
        if dist < 2.75:
            print(f"M3 CONFLICT: {c_name} vs {h_name} (dist={dist:.2f} < 2.75mm)")
            hole_conflicts += 1
        else:
            print(f"PASS: {c_name} vs {h_name} -> Clearance = {dist - 2.75:.2f} mm")

print(f"\nTotal M3 Hole Conflicts: {hole_conflicts}")
