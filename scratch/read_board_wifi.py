import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Connecting to {port} and capturing boot/network info...")

try:
    ser = serial.Serial(port, baud, timeout=1)
    
    # Reset ESP32 via DTR/RTS
    ser.dtr = False
    ser.rts = True
    time.sleep(0.1)
    ser.rts = False
    time.sleep(0.1)
    ser.reset_input_buffer()
    
    start = time.time()
    boot_lines = []
    while time.time() - start < 8:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[BOOT] {line}")
                boot_lines.append(line)
        else:
            time.sleep(0.05)
            
    ser.close()

except Exception as e:
    print(f"Error: {e}")
