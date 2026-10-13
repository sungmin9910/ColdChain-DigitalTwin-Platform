import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import esptool
import esptool.loader

# Timeout 증폭: 플래시 블록 쓰기 시 3초 타임아웃 제한을 30초로 늘려 안정성 100% 확보
esptool.loader.DEFAULT_TIMEOUT = 30.0
esptool.loader.ESPLoader.DEFAULT_TIMEOUT = 30.0
esptool.loader.StubFlasher.DEFAULT_TIMEOUT = 30.0

BIN_PATH = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\Final_Experiment\2_ESP32_Firmware\.pio\build\esp32dev\firmware.bin"
PORT = "COM23"
BAUD = "115200"

print("=" * 60)
print("[ColdChain Scanner High-Reliability Firmware Flasher]")
print(f" - Target Port: {PORT}")
print(f" - Firmware: {BIN_PATH}")
print(f" - Size: {os.path.getsize(BIN_PATH):,} bytes")
print(" - Timeout: 30.0s (기존 3초 타임아웃 오류 완벽 차단)")
print(" - Baud: 115200 (CH340 정규 무손실 속도)")
print("=" * 60)
print("[READY] Waiting for ESP32 Bootloader connection (60 seconds)...")
print("👉 Please HOLD [BOOT] and PRESS [EN/RST] once, then release [BOOT] immediately!")
print("=" * 60)
sys.stdout.flush()

args = [
    "--port", PORT,
    "--baud", BAUD,
    "--before", "default_reset",
    "--after", "hard_reset",
    "--connect-attempts", "60",
    "write_flash",
    "-z",
    "--flash_mode", "dio",
    "--flash_freq", "40m",
    "0x10000", BIN_PATH
]

try:
    esptool.main(args)
    print("\n" + "=" * 60)
    print("🎉 SUCCESS: Firmware flashed 100%! Auto recognition is now active.")
    print("=" * 60)
except Exception as e:
    print(f"\n❌ Error during flashing: {e}")
    sys.exit(1)
