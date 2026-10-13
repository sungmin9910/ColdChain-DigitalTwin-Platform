import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM23'
baud = 115200

print(f"Monitoring {port} for 20 seconds...")
print("Please scan the QR code right now if you can!")

ser = serial.Serial(port, baud, timeout=0.5)
ser.dtr = False
ser.rts = False
time.sleep(0.5)
ser.reset_input_buffer()

start = time.time()
while time.time() - start < 20:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"[{time.strftime('%H:%M:%S')}] {line}")
    time.sleep(0.02)

ser.close()
print("Monitoring finished.")
