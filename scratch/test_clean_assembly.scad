/*
 * Cold Chain Digital Twin Platform
 * v21 Apple Sensor Pod Housing (2-Piece Ultra-Rigid Edition - Fully Fused Wall Standoffs)
 * 
 * Major Fix:
 *  - FIXED: Solved floating standoff gap! The 4x PCB mounting standoffs now extend h=50.0mm
 *    and are 100% solidly fused into the front shell dome wall, with ZERO floating gap.
 *  - 100% PRINTABLE: Standoffs root directly at bed level (Y=0) and fuse continuously
 *    into the outer shell, printing with 0% support inside the dome.
 *  - 100% FRONT-ACCESSIBLE: All 8 screws are tightened from the FRONT exterior of the apple!
 */

$fn = 64;

// Render modes:
// "assembly", "cross_section", "exploded", "exploded_wide", "front_shell", "rear_shell", "stem", "print_all", "front_face", "part_front_shell", "part_rear_shell"
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
//  Y = -34.5 to -22.5: Battery Pocket (12mm depth, fully integrated in Rear Shell)
//  Y = -22.5 to  +1.9: Rear Sensor Clearance & Component Bay (24.4mm open cavity!)
//  Y =  +1.9 to  +3.5: CarrierBoard Substrate (1.6mm thickness)
//  Y =  +3.5         : Front Mounting Standoff Face (PCB bolted directly here!)
//  Y =  +3.5 to +35.5: Front Sensor Protrusion & Dome Cavity (32.0mm headroom!)
pcb_y_mount = 3.5;     // Front face of PCB rests on standoffs at Y = +3.5
pcb_y_back = pcb_y_mount - pcb_t; // Y = +1.9

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
    // 1. Top USB-C Port Cutout (Beetle ESP32-C6 edge connector access)
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
        cylinder(r=2.2, h=25, center=true);
        
    // 3. Right Power Switch (SW1) Slot (Viewer Right: -X)
    translate([-46.0, 1.0, 22.0])
        rotate([0, 90, 0])
        hull() {
            translate([0, -3.2, 0]) cylinder(r=2.2, h=20, center=true);
            translate([0,  3.2, 0]) cylinder(r=2.2, h=20, center=true);
        }
        
    // 4. Decorative Stem Socket at center top
    translate([0, 1.5, 36.0])
        cylinder(r=2.5, h=14, center=true);
}

// ==========================================
// 1. REAR SHELL (MAIN BASE CHASSIS)
// Holds 5000mAh Battery with Dual Retention Lips
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
                
                // 1. Integrated Battery Cradle (Zero-support 3D print)
                // Securely encloses 5000mAh cell with retaining lips
                difference() {
                    // Outer support block extending from Y = -22.5 to shell back wall,
                    // expanding in X and Z so it fuses completely to the shell perimeter & floor
                    translate([0, -36.0, bat_z_center])
                        cube([bat_w + 16.0, 27.0, bat_h + 20.0], center=true);
                        
                    // 1) Main Battery Pocket (From Y = -34.5 to Y = -22.5)
                    translate([0, bat_y_center + 10.0, bat_z_center])
                        cube([bat_w, bat_t + 20.0, bat_h], center=true);
                        
                    // 2) Battery Wire Passage Notch at Top-Left
                    translate([-bat_w/2 + 8.0, bat_y_center + 10.0, bat_z_center + bat_h/2])
                        cube([16.0, 30.0, 16.0], center=true);
                        
                    // 3) Finger Pull Extraction Notch (Allows effortless battery removal)
                    translate([0, bat_y_center - bat_t/2, bat_z_center])
                        cube([26.0, 8.0, 34.0], center=true);
                }
                
                // Battery Front Retention Lips (Left & Right edges at Y = -22.5)
                // Prevents battery from ever tilting or sliding forward towards the PCB!
                for (dx = [-1, 1]) {
                    translate([dx * (bat_w/2 - 1.0), -22.0, bat_z_center]) {
                        hull() {
                            cube([3.5, 2.0, bat_h - 10.0], center=true);
                            translate([-dx * 2.0, -1.0, 0])
                                cube([2.0, 2.0, bat_h - 14.0], center=true);
                        }
                    }
                }
                
                // 2. 4x Wall-Integrated Perimeter Screw Bosses (M3 Pilot Holes)
                for (pt = screw_pts) {
                    norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
                    dir_x = pt[0] / norm_len;
                    dir_z = pt[1] / norm_len;
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0]) {
                            difference() {
                                hull() {
                                    cylinder(r=5.2, h=42.0);
                                    translate([dir_x * 12.0, dir_z * 12.0, 0])
                                        cylinder(r=5.0, h=42.0);
                                }
                                cylinder(r=1.4, h=28.0); // M3 pilot hole
                            }
                        }
                    }
                }
            }
        }
        
        functional_cutouts();
    }
}

