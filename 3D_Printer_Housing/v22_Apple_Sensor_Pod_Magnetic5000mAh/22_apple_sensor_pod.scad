/*
 * Cold Chain Digital Twin Platform
 * v22 Apple Sensor Pod Housing (Enlarged Magnetic Snap + Chimney Convection Vents + GPS Holder)
 * 
 * Major Upgrades & Bug Fixes Verified in this Revision:
 *  1. ENLARGED MAGNETIC POCKETS FOR WIDER & LONGER MAGNETS (Zero Support Inside Holes!):
 *     - Pocket Diameter enlarged to D = 7.60mm (r = 3.80mm, entrance chamfer D = 8.50mm) and
 *       Cylindrical Depth enlarged to H = 5.50mm (plus 8.20mm tall 65-deg conical spire roof!).
 *     - Easily accommodates standard D6x3mm, D6x4mm, D6x5mm, stacked magnets, or wider D7mm magnets
 *       without ever getting blocked by first-layer squish or printing tolerances.
 *     - Bosses positioned at [(+-35.0, +25.0), (+-35.0, -22.0)] with r = 6.50mm so inner boss edges
 *       (|X| = 28.50mm) lie 100% outside the 56.4 x 70.4 mm battery bay (|X| = 28.20mm), and the
 *       Rear Shell boss is deepened to Y = -18.5mm so the conical spire roof never pokes through!
 *  2. CHIMNEY-EFFECT NATURAL CONVECTION VENTS (Top Exhaust + Bottom Intake + 3-Slot SHT45 Grill):
 *     - Bottom cold-air intake slots (Z = -28mm) + Top warm-air exhaust slots (Z = +30mm) continuously
 *       flush out MCU (ESP32-C6) and GPS heat via natural thermal buoyancy (Stack Effect).
 *     - 3-slot side ventilation grill at +X (Z = -4, +2, +8mm) for fast SHT45 ambient response.
 *     - All vents use 65-deg self-supporting teardrop roofs in Dome-Up printing (0% vent support!).
 *  3. 100% BED-FLUSH DOME-UP PRINTING (Z_min = 0.00 mm on BOTH Shells!):
 *     - Both Front Shell and Rear Shell have their entire 360-deg Y = 0.00mm outer rim sitting 100%
 *       flat on the print bed (Z = 0.00 mm), and all 4 PCB standoffs & ribs touch Z = 0.00 mm.
 */

$fn = 72;

// Render modes:
// "assembly", "cross_section", "exploded", "front_shell", "rear_shell", "stem", "print_all", "part_front_shell", "part_rear_shell"
render_part = "assembly"; 

wall_t = 3.0;          // Outer shell wall thickness (mm)
clearance = 0.25;      // 3D printing joint clearance (mm)

// CarrierBoard_v2_50x50 Exact Specifications (from EasyEDA)
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

// External GPS Ceramic Patch Antenna Specifications (User spec: 20 x 5 x 7 mm)
gps_len_z = 21.6;      // 20.0mm antenna length + 1.6mm clearance
gps_wid_x = 7.6;       // 5.0mm ceramic + 2.0mm solder bump + 0.6mm clearance
gps_dep_y = 11.0;      // 7.0mm width + margin
gps_wall  = 2.4;       // Holder wall thickness
gps_x_center = -36.5;  // Seated in the wide -X crescent cavity next to the PCB
gps_z_center = 1.0;

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
// 2. +X SHT45 3-Slot Side Ventilation Grill (Z = -4, +2, +8mm)
// 3. Option 1 Chimney-Effect Natural Convection Vents (Bottom Intake @ Z=-28mm + Top Exhaust @ Z=+30mm)
module functional_cutouts() {
    // 1. Top Stem Plug Socket (D=5.0mm, depth 7mm)
    translate([0, 1.5, 36.0])
        cylinder(r=2.5, h=14, center=true);
        
