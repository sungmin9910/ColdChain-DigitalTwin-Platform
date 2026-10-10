/*
 * Cold Chain Digital Twin Platform
 * v20 Apple Sensor Pod Housing (Modular 3-Piece Edition)
 * 
 * Major Fix over v19:
 *  - FIXED: Solved battery bay blockage! The rear shell now features a 100% WIDE-OPEN
 *    Drop-in Battery Cradle (Zero-support 3D print).
 *  - INTRODUCED: Removable Battery Divider & PCB Standoff Tray (20_apple_battery_tray.stl)
 *    which safely isolates the 5000mAh battery from sharp PCB solder points while
 *    providing 18.0mm rigid M3 mounting pillars for the CarrierBoard.
 *  - ADVANTAGE: All electronics stay securely fastened inside the rear base even when
 *    the front dome lid is opened for testing, switch toggling, and firmware flashing!
 * 
 * Outer Geometry:
 *  - Diameter: Exactly 100.0mm (10cm)
 *  - Height: 91.87mm (~9.2cm)
 * 
 * Hardware Compatibility:
 *  - Board: CarrierBoard_BeetleC6_EdgeUSB_50x50 (50x50mm, 43x43mm M3 hole pitch)
 *  - Total PCB Assembly Thickness: 35.0mm+ accommodated (17.5mm rear / 18.0mm front)
 *  - Battery: JRF PL105568 3.7V 5000mAh LiPo Cell (10.0 x 55.0 x 68.0mm)
 */

$fn = 64;

// Render mode: "cross_section", "assembly", "exploded", "rear_shell", "battery_tray", "front_shell", "stem", "print_all"
render_part = "assembly"; 

wall_t = 3.0;          // Outer shell wall thickness (mm)
clearance = 0.25;      // 3D printing joint clearance (mm)

// PCB Specifications
pcb_w = 50.0;
pcb_h = 50.0;
pcb_t = 1.6;
hole_pitch = 43.0;     // M3 hole spacing (43mm x 43mm)
pcb_z_center = 3.0;    // Center of PCB in Z

// Stack Coordinates along Y-axis (front-to-back):
//  Y = -34.5 to -22.5: Battery Pocket (12mm depth, fully open to +Y)
//  Y = -22.5 to -20.5: Removable Divider Tray Base (2.0mm thickness)
//  Y = -20.5 to  -2.5: Rear Sensor Clearance & Standoffs (18.0mm height!)
//  Y =  -2.5 to  -0.9: PCB Substrate (1.6mm thickness)
//  Y =  -0.9 to +17.5: Front Sensor Protrusion (18.4mm front clearance in dome)
pcb_y_mount = -2.5;    // Back face of PCB sits on standoffs at Y = -2.5
divider_y_face = -20.5;// Front face of divider plate
standoff_h = pcb_y_mount - divider_y_face; // Exactly 18.0mm!

// JRF PL105568 5000mAh Battery Specifications
bat_w = 58.0;          // Pocket width (cell width 55mm + 3mm margin)
bat_h = 73.0;          // Pocket height (cell body 68mm + 5mm margin for tabs)
bat_t = 12.0;          // Pocket thickness (cell thickness 10mm + 2mm margin)
bat_y_center = -28.5;  // Center Y of battery pocket (from Y=-34.5 to Y=-22.5)
bat_z_center = 2.0;    // Center Z of battery

// Perimeter Assembly Screws (4 corners outside PCB & battery)
screw_pts = [
    [-35.0,  26.0],    // Top-left
    [ 35.0,  26.0],    // Top-right
    [-34.0, -23.0],    // Bottom-left
    [ 34.0, -23.0]     // Bottom-right
];

