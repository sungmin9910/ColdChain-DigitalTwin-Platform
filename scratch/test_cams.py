import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# Let's test a few camera angles to find the exact one matching the user photo
views = [
    ("view1", "0,10,0,60,0,135,130"),
    ("view2", "15,10,5,55,0,145,110"),
    ("view3", "10,5,10,50,0,160,95"),
    ("view4", "5,15,10,40,0,130,90"),
]

for name, cam in views:
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

print("Done rendering test views")
