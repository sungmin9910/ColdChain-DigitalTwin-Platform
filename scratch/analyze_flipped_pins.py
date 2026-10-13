# Sockets on Carrier Board:
# Let's inspect J_SHT45, J_GY521, J_BH1750 as routed in KiCad:

# J_SHT45 (1x5 female socket, placed on bottom):
# When viewed from Bottom:
# The socket has 5 pins.
# In KiCad (F.Cu view):
# Pad 1 (dx=-5.08, dy=0): I2C_SDA (Net 5)
# Pad 2 (dx=-2.54, dy=0): I2C_SCL (Net 6)
# Pad 3 (dx= 0.00, dy=0): GND     (Net 1)
# Pad 4 (dx=+2.54, dy=0): 3V3     (Net 2)
# Pad 5 (dx=+5.08, dy=0): 3V3     (Net 2)
#
# BUT WAIT! On the Bottom side of the PCB:
# X is inverted! dx=-5.08 (Pad 1) is on the RIGHT when looking at the bottom!
# dx=+5.08 (Pad 5) is on the LEFT when looking at the bottom!
# Let's verify: In KiCad, looking at Back side (B.Cu), Left is +X, Right is -X!

# Let's print out both orientations for SHT45, GY-521, BH1750:

print("=== SHT45 Module ===")
# SHT45 module pins (from silk on module): [VIN, 3Vo, GND, SCL, SDA]
print("Module pins standard: [1: VIN, 2: 3Vo, 3: GND, 4: SCL, 5: SDA]")

print("\n=== GY-521 Module ===")
# GY-521 module pins (8 pins): [VCC, GND, SCL, SDA, XDA, XCL, AD0, INT]
print("Module pins standard: [1: VCC, 2: GND, 3: SCL, 4: SDA, 5: XDA, 6: XCL, 7: AD0, 8: INT]")

print("\n=== BH1750 Module ===")
# BH1750 module pins (5 pins): [VCC, GND, SCL, SDA, ADDR]
print("Module pins standard: [1: VCC, 2: GND, 3: SCL, 4: SDA, 5: ADDR]")
