# 22. 콜드체인 디지털 트윈 플랫폼 HW·SW 세부 계층 아키텍처 명세서

**문서 번호**: CC-DOC-2026-22  
**작성 일자**: 2026-11-13  
**작성자**: 콜드체인 디지털 트윈 연구팀 (한성민)  
**적용 대상**: ColdChain-DigitalTwin-Platform 전 계층 (IoT 센서노드, 스마트 스캐너, 클라우드 백엔드, 관제·소비자 대시보드)

---

## 1. 개요 (Overview)

본 문서는 산지유통센터(APC) 기반 신선 농산물(사과, 배 등) 콜드체인 디지털 트윈 플랫폼의 **물리적 하드웨어(HW)**와 **논리적 소프트웨어(SW)** 구성을 모듈, 부품, 통신 인터페이스 및 소스코드 단위로 세밀하게 분해·정의한 기준 아키텍처 명세서입니다.

---

## 2. 하드웨어 (HW) 세부 계층 구성

실증 플랫폼의 하드웨어는 역할에 따라 **① 차량/상자 탑재형 디지털 트윈 센서 노드**, **② 작업자용 핸드헬드 스마트 QR 스캐너**, **③ 현장 관제 키오스크 및 네트워크/클라우드 물리 인프라**의 3대 축으로 구성됩니다.

### 2.1 차량/상자 탑재형 디지털 트윈 센서 노드 (1~4호차 Fleet)
과일 상자 내부 또는 수송 탑차에 적재되어 이동 경로와 물리적 충격, 미기상 환경을 실시간 계측하는 핵심 엣지 디바이스입니다.

* **자체 설계 전용 인터페이스 PCB**:
  * **모델명**: `CarrierBoard Beetle ESP32-C6 EdgeUSB` (50.0 × 50.0 mm, 2층 FR-4, 두께 1.6 mm)
  * **구조적 특징**: SMD 직접 납땜 대신 2.54 mm 암형 핀헤더 소켓 원터치 체결 방식을 채택하여 센서 모듈 교체성 확보, 모서리 4개소 M3 고정홀(43 × 43 mm 피치, GND 접지 패드 연동) 설계
  * **참조**: [3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50/README.md](../3D%20modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50/README.md), [14_CarrierBoard_Assembly_Sensor_Pinout_and_Battery_Diagnostic_Guide.md](./14_CarrierBoard_Assembly_Sensor_Pinout_and_Battery_Diagnostic_Guide.md)
* **메인 MCU 및 독립 전원 계통**:
  * **MCU**: `DFRobot Beetle ESP32-C6 Mini` (`DFR1117`, RISC-V 단일코어 `ESP32-C6FH4`, 4MB 내장 Flash, Wi-Fi 6 지원) — 총 4대 구축 (`carrier-c6-01` ~ `carrier-c6-04`)
  * **충전·전원 제어**: 온보드 `TP4057` 리튬이온 충전 IC (500 mA 정전류 충전, Green LED 상태 표시) + SMD 슬라이드 스위치(`SW1`) + 2핀 탈부착 피그테일 커넥터
  * **배터리**: `JRF PL105568` 대용량 리튬폴리머 파우치 셀 (3.7V, **5,000 mAh** / 초기 프로토타입 18650 2,200 mAh 검증 완료, 연속 약 50~55시간 가동)
  * **참조**: [10_CarrierBoard_Power_Battery_Assembly_and_Telemetry_Guide.md](./10_CarrierBoard_Power_Battery_Assembly_and_Telemetry_Guide.md), [18_MultiCarrier_Board_Deployment_and_Fleet_Registration_Report.md](./18_MultiCarrier_Board_Deployment_and_Fleet_Registration_Report.md)
* **탑재 계측 센서 모듈 (4종)**:
  * **온습도 센서 (`Adafruit SHT45`)**: I2C (`0x44`, GPIO 19 SDA / GPIO 20 SCL 공용 버스), Bottom면 장착
  * **6축 관성·충격 센서 (`GY-521 / MPU6050`)**: I2C (`0x68`, 3축 가속도 + 3축 자이로스코프, 과실 충격 G-Force 계측), Bottom면 장착 *(초기 프로토타입 단계에서 `GY-25` 등 비교 검증)*
  * **조도 센서 (`BH1750 / GY-302`)**: I2C (`0x23`, 상자 개폐 및 탑차 도어 개방 광량 감지), Top면 장착
  * **위성 항법 모듈 (`ATGM336H Mini`)**: UART (`9600 bps`, GPIO 16 RX / GPIO 17 TX), 외장 세라믹 패치 안테나(20 × 5 × 7 mm) 체결, Bottom면 장착
