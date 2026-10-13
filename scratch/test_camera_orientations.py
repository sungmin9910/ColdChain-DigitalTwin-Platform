import subprocess

# Let's test different camera roll/angles to align exactly with user screenshot
# In user screenshot:
# Screw hole is at top center
# Vent hole is at top left
# Pillar goes straight down
# Cradle wall is to the right
# In test_new_boss_view.png, the pillar is angled at ~45 degrees.
# Let's try different rotZ / rotY / rotX to get it straight vertical.

cams = [
    ("rot1", "35,-15,24,65,35,175,80"),
    ("rot2", "35,-15,24,55,40,165,80"),
    ("rot3", "35,-15,24,60,30,190,80"),
    ("rot4", "35,-15,24,50,45,150,80"),
]

for name, cam in cams:
    img_path = f"scratch/test_{name}.png"
    cmd = [
        r"C:\Program Files\OpenSCAD\openscad.com",
        "-o", img_path,
        "--camera", cam,
        "--imgsize", "800,800",
        "--colorscheme", "Cornfield",
        "scratch/test_new_boss.scad"
    ]
    subprocess.run(cmd)

print("Done")
