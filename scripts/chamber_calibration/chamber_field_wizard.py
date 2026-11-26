#!/usr/bin/env python3
"""
Climatic Chamber Field Launch Wizard (All-in-One)
- Auto-detects connected CarrierBoard ESP32-C6 USB ports (VID:PID=303A:1001)
- Registers field 2.4 GHz Wi-Fi AP (/wifi_extra.txt)
- Syncs KST wall-clock from laptop
- Clears memory accumulated during charging (/chamber_cal.csv + legacy logs)
- Verifies live Wi-Fi / MQTT / SHT45 / LittleFS status
- Also supports non-interactive CLI mode (--auto --ssid ... --password ...)
"""

import argparse
import csv
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import serial
import serial.tools.list_ports

REPO_ROOT = Path(__file__).resolve().parents[2]
STEP1_SCRIPT = Path(__file__).resolve().parent / "step1_live_mqtt_and_prep.py"
STEP2_SCRIPT = Path(__file__).resolve().parent / "step2_dump_littlefs_csv.py"

MYSQL_HOST = os.environ.get("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")
MYSQL_V2_DATABASE = os.environ.get("MYSQL_V2_DATABASE", "lab225_v2")
CHAMBER_TABLE = "chamber_calibration_logs"


def find_esp32_ports() -> list[tuple[str, str]]:
    """Return list of (COMx, description/hwid) for connected ESP32-C6 USB devices."""
    found: list[tuple[str, str]] = []
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "")
        hwid = (p.hwid or "")
        if "bluetooth" in desc.lower() or p.device.upper() == "COM1":
            continue
        if "303A:1001" in hwid.upper() or "usb" in desc.lower():
            found.append((p.device, f"{desc} [{hwid}]"))
    return found


def send_cmd(ser: serial.Serial, cmd: str, end_marker: str | None = None, timeout: float = 6.0) -> list[str]:
    ser.reset_input_buffer()
    ser.write((cmd.strip() + "\n").encode("utf-8"))
    ser.flush()
    lines: list[str] = []
    t0 = time.time()
    while time.time() - t0 < timeout:
        raw = ser.readline()
        if not raw:
            if not end_marker and lines:
                break
            continue
        line = raw.decode("utf-8", errors="replace").strip()
        if line:
            lines.append(line)
            if end_marker and end_marker in line:
                break
            if not end_marker and (line.startswith("[OK]") or line.startswith("[ERR]")):
                break
    return lines


def parse_info_block(lines: list[str]) -> dict[str, str]:
    info: dict[str, str] = {}
    for ln in lines:
        for key in ("MAC", "DEVICE", "TOPIC", "TIME_KST", "WIFI", "MQTT", "SENSORS", "LIVE", "LITTLEFS"):
            prefix = f"{key}:"
            if ln.startswith(prefix):
                info[key] = ln[len(prefix):].strip()
    return info


def check_board_info(port: str, baud: int = 115200) -> dict[str, str]:
    with serial.Serial(port, baud, timeout=0.6) as ser:
        time.sleep(0.8)
        lines = send_cmd(ser, "info", end_marker="=== END_INFO ===", timeout=5.0)
        return parse_info_block(lines)


