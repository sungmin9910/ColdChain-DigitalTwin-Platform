import subprocess

cmd_front_face = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", "scratch/test_front_face.png",
    "--camera", "0,0,0,65,0,30,240",
    "--imgsize", "800,800",
    "--colorscheme", "Cornfield",
    "scratch/test_front_counterbore.scad"
]
subprocess.run(cmd_front_face)
print("Rendered front face")
