import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Connecting to {port} to inspect live g_force output...")

try:
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(0.5)
    
    start = time.time()
    count = 0
    while time.time() - start < 12 and count < 5:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[RECV] {line}")
                if "페이로드" in line or "g_force" in line or "충격" in line:
                    count += 1
        else:
            time.sleep(0.05)
            
    ser.close()

except Exception as e:
    print(f"Error: {e}")
