import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Configure Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

PCB_PATH = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText\CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb"
OUT_IMG = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText\Fig_CarrierBoard_Routing_Verification.png"
ARTIFACT_DIR = r"C:\Users\korea\.gemini\antigravity-ide\brain\531a7f17-5cfb-4c4c-a6c8-8be28bb2ba15"
ARTIFACT_IMG = os.path.join(ARTIFACT_DIR, "Fig_CarrierBoard_Routing_Verification.png")

with open(PCB_PATH, "r", encoding="utf-8") as f:
    pcb_text = f.read()

# 1. Parse Nets
net_names = {
    0: "NC",
    1: "GND",
    2: "3V3",
    3: "BAT+",
    4: "BAT",
    5: "I2C_SDA",
    6: "I2C_SCL",
    7: "GPS_RX",
    8: "GPS_TX"
}

net_colors = {
    1: "#2ECC71", # GND (Green)
    2: "#FF3366", # 3V3 (Vibrant Red/Crimson)
    3: "#FF9F43", # BAT+ (Warm Orange)
    4: "#FECA57", # BAT (Amber/Gold)
    5: "#00D2D3", # SDA (Cyan)
    6: "#A55EEA", # SCL (Bright Purple)
    7: "#F368E0", # GPS_RX (Pink)
    8: "#10AC84", # GPS_TX (Emerald)
}

# 2. Parse Segments
seg_pattern = re.compile(r'\(segment\s+\(start\s+([0-9.-]+)\s+([0-9.-]+)\)\s+\(end\s+([0-9.-]+)\s+([0-9.-]+)\)\s+\(width\s+([0-9.-]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+([0-9]+)\)\)')
segments = []
for m in seg_pattern.finditer(pcb_text):
    x1, y1, x2, y2, w, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6), int(m.group(7))
    segments.append({
        'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'w': w, 'layer': layer, 'net': net
    })

# 3. Parse Vias
via_pattern = re.compile(r'\(via\s+\(at\s+([0-9.-]+)\s+([0-9.-]+)\)\s+\(size\s+([0-9.-]+)\)\s+\(drill\s+([0-9.-]+)\).*?\(net\s+([0-9]+)\)\)')
vias = []
for m in via_pattern.finditer(pcb_text):
    x, y, s, d, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), int(m.group(5))
    vias.append({
        'x': x, 'y': y, 'size': s, 'drill': d, 'net': net
    })

# 4. Parse Footprints and Pads
fp_blocks = re.findall(r'\(footprint\s+"([^"]+)"\s+\(layer\s+"([^"]+)"\)\s+\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)(.*?)\n\t\)', pcb_text, re.DOTALL)
pads = []
for fp_name, fp_layer, fp_x, fp_y, fp_rot, fp_body in fp_blocks:
    fx, fy = float(fp_x), float(fp_y)
    rot = float(fp_rot) if fp_rot else 0.0
    ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_body)
    ref = ref_match.group(1) if ref_match else fp_name
    
    pad_matches = re.finditer(r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)\s+\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)\s+\(size\s+([0-9.-]+)\s+([0-9.-]+)\)(?:.*?\(drill\s+([0-9.-]+)\))?(?:.*?\(net\s+([0-9]+)\s+"([^"]*)")?', fp_body)
    for pm in pad_matches:
        pnum = pm.group(1)
        ptype = pm.group(2)
        pshape = pm.group(3)
        px, py = float(pm.group(4)), float(pm.group(5))
        sx, sy = float(pm.group(7)), float(pm.group(8))
        drill = float(pm.group(9)) if pm.group(9) else 0.0
        net = int(pm.group(10)) if pm.group(10) else 0
        net_name = pm.group(11) if pm.group(11) else ""
        
        rad = np.radians(rot)
        wx = fx + px * np.cos(rad) - py * np.sin(rad)
        wy = fy + px * np.sin(rad) + py * np.cos(rad)
        
        pads.append({
            'ref': ref, 'num': pnum, 'type': ptype, 'shape': pshape,
            'x': wx, 'y': wy, 'sx': sx, 'sy': sy, 'drill': drill,
            'net': net, 'net_name': net_name, 'fp_layer': fp_layer
        })

