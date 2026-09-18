import os
import subprocess
import json

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
TEST_PCB = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\test_new_pinout.kicad_pcb"
REPORT_JSON = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\test_new_pinout_report.json"

pcb_header = """(kicad_pcb
	(version 20260206)
	(generator "pcbnew")
	(generator_version "10.0")
	(general
		(thickness 1.6)
		(legacy_teardrops no)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(5 "F.SilkS" user "F.Silkscreen")
		(7 "B.SilkS" user "B.Silkscreen")
		(1 "F.Mask" user)
		(3 "B.Mask" user)
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
		(allow_soldermask_bridges_in_footprints no)
		(tenting (front yes) (back yes))
	)
	(net 0 "")
	(net 1 "GND")
	(net 2 "3V3")
	(net 3 "BAT+")
	(net 4 "BAT")
	(net 5 "I2C_SDA")
	(net 6 "I2C_SCL")
	(net 7 "GPS_RX")
	(net 8 "GPS_TX")

	(gr_line (start 102.0 100.0) (end 148.0 100.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
	(gr_line (start 148.0 100.0) (end 150.0 102.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
	(gr_line (start 150.0 102.0) (end 150.0 148.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
	(gr_line (start 150.0 148.0) (end 148.0 150.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
	(gr_line (start 148.0 150.0) (end 102.0 150.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
	(gr_line (start 102.0 150.0) (end 100.0 148.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
	(gr_line (start 100.0 148.0) (end 100.0 102.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))
	(gr_line (start 100.0 102.0) (end 102.0 100.0) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))

	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 103.5 103.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)
	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 146.5 103.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)
	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 103.5 146.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)
	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu") (at 146.5 146.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.5 5.5) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (layer "F.Cu") (at 116.11 111.55)
		(property "Reference" "J_MCU_L" (at 0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" thru_hole rect (at 0 -8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "2" thru_hole circle (at 0 -6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "3" thru_hole circle (at 0 -3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "4" thru_hole circle (at 0 -1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "5" thru_hole circle (at 0 1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "6" thru_hole circle (at 0 3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "7" thru_hole circle (at 0 6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "8" thru_hole circle (at 0 8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (layer "F.Cu") (at 133.89 111.55)
		(property "Reference" "J_MCU_R" (at 0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" thru_hole rect (at 0 -8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 4 "BAT"))
		(pad "2" thru_hole circle (at 0 -6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at 0 -3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "4" thru_hole circle (at 0 -1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
		(pad "5" thru_hole circle (at 0 1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
		(pad "6" thru_hole circle (at 0 3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "7" thru_hole circle (at 0 6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "8" thru_hole circle (at 0 8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "F.Cu") (at 142.75 123.2)
		(property "Reference" "J_BH1750" (at 0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 107.41 109.5)
		(property "Reference" "J_GPS" (at 0 0) (layer "B.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)

	(footprint "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal" (layer "F.Cu") (at 123.0 146.5)
		(property "Reference" "J1" (at 0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" thru_hole roundrect (at -1.0 0) (size 1.2 1.7) (drill 0.8) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.25) (net 3 "BAT+"))
		(pad "2" thru_hole oval (at 1.0 0) (size 1.2 1.7) (drill 0.8) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)

	(footprint "Button_Switch_SMD:SW_SPDT_PCM12" (layer "F.Cu") (at 116.0 146.5)
		(property "Reference" "SW1" (at 0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" smd roundrect (at -1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 3 "BAT+"))
		(pad "2" smd roundrect (at 0 0) (size 1.0 1.5) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 4 "BAT"))
		(pad "3" smd roundrect (at 1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 0 ""))
	)

	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 122.0 142.0)
		(property "Reference" "R3" (at 0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" smd roundrect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 5 "I2C_SDA"))
		(pad "2" smd roundrect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 2 "3V3"))
	)

	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 128.0 142.0)
		(property "Reference" "R4" (at 0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" smd roundrect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 6 "I2C_SCL"))
		(pad "2" smd roundrect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 113.25 127.5)
		(property "Reference" "J_SHT45" (at 0 0) (layer "B.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Horizontal" (layer "B.Cu") (at 138.42 127.5)
		(property "Reference" "J_GY521" (at 0 0) (layer "B.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))
		(pad "1" thru_hole rect (at -8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "2" thru_hole circle (at -6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at -3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "4" thru_hole circle (at -1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "5" thru_hole circle (at 1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "6" thru_hole circle (at 3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "7" thru_hole circle (at 6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "8" thru_hole circle (at 8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
	)
"""

