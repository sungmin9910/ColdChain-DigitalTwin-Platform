import serial
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Opening {port} to dump LittleFS records...")
ser = serial.Serial(port, baud, timeout=2)
time.sleep(0.5)

ser.reset_input_buffer()
print("Sending 'dump' command...")
ser.write(b"dump\n")

byte_buf = bytearray()
lines = []
dump_started = False
dump_ended = False
start_time = time.time()
last_time = time.time()

while True:
    if ser.in_waiting > 0:
        chunk = ser.read(ser.in_waiting)
        byte_buf.extend(chunk)
        last_time = time.time()
        
        while b'\n' in byte_buf:
            idx = byte_buf.find(b'\n')
            raw_line = bytes(byte_buf[:idx]).strip()
            del byte_buf[:idx+1]
            
            line_str = raw_line.decode('utf-8', errors='replace')
            if not line_str:
                continue
            if "LittleFS 블랙박스 덤프 시작" in line_str:
                dump_started = True
                print(">>> Dump started!")
                continue
            if "덤프 종료" in line_str:
                dump_ended = True
                print(f">>> {line_str}")
                break
            if dump_started and not dump_ended:
                lines.append(line_str)
        if dump_ended:
            break
    else:
        if dump_started and time.time() - last_time > 3.0:
            print(">>> Dump completed by timeout.")
            break
        if time.time() - start_time > 20.0:
            print(">>> Overall timeout.")
            break
        time.sleep(0.01)

ser.close()

valid_json = []
for l in lines:
    s_idx = l.find("{")
    e_idx = l.rfind("}")
    if s_idx != -1 and e_idx != -1 and e_idx > s_idx:
        sub = l[s_idx:e_idx+1]
        try:
            obj = json.loads(sub)
            valid_json.append(obj)
        except:
            pass

print(f"Total lines: {len(lines)}, Valid JSON: {len(valid_json)}")

out_file = 'scratch/carrier02_dump_1017.jsonl'
with open(out_file, 'w', encoding='utf-8') as f:
    for obj in valid_json:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')

print(f"Saved to {out_file}")
