import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM37'
baud = 115200

print(f"Connecting to {port}...")
ser = serial.Serial(port, baud, timeout=1)
ser.dtr = False
ser.rts = False

# Listen until boot finishes and MQTT begins
print("Waiting for boot to finish (watching serial stream)...")
boot_done = False
start_t = time.time()
while time.time() - start_t < 10:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print("  [BOOT]", line)
            if "MQTT" in line or "Wi-Fi" in line or "PASS" in line or "대기" in line:
                boot_done = True
                break
    time.sleep(0.1)

time.sleep(1.0)
print("\n>>> Sending 'clear' command now...")
ser.reset_input_buffer()
ser.write(b"clear\n")

# Wait for clear confirmation
start_t = time.time()
while time.time() - start_t < 3:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print("  [CLEAR]", line)
    time.sleep(0.05)

print("\n>>> Sending 'info' command to verify...")
ser.write(b"info\n")
start_t = time.time()
while time.time() - start_t < 3:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print("  [INFO]", line)
    time.sleep(0.05)

ser.close()
print("\nCompleted.")
