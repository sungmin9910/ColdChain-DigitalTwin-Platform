import numpy as np
import sys
sys.path.append('scratch')
from solve_zero_cross_routing import pads, dist_point_to_segment, seg_dist

def run_drc(top, bot):
    all_traces = [("F.Cu", t) for t in top] + [("B.Cu", t) for t in bot]
    errors = []

    for layer, (tname, tnet, x1, y1, x2, y2) in all_traces:
        for pname, pnet, px, py, pr in pads:
            if tnet != pnet and pnet != 0:
                if pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2'] and layer != "F.Cu":
                    continue
                d = dist_point_to_segment(px, py, x1, y1, x2, y2)
                if d < pr + 0.20:
                    errors.append(f"PAD ERROR {layer}: {tname}(Net {tnet}) close to {pname}(Net {pnet}), d={d:.3f}, req={pr+0.20:.3f}")

    for layer_name in ["F.Cu", "B.Cu"]:
        traces_l = [t for l, t in all_traces if l == layer_name]
        for i in range(len(traces_l)):
            for j in range(i+1, len(traces_l)):
                t1 = traces_l[i]
                t2 = traces_l[j]
                if t1[1] != t2[1]:
                    d = seg_dist(t1[2], t1[3], t1[4], t1[5], t2[2], t2[3], t2[4], t2[5])
                    if d < 0.20:
                        errors.append(f"TRACK ERROR {layer_name}: {t1[0]}(Net {t1[1]}) and {t2[0]}(Net {t2[1]}) close/cross! d={d:.3f}")

    return errors

# -------------------------------------------------------------
# TOP LAYER (F.Cu) - Red
# Signals on Top:
# - BAT+ (Net 3)
# - BAT (Net 4)
# - I2C_SDA (Net 5) -> 100% on Top Layer!
# - 3V3 (Net 2) -> MCU to BH1750 and Pull-ups
# - GND (Net 1) -> MCU Right to H2, BH1750, H4
# -------------------------------------------------------------
top = [
    # 1. BAT+ (J1 to SW1)
    ("BAT+_1", 3, 122.0, 146.5, 122.0, 148.2),
    ("BAT+_2", 3, 122.0, 148.2, 114.5, 148.2),
    ("BAT+_3", 3, 114.5, 148.2, 114.5, 146.5),

    # 2. BAT (SW1 Pin 2 to MCU Pin 1)
    # Straight vertical highway down X=124.5
    ("BAT_1", 4, 116.0, 146.5, 116.0, 145.0),
    ("BAT_2", 4, 116.0, 145.0, 124.5, 145.0),
    ("BAT_3", 4, 124.5, 145.0, 124.5, 102.66),
    ("BAT_4", 4, 124.5, 102.66, 116.11, 102.66),

    # 3. I2C_SDA on Top Layer (Red)
    # MCU_L_6 (116.11, 115.36) to SHT_5 (118.33, 127.50)
    ("SDA_T1", 5, 116.11, 115.36, 118.33, 115.36),
    ("SDA_T2", 5, 118.33, 115.36, 118.33, 127.50), # into SHT_5!
    # SHT_5 to R3_1 (121.25, 142.0)
    ("SDA_T3", 5, 118.33, 127.50, 121.25, 127.50),
    ("SDA_T4", 5, 121.25, 127.50, 121.25, 142.0), # into R3_1!
    # SDA Highway across Top Layer along Y=133.0 to GY_4 (137.18) and BH_4 (145.29)
    # Notice: at Y=133.0, BAT is at X=124.5!
    # To cross X=124.5 on Top Layer without hitting BAT:
    # Route via Y=146.0 (above SW1/BAT) or via a Via!
    # BUT wait: with 2 clean vias (at 122.0, 133.0 and 126.0, 133.0), SDA can hop to Bottom for 4mm to cross BAT!
    # OR: Why not route SDA along Y=101.5 or Y=121.5?
    # Wait, where does BAT end?
    # BAT ends at Y=102.66.
    # What if SDA crosses BAT via a clean 4mm bridge on B.Cu?
    # Let's check: at (122.5, 133.0) to (126.5, 133.0), on B.Cu it's 100% empty!
    # That is ONE single, neat via pair!
]

# Let's test a 100% clean orthogonal layout and print results
print("Checking architecture...")
