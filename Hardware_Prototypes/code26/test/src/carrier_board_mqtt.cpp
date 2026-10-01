#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <BH1750.h>
#include <SHTSensor.h>
#include <TinyGPSPlus.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <LittleFS.h>
#include <time.h>

// ==========================================
// 1. 하드웨어 핀 및 통신 파라미터 정의
// ==========================================
#define I2C_SDA_PIN   19
#define I2C_SCL_PIN   20

#define GPS_RX_PIN    16  // ESP32 RX (GPIO 16) <- PCB Net GPS_TX (J_GPS Pad 3 / ATGM336H TXD)
#define GPS_TX_PIN    17  // ESP32 TX (GPIO 17) -> PCB Net GPS_RX (J_GPS Pad 4 / ATGM336H RXD)
#define GPS_BAUDRATE  9600

// MQTT 브로커 및 토픽
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const char* mqtt_topic = "coldchain/truck01/sensor";
const char* device_id = "carrier-c6-01";

// Wi-Fi 네트워크 목록 (다중 AP 자동 접속)
struct WiFiNetwork {
  const char* ssid;
  const char* password;
};

const WiFiNetwork wifi_networks[] = {
  {"225", "123698745"},
  {"lab225", "123698745"},
  {"hani", "12345687"}
};
const int num_wifi_networks = sizeof(wifi_networks) / sizeof(wifi_networks[0]);

// 타이밍 및 임계값 파라미터
#define TX_INTERVAL_MS        5000    // 일반 텔레메트리 전송 주기 (5초)
#define SAMPLE_INTERVAL_MS    20      // IMU 고속 가속도 샘플링 (20ms = 50Hz)
#define SHOCK_THRESHOLD_G     1.8     // 충격 감지 임계값 (1.8G)
#define SHOCK_DEBOUNCE_MS     3000    // 충격 재감지 방지 데드타임 (3초)

// ==========================================
// 2. 센서 및 네트워크 객체
// ==========================================
Adafruit_MPU6050 mpu;
BH1750 lightMeter;
SHTSensor sht(SHTSensor::SHT4X);
TinyGPSPlus gps;

WiFiMulti wifiMulti;
WiFiClient espClient;
PubSubClient client(espClient);

bool mpu_ready = false;
bool bh1750_ready = false;
bool sht45_ready = false;

float max_g_force = 1.0;
unsigned long lastTxTime = 0;
unsigned long lastSampleTime = 0;
unsigned long lastShockTime = 0;
unsigned long lastMqttAttempt = 0;

// ==========================================
// 3. LittleFS 블랙박스 & 오프라인 버퍼 관리
// ==========================================
const char* master_log_file = "/telemetry_log.jsonl";   // 항시 영구 기록 (블랙박스 마스터 로그)
const char* offline_buffer_file = "/offline_buf.jsonl"; // 오프라인 시 임시 버퍼 (온라인 복구 시 전송)
#define MAX_LOG_SIZE_BYTES (1024 * 1024)               // 최대 1MB
bool littlefs_ready = false;
bool has_offline_data = false;
unsigned long totalSavedRecords = 0;

void logToLittleFS(const char* jsonStr, bool isOffline) {
  if (!littlefs_ready) return;

  // 1) 항시 블랙박스 영구 저장 (/telemetry_log.jsonl)
  File fMaster = LittleFS.open(master_log_file, FILE_APPEND);
  if (fMaster) {
    if (fMaster.size() < MAX_LOG_SIZE_BYTES) {
      fMaster.println(jsonStr);
      fMaster.flush();
      totalSavedRecords++;
      Serial.printf("  💾 [LittleFS 블랙박스] 저장 완료 (파일: %u B, 누적: %lu건)\n", (unsigned int)fMaster.size(), totalSavedRecords);
    } else {
      Serial.println("  ⚠️ [LittleFS 블랙박스] 1MB 용량 한도 도달");
    }
    fMaster.close();
  } else {
    Serial.println("  ❌ [LittleFS 블랙박스] 파일 열기 실패");
  }

  // 2) 오프라인 상태일 경우 재전송 버퍼에도 기록 (/offline_buf.jsonl)
  if (isOffline) {
    File fBuf = LittleFS.open(offline_buffer_file, FILE_APPEND);
    if (fBuf) {
      if (fBuf.size() < MAX_LOG_SIZE_BYTES) {
        fBuf.println(jsonStr);
        fBuf.flush();
        has_offline_data = true;
        Serial.printf("  📦 [LittleFS 오프라인 버퍼] 미전송 패킷 큐잉 (버퍼: %u B)\n", (unsigned int)fBuf.size());
      }
      fBuf.close();
    }
  }
}

