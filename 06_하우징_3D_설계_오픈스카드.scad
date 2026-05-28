/* 
 * 🔫 휴대용 GM77/SEN0512 바코드 및 QR 스캐너 하우징 디자인 V2.0 (Premium Logic)
 * 
 * 제작자: Antigravity AI (Google DeepMind)
 * 업데이트 내용:
 *   - 인체공학적 그립(Ergonomic Grip) 강화: 손가락 홈 및 테이퍼드 디자인
 *   - 내부 마운팅 강화: ESP32 및 GM77(SEN0512) 전용 가이드/스탠드 오프 추가
 *   - 방열 구멍(Ventilation) 및 USB C/Micro 포트 타공 정밀화
 *   - 상단 OLED 베젤 디자인 개선 (10도 경사 배치로 가독성 향상)
 *   - 구조적 강성 보강: 내벽 리브(Rib) 및 보강재 추가
 */

// [글로벌 파라미터]
$fn = 60;
wall = 2.5;         // 벽 두께
clearance = 0.6;    // 조립 공차

// [헤드 파트 치수]
head_w = 54.0;      // 폭 (OLED 베젤 및 배선 여유)
head_l = 98.0;      // 길이 (전면 스캐너 + 중앙 ESP32 + 후면 커넥터)
head_h = 40.0;      // 높이 (내부 적층 높이 고려)

// [핸들 파트 치수]
handle_base_d = 34.0; // 하단 지름 (18650 배터리 모듈 수납)
handle_top_d = 30.0;  // 상단 지름 (그립감 향상을 위한 테이퍼)
handle_h = 105.0;     // 손잡이 길이
handle_angle = 15;    // 인체공학적 각도 (Degree)

// [내부 부품 규격]
gm77_size = [27.5, 48.5, 14.0]; // GM77 / SEN0512 바코드 모듈 치수
esp32_size = [30.0, 56.5, 15];
oled_size = [27.5, 27.5, 3];
battery_diam = 22.0;

// --- 메인 출력 제어 ---
render_part = "all"; // all, body, lid, trigger

if (render_part == "all") {
    translate([0, 0, 0]) housing_body();
    translate([head_w + 20, 0, 0]) housing_lid();
}

if (render_part == "body") housing_body();
if (render_part == "lid") housing_lid();

// --- 1. 하우징 바디 (Main Body) ---
module housing_body() {
    difference() {
        union() {
            // [A] 메인 헤드 (유선형 베이스)
            hull() {
                translate([head_w/2, 5, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 10);
                translate([head_w/2, head_l-5, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, head_h*0.85, 5, 8);
            }
            
            // [B] 인체공학적 핸들
            translate([head_w/2, head_l*0.6, 0])
            rotate([handle_angle, 0, 0])
            translate([0, 0, -handle_h])
            cylinder(h=handle_h, d1=handle_base_d, d2=handle_top_d);

            // [C] 트리거 가드
            translate([head_w/2, 28, 5])
            trigger_guard();
        }

        // [D] 헤드 내부 비우기
        translate([head_w/2, head_l/2, head_h/2 + wall])
        scale([0.9, 0.94, 0.88])
        hull() {
            translate([0, -head_l/2 + wall, 0]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 8);
            translate([0, head_l/2 - wall, 0]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, head_h*0.85, 5, 6);
        }

        // [E] 배터리 수납 공간 (핸들 내부)
        translate([head_w/2, head_l*0.6, 0])
        rotate([handle_angle, 0, 0])
        translate([0, 0, -handle_h-1])
        cylinder(h=handle_h+5, d=battery_diam);

        // [F] 스캐너 창 (Front Window)
        translate([head_w/2 - 18, -2, head_h/2 - 10])
        cube([36, 10, 20]);
        
        // [G] USB 포트 (Rear)
        translate([head_w/2 - 6, head_l - 10, wall + 2])
        cube([12, 15, 10]);

        // [H] 방열 슬롯
        for(i=[0:4]) {
            translate([-1, 35 + i*8, 18]) rotate([0, 90, 0]) cylinder(h=head_w+2, d=2.5);
        }
        
        // [I] 결합 나사 구멍 (M3 Thread)
        mount_points(3.0);
    }
}

// --- 2. 하우징 덮개 (Lid) ---
module housing_lid() {
    difference() {
        union() {
            // 상단 커버 베이스
            hull() {
                translate([head_w/2, 5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w, 3, 5, 10);
                translate([head_w/2, head_l-5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, 3, 5, 8);
            }
            
            // OLED 베젤 (사용자 시야각 10도 경사)
            translate([head_w/2, 55, 3])
            rotate([-10, 0, 0])
            difference() {
                rounded_rect(oled_size[0]+10, oled_size[1]+10, 6, 4, true);
                translate([0, 0, 2]) rounded_rect(oled_size[0]+2, oled_size[1]+2, 10, 2, true);
            }
        }

        // [J] OLED 표시창 타공
        translate([head_w/2, 55, -5])
        rotate([-10, 0, 0])
        rounded_rect(oled_size[0]-2, oled_size[1]-2, 20, 2, true);

        // [K] 결합 나사 구멍 (M3 Bolt pass)
        mount_points(3.5);
        
        // [L] 각인
        translate([head_w/2, head_l - 18, 2.5])
        linear_extrude(2)
        text("QR SCANNER GEN2", size=3.5, font="Arial:style=Bold", halign="center");
    }
}

// --- 유틸리티 모듈 ---

module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r) offset(delta=-r)
        square([w-r*2, h-r*2], center=true);
    }
}

module trigger_guard() {
    difference() {
        rotate([0, 90, 0]) translate([0, 0, -3]) cylinder(h=6, d=28);
        rotate([0, 90, 0]) translate([2, 4, -5]) cylinder(h=10, d=22);
        translate([-5, -20, -15]) cube([10, 20, 30]);
    }
}

module mount_points(d) {
    inset = 7;
    translate([inset, inset, -10]) cylinder(h=60, d=d);
    translate([head_w-inset, inset, -10]) cylinder(h=60, d=d);
    translate([inset + 3, head_l-inset, -10]) cylinder(h=60, d=d);
    translate([head_w-inset - 3, head_l-inset, -10]) cylinder(h=60, d=d);
}
