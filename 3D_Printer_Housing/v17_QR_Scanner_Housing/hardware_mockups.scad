// hardware_mockups.scad - Reusable 3D hardware component drawings
// Target components: ESP32 DevKitC V4, SSD1306 OLED, GM77 Scanner, TP4056, VLT-VC013, MSL-1C2P, AK-TS-I015-42, 18650 Battery.

$fn = 16;

// ==========================================
// HARDWARE COMPONENT DRAWINGS
// ==========================================

// A. ESP32 DevKitC V4 (Size: 28.2 x 54.4 x 1.6 mm PCB)
module esp32_devkitc_mockup() {
    pcb_w = 28.2;
    pcb_l = 54.4;
    pcb_h = 1.6;
    
    // PCB Base
    color("DarkGreen") 
        difference() {
            cube([pcb_w, pcb_l, pcb_h], center=true);
            // Mounting holes (4 corners)
            for (x = [-11.5, 11.5], y = [-24.0, 24.0]) {
                translate([x, y, 0]) cylinder(h=pcb_h*2, d=2.0, center=true);
            }
        }
        
    // ESP32-WROOM-32E Shield Can (Metal cover)
    translate([0, 5.0, pcb_h/2 + 1.5]) {
        color("Silver") cube([18.0, 25.5, 3.0], center=true);
        // Antenna PCB region (black)
        translate([0, 12.75 + 3.0, -0.7]) 
            color([0.15, 0.15, 0.15]) cube([18.0, 6.0, 1.6], center=true);
    }
    
    // Micro-USB Port (front side)
    translate([0, -pcb_l/2 + 2.5, pcb_h/2 + 1.5])
        color("LightGray") cube([7.5, 5.5, 3.0], center=true);
        
    // Boot & EN push buttons
    translate([-7.0, -pcb_l/2 + 4.0, pcb_h/2 + 1.0]) {
        color("Silver") cube([3.5, 3.5, 2.0], center=true);
        color("Black") translate([0,0,1.0]) cylinder(h=1.0, d=1.8, center=true);
    }
    translate([7.0, -pcb_l/2 + 4.0, pcb_h/2 + 1.0]) {
        color("Silver") cube([3.5, 3.5, 2.0], center=true);
        color("Black") translate([0,0,1.0]) cylinder(h=1.0, d=1.8, center=true);
    }
    
    // Pin Headers
    color("Black") {
        translate([-pcb_w/2 + 1.27, 0, -pcb_h/2 - 1.25]) cube([2.54, pcb_l - 4, 2.5], center=true);
        translate([pcb_w/2 - 1.27, 0, -pcb_h/2 - 1.25]) cube([2.54, pcb_l - 4, 2.5], center=true);
    }
    color("Gold") {
        for (y = [-23.0 : 2.54 : 23.0]) {
            translate([-pcb_w/2 + 1.27, y, -pcb_h/2 - 4.5]) cylinder(h=6.0, d=0.64, center=true);
            translate([pcb_w/2 - 1.27, y, -pcb_h/2 - 4.5]) cylinder(h=6.0, d=0.64, center=true);
        }
    }
}

// B. SSD1306 OLED Module (0.96 inch, Size: 27.3 x 27.3 x 1.2 mm PCB)
module ssd1306_oled_mockup() {
    oled_w = 27.3;
    oled_l = 27.3;
    oled_h = 1.2;
    
    // PCB Base
    color("RoyalBlue")
        difference() {
            cube([oled_w, oled_l, oled_h], center=true);
            // 4 corner mount holes
            for (x = [-11.0, 11.0], y = [-11.0, 11.0]) {
                translate([x, y, 0]) cylinder(h=oled_h*3, d=2.0, center=true);
            }
        }
        
    // OLED Glass Screen (Active area centered)
    translate([0, -2.0, oled_h/2 + 0.8]) {
        color([0.05, 0.05, 0.05]) cube([26.0, 16.0, 1.6], center=true);
        // Active Display pixels
        translate([0, 0, 0.81]) 
            color("Cyan") cube([21.8, 11.0, 0.01], center=true);
    }
    
    // I2C 4-Pin Header
    translate([0, oled_l/2 - 2.0, -oled_h/2 - 1.25]) {
        color("Black") cube([10.16, 2.54, 2.5], center=true);
        color("Gold") {
            for (x = [-3.81 : 2.54 : 3.81]) {
                translate([x, 0, -3.0]) cylinder(h=6.0, d=0.64, center=true);
            }
        }
    }
}

// C. GM77 Barcode & QR Code Scanner Module (Size: 27.5 x 48.5 x 14.0 mm)
module gm77_scanner_mockup() {
    s_w = 27.5;
    s_l = 48.5;
    s_h = 14.0;
    
    // Main Casing
    color([0.25, 0.25, 0.27])
        difference() {
            cube([s_w, s_l, s_h], center=true);
            // Beveled corners
            translate([-s_w/2, -s_l/2, 0]) rotate([0, 0, 45]) cube([6.0, 6.0, s_h + 1], center=true);
            translate([s_w/2, -s_l/2, 0]) rotate([0, 0, -45]) cube([6.0, 6.0, s_h + 1], center=true);
        }
        
