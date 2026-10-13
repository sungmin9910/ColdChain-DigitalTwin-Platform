import serial
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = "COM16"
print(f"[{PORT} 모니터링 시작]")
try:
    ser = serial.Serial(PORT, 115200, timeout=0.5)
    # DTR/RTS reset pulse
    ser.dtr = False
    ser.rts = True
    time.sleep(0.1)
    ser.rts = False
    time.sleep(0.5)
    
    t0 = time.time()
    while time.time() - t0 < 6:
        line = ser.readline()
        if line:
            print(line.decode('utf-8', errors='replace').strip())
    ser.close()
except Exception as e:
    print(f"에러: {e}")
