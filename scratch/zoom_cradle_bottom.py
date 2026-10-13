import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# Let's zoom into the bottom of the battery cradle in rear_shell
# Looking at negative Z in CAD (the bottom of the apple and bottom of the battery cradle)
subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/zoom_cradle_bottom.png",
    "-D", 'render_part="part_rear_shell"',
    "--camera", "0,-20,-30,65,0,180,90",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    scad_file
])

# Also zoom from slicer view (print orientation, looking at the bottom of the cradle)
subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/zoom_cradle_slicer.png",
    "-D", 'render_part="rear_shell"',
    "--camera", "0,-25,25,50,0,0,100",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    scad_file
])

print("Rendered cradle bottom close ups")
