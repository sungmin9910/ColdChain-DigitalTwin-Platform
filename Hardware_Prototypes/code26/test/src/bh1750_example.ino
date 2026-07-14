/*
 BH1750 예시 (ESP32, I2C)
 연결: SDA -> 21, SCL -> 22
 라이브러리: BH1750
*/

#include <Wire.h>
#include <BH1750.h>

BH1750 lightMeter;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  if (lightMeter.begin()) {
    Serial.println("BH1750 initialized");
  } else {
    Serial.println("BH1750 init failed");
  }
}

void loop() {
  float lux = lightMeter.readLightLevel();
  Serial.print("Lux: ");
  Serial.println(lux);
  delay(1000);
}
