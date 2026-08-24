#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_AHTX0.h>
#include <BH1750.h>
#include <TinyGPS++.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include "secrets.h"
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <sys/time.h>
#include <FS.h>
#include <LittleFS.h>

// -----------------------------------------
// 1. 와이파이 및 MQTT 설정
// -----------------------------------------
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const char* mqtt_topic = "coldchain/truck01/sensor";

// -----------------------------------------
// 저전력 및 샘플링 튜닝 매크로
// -----------------------------------------
#define TX_INTERVAL_MS 60000          // 일반 센서 데이터 전송 주기 (1분)
#define SAMPLE_INTERVAL_MS 20         // 가속도 센서 고속 풀링 주기 (20ms = 50Hz)
#define SHOCK_THRESHOLD_G 1.8         // 심각한 충격(박스 손상/포트홀) 감지 임계값 (G)
#define SHOCK_DEBOUNCE_MS 3000        // 충격 이벤트 연속 발생 차단 시간 (3초 데드타임)

// -----------------------------------------
// 객체 및 핀 설정 (AHT10 / AHT20 센서 전용)
// -----------------------------------------
Adafruit_MPU6050 mpu;
Adafruit_AHTX0 aht;
BH1750 lightMeter;
TinyGPSPlus gps;

// ESP32-C3/S3 GPS용 Serial1 (RX: GPIO 20, TX: GPIO 21)
#define GPS_SERIAL Serial1

WiFiMulti wifiMulti;
WiFiClient espClient;
PubSubClient client(espClient);

// 오프라인 저장 설정 및 상태 추적 변수
const char* offline_file = "/offline.jsonl";
unsigned long lastReconnectAttempt = 0;
bool wasConnected = false;
bool checkOfflineData = false;

// 피크 홀드 및 타이밍 추적 변수
float max_g_force = 1.0;              // 중력이 있는 상태에서는 기본 1G
unsigned long lastTxTime = 0;
unsigned long lastSampleTime = 0;
unsigned long lastShockTime = 0;

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to WiFi...");
  
  WiFi.mode(WIFI_STA);
  WiFi.setTxPower(WIFI_POWER_11dBm);
  
  for (int i = 0; i < num_wifi_networks; i++) {
    wifiMulti.addAP(wifi_networks[i].ssid, wifi_networks[i].password);
  }

  while (wifiMulti.run() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected!");
  Serial.print("Connected SSID: ");
  Serial.println(WiFi.SSID());
}

bool reconnectNonBlocking() {
  if (!client.connected()) {
    unsigned long now = millis();
    if (now - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = now;
      Serial.print("Attempting MQTT connection (non-blocking)...");
      String clientId = "ESP32C3-AHT-";
      clientId += String(random(0xffff), HEX);
      if (client.connect(clientId.c_str())) {
        Serial.println("connected!");
        return true;
      } else {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        Serial.println(" try again in 5 seconds");
      }
    }
    return false;
  }
  return true;
}

void sendOfflineData() {
  if (!LittleFS.exists(offline_file)) return;

  File file = LittleFS.open(offline_file, FILE_READ);
  if (!file) {
    Serial.println("Failed to open offline file for reading");
    return;
  }

  Serial.println("📡 Found offline data. Publishing to MQTT...");

  File tempFile;
  bool useTemp = false;
  int sentCount = 0;
  int failCount = 0;

  while (file.available()) {
    String line = file.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) continue;

    bool published = false;
    if (client.connected() && failCount == 0) {
      if (client.publish(mqtt_topic, line.c_str())) {
        published = true;
        sentCount++;
        delay(50);
      } else {
        Serial.println("❌ Failed to publish offline record, buffering remaining...");
        failCount++;
      }
    }

    if (!published) {
      if (!useTemp) {
        tempFile = LittleFS.open("/temp.jsonl", FILE_WRITE);
        useTemp = true;
      }
      if (tempFile) {
        tempFile.println(line);
      }
    }
  }

  file.close();
  if (useTemp) {
    tempFile.close();
  }

  LittleFS.remove(offline_file);
  if (useTemp) {
    if (LittleFS.rename("/temp.jsonl", offline_file)) {
      Serial.println("Updated offline buffer with unsent records.");
    } else {
      Serial.println("Error updating offline buffer!");
    }
  }

  if (sentCount > 0) {
    Serial.printf("✅ Sent %d offline records.\n", sentCount);
  }
}

