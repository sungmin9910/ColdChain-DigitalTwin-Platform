import subprocess
import os

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
scratch_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520\scratch"

# Test individual cameras:
# When looking into inside cavity from +Y: rotX=60, rotY=0, rotZ=215, or rotX=65, rotZ=205
tests = [
    ("part_rear_shell", "test_p1_rear.png", "0,0,0,65,0,210,260"),
    ("part_battery_tray", "test_p3_tray.png", "0,0,0,60,0,215,220"),
    ("part_pcb", "test_p4_pcb.png", "0,0,0,60,0,215,200"),
    ("part_front_shell", "test_p5_front.png", "0,0,0,65,0,30,260")
]

for part, out, cam in tests:
    out_path = os.path.join(scratch_dir, out)
    cmd = [
        r"C:\Program Files\OpenSCAD\openscad.com",
        "-o", out_path,
        "-D", f'render_part="{part}"',
        "--camera", cam,
        "--imgsize", "800,800",
        "--colorscheme", "Tomorrow Night",
        scad_file
    ]
    subprocess.run(cmd)

print("Individual camera tests finished!")
