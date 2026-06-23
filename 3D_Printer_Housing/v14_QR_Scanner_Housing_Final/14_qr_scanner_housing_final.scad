/* 
 * Ergonomic Pistol Grip GM77/ESP32 QR Scanner Housing Design V14.0 (Final Debugged)
 * 
 * Features:
 *   - 3-Piece Assembly: Left Half, Right Half, and Trigger Button.
 *   - Integrated Front Bumper Bezel (no separate bumper print required).
 *   - Flush-Mounted SSD1306 OLED:
 *     - Flat Outer Bezel Platform (Z = 49.5mm) on the top shell.
 *     - Z-position lowered (PCB center Z = 45.88mm) to press the glass flush against the ceiling.
 *     - Window enlarged to 25.3mm x 17.5mm to house the glass panel perfectly.
 *     - [V14.0 Fixed] OLED Ceiling Guide slot translation Z coordinate fixed from 3.1 to -2.9.
 *       Grips the 1.2mm PCB between Z_abs = 45.0 and 46.6mm. Prevents top shell cutting / floating debris.
 *   - Screwless GM77 Mounting with Wide Front Scanner Window:
 *     - Removed bottom screw holes. Secures GM77 by a form-fitting pocket on the Left Half 
 *       and a thick clamping block on the Right Half pressing down at Z = 16.5mm.
 *     - [V14.0 Improved] Scanner window cutout width (X-axis) expanded to head_w + 10.0 (68.0mm)
 *       to cleanly penetrate the outer walls of both Left and Right halves, keeping the scan path open.
 *   - ESP32 Slide-Fit Mounting (Pin-Up):
 *     - Flipped ESP32 DevKitC V4 180 degrees (pins facing UPwards in +Z direction).
 *     - Slide-in guide channels on Left/Right halves (Z_abs: 5.4 to 7.3mm, slot width 1.9mm).
 *     - Back side open for insertion, front side has a 2.8mm stopper wall to lock the board in place.
 *     - Removed long clamping rib from Right Half to prevent assembly collisions.
 *   - Internal layout for 18650 Battery, TP4056 charger, Voltly Boost, trigger, and slide switches.
 *   - Vertical split plane (X = head_w/2) for support-free flat printing on the bed.
 */

// [Global Parameters]
$fn = 60;
wall = 2.5;         // Wall thickness
clearance = 0.35;   // Tolerances

// [Head Part Dimensions]
head_w = 58.0;      // Width
head_l = 142.0;     // Length
head_h = 50.0;      // Height
split_x = head_w/2; // Split plane

// [Handle Part Dimensions]
handle_base_d = 40.0;
handle_top_d = 32.0;
handle_h = 105.0;
handle_angle = 18;

// [Component Sizes]
gm77_size = [27.5, 48.5, 14.0];
esp32_size = [28.2, 54.4, 1.6]; // PCB thickness only for ledge height
oled_size = [27.3, 27.3, 3.0];
battery_diam = 18.5;
tp4056_size = [25.0, 19.0, 3.5]; // PCB width/length
stepup_size = [22.0, 11.0, 3.6];
tact_size = [6.2, 6.2, 5.0];     // Pocket size for tact switch
switch_size = [6.0, 10.0, 14.0]; // Slide switch body size

// --- Main Control ---
render_part = "exploded"; // assembly, exploded, left_half, right_half, trigger, cross_section

if (render_part == "assembly") {
    color("DimGray", 0.6) housing_left_half();
    color("LightGray", 0.6) housing_right_half();
    
    // Trigger Button (Orange)
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 2, -20])
    rotate([90, 0, 0])
    color("OrangeRed") trigger_button();
    
    all_head_electronics_assembly(is_exploded=false);
    internal_electronics_assembly(is_exploded=false);
}

if (render_part == "exploded") {
    // Left Half (slid left)
    color("DimGray") translate([-35, 0, 0]) housing_left_half();
    
    // Right Half (slid right)
    color("LightGray") translate([35, 0, 0]) housing_right_half();
    
    // Trigger Button (slid forward)
    translate([head_w/2, head_l*0.6 - 20, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 15, -20])
    rotate([90, 0, 0])
    color("OrangeRed") trigger_button();
    
    all_head_electronics_assembly(is_exploded=true);
    internal_electronics_assembly(is_exploded=true);
}

