/*
 * QR Scanner Housing V16.3 - Screwless Structure & Corrected Bevel Alignment
 *
 * Major revisions:
 *   1. OLED display rotation corrected to rotate([-55, 0, 0]) so that the screen faces the rear bevel window
 *      and the I2C gold pin headers face inside the housing cavity.
 *   2. TP4056 USB-C charger board rotation restored to original rotate([90, 0, 90]).
 *   3. All screw bosses and screw hole cuts are completely deactivated/removed from the housing halves
 *      to prepare for a screwless locking mechanism.
 *   4. Bevel rear cut and display guide path dynamically matched.
 */

// =============================================
//  SECTION 1: GLOBAL PARAMETERS
// =============================================
$fn = 50;
wall   = 2.5;
clearance = 0.35;

// --- Head ---
head_w = 58.0;     // Width  (X)
head_l = 130.0;    // Length (Y)  front=0, back=130
head_h = 50.0;     // Height (Z)
split_x = head_w / 2; // 29.0

// --- Handle ---
handle_h     = 105.0;
handle_angle = 20;
neck_y       = 75.0;   // Y where handle root starts

// --- Component Sizes ---
gm77_size    = [27.5, 48.5, 14.0];
esp32_size   = [28.2, 54.4, 1.6];
oled_size    = [27.3, 27.3, 1.2]; // PCB thickness = 1.2
battery_diam = 18.4;
tp4056_size  = [16.5, 27.5, 4.0]; 
stepup_size  = [11.0, 22.0, 3.6]; 
switch_size  = [3.5, 8.5, 3.5];   
tact_size    = [6.0, 6.0, 11.0];  

// --- Component placement coordinates ---
gm77_y  = 30.0;
gm77_z  = head_h / 2;  // Centered vertically to Z=25.0
esp32_y = 85.0;
esp32_z = wall + 3.5;

// Ergonomic 35-degree OLED display slope configurations
oled_bevel_angle = 35;
oled_pcb_y = 114.0;         // Lowered and pulled forward to fit internal space
oled_z     = 25.0;         // Lowered to prevent protruding through outer shell

// --- Assembly screw positions [y, z] in head coords ---
// (Kept as references, but deactivated in rendering)
head_screw_pts = [
    [70,  18],          
    [100, 10]           
];
// Handle screw positions [local_y, local_z]
handle_screw_pts = [
    [8, -30],
    [8, -78]
];
// Alignment pin positions [y, z] in head coords (kept for alignment)
align_pts = [
    [18, 10],           
    [65, 8],
    [head_l - 18, 6]    
];

// =============================================
//  SECTION 2: RENDER CONTROL
// =============================================
render_part = "assembly";
// Options: assembly, exploded, left_half, right_half, trigger, cross_section

