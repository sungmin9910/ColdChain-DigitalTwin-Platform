import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# Boss is at (35, 26). Parting plane is at Z=0.
# The user's photo looks from inside the shell cavity towards (35, 26), 
# looking from Z = 30..40 towards Z = 0? Or looking from Z = -20 towards Z = 20?
# Notice: the top of the pillar has the hole, and the pillar extends into the cavity!
# Wait, where is the screw hole? The screw hole is at the parting plane Z'=0!
# If the screw hole is at Z'=0, in the user photo the screw hole is at the top of the photo!
# And the pillar goes down deeper into the cavity!
# And at the end of the pillar (Z' = 26), the pillar ends with a flat bottom!
# So the camera is at roughly X=15, Y=10, looking towards (35, 26, 15) with camera elevated!

cams = [
    ("m1", "30,22,15,45,0,-120,90"),
    ("m2", "25,18,15,55,0,-135,100"),
    ("m3", "20,15,10,50,0,-140,110"),
    ("m4", "25,20,10,35,0,-130,120"),
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
