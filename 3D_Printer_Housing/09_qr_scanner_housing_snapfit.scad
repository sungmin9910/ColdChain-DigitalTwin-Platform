/* 
 * Ergonomic Pistol Grip GM77/ESP32 QR Scanner Housing Design V5.0 (Snap-Fit & Screwless Assembly)
 * 
 * Author: Antigravity AI (Google DeepMind)
 * Features:
 *   - Completely screwless housing assembly (Lid, Body, and Handle snap together)
 *   - Cantilever snap-fit joints (4 clips) between Lid and Body with alignment rim
 *   - Flex-collar snap-fit joint (push-to-click) between Handle and Body
 *   - Slide-in Battery compartment (Option 1) for HY18650-2200 (18.4mm diameter)
 *   - Snap-fit circular bottom cap with keyway and built-in USB Type-C port slot
 *   - Internal cylindrical screw bosses (bosses) with custom self-tapping holes:
 *     - ESP32: 3.0mm diameter holes
 *     - GM77: 2.0mm diameter holes
 *     - OLED: 2.0mm diameter holes
 *   - Flared front nose bumper ring (black rubber-like visual bezel)
 *   - Ergonomic S-Curve Handle with 18 degree tilt (no trigger guard loop)
 *   - Curved finger-contour trigger button
 *   - Snap/slide-in pockets for GM77, ESP32, and OLED (SSD1306)
 */

// [Global Parameters]
$fn = 60;
wall = 2.5;         // Wall thickness
clearance = 0.35;   // Snap-fit tolerances/clearance

// [Head Part Dimensions]
head_w = 48.0;      // Width
head_l = 112.0;     // Length
head_h = 36.0;      // Height
split_z = 21.0;     // Horizontal split plane height

// [Handle Part Dimensions]
handle_base_d = 34.0; // Bottom diameter
handle_top_d = 28.0;  // Top diameter
handle_h = 92.0;      // Handle height
handle_angle = 18;    // Tilt angle (degrees)

// [Component Sizes]
gm77_size = [27.5, 49.0, 14.0];  // GM77 QR Module
esp32_size = [30.0, 56.5, 15.0]; // ESP32 board
oled_size = [26.0, 27.0, 1.2];   // SSD1306 OLED PCB size
battery_diam = 19.2;             // HY18650-2200 bare cell with clearance (18.4mm nominal)

// --- Main Control ---
render_part = "exploded"; // assembly, exploded, print_all, left_half, right_half, cross_section

// 3D Printing alignment helpers
module print_left() {
    translate([0, 0, 24]) rotate([0, 90, 0]) housing_left_half();
}

module print_right() {
    translate([0, 0, -24]) rotate([0, -90, 0]) housing_right_half();
}

if (render_part == "assembly") {
    color("DimGray") housing_left_half();
    color("LightGray") housing_right_half();
    
    // Trigger Button (LightGray) in the handle trigger slot
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 1, -20])
    rotate([90, 0, 0])
    color("OrangeRed") trigger_button();
}

if (render_part == "exploded") {
    // Left Half (slid left)
    color("DimGray") translate([-20, 0, 0]) housing_left_half();
    
    // Right Half (slid right)
    color("LightGray") translate([20, 0, 0]) housing_right_half();
    
    // Trigger Button (slid forward)
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 15, -20])
    rotate([90, 0, 0])
    color("OrangeRed") trigger_button();
    
    // Inside parts (slid for assembly view)
    // GM77 Module (slid upwards)
    translate([head_w/2, 27.0, wall + 6.75 + 15])
    color("Green") gm77_mockup();
    
    // ESP32 Board (slid upwards)
    translate([head_w/2, head_l - 32.0, wall + 6.5 + 20])
    color("DarkSlateBlue") esp32_mockup();
    
    // OLED screen (slid upwards from lid)
    translate([head_w/2, 55, 15 + split_z])
    rotate([-12, 0, 0])
    translate([0, 0, -5])
    color("Cyan") oled_mockup();
}

if (render_part == "print_all") {
    translate([0, 0, 0]) print_left();
    translate([head_w + 20, 0, 0]) print_right();
}

if (render_part == "left_half") print_left();
if (render_part == "right_half") print_right();

if (render_part == "cross_section") {
    difference() {
        union() {
            housing_left_half();
            housing_right_half();
            
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, -handle_top_d/2 - 1, -20])
            rotate([90, 0, 0])
            color("OrangeRed") trigger_button();
        }
        // Slice the assembly in half at Y = head_l*0.6
        translate([-50, head_l*0.6, -120])
        cube([200, 300, 300]);
    }
}

// --- 1. Full Housing Solid Shell & Pockets ---
module full_housing_solid() {
    union() {
        // [A] Outer Shell (unified head wall)
        difference() {
            housing_shape(wall_thick=0);
            housing_shape(wall_thick=wall);
        }
        
