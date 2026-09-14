import math

HOLES = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]
HOLE_R = 3.0  # pad radius 2.75mm + 0.25mm clearance

def valid_rect(r, name=""):
    xmin, ymin, xmax, ymax = r
    # inside board
    if xmin < 100.5 or xmax > 149.5 or ymin < 100.5 or ymax > 149.5:
        return False
    # holes
    for hx, hy in HOLES:
        cx = max(xmin, min(hx, xmax))
        cy = max(ymin, min(hy, ymax))
        if math.hypot(cx - hx, cy - hy) < HOLE_R:
            return False
    return True

def overlap(r1, r2, clearance=0.5):
    # check if r1 and r2 overlap with clearance
    return not (r1[2] + clearance <= r2[0] or r1[0] - clearance >= r2[2] or
                r1[3] + clearance <= r2[1] or r1[1] - clearance >= r2[3])

# Beetle C6 TH Pins on Bottom:
# Left row: X=116.11, Y from 102.66 to 120.44 -> Keepout X in [114.5, 117.7], Y in [101.5, 121.5]
# Right row: X=133.89, Y from 102.66 to 120.44 -> Keepout X in [132.3, 135.5], Y in [101.5, 121.5]
MCU_KEEPOUT_L = (114.5, 101.5, 117.7, 121.5)
MCU_KEEPOUT_R = (132.3, 101.5, 135.5, 121.5)

# Components to place on Bottom:
# 1. SHT45 (SZH-MIN069):
#    Horizontal: 25.5(W) x 17.8(H). Pin header: 1x05 along 25.5 edge (X span 10.16mm).
#    Vertical: 17.8(W) x 25.5(H). Pin header: 1x05 along 25.5 edge (Y span 10.16mm).
# 2. GY-521 (SZH-EK007):
#    Horizontal: 20.70(W) x 15.65(H). Pin header: 1x08 along 20.70 edge (X span 17.78mm).
#    Vertical: 15.65(W) x 20.70(H). Pin header: 1x08 along 20.70 edge (Y span 17.78mm).
# 3. GPS (ATGM336H SZH-MIN053):
#    Horizontal: 15.7(W) x 13.1(H). Pin header: 1x05 along 13.1 edge (Y span 10.16mm).
#    Vertical: 13.1(W) x 15.7(H). Pin header: 1x05 along 13.1 edge (X span 10.16mm).

print("Searching valid Bottom placements...")

solutions = []

# SHT45 horizontal or vertical:
for sht_rot in ['H', 'V']:
    sht_w, sht_h = (25.5, 17.8) if sht_rot == 'H' else (17.8, 25.5)
    for sht_x in [x * 0.5 for x in range(201, 290)]:
        for sht_y in [y * 0.5 for y in range(201, 290)]:
            sht_r = (sht_x, sht_y, sht_x + sht_w, sht_y + sht_h)
            if not valid_rect(sht_r):
                continue
            if overlap(sht_r, MCU_KEEPOUT_L) or overlap(sht_r, MCU_KEEPOUT_R):
                continue
            
            # GY-521 horizontal or vertical:
            for gy_rot in ['H', 'V']:
                gy_w, gy_h = (20.7, 15.65) if gy_rot == 'H' else (15.65, 20.7)
                for gy_x in [x * 0.5 for x in range(201, 290)]:
                    for gy_y in [y * 0.5 for y in range(201, 290)]:
                        gy_r = (gy_x, gy_y, gy_x + gy_w, gy_y + gy_h)
                        if not valid_rect(gy_r):
                            continue
                        if overlap(gy_r, MCU_KEEPOUT_L) or overlap(gy_r, MCU_KEEPOUT_R):
                            continue
                        if overlap(sht_r, gy_r):
                            continue
                        
                        # GPS horizontal or vertical:
                        for gps_rot in ['H', 'V']:
                            gps_w, gps_h = (15.7, 13.1) if gps_rot == 'H' else (13.1, 15.7)
                            for gps_x in [x * 0.5 for x in range(201, 290)]:
                                for gps_y in [y * 0.5 for y in range(201, 290)]:
                                    gps_r = (gps_x, gps_y, gps_x + gps_w, gps_y + gps_h)
                                    if not valid_rect(gps_r):
                                        continue
                                    if overlap(gps_r, MCU_KEEPOUT_L) or overlap(gps_r, MCU_KEEPOUT_R):
                                        continue
                                    if overlap(sht_r, gps_r) or overlap(gy_r, gps_r):
                                        continue
                                    
                                    solutions.append((sht_rot, sht_r, gy_rot, gy_r, gps_rot, gps_r))
                                    if len(solutions) >= 5:
                                        break
                                if len(solutions) >= 5: break
                            if len(solutions) >= 5: break
                        if len(solutions) >= 5: break
                    if len(solutions) >= 5: break
                if len(solutions) >= 5: break
            if len(solutions) >= 5: break
        if len(solutions) >= 5: break
    if len(solutions) >= 5: break

print(f"Found {len(solutions)} valid layouts!")
for i, sol in enumerate(solutions):
    sht_rot, sht_r, gy_rot, gy_r, gps_rot, gps_r = sol
    print(f"\n--- Solution {i+1} ---")
    print(f"  SHT45 ({sht_rot}): X=[{sht_r[0]:.1f}, {sht_r[2]:.1f}], Y=[{sht_r[1]:.1f}, {sht_r[3]:.1f}]")
    print(f"  GY-521 ({gy_rot}): X=[{gy_r[0]:.1f}, {gy_r[2]:.1f}], Y=[{gy_r[1]:.1f}, {gy_r[3]:.1f}]")
    print(f"  GPS ({gps_rot}):    X=[{gps_r[0]:.1f}, {gps_r[2]:.1f}], Y=[{gps_r[1]:.1f}, {gps_r[3]:.1f}]")
