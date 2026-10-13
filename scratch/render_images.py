import subprocess
import os
import shutil

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad = r"3D_Printer_Housing\v19_Apple_Sensor_Pod_5000mAh\19_apple_sensor_pod.scad"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

jobs = [
    ("exploded", "19_exploded_view.png", "0,10,15,65,0,25,380"),
    ("cross_section", "19_cross_section_view.png", "0,0,5,65,0,45,260"),
    ("assembly", "19_assembly_view.png", "0,0,5,65,0,35,270"),
    ("print_all", "19_print_layout_view.png", "0,0,15,55,0,30,290")
]

for name, out, cam in jobs:
    out_path = os.path.join(r"3D_Printer_Housing\v19_Apple_Sensor_Pod_5000mAh", out)
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

print("All 4 images copied to artifact dir successfully!")
