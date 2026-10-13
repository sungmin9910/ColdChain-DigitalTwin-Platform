import subprocess

cams = [
    ("v_rot1", "35,-15,24,65,35,85,80"),
    ("v_rot2", "35,-15,24,35,65,100,80"),
    ("v_rot3", "35,-15,24,55,50,90,80"),
    ("v_rot4", "35,-15,24,70,25,95,80"),
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
