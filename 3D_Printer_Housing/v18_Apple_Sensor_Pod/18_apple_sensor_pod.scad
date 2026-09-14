/*
 * Cold Chain Digital Twin Platform
 * v18 Apple Sensor Pod Housing
 * 
 * Target Board: CarrierBoard_BeetleC6_EdgeUSB_50x50 (50mm x 50mm)
 * Target Battery: Lithium-ion / LiPo Pouch Cell (3.7V 500~1200mAh, ~50x30x10mm)
 * 
 * Features:
 *  - Authentic Apple Fruit Geometry (87mm Dia x 80mm Height)
 *  - Top stem depression with flush USB-C charging/programming port
 *  - Left 4mm circular ventilation hole for SHT45 temperature & humidity sensing
 *  - Right power switch (SW) access slot
 *  - Front aperture for BH1750 ambient light sensor
 *  - Internal 4x M3 standoffs (43mm x 43mm pitch) for PCB mounting
 *  - Bottom integrated cradle for Lithium-ion battery
 *  - 4x perimeter M3 assembly screw bosses outside the PCB footprint
 *  - Precision interlocking tongue-and-groove perimeter lip
 *  - Modular Apple Stem + Leaf accessory (acts as cosmetic stem or USB dust plug)
 */

$fn = 60;

// ==========================================
// 1. PARAMETERS & DIMENSIONS
// ==========================================

// Render control:
// "assembly", "exploded", "cross_section", "rear_shell", "front_shell", "stem", "print_all"
render_part = "cross_section"; 

wall_t = 2.8;          // Nominal wall thickness
clearance = 0.25;      // 3D printing joint clearance

// PCB Specifications
pcb_w = 50.0;
pcb_h = 50.0;
pcb_t = 1.6;
pcb_z_center = 3.0;    // Z offset of PCB center
pcb_y_mount = -4.0;    // Y position of PCB back face
hole_pitch = 43.0;     // M3 hole spacing (43mm x 43mm)

// Battery Compartment Specifications
bat_w = 52.0;          // Max width of pouch battery
bat_h = 13.0;          // Cradle pocket height
bat_t = 10.0;          // Pocket depth (Y-direction)
bat_z_pos = -28.5;     // Z center of battery

// Perimeter Assembly Screws (4 corners outside PCB)
screw_pts = [
    [-29.0,  23.0],    // Top-left
    [ 29.0,  23.0],    // Top-right
    [-27.0, -20.0],    // Bottom-left
    [ 27.0, -20.0]     // Bottom-right
];

// ==========================================
// 2. APPLE SPLINE PROFILES
// ==========================================

// Outer Apple Profile (R, Z) - Max Diameter ~87mm, Height ~80mm
apple_outer_profile = [
  [0.0, -32.5],
  [1.0, -33.1],
  [2.1, -33.7],
  [3.3, -34.3],
  [4.5, -34.9],
  [5.8, -35.4],
  [7.2, -36.0],
  [8.6, -36.6],
  [10.1, -37.1],
  [11.7, -37.6],
  [13.4, -38.1],
  [15.2, -38.4],
  [17.0, -38.7],
  [18.9, -38.8],
  [20.9, -38.7],
  [22.8, -38.5],
  [24.7, -38.0],
  [26.6, -37.3],
  [28.4, -36.4],
  [30.2, -35.3],
  [31.9, -33.9],
  [33.5, -32.3],
  [35.1, -30.4],
  [36.5, -28.4],
  [37.9, -26.1],
  [39.1, -23.6],
  [40.2, -20.9],
  [41.1, -18.0],
  [41.9, -15.0],
  [42.5, -11.9],
  [43.0, -8.7],
  [43.4, -5.4],
  [43.5, -2.1],
  [43.54, 1.2],
  [43.4, 4.4],
  [43.1, 7.6],
  [42.7, 10.7],
  [42.1, 13.7],
  [41.3, 16.5],
  [40.4, 19.3],
  [39.4, 21.9],
  [38.2, 24.4],
  [36.9, 26.8],
  [35.5, 29.1],
  [34.0, 31.2],
  [32.3, 33.2],
  [30.6, 35.1],
  [28.7, 36.8],
  [26.7, 38.3],
  [24.6, 39.6],
  [22.4, 40.5],
  [20.2, 41.1],
  [18.0, 41.2],
  [15.8, 40.8],
  [13.7, 40.1],
  [11.7, 39.0],
  [9.8, 37.8],
  [8.0, 36.4],
  [6.4, 35.1],
  [4.9, 33.9],
  [3.6, 33.0],
  [2.4, 32.3],
  [1.3, 31.8],
  [0.0, 31.5]
];

