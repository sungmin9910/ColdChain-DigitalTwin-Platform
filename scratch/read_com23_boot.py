import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM23'
baud = 115200

print(f"Reading boot log from {port}...")
ser = serial.Serial(port, baud, timeout=1)
ser.dtr = True
ser.rts = True
time.sleep(0.5)

start = time.time()
while time.time() - start < 5.0:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print("COM23:", line)
    time.sleep(0.05)

ser.close()
print("Done.")
