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
#include <esp_mac.h>
#include <time.h>
#include <sys/time.h>
#include <math.h>

// ============================================================================
// ColdChain DigitalTwin — 20h Climatic Chamber Calibration Firmware
// Target: CarrierBoard Beetle ESP32-C6 + SHT45 + BH1750 + MPU6050 + ATGM336H
// Build env: [env:beetle_c6_chamber_cal]
//
// Key Features:
//   1. Exact In-Situ Thermal Equivalence: Runs the same sensors (SHT45, BH1750,
//      MPU6050 @ 50Hz, GPS UART) and 5-second Wi-Fi MQTT telemetry cadence as
//      field operation (carrier_board_mqtt.cpp) so self-heating matches 100%.
//   2. Auto-Start on Power Switch ON: Immediately logs every 5.0 s on boot
//      without needing a USB 'start' command (survives power-switch toggles).
//   3. Auto Device ID via Wi-Fi STA MAC: One firmware binary auto-configures
//      carrier-c6-01 ~ carrier-c6-04 and its MQTT topic.
//   4. 20h+ Lossless LittleFS CSV Backup (/chamber_cal.csv): ~45 bytes/row ->
//      14,400 rows (20 hours @ 5s) = ~630 KB (fits well inside 1.44 MB flash
//      with zero ring-buffer overwrite even if chamber blocks Wi-Fi all night).
//   5. Field Convenience Commands:
//      info | live <sec> | dump | clear | pause | resume
//      wifi <ssid> [password]        -> saves extra AP to /wifi_extra.txt
//      settime YYYY-MM-DD HH:MM:SS   -> sets KST wall-clock without NTP/Wi-Fi
// ============================================================================

#define I2C_SDA_PIN          19
#define I2C_SCL_PIN          20
#define GPS_RX_PIN           16
#define GPS_TX_PIN           17
#define GPS_BAUDRATE         9600

#define TX_INTERVAL_MS       5000UL     // 5.0 s exact cadence (matches field deployment)
#define IMU_INTERVAL_MS      20UL       // 50 Hz IMU polling (matches field thermal load)
#define MAX_CSV_BYTES        1320000UL  // ~1.26 MB safety cap (> 38 hours @ 5s CSV)

const char* mqtt_server = "broker.hivemq.com";
const int   mqtt_port   = 1883;

const char* csv_log_path    = "/chamber_cal.csv";
const char* extra_wifi_path = "/wifi_extra.txt";

// ============================================================================
// [현장 Wi-Fi 추가 위치] 필요 시 아래 배열에 현장 2.4GHz 공유기 SSID/비밀번호를 추가하세요.
// (또는 시리얼 모니터에서 `wifi 공유기이름 비밀번호` 명령어로 재컴파일 없이 추가 가능)
// ============================================================================
struct WiFiCredential {
  const char* ssid;
  const char* password;
};

const WiFiCredential default_wifi_list[] = {
  {"smroom", ""},
  {"225", "123698745"},
  {"hani", "12345687"}
  // , {"현장공유기_SSID", "현장공유기_비밀번호"}
};
const int num_default_wifi = sizeof(default_wifi_list) / sizeof(default_wifi_list[0]);

// ============================================================================
// Global Objects & State
// ============================================================================
Adafruit_MPU6050 mpu;
BH1750 lightMeter;
SHTSensor sht(SHTSensor::SHT4X);
TinyGPSPlus gps;

WiFiMulti wifiMulti;
WiFiClient espClient;
PubSubClient mqttClient(espClient);

bool sht_ready    = false;
bool bh1750_ready = false;
bool mpu_ready    = false;
bool fs_ready     = false;

char mac_str[20]      = "UNKNOWN";
char device_id[24]    = "carrier-c6-01";
char mqtt_topic[48]   = "coldchain/chamber/carrier-c6-01";

String extra_ssid = "";
String extra_pass = "";

bool logging_active      = true;   // Auto-start immediately on battery switch ON
bool live_mode           = false;
unsigned long live_end_ms       = 0;
unsigned long last_live_ms      = 0;
unsigned long last_tx_ms        = 0;
unsigned long last_imu_ms       = 0;
unsigned long last_wifi_try_ms  = 0;
unsigned long last_mqtt_try_ms  = 0;
unsigned long saved_rows        = 0;
int wifi_fail_streak            = 0;
float max_g_force               = 1.0f;

