import scipy.interpolate as interp
import numpy as np

pts = np.array([
    [0.0, 7.0],
    [6.0, 4.0],
    [12.0, 1.2],
    [18.0, 0.0],
    [25.0, 1.2],
    [32.0, 6.0],
    [38.0, 15.0],
    [42.0, 28.0],
    [43.5, 42.0],
    [42.5, 54.0],
    [39.5, 64.0],
    [33.5, 73.0],
    [25.0, 78.5],
    [17.0, 77.0],
    [9.0, 73.0],
    [3.5, 69.0],
    [0.0, 68.0]
])

# Spline interpolation
t = np.linspace(0, 1, len(pts))
spl_r = interp.CubicSpline(t, pts[:, 0], bc_type='natural')
spl_z = interp.CubicSpline(t, pts[:, 1], bc_type='natural')

t_fine = np.linspace(0, 1, 80)
r_fine = spl_r(t_fine)
z_fine = spl_z(t_fine)

# Ensure r >= 0
r_fine = np.clip(r_fine, 0, None)
# Center at Z=0 for convenience
z_mid = (z_fine.max() + z_fine.min()) / 2.0
z_fine_centered = z_fine - z_mid

scad_pts = [[round(r, 2), round(z, 2)] for r, z in zip(r_fine, z_fine_centered)]
print(f"// Apple Profile Points (N={len(scad_pts)}):")
print("apple_profile = [")
for p in scad_pts:
    print(f"  [{p[0]}, {p[1]}],")
print("];")