    // 2. SHT45 Temperature/Humidity Sensor 3-Slot Side Ventilation Grill (+X wall, Z = -4, +2, +8mm)
    // Teardrop-peaked along +Y/-Y so zero support forms inside the slots during Dome-Up printing!
    for (z_s = [-4.0, 2.0, 8.0]) {
        hull() {
            translate([48.0, -2.0, z_s])
                rotate([0, 90, 0])
                cylinder(r=1.8, h=25, center=true);
            translate([48.0,  2.5, z_s])
                rotate([0, 90, 0])
                cylinder(r=0.4, h=25, center=true);
            translate([48.0, -6.5, z_s])
                rotate([0, 90, 0])
                cylinder(r=0.4, h=25, center=true);
        }
    }
    
    // 3. CHIMNEY-EFFECT BOTTOM COOL-AIR INTAKE VENTS (Z = -28.0mm on both Front and Rear shells)
    // Teardrop-sloped along +Y/-Y (65-deg self-supporting roof in Dome-Up orientation -> 0% vent support!)
    for (x_v = [-12.0, 0.0, 12.0]) {
        // Rear intake louver
        hull() {
            translate([x_v, -14.0, -28.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v, -19.0, -28.0]) cylinder(r=0.3, h=35, center=true);
        }
        // Front intake louver
        hull() {
            translate([x_v,  14.0, -28.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v,  19.0, -28.0]) cylinder(r=0.3, h=35, center=true);
        }
    }
    
    // 4. CHIMNEY-EFFECT TOP WARM-AIR EXHAUST VENTS (Z = +30.0mm near top dimple on both Front and Rear shells)
    // Allows rising heat from ESP32-C6 and GPS to escape continuously by natural buoyancy!
    for (x_v = [-12.0, 0.0, 12.0]) {
        // Rear exhaust louver
        hull() {
            translate([x_v, -14.0, 30.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v, -19.0, 30.0]) cylinder(r=0.3, h=35, center=true);
        }
        // Front exhaust louver
        hull() {
            translate([x_v,  14.0, 30.0]) cylinder(r=1.8, h=35, center=true);
            translate([x_v,  19.0, 30.0]) cylinder(r=0.3, h=35, center=true);
        }
    }
}

// ==========================================
// 1. REAR SHELL (MAIN BASE CHASSIS - PURPLE IN PHOTO)
// - Flat Y = 0.00mm Parting Rim (100% flush on print bed Z = 0.00mm!)
// - 4x Enlarged Magnetic Bosses & Pockets (D = 7.60mm x H = 5.50mm + 65-deg spire roof)
// - Wide-open 56.4 x 70.4 mm Flat Velcro Battery Floor at Y = -24.5mm
// - Chimney Convection Intake/Exhaust Vents
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
                // Deepened cylindrical section (h = 12.0mm) + self-supporting taper to Y = -20.0mm ensures the
                // 5.50mm pocket + 8.20mm conical spire roof (13.70mm total) is 100% enclosed inside solid boss!
                for (pt = screw_pts) {
                    norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
                    dir_x = pt[0] / norm_len;
                    dir_z = pt[1] / norm_len;
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0]) {
                            hull() {
                                // Upper solid boss around the 5.50mm deep magnet pocket (Y = 0 to -12.0mm)
                                cylinder(r=mag_boss_r, h=12.0);
                                translate([dir_x * 10.0, dir_z * 10.0, 0])
                                    cylinder(r=mag_boss_r, h=12.0);
                                // Self-supporting taper into the outer wall (down to Y = -20.0mm)
                                translate([dir_x * 3.0, dir_z * 3.0, 20.0])
                                    cylinder(r=5.5, h=0.5);
                            }
                        }
                    }
                }
            }
        }
        
        // 0. Rectangular Battery Corner-Clearance Bay above Y = -24.5mm (56.4mm wide x 70.4mm tall, r=2.2mm corners)
        // Ensures the 4 corners of the 55x68mm 5000mAh battery NEVER hit the curved apple wall or float!
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
                    // Wide entrance chamfer (D = 8.50mm -> 7.60mm) at Y = 0 for effortless magnet insertion
                    translate([0, 0, -0.1])
                        cylinder(r1=mag_r_rear + 0.45, r2=mag_r_rear, h=0.9);
                    // Enlarged D = 7.60mm x 5.50mm deep cylindrical magnet pocket (fits wider & longer magnets!)
                    translate([0, 0, -0.1])
                        cylinder(r=mag_r_rear, h=mag_h_rear + 0.1);
                    // Steep 65-deg self-supporting conical spire roof (>60-deg threshold -> 0% support inside magnet hole!)
                    translate([0, 0, mag_h_rear - 0.02])
                        cylinder(r1=mag_r_rear, r2=0.0, h=8.20);
                }
            }
        }
        
        functional_cutouts();
    }
}