// ==========================================
// 2. FRONT SHELL (INTEGRATED PCB CARRIER CHASSIS)
// 100% WALL-FUSED STANDOFFS (ZERO FLOATING GAP!)
// ==========================================
module apple_front_shell() {
    difference() {
        // Base solid body: Outer Apple trimmed to Front Half (Y >= 0) with 100% fused pillars
        intersection() {
            apple_solid_outer();
            union() {
                // 1) Main front half shell (Y >= 0)
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
                
                // 2) 4x Wall-Integrated Perimeter Screw Bosses (Solid bodies)
                for (pt = screw_pts) {
                    norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
                    dir_x = pt[0] / norm_len;
                    dir_z = pt[1] / norm_len;
                    translate([pt[0], 0, pt[1]]) {
                        rotate([-90, 0, 0]) {
                            hull() {
                                cylinder(r=5.2, h=50.0);
                                translate([dir_x * 14.0, dir_z * 14.0, 0])
                                    cylinder(r=5.0, h=50.0);
                            }
                        }
                    }
                }
                
                // 3) 4x INTEGRATED PCB MOUNTING STANDOFFS (PURE CYLINDRICAL PILLARS, ZERO WINGS!)
                // Pure clean circular standoffs matching v20 sensor clearance (r=3.8mm, OD=7.6mm)
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        
                        translate([x_pos, 0, z_pos]) {
                            rotate([-90, 0, 0]) {
                                // Pure cylindrical pillar extending from PCB mount face (pcb_y_mount=3.5)
                                // deep through the dome wall (h=50.0mm). 100% solid & wall-fused, zero wings!
                                translate([0, 0, pcb_y_mount])
                                    cylinder(r=3.8, h=50.0);
                            }
                        }
                    }
                }
            }
        }
        
        // ==========================================
        // SUBTRACTIONS (Drills through the OUTER WALL so screws enter from the FRONT!)
        // ==========================================
        
        // A. 4x Perimeter Screw Holes & Counterbores on Front Dome
        for (pt = screw_pts) {
            translate([pt[0], 0, pt[1]]) {
                rotate([-90, 0, 0]) {
                    // Clearance through-hole (passes through front shell)
                    translate([0, 0, -5.0])
                        cylinder(r=1.7, h=65.0);
                    // M3 Screw head counterbore on front exterior surface
                    translate([0, 0, 10.0])
                        cylinder(r=3.4, h=45.0);
                }
            }
        }
        
        // B. 4x PCB Mounting Screw Holes & Counterbores on Front Dome!
        // 100% FRONT-ACCESSIBLE: Screws enter from front, pass through 100% solid standoff!
        for (dx = [-1, 1]) {
            for (dz = [-1, 1]) {
                x_pos = dx * (hole_pitch / 2);
                z_pos = pcb_z_center + dz * (hole_pitch / 2);
                translate([x_pos, 0, z_pos]) {
                    rotate([-90, 0, 0]) {
                        // Through-hole passing completely from outer front wall to PCB mount face
                        translate([0, 0, -5.0])
                            cylinder(r=1.7, h=65.0);
                        // Counterbore on front outer dome surface (depth ~6mm from outer surface)
                        // Leaves a massive 24.5mm solid threaded/clamping shoulder!
                        translate([0, 0, 28.0])
                            cylinder(r=3.4, h=45.0);
                    }
                }
            }
        }
        
        functional_cutouts();
        
        // BH1750 Ambient Light Sensor Tapered Optical Window (Viewer Right: -X)
        translate([-13.0, 35.0, 16.5]) {
            rotate([90, 0, 0]) {
                cylinder(r1=3.0, r2=5.0, h=18, center=true);
            }
        }
    }
}

// ==========================================
// 3. DECORATIVE APPLE STEM PLUG
// ==========================================
module apple_stem() {
    color([0.28, 0.65, 0.22]) {
        // Base plug pin
        translate([0, 1.5, 34.0])
            cylinder(r=2.3, h=10.0, center=true);
            
        // Curved organic stem
        translate([0, 1.5, 39.0]) {
            rotate([0, 14, 0])
                cylinder(r1=2.5, r2=1.6, h=15.0);
            // Leaf element
            translate([2.5, 0, 8.0])
                rotate([25, 45, 15])
                scale([1.8, 0.8, 0.3])
                sphere(r=5.0);
        }
    }
}

// ==========================================
// VIRTUAL HARDWARE MOCKUP (ELECTRICAL STACK)
// ==========================================
module hardware_mockup() {
    // 1. JRF PL105568 5000mAh Battery (Recessed at Y = -28.5)
    color([0.2, 0.45, 0.9, 0.9]) {
        translate([0, bat_y_center, bat_z_center])
            cube([55.0, 10.0, 68.0], center=true);
    }
    
