/* 
 * Portable GM77/SEN0512 Barcode and QR Scanner Housing Design V2.1 (3D Printing Optimized)
 * 
 * Author: Antigravity AI (Google DeepMind)
 * Changelog:
 *   - 3D Print Optimization: Modular head body and handle separated completely.
 *   - Mating Flange: 4-point M3 bolt mounting interface (Pitch: 24x24mm).
 *   - Overhang Removal: Handle printed horizontally or flat to minimize support.
 *   - Mounting Standoffs: Internal standoff posts for ESP32 and GM77.
 *   - Top Lid Screen Mount: 4-point mounting posts for SSD1306 OLED screen.
 *   - Trigger Switch Hole: 12.2mm button hole on handle front.
 *   - Battery Chamber: 22mm hollow core inside handle for 18650 battery.
 *   - Ergonomic Grip: 3-stage finger grooves added.
 *   - Structural Ribs: Wall support ribs to prevent structural collapse.
 */

// [Global Parameters]
$fn = 60;
wall = 2.5;         // Wall thickness
clearance = 0.6;    // Tolerances

// [Head Part Dimensions]
head_w = 54.0;      // Width
head_l = 120.0;     // Length
head_h = 40.0;      // Height

// [Handle Part Dimensions]
handle_base_d = 34.0; // Bottom diameter (18650 battery size)
handle_top_d = 30.0;  // Top diameter (tapered)
handle_h = 105.0;     // Handle height
handle_angle = 15;    // Tilt angle (degree)

// [Component Sizes]
gm77_size = [27.5, 48.5, 14.0]; // GM77 Module
esp32_size = [30.0, 56.5, 15];
oled_size = [27.5, 27.5, 3];
battery_diam = 22.0;

// --- Main Control ---
render_part = "print_all"; // assembly, exploded, print_all, body, handle, lid

// 3D Printing alignment helpers
module print_body() {
    translate([0, 0, head_h]) rotate([180, 0, 0]) housing_body();
}

module print_handle() {
    rotate([180, 0, 0]) housing_handle();
}

module print_lid() {
    translate([0, 0, 3]) rotate([180, 0, 0]) housing_lid();
}

if (render_part == "assembly") {
    housing_body();
    translate([head_w/2, head_l*0.6, wall]) housing_handle();
    translate([0, 0, head_h - 3]) housing_lid();
}

if (render_part == "exploded") {
    housing_body();
    translate([head_w/2, head_l*0.6, -35]) housing_handle();
    translate([0, 0, head_h + 20]) housing_lid();
}

if (render_part == "print_all") {
    translate([0, 0, 0]) print_body();
    translate([head_w + 20, head_l*0.6, 0]) print_handle();
    translate([head_w * 2 + 40, 0, 0]) print_lid();
}

if (render_part == "body") print_body();
if (render_part == "handle") print_handle();
if (render_part == "lid") print_lid();

