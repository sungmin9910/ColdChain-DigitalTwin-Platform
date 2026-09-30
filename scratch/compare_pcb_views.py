import cv2
import matplotlib.pyplot as plt
import numpy as np

# Load user photo
photo = cv2.imread(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\.user_uploaded\media_1790766568838.jpg')

# The original photo is 768x1024. Let's inspect rotations:
# rot 90 counter-clockwise:
rot_ccw = cv2.rotate(photo, cv2.ROTATE_90_COUNTERCLOCKWISE)
# rot 90 clockwise:
rot_cw = cv2.rotate(photo, cv2.ROTATE_90_CLOCKWISE)

render_top = cv2.imread('3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/render_top_pcb.png')
render_bot = cv2.imread('3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/render_bottom_pcb.png')

fig, axes = plt.subplots(2, 2, figsize=(16, 16), dpi=150)

axes[0, 0].imshow(cv2.cvtColor(rot_ccw, cv2.COLOR_BGR2RGB))
axes[0, 0].set_title("User Photo (Rotated 90° CCW)", fontsize=14, fontweight='bold', color='blue')
axes[0, 0].axis('off')

axes[0, 1].imshow(cv2.cvtColor(rot_cw, cv2.COLOR_BGR2RGB))
axes[0, 1].set_title("User Photo (Rotated 90° CW)", fontsize=14, fontweight='bold', color='blue')
axes[0, 1].axis('off')

axes[1, 0].imshow(cv2.cvtColor(render_top, cv2.COLOR_BGR2RGB))
axes[1, 0].set_title("PCB Design Render (TOP - Front)", fontsize=14, fontweight='bold', color='green')
axes[1, 0].axis('off')

axes[1, 1].imshow(cv2.cvtColor(render_bot, cv2.COLOR_BGR2RGB))
axes[1, 1].set_title("PCB Design Render (BOTTOM - Back)", fontsize=14, fontweight='bold', color='purple')
axes[1, 1].axis('off')

plt.tight_layout()
plt.savefig('scratch/pcb_photo_comparison.png', bbox_inches='tight')
print("Saved scratch/pcb_photo_comparison.png")
