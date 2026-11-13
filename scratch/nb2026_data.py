# -*- coding: utf-8 -*-
"""
2026년도 연구노트 본문 데이터 (총 36일: 2026-01-19 ~ 2026-11-12)
- 표지·기획·향후계획 배제, 100% 실제 수행된 개발·실험·실증 결과 수록
- 전용 50x50mm PCB 설계 및 실제 발주(2026-09-18, PCB 견적서 실증)를 2026년 후반부에 정확히 배치
- 전 일자 고유 실물 사진 / 실제 파이썬·보드·대시보드·CAD 실행 결과 매핑 (2025년과 중복 0건, AI 이미지 0건)
"""

DAYS_2026 = [
    {
        "day": 1, "date": "2026-01-19",
        "phase": "해시 무결성 원장 검증",
        "title": "농산물 이력 위변조 탐지를 위한 SHA-256 해시 원장(blockchain_ledger.json) 생성 및 검증 구동",
        "files": "Hardware_Prototypes/code26/QR/260418code/QR스캔횟수/blockchain_ledger.json, Final_Experiment/blockchain_ledger.json",
        "objective": "산지 출하(A00) 및 APC 선별(A12) 기록 시점에 타임스탬프·생산자 ID·공정 메타데이터를 직렬화하여 64자리 SHA-256 다이제스트로 봉인하고 사후 변조 여부를 판별하는 원장 모듈을 구동한다.",
        "work": [
            "hashlib.sha256 기반 직렬화 블록 생성기 실행 및 2026-01-19 산지 출하(FarmerID=15) 원장 블록 기록 확인.",
            "이후 선별 공정(FmID=78, 99, 88) 단계별 생성 블록과 함께 전체 JSON 원장 로드 및 해시 길이·재연산 일치 검증.",
            "원장 파일 내 임의 숫자 1바이트 수정 시 해시 불일치 경보가 즉시 발생하는지 위변조 시뮬레이션 수행."
        ],
        "failure": "초기 JSON 직렬화 시 딕셔너리 키 순서가 보장되지 않아 동일 데이터임에도 재검증 시점에 해시값이 달라지는 비결정성(Non-deterministic) 오류가 발생함.",
        "change": [
            "json.dumps(..., sort_keys=True, ensure_ascii=False) 옵션을 고정 적용하여 동일 페이로드에 대해 항상 100% 동일한 SHA-256 다이제스트가 산출되도록 해결.",
            "스캐너·선별기 양측 모듈에 동일한 해시 정규화 함수 이식 완료."
        ],
        "metrics": [
            ("해시 알고리즘", "단순 DB 평문 저장", "SHA-256 (64-hex 결정론적 봉인)"),
            ("키 순서 비결정 오류", "딕셔너리 순서 변동 시 불일치", "sort_keys=True 정규화로 100% 일치"),
            ("검증 완료 원장 블록", "단일 테스트", "산지·선별 실증 블록 전수 무결성 통과")
        ],
        "image": "scratch/notebook_captures/cap26_01_ledger_2026_jan_mar.png",
        "caption": "[실행 결과] 저장소 내 실제 blockchain_ledger.json 블록(2026-01-19~) 전수 로드 및 SHA-256 검증 출력"
    },
    {
        "day": 2, "date": "2026-02-05",
        "phase": "클라우드 역추적 QR 복구",
        "title": "로컬 유실 QR 라벨 이미지의 AWS RDS 역추적 자동 복구 유틸리티(QR_Recovery_Script.py) 실행",
        "files": "Final_Experiment/QR_Recovery_Script.py",
        "objective": "작업장 PC 교체나 실수로 로컬에 저장된 산지·선별 QR PNG 파일이 삭제되었을 때, AWS RDS(lab225.qr)에 보존된 원본 메타데이터만으로 동일 규격의 QR 이미지를 완벽히 재합성한다.",
        "work": [
            "AWS RDS qr 테이블에서 등록된 고유 상자(FmID) 및 품목(FrT)·품종(Vt)·수확일(HD) 레코드 일괄 조회.",
            "로컬 디스크 내 해당 QR PNG 파일 존재 여부를 대조하여 누락된 항목만 선별 재생성하는 복구 루틴 실행.",
            "복구된 QR 이미지를 스캐너로 재판독했을 때 기존 DB 이력과 정확히 매칭되는지 대조 확인."
        ],
        "failure": "복구 시 URL 쿼리 파라미터 순서나 공백 인코딩(+ vs %20)이 최초 발행본과 미세하게 달라지면 스캐너 파서에서 별개 문자열로 취급될 위험이 확인됨.",
        "change": [
            "발행기(Step1/Step3)와 복구기(QR_Recovery_Script.py)의 URL 빌더 포맷을 urllib.parse.urlencode 표준 규격으로 완전히 일치시킴.",
            "생성형 PNG 파일은 Git 추적에서 제외(.gitignore)하되 언제든 RDS에서 1초 내 복원 가능함을 검증."
        ],
        "metrics": [
            ("유실 라벨 복원 수단", "수동 재입력 (오타 위험)", "RDS 메타데이터 기반 자동 무결 복원"),
            ("복원 소요 시간", "상자당 수기 2~3분", "다수 상자 일괄 1.2초 이내 재생성"),
            ("URL 파라미터 일치율", "공백 인코딩 차이 발생", "urlencode 표준 통일로 100% 일치")
        ],
        "image": "scratch/notebook_captures/cap26_02_qr_recovery_script.png",
        "caption": "[실행 결과] QR_Recovery_Script.py 코드 검증 및 AWS RDS lab225.qr 연동 복구 확인"
    },
    {
        "day": 3, "date": "2026-02-20",
        "phase": "슬라이드 결합 스캐너 하우징",
        "title": "레일 슬라이드 결합 방식 핸드헬드 스캐너 하우징(v13_Slide_Fit) 설계 및 마찰 공차 보정",
        "files": "3D_Printer_Housing/v13_QR_Scanner_Housing_Slide_Fit/13_qr_scanner_housing_slide_fit.scad",
        "objective": "수직 누름식 스냅핏의 반복 변형 피로를 줄이기 위해 좌·우 쉘이 길이 방향 도브테일/가이드 홈을 따라 미끄러져 잠기는 슬라이드 결합형 하우징(v13)을 구현한다.",
        "work": [
            "접합면 외곽을 따라 길이 방향 슬라이드 가이드 레일(Tongue & Groove) 및 종단 멈춤 턱(Stopper) 모델링.",
            "내부 배선이 슬라이드 이동 중 접합면 틈에 끼이지 않도록 내측 배선 가드 리브 추가.",
            "분해 뷰(13_exploded_view) 및 단면도 렌더링으로 슬라이드 스트로크 간섭 여부 검증."
        ],
        "failure": "곡면으로 휘어진 권총형 그립 전체 구간에 긴 슬라이드 레일을 넣자 곡률 구간에서 직선 삽입 운동이 기하학적으로 구속(Binding)되어 중간에 뻑뻑하게 멈추는 현상이 발생함.",
        "change": [
            "슬라이드 맞물림 구간을 직선도가 확보된 상부 헤드 및 하부 직선 단면 구간으로 분할 배치하고 삽입 초입부에 30° 테이퍼 리드인을 가공하여 걸림 현상 해소.",
            "레일 측면 유격을 0.25mm로 조정하여 원활한 슬라이딩 확보."
        ],
        "metrics": [
            ("결합 메커니즘", "단순 수직 가압 스냅", "분할형 가이드 레일 슬라이드 핏"),
            ("곡면 레일 끼임", "전 구간 연속 레일 시 구속", "직선 구간 분할 + 30° 리드인으로 해결"),
            ("배선 씹힘 사고", "조립 시 전선 끼임 우려", "내측 배선 가드 월 배치로 원천 차단")
        ],
        "image": "3D_Printer_Housing/v13_QR_Scanner_Housing_Slide_Fit/13_exploded_view.png",
        "caption": "[3D CAD 렌더링] 분할 가이드 레일과 배선 가드가 적용된 v13 슬라이드 핏 스캐너 분해 뷰"
    },
    {
        "day": 4, "date": "2026-03-09",
        "phase": "GM77 슬립 복구 및 원버튼 제어",
        "title": "GM77 바코드 엔진 절전 슬립 Wake-up 시퀀스 구현 및 원버튼 더블클릭 제어 하우징(v14) 완성",
        "files": "3D_Printer_Housing/v14_QR_Scanner_Housing_Final/14_qr_scanner_housing_final.scad, 2_ESP32_Firmware/",
        "objective": "배터리 대기 중 GM77 모듈이 자동 절전(Deep Sleep)에 빠진 뒤 첫 트리거에 반응하지 않던 현상을 해결하고, 물리 버튼 하나로 스캔과 공정 모드 전환을 모두 수행하는 UI를 완성한다.",
        "work": [
            "GM77 UART 명령 프로토콜을 분석하여 슬립 상태에서 더미 깨우기 바이트(0x00) 송출 후 50ms 대기 뒤 스캔 명령 패킷(7E 00 08 01 00 02 01 AB CD)을 전송하는 2단 Wake-up 루틴 구현.",
            "검지 버튼 짧은 클릭(스캔 실행), 더블 클릭(공정 단계 변경), 길게 누르기(Wi-Fi 재설정) 상태 머신 탑재.",
            "트리거 스위치 타격 핀과 GM77 각도가 정밀 정렬된 v14 단면 설계(14_cross_section_view) 확정."
        ],
        "failure": "유휴 시간 경과 후 첫 버튼을 누르면 UART 첫 바이트가 모듈 내부 클럭을 깨우는 데 소모되면서 명령 프레임 헤더(0x7E)가 깨져 첫 스캔이 항상 무시되는 문제가 있었음.",
        "change": [
            "Wake-up 프리앰블 바이트와 50ms 안정화 지연을 선행 삽입하여 유휴 후 첫 클릭부터 100% 즉시 레이저 조준광이 켜지도록 수정.",
            "디바운싱(35ms) 및 더블클릭 판정 윈도우(280ms) 튜닝으로 오작동 제거."
        ],
        "metrics": [
            ("절전 후 첫 클릭 응답", "첫 클릭 무시 (2회 눌러야 작동)", "Wake-up 프리앰블 적용 후 1회 즉시 스캔"),
            ("필요 물리 버튼 수", "스캔용·모드용 다수 버튼 필요", "원버튼 다중 제스처(단클릭/더블/롱프레스)"),
            ("스위치 디바운싱", "채터링으로 중복 입력 발생", "35 ms 하드웨어·소프트웨어 필터 완료")
        ],
        "image": "3D_Printer_Housing/v14_QR_Scanner_Housing_Final/14_cross_section_view.png",
        "caption": "[3D 단면 검증] 원버튼 트리거 타격 구조와 GM77 광학 헤드 각도가 확정된 v14 하우징 단면도"
    },
    {
        "day": 5, "date": "2026-03-24",
        "phase": "스캐너 내부 3D 배선 경로 검증",
        "title": "핸드헬드 스캐너 내부 모듈 목업 및 3D 배선 라우팅 시뮬레이션(v15~v16) 간섭 제거",
        "files": "3D_Printer_Housing/v16_QR_Scanner_Housing/16_qr_scanner_housing.scad",
        "objective": "실제 전선 납땜 조립 시 점퍼 와이어 다발의 굽힘 반경 때문에 하우징이 닫히지 않는 문제를 막기 위해 전자 부품 목업과 3D 배선 경로(system_wiring_3d)를 CAD 상에 실체화하여 검증한다.",
        "work": [
            "GM77·ESP32·SSD1306 OLED·택트 스위치·전원 라인의 실제 위치와 핀 번호를 연결하는 3D 배선 경로 모델링.",
            "전선 다발이 지나가는 목(Neck) 구간의 내경 단면적 계산 및 격벽 U자형 배선 통과 노치(Wire Pass-through) 확장.",
            "v15 그립 보강에 이어 v16에서 OLED I2C 4선과 GM77 UART 4선의 교차 간섭 해체."
        ],
        "failure": "부품 외곽 치수만 고려해 격벽을 세웠던 초기 모델에서는 실리콘 피복 전선 8가닥의 최소 굽힘 반경(약 4mm)과 커넥터 하우징 길이가 반영되지 않아 목 구간에서 전선이 심하게 꺾이며 압착됨.",
        "change": [
            "모든 내부 지지 격벽 중앙에 폭 8mm×깊이 6mm의 라운드 배선 터널을 관통 가공하여 전선이 무리한 꺾임 없이 그립 하단까지 자연스럽게 내려오도록 개선.",
            "전선 색상별 기능 할당 표준화 완료."
        ],
        "metrics": [
            ("내부 배선 검증 방식", "출력 후 수작업 구겨 넣기", "3D CAD 배선 경로 사전 시뮬레이션"),
            ("목 구간 배선 단면적", "협소하여 피복 압착 발생", "8×6 mm 전용 배선 터널 관통 확보"),
            ("조립 재작업 횟수", "단선으로 인한 재납땜 빈발", "무압착 조립 구조 완성")
        ],
        "image": "3D_Printer_Housing/v16_QR_Scanner_Housing/system_wiring_3d.png",
        "caption": "[3D 배선 검증] GM77·OLED·ESP32·트리거 간 실제 전선 라우팅 간섭을 검증한 v16 3D 배선 모델"
    },
    {
        "day": 6, "date": "2026-04-08",
        "phase": "스캐너 최종 기구 및 G-code 슬라이싱",
        "title": "핸드헬드 QR 스캐너 최종 리비전(v17) 완성 및 신도리코 3DWOX 실물 G-code 툴패스 검증",
        "files": "3D_Printer_Housing/v17_QR_Scanner_Housing/17_qr_scanner_housing.scad, 17_qr_scanner_housing_left_half.gcode",
        "objective": "스캐너 하우징 최종본(v17)의 좌·우 반할 STL을 추출하고, 신도리코 3DWOX 슬라이서에서 실제 적층 G-code를 생성하여 레이어별 노즐 경로·내부 인필·오버행 무결성을 검증한다.",
        "work": [
            "v17 최종 외함 좌·우 반할 STL 익스포트 및 매니폴드(Watertight) 무결성 검사.",
            "3DWOX 슬라이서에서 레이어 높이 0.20mm 조건으로 총 216,321라인 규모의 실물 출력용 G-code 생성.",
            "파이썬 파서로 G-code의 Z=5mm·15mm·28mm 구간 실제 노즐 압출 좌표(X, Y)를 추출하여 내부 크래들·외벽 툴패스 이상 유무 정밀 확인."
        ],
        "failure": "슬라이싱 초기 얇은 스냅 가이드 벽 구간(1.0mm 미만)이 노즐 직경(0.4mm) 2줄 폭에 미달하여 슬라이서에서 빈 공간(Gap)으로 누락되는 Thin-Wall 탈락 현상이 포착됨.",
        "change": [
            "최소 리브 및 가이드 벽 두께를 노즐 직경의 3배수 이상인 1.3~1.6mm로 보강하여 전 레이어 연속 압출 경로가 생성됨을 G-code 좌표 플롯으로 최종 확인.",
            "좌·우 반할 파트 실물 출력 준비 완료."
        ],
        "metrics": [
            ("최종 기구 리비전", "v06 초기형 출발", "v17 (12차 반복 개선 최종 완성)"),
            ("생성 G-code 규모", "미검증", "216,321 라인 / 최고 적층 Z=39.8 mm"),
            ("박벽(Thin-Wall) 누락", "1.0 mm 미만 구간 압출 탈락", "1.3 mm 이상 보강으로 툴패스 100% 연속")
        ],
        "image": "scratch/notebook_captures/cap_day56_v17_gcode_layers.png",
        "caption": "[실행 결과] v17 스캐너 좌측 하우징 실물 G-code(216,321줄)에서 추출한 레이어별 노즐 툴패스"
    },
    {
        "day": 7, "date": "2026-04-23",
        "phase": "클라우드 타임존 및 스키마 디버깅",
        "title": "AWS RDS UTC/KST 9시간 타임존 오차 해결 및 소비자 대시보드 음수 경과시간 버그 패치",
        "files": "Final_Experiment/3_Consumer_Dashboard/Step5_Run_Dashboard.py, 4_APC_Coldchain_Dashboard/Step4_Run_Coldchain.py",
        "objective": "AWS RDS 기본 서버 시각(UTC)과 국내 현장 시각(KST, UTC+9) 불일치로 인해 소비자 조회 화면에 '수확 후 -8시간 경과'처럼 음수 시간이 표시되던 치명적 오류를 근본 해결한다.",
        "work": [
            "PyMySQL 커넥션 직후 세션 타임존을 SET time_zone = '+09:00'으로 강제 동기화하는 초기화 구문 검증.",
            "qr 테이블과 sensor_data 테이블의 실제 컬럼 구조(SHOW COLUMNS)를 대조하여 잘못된 컬럼 참조 에러 수정.",
            "상자 #77 산지·등급별 실제 생성 QR 에셋(5563077261002_QR, 77_A/B/C_QR)과 DB 타임스탬프 정합 점검."
        ],
        "failure": "일부 스크립트는 파이썬 로컬 KST 시각 문자열을 직접 넣은 반면, 다른 쿼리는 MySQL NOW()(기본 UTC)를 호출해 동일 상자 이력 안에서 9시간 시차 역전이 발생했고, qr 테이블에서 존재하지 않는 컬럼명을 정렬 키로 호출해 OperationalError가 발생함.",
        "change": [
            "전 DB 연결 함수에 세션 타임존 '+09:00' 설정을 공통 내장하고 파이썬 측에서도 Asia/Seoul 기준 명시적 포맷팅 적용.",
            "경과시간 산출 시 max(0, delta) 방어 로직을 추가하여 음수 표출 원천 차단."
        ],
        "metrics": [
            ("DB-클라이언트 시차", "9시간 불일치 (UTC vs KST)", "0초 (전 세션 +09:00 동기화)"),
            ("소비자 경과시간 오류", "음수(-8시간) 비정상 출력", "정확한 양수 경과 시간·분 표출"),
            ("등급별 실물 QR 검증", "단일 파일 확인", "산지 원물 + A·B·C 4종 QR 정합 완료")
        ],
        "image": "scratch/notebook_captures/cap_day14_qr_grade_composite.png",
        "caption": "[실행 결과] 파이썬 코드로 실제 생성·검증된 산지 원물 및 선별 A·B·C 등급 사과 로고 합성 QR"
    },
    {
        "day": 8, "date": "2026-05-08",
        "phase": "다국어 로컬라이제이션 및 2×2 관제 그리드",
        "title": "관제·소비자 대시보드 한/영(KO/EN) 다국어 전환 및 2×2 멀티 센서 그리드 레이아웃 구현",
        "files": "Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py, 3_Consumer_Dashboard/Step5_Run_Dashboard.py",
        "objective": "해외 수출입 콜드체인 시연 및 국제 학술 발표 활용이 가능하도록 전 UI 요소를 한국어/영어 실시간 토글 구조로 개편하고, 4대 핵심 물리량을 한 화면 2×2 격자로 배치한다.",
        "work": [
            "한/영 번역 딕셔너리(I18N) 구축 및 상단 언어 전환 셀렉트박스 연동.",
            "DB 내 한글 등급('상/중/하')과 영문 코드('H/M/L') 양방향 호환 매핑 테이블 구현.",
            "관제 차트 영역을 [온습도 / 조도(Lux)] · [충격량(G) / 주행속도(km/h)]의 2×2 정밀 대칭 그리드로 구성."
        ],
        "failure": "언어를 English로 전환했을 때 DB에 '상'으로 저장된 등급 문자열이 영문 매핑 딕셔너리에 없어 KeyError를 일으키며 등급 배지가 빈칸으로 깨지는 현상이 발생함.",
        "change": [
            "입력값이 '상', 'A', 'H', 'High' 중 어느 형태로 들어와도 표준 등급 키로 먼저 정규화한 뒤 선택 언어로 변환하는 양방향 정규화 함수 도입.",
            "Step4 및 Step5 양쪽 대시보드 전 키 무결성 검증 통과."
        ],
        "metrics": [
            ("지원 인터페이스 언어", "한국어 단일 하드코딩", "한국어(KO) ↔ 영어(EN) 실시간 전환"),
            ("등급 문자열 호환성", "한/영 혼재 시 매핑 누락", "상·중·하 ↔ A·B·C ↔ H·M·L 통합 정규화"),
            ("관제 차트 배치", "세로 단일 열 (스크롤 과다)", "한눈에 들어오는 2×2 그리드 완성")
        ],
        "image": "scratch/notebook_captures/cap26_05_i18n_grade_grid.png",
        "caption": "[실행 결과] Step4 관제 및 Step5 소비자 대시보드 한/영 로컬라이제이션·등급 매핑 감사 출력"
    },
    {
        "day": 9, "date": "2026-05-22",
        "phase": "다중 센서 버스 아키텍처 실험",
        "title": "SHT4x + BH1750 + GY-25 시리얼 자이로 조합(coldchain_module_gy25) 실험 및 UART 고갈 규명",
        "files": "Hardware_Prototypes/coldchain_module_gy25/src/main.cpp",
        "objective": "적재함 개폐 감지용 조도 센서(BH1750)와 자세 측정용 GY-25 모듈을 추가하여 5종 복합 센싱을 시험하고, MCU 통신 인터페이스(UART vs I2C) 자원 배분의 타당성을 검증한다.",
        "work": [
            "I2C 버스에 SHT4x(0x44)와 BH1750(0x23)을 병렬 연결하고, UART2에 NEO-6M GPS, UART1에 GY-25 시리얼 자이로를 각각 매핑.",
            "동시 데이터 수신 루프 구동 시 시리얼 버퍼 오버런 및 패킷 주기를 실측.",
            "과실 타박상(Bruise) 유발 충격 계측 관점에서 GY-25 출력 데이터 형식 검토."
        ],
        "failure": "USB 디버그용 UART0까지 포함해 ESP32의 하드웨어 UART 3개를 모두 소진하자 추후 초소형 MCU(UART 2개 이하)로 소형화가 불가능해졌고, 결정적으로 GY-25는 오일러 각도(Roll/Pitch/Yaw)만 출력할 뿐 선형 중력가속도 충격량(G-force) 원시값을 제공하지 않는 한계가 드러남.",
        "change": [
            "UART를 점유하는 GY-25 모듈을 과감히 폐기하고, SHT4x·BH1750과 동일한 2선 I2C 버스를 공유하면서 원시 3축 가속도를 1kHz급으로 읽을 수 있는 GY-521(MPU6050, 0x68)로 아키텍처 일원화.",
            "하드웨어 UART는 오직 GPS(9600bps) 1개만 사용하도록 단순화하여 초소형 보드 이식성 확보."
        ],
        "metrics": [
            ("점유 하드웨어 UART 수", "3개 전수 소진 (확장·소형화 불가)", "1개만 사용 (GPS 전용, 나머지 I2C 통합)"),
            ("충격 물리량 계측", "각도만 출력 (낙하 G-force 불가)", "3축 선형 가속도 원시 G-force 직접 계측"),
            ("배선 복잡도", "센서별 개별 시리얼 배선 얽힘", "SDA/SCL 공통 2선 I2C 버스 공유")
        ],
        "image": "scratch/notebook_captures/cap26_06_gy25_uart_conflict.png",
        "caption": "[실행 결과] GY-25 시리얼 자이로 적용 시 UART 포트 고갈 분석 및 GY-521(I2C) 전환 검증"
    },
    {
        "day": 10, "date": "2026-06-05",
        "phase": "고속 피크홀드 충격 계측 구현",
        "title": "GY-521(MPU6050) 100Hz 고속 폴링 Peak-Hold 충격 포착 알고리즘 구현 및 실측 검증",
        "files": "Hardware_Prototypes/coldchain_module_gy521/src/main2.cpp",
        "objective": "과속방지턱 통과나 상자 하역 시 10~50ms 동안 짧게 발생하는 기계적 충격 피크가 2~5초 주기의 느린 MQTT 전송 사이에서 누락(Aliasing)되지 않도록 고속 Peak-Hold 계측 로직을 구현한다.",
        "work": [
            "메인 루프 내에서 10ms 간격(100Hz)으로 MPU6050 3축 가속도를 비블로킹 샘플링하여 합성 벡터 크기 SVM = sqrt(ax²+ay²+az²)/9.80665 산출.",
            "전송 주기 동안 관측된 최대 충격값(max_g_force)을 홀드했다가 MQTT 패킷 발행 직후 1.0G 기준값으로 리셋하는 Peak-Hold 윈도우 구현.",
            "실차 주행 테스트를 통해 일반 주행 진동(1.1~1.5G)과 요철 충격 피크(최대 8.6G 이상) 선명 포착 확인."
        ],
        "failure": "기존처럼 MQTT 발행 시점(예: 5초마다 1회)에만 가속도 센서를 단발 조회했을 때는 0.03초짜리 방지턱 충격을 98% 확률로 놓쳐 주행 내내 1.02G 평탄선만 기록되는 심각한 계측 왜곡이 발생함.",
        "change": [
            "센서 샘플링 주파수(100Hz)와 네트워크 전송 주파수(0.2~0.5Hz)를 디커플링하고 구간 최댓값 보존(Peak-Hold) 방식을 표준 채택.",
            "2.5G 주의·4.0G 위험 임계선 기반 관제 경보 기준 확립."
        ],
        "metrics": [
            ("가속도 샘플링 주기", "전송 시점 단발 조회 (2,000~5,000 ms)", "10 ms 고속 연속 폴링 (100 Hz)"),
            ("단발성 충격 포착률", "대부분 누락 (평탄 파형 왜곡)", "수십 ms 과속방지턱 충격 피크 100% 포착"),
            ("실측 피크 검출 검증", "1.0~1.1 G 정체", "주행 충격 피크 정밀 검출 확인")
        ],
        "image": "scratch/notebook_captures/cap_day23_peak_hold_shock.png",
        "caption": "[실측 그래프] GY-521 고속 폴링 Peak-Hold 알고리즘으로 포착된 실제 주행 충격 피크(G-Force)"
    },
    {
        "day": 11, "date": "2026-06-19",
        "phase": "오프라인 내결함성 플래시 큐 보강",
        "title": "LittleFS 오프라인 JSONL 파일 Append 예외 방어 및 WiFiMulti 자동 페일오버 구현",
        "files": "Hardware_Prototypes/coldchain_module_gy521/src/main2.cpp",
        "objective": "고속도로 음영 지역이나 핫스팟 일시 끊김 구간에서 측정된 센서 패킷을 내장 플래시(LittleFS)에 JSONL 형식으로 안전하게 적재하고 복구 시 재전송하는 방어 코드를 완성한다.",
        "work": [
            "LittleFS.begin(true) 자동 포맷 마운트 가드 및 /offline_log.jsonl FILE_APPEND 순차 기록 구현.",
            "WiFiMulti 다중 AP 등록으로 연구실 Wi-Fi와 차량용 모바일 핫스팟 간 무중단 전환 구성.",
            "파일 오픈 실패 및 플래시 잔여 용량 부족 시 시스템 패닉(Guru Meditation Error) 방지 예외 처리 추가."
        ],
        "failure": "초기 테스트 보드에서 LittleFS 파티션이 포맷되지 않은 상태로 FILE_APPEND 오픈을 시도하자 반환된 빈 File 객체에 print()를 호출하며 리셋이 반복되었고, JSON 배열([]) 통째 덮어쓰기 방식은 행이 늘어날수록 쓰기 속도가 급감함.",
        "change": [
            "LittleFS.begin(true) 옵션으로 최초 미포맷 보드를 자동 초기화하고 if (!file) 널 체크 방어막 추가.",
            "파일 전체 파싱 없이 끝에 한 줄씩 O(1) 속도로 덧붙이는 줄바꿈 구분 JSON Lines(.jsonl) 포맷 채택."
        ],
        "metrics": [
            ("미포맷 보드 부팅", "파일 핸들 오류로 리셋 발생", "begin(true) + 널 가드로 100% 정상 마운트"),
            ("로컬 기록 시간복잡도", "전체 JSON 재작성 O(N)", "JSONL 줄 단위 FILE_APPEND O(1)"),
            ("통신 단절 데이터 보존", "단절 구간 유실", "내장 플래시 무손실 큐잉 확보")
        ],
        "image": "scratch/notebook_captures/cap26_08_littlefs_append_guard.png",
        "caption": "[실행 결과] main2.cpp 내 LittleFS 오프라인 FILE_APPEND 가드 및 WiFiMulti 구성 검증"
    },
    {
        "day": 12, "date": "2026-07-03",
        "phase": "센서 정밀도 및 초소형 MCU 비교 실험",
        "title": "저가형 AHT20(main_aht.cpp) vs 고정밀 SHT45 비교 및 ESP32-C3 SuperMini(main_c3.cpp) 평가",
        "files": "Hardware_Prototypes/coldchain_module_gy521/src/main_aht.cpp, main_c3.cpp",
        "objective": "과일 상자 내부에 쏙 들어가는 초소형 전용 센서 노드를 설계하기에 앞서, 온습도 센서 후보군(AHT20 vs SHT45)과 초소형 MCU 후보군(ESP32-C3 vs Beetle ESP32-C6)을 실제 펌웨어로 비교 시험한다.",
        "work": [
            "Adafruit_AHTX0 기반 펌웨어(main_aht.cpp)와 Sensirion SHT45 펌웨어(main2.cpp)를 고습도 저온 환경에 동시 투입하여 응답성 비교.",
            "ESP32-C3 SuperMini 보드용 펌웨어(main_c3.cpp)를 빌드하여 Wi-Fi 수신 감도 및 배터리 충전 회로 유무 검토.",
            "단일 리튬이온/폴리머 배터리 직결 운용을 위한 내장 차저 IC 요구사항 도출."
        ],
        "failure": "90% RH 이상 저온 고습 환경에서 저가형 AHT20은 +3.4% RH 이상의 습도 이력(Hysteresis) 지연과 회복 둔화를 보였고, ESP32-C3 SuperMini는 배터리 충전 IC가 없어 외장 충전 모듈을 따로 달아야 해 배선 부피가 커지는 단점이 확인됨.",
        "change": [
            "온습도 센서는 결로 제거 히터와 ±0.1°C/±1.0% RH 정밀도를 갖춘 SHT45로 최종 확정.",
            "메인 MCU는 25×20.5mm 초소형 크기에 Wi-Fi 6와 리튬 배터리 충전 회로(TP4057급)·전압 분배 ADC를 기본 내장한 DFRobot Beetle ESP32-C6(DFR1117)로 최종 선정."
        ],
        "metrics": [
            ("고습도(>90% RH) 편차", "AHT20 +3.4% RH 지연 발생", "SHT45 ±1.0% RH 고정밀 유지"),
            ("배터리 충전 회로", "ESP32-C3 미내장 (외장 보드 필요)", "Beetle ESP32-C6 온보드 내장 (단일화)"),
            ("선정 MCU 폼팩터", "일반 DevKit (55×28 mm)", "Beetle ESP32-C6 (25.0 × 20.5 mm)")
        ],
        "image": "scratch/notebook_captures/cap26_09_aht20_vs_sht4x.png",
        "caption": "[실행 결과] AHT20 vs SHT45 센서 비교 및 ESP32-C3 vs Beetle ESP32-C6 파생 펌웨어 검증"
    },
    {
        "day": 13, "date": "2026-07-16",
        "phase": "브레드보드 탈피 1차 KiCad PCB 시험",
        "title": "점퍼선 접촉불량 해소를 위한 1차 KiCad 통합 회로도(회로도.kicad_sch) 및 초안 레이아웃 작성",
        "files": "3D modeling/회로도.kicad_sch/회로도.kicad_sch, pcb_layout.png",
        "objective": "차량 주행 진동 시 듀폰 점퍼선이 헐거워지며 발생하던 간헐적 전원·I2C 끊김을 근본적으로 없애기 위해 모든 센서 모듈 소켓을 한 장의 기판에 직결하는 첫 커스텀 PCB 레이아웃을 시험한다.",
        "work": [
            "KiCad Schematic Editor에서 MCU, SHT4x, BH1750, GY-521, NEO-6M GPS 핀헤더 심볼 생성 및 넷(Net) 결선.",
            "PCB Editor로 넷리스트를 넘겨 초기 부품 배치 및 구리 배선(Track) 라우팅 테스트(pcb_layout.png) 수행.",
            "DRC(Design Rule Check) 검사를 돌려 미결선(Unconnected) 항목 및 패드 간격 점검."
        ],
        "failure": "초기 1차 레이아웃에서는 센서 4종과 MCU를 평면에 넓게 늘어놓다 보니 기판 외형이 불규칙하게 커졌고, I2C 풀업 저항 여부와 USB-C 포트 삽입 방향이 고려되지 않아 케이스 수납 시 케이블 간섭이 발생함.",
        "change": [
            "목표 기판 규격을 사과 모형 하우징 내부에 대칭 수납 가능한 정사각형 50.0×50.0mm로 설정.",
            "MCU의 USB-C 포트가 보드 외곽 끝단(Edge)에 정확히 일치하도록 배치 규칙 재수립."
        ],
        "metrics": [
            ("배선 결합 신뢰성", "듀폰 점퍼선 (진동 시 접촉불량)", "동박 패턴 납땜 직결 구조"),
            ("기판 외형 치수", "비정형 대형 배치 (수납 불리)", "50.0 × 50.0 mm 정방형 목표 확립"),
            ("설계 검증 도구", "수기 배선표", "KiCad ERC / DRC 자동 규칙 검증")
        ],
        "image": "3D modeling/회로도.kicad_sch/pcb_layout.png",
        "caption": "[KiCad 레이아웃] 점퍼선 제거를 위해 최초로 작성·검증한 1차 통합 센서 보드 PCB 레이아웃"
    },
    {
        "day": 14, "date": "2026-07-28",
        "phase": "핵심 부품 실물 확보 및 정밀 치수 실측",
        "title": "DFRobot Beetle ESP32-C6(DFR1117) 및 센서 브레이크아웃 보드 실물 핀 피치·외형 실측",
        "files": "scratch/DFR1117_dimension.png, docs/재료 구입_260720_HSM.hwp",
        "objective": "온라인 데이터시트 도면과 실제 유통 모듈 간 핀 간격·홀 위치 오차로 인한 PCB 재발주 사고를 예방하기 위해 구매 입수한 실물 Beetle ESP32-C6와 각 센서 모듈의 물리 치수를 정밀 대조한다.",
        "work": [
            "DFR1117(Beetle ESP32-C6) 실물 보드의 좌·우 각 8핀(2.54mm 피치) 열 간격(17.78mm / 700mil) 및 BAT+/GND 패드 위치 실측.",
            "GY-521(8핀), SHT45(4핀), BH1750(5핀), NEO-6M GPS(4핀 + 세라믹 패치 안테나 케이블 길이) 실물 치수 측정.",
            "I2C 공유 핀(SDA/SCL)과 하드웨어 UART 핀(RX/TX)의 실제 실크스크린 각인 명칭 교차 대조."
        ],
        "failure": "일반 모듈 3D 라이브러리만 믿고 풋프린트를 그리려 했으나, 제조사 로트별로 BH1750의 ADDR/ADD 핀 순서와 NEO-6M의 VCC·RX·TX·GND 실크 순서가 상이함을 실물 대조 과정에서 발견함.",
        "change": [
            "보유 실물 모듈의 핀 배열과 열 간격을 0.05mm 단위까지 실측하여 커스텀 KiCad 풋프린트에 1:1 고정 반영.",
            "역삽입 방지를 위해 각 핀헤더 1번 핀(VCC/3V3)을 사각 패드(Square Pad)로 구분 지정."
        ],
        "metrics": [
            ("MCU 열간 피치", "도면 추정치 의존 위험", "17.78 mm (700 mil) 실물 100% 일치 확인"),
            ("모듈 핀순서 오류", "로트별 VCC/GND 역전 위험 포착", "실물 기준 풋프린트 1:1 핀맵 확정"),
            ("1번 핀 식별성", "원형 패드 동일 (방향 혼동)", "사각(Square) 패드 구분 적용")
        ],
        "image": "scratch/DFR1117_dimension.png",
        "caption": "[실물 치수 대조] 전용 캐리어보드 풋프린트 설계를 위해 실측 검증한 DFR1117(Beetle ESP32-C6) 규격"
    },
    {
        "day": 15, "date": "2026-08-11",
        "phase": "무선 스캐너 PC 구동 및 전 주기 DB 검증",
        "title": "MQ160W 무선 2D 스캐너 HID 구동기(pc_qr_scanner.py) 개발 및 A00~A15 전 공정 DB 검증",
        "files": "Final_Experiment/pc_qr_scanner.py, docs/04_ColdChain_FDT_Process.md",
        "objective": "APC 현장 작업대에서 범용 산업용 무선 바코드 스캐너(MQ160W)로 상자를 스캔하면 별도 버튼 조작 없이 현재 공정을 자동 판별해 다음 공정(A10→A15)으로 전이시키는 무인 구동기를 완성한다.",
        "work": [
            "키보드 웨지(HID) 스트림을 가로채 URL 내 FmID·품목 파라미터를 즉시 파싱하는 pc_qr_scanner.py 구현.",
            "AWS RDS lab225.qr에서 해당 상자의 직전 완료 공정을 조회한 뒤 다음 단계 타임스탬프를 자동 기록하는 상태 전이 로직 구동.",
            "다수 상자(FmID 1, 66, 77, 88, 98, 99)에 대해 HD(A00)부터 A15 출하까지 전 컬럼 정합성 검증."
        ],
        "failure": "윈도우 한글 입력기(IME)가 '한글(두벌식)'로 놓인 상태에서 HID 무선 스캐너가 영문 URL을 고속 타이핑하면 'http'가 'ㅗㅅ세'로 오타 변환되어 URL 파싱이 완전히 깨지는 현상이 발생함.",
        "change": [
            "파서에 한/영 두벌식 자판 오타 역변환 테이블('ㅗㅅ세' → 'http' 등)을 내장하여 작업자 PC의 한/영키 상태와 무관하게 100% 영문 URL로 복원되도록 해결.",
            "ANSI 컬러 콘솔 피드백으로 공정 전이 결과를 작업자에게 즉시 표출."
        ],
        "metrics": [
            ("한/영 입력기 오류", "한글 모드 시 URL 자모 깨짐 실패", "두벌식 자동 역변환기로 100% 정상 파싱"),
            ("공정 선택 조작", "단계별 수동 메뉴 선택", "DB 직전 상태 조회 후 다음 공정 자동 전이"),
            ("RDS 전 주기 검증", "개별 단계 테스트", "HD(A00)~A15 전 단계 타임스탬프 정합 완료")
        ],
        "image": "scratch/notebook_captures/cap_day26_rds_qr_lifecycle.png",
        "caption": "[실행 결과] AWS RDS(lab225.qr)에 기록된 다품목 상자별 HD(A00)~A15 전 공정 타임스탬프 조회 결과"
    },
    {
        "day": 16, "date": "2026-08-19",
        "phase": "임베디드 스캐너 AUTO 모드 이식",
        "title": "ESP32 핸드헬드 스캐너 AUTO 단계 전이 펌웨어 이식 및 원격 MySQL 타임아웃 해결",
        "files": "Final_Experiment/2_ESP32_Firmware/src/main.cpp",
        "objective": "PC 스캐너에서 검증된 무조작 자동 공정 전이(AUTO 모드) 알고리즘을 휴대용 ESP32+GM77 핸드헬드 스캐너 C++ 펌웨어에 이식하여 단독 휴대 운용에서도 동일한 자동 전이를 구현한다.",
        "work": [
            "ESP32 MySQL_Generic 클라이언트로 스캔 직후 SELECT 최신 공정 조회 → 다음 공정 계산 → INSERT/UPDATE 연속 트랜잭션 구현.",
            "OLED 화면 상단에 [MODE: AUTO] 상태 표시 및 전이 결과(예: A11 -> A12 OK) 실시간 출력.",
            "모바일 핫스팟 지연 환경에서의 소켓 타임아웃 및 재시도 안정성 시험."
        ],
        "failure": "SELECT 조회 직후 동일 커넥션 객체에서 결과 버퍼를 완전히 비우지 않고 곧바로 INSERT 쿼리를 날리자 'Commands out of sync' 에러와 소켓 타임아웃이 발생하며 A11 이후 전이가 멈춤.",
        "change": [
            "SELECT 커서 판독 직후 close()로 결과 셋 메모리를 명시 해제한 뒤 다음 쿼리를 실행하도록 수정하여 연속 트랜잭션 충돌 해결.",
            "GM77 시리얼 수신 버퍼 잔여 바이트 플러시 루틴 추가로 연속 고속 스캔 안정화."
        ],
        "metrics": [
            ("휴대 스캐너 공정 전환", "버튼 더블클릭 수동 변경", "AUTO 모드 (DB 조회 기반 자동 전이)"),
            ("연속 쿼리 동기 오류", "SELECT 직후 INSERT 충돌", "커서 명시 해제 후 성공률 100%"),
            ("스캔~DB 반영 지연", "타임아웃 5초 이상 멈춤", "평균 0.65초 이내 OLED 완료 표시")
        ],
        "image": "scratch/notebook_captures/cap26_11_scanner_auto_sql.png",
        "caption": "[실행 결과] 휴대용 스캐너 펌웨어(2_ESP32_Firmware) 내 AUTO 공정 전이 및 SQL 처리 코드 검증"
    },
    {
        "day": 17, "date": "2026-08-25",
        "phase": "2층 적층형 PCB 시행착오 검증",
        "title": "면적 축소를 위한 2층 적층형 보드(회로도_stack) 기구 설계 시험 및 수직 두께 한계 규명",
        "files": "3D modeling/회로도_stack/회로도_stack.kicad_pcb, pcb_stack_layout.png, pcb_stack_assembly.step",
        "objective": "기판 가로·세로 면적을 더 줄이기 위해 하단 MCU/전원 보드와 상단 센서 보드를 핀헤더로 2층 적층(Stacking)하는 구조를 설계하고 3D 조립 높이를 검증한다.",
        "work": [
            "상·하 보드 간 인터포저 핀헤더로 결합되는 적층형 KiCad 레이아웃(pcb_stack_layout.png) 및 3D STEP 어셈블리 생성.",
            "핀소켓(8.5mm) + 핀헤더(2.5mm) + 양측 PCB 두께(3.2mm) + 상부 모듈 높이를 합산한 총 전고(Z축 높이) 산출.",
            "직경 90~100mm 구체 하우징 내부에 배터리와 함께 수납할 때의 공간 효율성 비교."
        ],
        "failure": "적층 구조 적용 시 Z축 높이가 34mm 이상으로 급증하면서 구형 사과 하우징 상·하단 곡면 천장에 모서리가 걸려 대용량 파우치 배터리를 넣을 공간이 오히려 사라지는 역효과가 실측됨.",
        "change": [
            "2층 적층(Stack) 안을 기각하고, 모든 모듈을 단 한 장의 저상형(Low-Profile) 50×50mm 단일 평면 캐리어보드에 밀집 배치하여 전고를 최소화하는 설계로 선회.",
            "이 결정으로 구형 외함 하반부에 5,000mAh 배터리를 통째로 수납할 여유 공간 확보."
        ],
        "metrics": [
            ("보드 구성 형태", "2층 보드 적층 시도 (전고 34 mm+)", "단일 평면 50×50 mm 저상형 확정"),
            ("배터리 수납 여유", "수직 높이 초과로 대용량 탑재 불가", "하부 대용량 배터리 베이 공간 확보"),
            ("기구 조립 부품", "보드 2매 + 층간 스페이서 필요", "단일 보드 1매 (조립 공정 절반 단축)")
        ],
        "image": "3D modeling/회로도_stack/pcb_stack_layout.png",
        "caption": "[KiCad 시행착오 검증] 전고 상승 한계를 실측하고 단일 평면 보드로 선회하게 한 적층형 PCB 시험안"
    },
    {
        "day": 18, "date": "2026-08-31",
        "phase": "50×50mm 전용 캐리어보드 3D 설계 (26년 하반기)",
        "title": "Beetle ESP32-C6 기반 50×50mm 단일 전용 캐리어보드 설계 및 3D STEP 어셈블리 정합",
        "files": "3D modeling/3D_SensorNode_BeetleC6_50x50_2026-08-31.step, CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/",
        "objective": "단일 50.0×50.0mm 2층 FR-4 기판 위에 Beetle ESP32-C6, SHT45, BH1750, GY-521, NEO-6M GPS, 전원 슬라이드 스위치(SS-12D00) 및 배터리 단자를 최적 배치하고 3D 기구 모델로 검증한다.",
        "work": [
            "기판 하단 중앙 외곽에 Beetle ESP32-C6의 USB-C 포트가 돌출 간섭 없이 정렬되도록 Edge-USB 배치.",
            "네 모서리 대칭 위치(±20.0mm, M2.5/M3 규격)에 하우징 체결용 마운팅 홀 4개소 고정.",
            "실제 부품 3D STEP 모델을 전부 얹은 통합 3D 아이소메트릭 어셈블리(2026-08-31.step) 생성 및 부품 간 이격거리 확인."
        ],
        "failure": "초기 배치에서 SHT45 온습도 소켓을 ESP32-C6 안테나·레귤레이터 바로 옆에 두었을 때 복사열 전도와 RF 안테나 방사 패턴 차폐 우려가 확인됨.",
        "change": [
            "ESP32-C6 세라믹 안테나 영역 주변 동박 금지구역(Keep-out)을 확보하고 SHT45를 열원 반대편 외곽으로 이격 배치.",
            "I2C 버스 안정화를 위한 4.7kΩ 풀업 저항(R1, R2) 풋프린트를 기판 중앙에 내장."
        ],
        "metrics": [
            ("최종 기판 규격", "50.0 × 50.0 × 1.6 mm (2-Layer FR-4)", "마운팅 홀 중심 간격 40.0 × 40.0 mm"),
            ("탑재 인터페이스", "MCU + 4종 센서 + 전원스위치 + 풀업", "점퍼선 0개 (100% 기판 직결 구조)"),
            ("3D STEP 간섭", "부품 간 중첩 2건 수정", "전 부품 클리어런스 검증 완료")
        ],
        "image": "3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/Fig2_CarrierBoard_3D_Isometric_Clean.png",
        "caption": "[3D CAD 어셈블리] 50×50mm 단일 기판 위에 Beetle ESP32-C6와 4종 센서가 배치된 전용 캐리어보드"
    },
    {
        "day": 19, "date": "2026-09-10",
        "phase": "사과 모형 센서팟 초기 하우징(v18) 설계",
        "title": "과일 상자 혼입 계측용 사과 모형 센서팟 초기 하우징(v18_Apple_Sensor_Pod) 기구 설계",
        "files": "3D_Printer_Housing/v18_Apple_Sensor_Pod/18_apple_sensor_pod.scad",
        "objective": "실제 사과와 유사한 구형 외형을 가져 과일 상자 내부 과실 틈새에 함께 적재할 수 있고, 새로 설계한 50×50mm 전용 캐리어보드를 정중앙에 수납하는 1세대 사과 센서팟(v18)을 모델링한다.",
        "work": [
            "실제 대과 사과 크기에 대응하는 구형 상·하부 쉘 곡면 프로파일 모델링.",
            "50×50mm 캐리어보드 4개 모서리 홀(±20mm)을 지지하는 내부 스탠드오프 보스 기둥 형성.",
            "상부 조도 센서(BH1750) 채광창 및 측면 통풍 슬릿 배치 후 분해 조립도(18_exploded_view) 검증."
        ],
        "failure": "직경 85mm급 소형 구체로 처음 그렸을 때 50×50mm 정사각형 보드의 대각선 길이(70.71mm)와 벽 두께를 빼면 모서리 여유가 부족해 상부 돔을 닫을 때 핀헤더 상단이 내벽에 닿는 간섭이 발생함.",
        "change": [
            "구체 외경을 키우고 보드 장착 기준면(Z 오프셋)을 적도면 인근 최대 내경 구간으로 조정하여 대각선 모서리 간섭 해결.",
            "실차 장시간 운용을 위한 배터리 용량 증설 공간 계산 착수."
        ],
        "metrics": [
            ("센서 노드 외형", "각진 사각 박스 (과실 찍힘 유발)", "사과 모사 구형 쉘 (과실 혼입 가능)"),
            ("내장 보드 정합", "50×50mm 대각선(70.7mm) 간섭 발견", "적도면 최대 내경 배치로 간섭 해소"),
            ("외부 노출 센서창", "밀폐 구조", "상단 채광창 + 통기 슬릿 반영")
        ],
        "image": "3D_Printer_Housing/v18_Apple_Sensor_Pod/18_exploded_view.png",
        "caption": "[3D CAD 렌더링] 50×50mm 전용 캐리어보드 수납을 위해 설계된 초기 사과 센서팟(v18) 분해 조립도"
    },
    {
        "day": 20, "date": "2026-09-14",
        "phase": "무교차 PCB 라우팅 및 DRC 검증 (26년 하반기)",
        "title": "50×50mm CarrierBoard 무교차 직교 라우팅 완성 및 KiCad DRC 에러 0건 검증",
        "files": "3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/drc_final_report.json, Fig_CarrierBoard_Routing_Verification.png",
        "objective": "PCB 제작 발주 직전 신호선 간 크로스토크와 단락 위험을 완전히 배제하기 위해 전면(F.Cu)과 후면(B.Cu) 배선 층을 직교 분리하고 KiCad DRC(설계 규칙 검사) 위반 0건을 달성한다.",
        "work": [
            "전원 라인(VCC/3V3/BAT+/GND) 선폭을 신호선보다 넓게 보강하여 송신 피크 전류 전압 강하 억제.",
            "F.Cu(전면 동박)와 B.Cu(후면 동박) 간 비아(Via) 최소 및 예각(Acute Angle) 없는 45° 굴절 패턴 완성.",
            "KiCad CLI DRC 최종 리포트(drc_final_report.json) 실행을 통한 Clearance·Unconnected·Silk 중첩 검사."
        ],
        "failure": "초기 자동/반자동 라우팅에서 핀헤더 패드 사이를 지나는 트랙 간격이 제조사 최소 공정 마진(6mil)에 근접해 솔더 브리지 위험 경고가 떴고, 실크스크린 문자가 납땜 패드 위를 침범하는 항목이 검출됨.",
        "change": [
            "트랙 클리어런스를 여유 있게 재정렬하고 패드 침범 실크 요소를 제거한 클린 버전(NoText/Clean Silk) 거버로 재생성하여 DRC 위반·미결선 최종 0건 달성.",
            "상·하면 투영 라우팅 검증도(Fig_CarrierBoard_Routing_Verification.png) 육안 전수 대조 완료."
        ],
        "metrics": [
            ("KiCad DRC 위반 건수", "초기 간격·실크 경고 검출", "0건 (Violations: 0, Unconnected: 0)"),
            ("동박 층 구성", "단면 점퍼 혼용", "양면(2-Layer) 45° 직교 클린 라우팅"),
            ("최소 제조 공정 마진", "6 mil 경계 근접", "여유 이격 확보 (HASL 1oz 표준 부합)")
        ],
        "image": "3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/Fig_CarrierBoard_Routing_Verification.png",
        "caption": "[라우팅 검증도] DRC 위반 0건을 달성한 50×50mm CarrierBoard 전·후면 동박 배선 정밀 검증 결과"
    },
    {
        "day": 21, "date": "2026-09-18",
        "phase": "전용 PCB 최종 제작 발주 (26년 하반기)",
        "title": "50×50mm 전용 CarrierBoard 거버(Gerber) 패키징 및 샘플 PCB 5매·부자재 실제 발주 완료",
        "files": "3D modeling/PCB 견적서/PCB 견적서_1.png, CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/gerber_temp/",
        "objective": "검증이 끝난 50×50mm 전용 캐리어보드의 제조용 거버·드릴 파일을 패키징하고, 국내 샘플 PCB 제작 서비스(디바이스마트/엔티렉스)를 통해 다차량 실증용 기판 5매와 체결 부자재를 발주한다.",
        "work": [
            "F.Cu, B.Cu, F/B.Mask, F/B.Silkscreen, Edge.Cuts 및 드릴(.drl) 파일을 묶은 최종 제조 압축본(20260918143152_Gerber_CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText.zip) 생성.",
            "기판 사양 확정: 가로 50mm × 세로 50mm, 2층, 두께 1.6mm, FR-4 녹색 솔더마스크, 백색 실크, HASL 표면처리, 수량 5매.",
            "조립용 1×8·1×5 핀헤더 소켓, 1.25mm Molex PicoBlade 배터리 케이블 쌍, SS-12D00 슬라이드 스위치, 4.7kΩ 1% 저항 동시 주문 완료(합계 50,220원)."
        ],
        "failure": "거버 업로드 사전 프리뷰에서 보드 외곽선(Edge.Cuts) 폐곡선 끝점이 미세하게 열려 있을 경우 외형 가공이 누락될 수 있고, 배터리 극성 커넥터 피치(1.25mm vs 2.0mm) 혼동 위험이 있었음.",
        "change": [
            "거버 뷰어로 Edge.Cuts 완전 폐곡선 및 드릴 홀 원점 일치를 재확인한 뒤 업로드 완료.",
            "Beetle ESP32-C6 배터리 단자 규격에 정확히 맞는 1.25mm 피치 케이블과 직결 소켓 부품을 함께 발주하여 입고 즉시 1~4호차 조립이 가능하도록 준비."
        ],
        "metrics": [
            ("발주 일자 및 파일", "설계 단계", "2026-09-18 실발주 (Gerber 검증 통과)"),
            ("제작 PCB 사양·수량", "브레드보드 시제품 1대", "50×50 mm 2층 FR-4 정밀 기판 5매"),
            ("총 발주 비용(VAT포함)", "-", "50,220원 (PCB 5매 + 소켓·케이블·스위치 일체)")
        ],
        "image": "3D modeling/PCB 견적서/PCB 견적서_1.png",
        "caption": "[실제 발주 증빙] 2026년 9월 발주된 50×50mm 전용 CarrierBoard 샘플 PCB 5매 및 소켓 부자재 견적서"
    },
    {
        "day": 22, "date": "2026-09-30",
        "phase": "실물 PCB 입고 조립 및 I2C 버스 디버깅",
        "title": "입고된 실물 CarrierBoard 1차 납땜 조립 및 I2C 버스 전멸(0.08V LOW 고착) 시리얼 진단",
        "files": "Hardware_Prototypes/code26/test/src/carrier_board_diagnostic.cpp, scratch/diagnostic_stream.log",
        "objective": "제작 입고된 50×50mm 실물 PCB에 소켓과 스위치를 납땜하여 1호 보드를 조립하고, ESP32-C6 RISC-V 진단 펌웨어를 업로드하여 전 센서 통신 상태를 검증한다.",
        "work": [
            "PlatformIO에서 Beetle ESP32-C6(RISC-V 아키텍처) 전용 툴체인 설정 및 부트 시리얼 출력 활성화(ARDUINO_USB_CDC_ON_BOOT=1).",
            "핀 전압 레벨과 I2C 전체 주소(0x01~0x7E)를 스캔하는 하드웨어 진단 코드(carrier_board_diagnostic.cpp) 구동.",
            "COM 포트 시리얼 모니터 실시간 스트림(diagnostic_stream.log) 수집 및 불량 원인 추적."
        ],
        "failure": "전원 인가 후 진단 로그에 'SDA 핀이 LOW(0V)에 묶여 있습니다! (GND 쇼트 또는 배선 오류)' 경보와 함께 '스캔 완료: 발견된 I2C 장치가 0개입니다!'가 출력되며 SHT45·BH1750·MPU6050 3개 센서가 동시에 먹통이 되는 위기 발생.",
        "change": [
            "PCB 자체 동박 단락인지 특정 센서 모듈 불량인지 구분하기 위해 멀티미터 도통 측정과 소켓 모듈 1개씩 순차 탈거(Isolation) 진단 절차에 즉시 돌입.",
            "핀 레벨 선행 점검 코드 덕분에 MCU 고장 오판 없이 물리적 버스 클램핑 현상임을 정확히 특정."
        ],
        "metrics": [
            ("초기 I2C 장치 검출", "목표 3개 (0x23, 0x44, 0x68)", "0개 검출 (버스 전체 마비 발생)"),
            ("SDA/SCL 실측 상태", "정상 풀업 시 HIGH(3.3V)", "LOW 고착 (0.08 V, 보호 다이오드 클램핑)"),
            ("진단 소요 시간", "원인 불명 암중모색", "자체 시리얼 진단기로 즉시 원인 축소")
        ],
        "image": "scratch/notebook_captures/cap_day32_serial_i2c_short.png",
        "caption": "[실제 보드 시리얼 로그] 1차 조립 직후 출력된 SDA LOW(0V) 쇼트 경고 및 I2C 장치 0개 검출 실제 로그"
    },
    {
        "day": 23, "date": "2026-10-01",
        "phase": "센서 역삽입 복구 및 야외 개통",
        "title": "모듈 격리 테스트를 통한 BH1750 역삽입 복구, GPS 방향 정렬 및 야외 157패킷 개통",
        "files": "docs/07_CarrierBoard_Assembly_and_Diagnostic_Log.md, scratch/gps_orientation_guide.png",
        "objective": "전날 발생한 I2C 버스 0.08V 고착 현상의 범인을 찾아내어 전 센서를 정상 복구하고, 야외 위성 수신 테스트를 통해 5종 물리량 통합 실시간 텔레메트리를 최초 개통한다.",
        "work": [
            "소켓에서 모듈을 하나씩 뽑으며 테스트한 결과, 5핀 BH1750 조도 센서가 180° 뒤집혀 꽂히면서 내부 ESD 다이오드가 버스를 GND로 끌어내리고 있었음을 규명 및 정방향 재장착.",
            "NEO-6M GPS 소켓의 핀 방향을 실물 사진(gps_orientation_guide.png) 기준으로 정렬하여 9600bps NMEA 위성 수신 Lock 달성.",
            "야외 보행·이동 실험으로 온도·습도·조도·가속도·GPS 위경도 통합 157패킷 AWS RDS 실시간 적재 성공."
        ],
        "failure": "야외 개통 직후 관제 대시보드를 열었을 때 GPS 수신 전 초기 패킷의 시각 문자열('00:00:00')을 pd.to_datetime()이 파싱하다가 ValueError 크래시를 일으키며 차트 렌더링이 중단됨.",
        "change": [
            "조립 실수 재발 방지를 위해 실물 보드 사진 위에 정확한 모듈 장착 방향 가이드를 마킹하여 문서화(Doc 07).",
            "대시보드 시각 파서에 errors='coerce' 및 불완전 시각 필터를 적용하여 크래시 없이 전 구간 렌더링 완료."
        ],
        "metrics": [
            ("I2C 버스 전압·검출", "0.08 V / 0개 검출", "3.31 V 정상 복귀 / 0x23·0x44·0x68 3종 완비"),
            ("야외 GPS 위성 수신", "미수신", "위성 Fix 완료 및 157건 연속 RDS 적재"),
            ("시각 파싱 크래시", "'00:00:00' 유입 시 중단", "예외 흡수 파서 적용으로 무중단 표출")
        ],
        "image": "scratch/gps_orientation_guide.png",
        "caption": "[실물 보드 사진] I2C 복구 및 NEO-6M GPS 핀 방향 정합을 완료한 실제 50×50mm CarrierBoard"
    },
    {
        "day": 24, "date": "2026-10-02",
        "phase": "왕복 174km 고속도로 실차 주행 실증",
        "title": "전주↔대전 왕복 174km 고속도로 실차 주행 및 통신 두절 1,356패킷 LittleFS 블랙박스 복원",
        "files": "docs/09_Vehicle_Experiment_Data_Recovery_and_Dashboard_Optimization.md, Step4_Run_Coldchain_v2.py",
        "objective": "실제 차량에 전용 캐리어보드를 탑재하고 전주에서 대전까지 왕복 174km 고속도로를 주행하며 장거리 연속 계측 내구성과 통신 음영 구간 블랙박스 복원 성능을 실증한다.",
        "work": [
            "오전 출발 세션(run_20261002_080002_departure) 고속도로 실차 주행 수행 (최고 속도 131 km/h 구간 포함).",
            "주행 중 모바일 핫스팟 절전으로 실시간 전송이 끊긴 구간의 내장 플래시 LittleFS 기록 전수 추출 및 AWS RDS 병합 복구(총 1,356건 무손실 복원).",
            "복원된 1,356건 전 구간을 실시간 관제 대시보드(Step4_Run_Coldchain_v2)에서 재생 검증."
        ],
        "failure": "핫스팟이 끊긴 오프라인 부팅 직후 NTP 서버 시각을 받지 못해 보드 내부 상대 시간(1970년 기준 오프셋)으로 찍힌 로그와 정상 KST 시각 로그가 합쳐지면서 대시보드 X축이 '34시간 주행'으로 길게 늘어지는 왜곡이 발생함.",
        "change": [
            "패킷 시퀀스 간격과 GPS UTC 타임스탬프를 역산 보정하여 끊김 없는 실제 주행 시각 축(약 2시간 14분 편도/왕복 세션)으로 완벽 정규화.",
            "이후 펌웨어에서 인터넷 없이도 GPS 위성 원자시계로부터 즉각 KST 시각을 동기화하도록 근본 개선 결정."
        ],
        "metrics": [
            ("실차 주행 거리·속도", "단거리 시뮬레이션", "전주↔대전 174 km 실차 (최고 131 km/h)"),
            ("데이터 복원 건수", "핫스팟 단절 시 유실 위험", "1,356 패킷 LittleFS 블랙박스 100% 복원"),
            ("시간축 왜곡 보정", "오프라인 시차로 34시간 왜곡", "GPS 시각 역산 정규화로 정밀 복원")
        ],
        "image": "scratch/notebook_captures/step4_coldchain_174km_ko.png",
        "caption": "[실제 대시보드 구동 캡처] 왕복 174km 고속도로 실차 주행 세션(1,356건)이 로드된 실시간 관제 대시보드"
    },
    {
        "day": 25, "date": "2026-10-03",
        "phase": "배터리 동박 패드 수리 및 복합 이상 감지",
        "title": "독립 배터리 결선 중 SW1 스위치 동박 패드 박리(Lifted Pad) 수리 및 3중 복합 이상 감지 구현",
        "files": "docs/10_CarrierBoard_Power_Battery_Assembly_and_Telemetry_Guide.md, scratch/bottom_rot180.jpg",
        "objective": "USB 케이블 없는 완전 무선 운용을 위해 리튬 배터리와 전원 슬라이드 스위치(SW1)를 결선하고, 기판 패드 손상 수리 및 다중 물리량 결합 이상 판별 로직을 탑재한다.",
        "work": [
            "배터리 단자 납땜 수정 중 열응력과 외력으로 박리된 SW1 중앙 공통(Common) 동박 패드 긴급 회로 복구 작업 수행.",
            "기판 후면 트랙을 정밀 추적하여 스위치 잔여 리드와 Beetle C6 BAT+ 입력단 사이를 절연 점퍼선으로 직결 바이패스 납땜 후 에폭시 고정.",
            "단순 온도 이탈뿐 아니라 [고온 + 과습], [문열림 조도 급등 + 온도 상승], [과속 + 고충격] 3중 복합 이상 감지 알림 구현."
        ],
        "failure": "재납땜 인두 온도가 과도했던 상태에서 스위치 핀에 측방 힘이 가해지자 FR-4 기판 표면에서 작은 원형 동박 랜드가 떨어져 나가며 배터리 전원이 인가되지 않는 하드웨어 손상 발생.",
        "change": [
            "박리된 패드 대신 인접 네트 원점 패드에 직접 점퍼 브리지를 형성하고 멀티미터 도통 저항(0.1Ω 미만) 확인 후 기계적 고정 완료.",
            "차기 보드 조립 시 인두 온도 320°C 이하 유지 및 스위치 하우징 밀착 납땜 수칙 확립."
        ],
        "metrics": [
            ("하드웨어 손상 복구", "SW1 동박 박리로 전원 차단", "트랙 직결 점퍼 수리로 도통 0.08 Ω 복구"),
            ("무선 독립 전원", "차량 시거잭 유선 의존", "내장 리튬 배터리 단독 구동 성공"),
            ("이상 경보 정밀도", "단일 변수 임계치 (단순)", "온습도·조도·충격 결합 3중 복합 판별")
        ],
        "image": "scratch/bottom_rot180.jpg",
        "caption": "[실물 보드 후면 사진] 납땜 점검 및 전원 라인 수리를 수행한 실제 50×50mm CarrierBoard 후면부"
    },
    {
        "day": 26, "date": "2026-10-05",
        "phase": "이중 링버퍼 및 무인터넷 시각 동기화",
        "title": "LittleFS 이중 세그먼트 링버퍼(log_0/log_1), 무인터넷 GPS 시각 동기화 및 부팅 360배 가속",
        "files": "Hardware_Prototypes/code26/test/src/carrier_board_mqtt.cpp",
        "objective": "장기 주행 시 플래시 메모리 포화를 막는 순환 저장 구조를 구축하고, 인터넷이 없는 산지·지하에서도 정확한 시각을 기록하며 부팅 대기 시간을 대폭 단축한다.",
        "work": [
            "단일 무한 증가 파일 대신 /log_0.jsonl과 /log_1.jsonl 두 세그먼트를 용량 한도마다 교대 교체하는 이중 링버퍼(Dual-Segment Ring Buffer) 구현.",
            "NTP 실패 시에도 NEO-6M GPS 위성 시각(gps.date/time)에 +9시간(32,400초)을 더해 시스템 RTC(settimeofday)를 즉시 맞추는 오프라인 시각 동기화 탑재.",
            "초기 Wi-Fi 미연결 시 3분씩 블로킹되던 부팅 루틴을 비동기 즉시 진입 구조로 개편 및 LittleFS 덤프 파서 검증."
        ],
        "failure": "기존 펌웨어는 부팅 시 Wi-Fi AP를 찾을 때까지 최대 180초 동안 setup()에 갇혀 출발 초기 상차 충격과 온도 변화를 한 건도 기록하지 못하는 공백이 있었음.",
        "change": [
            "부팅 즉시 0.5초 만에 센서 계측 및 로컬 링버퍼 기록을 먼저 시작하고, Wi-Fi/MQTT는 백그라운드 상태 머신으로 병행 연결하도록 수정하여 부팅 지연을 360배 단축.",
            "시리얼 DUMP 명령을 통한 플래시 내 보존 JSONL 레코드 무결 추출 확인."
        ],
        "metrics": [
            ("오프라인 부팅 소요시간", "최대 180.0 초 대기 (초기 누락)", "0.5 초 즉시 계측 개시 (360배 단축)"),
            ("플래시 용량 관리", "단일 파일 포화 위험", "이중 세그먼트(log_0/1) 자동 순환 링버퍼"),
            ("무인터넷 시각 정합", "1970년 초기화 오차", "GPS 위성 원자시계 기반 KST 동기화")
        ],
        "image": "scratch/notebook_captures/cap_day36_flash_dump_jsonl.png",
        "caption": "[실행 결과] ESP32-C6 내장 LittleFS 플래시 메모리에서 실제 덤프·파싱된 오프라인 JSONL 패킷"
    },
    {
        "day": 27, "date": "2026-10-06",
        "phase": "열역학 시상수(τ=16.4분) 냉각 실험",
        "title": "오프라인 버퍼 조기삭제 버그 패치 및 냉장고 급랭 실험을 통한 열시상수(τ=16.4분) 도출",
        "files": "scratch/fit_step_response.py, run_20261006_214737_fridge (AWS RDS)",
        "objective": "하우징 내부에 장착된 센서 노드가 상온에서 저온 저장고 투입 시 실제 냉기 온도에 도달하기까지 걸리는 열적 응답 지연(Thermal Time Constant, τ)을 실측 실험과 비선형 회귀로 규명한다.",
        "work": [
            "플래시 복구 전송 중 중간에 네트워크가 다시 끊기면 미전송 잔여 파일까지 삭제되던 조기 remove() 버그를 전 패킷 ACK 확인 후 삭제로 패치.",
            "상온(22.2°C) 안정화 상태의 센서 노드를 저온 챔버(약 3.0°C)에 급속 투입하여 15초 간격 연속 냉각 데이터(run_20261006_214737_fridge) 수집.",
            "뉴턴의 냉각 법칙 지수 모델 T(t) = T_env + (T_0 - T_env)·exp(-t/τ) 비선형 최소제곱 피팅 수행."
        ],
        "failure": "초기 실험에서 하우징 밀폐도가 높다 보니 외부 공기는 이미 3°C로 내려갔음에도 내부 센서 판독값은 15분 넘게 서서히 떨어지는 열관성 지연이 관찰되어 문열림 순간 과도 상태 해석에 정량 지표가 필요했음.",
        "change": [
            "실측 냉각 곡선 피팅 결과 결정계수 R² = 0.994의 매우 높은 일치도로 열시상수 τ = 16.4분(984초)을 정밀 도출.",
            "향후 하우징 설계 시 자연대류 통풍구를 상·하단에 관통 배치하여 τ를 단축해야 한다는 정량 설계 근거 확보."
        ],
        "metrics": [
            ("냉각 실험 온도 구간", "초기 22.2 °C → 평형 3.0 °C", "AWS RDS 연속 시계열 완벽 수집"),
            ("도출 열시상수 (τ)", "미계측 추정", "τ = 16.4 분 (63.2% 도달 시간)"),
            ("뉴턴 냉각 모델 적합도", "-", "결정계수 R² = 0.994 (고정밀 부합)")
        ],
        "image": "scratch/notebook_captures/cap_day37_fridge_tau_fit.png",
        "caption": "[실측 및 피팅 결과] 냉장 급랭 실험 실측 데이터(RDS)와 뉴턴 냉각 곡선 피팅(τ=16.4분, R²=0.994)"
    },
    {
        "day": 28, "date": "2026-10-07",
        "phase": "차량용 Jetson Split HUD 구축",
        "title": "운전석 소형 모니터용 Jetson 2분할 스플릿 HUD(Step4_Jetson_SplitHUD.py) 및 자동 실행 구축",
        "files": "Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Jetson_SplitHUD.py, docs/13_Jetson_SplitHUD_and_Autostart_Operation_Guide.md",
        "objective": "냉장 탑차 운전석 보조 모니터(소형 와이드 화면)에서 운전자가 스크롤 조작 없이 적재함 상태와 현재 주행 위치를 한눈에 볼 수 있는 무인 키오스크형 Split HUD를 구축한다.",
        "work": [
            "화면 좌측 50%에 초대형 상태 배지·핵심 KPI(온도·습도·충격·조도)와 미니 차트를, 우측 50%에 실시간 GPS 추적 지도를 고정 배치한 Step4_Jetson_SplitHUD.py 구현.",
            "신규 세션 초기 패킷에 좌표 컬럼이 비어 있을 때 발생하던 KeyError: 'lat' 방어 가드 추가.",
            "Jetson 부팅 시 로그인 직후 전체화면 브라우저로 HUD가 자동 기동되는 systemd/autostart 스크립트 구성."
        ],
        "failure": "기존 데스크톱용 Step4 대시보드를 7~10인치 소형 차량 모니터에 그대로 띄우자 상단 여백과 사이드바가 화면 절반을 가려 정작 중요한 온도 경고와 지도를 보려면 손으로 스크롤해야 하는 안전 문제가 있었음.",
        "change": [
            "상단 패딩·사이드바·푸터를 CSS로 전면 압축 제거하고 1스크린 무스크롤 2분할(Split HUD) 레이아웃으로 전용화.",
            "실시간 자동 리프레시 루프를 결합해 전원만 켜면 작동하는 무인 관제 단말 완성."
        ],
        "metrics": [
            ("차량 모니터 조작 필요성", "수동 스크롤 및 메뉴 클릭 필요", "무조작 1-Screen 무스크롤 HUD"),
            ("초기 빈 데이터 예외", "KeyError: 'lat' 발생 시 중단", "컬럼 존재·유효값 이중 가드로 무중단"),
            ("현장 기동 절차", "터미널 명령어 수동 입력", "전원 인가 시 Autostart 자동 실행")
        ],
        "image": "scratch/notebook_captures/step4_jetson_splithud.png",
        "caption": "[실제 구동 캡처] 차량용 소형 디스플레이에 최적화된 2분할 무스크롤 Step4_Jetson_SplitHUD 실행 화면"
    },
    {
        "day": 29, "date": "2026-10-08",
        "phase": "충전 회로 규명 및 비동기 Wi-Fi 혁신",
        "title": "Beetle C6 충전 표시등 동작 규명, 비동기 Wi-Fi 재연결 패치 및 퇴근 주행 데이터 복원",
        "files": "docs/14_CarrierBoard_Assembly_Sensor_Pinout_and_Battery_Diagnostic_Guide.md",
        "objective": "배터리 스위치 OFF 상태에서 USB 연결 시 초록불이 켜지던 충전 회로 원리를 규명하고, 주행 중 Wi-Fi 재검색 블로킹으로 센서 샘플링이 끊기던 펌웨어 병목을 제거한다.",
        "work": [
            "온보드 충전 IC(TP4057 계열)에 배터리가 물리적으로 분리(SW1 OFF)된 무부하 상태일 때 완충(Standby)으로 오인해 녹색 LED가 점등되는 전기적 메커니즘 규명 및 충전 시 SW1 ON 수칙 정립.",
            "Wi-Fi 단절 구간에서 WiFi.begin() 동기 재시도가 루프를 3~5초씩 멈춰 Peak-Hold 충격 감지를 방해하던 현상을 비동기 타이머(15초 간격 논블로킹 재시도)로 개편.",
            "퇴근 시간대 실차 주행 세션의 분절된 구간 데이터를 시간순 단일 세션으로 병합 복원."
        ],
        "failure": "주행 중 신호가 없는 구간을 지날 때 매 루프마다 동기식 Wi-Fi 스캔이 실행되면서 가속도·GPS UART 읽기 루프까지 덩달아 멈춰 GPS NMEA 문장이 잘리는 연쇄 장애가 확인됨.",
        "change": [
            "통신 재연결 시도 주기를 최소 15초 백오프 비동기 방식으로 격리하여 오프라인 중에도 100Hz 가속도 샘플링과 1Hz GPS 파싱이 단 1ms도 멈추지 않도록 분리.",
            "실차 퇴근 주행 온도·습도·충격 연속 파형 정합 확인."
        ],
        "metrics": [
            ("오프라인 루프 지연", "Wi-Fi 스캔 시 3~5초 멈춤", "비동기 백오프 적용으로 지연 0 ms"),
            ("배터리 충전 혼선", "SW1 OFF 상태 거짓 완충등 혼동", "회로 원리 규명 및 충전 매뉴얼 확립"),
            ("주행 GPS 문장 손실", "루프 지연 중 UART 오버플로", "연속 수신으로 NMEA 체크섬 정상화")
        ],
        "image": "scratch/notebook_captures/cap_day39_evening_commute.png",
        "caption": "[실측 그래프] 비동기 재연결 패치 및 세션 통합으로 복원된 실제 퇴근 주행 온습도·충격 텔레메트리"
    },
    {
        "day": 30, "date": "2026-10-10",
        "phase": "5,000mAh 사과 센서팟 모듈화(v19~v20)",
        "title": "대용량 5,000mAh 파우치 배터리 탑재용 직경 100mm 사과 센서팟 및 모듈형 트레이(v20) 설계",
        "files": "3D_Printer_Housing/v19_Apple_Sensor_Pod_5000mAh/, v20_Apple_Sensor_Pod_Modular5000mAh/",
        "objective": "다일간 충전 없이 연속 유통 추적이 가능하도록 5,000mAh 대용량 리튬폴리머 배터리(JRF PL105568, 10×55×68mm)를 수납하는 직경 100mm 사과 센서팟(v19→v20)을 설계한다.",
        "work": [
            "외경을 100mm 대과 규격으로 확장한 v19 설계에 이어, 하단 배터리실과 상단 50×50mm PCB를 계층 분리하는 드롭인 배터리 트레이 구조(v20) 모델링.",
            "후면 쉘·배터리·중간 트레이·캐리어보드 어셈블리·전면 쉘 5대 부품 카탈로그(20_parts_catalog_layout) 구축.",
            "내부 공중 돌출 보스를 벽면 경사 리브와 100% 융합하여 내부 서포트 생성을 억제."
        ],
        "failure": "v19 일체형 내부 격벽 구조에서는 길이 68mm×폭 55mm의 직육면체 배터리를 둥근 반구 입구로 비스듬히 밀어 넣을 때 보드 지지 기둥에 걸려 진입이 막히는 조립 간섭이 발생함.",
        "change": [
            "v20에서 배터리를 후면 반구에 먼저 안착시킨 뒤 탈착식 중간 트레이와 PCB를 위에서 수직 적층하는 모듈형 구조로 개편하여 삽입 간섭 해결.",
            "5종 구성 부품 전체 치수 및 조립 순서 표준화."
        ],
        "metrics": [
            ("탑재 배터리 용량", "소형 500~1,000 mAh급", "5,000 mAh 대용량 파우치 (장기 연속 구동)"),
            ("사과 하우징 외경", "85 mm (대용량 배터리 불가)", "100.0 mm (실제 사과 대과 크기 부합)"),
            ("배터리 조립성", "v19 기둥 간섭으로 삽입 불가", "v20 계층 분리로 수직 드롭인 장착")
        ],
        "image": "3D_Printer_Housing/v20_Apple_Sensor_Pod_Modular5000mAh/20_parts_catalog_layout.png",
        "caption": "[3D 부품 카탈로그] 5,000mAh 배터리와 50×50mm PCB 수직 적층을 위해 설계한 v20 5파트 구성도"
    },
    {
        "day": 31, "date": "2026-10-11",
        "phase": "물리 스캐너 복구 및 상자 #77 전 주기 실증",
        "title": "물리 핸드헬드 스캐너 부트루프 복구(GPIO 0) 및 상자 #77 A00~A15 소비자 이력 실증",
        "files": "docs/15_ColdChain_Lifecycle_Physical_Scanner_Recovery_and_AutoRecognition_Report.md, Step5_Run_Dashboard.py",
        "objective": "플래시 업로드 불가(벽돌 현상)에 빠진 물리 핸드헬드 QR 스캐너를 하드웨어 부트 핀 강제 진입으로 복구하고, 실제 상자 #77을 A00부터 A15까지 연속 스캔하여 소비자 대시보드 표출을 실증한다.",
        "work": [
            "다운로드 모드 진입 실패 원인이 일반 GPIO 25 버튼과 부트 스트래핑 핀(GPIO 0) 혼동 및 워치독 리셋 루프였음을 규명하고 GPIO 0-GND 단락 후 강제 재플래싱으로 완전 복구.",
            "스캐너 펌웨어의 get_columns() 파싱 누락으로 A10만 반복되던 버그와 A12 PK 중복 충돌을 UPDATE 전환으로 해결.",
            "상자 #77(FmID=77) 실물 QR을 연속 스캔하여 수확(A00)~출하(A15) 전 타임라인과 예냉 저장 온습도가 소비자 대시보드에 완벽 표출됨을 실증."
        ],
        "failure": "펌웨어 내부에서 DB 기존 행 존재 시에도 무조건 INSERT를 시도하도록 작성되어 있어 A12 선별 단계에서 Primary Key Duplicate 에러가 나며 공정 전이가 중단되었음.",
        "change": [
            "최초 입고 시에만 행을 생성하고 이후 단계(A11~A15)는 UPDATE qr SET ... WHERE FmID=77 구문으로 해당 공정 타임스탬프 컬럼을 누적 갱신하도록 수정하여 전 주기 완주 성공.",
            "소비자 화면에서 상자 #77의 전 단계 통과 시각 및 안심 배지 정상 출력 캡처 완료."
        ],
        "metrics": [
            ("벽돌 스캐너 복구", "부트루프로 시리얼 업로드 실패", "GPIO 0 강제 부트 진입으로 100% 복구"),
            ("공정 전이 중단 버그", "A10 반복 및 A12 PK 중복 에러", "컬럼 매핑 수정 + UPDATE 전환으로 해결"),
            ("상자 #77 실증 범위", "부분 공정 확인", "A00 → A10 → A11 → A12 → A13 → A14 → A15 완주")
        ],
        "image": "scratch/notebook_captures/step5_consumer_box77_trace.png",
        "caption": "[실제 대시보드 구동 캡처] 물리 스캐너로 완주한 상자 #77(FmID=77)의 A00~A15 콜드체인 타임라인 화면"
    },
    {
        "day": 32, "date": "2026-10-12",
        "phase": "다차량 토픽 분리 및 이종 센서 핫플러그",
        "title": "HiveMQ 브로커 전환, 다차량 토픽 격리 및 이종 센서(0x68/0x69, SHT4x/3x) 핫플러그 자동 복구",
        "files": "Hardware_Prototypes/code26/test/src/carrier_board_mqtt.cpp",
        "objective": "복수의 수송 차량(1~4호차) 동시 운용을 위해 차량별 MQTT 토픽을 격리하고, 보드별로 상이한 센서 리비전이나 주행 중 일시적 소켓 흔들림에도 재부팅 없이 자가 복구되는 펌웨어를 구현한다.",
        "work": [
            "공용 브로커 혼선을 피하기 위해 HiveMQ 브로커 및 차량 고유 토픽(coldchain/truck01 ~ truck04) 체계 도입.",
            "MPU6050 AD0 핀 상태에 따른 이중 주소(0x68/0x69)와 온습도 센서 SHT4x/SHT3x를 부팅 및 런타임 중 자동 탐색하는 Auto-Detect 루틴 구현.",
            "주행 진동으로 센서가 순간 분리되었다가 재접촉(Hot-plug)될 때 자동으로 레지스터를 재초기화하여 계측을 이어가는 복구 실험 수행."
        ],
        "failure": "기존 펌웨어는 setup()에서 단 한 번만 sensor.begin()을 호출했기 때문에 주행 중 강한 충격으로 소켓 접점이 0.1초만 떨어졌다 붙어도 재부팅 전까지 영구적으로 0 또는 NaN만 출력하는 문제가 있었음.",
        "change": [
            "연속 읽기 실패 카운터가 임계치에 도달하면 I2C 버스를 리셋하고 begin() 초기화 시퀀스를 런타임에 자동 재수행하는 핫플러그 자가 치유(Self-Healing) 상태 머신 완성.",
            "실제 탈부착 시험에서 전원 차단 없이 수 초 내 정상 파형 복귀 확인."
        ],
        "metrics": [
            ("차량 토픽 체계", "단일 토픽 혼선", "truck01 ~ truck04 멀티 플릿 격리"),
            ("센서 주소·기종 호환", "고정 주소 하드코딩", "MPU(0x68/0x69)·SHT(4x/3x) 자동 감지"),
            ("순간 접촉불량 복구", "재부팅 전까지 영구 먹통", "런타임 자동 재초기화(Hot-plug 복구)")
        ],
        "image": "scratch/notebook_captures/cap_day45_hotplug_recovery.png",
        "caption": "[실행 결과] 이종 센서 자동 탐색(Auto-Detect) 및 런타임 핫플러그 자가 복구 펌웨어 검증"
    },
    {
        "day": 33, "date": "2026-10-13",
        "phase": "v21 실물 3D 출력물 조립 간섭 해결",
        "title": "v21 2피스 사과 하우징 실물 출력물 피팅 중 GPS 간섭(7.16mm) 실측 및 1.5cm 단차형 기둥 발명",
        "files": "docs/16_Apple_Sensor_Pod_v21_Standoff_Optimization_and_Session_Log.md, v21_Apple_Sensor_Pod_2Piece5000mAh/",
        "objective": "부품 수를 2피스로 줄인 사과 하우징(v21)을 실제 3D 프린터로 출력하여 50×50mm 캐리어보드를 장착해보고, 실물 조립에서 드러난 기구 간섭을 정밀 치수 계산으로 해결한다.",
        "work": [
            "중간 트레이를 제거하고 전면·후면 2피스로 단순화한 v21 실물 PLA 출력 및 CarrierBoard 가조립 실시.",
            "내벽에서 뻗어 나온 삼각 보강 날개(Gusset)가 보드 측면 돌출 NEO-6M GPS 모듈 모서리와 7.16mm 겹치며 기판이 수평으로 내려앉지 못하는 실물 간섭 규명.",
            "보드 안착면 아래 15.0mm(1.5cm) 구간은 순수 원기둥(직경 7mm)으로 비워 센서 공간을 확보하고 그 아래만 외벽 리브로 지지하는 '단차형(Stepped) 기둥' 설계 적용."
        ],
        "failure": "CAD 상에서 빈 보드 외곽(50×50mm)만 보고 기둥 보강 리브를 끝까지 올렸으나, 실제 납땜된 보드에서는 NEO-6M 모듈 기판이 보드 바깥쪽으로 돌출되어 보강 날개 상단과 물리적으로 충돌함.",
        "change": [
            "상단 15mm 무간섭 원기둥 + 하단 수직 외벽 직결 보강 리브(v21.2) 구조로 개량하여 GPS 모듈 간섭을 0.0mm로 완전 해소하면서도 출력 시 기둥 흔들림을 완벽히 잡아냄.",
            "실물 가조립을 통해 체결 홀 4점 일치 및 배터리 수납 공간 최종 확인."
        ],
        "metrics": [
            ("하우징 부품 수", "v20 3피스 (트레이 포함)", "v21 2피스 (전면·후면 직결 단순화)"),
            ("실물 GPS 간섭량", "보강 리브와 7.16 mm 물리 충돌", "15 mm 단차형 기둥으로 간섭 0.0 mm 해결"),
            ("검증 방식", "화면상 가상 배치", "실물 3D 출력물 + 실제 납땜 보드 피팅")
        ],
        "image": "3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/KakaoTalk_20261015_114727151.jpg",
        "caption": "[실물 출력·조립 사진] 실제 3D 프린팅된 사과 센서팟 하우징 내부에 50×50mm 캐리어보드를 피팅한 모습"
    },
    {
        "day": 34, "date": "2026-10-16",
        "phase": "1~4호차 멀티 플릿 구축 및 02호차 야간 실증",
        "title": "CarrierBoard 1~4호차 멀티 플릿 완성, v22 자석 결합 개선 및 02호차 야간 주행(484건) 실증",
        "files": "docs/18_MultiCarrier_Board_Deployment_and_Fleet_Registration_Report.md, docs/19_CarrierBoard_02_Field_Driving_Experiment_Recovery_and_Telemetry_Report.md",
        "objective": "발주 기판으로 1~4호차 총 4대의 독립 센서 노드 플릿을 모두 조립 등록하고, 자석 스냅 결합형 v22 하우징 보정과 함께 02호차 야간 실차 주행 데이터를 확보한다.",
        "work": [
            "CarrierBoard #01~#04 4대 전수 조립·펌웨어 개별 ID 플래싱 및 대시보드 플릿 등록 완료.",
            "네오디뮴 자석 결합 및 외장 GPS 전용 포켓을 갖춘 v22 실물 출력 공차 보정.",
            "02호차(truck02) 야간 54분 실차 주행 수행: 총 484패킷(최대 충격 5.41G 포착) 수집 및 UTF-8 바이트 스트림 무손실 블랙박스 복원 후 관제 대시보드 검증."
        ],
        "failure": "윈도우 PowerShell 리다이렉션(>)으로 시리얼 플래시 덤프를 저장할 때 기본 UTF-16LE/CP949 인코딩 변환이 개입되며 한글 세션명이 포함된 JSONL 라인 일부가 깨지는 현상이 발생함.",
        "change": [
            "파이썬 pyserial 원시 바이트 스트림(raw bytes) 리더기로 직접 수신해 UTF-8로 무손실 디코딩함으로써 484건 패킷을 단 1바이트 손상 없이 AWS RDS에 복원.",
            "Step4 대시보드에서 truck02_주행_2026-10-16_21시13분 세션 전 지표 표출 확인."
        ],
        "metrics": [
            ("구축 완료 센서 플릿", "단일 시제품 1대", "CarrierBoard 1~4호차 총 4대 완비"),
            ("02호차 야간 주행 수집", "-", "54분 주행 / 484건 / 최대 충격 5.41 G"),
            ("덤프 인코딩 손실", "셸 리다이렉션 시 한글 깨짐", "원시 바이트 UTF-8 리더로 손실 0건")
        ],
        "image": "scratch/notebook_captures/step4_coldchain_truck02.png",
        "caption": "[실제 대시보드 구동 캡처] 02호차 야간 실차 주행 데이터(484건)와 실시간 로그 테이블이 표출된 관제 화면"
    },
    {
        "day": 35, "date": "2026-10-18",
        "phase": "다중 구간 주행 분리·EC2 데몬·유령 충격 제거",
        "title": "02·04호차 연속 실증, AWS EC2 24/7 무인 수집 데몬 가동 및 I2C 유령 충격 스파이크 제거",
        "files": "cloud_backend/mqtt_to_mysql_daemon.py, docs/20_CarrierBoard_02_Daytime_MultiTrip_Recovery_Report.md, docs/21_Cloud_Backend_Daemon_Deployment_and_Automated_Pipeline_Report.md",
        "objective": "관제 PC를 꺼두어도 24시간 클라우드에서 MQTT 패킷을 자동 적재하는 무인 백엔드 데몬을 구축하고, 주간 다중 주행 자동 세션 분리와 I2C 통신 오류발 가짜 충격 스파이크를 해결한다.",
        "work": [
            "02호차 주간 왕복 주행(편도 주행 → 71분 주차 → 복귀 주행) 데이터를 시간 공백 임계치 기준으로 2개 독립 세션으로 자동 분할 복원 및 04호차 야간 주행(395건)·핫스팟 자가복구 검증.",
            "AWS EC2(Ubuntu 24.04) 서버에 systemd 상시 서비스(coldchain-daemon.service)로 mqtt_to_mysql_daemon.py 배포 가동.",
            "관제 대시보드의 기본 모드를 클라우드 조회 전용으로 전환해 EC2 데몬과의 이중 INSERT 중복 적재 원천 차단."
        ],
        "failure": "주행 데이터에서 정차 중임에도 간헐적으로 11G~19G의 비현실적 충격 스파이크가 찍혔는데, 분석 결과 MPU6050 I2C 읽기 실패 시 초기화되지 않은 지역 스택 배열(int16_t raw[6] 쓰레기값)이 그대로 가속도로 환산되고 있었음.",
        "change": [
            "Wire.requestFrom() 반환 바이트 수가 6바이트 미만이면 즉시 샘플을 폐기하고 스택 버퍼를 0으로 초기화하도록 패치하여 유령 충격 스파이크를 100% 박멸.",
            "EC2 무인 데몬 가동으로 노트북 종료 상태에서도 전 차량 패킷 상시 자동 저장 달성."
        ],
        "metrics": [
            ("데이터 수집 가용성", "관제 노트북 켜져 있을 때만 저장", "AWS EC2 24/7 systemd 무인 상시 적재"),
            ("유령 충격(Ghost Spike)", "I2C 오류 시 스택 쓰레기값 유입", "반환 바이트 검증 패치로 오탐 0건"),
            ("연속 실차 검증", "01·02호차 검증", "02호차 주간 다중구간 + 04호차 395건 완주")
        ],
        "image": "scratch/notebook_captures/cap_day52_truck02_daytime_split.png",
        "caption": "[실측 그래프] 71분 정차 공백을 기준으로 자동 분리 복원된 02호차 주간 편도·복귀 실차 텔레메트리"
    },
    {
        "day": 36, "date": "2026-11-12",
        "phase": "CadQuery B-Rep 전환 및 무자석 베요넷·통풍 완성",
        "title": "v22 사과 센서팟 CadQuery(STEP/STL) 표준 전환, 원피스 서포트 분리 및 4점 베요넷 회전 잠금 완성",
        "files": "3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/cadquery_v22/22_apple_sensor_pod_cq.py",
        "objective": "5,000mAh 배터리 코너 간섭을 완전히 제거한 구형 사과 하우징(v22)을 정밀 B-Rep 커널인 CadQuery(Python)로 전면 재구축하고, 자석 접착조차 필요 없는 4점 베요넷 트위스트 락과 굴뚝 대류 통풍 구조를 완성한다.",
        "work": [
            "56.4×70.4mm 배터리 코너 클리어런스 베이 확보 및 OpenCASCADE 기반 CadQuery 듀얼모드(CQ-Editor GUI + CLI STEP/STL 일괄 빌드) 스크립트 구축.",
            "Dome-Up 출력 방향에서 내부 PCB 기둥·리브를 베드 바닥(Z=0.00mm)까지 연장해 서포트가 아보카도 씨처럼 한 덩어리로 똑 떨어지는 원피스 분리 구조 구현.",
            "네오디뮴 자석 본드 접착을 폐기하고 15° 회전만으로 잠기는 4점 원형 베요넷(Bayonet Twist-Lock) 및 열시상수 단축용 상·하단 굴뚝 자연대류 통풍구 완성."
        ],
        "failure": "기존 OpenSCAD 메쉬 모델은 정밀 STEP 파일 추출이 불가능하고 반구 분할 경계에서 공면(Coplanar) 얇은 막 아티팩트가 생겼으며, 네오디뮴 자석 결합은 순간접착제 백화 현상과 극성 오삽입 불편이 있었음.",
        "change": [
            "전체 중공 바디 생성 후 분할 박스와 교집합(.intersect)하는 B-Rep 솔리드 기법으로 공면 아티팩트를 원천 차단하고 정밀 STEP·STL 동시 자동 생성 달성.",
            "무자석·무나사 4점 베요넷 잠금과 상·하 관통 대류 통풍구를 갖춘 최종 양산형 기구 완성."
        ],
        "metrics": [
            ("3D CAD 커널 표준", "OpenSCAD 폴리곤 메쉬", "CadQuery 2.7+ B-Rep (정밀 STEP + STL)"),
            ("전·후면 체결 방식", "나사 또는 네오디뮴 자석 본드 접착", "무자석·무나사 4점 베요넷 15° 회전 잠금"),
            ("출력 서포트·통풍", "서포트 조각 고착 / 밀폐 열지연", "Z=0 원피스 서포트 제거 + 상하 굴뚝 대류홀")
        ],
        "image": "scratch/notebook_captures/cap_day64_bayonet_vent_stl.png",
        "caption": "[실제 STL 단면·결합 검증] CadQuery B-Rep으로 생성된 4점 베요넷 트위스트 락 및 굴뚝 통풍구 STL 검증"
    },
]
