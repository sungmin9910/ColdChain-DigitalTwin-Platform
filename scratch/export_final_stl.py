import subprocess
import os

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
v21_dir = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v21_Apple_Sensor_Pod_2Piece5000mAh"
scad = os.path.join(v21_dir, "21_apple_sensor_pod.scad")
front_stl = os.path.join(v21_dir, "21_apple_front_shell.stl")

print("Exporting 21_apple_front_shell.stl with wall-fused standoffs...")
res = subprocess.run([
    openscad, "-o", front_stl,
    "-D", 'render_part="front_shell"',
    scad
], capture_output=True, text=True)

if res.returncode == 0:
    sz = os.path.getsize(front_stl) / 1024
    print(f"Export SUCCESS! Size: {sz:.1f} KB")
else:
    print(f"Export FAILED:\n{res.stderr}")
