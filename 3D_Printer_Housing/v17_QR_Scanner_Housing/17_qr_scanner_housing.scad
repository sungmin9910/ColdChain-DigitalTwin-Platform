/*
 * QR Scanner Housing V17 - Pistol Grip Style (HR2180BT Inspired)
 *
 * Key Design Features:
 *   1. Curved pistol grip handle with finger grooves, aligned on Y=0 axis.
 *   2. Flat, non-bent horizontal scanner head top profile with expanded space.
 *   3. Rear-slanted (55 degrees) OLED display optimized for user sightline.
 *   4. Side-by-side placement of the 18650 Battery and VLT-VC013 Booster in X-axis.
 *   5. Simple, circular click-style trigger push button.
 *   6. Left and Right halves split design with interlocking alignment pins.
 */

use <hardware_mockups.scad>

// =============================================
//  SECTION 1: GLOBAL PARAMETERS
// =============================================
$fn = 50;
wall   = 2.5;
clearance = 0.35;

// --- Head ---
head_w = 64.0;        // Width  (X) - Expanded from 57.0 for more interior space
head_l = 140.0;       // Length (Y) - Expanded from 130.0 for more interior space
head_h = 48.0;        // Height (Z) - Expanded from 44.0 for more interior space
split_x = head_w / 2; // 32.0

// --- Handle ---
handle_h     = 125.0; // Total length of grip along its axis (extended for battery/charger clearance)
handle_angle = 25;    // Backward sweep angle of the handle (increased from 20 for ergonomics)
neck_y       = 75.0;  // Y where handle root starts

// --- Component Sizes ---
gm77_size    = [27.5, 48.5, 14.0];
esp32_size   = [28.2, 54.4, 1.6];
oled_size    = [27.3, 27.3, 1.2]; 
battery_diam = 18.4;
tp4056_size  = [16.5, 27.5, 4.0]; 
stepup_size  = [11.0, 22.0, 3.6]; 
switch_size  = [3.5, 8.5, 3.5];   
tact_size    = [6.0, 6.0, 11.0];  

// --- Component placement coordinates (Global) ---
gm77_y  = 30.0;
gm77_z  = head_h / 2; // 24.0
esp32_y = 100.0;      // Shifted forward to avoid wire interference with OLED/ceiling and make room for connections
esp32_z = wall + 4.5; // Raised by 3.5mm to prevent Shield Can from overlapping with the housing bottom floor

// Ergonomic OLED display configurations
oled_bevel_angle = 55;
oled_pcb_y = 118.0; // Adjusted for higher Z placement and clearance
oled_z     = 34.0;  // Shifted up to 34.0 to maximize wire routing space below the PCB

// Alignment pin positions for side interlocking
align_pts = [
    [18, 10],           
    [65, 8],
    [head_l - 18, 6]    
];

// --- Assembly screw positions ---
head_screw_pts = [
    [52.0, 42.0]
];
handle_screw_pts = [
    [-11.0, -10.0],
    [12.5, -88.0]
];

// =============================================
//  SECTION 2: RENDER CONTROL
// =============================================
render_part = "assembly";
// Options: assembly, exploded, left_half, right_half, trigger, cross_section

if (render_part == "assembly") {
    color("DimGray",  0.55) housing_left_half();
    color("LightGray",0.55) housing_right_half();
    // trigger_at_pos(false); // Disabled orange trigger mockup as requested
    
    // Internal electronics
    head_electronics(false);
    handle_electronics(false);
}
else if (render_part == "exploded") {
    color("DimGray")   translate([-35, 0, 0]) housing_left_half();
    color("LightGray") translate([ 35, 0, 0]) housing_right_half();
    // trigger_at_pos(true); // Disabled orange trigger mockup as requested
    
    head_electronics(true);
    handle_electronics(true);
}
else if (render_part == "left_half") {
    housing_left_half();
}
else if (render_part == "right_half") {
    housing_right_half();
}
else if (render_part == "trigger") {
    trigger_button();
}
else if (render_part == "cross_section") {
    difference() {
        union() {
            housing_left_half();
            housing_right_half();
            // trigger_at_pos(false); // Disabled orange trigger mockup as requested
        }
        translate([split_x, -50, -200]) cube([200, 300, 400]);
    }
    head_electronics(false);
    handle_electronics(false);
}

