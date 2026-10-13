import subprocess
import os

scad_file = "scratch/test_solid_cradle.scad"
stl_file = "scratch/test_solid_cradle.stl"

# Export rear_shell print orientation: rotate([-90, 0, 0]) test_solid_cradle_rear_shell()
export_scad = r'''
$fn = 64;
include <test_solid_cradle.scad>
rotate([-90, 0, 0]) test_solid_cradle_rear_shell();
'''
with open("scratch/test_solid_export.scad", "w") as f:
    f.write(export_scad)

subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", stl_file,
    "scratch/test_solid_export.scad"
])

# Analyze overhangs
with open(stl_file, "r") as f:
    lines = f.readlines()

downward_faces = []
for i, line in enumerate(lines):
    line = line.strip()
    if line.startswith("facet normal"):
        parts = line.split()
        nx, ny, nz = float(parts[2]), float(parts[3]), float(parts[4])
        if nz < -0.9: # Downward facing overhang!
            v_zs = []
            for j in range(1, 8):
                if lines[i+j].strip().startswith("vertex"):
                    v_zs.append(float(lines[i+j].strip().split()[3]))
            if v_zs:
                z_avg = sum(v_zs) / len(v_zs)
                downward_faces.append(z_avg)

from collections import Counter
rounded_zs = [round(z, 1) for z in downward_faces]
counts = Counter(rounded_zs)
print("Downward overhang faces in test_solid_cradle (bed Z=0):")
for z, count in sorted(counts.items()):
    print(f"  Z = {z:5.1f} mm : {count} triangles")
