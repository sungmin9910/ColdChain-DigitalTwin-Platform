/*
 SHT45 예시 (ESP32, I2C)
 연결: SDA -> 21, SCL -> 22 (ESP32 기본 I2C)
*/

#include <Wire.h>
#include <SHTSensor.h>

SHTSensor sht(SHTSensor::SHT4X);

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!sht.init()) {
    Serial.println("SHT4x init failed");
    while (1) delay(1000);
  }

  sht.setAccuracy(SHTSensor::SHT_ACCURACY_HIGH);
  Serial.println("SHT4x ready");
}

void loop() {
  if (sht.readSample()) {
    Serial.print("Temperature: ");
    Serial.print(sht.getTemperature());
    Serial.println(" °C");
    Serial.print("Humidity: ");
    Serial.print(sht.getHumidity());
    Serial.println(" %RH");
  } else {
    Serial.println("Measurement failed");
  }

  delay(2000);
}
