import numpy as np

# Let's inspect the triangle normals and Z heights of horizontal faces in 20_apple_rear_shell.stl
with open(r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_rear_shell.stl", "r") as f:
    lines = f.readlines()

downward_horizontal_faces = [] # Normals pointing straight down (Z ~ -1)
for i, line in enumerate(lines):
    line = line.strip()
    if line.startswith("facet normal"):
        parts = line.split()
        nx, ny, nz = float(parts[2]), float(parts[3]), float(parts[4])
        if nz < -0.9: # Downward facing overhang!
            # Get the Z coordinates of the 3 vertices
            v_zs = []
            for j in range(1, 8):
                if lines[i+j].strip().startswith("vertex"):
                    v_zs.append(float(lines[i+j].strip().split()[3]))
            if v_zs:
                z_avg = sum(v_zs) / len(v_zs)
                downward_horizontal_faces.append(z_avg)

print(f"Total downward-facing horizontal faces (normals pointing down): {len(downward_horizontal_faces)}")
if downward_horizontal_faces:
    # Group by Z height
    from collections import Counter
    rounded_zs = [round(z, 1) for z in downward_horizontal_faces]
    counts = Counter(rounded_zs)
    print("Downward overhang faces by Z height (in mm from bed Z=0):")
    for z, count in sorted(counts.items()):
        print(f"  Z = {z:5.1f} mm : {count} triangles")
