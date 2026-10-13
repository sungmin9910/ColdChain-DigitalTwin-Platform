import serial
import time

s = serial.Serial('COM37', 115200, timeout=1)

# ESP32-C6 USB CDC reset sequence
s.dtr = False
s.rts = False
time.sleep(0.1)
s.dtr = True
s.rts = True
time.sleep(0.2)
s.dtr = False
s.rts = False

lines = []
start = time.time()
while time.time() - start < 5:
    raw = s.readline()
    if raw:
        line = raw.decode('utf-8', errors='replace').strip()
        if line:
            lines.append(line)

s.close()

for l in lines:
    print(l)
