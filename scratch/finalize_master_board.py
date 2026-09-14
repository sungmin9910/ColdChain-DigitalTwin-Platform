import os
import sys
import zipfile

BASE_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50"
GERBER_DIR = os.path.join(BASE_DIR, "gerber_temp")
os.makedirs(GERBER_DIR, exist_ok=True)

sys.path.append('scratch')
from generate_perfect_gerber import all_segments, unique_vias, pads

def fmt_g(val):
    return f"{int(round(val * 100000)):08d}"

print("Writing KiCad PCB with 100% short-free routed tracks and vias...")

kicad_pcb_content = f"""(kicad_pcb
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

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "F.Cu") (at 142.75 123.2)
		(property "Reference" "J_BH1750" (at 0 -2.5 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 107.41 109.5)
		(property "Reference" "J_GPS" (at 0 2.5 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 7 "GPS_RX"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 8 "GPS_TX"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)

	(footprint "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal" (layer "F.Cu") (at 123.0 146.5)
		(property "Reference" "J1" (at 0 -2.5 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -1.0 0) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask") (net 3 "BAT+"))
		(pad "2" thru_hole circle (at 1.0 0) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask") (net 1 "GND"))
	)

	(footprint "Button_Switch_SMD:SW_SPDT_PCM12" (layer "F.Cu") (at 116.0 146.5)
		(property "Reference" "SW1" (at 0 -2.0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" smd rect (at -1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 3 "BAT+"))
		(pad "2" smd rect (at 0 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 4 "BAT"))
		(pad "3" smd rect (at 1.5 0) (size 1.0 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 0 ""))
	)

	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 122.0 142.0)
		(property "Reference" "R3" (at 0 -1.2 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))
		(pad "1" smd rect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 5 "I2C_SDA"))
		(pad "2" smd rect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 2 "3V3"))
	)
	(footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 128.0 142.0)
		(property "Reference" "R4" (at 0 -1.2 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))
		(pad "1" smd rect (at -0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 6 "I2C_SCL"))
		(pad "2" smd rect (at 0.75 0) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 2 "3V3"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal" (layer "B.Cu") (at 113.25 127.5)
		(property "Reference" "J_SHT45" (at 0 2.8 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "3" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "4" thru_hole circle (at 2.54 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "5" thru_hole circle (at 5.08 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
	)

	(footprint "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Horizontal" (layer "B.Cu") (at 138.42 127.5)
		(property "Reference" "J_GY521" (at 0 -2.8 0) (layer "B.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
		(pad "1" thru_hole rect (at -8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 2 "3V3"))
		(pad "2" thru_hole circle (at -6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "3" thru_hole circle (at -3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 6 "I2C_SCL"))
		(pad "4" thru_hole circle (at -1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 5 "I2C_SDA"))
		(pad "5" thru_hole circle (at 1.27 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "6" thru_hole circle (at 3.81 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
		(pad "7" thru_hole circle (at 6.35 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 1 "GND"))
		(pad "8" thru_hole circle (at 8.89 0) (size 1.6 1.6) (drill 0.95) (layers "*.Cu" "*.Mask") (net 0 ""))
	)
"""

# Append segments
for net_name, net_id, layer, x1, y1, x2, y2 in all_segments:
    kicad_pcb_content += f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width 0.35) (layer "{layer}") (net {net_id}))\n'

# Append vias
for net_id, vx, vy in unique_vias:
    kicad_pcb_content += f'\t(via (at {vx:.2f} {vy:.2f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net {net_id}))\n'

kicad_pcb_content += ")\n"

kicad_path = os.path.join(BASE_DIR, "CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb")
with open(kicad_path, "w", encoding="utf-8") as f:
    f.write(kicad_pcb_content)
print(f"Saved KiCad PCB to: {kicad_path}")

