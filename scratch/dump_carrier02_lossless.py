import serial
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

port = 'COM8'
baud = 115200

print(f"Opening {port} for 100% lossless dump...")
ser = serial.Serial(port, baud, timeout=2)
time.sleep(0.5)

ser.reset_input_buffer()
print("Sending 'dump' command...")
ser.write(b"dump\n")

raw_lines = []
buffer = ""
dump_started = False
dump_ended = False
start_time = time.time()
last_time = time.time()

while True:
    if ser.in_waiting > 0:
        chunk = ser.read(ser.in_waiting).decode('utf-8', errors='replace')
        buffer += chunk
        last_time = time.time()
        
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            if "LittleFS 블랙박스 덤프 시작" in line:
                dump_started = True
                print(">>> Dump started!")
                continue
            if "덤프 종료" in line:
                dump_ended = True
                print(f">>> {line}")
                break
            if dump_started and not dump_ended:
                raw_lines.append(line)
        if dump_ended:
            break
    else:
        if dump_started and time.time() - last_time > 4.0:
            print(">>> Dump completed by timeout.")
            break
        if time.time() - start_time > 30.0:
            print(">>> Overall timeout reached.")
            break
        time.sleep(0.01)

ser.close()

# Process parsed lines
valid_json = []
non_json = []

for l in raw_lines:
    if l.startswith("{") and l.endswith("}"):
        try:
            obj = json.loads(l)
            valid_json.append(obj)
        except:
            non_json.append(l)
    else:
        # Check if line contains a json substring
        s_idx = l.find("{")
        e_idx = l.rfind("}")
        if s_idx != -1 and e_idx != -1 and e_idx > s_idx:
            sub = l[s_idx:e_idx+1]
            try:
                obj = json.loads(sub)
                valid_json.append(obj)
            except:
                non_json.append(l)
        else:
            non_json.append(l)

print(f"Total raw lines collected: {len(raw_lines)}")
print(f"Successfully decoded JSON objects: {len(valid_json)}")
print(f"Non-JSON lines (logs/headers): {len(non_json)}")

# Save all valid JSONs
out_path = 'scratch/carrier02_full_dump.jsonl'
with open(out_path, 'w', encoding='utf-8') as f:
    for obj in valid_json:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')

print(f"Saved to {out_path}")
