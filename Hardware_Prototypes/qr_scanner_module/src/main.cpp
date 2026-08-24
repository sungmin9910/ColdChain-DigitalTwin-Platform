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
#define BUTTON_PIN 0      // ESP32 기본 BOOT 버튼

// 객체 명시적 생성
HardwareSerial ScannerSerial(2);
MySQL_Connection conn((Client *)&client);
WiFiMulti wifiMulti;
WebServer server(80); // 80번 포트에 웹서버 생성

// --- OLED 설정 ---
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// 현재 스캔 단계 및 모드 (기본값: AUTO 메인 모드)
bool isAutoMode = true;
String manualMode = "A10";

// --- 중복 스캔 방지용 변수 ---
String lastScannedData = "";
unsigned long lastScanTime = 0;
const unsigned long SCAN_DEBOUNCE_INTERVAL = 5000; // 동일 바코드 중복 스캔 방지 시간 (5초)

// --- OLED 업데이트 함수 ---
void updateOLED(String msg = "", String fmId = "", String activeMode = "") {
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

  // 중단: 현재 모드 표시
  display.setCursor(0, 14);
  if (isAutoMode) {
    display.setTextSize(1);
    display.println("Mode: [ AUTO ]");
    if (activeMode != "" && fmId != "") {
      display.setCursor(0, 26);
      display.print("Box #"); display.print(fmId);
      display.setCursor(0, 36);
      display.setTextSize(2);
      display.print("-> "); display.println(activeMode);
    } else {
      display.setCursor(0, 30);
      display.setTextSize(1);
      display.println("Ready to Auto-Scan..");
    }
  } else {
    display.setTextSize(1);
    display.print("Mode: [ MANUAL ]");
    display.setCursor(0, 28);
    display.setTextSize(3);
    display.println(manualMode);
  }

  // 하단: 추가 메시지 (스캔 성공, DB 저장 등)
  if (msg != "") {
    display.setCursor(0, 54);
    display.setTextSize(1);
    display.println(msg);
  }

  display.display();
}

