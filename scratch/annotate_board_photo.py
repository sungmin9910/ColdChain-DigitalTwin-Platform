import cv2
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Font setting
font_path = "c:/Windows/Fonts/malgun.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

img_path = r"C:\Users\korea\.gemini\antigravity-ide\brain\96046e35-c490-4623-8dcc-08f815d0ba5f\.user_uploaded\media_1791435139683.jpg"
img = cv2.imread(img_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

h, w, _ = img_rgb.shape

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 11), dpi=200, gridspec_kw={'width_ratios': [1.2, 1]})

# === Left: Full Annotated View ===
ax1.imshow(img_rgb)
ax1.set_title("실물 PCB 정밀 해설 (현재 사진: [Top면 / 앞면])", fontsize=16, fontweight='bold', pad=15, color='#0a3622')

# Orientation
ax1.text(w * 0.5, 230, "▲ 기판 위쪽 (DFRobot Beetle ESP32-C6 USB 포트 방향) ▲", 
         fontsize=11, fontweight='bold', color='white', ha='center',
         bbox=dict(boxstyle="round,pad=0.4", fc="#0d6efd", ec="white", lw=1.5))

# Beetle Sockets
ax1.annotate("Beetle ESP32-C6 Mini 소켓\n(8핀 x 2열 - 앞면 실장)", 
             xy=(385, 420), xytext=(385, 290),
             arrowprops=dict(facecolor='#0dcaf0', edgecolor='black', width=2, headwidth=7),
             fontsize=10, fontweight='bold', color='black', ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#cff4fc", ec="#0dcaf0", lw=1.5))

# BH1750 Socket
ax1.annotate("BH1750 조도 센서 소켓\n(앞면 가로 실장)\n★주의: 센서 파란 뒷면이 위로 오게 장착", 
             xy=(580, 530), xytext=(630, 460),
             arrowprops=dict(facecolor='#198754', edgecolor='black', width=2, headwidth=7),
             fontsize=9, fontweight='bold', color='white', ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#198754", ec="white", lw=1.2))

# Bottom Joints
ax1.annotate("GPS (ATGM336H) 납땜부\n(소켓은 뒷면에 실장됨)", 
             xy=(195, 405), xytext=(140, 480),
             arrowprops=dict(facecolor='#ffc107', edgecolor='black', width=2, headwidth=7),
             fontsize=9, fontweight='bold', color='black', ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#fff3cd", ec="#ffc107", lw=1.2))

ax1.annotate("SHT45 온습도 납땜부\n(소켓은 뒷면에 실장됨)", 
             xy=(260, 585), xytext=(150, 660),
             arrowprops=dict(facecolor='#fd7e14', edgecolor='black', width=2, headwidth=7),
             fontsize=9, fontweight='bold', color='white', ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#fd7e14", ec="white", lw=1.2))

ax1.annotate("GY-521 IMU 납땜부\n(소켓은 뒷면에 실장됨)", 
             xy=(530, 580), xytext=(630, 660),
             arrowprops=dict(facecolor='#d63384', edgecolor='black', width=2, headwidth=7),
             fontsize=9, fontweight='bold', color='white', ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#d63384", ec="white", lw=1.2))

# Bottom Box highlight
rect_box = plt.Rectangle((250, 720), 180, 100, linewidth=2.5, edgecolor='#dc3545', facecolor='none', linestyle='--')
ax1.add_patch(rect_box)
ax1.text(340, 835, "▼ [전원 & 배터리 구역 확대] ▼", fontsize=10, fontweight='bold', color='#dc3545', ha='center')

ax1.axis('off')

# === Right: Zoomed Battery & Switch Area ===
# Crop around (250, 720) to (430, 820)
crop_y1, crop_y2 = 710, 830
crop_x1, crop_x2 = 250, 430
cropped = img_rgb[crop_y1:crop_y2, crop_x1:crop_x2]

ax2.imshow(cropped)
ax2.set_title("하단 전원 스위치(SW1) 및 배터리 홀 정밀 확대", fontsize=15, fontweight='bold', pad=15, color='#842029')

# In cropped coordinates:
# SW1 pads approx at x=280..315, y=778 -> in crop: x=30..65, y=68
# Battery holes approx at x=360, 384, y=775 -> in crop: x=110, 134, y=65

# SW1 Pad 1, 2, 3
ax2.annotate("SW1 1번\n(BAT+ 연결)", xy=(37, 68), xytext=(20, 20),
             arrowprops=dict(facecolor='#0dcaf0', edgecolor='black', width=1.5, headwidth=5),
             fontsize=9, fontweight='bold', color='black', ha='center',
             bbox=dict(boxstyle="round,pad=0.2", fc="#cff4fc", ec="#0dcaf0", lw=1))

ax2.annotate("SW1 2번\n(MCU BAT)", xy=(51, 68), xytext=(55, 105),
             arrowprops=dict(facecolor='#20c997', edgecolor='black', width=1.5, headwidth=5),
             fontsize=9, fontweight='bold', color='black', ha='center',
             bbox=dict(boxstyle="round,pad=0.2", fc="#d1e7dd", ec="#20c997", lw=1))

ax2.annotate("SW1 3번\n(미연결 NC)", xy=(65, 68), xytext=(75, 20),
             arrowprops=dict(facecolor='#6c757d', edgecolor='black', width=1.5, headwidth=5),
             fontsize=9, fontweight='bold', color='white', ha='center',
             bbox=dict(boxstyle="round,pad=0.2", fc="#6c757d", ec="white", lw=1))

# BAT+ hole (Left hole)
ax2.annotate("BAT+ [빨간선 +]\n★왼쪽 홀!", xy=(110, 65), xytext=(110, 110),
             arrowprops=dict(facecolor='#dc3545', edgecolor='black', width=2, headwidth=6),
             fontsize=10, fontweight='bold', color='white', ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#dc3545", ec="white", lw=1.5))

# GND hole (Right hole)
ax2.annotate("GND [검은선 -]\n★오른쪽 홀!", xy=(134, 65), xytext=(155, 25),
             arrowprops=dict(facecolor='#212529', edgecolor='black', width=2, headwidth=6),
             fontsize=10, fontweight='bold', color='white', ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#212529", ec="white", lw=1.5))

ax2.axis('off')

plt.tight_layout()
out_path = r"C:\Users\korea\.gemini\antigravity-ide\brain\96046e35-c490-4623-8dcc-08f815d0ba5f\annotated_board_guide.png"
plt.savefig(out_path, bbox_inches='tight')
print("Successfully regenerated:", out_path)