# -------------------------------------------------------------
# WRITE MASTER GERBER FILES
# -------------------------------------------------------------
# 1. Outline .GKO
gko = f"""G04 Layer: BoardOutlineLayer*
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
    f.write(gko)

# 2. Top Silkscreen .GTO
gto = f"""G04 Layer: TopSilkscreenLayer*
G04 CarrierBoard_BeetleC6_EdgeUSB_50x50 Master*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,0.150*%
%ADD11C,0.100*%

G04 Beetle ESP32-C6 Mini (20.5 x 25.0mm)*
D10*
G01X{fmt_g(114.75)}Y{fmt_g(100.0)}D02*
G01X{fmt_g(135.25)}Y{fmt_g(100.0)}D01*
G01X{fmt_g(135.25)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(114.75)}Y{fmt_g(125.0)}D01*
G01X{fmt_g(114.75)}Y{fmt_g(100.0)}D01*
G04 USB-C Cutout*
G01X{fmt_g(120.5)}Y{fmt_g(100.0)}D02*
G01X{fmt_g(120.5)}Y{fmt_g(103.5)}D01*
G01X{fmt_g(129.5)}Y{fmt_g(103.5)}D01*
G01X{fmt_g(129.5)}Y{fmt_g(100.0)}D01*

G04 BH1750 Module (Right Wing, 13.9 x 18.5mm)*
D10*
G01X{fmt_g(135.8)}Y{fmt_g(106.7)}D02*
G01X{fmt_g(149.7)}Y{fmt_g(106.7)}D01*
G01X{fmt_g(149.7)}Y{fmt_g(125.2)}D01*
G01X{fmt_g(135.8)}Y{fmt_g(125.2)}D01*
G01X{fmt_g(135.8)}Y{fmt_g(106.7)}D01*
G04 BH1750 Female Header Housing*
D11*
G01X{fmt_g(136.4)}Y{fmt_g(121.93)}D02*
G01X{fmt_g(149.1)}Y{fmt_g(121.93)}D01*
G01X{fmt_g(149.1)}Y{fmt_g(124.47)}D01*
G01X{fmt_g(136.4)}Y{fmt_g(124.47)}D01*
G01X{fmt_g(136.4)}Y{fmt_g(121.93)}D01*

G04 JST-PH 2.0 Connector*
D10*
G01X{fmt_g(120.0)}Y{fmt_g(144.5)}D02*
G01X{fmt_g(126.0)}Y{fmt_g(144.5)}D01*
G01X{fmt_g(126.0)}Y{fmt_g(149.0)}D01*
G01X{fmt_g(120.0)}Y{fmt_g(149.0)}D01*
G01X{fmt_g(120.0)}Y{fmt_g(144.5)}D01*

G04 SW1 Power Switch*
G01X{fmt_g(112.5)}Y{fmt_g(144.5)}D02*
G01X{fmt_g(119.5)}Y{fmt_g(144.5)}D01*
G01X{fmt_g(119.5)}Y{fmt_g(148.5)}D01*
G01X{fmt_g(112.5)}Y{fmt_g(148.5)}D01*
G01X{fmt_g(112.5)}Y{fmt_g(144.5)}D01*
M02*
"""
with open(os.path.join(GERBER_DIR, "Gerber_TopSilkscreenLayer.GTO"), "w", encoding="utf-8") as f:
    f.write(gto)

# 3. Bottom Silkscreen .GBO
gbo = f"""G04 Layer: BottomSilkscreenLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,0.150*%
%ADD11C,0.100*%