* **3D 프린팅 사과 모형 외함 (`Apple Sensor Pod v22`)**:
  * **출력 사양**: 직경 100 mm 구형 사과 형상, 신도리코 `3DWOX 2X` PLA 무서포트 단일 노즐 출력 최적화
  * **기구 설계**: Ø6 × 3 mm 네오디뮴 자석 8개 스틸-다웰(Steel-Dowel) 전단 잠금 결합, 1.5 cm 센서 간섭 회피 단차형 M3 보강 기둥, 내벽 일체형 GPS 세라믹 안테나 포켓, 후면 `BH1750` 경사형 채광창 및 평탄형 벨크로 배터리 베이 적용
  * **참조**: [3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/22_apple_sensor_pod.scad](../3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/22_apple_sensor_pod.scad), [17_Apple_Sensor_Pod_v22_Magnetic_and_GPS_Holder_Report.md](./17_Apple_Sensor_Pod_v22_Magnetic_and_GPS_Holder_Report.md)

---

### 2.2 작업자용 핸드헬드 스마트 QR 스캐너
산지유통센터(APC) 입고(`A10`)부터 최종 출하(`A15`)까지 과일 상자의 공정별 체크포인트를 기록하는 휴대용 단말입니다.

* **자체 제작 임베디드 스마트 스캐너 (`v17` 피스톨 그립형)**:
  * **제어 MCU**: `ESP32` 개발보드 (`ESP32-D0WD-V3`, 28.2 × 54.4 mm)
  * **광학 리더 엔진**: `GM77` 1D/2D 바코드·QR 리더 모듈 — UART2 연동 (GPIO 32 RX / GPIO 33 TX)
  * **상태 디스플레이**: `SSD1306` 0.96인치 단색 OLED (128 × 64 픽셀) — I2C 연동 (GPIO 21 SDA / GPIO 22 SCL, 작업자 시선 맞춤 55° 후방 경사 배치)
  * **조작 및 전원부**: 검지 트리거 택트 스위치(GPIO 25) + 온보드 BOOT 버튼(GPIO 0), `18650` 리튬이온 셀 + `TP4056` 충전 모듈 + `VLT-VC013` 승압 부스터 + 슬라이드 전원 스위치
  * **참조**: [Final_Experiment/2_ESP32_Firmware/src/main.cpp](../Final_Experiment/2_ESP32_Firmware/src/main.cpp), [3D_Printer_Housing/v17_QR_Scanner_Housing/17_qr_scanner_housing.scad](../3D_Printer_Housing/v17_QR_Scanner_Housing/17_qr_scanner_housing.scad), [15_ColdChain_Lifecycle_Physical_Scanner_Recovery_and_AutoRecognition_Report.md](./15_ColdChain_Lifecycle_Physical_Scanner_Recovery_and_AutoRecognition_Report.md)
* **비교 검증용 상용 무선 스캐너**:
  * `MQ160W` 2.4GHz 산업용 무선 핸드헬드 스캐너 + USB 무선 수신 동글 (Jetson Nano / PC 연결 운용)
  * **참조**: [05_Scanner_Comparison.md](./05_Scanner_Comparison.md)

---

### 2.3 현장/차량 관제 키오스크 & 네트워크·클라우드 물리 인프라
* **현장/차량용 키오스크 단말**: `NVIDIA Jetson Nano / Orin Nano` + 7~10인치 소형 HDMI 터치/외장 모니터
* **이동형 게이트웨이**: 운송 차량 내 스마트폰 2.4GHz Wi-Fi 모바일 핫스팟 (`hani`, `smroom`, `225`)
* **클라우드 서버 인프라 (AWS 서울 리전 `ap-northeast-2`)**:
  * 수집 데몬 서버: `Amazon EC2 t3.micro` (Ubuntu 24.04 LTS)
  * 관리형 데이터베이스: `Amazon RDS for MySQL 8.4.8` (`db.t3.micro`, 20 GiB SSD)
  * **참조**: [11_Jetson_Field_Monitoring_Setup_and_SupplyChain_Protocol.md](./11_Jetson_Field_Monitoring_Setup_and_SupplyChain_Protocol.md), [12_AWS_Cloud_RDS_Cost_and_Resource_Management_Guide.md](./12_AWS_Cloud_RDS_Cost_and_Resource_Management_Guide.md), [21_Cloud_Backend_Daemon_Deployment_and_Automated_Pipeline_Report.md](./21_Cloud_Backend_Daemon_Deployment_and_Automated_Pipeline_Report.md)

---

## 3. 소프트웨어 (SW) 세부 계층 구성

