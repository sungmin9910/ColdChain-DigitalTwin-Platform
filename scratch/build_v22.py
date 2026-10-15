import os
import subprocess
import time

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
v22_dir = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v22_Apple_Sensor_Pod_Magnetic5000mAh"
scad_file = os.path.join(v22_dir, "22_apple_sensor_pod.scad")

renders = [
    {
        "out": "22_front_shell_inside.png",
        "part": "part_front_shell",
        "cam": "0,0,5,65,0,0,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "22_gps_and_magnet_zoom.png",
        "part": "part_front_shell",
        "cam": "-25,5,5,60,0,35,140",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "22_rear_shell_cradle.png",
        "part": "part_rear_shell",
        "cam": "0,0,5,65,0,180,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "22_bh1750_window_view.png",
        "part": "part_rear_shell",
        "cam": "20,-10,-15,75,0,125,160",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "22_front_face_view.png",
        "part": "part_front_shell",
        "cam": "0,0,3,90,0,180,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "22_assembly_view.png",
        "part": "assembly",
        "cam": "0,0,5,65,0,215,280",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    },
    {
        "out": "22_cross_section_view.png",
        "part": "cross_section",
        "cam": "0,0,5,65,0,45,280",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    },
    {
        "out": "22_exploded_view.png",
        "part": "exploded",
        "cam": "0,0,0,65,0,215,420",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    }
]

print("=== 1. Rendering v22 PNG Views ===")
for r in renders:
    out_path = os.path.join(v22_dir, r["out"])
    cmd = [
        openscad,
        "-o", out_path,
        "-D", f'render_part="{r["part"]}"',
        "--camera", r["cam"],
        "--imgsize", r["size"],
        "--colorscheme", r["scheme"],
        scad_file
    ]
    t0 = time.time()
    print(f"Rendering {r['out']}...", end=" ", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"OK ({time.time()-t0:.1f}s)")
    else:
        print(f"FAILED!\n{res.stderr}")

print("\n=== 2. Exporting v22 Production STL Files ===")
stls = [
    ("22_apple_front_shell.stl", "front_shell"),
    ("22_apple_rear_shell.stl", "rear_shell"),
    ("22_apple_stem.stl", "stem"),
]
for stl_name, part_name in stls:
    stl_path = os.path.join(v22_dir, stl_name)
    t0 = time.time()
    print(f"Exporting {stl_name}...", end=" ", flush=True)
    res = subprocess.run([openscad, "-o", stl_path, "-D", f'render_part="{part_name}"', scad_file], capture_output=True, text=True)
    if res.returncode == 0:
        sz = os.path.getsize(stl_path) / 1024
        print(f"OK ({sz:.1f} KB, {time.time()-t0:.1f}s)")
    else:
        print(f"FAILED!\n{res.stderr}")
