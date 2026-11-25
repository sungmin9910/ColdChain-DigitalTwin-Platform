#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <LittleFS.h>
#include <esp_mac.h>
#include <math.h>

// ============================================================
// FDT Accelerometer High-Speed Calibration & Drop-Test Firmware
// Target: CarrierBoard Beetle ESP32-C6 + GY-521 (MPU6050)
//   - Range: +-16 G (MPU6050_RANGE_16_G)
//   - Gyro:  +-2000 deg/s (MPU6050_RANGE_2000_DEG)
//   - LPF:   260 Hz (MPU6050_BAND_260_HZ)
//   - Rate:  400 Hz (2500 us exact period, I2C 400 kHz)
//   - Mode 1 (USB): 6-Position Static Calibration (`static <sec>`)
//   - Mode 2 (Wireless Battery): Auto-Armed Pre/Post-Trigger Drop Capture -> LittleFS
// ============================================================

#define I2C_SDA_PIN         19
#define I2C_SCL_PIN         20
#define G_TO_MS2            9.80665f
#define RAD_TO_DEG_F        57.2957795f

#define SAMPLE_RATE_HZ      400
#define SAMPLE_PERIOD_US    (1000000UL / SAMPLE_RATE_HZ)  // 2500 us

// Drop capture window: 1.0 s pre-trigger + 1.5 s post-trigger = 2.5 s (1000 samples)
#define PRE_SAMPLES         400
#define POST_SAMPLES        600
#define DROP_TOTAL_SAMPLES  (PRE_SAMPLES + POST_SAMPLES)

// Static capture buffer: up to 10.0 s at 400 Hz = 4000 samples (~112 KB SRAM)
#define STATIC_MAX_SAMPLES  4000

// Drop detection thresholds (tunable via serial if needed)
#define FREEFALL_THRESH_G   0.45f   // |a| < 0.45 g
#define FREEFALL_CONSEC_N   5       // 5 samples = 12.5 ms continuous free-fall
#define IMPACT_THRESH_G     2.40f   // |a| > 2.40 g direct impact trigger
#define COOLDOWN_MS         3000    // 3 s cooldown after each saved drop
#define AUTO_ARM_DELAY_MS   8000    // Auto-arm 8 s after boot if no USB command arrives
#define MAX_DROP_FILES      45      // ~28 KB/file -> ~1.26 MB max

#pragma pack(push, 1)
struct CalSample {
  uint32_t t_us;
  float ax_g;
  float ay_g;
  float az_g;
  float gx_dps;
  float gy_dps;
  float gz_dps;
};

struct DropHeader {
  uint32_t magic;         // 0x46445431 ('FDT1')
  uint16_t sample_rate;   // 400
  uint16_t num_samples;   // 1000
  uint16_t pre_samples;   // 400
  uint16_t trigger_type;  // 1=FREEFALL, 2=IMPACT
  uint32_t boot_ms;       // millis() at trigger
  float peak_g;
  float min_g;
  float freefall_ms;
  float max_gyro_dps;
};
#pragma pack(pop)

static const uint32_t DROP_MAGIC = 0x46445431UL;

Adafruit_MPU6050 mpu;
bool mpu_ready = false;
bool fs_ready = false;
uint8_t mpu_addr = 0;

// Buffers in static SRAM
static CalSample pre_ring[PRE_SAMPLES];
static CalSample drop_buf[DROP_TOTAL_SAMPLES];
static CalSample static_buf[STATIC_MAX_SAMPLES];

int pre_head = 0;
int pre_count = 0;

bool armed = false;
bool usb_command_seen = false;
bool capturing_drop = false;
int post_captured = 0;
uint16_t cur_trigger_type = 0;
uint32_t cur_trigger_boot_ms = 0;
int freefall_streak = 0;
unsigned long last_drop_done_ms = 0;
unsigned long boot_time_ms = 0;
unsigned long next_sample_us = 0;

// Live monitor state
bool live_mode = false;
unsigned long live_end_ms = 0;
unsigned long last_live_print_ms = 0;

// Device identification
char mac_str[20] = "UNKNOWN";

