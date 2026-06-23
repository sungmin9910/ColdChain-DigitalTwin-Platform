/* 
 * Ergonomic Pistol Grip GM77/ESP32 QR Scanner Housing Design V4.0
 * 
 * Author: Antigravity AI (Google DeepMind)
 * Features:
 *   - Flared front nose bumper ring (black rubber-like visual bezel)
 *   - Fully rounded, organic domed head
 *   - Internal flange handle mating (seamless neck with no external plates)
 *   - Ergonomic S-Curve Handle with 18 degree tilt (no trigger guard loop)
 *   - Curved finger-contour trigger button
 *   - USB Type-C charging port slot at the bottom of the handle
 *   - Snap/slide-in pockets for GM77, ESP32, and OLED (SSD1306)
 *   - Solid Screw Bosses (bosses) for proper M3 screw assembly
 */

// [Global Parameters]
$fn = 60;
wall = 2.5;         // Wall thickness
clearance = 0.4;    // Tolerances

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
battery_diam = 22.0;             // Battery (18650 in holder)

// --- Main Control ---
render_part = "exploded"; // assembly, exploded, print_all, body, handle, lid, cross_section

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

if (render_part == "assembly") {
    color("DimGray") housing_body();
    color("DimGray") translate([head_w/2, head_l*0.6, wall]) housing_handle();
    color("DimGray") housing_lid();
    color("DarkSlateGray") front_bumper();
    
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
}

if (render_part == "body") print_body();
if (render_part == "handle") print_handle();
if (render_part == "lid") print_lid();

if (render_part == "cross_section") {
    difference() {
        union() {
            housing_body();
            translate([head_w/2, head_l*0.6, wall]) housing_handle();
            housing_lid();
            front_bumper();
            
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
            // [A] Outer Shell (organic head cut at split_z)
            intersection() {
                housing_shape(wall_thick=0);
                translate([-100, -50, -10]) cube([300, 300, split_z + 10]);
            }
            
            // [B] Internal Screw Bosses (Columns for M3 screws)
            translate([0, 0, wall])
            screw_bosses(h = split_z - wall, d_outer = 6.8);
            
            // [C] ESP32 Pocket Holder
            translate([head_w/2, head_l - 32.0, wall + 6.5]) {
                pcb_pocket(esp32_size[0], esp32_size[1], support_h=10, pocket_depth=3, wall_t=2, clearance_t=clearance);
            }
            
            // [D] GM77 Pocket Holder
            translate([head_w/2, 27.0, wall + 6.75]) {
                pcb_pocket(gm77_size[0], gm77_size[1], support_h=10.5, pocket_depth=3, wall_t=2, clearance_t=clearance);
            }
        }

        // --- Subtract from Body ---
        
        // Hollowing out the head interior
        housing_shape(wall_thick=wall);
        
        // ESP32 Screw holes (M3, 2.5mm tap)
        translate([head_w/2, head_l - 32.0, wall - 1]) {
            esp32_screw_holes(h=20, d_inner=2.5);
        }
        
        // GM77 Screw holes (M2, 1.8mm tap)
        translate([head_w/2, 27.0, wall - 1]) {
            gm77_screw_holes(h=20, d_inner=1.8);
        }

        // Handle Connector Hole (Collar entry slot, recess size handle_top_d + clearance)
        translate([head_w/2, head_l*0.6, -1])
        cylinder(h=wall*2, d=handle_top_d + 0.8);

        // Battery Wiring Hole (cylinder through bottom wall)
        translate([head_w/2, head_l*0.6, -2])
        cylinder(h=wall*4, d=battery_diam);

        // Flange Mounting Holes (M3, 3.4mm pass-through from inside the body)
        translate([head_w/2, head_l*0.6, -2]) {
            flange_screw_holes(h=15, d=3.4);
        }

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
        
        // Lid Mounting holes (M3 pass-through and countersinks from bottom)
        body_screw_passes(3.4);
        body_screw_countersinks(6.0);
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
            
            // [B] Internal Mounting Collar (slides inside the head bottom cutout)
            translate([0, 0, 0])
            rounded_rect(handle_top_d - 0.4, handle_top_d - 0.4, 8, 4.5, true);

            // [C] Recessed collar bezel for trigger button
            rotate([handle_angle, 0, 0])
            translate([0, -handle_top_d/2 + 0.6, -20])
            rotate([90, 0, 0])
            rounded_rect(15.0, 19.0, 3.0, 4.0, true);
        }

        // [D] Internal Chambers & Screws
        
        // Battery Room (Hollow cylinder)
        rotate([handle_angle, 0, 0])
        translate([0, 0, -handle_h-1])
        cylinder(h=handle_h+10, d=battery_diam);
        
        // Flange Mounting Screws (M3, 2.5mm tap holes extending downwards)
        flange_screw_holes(h=15, d=2.5);
        
        // Trigger Button Hole through handle wall
        rotate([handle_angle, 0, 0])
        translate([0, -handle_top_d/2, -20])
        rotate([90, 0, 0])
        cylinder(h=wall*5, d=11.0, center=true);

        // USB Type-C Charging Port Slot at the bottom of the handle
        rotate([handle_angle, 0, 0])
        translate([0, -4.5, -handle_h - 1]) {
            // Main connector hole
            cube([10.5, 5.8, 12], center=true);
            // Outer pocket for USB cable strain relief
            translate([0, 0, 2])
            cube([14.0, 8.0, 6], center=true);
        }
    }
}

