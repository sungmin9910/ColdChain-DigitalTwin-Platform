import cv2
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Set Korean Font
font_path = "c:/Windows/Fonts/malgun.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()


# Load user photo rotated 90 CCW
photo = cv2.imread('scratch/photo_rot_ccw.jpg')
photo_rgb = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)

h, w, _ = photo_rgb.shape

fig, ax = plt.subplots(figsize=(10, 10), dpi=200)
ax.imshow(photo_rgb)
ax.set_title("실물 PCB 정방향 뷰 (현재 보고 계신 면: [뒷면 / Bottom])", fontsize=15, fontweight='bold', pad=15)

# Annotations
# 1. Top Edge USB
ax.annotate("기판 위쪽 (USB-C 포트 방향)", xy=(w*0.5, h*0.1), xytext=(w*0.5, h*0.03),
            arrowprops=dict(facecolor='cyan', edgecolor='black', width=2, headwidth=8),
            fontsize=12, fontweight='bold', color='cyan', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#111", ec="cyan", lw=1.5))

# 2. Beetle C6 solder joints
ax.annotate("Beetle ESP32-C6\n(앞면에 꽂고 뒷면 납땜 완료!)", xy=(w*0.4, h*0.25), xytext=(w*0.15, h*0.25),
            arrowprops=dict(facecolor='yellow', edgecolor='black', width=2, headwidth=8),
            fontsize=10, fontweight='bold', color='yellow', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#111", ec="yellow", lw=1.5))

# 3. GPS socket
ax.annotate("GPS 1x5 소켓\n(정상 장착 완료!)", xy=(w*0.75, h*0.18), xytext=(w*0.85, h*0.35),
            arrowprops=dict(facecolor='lime', edgecolor='black', width=2, headwidth=8),
            fontsize=10, fontweight='bold', color='lime', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#111", ec="lime", lw=1.5))

# 4. GY-521 socket hole
ax.annotate("GY-521 IMU (8핀 소켓 자리)", xy=(w*0.25, h*0.55), xytext=(w*0.2, h*0.7),
            arrowprops=dict(facecolor='orange', edgecolor='black', width=2, headwidth=8),
            fontsize=10, fontweight='bold', color='orange', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#111", ec="orange", lw=1.5))

# 5. SHT45 socket hole
ax.annotate("SHT45 온습도 (5핀 소켓 자리)", xy=(w*0.7, h*0.55), xytext=(w*0.75, h*0.7),
            arrowprops=dict(facecolor='magenta', edgecolor='black', width=2, headwidth=8),
            fontsize=10, fontweight='bold', color='magenta', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#111", ec="magenta", lw=1.5))

# 6. Battery holes
ax.annotate("배터리 구멍 (기판 아래쪽)", xy=(w*0.5, h*0.83), xytext=(w*0.5, h*0.93),
            arrowprops=dict(facecolor='white', edgecolor='black', width=2, headwidth=8),
            fontsize=11, fontweight='bold', color='white', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#111", ec="white", lw=1.5))

ax.axis('off')
plt.tight_layout()
plt.savefig('scratch/guide_your_board.png', bbox_inches='tight')
print("Saved scratch/guide_your_board.png")
