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
#include <sys/time.h>

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
// 3. LittleFS 블랙박스 링버퍼 & 오프라인 버퍼 관리
// ==========================================
const char* master_log_curr = "/telemetry_log.jsonl";      // 현재 기록 세그먼트 (최대 512KB)
const char* master_log_old  = "/telemetry_log_old.jsonl";  // 직전 기록 세그먼트 (최대 512KB)
const char* offline_buffer_file = "/offline_buf.jsonl";    // 오프라인 시 임시 버퍼 (온라인 복구 시 전송)

#define SEGMENT_MAX_BYTES     (512 * 1024)                 // 세그먼트 당 512KB (총 1.0MB 항시 유지)
#define OFFLINE_BUF_MAX_BYTES (300 * 1024)                 // 오프라인 버퍼 최대 300KB

bool littlefs_ready = false;
bool has_offline_data = false;
unsigned long totalSavedRecords = 0;

// 스마트 주행 감지 래치 (Smart Trip Latch & LKP)
bool trip_active = false;      // 야외 출발 후 주행 상태 (터널/지하차도 통과 시에도 true 유지)
float last_valid_lat = 0.0;    // 직전 유효 위도 (터널 진입 시 데드레커닝 보존)
float last_valid_lng = 0.0;    // 직전 유효 경도

