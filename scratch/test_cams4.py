import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# Target point: the pillar top/mid at (35, 26, 12)
# We want the camera to be INSIDE the cavity, e.g. at (0, 0, -20) looking towards (35, 26, 12)?
# Note that rear_shell is rotate([-90,0,0]) apple_rear_shell().
# Let's inspect the coordinate system of rear_shell:
# The cavity is at Z > 0 (inside the bowl).
# Boss is at X=35, Y=26, Z in [0, 26].
# The user photo is looking at the pillar from INSIDE the bowl, looking upwards and towards the wall!
# That means camera is inside the bowl, say at (10, 0, 30), looking towards (35, 26, 10).
# In OpenSCAD:
# camera translation is the target point: transX=35, transY=26, transZ=10.
# The camera looks AT (transX, transY, transZ).
# The rotation rotX, rotY, rotZ defines the direction from which the camera looks!
# If rotX=0, rotZ=0: camera is directly above (+Z) looking down at the target.
# If rotX=90, rotZ=0: camera is at +Y looking towards -Y.
# If rotX=90, rotZ=90: camera is at -X looking towards +X.
# We want camera to be at negative X, negative Y relative to target (35, 26), 
# and above target in Z (looking down towards the bed/parting plane Z=0)!
# Vector from target to camera: (-dx, -dy, +dz).
# Azimuth angle from +Y towards -X is around rotZ = 45 to 60.
# Elevation angle rotX: around 50 to 70.

cams = [
    ("ang1", "33,24,12,65,0,50,75"),
    ("ang2", "33,24,12,55,0,45,70"),
    ("ang3", "33,24,12,60,0,30,80"),
    ("ang4", "33,24,12,70,0,60,75"),
]

for name, cam in cams:
    img_path = f"scratch/test_{name}.png"
    cmd = [
        r"C:\Program Files\OpenSCAD\openscad.com",
        "-o", img_path,
        "-D", 'render_part="rear_shell"',
        "--camera", cam,
        "--imgsize", "800,800",
        "--colorscheme", "Cornfield",
        scad_file
    ]
    subprocess.run(cmd)

print("Done")