// --- 1. Housing Body ---
module housing_body() {
    difference() {
        union() {
            // [A] Outer Shell minus Inner Hollowing
            difference() {
                // Main Casing
                hull() {
                    translate([head_w/2, 5, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 10);
                    translate([head_w/2, head_l-5, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, head_h*0.85, 5, 8);
                }

                // Inner Hollowing (Tall Z-axis scale to keep top open)
                translate([head_w/2, head_l/2, head_h/2 + wall + 5])
                scale([0.9, 0.94, 1.2])
                hull() {
                    translate([0, -head_l/2 + wall, 0]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 8);
                    translate([0, head_l/2 - wall, 0]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, head_h*0.85, 5, 6);
                }
            }
            
            // [B] Handle Mounting Pad
            translate([head_w/2, head_l*0.6, wall])
            rounded_rect(handle_top_d + 6, handle_top_d + 6, 4, 5, true);
            
            // [C] ESP32 Standoffs (4 posts, 10mm high)
            translate([head_w/2, head_l - 35, wall]) {
                esp32_standoffs(h=10, d_outer=5.0);
            }
            
            // [D] GM77 Standoffs (4 posts, 10.5mm high)
            translate([head_w/2, 29.25, wall]) {
                gm77_standoffs(h=10.5, d_outer=5.0);
            }
            
            // Rib Reinforcement
            reinforcement_ribs();
        }

        // [E] Difference holes
        
        // ESP32 Screw holes (M3, diameter 2.5mm)
        translate([head_w/2, head_l - 35, wall - 1]) {
            esp32_screw_holes(h=15, d_inner=2.5);
        }
        
        // GM77 Screw holes (M2, diameter 1.8mm)
        translate([head_w/2, 29.25, wall - 1]) {
            gm77_screw_holes(h=15, d_inner=1.8);
        }

        // Battery Wiring Hole (22mm)
        translate([head_w/2, head_l*0.6, -2])
        cylinder(h=wall*4, d=battery_diam);

        // Flange Mounting Holes (M3, 2.5mm tap)
        translate([head_w/2, head_l*0.6, -2]) {
            flange_screw_holes(h=15, d=2.5);
        }

        // Scanner Window (Width: 22mm, Height: 15mm)
        translate([head_w/2 - 11, -2, head_h/2 - 7.5])
        cube([22, 10, 15]);
        
        // USB Port (Rear)
        translate([head_w/2 - 6, head_l - 10, wall + 2])
        cube([12, 15, 10]);

        // Ventilation Slots
        for(i=[0:6]) {
            translate([-1, 35 + i*8, 18]) rotate([0, 90, 0]) cylinder(h=head_w+2, d=2.5);
        }
        
        // Lid Mounting holes
        mount_points(3.0);
    }
}

// --- 2. Modular Handle ---
module housing_handle() {
    difference() {
        union() {
            // [A] Tapered Handle Body (15 degree tilt)
            rotate([handle_angle, 0, 0])
            difference() {
                // Tapered cylinder
                translate([0, 0, -handle_h])
                cylinder(h=handle_h, d1=handle_base_d, d2=handle_top_d);
                
                // Finger Grooves
                for (z_pos = [-38, -58, -78]) {
                    let (t = (z_pos + handle_h) / handle_h) {
                        let (d_pos = handle_base_d * (1-t) + handle_top_d * t) {
                            translate([0, -d_pos/2 + 1.2, z_pos])
                            rotate([0, 90, 0])
                            cylinder(h=handle_base_d + 10, d=9.0, center=true);
                        }
                    }
                }
            }
            
            // [B] Horizontal Mounting Flange
            translate([0, 0, -2])
            rounded_rect(handle_top_d + 6, handle_top_d + 6, 4, 5, true);

            // [C] Trigger Guard
            translate([0, 28 - head_l*0.6, 5])
            trigger_guard();
        }

        // [D] Internal Chambers & Screws
        
        // Battery Room (Hollow cylinder)
        rotate([handle_angle, 0, 0])
        translate([0, 0, -handle_h-1])
        cylinder(h=handle_h+10, d=battery_diam);
        
        // Flange Mounting Holes (M3 pass, 3.4mm)
        flange_screw_holes(h=10, d=3.4);
        
        // Trigger Button Hole (12.2mm)
        rotate([handle_angle, 0, 0])
        translate([0, -handle_top_d/2, -20])
        rotate([90, 0, 0])
        cylinder(h=wall*4, d=12.2, center=true);
    }
}

// --- 3. Housing Lid ---
module housing_lid() {
    difference() {
        union() {
            // Lid Cover Base (3mm thickness)
            hull() {
                translate([head_w/2, 5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w, 3, 5, 1.0);
                translate([head_w/2, head_l-5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, 3, 5, 1.0);
            }
            
            // OLED Bezel (10 degree tilt)
            translate([head_w/2, 55, 3])
            rotate([-10, 0, 0])
            difference() {
                rounded_rect(oled_size[0]+10, oled_size[1]+10, 6, 4, true);
                translate([0, 0, 2]) rounded_rect(oled_size[0]+2, oled_size[1]+2, 10, 2, true);
            }
            
            // OLED Standoffs (4mm height)
            translate([head_w/2, 55, 0])
            rotate([-10, 0, 0])
            translate([0, 0, -4])
            oled_standoffs(h=4, d_outer=4.5);
        }

        // OLED Window cutout
        translate([head_w/2, 55, -5])
        rotate([-10, 0, 0])
        rounded_rect(oled_size[0]-2, oled_size[1]-2, 20, 2, true);
        
        // OLED Screw holes (M2, 1.8mm)
        translate([head_w/2, 55, 0])
        rotate([-10, 0, 0])
        translate([0, 0, -5])
        oled_screw_holes(h=4.5, d_inner=1.8);

        // Mounting holes (M3 pass, 3.5mm)
        mount_points(3.5);
        
        // Engraving
        translate([head_w/2, head_l - 18, 2.5])
        linear_extrude(2)
        text("QR SCANNER GEN2", size=3.5, font="Arial:style=Bold", halign="center");
    }
}

// --- Component Mounting Modules ---

module esp32_standoffs(h, d_outer) {
    w_pitch = 25.5; 
    l_pitch = 51.5; 
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module esp32_screw_holes(h, d_inner) {
    w_pitch = 25.5;
    l_pitch = 51.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module gm77_standoffs(h, d_outer) {
    w_pitch = 22.5; 
    l_pitch = 40.5; 
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module gm77_screw_holes(h, d_inner) {
    w_pitch = 22.5;
    l_pitch = 40.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module oled_standoffs(h, d_outer) {
    w_pitch = 23.5; 
    l_pitch = 23.5; 
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module oled_screw_holes(h, d_inner) {
    w_pitch = 23.5;
    l_pitch = 23.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module flange_screw_holes(h, d) {
    w_pitch = 24.0; 
    l_pitch = 24.0; 
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d);
}

module reinforcement_ribs() {
    rib_y_positions = [55, 113];
    for (y_pos = rib_y_positions) {
        translate([head_w/2, y_pos, head_h/2 + wall])
        difference() {
            scale([0.9, 1.0, 0.88]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 1.5, 8);
            scale([0.72, 2.0, 0.68]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 8);
        }
    }
}

// --- Utility Modules ---

module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
        square([w-r*2, h-r*2], center=true);
    }
}

module trigger_guard() {
    difference() {
        rotate([0, 90, 0]) translate([0, 0, -3]) cylinder(h=6, d=28);
        rotate([0, 90, 0]) translate([2, 4, -5]) cylinder(h=10, d=22);
        translate([-5, -20, -15]) cube([10, 20, 30]);
    }
}

module mount_points(d) {
    inset = 7;
    translate([inset, inset, -10]) cylinder(h=60, d=d);
    translate([head_w-inset, inset, -10]) cylinder(h=60, d=d);
    translate([inset + 3, head_l-inset, -10]) cylinder(h=60, d=d);
    translate([head_w-inset - 3, head_l-inset, -10]) cylinder(h=60, d=d);
}
