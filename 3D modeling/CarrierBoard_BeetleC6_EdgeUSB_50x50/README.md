# CarrierBoard Beetle ESP32-C6 EdgeUSB (50mm × 50mm) v9 (정밀 분기 배선 릴리즈)

## 1. 개요 및 설계 목적
본 캐리어 보드는 사용자가 직접 SMD 칩(QFN/BGA)을 납땜하지 않고, **디바이스마트에서 판매되는 시판 완제품 모듈(DFRobot Beetle ESP32-C6 Mini 및 센서 브레이크아웃 모듈 4종)을 2.54mm 암형 핀헤더 소켓(Female Header Socket)에 꽂아서 원터치로 조립할 수 있도록 설계된 전용 인터페이스 기판**입니다.

### 완벽한 개별 핀 분기 배선 (Discrete Branch Routing)
기존 버전에서 거버 생성 스크립트의 직선 좌표 오차로 인해 발생했던 **"하판에서 3.3V 트레이스가 SHT45 핀 헤더 전체를 관통하여 쇼트시키던 오류"** 및 **"상판에서 트레이스가 MCU 핀 사이를 침범하던 오류"**를 전면 수정하여, **모든 전원선과 신호선이 전용 채널을 통해 각 센서의 지정된 핀에만 1:1로 정확하게 인입되도록 재배선**했습니다:
- **3.3V 전원**: ESP32 3.3V 출력에서 분기되어 각 센서 1번 핀(VCC/VIN)에만 독립 인입
- **GND**: 상/하 분산 접지 버스로 각 센서의 GND 핀 및 M3 홀 4개소에 연결
- **I2C SDA / SCL**: ESP32 GPIO19 / GPIO20에서 분기되어 3개 I2C 센서 및 4.7kΩ 풀업 저항에만 독립 인입
- **GPS UART**: GPIO16/17에서 GPS 모듈 핀으로 $7.0\sim8.7\,\text{mm}$ 초단거리 직결

---

## 2. 부품별 실물 치수 및 실장 레이아웃

| 부품 / 모듈 | 실측 외형 치수 ($W \times L$) | 실장면 및 위치 | 소켓 규격 | 주요 특징 및 안전 여유 |
| :--- | :--- | :--- | :--- | :--- |
| **Beetle ESP32-C6** | **$20.50 \times 25.00\,\text{mm}$** | **Top (전면)** 하단 중앙<br>($X: 114.75\sim135.25, Y: 100.0\sim125.0$) | 1×8 소켓 2열 | • USB-C 포트 기판 하단(Y=100.0)과 Edge-Flush<br>• **후면 하부 100% 클린 존 (관통 핀 0개 사수)** |
| **BH1750 조도 (GY-302)** | **$13.90 \times 18.50\,\text{mm}$** | **Top (전면)** 우측 날개(Right Wing)<br>($X: 135.8\sim149.7, Y: 106.7\sim125.2$) | 1×5 수평 소켓 ($Y=123.2$) | • 상공을 향해 조도 수광 극대화<br>• Beetle C6와 $0.55\,\text{mm}$ 간격, M3 홀 패드와 $0.45\,\text{mm}$ 여유 |
| **GPS ATGM336H Mini** | **$13.10 \times 15.70\,\text{mm}$** | **Bottom (후면)** 좌측 날개(Left Wing)<br>($X: 100.8\sim113.9, Y: 107.5\sim123.2$) | 1×5 수평 소켓 ($Y=109.5$) | • Beetle C6 UART 핀(GPIO16/17)과 최단거리($7\sim8\,\text{mm}$) 직결<br>• Beetle C6와 $0.85\,\text{mm}$, M3 패드와 $1.25\,\text{mm}$ 안전 간격 |
| **SHT45 온습도 (Qwiic)** | **$25.50 \times 17.80\,\text{mm}$** | **Bottom (후면)** 좌상단<br>($X: 100.5\sim126.0, Y: 125.5\sim143.3$) | 1×5 수평 소켓 ($Y=127.5$) | • Pin 2(3Vo) NC 처리로 3.3V-GND 쇼트 완벽 방지<br>• 상단 M3 나사 패드($Y \ge 143.75$) 아래로 완전 인입 |
| **GY-521 IMU (MPU6050)** | **$20.70 \times 15.65\,\text{mm}$** | **Bottom (후면)** 우상단<br>($X: 128.5\sim149.2, Y: 125.5\sim141.15$) | 1×8 수평 소켓 ($Y=127.5$) | • SHT45와 **$2.50\,\text{mm}$의 넉넉한 수평 공극** 확보<br>• 상단 M3 패드와 $2.60\,\text{mm}$ 간격 |
| **JST-PH 2.0 & SW1** | JST: $6.0 \times 4.5$<br>SW1: $7.0 \times 4.0$ | **Top (전면)** 상단 중앙<br>($Y: 144.5\sim149.0$) | JST 2P TH / SW1 SMD | • SHT45/GY-521($Y \le 143.3$)과 2D 투영 겹침 0mm |
| **M3 고정홀 4개소** | 드릴 $\varnothing 3.2$, 패드 $\varnothing 5.5$ | 4개 모서리 ($3.5\,\text{mm}$ 인입) | 기계식 홀 | • 패드 접지(GND) 결선, 모든 센서 볼트 헤드 간섭 0mm |

