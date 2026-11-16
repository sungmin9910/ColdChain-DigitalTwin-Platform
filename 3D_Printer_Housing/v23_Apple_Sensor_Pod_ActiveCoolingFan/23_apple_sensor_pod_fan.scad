/*
 * Cold Chain Digital Twin Platform
 * v23 Apple Sensor Pod Housing — ACTIVE COOLING FAN EDITION (2510 Micro Fan + Enlarged Magnetic Snap)
 * 
 * Major Upgrades in v23:
 *  1. INTEGRATED 2510 (25 x 25 x 10 mm) ACTIVE COOLING FAN HOLDER & DIRECT AIR DUCT (+X Wall):
 *     - Dedicated screwless slide-in pocket on the +X inner wall of the Front Shell (symmetric to the
 *       -X GPS antenna holder), accommodating standard 25x25x10mm (2510) or 25x25x7mm (2507) 5V/3.3V fans.
 *     - Features an inner 16x20mm teardrop airflow window facing the ESP32-C6 & SHT45 sensor, a 4-slot
 *       outer aerodynamic grill through the +X apple wall, a top 2-pin wire exit slot, and a 65-deg
 *       self-supporting gothic gable roof (0% support inside the fan pocket during Dome-Up printing!).
 *  2. ENLARGED MAGNETIC POCKETS (D = 7.60mm x H = 5.50mm + 65-deg Conical Spire Roof):
 *     - Fits wider and longer neodymium magnets (D6x3, D6x4, D6x5, stacked, or D7mm) with zero blockage.
 *  3. FORCED + NATURAL CONVECTION CROSS-FLOW (Top/Bottom Louvers + +X Fan Duct):
 *     - Active fan airflow combines with top (Z=+30mm) and bottom (Z=-28mm) louvers to continuously sweep
 *       MCU/GPS heat out of the enclosure and keep SHT45 at true ambient temperature & humidity.
 */

$fn = 72;

// Render modes:
// "assembly", "cross_section", "exploded", "front_shell", "rear_shell", "stem", "print_all", "part_front_shell", "part_rear_shell"
render_part = "assembly"; 

wall_t = 3.0;          // Outer shell wall thickness (mm)
clearance = 0.25;      // 3D printing joint clearance (mm)

// CarrierBoard_v2_50x50 Exact Specifications (from EasyEDA / KiCad)
pcb_w = 50.0;
pcb_h = 50.0;
pcb_t = 1.6;
hole_pitch = 43.0;     // 4x M3 mounting holes at (+-21.5, +-21.5)
pcb_z_center = 3.0;    // Shifted +3mm in Z for optimal internal volume balance

// PCB Mount Plane at Y = 0.0mm (100% flush with Front Shell print bed Z=0.0!)
pcb_y_mount = 0.0;
pcb_y_back = pcb_y_mount - pcb_t; // Y = -1.6mm

// 4x Magnetic Bosses (Positioned so inner boss edge |X| = 28.50mm > 28.20mm battery bay!)
screw_pts = [
    [-35.0,  25.0],
    [ 35.0,  25.0],
    [-35.0, -22.0],
    [ 35.0, -22.0]
];

// Enlarged Magnet Pocket Specifications (Fits wider & longer magnets: D = 7.60mm, cylindrical depth = 5.50mm!)
mag_r_front = 3.80;    // D = 7.60mm diameter (entrance chamfer D = 8.50mm)
mag_h_front = 5.50;    // 5.50mm cylindrical depth (+ 8.20mm 65-deg conical roof = 13.70mm total center depth)
mag_r_rear  = 3.80;    // D = 7.60mm diameter (entrance chamfer D = 8.50mm)
mag_h_rear  = 5.50;    // 5.50mm cylindrical depth (+ 8.20mm 65-deg conical roof = 13.70mm total center depth)
mag_boss_r  = 6.50;    // D = 13.00mm boss outer diameter (2.70mm solid wall around D=7.60mm hole)

