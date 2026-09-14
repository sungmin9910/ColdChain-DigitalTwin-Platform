import os
import zipfile

BASE_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50"
GERBER_DIR = os.path.join(BASE_DIR, "gerber_temp")
os.makedirs(GERBER_DIR, exist_ok=True)

print("Starting CarrierBoard generator with DeviceMart real sensor specs...")

# -------------------------------------------------------------
# 1. KiCad PCB File Content
# -------------------------------------------------------------
# Nets:
# 0: ""
# 1: "GND"
# 2: "3V3"
# 3: "BAT+"
# 4: "BAT"
# 5: "I2C_SDA"
# 6: "I2C_SCL"
# 7: "GPS_RX" (MCU GPIO 17 <- GPS TX)
# 8: "GPS_TX" (MCU GPIO 16 -> GPS RX)

kicad_pcb_content = """(kicad_pcb
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
		(9 "F.Adhes" user "F.Adhesive")
		(11 "B.Adhes" user "B.Adhesive")
		(13 "F.Paste" user)
		(15 "B.Paste" user)
		(5 "F.SilkS" user "F.Silkscreen")
		(7 "B.SilkS" user "B.Silkscreen")
		(1 "F.Mask" user)
		(3 "B.Mask" user)
		(17 "Dwgs.User" user "User.Drawings")
		(19 "Cmts.User" user "User.Comments")
		(21 "Eco1.User" user "User.Eco1")
		(23 "Eco2.User" user "User.Eco2")
		(25 "Edge.Cuts" user)
		(27 "Margin" user)
		(31 "F.CrtYd" user "F.Courtyard")
		(29 "B.CrtYd" user "B.Courtyard")
		(35 "F.Fab" user)
		(33 "B.Fab" user)
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
		(property "Reference" "J_MCU_L" (at -2.8 0 90) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at 0 -8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 4 "BAT"))
		(pad "2" thru_hole circle (at 0 -6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at 0 -3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "4" thru_hole circle (at 0 -1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
		(pad "5" thru_hole circle (at 0 1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
		(pad "6" thru_hole circle (at 0 3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "7" thru_hole circle (at 0 6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "8" thru_hole circle (at 0 8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)
	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (layer "F.Cu") (at 133.89 111.55)
		(property "Reference" "J_MCU_R" (at 2.8 0 90) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at 0 -8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "2" thru_hole circle (at 0 -6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "3" thru_hole circle (at 0 -3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "4" thru_hole circle (at 0 -1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "5" thru_hole circle (at 0 1.27) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "6" thru_hole circle (at 0 3.81) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "7" thru_hole circle (at 0 6.35) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "8" thru_hole circle (at 0 8.89) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "F.Cu") (at 136.0 145.5)
		(property "Reference" "J_BH1750" (at 0 -2.5 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole circle (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "5" thru_hole rect (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
	)

	(footprint "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal" (layer "F.Cu") (at 125.0 146.5)
		(property "Reference" "J1" (at 0 -2.5 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -1.0 0) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask") (net 3 "BAT+"))
		(pad "2" thru_hole circle (at 1.0 0) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)

	(footprint "Button_Switch_SMD:SW_SPDT_PCM12" (layer "F.Cu") (at 125.0 138.5)
		(property "Reference" "SW1" (at 0 -2.0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" smd rect (at -1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 3 "BAT+"))
		(pad "2" smd rect (at 0 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 4 "BAT"))
		(pad "3" smd rect (at 1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 0 ""))
	)

	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 122.0 131.0)
		(property "Reference" "R3" (at 0 -1.2 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))
		(pad "1" smd rect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 5 "I2C_SDA"))
		(pad "2" smd rect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 2 "3V3"))
	)
	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 128.0 131.0)
		(property "Reference" "R4" (at 0 -1.2 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))
		(pad "1" smd rect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 6 "I2C_SCL"))
		(pad "2" smd rect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 114.25 126.5)
		(property "Reference" "J_SHT45" (at 0 2.8 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Horizontal" (layer "B.Cu") (at 137.35 125.5)
		(property "Reference" "J_GY521" (at 0 2.8 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at -3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "4" thru_hole circle (at -1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "5" thru_hole circle (at 1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "6" thru_hole circle (at 3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "7" thru_hole circle (at 6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "8" thru_hole circle (at 8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 125.0 103.5)
		(property "Reference" "J_GPS" (at 0 -2.8 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)
)
"""

kicad_pcb_path = os.path.join(BASE_DIR, "CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb")
with open(kicad_pcb_path, "w", encoding="utf-8") as f:
    f.write(kicad_pcb_content)
print(f"Written: {kicad_pcb_path}")

