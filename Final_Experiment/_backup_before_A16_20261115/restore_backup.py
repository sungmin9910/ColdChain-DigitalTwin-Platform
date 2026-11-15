"""
A16(도소매 도착) 및 소비자 주행 루트 연동 이전 상태로 즉시 복구하는 원클릭 롤백 스크립트.

사용법:
  1) 소스코드 원상복구:
     python Final_Experiment/_backup_before_A16_20261115/restore_backup.py --files

  2) 스캐너(ESP32) 펌웨어까지 이전 버전으로 재업로드 (예: COM16):
     python Final_Experiment/_backup_before_A16_20261115/restore_backup.py --files --flash COM16

  3) AWS RDS qr 테이블에 추가된 컬럼(Retail_AD, truck_device) 및 A16 레코드 제거:
     python Final_Experiment/_backup_before_A16_20261115/restore_backup.py --db
"""
import argparse
import os
import shutil
import subprocess
from pathlib import Path
import pymysql

BACKUP_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKUP_DIR.parent.parent

FILE_MAP = {
    "main.cpp.bak": REPO_ROOT / "Final_Experiment" / "2_ESP32_Firmware" / "src" / "main.cpp",
    "platformio.ini.bak": REPO_ROOT / "Final_Experiment" / "2_ESP32_Firmware" / "platformio.ini",
    "pc_qr_scanner.py.bak": REPO_ROOT / "Final_Experiment" / "pc_qr_scanner.py",
    "Step5_Run_Dashboard.py.bak": REPO_ROOT / "Final_Experiment" / "3_Consumer_Dashboard" / "Step5_Run_Dashboard.py",
}


def restore_files():
    for bak_name, dest_path in FILE_MAP.items():
        src = BACKUP_DIR / bak_name
        if src.exists():
            shutil.copy2(src, dest_path)
            print(f"[OK] 파일 복원 완료: {dest_path.relative_to(REPO_ROOT)}")


def flash_scanner(port: str):
    py_exe = Path.home() / ".platformio" / "penv" / "Scripts" / "python.exe"
    esptool_py = Path.home() / ".platformio" / "packages" / "tool-esptoolpy" / "esptool.py"
    boot_app0 = Path.home() / ".platformio" / "packages" / "framework-arduinoespressif32@3.20014.231204" / "tools" / "partitions" / "boot_app0.bin"
    cmd = [
        str(py_exe), str(esptool_py),
        "--chip", "esp32", "--port", port, "--baud", "115200",
        "--before", "no_reset", "--after", "hard_reset",
        "write_flash", "-z", "--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", "4MB",
        "0x1000", str(BACKUP_DIR / "bootloader_before_A16.bin"),
        "0x8000", str(BACKUP_DIR / "partitions_before_A16.bin"),
        "0xe000", str(boot_app0),
        "0x10000", str(BACKUP_DIR / "firmware_before_A16.bin"),
    ]
    print("[INFO] 먼저 스캐너 보드의 [BOOT] 누른 채 [EN] 1회 클릭 후 손을 떼어 다운로드 모드로 진입시켜 주세요.")
    print(f"[RUN] 스캐너 이전 바이너리 즉시 복원 실행: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("[OK] 스캐너 펌웨어 원상복구 완료!")


def rollback_db():
    conn = pymysql.connect(
        host="labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com",
        port=3306,
        user="admin",
        password=os.getenv("DB_PASSWORD", "12345678"),
        database="lab225",
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM qr WHERE Lo = 'A16'")
            cur.execute("SHOW COLUMNS FROM qr")
            cols = {r[0] for r in cur.fetchall()}
            if "Retail_AD" in cols:
                cur.execute("ALTER TABLE qr DROP COLUMN Retail_AD")
            if "truck_device" in cols:
                cur.execute("ALTER TABLE qr DROP COLUMN truck_device")
        conn.commit()
        print("[OK] AWS RDS lab225.qr 스키마 및 A16 레코드 롤백 완료!")
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Roll back A16 & consumer route changes.")
    parser.add_argument("--files", action="store_true", help="백업된 원본 소스코드 파일 복원")
    parser.add_argument("--flash", type=str, default="", help="복원된 펌웨어를 지정 COM 포트(예: COM16)로 업로드")
    parser.add_argument("--db", action="store_true", help="AWS RDS qr 테이블의 신규 컬럼(Retail_AD, truck_device) 제거")
    args = parser.parse_args()

    if not (args.files or args.flash or args.db):
        parser.print_help()
    else:
        if args.files:
            restore_files()
        if args.flash:
            if not args.files:
                restore_files()
            flash_scanner(args.flash)
        if args.db:
            rollback_db()
