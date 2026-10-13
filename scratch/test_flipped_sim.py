import subprocess
import os

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# Let's test rotating rear_shell by 180 degrees from its current print orientation:
# Current: rotate([-90, 0, 0]) apple_rear_shell()
# Flipped 180: rotate([180, 0, 0]) rotate([-90, 0, 0]) apple_rear_shell() = rotate([90, 0, 0]) apple_rear_shell()
# But wait! If rotated by [90, 0, 0], let's check its Z position:
# In apple_rear_shell(), Y <= 0.
# Under rotate([90, 0, 0]):
# Z' = -Y * sin(90) = -Y? Wait:
# rot around X by +90:
# (x, y, z) -> (x, y*cos90 - z*sin90, y*sin90 + z*cos90) = (x, -z, y).
# So Z' = y <= 0! It would be below the bed!
# To place it on the bed, we must translate it up so min Z = 0!

test_scad = r'''
$fn = 64;
use <../3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad>

// Flipped 180 degrees: Dome on the bed, rim facing UP like a bowl
module rear_shell_flipped() {
    // Current is rotate([-90, 0, 0]) apple_rear_shell()
    // Flipping 180 around X or Y:
    rotate([90, 0, 0])
    translate([0, 50.0, 0])
        apple_rear_shell();
}

rear_shell_flipped();
'''
with open("scratch/test_flipped.scad", "w") as f:
    f.write(test_scad)

subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/flipped_rear_view.png",
    "--camera", "0,0,25,60,0,45,220",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    "scratch/test_flipped.scad"
])

print("Rendered flipped rear shell view")
