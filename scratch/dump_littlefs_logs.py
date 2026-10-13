import serial
import time
import sys
import json
import os

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM37'
baud = 115200
output_file = 'scratch/flash_dump_20261002.jsonl'

print(f"Connecting to {port} at {baud} bps for full LittleFS dump...")

try:
    ser = serial.Serial(port, baud, timeout=3)
    ser.dtr = True
    ser.rts = True
    time.sleep(1)
    ser.reset_input_buffer()
    
    print("Sending 'dump' command to ESP32-C6...")
    ser.write(b"dump\n")
    
    dumping = False
    dumped_lines = []
    start_time = time.time()
    last_recv_time = time.time()
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        while True:
            # 10초 이상 데이터가 안 들어오거나 총 120초 경과 시 타임아웃
            if time.time() - last_recv_time > 8.0 and dumping:
                print("Dump completed (no more data received).")
                break
            if time.time() - start_time > 120:
                print("Dump timeout (120s limit reached).")
                break
                
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                last_recv_time = time.time()
                
                if "LittleFS 블랙박스 덤프 시작" in line:
                    dumping = True
                    print(">>> Dump transmission started!")
                    continue
                elif "덤프 종료" in line:
                    print(f">>> {line}")
                    break
                
                if dumping:
                    if line.startswith("{") and line.endswith("}"):
                        f_out.write(line + "\n")
                        dumped_lines.append(line)
                        if len(dumped_lines) % 500 == 0:
                            print(f"Dumped {len(dumped_lines)} records...")
            else:
                time.sleep(0.01)
                
    ser.close()
    
    print("\n" + "=" * 60)
    print(f"덤프 완료! 총 {len(dumped_lines)} 건의 레코드가 '{output_file}'에 저장되었습니다.")
    print("=" * 60)
    
except Exception as e:
    print(f"Error during dump: {e}")
