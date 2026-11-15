# 23. 실차 주행 실증 오류 해결(5종), 24/7 클라우드 통합 포털 배포 및 전 주기(1·2구간) 실증 매뉴얼

**문서 번호**: CC-DOC-2026-23  
**작성 일자**: 2026-11-15  
**작성자**: 콜드체인 디지털 트윈 연구팀 (한성민)  
**적용 대상**: FDT 캐리어 보드(`carrier-c6-02`), ESP32 스마트 스캐너(`esp32dev`), 소비자·관제 대시보드 및 4-in-1 통합 포털  

---

## 1. 2026-11-15 실차 주행 실험(`FmID=85`) 진단 및 5대 핵심 버그 패치 내역

### 1.1 소비자 대시보드 `📍 이동 경로` 탭 `TypeError` 크래시 및 출발점 좌표 보정
* **원인**:
  1. `PyMySQL`의 `cursor.fetchall()`이 튜플(`tuple`)을 반환하는 환경에서 `leg1_sensor_pts`(`list`)와 `leg2_sensor_pts`(`tuple`)를 `+` 연산자로 결합할 때 `TypeError: can only concatenate list (not "tuple") to list` 발생.
  2. `🌱 산지(A00)` 마커가 항상 우편번호(`55632` 장수군 등) 고정 좌표를 우선 참조하여, 실제 전주(집)에서 출발해 1구간 주행을 수행할 경우 장수군에서 전주까지 직선이 그어지는 문제 존재.
* **해결 ([Step5_Run_Dashboard.py](../Final_Experiment/3_Consumer_Dashboard/Step5_Run_Dashboard.py))**:
  1. `fetch_sensor_segment()` 반환값과 결합 연산을 `list(leg1_sensor_pts) + list(leg2_sensor_pts)`로 명시적 리스트 변환 처리.
  2. 1구간 실측 주행 궤적(`leg1_sensor_pts`)이 존재할 경우 실제 출발 첫 GPS 좌표(`leg1_sensor_pts[0]`)를 `🌱 산지(A00)` 마커로 최우선 적용하고, 1구간 주행 데이터가 없을 때만 우편번호 대표 좌표로 폴백하도록 개선.

### 1.2 관제 대시보드 주행 중간 접속 시 이전 경로 누락(중간부터 표시) 버그 해결
* **원인**:
  1. 주행 출발 직후 실내 캐시 GPS 시각이 1패킷 먼저 찍히고 이후 실제 출발 시각으로 갱신되면서 `timestamp_str` 역전이 발생해 세션이 2개로 쪼개지는 현상.
  2. 주행 도중 관제 대시보드(`Step4_Run_Coldchain_v2.py`)를 열었을 때, 첫 MQTT 패킷 수신 시점부터만 메모리에 쌓고 DB에 이미 적재된 동일 세션의 출발~현재 궤적을 프리로드(Preload)하지 않던 문제.
* **해결 ([Step4_Run_Coldchain_v2.py](../Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py), [Step4_Jetson_SplitHUD.py](../Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Jetson_SplitHUD.py), [mqtt_to_mysql_daemon.py](../cloud_backend/mqtt_to_mysql_daemon.py))**:
  * 주행 중 어느 시점에 대시보드를 열거나 새로고침하더라도 DB에서 해당 차량의 최근 활성 주행 궤적 전체를 즉시 프리로드하여 **출발 지점부터 현재 위치까지 끊김 없이 한 줄로 이어지도록 수정**.

### 1.3 FDT 캐리어 센서 보드(`COM8`, `carrier-c6-02`) 실내 GPS 캐시 시간 역전 버그 수정 및 재업로드
* **원인**: 실내(`Fix: NO`, `sats=0`)에서 전원을 켰을 때 GPS 모듈 백업 메모리에 남아 있던 과거 날짜/시각을 유효 시각으로 오인하여 시스템 시계를 과거로 되돌리고 이전 좌표를 송출함.
* **해결 ([carrier_board_mqtt.cpp](../Hardware_Prototypes/code26/test/src/carrier_board_mqtt.cpp))**:
  * 반드시 실제 위성 Fix(`gps.location.isValid() && gps.location.age() < 3000 && current_sats >= 3`)가 성립할 때만 GPS 시각 동기화 및 좌표를 사용하고, 실내 대기 중에는 `lat=0.0, lng=0.0` 및 NTP 현재 시각을 유지하도록 수정 후 **`COM8` 보드에 플래싱 및 검증 완료**.