module trigger_at_pos(exploded) {
    ey = exploded ? -18 : 0;
    translate([head_w/2, neck_y + ey, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -14, -22]) // Adjusted to match Y=0 alignment & tact switch placement
    rotate([90, 0, 0])
    color("OrangeRed") trigger_button();
}

// =============================================
//  SECTION 3: LEFT HALF
// =============================================
module housing_left_half() {
    union() {
        difference() {
            union() {
                // 1. Shell left portion
                intersection() {
                    full_shell();
                    translate([-100, -50, -200])
                    cube([100 + split_x, 300, 400]);
                }
                // 2. Alignment pins (male)
                alignment_features(true);
                // 3. Head internal mounts (Clipped to left half)
                intersection() {
                    head_outer();
                    intersection() {
                        union() {
                            gm77_pocket(true);
                            esp32_rail(true);
                        }
                        translate([-100, -50, -200]) cube([100 + split_x, 300, 400]);
                    }
                }
                // 4. Handle internal mounts (Clipped to left half local X < 0)
                intersection() {
                    handle_with_neck();
                    translate([head_w/2, neck_y, wall])
                    rotate([handle_angle, 0, 0])
                    intersection() {
                        union() {
                            battery_cradle(true);
                            charger_pocket(true);
                            boost_pocket(true);
                            tact_pocket(true);
                        }
                        translate([-50, -50, -150]) cube([50, 100, 200]);
                    }
                }
                // 5. Screw Bosses (Left Half)
                for (p = head_screw_pts) screw_boss_head(p[0], p[1], true);
                translate([head_w/2, neck_y, wall])
                rotate([handle_angle, 0, 0])
                for (p = handle_screw_pts) screw_boss_handle(p[0], p[1], true);
            }
            all_cuts();
            // Screw holes (Left Half)
            for (p = head_screw_pts) screw_hole_head(p[0], p[1], true);
            translate([head_w/2, neck_y, wall])
            rotate([handle_angle, 0, 0])
            for (p = handle_screw_pts) screw_hole_handle(p[0], p[1], true);
        }
        // 6. OLED Guide (Added AFTER cuts to prevent being carved away by the recessed pocket cutout)
        intersection() {
            head_outer();
            intersection() {
                oled_guide(true);
                translate([-100, -50, -200]) cube([100 + split_x, 300, 400]);
            }
        }
    }
}

// =============================================
//  SECTION 4: RIGHT HALF
// =============================================
module housing_right_half() {
    union() {
        difference() {
            union() {
                // 1. Shell right portion
                intersection() {
                    full_shell();
                    translate([split_x, -50, -200])
                    cube([100, 300, 400]);
                }
                // 2. Head internal mounts (Clipped to right half)
                intersection() {
                    head_outer();
                    intersection() {
                        union() {
                            gm77_pocket(false);
                            esp32_rail(false);
                        }
                        translate([split_x, -50, -200]) cube([100, 300, 400]);
                    }
                }
                // 3. Handle internal mounts (Clipped to right half local X > 0)
                intersection() {
                    handle_with_neck();
                    translate([head_w/2, neck_y, wall])
                    rotate([handle_angle, 0, 0])
                    intersection() {
                        union() {
                            battery_cradle(false);
                            charger_clamp();
                            tact_pocket(false);
                        }
                        translate([0, -50, -150]) cube([50, 100, 200]);
                    }
                }
                // 4. Screw Bosses (Right Half)
                for (p = head_screw_pts) screw_boss_head(p[0], p[1], false);
                translate([head_w/2, neck_y, wall])
                rotate([handle_angle, 0, 0])
                for (p = handle_screw_pts) screw_boss_handle(p[0], p[1], false);
            }
            all_cuts();
            alignment_features(false); // Female holes
            // Screw holes (Right Half)
            for (p = head_screw_pts) screw_hole_head(p[0], p[1], false);
            translate([head_w/2, neck_y, wall])
            rotate([handle_angle, 0, 0])
            for (p = handle_screw_pts) screw_hole_handle(p[0], p[1], false);
        }
        // 5. OLED Guide (Added AFTER cuts to prevent being carved away by the recessed pocket cutout)
        intersection() {
            head_outer();
            intersection() {
                oled_guide(false);
                translate([split_x, -50, -200]) cube([100, 300, 400]);
            }
        }
    }
}

