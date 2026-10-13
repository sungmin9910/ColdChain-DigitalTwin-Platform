import subprocess

# Render the exact match view to compare before and after
# The user's photo shows the top-right boss (X=35, Z=26)
# with the vent hole at the top-left and cradle wall at the right.
# Let's render the fixed model and the old model from this exact view.

cmd_fixed = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/compare_after_fixed.png",
    "--camera", "35,-15,22,65,0,230,80",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    "scratch/test_continuous.scad"
]
subprocess.run(cmd_fixed)

cmd_old = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/compare_before_old.png",
    "--camera", "35,-15,22,65,0,230,80",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    "scratch/test_wall_boss.scad"
]
subprocess.run(cmd_old)

print("Rendered before and after comparison images")
