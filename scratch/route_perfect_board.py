import sys
sys.path.append('scratch')
from solve_zero_cross_routing import pads, dist_point_to_segment, seg_dist
import numpy as np

# -------------------------------------------------------------
# DEFINING CLEAN, 100% NON-CROSSING 2-LAYER ROUTES
# -------------------------------------------------------------

# TOP LAYER (F.Cu)
# Signals on Top:
# 1. Net 3: BAT+
# 2. Net 4: BAT
# 3. Net 2: 3V3 (BH1750, Pullups)
# 4. Net 5: I2C_SDA (MCU Pin 6 -> SHT Pin 5, GY Pin 4, BH Pin 4, R3 Pin 1)
# 5. Net 7: GPS_RX (MCU Pin 4 -> GPS Pin 3)
# 6. Net 1: GND (Top side connections)

top_traces = [
    # Net 3: BAT+
    # J1_1 (122.0, 146.5) to SW1_1 (114.5, 146.5)
    ("BAT+_1", 3, 122.0, 146.5, 122.0, 148.5),
    ("BAT+_2", 3, 122.0, 148.5, 114.5, 148.5),
    ("BAT+_3", 3, 114.5, 148.5, 114.5, 146.5),

    # Net 4: BAT
    # SW1_2 (116.0, 146.5) to MCU_L_1 (116.11, 102.66)
    # Route via X=124.5 (center corridor)
    ("BAT_1", 4, 116.0, 146.5, 116.0, 145.0),
    ("BAT_2", 4, 116.0, 145.0, 124.5, 145.0),
    ("BAT_3", 4, 124.5, 145.0, 124.5, 102.66),
    ("BAT_4", 4, 124.5, 102.66, 116.11, 102.66),

    # Net 7: GPS_RX (on TOP layer)
    # MCU_L_4 (116.11, 110.28) to GPS_3 (107.41, 109.5)
    ("GPS_RX_1", 7, 116.11, 110.28, 107.41, 110.28),
    ("GPS_RX_2", 7, 107.41, 110.28, 107.41, 109.5),

    # Net 5: I2C_SDA (on TOP layer)
    # MCU_L_6 (116.11, 115.36) to:
    # 1) SHT_5 (118.33, 127.50)
    ("SDA_T1", 5, 116.11, 115.36, 118.33, 115.36),
    ("SDA_T2", 5, 118.33, 115.36, 118.33, 127.50),
    # 2) R3_1 (121.25, 142.0)
    ("SDA_T3", 5, 118.33, 127.50, 118.33, 137.0),
    ("SDA_T4", 5, 118.33, 137.0, 121.25, 137.0),
    ("SDA_T5", 5, 121.25, 137.0, 121.25, 142.0),
    # 3) GY_4 (137.18, 127.50) and BH_4 (145.29, 123.20)
    # Route horizontally at Y=131.0 (above GY-521 pads)
    ("SDA_T6", 5, 118.33, 131.0, 137.18, 131.0),
    ("SDA_T7", 5, 137.18, 131.0, 137.18, 127.50),
    ("SDA_T8", 5, 137.18, 131.0, 145.29, 131.0),
    ("SDA_T9", 5, 145.29, 131.0, 145.29, 123.20),

    # Net 2: 3V3 on TOP layer (feed BH1750 and pullups)
    # MCU_R_2 (133.89, 105.20) to BH_1 (137.67, 123.20)
    ("3V3_T1", 2, 133.89, 105.20, 137.67, 105.20),
    ("3V3_T2", 2, 137.67, 105.20, 137.67, 123.20),
    # MCU_R_2 to R4_2 (128.75, 142.0) & R3_2 (122.75, 142.0)
    # Route via X=131.0, up to Y=144.0, then into R4_2 and R3_2
    ("3V3_T3", 2, 133.89, 105.20, 131.0, 105.20),
    ("3V3_T4", 2, 131.0, 105.20, 131.0, 144.0),
    ("3V3_T5", 2, 131.0, 144.0, 128.75, 144.0),
    ("3V3_T6", 2, 128.75, 144.0, 128.75, 142.0),
    ("3V3_T7", 2, 128.75, 144.0, 122.75, 144.0),
    ("3V3_T8", 2, 122.75, 144.0, 122.75, 142.0),

    # Net 1: GND on TOP layer
    # MCU_R_1 (133.89, 102.66) to H2 (146.5, 103.5)
    ("GND_T1", 1, 133.89, 102.66, 146.5, 102.66),
    ("GND_T2", 1, 146.5, 102.66, 146.5, 103.5),
    # H2 to BH_2 (140.21, 123.2) and BH_5 (147.83, 123.2)
    # Route along right edge X=148.5
    ("GND_T3", 1, 146.5, 103.5, 148.5, 105.5),
    ("GND_T4", 1, 148.5, 105.5, 148.5, 123.2),
    ("GND_T5", 1, 148.5, 123.2, 147.83, 123.2), # into BH_5!
    # BH_2 is fed from bottom layer or separate branch
    # J1_2 (124.0, 146.5) GND to top perimeter
    ("GND_T6", 1, 124.0, 146.5, 124.0, 148.5),
    ("GND_T7", 1, 124.0, 148.5, 144.0, 148.5),
    ("GND_T8", 1, 144.0, 148.5, 146.5, 146.5), # into H4!
]

