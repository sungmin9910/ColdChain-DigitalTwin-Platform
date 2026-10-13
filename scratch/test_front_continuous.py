import subprocess

test_scad = r'''
$fn = 64;

apple_outer_profile = [
  [  0.00, -37.32], [  1.15, -38.01], [  2.41, -38.70], [  3.79, -39.39],
  [  5.17, -40.08], [  6.66, -40.65], [  8.27, -41.34], [  9.88, -42.03],
  [ 11.60, -42.60], [ 13.44, -43.18], [ 15.39, -43.75], [ 17.46, -44.10],
  [ 19.52, -44.44], [ 21.70, -44.56], [ 24.00, -44.44], [ 26.18, -44.21],
  [ 28.36, -43.64], [ 30.55, -42.83], [ 32.61, -41.80], [ 34.68, -40.54],
  [ 36.63, -38.93], [ 38.47, -37.09], [ 40.31, -34.91], [ 41.92, -32.61],
  [ 43.52, -29.97], [ 44.90, -27.10], [ 46.16, -24.00], [ 47.20, -20.67],
  [ 48.12, -17.23], [ 48.81, -13.67], [ 49.38,  -9.99], [ 49.84,  -6.20],
  [ 49.95,  -2.41], [ 50.00,   1.38], [ 49.84,   5.05], [ 49.49,   8.73],
  [ 49.04,  12.29], [ 48.35,  15.73], [ 47.43,  18.95], [ 46.39,  22.16],
  [ 45.25,  25.15], [ 43.87,  28.02], [ 42.37,  30.78], [ 40.77,  33.42],
  [ 39.04,  35.83], [ 37.09,  38.13], [ 35.14,  40.31], [ 32.96,  42.26],
  [ 30.66,  43.98], [ 28.25,  45.48], [ 25.72,  46.51], [ 23.20,  47.20],
  [ 20.67,  47.31], [ 18.14,  46.85], [ 15.73,  46.05], [ 13.44,  44.79],
  [ 11.25,  43.41], [  9.19,  41.80], [  7.35,  40.31], [  5.63,  38.93],
  [  4.13,  37.90], [  2.76,  37.09], [  1.49,  36.52], [  0.00,  36.17]
];

apple_inner_profile = [
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
];

module apple_solid_outer() {
    rotate_extrude(angle=360, $fn=72)
        polygon(concat([[0, apple_outer_profile[0][1]]], apple_outer_profile, [[0, apple_outer_profile[len(apple_outer_profile)-1][1]]]));
}

module apple_solid_inner() {
    rotate_extrude(angle=360, $fn=72)
        polygon(concat([[0, apple_inner_profile[0][1]]], apple_inner_profile, [[0, apple_inner_profile[len(apple_inner_profile)-1][1]]]));
}

screw_pts = [
    [-35.0,  26.0],
    [ 35.0,  26.0],
    [-34.0, -23.0],
    [ 34.0, -23.0]
];

module continuous_wall_boss_front() {
    for (pt = screw_pts) {
        norm_len = sqrt(pt[0]*pt[0] + pt[1]*pt[1]);
        dir_x = pt[0] / norm_len;
        dir_z = pt[1] / norm_len;
        
        translate([pt[0], 0, pt[1]]) {
            rotate([-90, 0, 0]) {
                difference() {
                    hull() {
                        cylinder(r=5.2, h=42.0);
                        translate([dir_x * 12.0, dir_z * 12.0, 0])
                            cylinder(r=5.0, h=42.0);
                    }
                    // M3 clearance through-hole
                    translate([0, 0, -1])
                        cylinder(r=1.7, h=44.0);
                    // M3 screw head counterbore from outer surface
                    // Note: In front_shell, the screw enters from the front (Y > 0).
                    // In rotate([-90, 0, 0]), Z=0 is Y=0 (parting plane).
                    // So outer skin is at the end of the cylinder (Z=something) or wait!
                    // Let's check how counterbore was positioned!
                }
            }
        }
    }
}

module test_front_shell() {
    difference() {
        intersection() {
            apple_solid_outer();
            union() {
                difference() {
                    intersection() {
                        apple_solid_outer();
                        translate([0, 70, 0]) cube([140, 140, 140], center=true);
                    }
                    intersection() {
                        apple_solid_inner();
                        translate([0, 70, 0]) cube([140, 140, 140], center=true);
                    }
                }
                
                continuous_wall_boss_front();
            }
        }
    }
}

test_front_shell();
'''

with open("scratch/test_front_continuous.scad", "w") as f:
    f.write(test_scad)

cmd_front = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/test_front_continuous_full.png",
    "--camera", "0,0,0,65,0,30,240",
    "--imgsize", "800,800",
    "--colorscheme", "Cornfield",
    "scratch/test_front_continuous.scad"
]
subprocess.run(cmd_front)
print("Rendered front continuous full")