// =============================================
//  SECTION 5: SHELL GEOMETRY
// =============================================
module full_shell() {
    difference() {
        shell_outer();
        shell_inner();
    }
}

module shell_outer() {
    difference() {
        union() {
            head_outer();
            difference() {
                handle_with_neck();
                head_inner();
            }
            neck_fill();
        }
        // Slanted cut for outer surface of the display wall (leaves wall=2.5mm thick slanted face at Z_local=3.9)
        translate([head_w/2, oled_pcb_y, oled_z])
        rotate([oled_bevel_angle, 0, 180])
        translate([0, 0, 1.4 + wall + 20.0/2]) 
        cube([head_w + 20, head_l + 20, 20.0], center=true);
    }
}

module shell_inner() {
    difference() {
        union() {
            head_inner();
            translate([head_w/2, neck_y, wall])
            rotate([handle_angle, 0, 0])
            handle_inner();
        }
        // Slanted cut for inner surface of the display wall (slanted face at Z_local=1.4)
        translate([head_w/2, oled_pcb_y, oled_z])
        rotate([oled_bevel_angle, 0, 180])
        translate([0, 0, 1.4 + 20.0/2]) 
        cube([head_w + 20, head_l + 20, 20.0], center=true);
    }
    // Wire routing passage
    translate([head_w/2, neck_y, 0])
    cylinder(h=30, d=24, center=true);
}

// Flat head profile - no slanting or bending downwards at the rear
module head_outer() {
    hull() {
        hslice(5,          head_w - 5, head_h - 2,  8,  0);
        hslice(35,         head_w - 2, head_h,      8,  0);
        hslice(70,         head_w,     head_h,      8,  0);
        hslice(head_l - 5, head_w - 2, head_h,      8,  0);
    }
}

module head_inner() {
    w2 = 2*wall;
    hull() {
        hslice(5+wall,       head_w - 5 - w2, head_h - 2 - w2, max(1,8-wall),   wall);
        hslice(35,           head_w - 2 - w2, head_h - w2,      max(1,8-wall),   wall);
        hslice(70,           head_w - w2,     head_h - w2,      max(1,8-wall),   wall);
        hslice(head_l-5-wall,head_w - 2 - w2, head_h - w2,      max(1,8-wall),   wall);
    }
}

module hslice(y, w, h, r, zoff) {
    translate([head_w/2, y, h/2 + zoff])
    rotate([90,0,0])
    rounded_rect(w, h, 1.0, r, true);
}

// --- Ergonomic Pistol Grip Handle Slice ---
// Straight local Z-axis sweeps (y_off = 0) to align with internal components
module handle_slice(z, rx, ry, r_fillet=4) {
    translate([0, 0, z])
    linear_extrude(height=0.1, center=true)
    offset(r=r_fillet)
    square([max(1.0, rx*2 - r_fillet*2), max(1.0, ry*2 - r_fillet*2)], center=true);
}

module handle_with_neck() {
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    handle_outer();
}

// Straight grip profile with finger grooves on the front side (ry variation)
// Expanded default rx from 16 to 18 to give booster and battery more X clearance
module handle_outer() {
    hull() {
        handle_slice(20,   19.0, 18.0);    // Top neck overlap
        handle_slice(0,    18.0, 17.5);    // Upper hand rest
        handle_slice(-15,  17.5, 15.5);    // Finger Groove 1 (Index/Middle)
        handle_slice(-35,  18.0, 17.5);    // Ridge 1
        handle_slice(-55,  17.5, 15.5);    // Finger Groove 2 (Ring finger)
        handle_slice(-75,  18.0, 17.5);    // Ridge 2
        handle_slice(-95,  17.5, 15.5);    // Finger Groove 3 (Little finger)
        handle_slice(-handle_h, 20.0, 22.0); // Flared bottom cap (Linked dynamically to handle_h)
    }
}

