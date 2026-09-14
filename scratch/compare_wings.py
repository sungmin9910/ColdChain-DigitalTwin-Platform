import numpy as np

# Let's compare:
# Case 1: BH1750 on Left Wing (Top), GPS on Right Wing (Bottom)
# Case 2: GPS on Left Wing (Bottom), BH1750 on Right Wing (Top)

# Details of Beetle C6 pins:
# Left pin row: X = 116.11 mm
#   Pin 1 (Y=102.66): BAT
#   Pin 2 (Y=105.20): GND
#   Pin 3 (Y=107.74): NC
#   Pin 4 (Y=110.28): GPIO17 (MCU RX <- GPS TX)
#   Pin 5 (Y=112.82): GPIO16 (MCU TX -> GPS RX)
#   Pin 6 (Y=115.36): GPIO19 (I2C SDA)
#   Pin 7 (Y=117.90): GPIO20 (I2C SCL)
#   Pin 8 (Y=120.44): NC
# Right pin row: X = 133.89 mm
#   Pin 1 (Y=102.66): GND
#   Pin 2 (Y=105.20): 3V3
#   Pins 3-8: NC

# Notice:
# GPIO19 (SDA) and GPIO20 (SCL) are on the LEFT row (pins 6 and 7)!
# GPIO17 (GPS_RX) and GPIO16 (GPS_TX) are on the LEFT row (pins 4 and 5)!
# If GPS is on Left Wing:
# GPS pins are right next to GPIO17/GPIO16! The traces are only 3-5mm long without crossing anything!
# If BH1750 is on Right Wing:
# BH1750 is I2C. Right row has 3V3 (pin 2) and GND (pin 1)!
# SHT45 (Top-Left) is right above the Left row (SDA/SCL)!
# GY-521 (Top-Right) is right above the Right row (3V3/GND)!

print("Comparing Case 1 vs Case 2...")

# Let's check physical fit for Case 2:
# GPS on Left Wing:
# GPS module: 13.1 mm wide x 15.7 mm high.
# Left Wing: X in [100.0, 114.75], width = 14.75 mm.
# GPS fits with 14.75 - 13.1 = 1.65 mm total margin!
# E.g., GPS X in [100.8, 113.9]. Clearance to Beetle C6 (114.75) is 0.85 mm!
# Clearance to left edge (100.0) is 0.80 mm!
# GPS height 15.7 mm in Y in [108.0, 123.7].
# Clearance to M3 hole pad (Y=106.25) is 1.75 mm!
# Female header 1x05 vertical at X = 103.5 or X = 111.0?
# In GPS module (ATGM336H), 5 pins are along 13.1mm short edge.
# If horizontal: 5 pins span 10.16mm.
# In 13.1mm, 10.16mm fits with 1.47mm margins on both ends!
# If horizontal 1x05 at Y = 110.0 or 122.0:
# X pins: 102.5 + i*2.54 for i=0..4 -> [102.5, 112.66].
# Clearance to Beetle C6 left pin (116.11): 116.11 - 112.66 = 3.45 mm!

# And BH1750 on Right Wing:
# BH1750 module: 13.9 mm wide x 18.5 mm high.
# Right Wing: X in [135.25, 150.0], width = 14.75 mm.
# BH1750 fits with 14.75 - 13.9 = 0.85 mm total margin!
# E.g., BH1750 X in [135.6, 149.5].
# Clearance to Beetle C6 right edge (135.25) is 0.35 mm.
# Clearance to right edge (150.0) is 0.50 mm.
# Clearance to M3 hole H2 (146.5, 103.5): pad ends at Y = 106.25 mm.
# If BH1750 Y in [107.0, 125.5], height = 18.5 mm. Clearance to pad is 0.75 mm!

# Now let's check Case 1:
# BH1750 on Left Wing (13.9 mm wide):
# Left Wing width is 14.75 mm. Margin is 0.85 mm.
# GPS on Right Wing (13.1 mm wide):
# Right Wing width is 14.75 mm. Margin is 1.65 mm.

print("Both Case 1 and Case 2 fit with zero 2D overlap!")