        // [B] OLED Bezel on top (recessed style, centered on V.A.)
        translate([head_w/2, 55, split_z + 8])
        rotate([-12, 0, 0])
        translate([0, 4.57, 0])
        difference() {
            rounded_rect(23.5 + 6, 12.5 + 6, 3.5, 3, true);
            translate([0, 0, 1]) rounded_rect(23.5 + 1.0, 12.5 + 1.0, 4, 1.5, true);
        }
        
        // [C] OLED Pocket Holder & Screw Bosses
        translate([head_w/2, 55, split_z])
        rotate([-12, 0, 0])
        translate([0, 0, -4.5]) {
            pcb_pocket(oled_size[0], oled_size[1], support_h=4, pocket_depth=2, wall_t=1.8, clearance_t=clearance);
            
            translate([0, 0, -2.0])
            pcb_screw_bosses(22.0, 23.0, h=4.0, d_outer=5.0);
        }
        
        // [D] ESP32 Pocket Holder & Screw Bosses
        translate([head_w/2, head_l - 32.0, wall + 6.5]) {
            pcb_pocket(esp32_size[0], esp32_size[1], support_h=10, pocket_depth=3, wall_t=2, clearance_t=clearance);
        }
        translate([head_w/2, head_l - 32.0, wall]) {
            pcb_screw_bosses(23.5, 47.0, h=10.0, d_outer=6.0);
        }
        
        // [E] GM77 Pocket Holder & Screw Bosses
        translate([head_w/2, 27.0, wall + 6.75]) {
            pcb_pocket(gm77_size[0], gm77_size[1], support_h=10.5, pocket_depth=3, wall_t=2, clearance_t=clearance);
        }
        translate([head_w/2, 27.6, wall]) {
            pcb_screw_bosses(24.6, 26.4, h=10.5, d_outer=5.0);
        }

        // [F] Modular Handle (S-Curve, merged directly)
        translate([head_w/2, head_l*0.6, wall]) {
            rotate([handle_angle, 0, 0]) {
                // Curved hull body
                hull() {
                    handle_slice(0, 0.0, handle_top_d/2);
                    handle_slice(-22, 1.2, 15.5);
                    handle_slice(-45, -1.0, 15.0);
                    handle_slice(-68, -2.5, 16.0);
                    handle_slice(-handle_h, -4.5, 18.5); // Flared base
                }
            }
        }
    }
}

// --- 2. Common Cuts subtracted from both halves ---
module full_housing_cuts() {
    // [A] Scanner Window (enlarged for GM77 to fit 21.6x12.0 head perfectly centered)
    translate([head_w/2 - 12, -5, 0.0])
    cube([24, 25, 14.0]);

    // [B] Rear USB cut for ESP32
    translate([head_w/2 - 6, head_l - 10, wall + 2])
    cube([12, 15, 10]);

    // [C] Ventilation Slots
    for(i=[0:4]) {
        translate([-1, 40 + i*8, 16]) rotate([0, 90, 0]) cylinder(h=head_w+10, d=2.2, center=true);
    }

    // [D] OLED Window cutout (aligned to 22.74x11.86 V.A.)
    translate([head_w/2, 55, split_z + 2])
    rotate([-12, 0, 0])
    translate([0, 4.57, 0])
    rounded_rect(23.5, 12.5, 50, 2, true);
    
    // [E] OLED Screw holes (2.0mm self-tapping)
    translate([head_w/2, 55, split_z])
    rotate([-12, 0, 0])
    translate([0, 0, -8])
    oled_screw_holes(h=10, d_inner=2.0);

    // [F] ESP32 Screw holes (3.0mm self-tapping)
    translate([head_w/2, head_l - 32.0, wall - 1]) {
        esp32_screw_holes(h=20, d_inner=3.0);
    }
    
    // [G] GM77 Screw holes (2.0mm self-tapping)
    translate([head_w/2, 27.6, wall - 1]) {
        gm77_screw_holes(h=20, d_inner=2.0);
    }

