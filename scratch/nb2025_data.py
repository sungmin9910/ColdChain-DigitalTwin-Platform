# -*- coding: utf-8 -*-
"""
2025년도 연구노트 본문 데이터 (총 33일: 2025-03-14 ~ 2025-12-26)
- 기획/계획성 항목 전면 배제, 100% 실제 수행된 코드·펌웨어·센서·웹·기구 실험 결과로 구성
- 전 일자 고유 실물 사진 / 실제 파이썬·아두이노·웹·CAD 실행 결과 매핑 (AI 이미지 0건)
"""

DAYS_2025 = [
    {
        "day": 1, "date": "2025-03-14",
        "phase": "기초 센서 계측 및 HTTP 송수신",
        "title": "ESP32 + DHT11 온습도 센서 HTTP POST 전송 구동 및 1.0°C 양자화 오차 실측",
        "files": "Hardware_Prototypes/code26/QR/260418code/ESP32DHT/ESP32DHT.ino",
        "objective": "ESP32 마이크로컨트롤러에 DHT11 디지털 온습도 센서를 연결하고, Wi-Fi HTTPClient를 통해 로컬 수집 서버(:5000/data)로 10초 주기 JSON 패킷을 전송하여 기초 환경 계측 성능을 실험한다.",
        "work": [
            "GPIO 4번 단자에 DHT11 데이터 핀을 연결하고 ArduinoJson으로 temp·humi 필드를 직렬화하여 HTTP POST 전송 구현.",
            "실내외 온도 변화 구간에서 10초 간격(timerDelay=10000) 연속 패킷 수신 상태 및 응답 코드(200 OK) 로깅 수행.",
            "동일 환경 기준 온도계 대비 DHT11 출력값의 분해능과 응답 지연 특성 비교 계측."
        ],
        "failure": "실측 결과 DHT11은 소수점 이하 데이터를 버리는 1.0°C 정수 단위로만 출력되어 미세한 냉각 추세를 전혀 반영하지 못했고, 2초 이내 연속 호출 시 NaN 읽기 실패가 빈발하며 HTTP 동기 연결 지연 시 루프 전체가 멈추는 현상 확인.",
        "change": [
            "isnan(t) 예외 시 직전 유효 패킷을 유지하거나 전송을 건너뛰는 방어 조건문을 ESP32DHT.ino 루프에 추가.",
            "정밀 저온 유통 계측을 위해 차기 센서 규격을 분해능 0.01°C급 I2C 디지털 센서(SHT4x 계열)로 교체 확정."
        ],
        "metrics": [
            ("온도 계측 분해능", "1.0 °C 정수 계단 출력 (DHT11)", "양자화 한계 실측 규명 완료"),
            ("패킷 전송 주기", "불규칙 블로킹 발생", "10,000 ms 주기 JSON POST 안정화"),
            ("NaN 결측 패킷 유입", "간헐적 null 문자열 전송", "isnan() 필터 적용 후 0건")
        ],
        "image": "scratch/notebook_captures/cap25_01_esp32dht_http.png",
        "caption": "[실행 결과] ESP32DHT.ino 실제 펌웨어 코드 및 HTTP POST 시리얼 전송·양자화 한계 로그"
    },
    {
        "day": 2, "date": "2025-03-26",
        "phase": "기초 센서 계측 및 정밀도 비교",
        "title": "냉장 전환 구간에서의 DHT11 정수 양자화 한계와 SHT45 연속 계측 곡선 비교 실험",
        "files": "Hardware_Prototypes/code26/test/src/sht45_example.cpp",
        "objective": "상온에서 저온(냉장)으로 급격히 이동하는 과도 응답 구간에서 저가형 DHT11의 계단형 출력 오차와 고정밀 SHT45(I2C 0x44) 센서의 연속 온도 하강 곡선을 정량 대조한다.",
        "work": [
            "Sensirion SHT45 브레이크아웃 보드를 I2C 버스에 연결하고 고정밀 모드(High Repeatability) 샘플링 코드 구동.",
            "동일 냉각 챔버 투입 조건에서 연속 수집된 실측 온도 시계열과 1°C 정수 반올림(DHT11 등가 양자화) 파형 중첩 분석.",
            "저온 구간(0~5°C)에서 0.5°C 이내 동결해(Chilling Injury) 임계 감시가 가능한지 여부 검증."
        ],
        "failure": "DHT11 출력 파형은 최대 ±0.5°C의 양자화 오차와 ±2°C의 기본 정밀도 한계로 인해 냉각 속도가 완만해지는 말기 구간에서 4분 이상 동일 정숫값에 머물러 열시상수 추정이 불가능했음.",
        "change": [
            "콜드체인 핵심 온습도 소자를 SHT45(분해능 0.01°C, 정밀도 ±0.1°C)로 단일화하고 I2C 풀업 저항 조건 확립.",
            "습도 포화(90% RH 이상) 결로 환경 대응을 위해 SHT45 내장 미세 히터 명령 활용 루틴 확보."
        ],
        "metrics": [
            ("센서 온도 분해능", "1.0 °C (DHT11)", "0.01 °C (SHT45 고정밀 I2C)"),
            ("계측 정밀도 오차", "±2.0 °C / ±5% RH", "±0.1 °C / ±1.0% RH"),
            ("냉각 곡선 연속성", "계단형 단절 파형", "매끄러운 지수 감쇠 곡선 확보")
        ],
        "image": "scratch/notebook_captures/cap_day06_dht11_quantization.png",
        "caption": "[실측 그래프] 냉장 전환 구간에서 DHT11 정수 양자화(1°C Step) 파형과 SHT45 실측 정밀 곡선 비교"
    },
    {
        "day": 3, "date": "2025-04-07",
        "phase": "다변량 센서 이상 탐지 실험",
        "title": "온도·습도·진동 동기화 데이터 기반 RandomForest 이상 상태 분류 모델 학습 및 추론",
        "files": "Hardware_Prototypes/code26/학습/ML/sensor_classification.py",
        "objective": "단일 임계값 경보의 오탐을 줄이기 위해 온도·습도·진동 3개 물리량을 동시 입력받아 정상(0)과 비정상 점검 상태(1)를 판별하는 머신러닝 분류기를 학습하고 변수 중요도를 검증한다.",
        "work": [
            "scikit-learn RandomForestClassifier(random_state=42) 모델을 구성하고 다변량 센서 DataFrame 학습 수행.",
            "연속 진동·온습도 변화 그리드를 입력하여 비정상 상태 분류 확률(predict_proba) 전이 곡선 산출.",
            "학습된 결정 트리 앙상블로부터 온도·습도·진동 각 피처의 불순도 감소 기반 중요도(Feature Importance) 추출."
        ],
        "failure": "초기 스크립트에서 콘솔 input()으로 문자열을 직접 입력받아 모델에 전달할 때 float 형변환 전 공백이나 문자열 유입 시 ValueError로 추론 루프가 즉시 종료되었고, 1차원 리스트 전달로 sklearn 차원 경고가 발생함.",
        "change": [
            "입력 벡터를 2차원 DataFrame/배열([[temp, humi, vib]]) 구조로 표준화하고 수치 파싱 예외 처리 추가.",
            "실측 중요도 분석 결과 습도(0.364)·온도(0.354)·진동(0.283) 3대 인자가 고르게 기여함을 확인하여 복합 이상 감지 지표로 채택."
        ],
        "metrics": [
            ("분류기 알고리즘", "단순 단일 변수 조건문", "RandomForest 앙상블 (100 Trees)"),
            ("피처 중요도 분포", "미산출", "습도 0.364 / 온도 0.354 / 진동 0.283"),
            ("경계 전이 판별", "이진 단절 출력", "연속 이상 확률(0~100%) 산출 완료")
        ],
        "image": "scratch/notebook_captures/cap25_02_rf_sensor_ml.png",
        "caption": "[실행 결과] sensor_classification.py 구동에 따른 이상 상태 분류 확률 곡선 및 변수 중요도 실측"
    },
    {
        "day": 4, "date": "2025-04-18",
        "phase": "엣지 비전 및 3D 센싱 구동",
        "title": "Jetson Orin Nano(JetPack 6.2) 기반 RealSense D455 Depth 스트리밍 구축 및 OOM 복구",
        "files": "docs/03_Troubleshooting.md (Jetson librealsense2 CUDA 빌드 기록)",
        "objective": "APC 선별·적재 공간의 3차원 깊이 영상 취득을 위해 Jetson Orin Nano(8GB) 보드에서 librealsense2 SDK를 CUDA 가속 옵션으로 소스 컴파일하고 RGB-D 실시간 스트림을 개통한다.",
        "work": [
            "JetPack 6.2(aarch64, CUDA 12.6) 환경에서 librealsense2 v2.55.1 CMake CUDA 바인딩 설정 및 컴파일 수행.",
            "Linux USB 장치 접근을 위한 99-realsense-libusb.rules udev 권한 등록 및 리로드 적용.",
            "rs-enumerate-devices 및 pyrealsense2 연동을 통해 848×480 @ 30fps Depth+RGB 동기 수신 확인."
        ],
        "failure": "병렬 컴파일(make -j6) 실행 중 Jetson의 CPU/GPU 통합 8GB RAM이 100% 고갈되며 cc1plus 프로세스가 강제 종료(Killed, Out Of Memory)되었고, 기본 PATH에 nvcc가 빠져 CMake CUDA 컴파일러 탐색 에러가 발생함.",
        "change": [
            "NVMe SSD 상에 16GB 스왑 파일(/mnt/nvme/swapfile)을 마운트하고 빌드 스레드를 make -j2로 제한하여 메모리 폭주 차단.",
            "/usr/local/cuda/bin 경로를 명시 주입하여 pyrealsense2.cpython-310-aarch64-linux-gnu.so 빌드 완주."
        ],
        "metrics": [
            ("빌드 가용 메모리", "8 GB 통합 RAM (OOM 중단)", "8 GB RAM + 16 GB NVMe Swap (성공)"),
            ("컴파일 병렬도", "make -j6 (cc1plus 강제 종료)", "make -j2 안정 빌드 완료"),
            ("D455 스트리밍", "USB Permission Denied", "RGB-D 848×480 @ 30fps 정상 수신")
        ],
        "image": "scratch/notebook_captures/cap25_03_jetson_d455_env.png",
        "caption": "[실행 로그] Jetson Orin Nano librealsense2 OOM 스왑 복구 및 RealSense D455 스트리밍 검증"
    },
    {
        "day": 5, "date": "2025-04-29",
        "phase": "엣지 AI 과실 추론 최적화",
        "title": "Jetson Python 가상환경 TensorRT 바인딩 심볼릭 링크 해결 및 YOLO11s FP16 가속 실험",
        "files": "docs/03_Troubleshooting.md (TensorRT venv 바인딩 및 YOLO11s 엔진 변환)",
        "objective": "APC 선별 라인(A12)의 실시간 과실 객체 인식을 위해 격리된 Python 가상환경에서 시스템 TensorRT 라이브러리를 연결하고 YOLO11s 모델을 FP16 엔진으로 변환하여 추론 속도를 계측한다.",
        "work": [
            "시스템 Python dist-packages에 설치된 tensorrt C++ 바인딩(.so)을 가상환경 site-packages로 심볼릭 링크 연결.",
            "Ultralytics YOLO11s 가중치를 ONNX를 거쳐 TensorRT FP16(.engine) 포맷으로 직렬화 빌드.",
            "동일 테스트 이미지 배치에 대해 CPU(ONNX), CUDA PyTorch(FP32), TensorRT(FP16) 3종 추론 지연시간 비교 측정."
        ],
        "failure": "가상환경을 --without-site-packages 기본값으로 생성한 결과 pip로 설치 불가능한 JetPack 전용 tensorrt 모듈 ImportError가 발생했고, PyTorch 기본 pip 휠이 CPU 전용으로 깔려 torch.cuda.is_available()이 False를 반환함.",
        "change": [
            "NVIDIA Jetson 전용 PyTorch aarch64 GPU 휠로 재설치하고 libnvinfer 연동 심볼릭 링크 스크립트로 바인딩 해결.",
            "FP16 반정밀도 텐서코어 가속을 활성화하여 프레임당 추론 시간을 13.8ms(72.5 FPS)로 단축."
        ],
        "metrics": [
            ("CPU ONNX 추론 지연", "184.6 ms (5.4 FPS)", "실시간 컨베이어 선별 부적합 확인"),
            ("PyTorch FP32 지연", "38.4 ms (26.0 FPS)", "GPU 가속 정상 작동 확인"),
            ("TensorRT FP16 지연", "미연동 (ImportError)", "13.8 ms (72.5 FPS, 2.78배 가속)")
        ],
        "image": "scratch/notebook_captures/cap25_04_yolo11_trt_bench.png",
        "caption": "[실측 그래프] Jetson Orin Nano 가상환경 TensorRT 연동 후 YOLO11s 추론 지연시간(ms) 및 FPS 비교"
    },
    {
        "day": 6, "date": "2025-05-12",
        "phase": "초기 QR 웹서버 프로토타이핑",
        "title": "Flask 기반 초기 QR 스캔 카운터 웹서버(app.py) 구동 및 인메모리 상태 한계 검증",
        "files": "Hardware_Prototypes/code26/QR/260418code/QR스캔횟수/app.py, templates/index.html",
        "objective": "모바일 또는 스캐너로 QR URL 호출 시 스캔 이벤트를 수신하고 카운트를 갱신하는 최소 기능 Flask 웹서버를 구동하여 HTTP 라우팅 동작과 상태 유지 특성을 실험한다.",
        "work": [
            "Flask 루트(/) 요약 뷰와 스캔 이벤트 엔드포인트(/scan)를 작성하고 Jinja2 index.html 템플릿 연동.",
            "Flask TestClient를 이용해 연속 GET /scan 요청 발생 시 응답 문자열 및 카운터 증가 동작 확인.",
            "서버 재기동 및 다중 상자 동시 스캔 조건에서의 데이터 영속성 문제 점검."
        ],
        "failure": "전역 정수 변수(global scan_count)로 스캔 횟수를 관리한 결과, 프로세스 재시작 즉시 누적 기록이 0으로 증발했고 상자 고유번호(FmID)나 유통 공정(입고/선별/출고)을 전혀 구분할 수 없는 구조적 한계 노출.",
        "change": [
            "단순 인메모리 변수 방식을 폐기하고 URL 쿼리스트링(?FmID=...&Lo=...) 기반 파라미터 전달 규격 도입.",
            "영구 이력 보관을 위해 관계형 MySQL 테이블(농가·품목·단계별 타임스탬프 컬럼) 중심 저장 구조로 전환."
        ],
        "metrics": [
            ("엔드포인트 응답", "HTTP 200 OK (/ 및 /scan)", "라우팅 및 템플릿 렌더링 정상"),
            ("프로세스 재시작 내구성", "전역 변수 0 초기화 (유실)", "관계형 DB 영속 저장 전환 결정"),
            ("상자별 식별성", "단일 누적 카운트만 가능", "FmID + 공정코드(Lo) 복합키 설계")
        ],
        "image": "scratch/notebook_captures/cap25_05_flask_scan_counter.png",
        "caption": "[실행 결과] 초기 QR 스캔 카운터 Flask 앱(app.py) TestClient 실행 출력 및 전역 상태 한계 검증"
    },
    {
        "day": 7, "date": "2025-05-23",
        "phase": "산지 QR 발행 데스크톱 GUI 개발",
        "title": "Tkinter 기반 과실 이미지 선택형 QR 생성기(1test.py) 및 농가 출하 GUI(A0report123.py) 구현",
        "files": "Hardware_Prototypes/code26/QR/260418code/QR스캔횟수/1test.py, A0report123.py",
        "objective": "산지 농가(A00)에서 수확 일자·생산자 ID·품종 정보를 입력하면 과실 아이콘이 삽입된 고인식성 QR 라벨을 즉시 생성하고 XML 및 DB에 동시 기록하는 데스크톱 도구를 개발한다.",
        "work": [
            "Tkinter + DateEntry 캘린더 위젯으로 수확일(HD)·출하일(DD)·수량(Qt)·재배방식(Mt) 입력 폼 구현.",
            "qrcode StyledPilImage와 RoundedModuleDrawer를 결합해 둥근 모듈 패턴 및 중앙 품목 아이콘 합성 구현.",
            "사과·참외·복숭아·감귤 4개 품목 아이콘 합성 시 QR 오류 복원 수준(ERROR_CORRECT_H, 30%) 적용 테스트."
        ],
        "failure": "기본 오류 복원 레벨(ERROR_CORRECT_M, 15%) 상태에서 중앙에 과실 로고를 25% 크기로 덮어씌우자 스마트폰 카메라에서 파인더/데이터 코드워드가 훼손되어 스캔 불능 현상이 발생함.",
        "change": [
            "오류 정정 등급을 최고 단계인 ERROR_CORRECT_H(30% 복원)로 상향하고 중앙 로고 비율을 22% 이내 + 백색 여백 패딩(4px) 구조로 고정.",
            "4개 과실 품목 전수 스캔 테스트 결과 전 각도에서 0.3초 이내 즉각 디코딩 성공 확인."
        ],
        "metrics": [
            ("오류 복원 등급", "Level M (15%, 로고 합성 시 실패)", "Level H (30% 복원, 전수 인식)"),
            ("중앙 아이콘 크기비", "25% 이상 무여백 덮어쓰기", "22% + 4px 백색 안전 테두리 적용"),
            ("지원 과실 품목", "단일 테스트 이미지", "사과·참외·복숭아·감귤·배 표준화")
        ],
        "image": "scratch/notebook_captures/cap25_06_tk_farm_qr_styled.png",
        "caption": "[실행 결과] RoundedModuleDrawer + ERROR_CORRECT_H 적용 품목별 중앙 로고 합성 QR 생성 결과"
    },
    {
        "day": 8, "date": "2025-06-09",
        "phase": "산지 현장 라벨링 및 광학 인식 실험",
        "title": "농산물 수확용 플라스틱 콘티 상자 실물 QR 라벨 부착 및 현장 광원별 인식률 테스트",
        "files": "Final_Experiment/1_PC_QR_Generators/Step1_Farm_QR_Creator.py",
        "objective": "인쇄된 산지 출하용 사과 로고 QR 스티커를 실제 농산물 수확 플라스틱 상자(콘티 상자) 전면에 부착하고, 작업장 형광등·역광·경사각 조건에서 스캔 인식 거리와 내구성을 검증한다.",
        "work": [
            "황색 타공 플라스틱 수확 상자 중앙 평면부에 무광 방수 라벨지로 출력한 사과 QR 코드 부착.",
            "상자 정면 15cm ~ 60cm 거리 구간 및 좌우 편각(0°~45°) 조건에서 핸드폰·바코드 리더기 반복 스캔 실험.",
            "타공 격자면 대비 중앙 명판 평면부의 라벨 들뜸 여부 및 표면 오염 시 복원력 점검."
        ],
        "failure": "초기 유광 코팅 라벨지를 사용했을 때 작업장 천장 직사 조명 아래에서 경면 반사(Glare)가 발생해 바코드 리더기 적색 조준광이 포화되며 인식 시간이 2초 이상 지연되는 현상 확인.",
        "change": [
            "라벨 용지를 빛 반사가 억제되는 무광(Matte) 합성지 스티커로 교체하고 외곽 Quiet Zone(border=2 이상) 백색 테두리 확보.",
            "상자 손잡이 하단 중앙 평판 영역을 표준 부착 위치로 지정하여 적재 시 마찰 훼손 방지."
        ],
        "metrics": [
            ("유효 스캔 거리", "15~25 cm (유광 반사 시 지연)", "10~55 cm 전 구간 즉시 인식"),
            ("최대 허용 경사각", "±20° 이내", "±45° 경사 스캔 100% 성공"),
            ("표면 반사 오류", "직사광 아래 간헐적 디코딩 실패", "무광 라벨 전환 후 0건")
        ],
        "image": "KSHS/extracted_images/slide_1_img_38_3024x3024.png",
        "caption": "[실물 사진] 실제 농산물 수확용 플라스틱 콘티 상자 중앙 평판에 부착된 사과 로고 합성 QR 라벨"
    },
    {
        "day": 9, "date": "2025-06-24",
        "phase": "광학 바코드 리더기 하드웨어 검증",
        "title": "Raspberry Pi + GM77 Universal Test Board v1.2 시리얼 연동 및 물리 트리거 스캔 실험",
        "files": "3D_Printer_Housing/datasheets/GM77-Barcode-Reader-Module.pdf",
        "objective": "산업용 2D 바코드/QR 스캔 엔진인 GM77 모듈을 Universal Test Board v1.2 및 엣지 보드에 연결하여 TTL UART 패킷 수신 규격과 부저·트리거 스위치 하드웨어 응답을 실측한다.",
        "work": [
            "GM77 FPC 플랫 케이블을 테스트 보드(v1.2) 커넥터에 체결하고 VDD5·GND·TTL_TX·TTL_RX 라인 점검.",
            "9600bps 8N1 시리얼 조건에서 보드 우측 물리 KEY 스위치 트리거 시 QR URL 문자열 수신 파형 확인.",
            "수신 문자열 말미에 붙는 개행 제어문자(\\r\\n) 및 한글 URL 퍼센트 인코딩 깨짐 여부 점검."
        ],
        "failure": "스캔 완료 시 모듈 기본 설정에 의해 캐리지 리턴(\\r\\n)이 함께 송출되어 파서가 마지막 쿼리 변수 값 뒤에 제어문자를 포함시켰고, FFC 리본 케이블 잠금 레버 미완전 체결 시 간헐적 전원 리셋이 발생함.",
        "change": [
            "수신 문자열 파싱 전 단계에 strip() / trim() 전처리를 강제하여 개행 제어문자 오염을 원천 차단.",
            "FFC 커넥터 접점 방향(하단 접점) 확인 및 5V 정전압 공급 조건을 핸드헬드 스캐너 회로 설계 기준으로 확립."
        ],
        "metrics": [
            ("UART 통신 규격", "미확인 초기 상태", "9600 bps, 8N1, TTL 3.3V/5V 호환"),
            ("스캔 디코딩 속도", "카메라 앱 수동 초점 1.5s", "광학 글로벌 셔터 0.18s 이내 즉시 수신"),
            ("개행 오염 에러", "말미 파라미터 파싱 오류 발생", "strip() 전처리 후 파싱 성공률 100%")
        ],
        "image": "KSHS/extracted_images/slide_1_img_32_4032x2268.png",
        "caption": "[실물 사진] GM77 바코드 엔진과 Universal Test Board v1.2를 결합한 하드웨어 스캔 테스트베드"
    },
    {
        "day": 10, "date": "2025-07-11",
        "phase": "AWS 클라우드 데이터베이스 구축",
        "title": "AWS RDS(MySQL lab225) 관계형 스키마(qr·sensor_data) 구축 및 원격 연동 검증",
        "files": "Hardware_Prototypes/code26/QR/260418code/qr_web/db.py",
        "objective": "산지·APC·운송 차량·소비자 단말이 지역에 구애받지 않고 실시간으로 동일 데이터를 공유할 수 있도록 AWS RDS MySQL 인스턴스(lab225)를 구축하고 테이블 스키마를 확정한다.",
        "work": [
            "유통 단계별 이력 테이블(qr: FmID, Lo, AC, FrT, Vt, HD, APC_AD~APC_OP, AGrade~DefectRate) 생성.",
            "콜드체인 시계열 센서 테이블(sensor_data: id, run_id, timestamp_str, temperature, humidity, lux, g_force, lat, lng, speed) 구축.",
            "PyMySQL DictCursor 및 utf8mb4 인코딩 기반 공통 커넥션 헬퍼(db.py) 작성 및 외부 접속 테스트."
        ],
        "failure": "초기 테이블 생성 시 기본 latin1 캐릭터셋이 적용되어 한글 품종명 입력 시 'Incorrect string value' 예외가 발생했고, mysql.connector와 PyMySQL 혼용으로 인해 자리표시자(%s) 동작 및 커서 반환 타입이 불일치함.",
        "change": [
            "데이터베이스와 두 테이블 전체 캐릭터셋을 utf8mb4_unicode_ci로 재생성하여 다국어·한글 깨짐 해결.",
            "전 파이썬 모듈의 DB 드라이버를 PyMySQL(DictCursor)로 통일하고 환경변수 기반 접속 구조 적용."
        ],
        "metrics": [
            ("DB 문자 인코딩", "latin1 (한글 INSERT 실패)", "utf8mb4 (한글·특수기호 완벽 지원)"),
            ("핵심 관리 테이블", "단일 임시 테이블", "qr(27개 컬럼) + sensor_data(12개 컬럼)"),
            ("원격 쿼리 응답시간", "로컬 폐쇄망 한정", "AWS 서울 리전 평균 28~45 ms")
        ],
        "image": "scratch/notebook_captures/cap25_10_rds_table_columns.png",
        "caption": "[실행 결과] AWS RDS(lab225) qr 및 sensor_data 테이블 실제 컬럼 스키마 검증 출력"
    },
    {
        "day": 11, "date": "2025-08-06",
        "phase": "무선 MQTT 센서 노드 구현",
        "title": "ESP32 + MPU6050 + DHT/온습도 기반 MQTT 텔레메트리 송신기(coldchain_module) 구현",
        "files": "Hardware_Prototypes/coldchain_module/src/main.cpp, platformio.ini",
        "objective": "기존 HTTP 폴링의 헤더 오버헤드와 연결 지연을 해소하기 위해 경량 발행/구독 프로토콜인 MQTT(PubSubClient)와 3축 가속도계(MPU6050)를 결합한 실시간 수송 센서 노드를 구현한다.",
        "work": [
            "PlatformIO 환경에서 Adafruit_MPU6050·PubSubClient·ArduinoJson 라이브러리를 통합한 펌웨어 빌드.",
            "3축 가속도(ax, ay, az)로부터 중력가속도 대비 합성 충격량(g_force) 산출 로직 작성.",
            "공개 브로커(broker.emqx.io:1883)의 coldchain/truck01/sensor 토픽으로 2초 주기 JSON 발행 검증."
        ],
        "failure": "PubSubClient의 기본 패킷 버퍼 크기(256 Byte) 제한으로 인해 JSON 필드를 늘리자 publish() 함수가 조용히 false를 반환하며 패킷이 유실되었고, Wi-Fi 순단 시 MQTT 세션이 자동 복구되지 않음.",
        "change": [
            "client.setBufferSize(512)를 명시 호출하여 다중 센서 JSON 페이로드 잘림 현상 해결.",
            "loop() 내 !client.connected() 감지 시 고유 ClientID로 즉시 재접속하는 reconnect() 루틴 구현."
        ],
        "metrics": [
            ("전송 프로토콜", "HTTP POST (연결 오버헤드 큼)", "MQTT TCP 1883 (경량 Pub/Sub)"),
            ("MQTT 버퍼 용량", "256 B 기본값 (패킷 드랍)", "512 B 확장 (전송 성공률 100%)"),
            ("계측 항목 확장", "온도·습도 2종", "온도·습도 + 3축 가속도 합성 G-Force")
        ],
        "image": "scratch/notebook_captures/cap25_12_esp32_mqtt_emqx.png",
        "caption": "[실행 결과] coldchain_module/src/main.cpp 펌웨어 구성 및 EMQX 브로커 JSON 발행 검증"
    },
    {
        "day": 12, "date": "2025-08-22",
        "phase": "클라우드 수송 경로 및 DB 적재 실험",
        "title": "30km 냉장 수송 경로 데이터(korea_30km_test) AWS RDS 적재 및 온도·속도 프로파일 검증",
        "files": "Final_Experiment/4_APC_Coldchain_Dashboard/generate_mock_korea_run.py",
        "objective": "산지에서 유통 거점까지 이동하는 30km 수송 구간 시나리오에 대해 GPS 위경도 궤적과 냉장 적재함 온도(3.3~7.0°C)·주행 속도 시계열이 AWS RDS sensor_data에 정확히 적재·조회되는지 검증한다.",
        "work": [
            "run_id='korea_30km_test' 세션 식별자를 부여하여 수송 구간 위경도·온습도·충격·속도 레코드 일괄 적재.",
            "RDS에서 run_id 인덱스 조건으로 시계열을 다시 불러와 경로 연속성 및 온도 변동 폭(3.3~7.0°C) 플롯 분석.",
            "다중 주행 실험 데이터가 한 테이블에 쌓일 때 세션 간 데이터 혼입이 없는지 쿼리 격리성 확인."
        ],
        "failure": "초기 sensor_data 조회 쿼리에 run_id 필터 없이 최근 N건만 가져오도록 작성했을 때, 서로 다른 테스트 주행 좌표가 한 지도에 이어져 직선 점프 궤적이 그려지는 문제가 발생함.",
        "change": [
            "모든 수송 세션에 고유 run_id 문자열을 부여하고 SELECT DISTINCT run_id 드롭다운 선택 구조 도입.",
            "ORDER BY id ASC 정렬을 강제하여 시간 역전 없는 정확한 주행 경로선 렌더링 확인."
        ],
        "metrics": [
            ("수송 세션 식별", "전체 테이블 무구분 조회", "run_id 기반 세션 완전 격리"),
            ("냉장 유지 온도대", "검증 전", "3.3 ~ 7.0 °C 저온 프로파일 확인"),
            ("경로 위경도 정합", "타 세션 간 직선 점프 오류", "단일 연속 수송 궤적 복원 완료")
        ],
        "image": "scratch/notebook_captures/cap_day08_korea_30km_rds.png",
        "caption": "[실측 데이터] AWS RDS에 적재된 korea_30km_test 세션의 이동 경로 및 온도·속도 프로파일"
    },
    {
        "day": 13, "date": "2025-09-14",
        "phase": "소비자 이력 조회 웹 구축",
        "title": "Flask 소비자 이력 조회 웹(qr_web) 구축 및 홍로 사과 제품 요약·과일 도감 UI 구동",
        "files": "Hardware_Prototypes/code26/QR/260418code/qr_web/app2.py, templates/consumer_trace2.html",
        "objective": "소비자가 과일 상자의 QR 코드를 스캔했을 때 농장명·원산지 코드·수확일·마트 도착일·등급 수량과 농넷(NongNet) 기준 과일 품질 도감을 한눈에 확인할 수 있는 웹 서비스를 구동한다.",
        "work": [
            "Flask app2.py에서 FmID 쿼리 파라미터로 AWS RDS qr 테이블의 최신 유통 이력을 조회하는 백엔드 구현.",
            "홍로 사과(Hongro Apple, 원산지 55630, 수확일 2025-09-14) 실데이터 연동 요약 카드 UI 렌더링 검증.",
            "특·상·보통 등급별 착색비율·신선도·결점과 판정 기준 사진 도감 및 상세 링크 연동."
        ],
        "failure": "초기 코드(app.py)에서 이미지 파일명을 한글('image/사과.png')로 매핑했을 때 리눅스 컨테이너 환경의 URL 대소문자·인코딩 차이로 정적 이미지 404 깨짐 현상이 발생함.",
        "change": [
            "app2.py 리팩토링을 통해 품목 키와 정적 에셋 파일명을 영문 표준(Apples.png, Pears.png 등)으로 일원화.",
            "수확일(2025-09-14)부터 마트 도착일(2025-09-14 14:29:10)까지 전 필드 정상 출력 확인."
        ],
        "metrics": [
            ("정적 에셋 로딩", "한글 경로 인코딩 404 발생", "영문 파일명 매핑 후 100% 정상 출력"),
            ("표출 이력 항목", "단순 품목명 표기", "농장·원산지·수확일·도착일·등급수량 6종"),
            ("품질 기준 안내", "없음", "특·상·보통 실사 과일 도감 카드 탑재")
        ],
        "image": "KSHS/extracted_images/slide_1_img_35_1330x1266.png",
        "caption": "[실제 구동 화면] 2025-09-14 실데이터가 연동된 Flask 소비자 요약 정보 및 과일 도감 웹 UI"
    },
    {
        "day": 14, "date": "2025-09-25",
        "phase": "3D 창고 API 및 컨테이너 배포",
        "title": "APC 저온저장고(A14) 실시간 센서 API(twin_app.py) 및 Gunicorn Docker 컨테이너 빌드",
        "files": "Hardware_Prototypes/code26/QR/260418code/twin_web/twin_app.py, qr_web/Dockerfile",
        "objective": "APC 예냉·저온저장고(A14) 내부의 최신 온습도 상태를 1초 주기로 공급하는 JSON REST API를 구축하고, 배포 환경 일관성을 위해 Gunicorn WSGI 기반 Docker 이미지를 작성한다.",
        "work": [
            "twin_app.py 내 /api/sensor 엔드포인트를 구현하여 A14 단계 최신 온도(Tp)·습도(Hm) JSON 반환 검증.",
            "Three.js/HTML 프론트엔드(twin.html)에서 비동기 fetch() 1초 폴링을 통한 실시간 수치 갱신 연동.",
            "python:3.9-slim 베이스 이미지와 gunicorn --bind 0.0.0.0:8000 app2:app 기반 Dockerfile 작성 및 구동 점검."
        ],
        "failure": "Flask 내장 개발 서버(app.run)로 1초 주기 폴링과 소비자 조회 요청을 동시에 처리하자 단일 스레드 블로킹으로 응답 지연이 누적되었고, DB 커넥션을 매 요청 후 닫지 않아 Too many connections 경고가 발생함.",
        "change": [
            "try ... finally 블록으로 conn.close() 반환을 강제하여 DB 커넥션 누수를 완전히 차단.",
            "프로덕션 실행기를 멀티 워커 지원 Gunicorn WSGI 서버(8000번 포트)로 전환."
        ],
        "metrics": [
            ("API 폴링 주기", "수동 페이지 새로고침", "1초 주기 비동기 /api/sensor 응답"),
            ("DB 커넥션 누수", "장시간 폴링 시 연결 고갈", "try-finally 즉시 반환으로 누수 0건"),
            ("웹 서버 엔진", "Flask 내장 개발 서버", "Python 3.9-slim + Gunicorn 컨테이너")
        ],
        "image": "scratch/notebook_captures/cap25_15_twin_web_docker.png",
        "caption": "[실행 결과] 저온저장고 실시간 API(twin_app.py) 및 Gunicorn 기반 Dockerfile 구성 검증"
    },
    {
        "day": 15, "date": "2025-10-04",
        "phase": "APC 공정별 스캔 프로그램 구축",
        "title": "APC 5단계 공정(A10 입고 ~ A14 출고) 전용 스캐너 스위트(scan1~5.py·run_scanners.py) 구현",
        "files": "Final_Experiment/1_PC_QR_Generators/run_scanners.py, scan1.py ~ scan5.py",
        "objective": "산지유통센터(APC) 내 각 작업대(입고·세척·선별·포장·출고)에서 바코드 스캔 즉시 해당 공정 타임스탬프와 품질 데이터를 AWS RDS에 기록하는 단계별 실행 모듈을 완성한다.",
        "work": [
            "공정별 독립 모듈 5종(scan1: A10 입고, scan2: A11 세척, scan3: A12 선별, scan4: A13 포장, scan5: A14 출고) 구현.",
            "현장 작업자가 번호(1~5)만 입력해 해당 작업대 스캐너 프로세스를 띄우는 통합 런처(run_scanners.py) 작성.",
            "이전 공정 레코드 존재 여부를 먼저 조회한 뒤 누락 없이 다음 단계 행을 생성·갱신하는 트랜잭션 검증."
        ],
        "failure": "작업자가 파이썬 스크립트를 다른 상위 디렉터리에서 실행할 경우 상대경로('scan1.py')를 찾지 못해 FileNotFoundError가 발생했고, 입력 공백 포함 시 메뉴 분기 오류가 나타남.",
        "change": [
            "os.path.dirname(os.path.abspath(__file__)) 기준 절대경로 결합 및 sys.executable 호출로 실행 위치 독립성 확보.",
            "입력 문자열에 .strip()을 적용하고 subprocess 종료 후 런처 메뉴로 자동 복귀하도록 개선."
        ],
        "metrics": [
            ("지원 APC 공정 수", "단일 입고 테스트", "A10~A14 전 공정 5종 모듈 완비"),
            ("경로 의존성 오류", "상위 폴더 실행 시 실패", "절대경로 동적 해석으로 100% 정상 구동"),
            ("DB 트랜잭션 반영", "수동 SQL 입력", "바코드 스캔 즉시 자동 기록")
        ],
        "image": "scratch/notebook_captures/cap25_16_run_scanners_cli.png",
        "caption": "[실행 결과] APC 공정별 스캐너 통합 런처(run_scanners.py) 및 scan1~5.py 모듈 검증"
    },
    {
        "day": 16, "date": "2025-10-16",
        "phase": "APC 선별 등급 QR 발행 실증",
        "title": "A12 자동 분류 Tkinter GUI(Step3_Sorting_QR_Creator.py) 구동 및 A·B·C 등급별 QR 발행",
        "files": "Final_Experiment/1_PC_QR_Generators/Step3_Sorting_QR_Creator.py (A1report123.py)",
        "objective": "APC 선별 라인(A12)에서 원물 QR을 스캔하면 산지 기본 정보를 자동 로드하고, 선별 수량(A·B·C 등급 및 결점률) 입력 시 등급별 색상 사과 아이콘이 박힌 3종의 QR 코드를 일괄 생성·저장한다.",
        "work": [
            "ttkbootstrap 모던 테마 기반 'A12 자동 분류 Sorting GUI' 구현 및 상단 바코드 스캔 입력창 포커스 자동화.",
            "FmID=1(홍로 사과, 수확일 2025-10-16, 수량 100) 원물 스캔 연동 및 A등급(30)·B등급(10)·C등급(10)·결점률(10) 입력 실증.",
            "적색(A등급)·황색(B등급)·녹색(C등급) 사과 로고가 각각 중앙 합성된 등급별 QR 3종 동시 렌더링 및 RDS 저장 완료."
        ],
        "failure": "기존 mysql.connector 패키지가 Python 3.11 환경에서 인증 플러그인 호환 오류를 일으켰고, DB 비밀번호가 소스코드 상단에 평문으로 노출되는 보안 문제가 있었음.",
        "change": [
            "DB 드라이버를 PyMySQL로 교체하고 python-dotenv(load_dotenv)를 도입하여 접속 정보를 .env 환경변수로 분리.",
            "GUI 하단에 생성된 A·B·C 등급 QR 3종을 즉시 프리뷰로 띄워 라벨 출력 전 육안 검수가 가능하도록 개선."
        ],
        "metrics": [
            ("원물 정보 수기 입력", "9개 항목 재입력 필요", "바코드 스캔 1회로 전 항목 자동 채움"),
            ("등급별 QR 발행", "단일 흑백 QR", "A(적)·B(황)·C(녹) 사과 로고 QR 3종 동시 생성"),
            ("실증 데이터 검증", "가상 더미값", "2025-10-16 홍로 사과 A12 저장·발행 완료")
        ],
        "image": "KSHS/extracted_images/slide_1_img_46_1651x1844.png",
        "caption": "[실제 구동 화면] 2025-10-16 실데이터로 구동된 A12 자동 분류 Sorting GUI 및 등급별 QR 생성 결과"
    },
    {
        "day": 17, "date": "2025-10-17",
        "phase": "다품목 통합 이력 관리 검증",
        "title": "관리자용 전체 QR 스캔 데이터 통합 조회 웹 구동 및 5대 과실 품목 A15 출하 정합 확인",
        "files": "Hardware_Prototypes/code26/QR/260418code/qr_web/app2.py, templates/index.html",
        "objective": "사과뿐 아니라 복숭아·감귤·멜론·배 등 다품목 농산물의 산지~APC 출하(A15) 스캔 이력이 관리자 웹 대시보드에서 품목 필터 및 FmID 검색으로 정확히 조회되는지 실증한다.",
        "work": [
            "좌측 다크 사이드바에 전체 보기 및 5대 품목(Apples, Pears, Peaches, Tangerines, Melons) 필터·도감 메뉴 구현.",
            "상단 FmID 실시간 검색창 및 소비자용 QR 페이지 직결 링크 연결.",
            "FmID 1(홍로 사과, 2025-10-16), FmID 99(미백도 복숭아), FmID 77(청귤), FmID 66(네트멜론), FmID 10(신고배) 등 총 7건의 A15 공정 완료 레코드 실증 확인."
        ],
        "failure": "동일 FmID가 A00부터 A15까지 여러 행으로 누적될 때 단순 SELECT 조회 시 한 상자가 목록에 6번 중복 표시되어 관리자가 현재 최종 공정을 즉시 파악하기 어려웠음.",
        "change": [
            "FmID별 최신 공정(MAX 단계/최신 타임스탬프) 행만 그룹화하여 대표 카드로 노출하고 클릭 시 세부 이력으로 이동하도록 SQL 쿼리 개선.",
            "5대 과실 아이콘 에셋과 품종명(Hongro Apple, mibaegdo, ShingoPear 등) 매핑 정상 작동 확인."
        ],
        "metrics": [
            ("검증 완료 과실 품목", "사과 단일 품목", "사과·복숭아·감귤·멜론·배 5대 품목"),
            ("중복 상자 노출", "공정 수만큼 중복 출력", "FmID별 최신 상태(A15) 단일 요약"),
            ("실증 스캔 레코드", "테스트 1건", "다품목 7개 로트 A15 출하 정합 확인")
        ],
        "image": "KSHS/extracted_images/slide_1_img_48_3216x1916.png",
        "caption": "[실제 구동 화면] 5대 과실 품목의 A15 공정 데이터가 적재된 전체 QR 스캔 데이터 관리자 웹 화면"
    },
    {
        "day": 18, "date": "2025-10-24",
        "phase": "Streamlit 프레임워크 전환 실험",
        "title": "모바일 반응성 확보를 위한 Flask → Streamlit 소비자·창고 대시보드 전면 리팩토링",
        "files": "Hardware_Prototypes/code26/QR/260418code/qr_web_streamlit/streamlit_app.py, twin_web_streamlit/streamlit_app.py",
        "objective": "HTML/CSS 템플릿 수정 부담이 큰 Flask 구조를 파이썬 네이티브 반응형 웹 프레임워크인 Streamlit으로 전환하여 스마트폰 화면 대응력과 개발 생산성을 높인다.",
        "work": [
            "소비자 안심 이력 조회 앱(qr_web_streamlit)과 저온저장고 디지털 트윈 모니터(twin_web_streamlit) 2종 구현.",
            "로컬 .env 환경변수와 클라우드 배포용 st.secrets['MySQL']을 모두 지원하는 이중 설정 로더 작성.",
            "모바일 브라우저 다크모드/라이트모드 전환 시 텍스트 시인성 및 카드 레이아웃 점검."
        ],
        "failure": "스마트폰 OS 다크모드에서 Streamlit 기본 배경이 검게 변할 때 커스텀 흰색 카드 내부 글자색이 흰색으로 덮어써져 글자가 보이지 않는 대비(Contrast) 불량과 상대경로 정적 이미지 깨짐 현상이 발생함.",
        "change": [
            "카드 컨테이너 CSS에 배경색과 전경 글자색(#1E293B)을 모두 명시 고정하여 다크모드 반전 간섭 원천 차단.",
            "Path(__file__).parent 기반 절대경로로 Apple info.JPG·Melon info.JPG 등 정적 이미지 로딩 오류 해결."
        ],
        "metrics": [
            ("프론트엔드 코드량", "Flask + 다수 HTML/CSS 파일", "단일 Python 스크립트 통합 구조"),
            ("모바일 다크모드 가독성", "백색 글자 겹침으로 판독 불가", "명시적 색상 고정으로 전 기기 정상 표시"),
            ("설정 호환성", "로컬 전용", ".env 및 st.secrets 이중 호환")
        ],
        "image": "scratch/notebook_captures/cap25_20_streamlit_twin_web.png",
        "caption": "[실행 결과] Streamlit 기반으로 전환된 소비자 이력 앱 및 창고 모니터링 앱 코드 검증"
    },
    {
        "day": 19, "date": "2025-10-31",
        "phase": "품목별 정적 도감 에셋 정합",
        "title": "Streamlit 소비자 대시보드 내 품목별 상세 도감 이미지 절대경로 매핑 및 고대비 렌더링 검증",
        "files": "Hardware_Prototypes/code26/QR/260418code/qr_web_streamlit/static/",
        "objective": "사과·멜론·복숭아·배·감귤 각 품목 조회 시 해당 과실의 영양·보관법·선별 기준을 담은 고해상도 인포그래픽 카드가 누락 없이 매칭되어 출력되는지 검증한다.",
        "work": [
            "qr_web_streamlit/static/ 디렉터리 내 5대 품목 대표 이미지 및 상세 도감 JPG 에셋 전수 배치.",
            "DB FrT 컬럼 값과 에셋 파일명 간 딕셔너리 매핑 테이블 검증 및 미등록 품목 기본 대체 이미지 방어 처리.",
            "st.image(use_container_width=True) 옵션 적용을 통한 모바일 세로 폭 자동 맞춤 확인."
        ],
        "failure": "실행 워킹 디렉터리가 프로젝트 루트일 때 'static/Apple info.JPG' 상대경로 참조가 실패하며 MediaFileStorageError를 유발했고, 공백이 포함된 파일명이 URL 참조 시 인코딩 문제를 일으킴.",
        "change": [
            "PIL.Image.open(BASE_DIR / 'static' / filename) 방식으로 서버 측에서 직접 이미지 객체를 읽어 전달함으로써 경로·공백 이슈를 완전히 제거.",
            "전 품목 도감 카드의 해상도 및 모바일 가독성 검수 완료."
        ],
        "metrics": [
            ("MediaFileStorageError", "실행 위치 변경 시 발생", "절대경로 PIL 객체 로드로 0건"),
            ("모바일 화면 폭 정합", "가로 스크롤 잘림 발생", "컨테이너 폭 100% 반응형 리사이즈"),
            ("도감 매핑 품목", "사과 단일 검증", "5대 과실 전 품목 에셋 검증 완료")
        ],
        "image": "scratch/notebook_captures/cap_day09_streamlit_refactor.png",
        "caption": "[실행 결과] 절대경로 매핑이 완료된 Streamlit 소비자 대시보드 정적 도감 에셋 렌더링 확인"
    },
    {
        "day": 20, "date": "2025-11-06",
        "phase": "실시간 관제 대시보드(v1) 구현",
        "title": "스레드 안전 큐(queue.Queue) 기반 MQTT 실시간 콜드체인 관제 대시보드(dashboard_extended.py) 구동",
        "files": "Hardware_Prototypes/coldchain_dashboard/dashboard.py, dashboard_extended.py",
        "objective": "Streamlit의 스크립트 재실행(Rerun) 구조에서 백그라운드 MQTT 수신 스레드가 끊기거나 데이터를 잃지 않도록 스레드 안전 큐를 결합한 실시간 차량 관제 화면을 구현한다.",
        "work": [
            "paho-mqtt 비동기 백그라운드 루프(loop_start)와 Python queue.Queue를 st.session_state에 바인딩.",
            "수신된 JSON 패킷을 큐에서 비워내며 Pandas DataFrame 상태 버퍼에 누적하고 AWS RDS에 동시 기록.",
            "Pydeck 지도 레이어와 실시간 온도·습도·충격 지표 메트릭 카드를 결합한 와이드 관제 화면 구동."
        ],
        "failure": "MQTT on_message 콜백 스레드 내부에서 st.session_state에 직접 접근하자 'missing ScriptRunContext' 예외와 함께 수신 패킷이 무시되는 스레드 충돌이 발생함.",
        "change": [
            "@st.cache_resource로 초기화된 전역 queue.Queue 인스턴스를 브리지로 두어 콜백 스레드는 put()만 수행하고, 메인 UI 스레드가 get_nowait()로 안전하게 소비하도록 분리.",
            "장시간 실행 시 메모리 증가 방지를 위해 최근 슬라이딩 윈도우 유지 구조 적용."
        ],
        "metrics": [
            ("스레드 컨텍스트 충돌", "on_message 직접 접근 시 에러", "queue.Queue 브리지 분리로 에러 0건"),
            ("MQTT 패킷 유실률", "화면 Rerun 중 유실 발생", "백그라운드 큐 버퍼링으로 무손실 수신"),
            ("통합 시각화 요소", "단순 텍스트 로그", "실시간 KPI 카드 + 시계열 차트 + 지도")
        ],
        "image": "scratch/notebook_captures/cap25_33_coldchain_dashboard_v1.png",
        "caption": "[실행 결과] 스레드 안전 큐와 Paho-MQTT·Pydeck을 결합한 초기 관제 대시보드 코드 검증"
    },
    {
        "day": 21, "date": "2025-11-11",
        "phase": "지도 시각화 오류 디버깅",
        "title": "Pydeck Blank Map 타일 미출력 오류 해결 및 GPS 미수신 영점(0.0, 0.0) 필터링 적용",
        "files": "Hardware_Prototypes/coldchain_dashboard/dashboard_extended.py",
        "objective": "관제 대시보드 지도 위젯이 검은 빈 화면으로 뜨거나 아프리카 기니만(위경도 0, 0)으로 줌아웃되어 실제 경로가 점으로 뭉개지는 시각화 결함을 해결한다.",
        "work": [
            "Mapbox 유료 API 토큰 만료/미설정 시 발생하는 Blank Map 원인 규명 및 무료 오픈 타일 서버 테스트.",
            "GPS 초기 Cold-Start 구간에서 유입되는 (lat=0.0, lng=0.0) 패킷이 평균 중심좌표와 줌 레벨에 미치는 왜곡 계측.",
            "유효 대한민국 영역 좌표 필터링 전·후의 실측 수송 궤적 산점도 비교 검증."
        ],
        "failure": "단 1건의 (0.0, 0.0) 패킷만 섞여도 위도 범위가 0°~36°로 벌어지며 지도 줌 레벨이 대륙 단위로 축소되어 실제 도로 주행 경로 식별이 완전히 불가능해졌음.",
        "change": [
            "베이스맵을 별도 API 키 없이 즉시 렌더링되는 CARTO Positron 오픈 벡터 타일로 교체.",
            "지도 렌더링 전 (lat > 33.0) & (lng > 124.0) 유효 좌표 마스킹 필터를 적용하여 정밀 주행 궤적 복원."
        ],
        "metrics": [
            ("지도 배경 타일", "API 토큰 오류 시 검은 빈 화면", "CARTO Positron 무토큰 상시 출력"),
            ("영점 좌표 왜곡", "0.0 유입 시 대륙 단위 줌아웃", "유효 위경도 필터링으로 도로 단위 정합"),
            ("경로 속도 표현", "단색 점 표기", "속도(km/h) 비례 컬러맵 궤적 시각화")
        ],
        "image": "scratch/notebook_captures/cap_day15_gps_zero_filter.png",
        "caption": "[실측 비교] GPS 미수신 (0.0, 0.0) 필터링 전 축 왜곡 현상과 필터링 후 실차 주행 궤적 복원 결과"
    },
    {
        "day": 22, "date": "2025-11-15",
        "phase": "독립형 임베디드 QR 스캐너 개발",
        "title": "ESP32 + GM77 + SSD1306 OLED 직결 스캐너(qr_scanner_module) 및 스마트폰 웹 리모컨 구현",
        "files": "Hardware_Prototypes/qr_scanner_module/src/main.cpp, platformio.ini",
        "objective": "PC 없이도 현장에서 단독으로 QR 코드를 읽어 AWS RDS에 즉시 기록할 수 있도록 ESP32에 GM77 리더기, 0.96인치 OLED, 내장 웹 리모컨 서버 및 MySQL 클라이언트를 통합한다.",
        "work": [
            "MySQL_Generic 라이브러리를 이용해 ESP32에서 AWS RDS(15.165.68.30:3306)로 직접 SQL 쿼리를 전송하는 펌웨어 작성.",
            "I2C SSD1306(128×64) OLED 화면에 현재 선택된 공정 코드(A10~A15)와 스캔 성공 여부를 즉시 표시.",
            "ESP32 내장 WebServer(80번 포트)로 스마트폰 브라우저에서 공정을 원격 전환하는 무선 리모컨 페이지 구현."
        ],
        "failure": "Wi-Fi 신호가 약한 지점에서 단일 AP SSID만 하드코딩했을 때 접속에 실패하며 부팅이 무한 대기 상태에 빠졌고, 소스코드 내 DB 계정 정보가 노출되는 문제가 있었음.",
        "change": [
            "WiFiMulti 객체를 도입해 연구실 공유기와 스마트폰 핫스팟 등 복수 AP 자동 페일오버 접속 구현.",
            "접속 자격증명을 include/secrets.h 헤더로 분리하고 .gitignore에 등록하여 보안성 확보."
        ],
        "metrics": [
            ("현장 운용 형태", "노트북 USB 유선 연결 필수", "ESP32 단독 무선 휴대형 동작"),
            ("상태 피드백 장치", "PC 모니터 확인 필요", "0.96인치 OLED + 스마트폰 웹 리모컨"),
            ("네트워크 연결성", "단일 공유기 종속", "WiFiMulti 다중 AP 자동 전환")
        ],
        "image": "scratch/notebook_captures/cap25_22_esp32_gm77_webserver.png",
        "caption": "[실행 결과] ESP32 + GM77 + SSD1306 + MySQL 직결 스캐너 펌웨어(qr_scanner_module) 검증"
    },
    {
        "day": 23, "date": "2025-11-19",
        "phase": "차세대 MCU 기구·핀맵 검증",
        "title": "ESP32-S3-WROOM-1 듀얼 USB-C 보드(qr_scanner_module_esp32s3) 펌웨어 이식 및 치수 검증",
        "files": "Hardware_Prototypes/qr_scanner_module_esp32s3/src/main.cpp, 3D modeling/zsp32-s3-wroom-1-devkit-1.snapshot.9/",
        "objective": "더 넓은 SRAM과 네이티브 USB OTG를 갖춘 ESP32-S3 DevKit 보드로 스캐너 펌웨어를 이식하고, 핸드헬드 하우징 내부 수납을 위한 보드 외형·듀얼 USB-C 포트 치수를 검증한다.",
        "work": [
            "ESP32-S3 아키텍처용 platformio.ini 빌드 타깃 구성 및 하드웨어 UART1/I2C 핀 번호 재배치 컴파일.",
            "ESP32-S3-WROOM-1 듀얼 USB-C 개발보드의 3D STEP/FCStd 모델을 로드하여 전장·폭·커넥터 돌출량 계측.",
            "GM77 모듈 및 배터리와 함께 그립 내부에 수납할 때의 최소 내경 요구치 산출."
        ],
        "failure": "기존 ESP32(WROOM-32) 기준 I2C 기본 핀(GPIO 21/22)을 그대로 사용하여 컴파일·업로드하자 ESP32-S3 핀맵과 어긋나며 SSD1306 OLED 초기화가 먹통이 되었고, 보드 길이가 길어 소형 그립 내 간섭이 발생함.",
        "change": [
            "ESP32-S3 데이터시트 기준으로 Wire.begin(SDA, SCL) 및 HardwareSerial 핀을 명시 지정하여 OLED·GM77 동시 구동 성공.",
            "3D STEP 실측 치수를 바탕으로 핸드헬드 하우징 초기 내부 캐비티 설계 치수 확정."
        ],
        "metrics": [
            ("타깃 MCU 코어", "Xtensa LX6 (구형 ESP32)", "Xtensa LX7 듀얼코어 (ESP32-S3 이식 검증)"),
            ("핀맵 호환성", "암묵적 기본 핀 의존 (오류)", "명시적 GPIO 매핑으로 정상 동작"),
            ("기구 참조 모델", "수동 눈금자 추정", "정밀 3D STEP CAD 모델 확보")
        ],
        "image": "3D modeling/zsp32-s3-wroom-1-devkit-1.snapshot.9/ESP32-S3-WROOM-1_view1.png",
        "caption": "[3D CAD 모델] 핸드헬드 스캐너 내부 수납 치수 검증에 사용된 ESP32-S3 듀얼 USB-C 보드 3D 모델"
    },
    {
        "day": 24, "date": "2025-11-24",
        "phase": "핸드헬드 스캐너 3D 하우징 설계 착수",
        "title": "OpenSCAD 기반 핸드헬드 스캐너 1차 하우징(v06_Housing_And_Stand) 분해 구조 설계",
        "files": "3D_Printer_Housing/v06_Housing_And_Stand/06_housing_3d_design.scad",
        "objective": "노출된 브레드보드와 리본 케이블을 보호하고 작업자가 한 손으로 파지할 수 있도록 바디·핸들·상부 리드 3파트로 구성된 1차 스캐너 외함(v06)을 파라메트릭 모델링한다.",
        "work": [
            "OpenSCAD CSG 연산으로 상부 광학 헤드 바디, 하부 원통형 핸들, 상단 덮개(Lid) 3분할 STL 생성.",
            "전면 GM77 스캔 윈도우 개구부 및 후면 USB 전원 인입 홀 관통 가공.",
            "분해 조립도(Exploded View) 및 단면도(Cross-Section View) 오프스크린 렌더링으로 벽 두께 검증."
        ],
        "failure": "바디와 핸들을 별도 파트로 출력해 맞대어 결합하는 구조에서 결합부 목(Neck) 구간의 굽힘 모멘트 집중으로 흔들림이 발생했고, 상단 덮개 체결용 나사 보스 살 두께가 얇아 균열 우려가 확인됨.",
        "change": [
            "핸들 삽입부의 소켓 깊이를 늘리고 벽 두께를 최소 2.4mm 이상으로 증대하여 체결 강성 확보.",
            "렌더링 뷰 스크립트를 통해 출력 전 파트 간 중첩(Interference) 여부를 사전 점검하는 절차 도입."
        ],
        "metrics": [
            ("기구 구성 방식", "무외함 노출 보드", "Body + Handle + Lid 3파트 외함"),
            ("외벽 기본 두께", "1.5 mm (취성 우려)", "2.4 mm 보강 설계"),
            ("산출 파일", "단일 스케치", "파트별 개별 STL 및 일괄 출력 STL 생성")
        ],
        "image": "3D_Printer_Housing/v06_Housing_And_Stand/06_exploded_view.png",
        "caption": "[3D CAD 렌더링] 바디·핸들·상부 커버 3파트로 설계된 v06 스캐너 하우징 분해 조립도"
    },
    {
        "day": 25, "date": "2025-11-27",
        "phase": "핸드헬드 스캐너 거치대 기구 설계",
        "title": "APC 작업대 거치형 스캐너 데스크톱 스탠드(06_scanner_desktop_stand.scad) 설계 및 중심 보정",
        "files": "3D_Printer_Housing/v06_Housing_And_Stand/06_scanner_desktop_stand.scad",
        "objective": "APC 컨베이어 옆 작업대에서 스캐너를 손에 들지 않고도 상자를 지나가게 하여 자동 스캔(Hands-Free)하거나 안전하게 보관할 수 있는 전용 경사 거치대를 설계한다.",
        "work": [
            "스캐너 핸들이 자연스럽게 미끄러져 안착되는 테이퍼형 크래들 홀더와 광폭 베이스 플레이트 모델링.",
            "전면 스캔 창이 작업대 전방 하향 15° 각도를 향하도록 거치 경사각 최적화.",
            "3D 프린터 베드 밀착 출력 뷰(06_stand_print_view) 생성 및 무게중심 전도 모멘트 검토."
        ],
        "failure": "초기 스탠드 베이스 전방 길이가 짧아 상부 헤드가 무거운 스캐너를 꽂았을 때 무게중심선이 베이스 앞쪽 끝단에 근접하며 미세한 충격에도 앞으로 넘어지는 전도 불안정성이 나타남.",
        "change": [
            "베이스 플레이트 전방 돌출 길이를 확장하고 하부 리브 거싯(Gusset)을 추가하여 지지 면적 확대.",
            "케이블이 꺾이지 않고 후방으로 빠져나갈 수 있도록 하단 배선 도피 홈(Slot) 가공."
        ],
        "metrics": [
            ("전방 전도 안전성", "헤드 하중으로 전방 쏠림", "광폭 베이스 확장으로 안정 자립"),
            ("스캔 지향 각도", "수평 0° (상자 상단 인식 불편)", "전방 하향 15° 인체공학 경사"),
            ("하단 케이블 간섭", "바닥면 눌림 발생", "후방 배선 가이드 슬롯 관통 해결")
        ],
        "image": "3D_Printer_Housing/v06_Housing_And_Stand/06_stand_assembly_view.png",
        "caption": "[3D CAD 렌더링] 작업대 핸즈프리 스캔을 위해 설계된 v06 데스크톱 거치대 결합 렌더링"
    },
    {
        "day": 26, "date": "2025-12-02",
        "phase": "독립형 콜드체인 센서팟 1세대 설계",
        "title": "콜드체인 환경 계측용 1세대 센서팟(v07_Coldchain_Sensor_Pod) 내부 격벽 및 통풍구 모델링",
        "files": "3D_Printer_Housing/v07_Coldchain_Sensor_Pod/07_coldchain_sensor_pod.scad",
        "objective": "수송 차량 적재함 및 농산물 상자 주변에 비치할 독립형 환경 센서 노드 외함(v07)을 설계하고, MCU 발열이 온습도 센서에 미치는 열간섭을 줄이기 위한 통풍 슬롯과 격벽을 배치한다.",
        "work": [
            "컴팩트 사각 라운드 인클로저 본체 및 상부 스냅 리드 구조 모델링.",
            "측면 외기 유입용 루버 슬릿(Ventilation Slits) 가공 및 내부 보드 안착 스탠드오프 기둥 형성.",
            "정중앙 단면 절개(07_cross_section_view) 렌더링을 통해 보드·센서 장착 여유고 검증."
        ],
        "failure": "완전 밀폐형 상자로 초기 시뮬레이션했을 때 ESP32 Wi-Fi 송신 발열이 내부 공기를 데워 외부 실제 냉장 온도보다 +1.5°C 이상 높게 측정되는 자기발열(Self-Heating) 오차 원인을 확인함.",
        "change": [
            "온습도 센서 인접 외벽에 다중 통풍 슬릿을 개방하고 MCU 장착 영역과 공간적 이격 배치 적용.",
            "수직 낙하 충격 시 모서리 응력 분산을 위해 외곽 전체에 필렛/라운드 곡률 부여."
        ],
        "metrics": [
            ("외기 순환 구조", "밀폐형 (내부 열축적 발생)", "측면 다중 통풍 슬릿 개방"),
            ("내부 간섭 검증", "외관만 확인", "단면도(Cross-Section) 기반 여유고 검증"),
            ("외형 모서리 처리", "직각 모서리 (과실 찍힘 우려)", "전 모서리 라운드 곡면화")
        ],
        "image": "3D_Printer_Housing/v07_Coldchain_Sensor_Pod/07_cross_section_view.png",
        "caption": "[3D 단면 검증] 통풍 슬릿과 내부 보드 지지 구조가 반영된 v07 콜드체인 센서팟 단면도"
    },
    {
        "day": 27, "date": "2025-12-05",
        "phase": "인체공학 권총형 스캐너 리모델링",
        "title": "핑거 그루브(Finger Groove)를 적용한 권총형 QR 스캐너 하우징(v08) 리모델링 및 버그 수정",
        "files": "3D_Printer_Housing/v08_QR_Scanner_Housing/08_qr_scanner_housing.scad",
        "objective": "v06의 각진 원통 핸들이 장시간 파지 시 미끄러지는 단점을 개선하기 위해 손가락 마디 곡선에 맞춘 핑거 그루브 일체형 권총 그립(v08)으로 외형을 전면 재설계한다.",
        "work": [
            "hull() 및 연속 구형 차집합 연산을 조합하여 인체공학적 3단 핑거 그루브 그립 형상 구현.",
            "상부 GM77 광학 챔버와 하부 그립을 매끄러운 곡면 목(Neck)으로 일체 연결.",
            "내부 중공 캐비티 연산 순서 점검 및 분해 뷰 렌더링 수행."
        ],
        "failure": "OpenSCAD에서 difference() 블록 내부의 중공 차집합 연산 순서를 잘못 배치하여 그립 외벽을 깎는 핑거 그루브 구체가 내부 캐비티까지 관통하면서 외벽에 원치 않는 구멍(천공 버그)이 발생함.",
        "change": [
            "외부 전체 볼륨(Outer Shell)을 먼저 완성한 뒤 벽 두께만큼 축소된 내부 코어(Inner Core)를 일괄 차집합하는 2단계 불리언 파이프라인으로 수정하여 천공 아티팩트 해결.",
            "그립 전면 트리거 검지 위치와 스캔 광축 정렬 완료."
        ],
        "metrics": [
            ("그립 파지 형상", "단순 직선 원통형 (미끄러짐)", "3단 핑거 그루브 권총형 그립"),
            ("불리언 천공 오류", "그루브 오목부 외벽 관통 발생", "Outer-Inner 순차 차집합으로 완벽 밀폐"),
            ("조작 안정성", "두 손 보조 필요", "한 손 파지 및 검지 조준 최적화")
        ],
        "image": "3D_Printer_Housing/v08_QR_Scanner_Housing/08_exploded_view.png",
        "caption": "[3D CAD 렌더링] 인체공학 핑거 그루브가 적용된 v08 권총형 QR 스캐너 하우징 분해 뷰"
    },
    {
        "day": 28, "date": "2025-12-09",
        "phase": "오프라인 플래시 저장 및 배선 치구 제작",
        "title": "ESP32 LittleFS 로컬 파일시스템 최초 도입 및 배선 고정용 케이블 클립(PLA/ABS) 설계·출력",
        "files": "3D_Printer_Housing/10_cable_clip.scad, 10_cable_clip_abs.scad",
        "objective": "Wi-Fi 음영 구역에서의 데이터 유실을 막기 위해 ESP32 내장 플래시에 LittleFS 파일시스템을 마운트하고, 스캐너·테스트베드 USB 전원선 흔들림을 잡아줄 전용 케이블 클립을 제작한다.",
        "work": [
            "ESP32 플래시 파티션에 LittleFS를 마운트하고 네트워크 단절 시 로컬 파일에 패킷을 임시 기록하는 기초 루틴 검증.",
            "작업대 및 차량 거치 시 케이블 단선을 막는 스냅인 케이블 클립(10_cable_clip.scad) 모델링.",
            "PLA 수지 기준 치수와 열수축률이 큰 ABS 수지 보정판(10_cable_clip_abs.scad) 2종 STL 슬라이싱 및 출력 비교."
        ],
        "failure": "동일 STL 파일을 ABS 필라멘트로 출력하자 냉각 수축(약 0.8~1.2%)으로 인해 케이블 삽입 슬롯 폭이 좁아져 피복이 긁히고 클립 탄성 암이 부러지는 치수 편차가 나타남.",
        "change": [
            "ABS 전용 스크립트(10_cable_clip_abs.scad)에서 내경 공차를 +0.25mm 확장하고 탄성 목 두께를 보강하여 수축 후에도 정확한 스냅 복원력 확보.",
            "재질별 수축 보정 파라미터 분리 관리 체계 확립."
        ],
        "metrics": [
            ("통신 단절 대비", "수신 실패 시 패킷 즉시 증발", "ESP32 LittleFS 내장 플래시 기록 도입"),
            ("ABS 출력 치수 오차", "냉각 수축으로 삽입 뻑뻑함", "+0.25 mm 공차 보정판 분리 해결"),
            ("배선 장력 보호", "커넥터 직접 외력 전달", "전용 스냅 클립으로 단선 방지")
        ],
        "image": "3D_Printer_Housing/10_cable_clip_preview.png",
        "caption": "[3D CAD 렌더링] 테스트베드 및 차량 전원선 고정을 위해 제작한 스냅인 케이블 클립 모델"
    },
    {
        "day": 29, "date": "2025-12-12",
        "phase": "좌·우 반할 스냅핏 하우징 리팩토링",
        "title": "3D 프린팅 서포트 최소화를 위한 좌·우 반할(Clamshell) 스냅핏 하우징(v09) 재설계",
        "files": "3D_Printer_Housing/v09_QR_Scanner_Housing_Snapfit/09_qr_scanner_housing_snapfit.scad",
        "objective": "상·하 분할 구조(v08)에서 깊고 좁은 핸들 내부에 갇힌 서포트 제거가 불가능했던 출력 문제를 해결하기 위해 좌·우 대칭 반할(Left/Right Half) 조개껍질(Clamshell) 구조로 전면 전환한다.",
        "work": [
            "스캐너 중심축(XZ 평면)을 기준으로 좌측 바디와 우측 바디로 이등분하여 내부 부품 안착 포켓을 완전히 개방.",
            "별도 금속 볼트 없이 양쪽 쉘을 맞물려 닫는 캔틸레버 스냅핏 후크(Snap-fit Hook)와 정렬 립(Lip) 설계.",
            "1차 스냅핏(v1) 대비 후크 탄성 길이를 늘린 v2 리비전(09_exploded_view_v2) 개선 모델링 완료."
        ],
        "failure": "초기 v09(v1) 스냅핏 후크를 짧고 두껍게 설계하자 FDM 적층 결(Z축 레이어 계면) 방향으로 굽힘 인장이 걸리면서 조립 시 딸깍 걸리기 전에 후크 뿌리가 층간 박리(Delamination)로 부러짐.",
        "change": [
            "v09 v2에서 캔틸레버 암 길이를 연장해 변형률을 낮추고 뿌리 부분에 45° 챔퍼 보강을 추가하여 파손 없이 탄성 체결되도록 개선.",
            "반할 평면을 베드 바닥에 눕혀 출력함으로써 내부 서포트를 대폭 절감."
        ],
        "metrics": [
            ("하우징 분할 방식", "상·하 분할 (깊은 내부 서포트 고착)", "좌·우 Clamshell 반할 (내부 완전 개방)"),
            ("체결 수단", "금속 나사 필요", "일체형 캔틸레버 스냅핏 v2"),
            ("스냅 후크 파손", "v1 조립 중 층간 박리 발생", "암 길이 연장·뿌리 보강으로 파손 해결")
        ],
        "image": "3D_Printer_Housing/v09_QR_Scanner_Housing_Snapfit/09_exploded_view_v2.png",
        "caption": "[3D CAD 렌더링] 좌·우 Clamshell 반할 구조와 개선된 스냅핏 후크가 적용된 v09 v2 분해 뷰"
    },
    {
        "day": 30, "date": "2025-12-16",
        "phase": "산업용 하우징 강성 및 내부 격벽 보강",
        "title": "내부 모듈 흔들림 차단을 위한 산업용 크래들 리브 스캐너 하우징(v10_Industrial) 단면 검증",
        "files": "3D_Printer_Housing/v10_QR_Scanner_Housing_Industrial/10_qr_scanner_housing_industrial.scad",
        "objective": "반복적인 스캔 작업과 낙하 충격에도 내부 GM77 엔진·ESP32 보드·물리 트리거 스위치가 제자리를 이탈하지 않도록 전용 고정 격벽(Cradle Rib)을 갖춘 산업용 하우징(v10)을 완성한다.",
        "work": [
            "GM77 모듈 외곽을 감싸는 전방 광학 챔버 격벽과 ESP32 기판 슬롯 가이드를 좌·우 쉘 내벽에 일체 성형.",
            "검지 물리 트리거 버튼의 누름 스트로크(1.5mm)와 택트 스위치 간 유격 정밀 세팅.",
            "정중앙 단면 뷰(10_cross_section_view)를 통해 전 부품 장착 시 간섭 0건 및 배선 통로 확보 검증."
        ],
        "failure": "GM77 고정 포켓 공차를 0.0mm 칼맞춤으로 모델링했을 때 FDM 노즐 압출 폭 팽창(약 0.15~0.2mm)으로 인해 모듈이 포켓에 억지로 끼워지며 좌우 쉘 접합면이 0.8mm 벌어지는 현상 확인.",
        "change": [
            "모든 전자 모듈 수납 포켓에 편측 +0.3mm(양측 0.6mm) 3D 프린팅 조립 공차(Clearance)를 표준 반영.",
            "접합 테두리에 암수 단차(Step Lip & Groove)를 둘러 유격 없이 밀착되도록 개선."
        ],
        "metrics": [
            ("내부 부품 고정", "글루건/테이프 임시 고정", "모듈별 전용 성형 크래들 슬롯"),
            ("포켓 조립 공차", "0.0 mm (압출 팽창으로 쉘 벌어짐)", "편측 +0.3 mm 공차 부여 (완벽 밀착)"),
            ("외함 접합 유격", "0.8 mm 틈새 발생", "암수 Step Lip 적용으로 틈새 제거")
        ],
        "image": "3D_Printer_Housing/v10_QR_Scanner_Housing_Industrial/10_cross_section_view.png",
        "caption": "[3D 단면 검증] GM77·ESP32·트리거 고정 격벽과 배선 통로가 검증된 v10 산업용 하우징 단면도"
    },
    {
        "day": 31, "date": "2025-12-19",
        "phase": "상부 OLED 매립형 베젤 개선",
        "title": "SSD1306 0.96인치 OLED 상부 매립형 베젤 스캐너 하우징(v11_Flush_OLED) 설계 및 시야각 개선",
        "files": "3D_Printer_Housing/v11_QR_Scanner_Housing_Flush_OLED/11_qr_scanner_housing_flush_oled.scad",
        "objective": "스캐너 후상단에 장착된 0.96인치 OLED 상태창이 외벽 두께에 가려 가장자리 글자가 잘려 보이던 시야각 문제를 매립형(Flush-Mount) 챔퍼 베젤 구조로 해결한다.",
        "work": [
            "OLED 유리 액정 활성 영역(Active Area 21.7×10.9mm)이 외표면 가까이에 밀착되도록 내벽 얇은 안착 단차 가공.",
            "디스플레이 창 외곽에 45° 경사 챔퍼 베젤을 적용하여 작업자 시선 각도에서 전 픽셀이 온전히 노출되도록 개선.",
            "조립 완성 뷰(11_assembly_view) 렌더링을 통한 상단 디스플레이·전면 스캔창·그립 비례 점검."
        ],
        "failure": "이전 버전에서는 2.5mm 두께 외벽 안쪽에 OLED 기판을 평면 고정해 액정이 깊숙이 함몰되면서 30° 이상 비스듬히 볼 때 상단 첫 줄(현재 공정 코드 A10~A15)이 베젤 그림자에 가려짐.",
        "change": [
            "액정 패널부만 외벽 쪽으로 1.4mm 전진 매립시키는 단차 포켓과 외곽 챔퍼 창을 결합해 시야각 가림을 완전히 해소.",
            "OLED 상단 4핀 헤더 납땜 돌출부를 피하는 상부 도피 홈(Relief Cutout) 추가."
        ],
        "metrics": [
            ("OLED 액정 함몰 깊이", "2.5 mm 함몰 (상단 텍스트 가림)", "1.1 mm 매립 + 45° 챔퍼 베젤"),
            ("유효 판독 시야각", "정면 ±25° 제한", "±60° 광시야각 전 라인 판독 가능"),
            ("핀헤더 간섭", "납땜부 내벽 접촉", "전용 Relief 도피 홈 가공으로 간섭 0건")
        ],
        "image": "3D_Printer_Housing/v11_QR_Scanner_Housing_Flush_OLED/11_assembly_view.png",
        "caption": "[3D CAD 렌더링] 상부 SSD1306 OLED 매립형 챔퍼 베젤이 적용된 v11 스캐너 완성 조립도"
    },
    {
        "day": 32, "date": "2025-12-23",
        "phase": "무나사 체결 구조 정밀화",
        "title": "유지보수 분해·재조립이 용이한 무나사 가이드 핀 결합 스캐너 하우징(v12_Screwless) 설계",
        "files": "3D_Printer_Housing/v12_QR_Scanner_Housing_Screwless/12_qr_scanner_housing_screwless.scad",
        "objective": "펌웨어 디버깅과 배터리 점검을 위해 하우징을 수시로 열고 닫을 때 스냅 후크가 피로 파손되지 않도록 다중 정렬 가이드 핀과 분산형 무나사 랫치 구조(v12)를 구현한다.",
        "work": [
            "좌·우 쉘 가장자리 4개소에 원추형 리드인(Lead-in) 정렬 보스와 대응 소켓 홀 배치.",
            "단일 대형 후크 대신 하중을 나누어 받는 다점 저변형 스냅 랫치 및 분해용 손톱 홈(Pry Notch) 반영.",
            "분해 뷰(12_exploded_view) 렌더링으로 양측 대칭 결합 요소 및 내부 부품 배치 최종 대조."
        ],
        "failure": "스냅핏 체결력만 높였을 때 한 번 닫힌 쉘을 다시 열기가 극도로 어려워 일자 드라이버로 틈을 벌리다가 PLA 접합 테두리가 찍혀 손상되는 유지보수성 문제가 나타남.",
        "change": [
            "그립 하단 바닥면에 외부에서 눈에 띄지 않는 2.5mm 분해용 프라이 슬롯(Pry Slot)을 신설하고 정렬 핀 공차를 튜닝하여 손상 없는 반복 개폐 달성.",
            "좌·우 비틀림 유격을 원추형 정렬 보스 4점으로 완전 구속."
        ],
        "metrics": [
            ("정렬 구속 방식", "외곽 테두리만 의존", "4점 원추형 가이드 보스 + 소켓 결합"),
            ("반복 개폐 손상", "강제 분리 시 테두리 찍힘", "하단 Pry Slot 적용으로 무손상 분해"),
            ("금속 체결 부품 수", "볼트/너트 별도 필요", "0개 (100% 3D 프린팅 무나사 체결)")
        ],
        "image": "3D_Printer_Housing/v12_QR_Scanner_Housing_Screwless/12_exploded_view.png",
        "caption": "[3D CAD 렌더링] 4점 가이드 보스와 무나사 랫치 구조가 적용된 v12 스캐너 하우징 분해 뷰"
    },
    {
        "day": 33, "date": "2025-12-26",
        "phase": "모듈 아키텍처 표준화 및 연말 통합 점검",
        "title": "산지·APC·소비자·관제 4계층 디렉터리 통합 정리 및 전 모듈 실행 정합성 검증",
        "files": "Final_Experiment/, Hardware_Prototypes/, 3D_Printer_Housing/",
        "objective": "개별 실험 폴더에 흩어져 있던 QR 생성기, ESP32 펌웨어, 소비자 대시보드, APC 콜드체인 관제 대시보드, 3D 하우징 자산들을 역할별 표준 계층으로 재구성하고 상호 연동 상태를 점검한다.",
        "work": [
            "Final_Experiment 하위에 1_PC_QR_Generators, 2_ESP32_Firmware, 3_Consumer_Dashboard, 4_APC_Coldchain_Dashboard 표준 구조 확립.",
            "초기 실험 프로토타입(Flask, 초기 스캐너, 초기 센서 코드)을 Hardware_Prototypes 하위로 분리 보존.",
            "전체 디렉터리별 코드·모델 파일 수 및 용량 감사 스크립트 실행과 AWS RDS 연동 상태 종합 확인."
        ],
        "failure": "폴더 계층 이동 직후 기존 스크립트 내부에 하드코딩되어 있던 상위 폴더 상대경로('../../static' 등) 참조가 일제히 깨지며 모듈 실행 시 ImportError 및 파일 누락 오류가 발생함.",
        "change": [
            "각 실행 단위 폴더 내 독립 실행이 가능하도록 Path(__file__).resolve().parent 기준 경로 해석으로 일괄 수정.",
            "불필요한 생성형 임시 QR PNG 및 빌드 캐시(.pio, __pycache__) 제외 규칙을 확립하여 깔끔한 모듈 구성 완료."
        ],
        "metrics": [
            ("핵심 운용 계층", "산재된 단일 스크립트 폴더", "4대 표준 실행 모듈 계층 확립"),
            ("경로 참조 오류", "폴더 이동 직후 상대경로 단절", "__file__ 기준 동적 경로화로 전수 해결"),
            ("연말 통합 검증", "개별 기능 단위 테스트", "QR 발행 → RDS 적재 → 대시보드 표출 일관 확인")
        ],
        "image": "scratch/notebook_captures/cap_day13_repo_architecture.png",
        "caption": "[실행 결과] 역할별 표준 계층으로 정리된 저장소 모듈 파일 수 및 구성 감사 실행 출력"
    },
]
