import os
import subprocess
import json

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
TARGET_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText"
SRC_PCB = os.path.join(TARGET_DIR, "CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb")
TEST_PCB = "scratch/test_routed.kicad_pcb"

# Read header & footprints from original file (lines 1 to 171)
# Line 171 is the last outline graphic line before the text strokes
with open(SRC_PCB, "r", encoding="utf-8") as f:
    lines = f.readlines()

header_and_footprints = lines[:171] # Up to component outline graphics

# Now let's add the remaining outline graphics for Bottom components:
# SHT45, GY-521, GPS
bot_outlines = """\t(gr_line (start 100.8 125.5) (end 126.0 125.5) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 126.0 125.5) (end 126.0 143.3) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 126.0 143.3) (end 100.8 143.3) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 100.8 143.3) (end 100.8 125.5) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 106.9 126.23) (end 119.6 126.23) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 119.6 126.23) (end 119.6 128.77) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 119.6 128.77) (end 106.9 128.77) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 106.9 128.77) (end 106.9 126.23) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 128.0 125.5) (end 148.5 125.5) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 148.5 125.5) (end 148.5 141.0) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 148.5 141.0) (end 128.0 141.0) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 128.0 141.0) (end 128.0 125.5) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 128.25 126.23) (end 148.59 126.23) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 148.59 126.23) (end 148.59 128.77) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 148.59 128.77) (end 128.25 128.77) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 128.25 128.77) (end 128.25 126.23) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 100.86 107.5) (end 113.96 107.5) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 113.96 107.5) (end 113.96 123.2) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 113.96 123.2) (end 100.86 123.2) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 100.86 123.2) (end 100.86 107.5) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 101.06 108.23) (end 113.76 108.23) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 113.76 108.23) (end 113.76 110.77) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 113.76 110.77) (end 101.06 110.77) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
\t(gr_line (start 101.06 110.77) (end 101.06 108.23) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
"""

tracks = []
vias = []

def add_track(x1, y1, x2, y2, layer, net, width=0.35):
    tracks.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {width}) (layer "{layer}") (net {net}))')

def add_via(x, y, net, size=0.8, drill=0.4):
    vias.append(f'\t(via (at {x:.2f} {y:.2f}) (size {size}) (drill {drill}) (layers "F.Cu" "B.Cu") (net {net}))')

# -------------------------------------------------------------
# 1. NET 3: BAT+ (J1 Pin 1 to SW1 Pin 1)
# -------------------------------------------------------------
# J1_1 at (122.0, 146.5) -> SW1_1 at (114.5, 146.5) along top edge
add_track(122.0, 146.5, 122.0, 148.2, "F.Cu", 3)
add_track(122.0, 148.2, 114.5, 148.2, "F.Cu", 3)
add_track(114.5, 148.2, 114.5, 146.5, "F.Cu", 3)

# -------------------------------------------------------------
# 2. NET 4: BAT (SW1 Pin 2 to MCU_L Pin 1)
# -------------------------------------------------------------
# SW1_2 at (116.0, 146.5) -> MCU_L_1 at (116.11, 102.66)
add_track(116.0, 146.5, 116.0, 144.8, "F.Cu", 4)
add_track(116.0, 144.8, 125.0, 144.8, "F.Cu", 4)
add_track(125.0, 144.8, 125.0, 102.66, "F.Cu", 4)
add_track(125.0, 102.66, 116.11, 102.66, "F.Cu", 4)

# -------------------------------------------------------------
# 3. NET 7: GPS_RX (MCU_L Pin 4 to GPS Pin 3)
# -------------------------------------------------------------
# MCU_L_4 at (116.11, 110.28) -> GPS_3 at (107.41, 109.5)
add_track(116.11, 110.28, 113.8, 110.28, "B.Cu", 7)
add_track(113.8, 110.28, 113.8, 107.2, "B.Cu", 7)
add_track(113.8, 107.2, 107.41, 107.2, "B.Cu", 7)
add_track(107.41, 107.2, 107.41, 109.5, "B.Cu", 7)

# -------------------------------------------------------------
# 4. NET 8: GPS_TX (MCU_L Pin 5 to GPS Pin 4)
# -------------------------------------------------------------
# MCU_L_5 at (116.11, 112.82) -> GPS_4 at (109.95, 109.5)
add_track(116.11, 112.82, 109.95, 112.82, "B.Cu", 8)
add_track(109.95, 112.82, 109.95, 109.5, "B.Cu", 8)

# -------------------------------------------------------------
# 5. NET 2: 3V3 POWER (ALL ON TOP LAYER - ZERO VIAS TO PULLUPS!)
# -------------------------------------------------------------
# Source: MCU_R_2 at (133.89, 105.20)
# Feed BH1750_1 at (137.67, 123.2):
add_track(133.89, 105.20, 137.67, 105.20, "F.Cu", 2)
add_track(137.67, 105.20, 137.67, 123.20, "F.Cu", 2)

