// view_mockups.scad - Visualization showcase for component mockups and 3D wiring harness

use <hardware_mockups.scad>

// View Modes: 
// "components" - Standalone component library layout
// "wiring"     - Unified 3D wiring diagram layout
// "both"       - Renders both layouts side-by-side
view_mode = "both"; 

// ----------------------------------------------------
// A. Virtual Assembly Coordinates for the 3D Wiring System
// ----------------------------------------------------
// These coordinates align the components in 3D space to simulate the physical handheld scanner assembly.

esp32_pos   = [0, 80, 5.0];          // Flipped (pin-up) near the scanner head ceiling
oled_pos    = [0, 110, 35.0];        // User-facing display on rear face
gm77_pos    = [0, 30, 8.0];          // Front scanner pocket
bat_pos     = [0, 50, -35.0];        // Inside the handle grip (oriented vertically)
chg_pos     = [0, 50, -70.0];        // Bottom charger tray
switch_pos  = [-12, 50, -68.0];      // Slide switch on handle base side
boost_pos   = [0, 50, -10.0];        // Main power distribution center
trigger_pos = [0, 35, -20.0];        // Pistol trigger button inside the grip

// ----------------------------------------------------
// 1. Standalone Components Layout Grid
// ----------------------------------------------------
module render_standalone_grid() {
    spacing_x = 45;
    spacing_y = 65;
    
    // Row 1: Core Electronics
    // Col 1: ESP32 DevKitC
    translate([0, spacing_y, 0]) {
        esp32_devkitc_mockup();
        translate([0, -32, 0]) render_3d_text("ESP32 DevKitC V4");
    }
    // Col 2: SSD1306 OLED
    translate([spacing_x, spacing_y, 0]) {
        ssd1306_oled_mockup();
        translate([0, -20, 0]) render_3d_text("SSD1306 OLED");
    }
    // Col 3: GM77 Scanner
    translate([spacing_x * 2, spacing_y, 0]) {
        gm77_scanner_mockup();
        translate([0, -30, 0]) render_3d_text("GM77 Scanner");
    }
    
    // Row 2: Power and Switches
    // Col 1: 18650 Battery
    translate([0, 0, 0]) {
        battery_18650_wire();
        translate([0, -38, 0]) render_3d_text("18650 Li-ion");
    }
    // Col 2: TP4056 USB-C Charger
    translate([spacing_x, 0, 0]) {
        charger_module_tp4056();
        translate([0, -18, 0]) render_3d_text("TP4056 Charger");
    }
    // Col 3: VLT-VC013 Booster
    translate([spacing_x * 2, 0, 0]) {
        booster_module_vlt_vc013();
        translate([0, -15, 0]) render_3d_text("VLT-VC013 Booster");
    }
    
    // Row 3: Mechanical Buttons
    // Col 1: MSL-1C2P Slide Switch
    translate([spacing_x/2, -spacing_y/2 - 10, 0]) {
        slide_switch_msl_1c2p();
        translate([0, -8, 0]) render_3d_text("Slide Switch");
    }
    // Col 2: AK-TS-I015-42 Tact Switch
    translate([spacing_x * 1.5, -spacing_y/2 - 10, 0]) {
        tact_switch_h11();
        translate([0, -8, 0]) render_3d_text("H11 Tact Switch");
    }
}

// Helper module to render 3D labels
module render_3d_text(t) {
    color([0.8, 0.8, 0.8])
        linear_extrude(height=1.0)
            text(t, size=3.0, halign="center", valign="center", font="Liberation Sans:style=Bold");
}

// ----------------------------------------------------
// 2. Unified 3D System Wiring Diagram Layout
// ----------------------------------------------------
module render_system_wiring_assembly() {
    // A. Components Placement (Aligned to coordinate guide)
    
    // ESP32 DevKitC (Flipped 180 deg, pin headers face up +Z)
    translate(esp32_pos) rotate([180, 0, 0]) esp32_devkitc_mockup();
    
    // SSD1306 OLED (Rear face display, pins face up)
    translate(oled_pos) rotate([90, 0, 180]) ssd1306_oled_mockup();
    
    // GM77 Scanner (Front face window pointing -Y)
    translate(gm77_pos) gm77_scanner_mockup();
    
    // 18650 Battery (Vertical orientation inside handle)
    translate(bat_pos) rotate([90, 0, 0]) battery_18650_wire();
    
    // TP4056 Charger (Bottom tray)
    translate(chg_pos) charger_module_tp4056();
    
    // Slide Switch (Handle base side mount)
    translate(switch_pos) rotate([0, 90, 90]) slide_switch_msl_1c2p();
    
    // VLT-VC013 Booster (Midsection distribution hub)
    translate(boost_pos) booster_module_vlt_vc013();
    
    // Tact Trigger Switch (Grip trigger slot)
    translate(trigger_pos) rotate([0, 90, 90]) tact_switch_h11();
    
    // B. Draw System Wiring harness connecting the points
    scanner_system_wiring(
        esp32_pos = esp32_pos,
        oled_pos = oled_pos,
        gm77_pos = gm77_pos,
        bat_pos = bat_pos,
        chg_pos = chg_pos,
        switch_pos = switch_pos,
        boost_pos = boost_pos,
        trigger_pos = trigger_pos
    );
}

// ----------------------------------------------------
// Main Render Pipeline
// ----------------------------------------------------
if (view_mode == "components") {
    // Center view for standalone components library
    translate([-45, -15, 0]) render_standalone_grid();
} else if (view_mode == "wiring") {
    // System wiring layout
    render_system_wiring_assembly();
} else if (view_mode == "both") {
    // Render both side-by-side (Standalone on the left, wired assembly on the right)
    translate([-60, -15, 0]) render_standalone_grid();
    translate([80, 50, 0]) render_system_wiring_assembly();
}