// External GPS Ceramic Patch Antenna Specifications (20 x 5 x 7 mm, mounted on -X wall)
gps_len_z = 21.6;
gps_wid_x = 7.6;
gps_dep_y = 11.0;
gps_wall  = 2.4;
gps_x_center = -36.5;
gps_z_center = 1.0;

// 2510 Active Cooling Fan Specifications (25 x 25 x 10 mm standard micro fan, mounted on +X wall)
fan_len_z = 25.8;      // 25.0mm fan height + 0.8mm clearance (Z = -11.4 to +14.4mm)
fan_dep_y = 25.8;      // 25.0mm fan width + 0.8mm clearance (Y = 0.0 to +25.8mm)
fan_wid_x = 10.6;      // 10.0mm fan thickness + 0.6mm clearance (fits 2510 [10mm] and 2507 [7mm] fans!)
fan_wall  = 1.8;       // Holder wall thickness
fan_x_center = 32.0;   // Pocket spans X = +26.7 to +37.3mm (inner wall at X = +25.1mm > +25.0mm PCB edge!)
fan_z_center = 1.5;    // Centered at Z = +1.5mm (clears bottom magnet boss Z=-15.5 and top boss Z=+18.5!)

// Outer Profile (R, Z) - Max Outer Diameter 100.0mm (R=50.0mm), Height 91.87mm
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
  [ 48.35, 15.73],
  [ 47.43, 18.95],
  [ 46.39, 22.16],
  [ 45.25, 25.15],
  [ 43.87, 28.02],
  [ 42.37, 30.78],
  [ 40.77, 33.42],
  [ 39.04, 35.83],
  [ 37.09, 38.13],
  [ 35.14, 40.31],
  [ 32.96, 42.26],
  [ 30.66, 43.98],
  [ 28.25, 45.48],
  [ 25.72, 46.51],
  [ 23.20, 47.20],
  [ 20.67, 47.31],
  [ 18.14, 46.85],
  [ 15.73, 46.05],
  [ 13.44, 44.79],
  [ 11.25, 43.41],
  [  9.19, 41.80],
  [  7.35, 40.31],
  [  5.63, 38.93],
  [  4.13, 37.90],
  [  2.76, 37.09],
  [  1.49, 36.52],
  [  0.00, 36.17]
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

// Natural continuous outer apple body
module apple_solid_outer() {
    rotate_extrude(angle=360, $fn=72) {
        polygon(concat([[0, apple_outer_profile[0][1]]], apple_outer_profile, [[0, apple_outer_profile[len(apple_outer_profile)-1][1]]]));
    }
}

// Natural continuous inner apple cavity
module apple_solid_inner() {
    rotate_extrude(angle=360, $fn=72) {
        polygon(concat([[0, apple_inner_profile[0][1]]], apple_inner_profile, [[0, apple_inner_profile[len(apple_inner_profile)-1][1]]]));
    }
}

// Shared functional cutouts:
// 1. Top Stem Socket
// 2. +X Active Cooling Fan 4-Slot Aerodynamic Duct Grill (Z = -6.0, -1.0, +4.0, +9.0mm, Y = +3.5 to +22.0mm)
// 3. Top & Bottom Forced/Natural Convection Louvers (Z = -28mm and Z = +30mm)
module functional_cutouts() {
    // 1. Top Stem Plug Socket (D=5.0mm, depth 7mm)
    translate([0, 1.5, 36.0])
        cylinder(r=2.5, h=14, center=true);
        