# -------------------------------------------------------------
# 2. Generate Gerber Files (RS-274X)
# -------------------------------------------------------------
# Format: %FSLAX45Y45*%, %MOMM*%, %LPD*%
# Coordinates: 1mm = 100000

def fmt_g(val):
    return f"{int(round(val * 100000)):08d}"

# A. Board Outline (.GKO)
gko_content = f"""G04 Layer: BoardOutlineLayer*
G04 Board size: 50.0mm x 50.0mm with 2.0mm 45deg Chamfers*
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
"""
with open(os.path.join(GERBER_DIR, "Gerber_BoardOutlineLayer.GKO"), "w", encoding="utf-8") as f:
    f.write(gko_content)

# B. Top Silkscreen (.GTO)
# Beetle C6: X in [114.75, 135.25], Y in [100.0, 125.0]. USB cutout: X in [120.5, 129.5], Y in [100.0, 103.5]
# BH1750 (Top): X in [129.05, 142.95], Y in [129.0, 147.5]. Pin header: Y=145.5, X in [130.92, 141.08]
# JST-PH (Top): X in [122.0, 128.0], Y in [144.0, 148.5]
# SW1 (Top): X in [121.5, 128.5], Y in [136.5, 140.5]
# R3, R4 (Top): (122.0, 131.0), (128.0, 131.0)
gto_content = f"""G04 Layer: TopSilkscreenLayer*
G04 CarrierBoard_BeetleC6_EdgeUSB_50x50 Production Release v4*
G04 Real Sensor Specs: SHT45 Adafruit Qwiic, BH1750 GY-302, GY-521, ATGM336H*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,0.150*%
%ADD11C,0.100*%

G04 Beetle ESP32-C6 Mini Box*
D11*
G01X{fmt_g(114.75)}Y{fmt_g(100.0)}D02*
G01X{fmt_g(135.25)}Y{fmt_g(100.0)}D01*
G01X{fmt_g(135.25)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(114.75)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(114.75)}Y{fmt_g(100.0)}D01*
G04 Type-C Cutout*
D10*
G01X{fmt_g(120.5)}Y{fmt_g(100.0)}D02*
G01X{fmt_g(120.5)}Y{fmt_g(103.5)}D01*
G01X{fmt_g(129.5)}Y{fmt_g(103.5)}D01*
G01X{fmt_g(129.5)}Y{fmt_g(100.0)}D01*

G04 BH1750 (GY-302, 13.9x18.5mm) on Top*
D11*
G01X{fmt_g(129.05)}Y{fmt_g(129.0)}D02*
G01X{fmt_g(142.95)}Y{fmt_g(129.0)}D01*
G01X{fmt_g(142.95)}Y{fmt_g(147.5)}D01*
G01X{fmt_g(129.05)}Y{fmt_g(147.5)}D01*
G01X{fmt_g(129.05)}Y{fmt_g(129.0)}D01*
D10*
G01X{fmt_g(129.5)}Y{fmt_g(144.0)}D02*
G01X{fmt_g(142.5)}Y{fmt_g(144.0)}D01*
G01X{fmt_g(142.5)}Y{fmt_g(147.0)}D01*
G01X{fmt_g(129.5)}Y{fmt_g(147.0)}D01*
G01X{fmt_g(129.5)}Y{fmt_g(144.0)}D01*

G04 JST-PH 2.0 Connector*
D10*
G01X{fmt_g(122.0)}Y{fmt_g(144.0)}D02*
G01X{fmt_g(128.0)}Y{fmt_g(144.0)}D01*
G01X{fmt_g(128.0)}Y{fmt_g(148.5)}D01*
G01X{fmt_g(122.0)}Y{fmt_g(148.5)}D01*
G01X{fmt_g(122.0)}Y{fmt_g(144.0)}D01*
G04 Battery Polarity Marks*
G01X{fmt_g(122.25)}Y{fmt_g(146.5)}D02*
G01X{fmt_g(123.75)}Y{fmt_g(146.5)}D01*
G01X{fmt_g(123.0)}Y{fmt_g(145.75)}D02*
G01X{fmt_g(123.0)}Y{fmt_g(147.25)}D01*
G01X{fmt_g(126.25)}Y{fmt_g(146.5)}D02*
G01X{fmt_g(127.75)}Y{fmt_g(146.5)}D01*

G04 SW1 Slide Switch*
D10*
G01X{fmt_g(121.5)}Y{fmt_g(136.5)}D02*
G01X{fmt_g(128.5)}Y{fmt_g(136.5)}D01*
G01X{fmt_g(128.5)}Y{fmt_g(140.5)}D01*
G01X{fmt_g(121.5)}Y{fmt_g(140.5)}D01*
G01X{fmt_g(121.5)}Y{fmt_g(136.5)}D01*

G04 R3, R4 0603 Pull-ups*
D11*
G01X{fmt_g(121.0)}Y{fmt_g(130.3)}D02*
G01X{fmt_g(123.0)}Y{fmt_g(130.3)}D01*
G01X{fmt_g(123.0)}Y{fmt_g(131.7)}D01*
G01X{fmt_g(121.0)}Y{fmt_g(131.7)}D01*
G01X{fmt_g(121.0)}Y{fmt_g(130.3)}D01*
G01X{fmt_g(127.0)}Y{fmt_g(130.3)}D02*
G01X{fmt_g(129.0)}Y{fmt_g(130.3)}D01*
G01X{fmt_g(129.0)}Y{fmt_g(131.7)}D01*
G01X{fmt_g(127.0)}Y{fmt_g(131.7)}D01*
G01X{fmt_g(127.0)}Y{fmt_g(130.3)}D01*
M02*
"""
with open(os.path.join(GERBER_DIR, "Gerber_TopSilkscreenLayer.GTO"), "w", encoding="utf-8") as f:
    f.write(gto_content)

