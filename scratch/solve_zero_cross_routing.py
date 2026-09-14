import numpy as np

# Pad definitions (exact same coordinates as in master board)
pads = [
    # M3 holes
    ('H1', 1, 103.5, 103.5, 2.75),
    ('H2', 1, 146.5, 103.5, 2.75),
    ('H3', 1, 103.5, 146.5, 2.75),
    ('H4', 1, 146.5, 146.5, 2.75),
    # JST-PH
    ('J1_1', 3, 122.0, 146.5, 0.8),
    ('J1_2', 1, 124.0, 146.5, 0.8),
    # SW1
    ('SW1_1', 3, 114.5, 146.5, 0.6),
    ('SW1_2', 4, 116.0, 146.5, 0.6),
    ('SW1_3', 0, 117.5, 146.5, 0.6),
    # R3 (SDA Pullup)
    ('R3_1', 5, 121.25, 142.0, 0.55),
    ('R3_2', 2, 122.75, 142.0, 0.55),
    # R4 (SCL Pullup)
    ('R4_1', 6, 127.25, 142.0, 0.55),
    ('R4_2', 2, 128.75, 142.0, 0.55),
]

# MCU Left (116.11)
# Pin 1: BAT(4), Pin 2: GND(1), Pin 3: NC, Pin 4: GPS_RX(7), Pin 5: GPS_TX(8), Pin 6: SDA(5), Pin 7: SCL(6), Pin 8: NC
mcu_l_nets = [4, 1, 0, 7, 8, 5, 6, 0]
for i, n in enumerate(mcu_l_nets):
    pads.append((f'MCU_L_{i+1}', n, 116.11, 102.66 + i*2.54, 0.8))

# MCU Right (133.89)
# Pin 1: GND(1), Pin 2: 3V3(2), Pins 3-8: NC
mcu_r_nets = [1, 2, 0, 0, 0, 0, 0, 0]
for i, n in enumerate(mcu_r_nets):
    pads.append((f'MCU_R_{i+1}', n, 133.89, 102.66 + i*2.54, 0.8))

# BH1750 (Right Wing, Y=123.2)
# Pin 1: 3V3(2), Pin 2: GND(1), Pin 3: SCL(6), Pin 4: SDA(5), Pin 5: ADDR->GND(1)
bh_nets = [2, 1, 6, 5, 1]
for i, n in enumerate(bh_nets):
    pads.append((f'BH_{i+1}', n, 137.67 + i*2.54, 123.2, 0.8))

# GPS (Left Wing, Y=109.5)
# Pin 1: 3V3(2), Pin 2: GND(1), Pin 3: TX->MCU_RX(7), Pin 4: RX<-MCU_TX(8), Pin 5: PPS(0)
gps_nets = [2, 1, 7, 8, 0]
for i, n in enumerate(gps_nets):
    pads.append((f'GPS_{i+1}', n, 102.33 + i*2.54, 109.5, 0.8))

# SHT45 (Top-Left, Y=127.5)
# Pin 1: VIN(2), Pin 2: 3Vo(0), Pin 3: GND(1), Pin 4: SCL(6), Pin 5: SDA(5)
sht_nets = [2, 0, 1, 6, 5]
for i, n in enumerate(sht_nets):
    pads.append((f'SHT_{i+1}', n, 108.17 + i*2.54, 127.5, 0.8))

# GY-521 (Top-Right, Y=127.5)
# Pin 1: VCC(2), Pin 2: GND(1), Pin 3: SCL(6), Pin 4: SDA(5), Pin 5: NC, Pin 6: NC, Pin 7: AD0->GND(1), Pin 8: NC
gy_nets = [2, 1, 6, 5, 0, 0, 1, 0]
for i, n in enumerate(gy_nets):
    pads.append((f'GY_{i+1}', n, 129.56 + i*2.54, 127.5, 0.8))

def dist_point_to_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return np.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1)*dx + (py - y1)*dy) / (dx*dx + dy*dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return np.hypot(px - proj_x, py - proj_y)

def seg_dist(x1, y1, x2, y2, x3, y3, x4, y4):
    pts1 = [ (x1 + t*(x2-x1), y1 + t*(y2-y1)) for t in np.linspace(0, 1, 25) ]
    pts2 = [ (x3 + t*(x4-x3), y3 + t*(y4-y3)) for t in np.linspace(0, 1, 25) ]
    min_d = 999.0
    for px, py in pts1:
        d = dist_point_to_segment(px, py, x3, y3, x4, y4)
        if d < min_d: min_d = d
    for px, py in pts2:
        d = dist_point_to_segment(px, py, x1, y1, x2, y2)
        if d < min_d: min_d = d
    return min_d

print(f"Total pads loaded: {len(pads)}")