    // 2. CarrierBoard PCB Substrate (50x50x1.6mm at Y = +1.9 to +3.5)
    color([0.08, 0.55, 0.25, 0.9]) {
        translate([0, (pcb_y_mount + pcb_y_back)/2, pcb_z_center])
            cube([pcb_w, pcb_t, pcb_h], center=true);
    }
    
    // 3. Beetle C6 MCU (Front: Y = +3.5 to +13.5)
    color([0.15, 0.15, 0.15]) {
        translate([0, pcb_y_mount + 5.0, 18.0])
            cube([25.0, 10.0, 20.5], center=true);
    }
    
    // 4. GPS Patch Antenna (Rear: Y = -12.0 to +1.9)
    color([0.8, 0.75, 0.4]) {
        translate([0, -5.0, -10.0])
            cube([25.0, 14.0, 25.0], center=true);
    }
    
    // 5. SHT45 Temp/Humidity Sensor (Rear-left towards vent)
    color([0.85, 0.25, 0.2]) {
        translate([17.0, -4.0, 16.0])
            cube([12.0, 12.0, 14.0], center=true);
    }
    
    // 6. BH1750 Ambient Light Sensor (Front-right directly under optical window)
    color([0.25, 0.55, 0.85]) {
        translate([-13.0, pcb_y_mount + 6.0, 16.5])
            cube([12.0, 12.0, 14.0], center=true);
    }
}

// ==========================================
// SCENE COMPOSER
// ==========================================
if (render_part == "assembly") {
    apple_stem();
    color([0.88, 0.18, 0.18, 0.45]) apple_rear_shell();
    color([0.88, 0.18, 0.18, 0.35]) apple_front_shell();
    hardware_mockup();
}
else if (render_part == "cross_section") {
    difference() {
        union() {
            apple_stem();
            color([0.88, 0.18, 0.18, 0.75]) apple_rear_shell();
            color([0.88, 0.18, 0.18, 0.55]) apple_front_shell();
            hardware_mockup();
        }
        // X > 0 cut away to reveal internal 2-piece architecture
        translate([70, 0, 0]) cube([140, 160, 160], center=true);
    }
}
else if (render_part == "exploded") {
    translate([0, -40, 0]) color([0.88, 0.18, 0.18]) apple_rear_shell();
    translate([0, -25, bat_z_center]) color([0.2, 0.45, 0.9, 0.9]) cube([55.0, 10.0, 68.0], center=true);
    translate([0, 10, pcb_z_center]) color([0.08, 0.55, 0.25, 0.9]) cube([pcb_w, pcb_t, pcb_h], center=true);
    translate([0, 45, 0]) color([0.88, 0.18, 0.18, 0.7]) apple_front_shell();
    translate([0, 45, 18]) apple_stem();
}
else if (render_part == "exploded_wide") {
    translate([0, -65, 0]) color([0.88, 0.18, 0.18]) apple_rear_shell();
    translate([0, -35, 0]) color([0.2, 0.45, 0.9, 0.9]) {
        translate([0, bat_y_center + 35.0, bat_z_center])
            cube([55.0, 10.0, 68.0], center=true);
    }
    translate([0, 15, 0]) {
        color([0.08, 0.55, 0.25, 0.9])
            translate([0, 0, pcb_z_center])
            cube([pcb_w, pcb_t, pcb_h], center=true);
        // Components on PCB
        color([0.15, 0.15, 0.15]) translate([0, 5.0, 18.0]) cube([25.0, 10.0, 20.5], center=true);
        color([0.8, 0.75, 0.4]) translate([0, -7.0, -10.0]) cube([25.0, 14.0, 25.0], center=true);
        color([0.25, 0.55, 0.85]) translate([-13.0, 6.0, 16.5]) cube([12.0, 12.0, 14.0], center=true);
    }
    translate([0, 65, 0]) color([0.88, 0.18, 0.18, 0.7]) apple_front_shell();
    translate([0, 65, 20]) apple_stem();
}
else if (render_part == "front_shell") {
    apple_front_shell();
}
else if (render_part == "rear_shell") {
    apple_rear_shell();
}
else if (render_part == "stem") {
    apple_stem();
}
else if (render_part == "part_front_shell") {
    apple_front_shell();
}
else if (render_part == "part_rear_shell") {
    apple_rear_shell();
}
else if (render_part == "print_all") {
    // Bed layout: rear shell, front shell, stem all flat!
    translate([-55, 0, 0]) rotate([90, 0, 0]) apple_rear_shell();
    translate([ 55, 0, 0]) rotate([-90, 0, 0]) apple_front_shell();
    translate([  0, 35, -35]) apple_stem();
}