module handle_slice(z, y_offset, r) {
    translate([0, y_offset, z])
    cylinder(h=0.1, r=r, center=true);
}

// --- 3. Housing Lid (Top Cover Half) ---
module housing_lid() {
    difference() {
        union() {
            // [A] Outer Shell (organic head cut at split_z)
            intersection() {
                housing_shape(wall_thick=0);
                translate([-100, -50, split_z]) cube([300, 300, 100]);
            }
            
            // [B] OLED Bezel on top (recessed style)
            translate([head_w/2, 55, split_z + 8])
            rotate([-12, 0, 0])
            difference() {
                rounded_rect(oled_size[0]+8, oled_size[1]+8, 3.5, 4, true);
                translate([0, 0, 1]) rounded_rect(oled_size[0]+1.5, oled_size[1]+1.5, 4, 2, true);
            }
            
            // [C] OLED Pocket Holder (extending downwards inside)
            translate([head_w/2, 55, split_z])
            rotate([-12, 0, 0])
            translate([0, 0, -4.5]) {
                pcb_pocket(oled_size[0], oled_size[1], support_h=4, pocket_depth=2, wall_t=1.8, clearance_t=clearance);
            }
            
            // [D] Internal Screw Bosses (Lid columns for screws)
            translate([0, 0, split_z])
            intersection() {
                screw_bosses(h = 20, d_outer = 6.8);
                // Keep inside lid boundaries
                housing_shape(wall_thick=0);
            }
        }

        // --- Subtract from Lid ---
        
        // Hollowing out the lid interior
        housing_shape(wall_thick=wall);
        
        // OLED Window cutout
        translate([head_w/2, 55, split_z + 2])
        rotate([-12, 0, 0])
        rounded_rect(oled_size[0]-2, oled_size[1]-2, 20, 2, true);
        
        // OLED Screw holes (M2, 1.8mm tap)
        translate([head_w/2, 55, split_z])
        rotate([-12, 0, 0])
        translate([0, 0, -8])
        oled_screw_holes(h=10, d_inner=1.8);

        // Screw tap holes (M3 tap, d=2.5) extending up from the bottom of the lid (blind holes, not through the top)
        lid_screw_taps(2.5, 12);
        
        // Brand/Model Engraving
        translate([head_w/2, head_l - 18, split_z + 12])
        rotate([0, 0, 0])
        linear_extrude(2)
        text("QR COLDCHAIN", size=3.5, font="Arial:style=Bold", halign="center");
    }
}

