import numpy as np
import sys
sys.path.append('scratch')
from solve_zero_cross_routing import pads, dist_point_to_segment, seg_dist

# TOP LAYER (F.Cu) - Red
top = [
    # 1. Net 3: BAT+
    ("BAT+_1", 3, 122.0, 146.5, 122.0, 148.2),
    ("BAT+_2", 3, 122.0, 148.2, 114.5, 148.2),
    ("BAT+_3", 3, 114.5, 148.2, 114.5, 146.5),

    # 2. Net 4: BAT (SW1 Pin 2 to MCU Pin 1)
    # Clean vertical track down X=114.0 (clear of all MCU and GPS pads)
    ("BAT_1", 4, 116.0, 146.5, 114.0, 146.5),
    ("BAT_2", 4, 114.0, 146.5, 114.0, 102.66),
    ("BAT_3", 4, 114.0, 102.66, 116.11, 102.66),

    # 3. Net 5: I2C_SDA on Top Layer (Red)
    # MCU_L_6 (116.11, 115.36) to SHT_5 (118.33, 127.50)
    ("SDA_T1", 5, 116.11, 115.36, 118.33, 115.36),
    ("SDA_T2", 5, 118.33, 115.36, 118.33, 127.50), # into SHT_5!
    # SHT_5 to R3_1 (121.25, 142.0)
    ("SDA_T3", 5, 118.33, 127.50, 121.25, 127.50),
    ("SDA_T4", 5, 121.25, 127.50, 121.25, 142.0), # into R3_1!
    # SDA Highway across Top Layer along Y=131.0 to GY_4 (137.18) and BH_4 (145.29)
    ("SDA_T5", 5, 121.25, 131.0, 137.18, 131.0),
    ("SDA_T6", 5, 137.18, 131.0, 137.18, 127.50), # into GY_4!
    ("SDA_T7", 5, 137.18, 131.0, 145.29, 131.0),
    ("SDA_T8", 5, 145.29, 131.0, 145.29, 123.20), # into BH_4!

    # 4. Net 2: 3V3 on Top Layer
    # MCU_R_2 (133.89, 105.20) to BH_1 (137.67, 123.20)
    ("3V3_T1", 2, 133.89, 105.20, 137.67, 105.20),
    ("3V3_T2", 2, 137.67, 105.20, 137.67, 123.20),
    # Feed Pull-ups R4_2 (128.75, 142.0) and R3_2 (122.75, 142.0)
    # Route via Y=144.0 (above R3/R4 SMD pads, below SW1)
    ("3V3_T3", 2, 137.67, 123.20, 137.67, 144.0),
    ("3V3_T4", 2, 137.67, 144.0, 128.75, 144.0),
    ("3V3_T5", 2, 128.75, 144.0, 128.75, 142.0), # into R4_2!
    ("3V3_T6", 2, 128.75, 144.0, 122.75, 144.0),
    ("3V3_T7", 2, 122.75, 144.0, 122.75, 142.0), # into R3_2!

    # 5. Net 1: GND on Top Layer
    # MCU_R_1 (133.89, 102.66) to H2 (146.5, 103.5)
    ("GND_T1", 1, 133.89, 102.66, 146.5, 102.66),
    ("GND_T2", 1, 146.5, 102.66, 146.5, 103.5),
    # Along right perimeter to BH_5 (147.83, 123.2) and BH_2 (140.21, 123.2)
    ("GND_T3", 1, 146.5, 103.5, 148.5, 105.5),
    ("GND_T4", 1, 148.5, 105.5, 148.5, 123.2),
    ("GND_T5", 1, 148.5, 123.2, 147.83, 123.2), # into BH_5!
    ("GND_T6", 1, 148.5, 117.5, 140.21, 117.5),
    ("GND_T7", 1, 140.21, 117.5, 140.21, 123.2), # into BH_2!
    # J1_2 (124.0, 146.5) to H4 (146.5, 146.5)
    ("GND_T8", 1, 124.0, 146.5, 124.0, 148.5),
    ("GND_T9", 1, 124.0, 148.5, 144.5, 148.5),
    ("GND_T10", 1, 144.5, 148.5, 146.5, 146.5), # into H4!
]

