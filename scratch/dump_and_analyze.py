import serial
import time
import sys
import json
import os

sys.stdout.reconfigure(encoding='utf-8')

def main():
    port = "COM7"
    baud = 115200
    print(f"Connecting to {port} @ {baud}...")
    try:
        ser = serial.Serial(port, baud, timeout=2)
    except Exception as e:
        print(f"Error opening port {port}: {e}")
        return

    time.sleep(1.0)
    ser.reset_input_buffer()

    # 1. info 명령어 전송
    print("--> Sending 'info' command...")
    ser.write(b"info\n")
    time.sleep(1.5)
    info_lines = []
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            info_lines.append(line)
            print(f"  [Board] {line}")

    # 2. dump 명령어 전송
    backup_file = "scratch/dump_20261006_evening.jsonl"
    print(f"\n--> Sending 'dump' command to save to '{backup_file}'...")
    ser.reset_input_buffer()
    ser.write(b"dump\n")
    
    start_time = time.time()
    last_recv_time = time.time()
    dumping = False
    count = 0
    
    with open(backup_file, 'w', encoding='utf-8') as f_out:
        while True:
            if time.time() - last_recv_time > 4.0 and dumping:
                break
            if time.time() - start_time > 40:
                print("Timeout (40s)")
                break
            
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                last_recv_time = time.time()
                
                if "LittleFS 블랙박스 덤프 시작" in line:
                    dumping = True
                    print(">>> Dump streaming started...")
                    continue
                elif "덤프 종료" in line:
                    print(f">>> {line}")
                    break
                
                if dumping and line.startswith("{") and line.endswith("}"):
                    f_out.write(line + "\n")
                    count += 1
                    if count % 100 == 0:
                        print(f"   Received {count} records...")
            else:
                time.sleep(0.01)

    ser.close()
    print(f"\nCompleted! Dumped {count} records to {backup_file}")

    # 3. 덤프 파일 분석
    if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
        with open(backup_file, 'r', encoding='utf-8') as f:
            records = [json.loads(line) for line in f if line.strip()]
        print(f"\nTotal parsed records: {len(records)}")
        if records:
            print(f"First record: {records[0].get('timestamp_str')} | Lat:{records[0].get('lat')} Lng:{records[0].get('lng')} Spd:{records[0].get('speed')} Status:{records[0].get('status')}")
            print(f"Last record:  {records[-1].get('timestamp_str')} | Lat:{records[-1].get('lat')} Lng:{records[-1].get('lng')} Spd:{records[-1].get('speed')} Status:{records[-1].get('status')}")

            # 2026-10-06 레코드 필터
            today_records = [r for r in records if str(r.get('timestamp_str', '')).startswith('2026-10-06')]
            print(f"Records from today (2026-10-06): {len(today_records)}")
            if today_records:
                print(f"Today First: {today_records[0].get('timestamp_str')} | Lat:{today_records[0].get('lat')} Spd:{today_records[0].get('speed')}")
                print(f"Today Last:  {today_records[-1].get('timestamp_str')} | Lat:{today_records[-1].get('lat')} Spd:{today_records[-1].get('speed')}")

if __name__ == "__main__":
    main()
