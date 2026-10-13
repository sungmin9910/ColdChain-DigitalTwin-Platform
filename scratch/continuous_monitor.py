import serial
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
log_file = r'scratch/diagnostic_stream.log'

print("Starting continuous diagnostic logger on COM37...")
try:
    ser = serial.Serial('COM37', 115200, timeout=1)
    ser.dtr = True
    ser.rts = True
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n--- Logger started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.flush()
        while True:
            line = ser.readline()
            if line:
                decoded = line.decode('utf-8', errors='replace').rstrip()
                if decoded:
                    out = f"{decoded}\n"
                    print(decoded)
                    f.write(out)
                    f.flush()
except Exception as e:
    print(f"Logger stopped: {e}")