# Feed GY-521_1 at (129.56, 127.50):
add_track(133.89, 105.20, 129.56, 105.20, "F.Cu", 2)
add_track(129.56, 105.20, 129.56, 127.50, "F.Cu", 2)

# Feed R4_2 at (128.75, 142.0):
add_track(129.56, 127.50, 128.75, 128.50, "F.Cu", 2)
add_track(128.75, 128.50, 128.75, 142.00, "F.Cu", 2)

# Feed R3_2 at (122.75, 142.0):
add_track(128.75, 142.00, 128.75, 144.00, "F.Cu", 2)
add_track(128.75, 144.00, 122.75, 144.00, "F.Cu", 2)
add_track(122.75, 144.00, 122.75, 142.00, "F.Cu", 2)

# Feed SHT45_1 at (108.17, 127.50) via Y=144.0:
add_track(122.75, 144.00, 108.17, 144.00, "F.Cu", 2)
add_track(108.17, 144.00, 108.17, 127.50, "F.Cu", 2)

# Feed GPS_1 at (102.33, 109.50) from SHT45_1:
add_track(108.17, 127.50, 102.33, 127.50, "F.Cu", 2)
add_track(102.33, 127.50, 102.33, 109.50, "F.Cu", 2)

# -------------------------------------------------------------
# 6. NET 6: I2C_SCL (BOTTOM LAYER + VIA TO R4)
# -------------------------------------------------------------
# MCU_L_7 at (116.11, 117.90) to SHT45_4 at (115.79, 127.50)
# To avoid MCU_L_8 at (116.11, 120.44), go east to X=119.2 first!
add_track(116.11, 117.90, 119.20, 117.90, "B.Cu", 6)
add_track(119.20, 117.90, 119.20, 124.50, "B.Cu", 6)
add_track(119.20, 124.50, 115.79, 124.50, "B.Cu", 6)
add_track(115.79, 124.50, 115.79, 127.50, "B.Cu", 6) # into SHT45_4

# SHT45_4 to Highway at Y=131.0:
add_track(115.79, 127.50, 115.79, 131.00, "B.Cu", 6)
# Highway across to GY-521_3 at (134.64, 127.5):
add_track(115.79, 131.00, 134.64, 131.00, "B.Cu", 6)
add_track(134.64, 131.00, 134.64, 127.50, "B.Cu", 6) # into GY-521_3

# Feed R4_1 at (127.25, 142.0) from Highway Y=131.0:
# Place via at (127.25, 139.0)
add_track(127.25, 131.00, 127.25, 139.00, "B.Cu", 6)
add_via(127.25, 139.00, 6)
add_track(127.25, 139.00, 127.25, 142.00, "F.Cu", 6) # into R4_1

# Connect to BH1750_3 at (142.75, 123.20):
# Route from GY-521_3 south to Y=121.2 (clear of GY-521 Pin 6 at 142.26, 127.5):
add_track(134.64, 127.50, 134.64, 121.20, "B.Cu", 6)
add_track(134.64, 121.20, 142.75, 121.20, "B.Cu", 6)
add_track(142.75, 121.20, 142.75, 123.20, "B.Cu", 6) # into BH1750_3

# -------------------------------------------------------------
# 7. NET 5: I2C_SDA (BOTTOM LAYER + VIA TO R3)
# -------------------------------------------------------------
# MCU_L_6 at (116.11, 115.36) to SHT45_5 at (118.33, 127.50)
add_track(116.11, 115.36, 118.33, 115.36, "B.Cu", 5)
add_track(118.33, 115.36, 118.33, 127.50, "B.Cu", 5) # into SHT45_5

# SHT45_5 to Highway at Y=133.5:
add_track(118.33, 127.50, 118.33, 133.50, "B.Cu", 5)
# Highway across to GY-521_4 at (137.18, 127.50):
add_track(118.33, 133.50, 137.18, 133.50, "B.Cu", 5)
add_track(137.18, 133.50, 137.18, 127.50, "B.Cu", 5) # into GY-521_4

# Feed R3_1 at (121.25, 142.0) from Highway Y=133.5:
# Place via at (121.25, 139.0)
add_track(121.25, 133.50, 121.25, 139.00, "B.Cu", 5)
add_via(121.25, 139.00, 5)
add_track(121.25, 139.00, 121.25, 142.00, "F.Cu", 5) # into R3_1

