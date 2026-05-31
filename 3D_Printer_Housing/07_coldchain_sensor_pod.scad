/* 
 * Cold Chain Digital Twin Sensor Tag Pod Housing V1.0
 * 
 * Author: Antigravity AI (Google DeepMind)
 * Description: 
 *   An industrial-grade, compact, and rugged housing for the cold chain tracking sensor node.
 *   Contains compartments for ESP32, DHT22 (with slanted ventilation grilles), MPU6050 IMU, 
 *   and an 18650 rechargeable battery. Features external mounting ears for shipping container installation.
 */

$fn = 60;
wall = 2.0;         // Wall thickness
clearance = 0.4;    // Assembly tolerances

// [Outer Dimensions]
pod_w = 68.0;       // Total width
pod_l = 92.0;       // Total length (excluding mounting ears)
pod_h = 28.0;       // Total height

// [Component Pocket Sizes]
esp32_size = [28.5, 52.5, 8.0];   // ESP32 DevKit
mpu6050_size = [15.5, 20.5, 5.0]; // MPU6050 Accelerometer
dht22_size = [16.0, 26.0, 10.0];   // DHT22 Temp/Humidity
battery_diam = 19.0;              // 18650 battery cell diameter
battery_len = 66.0;               // 18650 battery cell length

// --- Main Control ---
render_part = "assembly"; // assembly, exploded, print_all, body, lid, cross_section

// 3D Printing alignment helpers
module print_body() {
    sensor_pod_body();
}

module print_lid() {
    translate([0, 0, 4]) rotate([180, 0, 0]) sensor_pod_lid();
}

if (render_part == "assembly") {
    sensor_pod_body();
    translate([0, 0, pod_h * 0.7 + 2]) sensor_pod_lid();
}

if (render_part == "exploded") {
    sensor_pod_body();
    translate([0, 0, pod_h * 0.7 + 25]) sensor_pod_lid();
}

if (render_part == "print_all") {
    translate([0, 0, 0]) print_body();
    translate([pod_w + 15, 0, pod_h * 0.3]) print_lid();
}

if (render_part == "body") print_body();
if (render_part == "lid") print_lid();

if (render_part == "cross_section") {
    difference() {
        union() {
            sensor_pod_body();
            translate([0, 0, pod_h * 0.7 + 2]) sensor_pod_lid();
        }
        // Slice the assembly in half along the longitudinal symmetry plane (X = 0)
        translate([0, -100, -50])
        cube([100, 300, 200]);
    }
}

// --- 1. Pod Base Body ---
module sensor_pod_body() {
    base_h = pod_h * 0.7; // 70% of height is base body
    
    difference() {
        union() {
            // Main rounded box outer shell
            rounded_box(pod_w, pod_l, base_h, 8);
            
            // Mounting ears (screwing tabs on left/right ends)
            translate([-pod_w/2 - 6, 0, 2])
            mounting_ear();
            translate([pod_w/2 + 6, 0, 2])
            rotate([0, 0, 180])
            mounting_ear();
            
            // Internal support frames (Pockets)
            
            // A. ESP32 DevKit Pocket (X+ side)
            translate([15.5, -10, base_h/2 - 3])
            pcb_pocket(esp32_size[0], esp32_size[1], support_h=5, pocket_depth=3.5, wall_t=1.8, clearance_t=clearance);
            
            // B. MPU6050 Accelerometer Pocket (X+ side, forward)
            translate([15.5, 27.5, base_h/2 - 3.5])
            pcb_pocket(mpu6050_size[0], mpu6050_size[1], support_h=4, pocket_depth=3, wall_t=1.8, clearance_t=clearance);
            
            // C. DHT22 Pocket (X- side, forward)
            translate([-20.0, 24.0, base_h/2 - 2])
            pcb_pocket(dht22_size[0], dht22_size[1], support_h=6, pocket_depth=3, wall_t=1.8, clearance_t=clearance);
            
            // D. Battery Cradle Ribs (X- side)
            translate([-20.0, -20.0, 0])
            battery_cradle(battery_diam, 35, 12);
        }

        // --- Subtract cutouts ---
        
        // Hollowing out the main base cavity
        translate([0, 0, wall])
        rounded_box(pod_w - wall*2, pod_l - wall*2, base_h, 6);
        
        // ESP32 USB Port cutout (Rear wall)
        translate([15.5, -pod_l/2 - 2, 8.5])
        cube([12, 10, 7.5], center=true);
        
        // Power Slide Switch Cutout (Side wall)
        translate([pod_w/2 - 2, 15, 9.5])
        cube([10, 12.5, 6.5], center=true);

        // Slanted Louver Air Vents for DHT22 (Front-Left wall)
        // Angle-cut slots to let air in but keep drops out
        for (y_pos = [14, 21, 28, 35]) {
            translate([-pod_w/2 - 1, y_pos, base_h/2 + 2])
            rotate([25, 0, 0])
            cube([10, 3.5, 7.0], center=true);
        }
        
        // 4 corner screw holes (M3 tap, D=2.5mm)
        corner_screw_holes(h=15, d=2.5);
    }
}

// --- 2. Pod Lid Cover ---
module sensor_pod_lid() {
    lid_h = pod_h * 0.3; // 30% of height is lid
    
