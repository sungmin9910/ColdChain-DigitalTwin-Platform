import subprocess

openscad = r"C:\Program Files\OpenSCAD\openscad.com"

# 1. Zoom
subprocess.run([
    openscad, "-o", "scratch/stepped_zoom_correct.png",
    "-D", 'render_part="part_front_shell"',
    "--camera=20,15,20,65,0,320,120",
    "--imgsize=1024,1024",
    "--colorscheme=Cornfield",
    "scratch/test_stepped_housing.scad"
], check=True)

# 2. Inside view
subprocess.run([
    openscad, "-o", "scratch/stepped_inside_correct.png",
    "-D", 'render_part="part_front_shell"',
    "--camera=0,0,5,65,0,0,220",
    "--imgsize=1024,1024",
    "--colorscheme=Cornfield",
    "scratch/test_stepped_housing.scad"
], check=True)

# 3. Cross section
subprocess.run([
    openscad, "-o", "scratch/stepped_cross_correct.png",
    "-D", 'render_part="cross_section"',
    "--camera=0,0,5,65,0,45,280",
    "--imgsize=1024,1024",
    "--colorscheme=Tomorrow Night",
    "scratch/test_stepped_housing.scad"
], check=True)

print("Rendered all 3 stepped images!")
