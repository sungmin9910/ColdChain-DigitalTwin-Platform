import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches

# ----------------------------------------------------------------------
# Math utilities for 3D Isometric Projection
# ----------------------------------------------------------------------
COS30 = np.cos(np.radians(30))
SIN30 = np.sin(np.radians(30))

def iso_proj(x, y, z, xc=125.0, yc=125.0, flip_x=False):
    dx = (xc - x) if flip_x else (x - xc)
    dy = (y - yc)
    u = (dx - dy) * COS30
    v = (dx + dy) * SIN30 + z
    return u, v

def iso_poly(pts_3d, xc=125.0, yc=125.0, flip_x=False):
    return [iso_proj(x, y, z, xc, yc, flip_x) for x, y, z in pts_3d]

def draw_iso_prism(ax, x0, y0, z0, dx, dy, dz, facecolor, edgecolor='#222222', alpha=1.0, lw=1.0, xc=125.0, yc=125.0, flip_x=False):
    """Draw a 3D box in isometric projection with realistic face shading"""
    v = [
        (x0, y0, z0),          # 0
        (x0+dx, y0, z0),       # 1
        (x0+dx, y0+dy, z0),    # 2
        (x0, y0+dy, z0),       # 3
        (x0, y0, z0+dz),       # 4
        (x0+dx, y0, z0+dz),    # 5
        (x0+dx, y0+dy, z0+dz), # 6
        (x0, y0+dy, z0+dz),    # 7
    ]
    from matplotlib.colors import to_rgb
    rgb = np.array(to_rgb(facecolor))
    top_col = np.clip(rgb * 1.08, 0, 1)
    right_col = np.clip(rgb * 0.85, 0, 1)
    left_col = np.clip(rgb * 0.70, 0, 1)
    
    # Left face
    ax.add_patch(Polygon(iso_poly([v[0], v[3], v[7], v[4]], xc, yc, flip_x),
                         facecolor=left_col, edgecolor=edgecolor, alpha=alpha, lw=lw))
    # Right face
    ax.add_patch(Polygon(iso_poly([v[0], v[1], v[5], v[4]], xc, yc, flip_x),
                         facecolor=right_col, edgecolor=edgecolor, alpha=alpha, lw=lw))
    # Front-Y face
    ax.add_patch(Polygon(iso_poly([v[1], v[2], v[6], v[5]], xc, yc, flip_x),
                         facecolor=right_col, edgecolor=edgecolor, alpha=alpha, lw=lw))
    # Top face
    ax.add_patch(Polygon(iso_poly([v[4], v[5], v[6], v[7]], xc, yc, flip_x),
                         facecolor=top_col, edgecolor=edgecolor, alpha=alpha, lw=lw))

def draw_iso_pin_socket(ax, x_start, y_start, pin_count, is_horizontal=True, z_base=1.6, xc=125.0, yc=125.0, flip_x=False):
    """Draw realistic 2.54mm female pin header socket"""
    pitch = 2.54
    if is_horizontal:
        dx = pin_count * pitch
        dy = 2.54
        dz = 5.0
        draw_iso_prism(ax, x_start - pitch/2, y_start - dy/2, z_base, dx, dy, dz, '#1e272e', '#485460', lw=0.6, xc=xc, yc=yc, flip_x=flip_x)
        for i in range(pin_count):
            px = x_start + i * pitch
            py = y_start
            draw_iso_prism(ax, px - 0.5, py - 0.5, z_base + dz - 0.05, 1.0, 1.0, 0.05, '#d4af37', '#8a7322', lw=0.4, xc=xc, yc=yc, flip_x=flip_x)
    else:
        dx = 2.54
        dy = pin_count * pitch
        dz = 5.0
        draw_iso_prism(ax, x_start - dx/2, y_start - pitch/2, z_base, dx, dy, dz, '#1e272e', '#485460', lw=0.6, xc=xc, yc=yc, flip_x=flip_x)
        for i in range(pin_count):
            px = x_start
            py = y_start + i * pitch
            draw_iso_prism(ax, px - 0.5, py - 0.5, z_base + dz - 0.05, 1.0, 1.0, 0.05, '#d4af37', '#8a7322', lw=0.4, xc=xc, yc=yc, flip_x=flip_x)

# ----------------------------------------------------------------------
# Set Up Figure with Extra Margins
# ----------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 11), dpi=300)
plt.subplots_adjust(left=0.04, right=0.96, top=0.88, bottom=0.09, wspace=0.10)