module handle_inner() {
    hull() {
        handle_slice(12,   19.0 - wall, 18.0 - wall);
        handle_slice(0,    18.0 - wall, 17.5 - wall);
        handle_slice(-15,  17.5 - wall, 15.5 - wall);
        handle_slice(-35,  18.0 - wall, 17.5 - wall);
        handle_slice(-55,  17.5 - wall, 15.5 - wall);
        handle_slice(-75,  18.0 - wall, 17.5 - wall);
        handle_slice(-95,  17.5 - wall, 15.5 - wall);
        handle_slice(-handle_h + 1.0, 20.0 - wall, 22.0 - wall); // Inner cavity bottom (Linked dynamically to handle_h)
    }
}

// Smooth neck bridge - removed the second chin-reinforcing hull block to eliminate the sharp protrusion
module neck_fill() {
    hull() {
        translate([head_w/2, neck_y - 10, wall + 2])
        cube([44, 20, 0.1], center=true);
        
        translate([head_w/2, neck_y + 8, wall + 2])
        cube([42, 16, 0.1], center=true);

        translate([head_w/2, neck_y, wall])
        rotate([handle_angle, 0, 0])
        translate([0, 0, 15])
        cylinder(h=0.1, r=20, center=true);
    }
}

// =============================================
//  SECTION 6: ALL CUTS
// =============================================
module all_cuts() {
    // 1) GM77 scanner window - front face
    translate([head_w/2, 0, gm77_z])
    rotate([90,0,0])
    rounded_rect(gm77_size[0] + 6, gm77_size[2] - 2, 20.0, 2.0, true);

    // 2) OLED display window - exposes ONLY the active screen (size: 22.5 x 11.5)
    // 2-a) Screen window cutout (pierces the outer slanted wall from Z_local = 1.4 to 10.0)
    translate([head_w/2, oled_pcb_y, oled_z])
    rotate([oled_bevel_angle, 0, 180])
    translate([0, 0, 1.4 + 10.0/2])
    rounded_rect(22.5, 11.5, 10.0, 1.5, true);

    // 2-b) Recessed pocket inside the housing to hold the PCB (size: 28.1 x 28.1, depth: 20mm)
    translate([head_w/2, oled_pcb_y, oled_z])
    rotate([oled_bevel_angle, 0, 180])
    translate([0, 0, -10.0 + 1.4])
    cube([28.1, 28.1, 20.0], center=true);

    // 3) ESP32 USB slot - rear wall (cutout lengthened to accommodate deep ESP32 placement)
    translate([head_w/2 - 6.5, head_l - 19.0, 1.0])
    cube([13.0, 21.0, 9.0]);

    // 4) Ventilation slots
    for (i=[0:3])
        translate([-1, 45 + i*10, 20])
        rotate([0,90,0])
        cylinder(h=head_w+10, d=2.0, center=true);

    // 5) USB-C charger port (Bottom of handle, Y=0)
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h]) {
        translate([0,0,2.5]) cube([10.0, 4.2, 8.0], center=true);
        translate([0,0,0.8]) cube([14.0, 8.0, 2.5], center=true);
    }

    // 6) Slide switch cutout (Y=0, X=-14.5)
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0]) {
        translate([-14.5, 0, -handle_h+16])
        cube([6.0, 11.5, 16.0], center=true);
        translate([-18.0, 0, -handle_h+16])
        cube([12.0, 4.0, 9.0], center=true);
    }

    // 7) Trigger button hole (Y=-14)
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -14, -22])
    rotate([90,0,0])
    cylinder(h=wall*4, d=10.0, center=true);
}

// =============================================
//  SECTION 7: INTERNAL MOUNTS
// =============================================

// --- 7-A GM77 Pocket ---
module gm77_pocket(is_left) {
    pw  = gm77_size[0]/2 + clearance + 2.5;   
    pl  = gm77_size[1] + 2*clearance + 3.0;
    ph  = gm77_size[2] + 1.5;
    translate([head_w/2, gm77_y, gm77_z]) {
        difference() {
            if (is_left)
                translate([-pw/2, 0, 0]) cube([pw, pl, ph], center=true);
            else
                translate([ pw/2, 0, 0]) cube([pw, pl, ph], center=true);
            
            translate([0, 0, 1.0])
            cube([gm77_size[0]+2*clearance, gm77_size[1]+2*clearance, ph], center=true);
            
            cube([gm77_size[0]-4, gm77_size[1]-4, ph+4], center=true);
            
            translate([0, gm77_size[1]/2+clearance, 1.5])
            cube([14.0, 6.0, 12.0], center=true);
        }
    }
}

