import math

# Board: 100 to 150 mm in X and Y
# M3 Holes at (103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5).
# Keepout circle: center (hx, hy), radius = 2.75mm (pad) + 0.5mm (head clearance) = 3.25mm.
HOLES = [(103.5, 103.5), (146.5, 103.5), (103.5, 146.5), (146.5, 146.5)]

def rect_intersects_rect(r1, r2):
    # r = (xmin, ymin, xmax, ymax)
    return not (r1[2] <= r2[0] or r1[0] >= r2[2] or r1[3] <= r2[1] or r1[1] >= r2[3])

def rect_intersects_circle(r, cx, cy, radius):
    # closest point on rect to circle center
    closest_x = max(r[0], min(cx, r[2]))
    closest_y = max(r[1], min(cy, r[3]))
    dist = math.hypot(closest_x - cx, closest_y - cy)
    return dist < radius

def rect_inside_board(r, margin=0.5):
    return (r[0] >= 100.0 + margin and r[2] <= 150.0 - margin and
            r[1] >= 100.0 + margin and r[3] <= 150.0 - margin)

# MCU top side
MCU_RECT = (114.75, 100.0, 135.25, 125.0)
# MCU TH Pins on Bottom:
# Left row: X=116.11, Y=102.66 to 120.44 (pad diameter 1.6 -> X in [115.3, 116.9], Y in [101.8, 121.3])
MCU_TH_LEFT = (115.0, 101.5, 117.2, 121.5)
# Right row: X=133.89, Y=102.66 to 120.44
MCU_TH_RIGHT = (132.8, 101.5, 135.0, 121.5)

print("--- Testing Top Side Layout ---")
# 1. BH1750 on Top Right:
# GY-302 size: 13.9mm wide (X), 18.5mm high (Y).
# Header is at top: Y=146.0, spanning X from (cx - 5.08) to (cx + 5.08).
# Body: X from cx - 6.95 to cx + 6.95. Y from 146.0 - 16.5 = 129.5 to 148.0.
bh_cx = 136.0
bh_rect = (bh_cx - 6.95, 129.5, bh_cx + 6.95, 148.0)
print(f"BH1750 rect: {bh_rect}")
print(f"BH1750 inside board: {rect_inside_board(bh_rect)}")
print(f"BH1750 hits MCU: {rect_intersects_rect(bh_rect, MCU_RECT)}")
for h in HOLES:
    if rect_intersects_circle(bh_rect, h[0], h[1], 3.25):
        print(f"BH1750 hits hole {h}!")

# 2. Power: JST-PH and SW1 on Top Center
jst_rect = (122.0, 144.0, 128.0, 148.5)
sw_rect = (121.5, 136.0, 128.5, 140.5)
print(f"JST-PH rect: {jst_rect}, hits BH: {rect_intersects_rect(jst_rect, bh_rect)}")
print(f"SW1 rect: {sw_rect}, hits BH: {rect_intersects_rect(sw_rect, bh_rect)}")

print("\n--- Testing Bottom Side Layout ---")
# On Bottom Side, we need to place:
# - SHT45: Adafruit Qwiic (PCB 25.5 x 17.8 mm, with connectors ~32.0 x 17.8 mm)
# - GY-521: 15.65 x 20.70 mm
# - ATGM336H GPS: 13.1 x 15.7 mm

# Let's explore placements for Bottom side components!
# Can SHT45 be placed at Top-Left of Bottom (Y in [128.0, 146.0])?
# Let's check:
# SHT45 horizontal: Width = 25.5 mm (X), Height = 17.8 mm (Y).
# If X is [105.0, 130.5], Y is [127.0, 144.8]:
sht_rect = (105.0, 127.0, 130.5, 144.8)
print(f"SHT45 (horizontal) rect: {sht_rect}")
print(f"SHT45 inside board: {rect_inside_board(sht_rect)}")
for h in HOLES:
    if rect_intersects_circle(sht_rect, h[0], h[1], 3.25):
        print(f"SHT45 hits hole {h}!")

# Now where can GY-521 go?
# Option A: GY-521 on Bottom Left (vertical):
# GY-521 is 15.65mm wide (X) x 20.70mm high (Y).
# Pins along 20.70mm edge.
# Can it be placed at Y in [103.0, 124.0]?
# Remember MCU TH Left is at X in [115.0, 117.2].
# From X=100.0 to 115.0 is 15.0 mm. GY-521 width is 15.65 mm.
# 15.65 mm > 15.0 mm by 0.65 mm!
# What if GY-521 is rotated horizontally (Width=20.70, Height=15.65)?
# What if GY-521 is placed at Bottom Right or Center?
# Or what if SHT45 and GY-521 are placed differently?
# Let's test all orientations!