if (render_part == "left_half") housing_left_half();
if (render_part == "right_half") housing_right_half();
if (render_part == "trigger") trigger_button();

if (render_part == "cross_section") {
    difference() {
        union() {
            housing_left_half();
            housing_right_half();
            
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, -handle_top_d/2 - 2, -20])
            rotate([90, 0, 0])
            color("OrangeRed") trigger_button();
            
            all_head_electronics_assembly(is_exploded=false);
            internal_electronics_assembly(is_exploded=false);
        }
        // Slice through the X midline
        translate([split_x, -50, -150])
        cube([200, 300, 300]);
    }
}

// --- 1. Left Half (Holds all component pockets/ledges) ---
module housing_left_half() {
    difference() {
        union() {
            // Cut solid shell at midline
            intersection() {
                full_housing_solid();
                translate([-100.0, -50.0, -150.0]) cube([100.0 + split_x, 300.0, 300.0]);
            }
            
            // Front-upper and rear-upper screw bosses
            for (pt = head_screw_boss_points) {
                join_screw_boss(pt[0], pt[1], true);
            }
            
            // Handle screw bosses (aligned with handle translation)
            translate([head_w/2, head_l*0.6, wall])
            handle_bosses(true);
            
            // Alignment pins (male)
            alignment_pins(true);
            
            // --- Component Pockets & Ledges (Left Half Only) ---
            
            // A. OLED Flat Ceiling Guide (Left Half side) - Align to Z_inner_flat = 47.9
            translate([head_w/2, 60.0, 47.9]) {
                // Left guide wall & shelf (grips left edge of oled PCB)
                translate([-oled_size[0]/2 - clearance - 2.0, -oled_size[1]/2, -6.0]) {
                    difference() {
                        cube([6.0, oled_size[1], 6.0]); // solid block
                        translate([2.0, -0.1, -2.9]) // [V14.0 Fixed] Z slot position mapped from 3.1 to -2.9 (Z_abs: 45.0 to 46.6)
                        cube([4.2, oled_size[1] + 0.2, 1.6]); // slot for PCB edge (1.2mm PCB)
                    }
                }
            }
            
            // B. GM77 Pocket Tray (Left Half side - Press-fit pocket)
            translate([head_w/2, 27.0, wall + 6.75]) {
                difference() {
                    // Left half of pocket body
                    translate([- (gm77_size[0]/2 + clearance + 2.5)/2, 0, 0])
                    cube([gm77_size[0]/2 + clearance + 2.5, gm77_size[1] + 2*clearance + 5.0, 13.5], center=true);
                    
                    // Inner cavity cut
                    translate([0, 0, 1.5])
                    cube([gm77_size[0] + 2*clearance, gm77_size[1] + 2*clearance, 11.0], center=true);
                    
                    // Lens opening
                    cube([gm77_size[0] - 4, gm77_size[1] - 4, 15.0], center=true);
                    
                    // Back wall wire cutout
                    translate([0, gm77_size[1]/2 + clearance, 2.0])
                    cube([16.0, 6.0, 12.0], center=true);
                    
                    // Clear split plane (X > split_x)
                    translate([gm77_size[0]/2 + 5, 0, 0]) cube([10.0, 60.0, 20.0], center=true);
                }
            }
            
            // C. ESP32 Left Slide-in Guide Channel (Left Half)
            // PCB Left Edge is at X = head_w/2 - esp32_size[0]/2 = 14.9
            // We build a guide block along X = 11.9 to 17.9, Y = 80.0 to 137.2
            translate([head_w/2 - esp32_size[0]/2 - 3.0, 80.0, wall]) {
                difference() {
                    // Solid guide block (5mm width, 57.2mm length, 7.5mm height above wall)
                    cube([6.0, 57.2, 7.5]); 
                    
                    // Slide slot cutout (PCB edge slot: X depth 3.2mm, Y length 55mm open at back, Z height 1.9mm)
                    // Positioned at X = 3.0 (PCB edge X = 14.9), Y = 2.8 to 57.8 (open at Y_max for insert)
                    // Z height from 5.4 to 7.3 (relative Z: 2.9 to 4.8 above wall)
                    translate([3.0, 2.8, 2.9])
                    cube([3.2, 55.0, 1.9]); 
                }
            }
            
            // D. Battery Cradle Trough (Semi-cylindrical cradle in handle)
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, 0, 10.0]) // Shifted battery up by 10mm
            battery_cradle(true);
            