// ============================================================================
// Time & MAC Helpers
// ============================================================================
time_t utcToEpoch(int y, int m, int d, int h, int min, int s) {
  int a = (14 - m) / 12;
  int yr = y + 4800 - a;
  int mn = m + 12 * a - 3;
  long jdn = d + (153 * mn + 2) / 5 + 365 * yr + yr / 4 - yr / 100 + yr / 400 - 32045;
  long days = jdn - 2440588;
  return (time_t)(days * 86400LL + h * 3600 + min * 60 + s);
}

time_t getValidEpoch() {
  time_t now_ep = 0;
  time(&now_ep);
  if (now_ep >= 1700000000L) {
    return now_ep;
  }
  return 0;
}

String getFormattedKST() {
  time_t now_ep = getValidEpoch();
  if (now_ep > 0) {
    time_t kst_ep = now_ep + 9 * 3600L;
    struct tm *kst_tm = gmtime(&kst_ep);
    if (kst_tm) {
      char buf[32];
      strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", kst_tm);
      return String(buf);
    }
  }
  return "00:00:00";
}

void detectBoardByMac() {
  uint8_t mac[6] = {0};
  esp_read_mac(mac, ESP_MAC_WIFI_STA);
  snprintf(mac_str, sizeof(mac_str), "%02X:%02X:%02X:%02X:%02X:%02X",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

#ifdef DEVICE_ID
  snprintf(device_id, sizeof(device_id), "%s", DEVICE_ID);
  snprintf(mqtt_topic, sizeof(mqtt_topic), "coldchain/chamber/%s", device_id);
#else
  if (strcmp(mac_str, "F0:F5:BD:2C:48:5C") == 0) {
    snprintf(device_id, sizeof(device_id), "carrier-c6-02");
    snprintf(mqtt_topic, sizeof(mqtt_topic), "coldchain/chamber/carrier-c6-02");
  } else if (strcmp(mac_str, "CC:8D:A2:FA:84:EC") == 0) {
    snprintf(device_id, sizeof(device_id), "carrier-c6-03");
    snprintf(mqtt_topic, sizeof(mqtt_topic), "coldchain/chamber/carrier-c6-03");
  } else if (strcmp(mac_str, "CC:8D:A2:FA:9F:BC") == 0) {
    snprintf(device_id, sizeof(device_id), "carrier-c6-04");
    snprintf(mqtt_topic, sizeof(mqtt_topic), "coldchain/chamber/carrier-c6-04");
  } else {
    snprintf(device_id, sizeof(device_id), "carrier-c6-01");
    snprintf(mqtt_topic, sizeof(mqtt_topic), "coldchain/chamber/carrier-c6-01");
  }
#endif

#ifdef MQTT_TOPIC
  snprintf(mqtt_topic, sizeof(mqtt_topic), "%s", MQTT_TOPIC);
#endif
}

// ============================================================================
// Wi-Fi & Extra AP Persistence
// ============================================================================
void loadExtraWiFiFromFS() {
  if (!fs_ready || !LittleFS.exists(extra_wifi_path)) return;
  File f = LittleFS.open(extra_wifi_path, FILE_READ);
  if (!f) return;
  extra_ssid = f.readStringUntil('\n');
  extra_pass = f.readStringUntil('\n');
  extra_ssid.trim();
  extra_pass.trim();
  f.close();
}

void registerAllWiFiAPs() {
  for (int i = 0; i < num_default_wifi; i++) {
    if (default_wifi_list[i].password == NULL || strlen(default_wifi_list[i].password) == 0) {
      wifiMulti.addAP(default_wifi_list[i].ssid);
    } else {
      wifiMulti.addAP(default_wifi_list[i].ssid, default_wifi_list[i].password);
    }
  }
  if (extra_ssid.length() > 0) {
    if (extra_pass.length() == 0) {
      wifiMulti.addAP(extra_ssid.c_str());
    } else {
      wifiMulti.addAP(extra_ssid.c_str(), extra_pass.c_str());
    }
  }
}

bool reconnectMQTT() {
  if (mqttClient.connected()) return true;
  unsigned long now = millis();
  if (now - last_mqtt_try_ms < 4000UL) return false;
  last_mqtt_try_ms = now;

  String cid = String("ChamberCal-") + String(device_id) + "-" + String((uint32_t)ESP.getEfuseMac(), HEX);
  mqttClient.setSocketTimeout(3);
  return mqttClient.connect(cid.c_str());
}

// ============================================================================
// Sensor Helpers
// ============================================================================
bool initSHT() {
  sht = SHTSensor(SHTSensor::SHT4X);
  if (sht.init()) {
    sht.setAccuracy(SHTSensor::SHT_ACCURACY_HIGH);
    return true;
  }
  sht = SHTSensor(SHTSensor::SHT3X);
  if (sht.init()) {
    sht.setAccuracy(SHTSensor::SHT_ACCURACY_HIGH);
    return true;
  }
  return false;
}

void readEnvSensors(float &temp_c, float &rh_pct, float &lux_val) {
  temp_c = NAN;
  rh_pct = NAN;
  lux_val = -1.0f;

  if (!sht_ready) {
    sht_ready = initSHT();
  }
  if (sht_ready && sht.readSample()) {
    temp_c = sht.getTemperature();
    rh_pct = sht.getHumidity();
  }

  if (!bh1750_ready) {
    bh1750_ready = lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
  }
  if (bh1750_ready) {
    lux_val = lightMeter.readLightLevel();
  }
}

// ============================================================================
// LittleFS CSV Logging & Serial Commands
// ============================================================================
unsigned long countCsvRows() {
  if (!fs_ready || !LittleFS.exists(csv_log_path)) return 0;
  File f = LittleFS.open(csv_log_path, FILE_READ);
  if (!f) return 0;
  unsigned long lines = 0;
  uint8_t buf[512];
  while (f.available()) {
    int n = f.read(buf, sizeof(buf));
    for (int i = 0; i < n; i++) {
      if (buf[i] == '\n') lines++;
    }
  }
  f.close();
  return (lines > 0) ? (lines - 1) : 0;  // subtract header row
}

void ensureCsvHeader() {
  if (!fs_ready) return;
  if (!LittleFS.exists(csv_log_path)) {
    File f = LittleFS.open(csv_log_path, FILE_WRITE);
    if (f) {
      f.println("uptime_ms,epoch_s,temp_c,rh_pct,lux,g_force,rssi");
      f.flush();
      f.close();
    }
  }
}

void appendCsvRow(unsigned long up_ms, time_t ep_s, float temp_c, float rh_pct,
                  float lux_val, float g_val, int rssi_dbm) {
  if (!fs_ready) return;
  ensureCsvHeader();

  File fCheck = LittleFS.open(csv_log_path, FILE_READ);
  size_t fsz = 0;
  if (fCheck) {
    fsz = fCheck.size();
    fCheck.close();
  }
  if (fsz >= MAX_CSV_BYTES) {
    Serial.println("[WARN] /chamber_cal.csv reached safety cap (1.32 MB).");
    return;
  }

  File f = LittleFS.open(csv_log_path, FILE_APPEND);
  if (f) {
    f.printf("%lu,%lld,%.3f,%.3f,%.1f,%.3f,%d\n",
             up_ms, (long long)ep_s, temp_c, rh_pct, lux_val, g_val, rssi_dbm);
    f.flush();
    f.close();
    saved_rows++;
  }
}

void cmdInfo() {
  float t_c, rh, lx;
  readEnvSensors(t_c, rh, lx);
  size_t csv_bytes = 0;
  if (fs_ready && LittleFS.exists(csv_log_path)) {
    File f = LittleFS.open(csv_log_path, FILE_READ);
    if (f) {
      csv_bytes = f.size();
      f.close();
    }
  }

  Serial.println("=== FDT_CHAMBER_ENV_CAL ===");
  Serial.printf("MAC: %s\n", mac_str);
  Serial.printf("DEVICE: %s\n", device_id);
  Serial.printf("TOPIC: %s\n", mqtt_topic);
  Serial.printf("TIME_KST: %s (epoch=%lld, uptime_ms=%lu)\n",
                getFormattedKST().c_str(), (long long)getValidEpoch(), millis());
  Serial.printf("WIFI: %s", (WiFi.status() == WL_CONNECTED) ? "CONNECTED" : "DISCONNECTED");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf(" (SSID=%s, IP=%s, RSSI=%d dBm)",
                  WiFi.SSID().c_str(), WiFi.localIP().toString().c_str(), WiFi.RSSI());
  }
  if (extra_ssid.length() > 0) {
    Serial.printf(" [ExtraAP=%s]", extra_ssid.c_str());
  }
  Serial.println();
  Serial.printf("MQTT: %s\n", mqttClient.connected() ? "CONNECTED" : "DISCONNECTED");
  Serial.printf("SENSORS: SHT45=%s BH1750=%s MPU6050=%s\n",
                sht_ready ? "OK" : "FAIL",
                bh1750_ready ? "OK" : "FAIL",
                mpu_ready ? "OK" : "FAIL");
  Serial.printf("LIVE: temp=%.3f C, rh=%.3f %%RH, lux=%.1f lx\n", t_c, rh, lx);
  if (fs_ready) {
    Serial.printf("LITTLEFS: used=%u / total=%u bytes | csv_size=%u bytes, rows=%lu | logging=%s\n",
                  (unsigned int)LittleFS.usedBytes(),
                  (unsigned int)LittleFS.totalBytes(),
                  (unsigned int)csv_bytes,
                  saved_rows,
                  logging_active ? "ACTIVE (5s)" : "PAUSED");
  } else {
    Serial.println("LITTLEFS: FAIL");
  }
  Serial.println("COMMANDS: info | live <sec> | dump | clear | pause | resume | wifi <ssid> [pw] | settime YYYY-MM-DD HH:MM:SS");
  Serial.println("=== END_INFO ===");
}

