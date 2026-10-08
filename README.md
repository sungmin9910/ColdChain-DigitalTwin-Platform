# ❄️ ColdChain-DigitalTwin-Platform

> **수확 후 농산물의 신선도 보장을 위한 양방향 디지털 트윈 기반 실시간 유통 관제 및 신뢰성 검증(블록체인) 플랫폼**

---

## 📌 프로젝트 개요 (Overview)
본 플랫폼은 산지유통센터(APC)에서 출고된 신선 농산물이 최종 소비자에게 도달하기까지의 전 과정(Cold-Chain)을 **실시간 IoT 센서 데이터 수집, 다이나믹 QR 코드, 디지털 트윈 가시화, 블록체인 원장 기록**을 통해 모니터링하고 가치를 보장하는 통합 유통 추적 솔루션입니다.

* **연구 분야**: 생산정보 연계 농산물 수확 후 품질 표준화 및 양방향 디지털 트윈 관제
* **핵심 타겟**: APC 관리자(차량 노선 우회, 실시간 저장고 온도 조절) & 소비자(유통 이력, 신선 품질 신뢰성 조회)

---

## 🏗️ 시스템 아키텍처 (System Architecture)

```mermaid
flowchart TD
    subgraph Hardware_Layer [1. IoT 하드웨어 센서 노드]
        ESP32[ESP32 QR 스캐너/센서 노드] -->|WiFi/MQTT| CloudDB[(AWS Cloud MySQL)]
        Sensors[MPU6050 가속도 / GY-25 자이로 / 온습도 센서] -->|실시간 데이터 수집| ESP32
    end

    subgraph Core_Engine [2. 데이터 수집 및 가공 엔진]
        CloudDB -->|유통 이력 추출| QR_Gen[다이나믹 QR 생성 및 등급 매핑]
        CloudDB -->|실시간 스트리밍| Dashboards
        QR_Gen -->|품질 검증 데이터| BC[블록체인 원장 기록 시뮬레이터]
    end

    subgraph Application_Layer [3. 통합 대시보드 & 관제]
        Dashboards[Streamlit Dual-Dashboard System]
        Dashboards -->|관제용| APC[APC 콜드체인 통합 관제 대시보드]
        Dashboards -->|소비자용| Consumer[소비자 신뢰도 이력 조회 대시보드]
    end
```

---

## 🌟 핵심 기능 (Key Features)

1. **양방향 디지털 트윈 관제**: 운송 차량 내부의 온습도, 실시간 GPS 및 3축 가속도/자이로 센서를 매핑하여 차량 충격에 의한 농산물 손상량을 실시간 예측 및 최적화 노선 우회 제안.
2. **다이나믹 QR 코드 & 데이터 매핑**: 유통 구간별 상태 변화 정보를 동적으로 QR에 주입하고, 누락되거나 소실된 QR 배송 이력을 데이터베이스로부터 고화질 품질 등급(특/상/보통) 및 브랜드 로고와 함께 복구하는 자동화 파이프라인 탑재.
3. **블록체인 기반 이력 신뢰성 검증**: 데이터 위변조 방지를 위해 수집된 운송 및 품질 정보를 블록체인 트랜잭션 형태로 로컬 원장(`blockchain_ledger.json`)에 기록 및 동기화.
4. **듀얼 관제 시스템**: Streamlit 프레임워크를 기반으로 APC 물류 마스터용 화면과, 일반 소비자가 스마트폰 QR 스캔을 통해 "몇 시간 전 어디서 출고되어 어떤 온도 관리를 받았는지"를 즉시 조회하는 소비자 화면의 분리 구현.

---

## 📂 디렉터리 구성 (Directory Structure)

본 프로젝트는 프로토타입 연구 개발 단계부터 최종 실험실(PoC) 완성 단계까지의 전체 여정을 담고 있습니다.

### 🏆 1. [Final_Experiment/](./Final_Experiment/) (최종 완성 PoC)
실험실 단계에서 최종 검증을 마친 안정 버전의 시스템입니다.
* `1_PC_QR_Generators/`: 브랜드 로고 및 품질 등급 연계 다이나믹 QR 자동 생성 엔진.
* `2_ESP32_Firmware/`: OLED가 없는 경량 하드웨어용 Multi-WiFi 및 보안 Secrets 헤더 포함 스캔/송신 펌웨어.
* `3_Consumer_Dashboard/`: 소비자가 한눈에 KST 기준 정확한 운송 경과 시간과 품질 등급을 확인하는 대시보드.
* `4_APC_Coldchain_Dashboard/`: PC 관제용 대시보드(`Step4_Run_Coldchain_v2.py`) 및 젯슨 소형 디스플레이 전용 2분할 HUD(`Step4_Jetson_SplitHUD.py`).
* `QR_Recovery_Script.py`: 데이터베이스 정밀 쿼리를 통한 QR 코드 일괄 자동 복구 유틸리티.

