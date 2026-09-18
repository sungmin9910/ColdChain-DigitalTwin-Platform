# CarrierBoard Beetle ESP32-C6 EdgeUSB (50mm × 50mm) v10 (실물 핀맵 완벽 반영 릴리즈)

## 1. 개요 및 설계 목적
본 캐리어 보드는 사용자가 직접 SMD 칩(QFN/BGA)을 납땜하지 않고, **디바이스마트/국내외 시판 완제품 모듈(DFRobot Beetle ESP32-C6 Mini 및 센서 브레이크아웃 모듈 4종)을 2.54mm 암형 핀헤더 소켓(Female Header Socket)에 꽂아서 원터치로 조립할 수 있도록 설계된 고신뢰성 인터페이스 기판**입니다.

### 실물 모듈 핀 순서 100% 일치 및 제로 DRC 인증 (Zero DRC & Zero Unconnected)
실물 모듈의 실제 핀 배열 및 ESP32 실장 방향을 정밀 검증하여 완벽하게 반영했습니다:
- **Beetle ESP32-C6 뒤집힘(좌우 반전) 반영**: 좌측 행(`J_MCU_L`: GND, 3V3, IO4~IO7)과 우측 행(`J_MCU_R`: BAT, GND, VIN, IO17/RX, IO16/TX, IO19/SDA, IO20/SCL, IO6) 완벽 매핑.
- **ATGM336H GPS TX/RX 보정**: 모듈 Pin 3(TXD) $\rightarrow$ MCU RX(GPIO17), Pin 4(RXD) $\leftarrow$ MCU TX(GPIO16) 직결.
- **BH1750 조도센서 핀 순서 정렬**: 왼쪽부터 `ADDR, SDA, SCL, GND, VCC` (Pin 1 ADDR 접지로 I2C 주소 `0x23` 확정).
- **SHT45 온습도센서 핀 순서 정렬**: 왼쪽부터 `SDA, SCL, GND, 3.3V, VIN` (Pin 1 SDA, Pin 2 SCL, Pin 3 GND, Pin 4&5 3.3V 병렬 공급).
- **MPU6050 6축 IMU 핀 순서 정렬**: 왼쪽부터 `INT, AD0, XCL, XDA, SDA, SCL, GND, VCC` (Pin 2 AD0 접지로 I2C 주소 `0x68` 확정).
- **KiCad 10.0 DRC 완벽 통과**: 쇼트 0건, 오픈 0건, 미연결 0건 (**Critical Errors: 0, Unconnected Items: 0**).

---

## 2. 부품별 실물 치수 및 실장 레이아웃

| 부품 / 모듈 | 실측 외형 치수 ($W \times L$) | 실장면 및 위치 | 소켓 규격 | 주요 특징 및 안전 여유 |
| :--- | :--- | :--- | :--- | :--- |
| **Beetle ESP32-C6** | **$20.50 \times 25.00\,\text{mm}$** | **Top (전면)** 중앙 상부<br>($X: 114.75\sim135.25, Y: 100.0\sim125.0$) | 1×8 소켓 2열 | • USB-C 포트 기판 상단(Y=100.0)과 Edge-Flush<br>• 좌측 Pin 2에서 3.3V 주전원 출력, 우측 Pin 1으로 스위치된 배터리 전원 공급 |
| **BH1750 조도 (GY-302)** | **$13.90 \times 18.50\,\text{mm}$** | **Top (전면)** 우측 날개(Right Wing)<br>($X: 135.8\sim149.7, Y: 106.7\sim125.2$) | 1×5 수평 소켓 ($Y=123.2$) | • 상공을 향해 조도 수광 극대화<br>• Pin 1(ADDR) 접지 직결, Pin 5(VCC) 전면 3.3V 공급 |
| **GPS ATGM336H Mini** | **$13.10 \times 15.70\,\text{mm}$** | **Bottom (후면)** 좌측 날개(Left Wing)<br>($X: 100.8\sim113.9, Y: 107.5\sim123.2$) | 1×5 수평 소켓 ($Y=109.5$) | • Beetle C6 UART 핀과 최단거리 수평 직결 (비아 0개)<br>• TX/RX 핀 크로스 완벽 적용 |
| **SHT45 온습도 (Qwiic)** | **$25.50 \times 17.80\,\text{mm}$** | **Bottom (후면)** 좌하단<br>($X: 100.5\sim126.0, Y: 125.5\sim143.3$) | 1×5 수평 소켓 ($Y=127.5$) | • I2C SDA/SCL 수평 고속도로와 직결<br>• 하단 M3 나사 패드와 간섭 없는 안전 간격 확보 |
| **GY-521 IMU (MPU6050)** | **$20.70 \times 15.65\,\text{mm}$** | **Bottom (후면)** 우하단<br>($X: 128.5\sim149.2, Y: 125.5\sim141.15$) | 1×8 수평 소켓 ($Y=127.5$) | • SHT45와 $2.50\,\text{mm}$ 공극 확보<br>• Pin 2(AD0) 접지 직결, Pin 8(VCC) 3.3V 공급 |
| **JST-PH 2.0 & SW1** | JST: $6.0 \times 4.5$<br>SW1: $7.0 \times 4.0$ | **Top (전면)** 하단 중앙<br>($Y: 144.5\sim149.0$) | JST 2P TH / SW1 SMD | • 배터리 전원 슬라이드 스위치 제어<br>• 후면 센서와 물리적 간섭 0mm |
| **M3 고정홀 4개소** | 드릴 $\varnothing 3.2$, 패드 $\varnothing 5.0$ | 4개 모서리 ($3.5\,\text{mm}$ 인입) | 기계식 홀 | • 패드 접지(GND) 결선, 모서리 2mm 45도 챔퍼 가공 |

