
$fn = 64;
use <../3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad>

// Show half cross section in print orientation
difference() {
    rotate([-90, 0, 0]) apple_rear_shell();
    translate([0, 70, 25]) cube([140, 140, 140], center=true);
}