            // E. TP4056 Charger U-Pocket (thick-walled guide pocket on Left Half)
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            tp4056_u_pocket(true);
            
            // F. Voltly Boost U-Pocket
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            stepup_u_pocket(true);
            
            // G. Trigger Tact Switch Pocket
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            tact_switch_pocket(true);
            
            // H. Wire Guide Clip
            wire_clip(true);
        }
        
        full_housing_cuts();
        left_half_holes();
        translate([head_w/2, head_l*0.6, wall])
        handle_boss_holes(true);
    }
}

// --- 2. Right Half (Clamps components securely using matching ribs/ledges) ---
module housing_right_half() {
    difference() {
        union() {
            // Cut solid shell at midline
            intersection() {
                full_housing_solid();
                translate([split_x, -50.0, -150.0]) cube([100.0, 300.0, 300.0]);
            }
            
            // Screw bosses
            for (pt = head_screw_boss_points) {
                join_screw_boss(pt[0], pt[1], false);
            }
            
            // Handle screw bosses (aligned with handle translation)
            translate([head_w/2, head_l*0.6, wall])
            handle_bosses(false);
            
            // --- Clamping Ribs & Right Ledges (Right Half Only) ---
            
            // GM77 Clamping Rib (Presses down on top of GM77 at Z = 16.5)
            // Sits at X = head_w/2 + 2.0 to press down securely near the rear of scanner module
            translate([head_w/2 + 2.0, 40.0, 16.5])
            cube([6.0, 4.0, 20.0]);
            
            // A. OLED Flat Ceiling Guide (Right Half side) - Align to Z_inner_flat = 47.9
            translate([head_w/2, 60.0, 47.9]) {
                // Right guide wall & shelf (grips right edge of oled PCB)
                translate([oled_size[0]/2 + clearance - 4.0, -oled_size[1]/2, -6.0]) {
                    difference() {
                        cube([6.0, oled_size[1], 6.0]); // solid block
                        translate([-0.2, -0.1, -2.9]) // [V14.0 Fixed] Z slot position mapped from 3.1 to -2.9 (Z_abs: 45.0 to 46.6)
                        cube([4.2, oled_size[1] + 0.2, 1.6]); // slot for PCB edge
                    }
                }
            }
            
            // B. GM77 Pocket Tray (Right Half side - Press-fit pocket)
            translate([head_w/2, 27.0, wall + 6.75]) {
                difference() {
                    // Right half of pocket body
                    translate([(gm77_size[0]/2 + clearance + 2.5)/2, 0, 0])
                    cube([gm77_size[0]/2 + clearance + 2.5, gm77_size[1] + 2*clearance + 5.0, 13.5], center=true);
                    
                    // Inner cavity cut
                    translate([0, 0, 1.5])
                    cube([gm77_size[0] + 2*clearance, gm77_size[1] + 2*clearance, 11.0], center=true);
                    
                    // Lens opening
                    cube([gm77_size[0] - 4, gm77_size[1] - 4, 15.0], center=true);
                    
                    // Back wall wire cutout
                    translate([0, gm77_size[1]/2 + clearance, 2.0])
                    cube([16.0, 6.0, 12.0], center=true);
                    
                    // Clear split plane (X < split_x)
                    translate([-gm77_size[0]/2 - 5, 0, 0]) cube([10.0, 60.0, 20.0], center=true);
                }
            }
            
            // C. [V13.0 Improved] ESP32 Right Slide-in Guide Channel (Right Half)
            // PCB Right Edge is at X = head_w/2 + esp32_size[0]/2 = 43.1
            // We build a guide block along X = 40.1 to 46.1, Y = 80.0 to 137.2
            translate([head_w/2 + esp32_size[0]/2 - 3.0, 80.0, wall]) {
                difference() {
                    // Solid guide block
                    cube([6.0, 57.2, 7.5]); 
                    
                    // Slide slot cutout (open on the left -X side, and back +Y side)
                    // Slot Z is relative Z: 2.9 to 4.8 above wall (Z_abs: 5.4 to 7.3)
                    // Slot Y is relative Y: 2.8 to 57.8
                    // Slot X is relative X: -0.2 to 3.0 (湲濡쒕�?X: 39.9??�쎌�?43.1源뚳??)
                    translate([-0.2, 2.8, 2.9])
                    cube([3.2, 55.0, 1.9]); 
                }
            }
            
            // E. Battery Cradle Trough (Right Half side)
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            translate([0, 0, 10.0])
            battery_cradle(false);
            
            // F. TP4056 Clamping Rib
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            tp4056_clamping_rib(false);
            
            // G. Voltly Boost Clamping Rib
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            stepup_clamping_rib(false);
            
            // H. Trigger Tact Switch Clamping Rib
            translate([head_w/2, head_l*0.6, wall])
            rotate([handle_angle, 0, 0])
            tact_switch_pocket(false);
            
            // I. Wire Guide Clip
            wire_clip(false);
        }
        
        full_housing_cuts();
        right_half_holes();
        handle_bosses_clearance_cut();
        translate([head_w/2, head_l*0.6, wall])
        handle_boss_holes(false);
        alignment_pins(false);
    }
}

