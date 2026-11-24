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

const char server_addr[] = "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com"; // AWS RDS DNS 엔드포인트
const char server_fallback_ip[] = "15.165.68.30"; // DNS 장애 대비 폴백 IP
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

// ==========================================
// 공급망 v4 단계 및 모드 설정 (17자리 LotID · 3자리 FmID / A01~A04·B01~B06·C01~C02·D01)
// ==========================================
bool isAutoMode = true;
String manualMode = "A02";
const char* MANUAL_MODES[] = {"A02", "A03", "A04", "B01", "B03", "B04", "B05", "B06", "C01", "C02", "D01"};
const int NUM_MANUAL_MODES = sizeof(MANUAL_MODES) / sizeof(MANUAL_MODES[0]);

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

String getStageDescKo(String code) {
  if (code == "A02") return "농가 저장고 입고 (선택)";
  if (code == "A03") return "농가 저장고 출고 (선택)";
  if (code == "A04") return "농가 출하 · APC 출발 (1구간)";
  if (code == "B01") return "APC 입고 (1구간 도착)";
  if (code == "B03") return "APC 선별 출고 (등급별 유색)";
  if (code == "B04") return "APC 저장고 입고 (선택 · 유색)";
  if (code == "B05") return "APC 저장고 출고 (선택 · 유색)";
  if (code == "B06") return "APC 출하 (2구간 출발)";
  if (code == "C01") return "유통 창고 저장 (2구간 도착)";
  if (code == "C02") return "유통 출하 (3구간 출발)";
  if (code == "D01") return "판매처 도착 (3구간 도착)";
  return code;
}

bool isValidManualMode(String code) {
  for (int i = 0; i < NUM_MANUAL_MODES; i++) {
    if (code == MANUAL_MODES[i]) return true;
  }
  return false;
}

// OLED용 17자리(v4) / 16자리(v3) LotID 축약 표시 (21자 제한 대응)
String formatShortOledId(String labelId) {
  String s = labelId;
  s.replace("'", "");
  if (s.length() <= 16) return s;
  int dashIdx = s.indexOf('-');
  String base = (dashIdx > 0) ? s.substring(0, dashIdx) : s;
  String suffix = (dashIdx > 0) ? s.substring(dashIdx) : "";
  if (base.length() == 17) {
    // 예: 55630001411261124-A -> 001-411-261124-A
    return base.substring(5, 8) + "-" + base.substring(8, 11) + "-" + base.substring(11, 17) + suffix;
  }
  if (base.length() == 16) {
    // 예: 5563207411261122-A -> 07-411-261122-A
    return base.substring(5, 7) + "-" + base.substring(7, 10) + "-" + base.substring(10, 16) + suffix;
  }
  return s.substring(s.length() - 16);
}

// --- OLED 업데이트 함수 ---
void updateOLED(String msg = "", String lotLabel = "", String activeMode = "", unsigned long decLat = 0, unsigned long totLat = 0) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  // 상단: IP 주소 및 상태
  display.setCursor(0, 0);
  if (WiFi.status() == WL_CONNECTED) {
    display.print("WiFi:");
    display.println(WiFi.localIP());
  } else {
    display.println("WiFi: Disconnected");
  }
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);

  // 중단: 현재 모드 및 로트 ID 표시
  display.setCursor(0, 13);
  if (isAutoMode) {
    display.setTextSize(1);
    display.print("Mode: [ AUTO v4 ]");
    if (activeMode != "" && lotLabel != "") {
      display.setCursor(0, 23);
      display.println(formatShortOledId(lotLabel));
      display.setCursor(0, 34);
      display.setTextSize(2);
      display.print("-> ");
      display.println(activeMode);
    } else {
      display.setCursor(0, 26);
      display.setTextSize(1);
      display.println("Ready (A02~D01)...");
    }
  } else {
    display.setTextSize(1);
    display.print("Mode: [ MANUAL ]");
    display.setCursor(0, 24);
    display.setTextSize(2);
    display.print(manualMode);
    if (lotLabel != "") {
      display.setTextSize(1);
      display.setCursor(0, 42);
      display.println(formatShortOledId(lotLabel));
    }
  }

  // 하단: Latency 수치 또는 상태 메시지 표시
  display.setTextSize(1);
  display.setCursor(0, 54);
  if (decLat > 0 || totLat > 0) {
    display.printf("D:%lums T:%lums", decLat, totLat);
  } else if (msg != "") {
    display.println(msg);
  }

  display.display();
}

