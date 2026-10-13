import subprocess
import os

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
v21_dir = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v21_Apple_Sensor_Pod_2Piece5000mAh"
scad = os.path.join(v21_dir, "21_apple_sensor_pod.scad")

# Front shell inside view: looking into the cavity from -Y
f_png = os.path.join(v21_dir, "21_front_shell_inside.png")
subprocess.run([
    openscad, "-o", f_png,
    "-D", 'render_part="part_front_shell"',
    "--camera", "0,0,5,65,0,0,220",
    "--imgsize", "1024,1024",
    "--colorscheme", "Cornfield",
    scad
])

# Rear shell cradle view: looking into the cradle from +Y
r_png = os.path.join(v21_dir, "21_rear_shell_cradle.png")
subprocess.run([
    openscad, "-o", r_png,
    "-D", 'render_part="part_rear_shell"',
    "--camera", "0,0,5,65,0,180,220",
    "--imgsize", "1024,1024",
    "--colorscheme", "Cornfield",
    scad
])

print("Interior views rendered successfully!")
