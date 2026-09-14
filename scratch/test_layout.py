# Layout collision and clearance checker for 50x50mm Carrier Board

# Dimensions of modules (W x L x H):
# MCU: Beetle C6 = 20.5 x 25.0 mm. Pins: 2x 1x08, pitch 2.54, row distance 17.78.
# SHT45 (Adafruit SZH-MIN069): PCB = 25.5 x 17.8 mm (connectors W=32.0 mm). Pins: 1x05 along 25.5mm edge.
# GY-521 (MPU6050 SZH-EK007): PCB = 15.65 x 20.70 mm. Pins: 1x08 along 20.70mm edge (offset 1.28mm).
# BH1750 (GY-302 SZH-EK070): PCB = 13.9 x 18.5 mm. Pins: 1x05 along 13.9mm edge (offset 2.0mm).
# GPS (ATGM336H-5N SZH-MIN053): PCB = 13.1 x 15.7 mm. Pins: 1x05 along 13.1mm edge (offset 1.5mm).

# Board: X = 100.0 to 150.0, Y = 100.0 to 150.0
# Mounting holes: (103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5), pad diameter = 5.5mm

print("Analyzing optimal layout options...")

# Option 1:
# TOP SIDE:
# - Beetle C6 at bottom: X = 114.75 to 135.25, Y = 100.0 to 125.0 (Flush at Y=100.0)
# - BH1750 (Light sensor needs to be on TOP!):
#   Place BH1750 horizontally or vertically at top-right:
#   Pins at Y = 144.0, X = 134.0 to 144.16 (or vertically at X = 140.0, Y = 127.0 to 145.5).
# - JST-PH (Battery) and SW1:
#   Place at Top center: X = 123.0 to 127.0, Y = 140.0 to 148.0.
# - Can SHT45 be on TOP?
#   If SHT45 is on Top Left: X = 102.0 to 120.0, Y = 126.0 to 144.0.
#   Wait! If SHT45 is 25.5mm wide, X from 101 to 126.5 would hit the M3 hole at (103.5, 146.5) and hit SW1 at X=124!
#   What if SHT45 is on BOTTOM side?
#   Temp/Humidity sensor works completely fine on the bottom side (or facing downward/vented)!
#   On the Bottom side:
#   Available space is huge!
#   Bottom Left: GY-521 + SHT45?
#   Bottom Right: ATGM336H GPS?
