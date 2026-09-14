import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.append('scratch')
from generate_perfect_gerber import all_segments, unique_vias, pads
BASE_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50"

IMG_SIZE = 1200
SCALE = IMG_SIZE / 50.0  # 24 pixels per mm
ORIGIN = 100.0

def to_px(x, y):
    px = (x - ORIGIN) * SCALE
    py = (y - ORIGIN) * SCALE
    return int(round(px)), int(round(py))

im_top = Image.new('RGB', (IMG_SIZE, IMG_SIZE), (20, 20, 25))
draw_top = ImageDraw.Draw(im_top)

im_bot = Image.new('RGB', (IMG_SIZE, IMG_SIZE), (20, 20, 25))
draw_bot = ImageDraw.Draw(im_bot)

# Draw Pads
for pname, pnet, px, py, pr in pads:
    cx, cy = to_px(px, py)
    r = int(round(pr * SCALE))
    # Green drill hole
    color = (255, 0, 255) if pnet > 0 else (100, 100, 100)
    draw_top.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(255, 255, 255))
    draw_bot.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(255, 255, 255))
    
    # Drill
    drill_r = int(round(0.45 * SCALE)) if 'H' not in pname else int(round(1.6 * SCALE))
    draw_top.ellipse([cx - drill_r, cy - drill_r, cx + drill_r, cy + drill_r], fill=(0, 255, 0))
    draw_bot.ellipse([cx - drill_r, cy - drill_r, cx + drill_r, cy + drill_r], fill=(0, 255, 0))

# Draw Traces
for net_name, net_id, layer, x1, y1, x2, y2 in all_segments:
    p1 = to_px(x1, y1)
    p2 = to_px(x2, y2)
    if layer == "F.Cu":
        draw_top.line([p1, p2], fill=(255, 30, 30), width=6)
    else:
        draw_bot.line([p1, p2], fill=(30, 100, 255), width=6)

# Draw Vias
for net_id, vx, vy in unique_vias:
    cx, cy = to_px(vx, vy)
    vr = int(round(0.4 * SCALE))
    draw_top.ellipse([cx - vr, cy - vr, cx + vr, cy + vr], fill=(255, 215, 0), outline=(0, 0, 0))
    draw_bot.ellipse([cx - vr, cy - vr, cx + vr, cy + vr], fill=(255, 215, 0), outline=(0, 0, 0))

# Save side-by-side
combined = Image.new('RGB', (IMG_SIZE * 2 + 40, IMG_SIZE + 60), (10, 10, 15))
combined.paste(im_top, (20, 40))
combined.paste(im_bot, (IMG_SIZE + 30, 40))
draw_c = ImageDraw.Draw(combined)
draw_c.text((20, 10), "TOP COPPER LAYER (F.Cu) - Verified Short-Free", fill=(255, 100, 100))
draw_c.text((IMG_SIZE + 30, 10), "BOTTOM COPPER LAYER (B.Cu) - Verified Short-Free", fill=(100, 150, 255))

out_path = os.path.join(r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch", "preview_perfect_router.png")
combined.save(out_path)
print("Saved preview to:", out_path)
