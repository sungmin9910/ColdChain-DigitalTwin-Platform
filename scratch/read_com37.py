import serial
import time
import sys

port = 'COM37'
baud = 115200

print(f"Opening {port} at {baud} baud...")
try:
    ser = serial.Serial(port, baud, timeout=1)
    ser.setDTR(True)
    ser.setRTS(True)
    time.sleep(0.5)
    
    print("Listening for 15 seconds...")
    start = time.time()
    while time.time() - start < 15:
        line = ser.readline()
        if line:
            try:
                decoded = line.decode('utf-8', errors='replace').strip()
                if decoded:
                    print(decoded)
            except Exception as e:
                print(f"[raw]: {line}")
    ser.close()
    print("Done listening.")
except Exception as e:
    print(f"Error: {e}")
