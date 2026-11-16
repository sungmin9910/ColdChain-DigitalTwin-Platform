# ColdChain DigitalTwin 4-in-1 통합 웹 포털 (FastAPI + WebSocket)

기존 **Streamlit 대시보드(`Step4`, `Step5`) 및 Tkinter QR 생성기(`Step1`, `Step3`)를 100% 그대로 유지**하면서, 언제든 병행 실행하거나 향후 메인 시스템으로 즉시 전환할 수 있도록 구축한 **옵션 1 (FastAPI + 모던 웹 + WebSocket)** 통합 포털입니다.

---

## 1. 핵심 특징

1. **4대 화면 1개 사이트 통합 + 권한별 탭 분리 (RBAC)**
   - **비로그인 기본 화면**: `🔍 1. 소비자 안심 조회` 탭만 공개 (QR 스캔 시 로그인 없이 즉시 이력·경로 확인)
   - **상단 PIN 입력 시 권한별 탭 잠금 해제**:
     - `0000` (**통합 관리자**): 4개 탭 전체(`소비자` + `농가 QR` + `APC 선별 QR` + `실시간 차량 관제`) 활성화
     - `1111` (**농가 담당자**): `🌾 2. 농가 수확·QR 생성 (A00)` 탭 활성화
     - `2222` (**APC 작업자**): `🏭 3. APC 선별·등급 QR 생성 (A12)` 탭 활성화
     - `3333` (**콜드체인 관제사**): `🛰️ 4. 실시간 차량 관제 대시보드` 탭 활성화
2. **현재 Streamlit 메인 유지 & 차기 FastAPI 메인 전환 1클릭 스위치**
   - 동일한 AWS RDS MySQL(`15.165.68.30`, `lab225`)과 HiveMQ 브로커(`broker.hivemq.com`)를 공유하므로 **기존 Streamlit과 동시에 켜두어도 100% 호환**됩니다.
   - 농가 QR(`탭 2`) 및 APC 선별 QR(`탭 3`) 생성 화면 우측 상단에서 **QR 연결 대상 주소**를 선택할 수 있습니다:
     - `✅ [현재 메인] 기존 Streamlit 소비자 대시보드` (기본값 — 지금 당장 실험할 때 기존 시스템과 완벽 호환)
     - `🚀 [차기 메인 전환용] 현재 FastAPI 통합 포털` (나중에 FastAPI를 메인으로 바꿀 때 선택)

---

## 2. 24/7 클라우드 상시 접속 및 로컬 실행 방법

### 2.1 [상시 가동 중] AWS EC2 24/7 통합 포털 접속 주소
* **통합 포털 메인 URL (PC·스마트폰 LTE/5G 어디서나 접속)**: `http://54.180.112.191:8080`
* **소비자 이력 바로 조회 예시**: `http://54.180.112.191:8080/?FmID=85`
* **운영 인프라**: AWS EC2 (`i-05441dd44b416ddd5`, `ap-northeast-2`) 내 `coldchain-portal.service` (`systemd` 상시 데몬, 기존 `coldchain-daemon.service`와 병렬 가동)

### 2.2 로컬 PC 개발/테스트 실행
1. [run_portal.bat](file:///c:/Users/korea/Desktop/1hsm/hanhanhan/ColdChain-DigitalTwin-Platform/Final_Experiment/5_Unified_FastAPI_Portal/run_portal.bat) 파일을 더블클릭하거나 터미널에서 아래 명령어를 실행합니다:
   ```powershell
   cd Final_Experiment/5_Unified_FastAPI_Portal
   python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
   ```
2. 웹브라우저에서 **`http://localhost:8080`** (또는 특정 농가 바로 조회 시 `http://localhost:8080/?FmID=85`)으로 접속합니다.

---

## 3. 향후 모든 QR 코드의 기본 연결 주소를 FastAPI 포털로 전환하는 방법

1. **AWS EC2 서버 상시 실행 완료**:
   - `setup_ec2_portal.sh`를 통해 `coldchain-portal.service`가 `http://54.180.112.191:8080`에서 24/7 상시 가동 중입니다.
2. **QR 타겟 모드 전환**:
   - 웹 화면의 농가/APC 탭에서 **`🚀 [차기 메인 전환용] 현재 FastAPI 통합 포털`**을 선택하거나, `app.py`의 `STREAMLIT_CONSUMER_URL` 값을 `http://54.180.112.191:8080`으로 변경하면 모든 신규 생성 QR 코드가 이 통합 포털로 직접 연결됩니다.