// Inner Cavity Profile (R, Z) - Provides generous space for PCB & battery
apple_inner_profile = [
  [0.0, -29.0],
  [1.0, -29.6],
  [2.1, -30.2],
  [3.3, -30.7],
  [4.6, -31.3],
  [6.0, -31.9],
  [7.5, -32.5],
  [9.1, -33.1],
  [10.7, -33.6],
  [12.4, -34.1],
  [14.2, -34.5],
  [16.1, -34.8],
  [18.1, -35.0],
  [20.1, -35.1],
  [22.1, -34.9],
  [24.0, -34.5],
  [25.9, -33.9],
  [27.6, -33.1],
  [29.3, -32.1],
  [30.8, -30.9],
  [32.3, -29.4],
  [33.6, -27.8],
  [34.8, -26.0],
  [35.9, -24.0],
  [36.9, -21.8],
  [37.8, -19.5],
  [38.5, -17.0],
  [39.1, -14.4],
  [39.6, -11.7],
  [40.0, -8.9],
  [40.3, -6.1],
  [40.5, -3.2],
  [40.6, -0.3],
  [40.56, 2.6],
  [40.3, 5.4],
  [40.0, 8.2],
  [39.5, 10.9],
  [38.8, 13.5],
  [38.0, 16.1],
  [37.1, 18.5],
  [36.0, 20.8],
  [34.8, 23.0],
  [33.4, 25.1],
  [31.9, 27.0],
  [30.4, 28.8],
  [28.7, 30.5],
  [26.9, 32.0],
  [25.0, 33.4],
  [23.1, 34.6],
  [21.1, 35.6],
  [19.0, 36.4],
  [16.9, 36.9],
  [14.8, 37.1],
  [12.8, 37.0],
  [10.9, 36.5],
  [9.0, 35.7],
  [7.3, 34.7],
  [5.7, 33.6],
  [4.3, 32.5],
  [3.1, 31.6],
  [2.0, 30.9],
  [1.0, 30.3],
  [0.0, 29.8]
];

// ==========================================
// 3. BASE 3D GEOMETRY MODULES
// ==========================================

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

// Interlocking step flange (Tongue & Groove)
module perimeter_lip(is_male=true) {
    lip_w = 1.3;
    lip_d = 1.5;
    t_offset = is_male ? 0 : -clearance;
    
    intersection() {
        apple_solid_outer();
        difference() {
            cylinder(r=45, h=lip_d * 2, center=true);
            cylinder(r=37.5, h=lip_d * 3, center=true);
        }
    }
}

// Common functional cutouts (USB-C, Vent hole, Switch, Stem socket)
module functional_cutouts() {
    // 1. Top USB-C Port Cutout
    // Centered at X=0, top of PCB is Z=28
    translate([0, 0, 31.0]) {
        hull() {
            translate([-4.8, 0, 0]) cylinder(r=2.5, h=18, center=true);
            translate([ 4.8, 0, 0]) cylinder(r=2.5, h=18, center=true);
        }
        // Funnel bevel for easy cable plug-in
        translate([0, 0, 7.5])
            cylinder(r1=7.0, r2=10.0, h=6.0, center=true);
    }
    
    // 2. Left 4mm Circular Ventilation Hole for SHT45 (Viewer Left: +X in rot_z=180)
    translate([42.0, -3.0, 15.0])
        rotate([0, 90, 0])
        cylinder(r=2.0, h=25, center=true);
        
    // 3. Right Power Switch (SW1) Port (Viewer Right: -X in rot_z=180)
    translate([-40.0, -1.0, 20.0])
        rotate([0, 90, 0])
        hull() {
            translate([0, -2.5, 0]) cylinder(r=2.2, h=20, center=true);
            translate([0,  2.5, 0]) cylinder(r=2.2, h=20, center=true);
        }
        
