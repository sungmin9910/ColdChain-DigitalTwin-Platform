import os
import subprocess
import shutil

scad_file = r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\20_apple_sensor_pod.scad"

# Read original scad
with open(scad_file, "r", encoding="utf-8") as f:
    scad_code = f.read()

# Replace the scene composer section at the end of the file
marker = "// ==========================================\n// SCENE COMPOSER\n// =========================================="
base_code = scad_code.split(marker)[0]

new_scene_composer = r'''// ==========================================
// SCENE COMPOSER & ADVANCED VIEWS
// ==========================================

module pcb_assembly_mockup() {
    // CarrierBoard Substrate (Green)
    color([0.08, 0.55, 0.25, 0.95])
        cube([pcb_w, pcb_t, pcb_h], center=true);
        
    // Beetle C6 MCU (Front Face: +Y)
    color([0.15, 0.15, 0.15])
        translate([0, 5.0, 18.0 - pcb_z_center])
        cube([25.0, 10.0, 20.5], center=true);
        
    // BH1750 Light Sensor (Front-Right: +Y, -X)
    color([0.25, 0.55, 0.85])
        translate([-17.5, 7.5, 16.0 - pcb_z_center])
        cube([12.0, 12.0, 14.0], center=true);

    // GPS Patch Antenna (Rear Face: -Y)
    color([0.8, 0.75, 0.4])
        translate([0, -8.0, -10.0 - pcb_z_center])
        cube([25.0, 14.5, 25.0], center=true);

    // SHT45 Temp/Humidity Sensor (Rear-Left: -Y, +X)
    color([0.85, 0.25, 0.2])
        translate([17.0, -7.5, 16.0 - pcb_z_center])
        cube([12.0, 12.0, 14.0], center=true);
        
    // Corner M3 Mounting Holes Visualizer
    for (dx = [-1, 1]) {
        for (dz = [-1, 1]) {
            translate([dx * hole_pitch/2, 0, dz * hole_pitch/2])
                color([0.8, 0.8, 0.8])
                rotate([90, 0, 0])
                cylinder(r=1.6, h=pcb_t + 0.2, center=true);
        }
    }
}

if (render_part == "assembly") {
    apple_stem();
    color([0.88, 0.18, 0.18, 0.4]) apple_rear_shell();
    color([0.25, 0.72, 0.88, 0.7]) apple_battery_tray();
    color([0.88, 0.18, 0.18, 0.3]) apple_front_shell();
    hardware_mockup();
}
else if (render_part == "cross_section") {
    difference() {
        union() {
            apple_stem();
            color([0.88, 0.18, 0.18, 0.75]) apple_rear_shell();
            color([0.25, 0.72, 0.88, 0.9]) apple_battery_tray();
            color([0.88, 0.18, 0.18, 0.5]) apple_front_shell();
            hardware_mockup();
        }
        translate([70, 0, 0]) cube([140, 160, 160], center=true);
    }
}
// 1. WIDE EXPLODED VIEW (Ultra Clear Spacing along Y-axis)
else if (render_part == "exploded" || render_part == "exploded_wide") {
    // Alignment Guide Axis Lines
    for (pt = screw_pts) {
        translate([pt[0], 0, pt[1]])
            rotate([90, 0, 0])
            color([0.6, 0.7, 0.9, 0.35])
            cylinder(r=0.75, h=340, center=true);
    }
    
    // Layer 1: Rear Shell (Base Chassis)
    translate([0, -130, 0])
        color([0.88, 0.18, 0.18, 0.9])
        apple_rear_shell();
        
    // Layer 2: 5000mAh Battery Pouch
    translate([0, -65, bat_z_center])
        color([0.2, 0.45, 0.9, 0.95])
        cube([55.0, 10.0, 68.0], center=true);
        
    // Layer 3: Removable Battery Divider & PCB Standoff Tray
    translate([0, 0, 0])
        color([0.25, 0.75, 0.9, 0.95])
        apple_battery_tray();
        
    // Layer 4: CarrierBoard PCB Assembly with all 5 sensors
    translate([0, 65, pcb_z_center])
        pcb_assembly_mockup();
        
    // Layer 5: Front Shell Dome
    translate([0, 140, 0])
        color([0.88, 0.18, 0.18, 0.75])
        apple_front_shell();
        
    // Layer 6: Stem
    translate([0, 140, 24])
        apple_stem();
}
// 2. 2x3 GRID CATALOG LAYOUT (Inspection Workbench)
else if (render_part == "layout_catalog") {
    // Row 1 (Top: Z = +55)
    // Part 1: Rear Shell (Angled to see open battery bay)
    translate([-85, 0, 55])
        rotate([25, 45, -20])
        color([0.88, 0.18, 0.18])
        apple_rear_shell();
        
    // Part 2: 5000mAh Battery Pouch
    translate([0, 0, 55])
        rotate([0, 0, 0])
        color([0.2, 0.45, 0.9])
        cube([55.0, 10.0, 68.0], center=true);
        
    // Part 3: Removable Battery Divider Tray
    translate([85, 0, 55])
        rotate([25, 30, -10])
        color([0.25, 0.75, 0.9])
        apple_battery_tray();

    // Row 2 (Bottom: Z = -55)
    // Part 4: PCB Assembly with sensors
    translate([-85, 0, -55])
        rotate([15, 35, 0])
        pcb_assembly_mockup();
        
    // Part 5: Front Shell Dome
    translate([0, 0, -55])
        rotate([25, -45, 20])
        color([0.88, 0.18, 0.18, 0.85])
        apple_front_shell();
        
    // Part 6: Stem Accessory
    translate([85, 0, -55])
        scale([1.4, 1.4, 1.4])
        apple_stem();
}
// Individual Parts
else if (render_part == "part_rear_shell") {
    rotate([25, 40, -15])
    color([0.88, 0.18, 0.18])
    apple_rear_shell();
}
else if (render_part == "part_battery") {
    color([0.2, 0.45, 0.9])
    cube([55.0, 10.0, 68.0], center=true);
}
else if (render_part == "part_battery_tray") {
    rotate([25, 35, -15])
    color([0.25, 0.75, 0.9])
    apple_battery_tray();
}
else if (render_part == "part_pcb") {
    rotate([15, 35, 0])
    pcb_assembly_mockup();
}
else if (render_part == "part_front_shell") {
    rotate([25, -40, 15])
    color([0.88, 0.18, 0.18, 0.85])
    apple_front_shell();
}
else if (render_part == "rear_shell") {
    apple_rear_shell();
}
else if (render_part == "battery_tray") {
    rotate([90, 0, 0])
    translate([0, 21.5, -bat_z_center])
        apple_battery_tray();
}
else if (render_part == "front_shell") {
    apple_front_shell();
}
else if (render_part == "stem") {
    apple_stem();
}
else if (render_part == "print_all") {
    translate([-60, 0, 0]) rotate([90, 0, 0]) apple_rear_shell();
    translate([ 60, 0, 0]) rotate([-90, 0, 0]) apple_front_shell();
    translate([  0, 0, 0]) rotate([90, 0, 0]) translate([0, 21.5, -bat_z_center]) apple_battery_tray();
    translate([  0, 45, -35]) apple_stem();
}
'''

full_code = base_code + marker + "\n" + new_scene_composer

with open(scad_file, "w", encoding="utf-8") as f:
    f.write(full_code)

print("Updated 20_apple_sensor_pod.scad with wide exploded and layout views!")
