#!/usr/bin/env python3
"""
Step 2: Dump 20-Hour Lossless LittleFS CSV (/chamber_cal.csv) from CarrierBoard
Target Firmware: chamber_calibration_env.cpp ([env:beetle_c6_chamber_cal])

Usage:
  python scripts/chamber_calibration/step2_dump_littlefs_csv.py --port COM38
  python scripts/chamber_calibration/step2_dump_littlefs_csv.py --port COM38 --boot-kst "2026-11-26 09:00:00"
"""

import argparse
import re
import time
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import serial
import serial.tools.list_ports

KST = timezone(timedelta(hours=9))


def detect_port(preferred: str | None) -> str:
    if preferred:
        return preferred
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        if "usb" in desc and "bluetooth" not in desc:
            return p.device
    raise RuntimeError("USB 시리얼 포트를 찾지 못했습니다. --port COM38 형태로 지정해 주세요.")


def dump_from_serial(port: str, baud: int, timeout_s: float) -> tuple[dict[str, str], list[str]]:
    meta: dict[str, str] = {"device": "carrier-c6-unknown", "mac": "UNKNOWN"}
    csv_lines: list[str] = []

    with serial.Serial(port, baud, timeout=1.0) as ser:
        time.sleep(1.0)
        ser.reset_input_buffer()
        ser.write(b"dump\n")
        ser.flush()

        in_block = False
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            raw = ser.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            if "---CHAMBER_CSV_START---" in line:
                in_block = True
                continue
            if "---CHAMBER_CSV_END---" in line:
                break
            if in_block:
                if line.startswith("#"):
                    m_dev = re.search(r"device=(\S+)", line)
                    m_mac = re.search(r"mac=(\S+)", line)
                    if m_dev:
                        meta["device"] = m_dev.group(1)
                    if m_mac:
                        meta["mac"] = m_mac.group(1)
                else:
                    csv_lines.append(line)

    return meta, csv_lines


def reconstruct_timestamps(df: pd.DataFrame, boot_kst_str: str | None) -> pd.DataFrame:
    out = df.copy()
    if boot_kst_str:
        boot_dt = datetime.strptime(boot_kst_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST)
        out["timestamp_kst"] = [
            (boot_dt + timedelta(milliseconds=float(ms))).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            for ms in out["uptime_ms"]
        ]
        return out

    valid_mask = out["epoch_s"] >= 1700000000
    if valid_mask.any():
        # Anchor boot epoch from valid NTP/RTC rows so early pre-WiFi rows also get exact timestamps!
        idx_ref = valid_mask.idxmax()
        anchor_epoch = float(out.loc[idx_ref, "epoch_s"]) - float(out.loc[idx_ref, "uptime_ms"]) / 1000.0
        out["reconstructed_epoch_s"] = anchor_epoch + out["uptime_ms"].astype(float) / 1000.0
        out["timestamp_kst"] = [
            datetime.fromtimestamp(ep, tz=KST).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            for ep in out["reconstructed_epoch_s"]
        ]
    else:
        out["timestamp_kst"] = ""
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump LittleFS /chamber_cal.csv over USB Serial")
    parser.add_argument("--port", default=None, help="시리얼 포트 (예: COM38)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=120.0, help="최대 덤프 대기 시간(초)")
    parser.add_argument("--boot-kst", default=None, help="수기 메모한 전원 ON 시각 (예: '2026-11-26 09:00:00')")
    parser.add_argument("--out-root", default="data/chamber_calibration")
    args = parser.parse_args()

    port = detect_port(args.port)
    print(f"[INFO] {port} 에서 /chamber_cal.csv 덤프 수신 중...")
    meta, csv_lines = dump_from_serial(port, args.baud, args.timeout)

    if not csv_lines:
        raise RuntimeError("CSV 데이터를 수신하지 못했습니다. 챔버 펌웨어 플래싱 여부를 확인해 주세요.")

    df = pd.read_csv(StringIO("\n".join(csv_lines)))
    df = reconstruct_timestamps(df, args.boot_kst)

    dev_dir = Path(args.out_root) / meta["device"]
    dev_dir.mkdir(parents=True, exist_ok=True)
    tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = dev_dir / f"chamber_raw_{tag}.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    dur_hr = (df["uptime_ms"].max() - df["uptime_ms"].min()) / 3_600_000.0 if len(df) > 1 else 0.0
    print("=" * 68)
    print(f"[OK] 덤프 저장 완료: {out_csv}")
    print(f"  - 장치 ID / MAC : {meta['device']} ({meta['mac']})")
    print(f"  - 총 샘플 수    : {len(df):,} 행 (경과 시간: {dur_hr:.2f} 시간)")
    if len(df) > 0:
        print(f"  - 온도 범위     : {df['temp_c'].min():.3f} ~ {df['temp_c'].max():.3f} °C")
        print(f"  - 습도 범위     : {df['rh_pct'].min():.3f} ~ {df['rh_pct'].max():.3f} %RH")
        print(f"  - 조도 범위     : {df['lux'].min():.1f} ~ {df['lux'].max():.1f} lx")
    print("=" * 68)


if __name__ == "__main__":
    main()
