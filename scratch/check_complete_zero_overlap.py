import numpy as np

regions = {
    'MCU (Beetle C6)': (114.75, 135.25, 100.0, 125.0),
    'BH1750 (Left Wing)': (100.5, 114.4, 106.5, 125.0),
    'GPS (Right Wing)': (136.0, 149.1, 108.0, 123.7),
    'SHT45 (Top Left)': (100.5, 126.0, 125.5, 143.3),
    'GY521 (Top Right)': (127.0, 147.7, 126.0, 141.65),
    'JST_PH (Top Center)': (120.0, 126.0, 144.5, 149.0),
}

holes = [
    ('H1 (Bottom-Left)', 103.5, 103.5),
    ('H2 (Bottom-Right)', 146.5, 103.5),
    ('H3 (Top-Left)', 103.5, 146.5),
    ('H4 (Top-Right)', 146.5, 146.5)
]

print("=== CHECKING 2D OVERLAPS BETWEEN ALL COMPONENTS ===")
overlaps = 0
names = list(regions.keys())
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        n1, n2 = names[i], names[j]
        r1, r2 = regions[n1], regions[n2]
        
        # Check intersection
        x_overlap = max(0, min(r1[1], r2[1]) - max(r1[0], r2[0]))
        y_overlap = max(0, min(r1[3], r2[3]) - max(r1[2], r2[2]))
        
        if x_overlap > 0 and y_overlap > 0:
            print(f"COLLISION: {n1} and {n2} overlap by dx={x_overlap:.2f}, dy={y_overlap:.2f}")
            overlaps += 1
        else:
            # Check gap
            dx_gap = max(0, r2[0] - r1[1], r1[0] - r2[1])
            dy_gap = max(0, r2[2] - r1[3], r1[2] - r2[3])
            gap = max(dx_gap, dy_gap)
            print(f"CLEAR: {n1} and {n2} -> Gap = {gap:.2f} mm")

print(f"\nTotal Component 2D Overlaps: {overlaps}")

print("\n=== CHECKING M3 HOLE CLEARANCES ===")
hole_conflicts = 0
for h_name, hx, hy in holes:
    for n, r in regions.items():
        dx = max(0, r[0] - hx, hx - r[1])
        dy = max(0, r[2] - hy, hy - r[3])
        dist = np.hypot(dx, dy)
        if dist < 2.75:
            print(f"HOLE CONFLICT: {n} collides with {h_name} (dist={dist:.2f} < 2.75mm)")
            hole_conflicts += 1
        else:
            print(f"Hole Clear: {n} vs {h_name} -> Clearance = {dist - 2.75:.2f} mm")

print(f"Total Hole Conflicts: {hole_conflicts}")