// --- 7-B ESP32 Slide-in Rail ---
module esp32_rail(is_left) {
    rail_w = 5.0;
    rail_l = 55.0;
    rail_h = 8.5; // Raised to match new esp32_z standoff height
    slot_h = 1.9;
    pcb_hw = esp32_size[0] / 2;  
    if (is_left) {
        translate([head_w/2 - pcb_hw - 2.5, esp32_y - rail_l/2, wall]) {
            difference() {
                cube([rail_w, rail_l, rail_h]);
                translate([2.5, 2.5, 4.5]) // Raised PCB slot placement offset to match esp32_z (4.5mm Standoff)
                cube([3.0, rail_l - 2.5, slot_h]);
            }
        }
    } else {
        translate([head_w/2 + pcb_hw - 2.5, esp32_y - rail_l/2, wall]) {
            difference() {
                cube([rail_w, rail_l, rail_h]);
                translate([-0.2, 2.5, 4.5]) // Raised PCB slot placement offset to match esp32_z (4.5mm Standoff)
                cube([3.0, rail_l - 2.5, slot_h]);
            }
        }
    }
}

// --- 7-C OLED Clamping Stopper Ribs (Aligned to rotate [oled_bevel_angle, 0, 180]) ---
module oled_guide(is_left) {
    pcb_hw = oled_size[0]/2;
    gy = 6.0;  // Length of guide in Y (shortened from 12.0 to 6.0 for compact design)
    gz = 3.5;  // Depth of guide in Z (reduced from 8.0 to 3.5 to slim down the support bracket)
    slot_h = 1.6; // Slot height (PCB thickness 1.2 + clearance)
    
    translate([head_w/2, oled_pcb_y, oled_z])
    rotate([oled_bevel_angle, 0, 180]) {
        if (is_left) {
            // Left guide: Local +X (corresponds to Global -X / Left wall because of rotate 180)
            translate([pcb_hw - 1.5, -gy/2 - 4.0, -0.6 - gz]) {
                difference() {
                    cube([20.0, gy, gz + 2.6]);
                    // Limit slot cut to 1.55mm width to keep outer wall support solid
                    translate([1.3, -1.0, gz - 0.2]) 
                    cube([1.55, gy + 2.0, slot_h]);
                }
            }
        } else {
            // Right guide: Local -X (corresponds to Global +X / Right wall because of rotate 180)
            translate([-pcb_hw - 2.5 - 16.0, -gy/2 - 4.0, -0.6 - gz]) {
                difference() {
                    cube([20.0, gy, gz + 2.6]);
                    // Limit slot cut to 1.55mm width to keep outer wall support solid
                    translate([17.15, -1.0, gz - 0.2])
                    cube([1.55, gy + 2.0, slot_h]);
                }
            }
        }
    }
}

// --- 7-D Battery Cradle (X=3.0, Y=0, Z=-45) ---
module battery_cradle(is_left) {
    D = battery_diam + 0.4;
    x_pos = 3.0;
    if (is_left) {
        difference() {
            translate([x_pos, 0, -58]) cylinder(h=50, d=D+4, center=true); // Lowered from -45 to -58 to avoid switch collision
            translate([x_pos, 0, -58]) cylinder(h=52, d=D, center=true);
            translate([x_pos + D, 0, -58]) cube([D*2, D*2, 60], center=true);
            // Cutout to allow the boost converter module and wiring to pass through the cradle wall
            translate([-12.0, 0, -58]) cube([15.0, 15.0, 30.0], center=true);
        }
    } else {
        difference() {
            translate([x_pos, 0, -58]) cylinder(h=12, d=D+4, center=true);
            translate([x_pos, 0, -58]) cylinder(h=14, d=D, center=true);
            translate([x_pos - D, 0, -58]) cube([D*2, D*2, 20], center=true);
        }
    }
}