void logToLittleFS(const char* jsonStr, bool isOffline) {
  if (!littlefs_ready) return;

  // 1) 링버퍼(순환 기록): 현재 활성 파일이 512KB 이상이면 직전 세그먼트로 회전(Rotate)하여 항시 최신 1MB 보존
  if (LittleFS.exists(master_log_curr)) {
    File fCheck = LittleFS.open(master_log_curr, FILE_READ);
    if (fCheck) {
      size_t cur_sz = fCheck.size();
      fCheck.close();
      if (cur_sz >= SEGMENT_MAX_BYTES) {
        if (LittleFS.exists(master_log_old)) {
          LittleFS.remove(master_log_old);
        }
        LittleFS.rename(master_log_curr, master_log_old);
        Serial.printf("  🔄 [LittleFS 링버퍼 회전] %u B 도달 -> 이전 세그먼트 회전 (최신 1MB 항시 유지)\n", (unsigned int)cur_sz);
      }
    }
  }

  // 활성 세그먼트에 새 데이터 추가 (Append)
  File fMaster = LittleFS.open(master_log_curr, FILE_APPEND);
  if (fMaster) {
    fMaster.println(jsonStr);
    fMaster.flush();
    totalSavedRecords++;
    Serial.printf("  💾 [LittleFS 링버퍼] 저장 완료 (현재 세그먼트: %u B, 누적: %lu건)\n", 
                  (unsigned int)fMaster.size(), totalSavedRecords);
    fMaster.close();
  } else {
    Serial.println("  ❌ [LittleFS 링버퍼] 파일 열기 실패");
  }

  // 2) 오프라인 상태일 경우 재전송 버퍼에도 큐잉 (/offline_buf.jsonl)
  if (isOffline) {
    File fBuf = LittleFS.open(offline_buffer_file, FILE_APPEND);
    if (fBuf) {
      if (fBuf.size() < OFFLINE_BUF_MAX_BYTES) {
        fBuf.println(jsonStr);
        fBuf.flush();
        has_offline_data = true;
        Serial.printf("  📦 [LittleFS 오프라인 버퍼] 미전송 패킷 큐잉 (버퍼: %u B)\n", (unsigned int)fBuf.size());
      } else {
        Serial.println("  ⚠️ [LittleFS 오프라인 버퍼] 300KB 한도 도달");
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
// 4. GPS 위성 & NTP 시각 자동 동기화 (KST)
// ==========================================
bool gps_time_synced = false;

// UTC 날짜/시간을 표준 Unix Epoch(초)로 고속 변환하는 경량 함수
time_t utcToEpoch(int y, int m, int d, int h, int min, int s) {
  int a = (14 - m) / 12;
  int yr = y + 4800 - a;
  int mn = m + 12 * a - 3;
  long jdn = d + (153 * mn + 2) / 5 + 365 * yr + yr / 4 - yr / 100 + yr / 400 - 32045;
  long days = jdn - 2440588; // 1970-01-01 JDN
  return (time_t)(days * 86400LL + h * 3600 + min * 60 + s);
}

// 핫스팟/인터넷(NTP) 없이도 GPS 위성 신호가 잡히면 RTC 시스템 시각을 자동으로 UTC로 설정
void syncTimeFromGPS() {
  if (gps.date.isValid() && gps.time.isValid() && gps.date.year() >= 2024) {
    static unsigned long lastGpsSync = 0;
    if (!gps_time_synced || (millis() - lastGpsSync > 30000)) {
      lastGpsSync = millis();

      time_t utc_epoch = utcToEpoch(gps.date.year(), gps.date.month(), gps.date.day(),
                                    gps.time.hour(), gps.time.minute(), gps.time.second());
      if (utc_epoch > 1700000000) { // 2023년 이후 유효성 검증
        struct timeval tv = { .tv_sec = utc_epoch, .tv_usec = 0 };
        settimeofday(&tv, NULL);
        gps_time_synced = true;
        Serial.printf("  ⏰ [GPS 위성 시각 동기화 완료] %04d-%02d-%02d %02d:%02d:%02d UTC (KST 자동 적용)\n",
                      gps.date.year(), gps.date.month(), gps.date.day(),
                      gps.time.hour(), gps.time.minute(), gps.time.second());
      }
    }
  }
}

String getFormattedTime() {
  struct tm timeinfo;
  // 1순위: ESP32 시스템 RTC 시각 (NTP 또는 GPS settimeofday로 동기화된 시간, KST 자동 반영)
  if (getLocalTime(&timeinfo, 30)) {
    if (timeinfo.tm_year + 1900 >= 2024) {
      char timeStr[32];
      strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);
      return String(timeStr);
    }
  }

  // 2순위: 시스템 RTC가 아직 안 맞춰졌어도 GPS 위성 시각이 유효하다면 직접 KST(UTC+9) 계산
  if (gps.date.isValid() && gps.time.isValid() && gps.date.year() >= 2024) {
    time_t kst_epoch = utcToEpoch(gps.date.year(), gps.date.month(), gps.date.day(),
                                  gps.time.hour(), gps.time.minute(), gps.time.second()) + (9 * 3600);
    struct tm *kst_tm = gmtime(&kst_epoch);
    if (kst_tm) {
      char timeStr[32];
      strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", kst_tm);
      return String(timeStr);
    }
  }

  // 3순위: GPS 위성도 없고 NTP도 아직 연결되지 않은 초기 상태
  return "2026-10-01 00:00:00";
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

  bool gps_fix_ok = (gps.location.isValid() && gps.location.lat() != 0.0);
  if (gps_fix_ok) {
    lat = gps.location.lat();
    lng = gps.location.lng();
    speed = gps.speed.kmph();
    last_valid_lat = lat;
    last_valid_lng = lng;
    trip_active = true; // 야외 GPS Fix 성공 -> 주행 활성 래치 ON
    full_status += ", GPS: Fix OK (" + String(sats) + " sats)";
  } else {
    // 이동 속도 감지 (2.5 km/h 이상) 또는 충격 시 주행 시작으로 판정
    if (gps.speed.isValid() && gps.speed.kmph() > 2.5) {
      trip_active = true;
      speed = gps.speed.kmph();
    }
    if (g_force_val >= 1.5) {
      trip_active = true; // 차량 진동/충격 감지 시 주행 시작 래치 ON
    }

    if (trip_active && last_valid_lat != 0.0) {
      // 🚗 터널, 지하차도, 도심 음영 지역 통과 중: 직전 유효 위치(LKP) 유지
      lat = last_valid_lat;
      lng = last_valid_lng;
      full_status += ", GPS: 터널/음영구간 (직전 위치 유지, " + String(sats) + " sats)";
    } else {
      // 💤 아직 출발 전 실내/책상 위 대기 상태
      if (chars_rx > 0) {
        full_status += ", GPS: 실내 탐색 중 (" + String(sats) + " sats) [대기]";
      } else {
        full_status += ", GPS: No Data (Check Baud/Pin)";
      }
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
  Serial.printf("  [GPS 상태] 수신바이트: %lu, 위성수: %d, Fix: %s (위도: %.6f, 경도: %.6f, 상태: %s)\n",
                chars_rx, sats, gps_fix_ok ? "YES" : "NO", lat, lng,
                trip_active ? "🚗주행중(터널연속기록)" : "💤실내대기(저장보류)");

  // 4) LittleFS 블랙박스 스마트 저장 판정
  // - 주행 중(trip_active): 터널/음영지역 통과 중이라도 100% 5초마다 연속 저장!
  // - 비주행(실내/책상 위): 충격 이벤트(g_force >= 1.8G) 발생 시에만 긴급 저장, 평소엔 대기(메모리 보존)
  bool should_save_fs = trip_active || (g_force_val >= SHOCK_THRESHOLD_G);
  bool is_connected = client.connected();

  if (should_save_fs) {
    logToLittleFS(jsonBuffer, !is_connected);
  } else {
    Serial.println("  💤 [실내 대기 모드] 주행 출발 전 - LittleFS 저장 보류 (메모리 보호)");
  }

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
    
    // 고속 버퍼(512B)로 누적 레코드 카운트 (부팅 0.05초 완료)
    uint8_t count_buf[512];
    if (LittleFS.exists(master_log_old)) {
      File fOld = LittleFS.open(master_log_old, FILE_READ);
      if (fOld) {
        log_size += fOld.size();
        while (fOld.available()) {
          int n = fOld.read(count_buf, sizeof(count_buf));
          for (int i = 0; i < n; i++) {
            if (count_buf[i] == '\n') totalSavedRecords++;
          }
        }
        fOld.close();
      }
    }
    if (LittleFS.exists(master_log_curr)) {
      File fCurr = LittleFS.open(master_log_curr, FILE_READ);
      if (fCurr) {
        log_size += fCurr.size();
        while (fCurr.available()) {
          int n = fCurr.read(count_buf, sizeof(count_buf));
          for (int i = 0; i < n; i++) {
            if (count_buf[i] == '\n') totalSavedRecords++;
          }
        }
        fCurr.close();
      }
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
  Serial.println("   - clear 또는 reset: 저장된 로그 초기화");
  Serial.println("   - start / stop  : 주행 기록 강제 시작 / 대기 전환\n");
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
      if (!littlefs_ready) {
        Serial.println("LittleFS가 마운트되지 않았습니다.");
      } else {
        unsigned long count = 0;
        // 1) 이전 세그먼트가 있으면 먼저 덤프
        if (LittleFS.exists(master_log_old)) {
          File fOld = LittleFS.open(master_log_old, FILE_READ);
          if (fOld) {
            while (fOld.available()) {
              String line = fOld.readStringUntil('\n');
              Serial.println(line);
              count++;
            }
            fOld.close();
          }
        }
        // 2) 현재 활성 세그먼트 덤프
        if (LittleFS.exists(master_log_curr)) {
          File fCurr = LittleFS.open(master_log_curr, FILE_READ);
          if (fCurr) {
            while (fCurr.available()) {
              String line = fCurr.readStringUntil('\n');
              Serial.println(line);
              count++;
            }
            fCurr.close();
          }
        }
        if (count == 0) {
          Serial.println("저장된 로그 파일이 없습니다.");
        }
        Serial.printf("================ [덤프 종료: 총 %lu 건] ================\n\n", count);
      }
    } else if (cmd.equalsIgnoreCase("start")) {
      trip_active = true;
      Serial.println("\n🚗 [주행 모드 강제 시작] LittleFS 연속 저장을 시작합니다.\n");
    } else if (cmd.equalsIgnoreCase("stop")) {
      trip_active = false;
      Serial.println("\n💤 [대기 모드 전환] LittleFS 저장을 일시 정지합니다.\n");
    } else if (cmd.equalsIgnoreCase("clear") || cmd.equalsIgnoreCase("reset")) {
      if (LittleFS.exists(master_log_curr)) {
        LittleFS.remove(master_log_curr);
      }
      if (LittleFS.exists(master_log_old)) {
        LittleFS.remove(master_log_old);
      }
      if (LittleFS.exists(offline_buffer_file)) {
        LittleFS.remove(offline_buffer_file);
      }
      totalSavedRecords = 0;
      trip_active = false;
      last_valid_lat = 0.0;
      last_valid_lng = 0.0;
      Serial.println("\n🗑️ [LittleFS] 블랙박스 링버퍼 및 오프라인 버퍼가 0건으로 초기화되었습니다. (대기 모드 전환)\n");
    } else if (cmd.equalsIgnoreCase("info") || cmd.equalsIgnoreCase("stat")) {
      size_t total = LittleFS.totalBytes();
      size_t used = LittleFS.usedBytes();
      size_t fsize = 0;
      if (LittleFS.exists(master_log_curr)) {
        File fCurr = LittleFS.open(master_log_curr, FILE_READ);
        if (fCurr) {
          fsize += fCurr.size();
          fCurr.close();
        }
      }
      if (LittleFS.exists(master_log_old)) {
        File fOld = LittleFS.open(master_log_old, FILE_READ);
        if (fOld) {
          fsize += fOld.size();
          fOld.close();
        }
      }
      size_t obuf_size = 0;
      if (LittleFS.exists(offline_buffer_file)) {
        File fBuf = LittleFS.open(offline_buffer_file, FILE_READ);
        if (fBuf) {
          obuf_size = fBuf.size();
          fBuf.close();
        }
      }
      Serial.printf("\n📊 [LittleFS 링버퍼 현황] 전체: %u B, 사용: %u B | 블랙박스(최신1MB 유지): %u B (%lu건), 오프라인: %u B | 상태: %s\n\n",
                    (unsigned int)total, (unsigned int)used, (unsigned int)fsize, totalSavedRecords, (unsigned int)obuf_size,
                    trip_active ? "🚗 주행 기록 중" : "💤 실내 대기 중");
    }
  }
}

// ==========================================
// 8. MAIN LOOP
// ==========================================
void loop() {
  // 1) 시리얼 명령어 처리
  handleSerialCommands();

  // 2) GPS 백그라운드 NMEA 파싱 및 시각 자동 동기화
  while (Serial1.available() > 0) {
    gps.encode(Serial1.read());
  }
  syncTimeFromGPS();

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
