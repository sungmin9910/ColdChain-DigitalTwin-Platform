# Complete 3D and 2D physical clearance verification
# Board: 100.0 to 150.0 mm in X and Y (50x50mm)

# Real component bodies (Width x Height x Thickness)
# 1. Beetle C6 (Top): 20.5 x 25.0 mm. USB at bottom.
#    Body: X in [114.75, 135.25], Y in [100.0, 125.0]
#    Left Header (Top TH): X = 116.11, Y in [102.66, 120.44]
#    Right Header (Top TH): X = 133.89, Y in [102.66, 120.44]
#    KEEPOUT on Bottom: To prevent solder pin collisions with Beetle C6 underside components/USB,
#    NO Bottom through-hole pins inside X in [113.5, 136.5], Y in [100.0, 126.0]!

# 2. BH1750 GY-302 (Top): 13.9 x 18.5 mm.
#    Female header: 1x05 (span 10.16mm, plastic width 2.54mm).

# 3. SHT45 Adafruit Qwiic SZH-MIN069: 25.5 x 17.8 mm (connectors reach 32.0mm).
#    Female header: 1x05 (span 10.16mm, plastic width 2.54mm).

# 4. GY-521 SZH-EK007: 15.65 x 20.70 mm.
#    Female header: 1x08 (span 17.78mm, plastic width 2.54mm).
#    Pin holes are 1.28mm from one long edge, body extends 14.37mm to other side.

# 5. ATGM336H GPS SZH-MIN053: 13.1 x 15.7 mm.
#    Female header: 1x05 (span 10.16mm, plastic width 2.54mm).

# 6. JST-PH 2.0 (Top): 6.0 x 4.5 mm.
# 7. SW1 PCM12 (Top SMD): 7.0 x 4.0 mm.

# Let's write a script to evaluate clean, spacious configurations!
