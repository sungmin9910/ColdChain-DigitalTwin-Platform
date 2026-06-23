// hardware_mockups.scad - Reusable 3D hardware component drawings & wiring library
// Target components: ESP32 DevKitC V4, SSD1306 OLED, GM77 Scanner, TP4056, VLT-VC013, MSL-1C2P, AK-TS-I015-42, 18650 Battery.

$fn = 16;

// ==========================================
// 1. WIRING HELPERS & UTILITIES
// ==========================================

// Draw a round wire segment between two 3D points
module wire_segment(p1, p2, radius=0.5) {
    hull() {
        translate(p1) sphere(r=radius, $fn=8);
        translate(p2) sphere(r=radius, $fn=8);
    }
}

// Draw a multi-segment routed wire path
module wire_path(points, radius=0.5) {
    for (i = [0 : len(points) - 2]) {
        wire_segment(points[i], points[i+1], radius);
    }
}

// ==========================================
// 2. HARDWARE COMPONENT DRAWINGS
// ==========================================

// A. ESP32 DevKitC V4 (Size: 28.2 x 54.4 x 1.6 mm PCB)
module esp32_devkitc_mockup() {
    pcb_w = 28.2;
    pcb_l = 54.4;
    pcb_h = 1.6;
    
    // PCB Base
    color("DarkGreen") 
        difference() {
            cube([pcb_w, pcb_l, pcb_h], center=true);
            // Mounting holes (4 corners)
            for (x = [-11.5, 11.5], y = [-24.0, 24.0]) {
                translate([x, y, 0]) cylinder(h=pcb_h*2, d=2.0, center=true);
            }
        }
        
    // ESP32-WROOM-32E Shield Can (Metal cover)
    translate([0, 5.0, pcb_h/2 + 1.5]) {
        color("Silver") cube([18.0, 25.5, 3.0], center=true);
        // Antena PCB region (black)
        translate([0, 12.75 + 3.0, -0.7]) 
            color([0.15, 0.15, 0.15]) cube([18.0, 6.0, 1.6], center=true);
    }
    
    // Micro-USB Port (front side)
    translate([0, -pcb_l/2 + 2.5, pcb_h/2 + 1.5])
        color("LightGray") cube([7.5, 5.5, 3.0], center=true);
        
    // Boot & EN push buttons
    translate([-7.0, -pcb_l/2 + 4.0, pcb_h/2 + 1.0]) {
        color("Silver") cube([3.5, 3.5, 2.0], center=true);
        color("Black") translate([0,0,1.0]) cylinder(h=1.0, d=1.8, center=true);
    }
    translate([7.0, -pcb_l/2 + 4.0, pcb_h/2 + 1.0]) {
        color("Silver") cube([3.5, 3.5, 2.0], center=true);
        color("Black") translate([0,0,1.0]) cylinder(h=1.0, d=1.8, center=true);
    }
    
    // Pin Headers (Male pins pointing downwards, or upwards if flipped)
    color("Black") {
        translate([-pcb_w/2 + 1.27, 0, -pcb_h/2 - 1.25]) cube([2.54, pcb_l - 4, 2.5], center=true);
        translate([pcb_w/2 - 1.27, 0, -pcb_h/2 - 1.25]) cube([2.54, pcb_l - 4, 2.5], center=true);
    }
    color("Gold") {
        for (y = [-23.0 : 2.54 : 23.0]) {
            translate([-pcb_w/2 + 1.27, y, -pcb_h/2 - 4.5]) cylinder(h=6.0, d=0.64, center=true);
            translate([pcb_w/2 - 1.27, y, -pcb_h/2 - 4.5]) cylinder(h=6.0, d=0.64, center=true);
        }
    }
}

// B. SSD1306 OLED Module (0.96 inch, Size: 27.3 x 27.3 x 1.2 mm PCB)
module ssd1306_oled_mockup() {
    oled_w = 27.3;
    oled_l = 27.3;
    oled_h = 1.2;
    
    // PCB Base
    color("RoyalBlue")
        difference() {
            cube([oled_w, oled_l, oled_h], center=true);
            // 4 corner mount holes
            for (x = [-11.0, 11.0], y = [-11.0, 11.0]) {
                translate([x, y, 0]) cylinder(h=oled_h*3, d=2.0, center=true);
            }
        }
        
