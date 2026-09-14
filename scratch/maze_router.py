import heapq
import numpy as np
import os
import sys

# Board boundary: 100.0 to 150.0 in X and Y
GRID_RES = 0.25  # 0.25 mm per cell
ORIGIN_X = 100.0
ORIGIN_Y = 100.0
WIDTH_MM = 50.0
HEIGHT_MM = 50.0

GRID_W = int(round(WIDTH_MM / GRID_RES)) + 1  # 201
GRID_H = int(round(HEIGHT_MM / GRID_RES)) + 1  # 201

def to_grid(x, y):
    gx = int(round((x - ORIGIN_X) / GRID_RES))
    gy = int(round((y - ORIGIN_Y) / GRID_RES))
    return max(0, min(GRID_W - 1, gx)), max(0, min(GRID_H - 1, gy))

def to_world(gx, gy):
    return ORIGIN_X + gx * GRID_RES, ORIGIN_Y + gy * GRID_RES

sys.path.append('scratch')
from solve_zero_cross_routing import pads

# Grid: 0=F.Cu, 1=B.Cu
# Value in cell: 0 = free, >0 = routed Net ID, -1 = keepout/board edge, -2 = pad of another net, etc.
occ = np.zeros((2, GRID_W, GRID_H), dtype=np.int32)

# Mark edges (0.8mm border margin)
margin = int(round(0.8 / GRID_RES))
occ[:, :margin, :] = -1
occ[:, -margin:, :] = -1
occ[:, :, :margin] = -1
occ[:, :, -margin:] = -1

CLEARANCE = 0.30  # 0.30mm clearance
CLEAR_CELLS = int(np.ceil(CLEARANCE / GRID_RES))

smd_names = ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2']

pad_dict = {}
for pname, pnet, px, py, pr in pads:
    gx, gy = to_grid(px, py)
    pad_dict[pname] = (pnet, px, py, pr, gx, gy)
    layers = [0] if pname in smd_names else [0, 1]
    r_cells = int(np.ceil((pr + CLEARANCE) / GRID_RES))
    for l in layers:
        for dx in range(-r_cells, r_cells + 1):
            for dy in range(-r_cells, r_cells + 1):
                if dx*dx + dy*dy <= r_cells*r_cells:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                        if occ[l, nx, ny] == 0:
                            # mark as pad clearance zone for pnet
                            occ[l, nx, ny] = -100 - pnet

# Mark exact pad centers as the net itself
for pname, (pnet, px, py, pr, gx, gy) in pad_dict.items():
    layers = [0] if pname in smd_names else [0, 1]
    for l in layers:
        occ[l, gx, gy] = pnet

print("Grid setup complete.")

# A* Router
def astar_route(net_id, start_pos, target_positions, preferred_layer=None):
    """
    start_pos: (layer, gx, gy)
    target_positions: list of (layer, gx, gy)
    """
    targets = set(target_positions)
    target_coords = [(gx, gy) for (l, gx, gy) in targets]

    def heuristic(l, gx, gy):
        min_d = 999999
        for tgx, tgy in target_coords:
            d = abs(gx - tgx) + abs(gy - tgy)
            if d < min_d: min_d = d
        # small layer preference penalty
        layer_penalty = 0
        if preferred_layer is not None and l != preferred_layer:
            layer_penalty = 5
        return min_d + layer_penalty

    # Priority queue: (f_score, g_score, l, gx, gy)
    pq = []
    start_l, start_gx, start_gy = start_pos
    h0 = heuristic(start_l, start_gx, start_gy)
    heapq.heappush(pq, (h0, 0, start_l, start_gx, start_gy))
    
    g_score = {}
    g_score[(start_l, start_gx, start_gy)] = 0
    came_from = {}
    
    # 4 cardinal directions (keep traces rectilinear/orthogonal)
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    found_target = None
    
    while pq:
        f, g, l, gx, gy = heapq.heappop(pq)
        
        if (l, gx, gy) in targets:
            found_target = (l, gx, gy)
            break
            
        if g > g_score.get((l, gx, gy), 999999):
            continue
            
        # Try moving on same layer
        for dx, dy in dirs:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                cell_val = occ[l, nx, ny]
                # Can move if:
                # 1. cell is 0 (free)
                # 2. cell is net_id (already routed this net)
                # 3. cell is -100 - net_id (clearance zone of this net's pads)
                # 4. (l, nx, ny) is one of targets
                can_move = (cell_val == 0 or cell_val == net_id or cell_val == (-100 - net_id) or (l, nx, ny) in targets)
                if can_move:
                    ng = g + 1.0
                    # Layer change / bend penalty
                    if (l, nx, ny) not in g_score or ng < g_score[(l, nx, ny)]:
                        g_score[(l, nx, ny)] = ng
                        came_from[(l, nx, ny)] = (l, gx, gy)
                        heapq.heappush(pq, (ng + heuristic(l, nx, ny), ng, l, nx, ny))
                        
        # Try via to other layer (cost 15)
        nl = 1 - l
        cell_val = occ[nl, gx, gy]
        can_via = (cell_val == 0 or cell_val == net_id or cell_val == (-100 - net_id) or (nl, gx, gy) in targets)
        if can_via:
            ng = g + 15.0
            if (nl, gx, gy) not in g_score or ng < g_score[(nl, gx, gy)]:
                g_score[(nl, gx, gy)] = ng
                came_from[(nl, gx, gy)] = (l, gx, gy)
                heapq.heappush(pq, (ng + heuristic(nl, gx, gy), ng, nl, gx, gy))
                
    if found_target is None:
        return None
        
    # Reconstruct path
    curr = found_target
    path = [curr]
    while curr in came_from:
        curr = came_from[curr]
        path.append(curr)
    path.reverse()
    return path

