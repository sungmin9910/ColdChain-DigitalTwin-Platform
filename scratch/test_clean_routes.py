import numpy as np
import sys
sys.path.append('scratch')
from solve_zero_cross_routing import pads, dist_point_to_segment, seg_dist

def test_routes(top_traces, bottom_traces):
    errors = []
    
    # 1. Top traces vs Pads
    for tname, tnet, x1, y1, x2, y2 in top_traces:
        for pname, pnet, px, py, pr in pads:
            if tnet != pnet and pnet != 0:
                d = dist_point_to_segment(px, py, x1, y1, x2, y2)
                if d < pr + 0.25:
                    errors.append(f"Top Trace-Pad: {tname} (Net {tnet}) close to {pname} (Net {pnet}), d={d:.3f}, req={pr+0.25:.3f}")
                    
    # 2. Bottom traces vs Pads
    for tname, tnet, x1, y1, x2, y2 in bottom_traces:
        for pname, pnet, px, py, pr in pads:
            if tnet != pnet and pnet != 0:
                d = dist_point_to_segment(px, py, x1, y1, x2, y2)
                if d < pr + 0.25:
                    errors.append(f"Bot Trace-Pad: {tname} (Net {tnet}) close to {pname} (Net {pnet}), d={d:.3f}, req={pr+0.25:.3f}")

    # 3. Top Track-to-Track
    for i in range(len(top_traces)):
        for j in range(i+1, len(top_traces)):
            t1 = top_traces[i]
            t2 = top_traces[j]
            if t1[1] != t2[1]:
                d = seg_dist(t1[2], t1[3], t1[4], t1[5], t2[2], t2[3], t2[4], t2[5])
                if d < 0.25:
                    errors.append(f"Top Track-Track: {t1[0]}({t1[1]}) and {t2[0]}({t2[1]}), d={d:.3f}")

    # 4. Bot Track-to-Track
    for i in range(len(bottom_traces)):
        for j in range(i+1, len(bottom_traces)):
            t1 = bottom_traces[i]
            t2 = bottom_traces[j]
            if t1[1] != t2[1]:
                d = seg_dist(t1[2], t1[3], t1[4], t1[5], t2[2], t2[3], t2[4], t2[5])
                if d < 0.25:
                    errors.append(f"Bot Track-Track: {t1[0]}({t1[1]}) and {t2[0]}({t2[1]}), d={d:.3f}")

    return errors

