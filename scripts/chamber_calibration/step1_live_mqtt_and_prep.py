#!/usr/bin/env python3
"""
Step 1: Climatic Chamber Pre-Flight Board Setup & Live 4-Pod MQTT Recorder
Target Firmware: chamber_calibration_env.cpp ([env:beetle_c6_chamber_cal])

Usage Examples:
  1) Pre-flight setup on each board (sync KST clock, optional Wi-Fi AP, clear old CSV):
     python scripts/chamber_calibration/step1_live_mqtt_and_prep.py --prep --port COM38 --clear
     python scripts/chamber_calibration/step1_live_mqtt_and_prep.py --prep --port COM38 --wifi-ssid "Lab24G" --wifi-pass "12345678" --clear

  2) Run live 20-hour MQTT collector on laptop next to chamber:
     python scripts/chamber_calibration/step1_live_mqtt_and_prep.py --listen
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import serial
import serial.tools.list_ports

MYSQL_HOST = os.environ.get("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")
MYSQL_V2_DATABASE = os.environ.get("MYSQL_V2_DATABASE", "lab225_v2")
CHAMBER_TABLE = "chamber_calibration_logs"


def detect_port(preferred: str | None) -> str:
    if preferred:
        return preferred
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        if "usb" in desc and "bluetooth" not in desc:
            return p.device
    raise RuntimeError("USB 시리얼 포트를 찾지 못했습니다. --port COM38 형태로 지정해 주세요.")


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


def run_board_prep(args: argparse.Namespace) -> None:
    port = detect_port(args.port)
    print(f"[INFO] 보드 시리얼 연결 중: {port} ({args.baud} bps)")
    with serial.Serial(port, args.baud, timeout=0.6) as ser:
        time.sleep(1.0)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[1/4] 노트북 현재 시각(KST) 동기화 전송 -> {now_str}")
        for ln in send_cmd(ser, f"settime {now_str}"):
            print("  ", ln)

        if args.wifi_ssid:
            wifi_cmd = f"wifi {args.wifi_ssid} {args.wifi_pass}".strip()
            print(f"[2/4] 현장 Wi-Fi AP 등록 중 -> SSID='{args.wifi_ssid}'")
            for ln in send_cmd(ser, wifi_cmd, timeout=10.0):
                print("  ", ln)
        else:
            print("[2/4] 추가 Wi-Fi 미지정 (기존 등록 AP 유지)")

        if args.clear:
            print("[3/4] 기존 /chamber_cal.csv 초기화 (clear)...")
            for ln in send_cmd(ser, "clear"):
                print("  ", ln)
        else:
            print("[3/4] 기존 CSV 유지 (--clear 미사용)")

        send_cmd(ser, "resume")
        print("[4/4] 보드 최종 상태 점검 (info):")
        for ln in send_cmd(ser, "info", end_marker="=== END_INFO ===", timeout=6.0):
            print("  ", ln)


def run_mqtt_listener(args: argparse.Namespace) -> None:
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise RuntimeError("paho-mqtt 패키지가 필요합니다: pip install paho-mqtt") from exc

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    session_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"mqtt_chamber_live_{session_tag}.csv"

    fieldnames = [
        "pc_time_kst",
        "pc_epoch_s",
        "device",
        "mac",
        "board_time_kst",
        "board_epoch_s",
        "uptime_ms",
        "temp_c",
        "rh_pct",
        "lux",
        "g_force",
        "rssi",
        "topic",
    ]

    csv_file = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    csv_file.flush()

    db_conn = None
    if not args.no_db:
        try:
            import pymysql

            db_conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_V2_DATABASE,
                charset="utf8mb4",
                connect_timeout=8,
                autocommit=True,
            )
            with db_conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS `{MYSQL_V2_DATABASE}`.`{CHAMBER_TABLE}` (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        session_date DATE NOT NULL,
                        device_id VARCHAR(32) NOT NULL,
                        mac VARCHAR(24) DEFAULT NULL,
                        timestamp_kst VARCHAR(32) NOT NULL,
                        epoch_s BIGINT DEFAULT 0,
                        uptime_ms BIGINT DEFAULT 0,
                        temperature DOUBLE NOT NULL,
                        humidity DOUBLE NOT NULL,
                        lux DOUBLE DEFAULT 0.0,
                        g_force DOUBLE DEFAULT 1.0,
                        rssi INT DEFAULT -127,
                        created_at DATETIME NOT NULL,
                        UNIQUE KEY uk_dev_ts_up (device_id, timestamp_kst, uptime_ms),
                        KEY idx_session_dev (session_date, device_id),
                        KEY idx_dev_ts (device_id, timestamp_kst)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
            print(f"[DB] AWS RDS 전용 테이블 준비 완료 -> {MYSQL_V2_DATABASE}.{CHAMBER_TABLE}")
        except Exception as exc:
            print(f"[DB WARN] AWS RDS 연결 생략 (로컬 CSV만 저장합니다): {exc}")
            db_conn = None

    counts: dict[str, int] = {}

    def on_connect(client, userdata, flags, rc, *extra):
        print(f"[MQTT] 브로커 연결 완료 ({args.broker}:{args.port_mqtt}, rc={rc}) -> 구독: {args.topic}")
        client.subscribe(args.topic)

    def on_message(client, userdata, msg):
        nonlocal db_conn
        now_dt = datetime.now()
        try:
            payload = json.loads(msg.payload.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            return

        dev = str(payload.get("device", "unknown"))
        counts[dev] = counts.get(dev, 0) + 1
        raw_ts = str(payload.get("timestamp_str") or "").strip()
        ts_kst = raw_ts[:19] if (len(raw_ts) >= 19 and not raw_ts.startswith("00:00")) else now_dt.strftime("%Y-%m-%d %H:%M:%S")
        row = {
            "pc_time_kst": now_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "pc_epoch_s": f"{now_dt.timestamp():.3f}",
            "device": dev,
            "mac": payload.get("mac", ""),
            "board_time_kst": ts_kst,
            "board_epoch_s": payload.get("epoch_s", 0),
            "uptime_ms": payload.get("uptime_ms", 0),
            "temp_c": payload.get("temperature", ""),
            "rh_pct": payload.get("humidity", ""),
            "lux": payload.get("lux", ""),
            "g_force": payload.get("g_force", ""),
            "rssi": payload.get("rssi", ""),
            "topic": msg.topic,
        }
        writer.writerow(row)
        csv_file.flush()

        db_tag = "CSV"
        if db_conn is not None:
            try:
                db_conn.ping(reconnect=True)
                dt_utc = datetime.strptime(ts_kst, "%Y-%m-%d %H:%M:%S") - timedelta(hours=9)
                with db_conn.cursor() as cur:
                    cur.execute(
                        f"""
                        INSERT IGNORE INTO `{MYSQL_V2_DATABASE}`.`{CHAMBER_TABLE}`
                        (session_date, device_id, mac, timestamp_kst, epoch_s, uptime_ms,
                         temperature, humidity, lux, g_force, rssi, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            ts_kst[:10],
                            dev,
                            str(row["mac"]),
                            ts_kst,
                            int(row["board_epoch_s"] or 0),
                            int(row["uptime_ms"] or 0),
                            float(row["temp_c"] or 0.0),
                            float(row["rh_pct"] or 0.0),
                            float(row["lux"] or 0.0),
                            float(row["g_force"] or 1.0),
                            int(row["rssi"] or -127),
                            dt_utc.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                db_tag = "CSV+RDS"
            except Exception as exc:
                db_tag = f"CSV(DB_ERR:{exc})"

        print(
            f"[{row['pc_time_kst']}] {dev} (#{counts[dev]}) [{db_tag}] | "
            f"T={row['temp_c']} C | RH={row['rh_pct']} % | RSSI={row['rssi']}"
        )

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[START] 실시간 MQTT 챔버 백업 파일: {csv_path}")
    print("        종료하려면 Ctrl+C 를 누르세요.")
    try:
        client.connect(args.broker, args.port_mqtt, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n[DONE] 수신 종료. 누적 저장: {counts} -> {csv_path}")
    finally:
        csv_file.close()
        if db_conn is not None:
            try:
                db_conn.close()
            except Exception:
                pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Chamber Calibration Board Prep & Live MQTT Logger")
    parser.add_argument("--prep", action="store_true", help="USB 연결된 보드 시각 동기화/Wi-Fi 등록/초기화 수행")
    parser.add_argument("--listen", action="store_true", help="노트북에서 4개 보드 MQTT 패킷 실시간 CSV + AWS RDS 전용 테이블 저장")
    parser.add_argument("--port", default=None, help="시리얼 포트 (예: COM38)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--wifi-ssid", default=None, help="현장 2.4GHz Wi-Fi SSID 등록")
    parser.add_argument("--wifi-pass", default="", help="현장 2.4GHz Wi-Fi 비밀번호")
    parser.add_argument("--clear", action="store_true", help="보드 내 기존 /chamber_cal.csv 초기화")
    parser.add_argument("--broker", default="broker.hivemq.com")
    parser.add_argument("--port-mqtt", type=int, default=1883)
    parser.add_argument("--topic", default="coldchain/chamber/+")
    parser.add_argument("--no-db", action="store_true", help="AWS RDS DB 저장을 끄고 로컬 CSV만 저장")
    parser.add_argument("--out-dir", default="data/chamber_calibration/mqtt_live")
    args = parser.parse_args()

    if not args.prep and not args.listen:
        parser.print_help()
        sys.exit(1)

    if args.prep:
        run_board_prep(args)
    if args.listen:
        run_mqtt_listener(args)


if __name__ == "__main__":
    main()