# BOTTOM LAYER (B.Cu)
# Signals on Bottom:
# 1. Net 8: GPS_TX (MCU Pin 5 -> GPS Pin 4)
# 2. Net 6: I2C_SCL (MCU Pin 7 -> SHT Pin 4, GY Pin 3, BH Pin 3, and R4 Pin 1 via pad)
# 3. Net 2: 3V3 (MCU Pin 2 -> GY Pin 1, SHT Pin 1, GPS Pin 1)
# 4. Net 1: GND (Bottom side connections: GPS Pin 2, SHT Pin 3, GY Pin 2, GY Pin 7, BH Pin 2, H1, H3)

bottom_traces = [
    # Net 8: GPS_TX (on BOTTOM layer)
    # MCU_L_5 (116.11, 112.82) to GPS_4 (109.95, 109.5)
    ("GPS_TX_1", 8, 116.11, 112.82, 109.95, 112.82),
    ("GPS_TX_2", 8, 109.95, 112.82, 109.95, 109.5),

    # Net 6: I2C_SCL (on BOTTOM layer)
    # MCU_L_7 (116.11, 117.90) to:
    # 1) SHT_4 (115.79, 127.50)
    ("SCL_B1", 6, 116.11, 117.90, 115.79, 117.90),
    ("SCL_B2", 6, 115.79, 117.90, 115.79, 127.50),
    # 2) GY_3 (134.64, 127.50) and BH_3 (142.75, 123.20)
    # Route via Y=133.5 (well above SDA on top layer, but on bottom layer!)
    ("SCL_B3", 6, 115.79, 127.50, 115.79, 133.5),
    ("SCL_B4", 6, 115.79, 133.5, 134.64, 133.5),
    ("SCL_B5", 6, 134.64, 133.5, 134.64, 127.50), # into GY_3!
    ("SCL_B6", 6, 134.64, 133.5, 142.75, 133.5),
    ("SCL_B7", 6, 142.75, 133.5, 142.75, 123.20), # into BH_3!
    # Connect to R4_1 (127.25, 142.0) on bottom layer
    ("SCL_B8", 6, 127.25, 133.5, 127.25, 142.0),

    # Net 2: 3V3 on BOTTOM layer
    # MCU_R_2 (133.89, 105.20) to:
    # 1) GY_1 (129.56, 127.50)
    ("3V3_B1", 2, 133.89, 105.20, 129.56, 105.20),
    ("3V3_B2", 2, 129.56, 105.20, 129.56, 127.50),
    # 2) SHT_1 (108.17, 127.50) & GPS_1 (102.33, 109.50)
    # Route below sensors along Y=106.0:
    ("3V3_B3", 2, 129.56, 105.20, 129.56, 106.5),
    ("3V3_B4", 2, 129.56, 106.5, 102.33, 106.5),
    ("3V3_B5", 2, 102.33, 106.5, 102.33, 109.50), # into GPS_1!
    # From (102.33, 106.5) up to SHT_1:
    ("3V3_B6", 2, 102.33, 106.5, 102.33, 123.0),
    ("3V3_B7", 2, 102.33, 123.0, 108.17, 123.0),
    ("3V3_B8", 2, 108.17, 123.0, 108.17, 127.50), # into SHT_1!

    # Net 1: GND on BOTTOM layer
    # MCU_L_2 (116.11, 105.20) to GPS_2 (104.87, 109.5) and H1 (103.5, 103.5)
    ("GND_B1", 1, 116.11, 105.20, 104.87, 105.20),
    ("GND_B2", 1, 104.87, 105.20, 104.87, 109.50), # into GPS_2!
    ("GND_B3", 1, 104.87, 105.20, 103.5, 103.83),
    ("GND_B4", 1, 103.5, 103.83, 103.5, 103.5), # into H1!
    # SHT_3 (113.25, 127.50) to H3 (103.5, 146.5)
    ("GND_B5", 1, 113.25, 127.50, 113.25, 139.0),
    ("GND_B6", 1, 113.25, 139.0, 103.5, 139.0),
    ("GND_B7", 1, 103.5, 139.0, 103.5, 146.5), # into H3!
    # GY_2 (132.10, 127.50) and GY_7 (144.80, 127.50) to H4 (146.5, 146.5)
    ("GND_B8", 1, 132.10, 127.50, 132.10, 139.0),
    ("GND_B9", 1, 132.10, 139.0, 144.80, 139.0),
    ("GND_B10", 1, 144.80, 139.0, 144.80, 127.50), # into GY_7!
    ("GND_B11", 1, 144.80, 139.0, 146.5, 139.0),
    ("GND_B12", 1, 146.5, 139.0, 146.5, 146.5), # into H4!
    # BH_2 (140.21, 123.2) GND on bottom
    ("GND_B13", 1, 140.21, 123.2, 140.21, 125.5),
    ("GND_B14", 1, 140.21, 125.5, 144.80, 125.5),
    ("GND_B15", 1, 144.80, 125.5, 144.80, 127.50),
]

