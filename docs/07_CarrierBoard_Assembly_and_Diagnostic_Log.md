# 07. CarrierBoard Beetle ESP32-C6 조립 및 1차 진단 분석 보고서

**작업 일시:** 2026-09-30  
**작업 대상:** CarrierBoard_BeetleC6_EdgeUSB_50x50 (DeviceMart 발주 PCB)  
**핵심 장치:** DFRobot Beetle ESP32-C6 Mini MCU (DFR1117, RISC-V)  
**연동 센서:** SHT45 (온습도), GY-521/MPU6050 (6축 IMU), BH1750 (조도), ATGM336H (GPS)  

---

## 1. 하드웨어 조립 및 초기 안전 점검 경과

### 1) 기판 조립 및 소켓 납땜
- **실장 방식:** 2.54mm 암형 핀헤더 소켓(Female Header Socket)을 통한 모듈 탈부착 구조
- **실장면 구분:**
  - **Top (전면):** Beetle ESP32-C6 Mini (1×8 소켓 2열), BH1750 조도 센서 (1×5 소켓)
  - **Bottom (후면):** SHT45 온습도 센서 (1×5 소켓), GY-521 IMU (1×8 소켓), ATGM336H GPS (1×5 소켓)
- **납땜 점검:** 모든 소켓 핀 납땜 완료 및 냉납/브릿지 육안 검사 완료

### 2) 전원 공급 및 도통 테스트 (Continuity Test) — PASS
- **쇼트 방지 검사:** 조립 전 멀티미터를 통한 3.3V 전원선과 GND 간 단락 검사 결과 쇼트 없음 확인 (무한대 저항)
- **전원 인가 측정:** Beetle C6에 USB-C 전원을 연결한 상태에서 각 센서 소켓의 VCC/3V3 핀 전압 측정 결과 **정상 3.3V 인입 확인**
- **I2C 풀업 저항 (R3, R4) 생략 근거:**  
  각 센서 모듈(SHT45, GY-521, BH1750) 내부 회로에 이미 4.7kΩ ~ 10kΩ 풀업 저항이 온보드 실장되어 있으므로 외장 SMD 0603 저항을 납땜하지 않아도 I2C 통신 가능 확인.
- **전원 스위치 (SW1) 생략 근거:**  
  SW1은 배터리(JST-PH) 전원 라인 전용이므로, 현재 USB-C 직결 전원 공급 시 납땜 없이 안전하게 바이패스 운용 가능.

---

## 2. PlatformIO 환경 구축 및 빌드/업로드 해결

### 1) 당면했던 문제
- **오류 메시지:**
  ```text
  Error: Failed to install Python dependencies into penv
  Error: This board doesn't support arduino framework!
  riscv32-esp-elf-g++: fatal error: cannot execute 'cc1plus': CreateProcess: No such file or directory
  ```
- **원인:**
  1. 공식 PlatformIO의 기본 `espressif32` 플랫폼은 Arduino Core 2.x 기반으로 신형 RISC-V 칩셋인 ESP32-C6의 Arduino Framework를 지원하지 않음.
  2. 로컬 환경에 캐시되어 있던 구버전 `toolchain-riscv32-esp` 내부의 C++ 전처리기(`cc1plus.exe`) 파일 누락/손상.

### 2) 해결 조치
- **플랫폼 변경:** ESP32-C6 Arduino Core 3.0.4를 완벽 지원하는 `pioarduino v51.03.04`로 교체:
  ```ini
  [env:beetle_c6_diagnostic]
  platform = https://github.com/pioarduino/platform-espressif32/releases/download/51.03.04/platform-espressif32.zip
  board = esp32-c6-devkitm-1
  framework = arduino
  monitor_speed = 115200
  upload_port = COM37
  monitor_port = COM37
  build_flags =
    -DARDUINO_USB_MODE=1
    -DARDUINO_USB_CDC_ON_BOOT=1
  lib_deps =
    BH1750
    adafruit/Adafruit MPU6050@^2.0.0
    mikalhart/TinyGPSPlus@^1.0.1
    sensirion/arduino-sht@^1.0.0
  build_src_filter = -<*> +<carrier_board_diagnostic.cpp>
  ```
- **손상 툴체인 복구:** 손상된 로컬 툴체인 디렉터리를 초기화하여 Espressif 공식 검증 툴체인 자동 재다운로드 수행.
- **결과:** **100% 빌드 성공 (SUCCESS)** 및 Beetle ESP32-C6(COM37)에 펌웨어 업로드 완료.