// 오프라인 버퍼가 쌓여있다면 온라인 복구 시 MQTT로 순차 전송
void flushOfflineBuffer() {
  if (!littlefs_ready || !client.connected()) return;
  if (!has_offline_data) return; // 미전송 데이터가 없을 때는 스킵하여 불필요한 VFS I/O 방지

  File fBuf = LittleFS.open(offline_buffer_file, FILE_READ);
  if (!fBuf) {
    has_offline_data = false;
    return;
  }

  Serial.println("\n📡 [LittleFS 오프라인 버퍼 동기화] 미전송 데이터 MQTT 브로커 전송 중...");
  int sent = 0;
  while (fBuf.available() && client.connected()) {
    String line = fBuf.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) continue;
    if (client.publish(mqtt_topic, line.c_str())) {
      sent++;
      delay(40); // 네트워크 혼잡 방지
    } else {
      break;
    }
  }
  fBuf.close();

  // 정상 전송 후 오프라인 버퍼 삭제
  LittleFS.remove(offline_buffer_file);
  has_offline_data = false;
  Serial.printf("✅ [LittleFS 오프라인 동기화 완료] 총 %d건 브로커 전송 및 버퍼 초기화!\n\n", sent);
}

// ==========================================
// 3. NTP 시간 포맷 함수 (KST)
// ==========================================
String getFormattedTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo, 100)) {
    return "2026-10-01 00:00:00";
  }
  char timeStr[32];
  strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(timeStr);
}

// ==========================================
// 4. MQTT 비블로킹 재연결
// ==========================================
bool reconnectMQTT() {
  if (client.connected()) return true;

  unsigned long now = millis();
  if (now - lastMqttAttempt > 4000) {
    lastMqttAttempt = now;
    Serial.print("  [MQTT] Connecting to broker.emqx.io...");
    
    String clientId = "ESP32C6-ColdChain-";
    clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println(" OK (Connected!)");
      return true;
    } else {
      Serial.printf(" Failed, rc=%d (will retry)\n", client.state());
    }
  }
  return false;
}

// ==========================================
// 5. 텔레메트리 JSON 생성 및 MQTT 전송
// ==========================================
void transmitTelemetry(float g_force_val, const char* status_str) {
  // 1) 센서 데이터 수집
  float temp = 0.0, humi = 0.0, lux = 0.0;
  if (sht45_ready && sht.readSample()) {
    temp = sht.getTemperature();
    humi = sht.getHumidity();
  }
  if (bh1750_ready) {
    lux = lightMeter.readLightLevel();
  }

  // 2) GPS 위치/속도 및 위성 상태
  float lat = 0.0, lng = 0.0, speed = 0.0;
  int sats = gps.satellites.value();
  unsigned long chars_rx = gps.charsProcessed();
  String full_status = String(status_str);
  if (gps.location.isValid()) {
    lat = gps.location.lat();
    lng = gps.location.lng();
    speed = gps.speed.kmph();
    full_status += ", GPS: Fix OK (" + String(sats) + " sats)";
  } else {
    if (chars_rx > 0) {
      full_status += ", GPS: Searching (" + String(sats) + " sats)";
    } else {
      full_status += ", GPS: No Data (Check Baud/Pin)";
    }
  }

  // 3) JSON 빌드
  StaticJsonDocument<512> doc;
  doc["device"] = device_id;
  doc["timestamp_str"] = getFormattedTime();
  doc["temperature"] = serialized(String(temp, 2));
  doc["humidity"] = serialized(String(humi, 2));
  doc["lux"] = serialized(String(lux, 1));
  doc["g_force"] = serialized(String(g_force_val, 2));
  doc["lat"] = serialized(String(lat, 6));
  doc["lng"] = serialized(String(lng, 6));
  doc["speed"] = serialized(String(speed, 1));
  doc["sats"] = sats;
  doc["status"] = full_status;

  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);

  Serial.println("------------------------------------------------------------------");
  Serial.printf("[MQTT 전송] 토픽: %s\n", mqtt_topic);
  Serial.printf("  페이로드: %s\n", jsonBuffer);
  Serial.printf("  [GPS 상태] 수신바이트: %lu, 위성수: %d, Fix: %s (위도: %.6f, 경도: %.6f)\n",
                chars_rx, sats, gps.location.isValid() ? "YES" : "NO", lat, lng);

  // 4) LittleFS 블랙박스 항시 저장 및 오프라인 버퍼링
  bool is_connected = client.connected();
  logToLittleFS(jsonBuffer, !is_connected);

  // 5) MQTT 네트워크 전송
  if (is_connected) {
    bool pub_ok = client.publish(mqtt_topic, jsonBuffer);
    if (pub_ok) {
      Serial.println("  -> MQTT 발행 성공 (PASS)");
    } else {
      Serial.println("  -> MQTT 발행 실패 (Buffer/Net Error)");
    }
    // 미전송 오프라인 데이터가 있다면 함께 동기화
    flushOfflineBuffer();
  } else {
    Serial.println("  -> [오프라인 모드] 핫스팟/MQTT 미연결 (LittleFS에 안전 보존 중)");
  }
}

