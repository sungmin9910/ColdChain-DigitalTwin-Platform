import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create side-by-side plot of Top side and Bottom side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), dpi=150)

PCB_COLOR = '#1b4d2e'
PAD_COLOR = '#d4af37'
HOLE_PAD_COLOR = '#b0b0b0'

for ax, title in [(ax1, "TOP SIDE (Front View)"), (ax2, "BOTTOM SIDE (Back View)")]:
    ax.set_xlim(98, 152)
    ax.set_ylim(98, 152)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    
    # Board outline
    poly = patches.Polygon([
        (102, 100), (148, 100), (150, 102), (150, 148),
        (148, 150), (102, 150), (100, 148), (100, 102)
    ], closed=True, facecolor=PCB_COLOR, edgecolor='#0f2b1a', lw=2)
    ax.add_patch(poly)
    
    # M3 mounting holes (diameter 5.5mm pad, 3.2mm drill)
    for hx, hy in [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]:
        ax.add_patch(patches.Circle((hx, hy), 2.75, facecolor=HOLE_PAD_COLOR, edgecolor='#404040', lw=1))
        ax.add_patch(patches.Circle((hx, hy), 1.6, facecolor='#101010', edgecolor='none'))

# ==========================================
# --- TOP SIDE ---
# ==========================================
# 1. Beetle C6 (Top, Bottom-Center)
ax1.add_patch(patches.Rectangle((114.75, 100.0), 20.5, 25.0, facecolor='#2a4d69', edgecolor='white', lw=1.5, alpha=0.75))
ax1.text(125.0, 115.0, 'Beetle ESP32-C6\n(20.5 x 25.0mm)', color='white', ha='center', va='center', fontsize=9, fontweight='bold')
# USB-C Cutout
ax1.add_patch(patches.Rectangle((120.5, 100.0), 9.0, 3.5, facecolor='#d0d0d0', edgecolor='white', lw=1))
ax1.text(125.0, 101.75, 'USB-C (Flush)', color='black', ha='center', va='center', fontsize=7)

# MCU Female Sockets (Top)
for y in [102.66 + i*2.54 for i in range(8)]:
    ax1.add_patch(patches.Circle((116.11, y), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
    ax1.add_patch(patches.Circle((133.89, y), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
# Female Socket Plastic Housing (2.54mm wide)
ax1.add_patch(patches.Rectangle((116.11 - 1.27, 102.66 - 1.27), 2.54, 17.78 + 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))
ax1.add_patch(patches.Rectangle((133.89 - 1.27, 102.66 - 1.27), 2.54, 17.78 + 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

# 2. BH1750 (Top, Top-Right)
ax1.add_patch(patches.Rectangle((128.63, 127.5), 13.9, 18.5, facecolor='#336699', edgecolor='yellow', lw=1.5, alpha=0.75))
ax1.text(135.58, 136.0, 'BH1750 (GY-302)\n13.9 x 18.5mm', color='white', ha='center', va='center', fontsize=8, fontweight='bold')
# BH1750 Female Socket
for x in [130.5 + i*2.54 for i in range(5)]:
    ax1.add_patch(patches.Circle((x, 144.5), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
ax1.add_patch(patches.Rectangle((130.5 - 1.27, 144.5 - 1.27), 10.16 + 2.54, 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

# 3. JST-PH and SW1 (Top, Center)
ax1.add_patch(patches.Rectangle((119.0, 144.5), 6.0, 4.5, facecolor='#ffffff', edgecolor='black', lw=1))
ax1.text(122.0, 146.75, 'JST-PH', color='black', ha='center', va='center', fontsize=6)
ax1.add_patch(patches.Rectangle((118.5, 137.0), 7.0, 4.0, facecolor='#444444', edgecolor='white', lw=1))
ax1.text(122.0, 139.0, 'SW1', color='white', ha='center', va='center', fontsize=6)

# ==========================================
# --- BOTTOM SIDE ---
# ==========================================
# 1. SHT45 (Bottom, Top-Left) - COMPLETELY CLEARS M3 HOLE (Y_max = 143.3 < 143.75)
ax2.add_patch(patches.Rectangle((100.5, 125.5), 25.5, 17.8, facecolor='#6c5ce7', edgecolor='cyan', lw=1.5, alpha=0.75))
ax2.text(113.25, 136.0, 'SHT45 Qwiic\n(25.5 x 17.8mm)', color='white', ha='center', va='center', fontsize=8, fontweight='bold')
# SHT45 Female Socket
for x in [108.17 + i*2.54 for i in range(5)]:
    ax2.add_patch(patches.Circle((x, 127.5), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
ax2.add_patch(patches.Rectangle((108.17 - 1.27, 127.5 - 1.27), 10.16 + 2.54, 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

# 2. GY-521 (Bottom, Top-Right) - COMPLETELY CLEARS M3 HOLE (Y_max = 142.65 < 143.75, X_max = 143.7 < 143.75)
ax2.add_patch(patches.Rectangle((123.0, 127.0), 20.7, 15.65, facecolor='#d63031', edgecolor='orange', lw=1.5, alpha=0.75))
ax2.text(133.35, 136.0, 'GY-521 (MPU6050)\n20.7 x 15.65mm', color='white', ha='center', va='center', fontsize=8, fontweight='bold')
# GY-521 Female Socket
for x in [124.5 + i*2.54 for i in range(8)]:
    ax2.add_patch(patches.Circle((x, 128.5), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
ax2.add_patch(patches.Rectangle((124.5 - 1.27, 128.5 - 1.27), 17.78 + 2.54, 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

# 3. ATGM336H GPS (Bottom, Right-Wing) - 100% CLEAR OF BEETLE C6 & M3 HOLES
ax2.add_patch(patches.Rectangle((136.5, 108.0), 13.1, 15.7, facecolor='#00b894', edgecolor='lightgreen', lw=1.5, alpha=0.75))
ax2.text(143.05, 115.85, 'ATGM336H\n(13.1x15.7)', color='white', ha='center', va='center', fontsize=7, fontweight='bold')
# GPS Female Socket
for y in [110.0 + i*2.54 for i in range(5)]:
    ax2.add_patch(patches.Circle((143.0, y), 0.8, facecolor=PAD_COLOR, edgecolor='black', lw=0.5))
ax2.add_patch(patches.Rectangle((143.0 - 1.27, 110.0 - 1.27), 2.54, 10.16 + 2.54, facecolor='none', edgecolor='#ff4757', lw=1.2, ls='--'))

# Ghost of Beetle C6 area on Bottom (Clean Keepout Area)
ax2.add_patch(patches.Rectangle((114.75, 100.0), 20.5, 25.0, facecolor='#153520', edgecolor='#555555', lw=1, ls=':'))
ax2.text(125.0, 112.5, '[Clean Keepout Area]\n(No pins under Beetle C6!)', color='#88cc88', ha='center', va='center', fontsize=8, fontweight='bold')

plt.tight_layout()
out_png = 'scratch/preview_clean_layout.png'
plt.savefig(out_png, dpi=150)
print(f"Generated updated layout preview: {out_png}")