// --- 3. Internal Solid Shell & Neck Geometry ---
module full_housing_solid() {
    union() {
        // Main head body and handle shape
        difference() {
            union() {
                housing_shape(wall_thick=0);
                
                // Handle shape
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
            // Hollow interior (leaves wall thickness)
            housing_shape(wall_thick=wall);
        }
    }
}

// --- 4. Shared Cuts ---
module full_housing_cuts() {
    // [V14.0 Improved] GM77 Optical Window Cut (through the front wall)
    // Centered at X = head_w/2, Y = 8.0 (front wall), Z = wall + 6.75 = 9.25.
    // Width (X-axis) expanded to head_w + 10.0 (68.0mm) to completely pierce both outer walls.
    translate([head_w/2, 2.0, wall + 6.75])
    rotate([90, 0, 0])
    rounded_rect(26.0, 11.5, 20.0, 1.5, true);

    // OLED Flat Outer Bezel Cut (Flattening the top dome surface)
    // We shave off the rounded dome above Z = 49.5mm in the OLED window zone.
    translate([head_w/2, 60.0, 49.5 + 5.0])
    cube([31.0, 31.0, 10.0], center=true);

    // OLED Window Cutout (centered at Y = 60.0 + 4.57 = 64.57)
    // The cutout dimensions match the glass size (24.74 x 16.90) + clearance.
    // Cut from PCB top Z=46.48 upwards.
    translate([head_w/2, 60.0 + 4.57, 46.48 + 5.0])
    rounded_rect(25.3, 17.5, 10.0, 1.5, true);

    // Rear USB slot for programming ESP32
    // Lowered Z coordinate to match the lowered ESP32 position (Z_pcb = 5.5mm)
    translate([head_w/2 - 6.5, head_l - 10.0, 1.0])
    cube([13.0, 15.0, 9.5]);

    // Ventilation Slots on Head Sides
    for(i=[0:3]) {
        translate([-1, 45 + i*9, 18]) rotate([0, 90, 0]) cylinder(h=head_w+10, d=2.0, center=true);
    }

    // Handle Interior Hollowing
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    handle_interior();

    // Wire path from head to handle (Clean vertical entry)
    translate([head_w/2, head_l*0.6 - 2.0, 0.0])
    cylinder(h=25.0, d=22.0, center=true);

    // USB Type-C connector port hole in handle bottom
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h]) {
        // Inner connector profile
        translate([0, 0, 2.5])
        cube([9.6, 3.8, 6.0], center=true);
        // Outer counterbore for cable overmold
        translate([0, 0, 0.8])
        cube([13.5, 7.5, 2.5], center=true);
    }

    // Slide Switch Cutout on Left Hand Side near base (MSL-1C2P)
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0]) {
        // Switch body clearance pocket
        translate([-17.5, 0, -handle_h + 16.0])
        cube([6.0, 11.5, 16.0], center=true);
        // Knob slot
        translate([-21.0, 0, -handle_h + 16.0])
        cube([12.0, 4.0, 9.0], center=true);
        // Screw holes for ears (M2 self-tapping, 15mm pitch)
        translate([-23.0, 0, -handle_h + 16.0 - 7.5])
        rotate([0, 90, 0])
        cylinder(h=15.0, d=1.8, center=true);
        translate([-23.0, 0, -handle_h + 16.0 + 7.5])
        rotate([0, 90, 0])
        cylinder(h=15.0, d=1.8, center=true);
    }

    // Trigger Button Slide Hole
    translate([head_w/2, head_l*0.6, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -handle_top_d/2 - 1.0, -20.0])
    rotate([90, 0, 0])
    cylinder(h=wall*4, d=10.0, center=true); // Cylindrical button hole
}