void initMacString() {
  uint8_t mac[6] = {0};
  esp_efuse_mac_get_default(mac);
  snprintf(mac_str, sizeof(mac_str), "%02X:%02X:%02X:%02X:%02X:%02X",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

bool initMPU6050() {
  if (mpu.begin(0x68, &Wire)) {
    mpu_addr = 0x68;
  } else if (mpu.begin(0x69, &Wire)) {
    mpu_addr = 0x69;
  } else {
    return false;
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setGyroRange(MPU6050_RANGE_2000_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_260_HZ);
  return true;
}

inline bool readSample(CalSample &s) {
  sensors_event_t a, g, temp;
  if (!mpu.getEvent(&a, &g, &temp)) return false;
  s.t_us = micros();
  s.ax_g = a.acceleration.x / G_TO_MS2;
  s.ay_g = a.acceleration.y / G_TO_MS2;
  s.az_g = a.acceleration.z / G_TO_MS2;
  s.gx_dps = g.gyro.x * RAD_TO_DEG_F;
  s.gy_dps = g.gyro.y * RAD_TO_DEG_F;
  s.gz_dps = g.gyro.z * RAD_TO_DEG_F;
  return true;
}

inline float sampleMagG(const CalSample &s) {
  return sqrtf(s.ax_g * s.ax_g + s.ay_g * s.ay_g + s.az_g * s.az_g);
}

inline float sampleGyroMag(const CalSample &s) {
  return sqrtf(s.gx_dps * s.gx_dps + s.gy_dps * s.gy_dps + s.gz_dps * s.gz_dps);
}

int countDropFiles() {
  if (!fs_ready) return 0;
  int count = 0;
  for (int i = 1; i <= MAX_DROP_FILES; i++) {
    char path[24];
    snprintf(path, sizeof(path), "/drop_%03d.bin", i);
    if (LittleFS.exists(path)) count++;
  }
  return count;
}

int nextDropIndex() {
  for (int i = 1; i <= MAX_DROP_FILES; i++) {
    char path[24];
    snprintf(path, sizeof(path), "/drop_%03d.bin", i);
    if (!LittleFS.exists(path)) return i;
  }
  return -1;
}

void saveDropBufferToFS(int total_n) {
  if (!fs_ready) {
    Serial.println("[ERR] LittleFS not mounted!");
    return;
  }
  int idx = nextDropIndex();
  if (idx < 0) {
    Serial.println("[WARN] Drop storage full (MAX_DROP_FILES reached). Run 'clear' after dumping.");
    return;
  }

  float peak_g = 0.0f;
  float min_g = 99.0f;
  float max_gyro = 0.0f;
  int ff_samples = 0;
  int ff_max_run = 0;
  int ff_cur_run = 0;

  for (int i = 0; i < total_n; i++) {
    float mg = sampleMagG(drop_buf[i]);
    float gy = sampleGyroMag(drop_buf[i]);
    if (mg > peak_g) peak_g = mg;
    if (mg < min_g) min_g = mg;
    if (gy > max_gyro) max_gyro = gy;
    if (mg < FREEFALL_THRESH_G) {
      ff_cur_run++;
      if (ff_cur_run > ff_max_run) ff_max_run = ff_cur_run;
    } else {
      ff_cur_run = 0;
    }
  }
  ff_samples = ff_max_run;

  DropHeader hdr;
  hdr.magic = DROP_MAGIC;
  hdr.sample_rate = SAMPLE_RATE_HZ;
  hdr.num_samples = (uint16_t)total_n;
  hdr.pre_samples = (uint16_t)(total_n > POST_SAMPLES ? (total_n - POST_SAMPLES) : 0);
  hdr.trigger_type = cur_trigger_type;
  hdr.boot_ms = cur_trigger_boot_ms;
  hdr.peak_g = peak_g;
  hdr.min_g = min_g;
  hdr.freefall_ms = (ff_samples * 1000.0f) / SAMPLE_RATE_HZ;
  hdr.max_gyro_dps = max_gyro;

  char path[24];
  snprintf(path, sizeof(path), "/drop_%03d.bin", idx);
  File f = LittleFS.open(path, FILE_WRITE);
  if (!f) {
    Serial.printf("[ERR] Failed to open %s for write\n", path);
    return;
  }
  f.write((const uint8_t *)&hdr, sizeof(hdr));
  f.write((const uint8_t *)drop_buf, sizeof(CalSample) * total_n);
  f.flush();
  f.close();

  Serial.printf("[DROP_SAVED] id=%03d trig=%s peak=%.2fG min=%.2fG ff=%.1fms gyro=%.1fdps samples=%d\n",
                idx,
                (hdr.trigger_type == 1 ? "FREEFALL" : "IMPACT"),
                hdr.peak_g, hdr.min_g, hdr.freefall_ms, hdr.max_gyro_dps, total_n);
}

void cmdInfo() {
  Serial.println("=== FDT_ACCEL_CAL_400HZ ===");
  Serial.printf("MAC: %s\n", mac_str);
  Serial.printf("MPU6050: %s (addr=0x%02X, range=+-16G, gyro=+-2000dps, LPF=260Hz, rate=%dHz)\n",
                mpu_ready ? "OK" : "FAIL", mpu_addr, SAMPLE_RATE_HZ);
  Serial.printf("STATE: %s\n", armed ? "ARMED" : "DISARMED");
  if (fs_ready) {
    Serial.printf("LITTLEFS: used=%u / total=%u bytes, drops=%d\n",
                  (unsigned int)LittleFS.usedBytes(),
                  (unsigned int)LittleFS.totalBytes(),
                  countDropFiles());
  } else {
    Serial.println("LITTLEFS: FAIL");
  }
  if (mpu_ready) {
    CalSample s;
    if (readSample(s)) {
      Serial.printf("LIVE: ax=%.4f ay=%.4f az=%.4f |a|=%.4f G  gx=%.2f gy=%.2f gz=%.2f dps\n",
                    s.ax_g, s.ay_g, s.az_g, sampleMagG(s), s.gx_dps, s.gy_dps, s.gz_dps);
    }
  }
  Serial.println("COMMANDS: info | live <sec> | static <sec> | arm | disarm | list | dump <id> | clear");
  Serial.println("=== END_INFO ===");
}

void cmdStaticCapture(float seconds) {
  if (!mpu_ready) {
    Serial.println("[ERR] MPU6050 not ready!");
    return;
  }
  armed = false;
  capturing_drop = false;

  int n = (int)(seconds * SAMPLE_RATE_HZ);
  if (n < 40) n = 40;
  if (n > STATIC_MAX_SAMPLES) n = STATIC_MAX_SAMPLES;

  Serial.printf("---STATIC_START samples=%d rate=%d---\n", n, SAMPLE_RATE_HZ);
  unsigned long t_next = micros();
  for (int i = 0; i < n; i++) {
    while ((long)(micros() - t_next) < 0) {
      // tight wait for clean 2500 us cadence
    }
    t_next += SAMPLE_PERIOD_US;
    readSample(static_buf[i]);
  }

  uint32_t t0 = static_buf[0].t_us;
  Serial.println("t_ms,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps");
  for (int i = 0; i < n; i++) {
    float t_ms = (static_buf[i].t_us - t0) / 1000.0f;
    Serial.printf("%.3f,%.5f,%.5f,%.5f,%.2f,%.2f,%.2f\n",
                  t_ms,
                  static_buf[i].ax_g, static_buf[i].ay_g, static_buf[i].az_g,
                  static_buf[i].gx_dps, static_buf[i].gy_dps, static_buf[i].gz_dps);
  }
  Serial.println("---STATIC_END---");
}

void cmdListDrops() {
  Serial.println("---DROP_LIST_START---");
  Serial.println("id,trigger,boot_ms,samples,peak_g,min_g,freefall_ms,max_gyro_dps");
  if (fs_ready) {
    for (int i = 1; i <= MAX_DROP_FILES; i++) {
      char path[24];
      snprintf(path, sizeof(path), "/drop_%03d.bin", i);
      if (!LittleFS.exists(path)) continue;
      File f = LittleFS.open(path, FILE_READ);
      if (!f) continue;
      DropHeader hdr;
      if (f.read((uint8_t *)&hdr, sizeof(hdr)) == sizeof(hdr) && hdr.magic == DROP_MAGIC) {
        Serial.printf("%d,%s,%lu,%u,%.3f,%.3f,%.1f,%.1f\n",
                      i,
                      (hdr.trigger_type == 1 ? "FREEFALL" : "IMPACT"),
                      (unsigned long)hdr.boot_ms,
                      (unsigned int)hdr.num_samples,
                      hdr.peak_g, hdr.min_g, hdr.freefall_ms, hdr.max_gyro_dps);
      }
      f.close();
    }
  }
  Serial.println("---DROP_LIST_END---");
}

void cmdDumpDrop(int id) {
  if (!fs_ready) {
    Serial.println("[ERR] LittleFS not ready!");
    return;
  }
  char path[24];
  snprintf(path, sizeof(path), "/drop_%03d.bin", id);
  if (!LittleFS.exists(path)) {
    Serial.printf("[ERR] Drop %03d not found\n", id);
    return;
  }
  File f = LittleFS.open(path, FILE_READ);
  if (!f) {
    Serial.printf("[ERR] Cannot open %s\n", path);
    return;
  }
  DropHeader hdr;
  if (f.read((uint8_t *)&hdr, sizeof(hdr)) != sizeof(hdr) || hdr.magic != DROP_MAGIC) {
    Serial.printf("[ERR] Invalid header in %s\n", path);
    f.close();
    return;
  }
  Serial.printf("---DROP_DUMP_START id=%d rate=%u samples=%u pre=%u trig=%s peak=%.3f min=%.3f ff=%.1f gyro=%.1f---\n",
                id, (unsigned int)hdr.sample_rate, (unsigned int)hdr.num_samples,
                (unsigned int)hdr.pre_samples,
                (hdr.trigger_type == 1 ? "FREEFALL" : "IMPACT"),
                hdr.peak_g, hdr.min_g, hdr.freefall_ms, hdr.max_gyro_dps);
  Serial.println("t_ms,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps");

  CalSample s;
  uint32_t t0 = 0;
  for (uint16_t i = 0; i < hdr.num_samples; i++) {
    if (f.read((uint8_t *)&s, sizeof(s)) != sizeof(s)) break;
    if (i == 0) t0 = s.t_us;
    float t_ms = (s.t_us - t0) / 1000.0f;
    Serial.printf("%.3f,%.5f,%.5f,%.5f,%.2f,%.2f,%.2f\n",
                  t_ms, s.ax_g, s.ay_g, s.az_g, s.gx_dps, s.gy_dps, s.gz_dps);
  }
  f.close();
  Serial.printf("---DROP_DUMP_END id=%d---\n", id);
}

void cmdClearDrops() {
  int removed = 0;
  if (fs_ready) {
    for (int i = 1; i <= MAX_DROP_FILES; i++) {
      char path[24];
      snprintf(path, sizeof(path), "/drop_%03d.bin", i);
      if (LittleFS.exists(path)) {
        LittleFS.remove(path);
        removed++;
      }
    }
  }
  Serial.printf("[OK] Cleared %d drop files.\n", removed);
}

void handleSerialCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;
  usb_command_seen = true;
  live_mode = false;

  String lower = cmd;
  lower.toLowerCase();

  if (lower == "info" || lower == "status") {
    cmdInfo();
  } else if (lower.startsWith("static")) {
    float sec = 8.0f;
    int sp = lower.indexOf(' ');
    if (sp > 0) {
      float v = lower.substring(sp + 1).toFloat();
      if (v > 0.2f && v <= 10.0f) sec = v;
    }
    cmdStaticCapture(sec);
  } else if (lower.startsWith("live")) {
    float sec = 10.0f;
    int sp = lower.indexOf(' ');
    if (sp > 0) {
      float v = lower.substring(sp + 1).toFloat();
      if (v > 0.5f && v <= 120.0f) sec = v;
    }
    armed = false;
    live_mode = true;
    live_end_ms = millis() + (unsigned long)(sec * 1000.0f);
    Serial.printf("[LIVE] Monitoring for %.1fs (10Hz)...\n", sec);
  } else if (lower == "arm") {
    pre_head = 0;
    pre_count = 0;
    capturing_drop = false;
    freefall_streak = 0;
    armed = true;
    next_sample_us = micros();
    Serial.println("[OK] ARMED (400Hz auto drop capture active)");
  } else if (lower == "disarm" || lower == "stop") {
    armed = false;
    capturing_drop = false;
    Serial.println("[OK] DISARMED");
  } else if (lower == "list") {
    armed = false;
    cmdListDrops();
  } else if (lower.startsWith("dump")) {
    armed = false;
    int sp = lower.indexOf(' ');
    if (sp > 0) {
      int id = lower.substring(sp + 1).toInt();
      cmdDumpDrop(id);
    } else {
      Serial.println("[ERR] Usage: dump <id>");
    }
  } else if (lower == "clear") {
    armed = false;
    cmdClearDrops();
  } else {
    Serial.printf("[ERR] Unknown command: %s\n", cmd.c_str());
  }
}

void setup() {
  Serial.begin(115200);
  delay(800);

  initMacString();

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(400000);  // 400 kHz Fast-Mode I2C for stable 400 Hz MPU6050 polling

  mpu_ready = initMPU6050();
  fs_ready = LittleFS.begin(true);

  boot_time_ms = millis();
  next_sample_us = micros();

  cmdInfo();
  Serial.println("[BOOT] Wireless auto-arm in 8s unless a USB command is received...");
}

void loop() {
  // 1. Check incoming USB serial commands
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    handleSerialCommand(line);
  }

  // 2. Auto-arm on battery boot (no USB command received within 8s)
  if (!armed && !usb_command_seen && !live_mode && mpu_ready) {
    if (millis() - boot_time_ms >= AUTO_ARM_DELAY_MS) {
      pre_head = 0;
      pre_count = 0;
      capturing_drop = false;
      freefall_streak = 0;
      armed = true;
      next_sample_us = micros();
      Serial.println("[AUTO-ARM] 400Hz wireless drop capture ARMED!");
    }
  }

  // 3. Live alignment monitor (10 Hz)
  if (live_mode && mpu_ready) {
    unsigned long now_ms = millis();
    if (now_ms >= live_end_ms) {
      live_mode = false;
      Serial.println("[LIVE] Done.");
    } else if (now_ms - last_live_print_ms >= 100) {
      last_live_print_ms = now_ms;
      CalSample s;
      if (readSample(s)) {
        Serial.printf("ax=%+.4f  ay=%+.4f  az=%+.4f  |a|=%.4f G  (gx=%+.1f gy=%+.1f gz=%+.1f)\n",
                      s.ax_g, s.ay_g, s.az_g, sampleMagG(s), s.gx_dps, s.gy_dps, s.gz_dps);
      }
    }
    return;
  }

  // 4. Armed 400 Hz pre/post-trigger drop capture
  if (armed && mpu_ready) {
    unsigned long now_us = micros();
    if ((long)(now_us - next_sample_us) >= 0) {
      next_sample_us += SAMPLE_PERIOD_US;
      // Guard against long drift after flash write
      if ((long)(now_us - next_sample_us) > 50000L) {
        next_sample_us = now_us + SAMPLE_PERIOD_US;
      }

      CalSample s;
      if (!readSample(s)) return;
      float mag = sampleMagG(s);

      if (!capturing_drop) {
        // Store in circular pre-trigger ring buffer
        pre_ring[pre_head] = s;
        pre_head = (pre_head + 1) % PRE_SAMPLES;
        if (pre_count < PRE_SAMPLES) pre_count++;

        // Cooldown guard after previous drop
        if (millis() - last_drop_done_ms < COOLDOWN_MS) {
          freefall_streak = 0;
          return;
        }

        // Check triggers
        if (mag < FREEFALL_THRESH_G) {
          freefall_streak++;
        } else {
          freefall_streak = 0;
        }

        uint16_t trig = 0;
        if (freefall_streak >= FREEFALL_CONSEC_N) {
          trig = 1;  // FREEFALL
        } else if (mag > IMPACT_THRESH_G) {
          trig = 2;  // IMPACT
        }

        if (trig != 0) {
          // Copy pre-trigger ring in chronological order into drop_buf
          int start_idx = (pre_count == PRE_SAMPLES) ? pre_head : 0;
          for (int i = 0; i < pre_count; i++) {
            drop_buf[i] = pre_ring[(start_idx + i) % PRE_SAMPLES];
          }
          capturing_drop = true;
          post_captured = 0;
          cur_trigger_type = trig;
          cur_trigger_boot_ms = millis();
          freefall_streak = 0;
        }
      } else {
        // Append post-trigger samples
        int dst = pre_count + post_captured;
        if (dst < DROP_TOTAL_SAMPLES) {
          drop_buf[dst] = s;
        }
        post_captured++;

        if (post_captured >= POST_SAMPLES) {
          int total_n = pre_count + post_captured;
          if (total_n > DROP_TOTAL_SAMPLES) total_n = DROP_TOTAL_SAMPLES;
          saveDropBufferToFS(total_n);
          capturing_drop = false;
          pre_head = 0;
          pre_count = 0;
          last_drop_done_ms = millis();
          next_sample_us = micros() + SAMPLE_PERIOD_US;
        }
      }
    }
  }
}
