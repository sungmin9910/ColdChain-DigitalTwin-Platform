
$fn = 64;
use <../3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad>

// Cross section along X=0 plane
projection(cut=true) {
    rotate([0, 90, 0])
        apple_rear_shell();
}
