import os
import sys
import zipfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50"
GERBER_DIR = os.path.join(BASE_DIR, "gerber_temp")
os.makedirs(GERBER_DIR, exist_ok=True)

sys.path.append('scratch')
from font_renderer import render_text_to_segments
from solve_zero_cross_routing import pads, dist_point_to_segment, seg_dist

# -------------------------------------------------------------------------
# 1. TRACES DEFINITION (Pristine Aesthetic Architecture)
# -------------------------------------------------------------------------
top_traces = [
    # NET 3: BAT+ (J1 Pin 1 -> SW1 Pin 1 along top margin Y=148.2)
    ("BAT+_1", 3, 122.0, 146.5, 122.0, 148.2),
    ("BAT+_2", 3, 122.0, 148.2, 114.5, 148.2),
    ("BAT+_3", 3, 114.5, 148.2, 114.5, 146.5),

    # NET 4: BAT (SW1 Pin 2 -> MCU Pin 1 central vertical spine at X=125.0)
    ("BAT_1", 4, 116.0, 146.5, 116.0, 144.8),
    ("BAT_2", 4, 116.0, 144.8, 125.0, 144.8),
    ("BAT_3", 4, 125.0, 144.8, 125.0, 102.66),
    ("BAT_4", 4, 125.0, 102.66, 116.11, 102.66),

    # NET 7: GPS_RX (MCU Pin 4 GPIO17 -> GPS Pin 3 TX via Y=107.2)
    ("GPS_RX_1", 7, 116.11, 110.28, 113.8, 110.28),
    ("GPS_RX_2", 7, 113.8, 110.28, 113.8, 107.2),
    ("GPS_RX_3", 7, 113.8, 107.2, 107.41, 107.2),
    ("GPS_RX_4", 7, 107.41, 107.2, 107.41, 109.50),

    # NET 2: 3V3 on Top (MCU Right Pin 2 -> BH1750 Pin 1)
    ("3V3_T1", 2, 133.89, 105.20, 137.67, 105.20),
    ("3V3_T2", 2, 137.67, 105.20, 137.67, 123.20),

    # NET 1: GND on Top
    ("GND_T1", 1, 133.89, 102.66, 146.5, 102.66),
    ("GND_T2", 1, 146.5, 102.66, 146.5, 103.5),
    ("GND_T3", 1, 146.5, 103.5, 148.5, 105.5),
    ("GND_T4", 1, 148.5, 105.5, 148.5, 144.5),
    ("GND_T5", 1, 148.5, 144.5, 146.5, 146.5), # into H4
    ("GND_T6", 1, 148.5, 123.20, 147.83, 123.20), # BH1750 Pin 5 (ADDR)
    ("GND_T7", 1, 148.5, 108.50, 140.21, 108.50), # BH1750 Pin 2 (GND) routed low at Y=108.5!
    ("GND_T8", 1, 140.21, 108.50, 140.21, 123.20),
    ("GND_T9", 1, 124.0, 146.5, 124.0, 148.5),
    ("GND_T10", 1, 124.0, 148.5, 144.5, 148.5),
    ("GND_T11", 1, 144.5, 148.5, 146.5, 146.5), # J1 Pin 2 into H4
    ("GND_T12", 1, 132.10, 127.50, 132.10, 137.0),
    ("GND_T13", 1, 132.10, 137.0, 144.80, 137.0),
    ("GND_T14", 1, 144.80, 137.0, 144.80, 127.50), # into GY-521 Pin 7
    ("GND_T15", 1, 144.80, 137.0, 146.5, 137.0),
    ("GND_T16", 1, 146.5, 137.0, 146.5, 146.5), # into H4
    ("GND_T17", 1, 113.25, 127.50, 113.25, 138.0),
    ("GND_T18", 1, 113.25, 138.0, 103.5, 138.0),
    ("GND_T19", 1, 103.5, 138.0, 103.5, 146.5), # SHT45 Pin 3 into H3

    # NET 5: I2C_SDA on Top
    ("SDA_T1", 5, 116.11, 115.36, 118.33, 115.36),
    ("SDA_T2", 5, 118.33, 115.36, 118.33, 127.50), # into SHT45 Pin 5
    ("SDA_T3", 5, 118.33, 127.50, 121.25, 127.50),
    ("SDA_T4", 5, 121.25, 127.50, 121.25, 142.0), # into R3 Pin 1
    ("SDA_T5", 5, 121.25, 125.0, 123.5, 125.0), # to Via 1 at (123.5, 125.0)
    ("SDA_T6", 5, 126.5, 125.0, 137.18, 125.0), # from Via 2 at (126.5, 125.0)
    ("SDA_T7", 5, 137.18, 125.0, 137.18, 127.50), # into GY-521 Pin 4
    ("SDA_T8", 5, 137.18, 125.0, 145.29, 125.0),
    ("SDA_T9", 5, 145.29, 125.0, 145.29, 123.20), # into BH1750 Pin 4
]

