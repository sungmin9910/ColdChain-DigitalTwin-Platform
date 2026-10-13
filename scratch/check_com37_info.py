import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
port = 'COM37'
baud = 115200

try:
    ser = serial.Serial(port, baud, timeout=1)
    ser.dtr = False
    ser.rts = False
    time.sleep(3.0)
    ser.reset_input_buffer()
    ser.write(b"info\n")
    time.sleep(1.5)
    lines = []
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            lines.append(line)
    print(f"COM37 Response for 'info':")
    for l in lines:
        print("  ", l)
    ser.close()
except Exception as e:
    print(f"Error: {e}")