# =========================================================================
# TOP LAYER (F.Cu)
# =========================================================================
top = [
    # Net 3: BAT+ (J1 to SW1)
    ("BAT+_1", 3, 122.0, 146.5, 122.0, 148.2),
    ("BAT+_2", 3, 122.0, 148.2, 114.5, 148.2),
    ("BAT+_3", 3, 114.5, 148.2, 114.5, 146.5),

    # Net 4: BAT (SW1 to MCU_L_1)
    # SW1_2 is at (116.0, 146.5). Route via X=125.0 (between R3 at 122.75 and R4 at 127.25)
    ("BAT_1", 4, 116.0, 146.5, 116.0, 145.0),
    ("BAT_2", 4, 116.0, 145.0, 125.0, 145.0),
    ("BAT_3", 4, 125.0, 145.0, 125.0, 102.66),
    ("BAT_4", 4, 125.0, 102.66, 116.11, 102.66),

    # Net 7: GPS_RX (MCU_L_4 to GPS_3) on Top Layer
    ("GPS_RX_1", 7, 116.11, 110.28, 114.0, 110.28),
    ("GPS_RX_2", 7, 114.0, 110.28, 114.0, 107.0),
    ("GPS_RX_3", 7, 114.0, 107.0, 107.41, 107.0),
    ("GPS_RX_4", 7, 107.41, 107.0, 107.41, 109.50),

    # Net 5: I2C_SDA on Top Layer
    # MCU_L_6 (116.11, 115.36) to SHT_5 (118.33, 127.50)
    ("SDA_T1", 5, 116.11, 115.36, 117.8, 115.36),
    ("SDA_T2", 5, 117.8, 115.36, 117.8, 125.0),
    ("SDA_T3", 5, 117.8, 125.0, 118.33, 125.0),
    ("SDA_T4", 5, 118.33, 125.0, 118.33, 127.50), # into SHT_5!
    # SDA to R3_1 (121.25, 142.0)
    ("SDA_T5", 5, 118.33, 127.50, 121.25, 127.50),
    ("SDA_T6", 5, 121.25, 127.50, 121.25, 142.00), # into R3_1!

    # Net 2: 3V3 on Top Layer
    # MCU_R_2 (133.89, 105.20) to BH_1 (137.67, 123.20)
    ("3V3_T1", 2, 133.89, 105.20, 137.67, 105.20),
    ("3V3_T2", 2, 137.67, 105.20, 137.67, 123.20),
    # MCU_R_2 to R4_2 (128.75, 142.0) and R3_2 (122.75, 142.0)
    # Route via X=130.5 up to Y=144.0:
    ("3V3_T3", 2, 133.89, 105.20, 130.5, 105.20),
    ("3V3_T4", 2, 130.5, 105.20, 130.5, 144.0),
    ("3V3_T5", 2, 130.5, 144.0, 128.75, 144.0),
    ("3V3_T6", 2, 128.75, 144.0, 128.75, 142.0),
    # To R3_2: route from 125.0 up to 144.0... wait! BAT is at X=125.0, Y up to 145.0!
    # So cross BAT above Y=145.0, say at Y=146.0!
    ("3V3_T7", 2, 128.75, 144.0, 128.75, 146.0),
    ("3V3_T8", 2, 128.75, 146.0, 122.75, 146.0),
    ("3V3_T9", 2, 122.75, 146.0, 122.75, 142.0),
    # 3V3 to SHT_1 (108.17, 127.50) and GPS_1 (102.33, 109.50)
    # Route via Y=140.0 (well clear of H3 at 103.5, 146.5):
    ("3V3_T10", 2, 122.75, 146.0, 108.17, 146.0), # wait, H3 is at 103.5!
    # Route around H3: from (122.75, 142.0) go left at Y=140.0:
    ("3V3_T11", 2, 122.75, 142.0, 108.17, 142.0),
    ("3V3_T12", 2, 108.17, 142.0, 108.17, 127.50), # into SHT_1!
    ("3V3_T13", 2, 108.17, 142.0, 106.5, 142.0),
    ("3V3_T14", 2, 106.5, 142.0, 106.5, 120.0),
    ("3V3_T15", 2, 106.5, 120.0, 102.33, 120.0),
    ("3V3_T16", 2, 102.33, 120.0, 102.33, 109.50), # into GPS_1!

    # Net 1: GND on Top Layer
    ("GND_T1", 1, 133.89, 102.66, 146.5, 102.66),
    ("GND_T2", 1, 146.5, 102.66, 146.5, 103.5),
    ("GND_T3", 1, 146.5, 103.5, 148.5, 105.5),
    ("GND_T4", 1, 148.5, 105.5, 148.5, 123.20),
    ("GND_T5", 1, 148.5, 123.20, 147.83, 123.20), # into BH_5!
    ("GND_T6", 1, 148.5, 118.0, 140.21, 118.0),
    ("GND_T7", 1, 140.21, 118.0, 140.21, 123.20), # into BH_2!
    ("GND_T8", 1, 124.0, 146.5, 124.0, 148.5),
    ("GND_T9", 1, 124.0, 148.5, 144.5, 148.5),
    ("GND_T10", 1, 144.5, 148.5, 146.5, 146.5), # into H4!
]

