#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <BH1750.h>
#include <SHTSensor.h>
#include <TinyGPSPlus.h>

// ==========================================
// 1. 하드웨어 핀 정의 (CarrierBoard Beetle ESP32-C6)
// ==========================================
#define I2C_SDA_PIN   19
#define I2C_SCL_PIN   20

#define GPS_RX_PIN    16  // ESP32 RX <- GPS TXD
#define GPS_TX_PIN    17  // ESP32 TX -> GPS RXD
#define GPS_BAUDRATE  9600

// ==========================================
// 2. 센서 객체 생성
// ==========================================
Adafruit_MPU6050 mpu;
BH1750 lightMeter;
SHTSensor sht(SHTSensor::SHT4X);
TinyGPSPlus gps;

bool mpu_ready = false;
bool bh1750_ready = false;
bool sht45_ready = false;
unsigned long gps_chars_received = 0;

// ==========================================
// 3. I2C 버스 스캐너
// ==========================================
void scan_i2c_bus() {
  Serial.println("\n-------------------------------------------");
  Serial.println("🔍 [1] I2C 버스 스캔 시작 (SDA: GPIO 19, SCL: GPIO 20)");
  Serial.println("-------------------------------------------");
  byte count = 0;
  
  for (byte address = 1; address < 127; ++address) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    
    if (error == 0) {
      Serial.print("  -> 장치 발견! 주소: 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      
      if (address == 0x23) {
        Serial.println("  [★ BH1750 조도 센서 확인]");
      } else if (address == 0x44) {
        Serial.println("  [★ SHT45 온습도 센서 확인]");
      } else if (address == 0x68) {
        Serial.println("  [★ GY-521 (MPU6050) IMU 센서 확인]");
      } else {
        Serial.println("  [기타 I2C 장치]");
      }
      count++;
    }
  }
  
  if (count == 0) {
    Serial.println("  ❌ I2C 장치를 하나도 찾지 못했습니다! (소켓 체결 상태 확인 필요)");
  } else {
    Serial.printf("  총 %d개의 I2C 센서가 정상 응답했습니다.\n", count);
  }
  Serial.println("-------------------------------------------\n");
}

void setup() {
  Serial.begin(115200);
  delay(1500); // USB CDC 시리얼 안정화 대기
  
  Serial.println("\n=======================================================");
  Serial.println(" ColdChain DigitalTwin Carrier Board 종합 진단 테스트 ");
  Serial.println(" MCU: DFRobot Beetle ESP32-C6 Mini ");
  Serial.println("=======================================================\n");

  // I2C 초기화 (SDA=19, SCL=20)
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(100000); // 100kHz 표준 모드

  // 1. I2C 주소 스캔
  scan_i2c_bus();

  // 2. BH1750 조도 센서 초기화
  Serial.print("📦 [2] BH1750 조도 센서 초기화... ");
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    bh1750_ready = true;
    Serial.println("✅ 성공 (정상 작동)");
  } else {
    Serial.println("❌ 실패 (연결 또는 주소 확인 필요)");
  }

  // 3. SHT45 온습도 센서 초기화
  Serial.print("📦 [3] SHT45 온습도 센서 초기화... ");
  if (sht.init()) {
    sht.setAccuracy(SHTSensor::SHT_ACCURACY_HIGH);
    sht45_ready = true;
    Serial.println("✅ 성공 (정상 작동)");
  } else {
    Serial.println("❌ 실패 (연결 확인 필요)");
  }

  // 4. MPU6050 IMU 초기화
  Serial.print("📦 [4] GY-521 (MPU6050) 6축 IMU 초기화... ");
  if (mpu.begin()) {
    mpu_ready = true;
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("✅ 성공 (정상 작동)");
  } else {
    Serial.println("❌ 실패 (연결 확인 필요)");
  }

  // 5. GPS UART 초기화
  Serial.print("📦 [5] GPS ATGM336H UART 포트 열기 (RX:16, TX:17)... ");
  Serial1.begin(GPS_BAUDRATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  Serial.println("✅ 포트 오픈 완료");

  Serial.println("\n🚀 모든 센서 초기화 완료. 1초마다 실시간 측정값을 출력합니다...\n");
}

unsigned long last_print = 0;

void loop() {
  // GPS NMEA 데이터 백그라운드 수신
  while (Serial1.available() > 0) {
    char c = Serial1.read();
    gps.encode(c);
    gps_chars_received++;
  }

  // 1초 주기로 센서 데이터 출력
  unsigned long now = millis();
  if (now - last_print >= 1000) {
    last_print = now;

    Serial.println("------------------------------------------------------------------");
    Serial.printf("[⏱ 경과 시간: %lu 초]\n", now / 1000);

    // [1] SHT45 온습도
    if (sht45_ready && sht.readSample()) {
      Serial.printf("  🌡️  [온습도 SHT45]   온도: %5.1f °C  |  습도: %5.1f %%\n",
                    sht.getTemperature(), sht.getHumidity());
    } else {
      Serial.println("  🌡️  [온습도 SHT45]   데이터 읽기 실패 또는 미연결");
    }

    // [2] BH1750 조도
    if (bh1750_ready) {
      float lux = lightMeter.readLightLevel();
      Serial.printf("  💡 [조도 BH1750]     밝기: %6.1f Lux\n", lux);
    } else {
      Serial.println("  💡 [조도 BH1750]     데이터 읽기 실패 또는 미연결");
    }

    // [3] MPU6050 가속도/자이로
    if (mpu_ready) {
      sensors_event_t a, g, temp;
      mpu.getEvent(&a, &g, &temp);
      float g_total = sqrt(pow(a.acceleration.x, 2) + pow(a.acceleration.y, 2) + pow(a.acceleration.z, 2)) / 9.80665;
      Serial.printf("  🧭 [IMU MPU6050]     합성 가속도: %4.2f G (X:%4.1f, Y:%4.1f, Z:%4.1f)\n",
                    g_total, a.acceleration.x, a.acceleration.y, a.acceleration.z);
    } else {
      Serial.println("  🧭 [IMU MPU6050]     데이터 읽기 실패 또는 미연결");
    }

    // [4] GPS 통신 상태 (실내 위성 미수신 고려)
    if (gps_chars_received > 0) {
      if (gps.location.isValid()) {
        Serial.printf("  🛰️  [GPS ATGM336H]   위치 고정 성공! 위도: %f, 경도: %f (위성: %d개)\n",
                      gps.location.lat(), gps.location.lng(), gps.satellites.value());
      } else {
        Serial.printf("  🛰️  [GPS ATGM336H]   UART 정상 수신 중 (NMEA 수신 바이트: %lu) - 🔍 실내 위성 탐색 중...\n",
                      gps_chars_received);
      }
    } else {
      Serial.println("  🛰️  [GPS ATGM336H]   ❌ UART 데이터 수신 없음 (TX/RX 배선 또는 통신속도 확인 필요)");
    }
  }
}
