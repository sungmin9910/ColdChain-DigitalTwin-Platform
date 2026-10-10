/*
 * Cold Chain Digital Twin Platform
 * v19 Apple Sensor Pod Housing (5000mAh Battery & Rigid PCB Mount)
 * 
 * Target Board: CarrierBoard_BeetleC6_EdgeUSB_50x50 (50.0mm x 50.0mm)
 * Target Battery: JRF PL105568 3.7V 5000mAh LiPo Pouch Cell (10.0 x 55.0 x 68.0mm)
 * 
 * Features:
 *  - Authentic Apple Fruit Geometry (Dia 92.5mm x Height 85.0mm)
 *  - High-capacity 5000mAh Battery Compartment with safety isolation wall
 *  - Rigid 4x M3 PCB Standoff Mounting (43x43mm pitch, 8mm standoff height)
 *  - Top stem depression with flush USB-C charging/programming port
 *  - Side 4.0mm ventilation port for SHT45 temperature & humidity sensing
 *  - Front tapered aperture for BH1750 ambient light sensor (box open detect)
 *  - Side slot for SW1 power slide switch access
 *  - 4x Perimeter M3 assembly screw bosses outside the PCB/Battery envelope
 *  - Precision interlocking tongue-and-groove lip for dust and light sealing
 *  - Modular Apple Stem + Leaf accessory (cosmetic touch & USB dust plug)
 */

$fn = 64;

// Render mode: "cross_section", "assembly", "exploded", "rear_shell", "front_shell", "stem", "print_all"
render_part = "cross_section"; 

wall_t = 2.85;         // Nominal wall thickness
clearance = 0.25;      // 3D printing joint clearance

// PCB Specifications
pcb_w = 50.0;
pcb_h = 50.0;
pcb_t = 1.6;
hole_pitch = 43.0;     // M3 hole spacing (43mm x 43mm)
pcb_z_center = 2.5;    // Center of PCB in Z
pcb_y_mount = -1.6;    // Mount face (back of PCB) at Y = -1.6

// JRF PL105568 5000mAh Battery Specifications
bat_w = 57.0;          // Pocket width (cell width 55mm + 2mm margin)
bat_h = 72.0;          // Pocket height (cell body 68mm + 4mm margin for tabs)
bat_t = 11.5;          // Pocket thickness (cell thickness 10mm + 1.5mm margin)
bat_y_center = -18.0;  // Center Y of battery pocket
bat_z_center = 1.5;    // Center Z of battery

// Perimeter Assembly Screws (4 corners outside PCB & battery)
screw_pts = [
    [-32.0,  24.0],    // Top-left
    [ 32.0,  24.0],    // Top-right
    [-31.0, -21.0],    // Bottom-left
    [ 31.0, -21.0]     // Bottom-right
];

// Outer Apple Profile (R, Z) - Max Dia ~92.5mm, Height ~85mm (scale ~1.065)
apple_outer_profile = [
  [ 0.00, -34.61], [ 1.07, -35.25], [ 2.24, -35.89], [ 3.51, -36.53], [ 4.79, -37.17],
  [ 6.18, -37.70], [ 7.67, -38.34], [ 9.16, -38.98], [10.76, -39.51], [12.46, -40.04],
  [14.27, -40.58], [16.19, -40.90], [18.11, -41.22], [20.13, -41.32], [22.26, -41.22],
  [24.28, -41.00], [26.31, -40.47], [28.33, -39.73], [30.25, -38.77], [32.16, -37.60],
  [33.97, -36.10], [35.68, -34.40], [37.38, -32.38], [38.87, -30.25], [40.36, -27.80],
  [41.64, -25.13], [42.81, -22.26], [43.77, -19.17], [44.62, -15.98], [45.26, -12.67],
  [45.80,  -9.27], [46.22,  -5.75], [46.33,  -2.24], [46.37,   1.28], [46.22,   4.69],
  [45.90,   8.10], [45.48,  11.40], [44.84,  14.59], [43.99,  17.57], [43.03,  20.55],
  [41.96,  23.32], [40.68,  25.99], [39.30,  28.54], [37.81,  30.99], [36.21,  33.23],
  [34.40,  35.36], [32.59,  37.38], [30.57,  39.19], [28.44,  40.79], [26.20,  42.17],
  [23.86,  43.13], [21.51,  43.77], [19.17,  43.88], [16.83,  43.45], [14.59,  42.71],
  [12.46,  41.54], [10.44,  40.26], [ 8.52,  38.77], [ 6.82,  37.38], [ 5.22,  36.10],
  [ 3.83,  35.15], [ 2.56,  34.40], [ 1.38,  33.87], [ 0.00,  33.55]
];

