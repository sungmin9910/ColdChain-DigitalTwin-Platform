import subprocess

# Let's render the unrotated apple_rear_shell() zoomed directly into the boss at X=35, Z=26 and X=-35, Z=26.
# In unrotated coordinates:
# Boss 1: X = 35, Y goes from 0 to -26, Z = 26
# Boss 2: X = -35, Y goes from 0 to -26, Z = 26
# In test_wall_boss_clean.png:
# Camera was at (0,0,0), rot=(65, 0, 210), dist=240.
# If we center camera at (35, -13, 26) with rot=(65, 0, 210) and dist=80:

cmd1 = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/zoom_boss_pos.png",
    "--camera", "35,-13,26,65,0,210,80",
    "--imgsize", "800,800",
    "--colorscheme", "Cornfield",
    "scratch/test_wall_boss.scad"
]
subprocess.run(cmd1)

cmd2 = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/zoom_boss_neg.png",
    "--camera", "-35,-13,26,65,0,210,80",
    "--imgsize", "800,800",
    "--colorscheme", "Cornfield",
    "scratch/test_wall_boss.scad"
]
subprocess.run(cmd2)

print("Rendered zoomed boss views")
