import os

out_dir = r"3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText"
cpl_path = os.path.join(out_dir, "CPL_CarrierBoard_BeetleC6_50x50.csv")

# Refined CPL data with corrected rotations and mirrored bottom coordinates
# 1. J_MCU_L, J_MCU_R: Rotation = 90.0 (Vertical to match Beetle pins)
# 2. J_BH1750: Offset X by -5.08 to match Pin 1 origin of C50950
# 3. Bottom parts: Mirrored X (250.0 - X) so JLCPCB's bottom flip lands them exactly on the holes!

cpl_lines = [
    "Designator,Mid X,Mid Y,Layer,Rotation",
    "J_MCU_L,116.110,-111.550,Top,90.0",
    "J_MCU_R,133.890,-111.550,Top,90.0",
    "J_BH1750,137.670,-123.200,Top,0.0",
    "J1,123.000,-146.500,Top,0.0",
    "SW1,116.000,-146.500,Top,0.0",
    "R3,122.000,-142.000,Top,0.0",
    "R4,128.000,-142.000,Top,0.0",
    "J_GPS,142.590,-109.500,Bottom,0.0",
    "J_SHT45,136.750,-127.500,Bottom,0.0",
    "J_GY521,111.580,-127.500,Bottom,0.0"
]

with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("\n".join(cpl_lines) + "\n")

print("Generated refined CPL file successfully!")
print(open(cpl_path, encoding="utf-8").read())
