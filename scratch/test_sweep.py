import subprocess

# Let's test a sweep around (rotX=65, rotY=0, rotZ=210)
tests = [
    ("s1", "35,-15,22,65,0,180,80"),
    ("s2", "35,-15,22,65,0,230,80"),
    ("s3", "35,-15,22,50,0,200,80"),
    ("s4", "35,-15,22,75,0,220,80"),
]

for name, cam in tests:
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

print("Done sweep")
