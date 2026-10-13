import os
import sys
import subprocess
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ESPTOOL_PATH = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool.py"
BUILD_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\Final_Experiment\2_ESP32_Firmware\.pio\build\esp32dev"

BOOTLOADER = os.path.join(BUILD_DIR, "bootloader.bin")
PARTITIONS = os.path.join(BUILD_DIR, "partitions.bin")
FIRMWARE = os.path.join(BUILD_DIR, "firmware.bin")
PORT = "COM16"

print("=" * 60)
print(f"[ColdChain 스캐너 ESP32 플래싱 - 대상 포트: {PORT}]")
print(f" - Bootloader: {os.path.getsize(BOOTLOADER):,} bytes")
print(f" - Partitions: {os.path.getsize(PARTITIONS):,} bytes")
print(f" - Firmware:   {os.path.getsize(FIRMWARE):,} bytes")
print("=" * 60)
print("👉 [안내] 플래시 전체 지우기(Erase) 후 자동인식 펌웨어를 업로드합니다.")
print("👉 지금 ESP32 보드의 [BOOT] 버튼을 누른 채로 [EN] 버튼을 '딸깍' 누르고 손을 떼세요!")
print("=" * 60)
sys.stdout.flush()

# 1. Erase flash
print("\n[1단계] 손상된 플래시 메모리 초기화 (Chip Erase)...")
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
    print("❌ Chip Erase 실패.")
    sys.exit(1)

print("✅ Chip Erase 성공! 3개 파티션 전체 클린 플래싱 시작...")
sys.stdout.flush()

# 2. Write all partitions
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
    "0x1000", BOOTLOADER,
    "0x8000", PARTITIONS,
    "0x10000", FIRMWARE
]

proc = subprocess.Popen(write_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', errors='replace')
for line in proc.stdout:
    sys.stdout.write(line)
    sys.stdout.flush()

proc.wait()
if proc.returncode == 0:
    print("\n" + "=" * 60)
    print("🎉🎉🎉 [축하합니다! 펌웨어 업로드 완벽 성공!] 🎉🎉🎉")
    print("스마트 QR 스캐너가 이제 완제품 상태로 자동 인식(AUTO) 모드로 정상 부팅됩니다.")
    print("=" * 60)
else:
    print(f"\n❌ 플래싱 실패 코드: {proc.returncode}")
sys.exit(proc.returncode)
