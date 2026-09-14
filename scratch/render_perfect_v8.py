import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6), dpi=150)

PCB_COLOR = '#1b4d2e'
PAD_COLOR = '#d4af37'
HOLE_PAD_COLOR = '#b0b0b0'

# Case 2 Layout Coordinates:
# 1. Beetle C6 (Top, Bottom-Center):
#    X in [114.75, 135.25], Y in [100.0, 125.0]
#    Left pins: X = 116.11, Y in [102.66, 120.44]
#    Right pins: X = 133.89, Y in [102.66, 120.44]
# 2. GPS ATGM336H (Bottom, Left-Wing):
#    Module: 13.1 x 15.7 mm. X in [100.8, 113.9], Y in [107.5, 123.2]
#    Header: 1x05 horizontal at Y = 109.5, X in [102.5, 112.66]
# 3. BH1750 (Top, Right-Wing):
#    Module: 13.9 x 18.5 mm. X in [135.8, 149.7], Y in [107.0, 125.5]
#    Header: 1x05 horizontal at Y = 123.5, X in [137.5, 147.66]
# 4. SHT45 (Bottom, Top-Left):
#    Module: 25.5 x 17.8 mm. X in [100.5, 126.0], Y in [125.5, 143.3]
#    Header: 1x05 horizontal at Y = 127.5, X in [108.17, 118.33]
# 5. GY-521 (Bottom, Top-Right):
#    Module: 20.7 x 15.65 mm. X in [128.5, 149.2], Y in [125.5, 141.15]
#    Header: 1x08 horizontal at Y = 127.5, X in [129.5, 147.28]
# 6. JST-PH & SW1 (Top, Top-Center):
#    JST-PH: X in [120.0, 126.0], Y in [144.5, 149.0]
#    SW1: X in [112.5, 119.5], Y in [144.5, 148.5]

for ax, title in [(ax1, "1. TOP SIDE (Front View)"), (ax2, "2. BOTTOM SIDE (Back View)"), (ax3, "3. OVERLAID PROJECTION (Front + Back)")]:
    ax.set_xlim(98, 152)
    ax.set_ylim(98, 152)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=12, fontweight='bold', pad=12)
    
    # Board outline
    poly = patches.Polygon([
        (102, 100), (148, 100), (150, 102), (150, 148),
        (148, 150), (102, 150), (100, 148), (100, 102)
    ], closed=True, facecolor=PCB_COLOR, edgecolor='#0f2b1a', lw=2)
    ax.add_patch(poly)
    
    # M3 mounting holes
    for hx, hy in [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]:
        ax.add_patch(patches.Circle((hx, hy), 2.75, facecolor=HOLE_PAD_COLOR, edgecolor='#404040', lw=1))
        ax.add_patch(patches.Circle((hx, hy), 1.6, facecolor='#101010', edgecolor='none'))

