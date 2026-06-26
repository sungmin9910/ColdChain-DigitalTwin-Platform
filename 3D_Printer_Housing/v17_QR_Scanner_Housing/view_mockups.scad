// view_mockups.scad - Visualization showcase for component mockups

use <hardware_mockups.scad>

// View Modes: 
// "components" - Standalone component library layout
// "assembly"   - Unified 3D assembly layout
// "both"       - Renders both layouts side-by-side
view_mode = "both"; 

// --- Coordinates for the assembly layout ---
head_w = 64.0;
head_h = 48.0;
neck_y = 75.0;
wall   = 2.5;
handle_angle = 25;
handle_h     = 105.0;

gm77_pos    = [head_w/2, 30.0, 24.0];
esp32_pos   = [head_w/2, 112.0, 6.0];  // Updated for ESP32 rear wall alignment
oled_pos    = [head_w/2, 124.0, 25.0];  // Updated for extended head length Y=140.0
oled_bevel_angle = 55;

// Local coordinates in the handle (Y=0 aligned, switch at X=-14.5, trigger at Y=-14)
bat_local_pos    = [3.0, 0, -45.0];
chg_local_pos    = [0, 0, -handle_h + 13.75];
boost_local_pos  = [-12.0, 0, -45.0];
switch_local_pos = [-14.5, 0, -handle_h + 16.0];
trigger_local_pos= [0, -14.0, -22.0];

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
// 2. Unified 3D System Assembly Layout
// ----------------------------------------------------
module render_system_assembly() {
    // 1. GM77 Scanner
    translate(gm77_pos) gm77_scanner_mockup();
    
    // 2. ESP32 DevKitC V4 (Flipped)
    translate(esp32_pos) rotate([180, 0, 0]) esp32_devkitc_mockup();
    
    // 3. SSD1306 OLED (Slanted at 55 deg)
    translate(oled_pos) rotate([oled_bevel_angle, 0, 180]) ssd1306_oled_mockup();
    
    // 4. Handle elements (undergoing rotation to match grip)
    translate([head_w/2, neck_y, wall])
    rotate([handle_angle, 0, 0]) {
        // Battery
        translate(bat_local_pos) rotate([-90, 0, 0]) battery_18650_wire();
        
        // Charger Module TP4056
        translate(chg_local_pos) rotate([90, 0, 90]) charger_module_tp4056();
        
        // Booster VLT-VC013 (side-by-side with battery, fixed rotation [90, 0, 90])
        translate(boost_local_pos) rotate([90, 0, 90]) booster_module_vlt_vc013();
        
        // Slide Switch
        translate(switch_local_pos) rotate([0, -90, 0]) slide_switch_msl_1c2p();
        
        // Tact Trigger Switch
        translate(trigger_local_pos) rotate([90, 0, 0]) tact_switch_h11();
    }
}

// ----------------------------------------------------
// Main Render Pipeline
// ----------------------------------------------------
if (view_mode == "components") {
    translate([-45, -15, 0]) render_standalone_grid();
} else if (view_mode == "assembly") {
    render_system_assembly();
} else if (view_mode == "both") {
    translate([-60, -15, 0]) render_standalone_grid();
    translate([80, 50, 0]) render_system_assembly();
}
