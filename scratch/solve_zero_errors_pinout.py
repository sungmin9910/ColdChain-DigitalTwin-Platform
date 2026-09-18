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

"""

footprints_str = """
	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu")
		(at 103.5 103.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.0 5.0) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)
	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu")
		(at 146.5 103.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.0 5.0) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)
	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu")
		(at 103.5 146.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.0 5.0) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)
	(footprint "MountingHole:MountingHole_3.2mm_M3_Pad" (layer "F.Cu")
		(at 146.5 146.5)
		(pad "1" thru_hole circle (at 0 0) (size 5.0 5.0) (drill 3.2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (layer "F.Cu")
		(at 116.11 111.55)
		(property "Reference" "J_MCU_L" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" thru_hole rect (at 0 -8.89) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "2" thru_hole oval (at 0 -6.35) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "3" thru_hole oval (at 0 -3.81) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "4" thru_hole oval (at 0 -1.27) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "5" thru_hole oval (at 0 1.27) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "6" thru_hole oval (at 0 3.81) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "7" thru_hole oval (at 0 6.35) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "8" thru_hole oval (at 0 8.89) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (layer "F.Cu")
		(at 133.89 111.55)
		(property "Reference" "J_MCU_R" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" thru_hole rect (at 0 -8.89) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 4 "BAT"))
		(pad "2" thru_hole oval (at 0 -6.35) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole oval (at 0 -3.81) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "4" thru_hole oval (at 0 -1.27) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
		(pad "5" thru_hole oval (at 0 1.27) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
		(pad "6" thru_hole oval (at 0 3.81) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "7" thru_hole oval (at 0 6.35) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "8" thru_hole oval (at 0 8.89) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "F.Cu")
		(at 142.75 123.2)
		(property "Reference" "J_BH1750" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "2" thru_hole oval (at -2.54 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "3" thru_hole oval (at 0 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "4" thru_hole oval (at 2.54 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "5" thru_hole oval (at 5.08 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "F.Cu")
		(at 107.41 109.5)
		(property "Reference" "J_GPS" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole oval (at -2.54 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole oval (at 0 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
		(pad "4" thru_hole oval (at 2.54 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
		(pad "5" thru_hole oval (at 5.08 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
	)

	(footprint "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal" (layer "F.Cu")
		(at 123.0 146.5)
		(property "Reference" "J1" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" thru_hole roundrect (at -1.0 0) (size 1.2 1.7) (drill 0.8) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.25) (net 3 "BAT+"))
		(pad "2" thru_hole oval (at 1.0 0) (size 1.2 1.7) (drill 0.8) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)

	(footprint "Button_Switch_SMD:SW_SPDT_PCM12" (layer "F.Cu")
		(at 116.0 146.5)
		(property "Reference" "SW1" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" smd rect (at -1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Mask") (net 3 "BAT+"))
		(pad "2" smd rect (at 0 0) (size 1.0 1.5) (layers "F.Cu" "F.Mask") (net 4 "BAT"))
		(pad "3" smd rect (at 1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Mask"))
	)

	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu")
		(at 122.0 142.0)
		(property "Reference" "R3" (at 0 -1.5 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" smd roundrect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 5 "I2C_SDA"))
		(pad "2" smd roundrect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 2 "3V3"))
	)

	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu")
		(at 128.0 142.0)
		(property "Reference" "R4" (at 0 -1.5 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" smd roundrect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 6 "I2C_SCL"))
		(pad "2" smd roundrect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "F.Cu")
		(at 113.25 127.5)
		(property "Reference" "J_SHT45" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "2" thru_hole oval (at -2.54 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "3" thru_hole oval (at 0 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "4" thru_hole oval (at 2.54 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "5" thru_hole oval (at 5.08 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Horizontal" (layer "F.Cu")
		(at 138.42 127.5)
		(property "Reference" "J_GY521" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))
		(pad "1" thru_hole rect (at -8.89 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "2" thru_hole oval (at -6.35 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole oval (at -3.81 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "4" thru_hole oval (at -1.27 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask"))
		(pad "5" thru_hole oval (at 1.27 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "6" thru_hole oval (at 3.81 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "7" thru_hole oval (at 6.35 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "8" thru_hole oval (at 8.89 0) (size 1.524 1.524) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
	)
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
# 3. NET 2: 3V3 POWER DISTRIBUTION
# -------------------------------------------------------------
# Source: J_MCU_L Pin 2 (116.11, 105.20)
# Feed 1: West to GPS Pin 1 (102.33, 109.50)
add_track(116.11, 105.20, 107.00, 105.20, "F.Cu", 2)
add_track(107.00, 105.20, 107.00, 107.20, "F.Cu", 2)
add_track(107.00, 107.20, 102.33, 107.20, "F.Cu", 2) # below H1 pad!
add_track(102.33, 107.20, 102.33, 109.50, "F.Cu", 2) # into GPS Pin 1!

# Feed 2: South to SHT45 Pin 4 (115.79, 127.50) & Pin 5 (118.33, 127.50)
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

# Cross BAT spine at X=125.0 via B.Cu bridge at Y=143.50
add_track(122.75, 143.50, 123.80, 143.50, "F.Cu", 2)
add_via(123.80, 143.50, 2)
add_track(123.80, 143.50, 126.20, 143.50, "B.Cu", 2)
add_via(126.20, 143.50, 2)
add_track(126.20, 143.50, 128.75, 143.50, "F.Cu", 2)
add_track(128.75, 143.50, 128.75, 142.00, "F.Cu", 2) # into R4 Pin 2!

# Feed 4: Across to East Side (BH1750 Pin 5 & MPU6050 Pin 8)
# From MCU_L Pin 2 (116.11, 105.20), step up to Y=103.93
# Hop under BAT (at X=125.0) via B.Cu bridge from X=123.0 to X=127.0
add_track(116.11, 105.20, 117.50, 105.20, "F.Cu", 2)
add_track(117.50, 105.20, 117.50, 103.93, "F.Cu", 2)
add_track(117.50, 103.93, 123.00, 103.93, "F.Cu", 2)
add_via(123.00, 103.93, 2)
add_track(123.00, 103.93, 127.00, 103.93, "B.Cu", 2) # passes cleanly under BAT track!
add_via(127.00, 103.93, 2)
add_track(127.00, 103.93, 136.50, 103.93, "F.Cu", 2) # cleanly between Beetle Pin 1 & Pin 2, safely west of H2!
# Route South at X=136.50 (corridor between MCU_R and H2)
add_track(136.50, 103.93, 136.50, 121.80, "F.Cu", 2)
# Branch East to BH1750 Pin 5 (147.83, 123.20)
add_track(136.50, 121.80, 147.83, 121.80, "F.Cu", 2)
add_track(147.83, 121.80, 147.83, 123.20, "F.Cu", 2) # into BH1750 Pin 5!
# Branch to MPU6050 Pin 8 (147.31, 127.50)
add_track(147.83, 121.80, 147.31, 121.80, "F.Cu", 2)
add_track(147.31, 121.80, 147.31, 127.50, "F.Cu", 2) # into MPU6050 Pin 8!

# -------------------------------------------------------------
# 4. NET 7: GPS_RX (Bottom B.Cu - Direct Route with J_GPS Pin 5 Bypass)
# -------------------------------------------------------------
# MCU_R Pin 4 (133.89, 110.28) to GPS Pin 4 (109.95, 109.50)
# Step between MCU_L Pin 3 & Pin 4 at Y=109.01, bypass Pin 5 via Y=107.20
add_track(133.89, 110.28, 130.00, 109.01, "B.Cu", 7)
add_track(130.00, 109.01, 114.50, 109.01, "B.Cu", 7)
add_track(114.50, 109.01, 114.50, 107.20, "B.Cu", 7) # bypass East of Pin 5
add_track(114.50, 107.20, 109.95, 107.20, "B.Cu", 7) # north of Pin 5
add_track(109.95, 107.20, 109.95, 109.50, "B.Cu", 7) # into GPS Pin 4!

# -------------------------------------------------------------
# 5. NET 8: GPS_TX (Bottom B.Cu - Direct Horizontal Route)
# -------------------------------------------------------------
# MCU_R Pin 5 (133.89, 112.82) to GPS Pin 3 (107.41, 109.50)
# Passes cleanly between MCU_L Pin 5 and Pin 6 at Y=114.09!
add_track(133.89, 112.82, 130.00, 114.09, "B.Cu", 8)
add_track(130.00, 114.09, 107.41, 114.09, "B.Cu", 8)
add_track(107.41, 114.09, 107.41, 109.50, "B.Cu", 8) # into GPS Pin 3!

# -------------------------------------------------------------
# 6. NET 5: I2C_SDA (Bottom B.Cu)
# -------------------------------------------------------------
# MCU_R Pin 6 (133.89, 115.36)
# Drop West into center alleyway at X=131.00, then down to Highway Y=125.00
add_track(133.89, 115.36, 131.00, 115.36, "B.Cu", 5)
add_track(131.00, 115.36, 131.00, 125.00, "B.Cu", 5)

# Highway East to BH1750 Pin 2 (140.21, 123.20) & MPU6050 Pin 5 (139.69, 127.50)
add_track(131.00, 125.00, 139.69, 125.00, "B.Cu", 5)
add_track(139.69, 125.00, 139.69, 127.50, "B.Cu", 5) # into MPU6050 Pin 5!
add_track(139.69, 125.00, 140.21, 125.00, "B.Cu", 5)
add_track(140.21, 125.00, 140.21, 123.20, "B.Cu", 5) # into BH1750 Pin 2!

# Highway West to SHT45 Pin 1 (108.17, 127.50)
add_track(131.00, 125.00, 108.17, 125.00, "B.Cu", 5)
add_track(108.17, 125.00, 108.17, 127.50, "B.Cu", 5) # into SHT45 Pin 1!

# Tap to R3 Pin 1 (121.25, 142.00) on Top F.Cu
add_via(121.25, 125.00, 5)
add_track(121.25, 125.00, 121.25, 142.00, "F.Cu", 5) # into R3 Pin 1!

# -------------------------------------------------------------
# 7. NET 6: I2C_SCL (Bottom B.Cu)
# -------------------------------------------------------------
# MCU_R Pin 7 (133.89, 117.90)
# Runs East to X=142.23 (safely east of SDA at 139.69!)
add_track(133.89, 117.90, 142.23, 117.90, "B.Cu", 6)
add_track(142.23, 117.90, 142.23, 127.50, "B.Cu", 6) # into MPU6050 Pin 6!
add_track(142.23, 123.20, 142.75, 123.20, "B.Cu", 6) # into BH1750 Pin 3!

# Highway West along Y=130.00 to SHT45 Pin 2 (110.71, 127.50)
add_track(142.23, 127.50, 142.23, 130.00, "B.Cu", 6)
add_track(142.23, 130.00, 110.71, 130.00, "B.Cu", 6)
add_track(110.71, 130.00, 110.71, 127.50, "B.Cu", 6) # into SHT45 Pin 2!

# Tap to R4 Pin 1 (127.25, 142.00) on Top F.Cu
add_track(127.25, 130.00, 127.25, 131.50, "B.Cu", 6)
add_via(127.25, 131.50, 6)
add_track(127.25, 131.50, 127.25, 142.00, "F.Cu", 6) # into R4 Pin 1!

# -------------------------------------------------------------
# 8. NET 1: GND (Complete Unified Distribution)
# -------------------------------------------------------------
# 1) H1 (103.5, 103.5) & GPS Pin 2 (104.87, 109.5) & MCU_L Pin 1 (116.11, 102.66)
add_track(103.50, 103.50, 104.87, 103.50, "B.Cu", 1)
add_track(104.87, 103.50, 104.87, 109.50, "B.Cu", 1) # into GPS Pin 2!
add_track(104.87, 103.50, 116.11, 102.66, "B.Cu", 1) # into MCU_L Pin 1!

# 2) West Edge Highway: GPS Pin 2 (104.87, 109.50) -> H3 (103.5, 146.5) (Unites Island A & Island B!)
add_track(104.87, 109.50, 104.87, 137.00, "B.Cu", 1)
add_track(104.87, 137.00, 103.50, 137.00, "B.Cu", 1)
add_track(103.50, 137.00, 103.50, 146.50, "B.Cu", 1) # into H3!

# 3) SHT45 Pin 3 (113.25, 127.50) -> H3 (103.5, 146.5) on Top F.Cu
add_track(113.25, 127.50, 113.25, 137.00, "F.Cu", 1)
add_track(113.25, 137.00, 103.50, 137.00, "F.Cu", 1)
add_track(103.50, 137.00, 103.50, 146.50, "F.Cu", 1) # into H3!

# 4) H3 (103.5, 146.5) -> H4 (146.5, 146.5) along bottom edge at Y=148.50
add_track(103.50, 146.50, 105.50, 148.50, "B.Cu", 1)
add_track(105.50, 148.50, 144.50, 148.50, "B.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "B.Cu", 1) # into H4!

# J1 Pin 2 (124.0, 146.5) into H4 ground on F.Cu
add_track(124.00, 146.50, 124.00, 148.50, "F.Cu", 1)
add_track(124.00, 148.50, 144.50, 148.50, "F.Cu", 1)
add_track(144.50, 148.50, 146.50, 146.50, "F.Cu", 1) # into H4 on F.Cu!

# 5) MCU_R Pin 2 (133.89, 105.20) -> H2 (146.5, 103.5) on B.Cu!
add_track(133.89, 105.20, 142.00, 105.20, "B.Cu", 1)
add_track(142.00, 105.20, 142.00, 103.50, "B.Cu", 1)
add_track(142.00, 103.50, 146.50, 103.50, "B.Cu", 1) # into H2 on B.Cu!

# 6) Top GND bridge at Y=100.80 (connecting H1 to H2 along top edge)
add_track(103.50, 103.50, 105.50, 100.80, "B.Cu", 1)
add_track(105.50, 100.80, 144.50, 100.80, "B.Cu", 1)
add_track(144.50, 100.80, 146.50, 103.50, "B.Cu", 1) # into H2!

# 7) BH1750 Pin 1 (ADDR: 137.67, 123.20) -> MPU6050 Pin 2 (AD0: 132.07, 127.50) on F.Cu!
# Runs West at Y=123.20 (clear of 3V3 at 121.80!)
add_track(137.67, 123.20, 132.07, 123.20, "F.Cu", 1)
add_track(132.07, 123.20, 132.07, 127.50, "F.Cu", 1) # into MPU Pin 2!

# 8) MPU6050 Pin 2 (132.07, 127.50) & Pin 7 (144.77, 127.50) & BH1750 Pin 4 (145.29, 123.20) into H4
add_track(145.29, 123.20, 145.29, 144.50, "F.Cu", 1) # BH1750 Pin 4 drops South
add_track(144.77, 127.50, 145.29, 127.50, "F.Cu", 1) # MPU Pin 7 joins at 127.50
add_track(132.07, 127.50, 132.07, 137.00, "F.Cu", 1)
add_track(132.07, 137.00, 145.29, 137.00, "F.Cu", 1) # MPU Pin 2 joins at 137.00
add_track(145.29, 144.50, 146.50, 146.50, "F.Cu", 1) # into H4!

# Assemble PCB
content = pcb_header + footprints_str + "\n".join(tracks) + "\n" + "\n".join(vias) + "\n)\n"

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
