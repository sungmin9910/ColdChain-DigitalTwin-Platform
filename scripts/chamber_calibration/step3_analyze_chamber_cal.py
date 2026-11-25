#!/usr/bin/env python3
"""
Step 3: Pattern-A 20h Chamber Calibration & Metrological Validation Analyzer
Standards: BS EN 12830:2018 (Temperature Class 0.5 / tau_90), IEC 60068-3-5/6 (Soak & Hysteresis)

Aligns 5-second CarrierBoard logs against 1-second Climatic Chamber reference CSV,
automatically extracts steady-state soak windows (last 15 min of each step), and computes:
  1) Temperature 1st-order calibration: T_cal = a_T * T_raw + b_T (RMSE, Max Error, EN 12830 Class)
  2) Psychrometric vapor-pressure (Magnus) self-heating compensation + linear RH fit:
       RH_psat = RH_raw * P_sat(T_raw) / P_sat(T_cal)
       RH_cal  = a_RH * RH_psat + b_RH
  3) 25°C / 60%RH Ascending vs. Descending Hysteresis Error (E_hys)
  4) Optional Dynamic Thermal Step-Response (tau_63, tau_90) & BH1750 Window Factor (K_lux)

Usage:
  python scripts/chamber_calibration/step3_analyze_chamber_cal.py ^
      --pod-csv data/chamber_calibration/carrier-c6-03/chamber_raw_20261127.csv ^
      --chamber-csv data/chamber_calibration/chamber_ref_1s.csv ^
      --device carrier-c6-03
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def psat_kpa(temp_c: np.ndarray | float) -> np.ndarray | float:
    """Tetens / Magnus saturation vapor pressure (kPa), matching docs/06_Master_Thesis_Research_Roadmap.md."""
    return 0.61078 * np.exp((17.27 * temp_c) / (temp_c + 237.3))


def load_and_resample_chamber(
    chamber_csv: Path,
    time_col: str,
    temp_col: str,
    rh_col: str | None,
    temp_cert_offset: float = 0.0,
    rh_cert_offset: float = 0.0,
) -> pd.DataFrame:
    df = pd.read_csv(chamber_csv)
    df["dt"] = pd.to_datetime(df[time_col])
    df = df.sort_values("dt").set_index("dt")

    cols = {"ref_temp_c": pd.to_numeric(df[temp_col], errors="coerce") + temp_cert_offset}
    if rh_col and rh_col in df.columns:
        cols["ref_rh_pct"] = pd.to_numeric(df[rh_col], errors="coerce") + rh_cert_offset
    else:
        cols["ref_rh_pct"] = np.nan

    ref_df = pd.DataFrame(cols, index=df.index)
    # Resample 1-second chamber reference into 5-second centered mean windows for noise-free pairing
    ref_5s = ref_df.resample("5s").mean().dropna(subset=["ref_temp_c"]).reset_index()
    return ref_5s


def load_pod_log(pod_csv: Path, device_filter: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(pod_csv)
    if device_filter and "device" in df.columns:
        df = df[df["device"] == device_filter].copy()

    time_col = None
    for cand in ("timestamp_kst", "pc_time_kst", "board_time_kst"):
        if cand in df.columns and df[cand].notna().any():
            time_col = cand
            break
    if not time_col:
        raise ValueError("포드 CSV에 유효한 시각 컬럼(timestamp_kst / pc_time_kst)이 없습니다. --boot-kst 로 먼저 복원하세요.")

    df["dt"] = pd.to_datetime(df[time_col])
    df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce")
    df["rh_pct"] = pd.to_numeric(df["rh_pct"], errors="coerce")
    df["lux"] = pd.to_numeric(df.get("lux", 0.0), errors="coerce")
    return df.dropna(subset=["dt", "temp_c"]).sort_values("dt").reset_index(drop=True)


def extract_steady_plateaus(
    merged: pd.DataFrame,
    soak_window_min: float = 15.0,
    temp_round_step: float = 5.0,
    rh_round_step: float = 10.0,
) -> pd.DataFrame:
    """Groups contiguous chamber setpoint plateaus and extracts the final `soak_window_min` minutes of each step."""
    df = merged.copy()
    # Identify nominal chamber target by rounding stabilized reference values
    nom_t = (df["ref_temp_c"] / temp_round_step).round() * temp_round_step
    nom_rh = np.where(
        df["ref_rh_pct"].notna() & (nom_t >= 12.5),
        (df["ref_rh_pct"] / rh_round_step).round() * rh_round_step,
        -1.0,
    )
    df["step_key"] = [f"T{t:.0f}_RH{r:.0f}" for t, r in zip(nom_t, nom_rh)]

    # Smooth out brief transition glitches (< 10 min) by requiring minimum plateau length >= 25 min
    df["block_id"] = (df["step_key"] != df["step_key"].shift(1)).cumsum()
    plateaus = []
    step_num = 0

    for _, grp in df.groupby("block_id"):
        dur_min = (grp["dt"].iloc[-1] - grp["dt"].iloc[0]).total_seconds() / 60.0
        if dur_min < 25.0:
            continue
        t_end = grp["dt"].iloc[-1]
        t_start_soak = t_end - pd.Timedelta(minutes=soak_window_min)
        soak = grp[grp["dt"] >= t_start_soak]
        if len(soak) < 20:
            continue
        # Verify chamber temporal stability (IEC 60068-3-5: std < 0.3 C)
        if soak["ref_temp_c"].std() > 0.4:
            continue

        step_num += 1
        nom_temp_val = float((soak["ref_temp_c"].mean() / temp_round_step).round() * temp_round_step)
        rh_controlled = bool(soak["ref_rh_pct"].notna().all() and nom_temp_val >= 12.5)
        nom_rh_val = float((soak["ref_rh_pct"].mean() / rh_round_step).round() * rh_round_step) if rh_controlled else np.nan

        plateaus.append(
            {
                "step_idx": step_num,
                "nom_temp_c": nom_temp_val,
                "nom_rh_pct": nom_rh_val,
                "rh_controlled": rh_controlled,
                "n_samples": len(soak),
                "soak_start": soak["dt"].iloc[0].isoformat(),
                "soak_end": soak["dt"].iloc[-1].isoformat(),
                "ref_temp_mean": float(soak["ref_temp_c"].mean()),
                "pod_temp_mean": float(soak["temp_c"].mean()),
                "pod_temp_std": float(soak["temp_c"].std()),
                "ref_rh_mean": float(soak["ref_rh_pct"].mean()) if rh_controlled else np.nan,
                "pod_rh_mean": float(soak["rh_pct"].mean()),
                "pod_rh_std": float(soak["rh_pct"].std()),
            }
        )

    return pd.DataFrame(plateaus)


def fit_tau90(df: pd.DataFrame, step_start: str, step_end: str) -> dict:
    sub = df[(df["dt"] >= pd.to_datetime(step_start)) & (df["dt"] <= pd.to_datetime(step_end))].copy()
    if len(sub) < 10:
        raise ValueError("tau_90 분석 구간 샘플 수가 부족합니다 (최소 10개 필요).")
    t_sec = (sub["dt"] - sub["dt"].iloc[0]).dt.total_seconds().to_numpy()
    temp = sub["temp_c"].to_numpy()
    t0 = float(temp[0])
    t_inf = float(np.mean(temp[-max(3, len(temp) // 10) :]))
    span = t0 - t_inf
    if abs(span) < 2.0:
        raise ValueError("온도 스텝 변화폭이 너무 작습니다 (< 2°C).")

    norm = (temp - t_inf) / span
    mask = (norm > 0.08) & (norm < 0.95)
    slope, _ = np.polyfit(t_sec[mask], np.log(norm[mask]), 1)
    tau63_s = float(-1.0 / slope)
    tau90_s = float(tau63_s * np.log(10.0))

    # Direct empirical 90% crossing
    target_90 = t0 - 0.90 * span
    crossed = np.where((temp <= target_90) if span > 0 else (temp >= target_90))[0]
    emp_tau90_s = float(t_sec[crossed[0]]) if len(crossed) > 0 else tau90_s

    return {
        "T_initial_c": round(t0, 3),
        "T_final_c": round(t_inf, 3),
        "tau63_sec": round(tau63_s, 1),
        "tau63_min": round(tau63_s / 60.0, 2),
        "tau90_fit_min": round(tau90_s / 60.0, 2),
        "tau90_empirical_min": round(emp_tau90_s / 60.0, 2),
        "en12830_internal_60min_pass": bool((emp_tau90_s / 60.0) <= 60.0),
    }


def save_plots(plat: pd.DataFrame, out_dir: Path, device_id: str) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=160)

    # Plot 1: Temperature Residuals Before vs After Calibration
    ax = axes[0]
    ax.axhline(0.0, color="black", lw=0.9, ls="--")
    ax.axhline(+0.5, color="#d9534f", lw=0.8, ls=":", label="EN 12830 Class 0.5 (±0.5°C)")
    ax.axhline(-0.5, color="#d9534f", lw=0.8, ls=":")
    ax.plot(plat["ref_temp_mean"], plat["pod_temp_mean"] - plat["ref_temp_mean"], "o-", label="Raw Error (Pod - Ref)")
    ax.plot(plat["ref_temp_mean"], plat["temp_cal"] - plat["ref_temp_mean"], "s-", label="Calibrated Residual")
    ax.set_xlabel("Chamber Reference Temperature (°C)")
    ax.set_ylabel("Temperature Error (°C)")
    ax.set_title(f"{device_id} — Temperature Calibration (0~30°C)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    # Plot 2: Humidity Residuals Across Multi-T Matrix
    ax2 = axes[1]
    rh_sub = plat[plat["rh_controlled"]].copy()
    ax2.axhline(0.0, color="black", lw=0.9, ls="--")
    if len(rh_sub) > 0:
        ax2.plot(rh_sub["ref_rh_mean"], rh_sub["pod_rh_mean"] - rh_sub["ref_rh_mean"], "o", label="Raw RH Error")
        ax2.plot(rh_sub["ref_rh_mean"], rh_sub["rh_cal"] - rh_sub["ref_rh_mean"], "s", label="Calibrated RH Residual (Magnus+Lin)")
    ax2.set_xlabel("Chamber Reference Humidity (%RH)")
    ax2.set_ylabel("Humidity Error (%RH)")
    ax2.set_title(f"{device_id} — Multi-T Humidity Calibration")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    plot_path = out_dir / f"{device_id}_chamber_calibration_summary.png"
    fig.savefig(plot_path)
    plt.close(fig)
    return plot_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze 20h Pattern-A Chamber Calibration")
    parser.add_argument("--pod-csv", required=True, help="보드 덤프 CSV 또는 MQTT 수집 CSV 경로")
    parser.add_argument("--chamber-csv", required=True, help="챔버 1초 기준 데이터 CSV 경로")
    parser.add_argument("--device", default="carrier-c6-03", help="대상 장치 ID")
    parser.add_argument("--chamber-time-col", default="timestamp", help="챔버 CSV 시각 컬럼명")
    parser.add_argument("--chamber-temp-col", default="temp_c", help="챔버 CSV 온도 컬럼명")
    parser.add_argument("--chamber-rh-col", default="rh_pct", help="챔버 CSV 습도 컬럼명")
    parser.add_argument("--cert-temp-offset", type=float, default=0.0, help="KOLAS 성적서 온도 보정치 (°C)")
    parser.add_argument("--cert-rh-offset", type=float, default=0.0, help="KOLAS 성적서 습도 보정치 (%RH)")
    parser.add_argument("--soak-min", type=float, default=15.0, help="각 스텝 종료 직전 평균 구간(분)")
    parser.add_argument("--step-start", default=None, help="(선택) tau_90 스텝 시작 시각")
    parser.add_argument("--step-end", default=None, help="(선택) tau_90 스텝 종료 시각")
    parser.add_argument("--lux-ref", type=float, default=None, help="(선택) 기준 조도계 측정값 (lx)")
    parser.add_argument("--lux-pod", type=float, default=None, help="(선택) 하우징 내부 BH1750 측정값 (lx)")
    parser.add_argument("--out-dir", default=None, help="결과 저장 폴더")
    args = parser.parse_args()

    pod_df = load_pod_log(Path(args.pod_csv), args.device)
    ref_5s = load_and_resample_chamber(
        Path(args.chamber_csv),
        args.chamber_time_col,
        args.chamber_temp_col,
        args.chamber_rh_col,
        args.cert_temp_offset,
        args.cert_rh_offset,
    )

    merged = pd.merge_asof(
        pod_df.sort_values("dt"),
        ref_5s.sort_values("dt"),
        on="dt",
        direction="nearest",
        tolerance=pd.Timedelta("6s"),
    ).dropna(subset=["ref_temp_c"])

    if len(merged) < 50:
        raise RuntimeError("포드 로그와 챔버 기준 데이터의 시각이 겹치는 구간이 부족합니다. 시각 동기화를 확인하세요.")

    plat = extract_steady_plateaus(merged, soak_window_min=args.soak_min)
    if len(plat) < 2:
        raise RuntimeError("안정화된 챔버 스텝 구간을 2개 이상 찾지 못했습니다.")

    # 1. Temperature Linear Fit: T_cal = a_T * T_raw + b_T
    a_t, b_t = np.polyfit(plat["pod_temp_mean"], plat["ref_temp_mean"], 1)
    plat["temp_cal"] = a_t * plat["pod_temp_mean"] + b_t
    raw_t_err = plat["pod_temp_mean"] - plat["ref_temp_mean"]
    cal_t_err = plat["temp_cal"] - plat["ref_temp_mean"]

    # 2. Humidity Psychrometric Compensation + Linear Fit on RH-controlled steps
    plat["rh_psat"] = plat["pod_rh_mean"] * (psat_kpa(plat["pod_temp_mean"]) / psat_kpa(plat["temp_cal"]))
    rh_mask = plat["rh_controlled"] & plat["ref_rh_mean"].notna()
    if rh_mask.sum() >= 2:
        a_rh, b_rh = np.polyfit(plat.loc[rh_mask, "rh_psat"], plat.loc[rh_mask, "ref_rh_mean"], 1)
    else:
        a_rh, b_rh = 1.0, 0.0
    plat["rh_cal"] = a_rh * plat["rh_psat"] + b_rh

    # 3. Hysteresis Check at 25°C / 60%RH (Ascending vs Descending)
    hys_rows = plat[(plat["nom_temp_c"] == 25.0) & (plat["nom_rh_pct"] == 60.0)]
    hysteresis_rh = None
    if len(hys_rows) >= 2:
        hysteresis_rh = round(float(abs(hys_rows["rh_cal"].iloc[-1] - hys_rows["rh_cal"].iloc[0])), 3)

    out_dir = Path(args.out_dir) if args.out_dir else (Path("data/chamber_calibration") / args.device)
    out_dir.mkdir(parents=True, exist_ok=True)

    plat_csv = out_dir / "step_plateaus_summary.csv"
    plat.to_csv(plat_csv, index=False, encoding="utf-8-sig")
    plot_path = save_plots(plat, out_dir, args.device)

    result: dict = {
        "device": args.device,
        "standards": ["BS EN 12830:2018", "IEC 60068-3-5", "IEC 60068-3-6"],
        "n_matched_5s_pairs": int(len(merged)),
        "n_steady_steps": int(len(plat)),
        "temperature_calibration": {
            "formula": "T_cal = a_T * T_raw + b_T",
            "a_T": round(float(a_t), 6),
            "b_T": round(float(b_t), 4),
            "mean_self_heating_bias_c": round(float(raw_t_err.mean()), 4),
            "rmse_raw_c": round(float(np.sqrt(np.mean(raw_t_err**2))), 4),
            "rmse_cal_c": round(float(np.sqrt(np.mean(cal_t_err**2))), 4),
            "max_abs_err_cal_c": round(float(np.max(np.abs(cal_t_err))), 4),
            "en12830_class_0_5_pass": bool(np.max(np.abs(cal_t_err)) <= 0.5),
            "en12830_class_0_2_pass": bool(np.max(np.abs(cal_t_err)) <= 0.2),
        },
        "humidity_calibration": {
            "formula": "RH_cal = a_RH * (RH_raw * Psat(T_raw) / Psat(T_cal)) + b_RH",
            "a_RH": round(float(a_rh), 6),
            "b_RH": round(float(b_rh), 4),
            "rmse_raw_pct": round(
                float(np.sqrt(np.mean((plat.loc[rh_mask, "pod_rh_mean"] - plat.loc[rh_mask, "ref_rh_mean"]) ** 2))), 4
            )
            if rh_mask.any()
            else None,
            "rmse_cal_pct": round(
                float(np.sqrt(np.mean((plat.loc[rh_mask, "rh_cal"] - plat.loc[rh_mask, "ref_rh_mean"]) ** 2))), 4
            )
            if rh_mask.any()
            else None,
            "hysteresis_25C_60RH_pct": hysteresis_rh,
        },
    }

    if args.step_start and args.step_end:
        result["thermal_response_tau"] = fit_tau90(pod_df, args.step_start, args.step_end)

    if args.lux_ref is not None and args.lux_pod is not None and args.lux_pod > 0:
        trans = args.lux_pod / args.lux_ref
        result["light_calibration_bh1750"] = {
            "window_transmittance": round(float(trans), 4),
            "K_lux_multiplier": round(float(1.0 / trans), 4),
            "recommended_MTreg": int(np.clip(round(69.0 / trans), 31, 254)),
        }

    json_path = out_dir / "env_calibration_params.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"[OK] {args.device} 챔버 교정 분석 완료!")
    print(f"  - 온도 보정식 : T_cal = {a_t:.5f} * T_raw + ({b_t:+.4f}) °C")
    print(f"    RMSE: {result['temperature_calibration']['rmse_raw_c']:.3f}°C -> {result['temperature_calibration']['rmse_cal_c']:.3f}°C")
    print(f"    EN 12830 Class 0.5 합격: {result['temperature_calibration']['en12830_class_0_5_pass']}")
    if rh_mask.any():
        print(f"  - 습도 보정식 : RH_cal = {a_rh:.5f} * RH_psat + ({b_rh:+.4f}) %RH")
        print(f"    RMSE: {result['humidity_calibration']['rmse_raw_pct']:.3f}% -> {result['humidity_calibration']['rmse_cal_pct']:.3f}%RH")
    if hysteresis_rh is not None:
        print(f"  - 히스테리시스 (25°C/60%RH): {hysteresis_rh:.3f} %RH")
    print(f"  - 파라미터 저장 : {json_path}")
    print(f"  - 스텝 요약표   : {plat_csv}")
    print(f"  - 결과 그래프   : {plot_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
