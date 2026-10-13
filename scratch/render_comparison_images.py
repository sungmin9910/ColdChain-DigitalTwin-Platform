import subprocess, os

openscad = r"C:\Program Files\OpenSCAD\openscad.exe"
scad = r"3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

out_curr = os.path.join(artifact_dir, "print_orientation_current.png")
out_flipped = os.path.join(artifact_dir, "print_orientation_flipped.png")

# 1. Render Current Orientation
subprocess.run([
    openscad,
    "-o", out_curr,
    "-D", 'render_part="rear_shell"',
    "--imgsize=1000,800",
    "--autocenter",
    "--viewall",
    "--colorscheme=Nature",
    scad
], check=True)
print("Rendered current orientation.")

wrapper_scad = os.path.join(artifact_dir, "scratch", "flipped_wrapper.scad")
os.makedirs(os.path.dirname(wrapper_scad), exist_ok=True)
abs_scad = os.path.abspath(scad).replace("\\", "/")
with open(wrapper_scad, "w", encoding="utf-8") as f:
    f.write(f'''
include <{abs_scad}>;

// Flipped 180 deg
rotate([180, 0, 0])
rotate([-90, 0, 0])
apple_rear_shell();
''')

subprocess.run([
    openscad,
    "-o", out_flipped,
    "-D", 'render_part="none"',
    "--imgsize=1000,800",
    "--autocenter",
    "--viewall",
    "--colorscheme=DeepOcean",
    wrapper_scad
], check=True)
print("Rendered flipped orientation.")
