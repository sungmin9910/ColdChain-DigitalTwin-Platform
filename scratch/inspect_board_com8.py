import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Connecting to {port} at {baud}...")

try:
    ser = serial.Serial(port, baud, timeout=1)
    # Give it a moment, but do NOT toggle reset lines aggressively
    time.sleep(1)
    
    # Check if there is incoming stream
    print("\n--- [1] Checking live stream (3 seconds) ---")
    start = time.time()
    while time.time() - start < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[LIVE] {line}")
        else:
            time.sleep(0.05)
            
    # Send info command
    print("\n--- [2] Sending 'info' command ---")
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

    # Now let's try 'dump'
    print("\n--- [3] Sending 'dump' command and saving to scratch/carrier02_dump.jsonl ---")
    ser.reset_input_buffer()
    ser.write(b"dump\n")
    time.sleep(0.5)
    
    dumping = False
    dumped_records = []
    start = time.time()
    last_recv = time.time()
    
    with open("scratch/carrier02_dump.jsonl", "w", encoding="utf-8") as f_out:
        while True:
            if time.time() - last_recv > 5.0 and dumping:
                print("Dump finished (silence for 5s).")
                break
            if time.time() - start > 60.0:
                print("Dump timed out after 60s.")
                break
                
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                last_recv = time.time()
                if "LittleFS 블랙박스 덤프 시작" in line:
                    dumping = True
                    print(f"[DUMP START] {line}")
                    continue
                elif "덤프 종료" in line:
                    print(f"[DUMP END] {line}")
                    break
                
                if dumping:
                    if line.startswith("{") and line.endswith("}"):
                        f_out.write(line + "\n")
                        dumped_records.append(line)
                        if len(dumped_records) % 100 == 0:
                            print(f"Dumped {len(dumped_records)} records...")
                    else:
                        print(f"[DUMP MSG] {line}")
                else:
                    if line:
                        print(f"[PRE-DUMP] {line}")
            else:
                time.sleep(0.02)
                
    ser.close()
    print(f"\nTotal records saved to scratch/carrier02_dump.jsonl: {len(dumped_records)}")

except Exception as e:
    print(f"Error: {e}")
