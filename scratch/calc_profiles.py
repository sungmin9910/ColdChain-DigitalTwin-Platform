import numpy as np
import scipy.interpolate as interp

# Outer apple profile in (R, Z)
# Z ranges from -38.5 (bottom rim) to +41.5 (top rim), total height 80mm
# Max radius ~43mm at Z = +4mm
outer_pts = np.array([
    [0.0, -32.5],     # Bottom calyx dimple center
    [6.0, -35.5],
    [12.0, -37.8],
    [18.5, -38.8],    # Bottom resting ring
    [26.0, -37.5],
    [33.0, -33.0],
    [39.0, -22.0],
    [42.8, -8.0],
    [43.5, 4.0],      # Max belly radius
    [42.2, 16.0],
    [38.5, 27.5],
    [32.5, 36.5],
    [24.5, 41.2],     # Top shoulder rim
    [16.5, 39.5],
    [9.0, 35.8],
    [3.5, 32.5],
    [0.0, 31.5]       # Top stem dimple center
])

# Inner profile (wall thickness ~2.8 - 3.2mm)
# Ensures PCB (W=50, Z from -22 to +28) and Battery (W=50, Z from -34 to -22) have ample space
inner_pts = np.array([
    [0.0, -29.0],
    [6.0, -32.0],
    [12.0, -34.2],
    [18.5, -35.2],
    [25.0, -34.0],
    [31.0, -30.0],
    [36.0, -20.0],
    [39.8, -7.0],
    [40.5, 4.0],
    [39.2, 15.0],
    [35.5, 26.0],
    [29.5, 34.0],
    [22.0, 37.8],
    [14.5, 36.2],
    [7.5, 33.0],
    [2.5, 30.5],
    [0.0, 29.8]
])

def gen_spline(pts, n=90):
    t = np.linspace(0, 1, len(pts))
    spl_r = interp.CubicSpline(t, pts[:, 0], bc_type='natural')
    spl_z = interp.CubicSpline(t, pts[:, 1], bc_type='natural')
    t_fine = np.linspace(0, 1, n)
    r = np.clip(spl_r(t_fine), 0, None)
    z = spl_z(t_fine)
    return [[round(float(ri), 2), round(float(zi), 2)] for ri, zi in zip(r, z)]

outer_fine = gen_spline(outer_pts, 80)
inner_fine = gen_spline(inner_pts, 80)

print("// Profile generated successfully")
print(f"Outer points: {len(outer_fine)}, Inner points: {len(inner_fine)}")
print(f"Outer Z min: {min(p[1] for p in outer_fine)}, max: {max(p[1] for p in outer_fine)}, R max: {max(p[0] for p in outer_fine)}")
print(f"Inner Z min: {min(p[1] for p in inner_fine)}, max: {max(p[1] for p in inner_fine)}, R max: {max(p[0] for p in inner_fine)}")

with open("scratch/apple_profiles.scad", "w") as f:
    f.write("// Auto-generated apple profile coordinates\n\n")
    f.write("apple_outer_profile = [\n")
    for p in outer_fine:
        f.write(f"  [{p[0]}, {p[1]}],\n")
    f.write("];\n\n")
    f.write("apple_inner_profile = [\n")
    for p in inner_fine:
        f.write(f"  [{p[0]}, {p[1]}],\n")
    f.write("];\n")
