#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <WebServer.h> // 스마트폰 리모컨용 웹서버
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define USE_ESP32_WIFI true
#include <MySQL_Generic.h>

// --- 보안 설정 분리 ---
#include "secrets.h"

const char server_addr[] = "15.165.68.30"; // DB 호스트 IP
uint16_t db_port = 3306;
char user[] = "admin";
char db[] = "lab225";

// --- 핀 설정 (VN이 있는 왼쪽 열의 입출력 가능 핀) ---
// 주의: VP, VN(39), 34, 35는 입력 전용이므로 TX로 쓸 수 없습니다.
#define SCANNER_RX_PIN 32 // QR 스캐너의 TX 선 연결
#define SCANNER_TX_PIN 33 // QR 스캐너의 RX 선 연결
#define BUTTON_PIN 0      // 백업용: ESP32 기본 BOOT 버튼
#define SCAN_TRIGGER_PIN 25 // 메인: 스캔 및 단계 변경용 단일 택트 스위치
const byte triggerCmd[] = {0x04, 0xE4, 0x04, 0x00, 0xFF, 0x14}; // GM77용 START_DECODE 명령어
const byte setHostModeCmd[] = {0x07, 0xC6, 0x04, 0x08, 0x00, 0x8A, 0x08, 0xFE, 0x95}; // GM77 호스트 모드 설정 명령어

// OLED용 I2C 핀 및 크기 설정
#define OLED_SDA_PIN 21
#define OLED_SCL_PIN 22
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// 객체 명시적 생성
HardwareSerial ScannerSerial(2);
MySQL_Connection conn((Client *)&client);
WiFiMulti wifiMulti;
WebServer server(80); // 80번 포트에 웹서버 생성

// 현재 스캔 단계 및 모드 (기본값: AUTO 메인 모드)
bool isAutoMode = true;
String manualMode = "A10";

// ==========================================
// ⏱️ Latency(지연 시간) 정밀 측정용 전역 변수
// ==========================================
unsigned long t_trigger_start = 0; // 트리거 버튼 누른 시각
unsigned long t_decode_start = 0;  // 시리얼 수신 시작 시각 (자동 스캔 대비)
unsigned long t_decode_end = 0;    // 시리얼 디코드 수신 완료 시각
unsigned long t_db_start = 0;      // DB 쿼리 시작 시각
unsigned long t_db_end = 0;        // DB 저장 완료 시각

unsigned long last_decode_latency = 0; // 최근 측정된 Decode Latency (ms)
unsigned long last_total_latency = 0;  // 최근 측정된 Total Latency (ms)
unsigned long scan_counter = 0;        // 총 스캔 측정 횟수

// --- OLED 업데이트 함수 ---
void updateOLED(String msg = "", String fmId = "", String activeMode = "", unsigned long decLat = 0, unsigned long totLat = 0) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  // 상단: IP 주소 및 상태
  display.setCursor(0, 0);
  if (WiFi.status() == WL_CONNECTED) {
    display.print("WiFi: OK ");
    display.println(WiFi.localIP());
  } else {
    display.println("WiFi: Disconnected");
  }
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);

  // 중단: 현재 모드 및 박스 ID 표시
  display.setCursor(0, 13);
  if (isAutoMode) {
    display.setTextSize(1);
    display.print("Mode: [ AUTO ]");
    if (activeMode != "" && fmId != "") {
      display.setCursor(0, 24);
      display.print("Box #"); display.print(fmId);
      display.setCursor(0, 34);
      display.setTextSize(2);
      display.print("-> "); display.println(activeMode);
    } else {
      display.setCursor(0, 26);
      display.setTextSize(1);
      display.println("Ready to Auto-Scan..");
    }
  } else {
    display.setTextSize(1);
    display.print("Mode: [ MANUAL ]");
    display.setCursor(0, 25);
    display.setTextSize(2);
    display.println(manualMode);
  }

  // 하단: Latency 수치 또는 상태 메시지 표시
  display.setTextSize(1);
  display.setCursor(0, 52);
  if (decLat > 0 || totLat > 0) {
    display.printf("Dec:%lums Tot:%lums", decLat, totLat);
  } else if (msg != "") {
    display.println(msg);
  }

  display.display();
}

