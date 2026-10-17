import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
port = 'COM8'
baud = 115200

print(f"Waiting for {port} connection / data...")

while True:
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"\n[CONNECTED] Successfully opened {port}! Reading serial data...\n")
        while True:
            try:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    print(f"[RECV] {line}")
                    if "IMU 초기화" in line or "I2C 버스 스캔" in line or "페이로드" in line:
                        sys.stdout.flush()
            except (serial.SerialException, OSError):
                print("\n[DISCONNECTED] Port disconnected (cable unplugged). Waiting for re-plug...")
                ser.close()
                break
    except (serial.SerialException, OSError):
        time.sleep(0.5)