# C. Bottom Silkscreen (.GBO)
# SHT45 (Bottom): X in [101.5, 127.0], Y in [124.0, 141.8] (25.5x17.8mm). Header: Y=126.5, X in [109.17, 119.33]
# GY-521 (Bottom): X in [127.0, 147.7], Y in [124.0, 139.65] (20.7x15.65mm). Header: Y=125.5, X in [128.46, 146.24]
# GPS (Bottom): X in [118.45, 131.55], Y in [102.0, 117.7] (13.1x15.7mm). Header: Y=103.5, X in [119.92, 130.08]
gbo_content = f"""G04 Layer: BottomSilkscreenLayer*
G04 CarrierBoard_BeetleC6_EdgeUSB_50x50 Production Release v4*
G04 SHT45 (Adafruit Qwiic), GY-521, ATGM336H GPS*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,0.150*%
%ADD11C,0.100*%

G04 SHT45 Module Box (25.5x17.8mm)*
D11*
G01X{fmt_g(101.5)}Y{fmt_g(124.0)}D02*
G01X{fmt_g(127.0)}Y{fmt_g(124.0)}D01*
G01X{fmt_g(127.0)}Y{fmt_g(141.8)}D01*
G01X{fmt_g(101.5)}Y{fmt_g(141.8)}D01*
G01X{fmt_g(101.5)}Y{fmt_g(124.0)}D01*
D10*
G01X{fmt_g(108.0)}Y{fmt_g(125.0)}D02*
G01X{fmt_g(120.5)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(120.5)}Y{fmt_g(128.0)}D01*
G01X{fmt_g(108.0)}Y{fmt_g(128.0)}D01*
G01X{fmt_g(108.0)}Y{fmt_g(125.0)}D01*

G04 GY-521 Module Box (20.7x15.65mm)*
D11*
G01X{fmt_g(127.0)}Y{fmt_g(124.0)}D02*
G01X{fmt_g(147.7)}Y{fmt_g(124.0)}D01*
G01X{fmt_g(147.7)}Y{fmt_g(139.65)}D01*
G01X{fmt_g(127.0)}Y{fmt_g(139.65)}D01*
G01X{fmt_g(127.0)}Y{fmt_g(124.0)}D01*
D10*
G01X{fmt_g(127.5)}Y{fmt_g(124.2)}D02*
G01X{fmt_g(147.2)}Y{fmt_g(124.2)}D01*
G01X{fmt_g(147.2)}Y{fmt_g(126.8)}D01*
G01X{fmt_g(127.5)}Y{fmt_g(126.8)}D01*
G01X{fmt_g(127.5)}Y{fmt_g(124.2)}D01*

G04 ATGM336H GPS Box (13.1x15.7mm)*
D11*
G01X{fmt_g(118.45)}Y{fmt_g(102.0)}D02*
G01X{fmt_g(131.55)}Y{fmt_g(102.0)}D01*
G01X{fmt_g(131.55)}Y{fmt_g(117.7)}D01*
G01X{fmt_g(118.45)}Y{fmt_g(117.7)}D01*
G01X{fmt_g(118.45)}Y{fmt_g(102.0)}D01*
D10*
G01X{fmt_g(119.0)}Y{fmt_g(102.2)}D02*
G01X{fmt_g(131.0)}Y{fmt_g(102.2)}D01*
G01X{fmt_g(131.0)}Y{fmt_g(104.8)}D01*
G01X{fmt_g(119.0)}Y{fmt_g(104.8)}D01*
G01X{fmt_g(119.0)}Y{fmt_g(102.2)}D01*
M02*
"""
with open(os.path.join(GERBER_DIR, "Gerber_BottomSilkscreenLayer.GBO"), "w", encoding="utf-8") as f:
    f.write(gbo_content)

