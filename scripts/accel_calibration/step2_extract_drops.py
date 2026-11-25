#!/usr/bin/env python3
"""
Step 2: Wireless LittleFS Drop-Test Extractor & Immediate Quality Check (QC)
Reads 400 Hz binary drop events dumped from accel_calibration_400hz.cpp,
applies IEEE Std 1293 static calibration, and checks:
  - Peak G & saturation (< 15.5 G check)
  - Free-fall duration t_fall_meas vs theoretical sqrt(2h/g)
  - Impulse-momentum velocity change dV_meas vs theoretical sqrt(2gh)
  - Max angular velocity (rotation/tilt check)
"""

import argparse
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import serial
import serial.tools.list_ports

G0 = 9.80665

MAC_TO_DEVICE = {
    "F0:F5:BD:2C:48:5C": "carrier-c6-02",
    "CC:8D:A2:FA:84:EC": "carrier-c6-03",
    "CC:8D:A2:FA:9F:BC": "carrier-c6-04",
}


def detect_port(preferred: str | None) -> str:
    if preferred:
        return preferred
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        if "usb" in desc and "bluetooth" not in desc:
            return p.device
    raise RuntimeError("USB 시리얼 포트를 찾지 못했습니다. --port COM38 처럼 지정해 주세요.")


def send_and_read_until(ser: serial.Serial, cmd: str, end_marker: str, timeout: float = 20.0) -> list[str]:
    ser.reset_input_buffer()
    ser.write((cmd.strip() + "\n").encode("utf-8"))
    ser.flush()
    lines: list[str] = []
    t0 = time.time()
    while time.time() - t0 < timeout:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode("utf-8", errors="replace").strip()
        if line:
            lines.append(line)
            if end_marker in line:
                break
    return lines


def load_cal_params(device_dir: Path) -> dict | None:
    p = device_dir / "calibration_params.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def apply_calibration(df: pd.DataFrame, params: dict | None) -> pd.DataFrame:
    out = df.copy()
    if params:
        b = params["bias_g"]
        s = params["scale_factor"]
        out["ax_cal"] = (out["ax_g"] - b["x"]) / s["x"]
        out["ay_cal"] = (out["ay_g"] - b["y"]) / s["y"]
        out["az_cal"] = (out["az_g"] - b["z"]) / s["z"]
    else:
        out["ax_cal"] = out["ax_g"]
        out["ay_cal"] = out["ay_g"]
        out["az_cal"] = out["az_g"]
    out["mag_g"] = np.sqrt(out["ax_cal"] ** 2 + out["ay_cal"] ** 2 + out["az_cal"] ** 2)
    out["gyro_mag_dps"] = np.sqrt(out["gx_dps"] ** 2 + out["gy_dps"] ** 2 + out["gz_dps"] ** 2)
    return out


