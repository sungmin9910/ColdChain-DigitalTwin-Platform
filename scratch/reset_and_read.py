import serial
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

port = 'COM37'
baud = 115200

print(f"Connecting to {port} and resetting ESP32...")
ser = serial.Serial(port, baud, timeout=0.5)

# Standard ESP32 reset sequence via DTR/RTS
ser.setDTR(False)
ser.setRTS(True)
time.sleep(0.1)
ser.setRTS(False)
time.sleep(0.2)
ser.setDTR(True)

print("Listening for boot output for 12 seconds...")
start = time.time()
while time.time() - start < 12:
    line = ser.readline()
    if line:
        try:
            text = line.decode('utf-8', errors='replace').rstrip()
            if text:
                print(text)
        except Exception as e:
            print(f"[raw]: {line}")

ser.close()
print("Finished.")
