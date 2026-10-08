import cv2
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = "c:/Windows/Fonts/malgun.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

img_path = r"C:\Users\korea\.gemini\antigravity-ide\brain\96046e35-c490-4623-8dcc-08f815d0ba5f\.user_uploaded\media_1791435139683.jpg"
img = cv2.imread(img_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
h, w, _ = img_rgb.shape

fig, ax = plt.subplots(figsize=(11, 14), dpi=200)
ax.imshow(img_rgb)
ax.set_title("멀티미터 단계별 전원 측정 포인트 가이드", fontsize=16, fontweight='bold', pad=15, color='#0f5132')

# Ground Point Tip (Black probe)
ax.annotate("⚫ [검은색 프로브 (-)] 고정 위치\n네 모서리 나사 구멍 = GND 접지!", 
            xy=(160, 345), xytext=(220, 260),
            arrowprops=dict(facecolor='black', edgecolor='white', width=2, headwidth=7),
            fontsize=11, fontweight='bold', color='white', ha='center',
            bbox=dict(boxstyle="round,pad=0.4", fc="#212529", ec="white", lw=1.5))

# Point 1: Battery IN
ax.annotate("🔴 [Point 1] 배터리 직결 전압\n좌측 관통 홀 (3.7 ~ 4.2V)", 
            xy=(360, 775), xytext=(250, 900),
            arrowprops=dict(facecolor='red', edgecolor='black', width=2, headwidth=7),
            fontsize=10, fontweight='bold', color='white', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#dc3545", ec="white", lw=1.5))

# Point 2: MCU BAT (Right MCU socket, top pin 1)
ax.annotate("🔴 [Point 2] 스위치 통과 전압 (BAT)\n우측 MCU 소켓 맨 위 구멍\n(SW ON 시 3.7 ~ 4.2V)", 
            xy=(480, 335), xytext=(630, 270),
            arrowprops=dict(facecolor='orange', edgecolor='black', width=2, headwidth=7),
            fontsize=10, fontweight='bold', color='white', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#fd7e14", ec="white", lw=1.5))

# Point 3: 3V3 (Left MCU socket, pin 2)
ax.annotate("🔴 [Point 3] MCU LDO 출력 (3V3)\n좌측 MCU 소켓 위에서 2번째 구멍\n(★Beetle C6 장착 시 3.3V 출력!)", 
            xy=(295, 360), xytext=(150, 480),
            arrowprops=dict(facecolor='lime', edgecolor='black', width=2, headwidth=7),
            fontsize=10, fontweight='bold', color='black', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#20c997", ec="black", lw=1.5))

# Point 4: BH1750 3V3 pin
ax.annotate("🔴 [Point 4] 센서 전원선 (3V3)\nBH1750 소켓 맨 오른쪽 구멍\n(★정상 3.3V 확인 포인트)", 
            xy=(635, 530), xytext=(630, 620),
            arrowprops=dict(facecolor='deepskyblue', edgecolor='black', width=2, headwidth=7),
            fontsize=10, fontweight='bold', color='white', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#0d6efd", ec="white", lw=1.5))

ax.axis('off')
plt.tight_layout()
out_path = r"C:\Users\korea\.gemini\antigravity-ide\brain\96046e35-c490-4623-8dcc-08f815d0ba5f\multimeter_measure_guide.png"
plt.savefig(out_path, bbox_inches='tight')
print("Saved:", out_path)
