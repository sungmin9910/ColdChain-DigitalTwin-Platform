import serial
import time
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    ser = serial.Serial('COM37', 115200, timeout=1)
    ser.dtr = True
    ser.rts = True
    time.sleep(0.1)
    print("Connected to COM37. Reading 6 seconds...")
    t0 = time.time()
    while time.time() - t0 < 6:
        line = ser.readline()
        if line:
            decoded = line.decode('utf-8', errors='replace').rstrip()
            print(decoded)
    ser.close()
except Exception as e:
    print(f"Error: {e}")
