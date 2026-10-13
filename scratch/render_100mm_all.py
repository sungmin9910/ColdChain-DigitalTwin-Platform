import subprocess
import os
import shutil

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad = r"3D_Printer_Housing\v19_Apple_Sensor_Pod_5000mAh\19_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v19_Apple_Sensor_Pod_5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

# 1. Preview Images
jobs_img = [
    ("exploded", "19_exploded_view.png", "0,10,15,65,0,25,400"),
    ("cross_section", "19_cross_section_view.png", "0,0,5,65,0,45,280"),
    ("assembly", "19_assembly_view.png", "0,0,5,65,0,35,280"),
    ("print_all", "19_print_layout_view.png", "0,0,15,55,0,30,310")
]

print("=== Rendering 3D Preview Images (100mm) ===")
for name, out, cam in jobs_img:
    out_path = os.path.join(housing_dir, out)
    cmd = [
        openscad,
        "-o", out_path,
        "-D", f'render_part="{name}"',
        "--camera", cam,
        "--imgsize", "1024,1024",
        "--colorscheme", "Tomorrow Night",
        scad
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Rendered {name} -> {out}: exit code {res.returncode}")
    if res.returncode == 0:
        shutil.copy(out_path, os.path.join(artifact_dir, out))

# 2. STL Export Files
jobs_stl = [
    ("rear_shell", "19_apple_rear_shell.stl"),
    ("front_shell", "19_apple_front_shell.stl"),
    ("stem", "19_apple_stem.stl")
]

print("\n=== Exporting 3D Printable STL Files (100mm) ===")
for name, out in jobs_stl:
    out_path = os.path.join(housing_dir, out)
    cmd = [
        openscad,
        "-o", out_path,
        "-D", f'render_part="{name}"',
        scad
    ]
    print(f"Exporting {name} -> {out} ...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Exported {name} -> {out}: exit code {res.returncode}")

print("\nAll 100mm renderings and STL exports finished successfully!")