### 📜 2. [scripts/](./scripts/) (젯슨 자동 실행 및 런처 스크립트)
* `install_jetson_autostart.sh`: 젯슨 바탕화면 바로가기 아이콘 생성 + 부팅 시 자동 실행(Autostart) 통합 인스톨러.
* `run_jetson_hud.sh`: Streamlit 백그라운드 기동 및 Epiphany 브라우저 자동 오픈 런처.
* `stop_jetson_hud.sh`: 대시보드 및 브라우저 안전 종료 스크립트.
* `uninstall_jetson_autostart.sh`: 자동 실행 및 바탕화면 아이콘 삭제/해제 스크립트.

### 🧪 3. [Hardware_Prototypes/](./Hardware_Prototypes/) (센서/레거시 샌드박스)
* `coldchain_module`: 온습도/충격 감지 기본 ESP32 모듈 기초 설계 소스.
* `coldchain_module_gy25` / `gy521`: GY-25 자이로 및 MPU6050 센서 연동 캘리브레이션 테스트 샌드박스.
* `qr_scanner_module`: 아두이노 기반 바코드/QR 스캐너 트리거 및 수집 모듈.
* `code26/`: 초기 학습 및 실험 코딩 소스.

### 📄 4. [KSHS/](./KSHS/) (학술 발표 및 학회 성과 아카이브)
* 본 기술 플랫폼의 독창성과 학술적 기여를 인정받은 **한국원예학회(KSHS)** 제출 최종 초록, 포스터(PDF/HTML), 그리고 슬라이드 PPTX 파일이 들어있습니다.

### 📚 5. [docs/](./docs/) (기술 가이드 및 연구 로드맵)
* `04_ColdChain_FDT_Process.md`: 전체 농가-APC-소비자 FDT 유통 프로세스 규격서.
* `05_Scanner_Comparison.md`: ESP32 자작 스캐너 vs Jetson+MQ160W 비교 분석서.
* **`06_Master_Thesis_Research_Roadmap.md`**: **석사 학위 논문 본심사 및 SCIE 저널 게재를 위한 연구 고도화 처방전 로드맵**.
* `07_CarrierBoard_Assembly_and_Diagnostic_Log.md`: CarrierBoard 조립 및 하드웨어 진단 가이드.
* `08_Vehicle_Experiment_Handover_Guide.md`: 차량 주행 실험 인계 가이드 & 텔레메트리 파이프라인 분석.
* **`09_Vehicle_Experiment_Data_Recovery_and_Dashboard_Optimization.md`**: **실제 차량 주행(전주-대전 174km) 데이터 복구 및 과일 충격량(G-Force) 중심 관제 대시보드 고도화 보고서**.
* **`10_CarrierBoard_Power_Battery_Assembly_and_Telemetry_Guide.md`**: **CarrierBoard 전원 시스템, 배터리 결선, 멀티미터 진단 및 대시보드 텔레메트리 연동 가이드**.
* **`11_Jetson_Field_Monitoring_Setup_and_SupplyChain_Protocol.md`**: **젯슨 나노 현장 관제 키오스크 설정 및 콜드체인 실증 프로토콜 (A00~A15 연동)**.
* **`12_AWS_Cloud_RDS_Cost_and_Resource_Management_Guide.md`**: **AWS RDS 인프라 비용 분석, 잔여 크레딧($70), 스케줄 관리 및 예산 알림 가이드**.
* **`13_Jetson_SplitHUD_and_Autostart_Operation_Guide.md`**: **젯슨 전용 2분할 스플릿 HUD(세션 선택기 + 상시 실시간 모니터링) 및 부팅 자동 실행 가이드**.
* **`14_CarrierBoard_Assembly_Sensor_Pinout_and_Battery_Diagnostic_Guide.md`**: **CarrierBoard 하드웨어 조립, 전 센서 핀맵 매핑, 배터리 결선 및 TP4057 충전 진단 가이드**.

---

## 🛠️ 시작 가이드 (Quick Start)

### 1. 환경 설정 (Dependencies)
Python 3.10+ 환경에서 다음 명령어를 실행하여 필수 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

### 2. 젯슨 차량용 스플릿 HUD 실행 및 자동 시작 등록
```bash
# 통합 인스톨러 실행 (바탕화면 아이콘 + 부팅 자동 실행 등록 + 즉시 실행)
bash scripts/install_jetson_autostart.sh
```

### 3. PC 관제용 풀스크린 대시보드 구동
```bash
streamlit run Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py
```

### 4. 소비자 대시보드 구동
```bash
cd Final_Experiment/3_Consumer_Dashboard
streamlit run Step5_Run_Dashboard.py
```

### 5. QR 복구 스크립트 실행
```bash
cd Final_Experiment
python QR_Recovery_Script.py
```

---

## 👨‍🔬 담당 연구 및 연락처
* **한성민 ( 전북대학교 농업기계공학과 / 석사과정 )**
* **Agricultural Sensor and Robotics Lab** 학부연구생 3년 & 석사 1년차
* 📧 **Contact**: `yuyu6243@gmail.com`