// --- 5. Assembly Screw Bosses ---
head_screw_boss_points = [
    [15, 34],        // Front-upper head corner
    [head_l - 15, 34] // Rear-upper head corner
];

module join_screw_boss(y, z, is_left) {
    boss_r = 4.5;
    if (is_left) {
        translate([split_x - split_x, y, z])
        rotate([0, 90, 0])
        cylinder(h=split_x, r=boss_r);
    } else {
        translate([split_x, y, z])
        rotate([0, 90, 0])
        cylinder(h=split_x, r=boss_r);
    }
}

module left_half_holes() {
    for (pt = head_screw_boss_points) {
        y = pt[0];
        z = pt[1];
        // Clearance hole (3.2mm)
        translate([split_x - 34.0, y, z])
        rotate([0, 90, 0])
        cylinder(h=34.2, d=3.2);
        // Counterbore (6.0mm) for screw head
        translate([split_x - 34.0, y, z])
        rotate([0, 90, 0])
        cylinder(h=28.0, d=6.0);
    }
}

// Right half screw holes (pilot holes)
module right_half_holes() {
    for (pt = head_screw_boss_points) {
        y = pt[0];
        z = pt[1];
        // Pilot hole (2.5mm for M3 self-tapping)
        translate([split_x - 0.1, y, z])
        rotate([0, 90, 0])
        cylinder(h=8.2, d=2.5);
    }
}

module handle_bosses(is_left) {
    boss_r = 4.5;
    local_points = [
        [15, -32, 16.5],
        [16, -78, 17.5]
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

// Right half needs a cut to clear the left half's protruding screw boss tips
module handle_bosses_clearance_cut() {
    // Empty placeholder to maintain compatibility with script
}

module handle_boss_holes(is_left) {
    local_points = [
        [15, -32, 16.5],
        [16, -78, 17.5]
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
                cylinder(h=r_val + 1.2, d=3.2);
                // Counterbore
                translate([-r_val - 1.0, y, z_val])
                rotate([0, 90, 0])
                cylinder(h=r_val - 4.5, d=6.0);
            } else {
                // Pilot hole
                translate([-0.1, y, z_val])
                rotate([0, 90, 0])
                cylinder(h=8.5, d=2.5);
            }
        }
    }
}

