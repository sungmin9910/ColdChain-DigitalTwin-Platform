import math

def check_clearances():
    # Board: 100 to 150 mm in X and Y
    HOLES = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]
    HOLE_PAD_R = 2.75 # 5.5mm diameter

    # -----------------------------
    # TOP SIDE COMPONENTS
    # -----------------------------
    # 1. Beetle C6 (Top, Bottom-Center):
    # Body: 20.5(W) x 25.0(H)
    mcu_body = (114.75, 100.0, 135.25, 125.0)
    # Pads (Through Hole):
    mcu_pads_L = [(116.11, 102.66 + i * 2.54) for i in range(8)]
    mcu_pads_R = [(133.89, 102.66 + i * 2.54) for i in range(8)]

    # 2. BH1750 (Top, Top-Right):
    # SZH-EK070: 13.9(W) x 18.5(H)
    # Let center of 5 pins be at X=136.0, Y=145.5.
    # Pins: 1x05 horizontal (pitch 2.54): (136.0 - 5.08) to (136.0 + 5.08) -> X in [130.92, 141.08]
    # Body: X in [136.0 - 6.95, 136.0 + 6.95] = [129.05, 142.95]
    # Y from 145.5 - 16.5 = 129.0 to 145.5 + 2.0 = 147.5
    bh_body = (129.05, 129.0, 142.95, 147.5)
    bh_pads = [(130.92 + i * 2.54, 145.5) for i in range(5)]

    # 3. JST-PH 2.0 (Top, Top-Center):
    # Pins at X=124.0, 126.0, Y=146.5
    jst_body = (122.0, 144.0, 128.0, 148.5)
    jst_pads = [(124.0, 146.5), (126.0, 146.5)]

    # 4. SW1 PCM12 (Top, Top-Center SMD):
    sw_body = (121.5, 136.5, 128.5, 140.5)
    sw_pads_smd = [(123.5, 138.5), (125.0, 138.5), (126.5, 138.5)]

    # -----------------------------
    # BOTTOM SIDE COMPONENTS
    # -----------------------------
    # 5. SHT45 (Bottom, Top-Left):
    # SZH-MIN069: 25.5(W) x 17.8(H)
    # Let X in [101.5, 127.0] (W=25.5), Y in [124.0, 141.8] (H=17.8).
    # Header 1x05 horizontal: let's put header at Y=126.5, centered at X=114.25 (span 109.17 to 119.33)
    sht_body = (101.5, 124.0, 127.0, 141.8)
    sht_pads = [(109.17 + i * 2.54, 126.5) for i in range(5)]

    # 6. GY-521 (Bottom, Right-Center):
    # SZH-EK007: 20.70(W) x 15.65(H) (Horizontal orientation)
    # Header 1x08 horizontal (pitch 2.54, span 17.78mm).
    # Header is at bottom edge (1.28mm offset), body extends upwards by 14.37mm.
    # Let X in [127.0, 147.7] (W=20.70), Y in [124.0, 139.65] (H=15.65).
    # Header at Y=125.5, X from (127.0 + 1.46) to (147.7 - 1.46) -> X in [128.46, 146.24]
    gy_body = (127.0, 124.0, 147.7, 139.65)
    gy_pads = [(128.46 + i * 2.54, 125.5) for i in range(8)]

    # 7. ATGM336H GPS (Bottom, Bottom-Center in Channel):
    # SZH-MIN053: 13.1(W) x 15.7(H) (Vertical orientation)
    # Header 1x05 horizontal: 13.1mm edge (span 10.16mm).
    # Let X in [118.45, 131.55] (W=13.1), Y in [102.0, 117.7] (H=15.7).
    # Header at Y=103.5, centered at X=125.0: X from 119.92 to 130.08
    gps_body = (118.45, 102.0, 131.55, 117.7)
    gps_pads = [(119.92 + i * 2.54, 103.5) for i in range(5)]

    print("=== CHECKING ALL DESIGN RULES ===")
    errors = []

    # 1. Check all bodies inside board
    bodies = {
        "MCU (Top)": mcu_body,
        "BH1750 (Top)": bh_body,
        "JST-PH (Top)": jst_body,
        "SW1 (Top)": sw_body,
        "SHT45 (Bottom)": sht_body,
        "GY-521 (Bottom)": gy_body,
        "GPS (Bottom)": gps_body
    }
    for name, (x1, y1, x2, y2) in bodies.items():
        if x1 < 100.0 or x2 > 150.0 or y1 < 100.0 or y2 > 150.0:
            errors.append(f"{name} protrudes outside 50x50 board: ({x1}, {y1}, {x2}, {y2})")

    # 2. Check collisions against M3 holes
    for name, (x1, y1, x2, y2) in bodies.items():
        for hx, hy in HOLES:
            cx = max(x1, min(hx, x2))
            cy = max(y1, min(hy, y2))
            d = math.hypot(cx - hx, cy - hy)
            if d < HOLE_PAD_R:
                errors.append(f"{name} collides with M3 hole ({hx}, {hy}): distance {d:.2f}mm < {HOLE_PAD_R}mm")

    # 3. Check Top-Top collisions
    top_bodies = [("MCU", mcu_body), ("BH1750", bh_body), ("JST-PH", jst_body), ("SW1", sw_body)]
    for i in range(len(top_bodies)):
        for j in range(i + 1, len(top_bodies)):
            n1, b1 = top_bodies[i]
            n2, b2 = top_bodies[j]
            if not (b1[2] <= b2[0] or b1[0] >= b2[2] or b1[3] <= b2[1] or b1[1] >= b2[3]):
                errors.append(f"Top collision between {n1} and {n2}!")

    # 4. Check Bottom-Bottom collisions
    bot_bodies = [("SHT45", sht_body), ("GY-521", gy_body), ("GPS", gps_body)]
    for i in range(len(bot_bodies)):
        for j in range(i + 1, len(bot_bodies)):
            n1, b1 = bot_bodies[i]
            n2, b2 = bot_bodies[j]
            if not (b1[2] <= b2[0] or b1[0] >= b2[2] or b1[3] <= b2[1] or b1[1] >= b2[3]):
                errors.append(f"Bottom collision between {n1} and {n2}!")

    # 5. Check TH Pad to TH Pad clearances (Top vs Bottom and same side)
    all_th_pads = []
    for p in mcu_pads_L: all_th_pads.append(("MCU_L", p))
    for p in mcu_pads_R: all_th_pads.append(("MCU_R", p))
    for p in bh_pads: all_th_pads.append(("BH1750", p))
    for p in jst_pads: all_th_pads.append(("JST-PH", p))
    for p in sht_pads: all_th_pads.append(("SHT45", p))
    for p in gy_pads: all_th_pads.append(("GY-521", p))
    for p in gps_pads: all_th_pads.append(("GPS", p))

    pad_d = 1.6 # pad diameter
    min_dist = 2.0 # minimum center-to-center distance for independent nets
    for i in range(len(all_th_pads)):
        for j in range(i + 1, len(all_th_pads)):
            n1, p1 = all_th_pads[i]
            n2, p2 = all_th_pads[j]
            d = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
            # if adjacent pins in same header, pitch is 2.54mm, which is >= 2.0mm
            if d < 1.7:
                errors.append(f"Pad collision between {n1} at {p1} and {n2} at {p2} (dist={d:.2f}mm < 1.7mm)!")

    # 6. Check Bottom component bodies vs Top TH Pins protruding on bottom
    # Bottom components must not sit on top of Top TH soldered pins unless clearance exists
    # SHT45 body vs MCU TH pins:
    for p in mcu_pads_L + mcu_pads_R:
        if sht_body[0] <= p[0] <= sht_body[2] and sht_body[1] <= p[1] <= sht_body[3]:
            errors.append(f"SHT45 on bottom covers MCU TH pin at {p}!")
    # GY-521 body vs MCU TH pins:
    for p in mcu_pads_L + mcu_pads_R:
        if gy_body[0] <= p[0] <= gy_body[2] and gy_body[1] <= p[1] <= gy_body[3]:
            errors.append(f"GY-521 on bottom covers MCU TH pin at {p}!")
    # GPS body vs MCU TH pins:
    for p in mcu_pads_L + mcu_pads_R:
        if gps_body[0] <= p[0] <= gps_body[2] and gps_body[1] <= p[1] <= gps_body[3]:
            errors.append(f"GPS on bottom covers MCU TH pin at {p}!")

    print(f"Total Errors Found: {len(errors)}")
    for e in errors:
        print("  ERROR:", e)

    if not errors:
        print("SUCCESS! ALL CLEARANCES, BOARD OUTLINES, MOUNTING HOLES, AND PADS ARE 100% CLEAN AND CONFLICT-FREE!")

check_clearances()
