/* 
 * Portable GM77/SEN0512 Barcode and QR Scanner Housing Design V3.0 (Ergonomic & Compact)
 * 
 * Author: Antigravity AI (Google DeepMind)
 * Changelog:
 *   - Ergonomic Redesign: Smoothly curved head using multiple slices.
 *   - S-Curve Handle: Ergonomic handle with palm bulge and flared pinky rest.
 *   - PCB Pockets: Snap/slide-in pocket holders with support shelves for GM77, ESP32, and OLED.
 *   - Cross-section View: Symmetrical split view option for internal inspection.
 *   - Optimized Size: Compact design (head length reduced from 120mm to 112mm, width to 48mm).
 */

// [Global Parameters]
$fn = 60;
wall = 2.5;         // Wall thickness
clearance = 0.4;    // Tolerances

// [Head Part Dimensions]
head_w = 48.0;      // Width (optimized from 54)
head_l = 112.0;     // Length (optimized from 120)
head_h = 36.0;      // Height (optimized from 40)

// [Handle Part Dimensions]
handle_base_d = 34.0; // Bottom diameter
handle_top_d = 28.0;  // Top diameter (tapered for better grip)
handle_h = 90.0;      // Handle height (shorter and more compact)
handle_angle = 18;    // Tilt angle (degree) for natural wrist angle

// [Component Sizes]
gm77_size = [27.5, 48.5, 14.0]; // GM77 Module
esp32_size = [30.0, 56.5, 15.0];
oled_size = [27.5, 27.5, 3.0];
battery_diam = 22.0;

// --- Main Control ---
render_part = "print_all"; // assembly, exploded, print_all, body, handle, lid, cross_section

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

if (render_part == "cross_section") {
    difference() {
        union() {
            housing_body();
            translate([head_w/2, head_l*0.6, wall]) housing_handle();
            translate([0, 0, head_h - 3]) housing_lid();
        }
        // Slice the assembly in half at X = head_w/2
        translate([head_w/2, -50, -100])
        cube([200, 300, 300]);
    }
}

// --- 1. Housing Body ---
module housing_body() {
    difference() {
        union() {
            // [A] Outer Shell minus Inner Hollowing (Curved Head)
            difference() {
                housing_shape(wall_thick=0, extend_top=false);
                housing_shape(wall_thick=wall, extend_top=true);
            }
            
            // [B] Handle Mounting Pad
            translate([head_w/2, head_l*0.6, wall])
            rounded_rect(handle_top_d + 6, handle_top_d + 6, 4, 5, true);
            
            // [C] ESP32 Pocket Holder (support_h = 10mm, pocket_depth = 3mm)
            translate([head_w/2, head_l - 32.0, wall + 6.5]) {
                pcb_pocket(esp32_size[0], esp32_size[1], support_h=10, pocket_depth=3, wall_t=2, clearance_t=clearance);
            }
            
            // [D] GM77 Pocket Holder (support_h = 10.5mm, pocket_depth = 3mm)
            translate([head_w/2, 27.0, wall + 6.75]) {
                pcb_pocket(gm77_size[0], gm77_size[1], support_h=10.5, pocket_depth=3, wall_t=2, clearance_t=clearance);
            }
            
            // Rib Reinforcement
            reinforcement_ribs();
        }

        // [E] Difference holes
        
        // ESP32 Screw holes (M3, diameter 2.5mm)
        translate([head_w/2, head_l - 32.0, wall - 1]) {
            esp32_screw_holes(h=20, d_inner=2.5);
        }
        
        // GM77 Screw holes (M2, diameter 1.8mm)
        translate([head_w/2, 27.0, wall - 1]) {
            gm77_screw_holes(h=20, d_inner=1.8);
        }

        // Battery Wiring Hole (22mm)
        translate([head_w/2, head_l*0.6, -2])
        cylinder(h=wall*4, d=battery_diam);

        // Flange Mounting Holes (M3, 2.5mm tap)
        translate([head_w/2, head_l*0.6, -2]) {
            flange_screw_holes(h=15, d=2.5);
        }

        // Scanner Window (Width: 22mm, Height: 15mm)
        // Positioned to align with the camera lens
        translate([head_w/2 - 11, -2, 10.5])
        cube([22, 10, 15]);
        
        // USB Port (Rear)
        translate([head_w/2 - 6, head_l - 10, wall + 2])
        cube([12, 15, 10]);

        // Ventilation Slots
        for(i=[0:5]) {
            translate([-1, 35 + i*8, 18]) rotate([0, 90, 0]) cylinder(h=head_w+2, d=2.5);
        }
        
        // Lid Mounting holes
        mount_points(3.0);
    }
}

// --- Head Geometry Helper Modules ---
module slice(y, w, h, r, wall_thick=0, extend_top=false) {
    real_w = max(4, w - 2 * wall_thick);
    real_h = max(4, h - 2 * wall_thick) + (extend_top ? 20 : 0);
    real_r = max(1.0, r - wall_thick);
    z_center = real_h/2 + wall_thick;
    translate([head_w/2, y, z_center])
    rotate([90, 0, 0])
    rounded_rect(real_w, real_h, 1.0, real_r, true);
}

