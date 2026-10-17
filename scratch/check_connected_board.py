import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Connecting to {port} at {baud}...")

try:
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(1)
    
    # 1. Check live stream
    print("\n--- [1] Live Stream (4 seconds) ---")
    start = time.time()
    while time.time() - start < 4:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[LIVE] {line}")
        else:
            time.sleep(0.05)
            
    # 2. Send info command
    print("\n--- [2] Querying LittleFS Info ---")
    ser.reset_input_buffer()
    ser.write(b"info\n")
    time.sleep(0.5)
    
    start = time.time()
    while time.time() - start < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[INFO] {line}")
        else:
            time.sleep(0.05)
            
    ser.close()

except Exception as e:
    print(f"Error: {e}")
