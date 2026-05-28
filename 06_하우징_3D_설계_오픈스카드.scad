/* 
 * 🔫 휴대용 GM77/SEN0512 바코드 및 QR 스캐너 하우징 디자인 V2.0 (Premium Logic)
 * 
 * 제작자: Antigravity AI (Google DeepMind)
 * 업데이트 내용:
 *   - 3D 프린터 출력 최적화: 브릿지 및 오버행 최소화 설계
 *   - 부품 사양 맞춤형 헤드 길이 연장 (120mm)로 내부 공간 여유 확보
 *   - ESP32 및 GM77(SEN0512) 기판 전용 고정용 스탠드오프(Standoff) 추가
 *   - 상단 덮개 안쪽에 OLED 액정(SSD1306) 고정용 4점식 기둥 추가
 *   - 손잡이 전면(트리거 가드 안쪽)에 12mm 스위치/버튼용 홀 규격 반영
 *   - 18650 배터리(핸들 내 수납) 및 배선 통로 확보
 *   - 인체공학적 그립(Ergonomic Grip) 강화: 실질적인 3단 손가락 홈(Finger Grooves) 가공 추가
 *   - 구조적 강성 보강: 헤드 측벽 붕괴 방지용 가로형 격벽 보강 리브(Rib) 2개소 설계
 *   - 렌더링 엔진 버그 수정: rounded_rect 모듈의 이중 offset 공차 오류 및 lid 두께 대비 코너 반경 오류(r=10 -> r=1.0)를 전면 수정하여 헤드 쉘 및 덮개 바디가 완전히 렌더링되도록 개선
 */

// [글로벌 파라미터]
$fn = 60;
wall = 2.5;         // 벽 두께
clearance = 0.6;    // 조립 공차

// [헤드 파트 치수]
head_w = 54.0;      // 폭 (OLED 베젤 및 배선 여유)
head_l = 120.0;     // 길이 (GM77 스캐너 + 중앙 배선 + 후면 ESP32) - 부품 직렬 배치를 위해 120mm로 연장
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
            // [A] 메인 하우징 외형과 비우기 결합
            difference() {
                union() {
                    // 메인 헤드 (유선형 베이스)
                    hull() {
                        translate([head_w/2, 5, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 10);
                        translate([head_w/2, head_l-5, head_h/2]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, head_h*0.85, 5, 8);
                    }
                    
                    // 인체공학적 핸들 (3단 손가락 홈 및 테이퍼드 설계 적용)
                    translate([head_w/2, head_l*0.6, 0])
                    rotate([handle_angle, 0, 0])
                    difference() {
                        // 기본 테이퍼드 실린더 핸들
                        translate([0, 0, -handle_h])
                        cylinder(h=handle_h, d1=handle_base_d, d2=handle_top_d);
                        
                        // 손가락 홈 (Finger Grooves) 파기 (검지는 트리거 스위치에 위치하므로 중지/약지/소지 자리만 가공)
                        for (z_pos = [-38, -58, -78]) {
                            let (t = (z_pos + handle_h) / handle_h) { // t는 0 (하단) ~ 1 (상단)
                                let (d_pos = handle_base_d * (1-t) + handle_top_d * t) {
                                    translate([0, -d_pos/2 + 1.2, z_pos])
                                    rotate([0, 90, 0])
                                    cylinder(h=handle_base_d + 10, d=9.0, center=true);
                                }
                            }
                        }
                    }

                    // 트리거 가드
                    translate([head_w/2, 28, 5])
                    trigger_guard();
                }

                // 헤드 내부 비우기
                translate([head_w/2, head_l/2, head_h/2 + wall])
                scale([0.9, 0.94, 0.88])
                hull() {
                    translate([0, -head_l/2 + wall, 0]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 8);
                    translate([0, head_l/2 - wall, 0]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, head_h*0.85, 5, 6);
                }

                // 배터리 수납 공간 (핸들 내부)
                translate([head_w/2, head_l*0.6, 0])
                rotate([handle_angle, 0, 0])
                translate([0, 0, -handle_h-1])
                cylinder(h=handle_h+5, d=battery_diam);
            }
            
            // [B] 내부 구조물 추가 (Hollowing 공간 위에 결합)
            
            // ESP32용 고정 스탠드오프 (4개 기둥, 높이 10mm)
            translate([head_w/2, head_l - 35, wall]) {
                esp32_standoffs(h=10, d_outer=5.0);
            }
            
            // GM77용 고정 스탠드오프 (4개 기둥, 카메라 정렬 고려 높이 10.5mm)
            translate([head_w/2, 29.25, wall]) {
                gm77_standoffs(h=10.5, d_outer=5.0);
            }
            
            // 강성 보강용 가로 격벽 리브(Rib) 추가 (조립 간섭이 없는 중간 구역 Y=55, Y=113에 설계)
            reinforcement_ribs();
        }

        // [C] 나사 탭 및 포트 구멍 차집합 처리 (Difference)
        
        // ESP32용 스탠드오프 나사 구멍 (M3 나사용, 직경 2.5mm)
        translate([head_w/2, head_l - 35, wall - 1]) {
            esp32_screw_holes(h=15, d_inner=2.5);
        }
        
        // GM77용 스탠드오프 나사 구멍 (M2 나사용, 직경 1.8mm)
        translate([head_w/2, 29.25, wall - 1]) {
            gm77_screw_holes(h=15, d_inner=1.8);
        }

        // 스캐너 창 (Front Window)
        translate([head_w/2 - 18, -2, head_h/2 - 10])
        cube([36, 10, 20]);
        
        // USB 포트 (Rear)
        translate([head_w/2 - 6, head_l - 10, wall + 2])
        cube([12, 15, 10]);

        // 방열 슬롯
        for(i=[0:6]) {
            translate([-1, 35 + i*8, 18]) rotate([0, 90, 0]) cylinder(h=head_w+2, d=2.5);
        }
        
        // 트리거 버튼 타공 (핸들 전면에 수직하게 12.2mm 스위치 홀 생성)
        translate([head_w/2, head_l*0.6, 0])
        rotate([handle_angle, 0, 0])
        translate([0, -handle_top_d/2, -20]) // Z = -20 위치 (트리거 가드 내부 공간)
        rotate([90, 0, 0])
        cylinder(h=wall*4, d=12.2, center=true);
        
        // 결합 나사 구멍 (M3 Thread)
        mount_points(3.0);
    }
}