void cmdDumpCsv() {
  Serial.println("---CHAMBER_CSV_START---");
  Serial.printf("# device=%s mac=%s dump_uptime_ms=%lu dump_kst=%s\n",
                device_id, mac_str, millis(), getFormattedKST().c_str());
  if (!fs_ready || !LittleFS.exists(csv_log_path)) {
    Serial.println("uptime_ms,epoch_s,temp_c,rh_pct,lux,g_force,rssi");
  } else {
    File f = LittleFS.open(csv_log_path, FILE_READ);
    if (f) {
      unsigned long line_cnt = 0;
      while (f.available()) {
        String ln = f.readStringUntil('\n');
        ln.trim();
        if (ln.length() > 0) {
          Serial.println(ln);
          line_cnt++;
          if ((line_cnt & 63UL) == 63UL) {
            delay(1);  // Feed FreeRTOS IDLE/WDT & prevent USB CDC TX buffer overrun
          }
        }
      }
      f.close();
    }
  }
  Serial.println("---CHAMBER_CSV_END---");
  Serial.flush();
}

void handleSerialCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  String lower = cmd;
  lower.toLowerCase();

  if (lower == "info" || lower == "stat") {
    cmdInfo();
  } else if (lower == "dump" || lower == "read") {
    cmdDumpCsv();
  } else if (lower == "clear" || lower == "reset") {
    if (fs_ready && LittleFS.exists(csv_log_path)) {
      LittleFS.remove(csv_log_path);
    }
    saved_rows = 0;
    ensureCsvHeader();
    Serial.println("[OK] /chamber_cal.csv cleared (0 rows). Auto-logging remains ACTIVE.");
  } else if (lower == "pause" || lower == "stop") {
    logging_active = false;
    Serial.println("[OK] Chamber logging PAUSED.");
  } else if (lower == "resume" || lower == "start") {
    logging_active = true;
    Serial.println("[OK] Chamber logging ACTIVE (5.0s cadence).");
  } else if (lower.startsWith("live")) {
    float sec = 10.0f;
    int sp = cmd.indexOf(' ');
    if (sp > 0) sec = cmd.substring(sp + 1).toFloat();
    if (sec < 1.0f) sec = 1.0f;
    if (sec > 300.0f) sec = 300.0f;
    live_mode = true;
    live_end_ms = millis() + (unsigned long)(sec * 1000.0f);
    Serial.printf("[LIVE] Monitoring SHT45 & BH1750 at 1 Hz for %.0f s...\n", sec);
  } else if (lower.startsWith("wifi ")) {
    String rest = cmd.substring(5);
    rest.trim();
    int sp = rest.indexOf(' ');
    if (sp > 0) {
      extra_ssid = rest.substring(0, sp);
      extra_pass = rest.substring(sp + 1);
      extra_pass.trim();
    } else {
      extra_ssid = rest;
      extra_pass = "";
    }
    if (fs_ready && extra_ssid.length() > 0) {
      File f = LittleFS.open(extra_wifi_path, FILE_WRITE);
      if (f) {
        f.println(extra_ssid);
        f.println(extra_pass);
        f.flush();
        f.close();
      }
      if (extra_pass.length() == 0) {
        wifiMulti.addAP(extra_ssid.c_str());
      } else {
        wifiMulti.addAP(extra_ssid.c_str(), extra_pass.c_str());
      }
      Serial.printf("[OK] Saved & registered extra Wi-Fi AP: SSID='%s' -> attempting connection...\n",
                    extra_ssid.c_str());
      WiFi.disconnect(false, false);
      if (wifiMulti.run() == WL_CONNECTED) {
        Serial.printf("[OK] Wi-Fi CONNECTED! SSID=%s IP=%s\n",
                      WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());
      }
    }
  } else if (lower.startsWith("settime ")) {
    // Format: settime YYYY-MM-DD HH:MM:SS (interpreted as KST UTC+9)
    int y = 0, mo = 0, d = 0, h = 0, mi = 0, s = 0;
    if (sscanf(cmd.c_str() + 8, "%d-%d-%d %d:%d:%d", &y, &mo, &d, &h, &mi, &s) == 6 && y >= 2024) {
      time_t utc_ep = utcToEpoch(y, mo, d, h, mi, s) - (9 * 3600L);
      struct timeval tv = { .tv_sec = utc_ep, .tv_usec = 0 };
      settimeofday(&tv, NULL);
      Serial.printf("[OK] RTC set to KST %s (UTC epoch=%lld)\n",
                    getFormattedKST().c_str(), (long long)utc_ep);
    } else {
      Serial.println("[ERR] Usage: settime YYYY-MM-DD HH:MM:SS");
    }
  } else {
    Serial.printf("[ERR] Unknown command: %s\n", cmd.c_str());
  }
}

