import serial
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = "COM16"
print(f"[{PORT} 실시간 스캐너 로그 대기 시작]")
print("👉 물리 스캐너로 QR 코드를 스캔하면 여기에 결과가 즉시 표시됩니다...")
sys.stdout.flush()

try:
    ser = serial.Serial(PORT, 115200, timeout=1)
    while True:
        line = ser.readline()
        if line:
            text = line.decode('utf-8', errors='replace').strip()
            if text:
                print(f"[SCANNER] {text}")
                sys.stdout.flush()
except Exception as e:
    print(f"시리얼 오류: {e}")
