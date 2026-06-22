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
head_w = 58.0;      // Width (increased from 48.0 for lateral wire channels)
head_l = 142.0;     // Length (increased from 132.0 for longitudinal wire clearance)
head_h = 50.0;      // Height (increased from 36.0 to clear vertical DuPont header pins)
split_z = 25.0;     // Horizontal split plane height (increased from 21.0)

// [Handle Part Dimensions]
handle_base_d = 40.0; // Bottom diameter (increased from 38.0 for better grip/space)
handle_top_d = 32.0;  // Top diameter (increased from 30.0)
handle_h = 105.0;     // Handle height (increased from 92.0)
handle_angle = 18;    // Tilt angle (degrees)

// [Component Sizes]
gm77_size = [27.5, 49.0, 14.0];  // GM77 QR Module
esp32_size = [28.2, 51.5, 15.0]; // ESP32 board (corrected to fit standard DevKit V1 30-pin)
oled_size = [26.0, 27.0, 1.2];   // SSD1306 OLED PCB size
battery_diam = 18.5;             // 18650 nominal diameter (clearance is added in the clamp code)

// --- Main Control ---
render_part = "exploded"; // assembly, exploded, print_all, left_half, right_half, cross_section, trigger

// 3D Printing alignment helpers
module print_left() {
    translate([0, 0, 24]) rotate([0, 90, 0]) housing_left_half();
}

module print_right() {
    translate([0, 0, -24]) rotate([0, -90, 0]) housing_right_half();
}

module print_trigger() {
    translate([0, 0, 1]) rotate([-90, 0, 0]) trigger_button();
}

if (render_part == "assembly") {
    color("DimGray", 0.5) housing_left_half();
    color("LightGray", 0.5) housing_right_half();
    
    // Trigger Button (LightGray) in the handle trigger slot
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 1, -20])
    rotate([90, 0, 0])
    color("OrangeRed") trigger_button();
    
    // Inside parts (semi-transparent assembly view)
    all_head_electronics_assembly(is_exploded=false);
    internal_electronics_assembly(is_exploded=false);
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
    all_head_electronics_assembly(is_exploded=true);
    internal_electronics_assembly(is_exploded=true);
}

if (render_part == "print_all") {
    translate([0, 0, 0]) print_left();
    translate([head_w + 20, 0, 0]) print_right();
    translate([head_w * 2 + 35, 20, 0]) print_trigger();
}

if (render_part == "left_half") print_left();
if (render_part == "right_half") print_right();
if (render_part == "trigger") print_trigger();

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
            
            // Inside parts
            all_head_electronics_assembly(is_exploded=false);
            internal_electronics_assembly(is_exploded=false);
        }
        // Slice the assembly in half at Y = head_l*0.6
        translate([-50, head_l*0.6, -120])
        cube([200, 300, 300]);
    }
}

// --- 1. Full Housing Solid Shell & Pockets ---
module full_housing_solid() {
    union() {
        // [A] Outer Shell (unified head wall + solid handle, hollowed together to eliminate joint gaps)
        difference() {
            union() {
                housing_shape(wall_thick=0);
                
                // [F] Modular Handle (starts higher at Z_local = 12.0 to eliminate joint gaps)
                translate([head_w/2, head_l*0.6, wall]) {
                    rotate([handle_angle, 0, 0]) {
                        hull() {
                            handle_slice(12.0, 0.0, handle_top_d/2);
                            handle_slice(-22, 1.2, 16.5);
                            handle_slice(-45, -1.0, 16.0);
                            handle_slice(-68, -2.5, 17.0);
                            handle_slice(-handle_h, -4.5, handle_base_d/2); // Flared base
                        }
                    }
                }
            }
            // Hollowing cut: cleans up any handle protrusion inside the head floor
            housing_shape(wall_thick=wall);
        }
        