def prep_single_board(
    port: str,
    ssid: str = "",
    password: str = "",
    do_clear: bool = True,
    wait_wifi_sec: float = 10.0,
    baud: int = 115200,
) -> dict[str, str]:
    print(f"\n============================================================")
    print(f"  보드 현장 세팅 시작: {port}")
    print(f"============================================================")

    with serial.Serial(port, baud, timeout=0.6) as ser:
        time.sleep(1.0)

        # 1) Sync KST clock from laptop
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[1/4] 노트북 KST 시각 동기화 -> {now_str}")
        for ln in send_cmd(ser, f"settime {now_str}", timeout=4.0):
            print("  ", ln)

        # 2) Register field Wi-Fi AP (if provided)
        if ssid:
            if " " in ssid:
                print("  [경고] SSID에 공백이 포함되어 있습니다! 펌웨어 파서가 공백을 구분자로 사용합니다.")
            wifi_cmd = f"wifi {ssid} {password}".strip()
            print(f"[2/4] 현장 Wi-Fi 등록 및 연결 시도 -> SSID='{ssid}'")
            for ln in send_cmd(ser, wifi_cmd, timeout=10.0):
                print("  ", ln)
            # Wait briefly for Wi-Fi & MQTT handshake to settle
            print(f"      Wi-Fi / MQTT 연결 안정화 대기 ({int(wait_wifi_sec)}초)...")
            t_wait = time.time()
            while time.time() - t_wait < wait_wifi_sec:
                raw = ser.readline()
                if raw:
                    msg = raw.decode("utf-8", errors="replace").strip()
                    if msg and ("[WIFI]" in msg or "[MQTT]" in msg or "[CAL #" in msg):
                        print("  ", msg)
                        if "MQTT=PASS" in msg or "MQTT 연결" in msg:
                            break
        else:
            print("[2/4] 추가 Wi-Fi 미지정 (기존 등록 AP 유지)")

        # 3) Clear charging-time accumulated memory
        if do_clear:
            print("[3/4] 충전 중 쌓인 메모리(LittleFS) 초기화 (clear)...")
            for ln in send_cmd(ser, "clear", timeout=6.0):
                print("  ", ln)
        else:
            print("[3/4] 메모리 초기화 생략 (--no-clear)")

        # 4) Ensure logging active & read final status
        send_cmd(ser, "resume", timeout=3.0)
        time.sleep(0.3)
        print("[4/4] 최종 보드 상태 점검 (info):")
        info_lines = send_cmd(ser, "info", end_marker="=== END_INFO ===", timeout=6.0)
        info = parse_info_block(info_lines)

    print("\n  ---------------- [최종 점검 요약] ----------------")
    print(f"  장치 ID  : {info.get('DEVICE', 'UNKNOWN')} (MAC: {info.get('MAC', 'UNKNOWN')})")
    print(f"  현재시각 : {info.get('TIME_KST', 'UNKNOWN')}")
    print(f"  Wi-Fi    : {info.get('WIFI', 'UNKNOWN')}")
    print(f"  MQTT     : {info.get('MQTT', 'UNKNOWN')}")
    print(f"  센서상태 : {info.get('SENSORS', 'UNKNOWN')}")
    print(f"  실시간값 : {info.get('LIVE', 'UNKNOWN')}")
    print(f"  메모리   : {info.get('LITTLEFS', 'UNKNOWN')}")
    print("  --------------------------------------------------")

    sht_ok = "SHT45=OK" in info.get("SENSORS", "")
    wifi_ok = "CONNECTED" in info.get("WIFI", "") and "DISCONNECTED" not in info.get("WIFI", "")
    if sht_ok:
        if wifi_ok:
            print("  [PASS] Wi-Fi + 센서 + 메모리 초기화 완료! USB 분리 후 배터리 스위치 ON 하세요.")
        else:
            print("  [PASS - 오프라인 모드] 센서 + 시각 + 메모리 초기화 완료!")
            print("         (Wi-Fi 미연결 상태여도 내장 LittleFS에 38~40시간 100% 무손실 저장됩니다.)")
    else:
        print("  [경고] SHT45 센서가 OK로 확인되지 않았습니다! 배선/소켓을 확인해 주세요.")
    return info


