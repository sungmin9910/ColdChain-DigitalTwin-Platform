import sys
sys.path.append('scratch')
from solve_zero_cross_routing import pads, dist_point_to_segment, seg_dist

def run_drc(top, bot):
    all_traces = [("F.Cu", t) for t in top] + [("B.Cu", t) for t in bot]
    errors = []

    for layer, (tname, tnet, x1, y1, x2, y2) in all_traces:
        for pname, pnet, px, py, pr in pads:
            if tnet != pnet and pnet != 0:
                if pname in ['SW1_1', 'SW1_2', 'SW1_3', 'R3_1', 'R3_2', 'R4_1', 'R4_2'] and layer != "F.Cu":
                    continue
                d = dist_point_to_segment(px, py, x1, y1, x2, y2)
                if d < pr + 0.20:
                    errors.append(f"PAD ERROR {layer}: {tname}(Net {tnet}) close to {pname}(Net {pnet}), d={d:.3f}, req={pr+0.20:.3f}")

    for layer_name in ["F.Cu", "B.Cu"]:
        traces_l = [t for l, t in all_traces if l == layer_name]
        for i in range(len(traces_l)):
            for j in range(i+1, len(traces_l)):
                t1 = traces_l[i]
                t2 = traces_l[j]
                if t1[1] != t2[1]:
                    d = seg_dist(t1[2], t1[3], t1[4], t1[5], t2[2], t2[3], t2[4], t2[5])
                    if d < 0.20:
                        errors.append(f"TRACK ERROR {layer_name}: {t1[0]}(Net {t1[1]}) and {t2[0]}(Net {t2[1]}) close/cross! d={d:.3f}")

    return errors

print("DRC engine loaded.")
