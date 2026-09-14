import math

HOLES = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]
HOLE_PAD_R = 2.75

def inside(r, margin=0.5):
    return (r[0] >= 100.0 + margin and r[2] <= 150.0 - margin and
            r[1] >= 100.0 + margin and r[3] <= 150.0 - margin)

def clears_holes(r, margin=0.3):
    for hx, hy in HOLES:
        cx = max(r[0], min(hx, r[2]))
        cy = max(r[1], min(hy, r[3]))
        if math.hypot(cx - hx, cy - hy) < HOLE_PAD_R + margin:
            return False
    return True

def overlap(r1, r2, clearance=1.0):
    return not (r1[2] + clearance <= r2[0] or r1[0] - clearance >= r2[2] or
                r1[3] + clearance <= r2[1] or r1[1] - clearance >= r2[3])

# Beetle C6 on Top:
MCU_BODY = (114.75, 100.0, 135.25, 125.0)
MCU_PINS_L = [(116.11, 102.66 + i * 2.54) for i in range(8)]
MCU_PINS_R = [(133.89, 102.66 + i * 2.54) for i in range(8)]

# Under Beetle C6, NO TH pins on Bottom to prevent touching Beetle C6 components/USB:
MCU_KEEPOUT_TH = (114.5, 100.0, 135.5, 125.5)

# Components to place:
# 1. BH1750 (Top): 13.9(W) x 18.5(H) or 18.5(W) x 13.9(H)
# 2. JST-PH (Top): 6.0 x 4.5. Pins: (124.0, 146.5), (126.0, 146.5)
# 3. SW1 (Top SMD): 7.0 x 4.0. Pads: Y=138.5, X in [123.5, 126.5]
# 4. SHT45 (Top or Bottom): 25.5 x 17.8 or 17.8 x 25.5
# 5. GY-521 (Top or Bottom): 20.7 x 15.65 or 15.65 x 20.7
# 6. ATGM336H GPS (Top or Bottom): 13.1 x 15.7 or 15.7 x 13.1

# Let's search all possible side assignments:
# Which side for each?
# BH1750: MUST BE TOP (for light sensing)
# SHT45: Top or Bottom
# GY-521: Top or Bottom
# GPS: Top or Bottom

# Can GY-521 and GPS be on Bottom, and SHT45 be on Bottom?
# Or SHT45 on Top?
# Let's search configurations!

valid_configs = []

# BH1750 at Top-Right on TOP side:
# Y=145.5 for pins, X=136.0 (range 130.92 to 141.08)
# Body: X in [129.05, 142.95], Y in [128.5, 147.0]
bh_body = (129.05, 128.5, 142.95, 147.0)
bh_pins = [(130.92 + i*2.54, 145.5) for i in range(5)]
jst_pins = [(124.0, 146.5), (126.0, 146.5)]
jst_body = (122.0, 144.0, 128.0, 148.5)
sw_body = (121.5, 136.5, 128.5, 140.5)

top_bodies = [("MCU", MCU_BODY), ("BH1750", bh_body), ("JST-PH", jst_body), ("SW1", sw_body)]
top_th_pins = MCU_PINS_L + MCU_PINS_R + bh_pins + jst_pins

# Now search for 3 components: SHT45, GY521, GPS.
# They can be placed on Bottom (or Top if room).
# Let's check Bottom side placements:

