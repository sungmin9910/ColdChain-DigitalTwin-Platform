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

// 현재 스캔 단계 (A10 = scan1.py, A11 = scan2.py ...)
String currentMode = "A10";

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
  Serial.println("ESP32 Standalone Scanner Ready. (DB Fetch Mode)");
  Serial.println("Current Mode: " + currentMode);
  Serial.println("버튼(GPIO 0)을 누르거나 스마트폰 웹페이지(http://" + WiFi.localIP().toString() + ")에서 단계를 변경하세요.");
  Serial.println("==========================================");

  // 스캐너를 호스트 모드로 자동 전환 시도
  ScannerSerial.write(0x00);
  delay(50);
  ScannerSerial.write(setHostModeCmd, sizeof(setHostModeCmd));
  delay(100);

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

    // [쿼리 개선] 서브쿼리를 사용하여 DB 서버에서 직접 최신 센서 데이터를 결합합니다.
    String query = "";
    String sensor_sub = "(SELECT lat, lng, temperature, humidity FROM lab225.sensor_data ORDER BY id DESC LIMIT 1) S";

    if (currentMode == "A10") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, Lat, lon) ";
      query += "SELECT 'A10', " + ac + ", " + fmId + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", " + rp + ", NOW(), S.lat, S.lng ";
      query += "FROM " + sensor_sub;
    }
    else if (currentMode == "A11") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, Lat, lon) ";
      query += "SELECT 'A11', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, NOW(), S.lat, S.lng ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.FmID = " + fmId + " AND Q.APC_AD IS NOT NULL ORDER BY Q.APC_AD DESC LIMIT 1";
    }
    else if (currentMode == "A12") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, Lat, lon) ";
      query += "SELECT 'A12', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, NOW(), S.lat, S.lng ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A11' AND Q.FmID = " + fmId + " ORDER BY Q.APC_WD DESC LIMIT 1";
    }
    else if (currentMode == "A13") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A13', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, Q.APC_RT, NOW(), S.lat, S.lng, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A12' AND Q.FmID = " + fmId + " ORDER BY Q.APC_RT DESC LIMIT 1";
    }
    else if (currentMode == "A14") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A14', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, Q.APC_RT, Q.APC_PT, NOW(), S.temperature, S.humidity, S.lat, S.lng, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A13' AND Q.FmID = " + fmId + " ORDER BY Q.APC_PT DESC LIMIT 1";
    }
    else if (currentMode == "A15") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, APC_OP, Lat, lon, AGrade, BGrade, CGrade, DefectRate) ";
      query += "SELECT 'A15', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, Q.APC_WD, Q.APC_RT, Q.APC_PT, Q.APC_StD, NOW(), S.lat, S.lng, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate ";
      query += "FROM lab225.qr Q, " + sensor_sub + " ";
      query += "WHERE Q.Lo = 'A14' AND Q.FmID = " + fmId + " ORDER BY Q.APC_StD DESC LIMIT 1";
    }

    if (query_executor.execute(query.c_str())) {
      Serial.println("✅ DB 저장 성공! (최신 센서 데이터 자동 병합 완료)");
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

unsigned long lastButtonPress = 0; // 백업 BOOT 버튼 디바운스용

// 단일 택트 스위치용 더블클릭 감지 변수
int lastTriggerState = HIGH;
unsigned long triggerPressTime = 0;
int triggerClickCount = 0;
const unsigned long doubleClickDelay = 350; // 더블클릭 감지 제한 시간 (350ms)

void loop() {
  // 1. 메인 택트 스위치(GPIO 25) 처리 (싱글클릭: 스캔 / 더블클릭: 단계 변경)
  int currentTriggerState = digitalRead(SCAN_TRIGGER_PIN);
  
  // 버튼이 눌렸을 때 (HIGH -> LOW)
  if (currentTriggerState == LOW && lastTriggerState == HIGH) {
    if (triggerClickCount == 0) {
      triggerPressTime = millis();
    }
    triggerClickCount++;
    delay(50); // 간단한 디바운스 딜레이
  }
  lastTriggerState = currentTriggerState;

  // 클릭 판정 시간(350ms)이 경과한 경우
  if (triggerClickCount > 0 && (millis() - triggerPressTime > doubleClickDelay)) {
    if (triggerClickCount == 1) {
      // 싱글클릭 -> 스캔 명령어 전송
      Serial.println("\n🔫 1회 클릭: GM77 스캔 명령어 전송");
      
      // 슬립 모드 해제를 위한 Wake-up 시퀀스
      ScannerSerial.write(0x00);
      delay(50);
      
      ScannerSerial.write(triggerCmd, sizeof(triggerCmd));
    } 
    else if (triggerClickCount >= 2) {
      // 더블클릭 -> 스캔 단계 전환
      if (currentMode == "A10") currentMode = "A11";
      else if (currentMode == "A11") currentMode = "A13"; 
      else if (currentMode == "A13") currentMode = "A14";
      else if (currentMode == "A14") currentMode = "A15";
      else if (currentMode == "A15") currentMode = "A10";
      
      Serial.println("\n🔘 더블 클릭: 스캔 단계가 " + currentMode + "(으)로 변경되었습니다.");
      updateOLED("Mode Changed");
    }
    triggerClickCount = 0; // 카운트 리셋
  }

  // 2. 백업용 BOOT 버튼(GPIO 0) 처리 (단계 변경)
  if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > 500) {
    if (currentMode == "A10") currentMode = "A11";
    else if (currentMode == "A11") currentMode = "A13"; // A12는 PC에서 발급하므로 건너뜀
    else if (currentMode == "A13") currentMode = "A14";
    else if (currentMode == "A14") currentMode = "A15";
    else if (currentMode == "A15") currentMode = "A10";
    
    Serial.println("\n🔘 백업 BOOT 버튼 눌림 - 스캔 단계가 " + currentMode + "(으)로 변경되었습니다.");
    updateOLED("Mode Changed");
    lastButtonPress = millis();
  }

  // 3. 스캐너 데이터 처리
  if (ScannerSerial.available()) {
    String scannedData = ScannerSerial.readStringUntil('\r');
    scannedData.trim();
    if (scannedData.length() > 0) {
      Serial.println("\n📷 스캔된 데이터: " + scannedData);
      updateOLED("Scanned!");
      processScan(scannedData);
    }
  }

  // 웹서버 클라이언트 처리 (스마트폰 접속 대기)
  server.handleClient();
}