// --- Component Mounting Modules ---
module pcb_pocket(pcb_w, pcb_l, support_h, pocket_depth, wall_t, clearance_t) {
    difference() {
        cube([pcb_w + 2*clearance_t + 2*wall_t, pcb_l + 2*clearance_t + 2*wall_t, support_h + pocket_depth], center=true);
        
        translate([0, 0, support_h/2])
        cube([pcb_w + 2*clearance_t, pcb_l + 2*clearance_t, pocket_depth + 0.1], center=true);
        
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

module screw_bosses(h, d_outer) {
    inset = 7;
    y_front_screw = 15;
    y_rear_screw = head_l - 12;
    translate([inset, y_front_screw, 0]) cylinder(h=h, d=d_outer);
    translate([head_w-inset, y_front_screw, 0]) cylinder(h=h, d=d_outer);
    translate([inset + 3, y_rear_screw, 0]) cylinder(h=h, d=d_outer);
    translate([head_w-inset - 3, y_rear_screw, 0]) cylinder(h=h, d=d_outer);
}

// --- Component Mockups for Exploded View ---
module trigger_button() {
    // Ergonomic rounded trigger button with finger contour curves
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
    // GM77 size: [27.5, 48.5, 14.0]
    cube(gm77_size, center=true);
    // Camera lens ring at the front
    color("Black") translate([0, -gm77_size[1]/2 - 1.5, 0]) rotate([90, 0, 0]) cylinder(h=4, d=10, center=true);
}

module esp32_mockup() {
    // esp32_size: [30.0, 56.5, 15.0]
    cube([esp32_size[0], esp32_size[1], 1.6], center=true); // Board PCB
    color("Silver") translate([0, 0, 3]) cube([15, 22, 3.5], center=true); // Shield box
    color("Black") translate([0, esp32_size[1]/2 - 3, 2]) cube([8, 8, 4.5], center=true); // USB connector
}

module oled_mockup() {
    // oled_size: [27.5, 27.5, 3.0]
    cube([oled_size[0], oled_size[1], 1.2], center=true); // Board PCB
    color("Black") translate([0, 0, 1]) cube([oled_size[0]-2, oled_size[1]-4, 1.2], center=true); // Glass screen
}

// --- Utility Modules ---
module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
        square([w-r*2, h-r*2], center=true);
    }
}

module body_screw_passes(d) {
    inset = 7;
    y_front_screw = 15;
    y_rear_screw = head_l - 12;
    // Screws insert from bottom (Z = -5) up to the split plane (Z = split_z + 1)
    translate([inset, y_front_screw, -5]) cylinder(h=split_z + 10, d=d);
    translate([head_w-inset, y_front_screw, -5]) cylinder(h=split_z + 10, d=d);
    translate([inset + 3, y_rear_screw, -5]) cylinder(h=split_z + 10, d=d);
    translate([head_w-inset - 3, y_rear_screw, -5]) cylinder(h=split_z + 10, d=d);
}

module body_screw_countersinks(d) {
    inset = 7;
    y_front_screw = 15;
    y_rear_screw = head_l - 12;
    // Countersink recesses at the bottom (Z = -2 to Z = 4)
    translate([inset, y_front_screw, -2]) cylinder(h=6, d=d);
    translate([head_w-inset, y_front_screw, -2]) cylinder(h=6, d=d);
    translate([inset + 3, y_rear_screw, -2]) cylinder(h=6, d=d);
    translate([head_w-inset - 3, y_rear_screw, -2]) cylinder(h=6, d=d);
}

module lid_screw_taps(d, h) {
    inset = 7;
    y_front_screw = 15;
    y_rear_screw = head_l - 12;
    // Blind screw tap holes extending UP from split plane, NOT going through the top lid
    translate([inset, y_front_screw, split_z - 1]) cylinder(h=h, d=d);
    translate([head_w-inset, y_front_screw, split_z - 1]) cylinder(h=h, d=d);
    translate([inset + 3, y_rear_screw, split_z - 1]) cylinder(h=h, d=d);
    translate([head_w-inset - 3, y_rear_screw, split_z - 1]) cylinder(h=h, d=d);
}

