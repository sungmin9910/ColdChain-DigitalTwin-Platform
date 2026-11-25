# 온습도·조도 20시간 항온항습 챔버 교정 가이드 (`beetle_c6_chamber_cal`)

본 폴더(`scripts/chamber_calibration/`)는 **BS EN 12830:2018** 및 **IEC 60068-3-5/6** 규격에 따른 `SHT45`(온습도) 및 `BH1750`(조도) 센서의 **패턴 A (20시간 다온도 × 다습도 2차원 매트릭스)** 챔버 교정 실험 도구 모음입니다.

---

## 1. 실험 전 보드 펌웨어 업로드 (4대 공통 단일 타깃)

`chamber_calibration_env.cpp`는 보드의 Wi-Fi STA MAC 주소를 읽어 `carrier-c6-01 ~ 04` 및 **교정 전용 MQTT 토픽(`coldchain/chamber/carrier-c6-01~04`)** 을 자동 할당합니다. 실제 콜드체인 운영 DB 테이블(`sensor_data`, `sensor_telemetry`)에는 전혀 섞이지 않고, 전용 테이블 **`lab225_v2.chamber_calibration_logs`** 에만 5초 원본 전량이 분리 저장됩니다.

```powershell
cd Hardware_Prototypes/code26/test
pio run -e beetle_c6_chamber_cal -t upload --upload-port COM38
```

* **전원 스위치 자동 시작**: 배터리 스위치를 켜는 즉시 별도 시리얼 `start` 명령 없이 **5.0초 간격**으로 실차 동일 발열 조건(Wi-Fi MQTT + LittleFS `/chamber_cal.csv`) 기록이 자동 시작됩니다.
* **20시간 이상 오프라인 무손실 보장**: 금속 챔버 도어 차폐로 새벽에 Wi-Fi가 끊기더라도 `/chamber_cal.csv`(`~45 B/행`)에 최대 38시간 이상 덮어쓰기 없이 100% 보존됩니다.

---

## 2. 현장에서 Wi-Fi 추가 및 시각 동기화 (`step1_live_mqtt_and_prep.py`)

현장 `2.4 GHz` 공유기 정보를 코드(`default_wifi_list[]`)에 추가해 재업로드하거나, **재컴파일 없이** 아래 명령 한 줄로 보드에 Wi-Fi 등록·시각 동기화·초기화를 한 번에 수행할 수 있습니다:

```powershell
python scripts/chamber_calibration/step1_live_mqtt_and_prep.py --prep --port COM38 --wifi-ssid "현장공유기2.4G" --wifi-pass "비밀번호" --clear
```

이후 챔버 옆 노트북(절전 해제)에서 4대 보드의 실시간 MQTT 백업 수집기를 켜 둡니다:

```powershell
python scripts/chamber_calibration/step1_live_mqtt_and_prep.py --listen
```

---

## 3. 실험 종료 후 보드 내장 CSV 무손실 추출 (`step2_dump_littlefs_csv.py`)

20시간 실험 완료 후 각 보드를 USB로 연결해 내장 플래시의 원본 CSV를 추출합니다:

```powershell
python scripts/chamber_calibration/step2_dump_littlefs_csv.py --port COM38
```

---

## 4. 챔버 1초 기준 데이터와 매칭 및 보정식 산출 (`step3_analyze_chamber_cal.py`)

챔버에서 추출한 1초 단위 기준 CSV와 보드 5초 CSV를 자동 정렬하여 온도 선형 보정식($a_T, b_T$), 포화수증기압($P_{\text{sat}}$) 자체발열 보상 기반 습도 보정식($a_{RH}, b_{RH}$), `25°C / 60%RH` 히스테리시스 오차, 그리고 EN 12830 등급 합격 여부를 산출합니다:

```powershell
python scripts/chamber_calibration/step3_analyze_chamber_cal.py `
  --pod-csv data/chamber_calibration/carrier-c6-03/chamber_raw_YYYYMMDD_HHMMSS.csv `
  --chamber-csv data/chamber_calibration/chamber_ref_1s.csv `
  --device carrier-c6-03
```