# Silkscreen outlines (courtyard outlines)
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
# 1. NET 3: BAT+ (Top F.Cu)
# -------------------------------------------------------------
# J1 Pad 1 (122.0, 146.5) -> SW1 Pad 1 (114.5, 146.5)
add_track(122.0, 146.5, 122.0, 148.2, "F.Cu", 3)
add_track(122.0, 148.2, 114.5, 148.2, "F.Cu", 3)
add_track(114.5, 148.2, 114.5, 146.5, "F.Cu", 3)

# -------------------------------------------------------------
# 2. NET 4: BAT (Top F.Cu)
# -------------------------------------------------------------
# SW1 Pad 2 (116.0, 146.5) -> J_MCU_R Pad 1 (133.89, 102.66)
add_track(116.0, 146.5, 116.0, 144.8, "F.Cu", 4)
add_track(116.0, 144.8, 125.0, 144.8, "F.Cu", 4)
add_track(125.0, 144.8, 125.0, 102.66, "F.Cu", 4)
add_track(125.0, 102.66, 133.89, 102.66, "F.Cu", 4) # into MCU_R Pin 1!

# -------------------------------------------------------------
# 3. NET 2: 3V3 POWER (Top F.Cu)
# -------------------------------------------------------------
# Source: J_MCU_L Pin 2 (116.11, 105.20)
# Feed 1: West to GPS Pin 1 (102.33, 109.50)
# Avoid H1 pad (X: 100.75..106.25, Y: 100.75..106.25)
# Go to X=107.0 at Y=105.2, drop to Y=107.2 (below H1 pad!), go West to 102.33, then drop to 109.50!
add_track(116.11, 105.20, 107.00, 105.20, "F.Cu", 2)
add_track(107.00, 105.20, 107.00, 107.20, "F.Cu", 2)
add_track(107.00, 107.20, 102.33, 107.20, "F.Cu", 2) # below H1 pad!
add_track(102.33, 107.20, 102.33, 109.50, "F.Cu", 2) # into GPS Pin 1!

# Feed 2: South to SHT45 Pin 4 (115.79, 127.50) & Pin 5 (118.33, 127.50)
# Route West of MCU_L at X=114.50
add_track(116.11, 105.20, 114.50, 105.20, "F.Cu", 2)
add_track(114.50, 105.20, 114.50, 124.50, "F.Cu", 2)
add_track(114.50, 124.50, 115.79, 124.50, "F.Cu", 2)
add_track(115.79, 124.50, 115.79, 127.50, "F.Cu", 2) # into SHT45 Pin 4!
add_track(115.79, 124.50, 118.33, 124.50, "F.Cu", 2)
add_track(118.33, 124.50, 118.33, 127.50, "F.Cu", 2) # into SHT45 Pin 5!

# Feed 3: To Pull-ups R3 Pin 2 (122.75, 142.0) & R4 Pin 2 (128.75, 142.0)
add_track(118.33, 124.50, 118.33, 143.50, "F.Cu", 2)
add_track(118.33, 143.50, 122.75, 143.50, "F.Cu", 2)
add_track(122.75, 143.50, 122.75, 142.00, "F.Cu", 2) # into R3 Pin 2!

# Cross X=125.0 BAT spine at Y=143.5 via B.Cu bridge
add_track(122.75, 143.50, 123.80, 143.50, "F.Cu", 2)
add_via(123.80, 143.50, 2)
add_track(123.80, 143.50, 126.20, 143.50, "B.Cu", 2)
add_via(126.20, 143.50, 2)
add_track(126.20, 143.50, 128.75, 143.50, "F.Cu", 2)
add_track(128.75, 143.50, 128.75, 142.00, "F.Cu", 2) # into R4 Pin 2!

# Feed 4: North route across Beetle to East side (BH1750 & MPU6050)
# From MCU_L Pin 2 (116.11, 105.20), step up to Y=103.93 (between MCU_R Pin 1 and Pin 2!)
add_track(116.11, 105.20, 117.50, 105.20, "F.Cu", 2)
add_track(117.50, 105.20, 117.50, 103.93, "F.Cu", 2)
add_track(117.50, 103.93, 147.50, 103.93, "F.Cu", 2) # cleanly passes between BAT (102.66) and GND (105.20)!
add_track(147.50, 103.93, 147.83, 103.93, "F.Cu", 2)
add_track(147.83, 103.93, 147.83, 123.20, "F.Cu", 2) # into BH1750 Pin 5!
add_track(147.83, 123.20, 147.31, 123.20, "F.Cu", 2)
add_track(147.31, 123.20, 147.31, 127.50, "F.Cu", 2) # into MPU6050 Pin 8!