module housing_shape(wall_thick=0, extend_top=false) {
    y_front = 2 + wall_thick;
    y_rear = head_l - 2 - wall_thick;
    
    hull() {
        // Front slice: slightly smaller nose for camera window
        slice(y_front, head_w - 6, head_h - 6, 8, wall_thick, extend_top);
        // Front-middle: main body volume, highest point
        slice(head_l * 0.25, head_w, head_h, 12, wall_thick, extend_top);
        // Mid-rear: tapered transition
        slice(head_l * 0.65, head_w * 0.9, head_h * 0.9, 10, wall_thick, extend_top);
        // Rear slice: tapered tail
        slice(y_rear, head_w * 0.78, head_h * 0.78, 8, wall_thick, extend_top);
    }
}

// --- 2. Modular Handle ---
module housing_handle() {
    difference() {
        union() {
            // [A] Ergonomic S-Curve Handle Body (18 degree tilt)
            rotate([handle_angle, 0, 0])
            difference() {
                // Curved hull body
                hull() {
                    handle_slice(0, 0.0, handle_top_d/2);
                    handle_slice(-20, 1.0, 15.5);
                    handle_slice(-45, -1.0, 15.0);
                    handle_slice(-70, -2.5, 16.0);
                    handle_slice(-handle_h, -4.0, 18.0); // Flared base
                }
                
                // Ergonomic Finger Grooves on the front grip (-Y side)
                for (z_pos = [-30, -50, -70]) {
                    let (y_val = (z_pos == -30) ? -14.0 :
                                 (z_pos == -50) ? -15.2 : -17.2) {
                        translate([0, y_val, z_pos])
                        rotate([0, 90, 0])
                        cylinder(h=handle_base_d + 10, d=8.5, center=true);
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

module handle_slice(z, y_offset, r) {
    translate([0, y_offset, z])
    cylinder(h=0.1, r=r, center=true);
}

// --- 3. Housing Lid ---
module housing_lid() {
    difference() {
        union() {
            // Lid Cover Base (3mm thickness)
            hull() {
                translate([head_w/2, 2.5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w - 6, 3, 5, 1.0);
                translate([head_w/2, head_l * 0.25, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w, 3, 5, 1.0);
                translate([head_w/2, head_l * 0.65, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w * 0.9, 3, 5, 1.0);
                translate([head_w/2, head_l - 2.5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w * 0.78, 3, 5, 1.0);
            }
            
            // OLED Bezel (10 degree tilt)
            translate([head_w/2, 55, 3])
            rotate([-10, 0, 0])
            difference() {
                rounded_rect(oled_size[0]+10, oled_size[1]+10, 6, 4, true);
                translate([0, 0, 2]) rounded_rect(oled_size[0]+2, oled_size[1]+2, 10, 2, true);
            }
            
            // OLED Pocket Holder (replaces standalone standoffs)
            // Sits underneath the lid (extends from Z=0 to Z=-6)
            translate([head_w/2, 55, 0])
            rotate([-10, 0, 0])
            translate([0, 0, -3]) {
                pcb_pocket(oled_size[0], oled_size[1], support_h=4, pocket_depth=2, wall_t=2, clearance_t=clearance);
            }
        }

        // OLED Window cutout
        translate([head_w/2, 55, -5])
        rotate([-10, 0, 0])
        rounded_rect(oled_size[0]-2, oled_size[1]-2, 20, 2, true);
        
        // OLED Screw holes (M2, 1.8mm)
        translate([head_w/2, 55, 0])
        rotate([-10, 0, 0])
        translate([0, 0, -8])
        oled_screw_holes(h=10, d_inner=1.8);

        // Mounting holes (M3 pass, 3.5mm)
        mount_points(3.5);
        
        // Engraving
        translate([head_w/2, head_l - 18, 2.5])
        linear_extrude(2)
        text("QR SCANNER GEN2", size=3.5, font="Arial:style=Bold", halign="center");
    }
}

// --- Component Mounting Modules ---

module pcb_pocket(pcb_w, pcb_l, support_h, pocket_depth, wall_t, clearance_t) {
    difference() {
        // Outer body: fits the PCB size + wall + clearance
        cube([pcb_w + 2*clearance_t + 2*wall_t, pcb_l + 2*clearance_t + 2*wall_t, support_h + pocket_depth], center=true);
        
        // Inner pocket: cutout where the PCB board itself sits
        translate([0, 0, support_h/2])
        cube([pcb_w + 2*clearance_t, pcb_l + 2*clearance_t, pocket_depth + 0.1], center=true);
        
        // Bottom clearance: keeps the center open for components, leaving a support shelf
        translate([0, 0, -pocket_depth/2])
        cube([pcb_w - 2*wall_t, pcb_l - 2*wall_t, support_h + 0.1], center=true);
    }
}

module esp32_screw_holes(h, d_inner) {
    w_pitch = 25.5;
    l_pitch = 51.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module gm77_screw_holes(h, d_inner) {
    w_pitch = 22.5;
    l_pitch = 40.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
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
    rib_y_positions = [head_l * 0.5, head_l * 0.85];
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
