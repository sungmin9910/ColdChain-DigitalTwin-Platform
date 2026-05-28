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

// 현재 스캔 단계 (A10 = scan1.py, A11 = scan2.py ...)
String currentMode = "A10";

// --- 중복 스캔 방지용 변수 ---
String lastScannedData = "";
unsigned long lastScanTime = 0;
const unsigned long SCAN_DEBOUNCE_INTERVAL = 5000; // 동일 바코드 중복 스캔 방지 시간 (5초)

// --- OLED 업데이트 함수 ---
void updateOLED(String msg = "") {
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

  // 중단: 현재 모드 아주 크게 표시
  display.setCursor(0, 16);
  display.setTextSize(1);
  display.println("Current Mode:");
  
  display.setCursor(0, 28);
  display.setTextSize(3);
  display.println(currentMode);

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
  html += "<h1>현재 스캔 모드: <span style='color:#FF5722;font-size:50px;'>" + currentMode + "</span></h1>";
  
  if (currentMode == "A10") html += "<p style='font-size:20px;'>(박스 입고 단계)</p>";
  else if (currentMode == "A11") html += "<p style='font-size:20px;'>(세척 완료 단계)</p>";
  else if (currentMode == "A13") html += "<p style='font-size:20px;'>(포장 완료 단계)</p>";
  else if (currentMode == "A14") html += "<p style='font-size:20px;'>(저장 단계)</p>";
  else if (currentMode == "A15") html += "<p style='font-size:20px;'>(최종 출하 단계)</p>";
  
  html += "<br><br><a href='/next'><button>👉 다음 단계로 변경</button></a>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handleNext() {
  if (currentMode == "A10") currentMode = "A11";
  else if (currentMode == "A11") currentMode = "A13";
  else if (currentMode == "A13") currentMode = "A14";
  else if (currentMode == "A14") currentMode = "A15";
  else if (currentMode == "A15") currentMode = "A10";
  
  Serial.println("\n📱 폰에서 모드 변경됨 -> " + currentMode);
  updateOLED("Mode Changed via Web");
  
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
  Serial.println("ESP32 Standalone Scanner Ready. (DB Fetch Mode)");
  Serial.println("Current Mode: " + currentMode);
  Serial.println("버튼(GPIO 0)을 누르거나 스마트폰 웹페이지(http://" + WiFi.localIP().toString() + ")에서 단계를 변경하세요.");
  Serial.println("==========================================");
  
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
  // 1. 새 Streamlit URL 방식 (?FmID=33)
  String fmId = getQueryParam(url, "FmID");
  if (fmId != "NULL" && fmId != "''") return fmId;
  
  // 2. 기존 방식 (/qr/33?) - 역호환성 유지
  int lastSlash = url.lastIndexOf('/');
  int questionMark = url.indexOf('?');
  if (lastSlash != -1 && questionMark != -1 && lastSlash < questionMark) {
    String legacyId = url.substring(lastSlash + 1, questionMark);
    if (legacyId.length() > 0) return "'" + legacyId + "'";
  }
  
  return "NULL";
}