pcb_pts_2d = [
    (102.0, 100.0), (148.0, 100.0), (150.0, 102.0), (150.0, 148.0),
    (148.0, 150.0), (102.0, 150.0), (100.0, 148.0), (100.0, 102.0)
]

def render_pcb_base(ax, is_top=True, flip_x=False):
    z_bot = 0.0
    z_top = 1.6
    
    # Shadow underneath
    shadow_pts = [iso_proj(x, y, -2.0, flip_x=flip_x) for x, y in pcb_pts_2d]
    ax.add_patch(Polygon(shadow_pts, facecolor='#000000', alpha=0.15, edgecolor='none'))
    
    # Side edge walls
    n = len(pcb_pts_2d)
    for i in range(n):
        p1 = pcb_pts_2d[i]
        p2 = pcb_pts_2d[(i+1)%n]
        wall_3d = [(p1[0], p1[1], z_bot), (p2[0], p2[1], z_bot), (p2[0], p2[1], z_top), (p1[0], p1[1], z_top)]
        wall_poly = iso_poly(wall_3d, flip_x=flip_x)
        ax.add_patch(Polygon(wall_poly, facecolor='#0e2e16', edgecolor='#1d4a25', lw=0.7))
        
    # Main PCB Surface (FR-4 Solder Mask Green)
    surf_pts = [iso_proj(x, y, z_top, flip_x=flip_x) for x, y in pcb_pts_2d]
    ax.add_patch(Polygon(surf_pts, facecolor='#1b4d24', edgecolor='#2e783c', lw=1.5))
    
    # M3 Mounting Holes
    holes = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]
    for hx, hy in holes:
        theta = np.linspace(0, 2*np.pi, 28)
        pad_pts = [iso_proj(hx + 2.75*np.cos(t), hy + 2.75*np.sin(t), z_top + 0.02, flip_x=flip_x) for t in theta]
        ax.add_patch(Polygon(pad_pts, facecolor='#d4af37', edgecolor='#8a7322', lw=0.8))
        hole_pts = [iso_proj(hx + 1.6*np.cos(t), hy + 1.6*np.sin(t), z_top + 0.04, flip_x=flip_x) for t in theta]
        ax.add_patch(Polygon(hole_pts, facecolor='#0a0a0a', edgecolor='#333333', lw=0.5))

# ======================================================================
# [1] TOP-SIDE ASSEMBLY VIEW
# ======================================================================
ax = ax1
render_pcb_base(ax, is_top=True)

# Traces on Top (F.Cu)
from test_routing_perfection import top_traces, gnd_traces
for tname, net, x1, y1, x2, y2 in top_traces:
    col = '#f1c40f' if net in [5, 6] else ('#e67e22' if net in [2, 3, 4] else '#00d2d3')
    lw = 1.4 if net in [3, 4] else 1.0
    u1, v1 = iso_proj(x1, y1, 1.64)
    u2, v2 = iso_proj(x2, y2, 1.64)
    ax.plot([u1, u2], [v1, v2], color=col, lw=lw, alpha=0.9, solid_capstyle='round')

for tname, net, x1, y1, x2, y2 in gnd_traces:
    if "T" in tname:
        u1, v1 = iso_proj(x1, y1, 1.64)
        u2, v2 = iso_proj(x2, y2, 1.64)
        ax.plot([u1, u2], [v1, v2], color='#2ed573', lw=1.2, alpha=0.85, solid_capstyle='round')

# Top Sockets
draw_iso_pin_socket(ax, 116.11, 102.66, 8, is_horizontal=False, z_base=1.6)
draw_iso_pin_socket(ax, 133.89, 102.66, 8, is_horizontal=False, z_base=1.6)
draw_iso_pin_socket(ax, 137.67, 123.2, 5, is_horizontal=True, z_base=1.6)

# JST-PH 2.0 & SW1 & Resistors
draw_iso_prism(ax, 122.0 - 3.0, 146.5 - 2.25, 1.6, 6.0, 4.5, 6.0, '#f1f2f6', '#ced6e0', lw=0.8) # JST Header
draw_iso_prism(ax, 114.5 - 1.0, 146.5 - 2.0, 1.6, 7.0, 4.0, 3.5, '#747d8c', '#2f3542', lw=0.8)  # Switch Body
draw_iso_prism(ax, 117.0, 147.5, 5.1, 2.0, 1.5, 2.0, '#2f3542', '#000000', lw=0.6)              # Switch Knob
draw_iso_prism(ax, 121.25, 141.5, 1.6, 2.0, 1.2, 0.6, '#2f3542', '#ced6e0', lw=0.5)            # R3
draw_iso_prism(ax, 127.25, 141.5, 1.6, 2.0, 1.2, 0.6, '#2f3542', '#ced6e0', lw=0.5)            # R4

