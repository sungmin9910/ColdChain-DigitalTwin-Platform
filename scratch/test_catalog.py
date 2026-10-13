import subprocess

cmd = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520\scratch\test_catalog_620.png",
    "-D", 'render_part="layout_catalog"',
    "--camera", "0,0,0,40,0,25,640",
    "--imgsize", "1200,1200",
    "--colorscheme", "Tomorrow Night",
    r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
]
subprocess.run(cmd)
print("Rendered test_catalog_620.png")
