/*
 * Cold Chain Digital Twin Platform
 * v22 Apple Sensor Pod Housing (Magnetic Snap + GPS Antenna Holder + Method 1-A Light Window)
 * 100% SUPPORT-FREE EDITION FOR SINDOH 3DWOX 2X (PLA Single-Nozzle, Support = NONE)
 * 
 * Major Upgrades in v22:
 *  1. PRE-ORIENTED & SELF-SUPPORTING FOR SINDOH 3DWOX 2X (0% Support Needed!):
 *     - Both 22_apple_front_shell.stl and 22_apple_rear_shell.stl are pre-oriented BOWL-UP
 *       with z_min = 0.0mm centered on the build plate (no manual rotation needed in 3DWOX Desktop!).
 *     - Added a D=48mm flat bed-adhesion base pad at the dome pole (|Y|=48.8mm) with a 48-deg
 *       self-supporting lower dome chamfer, eliminating the steep 85-deg lower sphere overhang!
 *     - All internal features (flat Velcro battery floor, 33-deg retention lips, 32-deg GPS holder base,
 *       PCB standoffs, Red-Arrow ribs, and 8 magnet sockets) grow upward with ZERO overhangs!
 *  2. MAGNETIC SNAP + STEEL-DOWEL ALIGNMENT LOCK (Option A - 8x D6x3mm Neodymium Magnets):
 *     - Rear shell bosses have 1.80mm deep magnet pockets (1.20mm of magnet protrudes as a steel dowel pin).
 *     - Front shell bosses have 4.30mm deep magnet pockets (3.0mm magnet + 1.30mm recessed socket).
 *  3. INTEGRATED GPS ANTENNA HOLDER (20 x 5 x 7 mm Ceramic Patch Antenna):
 *     - Dedicated slide-in pocket built into the -X inner wall of the Front Shell (X=-36.5mm, Z=+1mm),
 *       with a gradual 32-deg self-supporting base ramp for Bowl-Up supportless printing.
 *  4. METHOD 1-A BH1750 OPTICAL WINDOW & FLAT VELCRO BATTERY FLOOR:
 *     - Rear shell battery floor is 100% flat (no center notch) for maximum Velcro tape adhesion.
 *     - Flared optical window placed on the Rear Shell wall aligned with BH1750.
 */

$fn = 64;

// Render modes:
// "assembly", "cross_section", "exploded", "front_shell", "rear_shell", "stem", "print_all", "front_face", "part_front_shell", "part_rear_shell"
render_part = "assembly"; 

wall_t = 3.0;          // Outer shell wall thickness (mm)
clearance = 0.25;      // 3D printing joint clearance (mm)
bed_flat_y = 48.0;     // Flat base plane on exterior dome pole (leaves 3.0mm solid floor & D=28mm flat bed pad)

// PCB Specifications
pcb_w = 50.0;
pcb_h = 50.0;
pcb_t = 1.6;
hole_pitch = 43.0;     // M3 hole spacing (43mm x 43mm)
pcb_z_center = 3.0;    // Center of PCB in Z

// Stack Coordinates along Y-axis (front-to-back):
pcb_y_mount = 3.5;     // Front face of PCB rests on standoffs at Y = +3.5
pcb_y_back = pcb_y_mount - pcb_t; // Y = +1.9

// JRF PL105568 5000mAh Battery Specifications
bat_w = 58.0;          // Pocket width (cell width 55mm + 3mm margin)
bat_h = 73.0;          // Pocket height (cell body 68mm + 5mm margin for tabs)
bat_t = 12.0;          // Pocket thickness (cell thickness 10mm + 2mm margin)
bat_y_center = -28.5;  // Center Y of battery pocket (from Y=-34.5 to Y=-22.5)
bat_z_center = 2.0;    // Center Z of battery

// 4x Magnetic Bosses (D6x3mm Neodymium Magnets)
screw_pts = [
    [-35.0,  26.0],    // Top-left (in SCAD Z-up) / Top-Right in user photo
    [ 35.0,  26.0],    // Top-right (in SCAD Z-up) / Bottom-Right in user photo
    [-34.0, -23.0],    // Bottom-left (in SCAD Z-up) / Top-Left in user photo
    [ 34.0, -23.0]     // Bottom-right (in SCAD Z-up) / Bottom-Left in user photo
];

