#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#define USE_ESP32_WIFI true
#include <MySQL_Generic.h>

// --- 보안 설정 분리 ---
#include "secrets.h"

const char server_addr[] = "15.165.68.30"; // DB 호스트 IP
uint16_t db_port = 3306;
char user[] = "admin";
char db[] = "lab225";

// --- 핀 설정 (ESP32-DevKit 결선에 맞게 변경) ---
#define SCANNER_RX_PIN 16 // DE2110 TX -> ESP32 RX2 (16)
#define SCANNER_TX_PIN 17 // DE2110 RX -> ESP32 TX2 (17)
#define BUTTON_PIN 0      // ESP32 기본 BOOT 버튼

// 객체 명시적 생성
HardwareSerial ScannerSerial(2);
// MySQL_Generic_WiFi.h에 WiFiClient client가 이미 선언되어 있으므로 여기서는 선언하지 않습니다.
MySQL_Connection conn((Client *)&client);
WiFiMulti wifiMulti; // 다중 와이파이 연결용 객체

// 현재 스캔 단계 (A10 = scan1.py, A11 = scan2.py ...)
String currentMode = "A10";

void setup() {
  Serial.begin(115200);
  
  // 시리얼 초기화
  ScannerSerial.begin(115200, SERIAL_8N1, SCANNER_RX_PIN, SCANNER_TX_PIN);
  
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
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP()); // ESP32의 현재 IP 출력
  
  Serial.println("==========================================");
  Serial.println("ESP32 Standalone Scanner Ready. (DB Fetch Mode)");
  Serial.println("Current Mode: " + currentMode);
  Serial.println("버튼(GPIO 0)을 누르거나 'MODE:A11' 텍스트 QR을 스캔하여 단계를 변경하세요.");
  Serial.println("==========================================");
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
  Serial.println("Connecting to AWS RDS...");
  if (conn.connect(server_addr, db_port, user, password_db)) {
    Serial.println("✅ AWS DB Connection Success!");
    MySQL_Query query_executor(&conn);

    // [센서 데이터 통합 가져오기 (GPS, 온습도)]
    String latStr = "NULL", lonStr = "NULL", tpStr = "NULL", hmStr = "NULL";
    String sensor_query = "SELECT latitude, longitude, temperature, humidity FROM sensor_data ORDER BY recorded_at DESC LIMIT 1";
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
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, Lat, lon) ";
      query += "SELECT 'A13', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, NOW(), " + latStr + ", " + lonStr + " ";
      query += "FROM lab225.qr WHERE Lo = 'A12' AND FmID = " + fmId + " ORDER BY APC_RT DESC LIMIT 1";
    }
    else if (currentMode == "A14") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, Tp, Hm, Lat, lon) ";
      query += "SELECT 'A14', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, NOW(), " + tpStr + ", " + hmStr + ", " + latStr + ", " + lonStr + " ";
      query += "FROM lab225.qr WHERE Lo = 'A13' AND FmID = " + fmId + " ORDER BY APC_PT DESC LIMIT 1";
    }
    else if (currentMode == "A15") {
      query = "INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, APC_OP, Lat, lon) ";
      query += "SELECT 'A15', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, NOW(), " + latStr + ", " + lonStr + " ";
      query += "FROM lab225.qr WHERE Lo = 'A14' AND FmID = " + fmId + " ORDER BY APC_StD DESC LIMIT 1";
    }

    if (query_executor.execute(query.c_str())) {
      Serial.println("✅ DB 저장 성공! (단계: " + currentMode + ")");
    } else {
      Serial.println("❌ DB 저장 실패: 쿼리 오류 또는 이전 단계 데이터 없음");
    }
    conn.close();
  } else {
    Serial.println("❌ DB 연결 실패 (AWS)");
    Serial.println("힌트1: AWS RDS 보안 그룹에서 현재 IP(" + WiFi.localIP().toString() + ")의 3306 포트를 허용했는지 확인하세요.");
    Serial.println("힌트2: AWS RDS의 '퍼블릭 액세스' 설정이 '예'로 되어있는지 확인하세요.");
  }
}

unsigned long lastButtonPress = 0;

void loop() {
  // 스캐너 데이터 처리
  if (ScannerSerial.available()) {
    String scannedData = ScannerSerial.readStringUntil('\r');
    scannedData.trim();
    if (scannedData.length() > 0) {
      Serial.println("\n📷 스캔된 데이터: " + scannedData);
      processScan(scannedData);
    }
  }

  // 버튼을 통한 수동 모드 전환 (디바운스 500ms 적용)
  if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > 500) {
    if (currentMode == "A10") currentMode = "A11";
    else if (currentMode == "A11") currentMode = "A12";
    else if (currentMode == "A12") currentMode = "A13";
    else if (currentMode == "A13") currentMode = "A14";
    else if (currentMode == "A14") currentMode = "A15";
    else if (currentMode == "A15") currentMode = "A10";
    
    Serial.println("\n🔘 버튼 눌림 - 스캔 단계가 " + currentMode + "(으)로 변경되었습니다.");
    lastButtonPress = millis();
  }
}

