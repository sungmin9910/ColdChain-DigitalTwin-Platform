import numpy as np

# Board: 100 to 150 in X and Y
# M3 holes: (103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5), pad R=2.75mm
# MCU: X in [114.75, 135.25], Y in [100.0, 125.0]

holes = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]

def collides_with_holes(x1, x2, y1, y2):
    for hx, hy in holes:
        # Distance from point (hx, hy) to rect [x1, x2] x [y1, y2]
        dx = max(0, x1 - hx, hx - x2)
        dy = max(0, y1 - hy, hy - y2)
        if np.hypot(dx, dy) < 2.75:
            return True
    return False

def collides_rect(r1, r2, margin=0.5):
    # r = (x1, x2, y1, y2)
    if r1[1] + margin <= r2[0] or r2[1] + margin <= r1[0]:
        return False
    if r1[3] + margin <= r2[2] or r2[3] + margin <= r1[2]:
        return False
    return True

mcu_rect = (114.75, 135.25, 100.0, 125.0)

# Sensor sizes (w, h):
# Can each sensor be oriented horizontally or vertically?
# SHT45: (25.5, 17.8) or (17.8, 25.5)
# GY-521: (20.7, 15.65) or (15.65, 20.7)
# BH1750: (13.9, 18.5) or (18.5, 13.9)
# GPS: (13.1, 15.7) or (15.7, 13.1)

print("Searching for zero-overlap 2D layout for all 5 components...")

# Let's test if there is ANY placement where:
# - MCU is fixed at mcu_rect
# - SHT45, GY-521, BH1750, GPS are within [100, 150] x [100, 150]
# - None overlap with MCU, holes, or each other!

import itertools

orientations = {
    'SHT45': [(25.5, 17.8), (17.8, 25.5)],
    'GY521': [(20.7, 15.65), (15.65, 20.7)],
    'BH1750': [(13.9, 18.5), (18.5, 13.9)],
    'GPS': [(13.1, 15.7), (15.7, 13.1)]
}

# Grid search with step 0.5mm
found = []
# To make search fast, notice:
# Left wing has width 14.75mm (100 to 114.75).
# Can any sensor fit in Left wing?
# SHT45: min dim 17.8 > 14.75 -> NO.
# GY521: min dim 15.65 > 14.75 -> NO.
# BH1750: min dim 13.9 <= 14.75 -> YES! (13.9 x 18.5) fits!
# GPS: min dim 13.1 <= 14.75 -> YES! (13.1 x 15.7) fits!

# Right wing has width 14.75mm (135.25 to 150).
# SHT45: NO
# GY521: NO
# BH1750: YES (13.9 x 18.5)
# GPS: YES (13.1 x 15.7)

print("Checking Left Wing + Right Wing + Top Half...")
# If GPS is in Right Wing and BH1750 is in Left Wing (or vice versa):
# Then the remaining two sensors (SHT45 and GY-521) MUST be in the Top Half!
# Let's test if SHT45 and GY-521 can fit together in the Top Half!
for sht_w, sht_h in orientations['SHT45']:
    for imu_w, imu_h in orientations['GY521']:
        for sht_x in np.arange(100.5, 149.5 - sht_w, 0.5):
            for sht_y in np.arange(125.5, 149.5 - sht_h, 0.5):
                sht_r = (sht_x, sht_x + sht_w, sht_y, sht_y + sht_h)
                if collides_with_holes(*sht_r) or collides_rect(sht_r, mcu_rect):
                    continue
                for imu_x in np.arange(100.5, 149.5 - imu_w, 0.5):
                    for imu_y in np.arange(125.5, 149.5 - imu_h, 0.5):
                        imu_r = (imu_x, imu_x + imu_w, imu_y, imu_y + imu_h)
                        if collides_with_holes(*imu_r) or collides_rect(imu_r, mcu_rect) or collides_rect(sht_r, imu_r):
                            continue
                        # Found valid SHT and IMU in top!
                        found.append((sht_r, imu_r))
                        break
                    if len(found) > 0:
                        break
                if len(found) > 0:
                    break
            if len(found) > 0:
                break
        if len(found) > 0:
            break

print(f"Can SHT45 and GY521 fit together in top half? {'YES' if len(found)>0 else 'NO'}")
if found:
    print("SHT45 rect:", found[0][0])
    print("GY521 rect:", found[0][1])