// Magnet Specifications (D6 x 3mm cylinder)
mag_r_front = 3.16;    // D=6.32mm pocket in Front Shell (receives magnet + rear protruding magnet)
mag_h_front = 4.30;    // 3.0mm magnet + 1.3mm recessed alignment socket
mag_r_rear  = 3.12;    // D=6.24mm press-fit pocket in Rear Shell
mag_h_rear  = 1.80;    // 1.8mm recessed -> 1.2mm of magnet protrudes as steel alignment pin!

// GPS Ceramic Antenna Specifications (20 x 5 x 7 mm)
gps_len_z = 21.6;      // 20.0mm antenna length + 1.6mm clearance
gps_wid_x = 7.6;       // Fits up to 7.0mm thickness/width + solder bump
gps_dep_y = 11.0;      // Pocket depth along Y (from Y=0 rim to Y=11.0mm)
gps_wall  = 2.4;       // Pocket wall thickness
gps_x_center = -36.5;  // Mounted in the open -X bay (top of user photo)
gps_z_center = 1.0;    // Centered between Z=-10 and Z=+12

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

// Outer solid with clean flat bed-adhesion pad at |Y| = bed_flat_y (48.0mm, D=28mm flat base)
module apple_solid_outer() {
    intersection() {
        rotate_extrude(angle=360, $fn=72) {
            polygon(concat([[0, apple_outer_profile[0][1]]], apple_outer_profile, [[0, apple_outer_profile[len(apple_outer_profile)-1][1]]]));
        }
        // Flatten extreme poles at |Y| = 48.0mm so both shells sit on a stable D=28mm flat circle at Z=0!
        cube([140, 2 * bed_flat_y, 140], center=true);
    }
}

module apple_solid_inner() {
    intersection() {
        rotate_extrude(angle=360, $fn=72) {
            polygon(concat([[0, apple_inner_profile[0][1]]], apple_inner_profile, [[0, apple_inner_profile[len(apple_inner_profile)-1][1]]]));
        }
        // Ensure a solid 3.0mm flat floor at both poles (|Y| <= 45.0mm)
        cube([140, 2 * (bed_flat_y - 3.0), 140], center=true);
    }
}

// Functional openings common to shells
module functional_cutouts() {
    // 1. Decorative Stem Socket at center top (Clean socket without gaping hole)
    translate([0, 1.5, 36.0])
        cylinder(r=2.5, h=14, center=true);
    
    // 2. Side Ventilation Hole for SHT45 (+X side)
    translate([48.0, -2.0, 16.0])
        rotate([0, 90, 0])
        cylinder(r=2.2, h=25, center=true);
}