# -------------------------------------------------------------
# 4. NET 5: I2C_SDA (Bottom B.Cu)
# -------------------------------------------------------------
# Source: J_MCU_R Pin 6 (133.89, 115.36)
# Target 1: East to BH1750 Pin 2 (140.21, 123.20) & MPU6050 Pin 5 (139.69, 127.50)
add_track(133.89, 115.36, 139.69, 115.36, "B.Cu", 5)
add_track(139.69, 115.36, 139.69, 127.50, "B.Cu", 5) # into MPU6050 Pin 5!
add_track(139.69, 123.20, 140.21, 123.20, "B.Cu", 5) # into BH1750 Pin 2!

# Target 2: West along Highway at Y=125.00 to SHT45 Pin 1 (108.17, 127.50)
# From 139.69, 125.00, run West along Y=125.00
add_track(139.69, 125.00, 108.17, 125.00, "B.Cu", 5) # Highway Y=125.00!
add_track(108.17, 125.00, 108.17, 127.50, "B.Cu", 5) # into SHT45 Pin 1!

# Tap to R3 Pin 1 (121.25, 142.00) on Top F.Cu
add_via(121.25, 125.00, 5)
add_track(121.25, 125.00, 121.25, 142.00, "F.Cu", 5) # into R3 Pin 1 on Top!

# -------------------------------------------------------------
# 5. NET 6: I2C_SCL (Bottom B.Cu)
# -------------------------------------------------------------
# Source: J_MCU_R Pin 7 (133.89, 117.90)
# Target 1: East to BH1750 Pin 3 (142.75, 123.20) & MPU6050 Pin 6 (142.23, 127.50)
add_track(133.89, 117.90, 142.23, 117.90, "B.Cu", 6)
add_track(142.23, 117.90, 142.23, 127.50, "B.Cu", 6) # into MPU6050 Pin 6!
add_track(142.23, 123.20, 142.75, 123.20, "B.Cu", 6) # into BH1750 Pin 3!

# Target 2: West along Highway at Y=130.00 to SHT45 Pin 2 (110.71, 127.50)
# From 142.23, drop to Y=130.0 at X=142.23? Wait, at X=142.23 GY-521 Pin 6 is at 127.50!
# We can drop to Y=130.00 at X=142.23 from 127.50 directly!
add_track(142.23, 127.50, 142.23, 130.00, "B.Cu", 6)
add_track(142.23, 130.00, 110.71, 130.00, "B.Cu", 6) # Highway Y=130.00!
add_track(110.71, 130.00, 110.71, 127.50, "B.Cu", 6) # into SHT45 Pin 2!

# Tap to R4 Pin 1 (127.25, 142.00) on Top F.Cu
add_track(127.25, 130.00, 127.25, 131.50, "B.Cu", 6)
add_via(127.25, 131.50, 6)
add_track(127.25, 131.50, 127.25, 142.00, "F.Cu", 6) # into R4 Pin 1 on Top!

# -------------------------------------------------------------
# 6. NET 7: GPS_RX (Bottom B.Cu)
# -------------------------------------------------------------
# J_MCU_R Pin 4 (133.89, 110.28) to J_GPS Pin 4 (109.95, 109.50)
# Route West into center alleyway, drop to Y=121.50, cross to West!
add_track(133.89, 110.28, 126.00, 110.28, "B.Cu", 7)
add_track(126.00, 110.28, 126.00, 121.50, "B.Cu", 7)
add_track(126.00, 121.50, 109.95, 121.50, "B.Cu", 7) # cross below MCU_L at Y=121.50
add_track(109.95, 121.50, 109.95, 109.50, "B.Cu", 7) # into GPS Pin 4!

# -------------------------------------------------------------
# 7. NET 8: GPS_TX (Bottom B.Cu)
# -------------------------------------------------------------
# J_MCU_R Pin 5 (133.89, 112.82) to J_GPS Pin 3 (107.41, 109.50)
# Route West into center alleyway, drop to Y=123.00, cross to West!
add_track(133.89, 112.82, 124.00, 112.82, "B.Cu", 8)
add_track(124.00, 112.82, 124.00, 123.00, "B.Cu", 8)
add_track(124.00, 123.00, 107.41, 123.00, "B.Cu", 8) # cross below MCU_L at Y=123.00
add_track(107.41, 123.00, 107.41, 109.50, "B.Cu", 8) # into GPS Pin 3!