// Outer Apple Profile (R, Z) - Exact Outer Diameter 100.0mm (R_max = 50.0mm), Height 91.87mm
apple_outer_profile = [
  [  0.00, -37.32],
  [  1.15, -38.01],
  [  2.41, -38.70],
  [  3.79, -39.39],
  [  5.17, -40.08],
  [  6.66, -40.65],
  [  8.27, -41.34],
  [  9.88, -42.03],
  [ 11.60, -42.60],
  [ 13.44, -43.18],
  [ 15.39, -43.75],
  [ 17.46, -44.10],
  [ 19.52, -44.44],
  [ 21.70, -44.56],
  [ 24.00, -44.44],
  [ 26.18, -44.21],
  [ 28.36, -43.64],
  [ 30.55, -42.83],
  [ 32.61, -41.80],
  [ 34.68, -40.54],
  [ 36.63, -38.93],
  [ 38.47, -37.09],
  [ 40.31, -34.91],
  [ 41.92, -32.61],
  [ 43.52, -29.97],
  [ 44.90, -27.10],
  [ 46.16, -24.00],
  [ 47.20, -20.67],
  [ 48.12, -17.23],
  [ 48.81, -13.67],
  [ 49.38,  -9.99],
  [ 49.84,  -6.20],
  [ 49.95,  -2.41],
  [ 50.00,   1.38],
  [ 49.84,   5.05],
  [ 49.49,   8.73],
  [ 49.04,  12.29],
  [ 48.35,  15.73],
  [ 47.43,  18.95],
  [ 46.39,  22.16],
  [ 45.25,  25.15],
  [ 43.87,  28.02],
  [ 42.37,  30.78],
  [ 40.77,  33.42],
  [ 39.04,  35.83],
  [ 37.09,  38.13],
  [ 35.14,  40.31],
  [ 32.96,  42.26],
  [ 30.66,  43.98],
  [ 28.25,  45.48],
  [ 25.72,  46.51],
  [ 23.20,  47.20],
  [ 20.67,  47.31],
  [ 18.14,  46.85],
  [ 15.73,  46.05],
  [ 13.44,  44.79],
  [ 11.25,  43.41],
  [  9.19,  41.80],
  [  7.35,  40.31],
  [  5.63,  38.93],
  [  4.13,  37.90],
  [  2.76,  37.09],
  [  1.49,  36.52],
  [  0.00,  36.17]
];

// Inner Cavity Profile (R, Z) - Inner Diameter 93.24mm, Cavity Height 82.91mm
apple_inner_profile = [
  [  0.00, -33.30],
  [  1.15, -33.99],
  [  2.41, -34.68],
  [  3.79, -35.25],
  [  5.28, -35.94],
  [  6.89, -36.63],
  [  8.61, -37.32],
  [ 10.45, -38.01],
  [ 12.29, -38.59],
  [ 14.24, -39.16],
  [ 16.31, -39.62],
  [ 18.49, -39.96],
  [ 20.79, -40.19],
  [ 23.08, -40.31],
  [ 25.38, -40.08],
  [ 27.56, -39.62],
  [ 29.74, -38.93],
  [ 31.69, -38.01],
  [ 33.65, -36.86],
  [ 35.37, -35.48],
  [ 37.09, -33.76],
  [ 38.59, -31.92],
  [ 39.96, -29.86],
  [ 41.23, -27.56],
  [ 42.37, -25.03],
  [ 43.41, -22.39],
  [ 44.21, -19.52],
  [ 44.90, -16.54],
  [ 45.48, -13.44],
  [ 45.93, -10.22],
  [ 46.28,  -7.01],
  [ 46.51,  -3.67],
  [ 46.62,  -0.34],
  [ 46.58,   2.99],
  [ 46.28,   6.20],
  [ 45.93,   9.42],
  [ 45.36,  12.52],
  [ 44.56,  15.50],
  [ 43.64,  18.49],
  [ 42.60,  21.24],
  [ 41.34,  23.89],
  [ 39.96,  26.41],
  [ 38.36,  28.82],
  [ 36.63,  31.01],
  [ 34.91,  33.07],
  [ 32.96,  35.03],
  [ 30.89,  36.75],
  [ 28.71,  38.36],
  [ 26.53,  39.73],
  [ 24.23,  40.88],
  [ 21.82,  41.80],
  [ 19.41,  42.37],
  [ 17.00,  42.60],
  [ 15.85,  42.49],
  [ 12.52,  41.92],
  [ 10.34,  41.00],
  [  8.38,  39.85],
  [  6.55,  38.59],
  [  4.94,  37.32],
  [  3.56,  36.29],
  [  2.30,  35.48],
  [  1.15,  34.80],
  [  0.00,  34.22]
];

