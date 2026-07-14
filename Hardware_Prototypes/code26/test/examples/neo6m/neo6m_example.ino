/*
 NEO-6M GPS 예시 (ESP32)
 연결 예시: GPS TX -> ESP32 GPIO16 (RX2), GPS RX -> ESP32 GPIO17 (TX2)
 라이브러리: TinyGPSPlus
*/

#include <TinyGPSPlus.h>

TinyGPSPlus gps;

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, 16, 17);
  Serial.println("GPS serial started (Serial2, RX=16, TX=17)");
}

void loop() {
  while (Serial2.available() > 0) {
    gps.encode(Serial2.read());
  }

  if (gps.location.isUpdated()) {
    Serial.print("Latitude: "); Serial.println(gps.location.lat(), 6);
    Serial.print("Longitude: "); Serial.println(gps.location.lng(), 6);
  }
  if (gps.time.isUpdated()) {
    Serial.print("Time: "); Serial.print(gps.time.hour()); Serial.print(":"); Serial.print(gps.time.minute()); Serial.print(":"); Serial.println(gps.time.second());
  }
  delay(1000);
}
