# 50mm × 50mm Beetle ESP32-C6 양면 소켓형 캐리어 PCB (Carrier Board)

본 프로젝트는 **DFRobot Beetle ESP32-C6 Mini**를 메인 MCU로 사용하고, 완제품 센서 브레이크아웃 모듈들(GY-521, SHT45, BH1750, GPS)을 암형 핀헤더 소켓으로 탈부착할 수 있도록 설계된 **50×50mm 양면 실장 캐리어 보드**입니다.

기존 칩(SMT) 직접 실장용 Gerber는 안전하게 보존되어 있으며, 본 폴더는 완제품 모듈을 꽂아 쓰는 프로토타입/실험 전용 설계입니다.

---

## 📁 파일 구성 안내

| 파일명 | 설명 | 용도 |
| :--- | :--- | :--- |
| **`Gerber_CarrierBoard_BeetleC6_50x50.zip`** | **JLCPCB 발주용 최종 Gerber 압축 파일** | PCB 제조사에 바로 업로드하여 주문 |
| **`CarrierBoard_BeetleC6_50x50.kicad_pcb`** | KiCad PCB 레이아웃 및 2층 배선 파일 | KiCad에서 PCB 보기 및 수정용 |
| **`CarrierBoard_BeetleC6_50x50.kicad_sch`** | KiCad 회로도 (Schematic) 파일 | 회로 결선 및 핀 매핑 검증용 |
| **`CarrierBoard_BeetleC6_50x50.kicad_pro`** | KiCad 프로젝트 설정 파일 | KiCad 7/8/10 연동 |
| **`BOM_CarrierBoard_BeetleC6_50x50.csv`** | 소켓 핀헤더 및 수동소자 자재 명세서 | 부품 구매 및 조립 목록 |

---

## 📐 물리적 배치 및 양면(Dual-Side) 소켓 구조

50×50mm 초소형 기판 크기 내에서 모듈 간 물리적 충돌(간섭)을 100% 방지하기 위해 **Top(전면)**과 **Bottom(후면)**으로 소켓을 분리 배치했습니다.

```
                  [ 50mm x 50mm 기판 구조 ]

        ▲ Top 면 (전면)                      ▼ Bottom 면 (후면)
+-------------------------------+   +-------------------------------+
| (H1)                     (H2) |   | (H1)                     (H2) |
|           [USB-C]             |   |                               |
|        +------------+         |   |                               |
| [SHT45]| Beetle C6  | [PWR SW]|   |                +------------+ |
| (5핀)  |   소켓     | [JST-PH]|   |                |   GY-521   | |
|        | (1x8 2열)  | (3.7V)  |   |                |  (MPU6050) | |
| [BH1750]              R1,R2   |   |                |  (8핀 소켓)| |
| (5핀)  +------------+ (ADC분압|   |                +------------+ |
|                               |   |     [GPS 모듈 소켓 (5핀)]    |
| (H3)                     (H4) |   | (H3)                     (H4) |
+-------------------------------+   +-------------------------------+
```

### 1. Top 면 (전면 실장 부품)
1. **DFRobot Beetle ESP32-C6 Mini 소켓 (`J_MCU_L`, `J_MCU_R`)**:
   - 2.54mm 1×8 Female Header 2열 (열 간격 17.78mm)
   - 상단 모서리에 USB-C 포트가 오도록 배치되어 **장착 상태에서 바로 충전 케이블 연결 가능**
2. **SHT45 온습도 센서 모듈 소켓 (`J_SHT45`)**:
   - 1×5 Female Header (`3V3 - GND - SCL - SDA - ALR`)
   - 전면에 배치되어 외부 공기와의 접촉 및 온도/습도 측정 최적화
3. **BH1750 조도 센서 모듈 소켓 (`J_BH1750`)**:
   - 1×5 Female Header (`3V3 - GND - SCL - SDA - ADDR`)
   - 전면에 배치되어 조도(빛) 감지 극대화
4. **전원부**:
   - `J1`: 3.7V LiPo 배터리용 JST-PH 2.0mm 커넥터
   - `SW1`: 전원 ON/OFF 슬라이드 스위치 (PCM12)
   - `R1, R2`: 배터리 잔량 센싱용 100kΩ 전압 분배 저항 (0603)
   - `R3, R4`: I2C 풀업 저항 4.7kΩ (0603)
   - `C1`: 3.3V 디커플링 커패시터 10µF (0603)

### 2. Bottom 면 (후면 실장 부품)
1. **GY-521 (MPU6050) 가속도/자이로 센서 모듈 소켓 (`J_GY521`)**:
   - 1×8 Female Header (`VCC - GND - SCL - SDA - XDA - XCL - AD0 - INT`)
   - 후면에 배치되어 전면의 센서/MCU와 수평 간섭 0%
2. **GPS 모듈 소켓 (`J_GPS`)**:
   - 1×5 Female Header (`3V3 - GPS_TX - GPS_RX - GND - PPS`)
   - 하단 후면에 배치되어 안테나 배선 간섭 최소화

---

## ⚡ 배터리 충전 및 실시간 잔량 모니터링

### 1. Beetle C6 자체 충전 회로 활용
- **외부 충전 모듈 불필요**: Beetle C6 보드에 이미 3.7V 리튬 배터리 충전 관리 IC가 내장되어 있습니다.
- 기판의 JST-PH 소켓에 배터리를 꽂아두고, **Beetle C6의 USB-C 포트에 케이블을 꽂으면 최대 0.5A로 자동 충전**됩니다.

### 2. 배터리 전압 및 잔량(%) 읽기 펌웨어 코드 예시
기판의 100kΩ : 100kΩ 분압 회로를 통해 배터리 전압이 1/2로 감압되어 **GPIO 4 (`BAT_ADC`)**로 입력됩니다.

```cpp
#define PIN_BAT_ADC 4

float readBatteryVoltage() {
  // ESP32 ADC는 0~3.3V (12bit: 0~4095)
  // 1/2 전압 분배이므로 실제 전압은 읽은 전압 x 2
  int raw = analogRead(PIN_BAT_ADC);
  float pinVoltage = (raw / 4095.0f) * 3.3f;
  float batteryVoltage = pinVoltage * 2.0f; // 분압비 보정
  return batteryVoltage;
}

int getBatteryPercentage(float v) {
  // 3.0V = 0%, 4.2V = 100% 선형 근사
  if (v >= 4.2f) return 100;
  if (v <= 3.0f) return 0;
  return (int)((v - 3.0f) / (4.2f - 3.0f) * 100.0f);
}
```

---

## 🏭 JLCPCB 1분 발주 방법

1. **[JLCPCB 웹사이트](https://jlcpcb.com/)**에 접속하여 로그인합니다.
2. 메인 화면의 **"Add Gerber file"** 버튼을 클릭하고, **`Gerber_CarrierBoard_BeetleC6_50x50.zip`** 파일을 업로드합니다.
3. 기판 치수가 **50mm × 50mm**, **2 Layers**로 자동 인식됩니다.
4. 추천 주문 옵션:
   - **PCB Qty**: 5장 (기본)
   - **PCB Thickness**: 1.6mm
   - **PCB Color**: Green, Matte Black, Blue 등 자유 선택
   - **Surface Finish**: HASL with lead (가장 저렴) 또는 LeadFree HASL
5. 견적 확인(기본 약 $2) 후 결제 및 주문을 완료합니다.