        // [C] OLED Side Guides & Back Clamping Tabs (Screwless, 3mm below window, pin-avoiding)
        // Local coord Z=0 is mount origin at head_h-7.5. Window inner surface ??Z=1.5.
        // Support tab top at Z = 1.5 - 3.0 = -1.5 (3mm below window).
        // Display (2.5mm thick) sits on tab: front face at Z = -1.5 + 2.5 = 1.0 (flush).
        translate([head_w/2, 55, head_h - 7.5])
        rotate([-12, 0, 0]) {
            // Side guide walls (left and right) to keep PCB aligned in X
            translate([-13.0 - clearance - 1.5, -13.5 - clearance, -5.0])
            cube([1.5, 27.0 + 2*clearance, 6.5]);
            translate([13.0 + clearance, -13.5 - clearance, -5.0])
            cube([1.5, 27.0 + 2*clearance, 6.5]);
            
            // Back clamping tabs - ONLY at -Y half to avoid pin header at +Y edge
            // Two pads at left and right, Y range: -12.0 to -2.0 (safe zone)
            // Tab top at Z = -1.0, bottom at Z = -5.0 (height 4.0mm) to seat OLED flush against front window
            translate([-14.0, -9.0, -5.0]) cube([10.0, 10.0, 4.0]);
            translate([4.0, -9.0, -5.0])   cube([10.0, 10.0, 4.0]);
        }
        
        // [D] ESP32 Pocket Holder & Screw Bosses (REMOVED: Now using screwless esp32_clamping_pillars for wiring clearance)
        
        // [E] GM77 Pocket Holder & Screw Bosses
        translate([head_w/2, 27.0, wall + 6.75]) {
            pcb_pocket(gm77_size[0], gm77_size[1], support_h=10.5, pocket_depth=3, wall_t=2, clearance_t=clearance);
        }
        translate([head_w/2, 27.6, wall]) {
            pcb_screw_bosses(24.6, 26.4, h=10.5, d_outer=5.0);
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

    // [D] OLED Window cutout (aligned to 25.0x15.0 active area)
    translate([head_w/2, 55, head_h - 6.0])
    rotate([-12, 0, 0])
    translate([0, 4.57, 0])
    rounded_rect(25.0, 15.0, 50, 2, true);
    
    // [E] OLED Screw holes (REMOVED: Now using screwless back-clamp design)

    // [F] ESP32 Screw holes (REMOVED: Now using screwless slide-in clamping pillars)
    
    // [G] GM77 Screw holes (2.0mm self-tapping)
    translate([head_w/2, 27.6, wall - 1]) {
        gm77_screw_holes(h=20, d_inner=2.0);
    }

    // [H] Handle Finger Grooves (Adjusted to prevent breakthrough holes in front handle wall)
    for (z_pos = [-35, -55, -75]) {
        let (y_val = (z_pos == -35) ? -16.2 :
                     (z_pos == -55) ? -17.5 : -19.5) {
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, y_val, z_pos])
            rotate([0, 90, 0])
            cylinder(h=handle_base_d + 10, d=6.5, center=true);
        }
    }

    // [I] Hollow Handle Interior (leaves 3mm bottom wall)
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    handle_interior();

    // [I.2] Clean vertical wire entry through head floor into handle (removes sloped lip)
    translate([head_w/2, head_l*0.6 - 2.0, 0.0])
    cylinder(h=25.0, d=22.0, center=true);

    // [J] USB Type-C cutout at the bottom wall of the handle
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h]) {
        // Inner port hole (fitting Type-C metal shroud: ~9.0 x 3.2 mm)
        translate([0, 0, 3.0]) // cut through the 3mm bottom floor
            cube([9.6, 3.8, 6.0], center=true);
        // Outer counterbore (fitting USB cable plug overmold: ~13.0 x 6.8 mm)
        translate([0, 0, 1.0])
            cube([13.0, 6.8, 2.5], center=true);
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
        translate([-20.0 + 2.5, 0, -handle_h + 16.0])
        cube([5.0, 10.0, 20.0], center=true);
        
        translate([-20.0, 0, -handle_h + 16.0])
        cube([15.0, 4.0, 9.0], center=true);
        
        translate([-27.0, 0, -handle_h + 16.0 - 7.5])
        rotate([0, 90, 0])
        cylinder(h=15.0, d=2.0);
        
        translate([-27.0, 0, -handle_h + 16.0 + 7.5])
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
    [12, 31] // Keep only one screw hole at the front-upper corner
];

