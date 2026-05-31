/* 
 * Desktop Presentation and Auto-Scan Stand for GM77/ESP32 Scanner V1.0
 * 
 * Author: Antigravity AI (Google DeepMind)
 * Description: 
 *   A table-mountable, angled presentation stand that holds the scanner housing at a 
 *   perfect 35-degree angle. This allows hands-free presentation scanning of QR codes 
 *   on agricultural produce packaging in the cold chain digital twin experiment.
 */

$fn = 60;
clearance = 0.4;

// [Stand Parameters]
base_w = 90.0;      // Base plate width
base_l = 95.0;      // Base plate length
base_h = 8.0;       // Base plate height
arm_h = 105.0;      // Height of the stand arm
arm_tilt = 35;      // Forward tilt angle (degrees)

// Scanner mating dimensions (matching 06_housing_3d_design.scad)
handle_top_d = 28.0;
flange_w = 28.0 + 6.0; // handle_top_d + 6 = 34mm flange

// --- Main Control ---
render_part = "assembly"; // assembly, print, cross_section

if (render_part == "assembly") {
    scanner_stand();
    
    // Position and show the scanner housing in the docked state for visual reference
    // The handle neck sits in the fork, flange rests in the recess
    translate([0, arm_h * sin(arm_tilt) - 13.5, arm_h * cos(arm_tilt) + base_h + 10])
    rotate([arm_tilt - 18, 0, 0]) { // aligned to the stand angle
        % scanner_dummy_reference(); // transparent reference
    }
}

if (render_part == "print") {
    scanner_stand();
}

if (render_part == "cross_section") {
    difference() {
        scanner_stand();
        // Cut half of the stand to see the internal thickness and arm ribs
        translate([0, -100, -20])
        cube([100, 300, 200]);
    }
}

// --- 1. Main Scanner Desktop Stand ---
module scanner_stand() {
    difference() {
        union() {
            // [A] Stable Table Base Plate (rounded rectangle)
            rounded_base(base_w, base_l, base_h, 10);
            
            // [B] Ergonomically Curved Support Arm
            hull() {
                // Bottom of the arm blending into the base
                translate([0, -10, base_h - 1])
                cylinder(h=5, d1=26, d2=22, center=true);
                
                // Top neck of the arm (tilted forward)
                translate([0, arm_h * sin(arm_tilt), arm_h * cos(arm_tilt) + base_h])
                rotate([arm_tilt, 0, 0])
                cylinder(h=2, d=32, center=true);
            }
            
            // [C] U-Shaped Cradle Fork
            translate([0, arm_h * sin(arm_tilt), arm_h * cos(arm_tilt) + base_h])
            rotate([arm_tilt, 0, 0])
            cradle_fork();
        }

        // [D] Screw holes to fix the stand to a workbench (M4, D=4.2mm + Countersink)
        translate([-base_w/2 + 12, 0, -1]) {
            cylinder(h=base_h + 3, d=4.2);
            translate([0, 0, base_h - 3.5]) cylinder(h=4, d1=4.2, d2=8.5);
        }
        translate([base_w/2 - 12, 0, -1]) {
            cylinder(h=base_h + 3, d=4.2);
            translate([0, 0, base_h - 3.5]) cylinder(h=4, d1=4.2, d2=8.5);
        }
        
        // Brand Engraving on the base plate
        translate([0, base_l/2 - 16, base_h - 1.2])
        linear_extrude(2)
        text("DYNAMIC SCANNER STAND", size=4.0, font="Arial:style=Bold", halign="center");
    }
}

// --- 2. U-Shaped Cradle Fork ---
module cradle_fork() {
    fork_outer_w = flange_w + 12; // 34 + 12 = 46mm outer width
    fork_outer_l = flange_w + 10; // 34 + 10 = 44mm
    fork_h = 24.0;
    