    // 2. +X Active Cooling Fan 4-Slot Aerodynamic Exhaust/Intake Grill (Aligned with 2510 Fan Center!)
    // Teardrop-peaked along +Y (65-deg roof in Dome-Up orientation -> 0% support inside fan grill!)
    for (z_s = [-6.0, -1.0, 4.0, 9.0]) {
        hull() {
            translate([44.0, 4.5, z_s])
                rotate([0, 90, 0])
                cylinder(r=1.6, h=25, center=true);
            translate([44.0, 19.5, z_s])
                rotate([0, 90, 0])
                cylinder(r=1.6, h=25, center=true);
            translate([44.0, 23.0, z_s])
                rotate([0, 90, 0])
                cylinder(r=0.35, h=25, center=true);
        }
        // Auxiliary SHT45 direct side breathing slit near Y = -2.0mm
        hull() {
            translate([48.0, -2.5, z_s])
                rotate([0, 90, 0])
                cylinder(r=1.4, h=25, center=true);
            translate([48.0, -6.0, z_s])
                rotate([0, 90, 0])
                cylinder(r=0.35, h=25, center=true);
        }
    }
    
    // 3. BOTTOM COOL-AIR INTAKE VENTS (Z = -28.0mm on both Front and Rear shells)
    for (x_v = [-12.0, 0.0, 12.0]) {
        hull() {
            translate([x_v, -14.0, -28.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v, -19.0, -28.0]) cylinder(r=0.3, h=35, center=true);
        }
        hull() {
            translate([x_v,  14.0, -28.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v,  19.0, -28.0]) cylinder(r=0.3, h=35, center=true);
        }
    }
    
    // 4. TOP WARM-AIR EXHAUST VENTS (Z = +30.0mm near top dimple on both Front and Rear shells)
    for (x_v = [-12.0, 0.0, 12.0]) {
        hull() {
            translate([x_v, -14.0, 30.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v, -19.0, 30.0]) cylinder(r=0.3, h=35, center=true);
        }
        hull() {
            translate([x_v,  14.0, 30.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v,  19.0, 30.0]) cylinder(r=0.3, h=35, center=true);
        }
    }
}

// ==========================================
// 1. REAR SHELL (MAIN BASE CHASSIS - PURPLE IN PHOTO)
// ==========================================
module apple_rear_shell() {
    difference() {
        intersection() {
            apple_solid_outer();
            union() {
                // 1) Main rear half shell (Y <= 0.0)
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
                
                // 2) Wide-Open Flat Velcro Battery Platform at Y = -24.5mm
                translate([0, -38.0, 0])
                    cube([140, 27.0, 140], center=true);
                
                // 3) 4x Enlarged Wall-Integrated Magnetic Bosses (r = 6.50mm, deepened to Y = -20.0mm!)
                for (pt = screw_pts) {
                    norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
                    dir_x = pt[0] / norm_len;
                    dir_z = pt[1] / norm_len;
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0]) {
                            hull() {
                                cylinder(r=mag_boss_r, h=12.0);
                                translate([dir_x * 10.0, dir_z * 10.0, 0])
                                    cylinder(r=mag_boss_r, h=12.0);
                                translate([dir_x * 3.0, dir_z * 3.0, 20.0])
                                    cylinder(r=5.5, h=0.5);
                            }
                        }
                    }
                }
            }
        }
        
        // 0. Rectangular Battery Corner-Clearance Bay above Y = -24.5mm (56.4mm wide x 70.4mm tall, r=2.2mm corners)
        translate([0, 0, -0.5]) {
            rotate([90, 0, 0]) {
                translate([0, 0, -0.5]) {
                    hull() {
                        for (cx = [-26.0, 26.0]) {
                            for (cz = [-33.0, 33.0]) {
                                translate([cx, cz, 0])
                                    cylinder(r=2.2, h=24.98);
                            }
                        }
                    }
                }
            }
        }
        
        // A. 4x Enlarged Rear Magnet Pockets (D = 7.60mm x H = 5.50mm + 65-deg spire roof -> 0% hole support!)
        for (pt = screw_pts) {
            translate([pt[0], 0, pt[1]]) {
                rotate([90, 0, 0]) {
                    translate([0, 0, -0.1])
                        cylinder(r1=mag_r_rear + 0.45, r2=mag_r_rear, h=0.9);
                    translate([0, 0, -0.1])
                        cylinder(r=mag_r_rear, h=mag_h_rear + 0.1);
                    translate([0, 0, mag_h_rear - 0.02])
                        cylinder(r1=mag_r_rear, r2=0.0, h=8.20);
                }
            }
        }
        
        functional_cutouts();
    }
}

