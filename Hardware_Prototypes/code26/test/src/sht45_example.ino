/*
 SHT45 예시 (ESP32, I2C)
 연결: SDA -> 21, SCL -> 22 (ESP32 기본 I2C)
*/

#include <Wire.h>
#include <SHTSensor.h>

SHTSensor sht(SHTSensor::SHT4X);

void scanI2cBus() {
  byte error;
  int nDevices = 0;

  Serial.println("Scanning I2C bus...");
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("I2C device found at 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
      nDevices++;
    }
  }

  if (nDevices == 0) {
    Serial.println("No I2C devices found");
  } else {
    Serial.print("Total I2C devices: ");
    Serial.println(nDevices);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Booting SHT45 test");

  Wire.begin(21, 22);
  scanI2cBus();

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