// Inner Cavity Profile (R, Z)
apple_inner_profile = [
  [ 0.00, -30.8], [ 1.07, -31.5], [ 2.24, -32.1], [ 3.51, -32.7], [ 4.90, -33.3],
  [ 6.39, -34.0], [ 7.99, -34.6], [ 9.69, -35.2], [11.39, -35.8], [13.20, -36.3],
  [15.12, -36.7], [17.15, -37.1], [19.28, -37.3], [21.41, -37.4], [23.54, -37.2],
  [25.56, -36.7], [27.58, -36.1], [29.39, -35.2], [31.20, -34.2], [32.80, -32.9],
  [34.40, -31.3], [35.79, -29.6], [37.07, -27.7], [38.24, -25.6], [39.30, -23.2],
  [40.26, -20.8], [41.01, -18.1], [41.64, -15.3], [42.17, -12.5], [42.60,  -9.5],
  [42.92,  -6.5], [43.13,  -3.4], [43.24,  -0.3], [43.20,   2.8], [42.92,   5.8],
  [42.60,   8.7], [42.07,  11.6], [41.32,  14.4], [40.47,  17.1], [39.51,  19.7],
  [38.34,  22.2], [37.07,  24.5], [35.58,  26.7], [33.97,  28.8], [32.38,  30.7],
  [30.57,  32.5], [28.65,  34.1], [26.63,  35.6], [24.60,  36.8], [22.47,  37.9],
  [20.24,  38.8], [18.00,  39.3], [15.76,  39.5], [13.63,  39.4], [11.61,  38.9],
  [ 9.59,  38.0], [ 7.77,  37.0], [ 6.07,  35.8], [ 4.58,  34.6], [ 3.30,  33.7],
  [ 2.13,  32.9], [ 1.07,  32.3], [ 0.00,  31.7]
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
    translate([0, 0, 33.0]) {
        hull() {
            translate([-5.0, 0, 0]) cylinder(r=2.8, h=20, center=true);
            translate([ 5.0, 0, 0]) cylinder(r=2.8, h=20, center=true);
        }
        translate([0, 0, 8.0])
            cylinder(r1=7.5, r2=11.0, h=6.5, center=true);
    }
    
    // 2. Left Ventilation Hole for SHT45 (Viewer Left: +X)
    translate([44.5, -2.0, 15.0])
        rotate([0, 90, 0])
        cylinder(r=2.0, h=25, center=true);
        
    // 3. Right Power Switch (SW1) Slot (Viewer Right: -X)
    translate([-42.5, 0.0, 20.5])
        rotate([0, 90, 0])
        hull() {
            translate([0, -3.0, 0]) cylinder(r=2.2, h=20, center=true);
            translate([0,  3.0, 0]) cylinder(r=2.2, h=20, center=true);
        }
        
    // 4. Stem Socket at center top
    translate([0, 0, 33.0])
        cylinder(r=2.4, h=12, center=true);
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
                        translate([0, -65, 0]) cube([130, 130, 130], center=true);
                    }
                    intersection() {
                        apple_solid_inner();
                        translate([0, -65, 0]) cube([130, 130, 130], center=true);
                    }
                }
                
                // 1. JRF PL105568 5000mAh Battery Cradle
                translate([0, bat_y_center, bat_z_center]) {
                    difference() {
                        // Outer cradle perimeter support block
                        cube([bat_w + 4.0, bat_t + 3.0, bat_h + 3.0], center=true);
                        // Battery pocket cavity
                        cube([bat_w, bat_t, bat_h], center=true);
                        // Wiring channel at top right for battery leads
                        translate([-bat_w/2 + 8.0, 0, bat_h/2 - 2.0])
                            cube([16.0, bat_t + 8.0, 12.0], center=true);
                        // Finger extraction notch at center
                        cube([22.0, bat_t + 8.0, 28.0], center=true);
                    }
                }
                
                // 2. Battery Safety Isolation Divider Plate (Y = -10.5 to -8.5)
                translate([0, -9.5, pcb_z_center])
                    cube([bat_w + 3.0, 2.0, bat_h + 2.0], center=true);
                
                // 3. 4x M3 PCB Standoff Pillars (Extending from divider to Y = pcb_y_mount)
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        translate([x_pos, -8.5, z_pos]) {
                            rotate([-90, 0, 0])
                            difference() {
                                cylinder(r=3.8, h=8.5 + pcb_y_mount);
                                // M3 Screw pilot hole (depth 7mm)
                                translate([0, 0, 8.5 + pcb_y_mount - 6.5])
                                    cylinder(r=1.4, h=7.5);
                            }
                        }
                    }
                }
                
                // 4. 4x Perimeter Shell Assembly Screw Bosses
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0])
                        difference() {
                            cylinder(r=4.8, h=12.0);
                            // M3 pilot thread hole
                            cylinder(r=1.4, h=12.5);
                        }
                    }
                }
            }
        }
        
        // Perimeter Mating Groove (Y = 0)
        translate([0, 0, 0]) {
            difference() {
                cylinder(r=46.0, h=1.5);
                cylinder(r=42.0, h=1.6);
            }
        }
        
        functional_cutouts();
    }
}