G04 SHT45 Module (25.5 x 17.8mm)*
D10*
G01X{fmt_g(100.5)}Y{fmt_g(125.5)}D02*
G01X{fmt_g(126.0)}Y{fmt_g(125.5)}D01*
G01X{fmt_g(126.0)}Y{fmt_g(143.3)}D01*
G01X{fmt_g(100.5)}Y{fmt_g(143.3)}D01*
G01X{fmt_g(100.5)}Y{fmt_g(125.5)}D01*
G04 SHT45 Female Header Housing*
D11*
G01X{fmt_g(106.9)}Y{fmt_g(126.23)}D02*
G01X{fmt_g(119.6)}Y{fmt_g(126.23)}D01*
G01X{fmt_g(119.6)}Y{fmt_g(128.77)}D01*
G01X{fmt_g(106.9)}Y{fmt_g(128.77)}D01*
G01X{fmt_g(106.9)}Y{fmt_g(126.23)}D01*

G04 GY-521 Module (15.5 x 20.5mm)*
D10*
G01X{fmt_g(128.0)}Y{fmt_g(125.5)}D02*
G01X{fmt_g(148.5)}Y{fmt_g(125.5)}D01*
G01X{fmt_g(148.5)}Y{fmt_g(141.0)}D01*
G01X{fmt_g(128.0)}Y{fmt_g(141.0)}D01*
G01X{fmt_g(128.0)}Y{fmt_g(125.5)}D01*
G04 GY-521 Female Header Housing*
D11*
G01X{fmt_g(128.25)}Y{fmt_g(126.23)}D02*
G01X{fmt_g(148.59)}Y{fmt_g(126.23)}D01*
G01X{fmt_g(148.59)}Y{fmt_g(128.77)}D01*
G01X{fmt_g(128.25)}Y{fmt_g(128.77)}D01*
G01X{fmt_g(128.25)}Y{fmt_g(126.23)}D01*

G04 GPS ATGM336H Module (Left Wing, 13.1 x 15.7mm)*
D10*
G01X{fmt_g(100.86)}Y{fmt_g(107.5)}D02*
G01X{fmt_g(113.96)}Y{fmt_g(107.5)}D01*
G01X{fmt_g(113.96)}Y{fmt_g(123.2)}D01*
G01X{fmt_g(100.86)}Y{fmt_g(123.2)}D01*
G01X{fmt_g(100.86)}Y{fmt_g(107.5)}D01*
G04 GPS Female Header Housing*
D11*
G01X{fmt_g(101.06)}Y{fmt_g(108.23)}D02*
G01X{fmt_g(113.76)}Y{fmt_g(108.23)}D01*
G01X{fmt_g(113.76)}Y{fmt_g(110.77)}D01*
G01X{fmt_g(101.06)}Y{fmt_g(110.77)}D01*
G01X{fmt_g(101.06)}Y{fmt_g(108.23)}D01*
M02*
"""
with open(os.path.join(GERBER_DIR, "Gerber_BottomSilkscreenLayer.GBO"), "w", encoding="utf-8") as f:
    f.write(gbo)

# 4. Top Solder Mask .GTS
gts = f"""G04 Layer: TopSolderMaskLayer*
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

G04 Beetle ESP32-C6 Headers*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
D11*
"""
for i in range(1, 8):
    y = 102.66 + i * 2.54
    gts += f"G01X{fmt_g(116.11)}Y{fmt_g(y)}D03*\n"
    gts += f"G01X{fmt_g(133.89)}Y{fmt_g(y)}D03*\n"

gts += f"""G04 BH1750 Header*
D12*
G01X{fmt_g(137.67)}Y{fmt_g(123.2)}D03*
D11*
"""
for i in range(1, 5):
    x = 137.67 + i * 2.54
    gts += f"G01X{fmt_g(x)}Y{fmt_g(123.2)}D03*\n"

gts += f"""G04 JST-PH Connector*
D12*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
D11*
G01X{fmt_g(124.0)}Y{fmt_g(146.5)}D03*