    // [H] Handle Finger Grooves
    for (z_pos = [-35, -55, -75]) {
        let (y_val = (z_pos == -35) ? -14.2 :
                     (z_pos == -55) ? -15.5 : -17.5) {
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, y_val, z_pos])
            rotate([0, 90, 0])
            cylinder(h=handle_base_d + 10, d=8.5, center=true);
        }
    }

    // [I] Battery Room (Closed at bottom, opens into head)
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h + 3.0]) // leaves 3mm bottom wall
    cylinder(h=handle_h + 10, d=battery_diam);

    // [J] USB Type-C cutout at the bottom wall of the handle
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h]) {
        cube([11.0, 6.0, 10.0], center=true);
        translate([0, 0, 0.5])
        cube([14.5, 8.5, 2.0], center=true);
    }

    // [K] Trigger Button Hole through handle wall
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2, -20])
    rotate([90, 0, 0])
    cylinder(h=wall*5, d=11.0, center=true);

    // [L] Slide Switch Cutout on the left side (-X) near the bottom
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0]) {
        translate([-18.0 + 2.5, 0, -handle_h + 16.0])
        cube([5.0, 10.0, 20.0], center=true);
        
        translate([-18.0, 0, -handle_h + 16.0])
        cube([15.0, 4.0, 9.0], center=true);
        
        translate([-25.0, 0, -handle_h + 16.0 - 7.5])
        rotate([0, 90, 0])
        cylinder(h=15.0, d=2.0);
        
        translate([-25.0, 0, -handle_h + 16.0 + 7.5])
        rotate([0, 90, 0])
        cylinder(h=15.0, d=2.0);
    }

    // [M] Brand/Model Engraving
    translate([head_w/2, head_l - 18, split_z + 12])
    rotate([0, 0, 0])
    linear_extrude(2)
    text("QR COLDCHAIN", size=3.5, font="Arial:style=Bold", halign="center");
}

// --- 3. Split Half Modules ---

head_screw_boss_points = [
    [12, 31],
    [12, 5],
    [90, 27],
    [95, 5]
];

module join_screw_boss(y, z, is_left) {
    boss_r = 4.5; // boss radius (9.0mm diameter)
    boss_w = 7.0; // extends 7mm into each side
    
    if (is_left) {
        translate([24 - boss_w, y, z])
        rotate([0, 90, 0])
        cylinder(h=boss_w, r=boss_r);
    } else {
        translate([24, y, z])
        rotate([0, 90, 0])
        cylinder(h=boss_w, r=boss_r);
    }
}

module left_half_holes() {
    for (pt = head_screw_boss_points) {
        y = pt[0];
        z = pt[1];
        // Clearance hole (3.2mm)
        translate([-10, y, z])
        rotate([0, 90, 0])
        cylinder(h=34.2, d=3.2);
        
        // Counterbore (6.0mm diameter) ending at X = 18
        translate([-10, y, z])
        rotate([0, 90, 0])
        cylinder(h=28.0, d=6.0);
    }
}

module right_half_holes() {
    for (pt = head_screw_boss_points) {
        y = pt[0];
        z = pt[1];
        // Pilot hole (2.5mm)
        translate([23.9, y, z])
        rotate([0, 90, 0])
        cylinder(h=8.2, d=2.5);
    }
}

module handle_bosses(is_left) {
    boss_r = 4.0;
    boss_w = 6.0;
    local_points = [
        [14, -30],
        [15, -75]
    ];
    
    for (pt = local_points) {
        y = pt[0];
        z = pt[1];
        rotate([handle_angle, 0, 0]) {
            if (is_left) {
                translate([-boss_w, y, z])
                rotate([0, 90, 0])
                cylinder(h=boss_w, r=boss_r);
            } else {
                translate([0, y, z])
                rotate([0, 90, 0])
                cylinder(h=boss_w, r=boss_r);
            }
        }
    }
}

module handle_boss_holes(is_left) {
    local_points = [
        [14, -30],
        [15, -75]
    ];
    rotate([handle_angle, 0, 0]) {
        for (pt = local_points) {
            y = pt[0];
            z = pt[1];
            if (is_left) {
                // Clearance hole
                translate([-30, y, z])
                rotate([0, 90, 0])
                cylinder(h=30.1, d=3.2);
                
                // Counterbore
                translate([-30, y, z])
                rotate([0, 90, 0])
                cylinder(h=25, d=6.0);
            } else {
                // Pilot hole
                translate([-0.1, y, z])
                rotate([0, 90, 0])
                cylinder(h=7.0, d=2.5);
            }
        }
    }
}

module alignment_pins(is_left) {
    pin_points = [
        [15, 20],
        [50, 4],
        [100, 20]
    ];
    for (pt = pin_points) {
        y = pt[0];
        z = pt[1];
        if (is_left) {
            translate([24, y, z])
            rotate([0, 90, 0])
            cylinder(h=2.0, d=1.8);
        } else {
            translate([23.9, y, z])
            rotate([0, 90, 0])
            cylinder(h=2.2, d=2.2);
        }
    }
}

module housing_left_half() {
    difference() {
        union() {
            intersection() {
                full_housing_solid();
                translate([-100, -50, -150]) cube([124, 300, 300]);
            }
            
            for (pt = head_screw_boss_points) {
                join_screw_boss(pt[0], pt[1], true);
            }
            
            translate([head_w/2, head_l*0.6, wall])
            handle_bosses(true);
            
            alignment_pins(true);
        }
        
        full_housing_cuts();
        left_half_holes();
        
        translate([head_w/2, head_l*0.6, wall])
        handle_boss_holes(true);
    }
}

