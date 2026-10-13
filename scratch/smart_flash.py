import os
import sys
import time
import serial
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = "COM16"
ESPTOOL_PATH = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool.py"
BUILD_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\Final_Experiment\2_ESP32_Firmware\.pio\build\esp32dev"

BOOTLOADER = os.path.join(BUILD_DIR, "bootloader.bin")
PARTITIONS = os.path.join(BUILD_DIR, "partitions.bin")
FIRMWARE = os.path.join(BUILD_DIR, "firmware.bin")

def run_cmd(cmd_list, desc=""):
    print(f"\n============================================================")
    print(f"🚀 {desc} 실행 중...")
    print(f"============================================================")
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', errors='replace')
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
    proc.wait()
    return proc.returncode

def main():
    print("=" * 65)
    print(f"[*] ColdChain 스마트 QR 스캐너 펌웨어 플래셔 (포트: {PORT})")
    print(f"    - Bootloader: {os.path.getsize(BOOTLOADER):,} bytes")
    print(f"    - Partitions: {os.path.getsize(PARTITIONS):,} bytes")
    print(f"    - Firmware:   {os.path.getsize(FIRMWARE):,} bytes")
    print("=" * 65)
    print("👉 [수행 방법]")
    print("   1. ESP32 보드 위의 [BOOT] 버튼을 손가락으로 꾹 누르고 계세요.")
    print("   2. 누른 상태에서 옆의 [EN] 버튼을 '딸깍' 1번 눌렀다 뗍니다.")
    print("   3. 마지막으로 [BOOT] 버튼에서도 손을 뗍니다.")
    print("👉 보드가 다운로드 모드(DOWNLOAD_BOOT)로 진입할 때까지 감지 대기합니다...")
    print("=" * 65)
    sys.stdout.flush()

    detected = False
    try:
        ser = serial.Serial(PORT, 115200, timeout=0.05)
        t_start = time.time()
        last_hint = 0
        while time.time() - t_start < 180:
            line = ser.readline()
            if line:
                decoded = line.decode('utf-8', errors='replace').strip()
                if "DOWNLOAD_BOOT" in decoded or "waiting for download" in decoded:
                    print(f"\n[보드 응답] {decoded}")
                    print("\n🎯🎯🎯 >>> 다운로드 모드(DOWNLOAD_BOOT) 진입 감지 성공! <<< 🎯🎯🎯")
                    detected = True
                    break
            if time.time() - last_hint > 5:
                print("⏳ [대기 중] [BOOT] 버튼을 누른 채로 [EN] 버튼을 딸깍 눌러주세요...")
                sys.stdout.flush()
                last_hint = time.time()
        ser.close()
    except Exception as e:
        print(f"시리얼 포트 에러: {e}")

    if not detected:
        print("\n⚠️ 타임아웃: 버튼 신호가 감지되지 않았습니다. 수동 재시도를 진행합니다.")
        return

    time.sleep(0.5)

    # 1. Erase Flash
    erase_cmd = [
        sys.executable, ESPTOOL_PATH,
        "--port", PORT,
        "--baud", "115200",
        "--before", "no_reset",
        "--after", "no_reset",
        "erase_flash"
    ]
    rc = run_cmd(erase_cmd, "1단계: 손상된 플래시 메모리 초기화 (Chip Erase)")
    if rc != 0:
        print(f"\n❌ Erase 실패 (코드: {rc})")
        return

    # 2. Write Flash
    write_cmd = [
        sys.executable, ESPTOOL_PATH,
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
    rc = run_cmd(write_cmd, "2단계: 3개 파티션 전체 클린 플래싱")
    if rc == 0:
        print("\n" + "=" * 65)
        print("🎉🎉🎉 [축하합니다! 펌웨어 플래싱이 100% 완료되었습니다!] 🎉🎉🎉")
        print("스마트 QR 스캐너가 이제 자동인식(AUTO) 모드로 정상 부팅됩니다.")
        print("=" * 65)
    else:
        print(f"\n❌ 플래싱 실패 (코드: {rc})")

if __name__ == '__main__':
    main()
