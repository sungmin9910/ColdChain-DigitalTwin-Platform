import subprocess
import os
import shutil

scale = 50.0 / 43.54  # 1.14837 to achieve exact outer diameter 100.0mm

outer_raw = [
  [ 0.0, -32.5], [ 1.0, -33.1], [ 2.1, -33.7], [ 3.3, -34.3], [ 4.5, -34.9],
  [ 5.8, -35.4], [ 7.2, -36.0], [ 8.6, -36.6], [10.1, -37.1], [11.7, -37.6],
  [13.4, -38.1], [15.2, -38.4], [17.0, -38.7], [18.9, -38.8], [20.9, -38.7],
  [22.8, -38.5], [24.7, -38.0], [26.6, -37.3], [28.4, -36.4], [30.2, -35.3],
  [31.9, -33.9], [33.5, -32.3], [35.1, -30.4], [36.5, -28.4], [37.9, -26.1],
  [39.1, -23.6], [40.2, -20.9], [41.1, -18.0], [41.9, -15.0], [42.5, -11.9],
  [43.0,  -8.7], [43.4,  -5.4], [43.5,  -2.1], [43.54,  1.2], [43.4,   4.4],
  [43.1,   7.6], [42.7,  10.7], [42.1,  13.7], [41.3,  16.5], [40.4,  19.3],
  [39.4,  21.9], [38.2,  24.4], [36.9,  26.8], [35.5,  29.1], [34.0,  31.2],
  [32.3,  33.2], [30.6,  35.1], [28.7,  36.8], [26.7,  38.3], [24.6,  39.6],
  [22.4,  40.5], [20.2,  41.1], [18.0,  41.2], [15.8,  40.8], [13.7,  40.1],
  [11.7,  39.0], [ 9.8,  37.8], [ 8.0,  36.4], [ 6.4,  35.1], [ 4.9,  33.9],
  [ 3.6,  33.0], [ 2.4,  32.3], [ 1.3,  31.8], [ 0.0,  31.5]
]

inner_raw = [
  [ 0.0, -29.0], [ 1.0, -29.6], [ 2.1, -30.2], [ 3.3, -30.7], [ 4.6, -31.3],
  [ 6.0, -31.9], [ 7.5, -32.5], [ 9.1, -33.1], [10.7, -33.6], [12.4, -34.1],
  [14.2, -34.5], [16.1, -34.8], [18.1, -35.0], [20.1, -35.1], [22.1, -34.9],
  [24.0, -34.5], [25.9, -33.9], [27.6, -33.1], [29.3, -32.1], [30.8, -30.9],
  [32.3, -29.4], [33.6, -27.8], [34.8, -26.0], [35.9, -24.0], [36.9, -21.8],
  [37.8, -19.5], [38.5, -17.0], [39.1, -14.4], [39.6, -11.7], [40.0,  -8.9],
  [40.3,  -6.1], [40.5,  -3.2], [40.6,  -0.3], [40.56,  2.6], [40.3,   5.4],
  [40.0,   8.2], [39.5,  10.9], [38.8,  13.5], [38.0,  16.1], [37.1,  18.5],
  [36.0,  20.8], [34.8,  23.0], [33.4,  25.1], [31.9,  27.0], [30.4,  28.8],
  [28.7,  30.5], [26.9,  32.0], [25.0,  33.4], [23.1,  34.6], [21.1,  35.6],
  [19.0,  36.4], [16.9,  36.9], [14.8,  37.1], [13.8,  37.0], [10.9,  36.5],
  [ 9.0,  35.7], [ 7.3,  34.7], [ 5.7,  33.6], [ 4.3,  32.5], [ 3.1,  31.6],
  [ 2.0,  30.9], [ 1.0,  30.3], [ 0.0,  29.8]
]

scaled_outer = [[round(r * scale, 2), round(z * scale, 2)] for r, z in outer_raw]
scaled_inner = [[round(r * scale, 2), round(z * scale, 2)] for r, z in inner_raw]

outer_str = ",\n  ".join([f"[{p[0]:6.2f}, {p[1]:6.2f}]" for p in scaled_outer])
inner_str = ",\n  ".join([f"[{p[0]:6.2f}, {p[1]:6.2f}]" for p in scaled_inner])