module apple_solid_outer() {
    rotate_extrude(angle=360, $fn=72) {
        polygon(concat([[0, apple_outer_profile[0][1]]], apple_outer_profile, [[0, apple_outer_profile[len(apple_outer_profile)-1][1]]]));
    }
}

module apple_solid_inner() {
    rotate_extrude(angle=360, $fn=72) {
        polygon(concat([[0, apple_inner_profile[0][1]]], apple_inner_profile, [[0, apple_inner_profile[len(apple_inner_profile)-1][1]]]));
    }
}

// Functional openings common to shells
module functional_cutouts() {
    // 1. Top USB-C Port Cutout
    translate([0, 1.5, 36.0]) {
        hull() {
            translate([-5.2, 0, 0]) cylinder(r=2.8, h=22, center=true);
            translate([ 5.2, 0, 0]) cylinder(r=2.8, h=22, center=true);
        }
        translate([0, 0, 9.0])
            cylinder(r1=8.0, r2=12.0, h=7.0, center=true);
    }
    
    // 2. Left Ventilation Hole for SHT45 (Viewer Left: +X)
    translate([48.0, -2.0, 16.0])
        rotate([0, 90, 0])
        cylinder(r=2.0, h=25, center=true);
        
    // 3. Right Power Switch (SW1) Slot (Viewer Right: -X)
    translate([-46.0, 1.0, 22.0])
        rotate([0, 90, 0])
        hull() {
            translate([0, -3.2, 0]) cylinder(r=2.2, h=20, center=true);
            translate([0,  3.2, 0]) cylinder(r=2.2, h=20, center=true);
        }
        
    // 4. Stem Socket at center top
    translate([0, 1.5, 36.0])
        cylinder(r=2.5, h=14, center=true);
}

// ==========================================
// 1. REAR SHELL (MAIN BASE CHASSIS)
// 100% Wide-Open Drop-In Battery Cradle
// ==========================================
module apple_rear_shell() {
    difference() {
        intersection() {
            apple_solid_outer();
            union() {
                // Main rear half shell (Y <= 0)
                difference() {
                    intersection() {
                        apple_solid_outer();
                        translate([0, -70, 0]) cube([140, 140, 140], center=true);
                    }
                    intersection() {
                        apple_solid_inner();
                        translate([0, -70, 0]) cube([140, 140, 140], center=true);
                    }
                }
                
                // 1. Open Battery Cradle Ribs (Recessed at Y = -28.5)
                // Completely OPEN to +Y so battery drops directly in!
                translate([0, bat_y_center, bat_z_center]) {
                    difference() {
                        // Outer cradle perimeter support box
                        cube([bat_w + 4.5, bat_t + 10.0, bat_h + 4.5], center=true);
                        // Battery pocket: cleared through to +Y face!
                        translate([0, 10.0, 0])
                            cube([bat_w, bat_t + 20.0, bat_h], center=true);
                        // Finger extraction notch at center rear
                        cube([24.0, 40.0, 30.0], center=true);
                        // Wire passage notch at top
                        translate([-bat_w/2 + 8.0, 10.0, bat_h/2])
                            cube([16.0, 30.0, 16.0], center=true);
                    }
                }
                
                // 2. 4x Perimeter Shell Assembly Screw Bosses
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0])
                        difference() {
                            cylinder(r=5.0, h=14.0);
                            cylinder(r=1.4, h=14.5);
                        }
                    }
                }
            }
        }
        
        functional_cutouts();
    }
}