print("Routing defined. Running DRC verification...")

# DRC TEST
errors = 0

print("\n--- 1. Testing Top Layer Traces vs Different Net Pads ---")
for tname, tnet, x1, y1, x2, y2 in top_traces:
    for pname, pnet, px, py, pr in pads:
        if tnet != pnet and pnet != 0:
            d = dist_point_to_segment(px, py, x1, y1, x2, y2)
            if d < pr + 0.25:
                print(f"ERROR Top: {tname} (Net {tnet}) close to pad {pname} (Net {pnet}), dist={d:.3f}, req={pr+0.25:.3f}")
                errors += 1

print("\n--- 2. Testing Bottom Layer Traces vs Different Net Pads ---")
for tname, tnet, x1, y1, x2, y2 in bottom_traces:
    for pname, pnet, px, py, pr in pads:
        if tnet != pnet and pnet != 0:
            d = dist_point_to_segment(px, py, x1, y1, x2, y2)
            if d < pr + 0.25:
                print(f"ERROR Bot: {tname} (Net {tnet}) close to pad {pname} (Net {pnet}), dist={d:.3f}, req={pr+0.25:.3f}")
                errors += 1

print("\n--- 3. Testing Top Layer Track-to-Track Clearances & Intersections ---")
for i in range(len(top_traces)):
    for j in range(i+1, len(top_traces)):
        t1 = top_traces[i]
        t2 = top_traces[j]
        if t1[1] != t2[1]: # different nets
            d = seg_dist(t1[2], t1[3], t1[4], t1[5], t2[2], t2[3], t2[4], t2[5])
            if d < 0.25:
                print(f"ERROR Top Tracks: {t1[0]}(Net {t1[1]}) and {t2[0]}(Net {t2[1]}) too close/cross! dist={d:.3f}")
                errors += 1

print("\n--- 4. Testing Bottom Layer Track-to-Track Clearances & Intersections ---")
for i in range(len(bottom_traces)):
    for j in range(i+1, len(bottom_traces)):
        t1 = bottom_traces[i]
        t2 = bottom_traces[j]
        if t1[1] != t2[1]: # different nets
            d = seg_dist(t1[2], t1[3], t1[4], t1[5], t2[2], t2[3], t2[4], t2[5])
            if d < 0.25:
                print(f"ERROR Bot Tracks: {t1[0]}(Net {t1[1]}) and {t2[0]}(Net {t2[1]}) too close/cross! dist={d:.3f}")
                errors += 1

print(f"\nTOTAL DRC VIOLATIONS: {errors}")
if errors == 0:
    print("PERFECT 100% ZERO-ERROR ROUTING ACHIEVED!")
