import subprocess

# Let's cut the shell in half (Y > 0 or X > 0) so we can see inside with zero occlusion
test_scad = r'''
$fn = 64;
use <../3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad>

// Show half cross section in print orientation
difference() {
    rotate([-90, 0, 0]) apple_rear_shell();
    translate([0, 70, 25]) cube([140, 140, 140], center=true);
}
'''
with open("scratch/cut_rear_print.scad", "w") as f:
    f.write(test_scad)

subprocess.run([
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/cut_rear_print.png",
    "--camera", "0,0,25,65,0,45,220",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    "scratch/cut_rear_print.scad"
])

print("Rendered cut_rear_print.png")