// --- 스마트폰 리모컨 UI 함수 ---
void handleRoot() {
  String html = "<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<style>body{font-family:'Malgun Gothic',sans-serif;text-align:center;margin-top:40px;background:#f4f4f9;} ";
  html += "button{padding:18px 36px;font-size:22px;background:#007BFF;color:white;border:none;border-radius:12px;box-shadow: 0 4px 6px rgba(0,0,0,0.1);} ";
  html += ".card{background:white;padding:20px;margin:20px auto;max-width:350px;border-radius:15px;box-shadow:0 2px 8px rgba(0,0,0,0.1);}</style></head><body>";
  html += "<h2>🚚 콜드체인 QR 스캐너</h2>";
  
  if (isAutoMode) {
    html += "<h1>현재 모드: <span style='color:#28A745;font-size:38px;'>🤖 AUTO (지능형)</span></h1>";
    html += "<p style='font-size:16px;color:#666;'>(스캔 시 DB 이력 기반 단계 자동 판단)</p>";
  } else {
    html += "<h1>현재 모드: <span style='color:#FF5722;font-size:38px;'>✋ MANUAL (" + manualMode + ")</span></h1>";
    if (manualMode == "A10") html += "<p style='font-size:16px;'>(수동: 박스 입고 단계)</p>";
    else if (manualMode == "A11") html += "<p style='font-size:16px;'>(수동: 세척 완료 단계)</p>";
    else if (manualMode == "A13") html += "<p style='font-size:16px;'>(수동: 포장 완료 단계)</p>";
    else if (manualMode == "A14") html += "<p style='font-size:16px;'>(수동: 저장 단계)</p>";
    else if (manualMode == "A15") html += "<p style='font-size:16px;'>(수동: 최종 출하 단계)</p>";
  }
  
  // 지연 시간 실시간 모니터링 카드
  html += "<div class='card'>";
  html += "<h3 style='margin:0 0 10px 0;'>⏱️ 최근 Latency 측정 결과</h3>";
  html += "<p style='margin:5px 0;'><strong>스캔 횟수:</strong> " + String(scan_counter) + " 회</p>";
  html += "<p style='margin:5px 0;'><strong>디코드 지연 (Decode):</strong> <span style='color:#007BFF;font-weight:bold;font-size:20px;'>" + String(last_decode_latency) + " ms</span></p>";
  html += "<p style='margin:5px 0;'><strong>전체 처리 시간 (Total):</strong> <span style='color:#28A745;font-weight:bold;font-size:20px;'>" + String(last_total_latency) + " ms</span></p>";
  html += "</div>";

  html += "<br><a href='/next'><button>👉 다음 모드/단계로 변경</button></a>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void cycleMode() {
  if (isAutoMode) {
    isAutoMode = false;
    manualMode = "A10";
  } else {
    if (manualMode == "A10") manualMode = "A11";
    else if (manualMode == "A11") manualMode = "A13";
    else if (manualMode == "A13") manualMode = "A14";
    else if (manualMode == "A14") manualMode = "A15";
    else if (manualMode == "A15") {
      isAutoMode = true; // 수동 모드 순환을 마치면 다시 AUTO 메인 모드로 복귀!
    }
  }
  
  if (isAutoMode) {
    Serial.println("\n🔄 모드 전환됨 -> 🤖 AUTO (지능형 자동 판단)");
    updateOLED("Mode: AUTO");
  } else {
    Serial.println("\n🔄 모드 전환됨 -> ✋ MANUAL (" + manualMode + ")");
    updateOLED("Mode: MANUAL " + manualMode);
  }
}

void handleNext() {
  cycleMode();
  server.sendHeader("Location", "/");
  server.send(303);
}

void setup() {
  Serial.begin(115200);

  // OLED 초기화
  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 20);
  display.println("Booting System...");
  display.display();
  
  // 시리얼 초기화 (GM77 기본 속도인 9600bps로 변경)
  ScannerSerial.begin(9600, SERIAL_8N1, SCANNER_RX_PIN, SCANNER_TX_PIN);
  
  // 버튼을 입력용으로 설정 (내부 풀업)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(SCAN_TRIGGER_PIN, INPUT_PULLUP); // 메인: 스캔 트리거 버튼 입력 설정

  // 다중 Wi-Fi 연결
  Serial.print("Connecting to WiFi...");
  
  // secrets.h에 등록된 모든 와이파이 추가
  for (int i = 0; i < num_wifi_networks; i++) {
    wifiMulti.addAP(wifi_networks[i].ssid, wifi_networks[i].password);
  }

  // 연결될 때까지 대기
  while (wifiMulti.run() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n✅ WiFi Connected!");
  Serial.print("Connected to SSID: ");
  Serial.println(WiFi.SSID());
  Serial.print("📱 스마트폰 리모컨 주소: http://");
  Serial.println(WiFi.localIP());

  // 웹서버 라우팅 및 시작
  server.on("/", handleRoot);
  server.on("/next", handleNext);
  server.begin();
  
  Serial.println("==================================================");
  Serial.println(" ColdChain Smart QR Scanner (Latency Benchmark)   ");
  Serial.println(" - Mode: AUTO / MANUAL Supported                  ");
  Serial.println(" - CSV Header: CSV_ROW,ScanID,FmID,Mode,Decode_ms,DB_ms,Total_ms");
  Serial.println("==================================================");

  // 스캐너를 호스트 모드로 자동 전환 시도
  ScannerSerial.write(0x00);
  delay(50);
  ScannerSerial.write(setHostModeCmd, sizeof(setHostModeCmd));
  delay(200);

  // GM77 호스트 모드 설정 응답(ACK 바이너리 데이터) 버퍼 비우기
  while (ScannerSerial.available()) {
    ScannerSerial.read();
  }

  updateOLED("System Ready");
}