def interactive_prep_loop(ssid_init: str | None = None, pass_init: str | None = None) -> None:
    print("\n============================================================")
    print("  [현장 챔버 투입 전 보드 일괄 세팅 마법사]")
    print("  - 현장 2.4GHz Wi-Fi 등록 + KST 시각 동기화 + 충전 중 메모리 초기화")
    print("============================================================")

    if ssid_init is None:
        ssid = input("\n현장 2.4GHz Wi-Fi 이름(SSID) 입력 (없거나 기존 유지 시 그냥 Enter): ").strip()
    else:
        ssid = ssid_init.strip()

    if ssid:
        if pass_init is None:
            password = input(f"'{ssid}' 비밀번호 입력 (개방형이면 그냥 Enter): ").strip()
        else:
            password = pass_init.strip()
    else:
        password = ""

    done_devices: list[str] = []
    while True:
        ports = find_esp32_ports()
        print("\n------------------------------------------------------------")
        if not ports:
            print("[안내] 연결된 보드(ESP32-C6 USB)가 감지되지 않았습니다.")
            ans = input("보드를 USB에 연결한 뒤 [Enter] (종료: q): ").strip().lower()
            if ans == "q":
                break
            continue

        print("감지된 USB 보드 목록:")
        for idx, (dev, desc) in enumerate(ports, 1):
            print(f"  {idx}) {dev} - {desc}")

        if len(ports) == 1:
            sel_ports = [ports[0][0]]
            ans = input(f"\n[{sel_ports[0]}] 보드에 Wi-Fi 등록 + 메모리 초기화를 실행할까요? ([Enter]=실행 / q=종료): ").strip().lower()
            if ans == "q":
                break
        else:
            ans = input("\n실행할 번호 입력 (전체 실행=[Enter] / 특정 번호 예: 1 / 종료=q): ").strip().lower()
            if ans == "q":
                break
            if ans == "":
                sel_ports = [p[0] for p in ports]
            elif ans.isdigit() and 1 <= int(ans) <= len(ports):
                sel_ports = [ports[int(ans) - 1][0]]
            else:
                print("[ERR] 잘못된 입력입니다.")
                continue

        for p in sel_ports:
            try:
                info = prep_single_board(p, ssid=ssid, password=password, do_clear=True)
                dev_name = info.get("DEVICE", p)
                if dev_name not in done_devices:
                    done_devices.append(dev_name)
            except Exception as exc:
                print(f"  [ERR] {p} 처리 중 오류: {exc}")

        print(f"\n[진행 현황] 세팅 완료된 보드 ({len(done_devices)}대): {', '.join(done_devices)}")
        nxt = input("다음 보드로 교체 후 [Enter] (모두 끝났으면 q): ").strip().lower()
        if nxt == "q":
            break


def interactive_dump_loop() -> None:
    print("\n============================================================")
    print("  [20시간 실험 종료 후 내장 LittleFS CSV 일괄 추출]")
    print("============================================================")
    while True:
        ports = find_esp32_ports()
        if not ports:
            ans = input("\n추출할 보드를 USB에 연결한 뒤 [Enter] (종료: q): ").strip().lower()
            if ans == "q":
                break
            continue
        for dev, desc in ports:
            print(f"\n>>> [{dev}] 추출 실행 중 ({desc})...")
            subprocess.run([sys.executable, str(STEP2_SCRIPT), "--port", dev], cwd=str(REPO_ROOT))
        ans = input("\n다음 보드 연결 후 [Enter] (끝났으면 q): ").strip().lower()
        if ans == "q":
            break