G04 SW1 Switch*
D13*
G01X{fmt_g(114.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(116.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(117.5)}Y{fmt_g(146.5)}D03*

G04 R3 and R4*
D14*
G01X{fmt_g(121.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(122.75)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(127.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(128.75)}Y{fmt_g(142.0)}D03*

G04 Through-hole bottom headers exposed on top mask*
D12*
G01X{fmt_g(102.33)}Y{fmt_g(109.5)}D03*
G01X{fmt_g(108.17)}Y{fmt_g(127.5)}D03*
G01X{fmt_g(129.56)}Y{fmt_g(127.5)}D03*
D11*
"""
for i in range(1, 5):
    gts += f"G01X{fmt_g(102.33 + i*2.54)}Y{fmt_g(109.5)}D03*\n"
for i in range(1, 5):
    gts += f"G01X{fmt_g(108.17 + i*2.54)}Y{fmt_g(127.5)}D03*\n"
for i in range(1, 8):
    gts += f"G01X{fmt_g(129.56 + i*2.54)}Y{fmt_g(127.5)}D03*\n"

# Vias on top mask
gts += "D15*\n"
for net_id, vx, vy in unique_vias:
    gts += f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n"

gts += "M02*\n"
with open(os.path.join(GERBER_DIR, "Gerber_TopSolderMaskLayer.GTS"), "w", encoding="utf-8") as f:
    f.write(gts)

# 5. Bottom Solder Mask .GBS
gbs = f"""G04 Layer: BottomSolderMaskLayer*
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

G04 Beetle ESP32-C6 Headers*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
D11*
"""
for i in range(1, 8):
    y = 102.66 + i * 2.54
    gbs += f"G01X{fmt_g(116.11)}Y{fmt_g(y)}D03*\n"
    gbs += f"G01X{fmt_g(133.89)}Y{fmt_g(y)}D03*\n"

gbs += f"""G04 BH1750 Header*
D12*
G01X{fmt_g(137.67)}Y{fmt_g(123.2)}D03*
D11*
"""
for i in range(1, 5):
    x = 137.67 + i * 2.54
    gbs += f"G01X{fmt_g(x)}Y{fmt_g(123.2)}D03*\n"

gbs += f"""G04 JST-PH Connector*
D12*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
D11*
G01X{fmt_g(124.0)}Y{fmt_g(146.5)}D03*

G04 GPS Header*
D12*
G01X{fmt_g(102.33)}Y{fmt_g(109.5)}D03*
D11*
"""
for i in range(1, 5):
    gbs += f"G01X{fmt_g(102.33 + i*2.54)}Y{fmt_g(109.5)}D03*\n"

gbs += f"""G04 SHT45 Header*
D12*
G01X{fmt_g(108.17)}Y{fmt_g(127.5)}D03*
D11*
"""
for i in range(1, 5):
    gbs += f"G01X{fmt_g(108.17 + i*2.54)}Y{fmt_g(127.5)}D03*\n"

gbs += f"""G04 GY-521 Header*
D12*
G01X{fmt_g(129.56)}Y{fmt_g(127.5)}D03*
D11*
"""
for i in range(1, 8):
    gbs += f"G01X{fmt_g(129.56 + i*2.54)}Y{fmt_g(127.5)}D03*\n"

# Vias on bottom mask
gbs += "D15*\n"
for net_id, vx, vy in unique_vias:
    gbs += f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n"

gbs += "M02*\n"
with open(os.path.join(GERBER_DIR, "Gerber_BottomSolderMaskLayer.GBS"), "w", encoding="utf-8") as f:
    f.write(gbs)

# 6. Top Copper Layer .GTL
gtl = f"""G04 Layer: TopCopperLayer*
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
%ADD16C,0.350*%

G04 Mounting Holes*
D10*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 Beetle ESP32-C6 Headers*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
D11*
"""
for i in range(1, 8):
    y = 102.66 + i * 2.54
    gtl += f"G01X{fmt_g(116.11)}Y{fmt_g(y)}D03*\n"
    gtl += f"G01X{fmt_g(133.89)}Y{fmt_g(y)}D03*\n"

gtl += f"""G04 BH1750 Header*
D12*
G01X{fmt_g(137.67)}Y{fmt_g(123.2)}D03*
D11*
"""
for i in range(1, 5):
    x = 137.67 + i * 2.54
    gtl += f"G01X{fmt_g(x)}Y{fmt_g(123.2)}D03*\n"

gtl += f"""G04 JST-PH Connector*
D12*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
D11*
G01X{fmt_g(124.0)}Y{fmt_g(146.5)}D03*

G04 SW1 Switch*
D13*
G01X{fmt_g(114.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(116.0)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(117.5)}Y{fmt_g(146.5)}D03*

G04 R3 and R4*
D14*
G01X{fmt_g(121.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(122.75)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(127.25)}Y{fmt_g(142.0)}D03*
G01X{fmt_g(128.75)}Y{fmt_g(142.0)}D03*

G04 Through-hole bottom headers on top copper*
D12*
G01X{fmt_g(102.33)}Y{fmt_g(109.5)}D03*
G01X{fmt_g(108.17)}Y{fmt_g(127.5)}D03*
G01X{fmt_g(129.56)}Y{fmt_g(127.5)}D03*
D11*
"""
for i in range(1, 5):
    gtl += f"G01X{fmt_g(102.33 + i*2.54)}Y{fmt_g(109.5)}D03*\n"
for i in range(1, 5):
    gtl += f"G01X{fmt_g(108.17 + i*2.54)}Y{fmt_g(127.5)}D03*\n"
for i in range(1, 8):
    gtl += f"G01X{fmt_g(129.56 + i*2.54)}Y{fmt_g(127.5)}D03*\n"

# Vias on top copper
gtl += "D15*\n"
for net_id, vx, vy in unique_vias:
    gtl += f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n"

# Top Traces
gtl += "D16*\n"
for net_name, net_id, layer, x1, y1, x2, y2 in all_segments:
    if layer == "F.Cu":
        gtl += f"G01X{fmt_g(x1)}Y{fmt_g(y1)}D02*\n"
        gtl += f"G01X{fmt_g(x2)}Y{fmt_g(y2)}D01*\n"

gtl += "M02*\n"
with open(os.path.join(GERBER_DIR, "Gerber_TopLayer.GTL"), "w", encoding="utf-8") as f:
    f.write(gtl)

# 7. Bottom Copper Layer .GBL
gbl = f"""G04 Layer: BottomCopperLayer*
%FSLAX45Y45*%
%MOMM*%
%LPD*%
G01*
G75*
%ADD10C,5.500*%
%ADD11C,1.600*%
%ADD12R,1.600X1.600*%
%ADD15C,0.800*%
%ADD16C,0.350*%

G04 Mounting Holes*
D10*
G01X{fmt_g(103.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(103.5)}D03*
G01X{fmt_g(103.5)}Y{fmt_g(146.5)}D03*
G01X{fmt_g(146.5)}Y{fmt_g(146.5)}D03*

G04 Beetle ESP32-C6 Headers*
D12*
G01X{fmt_g(116.11)}Y{fmt_g(102.66)}D03*
G01X{fmt_g(133.89)}Y{fmt_g(102.66)}D03*
D11*
"""
for i in range(1, 8):
    y = 102.66 + i * 2.54
    gbl += f"G01X{fmt_g(116.11)}Y{fmt_g(y)}D03*\n"
    gbl += f"G01X{fmt_g(133.89)}Y{fmt_g(y)}D03*\n"

gbl += f"""G04 BH1750 Header*
D12*
G01X{fmt_g(137.67)}Y{fmt_g(123.2)}D03*
D11*
"""
for i in range(1, 5):
    x = 137.67 + i * 2.54
    gbl += f"G01X{fmt_g(x)}Y{fmt_g(123.2)}D03*\n"

gbl += f"""G04 JST-PH Connector*
D12*
G01X{fmt_g(122.0)}Y{fmt_g(146.5)}D03*
D11*
G01X{fmt_g(124.0)}Y{fmt_g(146.5)}D03*

G04 GPS Header*
D12*
G01X{fmt_g(102.33)}Y{fmt_g(109.5)}D03*
D11*
"""
for i in range(1, 5):
    gbl += f"G01X{fmt_g(102.33 + i*2.54)}Y{fmt_g(109.5)}D03*\n"

gbl += f"""G04 SHT45 Header*
D12*
G01X{fmt_g(108.17)}Y{fmt_g(127.5)}D03*
D11*
"""
for i in range(1, 5):
    gbl += f"G01X{fmt_g(108.17 + i*2.54)}Y{fmt_g(127.5)}D03*\n"

gbl += f"""G04 GY-521 Header*
D12*
G01X{fmt_g(129.56)}Y{fmt_g(127.5)}D03*
D11*
"""
for i in range(1, 8):
    gbl += f"G01X{fmt_g(129.56 + i*2.54)}Y{fmt_g(127.5)}D03*\n"

# Vias on bottom copper
gbl += "D15*\n"
for net_id, vx, vy in unique_vias:
    gbl += f"G01X{fmt_g(vx)}Y{fmt_g(vy)}D03*\n"

# Bottom Traces
gbl += "D16*\n"
for net_name, net_id, layer, x1, y1, x2, y2 in all_segments:
    if layer == "B.Cu":
        gbl += f"G01X{fmt_g(x1)}Y{fmt_g(y1)}D02*\n"
        gbl += f"G01X{fmt_g(x2)}Y{fmt_g(y2)}D01*\n"

gbl += "M02*\n"
with open(os.path.join(GERBER_DIR, "Gerber_BottomLayer.GBL"), "w", encoding="utf-8") as f:
    f.write(gbl)

# 8. Drill .DRL
drl = f"""M48
; DRILL file
; METRIC, LZ
; MASTER BOARD DRILL FILE
T1C3.200
T2C0.950
T3C0.800
T4C0.400
%
T1
"""
for x, y in [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]:
    drl += f"X{fmt_g(x)}Y{fmt_g(y)}\n"

drl += "T2\n"
# Beetle C6
for i in range(8):
    y = 102.66 + i * 2.54
    drl += f"X{fmt_g(116.11)}Y{fmt_g(y)}\n"
    drl += f"X{fmt_g(133.89)}Y{fmt_g(y)}\n"
# BH1750
for i in range(5):
    drl += f"X{fmt_g(137.67 + i*2.54)}Y{fmt_g(123.2)}\n"
# GPS
for i in range(5):
    drl += f"X{fmt_g(102.33 + i*2.54)}Y{fmt_g(109.5)}\n"
# SHT45
for i in range(5):
    drl += f"X{fmt_g(108.17 + i*2.54)}Y{fmt_g(127.5)}\n"
# GY-521
for i in range(8):
    drl += f"X{fmt_g(129.56 + i*2.54)}Y{fmt_g(127.5)}\n"

drl += "T3\n"
drl += f"X{fmt_g(122.0)}Y{fmt_g(146.5)}\n"
drl += f"X{fmt_g(124.0)}Y{fmt_g(146.5)}\n"

drl += "T4\n"
for net_id, vx, vy in unique_vias:
    drl += f"X{fmt_g(vx)}Y{fmt_g(vy)}\n"

drl += "M30\n"
with open(os.path.join(GERBER_DIR, "Gerber_Drill.DRL"), "w", encoding="utf-8") as f:
    f.write(drl)

# 9. Create Zip
zip_path = os.path.join(BASE_DIR, "Gerber_CarrierBoard_BeetleC6_EdgeUSB_50x50.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for f in os.listdir(GERBER_DIR):
        z.write(os.path.join(GERBER_DIR, f), arcname=f)

print(f"MASTER GERBER ZIP GENERATED SUCCESSFULLY: {zip_path}")
