import os
import re

pcb_path = r"3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText\CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb"
out_dir = r"3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText"

with open(pcb_path, "r", encoding="utf-8") as f:
    text = f.read()

# Specific layer mapping based on our design:
# Top: J_MCU_L, J_MCU_R, J_BH1750, J1, SW1, R3, R4
# Bottom: J_GPS, J_SHT45, J_GY521
layer_map = {
    'J_MCU_L': 'Top',
    'J_MCU_R': 'Top',
    'J_BH1750': 'Top',
    'J1': 'Top',
    'SW1': 'Top',
    'R3': 'Top',
    'R4': 'Top',
    'J_GPS': 'Bottom',
    'J_SHT45': 'Bottom',
    'J_GY521': 'Bottom'
}

parts_info = {
    'J_MCU_L': {'comment': '1x8P Female Header 2.54mm', 'footprint': 'PinHeader_1x08_P2.54mm_Vertical', 'lcsc': 'C225484'},
    'J_MCU_R': {'comment': '1x8P Female Header 2.54mm', 'footprint': 'PinHeader_1x08_P2.54mm_Vertical', 'lcsc': 'C225484'},
    'J_BH1750': {'comment': '1x5P Female Header 2.54mm', 'footprint': 'PinHeader_1x05_P2.54mm_Horizontal', 'lcsc': 'C2897379'},
    'J_GPS': {'comment': '1x5P Female Header 2.54mm', 'footprint': 'PinHeader_1x05_P2.54mm_Horizontal', 'lcsc': 'C2897379'},
    'J_SHT45': {'comment': '1x5P Female Header 2.54mm', 'footprint': 'PinHeader_1x05_P2.54mm_Horizontal', 'lcsc': 'C2897379'},
    'J_GY521': {'comment': '1x8P Female Header 2.54mm', 'footprint': 'PinHeader_1x08_P2.54mm_Horizontal', 'lcsc': 'C225484'},
    'R3': {'comment': '4.7k 1% 0603', 'footprint': 'R_0603_1608Metric', 'lcsc': 'C23163'},
    'R4': {'comment': '4.7k 1% 0603', 'footprint': 'R_0603_1608Metric', 'lcsc': 'C23163'},
    'SW1': {'comment': 'SW_SPDT_PCM12', 'footprint': 'SW_SPDT_PCM12', 'lcsc': 'C318884'},
    'J1': {'comment': 'JST-PH-2P 2.0mm', 'footprint': 'JST_PH_S2B-PH-K_1x02_P2.00mm', 'lcsc': 'C131337'}
}

# Parse positions from kicad_pcb
fp_blocks = re.findall(r'\(footprint\s+"([^"]+)"\s+\(layer\s+"([^"]+)"\)\s+\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)(.*?)\n\t\)', text, re.DOTALL)

cpl_rows = ["Designator,Mid X,Mid Y,Layer,Rotation"]

for fp_name, fp_layer, x_str, y_str, rot_str, body in fp_blocks:
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', body)
    ref = ref_m.group(1) if ref_m else ""
    if ref in parts_info:
        layer = layer_map.get(ref, "Top")
        rot = float(rot_str) if rot_str else 0.0
        # JLCPCB uses positive X, and negative Y relative to board origin, or absolute coordinates
        # Standard KiCad CPL output format:
        cpl_rows.append(f"{ref},{float(x_str):.3f},{-float(y_str):.3f},{layer},{rot:.1f}")

# Group BOM
grouped = {}
for ref, info in parts_info.items():
    lcsc = info['lcsc']
    if lcsc not in grouped:
        grouped[lcsc] = {'comment': info['comment'], 'footprint': info['footprint'], 'refs': []}
    grouped[lcsc]['refs'].append(ref)

bom_rows = ["Comment,Designator,Footprint,LCSC Part #"]
for lcsc, data in grouped.items():
    refs_str = " ".join(data['refs']) if len(data['refs']) > 1 else data['refs'][0]
    bom_rows.append(f'"{data["comment"]}","{refs_str}","{data["footprint"]}","{lcsc}"')

cpl_path = os.path.join(out_dir, "CPL_CarrierBoard_BeetleC6_50x50.csv")
bom_path = os.path.join(out_dir, "BOM_CarrierBoard_BeetleC6_50x50.csv")

with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("\n".join(cpl_rows) + "\n")

with open(bom_path, "w", encoding="utf-8") as f:
    f.write("\n".join(bom_rows) + "\n")

print("Generated BOM and CPL successfully!")
print("--- BOM Content ---")
print(open(bom_path, encoding="utf-8").read())
print("--- CPL Content ---")
print(open(cpl_path, encoding="utf-8").read())