def analyze_single_drop(df: pd.DataFrame, height_cm: float) -> dict:
    t_s = df["t_ms"].to_numpy() / 1000.0
    mag = df["mag_g"].to_numpy()
    ax = df["ax_cal"].to_numpy()
    ay = df["ay_cal"].to_numpy()
    az = df["az_cal"].to_numpy()
    gyro = df["gyro_mag_dps"].to_numpy()

    # Primary impact peak
    peak_idx = int(np.argmax(mag))
    peak_g = float(mag[peak_idx])
    peak_axis_abs = float(max(abs(ax[peak_idx]), abs(ay[peak_idx]), abs(az[peak_idx])))
    saturated = peak_axis_abs >= 15.5

    # Determine dominant vertical axis from stationary pre-drop window (first 150 samples)
    pre_n = min(150, max(20, peak_idx - 50))
    pre_means = np.array([np.mean(ax[:pre_n]), np.mean(ay[:pre_n]), np.mean(az[:pre_n])])
    dom_idx = int(np.argmax(np.abs(pre_means)))
    dom_sign = 1.0 if pre_means[dom_idx] >= 0 else -1.0
    dom_axis_name = ("+X" if dom_sign > 0 else "-X", "+Y" if dom_sign > 0 else "-Y", "+Z" if dom_sign > 0 else "-Z")[dom_idx]

    # Free-fall segment immediately preceding peak_idx (mag < 0.50 g)
    ff_mask = mag[:peak_idx] < 0.50
    ff_indices = np.where(ff_mask)[0]
    t_fall_meas_ms = 0.0
    t_impact_start = peak_idx
    if len(ff_indices) >= 3:
        # Take the contiguous free-fall segment closest to peak_idx
        splits = np.where(np.diff(ff_indices) > 3)[0]
        last_seg = ff_indices[splits[-1] + 1 :] if len(splits) > 0 else ff_indices
        if len(last_seg) >= 3:
            t_fall_meas_ms = float((t_s[last_seg[-1]] - t_s[last_seg[0]]) * 1000.0)
            t_impact_start = int(last_seg[-1])

    # Impact contact pulse boundaries [i1, i2] around peak_idx where mag > 1.0 g
    i1 = peak_idx
    while i1 > max(0, t_impact_start - 5) and mag[i1] > 1.0:
        i1 -= 1
    i2 = peak_idx
    while i2 < len(mag) - 1 and mag[i2] > 1.0:
        i2 += 1

    # Impulse-momentum velocity change: integral of (a_net) dt during impact pulse
    # Use net magnitude (mag - 1.0)*G0 (robust to slight orientation change) and dominant axis projection
    a_dom = (ax, ay, az)[dom_idx] * dom_sign
    dv_axis_ms = float(np.trapezoid(np.maximum(0.0, a_dom[i1 : i2 + 1] - 1.0) * G0, t_s[i1 : i2 + 1]))
    dv_mag_ms = float(np.trapezoid(np.maximum(0.0, mag[i1 : i2 + 1] - 1.0) * G0, t_s[i1 : i2 + 1]))
    pulse_ms = float((t_s[i2] - t_s[i1]) * 1000.0)

    # Max gyro during free-fall + impact window
    win_start = max(0, i1 - 120)
    win_end = min(len(gyro), i2 + 20)
    max_gyro_dps = float(np.max(gyro[win_start:win_end]))

    h_m = height_cm / 100.0
    t_fall_ref_ms = math.sqrt(2.0 * h_m / G0) * 1000.0 if h_m > 0 else 0.0
    v_in_ref_ms = math.sqrt(2.0 * G0 * h_m) if h_m > 0 else 0.0

    return {
        "dom_axis": dom_axis_name,
        "peak_g": peak_g,
        "peak_axis_abs_g": peak_axis_abs,
        "saturated": saturated,
        "pulse_ms": pulse_ms,
        "t_fall_meas_ms": t_fall_meas_ms,
        "t_fall_ref_ms": t_fall_ref_ms,
        "dv_meas_ms": dv_mag_ms,
        "dv_axis_ms": dv_axis_ms,
        "v_in_ref_ms": v_in_ref_ms,
        "max_gyro_dps": max_gyro_dps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract 400Hz wireless drops from LittleFS & run QC")
    parser.add_argument("--port", default=None, help="시리얼 포트 (예: COM38)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--device", default=None, help="장치 ID (미지정 시 MAC 자동 식별)")
    parser.add_argument("--height", type=float, required=True, help="이번에 수행한 낙하 높이 (cm, 예: 10)")
    parser.add_argument("--rebound", type=float, default=0.0, help="240fps 영상 반발 높이 h' (cm, 나중에 CSV에서 수정 가능)")
    parser.add_argument("--clear", action="store_true", help="추출 완료 후 보드 LittleFS 자동 초기화")
    parser.add_argument("--out-root", default="data/accel_calibration")
    args = parser.parse_args()

    port = detect_port(args.port)
    print(f"[INFO] 포트 연결 중: {port}...")
    with serial.Serial(port, args.baud, timeout=0.5) as ser:
        time.sleep(1.2)
        info_lines = send_and_read_until(ser, "info", "=== END_INFO ===", timeout=5.0)
        mac = "UNKNOWN"
        for ln in info_lines:
            if ln.startswith("MAC:"):
                mac = ln.split("MAC:", 1)[1].strip()
        device = args.device or MAC_TO_DEVICE.get(mac, f"carrier-{mac.replace(':', '')[-4:].lower()}")

        device_dir = Path(args.out_root) / device
        drops_dir = device_dir / "drops"
        drops_dir.mkdir(parents=True, exist_ok=True)
        params = load_cal_params(device_dir)

        print(f"  - 장치 ID   : {device} (MAC: {mac})")
        print(f"  - 정적 교정 : {'적용됨' if params else '미적용(원시값 사용 - step1 먼저 권장)'}")

        list_lines = send_and_read_until(ser, "list", "---DROP_LIST_END---", timeout=8.0)
        drop_ids = []
        in_tbl = False
        print("\n[보드 내 저장된 낙하 이벤트 목록]")
        for ln in list_lines:
            if ln.startswith("id,"):
                in_tbl = True
                print("  " + ln)
                continue
            if "---DROP_LIST_END---" in ln:
                break
            if in_tbl:
                print("  " + ln)
                parts = ln.split(",")
                if parts and parts[0].isdigit():
                    drop_ids.append(int(parts[0]))

        if not drop_ids:
            print("\n[INFO] 저장된 낙하 이벤트가 없습니다.")
            return

        meta_path = device_dir / "drop_metadata.csv"
        existing_meta = pd.read_csv(meta_path) if meta_path.exists() else pd.DataFrame()
        next_trial_idx = 1
        if not existing_meta.empty:
            same_h = existing_meta[existing_meta["height_cm"] == args.height]
            if not same_h.empty:
                next_trial_idx = int(same_h["trial"].max()) + 1

        new_rows = []
        print(f"\n[추출 및 즉시 검증 시작 — 낙하 높이 h = {args.height:.1f} cm]")
        for did in drop_ids:
            dump_lines = send_and_read_until(ser, f"dump {did}", f"---DROP_DUMP_END id={did}---", timeout=20.0)
            rows = []
            in_csv = False
            for ln in dump_lines:
                if ln.startswith("t_ms,"):
                    in_csv = True
                    continue
                if "---DROP_DUMP_END" in ln:
                    break
                if in_csv:
                    parts = ln.split(",")
                    if len(parts) == 7:
                        try:
                            rows.append([float(x) for x in parts])
                        except ValueError:
                            pass
            if not rows:
                print(f"  [WARN] drop {did}: 데이터 없음")
                continue

            df_raw = pd.DataFrame(rows, columns=["t_ms", "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps"])
            df_cal = apply_calibration(df_raw, params)
            qc = analyze_single_drop(df_cal, args.height)

            fname = f"h{int(round(args.height)):02d}cm_t{next_trial_idx:02d}_id{did:03d}.csv"
            df_cal.to_csv(drops_dir / fname, index=False)

            flags = []
            if qc["saturated"]:
                flags.append("SATURATED(>=15.5G!)")
            if qc["max_gyro_dps"] > 250.0:
                flags.append("HIGH_ROTATION")
            if qc["t_fall_meas_ms"] < 20.0:
                flags.append("NO_FREEFALL(BUMP?)")
            flag_str = " | ".join(flags) if flags else "OK"

            print(
                f"  -> {fname}: Peak={qc['peak_g']:5.2f}G ({qc['dom_axis']}) | "
                f"t_fall={qc['t_fall_meas_ms']:5.1f}ms (이론 {qc['t_fall_ref_ms']:.1f}ms) | "
                f"dV={qc['dv_meas_ms']:4.2f}m/s (v_in={qc['v_in_ref_ms']:.2f}) | "
                f"gyro={qc['max_gyro_dps']:5.1f}dps | [{flag_str}]"
            )

            new_rows.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "device": device,
                "file": fname,
                "height_cm": args.height,
                "trial": next_trial_idx,
                "rebound_h_cm": args.rebound,
                "valid": 0 if ("NO_FREEFALL" in flag_str or "SATURATED" in flag_str) else 1,
                **qc,
                "qc_flag": flag_str,
            })
            next_trial_idx += 1

        if new_rows:
            df_new = pd.DataFrame(new_rows)
            df_all = pd.concat([existing_meta, df_new], ignore_index=True) if not existing_meta.empty else df_new
            df_all.to_csv(meta_path, index=False, encoding="utf-8-sig")
            print(f"\n[저장 완료] 메타데이터: {meta_path} (총 {len(df_all)}건)")

            if any(r["saturated"] for r in new_rows):
                print("  [주의!] 15.5 G 이상 포화가 감지되었습니다! 더 높은 낙하는 중단하세요.")

        do_clear = args.clear
        if not do_clear:
            ans = input("\n보드 LittleFS 낙하 데이터를 비우고 다음 높이 실험을 준비할까요? (y/N): ").strip().lower()
            do_clear = ans == "y"
        if do_clear:
            res = send_and_read_until(ser, "clear", "[OK]", timeout=5.0)
            print("  " + " ".join(res))


if __name__ == "__main__":
    main()
