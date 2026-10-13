import subprocess
import os

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh"

jobs_stl = [
    ("rear_shell", "20_apple_rear_shell.stl"),
    ("battery_tray", "20_apple_battery_tray.stl"),
    ("front_shell", "20_apple_front_shell.stl"),
    ("stem", "20_apple_stem.stl")
]

print("=== Re-Exporting All STLs Pre-Oriented Flat on Print Bed ===")
for name, out in jobs_stl:
    out_path = os.path.join(housing_dir, out)
    cmd = [
        openscad,
        "-o", out_path,
        "-D", f'render_part="{name}"',
        scad
    ]
    print(f"Exporting {name} -> {out} ...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Exported {name} -> {out}: exit code {res.returncode}")

print("\nRe-export completed successfully!")