// URL 파라미터 파싱
String getQueryParam(String url, String param) {
  int start = url.indexOf(param + "=");
  if (start == -1) return "NULL";
  start += param.length() + 1;
  int end = url.indexOf("&", start);
  if (end == -1) end = url.length();
  return "'" + url.substring(start, end) + "'";
}

// FmID 추출 (Streamlit 쿼리 파라미터 또는 기존 URL 패턴)
String getFmID(String url) {
  String fmId = getQueryParam(url, "FmID");
  if (fmId != "NULL" && fmId != "''") return fmId;
  
  int lastSlash = url.lastIndexOf('/');
  int questionMark = url.indexOf('?');
  if (lastSlash != -1 && questionMark != -1 && lastSlash < questionMark) {
    String legacyId = url.substring(lastSlash + 1, questionMark);
    if (legacyId.length() > 0) return "'" + legacyId + "'";
  }
  
  return "NULL";
}

void processScan(String rawData) {
  // 1. 스캔 데이터 수신 시 앞쪽에 섞인 GM77 ACK 응답 바이너리(0x04 등) 정제
  int httpIdx = rawData.indexOf("http");
  int modeIdx = rawData.indexOf("MODE:");

  if (httpIdx != -1) {
    rawData = rawData.substring(httpIdx);
  } else if (modeIdx != -1) {
    rawData = rawData.substring(modeIdx);
  } else {
    // 유효한 URL 및 MODE 명령어가 아닌 바이너리 신호는 무시
    return;
  }

  // 2. 모드 변경용 특수 QR 코드 인식
  if (rawData.startsWith("MODE:")) {
    String modeVal = rawData.substring(5);
    modeVal.trim();
    if (modeVal == "AUTO") {
      isAutoMode = true;
    } else {
      isAutoMode = false;
      manualMode = modeVal;
    }
    Serial.println("\n=================================");
    Serial.println("스캔 모드가 QR 스캔에 의해 변경되었습니다: " + (isAutoMode ? "AUTO" : manualMode));
    Serial.println("=================================\n");
    updateOLED("Mode Changed via QR");
    t_trigger_start = 0;
    return;
  }

  // 3. 일반 과일 QR URL 파싱
  String fmId = getFmID(rawData);
  if (fmId == "NULL" || fmId == "''") {
    Serial.println("❌ FmID를 찾을 수 없습니다.");
    updateOLED("No FmID!");
    t_trigger_start = 0;
    return;
  }

  String ac = getQueryParam(rawData, "AC");
  String frt = getQueryParam(rawData, "FrT");
  String vt = getQueryParam(rawData, "Vt");
  String ct = getQueryParam(rawData, "Ct");
  String hd = getQueryParam(rawData, "HD");
  String dd = getQueryParam(rawData, "DD");
  String qt = getQueryParam(rawData, "Qt");
  String mt = getQueryParam(rawData, "Mt");
  String hn = getQueryParam(rawData, "HN");
  String std = getQueryParam(rawData, "StD");
  String rp = getQueryParam(rawData, "Rp");

  // ⏱️ 디코드 지연 시간(Decode Latency) 계산
  unsigned long decode_latency = 0;
  if (t_trigger_start > 0) {
    decode_latency = t_decode_end - t_trigger_start;
  } else {
    decode_latency = t_decode_end - t_decode_start;
  }
  last_decode_latency = decode_latency;

  // 4. DB 접속 및 처리
  updateOLED("Connecting DB...");
  Serial.println("Connecting to AWS RDS...");
  
  t_db_start = millis(); // DB 처리 시작 시각

  if (conn.connect(server_addr, db_port, user, password_db)) {
    Serial.println("✅ AWS DB Connection Success!");
    MySQL_Query query_executor(&conn);
    
    query_executor.execute("SET time_zone = '+09:00'");

    // 타겟 모드 결정 (AUTO 메인 vs MANUAL 수동)
    String targetMode = "";
    if (isAutoMode) {
      // DB에서 해당 FmID의 최신 Lo 상태 조회
      String checkQuery = "SELECT Lo FROM lab225.qr WHERE FmID = " + fmId + " ORDER BY id DESC LIMIT 1";
      Serial.println("🔍 DB에서 FmID (" + fmId + ")의 이전 이력 조회 중...");
      String lastLo = "NONE";
      if (query_executor.execute(checkQuery.c_str())) {
        column_names *cols = query_executor.get_columns();
        row_values *row = query_executor.get_next_row();
        if (row != NULL && row->values[0] != NULL) {
          lastLo = String(row->values[0]);
          lastLo.trim();
        }
        while (row != NULL) { row = query_executor.get_next_row(); }
        query_executor.close();
      }

      Serial.println("💡 DB 이전 최신 이력(Lo): " + lastLo);
      if (lastLo == "NONE" || lastLo == "A00") targetMode = "A10";
      else if (lastLo == "A10") targetMode = "A11";
      else if (lastLo == "A11" || lastLo == "A12") targetMode = "A13";
      else if (lastLo == "A13") targetMode = "A14";
      else if (lastLo == "A14") targetMode = "A15";
      else if (lastLo == "A15") {
        Serial.println("⚠️ 이미 최종 출하(A15)가 완료된 상자입니다.");
        updateOLED("Already Completed!", fmId, "A15");
        conn.close();
        t_trigger_start = 0;
        return;
      }
      Serial.println("🤖 [AUTO] 지능형 판단 결과 단계: " + targetMode);
    } else {
      targetMode = manualMode;
      Serial.println("✋ [MANUAL] 수동 지정 단계: " + targetMode);
    }

    // 센서 데이터 서브쿼리
    String sensor_sub = "(SELECT lat, lng, temperature, humidity FROM lab225.sensor_data ORDER BY id DESC LIMIT 1) S";

    String query = "";
    if (targetMode == "A10") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, Lat, lon) ";
      query += "SELECT 'A10', " + ac + ", " + fmId + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", " + rp + ", NOW(), S.lat, S.lng ";
      query += "FROM " + sensor_sub;
    }
    else if (targetMode == "A11") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, Lat, lon) ";
      query += "SELECT 'A11', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, NOW(), S.lat, S.lng ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.FmID = " + fmId + " AND Q.APC_AD IS NOT NULL ORDER BY Q.APC_AD DESC LIMIT 1";
    }
    else if (targetMode == "A12") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, Lat, lon) ";
      query += "SELECT 'A12', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, NOW(), S.lat, S.lng ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A11' AND Q.FmID = " + fmId + " ORDER BY Q.APC_WD DESC LIMIT 1";
    }
    else if (targetMode == "A13") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A13', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, Q.APC_RT, NOW(), S.lat, S.lng, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A12' AND Q.FmID = " + fmId + " ORDER BY Q.APC_RT DESC LIMIT 1";
    }
    else if (targetMode == "A14") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A14', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, Q.APC_RT, Q.APC_PT, NOW(), S.temperature, S.humidity, S.lat, S.lng, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A13' AND Q.FmID = " + fmId + " ORDER BY Q.APC_PT DESC LIMIT 1";
    }
    else if (targetMode == "A15") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, APC_OP, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A15', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, Q.APC_RT, Q.APC_PT, Q.APC_StD, NOW(), S.lat, S.lng, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A14' AND Q.FmID = " + fmId + " ORDER BY Q.APC_StD DESC LIMIT 1";
    }

    bool isSuccess = query_executor.execute(query.c_str());
    t_db_end = millis(); // DB 처리 완료 시각

    // ⏱️ 지연 시간 계산 (ms)
    unsigned long db_latency = t_db_end - t_db_start;
    unsigned long total_latency = 0;
    if (t_trigger_start > 0) {
      total_latency = t_db_end - t_trigger_start;
    } else {
      total_latency = decode_latency + db_latency;
    }
    
    last_total_latency = total_latency;
    scan_counter++;

    if (isSuccess) {
      Serial.println("✅ DB 저장 성공! (단계: " + targetMode + ")");
      updateOLED("DB Save OK!", fmId, targetMode, decode_latency, total_latency);
    } else {
      Serial.println("❌ DB 저장 실패: 쿼리 오류 또는 이전 단계 데이터 없음");
      updateOLED("DB Save FAIL!", fmId, targetMode, decode_latency, total_latency);
    }

    // ==========================================
    // ⏱️ Latency 결과 리포트 출력
    // ==========================================
    Serial.println("==================================================");
    Serial.printf("⏱️ [스캔 #%lu Latency 리포트]\n", scan_counter);
    Serial.printf(" - 박스 ID (FmID)       : %s\n", fmId.c_str());
    Serial.printf(" - 진행 단계 (Mode)     : %s\n", targetMode.c_str());
    Serial.printf(" - 디코드 지연 (Decode) : %lu ms\n", decode_latency);
    Serial.printf(" - 클라우드 DB 지연     : %lu ms\n", db_latency);
    Serial.printf(" - 전체 처리 시간 (Total): %lu ms\n", total_latency);
    Serial.println("--------------------------------------------------");
    // 엑셀/파이썬 데이터 분석용 CSV 포맷 출력
    Serial.printf("CSV_ROW,%lu,%s,%s,%lu,%lu,%lu\n", scan_counter, fmId.c_str(), targetMode.c_str(), decode_latency, db_latency, total_latency);
    Serial.println("==================================================\n");

    conn.close();
  } else {
    Serial.println("❌ DB 연결 실패 (AWS)");
    updateOLED("DB Conn FAIL!");
  }

  // 다음 측정을 위해 트리거 시작 시각 리셋
  t_trigger_start = 0;
}