// ==========================================
// 2. FRONT SHELL (INTEGRATED PCB CARRIER CHASSIS - YELLOW IN PHOTO)
// - 360-deg Flat Outer Rim + 4x Enlarged Magnet Bosses + 4x PCB Pillars & Ribs (100% FLUSH at Y=0.0 = Bed Z=0.0!)
// - Integrated 20x5x7mm GPS Ceramic Antenna Pocket with 65-deg Gothic Gable Roof
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
                // Note: rotate([-90, 0, 0]) maps local +Y to global -Z, so use -dir_z to anchor radially outward!
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
                
                // 3) 4x MONOLITHIC RED-ARROW WALL-ANCHORED STANDOFFS (100% FLUSH ON BED Z=0 -> ZERO SUPPORT FRAGMENTS!)
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
                
                // 4) INTEGRATED GPS CERAMIC ANTENNA HOLDER (For 20 x 5 x 7 mm Antenna)
                difference() {
                    hull() {
                        translate([-40.5, 6.5, gps_z_center])
                            cube([19.0, 13.0, gps_len_z + 2*gps_wall], center=true);
                        translate([-45.5, 26.0, gps_z_center])
                            cube([9.0, 1.0, gps_len_z + 2*gps_wall - 4.0], center=true);
                    }
                        
                    // Inner Antenna Pocket Cavity with steep 65-deg gothic gable roof (0% support!)
                    hull() {
                        translate([gps_x_center, 4.75 - 0.1, gps_z_center])
                            cube([5.8, 9.6, gps_len_z], center=true);
                        translate([gps_x_center, 9.5 + 6.2, gps_z_center])
                            cube([0.2, 0.2, gps_len_z - 2.0], center=true);
                    }
                        
                    // Central Wider Relief Channel (7.8mm wide in X) with 65-deg gothic gable roof
                    hull() {
                        translate([gps_x_center, 4.75 - 0.1, gps_z_center])
                            cube([7.8, 9.6, gps_len_z - 5.0], center=true);
                        translate([gps_x_center, 9.5 + 8.0, gps_z_center])
                            cube([0.2, 0.2, gps_len_z - 7.0], center=true);
                    }
                        
                    // Lead-in Entry Chamfer at Y=0 mouth
                    translate([gps_x_center, 0.7, gps_z_center])
                        cube([8.2, 1.6, gps_len_z + 0.8], center=true);
                        
                    // Coaxial Pigtail Cable Exit Slot on +Z side with 65-deg pointed arch roof
                    hull() {
                        translate([gps_x_center, 4.5, gps_z_center + gps_len_z/2])
                            cube([4.4, 9.2, 8.0], center=true);
                        translate([gps_x_center, 9.0 + 4.8, gps_z_center + gps_len_z/2])
                            cube([0.2, 0.2, 6.0], center=true);
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
                    // Wide entrance chamfer (D = 8.50mm -> 7.60mm) at Y = 0 for effortless magnet insertion
                    translate([0, 0, -0.1])
                        cylinder(r1=mag_r_front + 0.45, r2=mag_r_front, h=0.9);
                    // Enlarged D = 7.60mm x 5.50mm deep cylindrical magnet pocket (fits wider & longer magnets!)
                    translate([0, 0, -0.1])
                        cylinder(r=mag_r_front, h=mag_h_front + 0.1);
                    // Steep 65-deg self-supporting conical spire roof (>60-deg threshold -> 0% support inside magnet hole!)
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
// VIRTUAL HARDWARE MOCKUP
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
    
    // 6. External Ceramic GPS Antenna (20 x 5 x 7 mm)
    color([0.88, 0.62, 0.42]) {
        translate([gps_x_center, 4.5, gps_z_center])
            cube([5.0, 7.0, 20.0], center=true);
    }
    
    // 7. 8x Neodymium Magnets (Visualized in silver)
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
    // Pre-oriented DOME-UP (flat 360-deg rim + 4 magnet bosses + 4 PCB pillars sit 100% flush on bed Z=0.0!)
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
