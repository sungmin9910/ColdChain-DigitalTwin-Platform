import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches

# Create publication-quality figure
fig = plt.figure(figsize=(16, 8), dpi=300)
plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.05, wspace=0.1)

# Helper function for isometric projection or 3D view
# We can create two 3D subplots: (a) Top Assembly, (b) Bottom Assembly
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

def draw_carrier_pcb(ax, is_top=True):
    # PCB Slab: 100 to 150 (50mm x 50mm), thickness 1.6mm
    # Center at (0,0) for clean rotation
    # Base coords: X in [-25, 25], Y in [-25, 25]
    # Chamfer 2mm at 4 corners
    verts = [
        (-23, -25, 0), (23, -25, 0), (25, -23, 0), (25, 23, 0),
        (23, 25, 0), (-23, 25, 0), (-25, 23, 0), (-25, -23, 0)
    ]
    t = 1.6
    top_verts = [(x, y, t) for x, y, z in verts]
    bot_verts = [(x, y, 0) for x, y, z in verts]
    
    # Draw PCB faces
    # Top face
    pcb_color = '#1e4620' if is_top else '#1b3f1d'
    top_poly = Poly3DCollection([top_verts], facecolor=pcb_color, edgecolor='#3a7540', alpha=0.95, linewidth=1)
    ax.add_collection3d(top_poly)
    
    # Bottom face
    bot_poly = Poly3DCollection([bot_verts], facecolor=pcb_color, edgecolor='#3a7540', alpha=0.95, linewidth=1)
    ax.add_collection3d(bot_poly)
    
    # Side faces
    n = len(verts)
    for i in range(n):
        side = [verts[i], verts[(i+1)%n], top_verts[(i+1)%n], top_verts[i]]
        ax.add_collection3d(Poly3DCollection([side], facecolor='#163318', edgecolor='#2f5f33', alpha=0.9, linewidth=0.5))
        
    # Mounting holes at 4 corners (+-21.5, +-21.5)
    for hx, hy in [(-21.5, -21.5), (21.5, -21.5), (-21.5, 21.5), (21.5, 21.5)]:
        theta = np.linspace(0, 2*np.pi, 20)
        # Pad gold ring
        r_pad = 2.75
        r_hole = 1.6
        xp = hx + r_pad * np.cos(theta)
        yp = hy + r_pad * np.sin(theta)
        ax.plot(xp, yp, t + 0.02 if is_top else -0.02, color='#e5b83b', lw=1.2)
        xh = hx + r_hole * np.cos(theta)
        yh = hy + r_hole * np.sin(theta)
        ax.plot(xh, yh, t + 0.02 if is_top else -0.02, color='#222222', lw=1.0)

def draw_box(ax, x0, y0, z0, dx, dy, dz, color, edge_color='black', alpha=0.9, label=None):
    # Draw a 3D rectangular box (e.g. module PCB or chip)
    verts = [
        [(x0, y0, z0), (x0+dx, y0, z0), (x0+dx, y0+dy, z0), (x0, y0+dy, z0)],
        [(x0, y0, z0+dz), (x0+dx, y0, z0+dz), (x0+dx, y0+dy, z0+dz), (x0, y0+dy, z0+dz)],
        [(x0, y0, z0), (x0+dx, y0, z0), (x0+dx, y0, z0+dz), (x0, y0, z0+dz)],
        [(x0, y0+dy, z0), (x0+dx, y0+dy, z0), (x0+dx, y0+dy, z0+dz), (x0, y0+dy, z0+dz)],
        [(x0, y0, z0), (x0, y0+dy, z0), (x0, y0+dy, z0+dz), (x0, y0, z0+dz)],
        [(x0+dx, y0, z0), (x0+dx, y0+dy, z0), (x0+dx, y0+dy, z0+dz), (x0+dx, y0, z0+dz)]
    ]
    ax.add_collection3d(Poly3DCollection(verts, facecolor=color, edgecolor=edge_color, alpha=alpha, linewidth=0.6))

