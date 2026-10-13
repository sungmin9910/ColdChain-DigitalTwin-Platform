import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# The boss is at X'=35, Y'=26. In the user photo:
# Looking from center of shell towards (35, 26, 13).
# Looking from negative X, negative Y towards positive X, positive Y.
cams = [
    ("c1", "30,22,12,60,0,-45,80"),
    ("c2", "30,22,12,70,0,-60,70"),
    ("c3", "25,18,10,75,0,-50,60"),
    ("c4", "25,18,10,65,0,-40,60")
]

for name, cam in cams:
    img_path = f"scratch/test_{name}.png"
    cmd = [
        r"C:\Program Files\OpenSCAD\openscad.com",
        "-o", img_path,
        "-D", 'render_part="rear_shell"',
        "--camera", cam,
        "--imgsize", "800,800",
        "--colorscheme", "Cornfield",
        scad_file
    ]
    subprocess.run(cmd)

print("Done")