void processScan(String rawData) {
  // 1. 모드 변경용 특수 QR 코드 인식
  if (rawData.startsWith("MODE:")) {
    currentMode = rawData.substring(5);
    currentMode.trim();
    Serial.println("\n=================================");
    Serial.println("스캔 단계가 변경되었습니다: " + currentMode);
    Serial.println("=================================\n");
    return;
  }

  // 2. 일반 과일 QR URL 파싱
  String fmId = getFmID(rawData);
  if (fmId == "NULL" || fmId == "''") {
    Serial.println("❌ FmID를 찾을 수 없습니다.");
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
    
    // [추가] AWS RDS 기본 시간(UTC)을 한국 시간(KST, +09:00)으로 맞춰주기
    query_executor.execute("SET time_zone = '+09:00'");

    // [센서 데이터 통합 가져오기 (GPS, 온습도)]
    String latStr = "NULL", lonStr = "NULL", tpStr = "NULL", hmStr = "NULL";
    // sensor_data 테이블의 실제 컬럼명(lat, lng) 및 정렬 조건(id DESC) 반영하여 쿼리 수정
    String sensor_query = "SELECT lat, lng, temperature, humidity FROM sensor_data ORDER BY id DESC LIMIT 1";
    if (query_executor.execute(sensor_query.c_str())) {
      column_names *cols = query_executor.get_columns();
      row_values *row = query_executor.get_next_row();
      if (row != NULL) {
        if (row->values[0] != NULL) latStr = row->values[0];
        if (row->values[1] != NULL) lonStr = row->values[1];
        if (row->values[2] != NULL) tpStr = row->values[2];
        if (row->values[3] != NULL) hmStr = row->values[3];
      }
      // 버퍼 비우기
      while (row != NULL) { row = query_executor.get_next_row(); }
    }

    // [INSERT 쿼리 생성 (INSERT ... SELECT 사용)]
    String query = "";
    if (currentMode == "A10") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, Lat, lon) VALUES ";
      query += "('A10', " + ac + ", " + fmId + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", " + rp + ", NOW(), " + latStr + ", " + lonStr + ")";
    }
    else if (currentMode == "A11") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, Lat, lon) ";
      query += "SELECT 'A11', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, NOW(), " + latStr + ", " + lonStr + " ";
      query += "FROM lab225.qr WHERE FmID = " + fmId + " AND APC_AD IS NOT NULL ORDER BY APC_AD DESC LIMIT 1";
    }
    else if (currentMode == "A12") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, Lat, lon) ";
      query += "SELECT 'A12', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, NOW(), " + latStr + ", " + lonStr + " ";
      query += "FROM lab225.qr WHERE Lo = 'A11' AND FmID = " + fmId + " ORDER BY APC_WD DESC LIMIT 1";
    }
    else if (currentMode == "A13") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A13', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, NOW(), " + latStr + ", " + lonStr + ", AGrade, BGrade, CGrade, DefectRate ";
      query += "FROM lab225.qr WHERE Lo = 'A12' AND FmID = " + fmId + " ORDER BY APC_RT DESC LIMIT 1";
    }
    else if (currentMode == "A14") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A14', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, NOW(), " + tpStr + ", " + hmStr + ", " + latStr + ", " + lonStr + ", AGrade, BGrade, CGrade, DefectRate ";
      query += "FROM lab225.qr WHERE Lo = 'A13' AND FmID = " + fmId + " ORDER BY APC_PT DESC LIMIT 1";
    }
    else if (currentMode == "A15") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, APC_OP, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A15', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, NOW(), " + latStr + ", " + lonStr + ", AGrade, BGrade, CGrade, DefectRate ";
      query += "FROM lab225.qr WHERE Lo = 'A14' AND FmID = " + fmId + " ORDER BY APC_StD DESC LIMIT 1";
    }

    if (query_executor.execute(query.c_str())) {
      Serial.println("✅ DB 저장 성공! (단계: " + currentMode + ")");
      updateOLED("DB Save OK!");
    } else {
      Serial.println("❌ DB 저장 실패: 쿼리 오류 또는 이전 단계 데이터 없음");
      updateOLED("DB Save FAIL!");
    }
    conn.close();
  } else {
    Serial.println("❌ DB 연결 실패 (AWS)");
    Serial.println("힌트1: AWS RDS 보안 그룹에서 현재 IP(" + WiFi.localIP().toString() + ")의 3306 포트를 허용했는지 확인하세요.");
    Serial.println("힌트2: AWS RDS의 '퍼블릭 액세스' 설정이 '예'로 되어있는지 확인하세요.");
    updateOLED("DB Conn FAIL!");
  }
}

unsigned long lastButtonPress = 0;

void loop() {
  // 스캐너 데이터 처리
  if (ScannerSerial.available()) {
    String scannedData = ScannerSerial.readStringUntil('\r');
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

  // 버튼을 통한 수동 모드 전환 (디바운스 500ms 적용)
  if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > 500) {
    if (currentMode == "A10") currentMode = "A11";
    else if (currentMode == "A11") currentMode = "A13"; // A12는 PC에서 발급하므로 건너뜀
    else if (currentMode == "A13") currentMode = "A14";
    else if (currentMode == "A14") currentMode = "A15";
    else if (currentMode == "A15") currentMode = "A10";
    
    Serial.println("\n🔘 버튼 눌림 - 스캔 단계가 " + currentMode + "(으)로 변경되었습니다.");
    updateOLED("Mode Changed");
    lastButtonPress = millis();
  }

  // 웹서버 클라이언트 처리 (스마트폰 접속 대기)
  server.handleClient();
}

