#!/usr/bin/env python3
"""
Step 3: Publication-Grade Paper Plots & Calibration Report Generator
Generates:
  1. fig1_static_6pos_comparison.png     (IEEE Std 1293 before vs after RMSE)
  2. fig2_drop_waveforms_overlay.png     (400 Hz time-aligned drop waveforms by height)
  3. fig3_calibration_validation.png     (3-panel: Peak G vs h, t_fall validation, dV validation)
  4. paper_calibration_report.md         (Ready-to-use tables & metrics)

Supports --synthetic-demo to self-test the entire analysis pipeline.
"""

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

G0 = 9.80665


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


def mape_pct(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    mask = np.abs(y_true) > 1e-9
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)


def generate_synthetic_demo(demo_dir: Path) -> None:
    """Create realistic synthetic static + drop data to verify the full pipeline."""
    rng = np.random.default_rng(42)
    (demo_dir / "drops").mkdir(parents=True, exist_ok=True)

    # 1. Synthetic IEEE Std 1293 static params
    poses = [
        {"pose": "+X", "raw_mag": 1.031, "cal_mag": 1.0012},
        {"pose": "-X", "raw_mag": 0.972, "cal_mag": 0.9991},
        {"pose": "+Y", "raw_mag": 1.024, "cal_mag": 1.0008},
        {"pose": "-Y", "raw_mag": 0.981, "cal_mag": 0.9989},
        {"pose": "+Z", "raw_mag": 1.045, "cal_mag": 1.0015},
        {"pose": "-Z", "raw_mag": 0.964, "cal_mag": 0.9993},
    ]
    raw_rmse = float(np.sqrt(np.mean([(p["raw_mag"] - 1.0) ** 2 for p in poses])))
    cal_rmse = float(np.sqrt(np.mean([(p["cal_mag"] - 1.0) ** 2 for p in poses])))
    params = {
        "device": "demo-carrier-c6",
        "mac": "00:00:00:00:00:00",
        "standard": "IEEE Std 1293 (Synthetic Self-Test)",
        "bias_g": {"x": 0.0295, "y": 0.0215, "z": 0.0405},
        "scale_factor": {"x": 1.0015, "y": 1.0025, "z": 1.0045},
        "raw_rmse_g": raw_rmse,
        "cal_rmse_g": cal_rmse,
        "improvement_pct": (1.0 - cal_rmse / raw_rmse) * 100.0,
        "poses": poses,
    }
    with open(demo_dir / "calibration_params.json", "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2)

    # 2. Synthetic 400 Hz drops (5..30 cm, 5 trials each)
    meta_rows = []
    dt = 0.0025
    t_arr = np.arange(0, 1000) * dt
    for h_cm in [5, 10, 15, 20, 25, 30]:
        h_m = h_cm / 100.0
        t_fall = math.sqrt(2.0 * h_m / G0)
        v_in = math.sqrt(2.0 * G0 * h_m)
        e_rest = 0.25  # realistic foam-damped box restitution
        h_reb_cm = h_cm * (e_rest ** 2)
        dv_true = v_in * (1.0 + e_rest)
        pulse_dur = 0.028  # 28 ms cushioned contact
        # Half-sine pulse integral: (2/pi) * A_net * pulse_dur = dv_true
        a_peak_net_g = (dv_true * math.pi / (2.0 * pulse_dur)) / G0

        for tr in range(1, 6):
            mag = np.ones_like(t_arr) + rng.normal(0, 0.015, size=len(t_arr))
            t_release = 0.70
            t_hit = t_release + t_fall * rng.normal(1.0, 0.015)
            ff_mask = (t_arr >= t_release) & (t_arr < t_hit)
            mag[ff_mask] = np.clip(rng.normal(0.05, 0.02, size=np.sum(ff_mask)), 0.0, 0.2)

            p_mask = (t_arr >= t_hit) & (t_arr <= t_hit + pulse_dur)
            tau = (t_arr[p_mask] - t_hit) / pulse_dur
            peak_scale = rng.normal(1.0, 0.03)
            mag[p_mask] = 1.0 + a_peak_net_g * peak_scale * np.sin(np.pi * tau) + rng.normal(0, 0.05, size=np.sum(p_mask))

            fname = f"h{h_cm:02d}cm_t{tr:02d}_demo.csv"
            df = pd.DataFrame({
                "t_ms": t_arr * 1000.0,
                "ax_cal": rng.normal(0, 0.02, size=len(t_arr)),
                "ay_cal": rng.normal(0, 0.02, size=len(t_arr)),
                "az_cal": -mag,
                "mag_g": mag,
                "gyro_mag_dps": rng.uniform(5, 40, size=len(t_arr)),
            })
            df.to_csv(demo_dir / "drops" / fname, index=False)

            dv_meas = float(np.trapezoid(np.maximum(0.0, mag[p_mask] - 1.0) * G0, t_arr[p_mask]))
            meta_rows.append({
                "file": fname,
                "height_cm": float(h_cm),
                "trial": tr,
                "rebound_h_cm": round(h_reb_cm * rng.normal(1.0, 0.04), 2),
                "valid": 1,
                "peak_g": float(np.max(mag)),
                "t_fall_meas_ms": float((t_hit - t_release) * 1000.0),
                "t_fall_ref_ms": t_fall * 1000.0,
                "dv_meas_ms": dv_meas,
                "v_in_ref_ms": v_in,
                "max_gyro_dps": float(np.max(df["gyro_mag_dps"])),
            })

    pd.DataFrame(meta_rows).to_csv(demo_dir / "drop_metadata.csv", index=False)


def build_report(device_dir: Path) -> None:
    out_dir = device_dir / "paper_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "font.size": 10,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "figure.dpi": 300,
    })

    report_lines = [f"# Accelerometer Calibration & Drop-Test Validation Report ({device_dir.name})\n"]

    # --- 1. Static 6-Position Plot ---
    param_path = device_dir / "calibration_params.json"
    if param_path.exists():
        with open(param_path, "r", encoding="utf-8") as f:
            params = json.load(f)
        poses = params.get("poses", [])
        if poses:
            labels = [p["pose"] for p in poses]
            raw_err = [(p["raw_mag"] - 1.0) * 1000.0 for p in poses]  # mg
            cal_err = [(p["cal_mag"] - 1.0) * 1000.0 for p in poses]  # mg
            x = np.arange(len(labels))
            w = 0.36

            fig, ax = plt.subplots(figsize=(7.2, 4.0))
            ax.bar(x - w / 2, raw_err, w, label=f"Raw (RMSE = {params['raw_rmse_g']*1000:.2f} mg)", color="#d9534f", alpha=0.85)
            ax.bar(x + w / 2, cal_err, w, label=f"Calibrated (RMSE = {params['cal_rmse_g']*1000:.2f} mg)", color="#2b7bba", alpha=0.9)
            ax.axhline(0, color="black", linewidth=0.9)
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.set_ylabel("Static Magnitude Error |a| - 1.0 g (mg)")
            ax.set_title("IEEE Std 1293 6-Position Static Gravity Calibration")
            ax.legend()
            fig.tight_layout()
            fig.savefig(out_dir / "fig1_static_6pos_comparison.png", dpi=300)
            plt.close(fig)

        b = params["bias_g"]
        s = params["scale_factor"]
        report_lines.extend([
            "## 1. Static 6-Position Calibration (IEEE Std 1293)\n",
            "| Axis | Bias (g) | Scale Factor |",
            "| :---: | :---: | :---: |",
            f"| X | {b['x']:+.5f} | {s['x']:.5f} |",
            f"| Y | {b['y']:+.5f} | {s['y']:.5f} |",
            f"| Z | {b['z']:+.5f} | {s['z']:.5f} |",
            "",
            f"- **Raw 1 g RMSE**: `{params['raw_rmse_g']:.5f} g` ({params['raw_rmse_g']*1000:.2f} mg)",
            f"- **Calibrated 1 g RMSE**: `{params['cal_rmse_g']:.5f} g` ({params['cal_rmse_g']*1000:.2f} mg, **{params['improvement_pct']:.1f}% reduction**)\n",
        ])

    # --- 2. Drop Waveforms & Validation Curves ---
    meta_path = device_dir / "drop_metadata.csv"
    if meta_path.exists():
        meta = pd.read_csv(meta_path)
        valid = meta[meta["valid"] == 1].copy()
        if valid.empty:
            print("[WARN] valid==1 인 낙하 데이터가 없습니다.")
            return

        # Recompute dv_ref using rebound_h_cm
        h_m = valid["height_cm"].to_numpy() / 100.0
        h_reb_m = np.maximum(0.0, valid["rebound_h_cm"].fillna(0.0).to_numpy() / 100.0)
        valid["dv_ref_ms"] = np.sqrt(2.0 * G0 * h_m) + np.sqrt(2.0 * G0 * h_reb_m)
        valid["v_in_ref_ms"] = np.sqrt(2.0 * G0 * h_m)

        # Fig 2: Representative waveforms overlaid by height
        heights = sorted(valid["height_cm"].unique())
        cmap = plt.cm.viridis(np.linspace(0.1, 0.9, len(heights)))
        fig, ax = plt.subplots(figsize=(8.0, 4.5))
        for col, h in zip(cmap, heights):
            sub = valid[valid["height_cm"] == h]
            # Pick median-peak trial as representative
            med_idx = (sub["peak_g"] - sub["peak_g"].median()).abs().idxmin()
            fpath = device_dir / "drops" / str(sub.loc[med_idx, "file"])
            if not fpath.exists():
                continue
            df = pd.read_csv(fpath)
            t_ms = df["t_ms"].to_numpy()
            mag = df["mag_g"].to_numpy()
            t_peak = t_ms[int(np.argmax(mag))]
            t_rel = t_ms - t_peak
            win = (t_rel >= -400.0) & (t_rel <= 200.0)
            ax.plot(t_rel[win], mag[win], label=f"h = {h:.0f} cm (Peak {mag.max():.2f} G)", color=col, linewidth=1.6)
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.9, label="1.0 g Baseline")
        ax.set_xlabel("Time Relative to Impact Peak (ms)")
        ax.set_ylabel("Calibrated Acceleration Magnitude |a| (g)")
        ax.set_title("400 Hz Drop-Test Impact Waveforms by Height (ASTM D5276 / ISO 2248)")
        ax.legend(loc="upper left", fontsize=8.5)
        fig.tight_layout()
        fig.savefig(out_dir / "fig2_drop_waveforms_overlay.png", dpi=300)
        plt.close(fig)

        # Fig 3: 3-Panel Validation Figure
        grp = valid.groupby("height_cm").agg(
            n=("peak_g", "count"),
            peak_mean=("peak_g", "mean"),
            peak_std=("peak_g", "std"),
            tfall_mean=("t_fall_meas_ms", "mean"),
            tfall_std=("t_fall_meas_ms", "std"),
            tfall_ref=("t_fall_ref_ms", "mean"),
            dv_mean=("dv_meas_ms", "mean"),
            dv_std=("dv_meas_ms", "std"),
            dv_ref=("dv_ref_ms", "mean"),
        ).reset_index()
        grp["cv_pct"] = (grp["peak_std"].fillna(0.0) / grp["peak_mean"]) * 100.0

        fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))

        # Panel (a): Impact velocity sqrt(2gh) vs Peak G (linear physically)
        v_in_grp = np.sqrt(2.0 * G0 * (grp["height_cm"].to_numpy() / 100.0))
        h_grp = grp["height_cm"].to_numpy()
        y_peak = grp["peak_mean"].to_numpy()
        # Fit Peak G = a * sqrt(h) + c
        coef = np.polyfit(np.sqrt(h_grp), y_peak, 1)
        h_fit = np.linspace(h_grp.min(), h_grp.max(), 100)
        y_fit = coef[0] * np.sqrt(h_fit) + coef[1]
        r2_peak = r2_score(y_peak, coef[0] * np.sqrt(h_grp) + coef[1])

        axes[0].errorbar(h_grp, y_peak, yerr=grp["peak_std"].fillna(0.0), fmt="o", capsize=4, color="#1f77b4", label="Measured (Mean ± SD)")
        axes[0].plot(h_fit, y_fit, "--", color="#d62728", label=f"Fit: {coef[0]:.2f}√h {coef[1]:+.2f} ($R^2$={r2_peak:.4f})")
        axes[0].set_xlabel("Drop Height h (cm)")
        axes[0].set_ylabel("Peak Acceleration (g)")
        axes[0].set_title("(a) Drop Height vs Peak G")
        axes[0].legend(fontsize=8)

        # Panel (b): Free-fall time validation
        tf_ref = valid["t_fall_ref_ms"].to_numpy()
        tf_meas = valid["t_fall_meas_ms"].to_numpy()
        r2_tf = r2_score(tf_ref, tf_meas)
        mape_tf = mape_pct(tf_ref, tf_meas)
        lim_tf = [0, max(tf_ref.max(), tf_meas.max()) * 1.1]
        axes[1].plot(lim_tf, lim_tf, "k--", linewidth=1.0, label="1:1 Ideal Line")
        axes[1].errorbar(grp["tfall_ref"], grp["tfall_mean"], yerr=grp["tfall_std"].fillna(0.0), fmt="s", capsize=4, color="#2ca02c", label="Measured (Mean ± SD)")
        axes[1].set_xlabel("Theoretical Free-Fall Time √(2h/g) (ms)")
        axes[1].set_ylabel("Measured Free-Fall Time (ms)")
        axes[1].set_title(f"(b) Time-Axis Check (MAPE={mape_tf:.1f}%, $R^2$={r2_tf:.4f})")
        axes[1].legend(fontsize=8)

        # Panel (c): Impulse-Momentum dV validation
        dv_ref_all = valid["dv_ref_ms"].to_numpy()
        dv_meas_all = valid["dv_meas_ms"].to_numpy()
        r2_dv = r2_score(dv_ref_all, dv_meas_all)
        mape_dv = mape_pct(dv_ref_all, dv_meas_all)
        lim_dv = [0, max(dv_ref_all.max(), dv_meas_all.max()) * 1.1]
        axes[2].plot(lim_dv, lim_dv, "k--", linewidth=1.0, label="1:1 Ideal Line")
        axes[2].errorbar(grp["dv_ref"], grp["dv_mean"], yerr=grp["dv_std"].fillna(0.0), fmt="^", capsize=4, color="#9467bd", label="Integrated ΔV (Mean ± SD)")
        axes[2].set_xlabel("Theoretical ΔV = √(2gh) + √(2gh') (m/s)")
        axes[2].set_ylabel("Sensor Integrated ΔV (m/s)")
        axes[2].set_title(f"(c) Impulse-Momentum Check (MAPE={mape_dv:.1f}%, $R^2$={r2_dv:.4f})")
        axes[2].legend(fontsize=8)

        fig.tight_layout()
        fig.savefig(out_dir / "fig3_calibration_validation.png", dpi=300)
        plt.close(fig)

        report_lines.extend([
            "## 2. Dynamic Drop-Test Validation (ASTM D5276 / ISO 2248)\n",
            "| Height (cm) | N | Peak G (Mean ± SD) | CV (%) | t_fall Meas / Ref (ms) | ΔV Meas / Ref (m/s) |",
            "| :---: | :---: | :---: | :---: | :---: | :---: |",
        ])
        for _, r in grp.iterrows():
            report_lines.append(
                f"| {r['height_cm']:.0f} | {int(r['n'])} | "
                f"{r['peak_mean']:.2f} ± {0.0 if pd.isna(r['peak_std']) else r['peak_std']:.2f} | "
                f"{r['cv_pct']:.1f}% | "
                f"{r['tfall_mean']:.1f} / {r['tfall_ref']:.1f} | "
                f"{r['dv_mean']:.2f} / {r['dv_ref']:.2f} |"
            )
        report_lines.extend([
            "",
            f"- **Peak G vs √h Fit**: $R^2 = {r2_peak:.4f}$",
            f"- **Free-Fall Time Accuracy**: MAPE = `{mape_tf:.2f}%`, $R^2 = {r2_tf:.4f}$",
            f"- **Impulse-Momentum ΔV Accuracy**: MAPE = `{mape_dv:.2f}%`, $R^2 = {r2_dv:.4f}$",
            f"- **Mean Repeatability (CV%)**: `{grp['cv_pct'].mean():.2f}%`",
        ])

    report_path = out_dir / "paper_calibration_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"[OK] 논문용 그래프 및 리포트 생성 완료 -> {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate paper figures & calibration report")
    parser.add_argument("--device-dir", default=None, help="장치 데이터 폴더 (예: data/accel_calibration/carrier-c6-03)")
    parser.add_argument("--synthetic-demo", action="store_true", help="가상 데이터로 파이프라인 자체 검증 실행")
    args = parser.parse_args()

    if args.synthetic_demo:
        demo_dir = Path("scratch/demo_accel_cal")
        generate_synthetic_demo(demo_dir)
        build_report(demo_dir)
        return

    if not args.device_dir:
        raise SystemExit("--device-dir 또는 --synthetic-demo 를 지정해 주세요.")
    build_report(Path(args.device_dir))


if __name__ == "__main__":
    main()
