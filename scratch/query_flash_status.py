import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM37'
baud = 115200

print(f"Connecting to {port} at {baud} bps...")
try:
    ser = serial.Serial(port, baud, timeout=2)
    ser.dtr = True
    ser.rts = True
    time.sleep(1)
    
    # 포트 버퍼 비우기
    ser.reset_input_buffer()
    
    print("\n--- Sending 'info' command ---")
    ser.write(b"info\n")
    time.sleep(0.5)
    
    # 응답 읽기
    start_time = time.time()
    lines = []
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[RECV] {line}")
                lines.append(line)
        else:
            time.sleep(0.1)

    print("\n--- Monitoring 3 seconds of live output ---")
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[STREAM] {line}")
        else:
            time.sleep(0.1)

    ser.close()
    print("\nSerial port closed successfully.")

except Exception as e:
    print(f"Error accessing {port}: {e}")
