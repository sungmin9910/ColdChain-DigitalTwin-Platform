import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ESPTOOL_PATH = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool.py"
BIN_PATH = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\Final_Experiment\2_ESP32_Firmware\.pio\build\esp32dev\firmware.bin"
PORT = "COM23"
BAUD = "115200"

print("=" * 60)
print("[ColdChain Scanner Auto Firmware Flasher (ROM Bootloader Mode)]")
print(f" - Target Port: {PORT}")
print(f" - Firmware: {BIN_PATH}")
print(f" - Size: {os.path.getsize(BIN_PATH):,} bytes")
print("=" * 60)
print("[READY] Waiting for ESP32 Bootloader connection (60 seconds)...")
print("👉 Please HOLD [BOOT] and PRESS [EN/RST] once, then release [BOOT] immediately!")
print("=" * 60)
sys.stdout.flush()

cmd = [
    sys.executable,
    ESPTOOL_PATH,
    "--port", PORT,
    "--baud", BAUD,
    "--before", "default_reset",
    "--after", "hard_reset",
    "--connect-attempts", "60",
    "write_flash",
    "-z",
    "--flash_mode", "dio",
    "--flash_freq", "20m",
    "0x10000", BIN_PATH
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', errors='replace')
for line in proc.stdout:
    sys.stdout.write(line)
    sys.stdout.flush()

proc.wait()
if proc.returncode == 0:
    print("\n" + "=" * 60)
    print("SUCCESS: Firmware flashed 100%! Auto recognition is now active.")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("FAILED: Timeout waiting for download mode.")
    print("=" * 60)
sys.exit(proc.returncode)
