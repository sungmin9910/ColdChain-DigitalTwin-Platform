/*
 * QR Scanner Housing V15.1 - Commercial Barcode Scanner Style (Fixed)
 *
 * Complete redesign from scratch. Inspired by Honeywell Voyager / Zebra DS2208.
 *
 * V15.1 Fixes:
 *   - All internal mount features clipped to shell outer (intersection)
 *     to prevent geometry protruding through rounded hull corners.
 *   - Added neck_fill() hull for smooth head-to-handle transition.
 *   - Handle top extends further into head (Z=20) for better blending.
 *   - Removed redundant handle_cavity_global from all_cuts.
 *
 * Key Design Features:
 *   - Wedge-shaped scanner head (narrow front, wide rear)
 *   - OLED display on REAR face (user-facing) for optimal visibility & printability
 *   - Smooth neck transition from head to grip
 *   - Screw bosses clipped to shell volume (never protrude outside)
 *   - Compact head length (130mm)
 *   - Left/Right vertical split at X = head_w/2 for support-free FDM printing
 *   - 3-Piece Assembly: Left Half, Right Half, Trigger Button
 *
 * Component Specs (identical to V14):
 *   GM77 Barcode Module:  27.5 x 48.5 x 14.0 mm
 *   ESP32 DevKitC V4:     28.2 x 54.4 x  1.6 mm (PCB)
 *   SSD1306 OLED:         27.3 x 27.3 x  3.0 mm
 *   18650 Battery:        dia 18.5 x 67.0 mm
 *   TP4056 Charger:       25.0 x 19.0 x  3.5 mm
 *   Boost Converter:      22.0 x 11.0 x  3.6 mm
 *   Tact Switch:           6.2 x  6.2 x  5.0 mm
 *   Slide Switch:          6.0 x 10.0 x 14.0 mm
 */

// =============================================
//  SECTION 1: GLOBAL PARAMETERS
// =============================================
$fn = 60;
wall   = 2.5;
clearance = 0.35;

// --- Head ---
head_w = 58.0;     // Width  (X)
head_l = 130.0;    // Length (Y)  front=0, back=130
head_h = 50.0;     // Height (Z)
split_x = head_w / 2;

// --- Handle ---
handle_h     = 105.0;
handle_angle = 20;
neck_y       = 75.0;   // Y where handle root starts

// --- Components (UNCHANGED from V14) ---
gm77_size    = [27.5, 48.5, 14.0];
esp32_size   = [28.2, 54.4, 1.6];
oled_size    = [27.3, 27.3, 3.0];
battery_diam = 18.5;
tp4056_size  = [25.0, 19.0, 3.5];
stepup_size  = [22.0, 11.0, 3.6];
tact_size    = [6.2, 6.2, 5.0];
switch_size  = [6.0, 10.0, 14.0];

// --- Component placement ---
gm77_y  = 30.0;
gm77_z  = wall + gm77_size[2]/2 + 0.5;
esp32_y = 85.0;
esp32_z = wall + 3.5;
oled_pcb_y = head_l - wall - 2.0;   // PCB near back wall
oled_z     = 30.0;                   // glass centre lands at ~25.4

// --- Assembly screw positions  [y, z] in head coords ---
head_screw_pts = [
    [22,  20],
    [head_l - 22, 20]
];
// Handle screw positions  [local_y, local_z]
handle_screw_pts = [
    [8, -30],
    [8, -78]
];
// Alignment pin positions [y, z] in head coords
align_pts = [
    [18, 10],
    [65, 8],
    [head_l - 18, 10]
];

// =============================================
//  SECTION 2: RENDER CONTROL
// =============================================
render_part = "exploded";
// Options: assembly, exploded, left_half, right_half, trigger, cross_section

