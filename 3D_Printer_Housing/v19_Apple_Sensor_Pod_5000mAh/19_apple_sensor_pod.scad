/*
 * Cold Chain Digital Twin Platform
 * v19 Apple Sensor Pod Housing (Diameter 100mm / 10cm Edition)
 * 
 * Target Board: CarrierBoard_BeetleC6_EdgeUSB_50x50 (50.0mm x 50.0mm)
 * Target Battery: JRF PL105568 3.7V 5000mAh LiPo Pouch Cell (10.0 x 55.0 x 68.0mm)
 * 
 * Outer Geometry:
 *  - Diameter: Exactly 100.0mm (10cm)
 *  - Height: 91.87mm (~9.2cm)
 * 
 * Key Features:
 *  - Spacious 5000mAh battery bay with 2.5mm isolation safety wall
 *  - Rigid 4x M3 PCB Standoff Mounting (43x43mm pitch, 8.5mm standoff height)
 *  - Top stem depression with flush USB-C charging/programming port
 *  - Side 4.0mm ventilation port for SHT45 temperature & humidity sensing
 *  - Front tapered aperture for BH1750 ambient light sensor
 *  - Side slot for SW1 power slide switch access
 *  - 4x Perimeter M3 assembly screw bosses with deep countersink
 *  - Precision interlocking tongue-and-groove lip for dust and light sealing
 *  - Modular Apple Stem + Leaf accessory (cosmetic touch & USB dust plug)
 */

$fn = 64;

// Render mode: "cross_section", "assembly", "exploded", "rear_shell", "front_shell", "stem", "print_all"
render_part = "cross_section"; 

wall_t = 3.0;          // Nominal wall thickness (mm)
clearance = 0.25;      // 3D printing joint clearance (mm)

// PCB Specifications
pcb_w = 50.0;
pcb_h = 50.0;
pcb_t = 1.6;
hole_pitch = 43.0;     // M3 hole spacing (43mm x 43mm)
pcb_z_center = 3.0;    // Center of PCB in Z
pcb_y_mount = -1.6;    // Mount face (back of PCB) at Y = -1.6

// JRF PL105568 5000mAh Battery Specifications
bat_w = 58.0;          // Pocket width (cell width 55mm + 3mm margin)
bat_h = 73.0;          // Pocket height (cell body 68mm + 5mm margin for tabs)
bat_t = 12.0;          // Pocket thickness (cell thickness 10mm + 2mm margin)
bat_y_center = -19.5;  // Center Y of battery pocket
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
    translate([0, 0, 36.0]) {
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
    translate([-46.0, 0.0, 22.0])
        rotate([0, 90, 0])
        hull() {
            translate([0, -3.2, 0]) cylinder(r=2.2, h=20, center=true);
            translate([0,  3.2, 0]) cylinder(r=2.2, h=20, center=true);
        }
        
    // 4. Stem Socket at center top
    translate([0, 0, 36.0])
        cylinder(r=2.5, h=14, center=true);
}