// --- 스마트폰 리모컨 UI 함수 (원터치 분기 선택 버튼 그리드) ---
void handleRoot() {
  String html = "<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<style>";
  html += "body{font-family:'Malgun Gothic',sans-serif;text-align:center;margin:18px;background:#f4f6fb;color:#1f2937;} ";
  html += ".card{background:white;padding:16px;margin:14px auto;max-width:420px;border-radius:16px;box-shadow:0 3px 10px rgba(0,0,0,0.08);} ";
  html += ".grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:10px;} ";
  html += ".btn{display:block;padding:14px 10px;font-size:15px;font-weight:700;text-decoration:none;border-radius:12px;color:white;background:#3b82f6;} ";
  html += ".btn-auto{background:#10b981;grid-column:span 2;font-size:17px;} ";
  html += ".btn-farm{background:#059669;} .btn-apc{background:#2563eb;} .btn-dist{background:#7c3aed;} .btn-retail{background:#ea580c;} ";
  html += ".btn-active{outline:4px solid #facc15;box-shadow:0 0 0 2px #111827;} ";
  html += ".sec-lbl{font-size:12px;color:#64748b;font-weight:700;text-align:left;margin:10px 0 4px 2px;} ";
  html += "</style></head><body>";

  html += "<h2 style='margin:6px 0;'>🚚 콜드체인 QR 스캐너 v4</h2>";

  html += "<div class='card'>";
  if (isAutoMode) {
    html += "<div style='font-size:28px;font-weight:900;color:#10b981;'>🤖 AUTO (자동 판단)</div>";
    html += "<p style='font-size:13px;color:#64748b;margin:6px 0 0 0;'>무색: A02→A03→A04→B01 | 유색: B03→B04→B05→B06→C01→C02→D01</p>";
  } else {
    html += "<div style='font-size:28px;font-weight:900;color:#ef4444;'>✋ MANUAL (" + manualMode + ")</div>";
    html += "<p style='font-size:14px;color:#374151;margin:6px 0 0 0;'>" + getStageDescKo(manualMode) + "</p>";
  }
  html += "</div>";

  // 원터치 단계 선택 리모컨 카드
  html += "<div class='card'>";
  html += "<h3 style='margin:0 0 8px 0;'>🎛️ 단계 원터치 전환 (분기 선택)</h3>";
  html += "<div class='grid'>";
  html += String("<a class='btn btn-auto") + (isAutoMode ? " btn-active" : "") + "' href='/set?mode=AUTO'>🤖 AUTO (지능형 자동 판단)</a>";
  html += "</div>";

  html += "<div class='sec-lbl'>🌱 농가 (무색 QR)</div><div class='grid'>";
  html += String("<a class='btn btn-farm") + (!isAutoMode && manualMode == "A02" ? " btn-active" : "") + "' href='/set?mode=A02'>A02 저장고 입고</a>";
  html += String("<a class='btn btn-farm") + (!isAutoMode && manualMode == "A03" ? " btn-active" : "") + "' href='/set?mode=A03'>A03 저장고 출고</a>";
  html += String("<a class='btn btn-farm") + (!isAutoMode && manualMode == "A04" ? " btn-active" : "") + "' href='/set?mode=A04' style='grid-column:span 2;'>A04 농가 출하 (APC 출발 · 직행 가능)</a>";
  html += "</div>";

  html += "<div class='sec-lbl'>🏢 APC (무색 B01 / 유색 B03~B06)</div><div class='grid'>";
  html += String("<a class='btn btn-apc") + (!isAutoMode && manualMode == "B01" ? " btn-active" : "") + "' href='/set?mode=B01'>B01 APC 입고</a>";
  html += String("<a class='btn btn-apc") + (!isAutoMode && manualMode == "B03" ? " btn-active" : "") + "' href='/set?mode=B03'>B03 선별 출고</a>";
  html += String("<a class='btn btn-apc") + (!isAutoMode && manualMode == "B04" ? " btn-active" : "") + "' href='/set?mode=B04'>B04 저장고 입고</a>";
  html += String("<a class='btn btn-apc") + (!isAutoMode && manualMode == "B05" ? " btn-active" : "") + "' href='/set?mode=B05'>B05 저장고 출고</a>";
  html += String("<a class='btn btn-apc") + (!isAutoMode && manualMode == "B06" ? " btn-active" : "") + "' href='/set?mode=B06' style='grid-column:span 2;'>B06 APC 출하 (저장고 생략 직행 가능)</a>";
  html += "</div>";

  html += "<div class='sec-lbl'>🏬 유통 · 🏪 판매처 (유색 QR)</div><div class='grid'>";
  html += String("<a class='btn btn-dist") + (!isAutoMode && manualMode == "C01" ? " btn-active" : "") + "' href='/set?mode=C01'>C01 유통창고</a>";
  html += String("<a class='btn btn-dist") + (!isAutoMode && manualMode == "C02" ? " btn-active" : "") + "' href='/set?mode=C02'>C02 유통출하</a>";
  html += String("<a class='btn btn-retail") + (!isAutoMode && manualMode == "D01" ? " btn-active" : "") + "' href='/set?mode=D01' style='grid-column:span 2;'>D01 판매처 도착</a>";
  html += "</div></div>";

  // 지연 시간 모니터링 카드
  html += "<div class='card'>";
  html += "<h3 style='margin:0 0 8px 0;'>⏱️ 최근 Latency 측정</h3>";
  html += "<p style='margin:4px 0;'><strong>스캔 횟수:</strong> " + String(scan_counter) + " 회</p>";
  html += "<p style='margin:4px 0;'><strong>Decode:</strong> <span style='color:#2563eb;font-weight:bold;'>" + String(last_decode_latency) + " ms</span> &nbsp;|&nbsp; ";
  html += "<strong>Total:</strong> <span style='color:#10b981;font-weight:bold;'>" + String(last_total_latency) + " ms</span></p>";
  html += "</div>";

  html += "</body></html>";
  server.send(200, "text/html", html);
}