if (render_part == "assembly") {
    color("DimGray",  0.6) housing_left_half();
    color("LightGray",0.6) housing_right_half();
    trigger_at_pos(false);
    head_electronics(false);
    handle_electronics(false);
}
if (render_part == "exploded") {
    color("DimGray")   translate([-35, 0, 0]) housing_left_half();
    color("LightGray") translate([ 35, 0, 0]) housing_right_half();
    trigger_at_pos(true);
    head_electronics(true);
    handle_electronics(true);
}
if (render_part == "left_half")  housing_left_half();
if (render_part == "right_half") housing_right_half();
if (render_part == "trigger")    trigger_button();
if (render_part == "cross_section") {
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
            // 2. Head screw bosses (self-clipping via intersection in module)
            for (p = head_screw_pts) screw_boss_head(p[0], p[1], true);
            // 3. Handle screw bosses (self-clipping)
            translate([head_w/2, neck_y, wall])
            rotate([handle_angle, 0, 0])
            for (p = handle_screw_pts) screw_boss_handle(p[0], p[1], true);
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
        for (p = head_screw_pts) screw_hole_head(p[0], p[1], true);
        translate([head_w/2, neck_y, wall])
        rotate([handle_angle, 0, 0])
        for (p = handle_screw_pts) screw_hole_handle(p[0], p[1], true);
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
            // 2. Head screw bosses
            for (p = head_screw_pts) screw_boss_head(p[0], p[1], false);
            // 3. Handle screw bosses
            translate([head_w/2, neck_y, wall])
            rotate([handle_angle, 0, 0])
            for (p = handle_screw_pts) screw_boss_handle(p[0], p[1], false);
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
        for (p = head_screw_pts) screw_hole_head(p[0], p[1], false);
        translate([head_w/2, neck_y, wall])
        rotate([handle_angle, 0, 0])
        for (p = handle_screw_pts) screw_hole_handle(p[0], p[1], false);
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
    // 1) GM77 scanner window - front face
    translate([head_w/2, 0, gm77_z])
    rotate([90,0,0])
    rounded_rect(gm77_size[0] + 6, gm77_size[2] - 2, 20.0, 2.0, true);

    // 2) OLED display window - rear face
    //    glass centre Z = oled_z - 4.57 = 25.43
    translate([head_w/2, head_l - 3, oled_z - 4.57])
    rotate([90,0,0])
    rounded_rect(25.5, 17.5, 12.0, 1.5, true);

    // 3) ESP32 USB slot - rear wall, low Z (pin-up orientation)
    translate([head_w/2 - 6.5, head_l - 10, 1.0])
    cube([13.0, 15.0, 9.0]);

    // 4) Ventilation slots - head sides
    for (i=[0:3])
        translate([-1, 45 + i*10, 20])
        rotate([0,90,0])
        cylinder(h=head_w+10, d=2.0, center=true);

    // 5) USB-C port - handle bottom
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0])
    translate([0, 0, -handle_h]) {
        translate([0,0,2.5]) cube([9.6, 3.8, 6.0], center=true);
        translate([0,0,0.8]) cube([13.5, 7.5, 2.5], center=true);
    }

    // 6) Slide switch cutout - left side handle
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
}

// =============================================
//  SECTION 7: INTERNAL MOUNTS
// =============================================

// --- 7-A  GM77 Pocket ---
module gm77_pocket(is_left) {
    pw  = gm77_size[0]/2 + clearance + 2.5;   // pocket half-width
    pl  = gm77_size[1] + 2*clearance + 3.0;
    ph  = gm77_size[2] + 1.5;
    translate([head_w/2, gm77_y, gm77_z]) {
        difference() {
            if (is_left)
                translate([-pw/2, 0, 0]) cube([pw, pl, ph], center=true);
            else
                translate([ pw/2, 0, 0]) cube([pw, pl, ph], center=true);
            // Inner cavity
            translate([0, 0, 1.0])
            cube([gm77_size[0]+2*clearance, gm77_size[1]+2*clearance, ph], center=true);
            // Lens opening
            cube([gm77_size[0]-4, gm77_size[1]-4, ph+4], center=true);
            // Wire exit
            translate([0, gm77_size[1]/2+clearance, 1.5])
            cube([14.0, 6.0, 12.0], center=true);
        }
    }
}

// --- 7-B  ESP32 Slide-in Rail ---
module esp32_rail(is_left) {
    rail_w = 5.0;
    rail_l = 55.0;
    rail_h = 7.5;
    slot_h = 1.9;
    pcb_hw = esp32_size[0] / 2;  // 14.1
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

// --- 7-C  OLED Guide (rear-face mount) ---
module oled_guide(is_left) {
    pcb_hw = oled_size[0]/2;
    gw = 3.5; gh = 28.0; gd = 5.0;
    slot_t = 1.6;  // PCB thickness + clearance
    if (is_left) {
        translate([head_w/2 - pcb_hw - clearance - gw,
                   oled_pcb_y - gd/2,
                   oled_z - gh/2]) {
            difference() {
                cube([gw, gd, gh]);
                translate([gw - slot_t - 0.3, -0.1, 1.5])
                cube([slot_t + 0.4, gd + 0.2, gh - 3.0]);
            }
        }
    } else {
        translate([head_w/2 + pcb_hw + clearance,
                   oled_pcb_y - gd/2,
                   oled_z - gh/2]) {
            difference() {
                cube([gw, gd, gh]);
                translate([-0.1, -0.1, 1.5])
                cube([slot_t + 0.4, gd + 0.2, gh - 3.0]);
            }
        }
    }
}

// --- 7-D  Battery Cradle ---
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

// --- 7-E  TP4056 Charger Pocket (left) & Clamp (right) ---
module charger_pocket(is_left) {
    zb = -handle_h + 3.0;
    pw = tp4056_size[1] + 2*clearance;
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
    zb = -handle_h + 3.0;
    pw = tp4056_size[1] + 2*clearance;
    translate([0.6, 0, zb + 12.5])
    cube([1.5, pw - 4.0, 20.0], center=true);
}

// --- 7-F  Boost Pocket (left) & Clamp (right) ---
module boost_pocket(is_left) {
    zb = -handle_h + 32.0;
    pw = stepup_size[1] + 2*clearance;
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
    pw = stepup_size[1] + 2*clearance;
    translate([0.6, 0, zb + 11.0])
    cube([1.5, pw - 3.0, 16.0], center=true);
}

// --- 7-G  Tact Switch Pocket ---
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
//  SECTION 8: ASSEMBLY HARDWARE
// =============================================

// --- Head screw bosses (clipped to head volume) ---
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

// --- Handle screw bosses (clipped to handle volume) ---
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

// --- Alignment pins ---
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
        // Finger-contact dome
        cylinder(h=1.5, d=9.8, center=true);
        translate([0,0,1.0]) sphere(d=9.8);
        // Piston body
        translate([0,0,-4.5]) cylinder(h=9.0, d=9.6, center=true);
        // Stop flange
        translate([0,0,-9.5]) cylinder(h=1.5, d=12.2, center=true);
        // Plunger stem
        translate([0,0,-13.5]) cylinder(h=6.0, d=4.0, center=true);
    }
}