    // 4. Apple Stem Center Socket (Top Calyx)
    translate([0, 0, 31.0])
        cylinder(r=2.25, h=10, center=true);
}

// ==========================================
// 4. REAR SHELL (MAIN BASE HOUSING)
// ==========================================

module apple_rear_shell() {
    difference() {
        intersection() {
            apple_solid_outer();
            union() {
                // Main outer half shell (Y <= 0)
                difference() {
                    intersection() {
                        apple_solid_outer();
                        translate([0, -60, 0]) cube([120, 120, 120], center=true);
                    }
                    intersection() {
                        apple_solid_inner();
                        translate([0, -60, 0]) cube([120, 120, 120], center=true);
                    }
                }
                
                // A. PCB Standoffs (4x M3 posts inside rear shell extending to Y = pcb_y_mount)
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        translate([x_pos, -35.0, z_pos]) {
                            rotate([-90, 0, 0])
                            difference() {
                                cylinder(r=3.5, h=35.0 + pcb_y_mount);
                                // Pilot hole for M3 screw / heat-set insert
                                translate([0, 0, 35.0 + pcb_y_mount - 7.0])
                                    cylinder(r=1.45, h=8.0);
                            }
                        }
                    }
                }
                
                // B. Lithium-ion Battery Cradle (Molded at bottom of rear shell)
                translate([0, -8.0, bat_z_pos]) {
                    difference() {
                        // Cradle frame
                        cube([bat_w + 3.6, 12.0, bat_h + 3.0], center=true);
                        // Battery pocket
                        translate([0, 1.2, 0])
                            cube([bat_w, bat_t, bat_h + 5], center=true);
                        // Cable pass-through slot on right side
                        translate([-21.0, 3.0, 0])
                            cube([8.0, 8.0, bat_h + 10], center=true);
                        // Center finger notch for easy battery removal
                        translate([0, 0, -4.0])
                            cube([16.0, 15.0, 10.0], center=true);
                    }
                }
                
                // C. 4x Perimeter Assembly Screw Bosses (Extend into -Y from Y=0)
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([90, 0, 0])
                        difference() {
                            cylinder(r=4.5, h=10.0);
                            // M3 pilot thread hole
                            translate([0, 0, 0])
                                cylinder(r=1.4, h=10.5);
                        }
                    }
                }
            }
        }
        
        // Recessed Groove for Tongue-and-Groove mating (Y = 0)
        translate([0, 0, 0]) {
            difference() {
                cylinder(r=43.5, h=1.4);
                cylinder(r=39.5, h=1.5);
            }
        }
        
        // Subtract functional cutouts
        functional_cutouts();
    }
}

// ==========================================
// 5. FRONT SHELL (FRONT COVER HOUSING)
// ==========================================

module apple_front_shell() {
    difference() {
        intersection() {
            apple_solid_outer();
            union() {
                // Main outer half shell (Y >= 0)
                difference() {
                    intersection() {
                        apple_solid_outer();
                        translate([0, 60, 0]) cube([120, 120, 120], center=true);
                    }
                    intersection() {
                        apple_solid_inner();
                        translate([0, 60, 0]) cube([120, 120, 120], center=true);
                    }
                }
                
                // A. Interlocking Male Lip (Tongue)
                translate([0, -1.2, 0]) {
                    intersection() {
                        difference() {
                            cylinder(r=42.2 - clearance, h=1.3);
                            cylinder(r=40.5 + clearance, h=2.0);
                        }
                        apple_solid_outer();
                    }
                }
                
                // B. 4x Perimeter Assembly Screw Bosses (Internal only)
                for (pt = screw_pts) {
                    translate([pt[0], 0, pt[1]]) {
                        rotate([-90, 0, 0])
                        difference() {
                            cylinder(r=4.5, h=10.0);
                            // Screw hole
                            translate([0, 0, -1])
                                cylinder(r=1.7, h=12.0);
                            // Countersink from outside
                            translate([0, 0, 6.0])
                                cylinder(r=3.2, h=6.0);
                        }
                    }
                }
            }
        }
        
        // Subtract functional cutouts
        functional_cutouts();
        
        // BH1750 Ambient Light Sensor Beveled Window (Viewer Right: -X)
        translate([-17.5, 36.0, 16.0])
            rotate([90, 0, 0])
            cylinder(r1=3.5, r2=2.0, h=15.0, center=true);
    }
}