# Elevated Modules (Z = 15.0 mm)
Z_ELEV = 15.0

# 1. Beetle ESP32-C6
for y in [102.66, 120.44]:
    for x in [116.11, 133.89]:
        u_bot, v_bot = iso_proj(x, y, 6.6)
        u_top, v_top = iso_proj(x, y, Z_ELEV)
        ax.plot([u_bot, u_top], [v_bot, v_top], color='#ff4757', lw=1.0, ls=':')

draw_iso_prism(ax, 114.75, 100.0, Z_ELEV, 20.5, 25.0, 1.6, '#1e3799', '#4a69bd', lw=1.0)
draw_iso_prism(ax, 121.0, 110.0, Z_ELEV + 1.6, 8.0, 8.0, 0.9, '#1e272e', '#485460', lw=0.6)
draw_iso_prism(ax, 120.5, 99.5, Z_ELEV + 0.4, 9.0, 6.5, 3.2, '#d2dae2', '#808e9b', lw=0.8)
draw_iso_prism(ax, 117.0, 120.5, Z_ELEV + 1.6, 16.0, 3.5, 0.8, '#0c2461', '#1e3799', lw=0.6)

# 2. BH1750 Ambient Light
for x in [137.67, 147.83]:
    u_bot, v_bot = iso_proj(x, 123.2, 6.6)
    u_top, v_top = iso_proj(x, 123.2, Z_ELEV)
    ax.plot([u_bot, u_top], [v_bot, v_top], color='#ffa502', lw=1.0, ls=':')

draw_iso_prism(ax, 135.8, 106.7, Z_ELEV, 13.9, 18.5, 1.6, '#0984e3', '#74b9ff', lw=1.0)
draw_iso_prism(ax, 141.0, 114.0, Z_ELEV + 1.6, 4.0, 4.0, 1.3, '#f1f2f6', '#dfe4ea', lw=0.6)

