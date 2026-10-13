
\ = 64;

module test_standoff(dir_x, dir_z) {
    pcb_y_mount = 3.5;
    clearance_h = 15.0; // 1.5cm sensor-free slender zone
    
    rotate([-90, 0, 0]) {
        // 1. Slender tip (0 ~ 1.5cm from PCB face, Y = 3.5 to 18.5)
        translate([0, 0, pcb_y_mount])
            cylinder(r=3.8, h=clearance_h + 0.1);
            
        // 2. Smooth 45-degree widening taper (Y = 18.5 to 21.5)
        translate([0, 0, pcb_y_mount + clearance_h])
            cylinder(r1=3.8, r2=5.2, h=3.0);
            
        // 3. Thick heavy-duty reinforced body with wall gusset (Y = 21.5 to 50.0)
        translate([0, 0, pcb_y_mount + clearance_h + 3.0]) {
            hull() {
                cylinder(r=5.2, h=30.0);
                translate([dir_x * 12.0, dir_z * 12.0, 0])
                    cylinder(r=4.8, h=30.0);
            }
        }
    }
}

// Render one standoff
test_standoff(1, 1);