bot_traces = [
    # NET 8: GPS_TX (MCU Pin 5 GPIO16 -> GPS Pin 4 RX via Y=112.82)
    ("GPS_TX_1", 8, 116.11, 112.82, 109.95, 112.82),
    ("GPS_TX_2", 8, 109.95, 112.82, 109.95, 109.50),

    # NET 2: 3V3 on Bottom
    ("3V3_B1", 2, 133.89, 105.20, 129.56, 105.20),
    ("3V3_B2", 2, 129.56, 105.20, 129.56, 127.50), # into GY-521 Pin 1
    ("3V3_B3", 2, 129.56, 127.50, 128.75, 128.5),
    ("3V3_B4", 2, 128.75, 128.5, 128.75, 142.0), # into R4 Pin 2
    ("3V3_B5a", 2, 128.75, 142.0, 128.75, 144.0),
    ("3V3_B5b", 2, 128.75, 144.0, 122.75, 144.0),
    ("3V3_B5c", 2, 122.75, 144.0, 122.75, 142.0), # into R3 Pin 2
    ("3V3_B6", 2, 122.75, 142.0, 122.75, 133.5),
    ("3V3_B7", 2, 122.75, 133.5, 108.17, 133.5),
    ("3V3_B8", 2, 108.17, 133.5, 108.17, 127.50), # into SHT45 Pin 1
    ("3V3_B9", 2, 108.17, 127.50, 102.33, 127.50),
    ("3V3_B10", 2, 102.33, 127.50, 102.33, 109.50), # into GPS Pin 1

    # NET 6: I2C_SCL on Bottom (Main Highway at Y=131.0)
    ("SCL_B1", 6, 116.11, 117.90, 115.79, 117.90),
    ("SCL_B2", 6, 115.79, 117.90, 115.79, 127.50), # into SHT45 Pin 4
    ("SCL_B3", 6, 115.79, 127.50, 115.79, 131.0),
    ("SCL_B4", 6, 115.79, 131.0, 134.64, 131.0),
    ("SCL_B5", 6, 134.64, 131.0, 134.64, 127.50), # into GY-521 Pin 3
    ("SCL_B6", 6, 134.64, 131.0, 142.75, 131.0),
    ("SCL_B7", 6, 142.75, 131.0, 142.75, 123.20), # into BH1750 Pin 3
    ("SCL_B8", 6, 127.25, 131.0, 127.25, 142.0), # into R4 Pin 1

    # NET 5: SDA Jumper on Bottom
    ("SDA_B_JUMP", 5, 123.5, 125.0, 126.5, 125.0),

    # NET 1: GND on Bottom
    ("GND_B1", 1, 116.11, 105.20, 104.87, 105.20),
    ("GND_B2", 1, 104.87, 105.20, 104.87, 109.50), # into GPS Pin 2
    ("GND_B3", 1, 104.87, 105.20, 103.5, 103.83),
    ("GND_B4", 1, 103.5, 103.83, 103.5, 103.5), # into H1
]

vias = [
    (5, 123.5, 125.0), # SDA Via 1
    (5, 126.5, 125.0), # SDA Via 2
]

# -------------------------------------------------------------------------
# 2. DRC VERIFICATION
# -------------------------------------------------------------------------
all_traces = [("F.Cu", t) for t in top_traces] + [("B.Cu", t) for t in bot_traces]
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

if errors:
    print(f"FAILED DRC with {len(errors)} errors:")
    for e in errors:
        print("  ->", e)
    sys.exit(1)
print(">>> DRC CHECK PASSED 100%! 0 ERRORS! <<<")

# -------------------------------------------------------------------------
# 3. SILKSCREEN GENERATION (Refined Aesthetics & Zero Conflicts)
# -------------------------------------------------------------------------
top_silk_segments = []
bot_silk_segments = []

def add_rect(seg_list, x1, y1, x2, y2):
    seg_list.append((x1, y1, x2, y1))
    seg_list.append((x2, y1, x2, y2))
    seg_list.append((x2, y2, x1, y2))
    seg_list.append((x1, y2, x1, y1))