module alignment_pins(is_left) {
    pin_points = [
        [22, 22],
        [60, 5],
        [125, 22]
    ];
    for (pt = pin_points) {
        y = pt[0];
        z = pt[1];
        if (is_left) {
            translate([split_x, y, z])
            rotate([0, 90, 0])
            cylinder(h=1.8, d=1.8);
        } else {
            translate([split_x - 0.1, y, z])
            rotate([0, 90, 0])
            cylinder(h=2.0, d=2.2);
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

// --- 6. Battery Cradle Trough ---
module battery_cradle(is_left) {
    D_bat = battery_diam + 0.4;
    L_bat = 67.0;
    
    // A simple semi-cylindrical channel to cradle the battery
    if (is_left) {
        difference() {
            // Cradle wall
            translate([0, 0, -45.0])
            cylinder(h=50.0, d=D_bat + 4.0, center=true);
            
            // Battery cavity
            translate([0, 0, -45.0])
            cylinder(h=52.0, d=D_bat, center=true);
            
            // Cut split plane (keep X < 0)
            translate([D_bat, 0, -45.0])
            cube([D_bat * 2, D_bat * 2, 60.0], center=true);
        }
    } else {
        // Clamping rib on Right Half
        difference() {
            // Cradle wall
            translate([0, 0, -45.0])
            cylinder(h=10.0, d=D_bat + 4.0, center=true);
            
            // Battery cavity
            translate([0, 0, -45.0])
            cylinder(h=12.0, d=D_bat, center=true);
            
            // Cut split plane (keep X > 0)
            translate([-D_bat, 0, -45.0])
            cube([D_bat * 2, D_bat * 2, 20.0], center=true);
        }
    }
}

// --- 7. Simplified TP4056 & Boost Pockets (Left Half) & Ribs (Right Half) ---
module tp4056_u_pocket(is_left) {
    z_bottom = -handle_h + 3.0;
    pcb_w = tp4056_size[1] + 2*clearance;
    pcb_t = tp4056_size[2] + 0.2;
    
    if (is_left) {
        translate([-pcb_t/2 - 2.0, 0, z_bottom + 12.5]) {
            difference() {
                // Pocket body block
                cube([pcb_t + 2.0, pcb_w + 5.0, 25.0], center=true);
                // Inside cavity (slides in from split plane +X)
                translate([1.0, 0, 0])
                cube([pcb_t + 0.2, pcb_w, 26.0], center=true);
                // Cut away bottom front for USB-C cable connector entry clearance
                translate([0, 0, -12.5])
                cube([6.0, 10.0, 4.0], center=true);
            }
        }
    }
}

module tp4056_clamping_rib(is_right) {
    z_bottom = -handle_h + 3.0;
    pcb_w = tp4056_size[1] + 2*clearance;
    
    // Sits at X = 0.6 to press PCB into left pocket
    translate([0.6, 0, z_bottom + 12.5])
    cube([1.5, pcb_w - 4.0, 20.0], center=true);
}

module stepup_u_pocket(is_left) {
    z_bottom = -handle_h + 32.0;
    pcb_w = stepup_size[1] + 2*clearance;
    pcb_t = stepup_size[2] + 0.2;
    
    if (is_left) {
        translate([-pcb_t/2 - 2.0, 0, z_bottom + 11.0]) {
            difference() {
                cube([pcb_t + 2.0, pcb_w + 5.0, 22.0], center=true);
                translate([1.0, 0, 0])
                cube([pcb_t + 0.2, pcb_w, 23.0], center=true);
            }
        }
    }
}

module stepup_clamping_rib(is_right) {
    z_bottom = -handle_h + 32.0;
    pcb_w = stepup_size[1] + 2*clearance;
    
    translate([0.6, 0, z_bottom + 11.0])
    cube([1.5, pcb_w - 3.0, 16.0], center=true);
}

// --- 8. Tact Switch Pocket (AK-TS-I015-42, 6x6x11mm) ---
module tact_switch_pocket(is_left) {
    if (is_left) {
        translate([0, -handle_top_d/2 + 7.0, -20.0]) {
            difference() {
                // Outer pocket box (Left half only)
                translate([-3.1, 0, 0])
                cube([6.2, 8.0, 9.0], center=true);
                
                // Switch body pocket (6.2 x 6.2 x 5.0 deep)
                translate([-3.1, 1.5, 0])
                cube([6.4, 5.2, 6.4], center=true);
                
                // Button plunger opening (diameter 4.2mm)
                translate([-3.1, -3.0, 0])
                rotate([90, 0, 0])
                cylinder(h=5.0, d=4.2, center=true);
                
                // Wire exit slot in the bottom (-Z side) for clean exit
                translate([-3.1, 1.5, -4.0])
                cube([5.0, 4.0, 3.0], center=true);
            }
        }
    } else {
        // Clamping wall on Right Half to lock switch in pocket when closed
        translate([0, -handle_top_d/2 + 7.0, -20.0]) {
            difference() {
                // Clamping wall
                translate([3.1, 0, 0])
                cube([6.2, 8.0, 9.0], center=true);
                
                // Matching switch body recess (half width)
                translate([3.1, 1.5, 0])
                cube([6.4, 5.2, 6.4], center=true);
                
                // Plunger opening
                translate([3.1, -3.0, 0])
                rotate([90, 0, 0])
                cylinder(h=5.0, d=4.2, center=true);
                
                // Wire exit slot
                translate([3.1, 1.5, -4.0])
                cube([5.0, 4.0, 3.0], center=true);
            }
        }
    }
}

// --- 9. Wire Guide Clip ---
module wire_clip(is_left) {
    if (is_left) {
        // Simple solid clip guide hook on Left Half wall
        translate([wall + 1.5, 75, wall + 3.0])
        rotate([90, 0, 0])
        difference() {
            cylinder(h=5.0, r=3.5, center=true);
            cylinder(h=7.0, r=2.0, center=true);
            translate([0, 2.5, 0]) cube([6.0, 3.0, 7.0], center=true);
        }
    } else {
        // Right side hook
        translate([head_w - wall - 1.5, 75, wall + 3.0])
        rotate([90, 0, 0])
        difference() {
            cylinder(h=5.0, r=3.5, center=true);
            cylinder(h=7.0, r=2.0, center=true);
            translate([0, 2.5, 0]) cube([6.0, 3.0, 7.0], center=true);
        }
    }
}

// --- 10. Head Geometry Helpers ---
module slice(y, w, h, r, wall_thick=0) {
    real_w = max(4.0, w - 2 * wall_thick);
    real_h = max(4.0, h - 2 * wall_thick);
    real_r = max(1.0, r - wall_thick);
    z_center = real_h/2 + wall_thick;
    translate([head_w/2, y, z_center])
    rotate([90, 0, 0])
    rounded_rect(real_w, real_h, 1.0, real_r, true);
}

module housing_shape(wall_thick=0) {
    y_front = 8.0 + wall_thick;
    y_rear = head_l - 2.0 - wall_thick;
    
    // Front bumper ring is fully integrated into the housing shape.
    hull() {
        slice(y_front, head_w, head_h, 10.0, wall_thick);
        slice(head_l * 0.35, head_w + 2.0, head_h + 2.0, 12.0, wall_thick);
        slice(head_l * 0.70, head_w, head_h, 10.0, wall_thick);
        slice(y_rear, head_w * 0.95, head_h * 0.95, 8.0, wall_thick);
    }
}

module handle_slice(z, y_offset, r) {
    translate([0, y_offset, z])
    cylinder(h=0.1, r=r, center=true);
}

// --- 11. Trigger Button (Cylindrical Sliding Piston with Stop Flange) ---
module trigger_button() {
    rotate([90, 0, 0]) {
        // Finger contact curved cap
        cylinder(h=1.5, d=9.8, center=true);
        translate([0, 0, 1.0]) sphere(d=9.8);
        
        // Piston slider body
        translate([0, 0, -4.5])
        cylinder(h=9.0, d=9.6, center=true);
        
        // Stop flange
        translate([0, 0, -9.5])
        cylinder(h=1.5, d=12.2, center=true);
        
        // Plunger stem (hits tact switch)
        translate([0, 0, -13.5])
        cylinder(h=6.0, d=4.0, center=true);
    }
}

// --- 12. Screw Boss Helper Modules ---
module pcb_screw_bosses(w_pitch, l_pitch, h, d_outer) {
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module gm77_screw_holes(h, d_inner) {
    w_pitch = 24.6;
    l_pitch = 26.4;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

// --- 13. Component Mockups for Visual Placement ---
module gm77_mockup() {
    color("Green") cube(gm77_size, center=true);
    color("Black") translate([0, -gm77_size[1]/2 - 1.5, 0]) rotate([90, 0, 0]) cylinder(h=4.0, d=10.0, center=true);
}

module esp32_mockup() {
    // ESP32 PCB
    color("Green") cube([esp32_size[0], esp32_size[1], 1.6], center=true);
    color("Silver") translate([0, 2.0, 3.0]) cube([15.0, 22.0, 3.5], center=true);
    color("Black") translate([0, esp32_size[1]/2 - 3.0, 2.0]) cube([8.0, 8.0, 4.5], center=true);
    
    // Visual UP-ward pin headers (for verification)
    color("Black") {
        translate([-12.7, 0, 4.5]) cube([1.2, 48.0, 8.0], center=true);
        translate([12.7, 0, 4.5]) cube([1.2, 48.0, 8.0], center=true);
    }
}

module oled_mockup() {
    // PCB (27.3 x 27.3 x 1.2)
    color("Blue") cube([oled_size[0], oled_size[1], 1.2], center=true);
    
    // Display Glass panel on the front face (+Z side)
    color("DimGray")
    translate([0, 4.57, 0.6 + 0.71])
    cube([24.74, 16.90, 1.42], center=true);
    
    // Active Area screen
    color("MidnightBlue")
    translate([0, 4.57, 0.6 + 1.42 + 0.05])
    cube([21.74, 10.86, 0.1], center=true);
    
    // OLED Header pins (on the back face at -Z side, near the top +Y side, pointing down -Z)
    color("Gold")
    translate([0, oled_size[1]/2 - 1.5, -0.6 - 3.0])
    cube([10.0, 1.2, 6.0], center=true); // Pin header pointing down (-Z)
    
    // DuPont connector housing (black plastic body) plugged into the pins, extending downwards
    color("Black")
    translate([0, oled_size[1]/2 - 1.5, -0.6 - 12.0])
    cube([12.0, 2.5, 12.0], center=true); // extending downwards in Z
}

module battery_mockup() {
    color("LimeGreen") {
        cylinder(h=67.0, d=18.4, center=true);
        translate([0, 0, 33.5]) cylinder(h=1.5, d=9.0, center=true);
    }
}

module tp4056_mockup() {
    color("Green") cube([tp4056_size[2], tp4056_size[1], tp4056_size[0]], center=true);
    color("Silver")
    translate([0, 0, -tp4056_size[0]/2 - 1.5])
    cube([3.2, 9.0, 5.0], center=true);
}

module stepup_mockup() {
    color("DarkCyan") cube([stepup_size[2], stepup_size[1], stepup_size[0]], center=true);
    color("Blue") translate([stepup_size[2]/2 + 2.0, 0, 5.0]) cube([4.0, 4.0, 4.0], center=true);
}

module switch_mockup() {
    color("Gray") cube([switch_size[0], switch_size[2], switch_size[1]], center=true);
    color("Black") translate([-switch_size[0]/2 - 2.5, 0, 0]) cube([5.0, 2.0, 3.0], center=true);
}

module tact_switch_mockup() {
    color("DarkSlateGray") cube([6.0, 6.0, 5.0], center=true);
    color("Red") translate([0, -6.0, 0]) rotate([90, 0, 0]) cylinder(h=6.0, d=3.2, center=true);
}

module all_head_electronics_assembly(is_exploded=false) {
    gm77_offset = is_exploded ? 20 : 0;
    esp32_offset = is_exploded ? 25 : 0;
    oled_offset = is_exploded ? 20 : 0;
    
    // GM77
    translate([head_w/2, 27.0, wall + 6.75 + gm77_offset])
    gm77_mockup();
    
    // ESP32 (Flipped for Pin-Up: Z = wall + 3.8 = 6.3mm for PCB center)
    translate([head_w/2, head_l - 32.0, wall + 3.8 + esp32_offset])
    esp32_mockup();
    
    // OLED (Flat against the ceiling inside the flat bezel at Z = 45.88mm)
    translate([head_w/2, 60.0, 45.88 + oled_offset])
    rotate([0, 0, 0])
    oled_mockup();
}

module internal_electronics_assembly(is_exploded=false) {
    bat_offset = is_exploded ? [0, 0, 30] : [0, 0, 0];
    tp_offset = is_exploded ? [0, 0, -30] : [0, 0, 0];
    su_offset = is_exploded ? [0, 25, 0] : [0, 0, 0];
    sw_offset = is_exploded ? [-25, 0, 0] : [0, 0, 0];
    tact_offset = is_exploded ? [0, -20, 0] : [0, 0, 0];
    
    translate([head_w/2, head_l*0.6, wall]) {
        rotate([handle_angle, 0, 0]) {
            // 1. Battery (Elevated Z=-45.0)
            translate([0, 0, -45.0] + bat_offset)
            battery_mockup();
            
            // 2. TP4056 vertical board (Z=-105 to -80)
            translate([0, 0, -handle_h + 15.5] + tp_offset)
            tp4056_mockup();
            
            // 3. Voltly Boost Module (Z=-73 to -51)
            translate([0, 0, -handle_h + 43.0] + su_offset)
            stepup_mockup();
            
            // 4. Slide Switch MSL-1C2P
            translate([-17.5, 0, -handle_h + 16.0] + sw_offset)
            switch_mockup();
            
            // 5. Tact Switch (behind trigger plunger)
            translate([0, -handle_top_d/2 + 7.0, -20.0] + tact_offset)
            rotate([0, 0, 0])
            tact_switch_mockup();
        }
    }
}

// --- Helper rounded rect ---
module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
        square([w-r*2, h-r*2], center=true);
    }
}

