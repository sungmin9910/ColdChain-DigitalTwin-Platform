import subprocess

openscad_path = r"C:\Program Files\OpenSCAD\openscad.exe"

# 1. Zoomed-in view of standoff
cmd1 = [
    openscad_path,
    "-o", "scratch/test_stepped_zoom.png",
    "-D", 'render_part="front_shell"',
    "--camera=-20,10,25,35,0,25,120",
    "--imgsize=1024,1024",
    "--colorscheme=DeepOcean",
    "scratch/test_stepped_housing.scad"
]
subprocess.run(cmd1, check=True)
print("Rendered test_stepped_zoom.png")

# 2. Inside view
cmd2 = [
    openscad_path,
    "-o", "scratch/test_stepped_inside.png",
    "-D", 'render_part="front_shell"',
    "--camera=0,-70,3,0,0,0,140",
    "--imgsize=1024,1024",
    "--colorscheme=Solarized",
    "scratch/test_stepped_housing.scad"
]
subprocess.run(cmd2, check=True)
print("Rendered test_stepped_inside.png")

# 3. Cross-section view with PCB
cmd3 = [
    openscad_path,
    "-o", "scratch/test_stepped_cross.png",
    "-D", 'render_part="cross_section"',
    "--camera=-50,-80,20,15,30,-50,220",
    "--imgsize=1024,1024",
    "--colorscheme=Metallic",
    "scratch/test_stepped_housing.scad"
]
subprocess.run(cmd3, check=True)
print("Rendered test_stepped_cross.png")