// ==========================================
// FRONT SHELL (PROTECTIVE DOME COVER)
// Covers MCU, Sensors and provides light window
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
                        translate([0, 65, 0]) cube([130, 130, 130], center=true);
                    }
                    intersection() {
                        apple_solid_inner();
                        translate([0, 65, 0]) cube([130, 130, 130], center=true);
                    }
                }
                
                // Perimeter Male Mating Lip (Tongue)
                translate([0, -1.3, 0]) {
                    intersection() {
                        difference() {
                            cylinder(r=44.7 - clearance, h=1.4);
                            cylinder(r=43.0 + clearance, h=2.2);
                        }
                        apple_solid_outer();
                    }
                }
                
                // 4x Perimeter Assembly Screw Bosses (Internal through-holes)
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([-90, 0, 0])
                        difference() {
                            cylinder(r=4.8, h=12.0);
                            // Through hole for M3 screw
                            translate([0, 0, -1])
                                cylinder(r=1.7, h=14.0);
                            // Countersink for M3 screw head from outside
                            translate([0, 0, 6.5])
                                cylinder(r=3.3, h=7.0);
                        }
                    }
                }
            }
        }
        
        functional_cutouts();
        
        // BH1750 Ambient Light Sensor Tapered Window (Viewer Right: -X)
        translate([-17.5, 38.0, 16.0])
            rotate([90, 0, 0])
            cylinder(r1=3.8, r2=2.2, h=18.0, center=true);
    }
}

// ==========================================
// APPLE STEM ACCESSORY (꼭지 & 잎사귀)
// ==========================================
module apple_stem() {
    color([0.45, 0.28, 0.12]) { // Woody brown
        translate([0, 0, 32.0]) {
            cylinder(r=2.2, h=7.0, center=true);
            translate([0, 0, 3.5])
            rotate([0, 12, 10])
                cylinder(r1=2.3, r2=1.5, h=22.0);
        }
    }
    color([0.2, 0.65, 0.2]) { // Fresh green
        translate([1.8, 0.6, 45.0])
        rotate([35, -20, 45])
        scale([2.0, 0.95, 0.35])
            sphere(r=5.2);
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
        color([0.85, 0.1, 0.1]) // Red Wire
            translate([-14.0, 2.0, 42.0])
            rotate([15, 0, 0])
            cylinder(r=0.7, h=14.0);
        color([0.15, 0.15, 0.15]) // Black Wire
            translate([14.0, 2.0, 42.0])
            rotate([15, 0, 0])
            cylinder(r=0.7, h=14.0);
        color([0.95, 0.95, 0.95]) // JST Plug
            translate([0, 5.0, 44.0])
            cube([6.5, 4.5, 5.0], center=true);
    }
}

// ==========================================
// SCENE RENDER LOGIC
// ==========================================
if (render_part == "cross_section") {
    // 3D Isometric Cutaway View: 1/4 cutaway revealing PCB, Standoffs, Battery & Cutouts
    difference() {
        union() {
            color([0.88, 0.15, 0.15]) apple_rear_shell();
            color([0.88, 0.15, 0.15, 0.85]) apple_front_shell();
            hardware_mockup();
            apple_stem();
        }
        // Cut away front-right half to reveal both PCB and battery inside
        translate([50, 0, 0]) cube([100, 120, 130], center=true);
    }
}
else if (render_part == "assembly") {
    color([0.88, 0.15, 0.15]) apple_rear_shell();
    color([0.88, 0.15, 0.15]) apple_front_shell();
    apple_stem();
}
else if (render_part == "exploded") {
    // Generously exploded view separating all layers in order:
    // [Rear Shell] -> [Battery] -> [PCB] -> [Front Shell] -> [Stem]
    translate([0, -85, 0]) color([0.88, 0.15, 0.15]) apple_rear_shell();
    
    // Battery floating in front of rear shell pocket
    translate([0, -40, 0]) {
        // Battery pouch (55 x 10 x 68 mm)
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
    translate([0, 15, 0]) {
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
        
        // Beetle ESP32-C6
        translate([0, pcb_t/2 + 2.0, 12.5]) {
            color([0.15, 0.15, 0.15]) cube([20.5, 2.5, 25.0], center=true);
            color([0.85, 0.85, 0.88]) translate([0, 0, 13.0]) cube([9.0, 3.2, 6.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.5, -2.0]) cube([7.0, 0.8, 7.0], center=true);
        }
        
        // Sensors
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
    translate([0, 75, 0]) color([0.88, 0.15, 0.15, 0.85]) apple_front_shell();
    
    // Stem elevated
    translate([0, 0, 35]) apple_stem();
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
    // Both shells laid flat on 3D printer bed (parting plane Y=0 facing down)
    translate([-55, 0, 0])
        rotate([90, 0, 0])
        apple_rear_shell();
    translate([ 55, 0, 0])
        rotate([-90, 0, 0])
        apple_front_shell();
    translate([0, 48, 0])
        rotate([90, 0, 0])
        apple_stem();
}