if (render_part == "assembly") {
    color("DimGray",  0.55) housing_left_half();
    color("LightGray",0.55) housing_right_half();
    trigger_at_pos(false);
    
    // Internal electronics
    head_electronics(false);
    handle_electronics(false);
}
else if (render_part == "exploded") {
    color("DimGray")   translate([-35, 0, 0]) housing_left_half();
    color("LightGray") translate([ 35, 0, 0]) housing_right_half();
    trigger_at_pos(true);
    
    head_electronics(true);
    handle_electronics(true);
}
else if (render_part == "left_half") {
    housing_left_half();
    head_electronics(false);
    handle_electronics(false);
}
else if (render_part == "right_half") {
    housing_right_half();
    head_electronics(false);
    handle_electronics(false);
}
else if (render_part == "trigger") {
    trigger_button();
}
else if (render_part == "cross_section") {
    difference() {
        union() {
            housing_left_half();
            housing_right_half();
            trigger_at_pos(false);
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
    translate([0, -16, -22])
    rotate([90, 0, 0])
    color("OrangeRed") trigger_button();
}

// =============================================
//  SECTION 3: LEFT HALF
// =============================================
module housing_left_half() {
    difference() {
        union() {
            // 1. Shell left portion
            intersection() {
                full_shell();
                translate([-100, -50, -200])
                cube([100 + split_x, 300, 400]);
            }
            // 2. Head screw bosses (DEACTIVATED: SCREWLESS DESIGN PREP)
            // for (p = head_screw_pts) screw_boss_head(p[0], p[1], true);
            
            // 3. Handle screw bosses (DEACTIVATED: SCREWLESS DESIGN PREP)
            // translate([head_w/2, neck_y, wall])
            // rotate([handle_angle, 0, 0])
            // for (p = handle_screw_pts) screw_boss_handle(p[0], p[1], true);
            
            // 4. Alignment pins (male)
            alignment_features(true);
            // 5. Head internal mounts — CLIPPED to head volume
            intersection() {
                head_outer();
                union() {
                    gm77_pocket(true);
                    esp32_rail(true);
                    oled_guide(true);
                }
            }
            // 6. Handle internal mounts — CLIPPED to handle volume
            intersection() {
                handle_with_neck();
                translate([head_w/2, neck_y, wall])
                rotate([handle_angle, 0, 0])
                union() {
                    battery_cradle(true);
                    charger_pocket(true);
                    boost_pocket(true);
                    tact_pocket(true);
                }
            }
        }
        all_cuts();
        // Screw holes deactivated
        // for (p = head_screw_pts) screw_hole_head(p[0], p[1], true);
        // translate([head_w/2, neck_y, wall])
        // rotate([handle_angle, 0, 0])
        // for (p = handle_screw_pts) screw_hole_handle(p[0], p[1], true);
    }
}

// =============================================
//  SECTION 4: RIGHT HALF
// =============================================
module housing_right_half() {
    difference() {
        union() {
            // 1. Shell right portion
            intersection() {
                full_shell();
                translate([split_x, -50, -200])
                cube([100, 300, 400]);
            }
            // 2. Head screw bosses (DEACTIVATED)
            // for (p = head_screw_pts) screw_boss_head(p[0], p[1], false);
            
            // 3. Handle screw bosses (DEACTIVATED)
            // translate([head_w/2, neck_y, wall])
            // rotate([handle_angle, 0, 0])
            // for (p = handle_screw_pts) screw_boss_handle(p[0], p[1], false);
            
            // 4. Head internal mounts — CLIPPED
            intersection() {
                head_outer();
                union() {
                    gm77_pocket(false);
                    esp32_rail(false);
                    oled_guide(false);
                }
            }
            // 5. Handle internal mounts — CLIPPED
            intersection() {
                handle_with_neck();
                translate([head_w/2, neck_y, wall])
                rotate([handle_angle, 0, 0])
                union() {
                    battery_cradle(false);
                    charger_clamp();
                    boost_clamp();
                    tact_pocket(false);
                }
            }
        }
        all_cuts();
        // Screw holes deactivated
        // for (p = head_screw_pts) screw_hole_head(p[0], p[1], false);
        // translate([head_w/2, neck_y, wall])
        // rotate([handle_angle, 0, 0])
        // for (p = handle_screw_pts) screw_hole_handle(p[0], p[1], false);
        alignment_features(false);   // Female holes
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
    head_outer();
    handle_with_neck();
    neck_fill();
}

module shell_inner() {
    head_inner();
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    handle_inner();
    // Wire passage between head and handle
    translate([head_w/2, neck_y, 0])
    cylinder(h=30, d=24, center=true);
}

// --- Head outer: wedge (narrow front -> wide mid -> taper rear) ---
module head_outer() {
    hull() {
        hslice(5,          44, 38,  8, 2);   // front - narrow, raised 2mm
        hslice(35,         54, 48, 10, 0);   // front-mid
        hslice(70, head_w, head_h, 12, 0);   // mid - widest
        hslice(head_l - 5, 54, 46,  8, 0);   // rear
    }
}
module head_inner() {
    w2 = 2*wall;
    hull() {
        hslice(5+wall,       44-w2, 38-w2, max(1,8-wall),  2);
        hslice(35,           54-w2, 48-w2, max(1,10-wall), 0);
        hslice(70,     head_w-w2, head_h-w2, max(1,12-wall), 0);
        hslice(head_l-5-wall,54-w2, 46-w2, max(1,8-wall),  0);
    }
}
module hslice(y, w, h, r, zoff) {
    translate([head_w/2, y, h/2 + zoff])
    rotate([90,0,0])
    rounded_rect(w, h, 1.0, r, true);
}

// --- Handle outer (extends further into head for overlap) ---
module handle_with_neck() {
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    handle_outer();
}
module handle_outer() {
    hull() {
        hdisk( 20, 19);      // top (more overlap into head)
        hdisk(-15, 17);
        hdisk(-45, 16);
        hdisk(-75, 17);
        hdisk(-handle_h, 20);
    }
}
module handle_inner() {
    hull() {
        hdisk( 12, 19 - wall);
        hdisk(-15, 17 - wall);
        hdisk(-45, 16 - wall);
        hdisk(-75, 17 - wall);
        hdisk(-handle_h + wall, 20 - wall);
    }
}
module hdisk(z, r) {
    translate([0,0,z]) cylinder(h=0.1, r=r, center=true);
}

// --- Neck fill: smooth bridge from head bottom to handle top ---
module neck_fill() {
    hull() {
        // Head bottom near junction point
        translate([head_w/2, neck_y - 10, wall + 2])
        cube([40, 20, 0.1], center=true);
        
        translate([head_w/2, neck_y + 8, wall + 2])
        cube([38, 16, 0.1], center=true);

        // Handle top
        translate([head_w/2, neck_y, wall])
        rotate([handle_angle, 0, 0])
        translate([0, 0, 15])
        cylinder(h=0.1, r=19, center=true);
    }
    // Front chin fill
    hull() {
        translate([head_w/2, neck_y - 15, wall])
        cube([34, 6, 0.1], center=true);
        
        translate([head_w/2, neck_y, wall])
        rotate([handle_angle, 0, 0])
        translate([0, -14, 0])
        cylinder(h=0.1, r=14, center=true);
    }
}

// =============================================
//  SECTION 6: ALL CUTS (windows, ports, vents, holes)
// =============================================
module all_cuts() {
    // 1) GM77 scanner window - front face (Centered vertically Z=25.0)
    translate([head_w/2, 0, gm77_z])
    rotate([90,0,0])
    rounded_rect(gm77_size[0] + 6, gm77_size[2] - 2, 20.0, 2.0, true);

    // 2) Ergonomic OLED display window - rear face (Angled matching rotate([-55,0,0]))
    translate([head_w/2, oled_pcb_y + 4.0, oled_z - 4.57])
    rotate([-90 + oled_bevel_angle, 0, 0]) // Fixed window rotation match
    rounded_rect(25.5, 17.5, 20.0, 1.5, true);

    // 3) ESP32 USB slot - rear wall, low Z (pin-up orientation)
    translate([head_w/2 - 6.5, head_l - 10, 1.0])
    cube([13.0, 15.0, 9.0]);

    // 4) Ventilation slots - head sides
    for (i=[0:3])
        translate([-1, 45 + i*10, 20])
        rotate([0,90,0])
        cylinder(h=head_w+10, d=2.0, center=true);

    // 5) USB-C port - handle bottom (Aligned with TP4056 board)
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h]) {
        translate([0,0,2.5]) cube([10.0, 4.2, 8.0], center=true);
        translate([0,0,0.8]) cube([14.0, 8.0, 2.5], center=true);
    }

    // 6) Slide switch cutout - left side handle (Fits MSL-1C2P switch body)
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0]) {
        translate([-17.5, 0, -handle_h+16])
        cube([6.0, 11.5, 16.0], center=true);
        translate([-21.0, 0, -handle_h+16])
        cube([12.0, 4.0, 9.0], center=true);
    }

    // 7) Trigger button hole
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    translate([0, -16, -22])
    rotate([90,0,0])
    cylinder(h=wall*4, d=10.0, center=true);

    // 8) Ergonomic Rear Bevel Cut for Handheld Sightline
    translate([head_w/2, head_l - 2.5, oled_z + 8])
    rotate([-oled_bevel_angle, 0, 0])
    cube([head_w + 10, 28.0, 30.0], center=true);
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
    rail_h = 7.5;
    slot_h = 1.9;
    pcb_hw = esp32_size[0] / 2;  
    if (is_left) {
        translate([head_w/2 - pcb_hw - 2.5, esp32_y - rail_l/2, wall]) {
            difference() {
                cube([rail_w, rail_l, rail_h]);
                translate([2.5, 2.5, 2.9])
                cube([3.0, rail_l - 2.5, slot_h]);
            }
        }
    } else {
        translate([head_w/2 + pcb_hw - 2.5, esp32_y - rail_l/2, wall]) {
            difference() {
                cube([rail_w, rail_l, rail_h]);
                translate([-0.2, 2.5, 2.9])
                cube([3.0, rail_l - 2.5, slot_h]);
            }
        }
    }
}