// ==========================================
// REAR SHELL (MAIN BASE CHASSIS)
// Holds 5000mAh Battery & PCB Standoffs
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
                
                // 1. JRF PL105568 5000mAh Battery Cradle
                translate([0, bat_y_center, bat_z_center]) {
                    difference() {
                        // Outer cradle perimeter support block
                        cube([bat_w + 4.5, bat_t + 3.5, bat_h + 3.5], center=true);
                        // Battery pocket cavity
                        cube([bat_w, bat_t, bat_h], center=true);
                        // Wiring channel at top right for battery leads
                        translate([-bat_w/2 + 8.0, 0, bat_h/2 - 2.0])
                            cube([18.0, bat_t + 10.0, 14.0], center=true);
                        // Finger extraction notch at center
                        cube([24.0, bat_t + 10.0, 30.0], center=true);
                    }
                }
                
                // 2. Battery Safety Isolation Divider Plate
                translate([0, -10.0, pcb_z_center])
                    cube([bat_w + 4.0, 2.5, bat_h + 2.0], center=true);
                
                // 3. 4x M3 PCB Standoff Pillars (Extending from divider to Y = pcb_y_mount)
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        translate([x_pos, -8.75, z_pos]) {
                            rotate([-90, 0, 0])
                            difference() {
                                cylinder(r=4.0, h=8.75 + pcb_y_mount);
                                // M3 Screw pilot hole (depth 7.5mm)
                                translate([0, 0, 8.75 + pcb_y_mount - 7.0])
                                    cylinder(r=1.4, h=8.0);
                            }
                        }
                    }
                }
                
                // 4. 4x Perimeter Shell Assembly Screw Bosses
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0])
                        difference() {
                            cylinder(r=5.0, h=14.0);
                            // M3 pilot thread hole
                            cylinder(r=1.4, h=14.5);
                        }
                    }
                }
            }
        }
        
        // Perimeter Mating Groove (Y = 0)
        translate([0, 0, 0]) {
            difference() {
                cylinder(r=49.6, h=1.6);
                cylinder(r=45.5, h=1.7);
            }
        }
        
        functional_cutouts();
    }
}