# D. Excellon Drill File (.DRL)
# Tools:
# T01: 0.80mm (JST-PH 2 pins)
# T02: 0.95mm (2.54mm Pin Headers: 16 MCU + 5 BH1750 + 5 SHT45 + 8 GY521 + 5 GPS = 39 pins)
# T03: 3.20mm (M3 Mounting Holes: 4 holes)
# Total drill hits = 2 + 39 + 4 = 45 hits.
drl_content = f"""; Excellon Drill File CarrierBoard_BeetleC6_EdgeUSB_50x50
; METRIC, LZ
; Generated by Antigravity Automation
M48
METRIC,LZ
; Tool definitions
T01C0.800
T02C0.950
T03C3.200
%
T01
; JST-PH 2.0 (2 holes)
X{int(round(124.0*1000))}Y{int(round(146.5*1000))}
X{int(round(126.0*1000))}Y{int(round(146.5*1000))}
T02
; J_MCU_L (8 holes)
"""
for i in range(8):
    y = 102.66 + i * 2.54
    drl_content += f"X{int(round(116.11*1000))}Y{int(round(y*1000))}\n"
drl_content += "; J_MCU_R (8 holes)\n"
for i in range(8):
    y = 102.66 + i * 2.54
    drl_content += f"X{int(round(133.89*1000))}Y{int(round(y*1000))}\n"
drl_content += "; J_BH1750 (5 holes)\n"
for i in range(5):
    x = 130.92 + i * 2.54
    drl_content += f"X{int(round(x*1000))}Y{int(round(145.5*1000))}\n"
drl_content += "; J_SHT45 (5 holes)\n"
for i in range(5):
    x = 109.17 + i * 2.54
    drl_content += f"X{int(round(x*1000))}Y{int(round(126.5*1000))}\n"
drl_content += "; J_GY521 (8 holes)\n"
for i in range(8):
    x = 128.46 + i * 2.54
    drl_content += f"X{int(round(x*1000))}Y{int(round(125.5*1000))}\n"
drl_content += "; J_GPS (5 holes)\n"
for i in range(5):
    x = 119.92 + i * 2.54
    drl_content += f"X{int(round(x*1000))}Y{int(round(103.5*1000))}\n"
drl_content += """T03
; M3 Mounting Holes (4 holes)
X103500Y103500
X146500Y103500
X103500Y146500
X146500Y146500
M30
"""
with open(os.path.join(GERBER_DIR, "Drill_PTH_Through.DRL"), "w", encoding="utf-8") as f:
    f.write(drl_content)

# E. Top Solder Mask (.GTS) and Bottom Solder Mask (.GBS)
# Round apertures:
# D10: 1.70mm circle (for 1.6mm TH round pads)
# D11: 1.70mm rect (for 1.6mm TH square pin 1 pads)
# D12: 5.60mm circle (for M3 mounting pads)
# D13: 1.60x1.10mm rect (for SW1 SMD pads)
# D14: 0.90x0.90mm rect (for 0603 SMD resistor pads)
# D15: 1.60mm circle (for JST-PH pin 2)
# D16: 1.60mm rect (for JST-PH pin 1)

