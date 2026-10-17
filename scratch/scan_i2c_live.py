import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Connecting to {port} to run I2C scan...")

try:
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(0.5)
    ser.reset_input_buffer()
    
    print("Sending 'scan' command...")
    ser.write(b"scan\n")
    time.sleep(0.5)
    
    start = time.time()
    while time.time() - start < 4:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[RECV] {line}")
        else:
            time.sleep(0.05)
            
    ser.close()

except Exception as e:
    print(f"Error: {e}")
