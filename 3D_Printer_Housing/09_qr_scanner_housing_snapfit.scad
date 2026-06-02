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
gm77_size = [27.5, 48.5, 14.0];  // GM77 QR Module
esp32_size = [30.0, 56.5, 15.0]; // ESP32 board
oled_size = [27.5, 27.5, 3.0];   // SSD1306 OLED
battery_diam = 19.2;             // HY18650-2200 bare cell with clearance (18.4mm nominal)

// --- Main Control ---
render_part = "exploded"; // assembly, exploded, print_all, body, handle, lid, battery_cap, cross_section

// 3D Printing alignment helpers
module print_body() {
    translate([0, 0, split_z]) rotate([180, 0, 0]) housing_body();
}

module print_handle() {
    rotate([180, 0, 0]) housing_handle();
}

module print_lid() {
    translate([0, 0, 3]) rotate([180, 0, 0]) housing_lid();
}

module print_battery_cap() {
    housing_battery_cap();
}

if (render_part == "assembly") {
    color("DimGray") housing_body();
    color("DimGray") translate([head_w/2, head_l*0.6, wall]) housing_handle();
    color("DimGray") housing_lid();
    color("DarkSlateGray") front_bumper();
    
    // Battery Cap in place
    color("DimGray")
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h])
    housing_battery_cap();
    
    // Trigger Button (LightGray) in the handle trigger slot
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 1, -20])
    rotate([90, 0, 0])
    color("LightGray") trigger_button();
}

if (render_part == "exploded") {
    // Main Body
    color("DimGray") housing_body();
    
    // Handle (slid downwards)
    color("DimGray") translate([head_w/2, head_l*0.6, wall - 40]) housing_handle();
    
    // Lid (slid upwards)
    color("DimGray") translate([0, 0, 30]) housing_lid();
    
    // Front Bumper (slid forward)
    color("DarkSlateGray") translate([head_w/2, -20, split_z]) front_bumper();
    
    // Trigger Button (slid forward)
    translate([head_w/2, head_l*0.6, wall - 40])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 15, -20])
    rotate([90, 0, 0])
    color("LightGray") trigger_button();
    
    // Battery Cap (slid downwards from handle)
    color("DimGray")
    translate([head_w/2, head_l*0.6, wall - 40])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h - 20])
    housing_battery_cap();
    
    // Inside parts (slid for assembly view)
    // GM77 Module (slid upwards)
    translate([head_w/2, 27.0, wall + 6.75 + 15])
    color("Green") gm77_mockup();
    
    // ESP32 Board (slid upwards)
    translate([head_w/2, head_l - 32.0, wall + 6.5 + 20])
    color("DarkSlateBlue") esp32_mockup();
    
    // OLED screen (slid downwards from lid)
    translate([head_w/2, 55, 30 + split_z])
    rotate([-12, 0, 0])
    translate([0, 0, -18])
    color("Cyan") oled_mockup();
}

if (render_part == "print_all") {
    translate([0, 0, 0]) print_body();
    translate([head_w + 20, head_l*0.6, 0]) print_handle();
    translate([head_w * 2 + 40, 0, 0]) print_lid();
    translate([head_w * 2 + 40, head_l*0.6, 0]) print_battery_cap();
}

if (render_part == "body") print_body();
if (render_part == "handle") print_handle();
if (render_part == "lid") print_lid();
if (render_part == "battery_cap") print_battery_cap();

if (render_part == "cross_section") {
    difference() {
        union() {
            housing_body();
            translate([head_w/2, head_l*0.6, wall]) housing_handle();
            housing_lid();
            front_bumper();
            
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, 0, -handle_h])
            housing_battery_cap();
            
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, -handle_top_d/2 - 1, -20])
            rotate([90, 0, 0])
            color("LightGray") trigger_button();
        }
        // Slice the assembly in half at X = head_w/2
        translate([head_w/2, -50, -120])
        cube([200, 300, 300]);
    }
}