void setup() {
  Serial.begin(115200);
  
  // GPS 초기화 (RX: GPIO 20, TX: GPIO 21)
  GPS_SERIAL.begin(9600, SERIAL_8N1, 20, 21);
  
  // I2C 초기화 (SDA: GPIO 8, SCL: GPIO 9)
  Wire.begin(8, 9); 

  // 1. MPU6050 초기화
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  // 2. AHT10 / AHT20 온습도 센서 초기화
  if (!aht.begin()) {
    Serial.println("❌ Could not find AHT10/AHT20 sensor! Check I2C wiring (SDA=8, SCL=9, addr 0x38)");
  } else {
    Serial.println("✅ AHT10/AHT20 Temp & Humidity Sensor initialized!");
  }

  // 3. BH1750 조도 센서 초기화
  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("Error initialising BH1750");
  }

  // 4. LittleFS 초기화
  if (!LittleFS.begin(true)) {
    Serial.println("An Error has occurred while mounting LittleFS");
  } else {
    Serial.println("LittleFS mounted successfully!");
  }

  setup_wifi();
  
  // 한국 시간(KST, GMT+9) 설정
  configTime(9 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("⏰ NTP Time Syncing...");

  client.setServer(mqtt_server, mqtt_port);

  // 전송 타이머 초기화
  unsigned long now = millis();
  lastTxTime = now;
  lastSampleTime = now;
}

// UTC tm 구조체를 Unix Epoch 초로 계산
time_t customTimegm(struct tm *t) {
  int year = t->tm_year + 1900;
  int month = t->tm_mon + 1;
  int day = t->tm_mday;
  int hour = t->tm_hour;
  int min = t->tm_min;
  int sec = t->tm_sec;

  static const int days_before_month[] = {
    0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
  };

  long days = (year - 1970) * 365 + (year - 1969) / 4 - (year - 1901) / 100 + (year - 1601) / 400;
  days += days_before_month[month - 1];
  days += day - 1;

  if (month > 2) {
    bool isLeap = (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0));
    if (isLeap) days++;
  }

  return (time_t)(((days * 24 + hour) * 60 + min) * 60 + sec);
}

// 데이터 계측 및 MQTT/LittleFS 전송 공통 함수
void transmitData(float g_force_val, String status_val) {
  // AHT10 / AHT20 온습도 측정
  sensors_event_t humidity, temp_evt;
  aht.getEvent(&humidity, &temp_evt);

  // BH1750 조도 측정
  float lux = lightMeter.readLightLevel();

  // KST 로컬 시간 정보 가져오기
  struct tm timeinfo;
  char timeStr[20] = "00:00:00";
  if (getLocalTime(&timeinfo, 10)) {
    strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);
  }

  // JSON 구성
  StaticJsonDocument<512> doc;
  doc["device"] = "gy521-aht";
  doc["timestamp_str"] = timeStr;
  doc["temperature"] = String(temp_evt.temperature, 2);
  doc["humidity"] = String(humidity.relative_humidity, 2);
  doc["lux"] = String(lux, 1);
  doc["g_force"] = String(g_force_val, 2);
  
  if (gps.location.isValid()) {
    doc["lat"] = String(gps.location.lat(), 6);
    doc["lng"] = String(gps.location.lng(), 6);
    doc["speed"] = String(gps.speed.kmph(), 1);
  } else {
    doc["lat"] = "0.0";
    doc["lng"] = "0.0";
  }
  
  doc["status"] = status_val;

  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);
  Serial.print("📡 Transmission: ");
  Serial.println(jsonBuffer);

  bool currentConnected = client.connected();
  if (currentConnected) {
    client.publish(mqtt_topic, jsonBuffer);
  } else {
    File file;
    if (LittleFS.exists(offline_file)) {
      file = LittleFS.open(offline_file, FILE_APPEND);
    } else {
      file = LittleFS.open(offline_file, FILE_WRITE);
    }

    if (file) {
      if (file.size() < 1000000) {
        file.println(jsonBuffer);
        Serial.println("💾 Saved data to LittleFS (Offline mode)");
      } else {
        Serial.println("⚠️ LittleFS buffer full!");
      }
      file.close();
    }
  }
}

