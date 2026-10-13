import subprocess
import os
import shutil

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

jobs = [
    ("cross_section", "20_cross_section_view.png", "0,0,5,65,0,45,280"),
    ("assembly", "20_assembly_view.png", "0,0,5,65,0,35,280")
]

for name, out, cam in jobs:
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
    subprocess.run(cmd)
    shutil.copy(out_path, os.path.join(artifact_dir, out))

print("Cross section and assembly renders updated!")