// ==========================================
// 2. REMOVABLE BATTERY DIVIDER & PCB STANDOFF TRAY
// Drops over battery, provides 18mm M3 standoffs
// ==========================================
module apple_battery_tray() {
    union() {
        // Flat safety divider plate (rests on battery cradle rim at Y = -22.5 to -20.5)
        translate([0, -21.5, bat_z_center]) {
            difference() {
                cube([bat_w + 4.0, 2.0, bat_h + 4.0], center=true);
                // Battery wire channel at top-left
                translate([-bat_w/2 + 8.0, 0, bat_h/2 - 2.0])
                    cube([14.0, 4.0, 14.0], center=true);
                // Finger pull / inspection window at center
                cube([24.0, 4.0, 26.0], center=true);
            }
        }
        
        // 4x PCB Standoff Pillars (18.0mm Height from Y = -20.5 to Y = -2.5)
        for (dx = [-1, 1]) {
            for (dz = [-1, 1]) {
                x_pos = dx * (hole_pitch / 2);
                z_pos = pcb_z_center + dz * (hole_pitch / 2);
                translate([x_pos, divider_y_face, z_pos]) {
                    rotate([-90, 0, 0])
                    difference() {
                        cylinder(r=4.0, h=standoff_h);
                        translate([0, 0, standoff_h - 8.0])
                            cylinder(r=1.4, h=9.0); // M3 pilot hole
                    }
                }
            }
        }
    }
}

// ==========================================
// 3. FRONT SHELL (PROTECTIVE DOME COVER)
// Provides 18mm+ depth for front sensors
// ==========================================
module apple_front_shell() {
    difference() {
        intersection() {
            apple_solid_outer();
            union() {
                // Main front half shell (Y >= 0)
                difference() {
                    intersection() {
                        apple_solid_outer();
                        translate([0, 70, 0]) cube([140, 140, 140], center=true);
                    }
                    intersection() {
                        apple_solid_inner();
                        translate([0, 70, 0]) cube([140, 140, 140], center=true);
                    }
                }
                
                // 4x Perimeter Assembly Screw Bosses (Internal through-holes)
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([-90, 0, 0])
                        difference() {
                            cylinder(r=5.0, h=14.0);
                            translate([0, 0, -1])
                                cylinder(r=1.7, h=16.0);
                            translate([0, 0, 7.5])
                                cylinder(r=3.4, h=8.0);
                        }
                    }
                }
            }
        }
        
        functional_cutouts();
        
        // BH1750 Ambient Light Sensor Tapered Window (Viewer Right: -X)
        translate([-17.5, 41.0, 16.0])
            rotate([90, 0, 0])
            cylinder(r1=4.0, r2=2.2, h=20.0, center=true);
    }
}

// ==========================================
// 4. APPLE STEM ACCESSORY (꼭지 & 잎사귀)
// ==========================================
module apple_stem() {
    color([0.45, 0.28, 0.12]) { // Woody brown
        translate([0, 1.5, 35.0]) {
            cylinder(r=2.3, h=8.0, center=true);
            translate([0, 0, 4.0])
            rotate([0, 12, 10])
                cylinder(r1=2.5, r2=1.6, h=24.0);
        }
    }
    color([0.2, 0.65, 0.2]) { // Fresh green
        translate([2.0, 2.2, 49.0])
        rotate([35, -20, 45])
        scale([2.2, 1.0, 0.38])
            sphere(r=5.5);
    }
}

// ==========================================
// VIRTUAL HARDWARE MOCKUP
// ==========================================
module hardware_mockup() {
    // 1. JRF PL105568 5000mAh Battery (Recessed at Y = -28.5)
    color([0.2, 0.45, 0.9, 0.9]) {
        translate([0, bat_y_center, bat_z_center])
            cube([55.0, 10.0, 68.0], center=true);
    }
    
    // 2. CarrierBoard PCB Substrate (50x50x1.6mm at Y = -2.5 to -0.9)
    color([0.08, 0.55, 0.25, 0.9]) {
        translate([0, pcb_y_mount + pcb_t/2, pcb_z_center])
            cube([pcb_w, pcb_t, pcb_h], center=true);
    }
    
