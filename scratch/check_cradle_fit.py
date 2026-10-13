# Let's inspect the exact intersection of the battery cradle and the shell wall
# In 20_apple_sensor_pod.scad:
# apple_rear_shell():
# difference() {
#   intersection() {
#     apple_solid_outer();
#     union() {
#       difference() {
#         intersection() { apple_solid_outer(); translate([0,-70,0]) cube([140,140,140], center=true); }
#         intersection() { apple_solid_inner(); translate([0,-70,0]) cube([140,140,140], center=true); }
#       }
#       cradle:
#         translate([0, bat_y_center, bat_z_center]) {
#           difference() {
#             cube([bat_w + 4.5, bat_t + 10.0, bat_h + 4.5], center=true);
#             ...
#           }
#         }
#       bosses:
#         ...
#     }
#   }
# }

# Notice:
# bat_y_center = -28.5
# bat_w = 58.0 (+4.5 -> 62.5, X in [-31.25, 31.25])
# bat_t = 12.0 (+10.0 -> 22.0, Y in [-39.5, -17.5])
# bat_h = 73.0 (+4.5 -> 77.5, Z in [-36.75, 40.75])
#
# Inner shell cavity at (X, Y, Z):
# Let's calculate the distance between cradle surfaces and the inner shell surface!

import math

inner_profile = [
  [  0.00, -33.30], [  1.15, -33.99], [  2.41, -34.68], [  3.79, -35.25],
  [  5.28, -35.94], [  6.89, -36.63], [  8.61, -37.32], [ 10.45, -38.01],
  [ 12.29, -38.59], [ 14.24, -39.16], [ 16.31, -39.62], [ 18.49, -39.96],
  [ 20.79, -40.19], [ 23.08, -40.31], [ 25.38, -40.08], [ 27.56, -39.62],
  [ 29.74, -38.93], [ 31.69, -38.01], [ 33.65, -36.86], [ 35.37, -35.48],
  [ 37.09, -33.76], [ 38.59, -31.92], [ 39.96, -29.86], [ 41.23, -27.56],
  [ 42.37, -25.03], [ 43.41, -22.39], [ 44.21, -19.52], [ 44.90, -16.54],
  [ 45.48, -13.44], [ 45.93, -10.22], [ 46.28,  -7.01], [ 46.51,  -3.67],
  [ 46.62,  -0.34], [ 46.58,   2.99], [ 46.28,   6.20], [ 45.93,   9.42],
  [ 45.36,  12.52], [ 44.56,  15.50], [ 43.64,  18.49], [ 42.60,  21.24],
  [ 41.34,  23.89], [ 39.96,  26.41], [ 38.36,  28.82], [ 36.63,  31.01],
  [ 34.91,  33.07], [ 32.96,  35.03], [ 30.89,  36.75], [ 28.71,  38.36],
  [ 26.53,  39.73], [ 24.23,  40.88], [ 21.82,  41.80], [ 19.41,  42.37],
  [ 17.00,  42.60], [ 15.85,  42.49], [ 12.52,  41.92], [ 10.34,  41.00],
  [  8.38,  39.85], [  6.55,  38.59], [  4.94,  37.32], [  3.56,  36.29],
  [  2.30,  35.48], [  1.15,  34.80], [  0.00,  34.22]
]

def get_r_inner(z):
    for i in range(len(inner_profile)-1):
        r1, z1 = inner_profile[i]
        r2, z2 = inner_profile[i+1]
        if min(z1, z2) <= z <= max(z1, z2):
            t = (z - z1) / (z2 - z1)
            return r1 + t * (r2 - r1)
    return 0

# Check bottom of cradle: Z = -36.75
# At Z = -36.75:
r_in_bottom = get_r_inner(-36.75)
print(f"At bottom of cradle Z = -36.75: R_inner = {r_in_bottom:.2f} mm")
# At X = 0, inner cavity Y is at -sqrt(R^2 - 0) = -r_in_bottom = -10.0 mm??
# Wait! In inner_profile, at Z = -36.75:
# Look at [6.89, -36.63] and [8.61, -37.32]!
# At Z = -36.75, R is only ~ 7.2 mm!
# And the cradle width is X = [-31.25, 31.25]!
# For X > 7.2 mm, there is NO CAVITY AT ALL at Z = -36.75!
# The bottom of the apple ends at Z = -33.3 at center, and drops to Z = -40 at R=23!

print("Let's check various Z levels along the cradle:")
for z in [-36.75, -30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0, 40.75]:
    r = get_r_inner(z)
    print(f"  Z = {z:6.2f}: R_inner = {r:5.2f} mm")
