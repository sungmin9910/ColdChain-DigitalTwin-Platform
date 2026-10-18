# 20. 04호차(carrier-c6-04) 야간 주행 실증 데이터 무손실 복원, 대시보드 실시간 궤적 프리로드 및 Wi-Fi 자가복구 펌웨어 적용 보고서

**문서 번호**: CC-DOC-2026-20  
**작성 일자**: 2026-10-18  
**작성자**: 콜드체인 디지털 트윈 연구팀  
**대상 하드웨어**: CarrierBoard 04호차 (`carrier-c6-04`, Base MAC: `CC:8D:A2:FA:9F:BC`)  
**연결 포트**: `COM9` (ESP32-C6 USB Serial/JTAG)  
**통합 관제 대상 세션**: `truck04_주행_2026-10-18_20시24분`  

---

## 1. 개요 및 배경

2026년 10월 18일 야간, 4호차 센서 노드(`carrier-c6-04`)를 탑재하여 실제 귀가 주행 환경에서 데이터 계측 실증을 수행했습니다.  
실험 중 두 가지 현장 운용 이슈가 식별되었습니다:
1. **대시보드 접속/새로고침 시 이동 궤적 단절**: 주행 중간에 대시보드에 접속하거나 새로고침하면 이전까지 주행해 온 경로가 화면에 표시되지 않고 접속한 시점부터만 점이 찍히는 현상.
2. **모바일 핫스팟 단절 후 재연결 불가**: 차량 이동 중 핫스팟 통신이 일시 단절된 후 전원이 켜진 상태에서 핫스팟을 다시 켜도 보드가 재연결되지 않아 보드 전원을 끌 수 없는 상황에서의 운용 제약.

이에 보드 내부 **LittleFS 블랙박스 메모리(430건)**를 즉시 전량 덤프하여 주행 전 구간 395건 데이터를 100% 무손실 복원하고 MySQL 클라우드 DB에 단일 정규 세션으로 적재 완료하였으며, 두 문제를 근본적으로 해결하는 대시보드 및 펌웨어 아키텍처 개선을 완료·적용했습니다.

---

## 2. LittleFS 블랙박스 데이터 무손실 추출 및 DB 정규화 적재

1. **하드웨어 진단 및 메모리 상태 확인**:
   * PC의 `COM9` 포트를 통해 Base MAC `CC:8D:A2:FA:9F:BC`의 04호차 단말 식별.
   * `info` 명령어 질의 결과: 총 430건(약 89.8 KB)의 LittleFS 블랙박스 레코드 확인.
2. **100% 무손실 덤프 및 데이터 분석 ([carrier_dump_20261018.jsonl](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/scratch/carrier_dump_20261018.jsonl))**:
   * 오늘(2026-10-18 20:24:51 ~ 21:04:44) 야간 주행 데이터 총 395건 분리 추출.
   * 유효 GPS 위성 좌표 331건 및 1.8G 이상 충격 이벤트 17회 감지.
3. **AWS RDS MySQL 단일 정규 세션 적재 ([insert_carrier04_tonight.py](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/scratch/insert_carrier04_tonight.py))**:
   * 통신 단절로 인해 파편화되었던 기존 167건을 백업 후 삭제하고, 전 구간 395건을 단일 세션 `truck04_주행_2026-10-18_20시24분`으로 공식 `INSERT`.
4. **보드 메모리 초기화**:
   * DB 적재 완료 후 `clear` 명령을 송신하여 LittleFS 링버퍼를 0건(0 Byte)으로 안전 초기화하여 차기 실험 준비 완료.

---

## 3. 주행 실증 텔레메트리 핵심 요약

| 계측 항목 | 상세 수치 및 분석 결과 |
| :--- | :--- |
| **계측 구간** | **2026-10-18 20:24:51 ~ 21:04:44** (총 39분 53초, 총 395개 레코드) |
| **GPS 데이터** | **331개 유효 위성 좌표** 수집 |
| **주행 속도** | 최고 속도 **73.7 km/h** |
| **온도 범위** | **24.76 ℃ ~ 25.86 ℃** |
| **습도 범위** | **65.48 % ~ 76.24 %** |
| **충격 이벤트** | 1.8G 이상 충격 **총 17회 감지** (최대 충격량 **3.01 G**) |

---

## 4. 핵심 문제 해결 및 구현 내역

### 4.1. [문제 1 해결] 실시간 주행 궤적 선행 로드(Preload) 아키텍처 적용
* **수정 파일**: [Step4_Run_Coldchain_v2.py](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py)
* **구현 내용**:
  * 실시간 모드 진입 시 메모리가 비어있더라도, 최근 6시간 이내의 활성 주행 세션 데이터를 DB에서 자동으로 조회하여 `data_history`에 프리로드(Preload).
  * 주행 도중 대시보드를 켜거나 F5 새로고침을 하더라도 **출발지부터 지금까지 달려온 이동 경로가 즉시 복원**되고, 그 뒤로 들어오는 실시간 패킷이 연속으로 결합되어 표시됩니다.
  * 드롭다운 세션 라벨에 `🚗 [10-18 야간주행] 20:24 자택복귀 (395건, 최고 74km/h)` 포맷을 적용하여 가독성을 극대화했습니다.

### 4.2. [문제 2 해결] 펌웨어 Wi-Fi 라디오 서브시스템 자가복구(Self-healing) 구현
* **수정 파일**: [carrier_board_mqtt.cpp](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/Hardware_Prototypes/code26/test/src/carrier_board_mqtt.cpp)
* **구현 내용**:
  * **Stale State 방지**: Wi-Fi 단절 감지 시 `client.disconnect()`, `espClient.stop()`, `WiFi.disconnect(true, true)`를 호출해 좀비 소켓 및 이전 BSSID/채널 캐시를 즉각 정리.
  * **라디오 Power-Cycle (보드 리셋 불필요)**: 재연결 시도가 3회 이상(약 45초) 실패할 경우, MCU 메인 코어 및 센서 계측/LittleFS 저장은 중단 없이 유지한 채 **Wi-Fi RF 모뎀만 소프트웨어적으로 전원 리셋(`WiFi.mode(WIFI_OFF) ➔ delay(80) ➔ WiFi.mode(WIFI_STA)`)**하여 새 핫스팟 비컨을 100% 감지하도록 개선.
  * **무손실 백필(Flush) 연동**: Wi-Fi 및 MQTT가 복구되는 즉시 누적된 오프라인 버퍼(`flushOfflineBuffer()`)를 브로커로 고속 안전 전송하여 데이터 유실 0.0% 보장.
* **펌웨어 배포**: PlatformIO를 통해 `beetle_c6_mqtt_truck04` 타깃으로 컴파일 및 `COM9` 보드에 플래싱 완료.