// --- 1. Housing Body (Bottom Head Half) ---
module housing_body() {
    difference() {
        union() {
            // [A] Outer Shell (organic head cut at split_z) with interior hollowing
            // (Hollowed first to prevent wiping out the interior bosses/pockets)
            difference() {
                intersection() {
                    housing_shape(wall_thick=0);
                    translate([-100, -50, -10]) cube([300, 300, split_z + 10]);
                }
                housing_shape(wall_thick=wall);
            }
            
            // [B] Alignment lip (rim) on the body extending above split plane
            intersection() {
                difference() {
                    housing_shape(wall_thick=1.2); // inner half of wall
                    housing_shape(wall_thick=wall);
                }
                translate([-100, -50, split_z]) cube([300, 300, 1.5]);
            }

            // [C] Raised locking shelf for the handle snap collar
            translate([head_w/2, head_l*0.6, wall])
            difference() {
                cylinder(h=6.0, d=34.0); // outer shelf wall
                cylinder(h=6.5, d=28.0); // collar passage
            }
            
            // [D] ESP32 Pocket Holder & Screw Bosses (Inner diameter: 3.0mm, Outer: 6.0mm)
            translate([head_w/2, head_l - 32.0, wall + 6.5]) {
                pcb_pocket(esp32_size[0], esp32_size[1], support_h=10, pocket_depth=3, wall_t=2, clearance_t=clearance);
            }
            translate([head_w/2, head_l - 32.0, wall]) {
                pcb_screw_bosses(23.5, 47.0, h=10.0, d_outer=6.0);
            }
            
            // [E] GM77 Pocket Holder & Screw Bosses (Inner diameter: 2.0mm, Outer: 5.0mm)
            translate([head_w/2, 27.0, wall + 6.75]) {
                pcb_pocket(gm77_size[0], gm77_size[1], support_h=10.5, pocket_depth=3, wall_t=2, clearance_t=clearance);
            }
            translate([head_w/2, 27.0, wall]) {
                pcb_screw_bosses(24.5, 26.0, h=10.5, d_outer=5.0);
            }
        }

        // --- Subtract from Body ---
        
        // Snap slots in left and right inner walls
        body_snap_pocket(wall, 35.0, orient_left=true);
        body_snap_pocket(wall, 80.0, orient_left=true);
        body_snap_pocket(head_w - wall, 35.0, orient_left=false);
        body_snap_pocket(head_w - wall, 80.0, orient_left=false);

        // ESP32 Screw holes (3.0mm self-tapping)
        translate([head_w/2, head_l - 32.0, wall - 1]) {
            esp32_screw_holes(h=20, d_inner=3.0);
        }
        
        // GM77 Screw holes (2.0mm self-tapping)
        translate([head_w/2, 27.0, wall - 1]) {
            gm77_screw_holes(h=20, d_inner=2.0);
        }

        // Collar passage through the bottom wall (Z = -1 to Z = wall + 0.1)
        translate([head_w/2, head_l*0.6, -1])
        cylinder(h=wall + 1.1, d=28.0);
        
        // Clearance for the expanded snap tabs inside the body (above Z = 8.5)
        translate([head_w/2, head_l*0.6, wall + 6.0])
        cylinder(h=15.0, d=32.0);

        // Scanner Window (deep to cut through flared nose)
        translate([head_w/2 - 12, -5, 10.5])
        cube([24, 25, 16]);
        
        // Rear USB cut for ESP32
        translate([head_w/2 - 6, head_l - 10, wall + 2])
        cube([12, 15, 10]);

        // Ventilation Slots
        for(i=[0:4]) {
            translate([-1, 40 + i*8, 16]) rotate([0, 90, 0]) cylinder(h=head_w+10, d=2.2, center=true);
        }
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
        // Front neck slice (just behind the bumper)
        slice(y_front, head_w, head_h, 10, wall_thick);
        
        // Hump middle (highest point, organic curve)
        slice(head_l * 0.35, head_w + 2, head_h + 2, 12, wall_thick);
        
        // Mid-rear transition
        slice(head_l * 0.70, head_w * 0.9, head_h * 0.9, 10, wall_thick);
        
        // Rear slice: tapered tail
        slice(y_rear, head_w * 0.78, head_h * 0.78, 8, wall_thick);
    }
}