# Fine-Tuned Module Layout to eliminate ANY visual overlap
modules = [
    {
        "id": "MCU",
        "name_ko": "DFRobot Beetle ESP32-C6 Mini",
        "name_sub": "20.5×25.0mm | 메인 MCU (전면 Top 실장)",
        "layer": "Top",
        "box": [114.75, 100.0, 20.5, 25.0],
        "bg_color": "#1A252C",
        "border_color": "#00D2D3",
        "badge_color": "#00D2D3",
        "header_pos": (125.0, 104.5),
        "sub_pos": (125.0, 106.8),
        "ic_box": [121.5, 111.0, 7.0, 6.0],
        "ic_label": "ESP32-C6\nRISC-V",
        "extra_gfx": "usb"
    },
    {
        "id": "BH1750",
        "name_ko": "BH1750 조도 센서 (GY-302)",
        "name_sub": "13.9×18.5mm | I2C: 0x23 (전면 Top)",
        "layer": "Top",
        "box": [135.8, 106.7, 13.9, 18.5],
        "bg_color": "#2C2216",
        "border_color": "#FFA502",
        "badge_color": "#FFA502",
        "header_pos": (142.75, 109.5),
        "sub_pos": (142.75, 111.8),
        "ic_box": [140.2, 114.5, 5.0, 4.5],
        "ic_label": "BH1750"
    },
    {
        "id": "GPS",
        "name_ko": "ATGM336H-5N GPS 모듈",
        "name_sub": "13.1×15.7mm | UART (후면 Bottom)",
        "layer": "Bottom",
        "box": [100.86, 107.5, 13.1, 15.7],
        "bg_color": "#152528",
        "border_color": "#2ED573",
        "badge_color": "#2ED573",
        "header_pos": (107.41, 118.5),
        "sub_pos": (107.41, 120.7),
        "ic_box": [104.2, 112.0, 6.5, 4.5],
        "ic_label": "ATGM336H"
    },
    {
        "id": "SHT45",
        "name_ko": "SHT45 온습도 센서 (Qwiic)",
        "name_sub": "25.5×17.8mm | I2C: 0x44 (후면 Bottom)",
        "layer": "Bottom",
        "box": [100.5, 125.5, 25.5, 17.8],
        "bg_color": "#1C192E",
        "border_color": "#9B59B6",
        "badge_color": "#9B59B6",
        "header_pos": (113.25, 138.5),
        "sub_pos": (113.25, 140.7),
        "ic_box": [110.5, 131.0, 5.5, 4.5],
        "ic_label": "SHT45"
    },
    {
        "id": "GY521",
        "name_ko": "GY-521 6축 IMU (MPU6050)",
        "name_sub": "20.7×15.65mm | I2C: 0x68 (후면 Bottom)",
        "layer": "Bottom",
        "box": [128.0, 125.5, 20.7, 15.65],
        "bg_color": "#162533",
        "border_color": "#3867D6",
        "badge_color": "#3867D6",
        "header_pos": (138.35, 138.0),
        "sub_pos": (138.35, 140.2),
        "ic_box": [135.5, 131.0, 5.7, 4.5],
        "ic_label": "MPU6050"
    },
    {
        "id": "SW1",
        "name_ko": "SW1 전원 스위치",
        "name_sub": "Top 실장",
        "layer": "Top",
        "box": [112.5, 144.5, 7.0, 4.2],
        "bg_color": "#261C14",
        "border_color": "#FF7F50",
        "badge_color": "#FF7F50",
        "header_pos": (116.0, 143.2),
        "sub_pos": None
    },
    {
        "id": "JST",
        "name_ko": "JST-PH 2.0 (배터리)",
        "name_sub": "Top 실장",
        "layer": "Top",
        "box": [120.0, 144.5, 6.0, 4.5],
        "bg_color": "#261C14",
        "border_color": "#FF7F50",
        "badge_color": "#FF7F50",
        "header_pos": (123.0, 143.2),
        "sub_pos": None
    },
    {
        "id": "PULLUPS",
        "name_ko": "R3/R4 4.7kΩ 풀업",
        "name_sub": "0603 SMD",
        "layer": "Top",
        "box": [120.5, 140.5, 8.5, 2.5],
        "bg_color": "#2A2A2A",
        "border_color": "#A4B0BE",
        "badge_color": "#A4B0BE",
        "header_pos": (124.75, 138.5),
        "sub_pos": None
    }
]

# Plotting Figure (Wide 3-Panel)
fig, axes = plt.subplots(1, 3, figsize=(25, 9.8), dpi=300)

chamfer_pts = [
    (102.0, 100.0), (148.0, 100.0),
    (150.0, 102.0), (150.0, 148.0),
    (148.0, 150.0), (102.0, 150.0),
    (100.0, 148.0), (100.0, 102.0),
    (102.0, 100.0)
]

