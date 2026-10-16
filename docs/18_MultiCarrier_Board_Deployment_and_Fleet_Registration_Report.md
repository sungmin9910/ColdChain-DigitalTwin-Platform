# 18. Multi-CarrierBoard 4대 전 차량 구축, MAC 맵핑 및 통합 관제 대시보드 등록 보고서

**문서 번호**: CC-DOC-2026-18  
**작성 일자**: 2026-10-16  
**작성자**: 콜드체인 디지털 트윈 연구팀  
**대상 하드웨어**: CarrierBoard Beetle ESP32-C6 EdgeUSB 50×50 (총 4대: 1호차 ~ 4호차)  
**핵심 장치**: DFRobot Beetle ESP32-C6 Mini MCU (RISC-V, ESP32-C6FH4)  
**연동 센서**: SHT45 (온습도), BH1750 (조도), GY-521/MPU6050 (6축 IMU), ATGM336H (GPS)

---

## 1. 개요 및 목적

본 문서는 농산물(사과/배) 수송용 프리미엄 콜드체인 디지털 트윈 모니터링 시스템의 확장을 위해 **CarrierBoard 1호차부터 4호차까지 총 4대의 독립 센서 노드를 개별 식별자/토픽으로 구축**하고, 각 보드의 고유 MAC 어드레스 매핑, 전용 펌웨어 자동 빌드/플래싱, 그리고 통합 관제 대시보드([Step4_Run_Coldchain_v2.py](file:///c:/Users/korea/Desktop/1hsm/hanhanhan/ColdChain-DigitalTwin-Platform/Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py)) 등록 및 실시간 검증 결과를 종합 기록한 공식 엔지니어링 문서입니다.

---

## 2. 1~4호차 단말별 식별자 및 하드웨어 매핑표

| 호차 | 단말 식별자 (`device`) | MQTT 발행/구독 토픽 | 실측 연결 포트 | MCU Base MAC 주소 | 센서 4종 상태 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1호차** | `carrier-c6-01` | `coldchain/truck01/sensor` | - | 기존 등록 단말 | 정상 (실차 주행 검증 완료) |
| **2호차** | `carrier-c6-02` | `coldchain/truck02/sensor` | `COM17` | `F0:F5:BD:2C:48:5C` | 정상 (온습도/조도/IMU/GPS) |
| **3호차** | `carrier-c6-03` | `coldchain/truck03/sensor` | `COM38` | `CC:8D:A2:FA:84:EC` | 정상 (온습도/조도/IMU/GPS) |
| **4호차** | `carrier-c6-04` | `coldchain/truck04/sensor` | `COM39` | `CC:8D:A2:FA:9F:BC` | 정상 (온습도/조도/IMU/GPS) |

---

## 3. 펌웨어 아키텍처 및 빌드 최적화

### 3.1 단말 ID 및 MQTT 토픽 매크로화 ([carrier_board_mqtt.cpp](file:///c:/Users/korea/Desktop/1hsm/hanhanhan/ColdChain-DigitalTwin-Platform/Hardware_Prototypes/code26/test/src/carrier_board_mqtt.cpp))
단일 소스 코드에서 빌드 플래그(`build_flags`)를 통해 단말 ID와 MQTT 토픽을 주입할 수 있도록 전처리기 매크로를 구축했습니다:

```cpp
// MQTT 브로커 및 토픽
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;

#ifndef MQTT_TOPIC
#define MQTT_TOPIC "coldchain/truck01/sensor"
#endif

#ifndef DEVICE_ID
#define DEVICE_ID "carrier-c6-01"
#endif

const char* mqtt_topic = MQTT_TOPIC;
const char* device_id = DEVICE_ID;
```

### 3.2 PlatformIO 멀티 타깃 환경 구축 ([platformio.ini](file:///c:/Users/korea/Desktop/1hsm/hanhanhan/ColdChain-DigitalTwin-Platform/Hardware_Prototypes/code26/test/platformio.ini))
하드코딩된 포트 지정을 제거하고, 각 차량별 독립 빌드 타깃을 정의하여 동적 포트 업로드를 지원합니다:

* `[env:beetle_c6_mqtt]`: 1호차 (`carrier-c6-01`)
* `[env:beetle_c6_mqtt_truck03]`: 3호차 (`carrier-c6-03`, `-DMQTT_TOPIC="coldchain/truck03/sensor"`)
* `[env:beetle_c6_mqtt_truck04]`: 4호차 (`carrier-c6-04`, `-DMQTT_TOPIC="coldchain/truck04/sensor"`)

---

## 4. 대시보드 확장 ([Step4_Run_Coldchain_v2.py](file:///c:/Users/korea/Desktop/1hsm/hanhanhan/ColdChain-DigitalTwin-Platform/Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py))

1. **`TRUCK_OPTIONS` 확장**: 3호차, 4호차 전용 식별자, 한글/영문 라벨, 토픽, 디바이스 ID를 통합 딕셔너리에 추가.
2. **동적 MQTT 구독 (`on_connect`)**: 개별 하드코딩 대신 `TRUCK_OPTIONS.values()` 순회를 통해 등록된 모든 차량의 토픽을 자동 일괄 구독.
3. **충돌 및 혼선 방지 필터**: 선택된 차량 이외의 타 차량 패킷은 조용히 백그라운드 스킵하며, 토픽과 장치명이 불일치하는 이상 패킷 유입 시 경고 알림 표시.

---

## 5. 실증 검증 결과

* **3호차 (`carrier-c6-03`)**:
  * 플래싱: `beetle_c6_mqtt_truck03` -> `COM38` (21.79초 소요, 성공)
  * 실측값: 24.52 ℃, 50.79 %, 483.3 lx, 1.00 G, GPS 카운트 정상 증가
  * MQTT: `coldchain/truck03/sensor` -> `MQTT 발행 성공 (PASS)`
* **4호차 (`carrier-c6-04`)**:
  * 플래싱: `beetle_c6_mqtt_truck04` -> `COM39` (21.40초 소요, 성공)
  * 실측값: 23.11 ℃, 52.31 %, 498.3 lx, 1.45 G, GPS 카운트 정상 증가
  * MQTT: `coldchain/truck04/sensor` -> `MQTT 발행 성공 (PASS)`

---

## 6. 결론

CarrierBoard 총 4대의 하드웨어 및 펌웨어 라인업이 완벽히 정렬되었으며, 향후 동시 다차량 주행 실험 및 저온저장고 교차 실증을 수행할 준비가 100% 완료되었습니다.
