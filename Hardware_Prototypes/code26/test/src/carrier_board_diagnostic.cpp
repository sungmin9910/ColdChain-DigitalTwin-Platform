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

#define GPS_RX_PIN    17  // ESP32 RX (GPIO 17) <- GPS TXD
#define GPS_TX_PIN    16  // ESP32 TX (GPIO 16) -> GPS RXD
#define GPS_BAUDRATE  9600

// 센서 객체
Adafruit_MPU6050 mpu;
BH1750 lightMeter;
SHTSensor sht(SHTSensor::SHT4X);
TinyGPSPlus gps;

bool mpu_ready = false;
bool bh1750_ready = false;
bool sht45_ready = false;
unsigned long gps_chars_received = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=======================================================");
  Serial.println("  ColdChain DigitalTwin Carrier Board 실시간 진단기   ");
  Serial.println("  MCU: DFRobot Beetle ESP32-C6 Mini                   ");
  Serial.println("=======================================================\n");

  // GPS 포트 열기
  Serial1.begin(GPS_BAUDRATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  // Wire 초기화
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(100000);
  Wire.setTimeOut(25); // I2C 버스 락 방지 타임아웃
}

unsigned long last_scan = 0;

void loop() {
  // GPS 백그라운드 수신
  while (Serial1.available() > 0) {
    char c = Serial1.read();
    gps.encode(c);
    gps_chars_received++;
  }

  unsigned long now = millis();
  if (now - last_scan >= 1000) {
    last_scan = now;

    // 1. GPIO 핀 전압 레벨 진단 (풀업 상태 확인)
    pinMode(I2C_SDA_PIN, INPUT_PULLUP);
    pinMode(I2C_SCL_PIN, INPUT_PULLUP);
    delayMicroseconds(50);
    int sda_lvl = digitalRead(I2C_SDA_PIN);
    int scl_lvl = digitalRead(I2C_SCL_PIN);

    // 다시 Wire 활성화
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    Wire.setTimeOut(25);

    Serial.println("------------------------------------------------------------------");
    Serial.printf("[실시간 진단 %lu초] SDA(GPIO 19): %s (%d) | SCL(GPIO 20): %s (%d)\n",
                  now / 1000,
                  sda_lvl ? "HIGH(정상)" : "LOW(쇼트/풀다운!)", sda_lvl,
                  scl_lvl ? "HIGH(정상)" : "LOW(쇼트/풀다운!)", scl_lvl);

    if (sda_lvl == 0 || scl_lvl == 0) {
      Serial.println("  ⚠️ I2C 버스 신호선이 0V로 접지(LOW)되어 있습니다.");
      Serial.println("     센서를 하나씩 소켓에서 뽑아보시면 어느 센서가 접지시키는지 바로 감지됩니다!");
    } else {
      // 2. I2C 버스 스캔
      Serial.print("  >> I2C 스캔 결과: ");
      int found = 0;
      bool found_bh = false, found_sht = false, found_mpu = false;

      for (byte addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        if (Wire.endTransmission() == 0) {
          Serial.printf("[0x%02X] ", addr);
          found++;
          if (addr == 0x23) found_bh = true;
          if (addr == 0x44) found_sht = true;
          if (addr == 0x68) found_mpu = true;
        }
      }

      if (found == 0) {
        Serial.println("장치 없음");
      } else {
        Serial.printf("(총 %d개 감지)\n", found);
      }

      // 센서 초기화 시도
      if (found_bh && !bh1750_ready) {
        if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) bh1750_ready = true;
      }
      if (found_sht && !sht45_ready) {
        if (sht.init()) {
          sht.setAccuracy(SHTSensor::SHT_ACCURACY_HIGH);
          sht45_ready = true;
        }
      }
      if (found_mpu && !mpu_ready) {
        if (mpu.begin()) {
          mpu_ready = true;
          mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
        }
      }

      // 3. 센서 실시간 측정값 출력
      if (sht45_ready && sht.readSample()) {
        Serial.printf("  [SHT45 온습도] 온도: %.1f C | 습도: %.1f %%\n",
                      sht.getTemperature(), sht.getHumidity());
      } else if (found_sht) {
        Serial.println("  [SHT45 온습도] 통신 연결됨 (샘플링 중...)");
      }

      if (bh1750_ready) {
        float lux = lightMeter.readLightLevel();
        Serial.printf("  [BH1750 조도]  밝기: %.1f Lux\n", lux);
      } else if (found_bh) {
        Serial.println("  [BH1750 조도]  통신 연결됨 (측정 중...)");
      }

      if (mpu_ready) {
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);
        float g_tot = sqrt(a.acceleration.x*a.acceleration.x + a.acceleration.y*a.acceleration.y + a.acceleration.z*a.acceleration.z) / 9.80665;
        Serial.printf("  [MPU6050 IMU] 합성 가속도: %.2f G (X:%.1f, Y:%.1f, Z:%.1f)\n",
                      g_tot, a.acceleration.x, a.acceleration.y, a.acceleration.z);
      } else if (found_mpu) {
        Serial.println("  [MPU6050 IMU]  통신 연결됨 (측정 중...)");
      }
    }

    // 4. GPS 상태 출력
    if (gps_chars_received > 0) {
      if (gps.location.isValid()) {
        Serial.printf("  [GPS] 위도: %f, 경도: %f (위성 %d개)\n",
                      gps.location.lat(), gps.location.lng(), gps.satellites.value());
      } else {
        Serial.printf("  [GPS] NMEA 수신 바이트: %lu (실내 위성 탐색 중...)\n", gps_chars_received);
      }
    } else {
      Serial.println("  [GPS] 수신 대기 중 (0 바이트)");
    }
  }
}