// --- 스마트폰 리모컨 UI 함수 ---
void handleRoot() {
  String html = "<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<style>body{font-family:'Malgun Gothic',sans-serif;text-align:center;margin-top:50px;background:#f4f4f9;} ";
  html += "button{padding:20px 40px;font-size:24px;background:#007BFF;color:white;border:none;border-radius:15px;box-shadow: 0 4px 6px rgba(0,0,0,0.1);}</style></head><body>";
  html += "<h2>🚚 콜드체인 QR 스캐너</h2>";
  
  if (isAutoMode) {
    html += "<h1>현재 모드: <span style='color:#28A745;font-size:45px;'>🤖 AUTO (지능형)</span></h1>";
    html += "<p style='font-size:20px;'>(스캔 시 DB 이력 기반 단계 자동 판단)</p>";
  } else {
    html += "<h1>현재 모드: <span style='color:#FF5722;font-size:45px;'>✋ MANUAL (" + manualMode + ")</span></h1>";
    if (manualMode == "A10") html += "<p style='font-size:20px;'>(수동: 박스 입고 단계)</p>";
    else if (manualMode == "A11") html += "<p style='font-size:20px;'>(수동: 세척 완료 단계)</p>";
    else if (manualMode == "A13") html += "<p style='font-size:20px;'>(수동: 포장 완료 단계)</p>";
    else if (manualMode == "A14") html += "<p style='font-size:20px;'>(수동: 저장 단계)</p>";
    else if (manualMode == "A15") html += "<p style='font-size:20px;'>(수동: 최종 출하 단계)</p>";
  }
  
  html += "<br><br><a href='/next'><button>👉 다음 모드/단계로 변경</button></a>";
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
  
  // OLED 초기화 (I2C 핀: SDA=21, SCL=22)
  Wire.begin();
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 20);
  display.println("Booting System...");
  display.display();

  // 시리얼 초기화 (GM77 모듈 기본 통신 속도 9600bps로 변경)
  ScannerSerial.begin(9600, SERIAL_8N1, SCANNER_RX_PIN, SCANNER_TX_PIN);
  
  // 버튼을 입력용으로 설정 (내부 풀업)
  pinMode(BUTTON_PIN, INPUT_PULLUP);

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
  Serial.println(WiFi.SSID()); // 실제 연결된 와이파이 이름 출력
  Serial.print("📱 스마트폰 리모컨 주소: http://");
  Serial.println(WiFi.localIP()); // ESP32의 현재 IP 출력

  // 웹서버 라우팅 및 시작
  server.on("/", handleRoot);
  server.on("/next", handleNext);
  server.begin();
  
  Serial.println("==========================================");
  Serial.println("ESP32 Standalone Scanner Ready.");
  Serial.println("Main Mode: AUTO (지능형 자동 판단)");
  Serial.println("Backup: 버튼 클릭 시 MANUAL 수동 모드로 순환");
  // 시리얼 부팅 더미 및 응답 버퍼 비우기
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
    return;
  }

  // 2. 일반 과일 QR URL 파싱
  String fmId = getFmID(rawData);
  if (fmId == "NULL" || fmId == "''") {
    Serial.println("❌ FmID를 찾을 수 없습니다.");
    updateOLED("No FmID!");
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

  // 3. DB 접속 및 처리
  updateOLED("Connecting DB...");
  Serial.println("Connecting to AWS RDS...");
  if (conn.connect(server_addr, db_port, user, password_db)) {
    Serial.println("✅ AWS DB Connection Success!");
    MySQL_Query query_executor(&conn);
    
    query_executor.execute("SET time_zone = '+09:00'");

    // 타겟 모드 결정 (AUTO 메인 vs MANUAL 수동)
    String targetMode = "";
    if (isAutoMode) {
      String checkQuery = "SELECT Lo FROM lab225.qr WHERE FmID = " + fmId + " ORDER BY id DESC LIMIT 1";
      Serial.println("🔍 DB에서 FmID (" + fmId + ")의 이전 이력 조회 중...");
      String lastLo = "NONE";
      if (query_executor.execute(checkQuery.c_str())) {
        row_values *row = query_executor.get_next_row();
        if (row != NULL && row->values[0] != NULL) {
          lastLo = String(row->values[0]);
        }
        while (row != NULL) { row = query_executor.get_next_row(); }
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
        return;
      }
      Serial.println("🤖 [AUTO] 지능형 판단 결과 단계: " + targetMode);
    } else {
      targetMode = manualMode;
      Serial.println("✋ [MANUAL] 수동 지정 단계: " + targetMode);
    }

    // [센서 데이터 통합 가져오기 (GPS, 온습도)]
    String latStr = "NULL", lonStr = "NULL", tpStr = "NULL", hmStr = "NULL";
    String sensor_query = "SELECT lat, lng, temperature, humidity FROM lab225.sensor_data ORDER BY id DESC LIMIT 1";
    Serial.println("🔍 GPS/센서 데이터 조회 중...");
    if (query_executor.execute(sensor_query.c_str())) {
      row_values *row = query_executor.get_next_row();
      if (row != NULL) {
        if (row->values[0] != NULL) latStr = row->values[0];
        if (row->values[1] != NULL) lonStr = row->values[1];
        if (row->values[2] != NULL) tpStr = row->values[2];
        if (row->values[3] != NULL) hmStr = row->values[3];
      }
      while (row != NULL) { row = query_executor.get_next_row(); }
    }

    // [INSERT 쿼리 생성]
    String query = "";
    if (targetMode == "A10") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, Lat, lon) VALUES ";
      query += "('A10', " + ac + ", " + fmId + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", " + rp + ", NOW(), " + latStr + ", " + lonStr + ")";
    }
    else if (targetMode == "A11") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, Lat, lon) ";
      query += "SELECT 'A11', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, NOW(), " + latStr + ", " + lonStr + " ";
      query += "FROM lab225.qr WHERE FmID = " + fmId + " AND APC_AD IS NOT NULL ORDER BY APC_AD DESC LIMIT 1";
    }
    else if (targetMode == "A12") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, Lat, lon) ";
      query += "SELECT 'A12', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, NOW(), " + latStr + ", " + lonStr + " ";
      query += "FROM lab225.qr WHERE Lo = 'A11' AND FmID = " + fmId + " ORDER BY APC_WD DESC LIMIT 1";
    }
    else if (targetMode == "A13") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A13', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, NOW(), " + latStr + ", " + lonStr + ", AGrade, BGrade, CGrade, DefectRate ";
      query += "FROM lab225.qr WHERE Lo = 'A12' AND FmID = " + fmId + " ORDER BY APC_RT DESC LIMIT 1";
    }
    else if (targetMode == "A14") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A14', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, NOW(), " + tpStr + ", " + hmStr + ", " + latStr + ", " + lonStr + ", AGrade, BGrade, CGrade, DefectRate ";
      query += "FROM lab225.qr WHERE Lo = 'A13' AND FmID = " + fmId + " ORDER BY APC_PT DESC LIMIT 1";
    }
    else if (targetMode == "A15") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, APC_OP, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A15', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, NOW(), " + latStr + ", " + lonStr + ", AGrade, BGrade, CGrade, DefectRate ";
      query += "FROM lab225.qr WHERE Lo = 'A14' AND FmID = " + fmId + " ORDER BY APC_StD DESC LIMIT 1";
    }

    if (query_executor.execute(query.c_str())) {
      Serial.println("✅ DB 저장 성공! (단계: " + targetMode + ")");
      updateOLED("DB Save OK!", fmId, targetMode);
    } else {
      Serial.println("❌ DB 저장 실패: 쿼리 오류 또는 이전 단계 데이터 없음");
      updateOLED("DB Save FAIL!");
    }
    conn.close();
  } else {
    Serial.println("❌ DB 연결 실패 (AWS)");
    updateOLED("DB Conn FAIL!");
  }
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

unsigned long lastButtonPress = 0;

void loop() {
  // 스캐너 데이터 처리 (NUL 및 바이너리 제어문자 제거 정제)
  if (ScannerSerial.available()) {
    delay(50); // 패킷 수신 완료 대기
    String scannedData = readCleanScannerData();
    scannedData.trim();
    if (scannedData.length() > 0) {
      unsigned long currentTime = millis();
      // 5초 이내 동일 바코드 중복 스캔 필터링
      if (scannedData == lastScannedData && (currentTime - lastScanTime < SCAN_DEBOUNCE_INTERVAL)) {
        Serial.println("⚠️ 중복 스캔 감지: " + scannedData + " (무시됨)");
        updateOLED("Duplicate Scan!");
      } else {
        lastScannedData = scannedData;
        lastScanTime = currentTime;
        Serial.println("\n📷 스캔된 데이터: " + scannedData);
        processScan(scannedData);
      }
    }
  }

  // 버튼을 통한 모드 순환 전환 (AUTO ↔ MANUAL A10->A11->A13->A14->A15->AUTO)
  if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > 500) {
    cycleMode();
    lastButtonPress = millis();
  }

  // 웹서버 클라이언트 처리
  server.handleClient();
}

