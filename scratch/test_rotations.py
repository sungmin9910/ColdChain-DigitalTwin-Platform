import numpy as np

# Let's test all 4 combinations of rotations for SHT45 and GY521 in Top Half (Y > 125.0):
# Dimensions:
# SHT45: H=(25.5, 17.8), V=(17.8, 25.5)
# GY521: H=(20.7, 15.65), V=(15.65, 20.7)

holes = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]

def check_holes(r):
    for hx, hy in holes:
        dx = max(0, r[0] - hx, hx - r[1])
        dy = max(0, r[2] - hy, hy - r[3])
        if np.hypot(dx, dy) < 2.75 + 0.2:
            return False
    return True

for sht_orient, (sw, sh) in [('SHT_Horizontal', (25.5, 17.8)), ('SHT_Vertical', (17.8, 25.5))]:
    for imu_orient, (iw, ih) in [('IMU_Horizontal', (20.7, 15.65)), ('IMU_Vertical', (15.65, 20.7))]:
        # Search best placements
        best_score = -1
        best_cfg = None
        for sx in np.arange(100.5, 149.5 - sw, 0.5):
            for sy in np.arange(125.5, 149.5 - sh, 0.5):
                sr = (sx, sx + sw, sy, sy + sh)
                if not check_holes(sr): continue
                for ix in np.arange(100.5, 149.5 - iw, 0.5):
                    for iy in np.arange(125.5, 149.5 - ih, 0.5):
                        ir = (ix, ix + iw, iy, iy + ih)
                        if not check_holes(ir): continue
                        
                        # Check overlap between sr and ir
                        x_ov = max(0, min(sr[1], ir[1]) - max(sr[0], ir[0]))
                        y_ov = max(0, min(sr[3], ir[3]) - max(sr[2], ir[2]))
                        if x_ov > 0 and y_ov > 0: continue
                        
                        # Calculate minimum clearance between them
                        dx = max(0, ir[0] - sr[1], sr[0] - ir[1])
                        dy = max(0, ir[2] - sr[3], sr[2] - ir[3])
                        gap = max(dx, dy)
                        if gap > best_score:
                            best_score = gap
                            best_cfg = (sr, ir)
        print(f"{sht_orient} + {imu_orient}: Best Gap = {best_score:.2f} mm")
        if best_cfg:
            print("  SHT:", best_cfg[0], "IMU:", best_cfg[1])
