import serial
import time
import sys

print("ESP32 COM16 모니터링 시작 (5초간 출력 확인)...")
try:
    s = serial.Serial('COM16', 115200, timeout=0.1)
    t0 = time.time()
    while time.time() - t0 < 5:
        line = s.readline()
        if line:
            print(line.decode('utf-8', errors='replace').strip())
    s.close()
except Exception as e:
    print(f"에러: {e}")