# =========================================================================
# BOTTOM LAYER (B.Cu)
# =========================================================================
bot = [
    # Net 8: GPS_TX (on Bottom layer)
    ("GPS_TX_1", 8, 116.11, 112.82, 109.95, 112.82),
    ("GPS_TX_2", 8, 109.95, 112.82, 109.95, 109.50),

    # Net 2: 3V3 on Bottom Layer (MCU_R_2 to GY_1)
    ("3V3_B1", 2, 133.89, 105.20, 129.56, 105.20),
    ("3V3_B2", 2, 129.56, 105.20, 129.56, 127.50),

    # Net 6: I2C_SCL on Bottom Layer
    ("SCL_B1", 6, 116.11, 117.90, 115.79, 117.90),
    ("SCL_B2", 6, 115.79, 117.90, 115.79, 127.50), # into SHT_4!
    # To GY_3 (134.64, 127.50) and BH_3 (142.75, 123.20)
    ("SCL_B3", 6, 115.79, 127.50, 115.79, 131.0),
    ("SCL_B4", 6, 115.79, 131.0, 134.64, 131.0),
    ("SCL_B5", 6, 134.64, 131.0, 134.64, 127.50), # into GY_3!
    ("SCL_B6", 6, 134.64, 131.0, 142.75, 131.0),
    ("SCL_B7", 6, 142.75, 131.0, 142.75, 123.20), # into BH_3!
    ("SCL_B8", 6, 127.25, 131.0, 127.25, 142.0), # into R4_1!

    # Net 5: I2C_SDA on Bottom Layer (feed GY_4 and BH_4 from SHT_5)
    # Route via Y=135.0 (above SCL at 131.0)
    ("SDA_B1", 5, 118.33, 127.50, 118.33, 135.0),
    ("SDA_B2", 5, 118.33, 135.0, 137.18, 135.0),
    ("SDA_B3", 5, 137.18, 135.0, 137.18, 127.50), # into GY_4!
    ("SDA_B4", 5, 137.18, 135.0, 145.29, 135.0),
    ("SDA_B5", 5, 145.29, 135.0, 146.5, 135.0),
    ("SDA_B6", 5, 146.5, 135.0, 146.5, 123.20),
    ("SDA_B7", 5, 146.5, 123.20, 145.29, 123.20), # into BH_4!

    # Net 1: GND on Bottom Layer
    # MCU_L_2 (116.11, 105.20) to GPS_2 (104.87, 109.50) and H1 (103.5, 103.5)
    ("GND_B1", 1, 116.11, 105.20, 104.87, 105.20),
    ("GND_B2", 1, 104.87, 105.20, 104.87, 109.50),
    ("GND_B3", 1, 104.87, 105.20, 103.5, 103.83),
    ("GND_B4", 1, 103.5, 103.83, 103.5, 103.5),
    # SHT_3 (113.25, 127.50) to H3 (103.5, 146.5)
    ("GND_B5", 1, 113.25, 127.50, 113.25, 138.0),
    ("GND_B6", 1, 113.25, 138.0, 103.5, 138.0),
    ("GND_B7", 1, 103.5, 138.0, 103.5, 146.5),
    # GY_2 (132.10, 127.50) and GY_7 (144.80, 127.50)
    # Route via Y=119.5 (below GY-521 pads and SCL)
    ("GND_B8", 1, 132.10, 127.50, 132.10, 119.5),
    ("GND_B9", 1, 132.10, 119.5, 144.80, 119.5),
    ("GND_B10", 1, 144.80, 119.5, 144.80, 127.50), # into GY_7!
    ("GND_B11", 1, 144.80, 119.5, 148.5, 119.5),
    ("GND_B12", 1, 148.5, 119.5, 148.5, 144.5),
    ("GND_B13", 1, 148.5, 144.5, 146.5, 146.5), # into H4!
]

errs = test_routes(top, bot)
print(f"Total Errors Found: {len(errs)}")
for e in errs:
    print("  ->", e)
if len(errs) == 0:
    print("CONGRATULATIONS: 100% CLEAN ELECTRICAL ROUTING, ZERO VIOLATIONS!")