// ==========================================
// 6. SETUP
// ==========================================
void setup() {
  Serial.begin(115200);
  delay(1200);

  Serial.println("\n=======================================================");
  Serial.println(" ColdChain DigitalTwin Carrier Board MQTT 텔레메트리 ");
  Serial.println(" MCU: DFRobot Beetle ESP32-C6 Mini ");
  Serial.println("=======================================================\n");

  // I2C 초기화
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(100000);
  Wire.setTimeOut(25);

  // 1. SHT45 온습도 센서 초기화
  Serial.print("📦 [1] SHT45 온습도 센서 초기화... ");
  if (sht.init()) {
    sht.setAccuracy(SHTSensor::SHT_ACCURACY_HIGH);
    sht45_ready = true;
    Serial.println("OK");
  } else {
    Serial.println("Fail");
  }

  // 2. BH1750 조도 센서 초기화
  Serial.print("📦 [2] BH1750 조도 센서 초기화... ");
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    bh1750_ready = true;
    Serial.println("OK");
  } else {
    Serial.println("Fail");
  }

  // 3. MPU6050 6축 IMU 초기화
  Serial.print("📦 [3] GY-521 (MPU6050) IMU 초기화... ");
  if (mpu.begin()) {
    mpu_ready = true;
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("OK");
  } else {
    Serial.println("Fail");
  }

  // 4. GPS UART 초기화
  Serial.print("📦 [4] GPS ATGM336H UART 포트 열기 (RX:16, TX:17)... ");
  Serial1.begin(GPS_BAUDRATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  Serial.println("OK");

  // 5. LittleFS 파일시스템 마운트
  Serial.print("📦 [5] LittleFS 파일시스템 마운트... ");
  if (LittleFS.begin(true)) {
    littlefs_ready = true;
    size_t total = LittleFS.totalBytes();
    size_t used = LittleFS.usedBytes();
    size_t log_size = 0;
    if (LittleFS.exists(master_log_file)) {
      File f = LittleFS.open(master_log_file, FILE_READ);
      log_size = f.size();
      while (f.available()) {
        if (f.read() == '\n') totalSavedRecords++;
      }
      f.close();
    }
    Serial.printf("OK (사용량: %u / %u bytes, 기존 누적: %u bytes, %lu건)\n", 
                  (unsigned int)used, (unsigned int)total, (unsigned int)log_size, totalSavedRecords);
  } else {
    Serial.println("Fail (LittleFS 마운트 실패)");
  }

  // 6. Wi-Fi Multi 초기화
  Serial.println("📡 [6] Wi-Fi Multi AP 등록 및 연결 시도...");
  WiFi.mode(WIFI_STA);
  for (int i = 0; i < num_wifi_networks; i++) {
    wifiMulti.addAP(wifi_networks[i].ssid, wifi_networks[i].password);
    Serial.printf("   + AP 등록: %s\n", wifi_networks[i].ssid);
  }

  // 7. MQTT 설정
  client.setServer(mqtt_server, mqtt_port);
  client.setBufferSize(512);

  // 8. NTP 시간 동기화 (KST: UTC+9)
  configTime(9 * 3600, 0, "pool.ntp.org", "time.nist.gov");

  Serial.println("\n🚀 초기화 완료! 실시간 루프 시작...\n");
  Serial.println("💡 [시리얼 명령어 가이드]");
  Serial.println("   - dump 또는 read : LittleFS에 저장된 모든 데이터 출력");
  Serial.println("   - info 또는 stat : 저장 용량 및 누적 건수 확인");
  Serial.println("   - clear 또는 reset: 저장된 로그 초기화\n");
}