    // 3. Beetle C6 MCU (Front: Y = -0.9 to +12.0)
    color([0.15, 0.15, 0.15]) {
        translate([0, 5.0, 18.0])
            cube([25.0, 10.0, 20.5], center=true);
    }
    
    // 4. GPS Patch Antenna (Rear: Y = -17.0 to -2.5)
    color([0.8, 0.75, 0.4]) {
        translate([0, -10.0, -10.0])
            cube([25.0, 14.5, 25.0], center=true);
    }
    
    // 5. SHT45 Temp/Humidity Sensor (Rear-left towards vent)
    color([0.85, 0.25, 0.2]) {
        translate([17.0, -9.0, 16.0])
            cube([12.0, 12.0, 14.0], center=true);
    }
    
    // 6. BH1750 Ambient Light Sensor (Front-right towards window)
    color([0.25, 0.55, 0.85]) {
        translate([-17.5, 8.0, 16.0])
            cube([12.0, 12.0, 14.0], center=true);
    }
}

// ==========================================
// SCENE COMPOSER
// ==========================================
// ==========================================
// SCENE COMPOSER & ADVANCED VIEWS
// ==========================================

module pcb_assembly_mockup() {
    // CarrierBoard Substrate (Green)
    color([0.08, 0.55, 0.25, 0.95])
        cube([pcb_w, pcb_t, pcb_h], center=true);
        
    // Beetle C6 MCU (Front Face: +Y)
    color([0.15, 0.15, 0.15])
        translate([0, 5.0, 18.0 - pcb_z_center])
        cube([25.0, 10.0, 20.5], center=true);
        
    // BH1750 Light Sensor (Front-Right: +Y, -X)
    color([0.25, 0.55, 0.85])
        translate([-17.5, 7.5, 16.0 - pcb_z_center])
        cube([12.0, 12.0, 14.0], center=true);

    // GPS Patch Antenna (Rear Face: -Y)
    color([0.8, 0.75, 0.4])
        translate([0, -8.0, -10.0 - pcb_z_center])
        cube([25.0, 14.5, 25.0], center=true);

    // SHT45 Temp/Humidity Sensor (Rear-Left: -Y, +X)
    color([0.85, 0.25, 0.2])
        translate([17.0, -7.5, 16.0 - pcb_z_center])
        cube([12.0, 12.0, 14.0], center=true);
        
    // Corner M3 Mounting Holes Visualizer
    for (dx = [-1, 1]) {
        for (dz = [-1, 1]) {
            translate([dx * hole_pitch/2, 0, dz * hole_pitch/2])
                color([0.8, 0.8, 0.8])
                rotate([90, 0, 0])
                cylinder(r=1.6, h=pcb_t + 0.2, center=true);
        }
    }
}