// ==========================================
// 2. FRONT SHELL (INTEGRATED PCB CARRIER + 2510 ACTIVE COOLING FAN DUCT + GPS HOLDER)
// ==========================================
module apple_front_shell() {
    difference() {
        intersection() {
            apple_solid_outer();
            union() {
                // 1) Main front half shell (Y >= 0.0)
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
                
                // 2) 4x Enlarged Wall-Integrated Magnetic Bosses (r = 6.50mm, 100% Flush at Y=0.0 = Bed Z=0.0!)
                for (pt = screw_pts) {
                    norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
                    dir_x = pt[0] / norm_len;
                    dir_z = pt[1] / norm_len;
                    translate([pt[0], 0, pt[1]]) {
                        rotate([-90, 0, 0]) {
                            hull() {
                                cylinder(r=mag_boss_r, h=12.0);
                                translate([dir_x * 10.0, -dir_z * 10.0, 0])
                                    cylinder(r=mag_boss_r, h=12.0);
                                translate([dir_x * 3.0, -dir_z * 3.0, 20.0])
                                    cylinder(r=5.5, h=0.5);
                            }
                        }
                    }
                }
                
                // 3) 4x MONOLITHIC RED-ARROW WALL-ANCHORED STANDOFFS (100% FLUSH ON BED Z=0!)
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        
                        rib_len_z = (dz > 0) ? 16.5 : 20.0;
                        rib_x = dx * 3.5;
                        rib_y = -dz * rib_len_z;
                        
                        translate([x_pos, 0, z_pos]) {
                            rotate([-90, 0, 0]) {
                                translate([0, 0, pcb_y_mount]) {
                                    hull() {
                                        cylinder(r=4.0, h=46.0);
                                        translate([rib_x, rib_y, 0])
                                            cylinder(r=4.2, h=46.0);
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 4) INTEGRATED GPS CERAMIC ANTENNA HOLDER ON -X WALL (For 20 x 5 x 7 mm Antenna)
                difference() {
                    hull() {
                        translate([-40.5, 6.5, gps_z_center])
                            cube([19.0, 13.0, gps_len_z + 2*gps_wall], center=true);
                        translate([-45.5, 26.0, gps_z_center])
                            cube([9.0, 1.0, gps_len_z + 2*gps_wall - 4.0], center=true);
                    }
                    hull() {
                        translate([gps_x_center, 4.75 - 0.1, gps_z_center])
                            cube([5.8, 9.6, gps_len_z], center=true);
                        translate([gps_x_center, 9.5 + 6.2, gps_z_center])
                            cube([0.2, 0.2, gps_len_z - 2.0], center=true);
                    }
                    hull() {
                        translate([gps_x_center, 4.75 - 0.1, gps_z_center])
                            cube([7.8, 9.6, gps_len_z - 5.0], center=true);
                        translate([gps_x_center, 9.5 + 8.0, gps_z_center])
                            cube([0.2, 0.2, gps_len_z - 7.0], center=true);
                    }
                    translate([gps_x_center, 0.7, gps_z_center])
                        cube([8.2, 1.6, gps_len_z + 0.8], center=true);
                    hull() {
                        translate([gps_x_center, 4.5, gps_z_center + gps_len_z/2])
                            cube([4.4, 9.2, 8.0], center=true);
                        translate([gps_x_center, 9.0 + 4.8, gps_z_center + gps_len_z/2])
                            cube([0.2, 0.2, 6.0], center=true);
                    }
                }
                
                // 5) INTEGRATED 2510 ACTIVE COOLING FAN HOLDER & AIR DUCT ON +X WALL (For 25 x 25 x 10 mm Fan)
                // Sits 100% flush on print bed (Y = 0.0mm = Z_print = 0.0mm), outside X = +25.0mm PCB edge!
                difference() {
                    // A. Outer Fan Housing Block fused into +X shell wall with 65-deg self-supporting upper ramp
                    hull() {
                        translate([37.5, 13.0, fan_z_center])
                            cube([24.6, 26.0, fan_len_z + 2*fan_wall], center=true);
                        translate([43.5, 36.5, fan_z_center])
                            cube([12.0, 1.0, fan_len_z + 2*fan_wall - 4.0], center=true);
                    }
                    
                    // B. 2510 Fan Slide-In Pocket Cavity (10.6mm in X x 25.8mm in Y x 25.8mm in Z)
                    // Includes steep 65-deg gothic gable roof above Y = +25.8mm -> 0% support inside pocket!
                    hull() {
                        translate([fan_x_center, fan_dep_y/2 - 0.1, fan_z_center])
                            cube([fan_wid_x, fan_dep_y + 0.2, fan_len_z], center=true);
                        translate([fan_x_center, fan_dep_y + 9.5, fan_z_center])
                            cube([0.4, 0.2, fan_len_z - 2.0], center=true);
                    }
                    
                    // C. Lead-in Entry Chamfer at Y = 0.0mm mouth for effortless fan insertion
                    translate([fan_x_center, 0.6, fan_z_center])
                        cube([fan_wid_x + 1.2, 1.4, fan_len_z + 1.0], center=true);
                    
                    // D. Inner Airflow Window on -X wall of fan holder (18.0mm tall x 20.0mm deep teardrop arch)
                    // Connects the 2510 fan rotor directly to the PCB / ESP32-C6 / SHT45 chamber!
                    hull() {
                        translate([fan_x_center - 6.0, 11.5, fan_z_center])
                            cube([14.0, 18.0, 18.0], center=true);
                        translate([fan_x_center - 6.0, 20.5 + 6.5, fan_z_center])
                            cube([14.0, 0.2, 14.0], center=true);
                    }
                    
                    // E. Top 2-Wire Fan Cable Exit Slot (+Z side, with 65-deg pointed arch roof)
                    hull() {
                        translate([fan_x_center, 6.0, fan_z_center + fan_len_z/2])
                            cube([6.0, 12.2, 8.0], center=true);
                        translate([fan_x_center, 12.0 + 5.5, fan_z_center + fan_len_z/2])
                            cube([0.4, 0.2, 6.0], center=true);
                    }
                }
            }
        }
        
        // ==========================================
        // SUBTRACTIONS
        // ==========================================
        
        // A. 4x Enlarged Front Magnet Pockets (D = 7.60mm x H = 5.50mm + 65-deg spire roof -> 0% hole support!)
        for (pt = screw_pts) {
            translate([pt[0], 0, pt[1]]) {
                rotate([-90, 0, 0]) {
                    translate([0, 0, -0.1])
                        cylinder(r1=mag_r_front + 0.45, r2=mag_r_front, h=0.9);
                    translate([0, 0, -0.1])
                        cylinder(r=mag_r_front, h=mag_h_front + 0.1);
                    translate([0, 0, mag_h_front - 0.02])
                        cylinder(r1=mag_r_front, r2=0.0, h=8.20);
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
        translate([0, 1.5, 34.0])
            cylinder(r=2.3, h=10.0, center=true);
            
        translate([0, 1.5, 39.0]) {
            rotate([0, 14, 0])
                cylinder(r1=2.5, r2=1.6, h=15.0);
            translate([2.5, 0, 8.0])
                rotate([25, 45, 15])
                scale([1.8, 0.8, 0.3])
                sphere(r=5.0);
        }
    }
}

// ==========================================
// VIRTUAL HARDWARE MOCKUP (INCLUDING 2510 ACTIVE COOLING FAN!)
// ==========================================
module hardware_mockup() {
    // 1. JRF PL105568 5000mAh Battery (55x68x10mm seated 100% flat on Y = -24.5mm Velcro floor!)
    color([0.2, 0.45, 0.9]) {
        translate([0, -19.5, -0.5])
            cube([55.0, 10.0, 68.0], center=true);
    }
    
    // 2. CarrierBoard PCB Substrate (50x50x1.6mm)
    color([0.08, 0.55, 0.25]) {
        translate([0, (pcb_y_mount + pcb_y_back)/2, pcb_z_center])
            cube([pcb_w, pcb_t, pcb_h], center=true);
    }
    
    // 3. BH1750 Ambient Light Sensor
    color([0.15, 0.45, 0.95]) {
        translate([15.5, pcb_y_back - 5.0, -15.0])
            cube([18.0, 10.0, 14.0], center=true);
    }
    
    // 4. Beetle ESP32-C6 MCU
    color([0.18, 0.18, 0.18]) {
        translate([16.0, pcb_y_back - 5.0, -1.0])
            cube([20.5, 10.0, 25.0], center=true);
    }
    
    // 5. ATGM336H GPS Module
    color([0.8, 0.75, 0.4]) {
        translate([4.0, pcb_y_mount + 5.0, 18.0])
            cube([16.0, 10.0, 16.0], center=true);
    }
    
    // 6. External Ceramic GPS Antenna (20 x 5 x 7 mm on -X wall)
    color([0.88, 0.62, 0.42]) {
        translate([gps_x_center, 4.5, gps_z_center])
            cube([5.0, 7.0, 20.0], center=true);
    }
    
    // 7. 2510 Micro Cooling Fan (25 x 25 x 10 mm seated inside the +X Fan Pocket!)
    color([0.15, 0.15, 0.18]) {
        difference() {
            translate([fan_x_center, 12.8, fan_z_center])
                cube([10.0, 25.0, 25.0], center=true);
            translate([fan_x_center, 12.8, fan_z_center])
                rotate([0, 90, 0])
                cylinder(r=11.0, h=12.0, center=true);
        }
        translate([fan_x_center, 12.8, fan_z_center])
            rotate([0, 90, 0])
            cylinder(r=6.5, h=9.0, center=true);
    }
    
    // 8. 8x Neodymium Magnets (Visualized in silver)
    color([0.80, 0.83, 0.88]) {
        for (pt = screw_pts) {
            translate([pt[0], 0, pt[1]])
                rotate([-90, 0, 0])
                translate([0, 0, -4.5])
                cylinder(r=3.5, h=4.5);
            translate([pt[0], 0, pt[1]])
                rotate([-90, 0, 0])
                translate([0, 0, 0.0])
                cylinder(r=3.5, h=4.5);
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
    translate([0, -25, -0.5]) color([0.2, 0.45, 0.9]) cube([55.0, 10.0, 68.0], center=true);
    translate([0, 10, pcb_z_center]) color([0.08, 0.55, 0.25]) cube([pcb_w, pcb_t, pcb_h], center=true);
    translate([fan_x_center, 25, fan_z_center]) color([0.15, 0.15, 0.18]) cube([10.0, 25.0, 25.0], center=true);
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
    // Pre-oriented DOME-UP (flat 360-deg rim + 4 magnet bosses + 4 PCB pillars + Fan Holder sit 100% flush on bed Z=0.0!)
    rotate([90, 0, 0]) apple_front_shell();
}
else if (render_part == "rear_shell") {
    // Pre-oriented DOME-UP (flat 360-deg rim + 4 magnet bosses sit 100% flush on bed Z=0.0!)
    rotate([-90, 0, 0]) apple_rear_shell();
}
else if (render_part == "stem") {
    translate([0, -1.5, -29.0]) apple_stem();
}
else if (render_part == "print_all") {
    translate([-55, 0, 0]) rotate([-90, 0, 0]) apple_rear_shell();
    translate([ 55, 0, 0]) rotate([ 90, 0, 0]) apple_front_shell();
    translate([  0, 45, -29.0]) apple_stem();
}