---

## 3. 전체 핀 매핑 테이블

### 1) Beetle ESP32-C6 개발보드
- **좌측 소켓 (`J_MCU_L`, X=116.11mm)**:
  - Pin 1 (`Y=102.66`): **GND**
  - Pin 2 (`Y=105.20`): **3V3** (캐리어보드 전체 3.3V 전원 공급원)
  - Pin 3~8 (`Y=107.74~120.44`): NC (ESP32 IO4~IO7)
- **우측 소켓 (`J_MCU_R`, X=133.89mm)**:
  - Pin 1 (`Y=102.66`): **BAT** (SW1 스위치 출력 $\leftarrow$ 배터리+)
  - Pin 2 (`Y=105.20`): **GND**
  - Pin 3 (`Y=107.74`): NC (VIN)
  - Pin 4 (`Y=110.28`): **GPS_RX** (ESP32 GPIO17 $\leftarrow$ GPS TX Pin 3)
  - Pin 5 (`Y=112.82`): **GPS_TX** (ESP32 GPIO16 $\rightarrow$ GPS RX Pin 4)
  - Pin 6 (`Y=115.36`): **I2C_SDA** (ESP32 GPIO19 $\leftrightarrow$ 모든 I2C 센서 SDA)
  - Pin 7 (`Y=117.90`): **I2C_SCL** (ESP32 GPIO20 $\rightarrow$ 모든 I2C 센서 SCL)
  - Pin 8 (`Y=120.44`): NC (IO6)

### 2) 센서 모듈 소켓 (왼쪽 핀 $\rightarrow$ 오른쪽 핀 순서)
| 모듈명 | 실장면 | 소켓 규격 | 핀 순서 (왼쪽 1번 $\rightarrow$ 끝번) | 기능 및 결선 상태 | I2C 주소 / Baud |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **BH1750 (GY-302)** | Top | 1×05 가로 | `1: ADDR, 2: SDA, 3: SCL, 4: GND, 5: VCC` | ADDR=GND, SDA=GPIO19, SCL=GPIO20, GND, VCC=3.3V | `0x23` |
| **GPS (ATGM336H)** | Bottom | 1×05 가로 | `1: 3V3, 2: GND, 3: TXD, 4: RXD, 5: NC` | 3V3, GND, TXD$\rightarrow$GPIO17(RX), RXD$\leftarrow$GPIO16(TX) | 9600 bps |
| **SHT45 (Qwiic)** | Bottom | 1×05 가로 | `1: SDA, 2: SCL, 3: GND, 4: 3.3V, 5: VIN` | SDA=GPIO19, SCL=GPIO20, GND, 3.3V & VIN 병렬 공급 | `0x44` |
| **GY-521 (IMU)** | Bottom | 1×08 가로 | `1: INT, 2: AD0, 3: XCL, 4: XDA, 5: SDA, 6: SCL, 7: GND, 8: VCC` | AD0=GND, SDA=GPIO19, SCL=GPIO20, GND, VCC=3.3V | `0x68` |

---

## 4. PCB 제조 발주 사양 (JLCPCB 기준)
- **압축 거버 파일**: `Gerber_CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText.zip`
- **외형 치수**: `50.0mm × 50.0mm` (모서리 2mm 45도 챔퍼)
- **레이어**: `2 Layers (FR-4)`
- **두께**: `1.6mm`
- **동박 두께**: `1 oz`
- **솔더마스크 색상**: `Matte Black` (또는 Green)
- **실크스크린**: `White` (NoText 미니멀 아웃라인)
- **DRC 검증**: KiCad 10.0 DRC 완벽 통과 (**Critical Errors: 0, Unconnected Items: 0**)