def draw_top(ax, alpha=0.85):
    # Beetle C6
    ax.add_patch(patches.Rectangle((114.75, 100.0), 20.5, 25.0, facecolor='#2a4d69', edgecolor='white', lw=1.5, alpha=alpha))
    ax.text(125.0, 115.0, 'Beetle ESP32-C6\n(20.5 x 25.0mm)', color='white', ha='center', va='center', fontsize=8, fontweight='bold')
    ax.add_patch(patches.Rectangle((120.5, 100.0), 9.0, 3.5, facecolor='#d0d0d0', edgecolor='white', lw=1))
    ax.text(125.0, 101.75, 'USB-C', color='black', ha='center', va='center', fontsize=6)
    
    # Beetle Sockets
    for y in [102.66 + i*2.54 for i in range(8)]:
        ax.add_patch(patches.Circle((116.11, y), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
        ax.add_patch(patches.Circle((133.89, y), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
    ax.add_patch(patches.Rectangle((116.11 - 1.27, 102.66 - 1.27), 2.54, 17.78 + 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))
    ax.add_patch(patches.Rectangle((133.89 - 1.27, 102.66 - 1.27), 2.54, 17.78 + 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

    # BH1750 (Top, Right Wing)
    ax.add_patch(patches.Rectangle((135.8, 106.7), 13.9, 18.5, facecolor='#f39c12', edgecolor='yellow', lw=1.5, alpha=alpha))
    ax.text(142.75, 114.5, 'BH1750\n(13.9x18.5)', color='black', ha='center', va='center', fontsize=7, fontweight='bold')
    for x in [137.67 + i*2.54 for i in range(5)]:
        ax.add_patch(patches.Circle((x, 123.2), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
    ax.add_patch(patches.Rectangle((137.67 - 1.27, 123.2 - 1.27), 10.16 + 2.54, 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

    # JST-PH & SW1
    ax.add_patch(patches.Rectangle((120.0, 144.5), 6.0, 4.5, facecolor='#ffffff', edgecolor='black', lw=1))
    ax.text(123.0, 146.75, 'JST', color='black', ha='center', va='center', fontsize=6)
    ax.add_patch(patches.Rectangle((112.5, 144.5), 7.0, 4.0, facecolor='#444444', edgecolor='white', lw=1))
    ax.text(116.0, 146.5, 'SW1', color='white', ha='center', va='center', fontsize=6)

def draw_bottom(ax, alpha=0.85):
    # GPS (Bottom, Left Wing)
    ax.add_patch(patches.Rectangle((100.8, 107.5), 13.1, 15.7, facecolor='#00b894', edgecolor='lightgreen', lw=1.5, alpha=alpha))
    ax.text(107.35, 117.0, 'ATGM336H\n(13.1x15.7)', color='white', ha='center', va='center', fontsize=7, fontweight='bold')
    for x in [102.33 + i*2.54 for i in range(5)]:
        ax.add_patch(patches.Circle((x, 109.5), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
    ax.add_patch(patches.Rectangle((102.33 - 1.27, 109.5 - 1.27), 10.16 + 2.54, 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

    # SHT45 (Bottom, Top-Left)
    ax.add_patch(patches.Rectangle((100.5, 125.5), 25.5, 17.8, facecolor='#6c5ce7', edgecolor='cyan', lw=1.5, alpha=alpha))
    ax.text(113.25, 136.0, 'SHT45 Qwiic\n(25.5 x 17.8mm)', color='white', ha='center', va='center', fontsize=7.5, fontweight='bold')
    for x in [108.17 + i*2.54 for i in range(5)]:
        ax.add_patch(patches.Circle((x, 127.5), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
    ax.add_patch(patches.Rectangle((108.17 - 1.27, 127.5 - 1.27), 10.16 + 2.54, 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

    # GY-521 (Bottom, Top-Right)
    ax.add_patch(patches.Rectangle((128.5, 125.5), 20.7, 15.65, facecolor='#d63031', edgecolor='orange', lw=1.5, alpha=alpha))
    ax.text(138.85, 136.0, 'GY-521 IMU\n(20.7x15.65)', color='white', ha='center', va='center', fontsize=7.5, fontweight='bold')
    for x in [129.56 + i*2.54 for i in range(8)]:
        ax.add_patch(patches.Circle((x, 127.5), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
    ax.add_patch(patches.Rectangle((129.56 - 1.27, 127.5 - 1.27), 17.78 + 2.54, 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

    # Clean Keepout under Beetle C6
    ax.add_patch(patches.Rectangle((114.75, 100.0), 20.5, 25.0, facecolor='#153520', edgecolor='#555555', lw=1, ls=':'))
    ax.text(125.0, 112.5, '[Clean Keepout]\n(0 Pins under Beetle)', color='#88cc88', ha='center', va='center', fontsize=7, fontweight='bold')

draw_top(ax1)
draw_bottom(ax2)

# Overlaid View (semi-transparent)
draw_top(ax3, alpha=0.5)
draw_bottom(ax3, alpha=0.5)
ax3.text(125.0, 101.75, 'USB-C', color='black', ha='center', va='center', fontsize=6)

plt.tight_layout()
out_png = 'scratch/preview_zero_overlap_v8.png'
plt.savefig(out_png, dpi=150)
print(f"Generated v8 zero-overlap preview: {out_png}")