소프트웨어는 데이터 수집부터 최종 가시화까지 **① 임베디드 펌웨어**, **② 클라우드 백엔드/DB 파이프라인**, **③ 다이나믹 QR·선별·블록체인 유틸리티**, **④ 디지털 트윈 웹 관제 및 소비자 대시보드**의 4계층으로 구분됩니다.

### 3.1 임베디드 펌웨어 계층 (C++ / PlatformIO & Arduino)
| 모듈 구분 | 핵심 알고리즘 및 구현 기능 | 주요 라이브러리 | 대상 소스코드 |
| :--- | :--- | :--- | :--- |
| **CarrierBoard 센서노드 펌웨어** | • **고속 진동/충격 샘플링**: 20 ms(`50 Hz`) 주기로 MPU6050 폴링, `1.8G` 이상 피크 감지 시 즉시 경보 발행(3초 디바운스)<br>• **정기 텔레메트리 송출**: 5초 주기 JSON 패킷 구성 및 MQTT 발행, 주행 자동 감지(`Smart Trip Latch`) 및 터널 구간 직전 좌표 유지<br>• **무손실 블랙박스 (`LittleFS`)**: 마스터 순환 링버퍼(512KB × 2 = 1MB) 상시 기록 및 통신 단절 시 오프라인 버퍼(1.5MB, 약 8시간) 적재 후 재연결 시 안전 이어보내기(`Safe Resume Flush`)<br>• **Wi-Fi 자가복구 & GPS 시각 동기화**: 오프라인 시 위성 UTC 시각 기반 KST 자동 동기화, 핫스팟 단절 시 RF 모뎀 소프트웨어 Power-Cycle 재연결 | `Adafruit_MPU6050`, `SHTSensor`, `BH1750`, `TinyGPSPlus`, `PubSubClient`, `ArduinoJson`, `LittleFS`, `WiFiMulti` | [carrier_board_mqtt.cpp](../Hardware_Prototypes/code26/test/src/carrier_board_mqtt.cpp), [platformio.ini](../Hardware_Prototypes/code26/test/platformio.ini) |
| **스마트 QR 스캐너 펌웨어** | • **지능형 자동 단계 인식 (`AUTO Mode`)**: 스캔된 URL에서 `FmID` 추출 후 RDS `lab225.qr` 테이블의 직전 `Lo` 상태를 조회해 `A00 → A10(입고) → A11(세척) → A12(선별) → A13(포장) → A14(저장) → A15(출하)` 다음 단계로 자동 전이 및 SQL `INSERT`<br>• **실시간 환경·위치 결합**: 스캔 시점 `sensor_data` 최신 위경도 및 온습도를 서브쿼리로 병합 저장<br>• **Latency 프로파일러 & 웹 리모컨**: 디코딩 및 DB 왕복 처리 시간(평균 1.8~2.3초) OLED 실시간 표출 및 포트 80 내장 웹서버 지원 | `MySQL_Generic`, `Adafruit_SSD1306`, `Adafruit_GFX`, `WebServer`, `WiFiMulti` | [main.cpp](../Final_Experiment/2_ESP32_Firmware/src/main.cpp) |

---

### 3.2 클라우드 백엔드 & 무인 데이터 파이프라인 계층
* **MQTT 브로커 라우팅**: `broker.hivemq.com:1883`을 통해 1~4호차 개별 토픽(`coldchain/truck01~04/sensor`) 분리 중계
* **24/7 상시 수신 데몬 (`cloud_backend/`)**:
  * `mqtt_to_mysql_daemon.py`가 EC2 내 `systemd`(`coldchain-daemon.service`) 백그라운드 데몬으로 상시 동작하며 PC 가동 여부와 무관하게 4개 차량 토픽을 동시 수신
  * `VehicleSessionTracker` 클래스가 주행 개시(속도 > 2.0 km/h 또는 GPS Fix) 및 종료(3분 이상 무진동 정차)를 판별해 세션 ID를 자동 분할하고, 비동기 큐 워커로 패킷 유실 없이 RDS에 적재
  * **참조**: [mqtt_to_mysql_daemon.py](../cloud_backend/mqtt_to_mysql_daemon.py), [coldchain-daemon.service](../cloud_backend/coldchain-daemon.service), [setup_ec2.sh](../cloud_backend/setup_ec2.sh)
* **관계형 데이터베이스 스키마 (`AWS RDS MySQL - lab225`)**:
  * `sensor_data`: 차량/단말별 시계열 환경·위치·충격량·세션(`run_id`) 저장 테이블
  * `qr`: 농산물 상자(`FmID`)별 `A00`~`A15` 전 주기 타임스탬프, 산지 정보, 선별 등급(`AGrade`~`CGrade`, `DefectRate`), 스캔 위치·온습도 이력 테이블

