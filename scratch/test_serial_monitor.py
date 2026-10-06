import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_serial():
    ser = serial.Serial("COM7", 115200, timeout=1)
    time.sleep(1)
    ser.write(b"info\n")
    start = time.time()
    while time.time() - start < 6:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[COM7] {line}")
        time.sleep(0.02)
    ser.close()

if __name__ == "__main__":
    test_serial()
