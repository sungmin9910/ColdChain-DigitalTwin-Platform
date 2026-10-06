import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_current_status():
    ser = serial.Serial("COM7", 115200, timeout=1.5)
    time.sleep(1)
    ser.reset_input_buffer()
    ser.write(b"info\n")
    time.sleep(1.2)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if "LittleFS" in line or "현황" in line or "전체" in line or "상태" in line:
            print(line)
    ser.close()

if __name__ == "__main__":
    check_current_status()