// --- Front Bumper Ring (Black Shroud) ---
module front_bumper() {
    difference() {
        // Rounded flared outer bezel
        hull() {
            translate([0, -2, (head_h + 4)/2]) rotate([90, 0, 0]) rounded_rect(head_w + 6, head_h + 4, 3, 10, true);
            translate([0, 8, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 3, 10, true);
        }
        // Inner camera window entry cutout
        translate([0, -4, 18.5])
        cube([24.2, 20, 16.2], center=true);
        
        // Inner body insert hollow
        hull() {
            translate([0, 5, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w + 0.8, head_h + 0.8, 6, 10, true);
        }
    }
}

// --- 2. Modular Handle (Snap-Fit Version with Slide-in Battery) ---
module housing_handle() {
    difference() {
        union() {
            // [A] Ergonomic S-Curve Handle Body (18 degree tilt)
            rotate([handle_angle, 0, 0])
            difference() {
                // Curved hull body
                hull() {
                    handle_slice(0, 0.0, handle_top_d/2);
                    handle_slice(-22, 1.2, 15.5);
                    handle_slice(-45, -1.0, 15.0);
                    handle_slice(-68, -2.5, 16.0);
                    handle_slice(-handle_h, -4.5, 18.5); // Flared base
                }
                
                // Ergonomic Finger Grooves on the front grip (-Y side)
                for (z_pos = [-35, -55, -75]) {
                    let (y_val = (z_pos == -35) ? -14.2 :
                                 (z_pos == -55) ? -15.5 : -17.5) {
                        translate([0, y_val, z_pos])
                        rotate([0, 90, 0])
                        cylinder(h=handle_base_d + 10, d=8.5, center=true);
                    }
                }
            }
            
            // [B] Flexible Snap Collar
            // Extends straight up into the body mating hole
            translate([0, 0, 0])
            handle_snap_collar();

            // [C] Recessed collar bezel for trigger button
            rotate([handle_angle, 0, 0])
            translate([0, -handle_top_d/2 + 0.6, -20])
            rotate([90, 0, 0])
            rounded_rect(15.0, 19.0, 3.0, 4.0, true);
        }

        // [D] Internal Chambers & Battery Room
        
        // Battery Room (Hollow cylinder for slide-in insertion from bottom)
        rotate([handle_angle, 0, 0])
        translate([0, 0, -handle_h-1])
        cylinder(h=handle_h+10, d=battery_diam);
        
        // Snap recesses for the battery cap inside the battery cylinder (at Z = -handle_h + 6.0)
        rotate([handle_angle, 0, 0])
        translate([0, 0, -handle_h + 6.0]) {
            translate([-battery_diam/2, 0, 0]) sphere(d=1.8);
            translate([battery_diam/2, 0, 0]) sphere(d=1.8);
        }

        // Keyway slot for battery cap alignment (+Y side)
        rotate([handle_angle, 0, 0])
        translate([0, battery_diam/2, -handle_h])
        cube([3.0, 2.0, 8.0], center=true);
        
        // Trigger Button Hole through handle wall
        rotate([handle_angle, 0, 0])
        translate([0, -handle_top_d/2, -20])
        rotate([90, 0, 0])
        cylinder(h=wall*5, d=11.0, center=true);

        // Slide Switch Cutout on the left side (-X) near the bottom (Option B)
        rotate([handle_angle, 0, 0]) {
            // 1. Recessed pocket for the switch body (depth 5.0mm, width 10.0mm, height 20.0mm)
            translate([-18.0 + 2.5, 0, -handle_h + 16.0])
            cube([5.0, 10.0, 20.0], center=true);
            
            // 2. Wire passage slot through the wall (width 4.0mm, height 9.0mm, goes to battery room)
            translate([-18.0, 0, -handle_h + 16.0])
            cube([15.0, 4.0, 9.0], center=true);
            
            // 3. M2 screw holes (diameter 2.0mm, pitch 15.0mm)
            translate([-25.0, 0, -handle_h + 16.0 - 7.5])
            rotate([0, 90, 0])
            cylinder(h=15.0, d=2.0);
            
            translate([-25.0, 0, -handle_h + 16.0 + 7.5])
            rotate([0, 90, 0])
            cylinder(h=15.0, d=2.0);
        }
    }
}

module handle_slice(z, y_offset, r) {
    translate([0, y_offset, z])
    cylinder(h=0.1, r=r, center=true);
}

// Flexible Collar Module with Locking Lip and Slots
module handle_snap_collar() {
    difference() {
        union() {
            // Main collar body
            cylinder(h=9.0, d=27.6);
            // Locking lip with guide chamfers
            translate([0, 0, 9.0])
            cylinder(h=1.5, d1=27.6, d2=29.6);
            translate([0, 0, 10.5])
            cylinder(h=1.5, d1=29.6, d2=27.6);
        }
        // Hollow core for battery wires (19.2mm diameter)
        translate([0, 0, -1])
        cylinder(h=15, d=battery_diam);
        
        // Cross slots for flexing
        translate([0, 0, 7.0])
        cube([32.0, 2.0, 11.0], center=true);
        translate([0, 0, 7.0])
        cube([2.0, 32.0, 11.0], center=true);
    }
}

// --- 3. Housing Lid (Top Cover Half with Snap Clips) ---
module housing_lid() {
    difference() {
        union() {
            // [A] Outer Shell (organic head cut at split_z) with interior hollowing
            // (Hollowed first to prevent wiping out the interior bosses/pockets)
            difference() {
                intersection() {
                    housing_shape(wall_thick=0);
                    translate([-100, -50, split_z]) cube([300, 300, 100]);
                }
                housing_shape(wall_thick=wall);
            }
            
            // [B] OLED Bezel on top (recessed style)
            translate([head_w/2, 55, split_z + 8])
            rotate([-12, 0, 0])
            difference() {
                rounded_rect(oled_size[0]+8, oled_size[1]+8, 3.5, 4, true);
                translate([0, 0, 1]) rounded_rect(oled_size[0]+1.5, oled_size[1]+1.5, 4, 2, true);
            }
            
            // [C] OLED Pocket Holder & Screw Bosses (Inner diameter: 2.0mm, Outer: 5.0mm)
            translate([head_w/2, 55, split_z])
            rotate([-12, 0, 0])
            translate([0, 0, -4.5]) {
                pcb_pocket(oled_size[0], oled_size[1], support_h=4, pocket_depth=2, wall_t=1.8, clearance_t=clearance);
                
                // Add bosses on the inside lid reference
                translate([0, 0, -2.0])
                pcb_screw_bosses(23.5, 23.5, h=4.0, d_outer=5.0);
            }
            
            // [D] 4 Snap Clips extending downwards from the lid
            snap_clip_on_lid(wall + 0.2, 35.0, orient_left=true);
            snap_clip_on_lid(wall + 0.2, 80.0, orient_left=true);
            snap_clip_on_lid(head_w - wall - 0.2, 35.0, orient_left=false);
            snap_clip_on_lid(head_w - wall - 0.2, 80.0, orient_left=false);
        }

        // --- Subtract from Lid ---
        
        // Alignment groove in the lid split plane
        intersection() {
            difference() {
                housing_shape(wall_thick=1.2 - clearance/2);
                housing_shape(wall_thick=wall + clearance/2);
            }
            translate([-100, -50, split_z - 0.1]) cube([300, 300, 1.5 + 0.1 + clearance/2]);
        }

        // OLED Window cutout
        translate([head_w/2, 55, split_z + 2])
        rotate([-12, 0, 0])
        rounded_rect(oled_size[0]-2, oled_size[1]-2, 50, 2, true);
        
        // OLED Screw holes (2.0mm self-tapping)
        translate([head_w/2, 55, split_z])
        rotate([-12, 0, 0])
        translate([0, 0, -8])
        oled_screw_holes(h=10, d_inner=2.0);
        
        // Brand/Model Engraving
        translate([head_w/2, head_l - 18, split_z + 12])
        rotate([0, 0, 0])
        linear_extrude(2)
        text("QR COLDCHAIN", size=3.5, font="Arial:style=Bold", halign="center");
    }
}

// --- 4. Battery Cap (Seals handle bottom, contains USB slot) ---
module housing_battery_cap() {
    difference() {
        union() {
            // Base plate of the cap (matches bottom flare diameter ~34mm)
            cylinder(h=2.5, d=34.0);
            
            // Inserting plug (clearance of 0.3mm to fit in 19.2mm hole)
            translate([0, 0, 2.5])
            difference() {
                cylinder(h=6.0, d=battery_diam - 0.3);
                cylinder(h=7.0, d=battery_diam - 4.3); // hollow core for wire routing
            }
            
            // Snap bumps on left and right sides of the plug
            translate([0, 0, 6.0]) {
                translate([-(battery_diam-0.3)/2, 0, 0]) sphere(d=1.5);
                translate([(battery_diam-0.3)/2, 0, 0]) sphere(d=1.5);
            }
            
            // Key tab on the front edge (+Y) to align USB slot
            translate([0, (battery_diam-0.3)/2, 2.5])
            cube([2.4, 1.4, 6.0], center=true);
        }
        
        // USB Type-C slot in the middle (11.0mm x 6.0mm)
        translate([0, 0, -1])
        cube([11.0, 6.0, 10.0], center=true);
        
        // Outer recess pocket on the bottom of the cap for USB cable relief
        translate([0, 0, -0.5])
        cube([14.5, 8.5, 2.0], center=true);
    }
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
    w_pitch = 24.5;
    l_pitch = 26.0;
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

// Snap Clip Module (2D polygon extruded)
module snap_clip_on_lid(x, y, orient_left=true) {
    translate([x, y, split_z])
    rotate([90, 0, 0]) // extrude along Y direction
    linear_extrude(height=6, center=true)
    if (orient_left) {
        polygon(points=[[0.6, 0], [-0.6, 0], [-0.6, -5], [-1.4, -5], [-0.6, -8], [0.6, -8]]);
    } else {
        polygon(points=[[-0.6, 0], [0.6, 0], [0.6, -5], [1.4, -5], [0.6, -8], [-0.6, -8]]);
    }
}

// Body Snap Pocket Module (subtracted from body walls)
module body_snap_pocket(x, y, orient_left=true) {
    dir = orient_left ? -1 : 1;
    translate([x, y, split_z - 4.8])
    translate([orient_left ? -1.2 : 0, -3.5, -3.7])
    cube([1.2, 7, 3.7]);
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
    cube([oled_size[0], oled_size[1], 1.2], center=true);
    color("Black") translate([0, 0, 1]) cube([oled_size[0]-2, oled_size[1]-4, 1.2], center=true);
}

// --- Utility Modules ---
module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
        square([w-r*2, h-r*2], center=true);
    }
}