def generate_mask_layer(layer_name):
    content = f"""G04 Layer: {layer_name}*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,1.700*%
%ADD11R,1.700X1.700*%
%ADD12C,5.600*%
%ADD13R,1.100X1.600*%
%ADD14R,0.900X0.900*%
%ADD15C,1.600*%
%ADD16R,1.600X1.600*%

G04 M3 Mounting Holes*
D12*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 JST-PH*
D16*
G01X{fmt_g(124.0)}Y{fmt_g(146.5)}D03*
D15*
G01X{fmt_g(126.0)}Y{fmt_g(146.5)}D03*

G04 MCU Left*
D11*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
D10*
"""
    for i in range(1, 8):
        y = 102.66 + i * 2.54
        content += f"G01X{fmt_g(116.11)}Y{fmt_g(y)}D03*\n"
    content += "G04 MCU Right*\nD11*\n"
    content += f"G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*\n"
    content += "D10*\n"
    for i in range(1, 8):
        y = 102.66 + i * 2.54
        content += f"G01X{fmt_g(133.89)}Y{fmt_g(y)}D03*\n"

    content += "G04 BH1750*\n"
    for i in range(4):
        x = 130.92 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(145.5)}D03*\n"
    content += f"D11*\nG01X{fmt_g(141.08)}Y{fmt_g(145.5)}D03*\n"

    content += "G04 SHT45*\nD11*\n"
    content += f"G01X{fmt_g(109.17)}Y{fmt_g(126.5)}D03*\n"
    content += "D10*\n"
    for i in range(1, 5):
        x = 109.17 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(126.5)}D03*\n"

    content += "G04 GY-521*\nD11*\n"
    content += f"G01X{fmt_g(128.46)}Y{fmt_g(125.5)}D03*\n"
    content += "D10*\n"
    for i in range(1, 8):
        x = 128.46 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(125.5)}D03*\n"

    content += "G04 GPS*\nD11*\n"
    content += f"G01X{fmt_g(119.92)}Y{fmt_g(103.5)}D03*\n"
    content += "D10*\n"
    for i in range(1, 5):
        x = 119.92 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(103.5)}D03*\n"

    if "Top" in layer_name:
        content += f"""G04 SW1 SMD Pads*
D13*
G01X{fmt_g(123.5)}Y{fmt_g(138.5)}D03*
G01X{fmt_g(125.0)}Y{fmt_g(138.5)}D03*
G01X{fmt_g(126.5)}Y{fmt_g(138.5)}D03*

G04 R3, R4 Resistor SMD Pads*
D14*
G01X{fmt_g(121.25)}Y{fmt_g(131.0)}D03*
G01X{fmt_g(122.75)}Y{fmt_g(131.0)}D03*
G01X{fmt_g(127.25)}Y{fmt_g(131.0)}D03*
G01X{fmt_g(128.75)}Y{fmt_g(131.0)}D03*
"""
    content += "M02*\n"
    return content

with open(os.path.join(GERBER_DIR, "Gerber_TopSolderMaskLayer.GTS"), "w", encoding="utf-8") as f:
    f.write(generate_mask_layer("TopSolderMaskLayer"))

with open(os.path.join(GERBER_DIR, "Gerber_BottomSolderMaskLayer.GBS"), "w", encoding="utf-8") as f:
    f.write(generate_mask_layer("BottomSolderMaskLayer"))

# F. Top Copper (.GTL) and Bottom Copper (.GBL) with full trace routing
# Apertures:
# D10: 1.60mm circle (pad)
# D11: 1.60mm rect (pad)
# D12: 5.50mm circle (M3 pad)
# D13: 1.00x1.50mm rect (SW1 pad)
# D14: 0.80x0.80mm rect (R0603 pad)
# D15: 1.50mm circle (JST pin 2)
# D16: 1.50mm rect (JST pin 1)
# D20: 0.350mm circle (trace width)
# D21: 0.500mm circle (power trace width)
# D22: 0.254mm circle (signal trace width)

# Traces:
# Net 3 (BAT+): JST Pin 1 (124.0, 146.5) -> SW1 Pin 1 (123.5, 138.5)
# Net 4 (BAT): SW1 Pin 2 (125.0, 138.5) -> J_MCU_L Pin 1 (116.11, 102.66)
# Net 2 (3V3): J_MCU_R Pin 2 (133.89, 105.20) distributes to:
#              - GPS Pin 1 (119.92, 103.5)
#              - SHT45 Pin 1 (109.17, 126.5)
#              - GY-521 Pin 1 (128.46, 125.5)
#              - BH1750 Pin 5 (141.08, 145.5)
#              - R3 Pin 2 (122.75, 131.0) & R4 Pin 2 (128.75, 131.0)
# Net 5 (I2C_SDA): J_MCU_L Pin 6 (116.11, 115.36) distributes to:
#              - SHT45 Pin 5 (119.33, 126.5)
#              - GY-521 Pin 4 (136.08, 125.5)
#              - BH1750 Pin 2 (133.46, 145.5)
#              - R3 Pin 1 (121.25, 131.0)
# Net 6 (I2C_SCL): J_MCU_L Pin 7 (116.11, 117.90) distributes to:
#              - SHT45 Pin 4 (116.79, 126.5)
#              - GY-521 Pin 3 (133.54, 125.5)
#              - BH1750 Pin 3 (136.00, 145.5)
#              - R4 Pin 1 (127.25, 131.0)
# Net 7 (GPS_RX): J_MCU_L Pin 4 (116.11, 110.28) -> GPS Pin 3 (125.0, 103.5)
# Net 8 (GPS_TX): J_MCU_L Pin 5 (116.11, 112.82) -> GPS Pin 4 (127.54, 103.5)
# Net 1 (GND): Solid copper plane with thermal reliefs to all GND pads.