if (render_part == "assembly") {
    apple_stem();
    color([0.88, 0.18, 0.18, 0.4]) apple_rear_shell();
    color([0.25, 0.72, 0.88, 0.7]) apple_battery_tray();
    color([0.88, 0.18, 0.18, 0.3]) apple_front_shell();
    hardware_mockup();
}
else if (render_part == "cross_section") {
    difference() {
        union() {
            apple_stem();
            color([0.88, 0.18, 0.18, 0.75]) apple_rear_shell();
            color([0.25, 0.72, 0.88, 0.9]) apple_battery_tray();
            color([0.88, 0.18, 0.18, 0.5]) apple_front_shell();
            hardware_mockup();
        }
        translate([70, 0, 0]) cube([140, 160, 160], center=true);
    }
}
// 1. WIDE EXPLODED VIEW (Ultra Clear Spacing along Y-axis)
else if (render_part == "exploded" || render_part == "exploded_wide") {
    // Alignment Guide Axis Lines
    for (pt = screw_pts) {
        translate([pt[0], 0, pt[1]])
            rotate([90, 0, 0])
            color([0.6, 0.7, 0.9, 0.35])
            cylinder(r=0.75, h=340, center=true);
    }
    
    // Layer 1: Rear Shell (Base Chassis)
    translate([0, -130, 0])
        color([0.88, 0.18, 0.18, 0.9])
        apple_rear_shell();
        
    // Layer 2: 5000mAh Battery Pouch
    translate([0, -65, bat_z_center])
        color([0.2, 0.45, 0.9, 0.95])
        cube([55.0, 10.0, 68.0], center=true);
        
    // Layer 3: Removable Battery Divider & PCB Standoff Tray
    translate([0, 0, 0])
        color([0.25, 0.75, 0.9, 0.95])
        apple_battery_tray();
        
    // Layer 4: CarrierBoard PCB Assembly with all 5 sensors
    translate([0, 65, pcb_z_center])
        pcb_assembly_mockup();
        
    // Layer 5: Front Shell Dome
    translate([0, 140, 0])
        color([0.88, 0.18, 0.18, 0.75])
        apple_front_shell();
        
    // Layer 6: Stem
    translate([0, 140, 24])
        apple_stem();
}
// 2. 2x3 GRID CATALOG LAYOUT (Inspection Workbench)
else if (render_part == "layout_catalog") {
    // Row 1 (Top: Z = +55)
    // Part 1: Rear Shell (Angled to see open battery bay)
    translate([-85, 0, 55])
        rotate([25, 45, -20])
        color([0.88, 0.18, 0.18])
        apple_rear_shell();
        
    // Part 2: 5000mAh Battery Pouch
    translate([0, 0, 55])
        rotate([0, 0, 0])
        color([0.2, 0.45, 0.9])
        cube([55.0, 10.0, 68.0], center=true);
        
    // Part 3: Removable Battery Divider Tray
    translate([85, 0, 55])
        rotate([25, 30, -10])
        color([0.25, 0.75, 0.9])
        apple_battery_tray();

    // Row 2 (Bottom: Z = -55)
    // Part 4: PCB Assembly with sensors
    translate([-85, 0, -55])
        rotate([15, 35, 0])
        pcb_assembly_mockup();
        
    // Part 5: Front Shell Dome
    translate([0, 0, -55])
        rotate([25, -45, 20])
        color([0.88, 0.18, 0.18, 0.85])
        apple_front_shell();
        
    // Part 6: Stem Accessory
    translate([85, 0, -55])
        scale([1.4, 1.4, 1.4])
        apple_stem();
}
// Individual Parts
else if (render_part == "part_rear_shell") {
    rotate([25, 40, -15])
    color([0.88, 0.18, 0.18])
    apple_rear_shell();
}
else if (render_part == "part_battery") {
    color([0.2, 0.45, 0.9])
    cube([55.0, 10.0, 68.0], center=true);
}
else if (render_part == "part_battery_tray") {
    rotate([25, 35, -15])
    color([0.25, 0.75, 0.9])
    apple_battery_tray();
}
else if (render_part == "part_pcb") {
    rotate([15, 35, 0])
    pcb_assembly_mockup();
}
else if (render_part == "part_front_shell") {
    rotate([25, -40, 15])
    color([0.88, 0.18, 0.18, 0.85])
    apple_front_shell();
}
else if (render_part == "rear_shell") {
    apple_rear_shell();
}
else if (render_part == "battery_tray") {
    rotate([90, 0, 0])
    translate([0, 21.5, -bat_z_center])
        apple_battery_tray();
}
else if (render_part == "front_shell") {
    apple_front_shell();
}
else if (render_part == "stem") {
    apple_stem();
}
else if (render_part == "print_all") {
    translate([-60, 0, 0]) rotate([90, 0, 0]) apple_rear_shell();
    translate([ 60, 0, 0]) rotate([-90, 0, 0]) apple_front_shell();
    translate([  0, 0, 0]) rotate([90, 0, 0]) translate([0, 21.5, -bat_z_center]) apple_battery_tray();
    translate([  0, 45, -35]) apple_stem();
}
