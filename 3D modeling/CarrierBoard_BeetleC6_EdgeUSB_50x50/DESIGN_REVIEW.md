# CarrierBoard Beetle ESP32-C6 EdgeUSB (50×50mm) 설계 검토 및 규격 보고서

본 문서는 `3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50` 기판의 설계 검토 내용, 핀 매핑 검증, 그리고 각 센서 모듈의 크기 산출 근거를 기록한 문서입니다.

---

## 1. 주요 설계 특징 및 장점

1. **Beetle ESP32-C6 하단 Edge-Flush 배치 ($Y=100.0\,\text{mm}$)**:
   - Beetle C6 개발보드를 180° 회전하여 PCB 최하단에 배치.
   - 첫 번째 핀($Y=102.66$)과 USB-C 끝단(약 $2.66\,\text{mm}$) 간격을 정확히 반영하여, **Type-C 포트가 $50\times50\,\text{mm}$ 기판 하단 외곽선과 0mm 오차로 Flush(일치)**되도록 설계.
   - 외부 케이스 조립 시 기판에서 케이블 직결 가능.
2. **양면(Dual-Side) 분산 실장으로 간섭 0mm 달성**:
   - **전면(Top)**: SHT45 (좌상단), BH1750 (우상단), JST-PH 2.0 배터리 단자 및 PCM12 전원 스위치 (상단 중앙), Beetle ESP32-C6 (하단 중앙)
   - **후면(Bottom)**: GY-521 IMU (좌측 수직), ATGM336H GPS (우측 수직)
   - 4개 센서와 MCU가 $50\times50\,\text{mm}$ 외곽선 안쪽에 100% 수납되며 부품 간 간섭 0mm.
3. **외곽 모서리 2mm 챔퍼(Chamfer) 가공**:
   - 거버 뷰어의 Arc 보간 오류(스캘럽 현상)를 방지하기 위해 45도 직선 챔퍼 적용.
4. **배터리 충전 및 전압 모니터링**:
   - Beetle C6 자체의 TP4057 충전 IC 활용.
   - Beetle C6 내부의 $1\text{M}\Omega:1\text{M}\Omega$ 분압 회로를 통해 **GPIO 0(ADC)**에서 배터리 잔량 바로 측정 가능 (외장 분압 저항 불필요).

---

## 2. 센서 모듈별 크기 산출 근거 및 정보 출처

| 부품 / 모듈 | 고려된 치수 ($W \times L$) | 소켓 규격 | 데이터 출처 / 근거 정보 |
| :--- | :--- | :--- | :--- |
| **Beetle ESP32-C6 Mini** | **$20.50 \times 25.00\,\text{mm}$** | 1x8 소켓 2열 (열 간격 $17.78\,\text{mm}$) | DFRobot 공식 치수 도면 (`DFR1117_dimension_V1.0.png`) |
| **GY-521 (MPU6050)** | **$15.50 \times 20.50\,\text{mm}$** | 1x8 수직 소켓 (후면 실장) | InvenSense 표준 규격 및 프로젝트 내 `GyroSensor_GY_521.step` (실측 $20.08 \times 15.08\,\text{mm}$) |
| **ATGM336H GPS** | **$13.00 \times 15.50\,\text{mm}$** | 1x5 수직 소켓 (후면 실장) | Zhongke Micro ATGM336H 5핀 미니 모듈 표준 규격 |
| **SHT45 (온습도)** | **$13.00 \times 12.00\,\text{mm}$** | 1x5 수평 소켓 (전면 실장) | Sensirion SHT4x 소형 범용 모듈 (거버 실크스크린 $13\times12\,\text{mm}$ 반영) |
| **BH1750 (조도)** | **$13.00 \times 12.00\,\text{mm}$** | 1x5 수평 소켓 (전면 실장) | ROHM BH1750FVI GY-302 모듈 표준 규격 |
| **JST-PH 2.0 & SW1** | JST: $6.0 \times 4.5\,\text{mm}$<br>SW1: $7.0 \times 4.0\,\text{mm}$ | JST 2P / PCM12 SPDT 슬라이드 | JST 및 C&K 표준 부품 라이브러리 |
| **기판 외곽 및 M3 홀** | **$50.0 \times 50.0\,\text{mm}$** | 드릴 $\varnothing 3.2$, 패드 $\varnothing 5.5\,\text{mm}$ | 모서리에서 $3.5\,\text{mm}$ 인입된 4개소 (`103.5`, `146.5`) |

---

## 3. 전기적 핀 매핑 검증 결과 (DFRobot 공식 회로도 V1.1 기준)

Beetle C6 180° 회전 배치 상태 기준:

| 신호명 | Beetle C6 핀 | 연결 대상 | 기능 설명 |
| :--- | :--- | :--- | :--- |
| **I2C SDA** | **GPIO 19** (좌측 Pin 6) | SHT45 Pin 4, BH1750 Pin 2, GY-521 Pin 5 | I2C 데이터 라인 (R3 $4.7\text{k}\Omega$ 풀업) |
| **I2C SCL** | **GPIO 20** (좌측 Pin 7) | SHT45 Pin 3, BH1750 Pin 3, GY-521 Pin 6 | I2C 클럭 라인 (R4 $4.7\text{k}\Omega$ 풀업) |
| **GPS TX** | **GPIO 16 / TX** (좌측 Pin 5) | ATGM336H GPS Pin 3 (RXD) | ESP32 송신 $\rightarrow$ GPS 수신 |
| **GPS RX** | **GPIO 17 / RX** (좌측 Pin 4) | ATGM336H GPS Pin 4 (TXD) | ESP32 수신 $\leftarrow$ GPS 송신 |
| **BAT** | **BAT** (좌측 Pin 1) | SW1 스위치 출력 $\leftarrow$ JST 배터리(+) | 배터리 전원 입력 및 Type-C 충전 라인 |
| **3V3** | **3V3** (우측 Pin 2) | 모든 센서(SHT45, BH1750, GY-521, GPS) VCC | 3.3V 센서 전원 공급 |
| **GND** | **GND** (좌 Pin 2, 우 Pin 1) | M3 나사홀 4개 및 센서 공통 접지 | GND 플레인 연결 |

---

## 4. ⚠️ 실물 제작 및 조립 시 필수 주의사항

1. **SHT45 모듈 핀 순서 확인 (치명적 쇼트 방지)**:
   - 본 캐리어 보드의 `J_SHT45` 핀헤더는 **`1: 3V3, 2: GND, 3: SCL, 4: SDA, 5: NC`** (소형 범용 모듈) 기준입니다.
   - 프로젝트 내 3D 모델로 존재하는 **Adafruit SHT45 모듈**의 경우 핀 순서가 **`VIN - 3Vo - GND - SCL - SDA`**이므로, Adafruit 모듈을 꽂으면 **3Vo와 GND가 직결 쇼트**됩니다. 반드시 `VCC-GND-SCL-SDA` 순서의 모듈인지 확인해야 합니다.
2. **KiCad PCB 파일과 발주 거버 파일 간의 차이**:
   - JLCPCB 발주용 파일(`Gerber_CarrierBoard_BeetleC6_EdgeUSB_50x50.zip`)에는 모든 동박 트레이스와 비아, R3/R4 풀업 저항 패드가 완벽히 포함되어 있어 발주 자체에는 문제가 없습니다.
   - 다만 `CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb` 파일 내부에는 풋프린트와 외곽선만 저장되어 있으므로, KiCad 프로그램 내에서 편집/DRC를 하려면 트레이스 동기화가 필요합니다.