    difference() {
        // Outer rounded body of the fork
        translate([0, 8, fork_h/2])
        linear_extrude(height=fork_h, center=true)
        offset(r=5)
        square([fork_outer_w - 10, fork_outer_l - 10], center=true);

        // U-Shape slot cutout for the scanner handle (opens forward, -Y)
        // Handle neck is diameter 28.0. Slot width is 28.0 + 0.8 clearance = 28.8mm.
        translate([0, -15, fork_h/2 + 1])
        cube([handle_top_d + clearance*2, fork_outer_l + 10, fork_h + 2], center=true);
        
        // Round bottom of the U-slot
        translate([0, 0, -1])
        cylinder(h=fork_h + 4, d=handle_top_d + clearance*2);
        
        // Flange locking recess pocket (recess for the 34x34mm scanner flange to sit in)
        // Depth is 3.5mm. Sits at the top of the fork to prevent vertical slippage.
        translate([0, 0, fork_h - 3.5]) {
            // Rectangular pocket cutout
            translate([0, 1.5, 2])
            cube([flange_w + clearance*2, flange_w + clearance*2 + 10, 4.1], center=true);
            
            // Rounded backing of the pocket
            cylinder(h=4.1, r=(flange_w + clearance*2)/2);
        }
        
        // Front chamfer for smooth slide-in entry
        translate([-16, -14, fork_h - 2]) rotate([0, 45, 0]) cube([10, 10, 10]);
        translate([16, -14, fork_h - 2]) rotate([0, -45, 0]) cube([10, 10, 10]);
    }
}

// --- Utility Modules ---

module rounded_base(w, l, h, r) {
    translate([0, 0, h/2])
    linear_extrude(height=h, center=true)
    offset(r=r)
    square([w - r*2, l - r*2], center=true);
}

// --- Dummy Scanner Reference for Assembly View ---
// Renders a simplified silhouette of our scanner so the user sees how it docks
module scanner_dummy_reference() {
    union() {
        // Scanner Head (from 06_housing_3d_design.scad)
        translate([0, -56*0.6, -2.5]) {
            // Hollow head shape
            difference() {
                hull() {
                    translate([0, 2, 18]) rotate([90,0,0]) rounded_rect_2d(42, 30, 8);
                    translate([0, 28, 18]) rotate([90,0,0]) rounded_rect_2d(48, 36, 12);
                    translate([0, 72.8, 18]) rotate([90,0,0]) rounded_rect_2d(43.2, 32.4, 10);
                    translate([0, 109.6, 18]) rotate([90,0,0]) rounded_rect_2d(37.4, 28, 8);
                }
                // Hollowing
                translate([0, 50, 18]) cube([44, 120, 32], center=true);
            }
            
            // Lid
            translate([0, 0, 33])
            rounded_base(48, 112, 3, 8);
        }
        
        // Flange (docking contact)
        translate([0, 0, -2])
        rounded_base(flange_w, flange_w, 4, 5);
        
        // Scanner Handle
        rotate([18, 0, 0]) {
            hull() {
                translate([0, 0, 0]) cylinder(h=0.1, r=14);
                translate([0, 1.0, -20]) cylinder(h=0.1, r=15.5);
                translate([0, -1.0, -45]) cylinder(h=0.1, r=15.0);
                translate([0, -2.5, -70]) cylinder(h=0.1, r=16.0);
                translate([0, -4.0, -90]) cylinder(h=0.1, r=18.0);
            }
            // Trigger Guard
            translate([0, 28 - 112*0.6, 5])
            difference() {
                rotate([0, 90, 0]) translate([0, 0, -3]) cylinder(h=6, d=28);
                rotate([0, 90, 0]) translate([2, 4, -5]) cylinder(h=10, d=22);
                translate([-5, -20, -15]) cube([10, 20, 30]);
            }
        }
    }
}

module rounded_rect_2d(w, h, r) {
    offset(r=r)
    square([w-r*2, h-r*2], center=true);
}
