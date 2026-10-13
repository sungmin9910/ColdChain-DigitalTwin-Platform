import os
import subprocess

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
v21_dir = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v21_Apple_Sensor_Pod_2Piece5000mAh"
scad_path = os.path.join(v21_dir, "21_apple_sensor_pod.scad")

with open(scad_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace standoffs: remove wings, make pure clean cylindrical pillars
old_block = """                // 3) 4x INTEGRATED PCB MOUNTING STANDOFFS (100% WALL-FUSED, ZERO GAP!)
                // Extends h=50.0mm so it penetrates deep into the outer shell wall!
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        norm_len = sqrt(x_pos*x_pos + z_pos*z_pos);
                        dir_x = x_pos / norm_len;
                        dir_z = z_pos / norm_len;
                        
                        translate([x_pos, 0, z_pos]) {
                            rotate([-90, 0, 0]) {
                                union() {
                                    // Main Standoff Pillar body extending h=50.0mm deep through the wall!
                                    translate([0, 0, pcb_y_mount])
                                        cylinder(r=4.8, h=50.0);
                                        
                                    // Bed-anchored anti-overhang foundation (Y = 0 to pcb_y_mount)
                                    // Prints cleanly directly from the build plate at layer 1!
                                    translate([0, 0, 0])
                                        cylinder(r=5.2, h=pcb_y_mount + 0.5);
                                        
                                    // Heavy-duty 45° Radial Gusset fusing the pillar solidly into the dome wall
                                    translate([0, 0, pcb_y_mount]) {
                                        hull() {
                                            cylinder(r=4.4, h=50.0);
                                            translate([dir_x * 14.0, dir_z * 14.0, 0])
                                                cylinder(r=4.0, h=50.0);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }"""

new_block = """                // 3) 4x INTEGRATED PCB MOUNTING STANDOFFS (PURE CYLINDERS, ZERO SENSOR INTERFERENCE!)
                // Pure clean circular standoffs matching v20 geometry (r=3.8mm, OD=7.6mm).
                // All wing/bar gussets completely removed so all PCB sensors fit with zero collision!
                // Extends from PCB mount face (pcb_y_mount=3.5mm) deep through the dome wall (h=50.0mm).
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        
                        translate([x_pos, 0, z_pos]) {
                            rotate([-90, 0, 0]) {
                                translate([0, 0, pcb_y_mount])
                                    cylinder(r=3.8, h=50.0);
                            }
                        }
                    }
                }"""

if old_block in code:
    code = code.replace(old_block, new_block)
    print("Replaced standoff block successfully!")
else:
    print("Warning: old_block not found exactly, checking lines...")

# Also update counterbore depth to Y=18.0 for versatile M3x20~30mm screw compatibility
old_cb = """                        // Counterbore on front outer dome surface (depth ~6mm from outer surface)
                        // Leaves a massive 24.5mm solid threaded/clamping shoulder!
                        translate([0, 0, 28.0])
                            cylinder(r=3.4, h=45.0);"""

new_cb = """                        // Counterbore on front outer dome surface
                        // Leaves a rigid 14.5mm solid clamping shoulder (fits standard M3x20mm~30mm screws!)
                        translate([0, 0, 18.0])
                            cylinder(r=3.4, h=45.0);"""

if old_cb in code:
    code = code.replace(old_cb, new_cb)
    print("Updated counterbore depth successfully!")

with open(scad_path, "w", encoding="utf-8") as f:
    f.write(code)
print("Updated:", scad_path)
