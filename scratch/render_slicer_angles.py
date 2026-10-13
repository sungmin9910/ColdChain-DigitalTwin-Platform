import subprocess

# Let's render rear_shell in print orientation (sitting on bed at Z=0)
# from 4 different angles looking at the battery cradle area!
views = [
    ("v1", "0,0,25,60,0,45,160"),
    ("v2", "0,0,25,60,0,135,160"),
    ("v3", "0,0,25,60,0,225,160"),
    ("v4", "0,0,25,60,0,315,160"),
]

for name, cam in views:
    subprocess.run([
        r"C:\Program Files\OpenSCAD\openscad.com",
        "-o", f"scratch/slicer_cradle_{name}.png",
        "-D", 'render_part="rear_shell"',
        "--camera", cam,
        "--imgsize", "900,900",
        "--colorscheme", "Cornfield",
        r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
    ])

print("Done rendering 4 slicer cradle views")