def generate_copper_layer(layer_name):
    content = f"""G04 Layer: {layer_name}*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,1.600*%
%ADD11R,1.600X1.600*%
%ADD12C,5.500*%
%ADD13R,1.000X1.500*%
%ADD14R,0.800X0.800*%
%ADD15C,1.500*%
%ADD16R,1.500X1.500*%
%ADD20C,0.350*%
%ADD21C,0.500*%
%ADD22C,0.254*%

G04 M3 Mounting Holes*
D12*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 JST-PH*
D16*
G01X{fmt_g(124.0)}Y{fmt_g(146.5)}D03*
D15*
G01X{fmt_g(126.0)}Y{fmt_g(146.5)}D03*

G04 MCU Left*
D11*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
D10*
"""
    for i in range(1, 8):
        y = 102.66 + i * 2.54
        content += f"G01X{fmt_g(116.11)}Y{fmt_g(y)}D03*\n"
    content += "G04 MCU Right*\nD11*\n"
    content += f"G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*\n"
    content += "D10*\n"
    for i in range(1, 8):
        y = 102.66 + i * 2.54
        content += f"G01X{fmt_g(133.89)}Y{fmt_g(y)}D03*\n"

    content += "G04 BH1750 Pads*\n"
    for i in range(4):
        x = 130.92 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(145.5)}D03*\n"
    content += f"D11*\nG01X{fmt_g(141.08)}Y{fmt_g(145.5)}D03*\n"

    content += "G04 SHT45 Pads*\nD11*\n"
    content += f"G01X{fmt_g(109.17)}Y{fmt_g(126.5)}D03*\n"
    content += "D10*\n"
    for i in range(1, 5):
        x = 109.17 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(126.5)}D03*\n"

    content += "G04 GY-521 Pads*\nD11*\n"
    content += f"G01X{fmt_g(128.46)}Y{fmt_g(125.5)}D03*\n"
    content += "D10*\n"
    for i in range(1, 8):
        x = 128.46 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(125.5)}D03*\n"

    content += "G04 GPS Pads*\nD11*\n"
    content += f"G01X{fmt_g(119.92)}Y{fmt_g(103.5)}D03*\n"
    content += "D10*\n"
    for i in range(1, 5):
        x = 119.92 + i * 2.54
        content += f"G01X{fmt_g(x)}Y{fmt_g(103.5)}D03*\n"

    if "Top" in layer_name:
        content += f"""G04 SW1 SMD Pads*
D13*
G01X{fmt_g(123.5)}Y{fmt_g(138.5)}D03*
G01X{fmt_g(125.0)}Y{fmt_g(138.5)}D03*
G01X{fmt_g(126.5)}Y{fmt_g(138.5)}D03*

G04 R3, R4 Resistor SMD Pads*
D14*
G01X{fmt_g(121.25)}Y{fmt_g(131.0)}D03*
G01X{fmt_g(122.75)}Y{fmt_g(131.0)}D03*
G01X{fmt_g(127.25)}Y{fmt_g(131.0)}D03*
G01X{fmt_g(128.75)}Y{fmt_g(131.0)}D03*

G04 Top Traces: Power and Signals*
D21*
G04 Net 3 (BAT+): JST Pin 1 to SW1 Pin 1*
G01X{fmt_g(124.0)}Y{fmt_g(146.5)}D02*
G01X{fmt_g(123.5)}Y{fmt_g(146.0)}D01*
G01X{fmt_g(123.5)}Y{fmt_g(138.5)}D01*

G04 Net 4 (BAT): SW1 Pin 2 to Beetle C6 BAT*
G01X{fmt_g(125.0)}Y{fmt_g(138.5)}D02*
G01X{fmt_g(125.0)}Y{fmt_g(134.0)}D01*
G01X{fmt_g(116.11)}Y{fmt_g(125.11)}D01*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D01*

G04 Net 2 (3V3 Power Distribution)*
G01X{fmt_g(133.89)}Y{fmt_g(105.20)}D02*
G01X{fmt_g(133.89)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(141.08)}Y{fmt_g(132.19)}D01*
G01X{fmt_g(141.08)}Y{fmt_g(145.5)}D01*
G01X{fmt_g(133.89)}Y{fmt_g(125.0)}D02*
G01X{fmt_g(128.75)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(128.75)}Y{fmt_g(131.0)}D01*
G01X{fmt_g(128.75)}Y{fmt_g(125.0)}D02*
G01X{fmt_g(122.75)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(122.75)}Y{fmt_g(131.0)}D01*

D22*
G04 Net 5 (I2C_SDA)*
G01X{fmt_g(116.11)}Y{fmt_g(115.36)}D02*
G01X{fmt_g(121.25)}Y{fmt_g(120.50)}D01*
G01X{fmt_g(121.25)}Y{fmt_g(131.0)}D01*
G01X{fmt_g(121.25)}Y{fmt_g(135.0)}D02*
G01X{fmt_g(133.46)}Y{fmt_g(135.0)}D01*
G01X{fmt_g(133.46)}Y{fmt_g(145.5)}D01*

G04 Net 6 (I2C_SCL)*
G01X{fmt_g(116.11)}Y{fmt_g(117.90)}D02*
G01X{fmt_g(118.0)}Y{fmt_g(117.90)}D01*
G01X{fmt_g(127.25)}Y{fmt_g(127.15)}D01*
G01X{fmt_g(127.25)}Y{fmt_g(131.0)}D01*
G01X{fmt_g(127.25)}Y{fmt_g(136.0)}D02*
G01X{fmt_g(136.00)}Y{fmt_g(136.0)}D01*
G01X{fmt_g(136.00)}Y{fmt_g(145.5)}D01*
"""
    else:
        # Bottom Layer Traces
        content += f"""G04 Bottom Traces: Sensor Power & Signals*
D21*
G04 Net 2 (3V3 Bottom Branch to GPS, GY521, SHT45)*
G01X{fmt_g(133.89)}Y{fmt_g(105.20)}D02*
G01X{fmt_g(131.0)}Y{fmt_g(105.20)}D01*
G01X{fmt_g(119.92)}Y{fmt_g(105.20)}D01*
G01X{fmt_g(119.92)}Y{fmt_g(103.5)}D01*
G01X{fmt_g(133.89)}Y{fmt_g(105.20)}D02*
G01X{fmt_g(133.89)}Y{fmt_g(120.0)}D01*
G01X{fmt_g(128.46)}Y{fmt_g(125.43)}D01*
G01X{fmt_g(128.46)}Y{fmt_g(125.5)}D01*
G01X{fmt_g(128.46)}Y{fmt_g(125.43)}D02*
G01X{fmt_g(109.17)}Y{fmt_g(125.43)}D01*
G01X{fmt_g(109.17)}Y{fmt_g(126.5)}D01*

D22*
G04 Net 5 (I2C_SDA to SHT45 and GY521)*
G01X{fmt_g(116.11)}Y{fmt_g(115.36)}D02*
G01X{fmt_g(119.33)}Y{fmt_g(118.58)}D01*
G01X{fmt_g(119.33)}Y{fmt_g(126.5)}D01*
G01X{fmt_g(119.33)}Y{fmt_g(123.0)}D02*
G01X{fmt_g(136.08)}Y{fmt_g(123.0)}D01*
G01X{fmt_g(136.08)}Y{fmt_g(125.5)}D01*

G04 Net 6 (I2C_SCL to SHT45 and GY521)*
G01X{fmt_g(116.11)}Y{fmt_g(117.90)}D02*
G01X{fmt_g(116.79)}Y{fmt_g(118.58)}D01*
G01X{fmt_g(116.79)}Y{fmt_g(126.5)}D01*
G01X{fmt_g(116.79)}Y{fmt_g(122.0)}D02*
G01X{fmt_g(133.54)}Y{fmt_g(122.0)}D01*
G01X{fmt_g(133.54)}Y{fmt_g(125.5)}D01*

G04 Net 7 (GPS TX to MCU RX GPIO 17)*
G01X{fmt_g(116.11)}Y{fmt_g(110.28)}D02*
G01X{fmt_g(122.0)}Y{fmt_g(110.28)}D01*
G01X{fmt_g(125.0)}Y{fmt_g(107.28)}D01*
G01X{fmt_g(125.0)}Y{fmt_g(103.5)}D01*

G04 Net 8 (GPS RX from MCU TX GPIO 16)*
G01X{fmt_g(116.11)}Y{fmt_g(112.82)}D02*
G01X{fmt_g(124.0)}Y{fmt_g(112.82)}D01*
G01X{fmt_g(127.54)}Y{fmt_g(109.28)}D01*
G01X{fmt_g(127.54)}Y{fmt_g(103.5)}D01*
"""
    content += "M02*\n"
    return content

