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
  pinMode(SCAN_TRIGGER_PIN, INPUT_PULLUP); // 신규: 스캔 트리거 버튼 입력 설정

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
  Serial.println("Backup: 더블 클릭 시 MANUAL 수동 모드로 순환");
  Serial.println("버튼(GPIO 0/25)을 누르거나 스마트폰 웹페이지(http://" + WiFi.localIP().toString() + ")에서 모드를 변경하세요.");
  Serial.println("==========================================");

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
      // DB에서 해당 FmID의 최신 Lo 상태 조회
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
    delay(50); // 패킷 수신 완료 대기
    String scannedData = readCleanScannerData();
    scannedData.trim();
    if (scannedData.length() > 0) {
      Serial.println("\n📷 스캔된 데이터: " + scannedData);
      processScan(scannedData);
    }
  }

  // 웹서버 클라이언트 처리
  server.handleClient();
}