void setScannerMode(String modeVal) {
  modeVal.trim();
  modeVal.toUpperCase();
  if (modeVal == "AUTO") {
    isAutoMode = true;
    Serial.println("\n🔄 모드 전환됨 -> 🤖 AUTO (지능형 자동 판단)");
    updateOLED("Mode: AUTO v4");
  } else if (isValidManualMode(modeVal)) {
    isAutoMode = false;
    manualMode = modeVal;
    Serial.println("\n🔄 모드 전환됨 -> ✋ MANUAL (" + manualMode + " - " + getStageDescKo(manualMode) + ")");
    updateOLED("Manual: " + manualMode);
  }
}

void cycleMode() {
  if (isAutoMode) {
    setScannerMode(MANUAL_MODES[0]);
    return;
  }
  for (int i = 0; i < NUM_MANUAL_MODES; i++) {
    if (manualMode == MANUAL_MODES[i]) {
      if (i + 1 < NUM_MANUAL_MODES) {
        setScannerMode(MANUAL_MODES[i + 1]);
      } else {
        setScannerMode("AUTO");
      }
      return;
    }
  }
  setScannerMode("AUTO");
}

void handleSetMode() {
  if (server.hasArg("mode")) {
    setScannerMode(server.arg("mode"));
  }
  server.sendHeader("Location", "/");
  server.send(303);
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
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 20);
  display.println("Booting Scanner v4...");
  display.display();

  // 시리얼 초기화 (GM77 기본 속도 9600bps)
  ScannerSerial.begin(9600, SERIAL_8N1, SCANNER_RX_PIN, SCANNER_TX_PIN);

  // 버튼을 입력용으로 설정 (내부 풀업)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(SCAN_TRIGGER_PIN, INPUT_PULLUP);

  // 다중 Wi-Fi 연결
  Serial.print("Connecting to WiFi...");
  for (int i = 0; i < num_wifi_networks; i++) {
    wifiMulti.addAP(wifi_networks[i].ssid, wifi_networks[i].password);
  }

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
  server.on("/set", handleSetMode);
  server.on("/next", handleNext);
  server.begin();

  Serial.println("==============================================================");
  Serial.println(" ColdChain Smart QR Scanner v4 (17-Digit LotID / A01~D01)");
  Serial.println(" - Modes: AUTO, A02~A04, B01, B03~B06, C01~C02, D01");
  Serial.println(" - CSV: CSV_ROW,ScanID,LotID,Mode,Decode_ms,DB_ms,Total_ms");
  Serial.println("==============================================================");

  // 스캐너 호스트 모드 설정
  ScannerSerial.write(0x00);
  delay(50);
  ScannerSerial.write(setHostModeCmd, sizeof(setHostModeCmd));
  delay(200);

  while (ScannerSerial.available()) {
    ScannerSerial.read();
  }

  updateOLED("System Ready v4");
}

// URL 퍼센트 인코딩(%XX) 및 공백(+) 디코딩 헬퍼 함수
String urlDecode(String str) {
  String decoded = "";
  char c;
  char code0;
  char code1;
  for (unsigned int i = 0; i < str.length(); i++) {
    c = str.charAt(i);
    if (c == '+') {
      decoded += ' ';
    } else if (c == '%' && i + 2 < str.length()) {
      code0 = str.charAt(++i);
      code1 = str.charAt(++i);
      auto hexVal = [](char ch) -> int {
        if (ch >= '0' && ch <= '9') return ch - '0';
        if (ch >= 'a' && ch <= 'f') return ch - 'a' + 10;
        if (ch >= 'A' && ch <= 'F') return ch - 'A' + 10;
        return 0;
      };
      c = (char)((hexVal(code0) << 4) | hexVal(code1));
      decoded += c;
    } else {
      decoded += c;
    }
  }
  decoded.replace("'", ""); // SQL 구문 깨짐 방지
  return decoded;
}

// URL 파라미터 파싱 (URL 디코딩 자동 적용, 파라미터 경계 ? 또는 & 정밀 매칭)
String getRawQueryParam(String url, String param) {
  int qPos = url.indexOf('?');
  if (qPos == -1) return "";
  String qs = url.substring(qPos + 1);
  int start = -1;
  if (qs.startsWith(param + "=")) {
    start = param.length() + 1;
  } else {
    int idx = qs.indexOf("&" + param + "=");
    if (idx != -1) start = idx + param.length() + 2;
  }
  if (start == -1) return "";
  int end = qs.indexOf("&", start);
  if (end == -1) end = qs.length();
  String rawVal = qs.substring(start, end);
  return urlDecode(rawVal);
}

String toSqlVal(String v) {
  v.trim();
  if (v.length() == 0) return "NULL";
  return "'" + v + "'";
}

String getQueryParam(String url, String param) {
  return toSqlVal(getRawQueryParam(url, param));
}