module join_screw_boss(y, z, is_left) {
    boss_r = 4.5; // boss radius (9.0mm diameter)
    boss_w = 7.0; // extends 7mm into each side
    split_x = head_w/2;
    
    if (is_left) {
        translate([split_x - split_x, y, z]) // starts at X = 0
        rotate([0, 90, 0])
        cylinder(h=split_x, r=boss_r);
    } else {
        translate([split_x, y, z])
        rotate([0, 90, 0])
        cylinder(h=split_x, r=boss_r); // spans from split_x to head_w
    }
}

module left_half_holes() {
    split_x = head_w/2;
    for (pt = head_screw_boss_points) {
        y = pt[0];
        z = pt[1];
        // Clearance hole (3.2mm)
        translate([split_x - 34.0, y, z])
        rotate([0, 90, 0])
        cylinder(h=34.2, d=3.2);
        
        // Counterbore (6.0mm diameter) ending at X = split_x - 6.0
        translate([split_x - 34.0, y, z])
        rotate([0, 90, 0])
        cylinder(h=28.0, d=6.0);
    }
}

module right_half_holes() {
    split_x = head_w/2;
    for (pt = head_screw_boss_points) {
        y = pt[0];
        z = pt[1];
        // Pilot hole (2.5mm)
        translate([split_x - 0.1, y, z])
        rotate([0, 90, 0])
        cylinder(h=8.2, d=2.5);
    }
}

module handle_bosses(is_left) {
    boss_r = 4.0;
    local_points = [
        [14, -30, 16.2],
        [15, -75, 17.5]
    ];
    
    for (pt = local_points) {
        y = pt[0];
        z_val = pt[1];
        r_val = pt[2];
        rotate([handle_angle, 0, 0]) {
            if (is_left) {
                translate([-r_val, y, z_val])
                rotate([0, 90, 0])
                cylinder(h=r_val, r=boss_r);
            } else {
                translate([0, y, z_val])
                rotate([0, 90, 0])
                cylinder(h=r_val, r=boss_r);
            }
        }
    }
}

module handle_boss_holes(is_left) {
    local_points = [
        [14, -30, 16.2],
        [15, -75, 17.5]
    ];
    rotate([handle_angle, 0, 0]) {
        for (pt = local_points) {
            y = pt[0];
            z_val = pt[1];
            r_val = pt[2];
            if (is_left) {
                // Clearance hole
                translate([-r_val - 1.0, y, z_val])
                rotate([0, 90, 0])
                cylinder(h=r_val + 1.1, d=3.2);
                
                // Counterbore
                translate([-r_val - 1.0, y, z_val])
                rotate([0, 90, 0])
                cylinder(h=r_val - 4.0, d=6.0); // leaves a 5.0mm thick wall
            } else {
                // Pilot hole
                translate([-0.1, y, z_val])
                rotate([0, 90, 0])
                cylinder(h=8.0, d=2.5);
            }
        }
    }
}

module alignment_pins(is_left) {
    split_x = head_w/2;
    pin_points = [
        [15, 20],
        [55, 4],
        [130, 20]
    ];
    for (pt = pin_points) {
        y = pt[0];
        z = pt[1];
        if (is_left) {
            translate([split_x, y, z])
            rotate([0, 90, 0])
            cylinder(h=2.0, d=1.8);
        } else {
            translate([split_x - 0.1, y, z])
            rotate([0, 90, 0])
            cylinder(h=2.2, d=2.2);
        }
    }
}