// ==========================================
// 1. REAR SHELL (MAIN BASE CHASSIS - PURPLE IN PHOTO)
// - 100% Flat Velcro Battery Floor (center notch removed)
// - Self-supporting 33-deg Battery Retention Lips (0% overhang in Bowl-Up printing)
// - 4x D6x3mm Magnet Bosses (1.8mm deep -> 1.2mm steel dowel protrusion)
// - Method 1-A BH1750 Optical Window
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
                
                // 1. Integrated Battery Cradle (100% Flat Velcro Floor, Zero-support 3D print)
                difference() {
                    translate([0, -36.0, bat_z_center])
                        cube([bat_w + 16.0, 27.0, bat_h + 20.0], center=true);
                        
                    // 1) Main Battery Pocket (From Y = -34.5 to Y = -22.5, completely flat floor!)
                    translate([0, bat_y_center + 10.0, bat_z_center])
                        cube([bat_w, bat_t + 20.0, bat_h], center=true);
                        
                    // 2) Battery Wire Passage Notch at Top-Left
                    translate([-bat_w/2 + 8.0, bat_y_center + 10.0, bat_z_center + bat_h/2])
                        cube([16.0, 30.0, 16.0], center=true);
                }
                
                // Self-Supporting Battery Front Retention Lips (33-deg gradual slope in Bowl-Up print!)
                for (dx = [-1, 1]) {
                    translate([dx * (bat_w/2 - 1.0), -22.0, bat_z_center]) {
                        hull() {
                            cube([3.5, 2.0, bat_h - 10.0], center=true);
                            translate([-dx * 2.0, -3.5, 0])
                                cube([1.5, 1.0, bat_h - 14.0], center=true);
                        }
                    }
                }
                
                // 2. 4x Wall-Integrated Magnetic Bosses (Enlarged r=6.2mm for D6x3mm Magnets)
                for (pt = screw_pts) {
                    norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
                    dir_x = pt[0] / norm_len;
                    dir_z = pt[1] / norm_len;
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0]) {
                            hull() {
                                cylinder(r=6.2, h=42.0);
                                translate([dir_x * 12.0, dir_z * 12.0, 0])
                                    cylinder(r=5.5, h=42.0);
                            }
                        }
                    }
                }
            }
        }
        
        // A. 4x Rear Magnet Pockets (D=6.24mm, depth=1.80mm -> 1.2mm of magnet protrudes as alignment pin!)
        // In Bowl-Up orientation, the pocket floor faces UP (100% supported by solid boss below!)
        for (pt = screw_pts) {
            translate([pt[0], 0, pt[1]]) {
                rotate([90, 0, 0]) {
                    // Main D6x3mm magnet recess (depth 1.80mm from Y=0)
                    translate([0, 0, -0.1])
                        cylinder(r=mag_r_rear, h=mag_h_rear + 0.1);
                    // Shallow central glue reservoir dimple
                    translate([0, 0, mag_h_rear - 0.05])
                        cylinder(r1=1.6, r2=0.8, h=1.2);
                }
            }
        }
        
        // B. METHOD 1-A BH1750 OPTICAL WINDOW (Aligned with BH1750 at Bottom-Left of user photo)
        hull() {
            translate([16.0, -8.5, -14.5])
                sphere(r=3.8);
            translate([48.0, -11.0, -11.0])
                sphere(r=4.8);
        }
        
        functional_cutouts();
    }
}

