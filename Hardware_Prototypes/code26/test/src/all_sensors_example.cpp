#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <BH1750.h>
#include <SHTSensor.h>

Adafruit_MPU6050 mpu;
BH1750 lightMeter;
SHTSensor sht(SHTSensor::SHT4X);

void printSensorStatus(const char* name, bool ok) {
  Serial.print(name);
  Serial.print(ok ? ": OK" : ": FAIL");
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("=== Multi-sensor test ===");
  Wire.begin(21, 22);

  bool mpuOk = mpu.begin();
  printSensorStatus("MPU6050", mpuOk);
  if (mpuOk) {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  bool bh1750Ok = lightMeter.begin();
  printSensorStatus("BH1750", bh1750Ok);

  bool shtOk = sht.init();
  printSensorStatus("SHT45", shtOk);
  if (shtOk) {
    sht.setAccuracy(SHTSensor::SHT_ACCURACY_HIGH);
  }

  Serial.println("Waiting for measurements...");
}

void loop() {
  Serial.println("----------------------------");

  if (mpu.begin()) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    Serial.print("Accel X: "); Serial.print(a.acceleration.x);
    Serial.print(" Y: "); Serial.print(a.acceleration.y);
    Serial.print(" Z: "); Serial.println(a.acceleration.z);

    Serial.print("Gyro  X: "); Serial.print(g.gyro.x);
    Serial.print(" Y: "); Serial.print(g.gyro.y);
    Serial.print(" Z: "); Serial.println(g.gyro.z);
  } else {
    Serial.println("MPU6050 measurement failed");
  }

  if (lightMeter.begin()) {
    float lux = lightMeter.readLightLevel();
    Serial.print("Lux: "); Serial.println(lux);
  } else {
    Serial.println("BH1750 measurement failed");
  }

  if (sht.readSample()) {
    Serial.print("Temp: "); Serial.print(sht.getTemperature()); Serial.println(" C");
    Serial.print("Hum:  "); Serial.print(sht.getHumidity()); Serial.println(" %RH");
  } else {
    Serial.println("SHT45 measurement failed");
  }

  delay(1000);
}