# --- TOP SILKSCREEN ---
# Outlines:
add_rect(top_silk_segments, 114.75, 100.0, 135.25, 125.0) # Beetle MCU Outline
top_silk_segments.extend([ # USB-C Cutout
    (120.5, 100.0, 120.5, 103.5),
    (120.5, 103.5, 129.5, 103.5),
    (129.5, 103.5, 129.5, 100.0)
])
add_rect(top_silk_segments, 135.8, 106.7, 149.7, 125.2) # BH1750 Outline
add_rect(top_silk_segments, 136.4, 121.93, 149.1, 124.47) # BH1750 Header Box
add_rect(top_silk_segments, 120.0, 144.5, 126.0, 149.0) # J1 JST-PH
add_rect(top_silk_segments, 112.5, 144.5, 119.5, 148.5) # SW1 Switch
add_rect(top_silk_segments, 120.8, 141.2, 123.2, 142.8) # R3
add_rect(top_silk_segments, 126.8, 141.2, 129.2, 142.8) # R4

# Top Texts:
top_texts = [
    # BH1750 Texts (Right side, Y=111 to 118 completely open!)
    ("BH1750", 138.8, 117.5, 1.5, 1.0, 0.3),
    ("LIGHT SENSOR", 136.5, 114.5, 0.95, 0.65, 0.2),
    ("ADDR: 0X23", 138.5, 112.0, 0.85, 0.55, 0.2),
    ("3V3 GND SCL SDA ADR", 136.4, 120.2, 0.7, 0.45, 0.18),

    # Beetle ESP32-C6 Texts (Centered between BAT spine X=125.0 and Right Header X=133.89)
    ("ESP32-C6", 126.2, 117.0, 1.1, 0.55, 0.18),
    ("BEETLE", 126.2, 114.8, 1.1, 0.55, 0.18),
    ("TOP MCU", 126.2, 112.6, 0.85, 0.50, 0.16),

    # MCU Pin Labels:
    ("BAT", 113.2, 102.2, 0.8, 0.5, 0.15),
    ("GND", 113.2, 104.7, 0.8, 0.5, 0.15),
    ("RX", 113.8, 109.8, 0.8, 0.5, 0.15),
    ("TX", 113.8, 112.3, 0.8, 0.5, 0.15),
    ("SDA", 113.2, 114.9, 0.8, 0.5, 0.15),
    ("SCL", 113.2, 117.4, 0.8, 0.5, 0.15),
    ("GND", 134.8, 102.2, 0.8, 0.5, 0.15),
    ("3V3", 134.8, 104.7, 0.8, 0.5, 0.15),

    # Power Section:
    ("+", 121.5, 143.2, 0.9, 0.6, 0.2),
    ("-", 124.5, 143.2, 0.9, 0.6, 0.2),
    ("3.7V BATT", 120.0, 140.8, 0.7, 0.45, 0.15),
    ("PWR SW", 113.8, 143.2, 0.7, 0.45, 0.15),
    ("ON", 113.2, 148.8, 0.6, 0.4, 0.15),
    ("OFF", 116.8, 148.8, 0.6, 0.4, 0.15),
    ("R3:SDA", 119.2, 138.5, 0.65, 0.42, 0.15),
    ("R4:SCL", 126.2, 138.5, 0.65, 0.42, 0.15),

    # Board Branding (Top left corner, well clear of H3 and traces):
    ("COLDCHAIN", 104.5, 137.5, 0.95, 0.62, 0.2),
    ("DIGITAL TWIN", 104.5, 135.5, 0.95, 0.62, 0.2),
    ("CARRIER V9.3", 104.5, 133.5, 0.85, 0.55, 0.18),
]

for txt, tx, ty, ch, cw, sp in top_texts:
    top_silk_segments.extend(render_text_to_segments(txt, tx, ty, ch, cw, sp))

# --- BOTTOM SILKSCREEN ---
# Outlines:
add_rect(bot_silk_segments, 100.5, 125.5, 126.0, 143.3) # SHT45 Outline
add_rect(bot_silk_segments, 106.9, 126.23, 119.6, 128.77) # SHT45 Header Box
add_rect(bot_silk_segments, 128.0, 125.5, 148.5, 141.0) # GY-521 Outline
add_rect(bot_silk_segments, 128.25, 126.23, 148.59, 128.77) # GY-521 Header Box
add_rect(bot_silk_segments, 100.86, 107.5, 113.96, 123.2) # GPS Outline
add_rect(bot_silk_segments, 101.06, 108.23, 113.76, 110.77) # GPS Header Box

