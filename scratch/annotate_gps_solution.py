import cv2
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

font_path = "c:/Windows/Fonts/malgun.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

gps_img = cv2.imread('scratch/gps_exact.png')
gps_rgb = cv2.cvtColor(gps_img, cv2.COLOR_BGR2RGB)
h, w, _ = gps_rgb.shape

fig, axes = plt.subplots(1, 2, figsize=(16, 9), dpi=150)

# Left: Current Wrong State
axes[0].imshow(gps_rgb)
axes[0].set_title("[현재 상태] GPS 모듈 180도 역방향 체결 (전원 0V 미인가)", fontsize=14, fontweight='bold', color='red', pad=12)

labels_socket = ["소켓: NC (5번)", "소켓: GPIO 17 (4번)\n(GPS_RX)", "소켓: GPIO 16 (3번)\n(GPS_TX)", "소켓: GND (2번)", "소켓: 3.3V (1번)"]
labels_module = ["모듈: VCC\n(LDO측)", "모듈: GND", "모듈: TXD", "모듈: RXD", "모듈: PPS\n(배터리측)"]

xs = np.linspace(w*0.12, w*0.88, 5)
for i, x in enumerate(xs):
    axes[0].annotate(f"{labels_socket[i]}\n▲\n{labels_module[i]}", xy=(x, h*0.15), xytext=(x, h*0.65),
                     arrowprops=dict(facecolor='red', edgecolor='black', width=1.5, headwidth=6),
                     fontsize=8.5, fontweight='bold', color='white', ha='center',
                     bbox=dict(boxstyle="round,pad=0.25", fc="#880000", ec="red", lw=1.2))

axes[0].text(w*0.5, h*0.95, "[원인 분석] 모듈 VCC가 소켓 NC(미연결)에 꽂혀 전원 0V -> UART 침묵", 
             fontsize=10.5, fontweight='bold', color='yellow', ha='center',
             bbox=dict(boxstyle="round,pad=0.35", fc="#222", ec="yellow"))
axes[0].axis('off')

# Right: Flipped 180
gps_flipped = cv2.flip(gps_rgb, 1)
axes[1].imshow(gps_flipped)
axes[1].set_title("[해결 방법] 모듈을 180도 뒤집어 체결 (정방향 정상화)", fontsize=14, fontweight='bold', color='green', pad=12)

labels_correct = [
    "소켓: NC (5번)\n▲\n모듈: PPS",
    "소켓: GPIO 17 (4번)\n▲\n모듈: RXD",
    "소켓: GPIO 16 (3번)\n▲\n모듈: TXD",
    "소켓: GND (2번)\n▲\n모듈: GND",
    "소켓: 3.3V (1번)\n▲\n모듈: VCC"
]

for i, x in enumerate(xs):
    axes[1].annotate(labels_correct[i], xy=(x, h*0.15), xytext=(x, h*0.65),
                     arrowprops=dict(facecolor='lime', edgecolor='black', width=1.5, headwidth=6),
                     fontsize=8.5, fontweight='bold', color='white', ha='center',
                     bbox=dict(boxstyle="round,pad=0.25", fc="#005500", ec="lime", lw=1.2))

axes[1].text(w*0.5, h*0.95, "[조치 방법] 모듈을 뽑아서 뒷면(글씨면)이 위를 향하게 꽂으시면 즉시 정상 동작!", 
             fontsize=10.5, fontweight='bold', color='lime', ha='center',
             bbox=dict(boxstyle="round,pad=0.35", fc="#222", ec="lime"))
axes[1].axis('off')

plt.tight_layout()
plt.savefig('scratch/gps_orientation_guide.png', bbox_inches='tight')
plt.savefig(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\gps_orientation_guide.png', bbox_inches='tight')
print("Successfully regenerated clean gps_orientation_guide.png")