---

## 3. 전체 핀 매핑 테이블

### 1) Beetle ESP32-C6 개발보드
- **좌측 소켓 (`J_MCU_L`, X=116.11mm)**:
  - Pin 1 (`Y=102.66`): **BAT** (SW1 스위치 출력 $\leftarrow$ 배터리+)
  - Pin 2 (`Y=105.20`): **GND**
  - Pin 3 (`Y=107.74`): NC (VIN)
  - Pin 4 (`Y=110.28`): **GPS_RX** (GPIO17 $\leftarrow$ GPS TX, 배선길이 8.7mm)
  - Pin 5 (`Y=112.82`): **GPS_TX** (GPIO16 $\rightarrow$ GPS RX, 배선길이 7.0mm)
  - Pin 6 (`Y=115.36`): **I2C_SDA** (GPIO19 $\leftrightarrow$ 모든 I2C 센서)
  - Pin 7 (`Y=117.90`): **I2C_SCL** (GPIO20 $\rightarrow$ 모든 I2C 센서)
  - Pin 8 (`Y=120.44`): NC
- **우측 소켓 (`J_MCU_R`, X=133.89mm)**:
  - Pin 1 (`Y=102.66`): **GND**
  - Pin 2 (`Y=105.20`): **3V3** (모든 센서 3.3V 공급)
  - Pin 3~8: NC

### 2) 센서 모듈 소켓
| 모듈명 | 실장면 | 소켓 규격 | 핀 순서 (1번 $\rightarrow$ 끝번) | I2C 주소 / Baud |
| :--- | :---: | :---: | :--- | :---: |
| **BH1750 (GY-302)** | Top | 1×05 가로 | `1: 3V3, 2: GND, 3: SCL, 4: SDA, 5: GND(ADDR)` | `0x23` |
| **GPS (ATGM336H)** | Bottom | 1×05 가로 | `1: 3V3, 2: GND, 3: GPS_RX(<-TX), 4: GPS_TX(->RX), 5: NC` | 9600 bps |
| **SHT45 (Qwiic)** | Bottom | 1×05 가로 | `1: 3V3(VIN), 2: NC(3Vo), 3: GND, 4: SCL, 5: SDA` | `0x44` |
| **GY-521 (IMU)** | Bottom | 1×08 가로 | `1: 3V3, 2: GND, 3: SCL, 4: SDA, 5: NC, 6: NC, 7: GND(AD0), 8: NC` | `0x68` |

---

## 4. PCB 제조 발주 사양 (JLCPCB 기준)
- **압축 거버 파일**: `Gerber_CarrierBoard_BeetleC6_EdgeUSB_50x50.zip`
- **외형 치수**: `50.0mm × 50.0mm` (모서리 2mm 45도 챔퍼)
- **레이어**: `2 Layers (FR-4)`
- **두께**: `1.6mm`
- **동박 두께**: `1 oz`
- **솔더마스크 색상**: `Matte Black` (또는 Green/Blue)
- **실크스크린**: `White`
