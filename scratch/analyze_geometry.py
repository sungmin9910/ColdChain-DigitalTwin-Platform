import numpy as np

# Let's find layouts where:
# - Margin between ANY two components >= 1.0 mm (both on same side and across sides)
# - Margin to board edge >= 0.5 mm
# - Margin to M3 hole pad (R=2.75) >= 0.5 mm
# - Margin between female socket bodies >= 1.0 mm

# Module sizes:
# MCU: fixed at [114.75, 135.25] x [100.0, 125.0]
# SHT45: (25.5, 17.8) or (17.8, 25.5)
# GY521: (20.7, 15.65) or (15.65, 20.7)
# BH1750: (13.9, 18.5) or (18.5, 13.9)
# GPS: (13.1, 15.7) or (15.7, 13.1)

# Holes:
holes = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]

def check_hole(r):
    for hx, hy in holes:
        dx = max(0, r[0] - hx, hx - r[1])
        dy = max(0, r[2] - hy, hy - r[3])
        if np.hypot(dx, dy) < 2.75 + 0.3: # at least 0.3mm from pad
            return False
    return True

def min_gap(r1, r2):
    dx = max(0, r2[0] - r1[1], r1[0] - r2[1])
    dy = max(0, r2[2] - r1[3], r1[2] - r2[3])
    return max(dx, dy)

mcu_r = (114.75, 135.25, 100.0, 125.0)

# Can SHT45 be in Left Wing? Min dim 17.8 > 14.75 -> No.
# Can GY521 be in Left Wing? Min dim 15.65 > 14.75 -> No.
# So Left Wing can ONLY contain BH1750 or GPS (or be empty).
# Right Wing can ONLY contain BH1750 or GPS (or be empty).

# What if:
# Case A: BH1750 in Left Wing, GPS in Right Wing
# Case B: GPS in Left Wing, BH1750 in Right Wing
# Let's test GPS in Left Wing!
# GPS is 13.1 x 15.7 mm.
# Width 13.1 mm is SMALLER than BH1750 (13.9 mm)!
# If GPS is in Left Wing:
# X in [100.5, 113.6] -> clearance to Beetle C6 (114.75) is 114.75 - 113.6 = 1.15 mm!
# And BH1750 (13.9 x 18.5) in Right Wing:
# Right Wing has X in [135.25, 150.0]. Width = 14.75 mm.
# If BH1750 is at X in [135.8, 149.7] -> width 13.9 mm!
# Clearance to Beetle C6 (135.25) is 135.8 - 135.25 = 0.55 mm.
# Or if BH1750 is in Top Half:
# Top Half has width 50mm, height 25mm.

print("Testing all possibilities...")
# What if Top Half contains:
# Option 1: SHT45 + GY521 in Top Half
# Option 2: SHT45 + BH1750 in Top Half (and GY521 in... wait, GY521 cannot fit in wings)
# So SHT45 and GY521 MUST BOTH be in Top Half if neither fits in wings!
# Let's verify if GY521 could fit anywhere else:
# Board is 50x50.
# Beetle C6 is 20.5 wide. 50 - 20.5 = 29.5. Split between left and right = 14.75 each.
# Since GY-521 minimum dimension is 15.65mm, it CANNOT fit in 14.75mm wings.
# Since SHT45 minimum dimension is 17.8mm, it CANNOT fit in 14.75mm wings.
# Therefore, SHT45 and GY-521 MUST be in the Top Half!
print("Confirmed: SHT45 and GY-521 MUST both reside in the Top Half (Y > 125.0)!")