# Annotations for Top Side (Well-spaced)
# Callout ①: Beetle C6
u_c6, v_c6 = iso_proj(125.0, 112.5, Z_ELEV + 2.5)
ax.annotate("① DFRobot Beetle ESP32-C6 Core Module\n"
            "   • 32-bit RISC-V @ 160MHz, Wi-Fi 6 & BLE 5\n"
            "   • Dim: 20.5 × 25.0 mm (Edge-Flush USB-C)\n"
            "   • Dual 1×08 Sockets (Removable One-Touch)",
            xy=(u_c6, v_c6), xytext=(u_c6 - 54, v_c6 + 8),
            arrowprops=dict(arrowstyle="->", color="#1e3799", lw=1.5),
            fontsize=9.2, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#1e3799", lw=1.2))

# Callout ②: BH1750 (Positioned to the right)
u_bh, v_bh = iso_proj(143.0, 116.0, Z_ELEV + 2.5)
ax.annotate("② BH1750 Ambient Light Sensor (GY-302)\n"
            "   • I2C Interface (0x23), 1–65535 lx Range\n"
            "   • Dim: 13.9 × 18.5 mm (Top Right Wing)\n"
            "   • Upward Aperture for Box-Opening Tamper",
            xy=(u_bh, v_bh), xytext=(u_bh + 6, v_bh + 12),
            arrowprops=dict(arrowstyle="->", color="#0984e3", lw=1.5),
            fontsize=9.2, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#0984e3", lw=1.2))

# Callout ③: JST-PH & Power Switch (Positioned at Back-Left)
u_pwr, v_pwr = iso_proj(118.0, 146.5, 6.0)
ax.annotate("③ Power Management & Bus Subsystem\n"
            "   • J1: JST-PH 2.0 (3.7V Rechargeable Li-ion Input)\n"
            "   • SW1: Slide Switch (Hardware Power Cutoff)\n"
            "   • R3, R4: 4.7kΩ I2C Pull-Up Resistors (0805 SMD)",
            xy=(u_pwr, v_pwr), xytext=(u_pwr - 42, v_pwr + 15),
            arrowprops=dict(arrowstyle="->", color="#2f3542", lw=1.5),
            fontsize=8.8, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#747d8c", lw=1.2))

# Mechanical Dimensions on Top Side
u_d1, v_d1 = iso_proj(100.0, 100.0, 0.0)
u_d2, v_d2 = iso_proj(150.0, 100.0, 0.0)
ax.plot([u_d1, u_d2], [v_d1 - 6, v_d2 - 6], color='#2c3e50', lw=1.2)
ax.plot([u_d1, u_d1], [v_d1, v_d1 - 8], color='#2c3e50', lw=0.8)
ax.plot([u_d2, u_d2], [v_d2, v_d2 - 8], color='#2c3e50', lw=0.8)
ax.text((u_d1 + u_d2)/2, (v_d1 + v_d2)/2 - 9, "Width: 50.0 mm", ha='center', va='top', fontsize=9, fontweight='bold', color='#2c3e50')

# Pitch dimension (43.0 mm)
u_h1, v_h1 = iso_proj(103.5, 103.5, 0.0)
u_h2, v_h2 = iso_proj(146.5, 103.5, 0.0)
ax.plot([u_h1, u_h2], [v_h1 - 3, v_h2 - 3], color='#7f8c8d', lw=1.0, ls='--')
ax.text((u_h1 + u_h2)/2, (v_h1 + v_h2)/2 - 5, "M3 Pitch: 43.0 mm", ha='center', va='top', fontsize=8, color='#7f8c8d')


# ======================================================================
# [2] BOTTOM-SIDE ASSEMBLY VIEW
# ======================================================================
ax = ax2
render_pcb_base(ax, is_top=False)

# Traces on Bottom (B.Cu)
from test_routing_perfection import bottom_traces
for tname, net, x1, y1, x2, y2 in bottom_traces:
    col = '#f1c40f' if net in [5, 6] else ('#e67e22' if net in [2, 3, 4] else '#00d2d3')
    lw = 1.4 if net in [2] else 1.0
    u1, v1 = iso_proj(x1, y1, 1.64)
    u2, v2 = iso_proj(x2, y2, 1.64)
    ax.plot([u1, u2], [v1, v2], color=col, lw=lw, alpha=0.9, solid_capstyle='round')

for tname, net, x1, y1, x2, y2 in gnd_traces:
    if "B" in tname or "H" in tname:
        u1, v1 = iso_proj(x1, y1, 1.64)
        u2, v2 = iso_proj(x2, y2, 1.64)
        ax.plot([u1, u2], [v1, v2], color='#2ed573', lw=1.2, alpha=0.85, solid_capstyle='round')

# Dual row MCU header soldered pins on Bottom
for y in [102.66 + i*2.54 for i in range(8)]:
    for x in [116.11, 133.89]:
        u, v = iso_proj(x, y, 1.65)
        ax.plot(u, v, marker='o', markersize=3.5, color='#d4af37', markeredgecolor='#8a7322')

# Bottom Sockets
draw_iso_pin_socket(ax, 108.17, 127.5, 5, is_horizontal=True, z_base=1.6)
draw_iso_pin_socket(ax, 129.56, 127.5, 8, is_horizontal=True, z_base=1.6)
draw_iso_pin_socket(ax, 102.33, 109.5, 5, is_horizontal=True, z_base=1.6)

# Elevated Bottom Sensor Modules
# 4. SHT45 Temp/RH
for x in [108.17, 118.33]:
    u_bot, v_bot = iso_proj(x, 127.5, 6.6)
    u_top, v_top = iso_proj(x, 127.5, Z_ELEV)
    ax.plot([u_bot, u_top], [v_bot, v_top], color='#20bf6b', lw=1.0, ls=':')

draw_iso_prism(ax, 100.5, 125.5, Z_ELEV, 25.5, 17.8, 1.6, '#0b3c5d', '#1d5f8a', lw=1.0)
draw_iso_prism(ax, 112.5, 133.0, Z_ELEV + 1.6, 2.5, 2.5, 0.8, '#dcdcdc', '#718093', lw=0.6)

# 5. GY-521 6-Axis IMU
for x in [129.56, 147.34]:
    u_bot, v_bot = iso_proj(x, 127.5, 6.6)
    u_top, v_top = iso_proj(x, 127.5, Z_ELEV)
    ax.plot([u_bot, u_top], [v_bot, v_top], color='#eb3b5a', lw=1.0, ls=':')

draw_iso_prism(ax, 128.5, 125.5, Z_ELEV, 20.7, 15.65, 1.6, '#10ac84', '#1dd1a1', lw=1.0)
draw_iso_prism(ax, 137.0, 131.0, Z_ELEV + 1.6, 4.0, 4.0, 0.9, '#1e272e', '#485460', lw=0.6)

# 6. ATGM336H Mini GPS
for x in [102.33, 112.49]:
    u_bot, v_bot = iso_proj(x, 109.5, 6.6)
    u_top, v_top = iso_proj(x, 109.5, Z_ELEV)
    ax.plot([u_bot, u_top], [v_bot, v_top], color='#3867d6', lw=1.0, ls=':')

draw_iso_prism(ax, 100.8, 107.5, Z_ELEV, 13.1, 15.7, 1.6, '#2d3436', '#636e72', lw=1.0)
draw_iso_prism(ax, 101.35, 109.35, Z_ELEV + 1.6, 12.0, 12.0, 3.5, '#d4af37', '#8a7322', lw=0.8)

# Annotations for Bottom Side (Clean, non-overlapping)
# Callout ④: SHT45 (Placed top-left)
u_sht, v_sht = iso_proj(113.0, 134.0, Z_ELEV + 2.5)
ax.annotate("④ Sensirion SHT45 Digital Temp/RH Sensor\n"
            "   • Accuracy: ±0.1°C, ±1.5% RH (Cold Chain Grade)\n"
            "   • Dim: 25.5 × 17.8 mm (Bottom Top-Left)\n"
            "   • Pin 2 NC Cut (Absolute 3.3V-GND Isolation)",
            xy=(u_sht, v_sht), xytext=(u_sht - 54, v_sht + 10),
            arrowprops=dict(arrowstyle="->", color="#0b3c5d", lw=1.5),
            fontsize=9.2, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#0b3c5d", lw=1.2))

# Callout ⑤: GY-521 IMU (Placed top-right)
u_imu, v_imu = iso_proj(138.8, 133.0, Z_ELEV + 2.5)
ax.annotate("⑤ InvenSense MPU-6050 6-Axis IMU (GY-521)\n"
            "   • 3-Axis Gyroscope + 3-Axis Accelerometer\n"
            "   • Dim: 20.7 × 15.65 mm (Bottom Top-Right)\n"
            "   • 2.50 mm Air Gap to SHT45 (Thermal Isolation)",
            xy=(u_imu, v_imu), xytext=(u_imu + 6, v_imu + 12),
            arrowprops=dict(arrowstyle="->", color="#10ac84", lw=1.5),
            fontsize=9.2, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#10ac84", lw=1.2))

# Callout ⑥: ATGM336H Mini GPS (Placed bottom-center)
u_gps, v_gps = iso_proj(107.0, 115.0, Z_ELEV + 4.5)
ax.annotate("⑥ ATGM336H Mini GNSS/GPS Tracking Module\n"
            "   • High Sensitivity (-162 dBm), 2.5m CEP Accuracy\n"
            "   • Ultra-Compact Dim: 13.1 × 15.7 mm (Left Wing)\n"
            "   • Integrated 12×12 mm Micro Ceramic Patch Antenna\n"
            "   • Ultra-Short UART Bus (7.0–8.7 mm direct trace)",
            xy=(u_gps, v_gps), xytext=(u_gps - 45, v_gps - 28),
            arrowprops=dict(arrowstyle="->", color="#2d3436", lw=1.5),
            fontsize=9.2, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#2d3436", lw=1.2))

# Subplot formatting
ax1.set_title("(a) Top-Side 3D Isometric View & Assembly Architecture\n(Edge-Flush MCU Core, Optical Sensor & Power Management)",
              fontsize=12.5, fontweight='bold', pad=22, color='#1e272e')
ax1.set_xlim(-68, 56)
ax1.set_ylim(-38, 48)
ax1.set_aspect('equal')
ax1.axis('off')

ax2.set_title("(b) Bottom-Side 3D Isometric View & Multi-Modal Sensor Array\n(Environmental Microclimate, 6-Axis Motion & Micro GNSS Tracking)",
              fontsize=12.5, fontweight='bold', pad=22, color='#1e272e')
ax2.set_xlim(-56, 68)
ax2.set_ylim(-38, 48)
ax2.set_aspect('equal')
ax2.axis('off')

# Publication Footer Box
fig.text(0.5, 0.03,
         "Carrier Board Mechanical Specifications: 50.0 mm × 50.0 mm × 1.6 mm (FR-4 Dual Layer, ENIG Gold Plating, 4× M3 Mounting Holes at 43.0 mm pitch)\n"
         "Plug-and-Play Architecture: 2.54 mm Pitch Gold-Plated Female Sockets Enable Solderless One-Touch Module Swapping and Zero Thermal Interference.",
         ha='center', fontsize=9.5, style='italic',
         bbox=dict(boxstyle='round,pad=0.6', facecolor='#f8f9fa', edgecolor='#b2bec3', lw=1.0))

out_path = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText\Fig2_CarrierBoard_3D_Isometric_Engineering_Drawing.png"
plt.savefig(out_path, dpi=300, facecolor='white')
print("Successfully generated refined publication figure:", out_path)