### 1.4 ESP32 스마트 QR 스캐너(`COM7`, `esp32dev`) URL 퍼센트 인코딩 디코딩 추가 및 재업로드
* **원인**: 유색 QR URL의 한글 등급 파라미터(`grade=%EC%83%81`) 및 공백(`+`, `%20`)을 디코딩하지 않고 그대로 읽던 문제.
* **해결 ([main.cpp](../Final_Experiment/2_ESP32_Firmware/src/main.cpp))**:
  * `urlDecode()` 함수를 추가하여 `%XX` UTF-8 퍼센트 인코딩과 `+` 공백을 완벽히 복원하고, 연구실(`225`, `smroom`)과 스마트폰 핫스팟/자택(`hani`) 다중 Wi-Fi를 등록하여 **`COM7` 보드에 플래싱 및 Wi-Fi 즉시 연결 검증 완료**.

### 1.5 PC 시계 오차로 인한 `A12` 선별 시각 역전 방지 및 `A11` 선행 검증 강화
* **원인**: PC 로컬 시계(`datetime.now()`)가 AWS RDS 서버 시계보다 약 30초 느려 `A10(입고)`·`A11(세척)` 이후에 `A12(선별)`를 수행했음에도 시각이 과거로 기록됨.
* **해결 ([Step3_Sorting_QR_Creator.py](../Final_Experiment/1_PC_QR_Generators/Step3_Sorting_QR_Creator.py), [app.py](../Final_Experiment/5_Unified_FastAPI_Portal/app.py), [Step5_Run_Dashboard.py](../Final_Experiment/3_Consumer_Dashboard/Step5_Run_Dashboard.py))**:
  * 모든 단계의 기록 시각을 AWS RDS 서버의 KST `NOW()` 기준으로 통일하고, 반드시 `Lo='A11'`(세척 완료) 데이터가 DB에 존재할 때만 `A12` 난수 등급 배분 및 유색 QR 생성이 가능하도록 검증 로직 통일.

---

## 2. 24/7 상시 클라우드 통합 포털 및 차세대 FastAPI 통합 포털 구축

### 2.1 [즉시 상시 운영] Streamlit Cloud 24/7 현장 작업자·관리자 통합 포털
컴퓨터를 완전히 끈 상태에서도 스마트폰(LTE/5G)만으로 현장에서 `A00` 무색 QR과 `A12` 유색 QR을 즉시 생성할 수 있도록 기존 24/7 클라우드 도메인에 PIN 권한 기반 포털을 내장했습니다.

* 🔗 **현장 작업자·관리자 통합 포털 (영구 고정 URL · PC 전원 무관 24시간 가동)**:
  👉 **https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/?mode=admin**
  * **PIN 번호**: `0000` (통합관리자) | `1111` (농가 `A00`) | `2222` (APC `A12`)
  * **소비자 QR 스캔 시 (`?FmID=85&grade=상`)**: 관리자 메뉴가 숨겨지고 100% 소비자 안심 이력 화면만 표시됨.

### 2.2 [차세대 메인 후보] 4-in-1 FastAPI + WebSocket 통합 포털 (`Final_Experiment/5_Unified_FastAPI_Portal/`)
* **폴더 위치**: [Final_Experiment/5_Unified_FastAPI_Portal/](../Final_Experiment/5_Unified_FastAPI_Portal/)
* **구성**: 단일 웹 서버(`app.py` + `templates/index.html`)에서 **① 소비자 안심 조회(기존 Streamlit 디자인·정보 100% 동일)**, **② 농가 수확·무색 QR 생성(`A00`, `StD`/`DD`/`HN` 분리 및 `Rp=NULL`)**, **③ APC 스캐너/FmID 연동 난수 등급 배분 및 유색 QR 생성(`A12`, `A11` 필수 검증)**, **④ 실시간 차량 관제(WebSocket 무깜빡임 + 조도 그래프 + 접이식 텔레메트리 로그)** 4개 탭을 PIN 권한별로 통합 제공.
* **생성된 QR 이미지 자동 저장 위치**:
  1. [Final_Experiment/1_PC_QR_Generators/](../Final_Experiment/1_PC_QR_Generators/) (`{AC}{FmID}{YYMMDD}_QR.png`, `{FmID}_A_QR.png`, `_B_QR.png`, `_C_QR.png`)
  2. [Final_Experiment/5_Unified_FastAPI_Portal/generated_qr/](../Final_Experiment/5_Unified_FastAPI_Portal/generated_qr/)