// 16자리 LotID 최우선 추출 (없으면 기존 FmID로 폴백)
String getLotIDClean(String url) {
  String lot = getRawQueryParam(url, "LotID");
  if (lot.length() > 0) return lot;
  lot = getRawQueryParam(url, "lot_id");
  if (lot.length() > 0) return lot;
  String fm = getRawQueryParam(url, "FmID");
  if (fm.length() > 0) return fm;

  int lastSlash = url.lastIndexOf('/');
  int questionMark = url.indexOf('?');
  if (lastSlash != -1 && questionMark != -1 && lastSlash < questionMark) {
    String legacyId = url.substring(lastSlash + 1, questionMark);
    if (legacyId.length() > 0) return legacyId;
  }
  return "";
}

// 유색 QR URL의 grade / pkg_grade 파라미터를 정규화 등급 코드("A", "B", "C")로 추출 (무색 QR이면 "" 반환)
String extractGradeCode(String url) {
  String gParam = getRawQueryParam(url, "pkg_grade");
  if (gParam.length() == 0) gParam = getRawQueryParam(url, "grade");
  if (gParam.length() == 0) return "";

  gParam.trim();
  String gUpper = gParam;
  gUpper.toUpperCase();

  if (gUpper == "B" || gUpper == "M" || gUpper == "MEDIUM" || gParam.indexOf("중") != -1) return "B";
  if (gUpper == "C" || gUpper == "L" || gUpper == "LOW" || gParam.indexOf("하") != -1) return "C";
  if (gUpper == "A" || gUpper == "H" || gUpper == "HIGH" || gParam.indexOf("상") != -1) return "A";
  return "";
}

String fetchSingleString(MySQL_Query &qe, String sql) {
  String out = "NONE";
  if (qe.execute(sql.c_str())) {
    qe.get_columns();
    row_values *row = qe.get_next_row();
    if (row != NULL && row->values[0] != NULL) {
      out = String(row->values[0]);
      out.trim();
    }
    while (row != NULL) { row = qe.get_next_row(); }
    qe.close();
  }
  return out;
}