// --- 7-C OLED Angled Bevel Guide (Ergonomic angle match) ---
module oled_guide(is_left) {
    pcb_hw = oled_size[0]/2;
    gw = 3.5; gh = 28.0; gd = 5.0;
    slot_t = 1.6;  
    
    translate([head_w/2, oled_pcb_y, oled_z])
    rotate([-oled_bevel_angle, 0, 0]) {
        if (is_left) {
            translate([-pcb_hw - clearance - gw, -gd/2, -gh/2])
            difference() {
                cube([gw, gd, gh]);
                translate([gw - slot_t - 0.3, -0.1, 1.5])
                cube([slot_t + 0.4, gd + 0.2, gh - 3.0]);
            }
        } else {
            translate([pcb_hw + clearance, -gd/2, -gh/2])
            difference() {
                cube([gw, gd, gh]);
                translate([-0.1, -0.1, 1.5])
                cube([slot_t + 0.4, gd + 0.2, gh - 3.0]);
            }
        }
    }
}

// --- 7-D Battery Cradle ---
module battery_cradle(is_left) {
    D = battery_diam + 0.4;
    if (is_left) {
        difference() {
            translate([0, 0, -45]) cylinder(h=50, d=D+4, center=true);
            translate([0, 0, -45]) cylinder(h=52, d=D, center=true);
            translate([D, 0, -45]) cube([D*2, D*2, 60], center=true);
        }
    } else {
        difference() {
            translate([0, 0, -45]) cylinder(h=12, d=D+4, center=true);
            translate([0, 0, -45]) cylinder(h=14, d=D, center=true);
            translate([-D, 0, -45]) cube([D*2, D*2, 20], center=true);
        }
    }
}

