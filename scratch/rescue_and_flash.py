import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ESPTOOL_PATH = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool.py"
BUILD_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\Final_Experiment\2_ESP32_Firmware\.pio\build\esp32dev"

BOOTLOADER = os.path.join(BUILD_DIR, "bootloader.bin")
PARTITIONS = os.path.join(BUILD_DIR, "partitions.bin")
FIRMWARE = os.path.join(BUILD_DIR, "firmware.bin")
PORT = "COM23"

print("=" * 60)
print("[ESP32 Rescue & Clean Flasher]")
print(f" - Bootloader: {os.path.getsize(BOOTLOADER):,} bytes")
print(f" - Partitions: {os.path.getsize(PARTITIONS):,} bytes")
print(f" - Firmware:   {os.path.getsize(FIRMWARE):,} bytes")
print("=" * 60)
print("👉 [복구 절차] 무한 재부팅 루프를 멈추기 위해:")
print(" 1. USB 케이블을 PC에서 뽑습니다.")
print(" 2. 보드의 [BOOT] 버튼을 손가락으로 꾹 누르고 계세요.")
print(" 3. [BOOT] 버튼을 누른 채로 USB를 다시 꽂습니다.")
print(" 4. 꽂은 후 [BOOT] 버튼에서 손을 떼세요!")
print("=" * 60)
sys.stdout.flush()

# Command to flash cleanly
cmd = [
    sys.executable,
    ESPTOOL_PATH,
    "--port", PORT,
    "--baud", "115200",
    "--before", "default_reset",
    "--after", "hard_reset",
    "--connect-attempts", "60",
    "write_flash",
    "-z",
    "--flash_mode", "dio",
    "--flash_freq", "40m",
    "0x1000", BOOTLOADER,
    "0x8000", PARTITIONS,
    "0x10000", FIRMWARE
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', errors='replace')
for line in proc.stdout:
    sys.stdout.write(line)
    sys.stdout.flush()

proc.wait()
if proc.returncode == 0:
    print("\n" + "=" * 60)
    print("🎉 [성공] 펌웨어 완벽 복구 및 업로드 완료!")
    print("이제 스마트 QR 스캐너가 부팅되어 자동 인식 모드로 동작합니다.")
    print("=" * 60)
else:
    print(f"\n❌ 실패 코드: {proc.returncode}")
sys.exit(proc.returncode)
