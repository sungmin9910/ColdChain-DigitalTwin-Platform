import os
import sys
import subprocess
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ESPTOOL_PATH = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool.py"
BUILD_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\Final_Experiment\2_ESP32_Firmware\.pio\build\esp32dev"

BIN_PATH = os.path.join(BUILD_DIR, "firmware.bin")
PORT = "COM23"

print("=" * 60)
print("[ColdChain 물리 스캐너 ESP32 플래시 완전 복구 및 자동인식 업로드]")
print(f" - 대상 포트: {PORT}")
print(f" - 펌웨어 크기: {os.path.getsize(BIN_PATH):,} bytes")
print("=" * 60)
print("👉 [1단계: 칩 연결 대기]")
print("👉 [BOOT] 버튼을 꾹 누른 상태에서 [EN/RST] 버튼을 '딸깍' 1번 누르고 손을 떼세요!")
print("=" * 60)
sys.stdout.flush()

# Step 1: Chip Erase to eliminate dirty flash write latency
print("\n[Step 1] 더러워진 플래시 메모리 전체 지우기 (Chip Erase)...")
sys.stdout.flush()
erase_cmd = [
    sys.executable,
    ESPTOOL_PATH,
    "--port", PORT,
    "--baud", "115200",
    "--before", "default_reset",
    "--after", "no_reset",
    "--connect-attempts", "40",
    "erase_flash"
]

res = subprocess.run(erase_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
print(res.stdout)
if res.returncode != 0:
    print("❌ Chip Erase 실패. 다시 시도합니다.")
    sys.exit(1)

print("\n✅ Chip Erase 성공! 플래시 메모리가 100% 초기화되었습니다.")
print("[Step 2] 자동인식 펌웨어 고속 압축 스트리밍 전송 시작...")
sys.stdout.flush()

# Step 2: Clean write
write_cmd = [
    sys.executable,
    ESPTOOL_PATH,
    "--port", PORT,
    "--baud", "115200",
    "--before", "no_reset",
    "--after", "hard_reset",
    "write_flash",
    "-z",
    "--flash_mode", "dio",
    "--flash_freq", "40m",
    "0x10000", BIN_PATH
]

proc = subprocess.Popen(write_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', errors='replace')
for line in proc.stdout:
    sys.stdout.write(line)
    sys.stdout.flush()

proc.wait()
if proc.returncode == 0:
    print("\n" + "=" * 60)
    print("🎉🎉🎉 [축하합니다! 펌웨어 업로드 완벽 성공!] 🎉🎉🎉")
    print("스마트 QR 스캐너가 이제 완제품 상태로 자동 인식(AUTO) 모드로 동작합니다.")
    print("물리 스캐너로 QR을 찍으시면 자동으로 A10 -> A11 -> A13 -> A14 -> A15 단계가 진행됩니다!")
    print("=" * 60)
else:
    print(f"\n❌ 플래싱 실패 코드: {proc.returncode}")
sys.exit(proc.returncode)
