import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
port = 'COM37'
baud = 115200

ser = serial.Serial(port, baud, timeout=0.2)
time.sleep(2.0)
ser.reset_input_buffer()

print("Sending 'info'...")
ser.write(b"info\n")

start = time.time()
while time.time() - start < 4.0:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print("RECV:", line)
    time.sleep(0.05)

ser.close()
