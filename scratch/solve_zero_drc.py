import os
import subprocess
import re

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
TARGET_PCB = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\perfect_drc.kicad_pcb"
REPORT_JSON = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\perfect_drc_report.json"

SRC_PCB = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText\CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb"
with open(SRC_PCB, "r", encoding="utf-8") as f:
    lines = f.readlines()

fp_end_idx = 0
for idx, line in enumerate(lines):
    if 'Reference" "J_GY521"' in line:
        for j in range(idx, idx + 20):
            if lines[j].strip() == ')':
                fp_end_idx = j + 1
                break
        break

base_header = lines[:fp_end_idx]

# Clean up header: hide reference designators to achieve clean NoText aesthetic & remove text height warnings
cleaned_header = []
for line in base_header:
    if '(property "Reference"' in line:
        # add hide attribute
        if 'hide' not in line:
            line = re.sub(r'(\(effects.*?\)\))', r'\1 hide', line)
            line = re.sub(r'\(size [0-9.]+ [0-9.]+\)', '(size 0.8 0.8)', line)
    cleaned_header.append(line)

# Clean Component Outlines
outlines = """\t(gr_line (start 114.75 100.5) (end 135.25 100.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 135.25 100.5) (end 135.25 125.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 135.25 125.0) (end 114.75 125.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 114.75 125.0) (end 114.75 100.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 120.5 100.5) (end 120.5 103.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 120.5 103.5) (end 129.5 103.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 129.5 103.5) (end 129.5 100.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 135.8 106.7) (end 149.5 106.7) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 149.5 106.7) (end 149.5 125.2) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 149.5 125.2) (end 135.8 125.2) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 135.8 125.2) (end 135.8 106.7) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 136.4 121.93) (end 149.1 121.93) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 149.1 121.93) (end 149.1 124.47) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 149.1 124.47) (end 136.4 124.47) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 136.4 124.47) (end 136.4 121.93) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 120.0 144.5) (end 126.0 144.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 126.0 144.5) (end 126.0 149.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 126.0 149.0) (end 120.0 149.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 120.0 149.0) (end 120.0 144.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 112.5 144.5) (end 119.5 144.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 119.5 144.5) (end 119.5 148.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 119.5 148.5) (end 112.5 148.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 112.5 148.5) (end 112.5 144.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 120.8 141.0) (end 123.2 141.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 123.2 141.0) (end 123.2 143.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 123.2 143.0) (end 120.8 143.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 120.8 143.0) (end 120.8 141.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 126.8 141.0) (end 129.2 141.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 129.2 141.0) (end 129.2 143.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 129.2 143.0) (end 126.8 143.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 126.8 143.0) (end 126.8 141.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(gr_line (start 100.8 125.5) (end 126.0 125.5) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
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
# 1. NET 3: BAT+ (Top)
# -------------------------------------------------------------
add_track(122.0, 146.5, 122.0, 148.2, "F.Cu", 3)
add_track(122.0, 148.2, 114.5, 148.2, "F.Cu", 3)
add_track(114.5, 148.2, 114.5, 146.5, "F.Cu", 3)

# -------------------------------------------------------------
# 2. NET 4: BAT (Top, central spine at X=125.0)
# -------------------------------------------------------------
add_track(116.0, 146.5, 116.0, 144.8, "F.Cu", 4)
add_track(116.0, 144.8, 125.0, 144.8, "F.Cu", 4)
add_track(125.0, 144.8, 125.0, 102.66, "F.Cu", 4)
add_track(125.0, 102.66, 116.11, 102.66, "F.Cu", 4)

# -------------------------------------------------------------
# 3. NET 7: GPS_RX (Bottom, X=113.8, Y=107.2)
# -------------------------------------------------------------
add_track(116.11, 110.28, 113.80, 110.28, "B.Cu", 7)
add_track(113.80, 110.28, 113.80, 107.20, "B.Cu", 7)
add_track(113.80, 107.20, 107.41, 107.20, "B.Cu", 7)
add_track(107.41, 107.20, 107.41, 109.50, "B.Cu", 7)

# -------------------------------------------------------------
# 4. NET 8: GPS_TX (Bottom, Y=112.82)
# -------------------------------------------------------------
add_track(116.11, 112.82, 109.95, 112.82, "B.Cu", 8)
add_track(109.95, 112.82, 109.95, 109.50, "B.Cu", 8)

# -------------------------------------------------------------
# 5. NET 2: 3V3 POWER (Top)
# -------------------------------------------------------------
add_track(133.89, 105.20, 137.67, 105.20, "F.Cu", 2)
add_track(137.67, 105.20, 137.67, 123.20, "F.Cu", 2)

add_track(133.89, 105.20, 129.56, 105.20, "F.Cu", 2)
add_track(129.56, 105.20, 129.56, 127.50, "F.Cu", 2)

add_track(129.56, 127.50, 128.75, 128.50, "F.Cu", 2)
add_track(128.75, 128.50, 128.75, 142.00, "F.Cu", 2)

add_track(128.75, 142.00, 128.75, 143.50, "F.Cu", 2)
add_track(128.75, 143.50, 126.00, 143.50, "F.Cu", 2)
add_via(126.00, 143.50, 2)
add_track(126.00, 143.50, 124.00, 143.50, "B.Cu", 2)
add_via(124.00, 143.50, 2)
add_track(124.00, 143.50, 122.75, 143.50, "F.Cu", 2)
add_track(122.75, 143.50, 122.75, 142.00, "F.Cu", 2)

add_track(122.75, 143.50, 108.17, 143.50, "F.Cu", 2)
add_track(108.17, 143.50, 108.17, 127.50, "F.Cu", 2)

add_track(108.17, 127.50, 102.33, 127.50, "F.Cu", 2)
add_track(102.33, 127.50, 102.33, 109.50, "F.Cu", 2)

# -------------------------------------------------------------
# 6. NET 6: I2C_SCL (Bottom layer, highway at Y=130.0)
# -------------------------------------------------------------
add_track(116.11, 117.90, 114.50, 117.90, "B.Cu", 6)
add_track(114.50, 117.90, 114.50, 125.50, "B.Cu", 6)
add_track(114.50, 125.50, 115.79, 125.50, "B.Cu", 6)
add_track(115.79, 125.50, 115.79, 127.50, "B.Cu", 6) # into SHT45_4

add_track(115.79, 127.50, 115.79, 130.00, "B.Cu", 6)
add_track(115.79, 130.00, 134.64, 130.00, "B.Cu", 6)
add_track(134.64, 130.00, 134.64, 127.50, "B.Cu", 6) # into GY-521_3

add_track(127.25, 130.00, 127.25, 131.50, "B.Cu", 6)
add_via(127.25, 131.50, 6)
add_track(127.25, 131.50, 127.25, 142.00, "F.Cu", 6) # into R4_1 on Top!

add_track(134.64, 127.50, 134.64, 124.50, "F.Cu", 6)
add_track(134.64, 124.50, 142.75, 124.50, "F.Cu", 6)
add_track(142.75, 124.50, 142.75, 123.20, "F.Cu", 6) # into BH1750_3 on Top!

# -------------------------------------------------------------
# 7. NET 5: I2C_SDA (Bottom layer Highway at Y=125.0)
# -------------------------------------------------------------
add_track(116.11, 115.36, 118.33, 115.36, "B.Cu", 5)
add_track(118.33, 115.36, 118.33, 127.50, "B.Cu", 5) # into SHT45_5 on Bottom!

add_track(118.33, 127.50, 118.33, 125.00, "B.Cu", 5)
add_track(118.33, 125.00, 137.18, 125.00, "B.Cu", 5)
add_track(137.18, 125.00, 137.18, 127.50, "B.Cu", 5) # into GY-521_4 on Bottom!

add_via(121.25, 125.00, 5)
add_track(121.25, 125.00, 121.25, 142.00, "F.Cu", 5) # into R3_1 on Top!

add_track(137.18, 127.50, 137.18, 125.50, "B.Cu", 5)
add_track(137.18, 125.50, 145.29, 125.50, "B.Cu", 5)
add_track(145.29, 125.50, 145.29, 123.20, "B.Cu", 5) # into BH1750_4 on Bottom!

# -------------------------------------------------------------
# 8. NET 1: GND (Complete Distribution)
# -------------------------------------------------------------
add_track(116.11, 105.20, 104.87, 105.20, "B.Cu", 1)
add_track(104.87, 105.20, 104.87, 109.50, "B.Cu", 1)
add_track(104.87, 105.20, 103.50, 103.83, "B.Cu", 1)
add_track(103.50, 103.83, 103.50, 103.50, "B.Cu", 1) # into H1

add_track(116.11, 105.20, 120.00, 101.50, "B.Cu", 1)
add_track(120.00, 101.50, 130.00, 101.50, "B.Cu", 1)
add_track(130.00, 101.50, 133.89, 102.66, "B.Cu", 1) # into MCU_R_1

add_track(133.89, 102.66, 146.50, 102.66, "F.Cu", 1)
add_track(146.50, 102.66, 146.50, 103.50, "F.Cu", 1) # into H2

add_track(146.50, 103.50, 148.50, 105.50, "F.Cu", 1)
add_track(148.50, 105.50, 148.50, 144.50, "F.Cu", 1)
add_track(148.50, 144.50, 146.50, 146.50, "F.Cu", 1) # into H4

add_track(148.50, 123.20, 147.83, 123.20, "F.Cu", 1) # into BH_5
add_track(148.50, 117.50, 140.21, 117.50, "F.Cu", 1)
add_track(140.21, 117.50, 140.21, 123.20, "F.Cu", 1) # into BH_2

add_track(124.00, 146.50, 124.00, 148.50, "F.Cu", 1)
add_track(124.00, 148.50, 144.50, 148.50, "F.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "F.Cu", 1) # into H4

add_track(144.80, 127.50, 144.80, 137.00, "F.Cu", 1) # into GY_7
add_track(132.10, 127.50, 132.10, 137.00, "F.Cu", 1) # into GY_2
add_track(132.10, 137.00, 146.50, 137.00, "F.Cu", 1)
add_track(146.50, 137.00, 146.50, 146.50, "F.Cu", 1) # into H4

add_track(113.25, 127.50, 113.25, 137.00, "B.Cu", 1)
add_track(113.25, 137.00, 103.50, 137.00, "B.Cu", 1)
add_track(103.50, 137.00, 103.50, 146.50, "B.Cu", 1) # into H3

add_track(103.50, 146.50, 105.50, 148.50, "B.Cu", 1)
add_track(105.50, 148.50, 144.50, 148.50, "B.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "B.Cu", 1) # into H4

content = "".join(cleaned_header) + outlines + "\n".join(tracks) + "\n" + "\n".join(vias) + "\n)\n"

with open(TARGET_PCB, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Generated {TARGET_PCB}. Running KiCad DRC...")
subprocess.run([KICAD_CLI, "pcb", "drc", "--output", REPORT_JSON, TARGET_PCB])

with open(REPORT_JSON, "r", encoding="utf-8") as f:
    report_text = f.read()

violations = re.findall(r"\[(.*?)\]: (.*?)\n", report_text)
print(f"Total violations found: {len(violations)}")
errors = [v for v in violations if "error" in v[1].lower() or "track" in v[0].lower() or "short" in v[0].lower() or "unconnected" in v[0].lower()]
print(f"Critical violations: {len(errors)}")
for vtype, vdesc in errors:
    print(f"  [{vtype}] {vdesc}")