// --- 7-E TP4056 Charger Pocket (Y=0) ---
module charger_pocket(is_left) {
    zb = -handle_h + 1.25; 
    pw = tp4056_size[0] + 2*clearance; 
    pt = tp4056_size[2] + 0.2;         
    if (is_left) {
        translate([-pt/2 - 2.0, 0, zb + 12.5])
        difference() {
            cube([pt + 2.0, pw + 5.0, 25.0], center=true);
            translate([1.0, 0, 0])
            cube([pt + 0.2, pw, 26.0], center=true);
            translate([0, 0, -12.5])
            cube([6.0, 10.0, 4.0], center=true);
        }
    }
}

module charger_clamp() {
    zb = -handle_h + 1.25;
    pw = tp4056_size[0] + 2*clearance;
    translate([0.6, 0, zb + 12.5])
    cube([1.5, pw - 4.0, 20.0], center=true);
}

// --- 7-F Boost Pocket side-by-side with Battery (X=-12.0, Y=0, Z=-45) ---
// Designed as a hollow tube (open at Z-ends) for clean wiring below battery to charger
module boost_pocket(is_left) {
    x_pos = -10.5; // Shifted slightly right to merge solidly with the battery cradle wall
    z_pos = -58.0; // Lowered from -45.0 to -58.0 to match lowered battery
    pw = stepup_size[0] + 2*clearance; 
    pt = stepup_size[2] + 0.2;         
    pl = 22.0;                         
    if (is_left) {
        translate([x_pos, 0, z_pos]) {
            difference() {
                // outer box
                cube([pt + 3.0, pw + 4.0, pl + 3.0], center=true);
                // inner slot (open at both top and bottom with +10.0 height overlap)
                cube([pt, pw, pl + 10.0], center=true);
                // wire slot cuts on front and back
                cube([pt + 5.0, pw - 4.0, pl + 10.0], center=true);
            }
        }
    }
}

module boost_clamp() {
    // Empty to avoid floating geometries
}

// --- 7-G Tact Switch Pocket (Y=-14) ---
module tact_pocket(is_left) {
    translate([0, -14, -22]) {
        if (is_left) {
            difference() {
                translate([-3.1, 0, 0]) cube([6.2, 8.0, 9.0], center=true);
                translate([-3.1, 1.0, 0]) cube([6.4, 5.2, 6.4], center=true);
                translate([-3.1,-3.0, 0]) rotate([90,0,0]) cylinder(h=5, d=4.2, center=true);
                translate([-3.1, 1.0,-4]) cube([5,4,3], center=true);
            }
        } else {
            difference() {
                translate([3.1, 0, 0]) cube([6.2, 8.0, 9.0], center=true);
                translate([3.1, 1.0, 0]) cube([6.4, 5.2, 6.4], center=true);
                translate([3.1,-3.0, 0]) rotate([90,0,0]) cylinder(h=5, d=4.2, center=true);
                translate([3.1, 1.0,-4]) cube([5,4,3], center=true);
            }
        }
    }
}

// Alignment features (Pins)
module alignment_features(is_left) {
    for (p = align_pts) {
        y = p[0]; z = p[1];
        if (is_left)
            translate([split_x, y, z]) rotate([0,90,0]) cylinder(h=1.8, d=1.8);
        else
            translate([split_x-0.1, y, z]) rotate([0,90,0]) cylinder(h=2.0, d=2.2);
    }
}

// =============================================
//  SECTION 7-H: ASSEMBLY SCREW BOSSES & HOLES (NEW)
// =============================================

module screw_boss_head(y, z, is_left) {
    br = 4.0;
    intersection() {
        if (is_left)
            translate([0, y, z]) rotate([0,90,0]) cylinder(h=split_x, r=br);
        else
            translate([split_x, y, z]) rotate([0,90,0]) cylinder(h=split_x, r=br);
        head_outer();
    }
}

module screw_hole_head(y, z, is_left) {
    if (is_left) {
        // M3 clearance hole
        translate([-1, y, z]) rotate([0,90,0]) cylinder(h=split_x+2, d=3.2);
        // Countersink recess leaving a 5mm mounting wall
        translate([-1, y, z]) rotate([0,90,0]) cylinder(h=split_x-5, d=6.0);
    } else {
        // M3 pilot hole
        translate([split_x-0.1, y, z]) rotate([0,90,0]) cylinder(h=10, d=2.5);
    }
}

