# ESP32 Sensor Examples

이 폴더는 ESP32(PlatformIO)에서 테스트할 수 있는 예시 스케치를 포함합니다.

파일 목록:
- `src/sht45_example.ino` — SHT45 (Sensirion SHT4x) 예시
- `src/bh1750_example.ino` — BH1750 조도 센서 예시
- `src/mpu6050_example.ino` — GY-521 (MPU6050) 예시
- `src/neo6m_example.ino` — NEO-6M GPS 예시

빌드/업로드 (PlatformIO):
```bash
cd code26/test
pio run -e esp32dev -t upload
pio device monitor -b 115200
```

라이브러리
- BH1750
- Adafruit MPU6050
- TinyGPSPlus
- Sensirion SHT4x (SHT45 사용 시)

배선 예시
- I2C 센서 (SHT45, BH1750, MPU6050): SDA -> GPIO21, SCL -> GPIO22, GND, VCC(3.3V)
- NEO-6M: TX -> ESP32 GPIO16 (RX2), RX -> ESP32 GPIO17 (TX2), GND, VCC

참고: 일부 예제는 특정 라이브러리 API를 사용합니다. 라이브러리 이름이 플랫폼/레지스트리와 다를 경우 README의 라이브러리 이름으로 검색해 설치하세요.
