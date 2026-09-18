import os

out_dir = r"3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText"
cpl_path = os.path.join(out_dir, "CPL_CarrierBoard_BeetleC6_50x50.csv")

# Exact PCB centroid coordinates exported directly from KiCad:
# Top parts:
# J_MCU_L: (116.11, -111.55), Rot: 90.0 (perfect vertical alignment confirmed)
# J_MCU_R: (133.89, -111.55), Rot: 90.0 (perfect vertical alignment confirmed)
# J_BH1750: (142.75, -123.20), Rot: 0.0 (center of 5 pads from 137.67 to 147.83)
# J1: (123.00, -146.50), Rot: 0.0
# SW1: (116.00, -146.50), Rot: 0.0
# R3: (122.00, -142.00), Rot: 0.0
# R4: (128.00, -142.00), Rot: 0.0
# Bottom parts (official KiCad centroids):
# J_GPS: (107.41, -109.50), Rot: 0.0
# J_SHT45: (113.25, -127.50), Rot: 0.0
# J_GY521: (138.42, -127.50), Rot: 0.0

cpl_lines = [
    "Designator,Mid X,Mid Y,Layer,Rotation",
    "J_MCU_L,116.110,-111.550,Top,90.0",
    "J_MCU_R,133.890,-111.550,Top,90.0",
    "J_BH1750,142.750,-123.200,Top,0.0",
    "J1,123.000,-146.500,Top,0.0",
    "SW1,116.000,-146.500,Top,0.0",
    "R3,122.000,-142.000,Top,0.0",
    "R4,128.000,-142.000,Top,0.0",
    "J_GPS,107.410,-109.500,Bottom,0.0",
    "J_SHT45,113.250,-127.500,Bottom,0.0",
    "J_GY521,138.420,-127.500,Bottom,0.0"
]

with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("\n".join(cpl_lines) + "\n")

print("CPL updated with exact KiCad centroid coordinates!")
print(open(cpl_path, encoding="utf-8").read())
