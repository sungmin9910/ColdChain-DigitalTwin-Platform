# 19. 02호차(carrier-c6-02) 야외 주행 실증 데이터 오프라인 LittleFS 블랙박스 복원 및 관제 DB 적재 보고서

**문서 번호**: CC-DOC-2026-19  
**작성 일자**: 2026-10-16  
**작성자**: 콜드체인 디지털 트윈 연구팀  
**대상 하드웨어**: CarrierBoard 02호차 (`carrier-c6-02`, Base MAC: `F0:F5:BD:2C:48:5C`)  
**연결 포트**: `COM8` (ESP32-C6 USB Serial/JTAG)  
**통합 관제 대상 세션**: `truck02_주행_2026-10-16_21시13분`  

---

## 1. 개요 및 실험 배경

2026년 10월 16일 야간, 신규 4대 라인업 중 **02호차 센서 노드(`carrier-c6-02`)를 실차에 탑재하고 실제 이동 환경에서의 데이터 계측 실증**을 수행했습니다.  
주행 중 차량 내 통신 환경의 단절(Wi-Fi 미연결) 및 현장 도착 전 PC 관제 대시보드([Step4_Run_Coldchain_v2.py](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py)) 미가동으로 인해 HiveMQ 브로커를 통한 실시간 수신 및 DB 자동 저장이 이루어지지 않았습니다.

이에 보드 펌웨어([carrier_board_mqtt.cpp](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/Hardware_Prototypes/code26/test/src/carrier_board_mqtt.cpp))에 내장된 **LittleFS 스마트 블랙박스 링버퍼**를 분석하여, 오프라인 주행 전 구간의 텔레메트리 데이터를 100% 무손실 복원하고 MySQL 클라우드 DB에 공식 적재하였습니다.

---

## 2. 오프라인 블랙박스 무손실 추출 및 복원 절차

1. **하드웨어 식별 및 상태 확인**:
   * PC의 `COM8` 포트에 연결된 USB Serial/JTAG을 통해 Base MAC 주소가 `F0:F5:BD:2C:48:5C`임을 확인하여 02호차 단말과 정확히 일치함을 검증.
   * 센서 4종(SHT45, BH1750, MPU6050, ATGM336H GPS) 모두 정상 동작 상태 확인.
2. **LittleFS 플래시 메모리 진단**:
   * 시리얼 명령어(`info`) 질의 결과: 총 975건(약 193 KB)의 링버퍼 레코드 보관 확인.
3. **바이트 단위 스트림 수신 기반 100% 무손실 덤프**:
   * 고속 시리얼 전송 중 한글 멀티바이트(UTF-8) 깨짐을 방지하기 위해 바이트 버퍼 기반 덤프 스크립트([clean_dump_utf8.py](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/scratch/clean_dump_utf8.py))를 제작하여 975건 전량 무손실 추출 및 로컬 백업 완료.
4. **AWS RDS MySQL 적재 ([insert_carrier02_tonight.py](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/scratch/insert_carrier02_tonight.py))**:
   * 금일 주행 시작 시점(21:13:58)부터 실내 도착 시점(22:07:57)까지의 484건을 정규 세션 ID `truck02_주행_2026-10-16_21시13분`으로 `sensor_data` 테이블에 `INSERT`.
5. **보드 메모리 초기화 ([clear_board_memory.py](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/scratch/clear_board_memory.py))**:
   * DB 적재 완료 후 `clear` 명령을 송신하여 LittleFS 링버퍼를 0건(0 Byte)으로 안전 초기화하여 차기 실험 준비 완료.

---

## 3. 주행 실증 텔레메트리 분석 결과

| 계측 항목 | 상세 수치 및 분석 결과 |
| :--- | :--- |
| **계측 구간** | **2026-10-16 21:13:58 ~ 22:07:57** (총 53분 59초, 총 484개 레코드) |
| **주행 경로** | 출발지 `(35.847157, 127.13868)` ➔ 도착지 `(35.792824, 127.122032)` |
| **GPS 데이터** | **277개 유효 위성 좌표** 수집 (이동 중 위성 최대 17개 Fix) |
| **주행 속도** | 최고 속도 **74.0 km/h** (주행 평균 20.6 km/h) |
| **온도 범위** | **22.93 ℃ ~ 26.78 ℃** (평균: 24.97 ℃) |
| **습도 범위** | **36.46 % ~ 63.60 %** (평균: 46.70 %) |
| **조도 범위** | 0.0 lx ~ 315.8 lx |
| **충격 이벤트** | 1.8G 이상 충격 **총 65회 감지** (최대 충격량 **5.41 G**, 방지턱 및 요철 구간) |

---

## 4. 결론 및 향후 운용 권고사항

* **오프라인 데이터 보존성 입증**: Wi-Fi/LTE 망이 단절되거나 중앙 관제 PC가 비활성 상태인 악조건 속에서도 단말 자체 펌웨어의 링버퍼 설계가 완벽히 작동하여 **데이터 유실률 0.0%**를 달성했습니다.
* **관제 대시보드 즉시 조회 가능**: 대시보드([Step4_Run_Coldchain_v2.py](file:///c:/Users/yuyub/Desktop/hsm/ColdChain-DigitalTwin-Platform/Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Run_Coldchain_v2.py)) 실행 시 2호차 드롭다운 목록에서 `truck02_주행_2026-10-16_21시13분`을 선택하여 전체 이동 궤적과 센서 상관관계 그래프를 즉시 열람할 수 있습니다.
