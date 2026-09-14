import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50"
GERBER_DIR = os.path.join(BASE_DIR, "gerber_temp")

def parse_gerber_lines(filepath):
    lines = []
    x, y = 0, 0
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('G01X') or line.startswith('X'):
                # Extract X and Y
                # Format: G01X00115790Y00127500D01*
                import re
                m = re.search(r'X(\d+)Y(\d+)D(\d+)', line)
                if m:
                    nx = int(m.group(1)) / 100000.0
                    ny = int(m.group(2)) / 100000.0
                    d = int(m.group(3))
                    if d == 1: # draw line from (x, y) to (nx, ny)
                        lines.append((x, y, nx, ny))
                    x, y = nx, ny
    return lines

bot_copper_lines = parse_gerber_lines(os.path.join(GERBER_DIR, "Gerber_BottomCopperLayer.GBL"))
bot_silk_lines = parse_gerber_lines(os.path.join(GERBER_DIR, "Gerber_BottomSilkscreenLayer.GBO"))

print(f"Parsed {len(bot_copper_lines)} copper trace segments and {len(bot_silk_lines)} silkscreen segments from actual Gerber files.")

# Render zoomed in on SHT45 (X: 100 to 125, Y: 120 to 142)
fig, ax = plt.subplots(figsize=(10, 6), dpi=250)
ax.set_facecolor('#121518')
ax.set_title("ZOOMED-IN ACTUAL GERBER PARSED: SHT45 AREA (B.Cu + B.SilkS)", color='white', fontsize=12, fontweight='bold', pad=10)
ax.set_xlim(100, 126)
ax.set_ylim(120, 143)
ax.set_aspect('equal')
ax.grid(True, color='#1f242b', linestyle=':', alpha=0.6)

# Silk lines in yellow
for x1, y1, x2, y2 in bot_silk_lines:
    ax.plot([x1, x2], [y1, y2], color='#ffea00', linewidth=1.2, alpha=0.95)

# Copper lines in blue
for x1, y1, x2, y2 in bot_copper_lines:
    ax.plot([x1, x2], [y1, y2], color='#0077ff', linewidth=3.0, solid_capstyle='round')

# Draw pads for SHT45
pads_sht = [
    (108.17, 127.50, True),  # Pin 1
    (110.71, 127.50, False), # Pin 2
    (113.25, 127.50, False), # Pin 3
    (115.79, 127.50, False), # Pin 4
    (118.33, 127.50, False), # Pin 5
]
for px, py, is_rect in pads_sht:
    if is_rect:
        rect = patches.Rectangle((px - 0.8, py - 0.8), 1.6, 1.6, facecolor='#0044ff', edgecolor='#00ff66', linewidth=1.2, zorder=5)
        ax.add_patch(rect)
    else:
        c = plt.Circle((px, py), 0.8, facecolor='#0044ff', edgecolor='#00ff66', linewidth=1.2, zorder=5)
        ax.add_patch(c)
    c2 = plt.Circle((px, py), 0.45, facecolor='#00ff66', zorder=6)
    ax.add_patch(c2)

out_img = r"C:\Users\korea\.gemini\antigravity-ide\brain\8cc94666-3a79-4076-a473-a6dc3e8746a0\preview_actual_gerber_sht45.png"
plt.savefig(out_img, bbox_inches='tight')
plt.close()
print(f"Saved actual gerber SHT45 zoom preview: {out_img}")