# -------------------------------------------------------------
# 8. NET 1: GND (Complete Distribution)
# -------------------------------------------------------------
# 1) H1 (103.5, 103.5) & GPS Pin 2 (104.87, 109.5) & MCU_L Pin 1 (116.11, 102.66)
add_track(103.50, 103.50, 104.87, 103.50, "B.Cu", 1)
add_track(104.87, 103.50, 104.87, 109.50, "B.Cu", 1) # into GPS Pin 2!
add_track(104.87, 103.50, 116.11, 102.66, "B.Cu", 1) # into MCU_L Pin 1!

# 2) SHT45 Pin 3 (113.25, 127.50) -> H3 (103.5, 146.5) on Top F.Cu (avoids B.Cu SCL line!)
add_track(113.25, 127.50, 113.25, 137.00, "F.Cu", 1)
add_track(113.25, 137.00, 103.50, 137.00, "F.Cu", 1)
add_track(103.50, 137.00, 103.50, 146.50, "F.Cu", 1) # into H3 on F.Cu!

# 3) H3 (103.5, 146.5) -> H4 (146.5, 146.5) along bottom edge at Y=148.50
add_track(103.50, 146.50, 105.50, 148.50, "B.Cu", 1)
add_track(105.50, 148.50, 144.50, 148.50, "B.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "B.Cu", 1) # into H4!

# J1 Pin 2 (124.0, 146.5) into H4 ground on F.Cu
add_track(124.00, 146.50, 124.00, 148.50, "F.Cu", 1)
add_track(124.00, 148.50, 144.50, 148.50, "F.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "F.Cu", 1) # into H4 on F.Cu!

# 4) MCU_R Pin 2 (133.89, 105.20) -> H2 (146.5, 103.5)
add_track(133.89, 105.20, 146.50, 105.20, "F.Cu", 1)
add_track(146.50, 105.20, 146.50, 103.50, "F.Cu", 1) # into H2!

# 5) H2 (146.5, 103.5) -> H4 (146.5, 146.5) on B.Cu!
add_track(146.50, 103.50, 146.50, 146.50, "B.Cu", 1)

# 6) BH1750 Pin 1 (137.67, 123.20) & Pin 4 (145.29, 123.20) into GND
# Pin 4 (145.29, 123.20) -> H4 on F.Cu
add_track(145.29, 123.20, 145.29, 144.50, "F.Cu", 1)
add_track(145.29, 144.50, 146.50, 146.50, "F.Cu", 1) # into H4!
# Pin 1 (137.67, 123.20) -> Pin 4 (145.29) via Y=121.0
add_track(137.67, 123.20, 137.67, 121.00, "F.Cu", 1)
add_track(137.67, 121.00, 145.29, 121.00, "F.Cu", 1)
add_track(145.29, 121.00, 145.29, 123.20, "F.Cu", 1)

# 7) MPU6050 Pin 2 (132.07, 127.50) & Pin 7 (144.77, 127.50) into GND
add_track(144.77, 127.50, 144.77, 137.00, "F.Cu", 1)
add_track(132.07, 127.50, 132.07, 137.00, "F.Cu", 1)
add_track(132.07, 137.00, 145.29, 137.00, "F.Cu", 1) # joins Pin 4 GND line!

# Top GND bridge at Y=100.80 (clears Pin 1 BAT pad at 133.89, 102.66!)
add_track(103.50, 103.50, 105.50, 100.80, "B.Cu", 1)
add_track(105.50, 100.80, 144.50, 100.80, "B.Cu", 1)
add_track(144.50, 100.80, 146.50, 103.50, "B.Cu", 1) # Top GND bridge at Y=100.80!

content = pcb_header + outlines + "\n".join(tracks) + "\n" + "\n".join(vias) + "\n)\n"

with open(TEST_PCB, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Generated {TEST_PCB}. Running KiCad DRC...")
res = subprocess.run([KICAD_CLI, "pcb", "drc", "--output", REPORT_JSON, "--format", "json", TEST_PCB], capture_output=True, text=True)
print("DRC Return Code:", res.returncode)

with open(REPORT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

violations = data.get("violations", [])
unconnected = data.get("unconnected_items", [])
errors = [v for v in violations if v.get("severity") == "error"]

print(f"Total Violations: {len(violations)}")
print(f"Unconnected Items: {len(unconnected)}")
print(f"Critical Errors: {len(errors)}")

for e in errors:
    print("  ERROR:", e.get("type"), e.get("description"))