    difference() {
        union() {
            // Main lid outer rounded shell
            rounded_box(pod_w, pod_l, lid_h, 8);
            
            // Inner alignment mating ring
            translate([0, 0, -2])
            difference() {
                rounded_box(pod_w - wall*2 - 0.4, pod_l - wall*2 - 0.4, 4, 6);
                translate([0, 0, -1])
                rounded_box(pod_w - wall*4, pod_l - wall*4, 6, 5);
            }
        }
        
        // Hollowing out the lid
        translate([0, 0, -wall])
        rounded_box(pod_w - wall*2, pod_l - wall*2, lid_h, 6);
        
        // Status LED Hole (D = 5.2mm)
        translate([15.5, 10, -2])
        cylinder(h=10, d=5.2, center=true);
        
        // 4 corner screw countersink holes (M3 pass, D=3.4mm, Head D=6mm)
        corner_screw_holes(h=20, d=3.4);
        corner_screw_countersinks(h=20, d=6.0);
        
        // Decorative / Branding Engravings
        translate([0, -15, lid_h - 1.2])
        linear_extrude(2) {
            text("COLDCHAIN SENSOR TAG", size=3.5, font="Arial:style=Bold", halign="center", valign="center");
        }
        
        // Simple Geometric Digital Twin Logo (Thermometer + WiFi shape)
        translate([0, 10, lid_h - 1.2])
        linear_extrude(2)
        logo_engraving();
    }
}

// --- Helper & Utility Modules ---

module rounded_box(w, l, h, r) {
    translate([0, 0, h/2])
    linear_extrude(height=h, center=true)
    offset(r=r)
    square([w - r*2, l - r*2], center=true);
}

module mounting_ear() {
    difference() {
        hull() {
            cylinder(h=4, r=8, center=true);
            translate([6, -10, 0]) cube([1, 20, 4], center=true);
        }
        // Screw hole for mounting (M4 bolt, D=4.2mm)
        cylinder(h=10, d=4.2, center=true);
    }
}

module pcb_pocket(pcb_w, pcb_l, support_h, pocket_depth, wall_t, clearance_t) {
    difference() {
        cube([pcb_w + 2*clearance_t + 2*wall_t, pcb_l + 2*clearance_t + 2*wall_t, support_h + pocket_depth], center=true);
        
        translate([0, 0, support_h/2])
        cube([pcb_w + 2*clearance_t, pcb_l + 2*clearance_t, pocket_depth + 0.1], center=true);
        
        translate([0, 0, -pocket_depth/2])
        cube([pcb_w - 2*wall_t, pcb_l - 2*wall_t, support_h + 0.1], center=true);
    }
}

module battery_cradle(d, length, support_w) {
    // Semi-cylindrical cradle ribs to hold 18650 battery cell
    difference() {
        union() {
            translate([0, -length/2 + 8, d/4]) rotate([90, 0, 0]) cylinder(h=6, d=d+4, center=true);
            translate([0, length/2 - 8, d/4]) rotate([90, 0, 0]) cylinder(h=6, d=d+4, center=true);
            
            // Floor bracket
            translate([0, 0, 2]) cube([d+4, length, 4], center=true);
        }
        // Subtract battery cylinder for the cell to sit snuggly
        translate([0, 0, d/2 + 2.5])
        rotate([90, 0, 0])
        cylinder(h=length + 10, d=d + clearance, center=true);
    }
}

module corner_screw_holes(h, d) {
    cx = pod_w/2 - 5.5;
    cy = pod_l/2 - 5.5;
    translate([-cx, -cy, -h/2 + pod_h]) cylinder(h=h, d=d);
    translate([cx, -cy, -h/2 + pod_h]) cylinder(h=h, d=d);
    translate([-cx, cy, -h/2 + pod_h]) cylinder(h=h, d=d);
    translate([cx, cy, -h/2 + pod_h]) cylinder(h=h, d=d);
}

module corner_screw_countersinks(h, d) {
    cx = pod_w/2 - 5.5;
    cy = pod_l/2 - 5.5;
    translate([-cx, -cy, pod_h * 0.3 - 2]) cylinder(h=h, d=d);
    translate([cx, -cy, pod_h * 0.3 - 2]) cylinder(h=h, d=d);
    translate([-cx, cy, pod_h * 0.3 - 2]) cylinder(h=h, d=d);
    translate([cx, cy, pod_h * 0.3 - 2]) cylinder(h=h, d=d);
}

module logo_engraving() {
    // Simple thermometer shape
    circle(r=2.5);
    translate([0, 2.5, 0]) square([2, 5], center=true);
    translate([0, 5, 0]) circle(r=1);
    
    // Wi-Fi signal arcs
    translate([5, 0, 0]) circle(r=0.8);
    difference() {
        translate([5, 0, 0]) circle(r=4.5);
        translate([5, 0, 0]) circle(r=3.0);
        translate([1.5, -5, 0]) square([10, 10]);
    }
    difference() {
        translate([5, 0, 0]) circle(r=8.0);
        translate([5, 0, 0]) circle(r=6.5);
        translate([1.5, -10, 0]) square([15, 20]);
    }
}
