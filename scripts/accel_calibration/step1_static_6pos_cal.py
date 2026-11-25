#!/usr/bin/env python3
"""
Step 1: IEEE Std 1293 6-Position Static Accelerometer Calibration
Target: CarrierBoard Beetle ESP32-C6 + MPU6050 (accel_calibration_400hz.cpp)
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import serial
import serial.tools.list_ports

MAC_TO_DEVICE = {
    "F0:F5:BD:2C:48:5C": "carrier-c6-02",
    "CC:8D:A2:FA:84:EC": "carrier-c6-03",
    "CC:8D:A2:FA:9F:BC": "carrier-c6-04",
}

POSES = [
    ("pos_Z", "z", +1, "1/6: [+Z 위] 기판 정면(또는 +Z축)이 수직 위를 향하게 평평히 놓으세요"),
    ("neg_Z", "z", -1, "2/6: [-Z 위] 1번 자세에서 정확히 180도 뒤집어 평평히 놓으세요"),
    ("pos_X", "x", +1, "3/6: [+X 위] 기판의 한쪽 옆면(+X축)이 수직 위를 향하게 세우세요"),
    ("neg_X", "x", -1, "4/6: [-X 위] 3번 자세에서 정확히 180도 뒤집어 세우세요"),
    ("pos_Y", "y", +1, "5/6: [+Y 위] 남은 옆면(+Y축)이 수직 위를 향하게 세우세요"),
    ("neg_Y", "y", -1, "6/6: [-Y 위] 5번 자세에서 정확히 180도 뒤집어 세우세요"),
]


def detect_port(preferred: str | None) -> str:
    if preferred:
        return preferred
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
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


def parse_info(lines: list[str]) -> dict:
    info = {"mac": "UNKNOWN", "mpu": "UNKNOWN", "live": ""}
    for ln in lines:
        if ln.startswith("MAC:"):
            info["mac"] = ln.split("MAC:", 1)[1].strip()
        elif ln.startswith("MPU6050:"):
            info["mpu"] = ln.split("MPU6050:", 1)[1].strip()
        elif ln.startswith("LIVE:"):
            info["live"] = ln.split("LIVE:", 1)[1].strip()
    return info


def capture_static_csv(ser: serial.Serial, duration_s: float) -> pd.DataFrame:
    lines = send_and_read_until(ser, f"static {duration_s:.1f}", "---STATIC_END---", timeout=duration_s + 25.0)
    rows = []
    in_csv = False
    for ln in lines:
        if ln.startswith("t_ms,"):
            in_csv = True
            continue
        if "---STATIC_END---" in ln:
            break
        if in_csv:
            parts = ln.split(",")
            if len(parts) == 7:
                try:
                    rows.append([float(x) for x in parts])
                except ValueError:
                    pass
    if not rows:
        raise RuntimeError("정적 데이터를 수신하지 못했습니다. 시리얼 연결을 확인하세요.")
    return pd.DataFrame(rows, columns=["t_ms", "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps"])


def auto_identify_axis(mean_vec: dict[str, float]) -> tuple[str, int]:
    best_axis = max(("x", "y", "z"), key=lambda a: abs(mean_vec[a]))
    sign = +1 if mean_vec[best_axis] >= 0 else -1
    return best_axis, sign


def main() -> None:
    parser = argparse.ArgumentParser(description="IEEE Std 1293 6-Position Static Calibration")
    parser.add_argument("--port", default=None, help="시리얼 포트 (예: COM38)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--device", default=None, help="장치 이름 (미지정 시 MAC으로 자동 식별)")
    parser.add_argument("--duration", type=float, default=8.0, help="자세당 수집 시간(초, 최대 10초)")
    parser.add_argument("--trim", type=float, default=1.0, help="앞뒤 제외 시간(초)")
    parser.add_argument("--out-root", default="data/accel_calibration", help="결과 저장 루트 폴더")
    args = parser.parse_args()

    port = detect_port(args.port)
    print(f"[INFO] 포트 연결 중: {port} ({args.baud} bps)...")
    with serial.Serial(port, args.baud, timeout=0.5) as ser:
        time.sleep(1.2)
        info_lines = send_and_read_until(ser, "info", "=== END_INFO ===", timeout=5.0)
        info = parse_info(info_lines)
        mac = info["mac"]
        device = args.device or MAC_TO_DEVICE.get(mac, f"carrier-{mac.replace(':', '')[-4:].lower()}")

        print(f"  - MAC 주소 : {mac}")
        print(f"  - 장치 ID  : {device}")
        print(f"  - MPU6050  : {info['mpu']}")
        print(f"  - 현재 값  : {info['live']}")
        if "OK" not in info["mpu"]:
            print("[ERR] MPU6050이 정상 인식되지 않았습니다. 배선/소켓을 확인하세요.")
            sys.exit(1)

        out_dir = Path(args.out_root) / device
        static_dir = out_dir / "static"
        static_dir.mkdir(parents=True, exist_ok=True)

        print("\n============================================================")
        print("  IEEE Std 1293: 6-자세 정적 중력 캘리브레이션 시작")
        print("  * 어느 축이 위를 향하든 자동으로 (+X/-X/+Y/-Y/+Z/-Z) 판별합니다.")
        print("  * 정육면체 지그의 6개 면을 하나씩 평평히 놓아 주세요.")
        print("============================================================\n")

        captured: dict[str, dict] = {}
        needed_keys = ["+x", "-x", "+y", "-y", "+z", "-z"]

        step_idx = 0
        while len(captured) < 6:
            remaining = [k for k in needed_keys if k not in captured]
            print(f"\n[진행 {len(captured)}/6] 아직 필요한 방향: {', '.join(remaining)}")

            # Show current reading and allow 'r' refresh until level
            while True:
                cur_info = parse_info(send_and_read_until(ser, "info", "=== END_INFO ===", timeout=4.0))
                print(f"  현재 센서값: {cur_info['live']}")
                user_in = input("  -> 수평 맞췄으면 [Enter] | 값 다시보기 [r] | 종료 [q]: ").strip().lower()
                if user_in == "q":
                    print("사용자에 의해 중단되었습니다.")
                    sys.exit(0)
                if user_in == "r":
                    continue
                break

            print(f"  수집 중 ({args.duration:.1f}초, 움직이지 마세요)...")
            df = capture_static_csv(ser, args.duration)

            t_max = df["t_ms"].max()
            trim_ms = args.trim * 1000.0
            core = df[(df["t_ms"] >= trim_ms) & (df["t_ms"] <= (t_max - trim_ms))]
            if len(core) < 100:
                core = df

            means = {
                "x": float(core["ax_g"].mean()),
                "y": float(core["ay_g"].mean()),
                "z": float(core["az_g"].mean()),
            }
            stds = {
                "x": float(core["ax_g"].std()),
                "y": float(core["ay_g"].std()),
                "z": float(core["az_g"].std()),
            }
            axis, sign = auto_identify_axis(means)
            key = f"{'+' if sign > 0 else '-'}{axis}"
            max_std = max(stds.values())
            mag = float(np.sqrt(means["x"] ** 2 + means["y"] ** 2 + means["z"] ** 2))

            print(f"  [판별 결과] 방향={key.upper()} | 평균=({means['x']:+.4f}, {means['y']:+.4f}, {means['z']:+.4f}) g | |a|={mag:.4f} g | 최대SD={max_std:.5f} g")
            if max_std > 0.015:
                print("  [경고] 수집 중 흔들림이 큽니다(SD > 0.015g). 다시 측정하는 것을 권장합니다.")
            if key in captured:
                ans = input(f"  이미 측정된 방향({key.upper()})입니다. 덮어쓸까요? (y/N): ").strip().lower()
                if ans != "y":
                    continue

            fname = f"pose_{'pos' if sign > 0 else 'neg'}_{axis.upper()}.csv"
            df.to_csv(static_dir / fname, index=False)
            captured[key] = {
                "file": fname,
                "n_total": int(len(df)),
                "n_core": int(len(core)),
                "means": means,
                "stds": stds,
                "raw_mag": mag,
            }
            step_idx += 1

        # Compute IEEE Std 1293 Bias and Scale Factor
        bias = {}
        scale = {}
        for ax in ("x", "y", "z"):
            yp = captured[f"+{ax}"]["means"][ax]
            ym = captured[f"-{ax}"]["means"][ax]
            bias[ax] = (yp + ym) / 2.0
            scale[ax] = (yp - ym) / 2.0

        # Evaluate before vs after RMSE across all 6 poses
        raw_mags = []
        cal_mags = []
        pose_summary = []
        for k in needed_keys:
            m = captured[k]["means"]
            rm = float(np.sqrt(m["x"] ** 2 + m["y"] ** 2 + m["z"] ** 2))
            cx = (m["x"] - bias["x"]) / scale["x"]
            cy = (m["y"] - bias["y"]) / scale["y"]
            cz = (m["z"] - bias["z"]) / scale["z"]
            cm = float(np.sqrt(cx ** 2 + cy ** 2 + cz ** 2))
            raw_mags.append(rm)
            cal_mags.append(cm)
            pose_summary.append({
                "pose": k.upper(),
                "raw_x": m["x"], "raw_y": m["y"], "raw_z": m["z"], "raw_mag": rm,
                "cal_x": cx, "cal_y": cy, "cal_z": cz, "cal_mag": cm,
                "raw_err_g": rm - 1.0,
                "cal_err_g": cm - 1.0,
            })

        raw_rmse = float(np.sqrt(np.mean((np.array(raw_mags) - 1.0) ** 2)))
        cal_rmse = float(np.sqrt(np.mean((np.array(cal_mags) - 1.0) ** 2)))

        params = {
            "device": device,
            "mac": mac,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "standard": "IEEE Std 1293 (6-Position Static Gravity Calibration)",
            "sample_rate_hz": 400,
            "range_g": 16,
            "lpf_hz": 260,
            "bias_g": bias,
            "scale_factor": scale,
            "raw_rmse_g": raw_rmse,
            "cal_rmse_g": cal_rmse,
            "improvement_pct": (1.0 - cal_rmse / raw_rmse) * 100.0 if raw_rmse > 0 else 0.0,
            "poses": pose_summary,
        }

        param_path = out_dir / "calibration_params.json"
        with open(param_path, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2, ensure_ascii=False)

        print("\n============================================================")
        print("  6-자세 정적 캘리브레이션 완료!")
        print("============================================================")
        for ax in ("x", "y", "z"):
            print(f"  {ax.upper()}축: Bias = {bias[ax]:+.5f} g | Scale Factor = {scale[ax]:.5f}")
        print(f"\n  보정 전 1g 기준 RMSE : {raw_rmse:.5f} g")
        print(f"  보정 후 1g 기준 RMSE : {cal_rmse:.5f} g  (오차 {params['improvement_pct']:.1f}% 감소)")
        print(f"  저장 경로            : {param_path}")
        print("============================================================")


if __name__ == "__main__":
    main()