# Bottom Texts:
bot_texts = [
    # SHT45 Texts (Y=135 to 141 completely open!)
    ("SHT45", 109.5, 139.5, 1.6, 1.0, 0.3),
    ("TEMP / HUMIDITY", 104.5, 136.8, 1.0, 0.68, 0.2),
    ("ADDR: 0X44", 109.5, 134.5, 0.85, 0.55, 0.2),
    ("VIN NC GND SCL SDA", 107.0, 124.5, 0.7, 0.45, 0.18),

    # GY-521 Texts (Y=133 to 140 completely open!)
    ("GY-521", 134.5, 138.0, 1.6, 1.0, 0.3),
    ("6-AXIS IMU", 133.0, 135.2, 1.0, 0.68, 0.2),
    ("ADDR: 0X68", 134.5, 132.8, 0.85, 0.55, 0.2),
    ("VCC GND SCL SDA XDA XCL AD0 INT", 128.5, 124.5, 0.65, 0.42, 0.15),

    # ATGM336H GPS Texts (Y=114 to 121 completely open!)
    ("ATGM336H", 102.5, 119.5, 1.3, 0.85, 0.25),
    ("GPS / GNSS", 102.0, 116.8, 0.95, 0.65, 0.2),
    ("9600 BAUD", 102.5, 114.2, 0.85, 0.55, 0.2),
    ("VCC GND TX RX PPS", 101.2, 106.5, 0.7, 0.45, 0.18),

    # Bottom Branding (Cleanly placed in bottom center):
    ("COLDCHAIN TWIN", 119.0, 108.5, 0.9, 0.6, 0.2),
    ("BOTTOM SENSORS", 118.5, 106.5, 0.85, 0.55, 0.2),
]

for txt, tx, ty, ch, cw, sp in bot_texts:
    bot_silk_segments.extend(render_text_to_segments(txt, tx, ty, ch, cw, sp))

print(f"Generated Silkscreen: Top has {len(top_silk_segments)} segments, Bottom has {len(bot_silk_segments)} segments.")