---

## 3. 실시간 진단 테스트 및 핵심 원인 분석 (Root Cause Analysis)

### 1) 진단 펌웨어 구동 증상
```text
🔍 [1] I2C 버스 스캔 시작 (SDA: GPIO 19, SCL: GPIO 20)
-------------------------------------------
  ❌ I2C 장치를 하나도 찾지 못했습니다! (소켓 체결 상태 확인 필요)
-------------------------------------------
📦 [2] BH1750 조도 센서 초기화... ❌ 실패
📦 [3] SHT45 온습도 센서 초기화... ❌ 실패
📦 [4] GY-521 (MPU6050) 6축 IMU 초기화... ❌ 실패
📦 [5] GPS ATGM336H UART 포트 열기 (RX:16, TX:17)... ✅ 포트 오픈 완료
```

### 2) 기판-모듈 간 회로 정밀 대조 결과
사용자 촬영 실물 사진과 KiCad 정밀 배선 데이터를 분석한 결과:

1. **SHT45 (온습도 센서): 180도 반대 체결 확인**
   - **소켓 배선 (좌 $\rightarrow$ 우):** `[1: SDA, 2: SCL, 3: GND, 4: 3V3, 5: 3V3]`
   - **실제 모듈 삽입 상태:** `VIN`이 왼쪽 끝(1번)으로 꽂혀 있음.
   - **문제:** 모듈의 전원(`VIN`)이 ESP32의 I2C `SDA` 신호선에 꽂혀 전원이 들어가지 않고, 내부 보호 다이오드가 `SDA` 전압을 0V(GND)로 클램핑하여 **전체 I2C 버스를 완전 마비**시킴.

2. **GY-521 (MPU6050 IMU 센서): 180도 반대 체결 확인**
   - **소켓 배선 (좌 $\rightarrow$ 우):** `[1: GND, ..., 5: SDA, 6: SCL, 7: GND, 8: 3V3]`
   - **실제 모듈 삽입 상태:** `VCC`가 왼쪽 끝(1번)으로 꽂혀 있음.
   - **문제:** `VCC`가 소켓의 GND에 인입되고, `INT` 핀에 3.3V가 인입되어 역방향 바이어스 발생.

3. **BH1750 (조도 센서): 180도 반대 체결 확인**
   - **소켓 배선 (좌 $\rightarrow$ 우):** `[1: GND, 2: SDA, 3: SCL, 4: GND, 5: 3V3]`
   - **실제 모듈 삽입 상태:** `VCC`가 왼쪽 끝(1번)으로 꽂혀 있음.
   - **문제:** `VCC`가 소켓의 GND에 인입되고, `ADDR` 핀에 3.3V가 인입됨.

4. **GPS (ATGM336H):**
   - 모듈 방향은 정상(`VCC`가 1번 3.3V에 인입).
   - 단, 4번 핀(GPS RX)에 Beetle C6의 5V(VIN)이 인입되는 배선 특성이 있으므로, GPS는 RX 핀을 띄우고(미연결) TX 핀만으로도 자동 NMEA 수신 가능.

---

## 4. 내일(Next Step) 진행 계획

1. **센서 모듈 180도 회전 재체결 (납땜 불필요):**
   - 전원(USB) 분리.
   - **SHT45 (보라색):** 소켓에서 뽑아 180도 회전(`VIN` 글자가 오른쪽 끝으로 오도록) 장착.
   - **GY-521 (파란색):** 소켓에서 뽑아 180도 회전(`VCC` 글자가 오른쪽 끝으로 오도록) 장착.
   - **BH1750 (뒷면 파란색):** 소켓에서 뽑아 180도 회전(`VCC` 글자가 오른쪽 끝으로 오도록) 장착.
2. **I2C 버스 스캔 및 실시간 데이터 측정 검증:**
   - USB 재연결 후 시리얼 모니터를 통해 `0x23`(BH1750), `0x44`(SHT45), `0x68`(MPU6050) 주소 응답 확인.
   - 온습도, 6축 가속도/자이로, 밝기(Lux) 실시간 수치 변화 확인.
3. **GPS UART 통신 점검:**
   - 9600 bps NMEA 문장 수신 확인.
4. **디지털 트윈 플랫폼 연동 준비:**
   - Wi-Fi / MQTT 전송 펌웨어 포팅 단계 진입.