void processScan(String rawData) {
  // 1. 앞쪽 GM77 ACK 제어 바이너리 제거
  int httpIdx = rawData.indexOf("http");
  int modeIdx = rawData.indexOf("MODE:");

  if (httpIdx != -1) {
    rawData = rawData.substring(httpIdx);
  } else if (modeIdx != -1) {
    rawData = rawData.substring(modeIdx);
  } else {
    return;
  }

  // 2. 모드 변경용 특수 QR 코드 인식 (MODE:AUTO, MODE:A02, MODE:B12 등)
  if (rawData.startsWith("MODE:")) {
    String modeVal = rawData.substring(5);
    setScannerMode(modeVal);
    t_trigger_start = 0;
    return;
  }

  // 3. 16자리 LotID 및 메타 파라미터 파싱
  String cleanLotId = getLotIDClean(rawData);
  if (cleanLotId.length() == 0) {
    Serial.println("❌ LotID/FmID를 찾을 수 없습니다.");
    updateOLED("No LotID!");
    t_trigger_start = 0;
    return;
  }

  String cleanAc = getRawQueryParam(rawData, "AC");
  String cleanFm = getRawQueryParam(rawData, "FmID");
  String cleanCc = getRawQueryParam(rawData, "CC");
  if (cleanLotId.length() == 17) {
    if (cleanAc.length() == 0) cleanAc = cleanLotId.substring(0, 5);
    if (cleanFm.length() == 0) cleanFm = cleanLotId.substring(5, 8);
    if (cleanCc.length() == 0) cleanCc = cleanLotId.substring(8, 11);
  } else if (cleanLotId.length() == 16) {
    if (cleanAc.length() == 0) cleanAc = cleanLotId.substring(0, 5);
    if (cleanFm.length() == 0) cleanFm = cleanLotId.substring(5, 7);
    if (cleanCc.length() == 0) cleanCc = cleanLotId.substring(7, 10);
  } else {
    if (cleanFm.length() == 0) cleanFm = cleanLotId;
  }

  String scannedGrade = extractGradeCode(rawData); // 유색 QR이면 "A"/"B"/"C", 무색 농가 QR이면 ""
  String displayPkgId = (scannedGrade.length() > 0) ? (cleanLotId + "-" + scannedGrade) : cleanLotId;

  String sqlLotId = toSqlVal(cleanLotId);
  String sqlFmId  = toSqlVal(cleanFm);
  String sqlAc    = toSqlVal(cleanAc);
  String sqlCc    = toSqlVal(cleanCc);
  String frt = getQueryParam(rawData, "FrT");
  String vt  = getQueryParam(rawData, "Vt");
  String ct  = getQueryParam(rawData, "Ct");
  String hd  = getQueryParam(rawData, "HD");
  String dd  = getQueryParam(rawData, "DD");
  String qt  = getQueryParam(rawData, "Qt");
  String mt  = getQueryParam(rawData, "Mt");
  String hn  = getQueryParam(rawData, "HN");
  String std = getQueryParam(rawData, "StD");
  String rp  = getQueryParam(rawData, "Rp");

  // ⏱️ Decode Latency
  unsigned long decode_latency = (t_trigger_start > 0) ? (t_decode_end - t_trigger_start) : (t_decode_end - t_decode_start);
  last_decode_latency = decode_latency;

  // 4. DB 접속 및 처리
  updateOLED("Connecting DB...");
  Serial.println("Connecting to AWS RDS...");
  t_db_start = millis();

  bool dbConnected = conn.connect(server_addr, db_port, user, password_db);
  if (!dbConnected) {
    dbConnected = conn.connect(server_fallback_ip, db_port, user, password_db);
  }

  if (dbConnected) {
    Serial.println("✅ AWS DB Connection Success!");
    MySQL_Query query_executor(&conn);
    query_executor.execute("SET time_zone = '+09:00'");

    String lotWhere = "(Q.LotID = " + sqlLotId + " OR (Q.LotID IS NULL AND Q.FmID = " + sqlLotId + "))";
    String lotWherePlain = "(LotID = " + sqlLotId + " OR (LotID IS NULL AND FmID = " + sqlLotId + "))";

    // 타겟 모드 결정 (AUTO vs MANUAL)
    String targetMode = "";
    if (isAutoMode) {
      if (scannedGrade.length() > 0) {
        // 유색 QR(A/B/C): 해당 등급 패키지 진행 상태 조회 (B03 선별출고 -> B04 -> B05 -> B06 -> C01 -> C02 -> D01)
        String pkgCheck =
          "SELECT Lo FROM lab225.qr WHERE " + lotWherePlain +
          " AND Lo IN ('B03','B04','B05','B06','C01','C02','D01') AND pkg_grade = '" + scannedGrade +
          "' ORDER BY id DESC LIMIT 1";
        String lastLo = fetchSingleString(query_executor, pkgCheck);

        if (lastLo == "NONE") {
          String baseCheck =
            "SELECT Lo FROM lab225.qr WHERE " + lotWherePlain +
            " AND Lo IN ('B01','B02') AND (pkg_grade IS NULL OR pkg_grade = '') ORDER BY id DESC LIMIT 1";
          lastLo = fetchSingleString(query_executor, baseCheck);
        }

        Serial.println("💡 [유색 QR] DB 최신 이력: " + lastLo + " (" + displayPkgId + ")");
        if (lastLo == "NONE" || lastLo == "B02" || lastLo == "B01") targetMode = "B03";
        else if (lastLo == "B03") targetMode = "B04";
        else if (lastLo == "B04") targetMode = "B05";
        else if (lastLo == "B05") targetMode = "B06";
        else if (lastLo == "B06") targetMode = "C01";
        else if (lastLo == "C01") targetMode = "C02";
        else if (lastLo == "C02") targetMode = "D01";
        else if (lastLo == "D01") {
          Serial.println("⚠️ 이미 판매처 도착(D01) 완료된 상품입니다: " + displayPkgId);
          updateOLED("Already Completed!", displayPkgId, "D01");
          conn.close();
          t_trigger_start = 0;
          return;
        }
      } else {
        // 무색 농가 QR: A01(수확) -> A02(저장입고) -> A03(저장출고) -> A04(농가출하) -> B01(APC입고)
        String rawCheck =
          "SELECT Lo FROM lab225.qr WHERE " + lotWherePlain +
          " AND (pkg_grade IS NULL OR pkg_grade = '') ORDER BY id DESC LIMIT 1";
        String lastLo = fetchSingleString(query_executor, rawCheck);

        Serial.println("💡 [무색 QR] DB 최신 이력: " + lastLo + " (" + cleanLotId + ")");
        if (lastLo == "NONE" || lastLo == "A01") targetMode = "A02";
        else if (lastLo == "A02") targetMode = "A03";
        else if (lastLo == "A03") targetMode = "A04";
        else if (lastLo == "A04") targetMode = "B01";
        else if (lastLo == "B01") {
          Serial.println("ℹ️ APC 입고(B01) 완료 상태입니다. 포털에서 B02 선별 후 유색 QR을 스캔하세요.");
          updateOLED("Do B02 Sorting!", cleanLotId, "B01");
          conn.close();
          t_trigger_start = 0;
          return;
        } else {
          Serial.println("ℹ️ 이미 APC 선별(B02) 이후 단계입니다. 유색 QR을 스캔하세요.");
          updateOLED("Use Colored QR!", cleanLotId, lastLo);
          conn.close();
          t_trigger_start = 0;
          return;
        }
      }
      Serial.println("🤖 [AUTO] 판단 단계: " + targetMode + " (" + displayPkgId + ")");
    } else {
      targetMode = manualMode;
      Serial.println("✋ [MANUAL] 지정 단계: " + targetMode + " (" + displayPkgId + ")");
    }

    // 최신 환경(온습도·차량단말) + 실내 0.0 방지 유효 GPS 좌표 조회
    String sLat = "NULL", sLng = "NULL", sTemp = "NULL", sHumi = "NULL", sDev = "NULL";
    const char* sensorQuery =
      "SELECT "
      "COALESCE((SELECT lat FROM lab225.sensor_data WHERE device=B.device AND lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1),"
      "(SELECT lat FROM lab225.sensor_data WHERE lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1)),"
      "COALESCE((SELECT lng FROM lab225.sensor_data WHERE device=B.device AND lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1),"
      "(SELECT lng FROM lab225.sensor_data WHERE lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1)),"
      "B.temperature,B.humidity,B.device "
      "FROM (SELECT temperature,humidity,device FROM lab225.sensor_data ORDER BY id DESC LIMIT 1) B";
    if (query_executor.execute(sensorQuery)) {
      query_executor.get_columns();
      row_values *srow = query_executor.get_next_row();
      if (srow != NULL) {
        if (srow->values[0] != NULL) sLat = String(srow->values[0]);
        if (srow->values[1] != NULL) sLng = String(srow->values[1]);
        if (srow->values[2] != NULL) sTemp = "'" + String(srow->values[2]) + "'";
        if (srow->values[3] != NULL) sHumi = "'" + String(srow->values[3]) + "'";
        if (srow->values[4] != NULL) sDev = "'" + String(srow->values[4]) + "'";
      }
      while (srow != NULL) { srow = query_executor.get_next_row(); }
      query_executor.close();
    }
    Serial.println("📡 매칭 FDT: " + sDev + " / Temp:" + sTemp + " Humi:" + sHumi + " GPS:(" + sLat + "," + sLng + ")");

    // 기존 행 존재 여부 확인 (A00이 DB에 아직 없는 경우에도 농가/입고 스캔 안전 폴백)
    String hasBaseRow = fetchSingleString(
      query_executor,
      "SELECT id FROM lab225.qr WHERE " + lotWherePlain + " AND (pkg_grade IS NULL OR pkg_grade = '') ORDER BY id DESC LIMIT 1"
    );
    bool baseExists = (hasBaseRow != "NONE" && hasBaseRow.length() > 0);

    String sqlGradeVal = (scannedGrade.length() > 0) ? ("'" + scannedGrade + "'") : "NULL";
    String effColoredGrade = (scannedGrade.length() > 0) ? ("'" + scannedGrade + "'") : "'A'";

    String query = "";
    if (targetMode == "A02") {
      // 농가 저장고 들어감 (온습도 + Farm_StD)
      if (baseExists) {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Tp, Hm, Lat, lon, truck_device) ";
        query += "SELECT 'A02', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, NOW(), " + sTemp + ", " + sHumi + ", " + sLat + ", " + sLng + ", COALESCE(" + sDev + ", Q.truck_device) ";
        query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo = 'A01' ORDER BY Q.id DESC LIMIT 1";
      } else {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Tp, Hm, Lat, lon, truck_device) ";
        query += "VALUES ('A02', " + sqlAc + ", " + sqlFmId + ", " + sqlLotId + ", " + sqlCc + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", NOW(), " + sTemp + ", " + sHumi + ", " + sLat + ", " + sLng + ", " + sDev + ")";
      }
    }
    else if (targetMode == "A03") {
      // 농가 저장고 나옴 (온습도 + Farm_StOut)
      if (baseExists) {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Tp, Hm, Lat, lon, truck_device) ";
        query += "SELECT 'A03', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, NOW(), " + sTemp + ", " + sHumi + ", " + sLat + ", " + sLng + ", COALESCE(" + sDev + ", Q.truck_device) ";
        query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo IN ('A02','A01') ORDER BY Q.id DESC LIMIT 1";
      } else {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StOut, Tp, Hm, Lat, lon, truck_device) ";
        query += "VALUES ('A03', " + sqlAc + ", " + sqlFmId + ", " + sqlLotId + ", " + sqlCc + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", NOW(), " + sTemp + ", " + sHumi + ", " + sLat + ", " + sLng + ", " + sDev + ")";
      }
    }
    else if (targetMode == "A04") {
      // 농가 출하 · APC로 출발 (A03/A02 또는 A01 직행 허용, 1구간 출발)
      if (baseExists) {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, Tp, Hm, Lat, lon, truck_device) ";
        query += "SELECT 'A04', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, NOW(), Q.Tp, Q.Hm, " + sLat + ", " + sLng + ", COALESCE(" + sDev + ", Q.truck_device) ";
        query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo IN ('A03','A02','A01') ORDER BY Q.id DESC LIMIT 1";
      } else {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_DD, Lat, lon, truck_device) ";
        query += "VALUES ('A04', " + sqlAc + ", " + sqlFmId + ", " + sqlLotId + ", " + sqlCc + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", NOW(), " + sLat + ", " + sLng + ", " + sDev + ")";
      }
    }
    else if (targetMode == "B01") {
      // APC 입고 (A04/A03/A02/A01 복사, 1구간 도착)
      if (baseExists) {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, Lat, lon, truck_device) ";
        query += "SELECT 'B01', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, NOW(), " + sLat + ", " + sLng + ", COALESCE(Q.truck_device, " + sDev + ") ";
        query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo IN ('A04','A03','A02','A01') ORDER BY Q.id DESC LIMIT 1";
      } else {
        query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, APC_AD, Lat, lon, truck_device) ";
        query += "VALUES ('B01', " + sqlAc + ", " + sqlFmId + ", " + sqlLotId + ", " + sqlCc + ", " + frt + ", " + vt + ", " + ct + ", " + hd + ", " + dd + ", " + qt + ", " + mt + ", " + hn + ", " + std + ", NOW(), " + sLat + ", " + sLng + ", " + sDev + ")";
      }
    }
    else if (targetMode == "B03") {
      // APC 선별 출고 (등급별 유색 QR A/B/C 스캔 -> APC_SortOut)
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, APC_RT, APC_SortOut, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) ";
      query += "SELECT 'B03', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, Q.APC_AD, Q.APC_RT, NOW(), " + sLat + ", " + sLng + ", Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(" + sDev + ", Q.truck_device), " + effColoredGrade + " ";
      query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo = 'B02' ORDER BY Q.id DESC LIMIT 1";
    }
    else if (targetMode == "B04") {
      // APC 저장고 입고 (선택 · 유색 QR, B03 또는 B02 이후 -> APC_StD + 온습도)
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, APC_RT, APC_SortOut, APC_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) ";
      query += "SELECT 'B04', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_SortOut, NOW(), " + sTemp + ", " + sHumi + ", " + sLat + ", " + sLng + ", Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(" + sDev + ", Q.truck_device), " + effColoredGrade + " ";
      query += "FROM lab225.qr Q WHERE " + lotWhere + " AND ((Q.Lo = 'B03' AND Q.pkg_grade = " + effColoredGrade + ") OR Q.Lo = 'B02') ";
      query += "ORDER BY CASE WHEN Q.Lo = 'B03' AND Q.pkg_grade = " + effColoredGrade + " THEN 0 ELSE 1 END, Q.id DESC LIMIT 1";
    }
    else if (targetMode == "B05") {
      // APC 저장고 출고 (선택 · 유색 QR, B04 이후 -> APC_StOut + 온습도)
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, APC_RT, APC_SortOut, APC_StD, APC_StOut, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) ";
      query += "SELECT 'B05', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_SortOut, Q.APC_StD, NOW(), " + sTemp + ", " + sHumi + ", " + sLat + ", " + sLng + ", Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(" + sDev + ", Q.truck_device), " + effColoredGrade + " ";
      query += "FROM lab225.qr Q WHERE " + lotWhere + " AND ((Q.Lo IN ('B04','B03') AND Q.pkg_grade = " + effColoredGrade + ") OR Q.Lo = 'B02') ";
      query += "ORDER BY CASE WHEN Q.Lo = 'B04' AND Q.pkg_grade = " + effColoredGrade + " THEN 0 WHEN Q.Lo = 'B03' AND Q.pkg_grade = " + effColoredGrade + " THEN 1 ELSE 2 END, Q.id DESC LIMIT 1";
    }
    else if (targetMode == "B06") {
      // APC 출하 (유색 QR: B05/B04/B03 또는 B02 직행 허용 -> 2구간 출발)
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, APC_RT, APC_SortOut, APC_StD, APC_StOut, APC_OP, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) ";
      query += "SELECT 'B06', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_SortOut, Q.APC_StD, Q.APC_StOut, NOW(), Q.Tp, Q.Hm, " + sLat + ", " + sLng + ", Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(" + sDev + ", Q.truck_device), " + effColoredGrade + " ";
      query += "FROM lab225.qr Q WHERE " + lotWhere + " AND ((Q.Lo IN ('B05','B04','B03') AND Q.pkg_grade = " + effColoredGrade + ") OR Q.Lo = 'B02') ";
      query += "ORDER BY CASE WHEN Q.Lo = 'B05' AND Q.pkg_grade = " + effColoredGrade + " THEN 0 WHEN Q.Lo = 'B04' AND Q.pkg_grade = " + effColoredGrade + " THEN 1 WHEN Q.Lo = 'B03' AND Q.pkg_grade = " + effColoredGrade + " THEN 2 ELSE 3 END, Q.id DESC LIMIT 1";
    }
    else if (targetMode == "C01") {
      // 유통 창고 저장 (유색 QR: B06 또는 레거시 B13 이후 -> 2구간 도착 + 온습도)
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, APC_RT, APC_SortOut, APC_StD, APC_StOut, APC_OP, Dist_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) ";
      query += "SELECT 'C01', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_SortOut, Q.APC_StD, Q.APC_StOut, Q.APC_OP, NOW(), " + sTemp + ", " + sHumi + ", " + sLat + ", " + sLng + ", Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(Q.truck_device, " + sDev + "), " + effColoredGrade + " ";
      query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo IN ('B06','B13') AND COALESCE(Q.pkg_grade, 'A') = " + effColoredGrade + " ORDER BY Q.id DESC LIMIT 1";
    }
    else if (targetMode == "C02") {
      // 유통 출하 / 판매처 출발 (유색 QR: C01 또는 B06/B13 직송 허용 -> 3구간 출발)
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, APC_RT, APC_SortOut, APC_StD, APC_StOut, APC_OP, Dist_StD, Dist_OP, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) ";
      query += "SELECT 'C02', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_SortOut, Q.APC_StD, Q.APC_StOut, Q.APC_OP, Q.Dist_StD, NOW(), Q.Tp, Q.Hm, " + sLat + ", " + sLng + ", Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(" + sDev + ", Q.truck_device), " + effColoredGrade + " ";
      query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo IN ('C01','B06','B13') AND COALESCE(Q.pkg_grade, 'A') = " + effColoredGrade + " ORDER BY Q.id DESC LIMIT 1";
    }
    else if (targetMode == "D01") {
      // 판매처 도착 (유색 QR: C02 또는 C01/B06/B13 직송 허용 -> 3구간 도착)
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_StOut, Farm_DD, APC_AD, APC_RT, APC_SortOut, APC_StD, APC_StOut, APC_OP, Dist_StD, Dist_OP, Retail_AD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) ";
      query += "SELECT 'D01', Q.AC, Q.FmID, " + sqlLotId + ", COALESCE(Q.CropCode, " + sqlCc + "), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_StOut, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_SortOut, Q.APC_StD, Q.APC_StOut, Q.APC_OP, Q.Dist_StD, Q.Dist_OP, NOW(), Q.Tp, Q.Hm, " + sLat + ", " + sLng + ", Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(Q.truck_device, " + sDev + "), " + effColoredGrade + " ";
      query += "FROM lab225.qr Q WHERE " + lotWhere + " AND Q.Lo IN ('C02','C01','B06','B13') AND COALESCE(Q.pkg_grade, 'A') = " + effColoredGrade + " ORDER BY Q.id DESC LIMIT 1";
    }

    bool isSuccess = false;
    if (query.length() > 0) {
      isSuccess = query_executor.execute(query.c_str());
    }
    t_db_end = millis();

    unsigned long db_latency = t_db_end - t_db_start;
    unsigned long total_latency = (t_trigger_start > 0) ? (t_db_end - t_trigger_start) : (decode_latency + db_latency);
    last_total_latency = total_latency;
    scan_counter++;

    String labelId = (scannedGrade.length() > 0) ? displayPkgId : cleanLotId;
    if (isSuccess) {
      Serial.println("✅ DB 저장 성공! (대상: " + labelId + " / 단계: " + targetMode + ")");
      updateOLED("DB Save OK!", labelId, targetMode, decode_latency, total_latency);
    } else {
      Serial.println("❌ DB 저장 실패: 선행 단계 데이터 없음 또는 쿼리 오류");
      updateOLED("DB Save FAIL!", labelId, targetMode, decode_latency, total_latency);
    }

    Serial.println("==================================================");
    Serial.printf("⏱️ [스캔 #%lu Latency 리포트]\n", scan_counter);
    Serial.printf(" - Lot/등급 ID          : %s\n", labelId.c_str());
    Serial.printf(" - 진행 단계 (Mode)     : %s (%s)\n", targetMode.c_str(), getStageDescKo(targetMode).c_str());
    Serial.printf(" - 디코드 지연 (Decode) : %lu ms\n", decode_latency);
    Serial.printf(" - 클라우드 DB 지연     : %lu ms\n", db_latency);
    Serial.printf(" - 전체 처리 시간 (Total): %lu ms\n", total_latency);
    Serial.printf("CSV_ROW,%lu,%s,%s,%lu,%lu,%lu\n", scan_counter, labelId.c_str(), targetMode.c_str(), decode_latency, db_latency, total_latency);
    Serial.println("==================================================\n");

    conn.close();
  } else {
    Serial.println("❌ DB 연결 실패 (AWS)");
    updateOLED("DB Conn FAIL!");
  }

  t_trigger_start = 0;
}

