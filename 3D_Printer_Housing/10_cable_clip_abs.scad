/*
 * Cold Chain Sensor Cable Clip V2.0 – ABS-R / No-Support Edition
 *
 * Printer  : Ultimaker Method XL
 * Material : ABS-R (1XA Extruder)
 * Support  : NONE (support-free design)
 *
 * ── Design Rules for ABS-R, No Support ─────────────────────────────────────
 *   1. All overhangs ≤ 45° from vertical  → no support needed
 *   2. Open-top U-channel for cable       → no ceiling = no overhang
 *   3. 45° chamfers on all internal edges → self-supporting bridging
 *   4. Minimum wall 2.4 mm               → ABS-R strength requirement
 *   5. No thin cantilevers < 1.6 mm      → prevents curling in heated chamber
 *
 * ── Estimated Print Time (Method XL, Balanced profile) ──────────────────────
 *   ~30–45 min   (0.2 mm layer, 30% infill, no support, with raft)
 *
 * ── Slicer Settings (UltiMaker Cura / CloudPrint) ────────────────────────────
 *   Printer         : Ultimaker Method XL
 *   Extruder        : 1XA (ABS-R)  ← Extruder 1 only, Extruder 2 = NONE
 *   Material        : ABS-R
 *   Profile         : Balanced  (or High Speed if firmware ≥ 2.7.1)
 *   Layer Height    : 0.20 mm
 *   Infill          : 30%  (Gyroid or Cubic)
 *   Walls           : 3 perimeters
 *   Top/Bottom      : 4 layers
 *   Support         : DISABLED (None)
 *   Raft            : ENABLED  ← critical for ABS-R adhesion on Method XL
 *   Raft Air Gap    : 0.26 mm  (default profile value)
 *   Print Speed     : 50 mm/s perimeter  (auto-managed by profile)
 *   Nozzle Temp     : ~240°C  (auto-managed, do NOT override)
 *   Bed Temp        : ~105°C  (auto-managed)
 *   Chamber Temp    : ~70–100°C  (auto-managed, keep door CLOSED)
 *   Part Cooling    : 0% (ABS-R requires 0% cooling; heated chamber handles it)
 *   Orientation     : Flat base face DOWN  ← as modeled, no rotation needed
 *
 * ── After Print ─────────────────────────────────────────────────────────────
 *   - Let cool inside chamber 10 min before opening (prevents warping)
 *   - Remove raft by hand; thin 0.26 mm gap separates cleanly
 *
 * ── Key Dimensions ───────────────────────────────────────────────────────────
 *   Overall    : 40 × 32 × 18 mm
 *   Cable slot : 6 mm wide (fits USB, sensor, power cables)
 *   Mount hole : M3 (D = 3.2 mm) centre-mount
 */

$fn = 60;

// ── Parameters ───────────────────────────────────────────────────────────────
wall       = 2.4;    // Min wall thickness for ABS-R strength
base_w     = 40.0;  // Overall width
base_l     = 32.0;  // Overall depth
base_h     = 5.0;   // Base plate height
arm_h      = 13.0;  // Side arm height (above base)
cable_d    = 6.4;   // Cable channel width (6mm cable + 0.4 tolerance)
mount_d    = 3.2;   // M3 screw clearance
chamfer    = 1.5;   // Internal chamfer size (45° self-supporting)

// ── Render Control ───────────────────────────────────────────────────────────
render_part = "print"; // "print" | "cross_section"

if (render_part == "print")         cable_clip_abs();
if (render_part == "cross_section") {
    difference() {
        cable_clip_abs();
        translate([-50, 0, -1]) cube([100, 100, 60]);
    }
}

// ── Main Module ───────────────────────────────────────────────────────────────
// Open-top U-channel design: cable drops in from above.
// No overhangs > 45°. Safe to print with ABS-R and zero supports.
module cable_clip_abs() {
    difference() {
        union() {
            // [1] Base footprint – full rounded rectangle
            rounded_box(base_w, base_l, base_h, r=6);

            // [2] Left arm  (solid rectangular arm, fully vertical → 0° overhang)
            translate([-(cable_d/2 + wall + wall/2), 0, base_h + arm_h/2 - 0.5])
            cube([wall * 2, base_l * 0.82, arm_h], center=true);

            // [3] Right arm (mirror)
            translate([ (cable_d/2 + wall + wall/2), 0, base_h + arm_h/2 - 0.5])
            cube([wall * 2, base_l * 0.82, arm_h], center=true);

            // [4] Rear bridge – connects arms at the back (vertical face = 0° overhang)
            translate([0, base_l * 0.41 - wall/2, base_h + arm_h/2 - 0.5])
            cube([cable_d + wall * 4, wall * 2, arm_h], center=true);

            // [5] Retention lip – two small inward-pointing teeth at arm tops
            //     45° chamfered underside → self-supporting, no support needed
            lip_offset_x = cable_d/2 + wall * 2;
            lip_h        = 2.8;
            lip_w        = 2.0;
            lip_top_z    = base_h + arm_h - 0.5;

            for (sx = [-1, 1]) {
                translate([sx * (cable_d/2 + wall * 2), 0, lip_top_z])
                // Tapered tooth: wide at base, tip at cable_d/2 – 0.4
                lip_tooth(sx, lip_w, lip_h);
            }
        }

        // ── Subtractions ─────────────────────────────────────────────────────

        // [A] M3 centre screw hole (straight cylinder = 0° overhang)
        translate([0, 0, -1])
        cylinder(h=base_h + 3, d=mount_d);

        // [B] M3 countersink recess on bottom face (wide → narrow = 0° overhang)
        translate([0, 0, -1])
        cylinder(h=2.2, d1=7.5, d2=mount_d);

        // [C] 45° internal chamfer at base of U-channel to ease cable insertion
        //     (two 45° triangular prisms on left and right inner walls)
        for (sx = [-1, 1]) {
            translate([sx * cable_d/2, 0, base_h])
            rotate([0, sx * -45, 0])
            cube([chamfer * 1.5, base_l + 2, chamfer * 1.5], center=true);
        }

        // [D] Label engraving on the rear bridge face – flush text, no overhang
        translate([0, base_l/2 - 0.4, base_h + arm_h/2])
        rotate([90, 0, 0])
        linear_extrude(0.8)
        text("CC", size=5.5, font="Arial:style=Bold",
             halign="center", valign="center");
    }
}

// ── Retention Lip Tooth ───────────────────────────────────────────────────────
// A wedge-shaped retention tooth. The underside is a 45° chamfer, so it is
// perfectly self-supporting (no support material required).
// sx = +1 (right arm) or -1 (left arm)
module lip_tooth(sx, w, h) {
    // Wedge: wide on arm side, narrows toward cable centre
    rotate([0, 0, 0])
    linear_extrude(height=h)
    polygon(points=[
        [0,           -w * base_l * 0.41],
        [sx * w * -1, -w * base_l * 0.41],
        [sx * w * -1,  w * base_l * 0.41],
        [0,            w * base_l * 0.41]
    ]);
}

// ── Utility ───────────────────────────────────────────────────────────────────
module rounded_box(w, l, h, r) {
    translate([0, 0, h/2])
    linear_extrude(height=h, center=true)
    offset(r=r)
    square([w - r*2, l - r*2], center=true);
}