# BOTTOM LAYER (B.Cu) - Blue
bot = [
    # 1. Net 7: GPS_RX on Bottom Layer
    # MCU_L_4 (116.11, 110.28) -> GPS_3 (107.41, 109.50)
    ("GPS_RX_1", 7, 116.11, 110.28, 107.41, 110.28),
    ("GPS_RX_2", 7, 107.41, 110.28, 107.41, 109.50),

    # 2. Net 8: GPS_TX on Bottom Layer
    # MCU_L_5 (116.11, 112.82) -> GPS_4 (109.95, 109.50)
    ("GPS_TX_1", 8, 116.11, 112.82, 109.95, 112.82),
    ("GPS_TX_2", 8, 109.95, 112.82, 109.95, 109.50),

    # 3. Net 6: I2C_SCL on Bottom Layer (Blue)
    # MCU_L_7 (116.11, 117.90) to SHT_4 (115.79, 127.50)
    ("SCL_B1", 6, 116.11, 117.90, 115.79, 117.90),
    ("SCL_B2", 6, 115.79, 117.90, 115.79, 127.50), # into SHT_4!
    # SCL Highway across Bottom Layer along Y=131.0 to GY_3 (134.64), BH_3 (142.75), R4_1 (127.25)
    ("SCL_B3", 6, 115.79, 127.50, 115.79, 131.0),
    ("SCL_B4", 6, 115.79, 131.0, 134.64, 131.0),
    ("SCL_B5", 6, 134.64, 131.0, 134.64, 127.50), # into GY_3!
    ("SCL_B6", 6, 134.64, 131.0, 142.75, 131.0),
    ("SCL_B7", 6, 142.75, 131.0, 142.75, 123.20), # into BH_3!
    ("SCL_B8", 6, 127.25, 131.0, 127.25, 142.0), # into R4_1!

    # 4. Net 2: 3V3 on Bottom Layer
    # MCU_R_2 (133.89, 105.20) to GY_1 (129.56, 127.50)
    ("3V3_B1", 2, 133.89, 105.20, 129.56, 105.20),
    ("3V3_B2", 2, 129.56, 105.20, 129.56, 127.50),
    # GY_1 to SHT_1 (108.17, 127.50) via Y=124.5 (corridor between MCU and SHT)
    ("3V3_B3", 2, 129.56, 127.50, 129.56, 124.5),
    ("3V3_B4", 2, 129.56, 124.5, 108.17, 124.5),
    ("3V3_B5", 2, 108.17, 124.5, 108.17, 127.50), # into SHT_1!
    # SHT_1 to GPS_1 (102.33, 109.50)
    ("3V3_B6", 2, 108.17, 124.5, 102.33, 124.5),
    ("3V3_B7", 2, 102.33, 124.5, 102.33, 109.50), # into GPS_1!

    # 5. Net 1: GND on Bottom Layer
    # MCU_L_2 (116.11, 105.20) to GPS_2 (104.87, 109.50) and H1 (103.5, 103.5)
    ("GND_B1", 1, 116.11, 105.20, 104.87, 105.20),
    ("GND_B2", 1, 104.87, 105.20, 104.87, 109.50), # into GPS_2!
    ("GND_B3", 1, 104.87, 105.20, 103.5, 103.83),
    ("GND_B4", 1, 103.5, 103.83, 103.5, 103.5), # into H1!
    # SHT_3 (113.25, 127.50) to H3 (103.5, 146.5) via Y=138.0
    ("GND_B5", 1, 113.25, 127.50, 113.25, 138.0),
    ("GND_B6", 1, 113.25, 138.0, 103.5, 138.0),
    ("GND_B7", 1, 103.5, 138.0, 103.5, 146.5), # into H3!
    # GY_2 (132.10, 127.50) and GY_7 (144.80, 127.50) to H4 (146.5, 146.5) via Y=138.0
    ("GND_B8", 1, 132.10, 127.50, 132.10, 138.0),
    ("GND_B9", 1, 132.10, 138.0, 144.80, 138.0),
    ("GND_B10", 1, 144.80, 138.0, 144.80, 127.50), # into GY_7!
    ("GND_B11", 1, 144.80, 138.0, 146.5, 138.0),
    ("GND_B12", 1, 146.5, 138.0, 146.5, 146.5), # into H4!
]

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

print(f"\nDRC Results: {len(errors)} errors found.")
for e in errors:
    print("  ->", e)

if len(errors) == 0:
    print("\nPERFECT! 100% CLEAN, ZERO-ERROR, AESTHETIC MASTER ROUTING!")
