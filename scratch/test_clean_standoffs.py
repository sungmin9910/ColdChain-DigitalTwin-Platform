import os
import subprocess

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
test_scad = r"scratch\test_clean_standoffs.scad"
output_png = r"scratch\test_clean_standoffs_view.png"

# Read 21_apple_sensor_pod.scad
with open(r"3D_Printer_Housing\v21_Apple_Sensor_Pod_2Piece5000mAh\21_apple_sensor_pod.scad", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the standoff section with pure cylindrical pillars (NO wings!)
old_standoff = """                // 3) 4x INTEGRATED PCB MOUNTING STANDOFFS (100% WALL-FUSED, ZERO GAP!)
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

new_standoff = """                // 3) 4x INTEGRATED PCB MOUNTING STANDOFFS (PURE CYLINDRICAL PILLARS, ZERO WINGS!)
                // Pure clean circular standoffs matching v20 sensor clearance (r=3.8mm, OD=7.6mm)
                for (dx = [-1, 1]) {
                    for (dz = [-1, 1]) {
                        x_pos = dx * (hole_pitch / 2);
                        z_pos = pcb_z_center + dz * (hole_pitch / 2);
                        
                        translate([x_pos, 0, z_pos]) {
                            rotate([-90, 0, 0]) {
                                // Pure cylindrical pillar extending from PCB mount face (pcb_y_mount=3.5)
                                // deep through the dome wall (h=50.0mm). 100% solid & wall-fused, zero wings!
                                translate([0, 0, pcb_y_mount])
                                    cylinder(r=3.8, h=50.0);
                            }
                        }
                    }
                }"""

assert old_standoff in code, "Old standoff block not found!"
test_code = code.replace(old_standoff, new_standoff)
test_code = test_code.replace('render_part = "assembly";', 'render_part = "part_front_shell";')

with open(test_scad, "w", encoding="utf-8") as f:
    f.write(test_code)

# Render inside view
cmd = [
    openscad,
    "-o", output_png,
    "--camera=0,0,5,65,0,0,220",
    "--imgsize=1024,1024",
    "--colorscheme=Cornfield",
    test_scad
]
subprocess.run(cmd, check=True)
print("Rendered:", output_png)
