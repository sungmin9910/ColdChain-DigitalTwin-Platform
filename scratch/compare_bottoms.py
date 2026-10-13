import cv2
import matplotlib.pyplot as plt
import numpy as np

# Load render_bottom_pcb.png
render_bot = cv2.imread('3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/render_bottom_pcb.png')
render_bot_rgb = cv2.cvtColor(render_bot, cv2.COLOR_BGR2RGB)

# Load user photo rotated 180 (so USB is top, matching render_bottom_pcb.png)
user_bot = cv2.imread('scratch/bottom_rot180.jpg')
user_bot_rgb = cv2.cvtColor(user_bot, cv2.COLOR_BGR2RGB)

fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=150)

axes[0].imshow(render_bot_rgb)
axes[0].set_title("PCB Design Render (BOTTOM View)", fontsize=14, fontweight='bold')

axes[1].imshow(user_bot_rgb)
axes[1].set_title("User Board (Rotated to match orientation)", fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('scratch/side_by_side_bottom.png', bbox_inches='tight')
print("Saved scratch/side_by_side_bottom.png")