---

## 3. 전 주기(1구간 + 2구간) 실차 실험 표준 진행 순서 (`집 ➔ 중간 정차(APC) ➔ 학교`)

PC를 켜두지 않고 **스마트폰(핫스팟 `hani`) + FDT 캐리어 보드 + ESP32 QR 스캐너 보드**만으로 진행하는 실전 프로토콜입니다.

1. **🏠 [출발 전 — 집] `A00` 농가 무색 QR 생성**:
   * 스마트폰에서 `https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/?mode=admin` 접속 (PIN: `0000`)
   * **`🌾 1. 농가 수확·무색 QR 생성 (A00)`** 에서 새 `FmID`(예: `86`)로 무색 QR 생성 후 핸드폰에 이미지 저장.
2. **🚗 [1구간 주행 — 집 ➔ 중간 지점] 산지 ➔ APC 운송**:
   * 스마트폰 핫스팟(`hani` / `12345687`) ON + **FDT 캐리어 센서 보드 전원 ON** 후 출발.
   * AWS EC2 상시 데몬(`coldchain-daemon.service`)이 자동으로 `lab225.sensor_data`에 1구간 GPS 궤적을 실시간 적재.
3. **🛑 [중간 지점 정차 — APC 공정] `A10` ➔ `A11` ➔ `A12`(유색 QR 생성) ➔ `A13` ➔ `A14` ➔ `A15`**:
   * **ESP32 QR 스캐너 전원 ON** (기본 `AUTO` 모드)
   * ① 핸드폰의 **무색 QR 1번째 스캔** ➔ 스캐너 OLED **`A10` (입고)** 확인
   * ② 핸드폰의 **무색 QR 2번째 스캔** ➔ 스캐너 OLED **`A11` (세척)** 확인
   * ③ 핸드폰에서 통합 포털(`?mode=admin`)의 **`🏭 2. APC 선별·유색 QR 생성 (A12)`** 탭 선택 ➔ `FmID`(`86`) 입력 후 버튼 터치 ➔ 난수(`A/B/C/결점`) 자동 배분 및 **유색(빨강·노랑·초록 사과) QR 3종 즉시 화면 표시**!
   * ④ 핸드폰 화면에 뜬 **빨간 사과(`A등급`) 유색 QR을 스캐너로 연속 3회 스캔**:
     * 1회 스캔 ➔ OLED **`A13` (포장)** 확인
     * 2회 스캔 ➔ OLED **`A14` (저온저장)** 확인
     * 3회 스캔 ➔ OLED **`A15` (APC 출고)** 확인
4. **🏫 [2구간 주행 및 도착 — 중간 지점 ➔ 학교] APC ➔ 판매처 냉장운송 및 `A16` 마감**:
   * FDT 보드가 켜진 상태로 다시 학교까지 주행 (2구간 파란색 GPS 궤적 자동 적재).
   * 학교 도착 후 핸드폰의 **유색 QR을 스캐너로 마지막 1회 스캔** ➔ OLED **`A16` (판매처 도착)** 확인.
5. **🔍 [최종 검증] 소비자 안심 이력 조회**:
   * 스마트폰 기본 카메라로 유색 QR을 스캔하면 **초록색 1구간(`집 ➔ 중간 지점`)**과 **파란색 2구간(`중간 지점 ➔ 학교`)** 도로 궤적, 평균 온도, 최대 충격량, `A00~A16` 타임라인이 완벽하게 표시됨.
