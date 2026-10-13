import os
import subprocess

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
test_scad = r"scratch\test_clean_assembly.scad"
output_png = r"scratch\test_clean_assembly_view.png"

# Read test_scad from previous step
with open(r"scratch\test_clean_standoffs.scad", "r", encoding="utf-8") as f:
    code = f.read()

# Change render_part to cross_section and assembly
code = code.replace('render_part = "part_front_shell";', 'render_part = "assembly";')

with open(test_scad, "w", encoding="utf-8") as f:
    f.write(code)

cmd = [
    openscad,
    "-o", output_png,
    "--camera=0,0,5,65,0,215,280",
    "--imgsize=1024,1024",
    "--colorscheme=Tomorrow Night",
    test_scad
]
subprocess.run(cmd, check=True)
print("Rendered:", output_png)

# Also render cross-section
output_cs_png = r"scratch\test_clean_cs_view.png"
code_cs = code.replace('render_part = "assembly";', 'render_part = "cross_section";')
with open(r"scratch\test_clean_cs.scad", "w", encoding="utf-8") as f:
    f.write(code_cs)

cmd2 = [
    openscad,
    "-o", output_cs_png,
    "--camera=0,0,5,65,0,45,280",
    "--imgsize=1024,1024",
    "--colorscheme=Tomorrow Night",
    r"scratch\test_clean_cs.scad"
]
subprocess.run(cmd2, check=True)
print("Rendered:", output_cs_png)