// =============================================
//  SECTION 10: COMPONENT MOCKUPS
// =============================================
module gm77_mockup() {
    color("Green") cube(gm77_size, center=true);
    color("Black") translate([0,-gm77_size[1]/2-1.5,0])
        rotate([90,0,0]) cylinder(h=4, d=10, center=true);
}
module esp32_mockup() {
    color("Green") cube([esp32_size[0], esp32_size[1], 1.6], center=true);
    color("Silver") translate([0,2,3]) cube([15,22,3.5], center=true);
    color("Black") translate([0, esp32_size[1]/2-3, 2]) cube([8,8,4.5], center=true);
    color("Black") {
        translate([-12.7,0,4.5]) cube([1.2,48,8], center=true);
        translate([ 12.7,0,4.5]) cube([1.2,48,8], center=true);
    }
}
module oled_mockup() {
    color("Blue") cube([oled_size[0], oled_size[1], 1.2], center=true);
    color("DimGray")    translate([0, 4.57, 0.6+0.71])  cube([24.74,16.90,1.42], center=true);
    color("MidnightBlue") translate([0, 4.57, 0.6+1.42+0.05]) cube([21.74,10.86,0.1], center=true);
    color("Gold")  translate([0, oled_size[1]/2-1.5, -0.6-3]) cube([10,1.2,6], center=true);
    color("Black") translate([0, oled_size[1]/2-1.5, -0.6-12]) cube([12,2.5,12], center=true);
}
module battery_mockup() {
    color("LimeGreen") {
        cylinder(h=67, d=18.4, center=true);
        translate([0,0,33.5]) cylinder(h=1.5, d=9, center=true);
    }
}
module tp4056_mockup() {
    color("Green") cube([tp4056_size[2], tp4056_size[1], tp4056_size[0]], center=true);
    color("Silver") translate([0,0,-tp4056_size[0]/2-1.5]) cube([3.2,9,5], center=true);
}
module stepup_mockup() {
    color("DarkCyan") cube([stepup_size[2], stepup_size[1], stepup_size[0]], center=true);
    color("Blue") translate([stepup_size[2]/2+2,0,5]) cube([4,4,4], center=true);
}
module switch_mockup() {
    color("Gray")  cube([switch_size[0], switch_size[2], switch_size[1]], center=true);
    color("Black") translate([-switch_size[0]/2-2.5,0,0]) cube([5,2,3], center=true);
}
module tact_switch_mockup() {
    color("DarkSlateGray") cube([6,6,5], center=true);
    color("Red") translate([0,-6,0]) rotate([90,0,0]) cylinder(h=6, d=3.2, center=true);
}

// =============================================
//  SECTION 11: ELECTRONICS ASSEMBLY VIEWS
// =============================================
module head_electronics(exploded) {
    g_off = exploded ? 20 : 0;
    e_off = exploded ? 25 : 0;
    o_off = exploded ? 20 : 0;

    // GM77
    translate([head_w/2, gm77_y, gm77_z + g_off])
    gm77_mockup();

    // ESP32  (pin-up)
    translate([head_w/2, esp32_y, esp32_z + e_off])
    esp32_mockup();

    // OLED  (rear-face, display toward +Y / user)
    translate([head_w/2, oled_pcb_y + o_off, oled_z])
    rotate([90, 0, 0])
    oled_mockup();
}

module handle_electronics(exploded) {
    bo  = exploded ? [0,0,30]  : [0,0,0];
    tp  = exploded ? [0,0,-30] : [0,0,0];
    su  = exploded ? [0,25,0]  : [0,0,0];
    sw  = exploded ? [-25,0,0] : [0,0,0];
    ta  = exploded ? [0,-20,0] : [0,0,0];

    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0]) {
        translate([0,0,-45] + bo) battery_mockup();
        translate([0,0,-handle_h+15.5] + tp) tp4056_mockup();
        translate([0,0,-handle_h+43]   + su) stepup_mockup();
        translate([-17.5,0,-handle_h+16] + sw) switch_mockup();
        translate([0,-14,-22] + ta) tact_switch_mockup();
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