void loop() {
  bool currentConnected = client.connected();

  if (wifiMulti.run() == WL_CONNECTED) {
    if (!currentConnected) {
      currentConnected = reconnectNonBlocking();
    }
  }

  if (currentConnected) {
    client.loop();
  }

  if (currentConnected && !wasConnected) {
    checkOfflineData = true;
  }
  wasConnected = currentConnected;

  if (currentConnected && checkOfflineData) {
    checkOfflineData = false;
    sendOfflineData();
  }

  while (GPS_SERIAL.available() > 0) {
    gps.encode(GPS_SERIAL.read());
  }

  unsigned long now = millis();

  // 1. 고속 가속도 샘플링 (50Hz)
  if (now - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = now;

    sensors_event_t a, g, temp_mpu;
    mpu.getEvent(&a, &g, &temp_mpu);
    
    float total_accel = sqrt(pow(a.acceleration.x, 2) + pow(a.acceleration.y, 2) + pow(a.acceleration.z, 2));
    float g_force = total_accel / 9.80665; 

    if (g_force > max_g_force) {
      max_g_force = g_force;
    }

    // 2. 실시간 임계값 초과 충격 이벤트 전송 (1.8G 이상)
    if (g_force >= SHOCK_THRESHOLD_G) {
      if (now - lastShockTime >= SHOCK_DEBOUNCE_MS) {
        lastShockTime = now;
        Serial.printf("⚠️ [SHOCK DETECTED] High G-Force event: %.2fg!\n", g_force);
        transmitData(g_force, "강한 충돌!!");
        max_g_force = 1.0; 
      }
    }
  }

  // 3. GPS 시각 동기화
  static unsigned long lastGpsSyncCheck = 0;
  if (now - lastGpsSyncCheck >= 1000) {
    lastGpsSyncCheck = now;

    if (gps.date.isValid() && gps.time.isValid() && gps.date.year() > 2020) {
      time_t now_time = time(NULL);
      struct tm *now_tm = localtime(&now_time);
      if (now_tm->tm_year < 120) {
        struct tm gpsTimeinfo = {0};
        gpsTimeinfo.tm_year = gps.date.year() - 1900;
        gpsTimeinfo.tm_mon = gps.date.month() - 1;
        gpsTimeinfo.tm_mday = gps.date.day();
        gpsTimeinfo.tm_hour = gps.time.hour();
        gpsTimeinfo.tm_min = gps.time.minute();
        gpsTimeinfo.tm_sec = gps.time.second();
        gpsTimeinfo.tm_isdst = 0;

        time_t utcEpoch = customTimegm(&gpsTimeinfo);
        if (utcEpoch != -1) {
          struct timeval tv = { .tv_sec = utcEpoch, .tv_usec = 0 };
          settimeofday(&tv, NULL);
          Serial.println("⏰ System time synced with GPS UTC!");
        }
      }
    }
  }

  // 4. 일반 데이터 주기적 전송 (1분 간격)
  if (now - lastTxTime >= TX_INTERVAL_MS) {
    lastTxTime = now;

    String status = "안전";
    if (max_g_force > SHOCK_THRESHOLD_G) {
      status = "강한 충돌!!";
    } else if (max_g_force > 1.3 || max_g_force < 0.7) {
      status = "이동/진동";
    }

    transmitData(max_g_force, status);
    max_g_force = 1.0; 
  }
}