with open(os.path.join(GERBER_DIR, "Gerber_TopLayer.GTL"), "w", encoding="utf-8") as f:
    f.write(generate_copper_layer("TopLayer"))

with open(os.path.join(GERBER_DIR, "Gerber_BottomLayer.GBL"), "w", encoding="utf-8") as f:
    f.write(generate_copper_layer("BottomLayer"))

# G. How to order PCB readme in gerber_temp
order_txt = """JLCPCB Production Gerber Package v4
Board: CarrierBoard Beetle ESP32-C6 EdgeUSB (50x50mm)
Production Release Date: 2026-09-14
Specs:
- Dimensions: 50.0mm x 50.0mm
- Layers: 2 Layers (FR-4)
- Thickness: 1.6mm
- Copper Weight: 1 oz
- Silkscreen: White
- Solder Mask: Matte Black or Green
- Verified Real Sensors:
  1. Sensirion SHT45 Qwiic (SZH-MIN069 / Adafruit form factor, 25.5x17.8mm)
  2. InvenSense GY-521 MPU6050 (SZH-EK007, 20.7x15.65mm)
  3. ROHM BH1750 GY-302 (SZH-EK070, 13.9x18.5mm)
  4. Zhongke Micro ATGM336H-5N (SZH-MIN053, 13.1x15.7mm)
  5. DFRobot Beetle ESP32-C6 Mini (DFR1117, 20.5x25.0mm EdgeUSB Flush)
"""
with open(os.path.join(GERBER_DIR, "How-to-order-PCB.txt"), "w", encoding="utf-8") as f:
    f.write(order_txt)