module screw_boss_handle(ly, lz, is_left) {
    br = 4.0;
    intersection() {
        if (is_left)
            translate([-22.0, ly, lz]) rotate([0,90,0]) cylinder(h=22.0, r=br);
        else
            translate([0, ly, lz])   rotate([0,90,0]) cylinder(h=22.0, r=br);
        handle_outer();
    }
}

module screw_hole_handle(ly, lz, is_left) {
    if (is_left) {
        // Clearance hole through left handle boss
        translate([-22, ly, lz]) rotate([0,90,0]) cylinder(h=23, d=3.2);
        // Countersink recess leaving a 5mm mounting wall
        translate([-22, ly, lz]) rotate([0,90,0]) cylinder(h=17, d=6.0);
    } else {
        // Pilot hole
        translate([-0.1, ly, lz]) rotate([0,90,0]) cylinder(h=10, d=2.5);
    }
}

// =============================================
//  SECTION 8: SIMPLE CLICK-STYLE TRIGGER BUTTON
// =============================================
module trigger_button() {
    rotate([90,0,0]) {
        cylinder(h=1.5, d=9.8, center=true);
        translate([0,0,1.0]) sphere(d=9.8);
        translate([0,0,-4.5]) cylinder(h=9.0, d=9.6, center=true);
        translate([0,0,-9.5]) cylinder(h=1.5, d=12.2, center=true);
        translate([0,0,-13.5]) cylinder(h=6.0, d=4.0, center=true);
    }
}

// =============================================
//  SECTION 9: ELECTRONICS ASSEMBLY VIEWS
// =============================================
module head_electronics(exploded) {
    g_off = exploded ? [0, -25, 0] : [0, 0, 0];
    e_off = exploded ? [0, 0, 25]  : [0, 0, 0];
    o_off = exploded ? [0, 25, 0]  : [0, 0, 0];

    // GM77 Scanner
    translate([head_w/2, gm77_y, gm77_z] + g_off)
        gm77_scanner_mockup();

    // ESP32 DevKitC V4 (Flipped 180 deg)
    translate([head_w/2, esp32_y, esp32_z] + e_off)
        rotate([180, 0, 0])
            esp32_devkitc_mockup();

    // SSD1306 OLED (Slanted at 55 deg)
    translate([head_w/2, oled_pcb_y, oled_z] + o_off)
        rotate([oled_bevel_angle, 0, 180])
            ssd1306_oled_mockup();
}

module handle_electronics(exploded) {
    bo = exploded ? [0, 0, 35]  : [0, 0, 0];
    tp = exploded ? [0, 0, -35] : [0, 0, 0];
    su = exploded ? [0, 25, 0]  : [0, 0, 0];
    sw = exploded ? [-25, 0, 0] : [0, 0, 0];
    ta = exploded ? [0, -20, 0] : [0, 0, 0];

    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0]) {
        // Battery (X=3.0, Y=0, Z=-58)
        translate([3.0, 0, -58] + bo) 
            rotate([-90, 0, 0])
                battery_18650_wire();
        
        // Charger Module TP4056 (Y=0)
        translate([0, 0, -handle_h + 13.75] + tp) 
            rotate([90, 0, 90])
                charger_module_tp4056();
        
        // Boost Converter VLT-VC013 (X=-10.5, Y=0, Z=-58)
        translate([-10.5, 0, -58.0] + su) 
            rotate([90, 0, 90])
                booster_module_vlt_vc013();
        
        // Slide Switch MSL-1C2P (Y=0)
        translate([-14.5, 0, -handle_h + 16.0] + sw) 
            rotate([0, -90, 0])
                slide_switch_msl_1c2p();
        
        // Tact Trigger Switch
        translate([0, -14, -22.0] + ta) 
            rotate([90, 0, 0])
                tact_switch_h11();
    }
}

// Helper module for rounded rectangle extrusion
module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
        square([w - r*2, h - r*2], center=true);
    }
}