// ==========================================
// 6. APPLE STEM ACCESSORY (꼭지 및 잎사귀)
// ==========================================

module apple_stem() {
    color([0.45, 0.28, 0.12]) { // Woody brown
        // Stem curve
        translate([0, 0, 30.0]) {
            // Lower mounting plug
            cylinder(r=2.1, h=6.0, center=true);
            
            // Stem shaft
            translate([0, 0, 3.0])
            rotate([0, 12, 10])
                cylinder(r1=2.2, r2=1.4, h=20.0);
        }
    }
    
    // Green Leaf
    color([0.2, 0.65, 0.2]) {
        translate([1.5, 0.5, 42.0])
        rotate([35, -20, 45])
        scale([1.8, 0.9, 0.3])
            sphere(r=5.0);
    }
}

// ==========================================
// 7. VIRTUAL 3D HARDWARE MOCKUP (VERIFICATION)
// ==========================================

module pcb_carrier_mockup() {
    translate([0, pcb_y_mount + pcb_t/2, pcb_z_center]) {
        // 1. PCB FR-4 Board (50x50x1.6mm)
        color([0.08, 0.42, 0.18, 0.95]) {
            difference() {
                cube([pcb_w, pcb_t, pcb_h], center=true);
                // 4x M3 corner mounting holes
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        translate([dx * hole_pitch/2, 0, dz * hole_pitch/2])
                            rotate([90, 0, 0])
                            cylinder(r=1.6, h=pcb_t + 1, center=true);
                    }
                }
            }
        }
        
        // 2. DFRobot Beetle ESP32-C6 (Top Center, USB-C flush with top)
        translate([0, pcb_t/2 + 2.0, 12.5]) {
            color([0.15, 0.15, 0.15]) // Black MCU board
                cube([20.5, 2.5, 25.0], center=true);
            // Metal USB-C Connector (Pointing UP)
            color([0.85, 0.85, 0.88])
                translate([0, 0, 12.5])
                cube([8.9, 3.2, 5.5], center=true);
            // ESP32 SoC Chip
            color([0.1, 0.1, 0.1])
                translate([0, 1.5, -2.0])
                cube([7.0, 0.8, 7.0], center=true);
        }
        
        // 3. SHT45 온습도 센서 (Top Left for viewer: +X)
        translate([17.5, pcb_t/2 + 1.5, 15.0]) {
            color([0.7, 0.15, 0.15]) // Red Adafruit board
                cube([10.0, 1.6, 12.0], center=true);
            // SHT45 DFN Chip
            color([0.9, 0.9, 0.9])
                translate([0, 1.0, 0])
                cube([2.5, 0.8, 2.5], center=true);
        }
        
        // 4. MPU6050 6축 가속도/자이로 센서 (Mid Left for viewer: +X)
        translate([17.5, pcb_t/2 + 1.5, 0.0]) {
            color([0.15, 0.35, 0.75]) // Blue GY-521 board
                cube([12.0, 1.6, 16.0], center=true);
        }
        
        // 5. BH1750 조도 센서 (Mid Right for viewer: -X)
        translate([-17.5, pcb_t/2 + 1.5, 6.0]) {
            color([0.15, 0.35, 0.75]) // Blue board
                cube([12.0, 1.6, 16.0], center=true);
            // Ambient light sensor IC
            color([0.1, 0.1, 0.1])
                translate([0, 1.0, 0])
                cube([3.0, 0.6, 3.0], center=true);
        }
        
        // 6. ATGM336H GPS Module (Bottom Left for viewer: +X)
        translate([15.0, pcb_t/2 + 3.0, -14.0]) {
            color([0.2, 0.4, 0.2])
                cube([13.0, 1.6, 15.0], center=true);
            // Ceramic Patch Antenna
            color([0.75, 0.7, 0.65])
                translate([0, 1.5, 0])
                cube([10.0, 2.5, 10.0], center=true);
        }
        
        // 7. MicroSD Socket (Bottom Center)
        translate([0, pcb_t/2 + 1.2, -16.0]) {
            color([0.8, 0.8, 0.85])
                cube([14.0, 1.8, 14.0], center=true);
        }
        
        // 8. JST-PH 2.0 Battery Connector (Bottom Right for viewer: -X)
        translate([-18.0, pcb_t/2 + 3.0, -14.0]) {
            color([0.95, 0.95, 0.95])
                cube([6.0, 5.0, 5.0], center=true);
        }
        
        // 9. Power Slide Switch SW1 (Top Right for viewer: -X)
        translate([-18.0, pcb_t/2 + 2.0, 21.0]) {
            color([0.8, 0.8, 0.8]) cube([6.5, 2.5, 3.5], center=true);
            color([0.2, 0.2, 0.2]) translate([-1.5, 1.5, 0]) cube([1.5, 2.0, 1.5], center=true);
        }
        
        // 10. 4x Corner M3 Screws
        for (dx = [-1, 1]) {
            for (dz = [-1, 1]) {
                translate([dx * hole_pitch/2, pcb_t/2 + 1.2, dz * hole_pitch/2])
                    color([0.75, 0.75, 0.78])
                    rotate([90, 0, 0])
                    cylinder(r=2.7, h=1.8, center=true);
            }
        }
    }
    
    // 11. Lithium-ion Pouch Battery (Under PCB)
    translate([0, -8.0, bat_z_pos]) {
        // Battery pouch (Silver aluminum foil)
        color([0.82, 0.84, 0.86, 0.95])
            cube([48.0, 8.5, 11.0], center=true);
        // Yellow Kapton Protection Tape & Leads on right side
        color([0.85, 0.65, 0.15])
            translate([-21.0, 0, 0])
            cube([4.0, 8.6, 11.1], center=true);
        // Red / Black Battery Leads heading to JST
        color([0.8, 0.1, 0.1])
            translate([-18.0, 4.0, 3.0])
            rotate([0, -45, 0])
            cylinder(r=0.6, h=12.0);
    }
}