// 시리얼에서 0x00(NUL) 및 제어 바이너리를 걸러내고 9600bps 속도에 맞춰 전체 URL을 수신하는 함수
String readCleanScannerData() {
  String result = "";
  unsigned long start = millis();
  unsigned long lastCharTime = millis();

  while (millis() - start < 1500) {
    if (ScannerSerial.available()) {
      char c = (char)ScannerSerial.read();
      uint8_t uc = (uint8_t)c;
      lastCharTime = millis();

      if (c == '\r' || c == '\n') {
        if (result.length() > 0) break;
      } else if (uc >= 32 && uc != 127 && uc != 255) {
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
int lastTriggerState = HIGH;
unsigned long triggerPressTime = 0;
int triggerClickCount = 0;
const unsigned long doubleClickDelay = 350;

void loop() {
  // 1. 메인 택트 스위치(GPIO 25): 싱글클릭=스캔 / 더블클릭=모드 순환
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
      Serial.println("\n🔫 1회 클릭: GM77 스캔 명령어 전송");
      t_trigger_start = millis();
      ScannerSerial.write(0x00);
      delay(50);
      ScannerSerial.write(triggerCmd, sizeof(triggerCmd));
    } else if (triggerClickCount >= 2) {
      cycleMode();
    }
    triggerClickCount = 0;
  }

  // 2. 백업 BOOT 버튼(GPIO 0): 모드 순환
  if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > 500) {
    cycleMode();
    lastButtonPress = millis();
  }

  // 3. 스캐너 데이터 수신 처리
  if (ScannerSerial.available()) {
    t_decode_start = millis();
    delay(50);
    String scannedData = readCleanScannerData();
    t_decode_end = millis();

    scannedData.trim();
    if (scannedData.length() > 0) {
      Serial.println("\n📷 스캔된 데이터: " + scannedData);
      processScan(scannedData);
    }
  }

  // 웹서버 클라이언트 처리
  server.handleClient();
}