// ==========================================
// 2. FRONT SHELL (INTEGRATED PCB CARRIER CHASSIS - YELLOW IN PHOTO)
// - 4x Red-Arrow Standoffs with Blind M3 Holes (Zero holes on front dome!)
// - 4x D6x3mm Recessed Magnet Pockets (depth=4.3mm)
// - Integrated 20x5x7mm GPS Ceramic Antenna Pocket with 32-deg Self-Supporting Base Ramp
// ==========================================
module apple_front_shell() {
    difference() {
        // Base solid body: Outer Apple trimmed to Front Half (Y >= 0) with 100% fused structures
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
                
                // 2) 4x Wall-Integrated Magnetic Bosses (Enlarged r=6.2mm for D6x3mm Magnets)
                for (pt = screw_pts) {
                    norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
                    dir_x = pt[0] / norm_len;
                    dir_z = pt[1] / norm_len;
                    translate([pt[0], 0, pt[1]]) {
                        rotate([-90, 0, 0]) {
                            hull() {
                                cylinder(r=6.2, h=50.0);
                                translate([dir_x * 14.0, dir_z * 14.0, 0])
                                    cylinder(r=5.5, h=50.0);
                            }
                        }
                    }
                }
                
                // 3) 4x MONOLITHIC RED-ARROW WALL-ANCHORED STANDOFFS (100% ZERO SENSOR INTERFERENCE)
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        
                        rib_len_z = (dz > 0) ? 16.5 : 20.0;
                        rib_x = dx * 3.5;
                        rib_y = -dz * rib_len_z;
                        
                        translate([x_pos, 0, z_pos]) {
                            rotate([-90, 0, 0]) {
                                // A. Main Boss Cylinder (r=4.0mm, h=46.0mm, solid anchor into shell)
                                translate([0, 0, pcb_y_mount])
                                    cylinder(r=4.0, h=46.0);
                                    
                                // B. Direct Wall-Anchor Rib along Red Arrows
                                translate([0, 0, pcb_y_mount + 1.5]) {
                                    hull() {
                                        cylinder(r=4.0, h=44.5);
                                        translate([rib_x, rib_y, 0])
                                            cylinder(r=4.2, h=44.5);
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 4) INTEGRATED GPS CERAMIC ANTENNA HOLDER (For 20 x 5 x 7 mm Antenna)
                // Engineered with a 32-deg gradual base ramp (from Y=26mm up to Y=11mm) so in Bowl-Up
                // printing it grows smoothly out of the side wall with 0% support!
                difference() {
                    // Outer solid body fused into -X shell wall with 32-deg self-supporting base ramp
                    hull() {
                        translate([-40.5, 5.5, gps_z_center])
                            cube([19.0, 11.0, gps_len_z + 2*gps_wall], center=true);
                        translate([-45.5, 25.0, gps_z_center])
                            cube([9.0, 1.0, gps_len_z + 2*gps_wall - 4.0], center=true);
                    }
                        
                    // Inner Antenna Pocket Cavity (21.6mm long in Z x 5.8mm wide in X x 9.5mm deep in Y)
                    // Flat upward-facing floor at Y=9.5mm when printed Bowl-Up!
                    translate([gps_x_center, 4.75 - 0.1, gps_z_center])
                        cube([5.8, 9.6, gps_len_z], center=true);
                        
                    // Central Wider Relief Channel (7.8mm wide in X) for rear solder bump or 7mm orientation
                    translate([gps_x_center, 4.75 - 0.1, gps_z_center])
                        cube([7.8, 9.6, gps_len_z - 5.0], center=true);
                        
                    // Lead-in Entry Chamfer at Y=0 mouth for effortless thumb insertion
                    translate([gps_x_center, 0.7, gps_z_center])
                        cube([8.2, 1.6, gps_len_z + 0.8], center=true);
                        
                    // Coaxial Pigtail Cable Exit Slot on +Z side (facing right side of PCB where GPS wire exits)
                    translate([gps_x_center, 4.5, gps_z_center + gps_len_z/2])
                        cube([4.4, 9.2, 8.0], center=true);
                }
            }
        }
        
        // ==========================================
        // SUBTRACTIONS (ZERO HOLES ON FRONT APPLE EXTERIOR!)
        // ==========================================
        
        // A. 4x Front Recessed Magnet Sockets (D=6.32mm, depth=4.30mm from Y=0)
        // In Bowl-Up orientation, the socket floor at Y=4.30mm faces UP (100% supported from below!)
        for (pt = screw_pts) {
            translate([pt[0], 0, pt[1]]) {
                rotate([-90, 0, 0]) {
                    // Self-centering entrance chamfer at Y=0
                    translate([0, 0, -0.1])
                        cylinder(r1=mag_r_front + 0.45, r2=mag_r_front, h=0.9);
                    // Main magnet + dowel socket (depth 4.30mm)
                    translate([0, 0, -0.1])
                        cylinder(r=mag_r_front, h=mag_h_front + 0.1);
                    // Shallow central glue reservoir dimple
                    translate([0, 0, mag_h_front - 0.05])
                        cylinder(r1=1.6, r2=0.8, h=1.2);
                }
            }
        }
        
        // B. 4x PCB Mounting Pilot BLIND Holes (Depth = 20.0mm from PCB mount face, NEVER pierces front skin!)
        for (dx = [-1, 1]) {
            for (dz = [-1, 1]) {
                x_pos = dx * (hole_pitch / 2);
                z_pos = pcb_z_center + dz * (hole_pitch / 2);
                translate([x_pos, 0, z_pos]) {
                    rotate([-90, 0, 0]) {
                        translate([0, 0, pcb_y_mount - 0.5])
                            cylinder(r=1.45, h=20.5);
                    }
                }
            }
        }
        
        functional_cutouts();
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
// VIRTUAL HARDWARE MOCKUP (MATCHING USER PHOTO ORIENTATION)
// ==========================================
module hardware_mockup() {
    // 1. JRF PL105568 5000mAh Battery (Seated inside Rear Shell Cradle)
    color([0.2, 0.45, 0.9]) {
        translate([0, -25.0, bat_z_center])
            cube([54.0, 9.5, 65.0], center=true);
    }
    
    // 2. CarrierBoard PCB Substrate (50x50x1.6mm at Y = +1.9 to +3.5)
    color([0.08, 0.55, 0.25]) {
        translate([0, (pcb_y_mount + pcb_y_back)/2, pcb_z_center])
            cube([pcb_w, pcb_t, pcb_h], center=true);
    }
    
    // 3. BH1750 Ambient Light Sensor (Mounted facing -Y at Bottom-Left of user photo: X=+15.5, Z=-15.0)
    color([0.15, 0.45, 0.95]) {
        translate([15.5, pcb_y_back - 5.0, -15.0])
            cube([18.0, 10.0, 14.0], center=true);
    }
    
    // 4. Beetle ESP32-C6 MCU (Mounted facing -Y at Bottom-Center of user photo: X=+16.0, Z=-1.0)
    color([0.18, 0.18, 0.18]) {
        translate([16.0, pcb_y_back - 5.0, -1.0])
            cube([20.5, 10.0, 25.0], center=true);
    }
    
    // 5. ATGM336H GPS Module (Underneath PCB facing +Y at Right side of user photo: Z=+18.0)
    color([0.8, 0.75, 0.4]) {
        translate([4.0, pcb_y_mount + 5.0, 18.0])
            cube([16.0, 10.0, 16.0], center=true);
    }
    
    // 6. External Ceramic GPS Antenna (20 x 5 x 7 mm seated inside the -X GPS Holder Pocket!)
    color([0.88, 0.62, 0.42]) {
        translate([gps_x_center, 4.5, gps_z_center])
            cube([5.0, 7.0, 20.0], center=true);
    }
    
    // 7. 8x D6x3mm Neodymium Magnets (Visualized in silver)
    color([0.80, 0.83, 0.88]) {
        for (pt = screw_pts) {
            // Rear magnet (from Y = -1.8 to Y = +1.2)
            translate([pt[0], 0, pt[1]])
                rotate([-90, 0, 0])
                translate([0, 0, -1.8])
                cylinder(r=3.0, h=3.0);
            // Front magnet (from Y = +1.2 to Y = +4.2)
            translate([pt[0], 0, pt[1]])
                rotate([-90, 0, 0])
                translate([0, 0, 1.2])
                cylinder(r=3.0, h=3.0);
        }
    }
}

// ==========================================
// SCENE COMPOSER
// ==========================================
if (render_part == "assembly") {
    apple_stem();
    color([0.62, 0.18, 0.75, 0.45]) apple_rear_shell();
    color([0.95, 0.78, 0.12, 0.40]) apple_front_shell();
    hardware_mockup();
}
else if (render_part == "cross_section") {
    apple_stem();
    color([0.62, 0.18, 0.75]) difference() {
        apple_rear_shell();
        translate([70, 0, 0]) cube([140, 160, 160], center=true);
    }
    color([0.95, 0.78, 0.12]) difference() {
        apple_front_shell();
        translate([70, 0, 0]) cube([140, 160, 160], center=true);
    }
    hardware_mockup();
}
else if (render_part == "exploded") {
    translate([0, -45, 0]) color([0.62, 0.18, 0.75]) apple_rear_shell();
    translate([0, -25, bat_z_center]) color([0.2, 0.45, 0.9]) cube([54.0, 9.5, 65.0], center=true);
    translate([0, 10, pcb_z_center]) color([0.08, 0.55, 0.25]) cube([pcb_w, pcb_t, pcb_h], center=true);
    translate([0, 45, 0]) color([0.95, 0.78, 0.12]) apple_front_shell();
    translate([0, 45, 18]) apple_stem();
}
else if (render_part == "part_front_shell") {
    apple_front_shell();
}
else if (render_part == "part_rear_shell") {
    apple_rear_shell();
}
else if (render_part == "front_shell") {
    // Pre-oriented for Sindoh 3DWOX 2X: Bowl-Up (open cavity facing +Z, flat base pad on bed Z=0.0!)
    translate([0, 0, bed_flat_y]) rotate([-90, 0, 0]) apple_front_shell();
}
else if (render_part == "rear_shell") {
    // Pre-oriented for Sindoh 3DWOX 2X: Bowl-Up (open cavity facing +Z, flat base pad on bed Z=0.0!)
    translate([0, 0, bed_flat_y]) rotate([90, 0, 0]) apple_rear_shell();
}
else if (render_part == "stem") {
    // Pre-oriented with stem plug base at Z=0.0!
    translate([0, -1.5, -29.0]) apple_stem();
}
else if (render_part == "print_all") {
    // Ready-to-print bed layout (Z >= 0, Bowl-Up, 0% support!)
    translate([-55, 0, bed_flat_y]) rotate([ 90, 0, 0]) apple_rear_shell();
    translate([ 55, 0, bed_flat_y]) rotate([-90, 0, 0]) apple_front_shell();
    translate([  0, 45, -29.0]) apple_stem();
}