scad_template = f'''/*
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
  {outer_str}
];

// Inner Cavity Profile (R, Z) - Inner Diameter 93.24mm, Cavity Height 82.91mm
apple_inner_profile = [
  {inner_str}
];

module apple_solid_outer() {{
    rotate_extrude(angle=360, $fn=72) {{
        polygon(concat([[0, apple_outer_profile[0][1]]], apple_outer_profile, [[0, apple_outer_profile[len(apple_outer_profile)-1][1]]]));
    }}
}}

module apple_solid_inner() {{
    rotate_extrude(angle=360, $fn=72) {{
        polygon(concat([[0, apple_inner_profile[0][1]]], apple_inner_profile, [[0, apple_inner_profile[len(apple_inner_profile)-1][1]]]));
    }}
}}

// Functional openings common to shells
module functional_cutouts() {{
    // 1. Top USB-C Port Cutout
    translate([0, 0, 36.0]) {{
        hull() {{
            translate([-5.2, 0, 0]) cylinder(r=2.8, h=22, center=true);
            translate([ 5.2, 0, 0]) cylinder(r=2.8, h=22, center=true);
        }}
        translate([0, 0, 9.0])
            cylinder(r1=8.0, r2=12.0, h=7.0, center=true);
    }}
    
    // 2. Left Ventilation Hole for SHT45 (Viewer Left: +X)
    translate([48.0, -2.0, 16.0])
        rotate([0, 90, 0])
        cylinder(r=2.0, h=25, center=true);
        
    // 3. Right Power Switch (SW1) Slot (Viewer Right: -X)
    translate([-46.0, 0.0, 22.0])
        rotate([0, 90, 0])
        hull() {{
            translate([0, -3.2, 0]) cylinder(r=2.2, h=20, center=true);
            translate([0,  3.2, 0]) cylinder(r=2.2, h=20, center=true);
        }}
        
    // 4. Stem Socket at center top
    translate([0, 0, 36.0])
        cylinder(r=2.5, h=14, center=true);
}}

// ==========================================
// REAR SHELL (MAIN BASE CHASSIS)
// Holds 5000mAh Battery & PCB Standoffs
// ==========================================
module apple_rear_shell() {{
    difference() {{
        intersection() {{
            apple_solid_outer();
            union() {{
                // Main rear half shell (Y <= 0)
                difference() {{
                    intersection() {{
                        apple_solid_outer();
                        translate([0, -70, 0]) cube([140, 140, 140], center=true);
                    }}
                    intersection() {{
                        apple_solid_inner();
                        translate([0, -70, 0]) cube([140, 140, 140], center=true);
                    }}
                }}
                
                // 1. JRF PL105568 5000mAh Battery Cradle
                translate([0, bat_y_center, bat_z_center]) {{
                    difference() {{
                        // Outer cradle perimeter support block
                        cube([bat_w + 4.5, bat_t + 3.5, bat_h + 3.5], center=true);
                        // Battery pocket cavity
                        cube([bat_w, bat_t, bat_h], center=true);
                        // Wiring channel at top right for battery leads
                        translate([-bat_w/2 + 8.0, 0, bat_h/2 - 2.0])
                            cube([18.0, bat_t + 10.0, 14.0], center=true);
                        // Finger extraction notch at center
                        cube([24.0, bat_t + 10.0, 30.0], center=true);
                    }}
                }}
                
                // 2. Battery Safety Isolation Divider Plate
                translate([0, -10.0, pcb_z_center])
                    cube([bat_w + 4.0, 2.5, bat_h + 2.0], center=true);
                
                // 3. 4x M3 PCB Standoff Pillars (Extending from divider to Y = pcb_y_mount)
                for (dx = [-1, 1]) {{
                    for (dz = [-1, 1]) {{
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        translate([x_pos, -8.75, z_pos]) {{
                            rotate([-90, 0, 0])
                            difference() {{
                                cylinder(r=4.0, h=8.75 + pcb_y_mount);
                                // M3 Screw pilot hole (depth 7.5mm)
                                translate([0, 0, 8.75 + pcb_y_mount - 7.0])
                                    cylinder(r=1.4, h=8.0);
                            }}
                        }}
                    }}
                }}
                
                // 4. 4x Perimeter Shell Assembly Screw Bosses
                for (pt = screw_pts) {{
                    translate([pt[0], 0, pt[1]]) {{
                        rotate([90, 0, 0])
                        difference() {{
                            cylinder(r=5.0, h=14.0);
                            // M3 pilot thread hole
                            cylinder(r=1.4, h=14.5);
                        }}
                    }}
                }}
            }}
        }}
        
        // Perimeter Mating Groove (Y = 0)
        translate([0, 0, 0]) {{
            difference() {{
                cylinder(r=49.6, h=1.6);
                cylinder(r=45.5, h=1.7);
            }}
        }}
        
        functional_cutouts();
    }}
}}

// ==========================================
// FRONT SHELL (PROTECTIVE DOME COVER)
// ==========================================
module apple_front_shell() {{
    difference() {{
        intersection() {{
            apple_solid_outer();
            union() {{
                // Main front half shell (Y >= 0)
                difference() {{
                    intersection() {{
                        apple_solid_outer();
                        translate([0, 70, 0]) cube([140, 140, 140], center=true);
                    }}
                    intersection() {{
                        apple_solid_inner();
                        translate([0, 70, 0]) cube([140, 140, 140], center=true);
                    }}
                }}
                
                // Perimeter Male Mating Lip (Tongue)
                translate([0, -1.4, 0]) {{
                    intersection() {{
                        difference() {{
                            cylinder(r=48.2 - clearance, h=1.5);
                            cylinder(r=46.5 + clearance, h=2.5);
                        }}
                        apple_solid_outer();
                    }}
                }}
                
                // 4x Perimeter Assembly Screw Bosses (Internal through-holes)
                for (pt = screw_pts) {{
                    translate([pt[0], 0, pt[1]]) {{
                        rotate([-90, 0, 0])
                        difference() {{
                            cylinder(r=5.0, h=14.0);
                            // Through hole for M3 screw
                            translate([0, 0, -1])
                                cylinder(r=1.7, h=16.0);
                            // Countersink for M3 screw head from outside
                            translate([0, 0, 7.5])
                                cylinder(r=3.4, h=8.0);
                        }}
                    }}
                }}
            }}
        }}
        
        functional_cutouts();
        
        // BH1750 Ambient Light Sensor Tapered Window (Viewer Right: -X)
        translate([-17.5, 41.0, 16.0])
            rotate([90, 0, 0])
            cylinder(r1=4.0, r2=2.2, h=20.0, center=true);
    }}
}}

// ==========================================
// APPLE STEM ACCESSORY (꼭지 & 잎사귀)
// ==========================================
module apple_stem() {{
    color([0.45, 0.28, 0.12]) {{ // Woody brown
        translate([0, 0, 35.0]) {{
            cylinder(r=2.3, h=8.0, center=true);
            translate([0, 0, 4.0])
            rotate([0, 12, 10])
                cylinder(r1=2.5, r2=1.6, h=24.0);
        }}
    }}
    color([0.2, 0.65, 0.2]) {{ // Fresh green
        translate([2.0, 0.7, 49.0])
        rotate([35, -20, 45])
        scale([2.2, 1.0, 0.38])
            sphere(r=5.5);
    }}
}}

// ==========================================
// VIRTUAL 3D HARDWARE MOCKUP (PCB + BATTERY)
// ==========================================
module hardware_mockup() {{
    // 1. CarrierBoard PCB Assembly
    translate([0, pcb_y_mount + pcb_t/2, pcb_z_center]) {{
        // FR-4 PCB (50x50x1.6mm)
        color([0.08, 0.42, 0.18, 0.95]) {{
            difference() {{
                cube([pcb_w, pcb_t, pcb_h], center=true);
                for (dx = [-1, 1]) {{
                    for (dz = [-1, 1]) {{
                        translate([dx * hole_pitch/2, 0, dz * hole_pitch/2])
                            rotate([90, 0, 0])
                            cylinder(r=1.6, h=pcb_t + 1, center=true);
                    }}
                }}
            }}
        }}
        
        // Beetle ESP32-C6 (Top Center, USB-C pointing UP)
        translate([0, pcb_t/2 + 2.0, 12.5]) {{
            color([0.15, 0.15, 0.15]) cube([20.5, 2.5, 25.0], center=true);
            color([0.85, 0.85, 0.88]) translate([0, 0, 13.0]) cube([9.0, 3.2, 6.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.5, -2.0]) cube([7.0, 0.8, 7.0], center=true);
        }}
        
        // SHT45 (Top Left: +X)
        translate([17.5, pcb_t/2 + 1.5, 15.0]) {{
            color([0.75, 0.15, 0.15]) cube([10.0, 1.6, 12.0], center=true);
            color([0.9, 0.9, 0.9]) translate([0, 1.0, 0]) cube([2.5, 0.8, 2.5], center=true);
        }}
        
        // MPU6050 (Mid Left: +X)
        translate([17.5, pcb_t/2 + 1.5, 0.0])
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
            
        // BH1750 (Mid Right: -X)
        translate([-17.5, pcb_t/2 + 1.5, 6.0]) {{
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.0, 0]) cube([3.0, 0.6, 3.0], center=true);
        }}
        
        // ATGM336H GPS (Bottom Left: +X)
        translate([15.0, pcb_t/2 + 3.0, -14.0]) {{
            color([0.2, 0.4, 0.2]) cube([13.0, 1.6, 15.0], center=true);
            color([0.75, 0.7, 0.65]) translate([0, 1.5, 0]) cube([10.0, 2.5, 10.0], center=true);
        }}
        
        // SW1 Power Switch (Top Right: -X)
        translate([-18.0, pcb_t/2 + 2.0, 21.0]) {{
            color([0.8, 0.8, 0.8]) cube([6.5, 2.5, 3.5], center=true);
            color([0.2, 0.2, 0.2]) translate([-1.5, 1.5, 0]) cube([1.5, 2.0, 1.5], center=true);
        }}
        
        // 4x M3 Screws fixing PCB to Standoffs
        for (dx = [-1, 1]) {{
            for (dz = [-1, 1]) {{
                translate([dx * hole_pitch/2, pcb_t/2 + 1.2, dz * hole_pitch/2])
                    color([0.78, 0.78, 0.82])
                    rotate([90, 0, 0])
                    cylinder(r=2.8, h=2.0, center=true);
            }}
        }}
    }}
    
    // 2. JRF PL105568 5000mAh Battery (Behind Safety Wall in Rear Shell)
    translate([0, bat_y_center, bat_z_center]) {{
        // Silver Pouch Body (55 x 10 x 68 mm)
        color([0.84, 0.86, 0.88, 0.98])
            cube([55.0, 10.0, 68.0], center=true);
        // Yellow Kapton Insulation Tape & Top Solder Tabs
        color([0.88, 0.68, 0.15])
            translate([0, 0, 33.5])
            cube([55.2, 10.2, 3.0], center=true);
        // Metal Tabs
        color([0.85, 0.85, 0.9]) {{
            translate([-14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
            translate([ 14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
        }}
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
    }}
}}

// ==========================================
// SCENE RENDER LOGIC
// ==========================================
if (render_part == "cross_section") {{
    // 3D Isometric Cutaway View: Cut away front-right half to reveal both PCB and battery
    difference() {{
        union() {{
            color([0.88, 0.15, 0.15]) apple_rear_shell();
            color([0.88, 0.15, 0.15, 0.85]) apple_front_shell();
            hardware_mockup();
            apple_stem();
        }}
        translate([55, 0, 0]) cube([110, 130, 140], center=true);
    }}
}}
else if (render_part == "assembly") {{
    color([0.88, 0.15, 0.15]) apple_rear_shell();
    color([0.88, 0.15, 0.15]) apple_front_shell();
    apple_stem();
}}
else if (render_part == "exploded") {{
    // Generously exploded view separating all layers in order
    translate([0, -85, 0]) color([0.88, 0.15, 0.15]) apple_rear_shell();
    
    // Battery floating in front of rear shell pocket
    translate([0, -40, 0]) {{
        color([0.84, 0.86, 0.88, 0.98])
            cube([55.0, 10.0, 68.0], center=true);
        color([0.88, 0.68, 0.15])
            translate([0, 0, 33.5])
            cube([55.2, 10.2, 3.0], center=true);
        color([0.85, 0.85, 0.9]) {{
            translate([-14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
            translate([ 14.0, 0, 36.5]) cube([6.0, 0.4, 6.0], center=true);
        }}
        color([0.85, 0.1, 0.1])
            translate([-14.0, 2.0, 42.0]) rotate([15, 0, 0]) cylinder(r=0.7, h=14.0);
        color([0.15, 0.15, 0.15])
            translate([14.0, 2.0, 42.0]) rotate([15, 0, 0]) cylinder(r=0.7, h=14.0);
        color([0.95, 0.95, 0.95])
            translate([0, 5.0, 44.0]) cube([6.5, 4.5, 5.0], center=true);
    }}
    
    // PCB Assembly floating in center
    translate([0, 18, 0]) {{
        color([0.08, 0.42, 0.18, 0.95]) {{
            difference() {{
                cube([pcb_w, pcb_t, pcb_h], center=true);
                for (dx = [-1, 1]) {{
                    for (dz = [-1, 1]) {{
                        translate([dx * hole_pitch/2, 0, dz * hole_pitch/2])
                            rotate([90, 0, 0])
                            cylinder(r=1.6, h=pcb_t + 1, center=true);
                    }}
                }}
            }}
        }}
        
        translate([0, pcb_t/2 + 2.0, 12.5]) {{
            color([0.15, 0.15, 0.15]) cube([20.5, 2.5, 25.0], center=true);
            color([0.85, 0.85, 0.88]) translate([0, 0, 13.0]) cube([9.0, 3.2, 6.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.5, -2.0]) cube([7.0, 0.8, 7.0], center=true);
        }}
        
        translate([17.5, pcb_t/2 + 1.5, 15.0]) {{
            color([0.75, 0.15, 0.15]) cube([10.0, 1.6, 12.0], center=true);
            color([0.9, 0.9, 0.9]) translate([0, 1.0, 0]) cube([2.5, 0.8, 2.5], center=true);
        }}
        translate([17.5, pcb_t/2 + 1.5, 0.0])
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
        translate([-17.5, pcb_t/2 + 1.5, 6.0]) {{
            color([0.15, 0.35, 0.75]) cube([12.0, 1.6, 16.0], center=true);
            color([0.1, 0.1, 0.1]) translate([0, 1.0, 0]) cube([3.0, 0.6, 3.0], center=true);
        }}
        translate([15.0, pcb_t/2 + 3.0, -14.0]) {{
            color([0.2, 0.4, 0.2]) cube([13.0, 1.6, 15.0], center=true);
            color([0.75, 0.7, 0.65]) translate([0, 1.5, 0]) cube([10.0, 2.5, 10.0], center=true);
        }}
        translate([-18.0, pcb_t/2 + 2.0, 21.0]) {{
            color([0.8, 0.8, 0.8]) cube([6.5, 2.5, 3.5], center=true);
            color([0.2, 0.2, 0.2]) translate([-1.5, 1.5, 0]) cube([1.5, 2.0, 1.5], center=true);
        }}
        for (dx = [-1, 1]) {{
            for (dz = [-1, 1]) {{
                translate([dx * hole_pitch/2, pcb_t/2 + 1.2, dz * hole_pitch/2])
                    color([0.78, 0.78, 0.82])
                    rotate([90, 0, 0])
                    cylinder(r=2.8, h=2.0, center=true);
            }}
        }}
    }}
    
    // Front Shell moved forward
    translate([0, 80, 0]) color([0.88, 0.15, 0.15, 0.85]) apple_front_shell();
    
    // Stem elevated
    translate([0, 0, 38]) apple_stem();
}}
else if (render_part == "rear_shell") {{
    apple_rear_shell();
}}
else if (render_part == "front_shell") {{
    apple_front_shell();
}}
else if (render_part == "stem") {{
    apple_stem();
}}
else if (render_part == "print_all") {{
    translate([-58, 0, 0])
        rotate([90, 0, 0])
        apple_rear_shell();
    translate([ 58, 0, 0])
        rotate([-90, 0, 0])
        apple_front_shell();
    translate([0, 52, 0])
        rotate([90, 0, 0])
        apple_stem();
}}
'''

with open(r"3D_Printer_Housing\v19_Apple_Sensor_Pod_5000mAh\19_apple_sensor_pod.scad", "w", encoding="utf-8") as f:
    f.write(scad_template)

print("Updated 19_apple_sensor_pod.scad to 100mm diameter successfully!")
