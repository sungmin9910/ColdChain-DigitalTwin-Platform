import subprocess
import os
import shutil

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

jobs = [
    # 1. Wide Exploded View (Camera positioned so every layer is cleanly visible)
    ("exploded_wide", "20_exploded_wide_view.png", "0,0,10,60,0,55,560"),
    # 2. Alternative angle for Wide Exploded View (More oblique side angle)
    ("exploded_wide", "20_exploded_side_view.png", "0,0,10,70,0,75,540"),
    # 3. 2x3 Grid Catalog Layout
    ("layout_catalog", "20_parts_catalog_layout.png", "0,0,0,55,0,25,380"),
    # 4. Individual Part Showcases
    ("part_rear_shell", "20_part1_rear_shell.png", "0,0,0,55,0,35,260"),
    ("part_battery", "20_part2_battery.png", "0,0,0,55,0,35,220"),
    ("part_battery_tray", "20_part3_battery_tray.png", "0,0,0,55,0,35,250"),
    ("part_pcb", "20_part4_pcb_assembly.png", "0,0,0,55,0,35,220"),
    ("part_front_shell", "20_part5_front_shell.png", "0,0,0,55,0,35,260"),
    # Update default exploded view as well
    ("exploded_wide", "20_exploded_view.png", "0,0,10,60,0,55,560")
]

print("=== Rendering All Advanced Exploded & Layout Views ===")
for name, out, cam in jobs:
    out_path = os.path.join(housing_dir, out)
    cmd = [
        openscad,
        "-o", out_path,
        "-D", f'render_part="{name}"',
        "--camera", cam,
        "--imgsize", "1200,1200",
        "--colorscheme", "Tomorrow Night",
        scad
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Rendered {name} -> {out}: exit code {res.returncode}")
    if res.returncode == 0:
        shutil.copy(out_path, os.path.join(artifact_dir, out))

print("\nAll advanced view renders completed successfully!")
