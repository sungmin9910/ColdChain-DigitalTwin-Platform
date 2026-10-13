import subprocess
import os

scad_file = r'3D_Printer_Housing\v19_Apple_Sensor_Pod_5000mAh\19_apple_sensor_pod.scad'
img_file = r'C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520\scratch\rear_shell_inside.png'

cmd = [
    r'C:\Program Files\OpenSCAD\openscad.com',
    '-o', img_file,
    '--camera', '0,-10,5,65,0,215,280',
    '--imgsize', '1024,1024',
    '--colorscheme', 'Tomorrow Night',
    '-D', 'render_part="rear_shell"',
    scad_file
]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Done. Returncode:', res.returncode)
