import subprocess
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"
housing_dir = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

print("1. Rendering main assembly and exploded views...")
# Assembly & Cross section
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_cross_section_view.png"), "-D", 'render_part="cross_section"', "--camera", "0,0,5,65,0,45,280", "--imgsize", "1024,1024", "--colorscheme", "Tomorrow Night", scad_file])
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_assembly_view.png"), "-D", 'render_part="assembly"', "--camera", "0,0,5,65,0,35,280", "--imgsize", "1024,1024", "--colorscheme", "Tomorrow Night", scad_file])

# Exploded
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_exploded_view_front.png"), "-D", 'render_part="exploded_wide"', "--camera", "0,0,0,60,0,215,680", "--imgsize", "1200,1200", "--colorscheme", "Tomorrow Night", scad_file])
shutil.copy(os.path.join(housing_dir, "20_exploded_view_front.png"), os.path.join(housing_dir, "20_exploded_view.png"))

# Details
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_detail_1_rear_shell.png"), "-D", 'render_part="part_rear_shell"', "--camera", "0,0,0,65,0,210,240", "--imgsize", "1000,1000", "--colorscheme", "Tomorrow Night", scad_file])
subprocess.run([openscad, "-o", os.path.join(housing_dir, "20_detail_5_front_shell.png"), "-D", 'render_part="part_front_shell"', "--camera", "0,0,0,65,0,30,240", "--imgsize", "1000,1000", "--colorscheme", "Tomorrow Night", scad_file])

print("2. Rendering Boss Close-Ups in Slicer Theme (Cornfield)...")
boss_rear_fixed = os.path.join(housing_dir, "20_boss_rear_wall_close.png")
subprocess.run([openscad, "-o", boss_rear_fixed, "-D", 'render_part="part_rear_shell"', "--camera", "35,-15,22,65,0,230,75", "--imgsize", "1000,1000", "--colorscheme", "Cornfield", scad_file])

boss_front_fixed = os.path.join(housing_dir, "20_boss_front_wall_close.png")
subprocess.run([openscad, "-o", boss_front_fixed, "-D", 'render_part="part_front_shell"', "--camera", "35,15,22,65,0,50,75", "--imgsize", "1000,1000", "--colorscheme", "Cornfield", scad_file])

print("3. Generating Side-by-Side Comparison...")
# Render Old vs Fixed from the exact angle of user photo
old_img_path = r"scratch\compare_before_old.png"
fixed_img_path = os.path.join(housing_dir, "20_boss_rear_wall_close.png")

if os.path.exists(old_img_path) and os.path.exists(fixed_img_path):
    img_before = Image.open(old_img_path).convert("RGB").resize((700, 700))
    img_after = Image.open(fixed_img_path).convert("RGB").resize((700, 700))
    
    # Combined canvas: 1440 x 780
    combined = Image.new("RGB", (1440, 780), color=(24, 26, 27))
    draw = ImageDraw.Draw(combined)
    
    # Paste images
    combined.paste(img_before, (20, 60))
    combined.paste(img_after, (720, 60))
    
    # Text banners
    try:
        font_title = ImageFont.truetype("malgun.ttf", 26)
        font_sub = ImageFont.truetype("malgun.ttf", 20)
    except:
        font_title = font_sub = ImageFont.load_default()
        
    draw.text((150, 15), "[수정 전] 나사 기둥 끝단이 공중에 뜸 (Overhang Step)", fill=(255, 90, 90), font=font_title)
    draw.text((850, 15), "[수정 후] 외벽에 100% 밀착 일체화 (Zero Overhang)", fill=(80, 220, 100), font=font_title)
    
    comp_path = os.path.join(housing_dir, "20_boss_fix_comparison.png")
    combined.save(comp_path)
    shutil.copy(comp_path, os.path.join(artifact_dir, "20_boss_fix_comparison.png"))
    print(f"Saved side-by-side comparison to {comp_path}")

# Copy all housing pngs to artifact dir
for f in os.listdir(housing_dir):
    if f.endswith(".png"):
        shutil.copy(os.path.join(housing_dir, f), os.path.join(artifact_dir, f))

print("All renders and artifacts updated successfully!")
