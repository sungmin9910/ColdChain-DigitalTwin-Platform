import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM23'
baud = 115200

print(f"Monitoring {port} for 8 seconds (DTR=False, RTS=False)...")
try:
    ser = serial.Serial(port, baud, timeout=0.5)
    ser.dtr = False
    ser.rts = False
    start = time.time()
    while time.time() - start < 8.0:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[{time.strftime('%H:%M:%S')}] {line}")
        time.sleep(0.02)
    ser.close()
    print("Done monitoring.")
except Exception as e:
    print(f"Error: {e}")