# -------------------------------------------------------------------------
# 4. EXPORT KICAD PCB FILE
# -------------------------------------------------------------------------
kicad_path = os.path.join(BASE_DIR, "CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb")
with open(kicad_path, "w", encoding="utf-8") as f:
    f.write(f"""(kicad_pcb
\t(version 20260206)
\t(generator "pcbnew")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(2 "B.Cu" signal)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(25 "Edge.Cuts" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(tenting (front yes) (back yes))
\t)
\t(net 0 "")
\t(net 1 "GND")
\t(net 2 "3V3")
\t(net 3 "BAT+")
\t(net 4 "BAT")
\t(net 5 "I2C_SDA")
\t(net 6 "I2C_SCL")
\t(net 7 "GPS_RX")
\t(net 8 "GPS_TX")

\t(gr_line (start 102.0 100.0) (end 148.0 100.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
\t(gr_line (start 148.0 100.0) (end 150.0 102.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
\t(gr_line (start 150.0 102.0) (end 150.0 148.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
\t(gr_line (start 150.0 148.0) (end 148.0 150.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
\t(gr_line (start 148.0 150.0) (end 102.0 150.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
\t(gr_line (start 102.0 150.0) (end 100.0 148.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
\t(gr_line (start 100.0 148.0) (end 100.0 102.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
\t(gr_line (start 100.0 102.0) (end 102.0 100.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))

\t(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 103.5 103.5)
\t\t(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t)
\t(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 146.5 103.5)
\t\t(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t)
\t(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 103.5 146.5)
\t\t(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t)
\t(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 146.5 146.5)
\t\t(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t)

\t(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (layer "F.Cu") (at 116.11 111.55)
\t\t(property "Reference" "J_MCU_L" (at -2.8 0 90) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" thru_hole rect (at 0 -8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 4 "BAT"))
\t\t(pad "2" thru_hole circle (at 0 -6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t\t(pad "3" thru_hole circle (at 0 -3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "4" thru_hole circle (at 0 -1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
\t\t(pad "5" thru_hole circle (at 0 1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
\t\t(pad "6" thru_hole circle (at 0 3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
\t\t(pad "7" thru_hole circle (at 0 6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
\t\t(pad "8" thru_hole circle (at 0 8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t)
\t(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (layer "F.Cu") (at 133.89 111.55)
\t\t(property "Reference" "J_MCU_R" (at 2.8 0 90) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" thru_hole rect (at 0 -8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t\t(pad "2" thru_hole circle (at 0 -6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
\t\t(pad "3" thru_hole circle (at 0 -3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "4" thru_hole circle (at 0 -1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "5" thru_hole circle (at 0 1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "6" thru_hole circle (at 0 3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "7" thru_hole circle (at 0 6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "8" thru_hole circle (at 0 8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t)

\t(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "F.Cu") (at 142.75 123.2)
\t\t(property "Reference" "J_BH1750" (at 0 -2.5 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
\t\t(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t\t(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
\t\t(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
\t\t(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t)

\t(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 107.41 109.5)
\t\t(property "Reference" "J_GPS" (at 0 2.5 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
\t\t(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t\t(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
\t\t(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
\t\t(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t)

\t(footprint "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal" (layer "F.Cu") (at 123.0 146.5)
\t\t(property "Reference" "J1" (at 0 -2.5 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" thru_hole rect (at -1.0 0) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask") (net 3 "BAT+"))
\t\t(pad "2" thru_hole circle (at 1.0 0) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t)

\t(footprint "Button_Switch_SMD:SW_SPDT_PCM12" (layer "F.Cu") (at 116.0 146.5)
\t\t(property "Reference" "SW1" (at 0 -2.0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" smd rect (at -1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 3 "BAT+"))
\t\t(pad "2" smd rect (at 0 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 4 "BAT"))
\t\t(pad "3" smd rect (at 1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 0 ""))
\t)

\t(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 122.0 142.0)
\t\t(property "Reference" "R3" (at 0 -1.2 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))
\t\t(pad "1" smd rect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 5 "I2C_SDA"))
\t\t(pad "2" smd rect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 2 "3V3"))
\t)
\t(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 128.0 142.0)
\t\t(property "Reference" "R4" (at 0 -1.2 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))
\t\t(pad "1" smd rect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 6 "I2C_SCL"))
\t\t(pad "2" smd rect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 2 "3V3"))
\t)

\t(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 113.25 127.5)
\t\t(property "Reference" "J_SHT45" (at 0 2.8 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
\t\t(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t\t(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
\t\t(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
\t)

\t(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Horizontal" (layer "B.Cu") (at 138.42 127.5)
\t\t(property "Reference" "J_GY521" (at 0 -2.8 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
\t\t(pad "1" thru_hole rect (at -8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
\t\t(pad "2" thru_hole circle (at -6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t\t(pad "3" thru_hole circle (at -3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
\t\t(pad "4" thru_hole circle (at -1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
\t\t(pad "5" thru_hole circle (at 1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "6" thru_hole circle (at 3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t\t(pad "7" thru_hole circle (at 6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
\t\t(pad "8" thru_hole circle (at 8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
\t)
""")

    # Append KiCad Silkscreen text & lines
    for x1, y1, x2, y2 in top_silk_segments:
        f.write(f'\t(gr_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))\n')
    for x1, y1, x2, y2 in bot_silk_segments:
        f.write(f'\t(gr_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))\n')

    # Append KiCad Segments
    for tname, net_id, x1, y1, x2, y2 in top_traces:
        f.write(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width 0.35) (layer "F.Cu") (net {net_id}))\n')
    for tname, net_id, x1, y1, x2, y2 in bot_traces:
        f.write(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width 0.35) (layer "B.Cu") (net {net_id}))\n')

    # Append KiCad Vias
    for net_id, vx, vy in vias:
        f.write(f'\t(via (at {vx:.2f} {vy:.2f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net {net_id}))\n')

    f.write(")\n")

print(f"Saved master KiCad PCB: {kicad_path}")

# -------------------------------------------------------------------------
# 5. GERBER EXPORT ENGINE
# -------------------------------------------------------------------------
def fmt_g(val):
    return f"{int(round(val * 100000)):08d}"

# 1. Outline .GKO
with open(os.path.join(GERBER_DIR, "Gerber_BoardOutlineLayer.GKO"), "w", encoding="utf-8") as f:
    f.write(f"""G04 Layer: BoardOutlineLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,0.100*%
D10*
G01X{fmt_g(102.0)}Y{fmt_g(100.0)}D02*
G01X{fmt_g(148.0)}Y{fmt_g(100.0)}D01*
G01X{fmt_g(150.0)}Y{fmt_g(102.0)}D01*
G01X{fmt_g(150.0)}Y{fmt_g(148.0)}D01*
G01X{fmt_g(148.0)}Y{fmt_g(150.0)}D01*
G01X{fmt_g(102.0)}Y{fmt_g(150.0)}D01*
G01X{fmt_g(100.0)}Y{fmt_g(148.0)}D01*
G01X{fmt_g(100.0)}Y{fmt_g(102.0)}D01*
G01X{fmt_g(102.0)}Y{fmt_g(100.0)}D01*
M02*
""")

