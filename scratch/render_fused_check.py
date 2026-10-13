import subprocess
import os
import shutil

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
v21_dir = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v21_Apple_Sensor_Pod_2Piece5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\139db524-fcfc-4f20-aaa2-e61762915e57"
scad = os.path.join(v21_dir, "21_apple_sensor_pod.scad")

f_png = os.path.join(v21_dir, "21_front_shell_inside.png")
subprocess.run([
    openscad, "-o", f_png,
    "-D", 'render_part="part_front_shell"',
    "--camera", "0,0,5,65,0,0,220",
    "--imgsize", "1024,1024",
    "--colorscheme", "Cornfield",
    scad
])
shutil.copy2(f_png, os.path.join(artifact_dir, "21_front_shell_inside.png"))

# Also zoomed view looking at the standoff wall connection from side
zoom_png = os.path.join(v21_dir, "21_standoff_wall_zoom.png")
subprocess.run([
    openscad, "-o", zoom_png,
    "-D", 'render_part="part_front_shell"',
    "--camera", "20,15,20,65,0,320,120",
    "--imgsize", "1024,1024",
    "--colorscheme", "Cornfield",
    scad
])
shutil.copy2(zoom_png, os.path.join(artifact_dir, "21_standoff_wall_zoom.png"))

c_png = os.path.join(v21_dir, "21_cross_section_view.png")
subprocess.run([
    openscad, "-o", c_png,
    "-D", 'render_part="cross_section"',
    "--camera", "0,0,5,65,0,45,280",
    "--imgsize", "1024,1024",
    "--colorscheme", "Tomorrow Night",
    scad
])
shutil.copy2(c_png, os.path.join(artifact_dir, "21_cross_section_view.png"))

print("Rendered successfully!")
