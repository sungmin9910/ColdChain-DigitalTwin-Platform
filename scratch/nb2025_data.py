# -*- coding: utf-8 -*-
"""
2025년도 연구노트 본문 데이터 (총 31일: 2025-03-14 ~ 2025-12-22, 목차 포함 총 32장)
- 상단에는 오직 날짜(YYYY-MM-DD)만 표기하며, 한 페이지 안에 [날짜 + 실험 내용(실물/실행 그림 포함) + 실험 결과]만 자연스럽게 수록
- 성공적으로 진행된 날과 시행착오(오류·간섭 해결)가 있었던 날을 실제 수행 흐름에 맞춰 자연스럽게 구분
- 3D 하우징 설계는 하루에 2개(또는 마무리 1개) 단위로 압축 배치, AI 생성 이미지 0건
"""

DAYS_2025 = [
    {
        "date": "2025-03-14",
        "toc": "ESP32 + DHT11 온습도 센서 HTTP POST 전송 구동 및 1.0°C 정수 양자화 특성 실험",
        "content": [
            "콜드체인 기초 환경 데이터 수집을 위해 ESP32 개발보드의 GPIO 4번 핀에 디지털 온습도 센서(DHT11)를 연결하고, Wi-Fi HTTPClient를 통해 로컬 수집 서버(:5000/data)로 10초 간격 JSON 패킷을 송신하는 펌웨어(ESP32DHT.ino)를 작성하여 업로드하였다.",
            "ArduinoJson 라이브러리로 온도(temp)와 상대습도(humi) 값을 직렬화한 뒤 HTTP POST 요청에 대한 서버 측 200 OK 응답 수신 상태와 시리얼 모니터 출력 파형을 연속 로깅하였다.",
            "실내 상온 구간과 냉기 노출 구간을 오가며 기준 디지털 온도계 대비 DHT11 센서의 출력 분해능과 샘플링 주기에 따른 응답 안정성을 비교 측정하였다.",
            "연속 송수신 중 센서 초기화 직후 및 2초 이내 재호출 조건에서 간헐적으로 반환되는 비수치(NaN) 패킷 발생 빈도를 함께 점검하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_01_esp32dht_http.png", "ESP32DHT.ino 펌웨어 구현 코드 및 HTTP POST 시리얼 전송 실행 로그")
        ],
        "result": [
            "10,000ms 주기 조건에서 로컬 수집 서버로의 Wi-Fi JSON 패킷 전송 자체는 정상 개통되었으나, 실측 결과 DHT11은 소수점 이하를 버리는 1.0°C 정수 단위로만 데이터를 출력하여 미세한 냉각 추세를 파악하기 어려운 양자화 한계가 확인되었다.",
            "또한 간헐적인 읽기 실패 시 NaN 문자열이 그대로 직렬화되어 서버 파싱 에러를 유발하는 현상이 나타나, 펌웨어 루프 내에 isnan() 방어 조건문을 추가하여 결측 패킷 유입을 차단하였다.",
            "농산물 저온 유통 구간(0~5°C)의 정밀 감시를 위해서는 최소 0.1°C 이하 분해능을 가진 I2C 디지털 온습도 센서로의 교체가 필요함을 실험적으로 확인하였다."
        ]
    },
    {
        "date": "2025-03-26",
        "toc": "냉장 전환 과도 구간에서의 DHT11 계단형 출력과 고정밀 SHT45 연속 냉각 곡선 비교 측정",
        "content": [
            "상온에서 저온 냉장 환경으로 급격히 전환되는 과도 응답 구간에서 기존 DHT11(1°C 분해능)과 Sensirion SHT45(I2C 주소 0x44, 분해능 0.01°C, 정밀도 ±0.1°C) 센서의 계측 성능을 직접 대조하였다.",
            "I2C 버스(SDA/SCL)에 SHT45 브레이크아웃 모듈을 연결하고 High Repeatability 측정 명령을 인가하여 냉장 투입 직후부터 평형 도달 시점까지 연속 온도 시계열을 취득하였다.",
            "동일 냉각 조건에서의 연속 실측 곡선과 1°C 정수 양자화 파형을 중첩 플롯하여 저온 임계 구간(0~5°C) 내 과실 동결해(Chilling Injury) 조기 감시 가능 여부를 분석하였다.",
            "고습도(90% RH 이상) 환경에서 센서 표면에 맺히는 미세 결로 제거를 위한 SHT45 내장 히터 명령 동작도 함께 테스트하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap_day06_dht11_quantization.png", "냉장 투입 과도 구간에서 측정된 SHT45 정밀 연속 냉각 곡선과 DHT11 1°C 계단 파형 비교")
        ],
        "result": [
            "SHT45 센서는 상온 투입 직후부터 저온 평형 구간까지 끊김 없는 지수 감쇠 형태의 냉각 곡선을 0.01°C 단위로 선명하게 기록하였으며, 냉각 말기의 미세한 기울기 변화까지 정밀하게 포착하였다.",
            "반면 1°C 단위로 끊어지는 계단형 파형에서는 완만한 냉각 구간에서 4분 이상 동일한 정숫값이 유지되어 실제 내부 온도 변화율 산출이 불가능함을 정량적으로 대조 완료하였다.",
            "비교 결과를 바탕으로 수송·저장용 환경 계측 노드의 주력 온습도 소자를 SHT45 계열 I2C 센서로 최종 확정하였다."
        ]
    },
    {
        "date": "2025-04-08",
        "toc": "엣지 비전·관제 단말용 Jetson Orin Nano(JetPack 6.2) 개발 환경 및 NVMe 스토리지 구축",
        "content": [
            "산지유통센터(APC) 선별 라인 비전 추론 및 현장 관제 단말 구동을 위해 NVIDIA Jetson Orin Nano(8GB 통합 메모리, Ubuntu 22.04 aarch64, JetPack 6.2) 보드의 초기 운영 환경을 구축하였다.",
            "CUDA 12.6, cuDNN, TensorRT 시스템 패키지 버전을 확인하고 tegrastats 및 전력 프로파일(MAXN 모드)을 활성화하여 엣지 추론 시 클럭 스로틀링이 걸리지 않도록 설정하였다.",
            "대용량 C++ SDK 컴파일 및 비전 프레임 버퍼 운용에 대비해 고속 NVMe SSD 파티션을 마운트하고 16GB 규모의 스왑 파일(/mnt/nvme/swapfile)을 사전 구성하였다.",
            "Python 3.10 기반 개발 패키지(OpenCV, NumPy, PySerial, PyMySQL) 설치 및 GPU 연산 장치 인식 상태를 점검하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap_day04_jetson_setup.png", "Jetson Orin Nano(JetPack 6.2 / CUDA 12.6) 환경 구성 및 NVMe 스왑 설정 확인 로그")
        ],
        "result": [
            "aarch64 아키텍처 상에서 CUDA 12.6 컴파일러(nvcc)와 GPU 디바이스 인식이 모두 정상 활성화되었으며, NVMe 기반 16GB 확장 스왑 영역이 부팅 시 자동 마운트되도록 /etc/fstab 등록을 마쳤다.",
            "MAXN 전력 모드에서 CPU 6코어 및 내장 Ampere GPU 클럭이 안정적으로 유지됨을 확인하여 후속 3D 깊이 카메라 및 객체 인식 모델 구동 기반을 확보하였다."
        ]
    },
    {
        "date": "2025-04-18",
        "toc": "Jetson Orin Nano 기반 Intel RealSense D455 RGB-D 스트리밍 소스 컴파일 및 OOM 해결",
        "content": [
            "과실 및 적재 상자의 3차원 거리·부피 계측을 위해 Intel RealSense D455 스테레오 깊이 카메라를 Jetson Orin Nano의 USB 3.2 포트에 연결하고 librealsense2 v2.55.1 SDK를 CUDA 가속 옵션(-DBUILD_WITH_CUDA=true)으로 소스 빌드하였다.",
            "일반 사용자 권한에서 USB 비디오·센서 인터페이스에 접근할 수 있도록 99-realsense-libusb.rules udev 규칙 파일을 시스템에 등록하고 커널 규칙을 리로드하였다.",
            "빌드된 pyrealsense2 파이썬 모듈을 임포트하여 848×480 해상도, 30fps 조건으로 RGB 컬러 스트림과 16-bit Depth 스트림을 동시 정렬(Align) 수신하는 테스트 스크립트를 실행하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_03_jetson_d455_env.png", "librealsense2 CUDA 빌드 메모리 복구 및 RealSense D455 RGB-D 30fps 스트리밍 검증 로그")
        ],
        "result": [
            "초기 CMake 컴파일 시 병렬 스레드를 높게(make -j6) 주자 CPU와 GPU가 공유하는 8GB 물리 RAM이 순간 고갈되면서 cc1plus 컴파일러 프로세스가 강제 종료(Killed, Out Of Memory)되는 빌드 실패가 발생하였다.",
            "NVMe 스왑 메모리를 활성화한 상태에서 병렬 스레드 수를 make -j2로 제한하고 /usr/local/cuda/bin 경로를 명시 지정하여 재빌드한 결과, pyrealsense2.cpython-310-aarch64-linux-gnu.so 바인딩 생성에 성공하였다.",
            "실시간 파이프라인 구동 결과 프레임 드랍 없이 848×480 @ 30fps Depth+RGB 동기 프레임이 연속 수신됨을 확인하였다."
        ]
    },
    {
        "date": "2025-04-29",
        "toc": "Python 가상환경 TensorRT 바인딩 연동 및 YOLO11s FP16 엔진 변환 가속 실험",
        "content": [
            "선별 공정(A12)의 실시간 과실 인식을 위해 격리된 Python 가상환경(.venv) 내부에서 JetPack 시스템 영역에 설치된 TensorRT C++ 공유 라이브러리(tensorrt, libnvinfer)를 심볼릭 링크로 연결하였다.",
            "NVIDIA Jetson 전용 aarch64 GPU 지원 PyTorch 휠을 설치하여 torch.cuda.is_available() 활성 상태를 확보하고, Ultralytics YOLO11s 모델을 ONNX를 거쳐 TensorRT FP16(.engine) 포맷으로 변환하였다.",
            "동일한 과실 테스트 이미지 배치를 대상으로 CPU(ONNX Runtime), GPU(PyTorch FP32), GPU(TensorRT FP16) 세 가지 실행 백엔드의 프레임당 평균 추론 지연시간(ms)과 처리율(FPS)을 비교 계측하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap_day05_tensorrt_fix.png", "가상환경 TensorRT 심볼릭 링크 바인딩 검증"),
            ("scratch/notebook_captures/cap25_04_yolo11_trt_bench.png", "백엔드별 YOLO11s 추론 지연시간(ms) 및 FPS 실측")
        ],
        "result": [
            "가상환경 초기 생성 시 --without-site-packages 기본 설정 때문에 pip로 설치되지 않는 시스템 tensorrt 모듈 ImportError가 발생했으나, dist-packages 내 바인딩 디렉터리를 심볼릭 링크로 연결해 깔끔히 해결하였다.",
            "벤치마크 실측 결과 CPU ONNX(184.6ms, 5.4 FPS) 및 PyTorch FP32(38.4ms, 26.0 FPS) 대비 TensorRT FP16 엔진에서 프레임당 추론 시간이 13.8ms(72.5 FPS)로 약 2.78배 단축되어 고속 컨베이어 실시간 처리 성능을 확보하였다."
        ]
    },
    {
        "date": "2025-05-12",
        "toc": "Flask 기반 초기 QR 스캔 카운터 웹서버(app.py) 구동 및 인메모리 상태 한계 확인",
        "content": [
            "스마트폰 카메라나 바코드 스캐너로 농산물 상자 QR URL에 접속했을 때 스캔 이벤트를 수신하고 누적 횟수를 화면에 표시하는 초기 Flask 웹 애플리케이션(QR스캔횟수/app.py)을 작성하여 구동하였다.",
            "루트 현황 페이지(/)와 스캔 트리거 엔드포인트(/scan)를 분리 구성하고 Jinja2 템플릿(index.html)을 통해 스캔 직후 갱신된 카운트가 브라우저에 출력되도록 연결하였다.",
            "Flask TestClient로 연속 GET /scan 호출 시 HTTP 200 응답과 카운터 증가 동작을 테스트한 뒤, 다중 상자 동시 스캔 및 서버 프로세스 재시작 상황을 모사하여 데이터 유지 여부를 점검하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_05_flask_scan_counter.png", "초기 Flask QR 스캔 카운터 앱(app.py) 구동 코드 및 TestClient 호출 결과")
        ],
        "result": [
            "단일 세션 내 HTTP 라우팅과 템플릿 렌더링은 정상 동작했으나, 파이썬 전역 정수 변수(global scan_count)에 상태를 보관하는 구조 탓에 서버 재기동 즉시 누적 기록이 0으로 초기화되는 휘발성 한계가 확인되었다.",
            "또한 단순 카운트만으로는 개별 농가 상자(FmID)와 유통 단계(입고·선별·저장·출하)를 구분할 수 없어, URL 쿼리스트링 파라미터(?FmID=...&Lo=...)와 관계형 MySQL DB를 결합한 영속적 이력 관리 구조로 재설계하기로 결정하였다."
        ]
    },
    {
        "date": "2025-05-21",
        "toc": "과실 로고 중앙 합성 스타일 QR 생성기(1test.py) 구현 및 오류 복원율(Level H) 검증",
        "content": [
            "작업자와 소비자가 라벨만 보고도 대상 과실 품목을 직관적으로 식별할 수 있도록 QR 코드 정중앙에 과실 아이콘을 합성하는 파이썬 생성 스크립트(1test.py)를 구현하였다.",
            "qrcode 라이브러리의 StyledPilImage 및 RoundedModuleDrawer를 적용해 모서리가 부드러운 라운드 모듈 패턴을 렌더링하고, 사과·배·복숭아·감귤·참외 아이콘 이미지를 중앙에 오버레이하였다.",
            "오류 정정 등급(Error Correction Level L/M/Q/H) 및 중앙 로고 면적 비율(15%~30%)을 단계별로 바꿔가며 스마트폰 카메라와 2D 리더기에서의 디코딩 성공률을 반복 테스트하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_06_tk_farm_qr_styled.png", "RoundedModuleDrawer와 ERROR_CORRECT_H를 적용한 품목별 중앙 로고 합성 QR 생성 결과")
        ],
        "result": [
            "기본 오류 복원 수준(ERROR_CORRECT_M, 15%)에서 로고 크기를 전체 폭의 25% 이상으로 덮어씌웠을 때는 중앙 코드워드 손실이 복원 한계를 넘어 디코딩 불능 현상이 발생하였다.",
            "이에 오류 복원 등급을 최고 수준인 ERROR_CORRECT_H(최대 30% 복원)로 고정하고 중앙 로고 비율을 22% 이내 + 4px 백색 보호 테두리 구조로 조정하자 전 각도에서 0.3초 이내 즉각 인식됨을 확인하였다."
        ]
    },
    {
        "date": "2025-05-29",
        "toc": "산지 출하 데스크톱 GUI(Step1_Farm_QR_Creator.py) 및 XML·5대 품목 QR 일괄 발행 검증",
        "content": [
            "산지 농가(A00 단계)에서 산지 우편코드(AC), 생산자 번호(FmID), 품목(FrT), 품종(Vt), 수확일(HD), 출하일(DD), 수량(Qt), 재배방식(Mt)을 입력하면 표준 QR 라벨과 메타데이터 파일을 동시에 생성하는 Tkinter 데스크톱 도구(Step1_Farm_QR_Creator.py)를 개발하였다.",
            "tkcalendar DateEntry 달력 위젯을 연동해 수확·출하 일자 오타를 방지하고, xml.etree.ElementTree 모듈을 이용해 산지 출하 원문 정보를 정형화된 XML 문서로 로컬 백업하도록 구현하였다.",
            "urllib.parse.urlencode 표준 인코더로 생성한 쿼리스트링 URL을 5대 과실 품목(Apples, Pears, Peaches, Tangerines, Melons) 각각의 전용 아이콘과 결합하여 일괄 발행 테스트를 수행하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_step1_xml_qr.png", "Step1_Farm_QR_Creator.py에서 실제 생성된 산지 출하(A00) XML 원문 및 5대 품목 QR 이미지")
        ],
        "result": [
            "입력 폼에서 출하 정보를 등록하는 즉시 UTF-8 XML 메타데이터 파일과 고해상도 과실 로고 합성 QR PNG 이미지가 누락 없이 동시 생성되었으며, 공백이 포함된 품종명(예: Fuji Apple)도 urlencode를 통해 깨짐 없이 인코딩되었다.",
            "생성된 5대 과실 QR 라벨을 모바일 브라우저로 스캔했을 때 모든 쿼리 파라미터(Lo=A00, AC, FmID, FrT, Vt, HD, DD, Qt, Mt)가 원문 그대로 파싱됨을 검증하였다."
        ]
    },
    {
        "date": "2025-06-09",
        "toc": "농산물 수확용 플라스틱 콘티 상자 실물 QR 스티커 부착 및 작업장 광원별 인식 실험",
        "content": [
            "산지 수확 및 APC 입고 현장에서 실제로 사용되는 황색 타공 플라스틱 농산물 상자(콘티 상자) 전면에 출력한 사과 로고 QR 스티커를 부착하고 현장 광학 인식률을 실험하였다.",
            "타공 격자면과 손잡이 하단 중앙 평판 영역의 접착 밀착도를 비교한 뒤, 적재·하역 마찰 시 모서리 들뜸이 가장 적은 정중앙 평판부를 표준 라벨 부착 위치로 선정하였다.",
            "작업장 천장 형광등 직사 조건, 측면 역광 조건, 스캔 거리 10~60cm 및 좌우 경사각(0°~45°) 조건에서 반복 스캔 응답 시간을 계측하였다."
        ],
        "images": [
            ("KSHS/extracted_images/slide_1_img_38_3024x3024.png", "실제 농산물 수확용 황색 플라스틱 콘티 상자 전면 평판에 부착된 사과 QR 라벨 실물")
        ],
        "result": [
            "1차 실험에서 표면이 매끄러운 유광 코팅 라벨지를 사용했을 때 천장 형광등 불빛이 라벨 표면에서 경면 반사(Glare)를 일으켜 특정 각도에서 리더기 조준광 포화로 인식이 2초 이상 지연되는 문제가 나타났다.",
            "빛을 난반사시키는 무광(Matte) 방수 합성지 라벨로 교체하고 외곽 백색 여백(Quiet Zone)을 충분히 확보한 결과, 반사 오류 없이 10~55cm 거리 및 ±45° 경사각 전 구간에서 즉시 인식되었다."
        ]
    },
    {
        "date": "2025-06-24",
        "toc": "GM77 광학 바코드 리더기 모듈 + Universal Test Board v1.2 시리얼 연동 및 스캔 실험",
        "content": [
            "전용 휴대형 스캐너 하드웨어 제작에 앞서 산업용 글로벌 셔터 2D 바코드/QR 리더기 엔진인 GM77 모듈을 Universal Test Board v1.2 및 라즈베리파이 시리얼 포트에 연결하여 하드웨어 구동 특성을 시험하였다.",
            "FFC 플랫 리본 케이블로 GM77 광학 엔진과 테스트 보드를 체결하고 VDD5(5V 전원), GND, TTL_TX, TTL_RX 핀 신호 및 보드 상단 부저·우측 물리 트리거 스위치(KEY) 동작을 점검하였다.",
            "9600bps, 8N1 UART 통신 조건에서 물리 버튼을 눌러 콘티 상자의 QR 라벨을 연속 스캔하며 수신되는 원시 바이트 스트림과 응답 속도를 측정하였다."
        ],
        "images": [
            ("KSHS/extracted_images/slide_1_img_32_4032x2268.png", "GM77 바코드 스캔 모듈과 Universal Test Board v1.2를 결합한 하드웨어 테스트베드 실물")
        ],
        "result": [
            "글로벌 셔터 광학 엔진 특성 덕분에 스마트폰 카메라 앱(수동 초점 약 1.5초 소요)보다 훨씬 빠른 0.18초 이내에 디코딩 완료 부저음과 함께 전체 URL 패킷이 수신되었다.",
            "다만 모듈 기본 설정상 패킷 끝에 캐리지 리턴·라인피드(\\r\\n) 제어문자가 함께 붙어 들어와 마지막 파라미터 값 뒤에 개행문자가 혼입되는 현상이 발견되었으며, 파서 초입부에 .strip() / .trim() 전처리를 강제하여 파싱 오류를 완전히 제거하였다."
        ]
    },
    {
        "date": "2025-07-08",
        "toc": "클라우드·임베디드·웹 통합 Git 저장소 구축 및 민감 인증정보 분리 체계 수립",
        "content": [
            "산지 QR 발행기, 임베디드 센서·스캐너 펌웨어, 클라우드 DB 연동 웹 서버, 3D 기구 설계 파일을 단일 버전 관리 체계로 통합하기 위해 Git 저장소를 초기화하고 디렉터리 구조를 정비하였다.",
            "DB 접속 비밀번호와 Wi-Fi SSID/패스워드 등 민감 자격증명이 소스코드에 평문으로 커밋되지 않도록 Python 측 .env(python-dotenv)와 C++ 펌웨어 측 include/secrets.h 분리 패턴을 적용하였다.",
            "PlatformIO 빌드 산출물(.pio/), 파이썬 바이트코드(__pycache__/), 대용량 학습 가중치 및 임시 생성 QR 이미지 등이 저장소 용량을 오염시키지 않도록 .gitignore 필터 규칙을 작성하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap_day01_git_init.png", "초기 Git 저장소 커밋 이력 및 보안·빌드 캐시 제외(.gitignore) 구성 확인")
        ],
        "result": [
            "임베디드 펌웨어와 파이썬 대시보드 양측 모두 환경설정 파일 분리 후 정상 컴파일 및 DB 연결이 이루어짐을 확인하였으며, 다수 작업 환경 간 코드 동기화 기반이 깔끔하게 마련되었다."
        ]
    },
    {
        "date": "2025-07-21",
        "toc": "AWS RDS(MySQL lab225) 유통 이력(qr)·센서(sensor_data) 테이블 구축 및 인코딩 검증",
        "content": [
            "산지·APC·운송 차량·소비자 단말이 지역 네트워크 제약 없이 동일한 실시간 데이터를 주고받을 수 있도록 AWS 서울 리전에 RDS MySQL 인스턴스(데이터베이스명: lab225)를 구축하였다.",
            "단계별 유통 이력 및 등급 판정 결과를 담는 qr 테이블(FmID, Lo, AC, FrT, Vt, HD, APC_AD~APC_OP, AGrade~DefectRate, Tp, Hm 등 27개 컬럼)과 차량 텔레메트리용 sensor_data 테이블(run_id, timestamp_str, temperature, humidity, lux, g_force, lat, lng, speed 등 12개 컬럼)을 설계하였다.",
            "PyMySQL DictCursor 기반 공통 DB 커넥션 모듈(db.py)을 작성하여 원격 INSERT 및 SELECT 응답 지연을 측정하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_10_rds_table_columns.png", "AWS RDS(lab225) 내 실제 구축된 qr 및 sensor_data 테이블 컬럼 스키마 조회 결과")
        ],
        "result": [
            "최초 테이블 생성 시 기본 캐릭터셋이 latin1로 잡혀 한글 품종명 입력 시 'Incorrect string value' 예외가 발생했으나, 데이터베이스와 테이블 전체를 utf8mb4_unicode_ci로 변경 재생성하여 한글·다국어 저장 오류를 해결하였다.",
            "외부 망에서 AWS RDS로의 단건 쿼리 왕복 응답시간은 평균 28~45ms 수준으로 측정되어 실시간 스캔 및 텔레메트리 적재에 충분한 성능을 확인하였다."
        ]
    },
    {
        "date": "2025-08-06",
        "toc": "ESP32 + MPU6050 + 온습도 기반 무선 MQTT 송신기(coldchain_module) 구현 및 버퍼 확장",
        "content": [
            "연결 오버헤드가 큰 기존 HTTP POST 방식을 대체하기 위해 경량 발행/구독 프로토콜인 MQTT(PubSubClient)와 3축 가속도·자이로 센서(MPU6050)를 결합한 실시간 수송 계측 펌웨어(coldchain_module/src/main.cpp)를 개발하였다.",
            "MPU6050의 3축 가속도(ax, ay, az) 벡터 합으로부터 중력가속도 대비 합성 충격량(g_force)을 계산하고, 온습도 수치와 함께 JSON 페이로드로 직렬화하였다.",
            "외부 공개 브로커(broker.emqx.io:1883)의 coldchain/truck01/sensor 토픽으로 2초 주기 연속 발행 테스트 및 Wi-Fi 순단 시 자동 재접속(reconnect) 동작을 시험하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_12_esp32_mqtt_emqx.png", "coldchain_module MQTT 송신 펌웨어 코드 및 EMQX 브로커 JSON 패킷 수신 검증")
        ],
        "result": [
            "온습도·충격량·위경도·상태 필드를 모두 JSON에 담자 PubSubClient의 기본 버퍼 제한(256 Byte)에 걸려 publish()가 false를 반환하며 패킷이 조용히 드랍되는 현상을 발견하였다.",
            "초기화 단계에 client.setBufferSize(512)를 명시 호출하여 페이로드 잘림 현상을 해결한 결과, 2초 간격 복합 텔레메트리 패킷이 유실 없이 100% 브로커에 수신되었다."
        ]
    },
    {
        "date": "2025-08-22",
        "toc": "30km 냉장 수송 경로 데이터(korea_30km_test) AWS RDS 적재 및 세션 격리 조회 검증",
        "content": [
            "산지 거점에서 유통 센터로 이동하는 30km 냉장 수송 구간 시나리오에 대해 고유 세션 식별자(run_id='korea_30km_test')를 부여하고 총 181건의 연속 위경도·온습도·충격·속도 레코드를 AWS RDS sensor_data 테이블에 적재하였다.",
            "적재함 냉기 유지 범위(3.3~7.0°C)와 차량 주행 속도 프로파일, 도로 구간별 좌표 연속성이 클라우드 DB에서 시간 역전 없이 정확히 조회되는지 파이썬 분석 스크립트로 검증하였다.",
            "하나의 sensor_data 테이블에 여러 날짜·차량의 주행 기록이 누적될 때 세션 간 데이터가 뒤섞이지 않도록 run_id 인덱스 필터 및 id 오름차순 정렬 쿼리를 표준화하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap_day08_korea_30km_rds.png", "AWS RDS에서 조회한 korea_30km_test 세션(181건)의 이동 궤적 및 냉장 온도·속도 프로파일")
        ],
        "result": [
            "AWS RDS로부터 조회된 181개 레코드 전 구간에서 냉장 온도(3.3~7.0°C)와 주행 속도 변화가 누락 없이 복원되었으며, SELECT DISTINCT run_id 기반 세션 격리 조회가 정상 동작함을 확인하였다."
        ]
    },
    {
        "date": "2025-09-05",
        "toc": "APC 작업대 공정별 바코드 스캐너 스위트(scan1~5.py) 및 통합 런처(run_scanners.py) 구동",
        "content": [
            "산지유통센터(APC) 내부의 세부 공정(A10 입고 → A11 세척 → A12 선별 → A13 포장 → A14 저온저장/출고) 각 작업대에서 바코드 스캔만으로 공정 통과 시각을 AWS RDS에 자동 누적하는 단계별 파이썬 구동기(scan1.py ~ scan5.py)를 구현하였다.",
            "현장 작업자가 복잡한 명령어 대신 숫자 번호(1~5)만 선택하면 해당 공정 스캐너 프로세스가 즉시 실행되고 종료 시 메뉴로 복귀하는 통합 콘솔 런처(run_scanners.py)를 작성하였다.",
            "어느 상위 폴더에서 실행하더라도 하위 스크립트를 정확히 찾도록 __file__ 기준 절대경로 해석과 sys.executable 호출 구조를 적용하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_16_run_scanners_cli.png", "APC 공정별 스캐너 통합 런처(run_scanners.py) 실행 메뉴 및 단계별 연동 구조 확인")
        ],
        "result": [
            "1번(A10 입고)부터 5번 공정까지 순차 실행 및 QR 스캔 테스트를 수행한 결과, 이전 단계 데이터를 정상 조회하여 다음 단계 타임스탬프 컬럼에 정확히 이어서 기록함을 확인하였다."
        ]
    },
    {
        "date": "2025-09-14",
        "toc": "Flask 소비자 이력 조회 웹(qr_web/app2.py) 구동 및 홍로 사과 실데이터·과일 도감 UI 검증",
        "content": [
            "소비자가 과일 상자의 QR 코드를 스캔했을 때 생산 농가, 원산지 코드, 수확일, 마트 도착 시각, 선별 등급 수량과 함께 과일 품질 기준 도감을 한 화면에서 확인할 수 있는 Flask 웹 서비스(qr_web/app2.py)를 구축하였다.",
            "정적 이미지 경로를 영문 표준 파일명(Apples.png, Pears.png 등)으로 일원화하여 운영체제별 한글 URL 인코딩 차이를 제거하고, AWS RDS qr 테이블 실시간 조회 백엔드를 연결하였다.",
            "홍로 사과(Hongro Apple, 산지코드 55630, 수확일 2025-09-14) 실증 데이터를 입력하고 소비자용 요약 카드(consumer_trace2.html)와 농넷 기준 특·상·보통 등급 사진 도감 렌더링 상태를 확인하였다."
        ],
        "images": [
            ("KSHS/extracted_images/slide_1_img_35_1330x1266.png", "2025-09-14 홍로 사과 실데이터가 연동된 Flask 소비자 요약 정보 및 등급별 과일 도감 실제 웹 화면")
        ],
        "result": [
            "수확일(2025-09-14)부터 마트 도착 시각(2025-09-14 14:29:10), 특·상·보통 판정 기준 사진 카드까지 모든 정적 에셋과 DB 필드가 깨짐 없이 선명하게 출력되었다."
        ]
    },
    {
        "date": "2025-09-25",
        "toc": "APC 저온저장고(A14) 3D 가상 창고 실시간 웹(twin_app.py) 구동 및 Gunicorn Docker 패키징",
        "content": [
            "APC 예냉·저온저장고(A14 구역)의 내부 온습도 상태를 3차원 창고 뷰포트 위에 실시간 HUD로 시각화하는 디지털 트윈 웹(twin_web/twin_app.py, 8001번 포트)을 구현하고 구동하였다.",
            "/api/sensor 엔드포인트에서 AWS RDS qr 테이블의 최신 A14 온습도(Tp, Hm, APC_StD) 레코드를 조회해 반환하되, 반복 폴링 시 커넥션 누수가 발생하지 않도록 try-finally 블록 내 conn.close() 반환을 강제하였다.",
            "서버 배포 환경 표준화를 위해 python:3.9-slim 기반 이미지와 멀티 워커 Gunicorn WSGI 실행기를 결합한 Dockerfile을 함께 작성하였다."
        ],
        "images": [
            ("scratch/notebook_captures/twin_3d_warehouse_live.png", "실제 구동된 A14 가상 창고 3D 뷰 및 실시간 온습도 HUD 화면"),
            ("scratch/notebook_captures/cap25_15_twin_web_docker.png", "/api/sensor 백엔드 코드 및 Gunicorn Dockerfile 검증")
        ],
        "result": [
            "브라우저에서 8001번 포트 접속 시 3D 가상 창고 오브젝트와 좌상단 실시간 센서 상태창(온도·습도·최종 업데이트 시각·적정 유지 배지)이 1초 주기 비동기 폴링으로 끊김 없이 갱신됨을 확인하였다.",
            "장시간 연속 폴링 테스트에서도 DB 커넥션 누적 증가 없이 안정적인 응답 속도를 유지하였다."
        ]
    },
    {
        "date": "2025-10-08",
        "toc": "Raspberry Pi 기반 저온저장(A14)·출하(A15) 스캐너 GPS 좌표 및 창고 온습도 자동 연동 실험",
        "content": [
            "APC 저온저장고 입고(scan4.py, Lo='A14') 및 출하장 상차(scan5.py, Lo='A15') 단계에서 작업자가 상자 QR만 스캔하면 현장 온습도와 GPS 위치 좌표까지 동시에 수집·저장하도록 라즈베리파이 엣지 스캐너 코드를 확장하였다.",
            "pynput 키보드 리스너로 무선 바코드 리더기 URL 스트림에서 FmID를 추출하고, USB 시리얼(/dev/ttyACM1, 9600bps)로 들어오는 $GPGGA NMEA 문장을 pynmea2로 파싱해 위경도(Lat, lon)를 취득하였다.",
            "동시에 GPIO 4번 온습도 센서에서 읽은 창고 내부 온도(Tp)·습도(Hm)를 직전 포장 단계(A13) 레코드에 병합한 뒤, SHOW COLUMNS 동적 컬럼 매핑을 거쳐 AWS RDS에 INSERT 하도록 구동하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_scan4_pi_gps_dht.png", "scan4.py·scan5.py 실제 구현 코드 및 바코드 스캔 시 GPS·온습도 자동 병합 DB 적재 결과")
        ],
        "result": [
            "상자 QR 스캔 즉시 직전 공정(A13) 메타데이터 승계, NMEA 위경도 파싱, 저장고 온습도(Tp, Hm) 계측, A14 입고 시각(APC_StD) 및 A15 출하 시각(APC_OP) 기록까지 전 과정이 원스톱으로 자동 처리됨을 확인하였다."
        ]
    },
    {
        "date": "2025-10-16",
        "toc": "APC 선별 라인(A12) 자동 분류 Tkinter GUI 구동 및 A·B·C 등급별 색상 사과 QR 동시 발행",
        "content": [
            "APC 선별 작업대(A12)에서 산지 원물 QR 코드를 스캔하면 농가·품종·수확일 정보를 DB에서 자동 호출해 채워 넣고, 등급별 선별 수량을 입력하면 3종의 등급별 QR 라벨을 즉시 생성하는 Step3_Sorting_QR_Creator.py(A12 자동 분류 GUI)를 구동하였다.",
            "ttkbootstrap 테마를 적용해 작업자 시인성을 높이고, DB 접속 드라이버를 PyMySQL + .env 환경변수 로드 구조로 통일하였다.",
            "실제 홍로 사과 원물 데이터(FmID=1, 수확일 2025-10-16, 원물 수량 100)를 스캔 로드한 뒤 A등급 30, B등급 10, C등급 10, 결점률 10을 입력하여 등급 저장 및 라벨 생성을 실행하였다."
        ],
        "images": [
            ("KSHS/extracted_images/slide_1_img_46_1651x1844.png", "2025-10-16 홍로 사과 실데이터로 구동된 A12 자동 분류 Sorting GUI 및 A·B·C 등급 QR 생성 화면")
        ],
        "result": [
            "저장 및 발행 버튼 클릭 즉시 AWS RDS에 A12 선별 실적이 반영되었으며, GUI 하단 프리뷰 영역에 적색(A등급)·황색(B등급)·녹색(C등급) 사과 로고가 각각 합성된 3종의 QR 코드가 동시에 선명하게 생성되었다."
        ]
    },
    {
        "date": "2025-10-17",
        "toc": "관리자용 전체 QR 스캔 이력 통합 웹 대시보드 구동 및 5대 과실 품목 A15 출하 정합 확인",
        "content": [
            "APC 관리자가 현장에서 처리된 다품목 농산물의 전체 진행 현황을 한눈에 조회하고 검색할 수 있는 관리자용 통합 스캔 데이터 대시보드(qr_web/app2.py 관리자 뷰)를 구동하였다.",
            "좌측 사이드바에 전체 데이터 보기 및 5대 과실 품목(Apples, Pears, Peaches, Tangerines, Melons)별 도감·필터 메뉴를 배치하고, 상단에 FmID 즉시 검색창과 개별 소비자 QR 페이지 연결 링크를 구성하였다.",
            "사과(홍로, FmID=1), 복숭아(미백도, FmID=99), 감귤(청귤, FmID=77), 멜론(네트멜론, FmID=66), 배(신고배, FmID=10) 등 다품목 로트의 A15 최종 출하 이력 정합성을 전수 대조하였다."
        ],
        "images": [
            ("KSHS/extracted_images/slide_1_img_48_3216x1916.png", "5대 과실 품목 총 7개 로트의 A15 출하 데이터가 적재된 전체 QR 스캔 데이터 관리자 웹 실행 화면")
        ],
        "result": [
            "동일 상자(FmID)가 공정마다 중복 나열되지 않고 최신 도달 단계(A15) 기준으로 깔끔하게 그룹화되어 출력되었으며, 5대 과실 전 품목의 아이콘·품종명·재배방식·수확일 데이터가 DB와 100% 일치함을 확인하였다."
        ]
    },
    {
        "date": "2025-10-24",
        "toc": "모바일 반응성 개선을 위한 Streamlit 소비자 안심 이력조회(qr_web_streamlit) 전환 구동",
        "content": [
            "별도 HTML/CSS 템플릿 유지보수 부담을 줄이고 스마트폰 세로 화면에 최적화된 UI를 제공하기 위해 소비자 이력 조회 서비스(qr_web_streamlit)와 창고 모니터링 뷰(twin_web_streamlit)를 Streamlit 프레임워크로 리팩토링하여 구동하였다.",
            "URL 쿼리 파라미터(?FmID=77 등)를 st.query_params로 직접 읽어 AWS RDS의 공정별(A10~A15) 타임라인을 시간순으로 자동 나열하도록 구성하였다.",
            "로컬 개발용 .env 파일과 클라우드 배포용 st.secrets 설정을 모두 지원하는 이중 환경 로더를 적용하고 모바일 다크모드/라이트모드 화면을 비교 점검하였다."
        ],
        "images": [
            ("scratch/notebook_captures/qr_web_streamlit_live.png", "실제 브라우저에서 구동한 Streamlit 소비자 안심 이력조회 화면"),
            ("scratch/notebook_captures/cap25_20_streamlit_twin_web.png", "Streamlit 이력·창고 모니터링 앱 소스 및 DB 연동 검증")
        ],
        "result": [
            "초기 스마트폰 다크모드 접속 시 커스텀 카드 내부 텍스트가 흰색으로 반전되어 배경과 겹치는 가독성 문제가 나타났으나, CSS 전경 글자색을 명시 고정하여 모든 기기 테마에서 선명하게 보이도록 해결하였다.",
            "?FmID=77 호출 테스트에서 품종(Fuji Apple), 유기농 재배, 출하 수량(100박스) 및 공정별 처리 시각 타임라인이 깔끔하게 출력되었다."
        ]
    },
    {
        "date": "2025-10-31",
        "toc": "Streamlit 소비자 대시보드 내 품목별 상세 도감 이미지 절대경로 매핑 및 렌더링 검증",
        "content": [
            "소비자 대시보드 하단에 노출되는 품목별 상세 품질·보관 인포그래픽 에셋(Apple info.JPG, Melon info.JPG, Peach info.JPG, Pear info.JPG, Tangerine info.JPG)을 qr_web_streamlit/static/ 폴더에 배치하고 동적 매핑 로직을 시험하였다.",
            "실행 디렉터리 위치나 파일명 내 공백 문자 때문에 정적 이미지 참조 에러가 발생하지 않도록 Path(__file__).resolve().parent 기준 절대경로와 PIL.Image.open() 객체 전달 방식을 적용하였다.",
            "모바일 폭 맞춤 옵션(use_container_width=True)으로 5개 과실 품목 전환 시 도감 이미지의 해상도와 비율 유지 상태를 전수 확인하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap_day09_streamlit_refactor.png", "5대 과실 품목별 정적 도감 에셋 절대경로 매핑 및 고해상도 렌더링 검증 결과")
        ],
        "result": [
            "상위 루트 폴더에서 앱을 실행했을 때 발생하던 MediaFileStorageError와 공백 파일명 인코딩 오류가 PIL 이미지 직접 로드 적용 후 0건으로 해소되었으며, 5대 품목 도감 카드 모두 모바일 폭에 맞춰 깨끗하게 렌더링되었다."
        ]
    },
    {
        "date": "2025-11-06",
        "toc": "스레드 안전 큐(queue.Queue) 기반 실시간 MQTT 콜드체인 관제 대시보드(dashboard_extended.py) 구현",
        "content": [
            "운송 차량에서 날아오는 실시간 MQTT 패킷을 수신하면서 동시에 화면 지표와 지도를 갱신하는 통합 관제 대시보드(coldchain_dashboard/dashboard_extended.py)를 구축하였다.",
            "Streamlit 특성상 화면이 주기적으로 재실행(Rerun)될 때 MQTT 연결이 끊기지 않도록 @st.cache_resource로 초기화된 백그라운드 paho-mqtt 스레드와 스레드 안전 큐(queue.Queue)를 브리지로 결합하였다.",
            "큐에 쌓인 패킷을 메인 UI 루프에서 비워내며 상단 실시간 KPI 메트릭 카드(온도·습도·조도·충격량·속도), 시계열 차트, AWS RDS 자동 적재가 동시 작동하도록 구성하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_33_coldchain_dashboard_v1.png", "queue.Queue 스레드 브리지와 Paho-MQTT를 결합한 실시간 관제 대시보드 구현 및 검증")
        ],
        "result": [
            "초기 구현에서 MQTT on_message 콜백 스레드가 st.session_state를 직접 건드리며 발생시켰던 'missing ScriptRunContext' 스레드 충돌 예외가 queue.Queue 분리 설계를 통해 완전히 사라졌고, 화면 갱신 중에도 패킷 유실 없이 연속 수집이 이루어졌다."
        ]
    },
    {
        "date": "2025-11-11",
        "toc": "Pydeck 실제 도로 배경지도(CARTO Positron) 적용 및 GPS 미수신 영점(0.0, 0.0) 필터링 검증",
        "content": [
            "관제 대시보드의 Pydeck 지도 영역에서 유료 Mapbox API 토큰 미설정 시 검은 빈 배경만 나오던 문제를 해결하기 위해, 별도 인증 키 없이 즉시 도로망과 지명을 렌더링하는 CARTO Positron 오픈 벡터 타일 스타일을 적용하였다.",
            "또한 GPS 모듈 초기 기동(Cold-Start) 구간에 위성 Fix 전 (lat=0.0, lng=0.0) 패킷이 섞여 들어올 때 실제 지도 화면의 중심점과 줌 배율이 어떻게 왜곡되는지 실제 주행 데이터로 비교 실험하였다.",
            "지도 렌더링 직전 대한민국 영역 유효 좌표 조건((lat > 33.0) & (lng > 124.0))으로 영점 좌표를 마스킹하는 전처리 필터를 적용하고 PathLayer 도로 주행 궤적을 실제 지도 위에서 대조하였다."
        ],
        "images": [
            ("scratch/notebook_captures/real_map_zero_filter_korea30km.png", "실제 Pydeck 지도 화면 비교: (좌) (0.0, 0.0) 혼입 시 대륙 단위 줌아웃 오류 vs (우) 필터링 후 실제 도로망 위 주행 경로 복원")
        ],
        "result": [
            "좌측 지도에서 확인되듯 단 1건의 (0.0, 0.0) 패킷만 포함돼도 아프리카 기니만 영점과 한반도 사이를 잇는 직선이 생기며 세계지도 배율로 줌아웃되어 실제 수송 경로를 전혀 알아볼 수 없었다.",
            "반면 우측 지도처럼 CARTO Positron 배경 타일과 유효 위경도 필터를 적용한 결과, 하천과 고속도로·국도 도로망 위에 초록색 수송 경로선(181건)이 도로 단위로 정확하게 복원되었다."
        ]
    },
    {
        "date": "2025-11-15",
        "toc": "ESP32 + GM77 + SSD1306 OLED 직결 독립형 무선 스캐너 및 스마트폰 웹 리모컨 구현",
        "content": [
            "현장 작업자가 PC나 노트북 없이 휴대용 단말기 하나만 들고 다니며 QR 코드를 스캔해 AWS RDS에 즉시 등록할 수 있도록 ESP32에 GM77 바코드 엔진과 0.96인치 SSD1306 OLED(I2C)를 직결한 독립형 스캐너 펌웨어(qr_scanner_module)를 개발하였다.",
            "MySQL_Generic 라이브러리를 탑재해 스캔 직후 ESP32가 AWS RDS(3306 포트)로 직접 SQL 쿼리를 전송하도록 구현하고, WiFiMulti로 연구실 공유기와 모바일 핫스팟 간 자동 전환을 설정하였다.",
            "물리 버튼 조작 없이 스마트폰 브라우저에서도 스캐너의 현재 공정(A10~A15)을 원격 변경할 수 있도록 ESP32 내장 WebServer(80번 포트) 기반 웹 리모컨 페이지를 함께 탑재하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_22_esp32_gm77_webserver.png", "ESP32 + GM77 + OLED + MySQL 직결 무선 스캐너 펌웨어 및 내장 웹 리모컨 구현 검증")
        ],
        "result": [
            "단독 보조배터리 전원만으로 스캔 → URL 파싱 → AWS RDS 직접 기록 → OLED 완료 메시지 표출까지 전 과정이 PC 연결 없이 무선으로 매끄럽게 동작하였으며, 스마트폰 웹 리모컨을 통한 실시간 공정 모드 전환도 정상 확인되었다."
        ]
    },
    {
        "date": "2025-11-20",
        "toc": "ESP32-S3 듀얼 USB-C 보드 스캐너 펌웨어 핀맵 이식 및 3D STEP 수납 치수 검증",
        "content": [
            "더 넉넉한 메모리와 듀얼 USB-C 포트를 갖춘 차세대 ESP32-S3-WROOM-1 개발보드(qr_scanner_module_esp32s3)로 무선 스캐너 펌웨어를 이식하고 컴파일·구동 테스트를 진행하였다.",
            "핸드헬드 하우징 설계의 기준 치수를 확보하기 위해 ESP32-S3 보드의 정밀 3D CAD 모델(STEP/FCStd)을 불러와 기판 전장·폭·핀헤더 높이 및 USB-C 커넥터 돌출량을 계측하였다.",
            "구형 ESP32(WROOM-32)와 달라진 GPIO 매트릭스에 맞춰 I2C(OLED) 및 HardwareSerial(GM77) 핀 번호를 재할당하였다."
        ],
        "images": [
            ("3D modeling/zsp32-s3-wroom-1-devkit-1.snapshot.9/ESP32-S3-WROOM-1_view1.png", "스캐너 하우징 내부 수납 공간 설계에 활용된 ESP32-S3 듀얼 USB-C 개발보드 3D CAD 모델")
        ],
        "result": [
            "이식 초기에는 기존 보드의 암묵적 기본 I2C 핀(21/22번) 설정이 그대로 남아 SSD1306 화면이 켜지지 않았으나, Wire.begin(SDA, SCL)과 UART 핀을 명시 지정하여 OLED 표출과 GM77 스캔이 모두 정상 작동하였다.",
            "3D 모델 실측 결과 ESP32-S3 보드의 세로 전장이 길어 소형 그립 수납 시 여유 공차 확보가 중요함을 확인하고 외함 내부 캐비티 설계 치수에 반영하였다."
        ]
    },
    {
        "date": "2025-11-26",
        "toc": "핸드헬드 스캐너 1차 3파트 하우징(v06) 및 콜드체인 통풍 센서팟(v07) 3D 기구 설계",
        "content": [
            "외부에 노출된 스캐너 회로와 수송용 센서 보드를 보호하기 위해 OpenSCAD 파라메트릭 모델링으로 1차 핸드헬드 스캐너 외함(v06)과 독립형 콜드체인 센서팟 외함(v07) 2종을 연속 설계하였다.",
            "스캐너 하우징(v06)은 상부 광학 헤드 바디, 하부 원통형 핸들, 상단 덮개(Lid)의 3파트 분할 구조로 설계하고 전방 GM77 스캔 창과 후방 전원 인입 홀을 관통 가공하였다.",
            "콜드체인 센서팟(v07)은 사각 라운드 인클로저 측면에 다중 루버 통풍 슬릿(Ventilation Slits)을 내고 내부 보드 지지 스탠드오프를 배치하여 단면 절개 뷰로 부품 장착 높이를 점검하였다."
        ],
        "images": [
            ("3D_Printer_Housing/v06_Housing_And_Stand/06_exploded_view.png", "바디·핸들·상부 커버 3파트로 설계된 v06 스캐너 분해도"),
            ("3D_Printer_Housing/v07_Coldchain_Sensor_Pod/07_cross_section_view.png", "측면 통풍 슬릿이 적용된 v07 콜드체인 센서팟 단면도")
        ],
        "result": [
            "v06 스캐너는 바디와 원통 핸들을 별도 파트로 맞대어 끼우는 목(Neck) 부위에 굽힘 하중이 집중되는 약점이 파악되어 일체형 그립 구조로의 개선 필요성을 도출하였다.",
            "v07 센서팟은 완전 밀폐 시 ESP32 Wi-Fi 발열로 내부 온도가 +1.5°C가량 높게 찍히던 자기발열 문제를 측면 다중 통풍 슬릿 개방과 보드 이격 배치로 완화할 수 있음을 단면 검증으로 확인하였다."
        ]
    },
    {
        "date": "2025-12-04",
        "toc": "인체공학 핑거 그루브 권총형 그립(v08) 및 좌·우 반할 스냅핏 스캐너 하우징(v09) 재설계",
        "content": [
            "v06의 미끄러운 원통 핸들과 목 결합부 약점을 해소하기 위해 3단 손가락 홈(Finger Groove)을 가진 일체형 권총 그립 하우징(v08)으로 외형을 전면 리모델링하였다.",
            "이어서 상·하 분할 구조에서 깊고 좁은 핸들 내부에 생기는 3D 프린터 서포트를 제거하기 어렵던 문제를 해결하고자, 중심축(XZ 평면) 기준 좌·우 대칭 조개껍질(Clamshell) 반할 스냅핏 구조(v09)로 분할 방식을 전환하였다.",
            "별도 금속 볼트 없이 양쪽 쉘을 맞물려 닫는 캔틸레버 스냅핏 후크의 암 길이와 뿌리 보강 챔퍼를 v09 v2까지 개선하여 분해 조립도를 렌더링하였다."
        ],
        "images": [
            ("3D_Printer_Housing/v08_QR_Scanner_Housing/08_exploded_view.png", "핑거 그루브 일체형 권총 그립을 적용한 v08 하우징"),
            ("3D_Printer_Housing/v09_QR_Scanner_Housing_Snapfit/09_exploded_view_v2.png", "좌·우 Clamshell 반할 및 보강 스냅핏이 적용된 v09 v2")
        ],
        "result": [
            "v08 초기 불리언 연산에서 핑거 그루브 차집합 구체가 내벽까지 파고들던 외벽 천공 버그를 외부 쉘 선행 합집합 후 내부 코어 일괄 차집합 순서로 교정하여 완벽한 곡면 그립을 얻었다.",
            "또한 v09 좌·우 반할 구조 도입으로 반할 평면을 프린터 베드에 눕혀 출력할 수 있게 되어 내부 서포트 제거 난이도가 획기적으로 낮아졌고, 연장형 스냅 후크(v2)로 적층 결 박리 파손도 방지하였다."
        ]
    },
    {
        "date": "2025-12-09",
        "toc": "Wi-Fi 단절 대비 ESP32 내장 플래시 LittleFS 파일시스템 마운트 및 로컬 로깅·복원 검증",
        "content": [
            "수송 차량이 고속도로 음영 지역을 지나거나 공유기 연결이 일시 끊겼을 때 계측 패킷이 증발하지 않도록, ESP32 내장 SPI 플래시 파티션에 LittleFS 파일시스템을 마운트하여 로컬 블랙박스 큐를 구축하는 실험을 수행하였다.",
            "최초 업로드 보드에서 파티션 미포맷 에러가 나더라도 자동으로 초기화하도록 LittleFS.begin(true) 옵션을 적용하고, 전체 파일을 다시 쓰는 부담이 없는 줄 단위 JSON Lines(/offline_log.jsonl, FILE_APPEND) 기록 함수를 작성하였다.",
            "의도적으로 Wi-Fi AP 전원을 끈 상태에서 연속 3개 패킷이 플래시에 누적 기록되는지 확인한 뒤, 보드 전원을 완전히 껐다 켜는(Power-Cycle) 재부팅 시험을 거쳐 Wi-Fi 재연결 시 저장 패킷이 브로커로 일괄 재전송되고 파일이 정리되는지 시리얼 모니터로 검증하였다."
        ],
        "images": [
            ("scratch/notebook_captures/cap25_littlefs_exec.png", "ESP32 LittleFS 마운트·JSONL 저장 펌웨어 코드 및 전원 재부팅 후 무손실 복원 시리얼 실행 로그")
        ],
        "result": [
            "시리얼 실행 로그에서 총 1,441,792 Byte 플래시 파티션이 정상 마운트되었고, Wi-Fi 타임아웃 즉시 오프라인 큐 모드로 전환되어 온습도·충격 JSON 패킷 3건(361 Byte)이 /offline_log.jsonl에 순차 기록되었다.",
            "전원 차단 후 재부팅 뒤에도 플래시 내 361 Byte 레코드가 손실 없이 그대로 보존되어 있었으며, 공유기 재접속 직후 3건 전량 MQTT 재발행 및 LittleFS.remove() 초기화를 깔끔하게 마쳤다."
        ]
    },
    {
        "date": "2025-12-15",
        "toc": "내부 모듈 크래들 격벽 스캐너 하우징(v10) 및 상부 OLED 매립형 베젤(v11) 연속 설계",
        "content": [
            "반복 스캔 작업과 충격에도 내부 전자 부품이 흔들리지 않도록 GM77 광학 챔버 격벽, ESP32 기판 슬롯, 물리 트리거 스위치 가이드를 내벽에 일체 성형한 산업용 하우징(v10)을 설계하고 편측 +0.3mm 조립 공차를 반영하였다.",
            "연이어 후상단 0.96인치 SSD1306 OLED 디스플레이가 2.5mm 외벽 두께 안쪽에 깊숙이 묻혀 비스듬한 각도에서 첫 줄 공정 코드(A10~A15)가 가려지던 문제를 해결하기 위해 매립형(Flush-Mount) 베젤 하우징(v11)을 설계하였다.",
            "액정 활성 영역을 외표면 쪽으로 1.4mm 전진 안착시키는 단차 포켓과 외곽 45° 경사 챔퍼 베젤, 상단 4핀 납땜부 간섭 도피 홈(Relief Cutout)을 적용하여 단면도 및 조립 뷰로 검증하였다."
        ],
        "images": [
            ("3D_Printer_Housing/v10_QR_Scanner_Housing_Industrial/10_cross_section_view.png", "모듈별 고정 크래들과 +0.3mm 공차가 반영된 v10 단면도"),
            ("3D_Printer_Housing/v11_QR_Scanner_Housing_Flush_OLED/11_assembly_view.png", "상부 SSD1306 OLED 45° 매립형 챔퍼 베젤을 적용한 v11 조립도")
        ],
        "result": [
            "v10 단면 검증을 통해 글루건 등 임시 고정재 없이도 성형 크래들과 암수 단차(Step Lip) 테두리만으로 전 부품이 유격 없이 정위치에 구속됨을 확인하였다.",
            "v11 매립형 챔퍼 베젤 적용 결과 작업자가 스캐너를 자연스럽게 쥔 시야각(±60°) 전 범위에서 OLED 네 모서리 픽셀 가림 없이 모든 상태 텍스트를 선명하게 판독할 수 있게 되었다."
        ]
    },
    {
        "date": "2025-12-22",
        "toc": "4점 정렬 보스 및 분해 슬롯을 갖춘 무나사 스캐너 하우징(v12) 완성 및 연말 모듈 통합 점검",
        "content": [
            "펌웨어 디버깅과 배터리 교체를 위해 하우징을 반복 개폐할 때 테두리가 손상되지 않도록 4개소 원추형 리드인 정렬 보스, 분산형 저변형 스냅 랫치, 그립 바닥면 분해용 프라이 슬롯(Pry Slot)을 결합한 무나사 하우징(v12)을 설계하였다.",
            "분해 뷰(12_exploded_view)와 중앙 단면 뷰(12_cross_section_view)를 동시에 생성하여 좌·우 비틀림 구속 상태와 내부 부품 간섭 부재 여부를 최종 확인하였다.",
            "아울러 연말 마무리에 맞춰 산지·APC QR 생성기(1_PC_QR_Generators), 임베디드 펌웨어(2_ESP32_Firmware), 소비자 대시보드(3_Consumer_Dashboard), 관제 대시보드(4_APC_Coldchain_Dashboard) 4대 실행 계층의 경로와 AWS RDS 연동을 종합 점검하였다."
        ],
        "images": [
            ("3D_Printer_Housing/v12_QR_Scanner_Housing_Screwless/12_exploded_view.png", "4점 원추형 정렬 보스와 무나사 랫치가 적용된 v12 분해도"),
            ("3D_Printer_Housing/v12_QR_Scanner_Housing_Screwless/12_cross_section_view.png", "하단 분해 슬롯 및 내부 안착 간섭 0건을 확인한 v12 단면도")
        ],
        "result": [
            "금속 볼트·너트 없이 3D 프린터 출력물 자체 탄성 랫치와 4점 정렬 핀만으로 뒤틀림 없는 견고한 결합과 손상 없는 반복 분해 구조를 완성하였다.",
            "산지 QR 발행부터 APC 공정 스캔, AWS RDS 적재, 실시간 지도·소비자 대시보드 표출까지 2025년 구축 전 파이프라인이 상호 오류 없이 일관되게 작동함을 최종 확인하였다."
        ]
    },
]
