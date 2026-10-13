import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# 1. Print orientation (rear_shell sitting on bed, looking inside the cradle)
# Z_print is up, bed is Z=0
subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/cradle_view_print.png",
    "-D", 'render_part="rear_shell"',
    "--camera", "0,0,20,55,0,35,180",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    scad_file
])

# 2. CAD orientation looking at the bottom of the cradle (negative Z in CAD)
subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/cradle_view_cad_bottom.png",
    "-D", 'render_part="part_rear_shell"',
    "--camera", "0,0,-20,60,0,180,180",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    scad_file
])

# 3. Looking at the back / floor of the cradle (Y = -28.5 to -39.5)
subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/cradle_view_floor.png",
    "-D", 'render_part="part_rear_shell"',
    "--camera", "0,-30,0,70,0,120,180",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    scad_file
])

print("Rendered cradle inspection views")