# --- PLOT 1: TOP ASSEMBLY ---
ax = ax1
draw_carrier_pcb(ax, is_top=True)
# Traces on Top (F.Cu) in copper gold
# Let's draw representative clean traces
top_traces = [
    # SDA highway & branches
    [(-8.89, -9.64), (-7.2, -9.64), (-7.2, 0), (-6.67, 0), (-6.67, 2.5)],
    [(-6.67, 0), (1.5, 0), (1.5, 17.0)],
    [(1.5, 0), (12.18, 0), (12.18, 2.5)],
    [(12.18, 0), (20.29, 0), (20.29, -1.8)],
    # 3V3 trace
    [(8.89, -19.8), (12.67, -19.8), (12.67, -1.8)],
    # GND traces
    [(8.89, -22.34), (21.5, -22.34), (21.5, -21.5)],
    [(21.5, -21.5), (23.5, -19.5), (23.5, -1.8)],
    # BAT trace
    [(-2.0, 21.5), (-2.0, 19.8), (0.0, 19.8), (0.0, -22.34), (-8.89, -22.34)]
]
for tr in top_traces:
    xs = [p[0] for p in tr]
    ys = [p[1] for p in tr]
    zs = [1.65] * len(tr)
    ax.plot(xs, ys, zs, color='#d4af37', lw=1.5, alpha=0.85)

# 1. Beetle ESP32-C6 Socket & Module
# Sockets (2 rows of 1x8, height 5.0mm)
draw_box(ax, -8.89 - 1.27, -22.34 - 1.27, 1.6, 2.54, 20.32, 5.0, '#1c1c1c', '#444444')
draw_box(ax, 8.89 - 1.27, -22.34 - 1.27, 1.6, 2.54, 20.32, 5.0, '#1c1c1c', '#444444')
# Beetle C6 Module (20.5 x 25.0 mm, elevated at z=6.6mm)
draw_box(ax, -10.25, -25.0, 6.6, 20.5, 25.0, 1.6, '#1a3a5f', '#2a5a8f', alpha=0.95)
# Beetle SoC Chip (ESP32-C6 QFN)
draw_box(ax, -4.0, -15.0, 8.2, 8.0, 8.0, 1.0, '#111111', '#555555')
# Beetle USB-C Port
draw_box(ax, -4.5, -25.5, 6.8, 9.0, 6.5, 3.2, '#c0c0c0', '#777777')

# 2. BH1750 Ambient Light Sensor (13.9 x 18.5mm, Top Right Wing)
# Socket
draw_box(ax, 15.2 - 1.27, -1.8 - 1.27, 1.6, 12.7, 2.54, 5.0, '#1c1c1c', '#444444')
# Module PCB
draw_box(ax, 13.6, -18.3, 6.6, 13.9, 18.5, 1.6, '#0f4c81', '#1f6ca1', alpha=0.95)
# Optical Sensor IC (white/translucent)
draw_box(ax, 18.5, -10.0, 8.2, 4.0, 4.0, 1.2, '#eef2f5', '#99aabb')

# 3. JST-PH & Power Switch (Top-Center)
draw_box(ax, -2.0, 19.5, 1.6, 6.0, 4.5, 6.0, '#f5f5f5', '#aaaaaa') # JST White
draw_box(ax, -6.5, 12.0, 1.6, 7.0, 4.0, 3.5, '#444444', '#888888') # Switch Metal

# --- PLOT 2: BOTTOM ASSEMBLY ---
ax = ax2
draw_carrier_pcb(ax, is_top=False)
# Bottom Traces (B.Cu) in bright amber
bot_traces = [
    # SCL Highway & branches
    [(-9.21, 2.5), (-9.21, 6.0), (9.64, 6.0), (9.64, 2.5)],
    [(9.64, 6.0), (17.75, 6.0), (17.75, -1.8)],
    [(-8.89, -7.1), (-9.21, -7.1), (-9.21, 2.5)],
    # GPS TX trace
    [(-8.89, -12.18), (-15.05, -12.18), (-15.05, -15.5)],
    # 3V3 Bottom Feed
    [(8.89, -19.8), (4.56, -19.8), (4.56, 2.5)],
    [(4.56, 2.5), (3.75, 17.0), (-2.25, 17.0), (-2.25, 10.0), (-16.83, 10.0), (-16.83, 2.5)],
    [(-16.83, 2.5), (-22.67, 2.5), (-22.67, -15.5)]
]
for tr in bot_traces:
    xs = [p[0] for p in tr]
    ys = [p[1] for p in tr]
    zs = [-0.05] * len(tr)
    ax.plot(xs, ys, zs, color='#e67e22', lw=1.5, alpha=0.85)

