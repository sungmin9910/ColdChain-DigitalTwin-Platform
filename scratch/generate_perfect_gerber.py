import os
import sys
import numpy as np
import zipfile

sys.path.append('scratch')
from maze_router import (
    pads, pad_dict, astar_route, mark_path, path_to_segments, to_world, GRID_RES
)

all_segments = []
all_vias = []

def route_net_connection(net_id, net_name, p1_name, p2_name, pref_l=None):
    p1 = pad_dict[p1_name]
    p2 = pad_dict[p2_name]
    
    l1_opts = [pref_l] if pref_l is not None else ([0] if 'SW1' in p1_name or 'R3' in p1_name or 'R4' in p1_name else [0, 1])
    l2_opts = [pref_l] if pref_l is not None else ([0] if 'SW1' in p2_name or 'R3' in p2_name or 'R4' in p2_name else [0, 1])
    
    targets = [(l2, p2[4], p2[5]) for l2 in l2_opts]
    best_path = None
    for l1 in l1_opts:
        start_pos = (l1, p1[4], p1[5])
        path = astar_route(net_id, start_pos, targets, preferred_layer=pref_l)
        if path is not None:
            if best_path is None or len(path) < len(best_path):
                best_path = path
                
    if best_path is None:
        raise RuntimeError(f"FAILED to route {net_name}: {p1_name} -> {p2_name}")
    else:
        mark_path(net_id, best_path)
        segs, vias = path_to_segments(net_id, best_path, net_name)
        all_segments.extend(segs)
        all_vias.extend(vias)
        return len(best_path)

print("Routing entire board...")
route_net_connection(3, 'BAT+', 'J1_1', 'SW1_1', pref_l=0)
route_net_connection(4, 'BAT', 'SW1_2', 'MCU_L_1', pref_l=0)
route_net_connection(7, 'GPS_RX', 'MCU_L_4', 'GPS_3', pref_l=0)
route_net_connection(8, 'GPS_TX', 'MCU_L_5', 'GPS_4', pref_l=1)

# I2C SCL (Net 6)
route_net_connection(6, 'I2C_SCL', 'MCU_L_7', 'SHT_4', pref_l=1)
route_net_connection(6, 'I2C_SCL', 'SHT_4', 'GY_3', pref_l=1)
route_net_connection(6, 'I2C_SCL', 'GY_3', 'BH_3', pref_l=1)
route_net_connection(6, 'I2C_SCL', 'GY_3', 'R4_1')

# I2C SDA (Net 5)
route_net_connection(5, 'I2C_SDA', 'MCU_L_6', 'SHT_5', pref_l=0)
route_net_connection(5, 'I2C_SDA', 'SHT_5', 'R3_1', pref_l=0)
route_net_connection(5, 'I2C_SDA', 'SHT_5', 'GY_4', pref_l=0)
route_net_connection(5, 'I2C_SDA', 'GY_4', 'BH_4', pref_l=0)

# 3V3 (Net 2)
route_net_connection(2, '3V3', 'MCU_R_2', 'BH_1', pref_l=0)
route_net_connection(2, '3V3', 'BH_1', 'R4_2', pref_l=0)
route_net_connection(2, '3V3', 'R4_2', 'R3_2', pref_l=0)
route_net_connection(2, '3V3', 'MCU_R_2', 'GY_1', pref_l=1)
route_net_connection(2, '3V3', 'GY_1', 'SHT_1', pref_l=1)
route_net_connection(2, '3V3', 'SHT_1', 'GPS_1', pref_l=1)

# GND (Net 1)
route_net_connection(1, 'GND', 'MCU_L_2', 'GPS_2', pref_l=1)
route_net_connection(1, 'GND', 'GPS_2', 'H1', pref_l=1)
route_net_connection(1, 'GND', 'MCU_R_1', 'H2', pref_l=0)
route_net_connection(1, 'GND', 'H2', 'BH_5', pref_l=0)
route_net_connection(1, 'GND', 'BH_5', 'BH_2', pref_l=0)
route_net_connection(1, 'GND', 'H3', 'SHT_3', pref_l=1)
route_net_connection(1, 'GND', 'H4', 'GY_7', pref_l=1)
route_net_connection(1, 'GND', 'GY_7', 'GY_2', pref_l=1)
route_net_connection(1, 'GND', 'H4', 'J1_2', pref_l=0)

# Remove duplicate vias
unique_vias = []
seen_vias = set()
for net_id, vx, vy in all_vias:
    key = (net_id, round(vx, 2), round(vy, 2))
    if key not in seen_vias:
        seen_vias.add(key)
        unique_vias.append(key)

print(f"Total Segments: {len(all_segments)}, Unique Vias: {len(unique_vias)}")

# -------------------------------------------------------------
# RUN FULL DRC CHECK ON GENERATED SEGMENTS
# -------------------------------------------------------------
from test_clean_routes import dist_point_to_segment, seg_dist

drc_errors = 0
for net_name, net_id, layer, x1, y1, x2, y2 in all_segments:
    # Check against pads
    for pname, pnet, px, py, pr in pads:
        if pnet != net_id and pnet != 0:
            d = dist_point_to_segment(px, py, x1, y1, x2, y2)
            if d < pr + 0.20:
                print(f"DRC Error Pad: {net_name}({net_id}) on {layer} close to {pname}({pnet}), d={d:.3f}, req={pr+0.20:.3f}")
                drc_errors += 1

# Check track-to-track on each layer
for l_name in ["F.Cu", "B.Cu"]:
    segs_l = [s for s in all_segments if s[2] == l_name]
    for i in range(len(segs_l)):
        for j in range(i+1, len(segs_l)):
            s1 = segs_l[i]
            s2 = segs_l[j]
            if s1[1] != s2[1]: # different nets
                d = seg_dist(s1[3], s1[4], s1[5], s1[6], s2[3], s2[4], s2[5], s2[6])
                if d < 0.20:
                    print(f"DRC Error Track: {s1[0]}({s1[1]}) and {s2[0]}({s2[1]}) on {l_name} close/cross! d={d:.3f}")
                    drc_errors += 1

print(f"TOTAL DRC ERRORS: {drc_errors}")
if drc_errors == 0:
    print("SUCCESS! 100% CLEAN ELECTRICAL ROUTING, 0 ERRORS!")