    // OLED Glass Screen (Active area centered)
    translate([0, -2.0, oled_h/2 + 0.8]) {
        color([0.05, 0.05, 0.05]) cube([26.0, 16.0, 1.6], center=true);
        // Active Display pixels (light cyan mockup screen)
        translate([0, 0, 0.81]) 
            color("Cyan") cube([21.8, 11.0, 0.01], center=true);
    }
    
    // I2C 4-Pin Header (GND, VCC, SCL, SDA) at the top edge (+Y)
    translate([0, oled_l/2 - 2.0, -oled_h/2 - 1.25]) {
        color("Black") cube([10.16, 2.54, 2.5], center=true);
        color("Gold") {
            for (x = [-3.81 : 2.54 : 3.81]) {
                translate([x, 0, -3.0]) cylinder(h=6.0, d=0.64, center=true);
            }
        }
    }
}

// C. GM77 Barcode & QR Code Scanner Module (Size: 27.5 x 48.5 x 14.0 mm)
module gm77_scanner_mockup() {
    s_w = 27.5;
    s_l = 48.5;
    s_h = 14.0;
    
    // Main Casing (Metallic dark grey housing)
    color([0.25, 0.25, 0.27])
        difference() {
            cube([s_w, s_l, s_h], center=true);
            // Beveled corners at front-lens end (-Y side)
            translate([-s_w/2, -s_l/2, 0]) rotate([0, 0, 45]) cube([6.0, 6.0, s_h + 1], center=true);
            translate([s_w/2, -s_l/2, 0]) rotate([0, 0, -45]) cube([6.0, 6.0, s_h + 1], center=true);
        }
        
    // Scanner Lens Window (front face, -Y side)
    translate([0, -s_l/2 + 0.2, 0]) {
        color("Black") cube([20.0, 0.5, 8.0], center=true);
        // Glass Lens
        translate([0, -0.1, 0]) 
            color("Cyan", 0.6) cube([14.0, 0.4, 6.0], center=true);
        // Status LED indicators
        translate([-8.0, -0.2, 3.0]) color("Green") sphere(r=0.6);
        translate([8.0, -0.2, 3.0]) color("Red") sphere(r=0.6);
    }
    
    // Bottom PCB and mounting tab details
    translate([0, 0, -s_h/2 + 0.5]) {
        color("DarkGreen") cube([s_w - 2.0, s_l - 2.0, 1.0], center=true);
        // Gold mounting holes on the base PCB
        color("Gold") {
            for (x = [-10.0, 10.0], y = [-20.0, 20.0]) {
                translate([x, y, -0.5]) cylinder(h=1.2, d=2.0, center=true);
            }
        }
    }
}

// D. Voltly VLT-VC013 DC-DC Boost Module (Size: 22.0 x 11.0 x 3.6 mm)
module booster_module_vlt_vc013() {
    b_w = 11.0;
    b_l = 22.0;
    b_h = 1.2;
    
    // PCB (Blue/Teal)
    color([0.0, 0.4, 0.4]) cube([b_w, b_l, b_h], center=true);
    
    // Inductor block (grey)
    translate([0, -3.0, b_h/2 + 1.2])
        color("DimGray") cube([6.0, 6.0, 2.4], center=true);
        
    // Boost Controller IC & diodes
    translate([0, 4.0, b_h/2 + 0.5])
        color("Black") cube([4.0, 3.0, 1.0], center=true);
        