---

### 3.3 다이나믹 QR 생성 · 등급 선별 · 블록체인 해시 검증 계층
* **산지 수확 등록 및 최초 QR 생성기 (`A00`)**: `Tkinter` 기반 데스크톱 앱으로 산지 정보·품종·재배방식 입력 시 과일 일러스트 로고가 삽입된 스타일드 QR 코드를 생성하고 RDS 등록 및 `SHA-256` 해시를 원장에 기록 ([Step1_Farm_QR_Creator.py](../Final_Experiment/1_PC_QR_Generators/Step1_Farm_QR_Creator.py))
* **APC 품질 선별 및 다이나믹 QR 갱신기 (`A12`)**: `ttkbootstrap` GUI로 세척 완료(`A11`) 물량의 특/상/보통 및 결점과 수량을 매핑하여 `A12` 레코드와 해시 체인을 갱신 ([Step3_Sorting_QR_Creator.py](../Final_Experiment/1_PC_QR_Generators/Step3_Sorting_QR_Creator.py), [blockchain_ledger.json](../Final_Experiment/blockchain_ledger.json))
* **스캐너 에뮬레이터 및 QR 복구 유틸리티**: USB 스캐너 연동 CLI 스크립트 및 DB 기반 유실 QR 이미지 자동 재발행 도구 ([pc_qr_scanner.py](../Final_Experiment/pc_qr_scanner.py), [QR_Recovery_Script.py](../Final_Experiment/QR_Recovery_Script.py))

---

### 3.4 디지털 트윈 통합 관제 & 소비자 웹 애플리케이션 계층 (Streamlit)
* **APC 마스터 통합 관제 대시보드 (PC 웹)**: 1~4호차 개별 관제, `PyDeck` 기반 실시간 주행 궤적 및 충격 이벤트 지도, `Altair` 이중 Y축(G-Force & 속도 / 온도 & 습도) 시계열 분석, 다중 이상 징후(`≥1.8G` 충격, `≥300 lx` 조도 급변, `≥2.0℃` 온도 급변) 경보 및 전체 CSV 추출 제공 ([Step4_Run_Coldchain_v2.py](../Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py))
* **차량/현장 키오스크 전용 2분할 스플릿 HUD (Jetson용)**: 소형 스크린 무스크롤(No-Scroll) 다크모드 UI, 2-슬롯 FIFO 뷰 전환기, 부팅 시 `Epiphany` 브라우저 자동 실행 셸 스크립트 제공 ([Step4_Jetson_SplitHUD.py](../Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Jetson_SplitHUD.py), [install_jetson_autostart.sh](../scripts/install_jetson_autostart.sh))
* **소비자용 모바일 안심 이력 대시보드**: 스마트폰 QR 스캔 즉시 연결되는 반응형 웹앱으로, 한국어/영어 다국어 전환, 생산자 프로필, 선별 등급, `A00~A15` 단계별 경과 시간 타임라인 및 GPS 유통 경로 지도 제공 ([Step5_Run_Dashboard.py](../Final_Experiment/3_Consumer_Dashboard/Step5_Run_Dashboard.py))

---

## 4. HW ↔ SW 종단간 인터페이스 매트릭스

| 출발 계층 (HW) | 구동 소프트웨어 (SW) | 물리 배선 / 네트워크 프로토콜 | 도착 계층 (SW / 클라우드) |
| :--- | :--- | :--- | :--- |
| **4종 환경·충격 센서** | 센서 수집 루프 (`carrier_board_mqtt.cpp`) | `I2C` (GPIO 19/20) & `UART` (GPIO 16/17) | **Beetle ESP32-C6 MCU** |
| **Beetle ESP32-C6 (1~4호차)** | MQTT 퍼블리셔 & LittleFS 로거 | `2.4GHz Wi-Fi` → `MQTT` (`TCP 1883`, JSON) | **HiveMQ** → **AWS EC2 데몬** → **RDS (`sensor_data`)** |
| **GM77 바코드 모듈 & OLED** | `AUTO` 스캐너 펌웨어 (`main.cpp`) | `UART2` (GPIO 32/33) & `I2C` (GPIO 21/22) | **ESP32 스캐너 MCU** |
| **ESP32 스마트 QR 스캐너** | MySQL Direct 커넥터 | `2.4GHz Wi-Fi` → `MySQL Protocol` (`TCP 3306`) | **AWS RDS (`qr` 테이블)** |
| **PC / Jetson / 소비자 스마트폰** | Streamlit 대시보드 3종 & Tkinter 앱 | `TCP 3306` (`PyMySQL`) & `MQTT 1883` | **관제 모니터 / 키오스크 HUD / 모바일 브라우저** |