def draw_base(ax, title, subtitle):
    pcb_patch = patches.Polygon(chamfer_pts, closed=True, facecolor='#0D1117', edgecolor='#30363D', linewidth=2.5, zorder=1)
    ax.add_patch(pcb_patch)
    
    ax.set_xlim(97.0, 153.0)
    ax.set_ylim(94.0, 153.0)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.grid(True, linestyle=':', color='#21262D', alpha=0.8, zorder=0)
    ax.set_xlabel('기판 X 좌표 (mm)', fontsize=11, color='#C9D1D9', labelpad=6)
    ax.set_ylabel('기판 Y 좌표 (mm)', fontsize=11, color='#C9D1D9', labelpad=6)
    
    # Title & Subtitle cleanly separated above board
    ax.text(125.0, 95.0, title, fontsize=13.0, fontweight='bold', color='#58A6FF', ha='center', va='bottom')
    ax.text(125.0, 97.2, subtitle, fontsize=9.5, color='#8B949E', ha='center', va='bottom')
    
    # 4 Mounting Holes (M3)
    for hx, hy, hname in [(103.5, 103.5, 'H1'), (146.5, 103.5, 'H2'), (103.5, 146.5, 'H3'), (146.5, 146.5, 'H4')]:
        ax.add_patch(patches.Circle((hx, hy), 5.5/2, facecolor='#161B22', edgecolor='#238636', linewidth=1.5, zorder=2))
        ax.add_patch(patches.Circle((hx, hy), 3.2/2, facecolor='#000000', edgecolor='#8B949E', linewidth=1, zorder=3))
        ax.text(hx, hy, f'{hname}\nM3 GND', color='#3FB950', fontsize=6.8, ha='center', va='center', fontweight='bold', zorder=4)

def draw_module_boxes(ax, layer_focus=None, alpha_factor=1.0):
    for m in modules:
        bx, by, bw, bh = m['box']
        is_focused = (layer_focus is None) or (m['layer'] == layer_focus) or (m['id'] in ['SW1', 'JST', 'PULLUPS'] and layer_focus == 'Top')
        
        alpha_bg = 0.50 * alpha_factor if is_focused else 0.12
        alpha_line = 0.90 * alpha_factor if is_focused else 0.20
        text_alpha = 1.0 if is_focused else 0.25
        
        card = patches.FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.2,rounding_size=0.8",
                                     facecolor=m['bg_color'], edgecolor=m['border_color'],
                                     linewidth=1.6 if is_focused else 0.7, alpha=alpha_bg, zorder=2)
        ax.add_patch(card)
        
        card_border = patches.FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.2,rounding_size=0.8",
                                            fill=False, edgecolor=m['border_color'],
                                            linewidth=1.6 if is_focused else 0.7, alpha=alpha_line, zorder=3)
        ax.add_patch(card_border)
        
        # IC chip simulation
        if 'ic_box' in m and is_focused:
            ix, iy, iw, ih = m['ic_box']
            ic_patch = patches.Rectangle((ix, iy), iw, ih, facecolor='#0B0F14', edgecolor='#484F58', linewidth=1.0, zorder=3)
            ax.add_patch(ic_patch)
            ax.text(ix + iw/2, iy + ih/2, m['ic_label'], color='#E6EDF3', fontsize=5.8, ha='center', va='center', fontweight='bold', zorder=4)
            
        # USB-C port on Beetle
        if m.get('extra_gfx') == 'usb' and is_focused:
            usb_patch = patches.Rectangle((121.0, 99.5), 8.0, 1.8, facecolor='#C9D1D9', edgecolor='#FFFFFF', linewidth=1.0, zorder=4)
            ax.add_patch(usb_patch)
            ax.text(125.0, 98.7, 'USB-C (Flush)', color='#58A6FF', fontsize=7.0, ha='center', va='bottom', fontweight='bold', zorder=5)
            
        # Header Badge Text
        hx, hy = m['header_pos']
        if is_focused or layer_focus is None:
            ax.text(hx, hy, m['name_ko'], color=m['badge_color'], fontsize=7.8, fontweight='bold', ha='center', va='center',
                    alpha=text_alpha, zorder=12,
                    bbox=dict(boxstyle="round,pad=0.18", fc="#0D1117", ec=m['border_color'], lw=0.9, alpha=0.92 * text_alpha))
            if m['sub_pos']:
                sx, sy = m['sub_pos']
                ax.text(sx, sy, m['name_sub'], color='#8B949E', fontsize=6.2, ha='center', va='center', alpha=text_alpha, zorder=12)

