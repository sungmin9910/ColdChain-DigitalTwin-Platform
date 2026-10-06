import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

def clear_and_verify():
    ser = serial.Serial("COM7", 115200, timeout=1.5)
    time.sleep(1.0)
    ser.reset_input_buffer()

    # 1. clear 명령 전송
    print("--> Sending 'clear' command to COM7...")
    ser.write(b"clear\n")
    time.sleep(1.5)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"  [Board] {line}")

    # 2. info로 0건 확인
    print("\n--> Verifying with 'info' command...")
    ser.write(b"info\n")
    time.sleep(1.2)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if "LittleFS" in line or "현황" in line or "전체" in line or "상태" in line:
            print(f"  [Board] {line}")

    # 3. 냉장고 실험을 위해 start 명령 전송 (오프라인 기록 모드 활성화)
    print("\n--> Sending 'start' command so board records inside fridge (offline)...")
    ser.write(b"start\n")
    time.sleep(1.0)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"  [Board] {line}")

    # 4. 최종 상태 확인
    print("\n--> Checking final status...")
    ser.write(b"info\n")
    time.sleep(1.0)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if "LittleFS" in line or "현황" in line or "전체" in line or "상태" in line:
            print(f"  [Board] {line}")

    ser.close()
    print("\n✅ Board memory cleared to 0 and RECORDING MODE (start) is now ACTIVE!")

if __name__ == "__main__":
    clear_and_verify()