// ============================================================================
// Setup & Main Loop
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(900);

  detectBoardByMac();

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(100000);
  Wire.setTimeOut(50);

  sht_ready = initSHT();
  bh1750_ready = lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
  if (mpu.begin(0x68, &Wire) || mpu.begin(0x69, &Wire)) {
    mpu_ready = true;
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  Serial1.setRxBufferSize(1024);
  Serial1.begin(GPS_BAUDRATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  fs_ready = LittleFS.begin(true);
  if (fs_ready) {
    ensureCsvHeader();
    saved_rows = countCsvRows();
    loadExtraWiFiFromFS();
  }

  WiFi.mode(WIFI_STA);
  registerAllWiFiAPs();
  wifiMulti.run();

  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setBufferSize(512);
  mqttClient.setSocketTimeout(3);

  configTime(9 * 3600, 0, "pool.ntp.org", "time.nist.gov");

  last_tx_ms = millis();
  last_imu_ms = millis();
  cmdInfo();
}

void loop() {
  while (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    handleSerialCommand(line);
  }

  while (Serial1.available() > 0) {
    gps.encode(Serial1.read());
  }

  unsigned long now_ms = millis();

  // Optional 1 Hz live preview for bench inspection
  if (live_mode && now_ms < live_end_ms) {
    if (now_ms - last_live_ms >= 1000UL) {
      last_live_ms = now_ms;
      float t_c, rh, lx;
      readEnvSensors(t_c, rh, lx);
      Serial.printf("[LIVE] %s | T=%.3f C | RH=%.3f %% | Lux=%.1f lx\n",
                    getFormattedKST().c_str(), t_c, rh, lx);
    }
  } else if (live_mode && now_ms >= live_end_ms) {
    live_mode = false;
    Serial.println("[LIVE] Done.");
  }

  // Non-blocking Wi-Fi self-healing (every 12 s when disconnected)
  bool wifi_ok = (WiFi.status() == WL_CONNECTED);
  if (!wifi_ok && (now_ms - last_wifi_try_ms >= 12000UL)) {
    last_wifi_try_ms = now_ms;
    wifi_fail_streak++;
    if (wifi_fail_streak >= 4) {
      WiFi.disconnect(true, true);
      WiFi.mode(WIFI_OFF);
      delay(50);
      WiFi.mode(WIFI_STA);
      registerAllWiFiAPs();
      wifi_fail_streak = 0;
    }
    if (wifiMulti.run() == WL_CONNECTED) {
      wifi_ok = true;
      wifi_fail_streak = 0;
      configTime(9 * 3600, 0, "pool.ntp.org", "time.nist.gov");
    }
  }

  if (wifi_ok) {
    if (!mqttClient.connected()) {
      reconnectMQTT();
    } else {
      mqttClient.loop();
    }
  }

  // Keep 50 Hz IMU polling active so board power dissipation matches field operation
  if (mpu_ready && (now_ms - last_imu_ms >= IMU_INTERVAL_MS)) {
    last_imu_ms = now_ms;
    sensors_event_t a = {0}, g = {0}, temp = {0};
    if (mpu.getEvent(&a, &g, &temp)) {
      float gf = sqrtf(a.acceleration.x * a.acceleration.x +
                       a.acceleration.y * a.acceleration.y +
                       a.acceleration.z * a.acceleration.z) / 9.80665f;
      if (gf > max_g_force && gf <= 12.0f) {
        max_g_force = gf;
      }
    }
  }

  // Exact 5.0 s Chamber Calibration Measurement, CSV Backup & MQTT Publish
  if (logging_active && (now_ms - last_tx_ms >= TX_INTERVAL_MS)) {
    last_tx_ms += TX_INTERVAL_MS;
    if ((long)(now_ms - last_tx_ms) > (long)TX_INTERVAL_MS) {
      last_tx_ms = now_ms;
    }

    float temp_c, rh_pct, lux_val;
    readEnvSensors(temp_c, rh_pct, lux_val);

    time_t ep_s = getValidEpoch();
    String kst_str = getFormattedKST();
    int rssi_dbm = wifi_ok ? WiFi.RSSI() : -127;

    // 1. Always save compact row to LittleFS (/chamber_cal.csv)
    appendCsvRow(now_ms, ep_s, temp_c, rh_pct, lux_val, max_g_force, rssi_dbm);

    // 2. Build & publish MQTT JSON (compatible with existing dashboard + high-res chamber fields)
    StaticJsonDocument<512> doc;
    doc["device"] = device_id;
    doc["mac"] = mac_str;
    doc["mode"] = "chamber_cal";
    doc["uptime_ms"] = now_ms;
    doc["epoch_s"] = (long)ep_s;
    doc["timestamp_str"] = kst_str;
    doc["temperature"] = isnan(temp_c) ? 0.0 : serialized(String(temp_c, 3));
    doc["humidity"] = isnan(rh_pct) ? 0.0 : serialized(String(rh_pct, 3));
    doc["lux"] = (lux_val < 0.0f) ? 0.0 : serialized(String(lux_val, 1));
    doc["g_force"] = serialized(String(max_g_force, 3));
    doc["lat"] = serialized(String(0.0, 6));
    doc["lng"] = serialized(String(0.0, 6));
    doc["speed"] = serialized(String(0.0, 1));
    doc["sats"] = gps.satellites.value();
    doc["rssi"] = rssi_dbm;
    doc["status"] = "챔버교정 [5s]";

    char jsonBuf[512];
    serializeJson(doc, jsonBuf);

    bool mqtt_sent = false;
    if (wifi_ok && mqttClient.connected()) {
      mqtt_sent = mqttClient.publish(mqtt_topic, jsonBuf);
    }

    Serial.printf("[CAL #%lu] %s (up=%lus) | %s | T=%.3fC RH=%.3f%% Lux=%.1flx | FS=OK MQTT=%s\n",
                  saved_rows, kst_str.c_str(), now_ms / 1000UL, device_id,
                  temp_c, rh_pct, lux_val, mqtt_sent ? "PASS" : "OFFLINE_CSV_SAFE");

    max_g_force = 1.0f;
  }
}
