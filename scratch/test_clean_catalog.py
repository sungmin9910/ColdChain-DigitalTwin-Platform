import subprocess

scad_content = r'''
$fn = 64;
include <../3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_apple_sensor_pod.scad>

module clean_catalog() {
    // Row 1 (Top: Z = +55)
    // 1. Rear Shell (Facing +Y, tilted slightly back 15 deg to clearly see battery bay)
    translate([-90, 0, 55])
        rotate([-15, 0, 0])
        color([0.88, 0.18, 0.18])
        apple_rear_shell();
        
    // 2. Battery Pouch (5000mAh)
    translate([0, 0, 55])
        rotate([-15, 0, 0])
        color([0.2, 0.45, 0.9])
        cube([55.0, 10.0, 68.0], center=true);
        
    // 3. Battery Tray (Divider + 4 Standoffs pointing toward viewer)
    translate([90, 0, 55])
        rotate([-15, 0, 0])
        color([0.25, 0.75, 0.9])
        apple_battery_tray();

    // Row 2 (Bottom: Z = -55)
    // 4. PCB Assembly (CarrierBoard + 5 Sensors facing viewer)
    translate([-90, 0, -55])
        rotate([-15, 0, 0])
        pcb_assembly_mockup();
        
    // 5. Front Shell (Outer dome & cutouts facing viewer)
    translate([0, 0, -55])
        rotate([165, 0, 0])
        color([0.88, 0.18, 0.18, 0.9])
        apple_front_shell();
        
    // 6. Apple Stem
    translate([90, 0, -65])
        scale([1.5, 1.5, 1.5])
        apple_stem();
}

clean_catalog();
'''

with open('scratch/test_clean_catalog.scad', 'w', encoding='utf-8') as f:
    f.write(scad_content)

cmd = [
    r"C:\Program Files\OpenSCAD\openscad.com",
    "-o", r"C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520\scratch\test_clean_catalog.png",
    "--camera", "0,0,0,0,0,180,680",
    "--imgsize", "1200,1200",
    "--colorscheme", "Tomorrow Night",
    "scratch/test_clean_catalog.scad"
]
subprocess.run(cmd)
print("Rendered test_clean_catalog.png")
