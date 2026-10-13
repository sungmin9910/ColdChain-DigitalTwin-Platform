import subprocess
import os
import shutil

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

# 1. Update the wide exploded camera in render list
# distance 680 fits all 6 parts from top-right to bottom-left with zero clipping!
cmd_exploded_front = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", os.path.join(housing_dir, "20_exploded_view_front.png"),
    "-D", 'render_part="exploded_wide"',
    "--camera", "0,0,0,60,0,215,680",
    "--imgsize", "1400,1400",
    "--colorscheme", "Tomorrow Night",
    scad_file
]
subprocess.run(cmd_exploded_front)
shutil.copy(os.path.join(housing_dir, "20_exploded_view_front.png"), os.path.join(artifact_dir, "20_exploded_view_front.png"))

# Also overwrite 20_exploded_view.png with this superior view
shutil.copy(os.path.join(housing_dir, "20_exploded_view_front.png"), os.path.join(housing_dir, "20_exploded_view.png"))
shutil.copy(os.path.join(housing_dir, "20_exploded_view_front.png"), os.path.join(artifact_dir, "20_exploded_view.png"))

# 2. Opposite side angle (reveals back of front shell, back of PCB sensors, back of tray)
cmd_exploded_rear = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", os.path.join(housing_dir, "20_exploded_view_rear.png"),
    "-D", 'render_part="exploded_wide"',
    "--camera", "0,0,0,60,0,35,680",
    "--imgsize", "1400,1400",
    "--colorscheme", "Tomorrow Night",
    scad_file
]
subprocess.run(cmd_exploded_rear)
shutil.copy(os.path.join(housing_dir, "20_exploded_view_rear.png"), os.path.join(artifact_dir, "20_exploded_view_rear.png"))

# 3. Individual part detailed renders
parts = [
    ("part_rear_shell", "20_detail_1_rear_shell.png", "0,0,0,65,0,210,240"),
    ("part_battery", "20_detail_2_battery.png", "0,0,0,55,0,215,200"),
    ("part_battery_tray", "20_detail_3_battery_tray.png", "0,0,0,60,0,215,220"),
    ("part_pcb", "20_detail_4_pcb_assembly.png", "0,0,0,60,0,215,200"),
    ("part_front_shell", "20_detail_5_front_shell.png", "0,0,0,65,0,30,240")
]

for p_name, out_name, cam in parts:
    out_path = os.path.join(housing_dir, out_name)
    cmd = [
        r"C:\Program Files\OpenSCAD\openscad.com",
        "-o", out_path,
        "-D", f'render_part="{p_name}"',
        "--camera", cam,
        "--imgsize", "1000,1000",
        "--colorscheme", "Tomorrow Night",
        scad_file
    ]
    subprocess.run(cmd)
    shutil.copy(out_path, os.path.join(artifact_dir, out_name))

print("All final exploded and detail renders generated!")