// --- 7-E TP4056 Charger Pocket ---
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

// --- 7-F Boost Pocket ---
module boost_pocket(is_left) {
    zb = -handle_h + 32.0;
    pw = stepup_size[0] + 2*clearance; 
    pt = stepup_size[2] + 0.2;         
    if (is_left) {
        translate([-pt/2 - 2.0, 0, zb + 11.0])
        difference() {
            cube([pt + 2.0, pw + 5.0, 22.0], center=true);
            translate([1.0, 0, 0])
            cube([pt + 0.2, pw, 23.0], center=true);
        }
    }
}
module boost_clamp() {
    zb = -handle_h + 32.0;
    pw = stepup_size[0] + 2*clearance;
    translate([0.6, 0, zb + 11.0])
    cube([1.5, pw - 3.0, 16.0], center=true);
}

// --- 7-G Tact Switch Pocket ---
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

// =============================================
//  SECTION 8: ASSEMBLY HARDWARE (INACTIVE IN RENDERING)
// =============================================

// Replaced with screwless assembly plan; modules kept for reference
module screw_boss_head(y, z, is_left) {
    br = 4.0; bl = 14.0;
    intersection() {
        if (is_left)
            translate([split_x - bl, y, z]) rotate([0,90,0]) cylinder(h=bl, r=br);
        else
            translate([split_x, y, z])       rotate([0,90,0]) cylinder(h=bl, r=br);
        head_outer();
    }
}
module screw_hole_head(y, z, is_left) {
    if (is_left) {
        translate([-1, y, z]) rotate([0,90,0]) cylinder(h=split_x+2, d=3.2);
        translate([-1, y, z]) rotate([0,90,0]) cylinder(h=split_x-5,  d=6.0);
    } else {
        translate([split_x-0.1, y, z]) rotate([0,90,0]) cylinder(h=10, d=2.5);
    }
}