print("Testing placement search...")
for gy_rot in ['H', 'V']:
    gy_w, gy_h = (20.7, 15.65) if gy_rot == 'H' else (15.65, 20.7)
    for gy_x in [x * 0.5 for x in range(201, 290)]:
        for gy_y in [y * 0.5 for y in range(201, 290)]:
            gy_r = (gy_x, gy_y, gy_x + gy_w, gy_y + gy_h)
            if not inside(gy_r) or not clears_holes(gy_r): continue
            
            # GY pins
            if gy_rot == 'H':
                # pins along bottom long edge (offset 1.28)
                gy_p_y = gy_y + 1.28
                gy_p_xs = [gy_x + 1.46 + i*2.54 for i in range(8)]
                gy_pins = [(x, gy_p_y) for x in gy_p_xs]
            else:
                gy_p_x = gy_x + 1.28
                gy_p_ys = [gy_y + 1.46 + i*2.54 for i in range(8)]
                gy_pins = [(gy_p_x, y) for y in gy_p_ys]
                
            # check GY pins against keepout and top TH pins
            if any(MCU_KEEPOUT_TH[0] <= p[0] <= MCU_KEEPOUT_TH[2] and MCU_KEEPOUT_TH[1] <= p[1] <= MCU_KEEPOUT_TH[3] for p in gy_pins):
                continue
            if any(math.hypot(p[0]-tp[0], p[1]-tp[1]) < 2.0 for p in gy_pins for tp in top_th_pins):
                continue

            for sht_rot in ['H', 'V']:
                sht_w, sht_h = (25.5, 17.8) if sht_rot == 'H' else (17.8, 25.5)
                for sht_x in [x * 0.5 for x in range(201, 290)]:
                    for sht_y in [y * 0.5 for y in range(201, 290)]:
                        sht_r = (sht_x, sht_y, sht_x + sht_w, sht_y + sht_h)
                        if not inside(sht_r) or not clears_holes(sht_r): continue
                        if overlap(gy_r, sht_r): continue
                        
                        # SHT pins
                        if sht_rot == 'H':
                            sht_p_y = sht_y + 2.0
                            sht_pins = [(sht_x + 7.67 + i*2.54, sht_p_y) for i in range(5)]
                        else:
                            sht_p_x = sht_x + 2.0
                            sht_pins = [(sht_p_x, sht_y + 7.67 + i*2.54) for i in range(5)]
                            
                        if any(MCU_KEEPOUT_TH[0] <= p[0] <= MCU_KEEPOUT_TH[2] and MCU_KEEPOUT_TH[1] <= p[1] <= MCU_KEEPOUT_TH[3] for p in sht_pins):
                            continue
                        if any(math.hypot(p[0]-tp[0], p[1]-tp[1]) < 2.0 for p in sht_pins for tp in top_th_pins):
                            continue
                        if any(math.hypot(p[0]-gp[0], p[1]-gp[1]) < 2.0 for p in sht_pins for gp in gy_pins):
                            continue

                        for gps_rot in ['H', 'V']:
                            gps_w, gps_h = (15.7, 13.1) if gps_rot == 'H' else (13.1, 15.7)
                            for gps_x in [x * 0.5 for x in range(201, 290)]:
                                for gps_y in [y * 0.5 for y in range(201, 290)]:
                                    gps_r = (gps_x, gps_y, gps_x + gps_w, gps_y + gps_h)
                                    if not inside(gps_r) or not clears_holes(gps_r): continue
                                    if overlap(gy_r, gps_r) or overlap(sht_r, gps_r): continue
                                    
                                    if gps_rot == 'H':
                                        gps_p_x = gps_x + 2.0
                                        gps_pins = [(gps_p_x, gps_y + 1.47 + i*2.54) for i in range(5)]
                                    else:
                                        gps_p_y = gps_y + 2.0
                                        gps_pins = [(gps_x + 1.47 + i*2.54, gps_p_y) for i in range(5)]
                                        
                                    if any(MCU_KEEPOUT_TH[0] <= p[0] <= MCU_KEEPOUT_TH[2] and MCU_KEEPOUT_TH[1] <= p[1] <= MCU_KEEPOUT_TH[3] for p in gps_pins):
                                        continue
                                    if any(math.hypot(p[0]-tp[0], p[1]-tp[1]) < 2.0 for p in gps_pins for tp in top_th_pins):
                                        continue
                                    if any(math.hypot(p[0]-gp[0], p[1]-gp[1]) < 2.0 for p in gps_pins for gp in gy_pins):
                                        continue
                                    if any(math.hypot(p[0]-sp[0], p[1]-sp[1]) < 2.0 for p in gps_pins for sp in sht_pins):
                                        continue

                                    valid_configs.append((gy_rot, gy_r, gy_pins, sht_rot, sht_r, sht_pins, gps_rot, gps_r, gps_pins))
                                    if len(valid_configs) >= 3: break
                                if len(valid_configs) >= 3: break
                            if len(valid_configs) >= 3: break
                        if len(valid_configs) >= 3: break
                    if len(valid_configs) >= 3: break
                if len(valid_configs) >= 3: break
            if len(valid_configs) >= 3: break
        if len(valid_configs) >= 3: break
    if len(valid_configs) >= 3: break

print(f"Search complete! Found {len(valid_configs)} valid layouts.")
for i, cfg in enumerate(valid_configs):
    gy_rot, gy_r, gy_pins, sht_rot, sht_r, sht_pins, gps_rot, gps_r, gps_pins = cfg
    print(f"\nConfiguration {i+1}:")
    print(f"  GY-521 ({gy_rot}): Rect={gy_r}, Pin1={gy_pins[0]}")
    print(f"  SHT45  ({sht_rot}): Rect={sht_r}, Pin1={sht_pins[0]}")
    print(f"  GPS    ({gps_rot}): Rect={gps_r}, Pin1={gps_pins[0]}")