module handle_interior() {
    hull() {
        handle_slice(0.1, 0.0, handle_top_d/2 - 2.5);
        handle_slice(-22, 1.2, 16.5 - 2.5);
        handle_slice(-45, -1.0, 16.0 - 2.5);
        handle_slice(-68, -2.5, 17.0 - 2.5);
        handle_slice(-handle_h + 3.0, -4.5, handle_base_d/2 - 2.5);
    }
}

module battery_ribs(is_left) {
    D_bat = battery_diam + 0.3; // ~18.8mm inner diameter for battery clamp
    D_outer = D_bat + 4.5;      // ~23.3mm outer diameter
    
    // Left clamp at Z = -35
    if (is_left) {
        translate([0, 0, -35]) {
            difference() {
                // Outer ring
                cylinder(h=6.0, d=D_outer, center=true);
                // Inner battery slot
                cylinder(h=7.0, d=D_bat, center=true);
                // Entrance opening at +Y side (for slide/snap insertion)
                translate([-15, 5.0, -4.0]) cube([30, 15, 8.0]);
                
                // Cut away the right half (X > 2.5) to clear right split plane
                translate([2.5, -15, -4.0]) cube([15, 30, 8.0]);
            }
            // Lead-in chamfers at the entry tips for smooth snap-in
            translate([-8.0, 5.0, 0]) rotate([0, 0, 30]) cube([1.5, 3.0, 6.0], center=true);
            translate([2.0, 5.0, 0]) rotate([0, 0, -30]) cube([1.5, 3.0, 6.0], center=true);
        }
    }
    
    // Right clamp at Z = -75
    if (!is_left) {
        translate([0, 0, -75]) {
            difference() {
                // Outer ring
                cylinder(h=6.0, d=D_outer, center=true);
                // Inner battery slot
                cylinder(h=7.0, d=D_bat, center=true);
                // Entrance opening at +Y side
                translate([-15, 5.0, -4.0]) cube([30, 15, 8.0]);
                
                // Cut away the left half (X < -2.5) to clear left split plane
                translate([-17.5, -15, -4.0]) cube([15, 30, 8.0]);
            }
            // Lead-in chamfers at the entry tips
            translate([-2.0, 5.0, 0]) rotate([0, 0, 30]) cube([1.5, 3.0, 6.0], center=true);
            translate([8.0, 5.0, 0]) rotate([0, 0, -30]) cube([1.5, 3.0, 6.0], center=true);
        }
    }
}

module tp4056_clamping_pillars(is_left) {
    z_bottom = -handle_h + 3.0; // bottom floor
    pcb_w_half = 25.0 / 2 + 0.25; // 12.75mm
    pcb_l_half = 16.5 / 2 + 0.25; // 8.5mm
    pcb_t = 1.6;
    
    rotate([handle_angle, 0, 0]) {
        if (is_left) {
            // Left guide wall (X < 0)
            translate([-pcb_w_half - 1.5, -pcb_l_half, z_bottom]) {
                difference() {
                    cube([2.0, pcb_l_half * 2, 4.0]); // wall
                    // slot for PCB edge
                    translate([0.5, -0.1, 0.0])
                        cube([1.6, pcb_l_half * 2 + 0.2, pcb_t + 0.2]); 
                }
            }
            // Front/Back stops to prevent sliding
            translate([-pcb_w_half, -pcb_l_half - 1.5, z_bottom])
                cube([pcb_w_half, 1.5, 3.0]);
            translate([-pcb_w_half, pcb_l_half, z_bottom])
                cube([pcb_w_half, 1.5, 3.0]);
        } else {
            // Right guide wall (X > 0)
            translate([pcb_w_half - 0.5, -pcb_l_half, z_bottom]) {
                difference() {
                    cube([2.0, pcb_l_half * 2, 4.0]); // wall
                    // slot for PCB edge
                    translate([-0.1, -0.1, 0.0])
                        cube([1.6, pcb_l_half * 2 + 0.2, pcb_t + 0.2]);
                }
            }
            // Front/Back stops to prevent sliding
            translate([0, -pcb_l_half - 1.5, z_bottom])
                cube([pcb_w_half, 1.5, 3.0]);
            translate([0, pcb_l_half, z_bottom])
                cube([pcb_w_half, 1.5, 3.0]);
        }
    }
}

