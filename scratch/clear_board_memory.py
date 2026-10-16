import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Connecting to {port} to clear LittleFS memory...")
ser = serial.Serial(port, baud, timeout=2)
time.sleep(0.5)

ser.reset_input_buffer()
print("Sending 'clear' command to MCU...")
ser.write(b"clear\n")
time.sleep(1.0)

# Read output
start = time.time()
while time.time() - start < 3:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"[RECV] {line}")
    else:
        time.sleep(0.05)

# Verify with info command
print("\nVerifying with 'info' command...")
ser.reset_input_buffer()
ser.write(b"info\n")
time.sleep(0.5)

start = time.time()
while time.time() - start < 3:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"[INFO] {line}")
    else:
        time.sleep(0.05)

ser.close()
print("\nMemory clear complete.")