def draw_pads(ax, layer_filter=None):
    for p in pads:
        if p['ref'].startswith('MountingHole'):
            continue
        if layer_filter == 'F.Cu' and p['type'] == 'smd' and p['fp_layer'] != 'F.Cu':
            continue
        if layer_filter == 'B.Cu' and p['type'] == 'smd' and p['fp_layer'] != 'B.Cu':
            continue
            
        color = net_colors.get(p['net'], '#8B949E')
        
        if p['shape'] in ['circle', 'thru_hole']:
            ax.add_patch(patches.Circle((p['x'], p['y']), p['sx']/2, facecolor='#161B22', edgecolor=color, linewidth=1.4, zorder=6))
            if p['drill'] > 0:
                ax.add_patch(patches.Circle((p['x'], p['y']), p['drill']/2, facecolor='#000000', zorder=7))
        elif p['shape'] == 'rect':
            ax.add_patch(patches.Rectangle((p['x']-p['sx']/2, p['y']-p['sy']/2), p['sx'], p['sy'], facecolor='#161B22', edgecolor=color, linewidth=1.4, zorder=6))
            if p['drill'] > 0:
                ax.add_patch(patches.Circle((p['x'], p['y']), p['drill']/2, facecolor='#000000', zorder=7))
        else:
            ax.add_patch(patches.Rectangle((p['x']-p['sx']/2, p['y']-p['sy']/2), p['sx'], p['sy'], facecolor='#161B22', edgecolor=color, linewidth=1.1, zorder=6))
            
        if p['net'] > 0:
            short_net = net_names[p['net']].replace('I2C_', '').replace('GPS_', '')
            ax.text(p['x'], p['y']-0.05, short_net, color='#FFFFFF', fontsize=5.2, ha='center', va='center', fontweight='bold', zorder=8)

# Panel 1: Composite
ax1 = axes[0]
draw_base(ax1, "Panel 1: 전체 센서 배치 및 2층 배선 종합 투시도", "Top/Bottom 모든 부품 실장 위치와 X-Ray 입체 배선")
draw_module_boxes(ax1, layer_focus=None, alpha_factor=0.85)
draw_pads(ax1)

for s in segments:
    if s['layer'] == 'B.Cu':
        c = net_colors.get(s['net'], '#3498DB')
        ax1.plot([s['x1'], s['x2']], [s['y1'], s['y2']], color=c, linewidth=2.8, alpha=0.85, zorder=4, solid_capstyle='round')

for s in segments:
    if s['layer'] == 'F.Cu':
        c = net_colors.get(s['net'], '#FF3366')
        ax1.plot([s['x1'], s['x2']], [s['y1'], s['y2']], color=c, linewidth=2.5, alpha=0.95, zorder=5, solid_capstyle='round')

for v in vias:
    ax1.add_patch(patches.Circle((v['x'], v['y']), v['size']/2, facecolor='#FECA57', edgecolor='#FFFFFF', linewidth=1.2, zorder=9))
    ax1.add_patch(patches.Circle((v['x'], v['y']), v['drill']/2, facecolor='#000000', zorder=10))

# Panel 2: Front Layer
ax2 = axes[1]
draw_base(ax2, "Panel 2: 전면(Top) 센서 배치 및 F.Cu 전원/풀업 배선", "Beetle C6, BH1750 조도, SW1, 배터리, R3/R4 풀업")
draw_module_boxes(ax2, layer_focus='Top', alpha_factor=1.0)
draw_pads(ax2, 'F.Cu')

for s in segments:
    if s['layer'] == 'F.Cu':
        c = net_colors.get(s['net'], '#FF3366')
        ax2.plot([s['x1'], s['x2']], [s['y1'], s['y2']], color=c, linewidth=3.0, alpha=0.95, zorder=5, solid_capstyle='round')

for v in vias:
    ax2.add_patch(patches.Circle((v['x'], v['y']), v['size']/2, facecolor='#FECA57', edgecolor='#FFFFFF', linewidth=1.2, zorder=9))
    ax2.add_patch(patches.Circle((v['x'], v['y']), v['drill']/2, facecolor='#000000', zorder=10))

ax2.annotate("3.3V 주 전원선 (Top 레이어)\nBH1750 Pin 5 & MPU Pin 8 직결", xy=(136.5, 115.0), xytext=(142.5, 105.5),
             arrowprops=dict(arrowstyle="->", color="#FF3366", lw=1.5), fontsize=7.8, color="#FF6B6B", fontweight='bold', zorder=15,
             bbox=dict(boxstyle="round,pad=0.2", fc="#0D1117", ec="#FF3366", lw=0.9))