# Connect to BH1750_4 at (145.29, 123.20):
# Route from GY-521_4 south to Y=121.2:
add_track(137.18, 127.50, 137.18, 119.50, "B.Cu", 5)
add_track(137.18, 119.50, 145.29, 119.50, "B.Cu", 5)
add_track(145.29, 119.50, 145.29, 123.20, "B.Cu", 5) # into BH1750_4

# -------------------------------------------------------------
# 8. NET 1: GND (ROBUST COMPLETE DISTRIBUTION)
# -------------------------------------------------------------
# Bottom GND:
# MCU_L_2 at (116.11, 105.20) to GPS_2 at (104.87, 109.50) and H1 at (103.5, 103.5):
add_track(116.11, 105.20, 104.87, 105.20, "B.Cu", 1)
add_track(104.87, 105.20, 104.87, 109.50, "B.Cu", 1) # into GPS_2
add_track(104.87, 105.20, 103.50, 103.83, "B.Cu", 1)
add_track(103.50, 103.83, 103.50, 103.50, "B.Cu", 1) # into H1

# Connect MCU_L_2 across to MCU_R_1 at (133.89, 102.66):
add_track(116.11, 105.20, 120.00, 101.50, "B.Cu", 1)
add_track(120.00, 101.50, 130.00, 101.50, "B.Cu", 1)
add_track(130.00, 101.50, 133.89, 102.66, "B.Cu", 1) # into MCU_R_1

# MCU_R_1 to H2 at (146.5, 103.5):
add_track(133.89, 102.66, 146.50, 102.66, "F.Cu", 1)
add_track(146.50, 102.66, 146.50, 103.50, "F.Cu", 1) # into H2

# H2 to H4 at (146.5, 146.5) along right edge X=148.5:
add_track(146.50, 103.50, 148.50, 105.50, "F.Cu", 1)
add_track(148.50, 105.50, 148.50, 144.50, "F.Cu", 1)
add_track(148.50, 144.50, 146.50, 146.50, "F.Cu", 1) # into H4

# Connect BH1750 GNDs on F.Cu:
add_track(148.50, 123.20, 147.83, 123.20, "F.Cu", 1) # into BH_5
add_track(148.50, 117.50, 140.21, 117.50, "F.Cu", 1)
add_track(140.21, 117.50, 140.21, 123.20, "F.Cu", 1) # into BH_2

# J1_2 at (124.0, 146.5) to H4:
add_track(124.00, 146.50, 124.00, 148.50, "F.Cu", 1)
add_track(124.00, 148.50, 144.50, 148.50, "F.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "F.Cu", 1) # into H4

# GY-521 GNDs to H4:
add_track(144.80, 127.50, 144.80, 137.00, "F.Cu", 1) # into GY_7
add_track(132.10, 127.50, 132.10, 137.00, "F.Cu", 1) # into GY_2
add_track(132.10, 137.00, 146.50, 137.00, "F.Cu", 1)
add_track(146.50, 137.00, 146.50, 146.50, "F.Cu", 1) # into H4

# SHT45_3 at (113.25, 127.5) to H3 at (103.5, 146.5):
add_track(113.25, 127.50, 113.25, 138.00, "F.Cu", 1)
add_track(113.25, 138.00, 103.50, 138.00, "F.Cu", 1)
add_track(103.50, 138.00, 103.50, 146.50, "F.Cu", 1) # into H3

# Connect H1 to H3 along left edge X=101.5 on F.Cu:
add_track(103.50, 103.50, 101.50, 105.50, "F.Cu", 1)
add_track(101.50, 105.50, 101.50, 144.50, "F.Cu", 1)
add_track(101.50, 144.50, 103.50, 146.50, "F.Cu", 1) # into H3

# Connect H3 to H4 along top edge on B.Cu (clear of F.Cu BAT+):
add_track(103.50, 146.50, 105.50, 148.50, "B.Cu", 1)
add_track(105.50, 148.50, 144.50, 148.50, "B.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "B.Cu", 1) # into H4

# Stitching Vias between F.Cu GND and B.Cu GND:
add_via(103.50, 103.50, 1) # near H1
add_via(146.50, 103.50, 1) # near H2
add_via(103.50, 146.50, 1) # near H3
add_via(146.50, 146.50, 1) # near H4

# Assemble content
pcb_content = "".join(header_and_footprints) + bot_outlines + "\n".join(tracks) + "\n" + "\n".join(vias) + "\n)\n"

with open(TEST_PCB, "w", encoding="utf-8") as f:
    f.write(pcb_content)

print("Generated test_routed.kicad_pcb. Running KiCad DRC...")
res = subprocess.run([KICAD_CLI, "pcb", "drc", "--output", "scratch/drc_result.json", TEST_PCB], capture_output=True, text=True)
print("Return code:", res.returncode)
print(res.stdout)
