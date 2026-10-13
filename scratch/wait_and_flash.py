import os
import sys
import time
import subprocess
import serial.tools.list_ports

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ESPTOOL_PATH = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool.py"
BUILD_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\Final_Experiment\2_ESP32_Firmware\.pio\build\esp32dev"

BOOTLOADER = os.path.join(BUILD_DIR, "bootloader.bin")
PARTITIONS = os.path.join(BUILD_DIR, "partitions.bin")
FIRMWARE = os.path.join(BUILD_DIR, "firmware.bin")

print("=" * 60)
print("[ESP32 Auto-Detect & Rescue Flasher]")
print("👉 [안내] USB 케이블이 꽂히는 순간을 실시간 감지 중입니다...")
print("👉 [BOOT] 버튼을 손가락으로 누른 상태에서 USB를 PC에 꽂아주세요!")
print("=" * 60)
sys.stdout.flush()

detected_port = None
for _ in range(60):
    ports = [p.device for p in serial.tools.list_ports.comports() if "CH340" in p.description or "USB" in p.description or "CP210" in p.description]
    if ports:
        detected_port = ports[0]
        print(f"\n✅ 포트 감지 성공: {detected_port}!")
        break
    time.sleep(1)

if not detected_port:
    print("\n❌ 60초 내에 포트가 감지되지 않았습니다.")
    sys.exit(1)

# Allow 0.5s for Windows USB driver to settle
time.sleep(0.5)

cmd = [
    sys.executable,
    ESPTOOL_PATH,
    "--port", detected_port,
    "--baud", "115200",
    "--before", "default_reset",
    "--after", "hard_reset",
    "--connect-attempts", "20",
    "write_flash",
    "-z",
    "--flash_mode", "dio",
    "--flash_freq", "40m",
    "0x1000", BOOTLOADER,
    "0x8000", PARTITIONS,
    "0x10000", FIRMWARE
]

print(f"🚀 {detected_port} 포트에 즉시 펌웨어 복구 전송 시작...")
sys.stdout.flush()

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', errors='replace')
for line in proc.stdout:
    sys.stdout.write(line)
    sys.stdout.flush()

proc.wait()
if proc.returncode == 0:
    print("\n" + "=" * 60)
    print("🎉 [성공] 펌웨어 완벽 복구 및 업로드 완료!")
    print("이제 스마트 QR 스캐너가 정상 부팅되어 지능형 자동 단계 인식을 수행합니다.")
    print("=" * 60)
else:
    print(f"\n❌ 플래싱 실패 코드: {proc.returncode}")
sys.exit(proc.returncode)
