/*
 * Cold Chain Sensor Wiring Cable Clip V1.0
 *
 * Author: Antigravity AI (Google DeepMind)
 * Description:
 *   A simple, snap-fit cable management clip designed for cold chain
 *   sensor pod wiring. Mounts onto standard DIN rail or flat surfaces
 *   using a single M3 screw. Holds cables of 4~8mm diameter.
 *   Estimated print time: ~25–40 minutes (0.2mm layer, 20% infill)
 *
 * Print Settings:
 *   - Layer Height: 0.2 mm
 *   - Infill: 20%
 *   - Supports: NOT required
 *   - Orientation: Flat side down (as designed)
 *
 * Key Dimensions:
 *   - Overall footprint: ~38 × 28 × 14 mm
 *   - Cable slot diameter: 6 mm (suitable for USB / sensor cables)
 *   - Mounting hole: M3 (D=3.2mm)
 */

$fn = 60;

// ── Parameters ──────────────────────────────────────────────────────────────
wall        = 2.2;     // Wall thickness
base_w      = 38.0;   // Clip overall width
base_l      = 28.0;   // Clip overall length (depth)
base_h      = 5.0;    // Base plate height
clip_h      = 14.0;   // Height of the cable-retaining arch above the base
cable_d     = 6.0;    // Inner cable channel diameter (adjust to your cable OD)
gap_w       = 4.8;    // Snap-fit opening gap width (slightly less than cable_d)
snap_thick  = 1.4;    // Thickness of the snap arms
mount_d     = 3.2;    // M3 screw clearance hole
label_depth = 0.6;    // Engraved label depth

// ── Render Control ───────────────────────────────────────────────────────────
render_part = "print"; // "print" | "assembly" | "cross_section"

if (render_part == "print")        cable_clip();
if (render_part == "assembly")     cable_clip();
if (render_part == "cross_section") {
    difference() {
        cable_clip();
        translate([0, -50, -1]) cube([100, 100, 50]);
    }
}

// ── Main Module ──────────────────────────────────────────────────────────────
module cable_clip() {
    difference() {
        union() {
            // [1] Base plate – rounded rectangle
            rounded_box(base_w, base_l, base_h, r=5);

            // [2] Left arch wall
            translate([-base_w/4, 0, base_h - 0.5])
            arch_wall();

            // [3] Right arch wall (mirrored)
            translate([base_w/4, 0, base_h - 0.5])
            arch_wall();

            // [4] Cable bridge spanning the top of both arch walls
            cable_bridge();
        }

        // ── Subtractions ──────────────────────────────────────────────────

        // [A] Cable channel cylinder (runs front-to-back through the arch)
        translate([0, 0, base_h + clip_h/2 + 1.5])
        rotate([90, 0, 0])
        cylinder(h=base_l + 4, d=cable_d, center=true);

        // [B] Snap-fit gap – vertical slit in the front opening
        translate([0, -base_l/2 - 1, base_h])
        cube([gap_w, base_l * 0.55, clip_h + 4], center=false);

        // [C] M3 mounting screw hole in the base plate centre
        translate([0, 0, -1])
        cylinder(h=base_h + 3, d=mount_d);

        // [D] Small countersink / washer recess on the bottom
        translate([0, 0, -1])
        cylinder(h=2.0, d1=7.5, d2=mount_d);

        // [E] "CC" brand mark engraved on the top bridge
        translate([0, 2, base_h + clip_h + 1.5])
        rotate([180, 0, 0])
        linear_extrude(label_depth + 0.1)
        text("CC CLIP", size=3.2, font="Arial:style=Bold",
             halign="center", valign="center");
    }
}

// ── Arch Wall ────────────────────────────────────────────────────────────────
// One half of the C-shaped retaining arch
module arch_wall() {
    arch_w     = base_w/2 - gap_w/2 - wall;  // width of each arm
    arch_depth = base_l * 0.75;               // depth (front-to-back)

    // Vertical arm body
    cube([wall*1.8, arch_depth, clip_h], center=true);
}

// ── Cable Bridge ─────────────────────────────────────────────────────────────
// Horizontal cap that joins both arch walls and fully encircles the cable
module cable_bridge() {
    bridge_h = wall * 1.6;
    top_z    = base_h + clip_h - bridge_h/2 + 1.5;

    translate([0, 0, top_z])
    difference() {
        // Solid rounded bridge slab
        rounded_box(base_w * 0.72, base_l * 0.75, bridge_h, r=3);
    }
}

// ── Utility ──────────────────────────────────────────────────────────────────
module rounded_box(w, l, h, r) {
    translate([0, 0, h/2])
    linear_extrude(height=h, center=true)
    offset(r=r)
    square([w - r*2, l - r*2], center=true);
}