# 2. Top Silkscreen .GTO
with open(os.path.join(GERBER_DIR, "Gerber_TopSilkscreenLayer.GTO"), "w", encoding="utf-8") as f:
    f.write(f"""G04 Layer: TopSilkscreenLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,0.120*%
D10*
""")
    for x1, y1, x2, y2 in top_silk_segments:
        f.write(f"G01X{fmt_g(x1)}Y{fmt_g(y1)}D02*\n")
        f.write(f"G01X{fmt_g(x2)}Y{fmt_g(y2)}D01*\n")
    f.write("M02*\n")

# 3. Bottom Silkscreen .GBO
with open(os.path.join(GERBER_DIR, "Gerber_BottomSilkscreenLayer.GBO"), "w", encoding="utf-8") as f:
    f.write(f"""G04 Layer: BottomSilkscreenLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,0.120*%
D10*
""")
    for x1, y1, x2, y2 in bot_silk_segments:
        f.write(f"G01X{fmt_g(x1)}Y{fmt_g(y1)}D02*\n")
        f.write(f"G01X{fmt_g(x2)}Y{fmt_g(y2)}D01*\n")
    f.write("M02*\n")

# 4. Top Solder Mask .GTS
with open(os.path.join(GERBER_DIR, "Gerber_TopSolderMaskLayer.GTS"), "w", encoding="utf-8") as f:
    f.write(f"""G04 Layer: TopSolderMaskLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,5.600*%
%ADD11C,1.700*%
%ADD12R,1.700X1.700*%
%ADD13R,1.100X1.600*%
%ADD14R,0.900X0.900*%
%ADD15C,0.900*%

G04 Mounting Holes*
D10*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 Rect Pin 1s*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(137.67)}Y{fmt_g(123.20)}D03*
G01X{fmt_g(102.33)}Y{fmt_g(109.50)}D03*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(108.17)}Y{fmt_g(127.50)}D03*
G01X{fmt_g(129.56)}Y{fmt_g(127.50)}D03*

G04 Circular THT Pads*
D11*
""")
    for pname, pnet, px, py, pr in pads:
        if pname.startswith("H") or pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2'] or pname.endswith("_1"):
            continue
        f.write(f"G01X{fmt_g(px)}Y{fmt_g(py)}D03*\n")

    f.write(f"""G04 SMD Pads*
D13*
G01X{fmt_g(114.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(116.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(117.5)}Y{fmt_g(146.5)}D03*
D14*
G01X{fmt_g(121.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(122.75)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(127.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(128.75)}Y{fmt_g(142.0)}D03*

G04 Vias*
D15*
""")
    for net_id, vx, vy in vias:
        f.write(f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n")
    f.write("M02*\n")

# 5. Bottom Solder Mask .GBS
with open(os.path.join(GERBER_DIR, "Gerber_BottomSolderMaskLayer.GBS"), "w", encoding="utf-8") as f:
    f.write(f"""G04 Layer: BottomSolderMaskLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,5.600*%
%ADD11C,1.700*%
%ADD12R,1.700X1.700*%
%ADD15C,0.900*%

G04 Mounting Holes*
D10*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 Rect Pin 1s*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(137.67)}Y{fmt_g(123.20)}D03*
G01X{fmt_g(102.33)}Y{fmt_g(109.50)}D03*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(108.17)}Y{fmt_g(127.50)}D03*
G01X{fmt_g(129.56)}Y{fmt_g(127.50)}D03*

G04 Circular THT Pads*
D11*
""")
    for pname, pnet, px, py, pr in pads:
        if pname.startswith("H") or pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2'] or pname.endswith("_1"):
            continue
        f.write(f"G01X{fmt_g(px)}Y{fmt_g(py)}D03*\n")

    f.write(f"""G04 Vias*
D15*
""")
    for net_id, vx, vy in vias:
        f.write(f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n")
    f.write("M02*\n")

# 6. Top Copper .GTL
with open(os.path.join(GERBER_DIR, "Gerber_TopCopperLayer.GTL"), "w", encoding="utf-8") as f:
    f.write(f"""G04 Layer: TopCopperLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,5.500*%
%ADD11C,1.600*%
%ADD12R,1.600X1.600*%
%ADD13R,1.000X1.500*%
%ADD14R,0.800X0.800*%
%ADD15C,0.800*%
%ADD20C,0.350*%

G04 Mounting Holes*
D10*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 Rect Pin 1s*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(137.67)}Y{fmt_g(123.20)}D03*
G01X{fmt_g(102.33)}Y{fmt_g(109.50)}D03*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(108.17)}Y{fmt_g(127.50)}D03*
G01X{fmt_g(129.56)}Y{fmt_g(127.50)}D03*

G04 Circular THT Pads*
D11*
""")
    for pname, pnet, px, py, pr in pads:
        if pname.startswith("H") or pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2'] or pname.endswith("_1"):
            continue
        f.write(f"G01X{fmt_g(px)}Y{fmt_g(py)}D03*\n")

    f.write(f"""G04 SMD Pads*
D13*
G01X{fmt_g(114.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(116.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(117.5)}Y{fmt_g(146.5)}D03*
D14*
G01X{fmt_g(121.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(122.75)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(127.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(128.75)}Y{fmt_g(142.0)}D03*

G04 Vias*
D15*
""")
    for net_id, vx, vy in vias:
        f.write(f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n")

    f.write(f"""G04 Top Traces*
D20*
""")
    for tname, net_id, x1, y1, x2, y2 in top_traces:
        f.write(f"G01X{fmt_g(x1)}Y{fmt_g(y1)}D02*\n")
        f.write(f"G01X{fmt_g(x2)}Y{fmt_g(y2)}D01*\n")
    f.write("M02*\n")

# 7. Bottom Copper .GBL
with open(os.path.join(GERBER_DIR, "Gerber_BottomCopperLayer.GBL"), "w", encoding="utf-8") as f:
    f.write(f"""G04 Layer: BottomCopperLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,5.500*%
%ADD11C,1.600*%
%ADD12R,1.600X1.600*%
%ADD15C,0.800*%
%ADD20C,0.350*%

G04 Mounting Holes*
D10*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 Rect Pin 1s*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(137.67)}Y{fmt_g(123.20)}D03*
G01X{fmt_g(102.33)}Y{fmt_g(109.50)}D03*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(108.17)}Y{fmt_g(127.50)}D03*
G01X{fmt_g(129.56)}Y{fmt_g(127.50)}D03*

G04 Circular THT Pads*
D11*
""")
    for pname, pnet, px, py, pr in pads:
        if pname.startswith("H") or pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2'] or pname.endswith("_1"):
            continue
        f.write(f"G01X{fmt_g(px)}Y{fmt_g(py)}D03*\n")

    f.write(f"""G04 Vias*
D15*
""")
    for net_id, vx, vy in vias:
        f.write(f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n")

    f.write(f"""G04 Bottom Traces*
D20*
""")
    for tname, net_id, x1, y1, x2, y2 in bot_traces:
        f.write(f"G01X{fmt_g(x1)}Y{fmt_g(y1)}D02*\n")
        f.write(f"G01X{fmt_g(x2)}Y{fmt_g(y2)}D01*\n")
    f.write("M02*\n")

# 8. Drill .DRL
with open(os.path.join(GERBER_DIR, "Gerber_Drill.DRL"), "w", encoding="utf-8") as f:
    f.write(f"""M48
; DRILL file
; FORMAT={{4:4}}/ absolute / metric / keep zeros
METRIC,TZ
T1C3.200
T2C0.950
T3C0.800
T4C0.400
%
G90
G05
T1
X{int(round(103.5*10000))}Y{int(round(103.5*10000))}
X{int(round(146.5*10000))}Y{int(round(103.5*10000))}
X{int(round(103.5*10000))}Y{int(round(146.5*10000))}
X{int(round(146.5*10000))}Y{int(round(146.5*10000))}
T2
""")
    for pname, pnet, px, py, pr in pads:
        if pname.startswith("H") or pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2', 'J1_1', 'J1_2']:
            continue
        f.write(f"X{int(round(px*10000))}Y{int(round(py*10000))}\n")
    f.write("T3\n")
    f.write(f"X{int(round(122.0*10000))}Y{int(round(146.5*10000))}\n")
    f.write(f"X{int(round(124.0*10000))}Y{int(round(146.5*10000))}\n")
    f.write("T4\n")
    for net_id, vx, vy in vias:
        f.write(f"X{int(round(vx*10000))}Y{int(round(vy*10000))}\n")
    f.write("M30\n")

print("Generated all 8 Gerber files in gerber_temp.")

# -------------------------------------------------------------------------
# 6. ZIP PACKAGING
# -------------------------------------------------------------------------
zip_path = os.path.join(BASE_DIR, "Gerber_CarrierBoard_BeetleC6_EdgeUSB_50x50.zip")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for fname in os.listdir(GERBER_DIR):
        fpath = os.path.join(GERBER_DIR, fname)
        if os.path.isfile(fpath) and fname.startswith("Gerber_"):
            zipf.write(fpath, fname)
print(f"Updated master zip package: {zip_path}")

# -------------------------------------------------------------------------
# 7. HIGH-RESOLUTION RENDERING
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=250)

# Top Layer
ax = axes[0]
ax.set_facecolor('#121518')
ax.set_title("TOP LAYER (F.Cu + F.SilkS) - Red Copper, Yellow Silk", color='white', fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(98, 152)
ax.set_ylim(98, 152)
ax.set_aspect('equal')
ax.grid(True, color='#1f242b', linestyle=':', alpha=0.6)

outline_poly = [[102,100],[148,100],[150,102],[150,148],[148,150],[102,150],[100,148],[100,102],[102,100]]
poly_x, poly_y = zip(*outline_poly)
ax.plot(poly_x, poly_y, color='white', linewidth=1.5)

for x1, y1, x2, y2 in top_silk_segments:
    ax.plot([x1, x2], [y1, y2], color='#ffea00', linewidth=1.1, alpha=0.95)

for tname, net_id, x1, y1, x2, y2 in top_traces:
    ax.plot([x1, x2], [y1, y2], color='#ff2a3a', linewidth=2.2, solid_capstyle='round')

for net_id, vx, vy in vias:
    c = plt.Circle((vx, vy), 0.4, facecolor='#22cc88', edgecolor='#ffffff', linewidth=1.0, zorder=10)
    ax.add_patch(c)

for pname, pnet, px, py, pr in pads:
    if pname.startswith("H"):
        c = plt.Circle((px, py), pr, facecolor='#ff00ff', edgecolor='#00ffcc', linewidth=1.2, zorder=5)
        ax.add_patch(c)
        c2 = plt.Circle((px, py), 1.6, facecolor='#121518', zorder=6)
        ax.add_patch(c2)
    elif pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2']:
        rect = patches.Rectangle((px - 0.4, py - 0.4), 0.8, 0.8, facecolor='#ff00ff', edgecolor='#ffffff', linewidth=0.8, zorder=5)
        ax.add_patch(rect)
    else:
        c = plt.Circle((px, py), pr, facecolor='#ff00ff', edgecolor='#00ff66', linewidth=1.0, zorder=5)
        ax.add_patch(c)
        c2 = plt.Circle((px, py), 0.45, facecolor='#00ff66', zorder=6)
        ax.add_patch(c2)

# Bottom Layer
ax = axes[1]
ax.set_facecolor('#121518')
ax.set_title("BOTTOM LAYER (B.Cu + B.SilkS) - Blue Copper, Yellow Silk", color='white', fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(98, 152)
ax.set_ylim(98, 152)
ax.set_aspect('equal')
ax.grid(True, color='#1f242b', linestyle=':', alpha=0.6)

ax.plot(poly_x, poly_y, color='white', linewidth=1.5)

for x1, y1, x2, y2 in bot_silk_segments:
    ax.plot([x1, x2], [y1, y2], color='#ffea00', linewidth=1.1, alpha=0.95)

for tname, net_id, x1, y1, x2, y2 in bot_traces:
    ax.plot([x1, x2], [y1, y2], color='#0077ff', linewidth=2.2, solid_capstyle='round')

for net_id, vx, vy in vias:
    c = plt.Circle((vx, vy), 0.4, facecolor='#22cc88', edgecolor='#ffffff', linewidth=1.0, zorder=10)
    ax.add_patch(c)

for pname, pnet, px, py, pr in pads:
    if pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2']:
        continue
    if pname.startswith("H"):
        c = plt.Circle((px, py), pr, facecolor='#0044ff', edgecolor='#00ffcc', linewidth=1.2, zorder=5)
        ax.add_patch(c)
        c2 = plt.Circle((px, py), 1.6, facecolor='#121518', zorder=6)
        ax.add_patch(c2)
    else:
        c = plt.Circle((px, py), pr, facecolor='#0044ff', edgecolor='#00ff66', linewidth=1.0, zorder=5)
        ax.add_patch(c)
        c2 = plt.Circle((px, py), 0.45, facecolor='#00ff66', zorder=6)
        ax.add_patch(c2)

plt.tight_layout()
preview_png = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\preview_aesthetic_master.png"
plt.savefig(preview_png, bbox_inches='tight')
plt.close()

# Also copy to artifacts directory for direct embedding
artifact_png = r"C:\Users\korea\.gemini\antigravity-ide\brain\8cc94666-3a79-4076-a473-a6dc3e8746a0\preview_aesthetic_master.png"
import shutil
shutil.copyfile(preview_png, artifact_png)

print(f"Saved master aesthetic preview to: {preview_png} and {artifact_png}")
