import matplotlib.pyplot as plt
import matplotlib.patches as patches
from test_routing_perfection import top_traces, bottom_traces, gnd_traces, pads

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=150)

# Colors matching user's Gerber viewer:
BG_COLOR = '#0d1117'
BOARD_OUTLINE_COLOR = '#ffffff'
SILK_COLOR = '#f1c40f'
DRILL_COLOR = '#00ff00'

# Top layer: Red traces, Magenta pads
TOP_TRACE_COLOR = '#ff2222'
TOP_PAD_COLOR = '#ff00aa'

# Bottom layer: Blue traces, Blue pads
BOT_TRACE_COLOR = '#2277ff'
BOT_PAD_COLOR = '#0055dd'

for ax, title in [(ax1, "TOP LAYER (Front Routing View - Red Traces)"), (ax2, "BOTTOM LAYER (Back Routing View - Blue Traces)")]:
    ax.set_facecolor(BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_xlim(98, 152)
    ax.set_ylim(98, 152)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=13, fontweight='bold', color='white', pad=12)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#444444')
    
    # Board outline
    poly = patches.Polygon([
        (102, 100), (148, 100), (150, 102), (150, 148),
        (148, 150), (102, 150), (100, 148), (100, 102)
    ], closed=True, fill=False, edgecolor=BOARD_OUTLINE_COLOR, lw=1.5)
    ax.add_patch(poly)

# --- TOP LAYER ---
# Outlines on Top: Beetle C6, BH1750, JST-PH, SW1
ax1.add_patch(patches.Rectangle((114.75, 100.0), 20.5, 25.0, fill=False, edgecolor=SILK_COLOR, lw=1.2))
ax1.add_patch(patches.Rectangle((120.5, 100.0), 9.0, 3.5, fill=False, edgecolor=SILK_COLOR, lw=1.0))
ax1.add_patch(patches.Rectangle((135.8, 106.7), 13.9, 18.5, fill=False, edgecolor=SILK_COLOR, lw=1.2))
ax1.add_patch(patches.Rectangle((120.0, 144.5), 6.0, 4.5, fill=False, edgecolor=SILK_COLOR, lw=1.0))
ax1.add_patch(patches.Rectangle((112.5, 144.5), 7.0, 4.0, fill=False, edgecolor=SILK_COLOR, lw=1.0))

# Top Traces
for name, net, x1, y1, x2, y2 in top_traces:
    ax1.plot([x1, x2], [y1, y2], color=TOP_TRACE_COLOR, lw=2.2, solid_capstyle='round')
for name, net, x1, y1, x2, y2 in gnd_traces:
    if "_T" in name:
        ax1.plot([x1, x2], [y1, y2], color=TOP_TRACE_COLOR, lw=2.2, solid_capstyle='round')

# Pads on Top
for p_name, net, px, py, p_rad in pads:
    # If M3 hole
    if 'H' in p_name and len(p_name) == 2:
        ax1.add_patch(patches.Circle((px, py), 2.75, facecolor=TOP_PAD_COLOR, edgecolor='none'))
        ax1.add_patch(patches.Circle((px, py), 1.6, facecolor=DRILL_COLOR, edgecolor='none'))
    elif 'R3' in p_name or 'R4' in p_name:
        ax1.add_patch(patches.Rectangle((px - 0.4, py - 0.4), 0.8, 0.8, facecolor=TOP_PAD_COLOR, edgecolor='none'))
    elif 'SW1' in p_name:
        ax1.add_patch(patches.Rectangle((px - 0.5, py - 0.75), 1.0, 1.5, facecolor=TOP_PAD_COLOR, edgecolor='none'))
    else: # Through-Hole pad
        if '1' in p_name and ('MCU' in p_name or 'BH' in p_name or 'GPS' in p_name or 'SHT' in p_name or 'GY' in p_name or 'J1' in p_name):
            ax1.add_patch(patches.Rectangle((px - 0.8, py - 0.8), 1.6, 1.6, facecolor=TOP_PAD_COLOR, edgecolor='none'))
        else:
            ax1.add_patch(patches.Circle((px, py), 0.8, facecolor=TOP_PAD_COLOR, edgecolor='none'))
        ax1.add_patch(patches.Circle((px, py), 0.475, facecolor=DRILL_COLOR, edgecolor='none'))

# --- BOTTOM LAYER ---
# Outlines on Bottom: SHT45, GY-521, GPS, Keepout
ax2.add_patch(patches.Rectangle((100.5, 125.5), 25.5, 17.8, fill=False, edgecolor=SILK_COLOR, lw=1.2))
ax2.add_patch(patches.Rectangle((128.5, 125.5), 20.7, 15.65, fill=False, edgecolor=SILK_COLOR, lw=1.2))
ax2.add_patch(patches.Rectangle((100.8, 107.5), 13.1, 15.7, fill=False, edgecolor=SILK_COLOR, lw=1.2))
ax2.add_patch(patches.Rectangle((114.75, 100.0), 20.5, 25.0, fill=False, edgecolor='#555555', lw=1.0, ls=':'))

# Bottom Traces
for name, net, x1, y1, x2, y2 in bottom_traces:
    ax2.plot([x1, x2], [y1, y2], color=BOT_TRACE_COLOR, lw=2.2, solid_capstyle='round')
for name, net, x1, y1, x2, y2 in gnd_traces:
    if "_B" in name:
        ax2.plot([x1, x2], [y1, y2], color=BOT_TRACE_COLOR, lw=2.2, solid_capstyle='round')

# Pads on Bottom
for p_name, net, px, py, p_rad in pads:
    if 'R3' in p_name or 'R4' in p_name or 'SW1' in p_name:
        continue # SMD top only
    if 'H' in p_name and len(p_name) == 2:
        ax2.add_patch(patches.Circle((px, py), 2.75, facecolor=BOT_PAD_COLOR, edgecolor='none'))
        ax2.add_patch(patches.Circle((px, py), 1.6, facecolor=DRILL_COLOR, edgecolor='none'))
    else:
        if '1' in p_name and ('MCU' in p_name or 'BH' in p_name or 'GPS' in p_name or 'SHT' in p_name or 'GY' in p_name or 'J1' in p_name):
            ax2.add_patch(patches.Rectangle((px - 0.8, py - 0.8), 1.6, 1.6, facecolor=BOT_PAD_COLOR, edgecolor='none'))
        else:
            ax2.add_patch(patches.Circle((px, py), 0.8, facecolor=BOT_PAD_COLOR, edgecolor='none'))
        ax2.add_patch(patches.Circle((px, py), 0.475, facecolor=DRILL_COLOR, edgecolor='none'))

plt.tight_layout()
out_png = 'scratch/preview_routed_layers.png'
plt.savefig(out_png, dpi=150, facecolor=fig.get_facecolor())
print(f"Generated realistic Gerber preview: {out_png}")