ax2.annotate("BAT 전원선 (X=125.0 스파인)", xy=(125.0, 118.0), xytext=(117.5, 126.0),
             arrowprops=dict(arrowstyle="->", color="#FECA57", lw=1.5), fontsize=7.8, color="#FECA57", fontweight='bold', zorder=15,
             bbox=dict(boxstyle="round,pad=0.2", fc="#0D1117", ec="#FECA57", lw=0.9))

# Panel 3: Back Layer
ax3 = axes[2]
draw_base(ax3, "Panel 3: 후면(Bottom) 센서 배치 및 B.Cu I2C/GPS 배선", "SHT45 온습도, GY-521 6축 IMU, ATGM336H GPS")
draw_module_boxes(ax3, layer_focus='Bottom', alpha_factor=1.0)
draw_pads(ax3, 'B.Cu')

for s in segments:
    if s['layer'] == 'B.Cu':
        c = net_colors.get(s['net'], '#3498DB')
        ax3.plot([s['x1'], s['x2']], [s['y1'], s['y2']], color=c, linewidth=3.0, alpha=0.95, zorder=5, solid_capstyle='round')

for v in vias:
    ax3.add_patch(patches.Circle((v['x'], v['y']), v['size']/2, facecolor='#FECA57', edgecolor='#FFFFFF', linewidth=1.2, zorder=9))
    ax3.add_patch(patches.Circle((v['x'], v['y']), v['drill']/2, facecolor='#000000', zorder=10))

ax3.annotate("I2C SCL 고속도로 (Y=130.0)\nMPU Pin 6, BH1750 Pin 3, SHT45 Pin 2", xy=(125.0, 130.0), xytext=(123.0, 134.5),
             arrowprops=dict(arrowstyle="->", color="#A55EEA", lw=1.5), fontsize=7.8, color="#D7BDE2", fontweight='bold', zorder=15,
             bbox=dict(boxstyle="round,pad=0.2", fc="#0D1117", ec="#A55EEA", lw=0.9))
ax3.annotate("I2C SDA 고속도로 (Y=125.0)\nMPU Pin 5, BH1750 Pin 2, SHT45 Pin 1", xy=(127.0, 125.0), xytext=(127.5, 120.5),
             arrowprops=dict(arrowstyle="->", color="#00D2D3", lw=1.5), fontsize=7.8, color="#80DEEA", fontweight='bold', zorder=15,
             bbox=dict(boxstyle="round,pad=0.2", fc="#0D1117", ec="#00D2D3", lw=0.9))
ax3.annotate("GPS UART 직결 (RX/TX 보정 완료)\nMCU핀 간격 정밀 통과 (비아 0개)", xy=(110.0, 109.5), xytext=(101.5, 103.5),
             arrowprops=dict(arrowstyle="->", color="#10AC84", lw=1.5), fontsize=7.8, color="#A3E4D7", fontweight='bold', zorder=15,
             bbox=dict(boxstyle="round,pad=0.2", fc="#0D1117", ec="#10AC84", lw=0.9))

# Legend
legend_elements = [
    patches.Patch(color=net_colors[2], label='Net 2: 3V3 전원선 (Top F.Cu)'),
    patches.Patch(color=net_colors[1], label='Net 1: GND 접지 버스'),
    patches.Patch(color=net_colors[5], label='Net 5: I2C_SDA (Bottom B.Cu)'),
    patches.Patch(color=net_colors[6], label='Net 6: I2C_SCL (Bottom B.Cu)'),
    patches.Patch(color=net_colors[7], label='Net 7: GPS_RX (Bottom B.Cu)'),
    patches.Patch(color=net_colors[8], label='Net 8: GPS_TX (Bottom B.Cu)'),
    patches.Patch(color=net_colors[4], label='Net 4: BAT (Top F.Cu)'),
    patches.Patch(color='#FECA57', label='Via (외경 0.8mm / 드릴 0.4mm)')
]
fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=9.2, frameon=True, facecolor='#161B22', edgecolor='#30363D')

plt.tight_layout(rect=[0, 0.05, 1, 0.96])
plt.suptitle("CarrierBoard Beetle ESP32-C6 EdgeUSB (50x50mm) - 센서 실장 위치 및 레이어별 정밀 배선 검증도",
             fontsize=15.5, fontweight='bold', color='#FFFFFF')

plt.savefig(OUT_IMG, dpi=300, facecolor='#0D1117')
plt.savefig(ARTIFACT_IMG, dpi=300, facecolor='#0D1117')
print(f"Refined and saved {OUT_IMG}")