// --- 2. 하우징 덮개 (Lid) ---
module housing_lid() {
    difference() {
        union() {
            // 상단 커버 베이스 (두께 3mm에 맞춰 코너 반경 r=1.0으로 수정하여 렌더링 에러 해결)
            hull() {
                translate([head_w/2, 5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w, 3, 5, 1.0);
                translate([head_w/2, head_l-5, 1.5]) rotate([90, 0, 0]) rounded_rect(head_w*0.85, 3, 5, 1.0);
            }
            
            // OLED 베젤 (사용자 시야각 10도 경사)
            translate([head_w/2, 55, 3])
            rotate([-10, 0, 0])
            difference() {
                rounded_rect(oled_size[0]+10, oled_size[1]+10, 6, 4, true);
                translate([0, 0, 2]) rounded_rect(oled_size[0]+2, oled_size[1]+2, 10, 2, true);
            }
            
            // OLED 고정용 스탠드오프 (Lid 안쪽 방향으로 4mm 돌출)
            translate([head_w/2, 55, 0])
            rotate([-10, 0, 0])
            translate([0, 0, -4])
            oled_standoffs(h=4, d_outer=4.5);
        }

        // [J] OLED 표시창 타공
        translate([head_w/2, 55, -5])
        rotate([-10, 0, 0])
        rounded_rect(oled_size[0]-2, oled_size[1]-2, 20, 2, true);
        
        // OLED 스탠드오프 나사 구멍 (M2 나사용, 직경 1.8mm blind hole)
        translate([head_w/2, 55, 0])
        rotate([-10, 0, 0])
        translate([0, 0, -5])
        oled_screw_holes(h=4.5, d_inner=1.8);

        // [K] 결합 나사 구멍 (M3 Bolt pass)
        mount_points(3.5);
        
        // [L] 각인
        translate([head_w/2, head_l - 18, 2.5])
        linear_extrude(2)
        text("QR SCANNER GEN2", size=3.5, font="Arial:style=Bold", halign="center");
    }
}

// --- 부품 고정 모듈 (Standoffs & Holes) ---

module esp32_standoffs(h, d_outer) {
    w_pitch = 25.5; // ESP32 DevKit 고정 나사 홀 가로 간격
    l_pitch = 51.5; // ESP32 DevKit 고정 나사 홀 세로 간격
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module esp32_screw_holes(h, d_inner) {
    w_pitch = 25.5;
    l_pitch = 51.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module gm77_standoffs(h, d_outer) {
    w_pitch = 22.5; // GM77 고정 홀 가로 간격
    l_pitch = 40.5; // GM77 고정 홀 세로 간격
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module gm77_screw_holes(h, d_inner) {
    w_pitch = 22.5;
    l_pitch = 40.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module oled_standoffs(h, d_outer) {
    w_pitch = 23.5; // 0.96 OLED 고정 나사 홀 가로 간격
    l_pitch = 23.5; // 0.96 OLED 고정 나사 홀 세로 간격
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_outer);
}

module oled_screw_holes(h, d_inner) {
    w_pitch = 23.5;
    l_pitch = 23.5;
    translate([-w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, -l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([-w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
    translate([w_pitch/2, l_pitch/2, 0]) cylinder(h=h, d=d_inner);
}

module reinforcement_ribs() {
    // 내부 강성 강화를 위한 U자형 가로 보강 리브 (배선/부품 간섭 우회)
    rib_y_positions = [55, 113];
    for (y_pos = rib_y_positions) {
        translate([head_w/2, y_pos, head_h/2 + wall])
        difference() {
            // 리브 외각 (내벽과 완벽 밀착 및 보강)
            scale([0.9, 1.0, 0.88]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 1.5, 8);
            // 리브 내부 (부품 관통 및 중앙 배선 통로 확보)
            scale([0.72, 2.0, 0.68]) rotate([90, 0, 0]) rounded_rect(head_w, head_h, 5, 8);
        }
    }
}

// --- 유틸리티 모듈 (버그 수정: 1개의 offset(r)만 사용하여 정사이즈 w, h 가 구현되도록 수정) ---

module rounded_rect(w, h, depth, r, centered=true) {
    if (centered) {
        linear_extrude(height=depth, center=true)
        offset(r=r)
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
