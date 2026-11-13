# -*- coding: utf-8 -*-
"""
68일차 전 일자(Day 01 ~ Day 68) 1:1 실제 사진 및 실제 파이썬·보드·DB·CAD 실행 결과 매핑
(AI 생성 이미지 0건 — 모든 파일은 저장소 내 실물 촬영본, 실제 코드/DB/로그 실행 캡처, 실제 CAD/슬라이서 산출물임)
"""

DAY_IMAGE_MAP: dict[int, tuple[str, str]] = {
    1: (
        "scratch/notebook_captures/cap_day01_git_init.png",
        "그림 1. Git 저장소 최초 초기화(commit 65b215f, 2026-03-22) 및 초기 커밋 로그 실제 조회 결과",
    ),
    2: (
        "KSHS/extracted_images/slide_1_img_38_3024x3024.png",
        "그림 2. 연구실 내 실제 농산물 물류 플라스틱 상자(콘티 상자) 전면에 부착한 사과 QR 코드 실물 촬영 사진",
    ),
    3: (
        "KSHS/extracted_images/slide_1_img_35_1330x1266.png",
        "그림 3. 농산물 특·상·보통 선별 등급별 실물 사과 촬영 이미지 및 외관·결점과 판정 기준 웹 페이지 구동 화면",
    ),
    4: (
        "scratch/notebook_captures/cap_day04_jetson_setup.png",
        "그림 4. Jetson Orin Nano(JetPack 6.2) 3D Depth(D455) 환경 구축 및 Swap 메모리 증설 Git 커밋 실행 기록",
    ),
    5: (
        "scratch/notebook_captures/cap_day05_tensorrt_fix.png",
        "그림 5. Jetson 가상환경(venv) TensorRT 바인딩 해결 이력 및 초기 머신러닝·비전 프로토타입 파이썬 모듈 목록",
    ),
    6: (
        "scratch/notebook_captures/cap_day06_dht11_quantization.png",
        "그림 6. 파이썬 실측 분석 결과: DHT11 정수 양자화(1°C 계단 오차) 한계와 SHT45 고정밀(0.01°C) 냉각 곡선 비교",
    ),
    7: (
        "KSHS/extracted_images/slide_1_img_48_3216x1916.png",
        "그림 7. 초기 Flask 웹 프로토타입('전체 QR 스캔 데이터 및 과일 도감') 실제 브라우저 구동 화면 캡처",
    ),
    8: (
        "scratch/notebook_captures/cap_day08_korea_30km_rds.png",
        "그림 8. AWS RDS(sensor_data)에 적재된 초기 냉장 수송 실험(korea_30km_test, 181건) 경로 및 온도·속도 파이썬 플롯",
    ),
    9: (
        "scratch/notebook_captures/cap_day09_streamlit_refactor.png",
        "그림 9. Streamlit 전면 개편 과정에서 절대경로(Path(__file__).parent)로 복구한 과일 도감 정적 이미지 렌더링 검증",
    ),
    10: (
        "scratch/notebook_captures/cap_day10_rds_schema_kst.png",
        "그림 10. PyMySQL을 통한 AWS RDS(lab225) 실제 스키마 조회(FmID 기본키 확인) 및 KST(+09:00) 타임존 동기화 실행 결과",
    ),
    11: (
        "scratch/notebook_captures/cap_day11_sha256_ledger.png",
        "그림 11. AWS RDS 상자 #77(FmID=77) 실데이터에 대한 A00~A15 단계별 SHA-256 해시체인 무결성 검증 파이썬 실행 결과",
    ),
    12: (
        "scratch/notebook_captures/step5_consumer_box77_top.png",
        "그림 12. 소비자 추적 대시보드(Step5_Run_Dashboard.py, FmID=77) 실시간 구동 화면 — 원산지·품종 및 안전성 검증 배지",
    ),
    13: (
        "scratch/notebook_captures/cap_day13_repo_architecture.png",
        "그림 13. 전체 저장소 디렉터리 계층 리팩토링 후 5대 핵심 모듈별 파일 수 및 용량 파이썬 실측 감사 출력",
    ),
    14: (
        "scratch/notebook_captures/cap_day14_qr_grade_composite.png",
        "그림 14. 파이썬(qrcode + Pillow)으로 실제 생성·보존된 상자 #77 산지 원물 QR 및 A·B·C 등급 과일 로고 합성 QR",
    ),
    15: (
        "scratch/notebook_captures/cap_day15_gps_zero_filter.png",
        "그림 15. GPS 미수신 (0.0, 0.0) 좌표 포함 시 발생하는 지도 축 왜곡 현상과 유효 좌표 필터링 후 실차 궤적 복원 결과",
    ),
    16: (
        "KSHS/extracted_images/slide_1_img_32_4032x2268.png",
        "그림 16. 연구실 책상 위에서 촬영한 GM77 광학 바코드·QR 스캐너 모듈 및 Universal Test Board V1.2 실물 연동 사진",
    ),
    17: (
        "3D_Printer_Housing/v09_QR_Scanner_Housing_Snapfit/09_assembly_view.png",
        "그림 17. OpenSCAD로 설계한 핸드헬드 QR 스캐너 하우징 초기 조립체 렌더링(상단 OLED 창 및 그립 핑거 그루브 적용)",
    ),
    18: (
        "3D_Printer_Housing/v06_Housing_And_Stand/06_exploded_view.png",
        "그림 18. 1차 3D 프린팅 슬라이싱 검증을 위해 설계한 스캐너 본체 및 거치 스탠드(v06) 분해도 렌더링",
    ),
    19: (
        "3D_Printer_Housing/v11_QR_Scanner_Housing_Flush_OLED/11_exploded_view.png",
        "그림 19. 서포트 제거 및 조립성 확보를 위해 좌/우 반할(Left/Right) 구조와 매립형 OLED를 적용한 v11 분해도",
    ),
    20: (
        "scratch/notebook_captures/step4_coldchain_174km_ko.png",
        "그림 20. 한/영 다국어 및 2×2 관제 그리드가 적용된 통합 관제 대시보드(Step4_Run_Coldchain_v2.py) 실제 구동 화면",
    ),
    21: (
        "3D_Printer_Housing/v14_QR_Scanner_Housing_Final/14_exploded_view.png",
        "그림 21. 원버튼 제어 스위치 및 슬라이드 결합 구조를 보강한 핸드헬드 스캐너 하우징(v14) 정밀 분해도 렌더링",
    ),
    22: (
        "3D_Printer_Housing/v16_QR_Scanner_Housing/system_wiring_3d.png",
        "그림 22. 스캐너 하우징 내부 부품(ESP32 + GM77 + 18650 배터리 + 승압 모듈 + OLED) 3D 실장 및 배선 간섭 검증 뷰",
    ),
    23: (
        "scratch/notebook_captures/cap_day23_peak_hold_shock.png",
        "그림 23. GY-521 고속 폴링 Peak-Hold 알고리즘으로 포착한 실차 주행 중 순간 충격 피크(최대 17.69G) AWS RDS 실측 그래프",
    ),
    24: (
        "3D modeling/회로도.kicad_sch/pcb_layout.png",
        "그림 24. 점퍼선 접촉 불량 해소를 위해 최초 설계한 75×60mm 브레이크아웃 센서 캐리어 보드 초안 레이아웃",
    ),
    25: (
        "KSHS/extracted_images/slide_1_img_46_1651x1844.png",
        "그림 25. 선별 공정(A12) 자동 분류 및 A·B·C 등급별 과일 QR 일괄 발행을 수행하는 파이썬 Tkinter 'Sorting GUI' 실행 캡처",
    ),
    26: (
        "scratch/notebook_captures/cap_day26_rds_qr_lifecycle.png",
        "그림 26. AWS RDS(lab225.qr) 테이블 실제 쿼리 결과 — 수확(A00)부터 출하(A15)까지 전 공정 타임스탬프 데이터 실증",
    ),
    27: (
        "scratch/DFR1117_dimension.png",
        "그림 27. 초소형 센서팟 메인 MCU로 최종 선정된 DFRobot Beetle ESP32-C6(DFR1117, 20.5×25.0mm) 외형 치수 및 핀맵",
    ),
    28: (
        "3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/Fig2_CarrierBoard_Annotated_Publication.png",
        "그림 28. 독자 설계한 50.0×50.0mm 양면 CarrierBoard PCB의 Top(MCU·조도·스위치) 및 Bottom(온습도·IMU·GPS) 아트웍",
    ),
    29: (
        "3D_Printer_Housing/v18_Apple_Sensor_Pod/18_exploded_view.png",
        "그림 29. 농산물 상자 내 과일과 동일 조건 계측을 위해 최초 모델링한 사과 형상 센서팟(v18) 분해도 렌더링",
    ),
    30: (
        "3D modeling/PCB 견적서/PCB 견적서_1.png",
        "그림 30. 최종 DRC 검증을 마친 50×50mm FR-4 양면 CarrierBoard 거버 패키지 실제 제작 발주 견적서(2026.09.21)",
    ),
    31: (
        "3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/Fig7_FDT_CrossSection_Engineering_Schematic.png",
        "그림 31. 과일 디지털 트윈(FDT) 사과 센서팟 단면 아키텍처 및 미세기후 통기 포트(ePTFE 멤브레인) 공학 설계도",
    ),
    32: (
        "scratch/notebook_captures/cap_day32_serial_i2c_short.png",
        "그림 32. 1차 납땜 조립 직후 보드 시리얼 모니터 실제 출력 로그(diagnostic_stream.log) — SDA(GPIO 19) LOW 접지 현상 포착",
    ),
    33: (
        "scratch/gps_orientation_guide.png",
        "그림 33. 실물 CarrierBoard 소켓 확대 촬영 및 핀 대조 분석 — 모듈 180° 역방향 오삽입 원인 규명 및 정방향 교정 사진",
    ),
    34: (
        "scratch/notebook_captures/cap_day34_174km_telemetry.png",
        "그림 34. 전주↔대전 왕복 174km 고속도로 실차 주행(1,834건, 최고 120.1km/h) LittleFS 복원 및 AWS RDS 실측 텔레메트리",
    ),
    35: (
        "scratch/bottom_rot180.jpg",
        "그림 35. SW1 전원부 보강 및 센서 정방향 체결 완료 후 USB-C 전원이 인가되어 정상 가동 중인 실물 CarrierBoard(녹색 LED 점등)",
    ),
    36: (
        "scratch/notebook_captures/cap_day36_flash_dump_jsonl.png",
        "그림 36. ESP32-C6 내장 LittleFS 플래시 메모리에서 직접 덤프한 실제 블랙박스 파일(2,994건 / 3,900+건) 파싱 실행 화면",
    ),
    37: (
        "scratch/notebook_captures/cap_day37_fridge_tau_fit.png",
        "그림 37. 상온(27.62°C)에서 냉장고 투입 시 실측 급랭 데이터(n=185) 및 Newton 냉각 법칙 비선형 회귀 열시상수(τ) 도출 결과",
    ),
    38: (
        "scratch/notebook_captures/step4_jetson_splithud.png",
        "그림 38. 차량용 소형 디스플레이에 최적화된 2분할 스플릿 HUD 대시보드(Step4_Jetson_SplitHUD.py) 실제 실행 화면",
    ),
    39: (
        "scratch/notebook_captures/cap_day39_evening_commute.png",
        "그림 39. 퇴근 시간 실차 주행 중 두 세션으로 분절되었던 144건 패킷의 연속 궤적·속도 병합 복원 결과(최고 63.2km/h)",
    ),
    40: (
        "3D_Printer_Housing/v19_Apple_Sensor_Pod_5000mAh/19_cross_section_view.png",
        "그림 40. 5,000mAh 대용량 파우치 배터리(JRF PL105568) 수납을 위해 외경을 100mm로 확장한 사과 센서팟(v19) 단면도",
    ),
    41: (
        "3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_boss_fix_comparison.png",
        "그림 41. 3D 프린팅 슬라이서 검수 중 발견된 내부 기둥 공중 단차(좌: 수정 전)와 곡면 외벽 100% 일체화 해결 결과(우: 수정 후)",
    ),
    42: (
        "scratch/notebook_captures/cap_day42_scanner_firmware_fix.png",
        "그림 42. 스마트 QR 스캐너 펌웨어(qr_scanner_module/src/main.cpp) 트리거 핀(GPIO 25) 및 GM77 UART 제어 코드 검증",
    ),
    43: (
        "scratch/notebook_captures/step5_consumer_box77_trace.png",
        "그림 43. get_columns() 및 A12 PK 충돌 패치 후 상자 #77의 수확~출하(A00~A15) 전 공정이 완주된 소비자 타임라인 실증 화면",
    ),
    44: (
        "scratch/notebook_captures/cap_day44_multitruck_rds_summary.png",
        "그림 44. HiveMQ 클라우드 브로커 및 차량별 독립 토픽(truck01~04) 분리에 따른 AWS RDS 단말별 수집 패킷·최고속도 집계",
    ),
    45: (
        "scratch/notebook_captures/cap_day45_hotplug_recovery.png",
        "그림 45. 주행 진동으로 인한 I2C 일시 순단(0.0°C) 직후 펌웨어 자동 재초기화 루틴이 즉각 정상 계측을 복구한 실측 그래프",
    ),
    46: (
        "3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/21_exploded_view.png",
        "그림 46. 조립 유격을 유발하던 중간 배터리 트레이를 제거하고 전·후면 2피스 직결 구조로 재설계한 v21 센서팟 분해도",
    ),
    47: (
        "scratch/stepped_cross_correct.png",
        "그림 47. v21 보강 날개와 GPS 모듈 간 7.16mm 물리 간섭을 완벽히 회피한 1.5cm 단차형(Stepped) 스탠드오프 단면 검증",
    ),
    48: (
        "3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/21_standoff_wall_zoom.png",
        "그림 48. 스탠드오프 보강 리브를 대각선에서 상·하(천장/바닥) 외벽 수직 직결 구조로 변경한 내부 확대 렌더링",
    ),
    49: (
        "3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/KakaoTalk_20261015_114727151.jpg",
        "그림 49. 신도리코 3DWOX로 출력한 노란색 v21 전면 쉘 내부에 실물 CarrierBoard(Beetle C6·BH1750·SW1·GPS)를 체결한 실제 사진",
    ),
    50: (
        "3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/KakaoTalk_20261015_114740653.jpg",
        "그림 50. 3D 프린팅된 보라색 후면 쉘 크래들 내부에 5,000mAh 대용량 리튬폴리머 배터리를 실장하여 공차를 점검한 실제 촬영 사진",
    ),
    51: (
        "scratch/notebook_captures/step4_coldchain_truck02.png",
        "그림 51. 02호차(carrier-c6-02) 야간 도심 주행 실증(484건, 최고 74km/h, 최대 5.41G 충격) 통합 관제 대시보드 구동 캡처",
    ),
    52: (
        "scratch/notebook_captures/cap_day52_truck02_daytime_split.png",
        "그림 52. 02호차 주간 왕복 주행에서 71분 장기 정차 공백을 감지하여 편도(199건)·복귀(41건) 세션을 자동 분리한 RDS 실측 결과",
    ),
    53: (
        "scratch/notebook_captures/cap_day53_ec2_daemon_code_log.png",
        "그림 53. PC 대시보드 종료 상태에서도 24시간 무인 적재를 수행하는 AWS EC2 수집 데몬(mqtt_to_mysql_daemon.py) 핵심 구조",
    ),
    54: (
        "scratch/notebook_captures/cap_day54_ghost_shock_fix.png",
        "그림 54. I2C 읽기 실패 시 스택 미초기화 쓰레기값에 의한 유령 충격 패치 코드(carrier_board_mqtt.cpp) 및 중복 적재 차단 검증",
    ),
    55: (
        "scratch/notebook_captures/cap_day55_truck04_telemetry.png",
        "그림 55. 04호차(carrier-c6-04) 야간 주행(395건) 및 장거리 고속 주행(1,518건, 최고 109.1km/h) AWS RDS 무인 수집 결과",
    ),
    56: (
        "scratch/notebook_captures/cap_day56_v17_gcode_layers.png",
        "그림 56. 실물 스캐너 좌측 하우징 슬라이싱 파일(17_qr_scanner_housing_left_half.gcode) 파이썬 툴패스 및 레이어 분포 검증",
    ),
    57: (
        "3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_cradle_bottom_fix_comparison.png",
        "그림 57. 배터리 안착부 하단 아치형 공중 틈새 발생 문제(좌)와 바닥 외벽 100% 솔리드 일체화 보강 결과(우) 비교",
    ),
    58: (
        "3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/22_print_layout_view.png",
        "그림 58. 사과 고유의 100% 구형 외관을 보존하기 위해 확정한 v22 전·후면 쉘 Dome-Up(사과 껍질 위쪽) 출력 베드 배치도",
    ),
    59: (
        "3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/22_gps_and_magnet_zoom.png",
        "그림 59. v22 내부 GPS 세라믹 안테나 전용 수납 포켓 및 열수축 공차를 반영한 네오디뮴 자석 보스 확대 렌더링",
    ),
    60: (
        "3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/KakaoTalk_20261015_114727151_01.jpg",
        "그림 60. 실물 가조립 중 고정 포켓 부재로 외부로 노출되었던 ATGM336H GPS 세라믹 패치 안테나 근접 촬영 사진(전용 홀더 설계 근거)",
    ),
    61: (
        "3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/cadquery_v22/22_cq_preview.png",
        "그림 61. OpenSCAD에서 CadQuery 2.7(OpenCASCADE 정밀 B-Rep 커널)로 전면 이식하여 렌더링한 v22 사과 센서팟 3피스 어셈블리",
    ),
    62: (
        "scratch/notebook_captures/cap_day62_cadquery_step_audit.png",
        "그림 62. CadQuery 스크립트 일괄 빌드 실행을 통한 정밀 STEP 원본 및 3DWOX 슬라이서용 STL 치수·바닥 밀착(Z_min=0) 검증 출력",
    ),
    63: (
        "scratch/notebook_captures/cap_day63_stl_z0_cross_section.png",
        "그림 63. 실제 생성된 Front/Rear Shell STL 메쉬의 중심 단면(Y≈0) 파싱 결과 — 내부 기둥 베드 직결(Z=0.00mm)로 원피스 서포트 제거",
    ),
    64: (
        "scratch/notebook_captures/cap_day64_bayonet_vent_stl.png",
        "그림 64. 네오디뮴 자석을 대체한 4점 원형 베요넷 회전 잠금(Bayonet Twist-Lock) 러그 및 상·하단 굴뚝형 자연대류 통풍구 STL 투영",
    ),
    65: (
        "scratch/notebook_captures/cap_day65_bug_audit_exec.png",
        "그림 65. 클라우드 데몬·펌웨어·대시보드 전 소스코드 대상 정적 진단 실행 결과 — 상용화 전 해결할 8대 세부 결함 목록",
    ),
    66: (
        "scratch/notebook_captures/cap_day66_korea_coldchain_chart.png",
        "그림 66. 국내 과실류 유통 경로 비중(도매시장 경유 ~51%)과 본 연구 AWS RDS 실측 세션별 최고 상온 노출 온도 정량 대조 차트",
    ),
    67: (
        "scratch/side_by_side_bottom.png",
        "그림 67. 50×50mm CarrierBoard Bottom CAD 설계도와 실제 조립·운용된 센서노드 하드웨어 정방향 실물 대조 검증",
    ),
    68: (
        "scratch/notebook_captures/cap_day68_8month_milestone_summary.png",
        "그림 68. 8개월간(2026.03~11) 실제 Git 월별 커밋 추이 및 AWS RDS 누적 무유실 수집 레코드(31개 세션, 6,500+건) 최종 결산",
    ),
}