// ==========================================
// 8. SCENE RENDER LOGIC
// ==========================================

// A. Cross Section View (Matching user reference image)
if (render_part == "cross_section") {
    // Red Apple Rear Shell
    color([0.88, 0.12, 0.14])
        apple_rear_shell();
        
    // Hardware Mockup (PCB, Modules, Battery)
    pcb_carrier_mockup();
}

// B. Full Assembly View
if (render_part == "assembly") {
    color([0.88, 0.12, 0.14])
        apple_rear_shell();
    color([0.88, 0.12, 0.14])
        apple_front_shell();
    apple_stem();
}

// C. Exploded View
if (render_part == "exploded") {
    // Rear Shell moved backward
    translate([0, -45, 0])
        color([0.88, 0.12, 0.14])
        apple_rear_shell();
        
    // Hardware Mockup centered
    pcb_carrier_mockup();
    
    // Front Shell moved forward and slightly offset for clear visibility
    translate([0, 50, 0])
        color([0.88, 0.12, 0.14, 0.85])
        apple_front_shell();
        
    // Stem elevated
    translate([0, 0, 25])
        apple_stem();
        
    // Assembly Screws
    for (pt = screw_pts) {
        translate([pt[0], 70, pt[1]])
            color([0.75, 0.75, 0.78])
            rotate([90, 0, 0])
            cylinder(r=2.5, h=16);
    }
}

// D. 3D Print Layout View (Flat on build plate Z=0, dome facing UP)
if (render_part == "print_all") {
    // Rear Shell oriented with flat rim on bed Z=0, dome in +Z
    translate([-50, 0, 0])
        rotate([-90, 0, 0])
        apple_rear_shell();
        
    // Front Shell oriented with flat rim on bed Z=0, dome in +Z
    translate([50, 0, 0])
        rotate([90, 0, 0])
        apple_front_shell();
        
    // Stem standing upright on base
    translate([0, 0, -27.0])
        apple_stem();
}

// E. Single Component Exports for STL (Ready to print)
if (render_part == "rear_shell") {
    rotate([-90, 0, 0])
        apple_rear_shell();
}

if (render_part == "front_shell") {
    rotate([90, 0, 0])
        apple_front_shell();
}

if (render_part == "stem") {
    translate([0, 0, -27.0])
        apple_stem();
}