// 시리얼에서 0x00(NUL) 및 제어 바이너리를 걸러내고 9600bps 속도에 맞춰 전체 URL(최대 1.5초)을 완전하게 수신하는 함수
String readCleanScannerData() {
  String result = "";
  unsigned long start = millis();
  unsigned long lastCharTime = millis();

  while (millis() - start < 1500) {
    if (ScannerSerial.available()) {
      char c = (char)ScannerSerial.read();
      lastCharTime = millis();
      
      if (c == '\r' || c == '\n') {
        if (result.length() > 0) break;
      } else if (c >= 32 && c <= 126) {
        result += c;
      }
    } else {
      if (result.length() > 0 && (millis() - lastCharTime > 150)) {
        break;
      }
      delay(5);
    }
  }
  return result;
}

unsigned long lastButtonPress = 0; // 백업 BOOT 버튼 디바운스용

// 단일 택트 스위치용 더블클릭 감지 변수
int lastTriggerState = HIGH;
unsigned long triggerPressTime = 0;
int triggerClickCount = 0;
const unsigned long doubleClickDelay = 350; // 더블클릭 감지 제한 시간 (350ms)

void loop() {
  // 1. 메인 택트 스위치(GPIO 25) 처리 (싱글클릭: 스캔 / 더블클릭: 모드 및 단계 변경)
  int currentTriggerState = digitalRead(SCAN_TRIGGER_PIN);
  
  if (currentTriggerState == LOW && lastTriggerState == HIGH) {
    if (triggerClickCount == 0) {
      triggerPressTime = millis();
    }
    triggerClickCount++;
    delay(50);
  }
  lastTriggerState = currentTriggerState;

  if (triggerClickCount > 0 && (millis() - triggerPressTime > doubleClickDelay)) {
    if (triggerClickCount == 1) {
      // 1회 클릭: GM77 스캔 트리거 명령어 전송
      Serial.println("\n🔫 1회 클릭: GM77 스캔 명령어 전송");
      t_trigger_start = millis(); // ⏱️ [트리거 시작 시점 기록]
      
      ScannerSerial.write(0x00);
      delay(50);
      ScannerSerial.write(triggerCmd, sizeof(triggerCmd));
    } 
    else if (triggerClickCount >= 2) {
      // 2회 클릭 (더블클릭): AUTO ↔ MANUAL 모드 및 단계 순환 전환
      cycleMode();
    }
    triggerClickCount = 0;
  }

  // 2. 백업용 BOOT 버튼(GPIO 0) 처리 (모드 순환 전환)
  if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > 500) {
    cycleMode();
    lastButtonPress = millis();
  }

  // 3. 스캐너 데이터 수신 처리 (NUL 및 바이너리 제어문자 제거 정제)
  if (ScannerSerial.available()) {
    t_decode_start = millis(); // 패킷 도착 감지 시점
    delay(50); // 패킷 수신 완료 대기
    String scannedData = readCleanScannerData();
    t_decode_end = millis(); // ⏱️ [디코드 및 시리얼 수신 완료 시점]
    
    scannedData.trim();
    if (scannedData.length() > 0) {
      Serial.println("\n📷 스캔된 데이터: " + scannedData);
      processScan(scannedData);
    }
  }

  // 웹서버 클라이언트 처리
  server.handleClient();
}
