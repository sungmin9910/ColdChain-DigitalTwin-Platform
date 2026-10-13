import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM37'
baud = 115200

print(f"Opening {port} at {baud} bps to clear LittleFS...")

try:
    ser = serial.Serial(port, baud, timeout=1)
    ser.dtr = False
    ser.rts = False
    time.sleep(2.0)
    ser.reset_input_buffer()
    
    print("Sending 'clear' command to ESP32-C6...")
    ser.write(b"clear\n")
    time.sleep(1.5)
    
    lines = []
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            lines.append(line)
            print("RECV:", line)
            
    print("\nSending 'info' command to verify LittleFS status...")
    ser.write(b"info\n")
    time.sleep(1.5)
    
    info_lines = []
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            info_lines.append(line)
            print("INFO:", line)
            
    ser.close()
    print("\nDone.")
    
except Exception as e:
    print(f"Error: {e}")
