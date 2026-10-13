import os
import subprocess
import time
import shutil

openscad = r"C:\Program Files\OpenSCAD\openscad.com"
v21_dir = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v21_Apple_Sensor_Pod_2Piece5000mAh"
artifact_dir = r"C:\Users\korea\.gemini\antigravity-ide\brain\139db524-fcfc-4f20-aaa2-e61762915e57"
scad_file = os.path.join(v21_dir, "21_apple_sensor_pod.scad")

print("=== 1. Rendering Updated 3D Visualization PNGs ===")

renders = [
    # 1. Front Face View (Shows all 8 front-accessible screw holes clearly!)
    {
        "out": "21_front_face_view.png",
        "part": "part_front_shell",
        "cam": "0,0,3,90,0,180,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    # 2. Assembled Pod Front-Quarter View (Looking at front dome with screws & windows)
    {
        "out": "21_assembly_view.png",
        "part": "assembly",
        "cam": "0,0,5,65,0,215,280",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    },
    # 3. Cross-Section (Reveals screws passing from front dome through standoffs into PCB)
    {
        "out": "21_cross_section_view.png",
        "part": "cross_section",
        "cam": "0,0,5,65,0,45,280",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    },
    # 4. Front Shell Interior (4x Standoffs with Through-Holes & anti-overhang gussets)
    {
        "out": "21_front_shell_inside.png",
        "part": "part_front_shell",
        "cam": "0,0,5,65,0,0,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    # 5. Rear Shell Interior (Drop-in Battery Cradle with Retention Lips)
    {
        "out": "21_rear_shell_cradle.png",
        "part": "part_rear_shell",
        "cam": "0,0,5,65,0,180,220",
        "size": "1024,1024",
        "scheme": "Cornfield"
    },
    # 6. Exploded Architecture View
    {
        "out": "21_exploded_view.png",
        "part": "exploded_wide",
        "cam": "0,0,0,60,0,215,680",
        "size": "1200,1200",
        "scheme": "Tomorrow Night"
    },
    # 7. Print Bed Layout (Ready for 3DWOX 2X)
    {
        "out": "21_print_layout_view.png",
        "part": "print_all",
        "cam": "0,0,0,65,0,40,350",
        "size": "1024,1024",
        "scheme": "Tomorrow Night"
    }
]

for r in renders:
    out_path = os.path.join(v21_dir, r["out"])
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
        shutil.copy2(out_path, os.path.join(artifact_dir, r["out"]))
    else:
        print(f"FAILED!\n{res.stderr}")

print("\n=== 2. Re-exporting 21_apple_front_shell.stl ===")
front_stl = os.path.join(v21_dir, "21_apple_front_shell.stl")
t0 = time.time()
res = subprocess.run([openscad, "-o", front_stl, "-D", 'render_part="front_shell"', scad_file], capture_output=True, text=True)
if res.returncode == 0:
    sz = os.path.getsize(front_stl) / 1024
    print(f"Exported 21_apple_front_shell.stl ({sz:.1f} KB, {time.time()-t0:.1f}s)")
else:
    print(f"STL Export Failed:\n{res.stderr}")

print("\nAll updated renders and front STL export finished!")
