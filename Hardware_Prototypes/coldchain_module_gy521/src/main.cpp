#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_SHT4x.h>
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
// 와이파이 설정은 secrets.h에서 다중으로 관리합니다.
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const char* mqtt_topic = "coldchain/truck01/sensor";

// -----------------------------------------
// 객체 및 핀 설정
// -----------------------------------------
Adafruit_MPU6050 mpu;
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
BH1750 lightMeter;
TinyGPSPlus gps;

// GPS는 Serial2 사용 (RX: 16, TX: 17)
#define GPS_SERIAL Serial2

WiFiMulti wifiMulti;
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;

// 오프라인 저장 설정 및 상태 추적 변수
const char* offline_file = "/offline.jsonl";
unsigned long lastReconnectAttempt = 0;
bool wasConnected = false;
bool checkOfflineData = false;

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to WiFi...");
  
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
      String clientId = "ESP32-GY521-";
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
        delay(50); // prevent network congestion
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
  GPS_SERIAL.begin(9600, SERIAL_8N1, 16, 17); // GPS 초기화
  
  Wire.begin(); 

  // 1. MPU6050 초기화
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  // 2. SHT4x 초기화
  if (!sht4.begin()) {
    Serial.println("Couldn't find SHT4x sensor");
  } else {
    sht4.setPrecision(SHT4X_HIGH_PRECISION);
    sht4.setHeater(SHT4X_NO_HEATER);
  }

  // 3. BH1750 초기화
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
}

void loop() {
  bool currentConnected = client.connected();

  // WiFi가 연결된 상태에서만 MQTT 재연결 시도 (비블로킹)
  if (wifiMulti.run() == WL_CONNECTED) {
    if (!currentConnected) {
      currentConnected = reconnectNonBlocking();
    }
  }

  if (currentConnected) {
    client.loop();
  }

  // 연결 상태가 오프라인에서 온라인으로 전환되었을 때 플러시 플래그 활성화
  if (currentConnected && !wasConnected) {
    checkOfflineData = true;
  }
  wasConnected = currentConnected;

  // 플래그가 활성화되면 저장된 오프라인 데이터 전송
  if (currentConnected && checkOfflineData) {
    checkOfflineData = false;
    sendOfflineData();
  }

  // GPS 데이터 파싱
  while (GPS_SERIAL.available() > 0) {
    gps.encode(GPS_SERIAL.read());
  }

  // 1초마다 데이터 센싱 및 전송
  unsigned long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;

    // GPS 데이터가 유효하고 시스템 시간이 아직 동기화되지 않은 경우, GPS 시간으로 시스템 시간 설정
    if (gps.date.isValid() && gps.time.isValid() && gps.date.year() > 2020) {
      time_t now_time = time(NULL);
      struct tm *now_tm = localtime(&now_time);
      if (now_tm->tm_year < 120) { // 시스템 시간이 2020년 이전인 경우 (미동기화 상태)
        struct tm gpsTimeinfo = {0};
        gpsTimeinfo.tm_year = gps.date.year() - 1900;
        gpsTimeinfo.tm_mon = gps.date.month() - 1;
        gpsTimeinfo.tm_mday = gps.date.day();
        gpsTimeinfo.tm_hour = gps.time.hour();
        gpsTimeinfo.tm_min = gps.time.minute();
        gpsTimeinfo.tm_sec = gps.time.second();
        gpsTimeinfo.tm_isdst = 0;

        time_t t_of_day = mktime(&gpsTimeinfo);
        if (t_of_day != -1) {
          t_of_day += 9 * 3600; // GMT+9 시간대 보정 (mktime의 현지 시간 기준 해석을 고려)
          struct timeval tv = { .tv_sec = t_of_day, .tv_usec = 0 };
          settimeofday(&tv, NULL);
          Serial.println("⏰ System time synced with GPS!");
        }
      }
    }

    // 가속도 및 충격량 계산
    sensors_event_t a, g, temp_mpu;
    mpu.getEvent(&a, &g, &temp_mpu);
    float total_accel = sqrt(pow(a.acceleration.x, 2) + pow(a.acceleration.y, 2) + pow(a.acceleration.z, 2));
    float g_force = total_accel / 9.80665; 

    // SHT45 온습도
    sensors_event_t humidity, temp_sht;
    sht4.getEvent(&humidity, &temp_sht);

    // BH1750 조도
    float lux = lightMeter.readLightLevel();

    // 상태 판별
    String status = "안전";
    if (g_force > 2.0) status = "강한 충돌!!";
    else if (g_force > 1.3 || g_force < 0.7) status = "이동/진동";

    // 시간 정보 가져오기
    struct tm timeinfo;
    char timeStr[20] = "00:00:00";
    // getLocalTime의 기본 대기시간이 5초이므로, 루프 지연을 방지하기 위해 10ms 타임아웃 지정
    if (getLocalTime(&timeinfo, 10)) {
      strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);
    }

    // JSON 구성
    StaticJsonDocument<512> doc;
    doc["device"] = "gy521";
    doc["timestamp_str"] = timeStr;
    doc["temperature"] = String(temp_sht.temperature, 2);
    doc["humidity"] = String(humidity.relative_humidity, 2);
    doc["lux"] = String(lux, 1);
    doc["g_force"] = String(g_force, 2);
    
    if (gps.location.isValid()) {
      doc["lat"] = String(gps.location.lat(), 6);
      doc["lng"] = String(gps.location.lng(), 6);
      doc["speed"] = String(gps.speed.kmph(), 1);
    } else {
      doc["lat"] = "0.0";
      doc["lng"] = "0.0";
    }
    
    doc["status"] = status;

    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);
    Serial.println(jsonBuffer);

    // 온라인이면 전송, 오프라인이면 LittleFS에 저장
    if (currentConnected) {
      client.publish(mqtt_topic, jsonBuffer);
    } else {
      File file = LittleFS.open(offline_file, FILE_APPEND);
      if (file) {
        if (file.size() < 1000000) { // 1MB 제한
          file.println(jsonBuffer);
          Serial.println("💾 Saved data to LittleFS (Offline mode)");
        } else {
          Serial.println("⚠️ LittleFS buffer full (>= 1MB)!");
        }
        file.close();
      } else {
        Serial.println("❌ Failed to open offline file for appending!");
      }
    }
  }
}