// ==========================================
// 7. 시리얼 인터랙티브 명령어 처리
// ==========================================
void handleSerialCommands() {
  while (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() == 0) continue;

    if (cmd.equalsIgnoreCase("read") || cmd.equalsIgnoreCase("dump")) {
      Serial.println("\n================ [LittleFS 블랙박스 덤프 시작] ================");
      if (!littlefs_ready || !LittleFS.exists(master_log_file)) {
        Serial.println("저장된 로그 파일이 없습니다.");
      } else {
        File f = LittleFS.open(master_log_file, FILE_READ);
        unsigned long count = 0;
        while (f.available()) {
          String line = f.readStringUntil('\n');
          Serial.println(line);
          count++;
        }
        f.close();
        Serial.printf("================ [덤프 종료: 총 %lu 건] ================\n\n", count);
      }
    } else if (cmd.equalsIgnoreCase("clear") || cmd.equalsIgnoreCase("reset")) {
      if (LittleFS.exists(master_log_file)) {
        LittleFS.remove(master_log_file);
      }
      if (LittleFS.exists(offline_buffer_file)) {
        LittleFS.remove(offline_buffer_file);
      }
      totalSavedRecords = 0;
      Serial.println("\n🗑️ [LittleFS] 블랙박스 및 오프라인 버퍼가 초기화되었습니다.\n");
    } else if (cmd.equalsIgnoreCase("info") || cmd.equalsIgnoreCase("stat")) {
      size_t total = LittleFS.totalBytes();
      size_t used = LittleFS.usedBytes();
      size_t fsize = 0;
      if (LittleFS.exists(master_log_file)) {
        File f = LittleFS.open(master_log_file, FILE_READ);
        fsize = f.size();
        f.close();
      }
      Serial.printf("\n📊 [LittleFS 현황] 전체: %u B, 사용: %u B, 마스터로그: %u B (총 %lu건 기록됨)\n\n",
                    (unsigned int)total, (unsigned int)used, (unsigned int)fsize, totalSavedRecords);
    }
  }
}

// ==========================================
// 8. MAIN LOOP
// ==========================================
void loop() {
  // 1) 시리얼 명령어 처리
  handleSerialCommands();

  // 2) GPS 백그라운드 NMEA 파싱
  while (Serial1.available() > 0) {
    gps.encode(Serial1.read());
  }

  // 3) Wi-Fi 및 MQTT 연결 유지 (비블로킹)
  bool wifi_connected = (wifiMulti.run() == WL_CONNECTED);
  if (wifi_connected) {
    if (!client.connected()) {
      reconnectMQTT();
    }
    client.loop();
  }

  unsigned long now = millis();

  // 4) 고속 가속도 샘플링 (20ms 간격)
  if (mpu_ready && (now - lastSampleTime >= SAMPLE_INTERVAL_MS)) {
    lastSampleTime = now;
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    float total_acc = sqrt(a.acceleration.x * a.acceleration.x +
                           a.acceleration.y * a.acceleration.y +
                           a.acceleration.z * a.acceleration.z);
    float g_force = total_acc / 9.80665;

    // 피크 홀드
    if (g_force > max_g_force) {
      max_g_force = g_force;
    }

    // 급격한 충격 이벤트 발생 시 즉시 전송
    if (g_force >= SHOCK_THRESHOLD_G) {
      if (now - lastShockTime >= SHOCK_DEBOUNCE_MS) {
        lastShockTime = now;
        Serial.printf("\n🚨 [충격 감지!] 충격량: %.2f G\n", g_force);
        transmitTelemetry(g_force, "충격 발생");
        max_g_force = 1.0;
      }
    }
  }

  // 5) 주기적 텔레메트리 전송 (5초 간격)
  if (now - lastTxTime >= TX_INTERVAL_MS) {
    lastTxTime = now;
    transmitTelemetry(max_g_force, "정상");
    max_g_force = 1.0; // 전송 후 피크 홀드 리셋
  }
}
