import subprocess
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh"
artifact_dir = r"C:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform"

# Let's create a temporary scad that calls apple_rear_shell() unrotated
temp_scad = r'''
use <../3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad>
color([0.88, 0.18, 0.18]) apple_rear_shell();
'''
with open("scratch/temp_rear.scad", "w") as f:
    f.write(temp_scad)

after_img = r"scratch\compare_after_fixed_exact.png"
subprocess.run([
    openscad,
    "-o", after_img,
    "--camera", "35,-15,22,65,0,230,80",
    "--imgsize", "900,900",
    "--colorscheme", "Cornfield",
    "scratch/temp_rear.scad"
])

before_img = r"scratch\compare_before_old.png"

img_b = Image.open(before_img).convert("RGB").resize((700, 700))
img_a = Image.open(after_img).convert("RGB").resize((700, 700))

combined = Image.new("RGB", (1440, 780), color=(24, 26, 27))
combined.paste(img_b, (15, 65))
combined.paste(img_a, (725, 65))

draw = ImageDraw.Draw(combined)
try:
    font_title = ImageFont.truetype("malgun.ttf", 24)
except:
    font_title = ImageFont.load_default()

draw.text((80, 20), "[수정 전] 기둥 하단이 공중에 떠서 단차 발생 (Floating Step)", fill=(255, 90, 90), font=font_title)
draw.text((790, 20), "[수정 후] 기둥이 외벽 곡면으로 100% 밀착 일체화 (벽면에 부착)", fill=(80, 230, 110), font=font_title)

out_comp = os.path.join(housing_dir, "20_boss_fix_comparison.png")
combined.save(out_comp)
artifact_comp = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520\20_boss_fix_comparison.png"
shutil.copy(out_comp, artifact_comp)
print("Updated 20_boss_fix_comparison.png successfully!")
