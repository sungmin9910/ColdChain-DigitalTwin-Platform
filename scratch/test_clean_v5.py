import math

# Clearance calculation for 100% non-overlapping design
# Board: 100.0 to 150.0 mm in X and Y
# Holes: (103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5). Pad radius = 2.75mm

# 1. Beetle C6 (Top): X in [114.75, 135.25], Y in [100.0, 125.0]
#    Left pins: X = 116.11, Y in [102.66, 120.44]
#    Right pins: X = 133.89, Y in [102.66, 120.44]
#    KEEPOUT: X in [113.5, 136.5], Y in [100.0, 126.0] -> NO OTHER THROUGH HOLES!

# 2. GPS ATGM336H (Bottom, Right-Wing):
#    Module: W=13.1, L=15.7.
#    Body: X in [136.5, 149.6], Y in [108.0, 123.7]
#    Pins: 1x05 vertical at X = 143.0, Y in [109.0, 119.16] (pads at Y=109.0 + i*2.54)
#    Distance to Beetle C6 right pin (133.89): 143.0 - 133.89 = 9.11 mm! (Zero interference!)
#    Distance to H2 (146.5, 103.5): Y distance = 108.0 - 103.5 = 4.5 mm (pad outer is 106.25, clearance 1.75mm)!
#    Clearance to right PCB edge (150.0): 150.0 - 149.6 = 0.4 mm!

# 3. Top Region (Y in [127.0, 150.0]):
#    Available height = 23.0 mm. Available width = 50.0 mm.
#    Here we place:
#    - BH1750 (Top, Top-Right): 13.9(W) x 18.5(H).
#      X in [130.0, 143.9], Y in [128.5, 147.0]. Pins at Y=145.5, X in [131.87, 142.03]
#    - JST-PH (Top, Top-Center): X in [122.5, 128.5], Y in [144.0, 148.5]. Pins at (124.5, 146.5), (126.5, 146.5)
#    - SW1 (Top SMD): X in [122.5, 128.5], Y in [136.5, 140.5]
#    - SHT45 (Bottom, Top-Left): 25.5(W) x 17.8(H).
#      X in [102.0, 127.5], Y in [128.5, 146.3].
#      Pins at Y=131.0, centered at X=114.75: X in [109.67, 119.83]
#      Distance to Beetle C6 top edge (Y=125.0): 128.5 - 125.0 = 3.5 mm!
#      Distance to GY-521: where does GY-521 go?

# Where does GY-521 go?
# Can GY-521 go on the Left-Wing?
# Left-Wing: X in [100.5, 115.0], Y in [107.0, 126.0]
# GY-521 is 15.65mm x 20.70mm!
# If GY-521 is vertical: W=15.65, H=20.70!
# If X in [100.5, 116.15]:
# Notice Beetle C6 left pins are at X = 116.11!
# 116.15 touches 116.11!
# BUT WHAT IF BEETLE C6 IS SHIFTED RIGHT BY 2.0 mm?
# Or what if GY-521 is on the Top-Right (Bottom) under BH1750?
# Let's check:
# Can GY-521 and BH1750 share the Top-Right on opposite sides?
# On Top side: BH1750 pins at Y = 145.5 mm.
# On Bottom side: GY-521 pins at Y = 130.0 mm.
# Separation between their pins is 15.5 mm!
# And both are on opposite sides (+Z vs -Z)!
# Solder pins of BH1750 are at Y=145.5 mm.
# If GY-521 body on bottom is from Y=128.5 to 144.15 mm:
# Y=144.15 is 1.35mm BELOW BH1750 pins (Y=145.5)!
# There is NO collision between GY-521 and BH1750 pins!

print("Testing exact clearances...")
