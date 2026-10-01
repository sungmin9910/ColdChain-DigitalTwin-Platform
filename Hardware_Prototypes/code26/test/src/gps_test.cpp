#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n=================================");
  Serial.println("  ESP32-C6 Serial0 vs Serial1 GPS 테스트  ");
  Serial.println("=================================");

  // 혹시 Serial0이 기본 실행 중이라면 종료 후 재시작 테스트
  Serial0.end();
}

void loop() {
  // 테스트 1: Serial0 기본 하드웨어 UART (RX:17, TX:16)
  Serial.println("\n--- [1] Serial0.begin(9600) (기본 UART0: RX=17, TX=16) 5초간 ---");
  Serial0.begin(9600);
  unsigned long start = millis();
  int count0 = 0;
  while (millis() - start < 5000) {
    if (Serial0.available()) {
      char c = Serial0.read();
      Serial.write(c);
      count0++;
    }
  }
  Serial0.end();
  Serial.printf("\n>> Serial0 (RX:17) 수신 바이트: %d\n", count0);

  // 테스트 2: Serial0 핀 교체 (RX:16, TX:17)
  Serial.println("\n--- [2] Serial0.begin(9600, SERIAL_8N1, 16, 17) (RX=16, TX=17) 5초간 ---");
  Serial0.begin(9600, SERIAL_8N1, 16, 17);
  start = millis();
  int count0_swap = 0;
  while (millis() - start < 5000) {
    if (Serial0.available()) {
      char c = Serial0.read();
      Serial.write(c);
      count0_swap++;
    }
  }
  Serial0.end();
  Serial.printf("\n>> Serial0 (RX:16) 수신 바이트: %d\n", count0_swap);

  // 테스트 3: Serial1 (RX:17, TX:16)
  Serial.println("\n--- [3] Serial1 (RX=17, TX=16, 9600 baud) ---");
  Serial1.begin(9600, SERIAL_8N1, 17, 16);
  start = millis();
  int count1 = 0;
  while (millis() - start < 8000) {
    if (Serial1.available()) {
      int c = Serial1.read();
      Serial.printf(" [0x%02X '%c'] ", c, (c >= 32 && c <= 126) ? (char)c : '.');
      count1++;
    }
  }
  Serial1.end();
  Serial.printf("\n>> Serial1 (RX:17) 수신 바이트: %d\n", count1);

  // 테스트 4: Serial1 (RX:16, TX:17)
  Serial.println("\n--- [4] Serial1.begin(9600, SERIAL_8N1, 16, 17) 5초간 ---");
  Serial1.begin(9600, SERIAL_8N1, 16, 17);
  start = millis();
  int count1_swap = 0;
  while (millis() - start < 5000) {
    if (Serial1.available()) {
      char c = Serial1.read();
      Serial.write(c);
      count1_swap++;
    }
  }
  Serial1.end();
  Serial.printf("\n>> Serial1 (RX:16) 수신 바이트: %d\n", count1_swap);

  delay(3000);
}