    // Solder pads (Gold, 4 corners)
    color("Gold") {
        // IN+ (bottom left), IN- (bottom right)
        translate([-b_w/2 + 1.5, -b_l/2 + 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([b_w/2 - 1.5, -b_l/2 + 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        // OUT+ (top left), OUT- (top right)
        translate([-b_w/2 + 1.5, b_l/2 - 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([b_w/2 - 1.5, b_l/2 - 1.5, b_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
    }
}

// E. TP4056 USB-C Li-ion Charger Module [SZH-LIP001] (Size: 27.5 x 16.5 x 4.0 mm)
module charger_module_tp4056() {
    c_w = 16.5;
    c_l = 27.5;
    c_h = 1.2;
    
    // PCB (Dark Blue)
    color([0.0, 0.1, 0.5]) cube([c_w, c_l, c_h], center=true);
    
    // USB-C Connector (metal) - overhangs front slightly (-Y side)
    translate([0, -c_l/2 + 4.0, c_h/2 + 1.6])
        color("LightGray") cube([9.0, 6.5, 3.2], center=true);
        
    // TP4056 chip (SOIC-8, black)
    translate([-3.0, 3.0, c_h/2 + 0.5])
        color("Black") cube([4.0, 5.0, 1.0], center=true);
        
    // DW01 Protection chip (SOT-23-6) & Mosfets
    translate([3.0, 3.0, c_h/2 + 0.5])
        color("Black") cube([3.0, 3.0, 1.0], center=true);
        
    // Solder pads (Gold)
    color("Gold") {
        // BAT+ and BAT- (middle rear)
        translate([-c_w/2 + 1.5, 9.0, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([c_w/2 - 1.5, 9.0, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        // OUT+ and OUT- (back corners)
        translate([-c_w/2 + 1.5, c_l/2 - 1.5, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
        translate([c_w/2 - 1.5, c_l/2 - 1.5, c_h/2 + 0.05]) cylinder(h=0.1, d=2.0, center=true);
    }
}

// F. MSL-1C2P Slide Switch (Size: 8.5 x 3.5 x 3.5 mm body, 2.0 mm knob)
module slide_switch_msl_1c2p() {
    s_w = 3.5;
    s_l = 8.5;
    s_h = 3.5;
    
    // Metal bracket/housing
    color("Silver") cube([s_w, s_l, s_h], center=true);
    
    // Red slide knob (2.0mm tall)
    translate([0, 0, s_h/2 + 1.0])
        color("Red") cube([1.5, 2.5, 2.0], center=true);
        
    // 3 pins under the switch
    color("Silver") {
        translate([0, -2.5, -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
        translate([0, 0,    -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
        translate([0, 2.5,  -s_h/2 - 1.5]) cylinder(h=3.0, d=0.5, center=true);
    }
}

// G. Tact Trigger Switch (AK-TS-I015-42, Size: 6.0 x 6.0 x 11.0 mm H11)
module tact_switch_h11() {
    b_w = 6.0;
    b_l = 6.0;
    b_h = 3.5;
    
    // Base plastic body (black)
    color([0.15, 0.15, 0.15]) cube([b_w, b_l, b_h], center=true);
    
    // Metal top bracket plate
    translate([0,0,b_h/2 + 0.05])
        color("Silver") cube([b_w - 0.2, b_l - 0.2, 0.1], center=true);
        
    // Switch Button Stem (Long H11 stem, total switch height 11mm, stem height ~7.5mm)
    translate([0, 0, b_h/2 + 3.75])
        color("DimGray") cylinder(h=7.5, d=3.0, center=true);
        
    // 4 Pins (solder legs)
    color("Silver") {
        for (x = [-2.8, 2.8], y = [-2.2, 2.2]) {
            translate([x, y, -b_h/2 - 1.0]) cylinder(h=2.0, d=0.6, center=true);
        }
    }
}

// H. 18650 Battery Cell (BT187, Size: D18.4 x 65.2 mm with pre-soldered wires)
module battery_18650_wire() {
    bat_d = 18.4;
    bat_l = 65.2;
    
    // Battery Cylinder wrap (Dodger Blue wrap)
    color([0.2, 0.5, 0.9])
        rotate([90, 0, 0])
            cylinder(h=bat_l, d=bat_d, center=true);
            
    // (+) Positive button cap (+Y side)
    translate([0, bat_l/2 + 0.5, 0])
        rotate([90,0,0])
            color("Silver") cylinder(h=1.0, d=6.0, center=true);
            
    // Lead Wires (soldered onto tabs)
    // Red (+Y side)
    translate([0, bat_l/2 + 1.0, 3.0]) {
        color("Red") {
            rotate([0, 90, 0]) cylinder(h=5.0, d=1.2, center=true);
            // flexible wire curve mockup
            translate([2.5, -5.0, 5.0]) rotate([45,0,0]) cylinder(h=15.0, d=1.2, center=true);
        }
    }
    // Black (-Y side)
    translate([0, -bat_l/2 - 1.0, 3.0]) {
        color("Black") {
            rotate([0, 90, 0]) cylinder(h=5.0, d=1.2, center=true);
            translate([2.5, 5.0, 5.0]) rotate([-45,0,0]) cylinder(h=15.0, d=1.2, center=true);
        }
    }
}

// ==========================================
// 3. SYSTEM 3D WIRING HARNESS
// ==========================================
// Visualizes the complete wiring connection paths based on designated module locations.

module scanner_system_wiring(
    esp32_pos, oled_pos, gm77_pos,
    bat_pos, chg_pos, switch_pos,
    boost_pos, trigger_pos
) {
    // ----------------------------------------------------
    // Terminal Solder Point Offsets (Relative to Module Center)
    // ----------------------------------------------------
    
    // 18650 Battery Terminals (horizontal battery, rotated [90, 0, 0])
    bat_vcc = bat_pos + [0, 32.6, 0];
    bat_gnd = bat_pos + [0, -32.6, 0];
    
    // TP4056 Charger (horizontal PCB, USB connector facing -Y)
    chg_bat_vcc = chg_pos + [-16.5/2 + 1.5, 9.0, 1.2/2];
    chg_bat_gnd = chg_pos + [ 16.5/2 - 1.5, 9.0, 1.2/2];
    chg_out_vcc = chg_pos + [-16.5/2 + 1.5, 27.5/2 - 1.5, 1.2/2];
    chg_out_gnd = chg_pos + [ 16.5/2 - 1.5, 27.5/2 - 1.5, 1.2/2];
    
    // Slide Switch (pins pointing downward -Z)
    sw_pin_in  = switch_pos + [0, 0, -3.5/2];      // Center pin
    sw_pin_out = switch_pos + [0, 2.5, -3.5/2];    // ON pin
    
    // VLT-VC013 Booster (horizontal, input pads at -Y, output pads at +Y)
    bst_in_vcc  = boost_pos + [-11.0/2 + 1.5, -22.0/2 + 1.5, 1.2/2];
    bst_in_gnd  = boost_pos + [ 11.0/2 - 1.5, -22.0/2 + 1.5, 1.2/2];
    bst_out_vcc = boost_pos + [-11.0/2 + 1.5,  22.0/2 - 1.5, 1.2/2];
    bst_out_gnd = boost_pos + [ 11.0/2 - 1.5,  22.0/2 - 1.5, 1.2/2];
    
    // ESP32 DevKitC (pins facing upward +Z in flipped state)
    esp_5v  = esp32_pos + [-28.2/2 + 1.27, -54.4/2 + 1.27*2, 1.6/2]; // 5V is pin 2 from USB side left
    esp_gnd = esp32_pos + [-28.2/2 + 1.27, -54.4/2 + 1.27*6, 1.6/2]; // GND is pin 6 left
    esp_sda = esp32_pos + [ 28.2/2 - 1.27,  54.4/2 - 1.27*6, 1.6/2]; // SDA (GPIO21) right side
    esp_scl = esp32_pos + [ 28.2/2 - 1.27,  54.4/2 - 1.27*5, 1.6/2]; // SCL (GPIO22) right side
    esp_rx2 = esp32_pos + [-28.2/2 + 1.27,  54.4/2 - 1.27*9, 1.6/2]; // RX2 (GPIO16) left side
    esp_tx2 = esp32_pos + [-28.2/2 + 1.27,  54.4/2 - 1.27*8, 1.6/2]; // TX2 (GPIO17) left side
    esp_g4  = esp32_pos + [-28.2/2 + 1.27, -54.4/2 + 1.27*12, 1.6/2];// GPIO4 (trigger input)
    
    // SSD1306 OLED (I2C pin headers pointing downward -Z)
    oled_gnd = oled_pos + [-3.81, 27.3/2 - 2.0, -1.2/2];
    oled_vcc = oled_pos + [-1.27, 27.3/2 - 2.0, -1.2/2];
    oled_scl = oled_pos + [ 1.27, 27.3/2 - 2.0, -1.2/2];
    oled_sda = oled_pos + [ 3.81, 27.3/2 - 2.0, -1.2/2];
    
    // GM77 Scanner (UART connector pads at the back side +Y)
    gm_vcc = gm77_pos + [-13.75 + 2.0,  48.5/2, -14.0/2 + 0.5]; // Pin 1
    gm_gnd = gm77_pos + [-13.75 + 4.5,  48.5/2, -14.0/2 + 0.5]; // Pin 2
    gm_tx  = gm77_pos + [-13.75 + 7.0,  48.5/2, -14.0/2 + 0.5]; // Pin 3
    gm_rx  = gm77_pos + [-13.75 + 9.5,  48.5/2, -14.0/2 + 0.5]; // Pin 4
    
    // Tact Button (H11 pins pointing downward -Z)
    tact_sig = trigger_pos + [-2.8, -2.2, -3.5/2];
    tact_gnd = trigger_pos + [ 2.8, -2.2, -3.5/2];

    // ----------------------------------------------------
    // Draw 3D Wire Connections
    // ----------------------------------------------------
    
    // W1: Battery VCC -> Charger BAT+
    color("Red") wire_path([bat_vcc, bat_vcc + [0, 4, 10], chg_bat_vcc + [0, -5, 10], chg_bat_vcc], radius=0.6);
    
    // W2: Battery GND -> Charger BAT-
    color("Black") wire_path([bat_gnd, bat_gnd + [0, -4, 10], chg_bat_gnd + [0, -5, 10], chg_bat_gnd], radius=0.6);
    
    // W3: Charger OUT+ -> Slide Switch Center
    color("Red") wire_path([chg_out_vcc, chg_out_vcc + [0, 5, 2], sw_pin_in + [-2, -2, -4], sw_pin_in], radius=0.5);
    
    // W4: Slide Switch ON -> Booster IN+
    color("Red") wire_path([sw_pin_out, sw_pin_out + [0, 2, -6], bst_in_vcc + [0, -4, -6], bst_in_vcc], radius=0.5);
    
    // W5: Charger OUT- -> Booster IN- (System GND link)
    color("Black") wire_path([chg_out_gnd, chg_out_gnd + [0, 5, -2], bst_in_gnd + [0, -4, -6], bst_in_gnd], radius=0.5);
    
    // W6: Booster OUT+ (5V) -> ESP32 5V
    color("Red") wire_path([bst_out_vcc, bst_out_vcc + [0, 4, 6], esp_5v + [0, -4, -8], esp_5v], radius=0.5);
    
    // W7: Booster OUT- (GND) -> ESP32 GND
    color("Black") wire_path([bst_out_gnd, bst_out_gnd + [0, 4, 4], esp_gnd + [0, -4, -8], esp_gnd], radius=0.5);
    
    // W8: 5V Rail -> GM77 VCC
    color("Red") wire_path([bst_out_vcc + [0, 4, 6], gm_vcc + [0, 6, -10], gm_vcc], radius=0.4);
    
    // W9: GND Rail -> GM77 GND
    color("Black") wire_path([bst_out_gnd + [0, 4, 4], gm_gnd + [0, 6, -10], gm_gnd], radius=0.4);
    
    // W10: 5V Rail -> OLED VCC
    color("Red") wire_path([bst_out_vcc + [0, 4, 6], oled_vcc + [0, 10, -5], oled_vcc], radius=0.4);
    
    // W11: GND Rail -> OLED GND
    color("Black") wire_path([bst_out_gnd + [0, 4, 4], oled_gnd + [0, 10, -5], oled_gnd], radius=0.4);
    
    // W12: ESP32 SDA -> OLED SDA (I2C)
    color("Yellow") wire_path([esp_sda, esp_sda + [5, 5, 8], oled_sda + [5, 10, -5], oled_sda], radius=0.4);
    
    // W13: ESP32 SCL -> OLED SCL (I2C)
    color("Blue") wire_path([esp_scl, esp_scl + [3, 5, 8], oled_scl + [3, 10, -5], oled_scl], radius=0.4);
    
    // W14: ESP32 RX2 -> GM77 TX (UART)
    color("Green") wire_path([esp_rx2, esp_rx2 + [-5, 5, 5], gm_tx + [-3, 10, -5], gm_tx], radius=0.4);
    
    // W15: ESP32 TX2 -> GM77 RX (UART)
    color("Orange") wire_path([esp_tx2, esp_tx2 + [-3, 5, 5], gm_rx + [-1, 10, -5], gm_rx], radius=0.4);
    
    // W16: ESP32 GPIO4 -> Tact Switch signal (Trigger button)
    color("Purple") wire_path([esp_g4, esp_g4 + [-8, -5, -15], tact_sig + [-2, -2, -6], tact_sig], radius=0.4);
    
    // W17: Tact Switch GND -> System GND (Booster OUT- / ESP32 GND)
    color("Black") wire_path([tact_gnd, tact_gnd + [2, -2, -6], bst_out_gnd + [0, -10, -15], bst_out_gnd], radius=0.4);
}