# 1. SHT45 Temp/RH Sensor (25.5 x 17.8mm, Bottom Top-Left)
# Socket
draw_box(ax, -21.83 - 1.27, 2.5 - 1.27, -5.0, 12.7, 2.54, 5.0, '#1c1c1c', '#444444')
# Module PCB
draw_box(ax, -24.5, 0.5, -6.6 - 1.6, 25.5, 17.8, 1.6, '#0b3c5d', '#1d5f8a', alpha=0.95)
# SHT45 DFN Sensor IC (Metal Cap)
draw_box(ax, -13.0, 8.0, -9.0, 2.5, 2.5, 0.8, '#dcdcdc', '#666666')

# 2. GY-521 6-Axis IMU (20.7 x 15.65mm, Bottom Top-Right)
# Socket
draw_box(ax, 4.56 - 1.27, 2.5 - 1.27, -5.0, 20.32, 2.54, 5.0, '#1c1c1c', '#444444')
# Module PCB
draw_box(ax, 3.5, 0.5, -6.6 - 1.6, 20.7, 15.65, 1.6, '#145214', '#288028', alpha=0.95)
# MPU6050 QFN IC
draw_box(ax, 11.5, 6.0, -9.0, 4.0, 4.0, 0.9, '#1a1a1a', '#555555')

# 3. ATGM336H Mini GPS (13.1 x 15.7mm, Bottom Left Wing) - REAL MICRO SIZE!
# Socket
draw_box(ax, -21.83 - 1.27, -15.5 - 1.27, -5.0, 12.7, 2.54, 5.0, '#1c1c1c', '#444444')
# Module PCB
draw_box(ax, -24.2, -17.5, -6.6 - 1.6, 13.1, 15.7, 1.6, '#1f3a52', '#325d88', alpha=0.95)
# Ceramic Patch Antenna (Gold/Silver cube 12x12x4mm)
draw_box(ax, -23.7, -16.0, -6.6 - 1.6 - 4.0, 12.0, 12.0, 4.0, '#c8b282', '#7a6a4a')

# Formatting both 3D axes
for ax, title, elev, azim in [(ax1, "(a) Top-Side 3D Isometric View\n(MCU & Optical Sensor)", 32, -55),
                              (ax2, "(b) Bottom-Side 3D Isometric View\n(Multi-Modal Environmental & Motion Sensors)", -32, -125)]:
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlim(-30, 30)
    ax.set_ylim(-30, 30)
    ax.set_zlim(-15, 15)
    ax.axis('off') # Turn off 3D box axes for clean white background
    ax.set_facecolor('white')

# Add callout annotations & dimension notes
fig.text(0.5, 0.04, 
         "Carrier Board Dimensions: 50.0 mm x 50.0 mm x 1.6 mm (FR-4, ENIG Gold Pads, 2.54mm Female Header Sockets)\n"
         "Real Component Dimensions: Beetle C6 (20.5x25mm), BH1750 (13.9x18.5mm), ATGM336H GPS (13.1x15.7mm), SHT45 (25.5x17.8mm), GY-521 (20.7x15.65mm)",
         ha='center', fontsize=10, style='italic', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', edgecolor='#cccccc'))

out_path = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText\Fig2_CarrierBoard_3D_Isometric_Publication.png"
plt.savefig(out_path, dpi=300, facecolor='white')
print("Successfully generated 3D Isometric Publication Figure:", out_path)
