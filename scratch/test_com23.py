import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM23'
print(f"Testing newly connected device on {port}...")

for baud in [115200, 9600]:
    try:
        ser = serial.Serial(port, baud, timeout=1)
        ser.dtr = False
        ser.rts = False
        time.sleep(0.5)
        lines = []
        start = time.time()
        while time.time() - start < 2.0:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    lines.append(line)
        ser.close()
        if lines:
            print(f"[{baud} bps] Received {len(lines)} lines from {port}:")
            for l in lines[:5]:
                print("  ", l)
            break
        else:
            print(f"[{baud} bps] Port opened, but no stream output yet (normal if waiting for trigger/scan).")
    except Exception as e:
        print(f"[{baud} bps] Error: {e}")
