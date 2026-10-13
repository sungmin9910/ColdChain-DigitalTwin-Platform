
\ = 64;
use <../3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/21_apple_sensor_pod.scad>;

// Let's test the reinforced standoff module
module stepped_standoff(dir_x, dir_z) {
    pcb_y_mount = 3.5;
    sensor_clearance_h = 15.0; // 1.5cm slender zone for sensor clearance!
    transition_h = 5.0;        // 5mm smooth taper transition
    
    rotate([-90, 0, 0]) {
        // Zone 1: Pure slender cylinder for the first 1.5cm (Y = 3.5 to 18.5)
        translate([0, 0, pcb_y_mount])
            cylinder(r=3.8, h=sensor_clearance_h);
            
        // Zone 2: Smooth 45-degree conical taper (Y = 18.5 to 23.5)
        translate([0, 0, pcb_y_mount + sensor_clearance_h])
            cylinder(r1=3.8, r2=5.0, h=transition_h);
            
        // Zone 3: Heavy-duty wall gusset/wing from Y >= 23.5 to 50.0 (deep inside dome)
        translate([0, 0, pcb_y_mount + sensor_clearance_h + transition_h]) {
            hull() {
                cylinder(r=5.0, h=30.0);
                translate([dir_x * 12.0, dir_z * 12.0, 0])
                    cylinder(r=4.5, h=30.0);
            }
        }
    }
}

// Render test
stepped_standoff(1, 1);