    // Scanner Lens Window
    translate([0, -s_l/2 + 0.2, 0]) {
        color("Black") cube([20.0, 0.5, 8.0], center=true);
        // Glass Lens
        translate([0, -0.1, 0]) 
            color("Cyan", 0.6) cube([14.0, 0.4, 6.0], center=true);
        // Status LED indicators
        translate([-8.0, -0.2, 3.0]) color("Green") sphere(r=0.6);
        translate([8.0, -0.2, 3.0]) color("Red") sphere(r=0.6);
    }
    
    // Bottom PCB and mounting tab details
    translate([0, 0, -s_h/2 + 0.5]) {
        color("DarkGreen") cube([s_w - 2.0, s_l - 2.0, 1.0], center=true);
        color("Gold") {
            for (x = [-10.0, 10.0], y = [-20.0, 20.0]) {
                translate([x, y, -0.5]) cylinder(h=1.2, d=2.0, center=true);
            }
        }
    }
}

// D. Voltly VLT-VC013 DC-DC Boost Module (Size: 22.0 x 11.0 x 3.6 mm)
module booster_module_vlt_vc013() {
    b_w = 11.0;
    b_l = 22.0;
    b_h = 1.2;
    
    // PCB (Blue/Teal)
    color([0.0, 0.4, 0.4]) cube([b_w, b_l, b_h], center=true);
    
    // Inductor block (grey)
    translate([0, -3.0, b_h/2 + 1.2])
        color("DimGray") cube([6.0, 6.0, 2.4], center=true);
        
    // Boost Controller IC
    translate([0, 4.0, b_h/2 + 0.5])
        color("Black") cube([4.0, 3.0, 1.0], center=true);
        
    // Solder pads
    color("Gold") {
        translate([-b_w/2 + 1.5, -b_l/2 + 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([b_w/2 - 1.5, -b_l/2 + 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([-b_w/2 + 1.5, b_l/2 - 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([b_w/2 - 1.5, b_l/2 - 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
    }
}

// E. TP4056 USB-C Li-ion Charger Module [SZH-LIP001] (Size: 27.5 x 16.5 x 4.0 mm)
module charger_module_tp4056() {
    c_w = 16.5;
    c_l = 27.5;
    c_h = 1.2;
    
    // PCB
    color([0.0, 0.1, 0.5]) cube([c_w, c_l, c_h], center=true);
    
    // USB-C Connector
    translate([0, -c_l/2 + 4.0, c_h/2 + 1.6])
        color("LightGray") cube([9.0, 6.5, 3.2], center=true);
        
    // TP4056 chip
    translate([-3.0, 3.0, c_h/2 + 0.5])
        color("Black") cube([4.0, 5.0, 1.0], center=true);
        
    // DW01 Protection chip
    translate([3.0, 3.0, c_h/2 + 0.5])
        color("Black") cube([3.0, 3.0, 1.0], center=true);
        
    // Solder pads
    color("Gold") {
        translate([-c_w/2 + 1.5, 9.0, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([c_w/2 - 1.5, 9.0, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([-c_w/2 + 1.5, c_l/2 - 1.5, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([c_w/2 - 1.5, c_l/2 - 1.5, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
    }
}

// F. MSL-1C2P Slide Switch (Size: 8.5 x 3.5 x 3.5 mm body, 2.0 mm knob)
module slide_switch_msl_1c2p() {
    s_w = 3.5;
    s_l = 8.5;
    s_h = 3.5;
    
    // Metal housing
    color("Silver") cube([s_w, s_l, s_h], center=true);
    
    // Slide knob
    translate([0, 0, s_h/2 + 1.0])
        color("Red") cube([1.5, 2.5, 2.0], center=true);
        
    // Pins
    color("Silver") {
        translate([0, -2.5, -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
        translate([0, 0,    -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
        translate([0, 2.5,  -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
    }
}

// G. Tact Trigger Switch (AK-TS-I015-42, Size: 6.0 x 6.0 x 11.0 mm H11)
module tact_switch_h11() {
    b_w = 6.0;
    b_l = 6.0;
    b_h = 3.5;
    
    // Base plastic body
    color([0.15, 0.15, 0.15]) cube([b_w, b_l, b_h], center=true);
    
    // Metal plate
    translate([0,0,b_h/2 + 0.05])
        color("Silver") cube([b_w - 0.2, b_l - 0.2, 0.1], center=true);
        
    // Switch Button Stem
    translate([0, 0, b_h/2 + 3.75])
        color("DimGray") cylinder(h=7.5, d=3.0, center=true);
        
    // Pins
    color("Silver") {
        for (x = [-2.8, 2.8], y = [-2.2, 2.2]) {
            translate([x, y, -b_h/2 - 1.0]) cylinder(h=2.0, d=0.6, center=true);
        }
    }
}

// H. 18650 Battery Cell (BT187, Size: D18.4 x 65.2 mm with pre-soldered wires)
module battery_18650_wire() {
    bat_d = 18.4;
    bat_l = 65.2;
    
    // Battery Cylinder wrap
    color([0.2, 0.5, 0.9])
        rotate([90, 0, 0])
            cylinder(h=bat_l, d=bat_d, center=true);
            
    // Positive button cap
    translate([0, bat_l/2 + 0.5, 0])
        rotate([90,0,0])
            color("Silver") cylinder(h=1.0, d=6.0, center=true);
}
