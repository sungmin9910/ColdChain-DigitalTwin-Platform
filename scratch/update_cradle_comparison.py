import subprocess
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

# 1. Update the main inspection renders
print("1. Updating renders...")
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_cross_section_view.png"), "-D", 'render_part="cross_section"', "--camera", "0,0,5,65,0,45,280", "--imgsize", "1024,1024", "--colorscheme", "Tomorrow Night", scad_file])
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_assembly_view.png"), "-D", 'render_part="assembly"', "--camera", "0,0,5,65,0,35,280", "--imgsize", "1024,1024", "--colorscheme", "Tomorrow Night", scad_file])
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_exploded_view_front.png"), "-D", 'render_part="exploded_wide"', "--camera", "0,0,0,60,0,215,680", "--imgsize", "1200,1200", "--colorscheme", "Tomorrow Night", scad_file])
shutil.copy(os.path.join(housing_dir, "20_exploded_view_front.png"), os.path.join(housing_dir, "20_exploded_view.png"))
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_detail_1_rear_shell.png"), "-D", 'render_part="part_rear_shell"', "--camera", "0,0,0,65,0,210,240", "--imgsize", "1000,1000", "--colorscheme", "Tomorrow Night", scad_file])

# 2. Render cradle bottom comparison
print("2. Generating Cradle Comparison...")
before_cradle = r"scratch\cradle_view_cad_bottom.png"
after_cradle = r"scratch\cradle_bottom_after.png"

# Render exact matching view on new model
subprocess.run([
    openscad,
    "-o", after_cradle,
    "-D", 'render_part="part_rear_shell"',
    "--camera", "0,0,-20,60,0,180,180",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    scad_file
])

img_b = Image.open(before_cradle).convert("RGB").resize((700, 700))
img_a = Image.open(after_cradle).convert("RGB").resize((700, 700))

combined = Image.new("RGB", (1440, 780), color=(24, 26, 27))
combined.paste(img_b, (15, 65))
combined.paste(img_a, (725, 65))

draw = ImageDraw.Draw(combined)
try:
    font_title = ImageFont.truetype("malgun.ttf", 24)
except:
    font_title = ImageFont.load_default()

draw.text((70, 20), "[수정 전] 배터리 안착부 하단이 공중에 뜸 (아치형 공중 틈새 발생)", fill=(255, 90, 90), font=font_title)
draw.text((780, 20), "[수정 후] 배터리 안착부 하단 및 바닥 외벽 100% 밀착 일체화 (틈새 제거)", fill=(80, 230, 110), font=font_title)

comp_out = os.path.join(housing_dir, "20_cradle_bottom_fix_comparison.png")
combined.save(comp_out)
shutil.copy(comp_out, os.path.join(artifact_dir, "20_cradle_bottom_fix_comparison.png"))

# Copy all pngs to artifact dir
for f in os.listdir(housing_dir):
    if f.endswith(".png"):
        shutil.copy(os.path.join(housing_dir, f), os.path.join(artifact_dir, f))

print("All updated and comparison saved!")
