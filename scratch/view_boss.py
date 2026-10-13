import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
img_path = r"scratch\test_view_inside.png"

# We want to view rear shell inside, looking at the boss.
# Notice rear_shell module has rotate([-90,0,0]) apple_rear_shell().
# Let's render directly apple_rear_shell() unrotated or rear_shell rotated.
# If rotated [-90,0,0]:
# X is X, Y is Z, Z is -Y (Z is depth into dome, from 0 to 45).
# So the boss is at X=35, Y=26, Z=0 to 26!
# Camera looking at (35, 26, 15) from slightly above and inside.
cmd = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", img_path,
    "-D", 'render_part="rear_shell"',
    "--camera", "20,15,35,45,0,220,100",
    "--imgsize", "800,800",
    "--colorscheme", "Cornfield",
    scad_file
]
subprocess.run(cmd)
print("Rendered test_view_inside.png")
