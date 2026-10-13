import subprocess
import os

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# Let's read 20_apple_sensor_pod.scad and enhance it with wide exploded view and catalog layout
with open(scad_file, "r", encoding="utf-8") as f:
    content = f.read()

# Let's inspect what render_part branches exist
print("Read scad file, size:", len(content))