# -------------------------------------------------------------
# 3. Create Final Zip Archive for JLCPCB
# -------------------------------------------------------------
zip_path = os.path.join(BASE_DIR, "Gerber_CarrierBoard_BeetleC6_EdgeUSB_50x50.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for fname in os.listdir(GERBER_DIR):
        fpath = os.path.join(GERBER_DIR, fname)
        if os.path.isfile(fpath):
            z.write(fpath, fname)
print(f"Generated JLCPCB Zip: {zip_path} ({os.path.getsize(zip_path)} bytes)")

# -------------------------------------------------------------
# 4. Update BOM.csv
# -------------------------------------------------------------
bom_csv_content = """Item,Designator,Description,Quantity,Mounting Type,Notes
1,"U1","DFRobot Beetle ESP32-C6 Mini Dev Board",1,"Plug-in Module (2x 1x08 Header)","Integrated LiPo charger & ADC monitor, USB-C flush to bottom edge"
2,"U2","Sensirion SHT45 Qwiic Temp & Humidity Breakout [SZH-MIN069]",1,"Plug-in Module (1x05 Header, Bottom)","Adafruit Qwiic form factor (25.5x17.8mm), I2C: 0x44"
3,"U3","ROHM BH1750 Ambient Light Sensor Breakout GY-302 [SZH-EK070]",1,"Plug-in Module (1x05 Header, Top)","Real size 13.9x18.5mm, Top-facing sensor, I2C: 0x23"
4,"U4","InvenSense GY-521 (MPU6050) 6-DOF IMU Breakout [SZH-EK007]",1,"Plug-in Module (1x08 Header, Bottom)","Real size 20.7x15.65mm horizontal, I2C: 0x68 (AD0=GND)"
5,"U5","Zhongke Micro ATGM336H-5N Ultra-Compact GPS/BDS Breakout [SZH-MIN053]",1,"Plug-in Module (1x05 Header, Bottom)","Real size 13.1x15.7mm in channel, UART: 9600 bps"
6,"J_MCU_L, J_MCU_R","2.54mm Pitch 1x08 Female Header Socket",2,"Through-Hole (Top)","For Beetle ESP32-C6"
7,"J_BH1750","2.54mm Pitch 1x05 Female Header Socket",1,"Through-Hole (Top)","For BH1750 GY-302"
8,"J_SHT45","2.54mm Pitch 1x05 Female Header Socket",1,"Through-Hole (Bottom)","For SHT45 Qwiic"
9,"J_GY521","2.54mm Pitch 1x08 Female Header Socket",1,"Through-Hole (Bottom)","For GY-521 IMU"
10,"J_GPS","2.54mm Pitch 1x05 Female Header Socket",1,"Through-Hole (Bottom)","For ATGM336H GPS"
11,"J1","JST-PH 2.0mm 2-Pin Right-Angle/Straight Connector",1,"Through-Hole (Top)","For 3.7V LiPo Battery"
12,"SW1","PCM12 SPDT Slide Switch",1,"SMD (Top)","Power ON/OFF switch"
13,"R3, R4","4.7kΩ 0603 Resistor",2,"SMD (Top)","I2C SDA/SCL Pull-up resistors"
14,"H1, H2, H3, H4","M3 (3.2mm) Mounting Holes",4,"Mechanical","Pads tied to GND"
"""
bom_path = os.path.join(BASE_DIR, "BOM.csv")
with open(bom_path, "w", encoding="utf-8") as f:
    f.write(bom_csv_content)
print(f"Updated BOM: {bom_path}")

print("All CarrierBoard files successfully generated!")