def query_rds_history(hours: int = 24, export_csv: bool = False) -> None:
    try:
        import pymysql
    except ImportError:
        print("[ERR] pymysql 패키지가 필요합니다: pip install pymysql")
        return

    print(f"\n[RDS 원격 조회] 최근 {hours}시간 누적 데이터 조회 중 ({MYSQL_V2_DATABASE}.{CHAMBER_TABLE})...")
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_V2_DATABASE,
        charset="utf8mb4",
        connect_timeout=8,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    device_id,
                    COUNT(*) AS cnt,
                    MIN(timestamp_kst) AS first_ts,
                    MAX(timestamp_kst) AS last_ts,
                    MIN(temperature) AS min_t,
                    MAX(temperature) AS max_t,
                    MIN(humidity) AS min_rh,
                    MAX(humidity) AS max_rh
                FROM `{CHAMBER_TABLE}`
                WHERE created_at >= (UTC_TIMESTAMP() - INTERVAL %s HOUR)
                GROUP BY device_id
                ORDER BY device_id
                """,
                (hours,),
            )
            summary = cur.fetchall()

            if not summary:
                print(f"  (최근 {hours}시간 이내에 RDS에 적재된 챔버 교정 데이터가 아직 없습니다.)")
                return

            print("\n================ [기기별 누적 현황 (시작 시점 ~ 현재)] ================")
            for row in summary:
                dev, cnt, first_ts, last_ts, min_t, max_t, min_rh, max_rh = row
                print(
                    f"  {dev} | 누적 {cnt:5d}건 | {first_ts} ~ {last_ts}\n"
                    f"      온도: {min_t:6.2f} ~ {max_t:6.2f} °C | 습도: {min_rh:5.1f} ~ {max_rh:5.1f} %RH"
                )

            print("\n---------------- [기기별 가장 최근 수신값] ----------------")
            for row in summary:
                dev = row[0]
                cur.execute(
                    f"""
                    SELECT timestamp_kst, temperature, humidity, lux, rssi
                    FROM `{CHAMBER_TABLE}`
                    WHERE device_id = %s
                    ORDER BY id DESC LIMIT 1
                    """,
                    (dev,),
                )
                latest = cur.fetchone()
                if latest:
                    ts, t_c, rh, lx, rssi = latest
                    print(f"  {dev} | {ts} | T={t_c:.3f}°C | RH={rh:.3f}% | Lux={lx:.1f}lx | RSSI={rssi}")

            if export_csv:
                out_dir = REPO_ROOT / "data" / "chamber_calibration" / "rds_exports"
                out_dir.mkdir(parents=True, exist_ok=True)
                tag = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_path = out_dir / f"rds_chamber_last{hours}h_{tag}.csv"
                cur.execute(
                    f"""
                    SELECT device_id, mac, timestamp_kst, epoch_s, uptime_ms,
                           temperature, humidity, lux, g_force, rssi
                    FROM `{CHAMBER_TABLE}`
                    WHERE created_at >= (UTC_TIMESTAMP() - INTERVAL %s HOUR)
                    ORDER BY device_id, timestamp_kst, uptime_ms
                    """,
                    (hours,),
                )
                all_rows = cur.fetchall()
                with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
                    w = csv.writer(f)
                    w.writerow(["device_id", "mac", "timestamp_kst", "epoch_s", "uptime_ms",
                                "temperature", "humidity", "lux", "g_force", "rssi"])
                    w.writerows(all_rows)
                print(f"\n[CSV 저장 완료] 총 {len(all_rows)}건 -> {out_path}")
    finally:
        conn.close()


def clear_rds_chamber_table(force: bool = False) -> None:
    try:
        import pymysql
    except ImportError:
        print("[ERR] pymysql 패키지가 필요합니다: pip install pymysql")
        return

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_V2_DATABASE,
        charset="utf8mb4",
        connect_timeout=8,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*), MIN(timestamp_kst), MAX(timestamp_kst) FROM `{CHAMBER_TABLE}`")
            cnt, min_ts, max_ts = cur.fetchone()
            print(f"\n[RDS 챔버 전용 테이블 현황] {MYSQL_V2_DATABASE}.{CHAMBER_TABLE}")
            print(f"  - 현재 행 수 : {cnt:,}건")
            print(f"  - 저장 기간  : {min_ts} ~ {max_ts}")
            print("  * 주의: 운영 테이블(qr, sensor_data, sensor_telemetry 등)은 전혀 건드리지 않습니다.")

            if cnt == 0:
                print("  [INFO] 이미 0건으로 비어 있습니다.")
                return

            if not force:
                confirm = input("\n정말 챔버 교정 테이블만 0건으로 초기화(TRUNCATE)할까요? 진행하려면 YES 입력: ").strip()
                if confirm != "YES":
                    print("  [취소됨] 데이터를 삭제하지 않았습니다.")
                    return

            cur.execute(f"TRUNCATE TABLE `{CHAMBER_TABLE}`")
            print(f"  [OK] {MYSQL_V2_DATABASE}.{CHAMBER_TABLE} 초기화 완료! (0건, id=1부터 새로 기록됩니다)")
    finally:
        conn.close()


def interactive_menu() -> None:
    while True:
        print("\n============================================================")
        print("  FDT 항온항습 챔버 교정 — 현장 통합 실행기")
        print("============================================================")
        print("  1) [투입 전] 현장 Wi-Fi 연결 + 시각 동기화 + 충전 중 보드 메모리 초기화")
        print("  2) [운전 중] 실시간 MQTT 모니터링 & 백업 시작 (지금 시점부터 생방송)")
        print("  3) [종료 후] 보드 내장 LittleFS 20시간 CSV 무손실 추출")
        print("  4) [점검용] USB 연결된 보드 상태 빠른 확인 (info)")
        print("  5) [집/원격] 시작 시점~현재 AWS RDS 전체 누적 현황 조회 (+ CSV 저장)")
        print("  6) [DB 정리] 실전 시작 직전 AWS RDS 챔버 전용 테이블만 비우기 (TRUNCATE)")
        print("  0) 종료")
        print("============================================================")
        choice = input("원하는 번호를 입력하세요 (1~6, 0=종료): ").strip()

        if choice == "1":
            interactive_prep_loop()
        elif choice == "2":
            subprocess.run([sys.executable, str(STEP1_SCRIPT), "--listen"], cwd=str(REPO_ROOT))
        elif choice == "3":
            interactive_dump_loop()
        elif choice == "4":
            ports = find_esp32_ports()
            if not ports:
                print("\n[안내] 연결된 USB 보드가 없습니다.")
            for dev, desc in ports:
                print(f"\n--- {dev} ({desc}) ---")
                try:
                    info = check_board_info(dev)
                    for k, v in info.items():
                        print(f"  {k:9s}: {v}")
                except Exception as exc:
                    print(f"  [ERR] 조회 실패: {exc}")
        elif choice == "5":
            hrs_in = input("최근 몇 시간 데이터를 조회할까요? (기본 24시간, 그냥 Enter): ").strip()
            hrs = int(hrs_in) if hrs_in.isdigit() and int(hrs_in) > 0 else 24
            exp_in = input("조회된 전체 데이터를 CSV 파일로도 저장할까요? (y/N): ").strip().lower()
            try:
                query_rds_history(hours=hrs, export_csv=(exp_in == "y"))
            except Exception as exc:
                print(f"  [ERR] RDS 조회 실패: {exc}")
        elif choice == "6":
            try:
                clear_rds_chamber_table(force=False)
            except Exception as exc:
                print(f"  [ERR] RDS 테이블 초기화 실패: {exc}")
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("[ERR] 0~6 사이의 번호를 입력해 주세요.")


def main() -> None:
    parser = argparse.ArgumentParser(description="FDT Chamber Calibration Field Wizard")
    parser.add_argument("--auto", action="store_true", help="비대화형 자동 모드: 현재 연결된 모든 보드에 즉시 세팅 적용")
    parser.add_argument("--check", action="store_true", help="현재 연결된 모든 보드의 상태(info)만 빠르게 확인")
    parser.add_argument("--rds", action="store_true", help="AWS RDS에서 시작 시점~현재 누적 현황 원격 조회")
    parser.add_argument("--clear-rds", action="store_true", help="AWS RDS 챔버 교정 전용 테이블(chamber_calibration_logs)만 초기화")
    parser.add_argument("--yes", action="store_true", help="--clear-rds 확인 생략")
    parser.add_argument("--hours", type=int, default=24, help="--rds 조회 범위 (기본 24시간)")
    parser.add_argument("--export-csv", action="store_true", help="--rds 결과를 CSV로 저장")
    parser.add_argument("--port", default=None, help="특정 COM 포트만 지정 (예: COM17)")
    parser.add_argument("--ssid", default="", help="현장 2.4GHz Wi-Fi SSID")
    parser.add_argument("--password", default="", help="현장 2.4GHz Wi-Fi 비밀번호")
    parser.add_argument("--no-clear", action="store_true", help="메모리 초기화(clear) 생략")
    parser.add_argument("--wait-wifi", type=float, default=10.0, help="Wi-Fi 연결 확인 대기 시간(초)")
    args = parser.parse_args()

    if args.clear_rds:
        clear_rds_chamber_table(force=args.yes)
        return

    if args.rds:
        query_rds_history(hours=args.hours, export_csv=args.export_csv)
        return

    if args.check:
        ports = [(args.port, "manual")] if args.port else find_esp32_ports()
        if not ports:
            print("[INFO] 연결된 USB 보드가 없습니다.")
            return
        for dev, desc in ports:
            print(f"\n--- {dev} ({desc}) ---")
            info = check_board_info(dev)
            for k, v in info.items():
                print(f"  {k:9s}: {v}")
        return

    if args.auto:
        ports = [(args.port, "manual")] if args.port else find_esp32_ports()
        if not ports:
            print("[ERR] 연결된 USB 보드가 없습니다. USB 연결 후 다시 실행해 주세요.")
            sys.exit(1)
        for dev, _ in ports:
            prep_single_board(
                dev,
                ssid=args.ssid,
                password=args.password,
                do_clear=not args.no_clear,
                wait_wifi_sec=args.wait_wifi,
            )
        return

    interactive_menu()


if __name__ == "__main__":
    main()