// ==========================================
// FRONT SHELL (PROTECTIVE DOME COVER)
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
                
                // Perimeter Male Mating Lip (Tongue)
                translate([0, -1.4, 0]) {
                    intersection() {
                        difference() {
                            cylinder(r=48.2 - clearance, h=1.5);
                            cylinder(r=46.5 + clearance, h=2.5);
                        }
                        apple_solid_outer();
                    }
                }
                
                // 4x Perimeter Assembly Screw Bosses (Internal through-holes)
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([-90, 0, 0])
                        difference() {
                            cylinder(r=5.0, h=14.0);
                            // Through hole for M3 screw
                            translate([0, 0, -1])
                                cylinder(r=1.7, h=16.0);
                            // Countersink for M3 screw head from outside
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
// APPLE STEM ACCESSORY (꼭지 & 잎사귀)
// ==========================================
module apple_stem() {
    color([0.45, 0.28, 0.12]) { // Woody brown
        translate([0, 0, 35.0]) {
            cylinder(r=2.3, h=8.0, center=true);
            translate([0, 0, 4.0])
            rotate([0, 12, 10])
                cylinder(r1=2.5, r2=1.6, h=24.0);
        }
    }
    color([0.2, 0.65, 0.2]) { // Fresh green
        translate([2.0, 0.7, 49.0])
        rotate([35, -20, 45])
        scale([2.2, 1.0, 0.38])
            sphere(r=5.5);
    }
}

// ==========================================
// VIRTUAL 3D HARDWARE MOCKUP (PCB + BATTERY)
// ==========================================
module hardware_mockup() {
    // 1. CarrierBoard PCB Assembly
    translate([0, pcb_y_mount + pcb_t/2, pcb_z_center]) {
        // FR-4 PCB (50x50x1.6mm)
        color([0.08, 0.42, 0.18, 0.95]) {
            difference() {
                cube([pcb_w, pcb_t, pcb_h], center=true);
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        translate([dx * hole_pitch/2, 0, dz * hole_pitch/2])
                            rotate([90, 0, 0])
                            cylinder(r=1.6, h=pcb_t + 1, center=true);
                    }
                }
            }
        }
        
        // Beetle ESP32-C6 (Top Center, USB-C pointing UP)
        translate([0, pcb_t/2 + 2.0, 12.5]) {
            color([0.15, 0.15, 0.15]) cube([20.5, 2.5, 25.0], center=true);
            color([0.85, 0.85, 0.88]) translate([0, 0, 13.0]) cube([9.0, 3.2, 6.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.5, -2.0]) cube([7.0, 0.8, 7.0], center=true);
        }
        
        // SHT45 (Top Left: +X)
        translate([17.5, pcb_t/2 + 1.5, 15.0]) {
            color([0.75, 0.15, 0.15]) cube([10.0, 1.6, 12.0], center=true);
            color([0.9, 0.9, 0.9]) translate([0, 1.0, 0]) cube([2.5, 0.8, 2.5], center=true);
        }
        
        // MPU6050 (Mid Left: +X)
        translate([17.5, pcb_t/2 + 1.5, 0.0])
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
            
        // BH1750 (Mid Right: -X)
        translate([-17.5, pcb_t/2 + 1.5, 6.0]) {
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.0, 0]) cube([3.0, 0.6, 3.0], center=true);
        }
        
        // ATGM336H GPS (Bottom Left: +X)
        translate([15.0, pcb_t/2 + 3.0, -14.0]) {
            color([0.2, 0.4, 0.2]) cube([13.0, 1.6, 15.0], center=true);
            color([0.75, 0.7, 0.65]) translate([0, 1.5, 0]) cube([10.0, 2.5, 10.0], center=true);
        }
        
        // SW1 Power Switch (Top Right: -X)
        translate([-18.0, pcb_t/2 + 2.0, 21.0]) {
            color([0.8, 0.8, 0.8]) cube([6.5, 2.5, 3.5], center=true);
            color([0.2, 0.2, 0.2]) translate([-1.5, 1.5, 0]) cube([1.5, 2.0, 1.5], center=true);
        }
        
        // 4x M3 Screws fixing PCB to Standoffs
        for (dx = [-1, 1]) {
            for (dz = [-1, 1]) {
                translate([dx * hole_pitch/2, pcb_t/2 + 1.2, dz * hole_pitch/2])
                    color([0.78, 0.78, 0.82])
                    rotate([90, 0, 0])
                    cylinder(r=2.8, h=2.0, center=true);
            }
        }
    }
    
    // 2. JRF PL105568 5000mAh Battery (Behind Safety Wall in Rear Shell)
    translate([0, bat_y_center, bat_z_center]) {
        // Silver Pouch Body (55 x 10 x 68 mm)
        color([0.84, 0.86, 0.88, 0.98])
            cube([55.0, 10.0, 68.0], center=true);
        // Yellow Kapton Insulation Tape & Top Solder Tabs
        color([0.88, 0.68, 0.15])
            translate([0, 0, 33.5])
            cube([55.2, 10.2, 3.0], center=true);
        // Metal Tabs
        color([0.85, 0.85, 0.9]) {
            translate([-14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
            translate([ 14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
        }
        // Red & Black Lead Wires + White 2-Pin JST Connector
        color([0.85, 0.1, 0.1])
            translate([-14.0, 2.0, 42.0])
            rotate([15, 0, 0])
            cylinder(r=0.7, h=14.0);
        color([0.15, 0.15, 0.15])
            translate([14.0, 2.0, 42.0])
            rotate([15, 0, 0])
            cylinder(r=0.7, h=14.0);
        color([0.95, 0.95, 0.95])
            translate([0, 5.0, 44.0])
            cube([6.5, 4.5, 5.0], center=true);
    }
}

// ==========================================
// SCENE RENDER LOGIC
// ==========================================
if (render_part == "cross_section") {
    // 3D Isometric Cutaway View: Cut away front-right half to reveal both PCB and battery
    difference() {
        union() {
            color([0.88, 0.15, 0.15]) apple_rear_shell();
            color([0.88, 0.15, 0.15, 0.85]) apple_front_shell();
            hardware_mockup();
            apple_stem();
        }
        translate([55, 0, 0]) cube([110, 130, 140], center=true);
    }
}
else if (render_part == "assembly") {
    color([0.88, 0.15, 0.15]) apple_rear_shell();
    color([0.88, 0.15, 0.15]) apple_front_shell();
    apple_stem();
}
else if (render_part == "exploded") {
    // Generously exploded view separating all layers in order
    translate([0, -85, 0]) color([0.88, 0.15, 0.15]) apple_rear_shell();
    
    // Battery floating in front of rear shell pocket
    translate([0, -40, 0]) {
        color([0.84, 0.86, 0.88, 0.98])
            cube([55.0, 10.0, 68.0], center=true);
        color([0.88, 0.68, 0.15])
            translate([0, 0, 33.5])
            cube([55.2, 10.2, 3.0], center=true);
        color([0.85, 0.85, 0.9]) {
            translate([-14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
            translate([ 14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
        }
        color([0.85, 0.1, 0.1])
            translate([-14.0, 2.0, 42.0]) rotate([15, 0, 0]) cylinder(r=0.7, h=14.0);
        color([0.15, 0.15, 0.15])
            translate([14.0, 2.0, 42.0]) rotate([15, 0, 0]) cylinder(r=0.7, h=14.0);
        color([0.95, 0.95, 0.95])
            translate([0, 5.0, 44.0]) cube([6.5, 4.5, 5.0], center=true);
    }
    
    // PCB Assembly floating in center
    translate([0, 18, 0]) {
        color([0.08, 0.42, 0.18, 0.95]) {
            difference() {
                cube([pcb_w, pcb_t, pcb_h], center=true);
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        translate([dx * hole_pitch/2, 0, dz * hole_pitch/2])
                            rotate([90, 0, 0])
                            cylinder(r=1.6, h=pcb_t + 1, center=true);
                    }
                }
            }
        }
        
        translate([0, pcb_t/2 + 2.0, 12.5]) {
            color([0.15, 0.15, 0.15]) cube([20.5, 2.5, 25.0], center=true);
            color([0.85, 0.85, 0.88]) translate([0, 0, 13.0]) cube([9.0, 3.2, 6.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.5, -2.0]) cube([7.0, 0.8, 7.0], center=true);
        }
        
        translate([17.5, pcb_t/2 + 1.5, 15.0]) {
            color([0.75, 0.15, 0.15]) cube([10.0, 1.6, 12.0], center=true);
            color([0.9, 0.9, 0.9]) translate([0, 1.0, 0]) cube([2.5, 0.8, 2.5], center=true);
        }
        translate([17.5, pcb_t/2 + 1.5, 0.0])
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
        translate([-17.5, pcb_t/2 + 1.5, 6.0]) {
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.0, 0]) cube([3.0, 0.6, 3.0], center=true);
        }
        translate([15.0, pcb_t/2 + 3.0, -14.0]) {
            color([0.2, 0.4, 0.2]) cube([13.0, 1.6, 15.0], center=true);
            color([0.75, 0.7, 0.65]) translate([0, 1.5, 0]) cube([10.0, 2.5, 10.0], center=true);
        }
        translate([-18.0, pcb_t/2 + 2.0, 21.0]) {
            color([0.8, 0.8, 0.8]) cube([6.5, 2.5, 3.5], center=true);
            color([0.2, 0.2, 0.2]) translate([-1.5, 1.5, 0]) cube([1.5, 2.0, 1.5], center=true);
        }
        for (dx = [-1, 1]) {
            for (dz = [-1, 1]) {
                translate([dx * hole_pitch/2, pcb_t/2 + 1.2, dz * hole_pitch/2])
                    color([0.78, 0.78, 0.82])
                    rotate([90, 0, 0])
                    cylinder(r=2.8, h=2.0, center=true);
            }
        }
    }
    
    // Front Shell moved forward
    translate([0, 80, 0]) color([0.88, 0.15, 0.15, 0.85]) apple_front_shell();
    
    // Stem elevated
    translate([0, 0, 38]) apple_stem();
}
else if (render_part == "rear_shell") {
    apple_rear_shell();
}
else if (render_part == "front_shell") {
    apple_front_shell();
}
else if (render_part == "stem") {
    apple_stem();
}
else if (render_part == "print_all") {
    translate([-58, 0, 0])
        rotate([90, 0, 0])
        apple_rear_shell();
    translate([ 58, 0, 0])
        rotate([-90, 0, 0])
        apple_front_shell();
    translate([0, 52, 0])
        rotate([90, 0, 0])
        apple_stem();
}