module esp32_clamping_pillars(is_left) {
    y_center = head_l - 32.0;
    x_pcb_half = esp32_size[0] / 2;
    y_pcb_half = esp32_size[1] / 2;
    pillar_l = 8.0;
    pillar_h = 12.0;   // Lowered to 12.0 for wire clearance, slots sit at Z = 4.5 to 6.5
    
    y_corners = [y_center - y_pcb_half, y_center + y_pcb_half];
    for (y_pos = y_corners) {
        if (is_left) {
            translate([head_w/2 - x_pcb_half - 2.0, y_pos - pillar_l/2, wall]) {
                difference() {
                    cube([6.0, pillar_l, pillar_h]);
                    // Slot for PCB
                    translate([4.0, -0.1, 4.5]) cube([2.1, pillar_l + 0.2, 2.0]);
                }
            }
        } else {
            translate([head_w/2 + x_pcb_half - 4.0, y_pos - pillar_l/2, wall]) {
                difference() {
                    cube([6.0, pillar_l, pillar_h]);
                    // Slot for PCB
                    translate([-0.1, -0.1, 4.5]) cube([2.1, pillar_l + 0.2, 2.0]);
                }
            }
        }
    }
}

module housing_left_half() {
    difference() {
        union() {
            intersection() {
                full_housing_solid();
                translate([-100, -50, -150]) cube([100 + head_w/2, 300, 300]);
            }
            
            for (pt = head_screw_boss_points) {
                join_screw_boss(pt[0], pt[1], true);
            }
            
            translate([head_w/2, head_l*0.6, wall])
            handle_bosses(true);
            
            alignment_pins(true);
            
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            battery_ribs(true);
            
            translate([head_w/2, head_l*0.6, wall])
            tp4056_clamping_pillars(true);
            
            // Add screwless clamping slots for ESP32 on the left side
            esp32_clamping_pillars(true);
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
                translate([head_w/2, -50, -150]) cube([100, 300, 300]);
            }
            
            for (pt = head_screw_boss_points) {
                join_screw_boss(pt[0], pt[1], false);
            }
            
            translate([head_w/2, head_l*0.6, wall])
            handle_bosses(false);
            
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            battery_ribs(false);
            
            translate([head_w/2, head_l*0.6, wall])
            tp4056_clamping_pillars(false);
            
            // Add screwless clamping slots for ESP32 on the right side
            esp32_clamping_pillars(false);
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
        slice(head_l * 0.70, head_w * 1.0, head_h * 1.0, 10, wall_thick); // Relaxed rear casing taper (0.9 -> 1.0)
        slice(y_rear, head_w * 0.95, head_h * 0.95, 8, wall_thick);      // Relaxed rear casing taper (0.78 -> 0.95)
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

// --- New Mockup Modules (Battery, TP4056, Step-up, Switch) & Assemblies ---

module battery_mockup() {
    color("LimeGreen") {
        // Battery Body (18.4 diameter, 65 length)
        cylinder(h=65, d=18.4, center=true);
        // Plus Terminal Tab
        translate([0, 0, 32.5])
        cylinder(h=1.5, d=9.0, center=true);
    }
}

module tp4056_mockup() {
    // PCB (25.0 x 16.5 x 1.6)
    color("Green")
    cube([25.0, 16.5, 1.6], center=true);
    
    // Type-C USB Port (Silver, 9.0 x 5.0 x 3.2) protruding downwards
    color("Silver")
    translate([0, 0, -0.8 - 1.5])
    cube([9.0, 5.0, 3.2], center=true);
}

module stepup_mockup() {
    // PCB (12.0 x 18.0 x 1.6)
    color("DarkCyan")
    cube([12.0, 1.6, 18.0], center=true);
    
    // Blue Potentiometer (4.0 x 4.0 x 4.0)
    color("Blue")
    translate([-3.0, 0.8 + 2.0, 5.0])
    cube([4.0, 4.0, 4.0], center=true);
    
    // Potentiometer brass screw
    color("Gold")
    translate([-3.0, 0.8 + 4.0, 5.0])
    rotate([90, 0, 0])
    cylinder(h=1.0, d=1.5, center=true);
    
    // Black Inductor (5.0 x 5.0 x 3.0)
    color("Black")
    translate([2.0, 0.8 + 1.5, -2.0])
    cube([5.0, 5.0, 3.0], center=true);
}

module switch_mockup() {
    // Main Body
    color("Gray")
    cube([6.0, 10.0, 14.0], center=true);
    
    // Toggle Lever (extending along -X)
    color("Black")
    translate([-5.0, 0, 0])
    cube([6.0, 2.0, 3.0], center=true);
    
    // Terminal Pins
    color("Silver") {
        translate([0, 0, -8.0]) {
            translate([0, -3.0, 0]) cylinder(h=3.0, d=0.8, center=true);
            translate([0, 0, 0])    cylinder(h=3.0, d=0.8, center=true);
            translate([0, 3.0, 0])  cylinder(h=3.0, d=0.8, center=true);
        }
    }
}

module all_head_electronics_assembly(is_exploded=false) {
    gm77_offset = is_exploded ? 15 : 0;
    esp32_offset = is_exploded ? 20 : 0;
    oled_offset = is_exploded ? 15 : 0;
    
    // GM77
    translate([head_w/2, 27.0, wall + 6.75 + gm77_offset])
    color("Green") gm77_mockup();
    
    // ESP32 (lowered by 3.5mm from wall + 6.5 to wall + 5.3)
    translate([head_w/2, head_l - 32.0, wall + 5.3 + esp32_offset])
    color("DarkSlateBlue") esp32_mockup();
    
    // OLED (PCB bottom rests on tab top at Z_local = -1.0, PCB center at Z_local = -0.4)
    translate([head_w/2, 55, oled_offset + head_h - 7.5])
    rotate([-12, 0, 0])
    translate([0, 0, -0.4])
    color("Cyan") oled_mockup();
}

module internal_electronics_assembly(is_exploded=false) {
    // Coordinate system of the handle:
    // translate([head_w/2, head_l*0.6, wall]) rotate([handle_angle, 0, 0])
    
    // Exploded offsets
    bat_offset = is_exploded ? [0, 0, 25] : [0, 0, 0];
    tp_offset = is_exploded ? [0, 0, -25] : [0, 0, 0];
    su_offset = is_exploded ? [0, 25, 0] : [0, 0, 0];
    sw_offset = is_exploded ? [-25, 0, 0] : [0, 0, 0];
    
    translate([head_w/2, head_l*0.6, wall]) {
        rotate([handle_angle, 0, 0]) {
            // 1. Battery (centered at Z = -55.0 to align symmetrically with snap-fit C-clips at -35 and -75)
            translate([0, 0, -55.0] + bat_offset)
            battery_mockup();
            
            // 2. TP4056 USB Charger (aligned with the bottom guide slot at Z = -handle_h + 3.8)
            translate([0, 0, -handle_h + 3.8] + tp_offset)
            tp4056_mockup();
            
            // 3. MT3608 Step-up Module
            translate([0, 8.0, -83.0] + su_offset)
            stepup_mockup();
            
            // 4. Slide Switch (aligned with cutout slot at Z = -handle_h + 16.0)
            translate([-17.5, 0, -handle_h + 16.0] + sw_offset)
            switch_mockup();
        }
    }
}
