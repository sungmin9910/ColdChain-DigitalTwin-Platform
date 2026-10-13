# Let's inspect a 2D cross section along X=0 (YZ plane) of apple_rear_shell()
# This will show us EXACTLY what the cross section looks like!

import subprocess

test_scad = r'''
$fn = 64;
use <../3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad>

// Cross section along X=0 plane
projection(cut=true) {
    rotate([0, 90, 0])
        apple_rear_shell();
}
'''
with open("scratch/cut_x0.scad", "w") as f:
    f.write(test_scad)

subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/cut_x0.png",
    "--camera", "0,0,0,0,0,0,120",
    "--imgsize", "900,900",
    "scratch/cut_x0.scad"
])

print("Rendered 2D cross section at X=0")
