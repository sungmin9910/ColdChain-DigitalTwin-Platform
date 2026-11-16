import os
import shutil
import subprocess
import time
import struct

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
v23_dir = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v23_Apple_Sensor_Pod_ActiveCoolingFan"
cq_dir = os.path.join(v23_dir, "cadquery_v23")
scad_file = os.path.join(v23_dir, "23_apple_sensor_pod_fan.scad")

def get_stl_bounds(path):
    with open(path, "rb") as f:
        header = f.read(80)
        count_bytes = f.read(4)
        if len(count_bytes) < 4:
            return None
        count = struct.unpack("<I", count_bytes)[0]
        if header.startswith(b"solid") and os.path.getsize(path) != 84 + count * 50:
            f.seek(0)
            xs, ys, zs = [], [], []
            for line in f:
                parts = line.strip().split()
                if len(parts) == 4 and parts[0] == b"vertex":
                    xs.append(float(parts[1]))
                    ys.append(float(parts[2]))
                    zs.append(float(parts[3]))
            return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
        else:
            xs, ys, zs = [], [], []
            for _ in range(count):
                data = f.read(50)
                vals = struct.unpack("<12fH", data)
                for i in (3, 6, 9):
                    xs.append(vals[i])
                    ys.append(vals[i+1])
                    zs.append(vals[i+2])
            return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

renders = [
    {
        "out": "23_front_shell_inside.png",
        "part": "part_front_shell",
        "cam": "0,0,5,65,0,0,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "23_fan_duct_zoom.png",
        "part": "part_front_shell",
        "cam": "25,5,5,60,0,325,140",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "23_rear_shell_cradle.png",
        "part": "part_rear_shell",
        "cam": "0,0,5,65,0,180,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    {
        "out": "23_assembly_view.png",
        "part": "assembly",
        "cam": "0,0,5,65,0,135,280",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    },
    {
        "out": "23_cross_section_view.png",
        "part": "cross_section",
        "cam": "0,0,5,65,0,45,280",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    },
    {
        "out": "23_exploded_view.png",
        "part": "exploded",
        "cam": "0,0,0,65,0,135,420",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    },
    {
        "out": "23_print_layout_view.png",
        "part": "print_all",
        "cam": "0,0,20,60,0,35,340",
        "size": "1024,1024",
        "scheme": "Cornfield"
    }
]

print("=== 1. Rendering v23 PNG Views ===")
for r in renders:
    out_path = os.path.join(v23_dir, r["out"])
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

print("\n=== 2. Exporting v23 Production STL Files ===")
stls = [
    ("23_apple_front_shell_fan.stl", "front_shell"),
    ("23_apple_rear_shell_fan.stl", "rear_shell"),
    ("23_apple_stem.stl", "stem"),
]
for stl_name, part_name in stls:
    stl_path = os.path.join(v23_dir, stl_name)
    t0 = time.time()
    print(f"Exporting {stl_name}...", end=" ", flush=True)
    res = subprocess.run([openscad, "-o", stl_path, "-D", f'render_part="{part_name}"', scad_file], capture_output=True, text=True)
    if res.returncode == 0:
        cq_stl = os.path.join(cq_dir, stl_name.replace(".stl", "_cq.stl"))
        if os.path.exists(cq_dir):
            shutil.copy2(stl_path, cq_stl)
        sz = os.path.getsize(stl_path) / 1024
        b = get_stl_bounds(stl_path)
        print(f"OK ({sz:.1f} KB, {time.time()-t0:.1f}s) | Bounds: X[{b[0]:.1f},{b[1]:.1f}] Y[{b[2]:.1f},{b[3]:.1f}] Z[{b[4]:.2f},{b[5]:.2f}]")
    else:
        print(f"FAILED!\n{res.stderr}")