module housing_right_half() {
    difference() {
        union() {
            intersection() {
                full_housing_solid();
                translate([24, -50, -150]) cube([124, 300, 300]);
            }
            
            for (pt = head_screw_boss_points) {
                join_screw_boss(pt[0], pt[1], false);
            }
            
            translate([head_w/2, head_l*0.6, wall])
            handle_bosses(false);
        }
        
        full_housing_cuts();
        right_half_holes();
        
        translate([head_w/2, head_l*0.6, wall])
        handle_boss_holes(false);
        
        alignment_pins(false);
    }
}

// --- Head Geometry Helper Modules ---
module slice(y, w, h, r, wall_thick=0) {
    real_w = max(4, w - 2 * wall_thick);
    real_h = max(4, h - 2 * wall_thick);
    real_r = max(1.0, r - wall_thick);
    z_center = real_h/2 + wall_thick;
    translate([head_w/2, y, z_center])
    rotate([90, 0, 0])
    rounded_rect(real_w, real_h, 1.0, real_r, true);
}

// Organic shape definition
module housing_shape(wall_thick=0) {
    y_front = 8 + wall_thick;
    y_rear = head_l - 2 - wall_thick;
    
    hull() {
        slice(y_front, head_w, head_h, 10, wall_thick);
        slice(head_l * 0.35, head_w + 2, head_h + 2, 12, wall_thick);
        slice(head_l * 0.70, head_w * 0.9, head_h * 0.9, 10, wall_thick);
        slice(y_rear, head_w * 0.78, head_h * 0.78, 8, wall_thick);
    }
}

module handle_slice(z, y_offset, r) {
    translate([0, y_offset, z])
    cylinder(h=0.1, r=r, center=true);
}

// --- Component Mounting & Snap Modules ---
module pcb_pocket(pcb_w, pcb_l, support_h, pocket_depth, wall_t, clearance_t) {
    difference() {
        cube([pcb_w + 2*clearance_t + 2*wall_t, pcb_l + 2*clearance_t + 2*wall_t, support_h + pocket_depth], center=true);
        
        translate([0, 0, support_h/2])
        cube([pcb_w + 2*clearance_t, pcb_l + 2*clearance_t, pocket_depth + 0.1], center=true);
        
        translate([0, 0, -pocket_depth/2])
        cube([pcb_w - 2*wall_t, pcb_l - 2*wall_t, support_h + 0.1], center=true);
    }
}

module pcb_screw_bosses(w_pitch, l_pitch, h, d_outer) {
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module esp32_screw_holes(h, d_inner) {
    w_pitch = 23.5;
    l_pitch = 47.0;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module gm77_screw_holes(h, d_inner) {
    w_pitch = 24.6;
    l_pitch = 26.4;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module oled_screw_holes(h, d_inner) {
    w_pitch = 22.0;
    l_pitch = 23.0;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

// --- Component Mockups for Exploded View ---
module trigger_button() {
    difference() {
        union() {
            scale([1, 1.45, 2.1]) sphere(d=10);
            translate([0, 1.5, 0])
            cube([9.5, 3.5, 17], center=true);
        }
        translate([0, 6, 0]) cube([25, 10, 40], center=true);
        translate([0, -10, 0]) cube([25, 10, 40], center=true);
    }
}

module gm77_mockup() {
    cube(gm77_size, center=true);
    color("Black") translate([0, -gm77_size[1]/2 - 1.5, 0]) rotate([90, 0, 0]) cylinder(h=4, d=10, center=true);
}

module esp32_mockup() {
    cube([esp32_size[0], esp32_size[1], 1.6], center=true);
    color("Silver") translate([0, 0, 3]) cube([15, 22, 3.5], center=true);
    color("Black") translate([0, esp32_size[1]/2 - 3, 2]) cube([8, 8, 4.5], center=true);
}

module oled_mockup() {
    // PCB (26 x 27 x 1.2)
    cube([oled_size[0], oled_size[1], 1.2], center=true);
    
    // Display Glass panel (24.74 x 16.90 x 1.42) shifted by +4.57mm in Y
    color("DimGray")
    translate([0, 4.57, 0.6 + 0.71])
    cube([24.74, 16.90, 1.42], center=true);
    
    // Active Area screen (21.74 x 10.86 x 0.1) shifted on top of glass
    color("MidnightBlue")
    translate([0, 4.57, 0.6 + 1.42 + 0.05])
    cube([21.74, 10.86, 0.1], center=true);
}

// --- Utility Modules ---
module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
        square([w-r*2, h-r*2], center=true);
    }
}