module screw_boss_handle(ly, lz, is_left) {
    br = 4.0; bl = 14.0;
    intersection() {
        if (is_left)
            translate([-bl, ly, lz]) rotate([0,90,0]) cylinder(h=bl, r=br);
        else
            translate([0, ly, lz])   rotate([0,90,0]) cylinder(h=bl, r=br);
        handle_outer();
    }
}
module screw_hole_handle(ly, lz, is_left) {
    if (is_left) {
        translate([-15, ly, lz]) rotate([0,90,0]) cylinder(h=16, d=3.2);
        translate([-15, ly, lz]) rotate([0,90,0]) cylinder(h=9,  d=6.0);
    } else {
        translate([-0.1, ly, lz]) rotate([0,90,0]) cylinder(h=10, d=2.5);
    }
}

// Alignment pins kept for side-to-side interlocking
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
//  SECTION 9: TRIGGER BUTTON
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
//  SECTION 10: PRECISION COMPONENT MOCKUPS
// =============================================

module esp32_devkitc_mockup() {
    pcb_w = 28.2; pcb_l = 54.4; pcb_h = 1.6;
    color("DarkGreen") 
        difference() {
            cube([pcb_w, pcb_l, pcb_h], center=true);
            for (x = [-11.5, 11.5], y = [-24.0, 24.0]) {
                translate([x, y, 0]) cylinder(h=pcb_h*2, d=2.0, center=true);
            }
        }
    translate([0, 5.0, pcb_h/2 + 1.5]) {
        color("Silver") cube([18.0, 25.5, 3.0], center=true);
        translate([0, 12.75 + 3.0, -0.7]) 
            color([0.15, 0.15, 0.15]) cube([18.0, 6.0, 1.6], center=true);
    }
    translate([0, -pcb_l/2 + 2.5, pcb_h/2 + 1.5])
        color("LightGray") cube([7.5, 5.5, 3.0], center=true);
    translate([-7.0, -pcb_l/2 + 4.0, pcb_h/2 + 1.0]) {
        color("Silver") cube([3.5, 3.5, 2.0], center=true);
        color("Black") translate([0,0,1.0]) cylinder(h=1.0, d=1.8, center=true);
    }
    translate([7.0, -pcb_l/2 + 4.0, pcb_h/2 + 1.0]) {
        color("Silver") cube([3.5, 3.5, 2.0], center=true);
        color("Black") translate([0,0,1.0]) cylinder(h=1.0, d=1.8, center=true);
    }
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

module ssd1306_oled_mockup() {
    oled_w = 27.3; oled_l = 27.3; oled_h = 1.2;
    color("RoyalBlue")
        difference() {
            cube([oled_w, oled_l, oled_h], center=true);
            for (x = [-11.0, 11.0], y = [-11.0, 11.0]) {
                translate([x, y, 0]) cylinder(h=oled_h*3, d=2.0, center=true);
            }
        }
    translate([0, -2.0, oled_h/2 + 0.8]) {
        color([0.05, 0.05, 0.05]) cube([26.0, 16.0, 1.6], center=true);
        translate([0, 0, 0.81]) 
            color("Cyan") cube([21.8, 11.0, 0.01], center=true);
    }
    translate([0, oled_l/2 - 2.0, -oled_h/2 - 1.25]) {
        color("Black") cube([10.16, 2.54, 2.5], center=true);
        color("Gold") {
            for (x = [-3.81 : 2.54 : 3.81]) {
                translate([x, 0, -3.0]) cylinder(h=6.0, d=0.64, center=true);
            }
        }
    }
}

module gm77_scanner_mockup() {
    s_w = 27.5; s_l = 48.5; s_h = 14.0;
    color([0.25, 0.25, 0.27])
        difference() {
            cube([s_w, s_l, s_h], center=true);
            translate([-s_w/2, -s_l/2, 0]) rotate([0, 0, 45]) cube([6.0, 6.0, s_h + 1], center=true);
            translate([s_w/2, -s_l/2, 0]) rotate([0, 0, -45]) cube([6.0, 6.0, s_h + 1], center=true);
        }
    translate([0, -s_l/2 + 0.2, 0]) {
        color("Black") cube([20.0, 0.5, 8.0], center=true);
        translate([0, -0.1, 0]) 
            color("Cyan", 0.6) cube([14.0, 0.4, 6.0], center=true);
        translate([-8.0, -0.2, 3.0]) color("Green") sphere(r=0.6);
        translate([8.0, -0.2, 3.0]) color("Red") sphere(r=0.6);
    }
    translate([0, 0, -s_h/2 + 0.5]) {
        color("DarkGreen") cube([s_w - 2.0, s_l - 2.0, 1.0], center=true);
        color("Gold") {
            for (x = [-10.0, 10.0], y = [-20.0, 20.0]) {
                translate([x, y, -0.5]) cylinder(h=1.2, d=2.0, center=true);
            }
        }
    }
}

module booster_module_vlt_vc013() {
    b_w = 11.0; b_l = 22.0; b_h = 1.2;
    color([0.0, 0.4, 0.4]) cube([b_w, b_l, b_h], center=true);
    translate([0, -3.0, b_h/2 + 1.2])
        color("DimGray") cube([6.0, 6.0, 2.4], center=true);
    translate([0, 4.0, b_h/2 + 0.5])
        color("Black") cube([4.0, 3.0, 1.0], center=true);
    color("Gold") {
        translate([-b_w/2 + 1.5, -b_l/2 + 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([b_w/2 - 1.5, -b_l/2 + 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([-b_w/2 + 1.5, b_l/2 - 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([b_w/2 - 1.5, b_l/2 - 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
    }
}

module charger_module_tp4056() {
    c_w = 16.5; c_l = 27.5; c_h = 1.2;
    color([0.0, 0.1, 0.5]) cube([c_w, c_l, c_h], center=true);
    translate([0, -c_l/2 + 4.0, c_h/2 + 1.6])
        color("LightGray") cube([9.0, 6.5, 3.2], center=true);
    translate([-3.0, 3.0, c_h/2 + 0.5])
        color("Black") cube([4.0, 5.0, 1.0], center=true);
    translate([3.0, 3.0, c_h/2 + 0.5])
        color("Black") cube([3.0, 3.0, 1.0], center=true);
    color("Gold") {
        translate([-c_w/2 + 1.5, 9.0, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([c_w/2 - 1.5, 9.0, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([-c_w/2 + 1.5, c_l/2 - 1.5, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([c_w/2 - 1.5, c_l/2 - 1.5, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
    }
}

module slide_switch_msl_1c2p() {
    s_w = 3.5; s_l = 8.5; s_h = 3.5;
    color("Silver") cube([s_w, s_l, s_h], center=true);
    translate([0, 0, s_h/2 + 1.0])
        color("Red") cube([1.5, 2.5, 2.0], center=true);
    color("Silver") {
        translate([0, -2.5, -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
        translate([0, 0,    -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
        translate([0, 2.5,  -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
    }
}

module tact_switch_h11() {
    b_w = 6.0; b_l = 6.0; b_h = 3.5;
    color([0.15, 0.15, 0.15]) cube([b_w, b_l, b_h], center=true);
    translate([0,0,b_h/2 + 0.05])
        color("Silver") cube([b_w - 0.2, b_l - 0.2, 0.1], center=true);
    translate([0, 0, b_h/2 + 3.75])
        color("DimGray") cylinder(h=7.5, d=3.0, center=true);
    color("Silver") {
        for (x = [-2.8, 2.8], y = [-2.2, 2.2]) {
            translate([x, y, -b_h/2 - 1.0]) cylinder(h=2.0, d=0.6, center=true);
        }
    }
}

module battery_18650_wire() {
    bat_d = 18.4; bat_l = 65.2;
    color([0.2, 0.5, 0.9])
        rotate([90, 0, 0])
            cylinder(h=bat_l, d=bat_d, center=true);
    translate([0, bat_l/2 + 0.5, 0])
        rotate([90,0,0])
            color("Silver") cylinder(h=1.0, d=6.0, center=true);
    translate([0, bat_l/2 + 1.0, 3.0]) {
        color("Red") {
            rotate([0, 90, 0]) cylinder(h=5.0, d=1.2, center=true);
            translate([2.5, -3.0, 3.0]) rotate([45,0,0]) cylinder(h=10.0, d=1.2, center=true);
        }
    }
    translate([0, -bat_l/2 - 1.0, 3.0]) {
        color("Black") {
            rotate([0, 90, 0]) cylinder(h=5.0, d=1.2, center=true);
            translate([2.5, 3.0, 3.0]) rotate([-45,0,0]) cylinder(h=10.0, d=1.2, center=true);
        }
    }
}

// =============================================
//  SECTION 11: ELECTRONICS ASSEMBLY VIEWS
// =============================================

module head_electronics(exploded) {
    g_off = exploded ? [0, -25, 0] : [0, 0, 0];
    e_off = exploded ? [0, 0, 25]  : [0, 0, 0];
    o_off = exploded ? [0, 25, 0]  : [0, 0, 0];

    // GM77 Scanner
    translate([head_w/2, gm77_y, gm77_z] + g_off)
        gm77_scanner_mockup();

    // ESP32 DevKitC V4 (Flipped 180 deg, pin-headers facing up)
    translate([head_w/2, esp32_y, esp32_z] + e_off)
        rotate([180, 0, 0])
            esp32_devkitc_mockup();

    // SSD1306 OLED (Corrected rotation: rotate([-55, 0, 0]) so screen faces back window and pins face inside)
    translate([head_w/2, oled_pcb_y, oled_z] + o_off)
        rotate([-90 + oled_bevel_angle, 0, 0])
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
        // Battery
        translate([0, 0, -45] + bo) 
            rotate([-90, 0, 0])
                battery_18650_wire();
        
        // Charger Module TP4056 (Restored original rotation rotate([90, 0, 90]))
        translate([0, 0, -handle_h + 13.75] + tp) 
            rotate([90, 0, 90])
                charger_module_tp4056();
        
        // Boost Converter VLT-VC013
        translate([0, 0, -handle_h + 43.0] + su) 
            rotate([0, 90, 90])
                booster_module_vlt_vc013();
        
        // Slide Switch MSL-1C2P (Corrected to rotate([0, -90, 0]) to face knob outwards and pins inwards)
        translate([-17.5, 0, -handle_h + 16.0] + sw) 
            rotate([0, -90, 0])
                slide_switch_msl_1c2p();
        
        // Tact Trigger Switch
        translate([0, -14, -22.0] + ta) 
            rotate([90, 0, 0])
                tact_switch_h11();
    }
}

// =============================================
//  SECTION 12: HELPER MODULES
// =============================================
module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
        square([w - r*2, h - r*2], center=true);
    }
}