def mark_path(net_id, path):
    clear_r = int(np.ceil(CLEARANCE / GRID_RES))
    for l, gx, gy in path:
        # Mark cell as net_id
        occ[l, gx, gy] = net_id
        # Mark clearance zone
        for dx in range(-clear_r, clear_r + 1):
            for dy in range(-clear_r, clear_r + 1):
                if dx*dx + dy*dy <= clear_r*clear_r:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                        if occ[l, nx, ny] == 0:
                            occ[l, nx, ny] = -100 - net_id

def path_to_segments(net_id, path, net_name):
    # Simplify straight lines into segments
    if not path or len(path) < 2:
        return [], []
    segments = []
    vias = []
    
    cur_l, cur_x, cur_y = path[0]
    seg_start = (cur_l, cur_x, cur_y)
    prev_dir = None
    
    for i in range(1, len(path)):
        pl, px, py = path[i]
        if pl != cur_l: # VIA!
            # End previous segment
            w_s_x, w_s_y = to_world(seg_start[1], seg_start[2])
            w_e_x, w_e_y = to_world(cur_x, cur_y)
            if (w_s_x, w_s_y) != (w_e_x, w_e_y):
                layer_name = "F.Cu" if cur_l == 0 else "B.Cu"
                segments.append((net_name, net_id, layer_name, w_s_x, w_s_y, w_e_x, w_e_y))
            vx, vy = to_world(cur_x, cur_y)
            vias.append((net_id, vx, vy))
            seg_start = (pl, px, py)
            cur_l, cur_x, cur_y = pl, px, py
            prev_dir = None
            continue
            
        cur_dir = (px - cur_x, py - cur_y)
        if prev_dir is not None and cur_dir != prev_dir:
            # Direction changed, finish segment
            w_s_x, w_s_y = to_world(seg_start[1], seg_start[2])
            w_e_x, w_e_y = to_world(cur_x, cur_y)
            layer_name = "F.Cu" if cur_l == 0 else "B.Cu"
            segments.append((net_name, net_id, layer_name, w_s_x, w_s_y, w_e_x, w_e_y))
            seg_start = (cur_l, cur_x, cur_y)
            
        prev_dir = cur_dir
        cur_x, cur_y = px, py
        
    # Final segment
    w_s_x, w_s_y = to_world(seg_start[1], seg_start[2])
    w_e_x, w_e_y = to_world(cur_x, cur_y)
    if (w_s_x, w_s_y) != (w_e_x, w_e_y):
        layer_name = "F.Cu" if cur_l == 0 else "B.Cu"
        segments.append((net_name, net_id, layer_name, w_s_x, w_s_y, w_e_x, w_e_y))
        
    return segments, vias

print("A* maze router algorithm loaded.")
