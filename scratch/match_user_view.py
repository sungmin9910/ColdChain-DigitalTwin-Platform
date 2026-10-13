import subprocess

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
img_path = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520\scratch\match_user_screenshot.png"

cmd = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", img_path,
    "-D", 'render_part="rear_shell"',
    "--camera", "20,-10,20,65,0,195,150",
    "--imgsize", "1000,1000",
    "--colorscheme", "Cornfield",
    scad_file
]
subprocess.run(cmd)
print("Rendered match_user_screenshot.png")
