"""Generate publication-quality evaluation figures and Markdown summary from real experiment outputs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_cache_hinglish_scribe")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RES_DIR = ROOT / "results"
FIG_DIR = RES_DIR / "figures"


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    bench = json.loads((RES_DIR / "asr_severity_benchmark.json").read_text(encoding="utf-8"))
    oracle = json.loads((RES_DIR / "oracle_ablation.json").read_text(encoding="utf-8"))
    kannada = json.loads((RES_DIR / "kannada_portability.json").read_text(encoding="utf-8"))

    overall = bench["overall_by_arm"]
    by_cell = bench["by_arm_and_condition"]

    plt.rcParams.update(
        {
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "axes.edgecolor": "#CBD5E1",
            "axes.linewidth": 0.9,
            "grid.color": "#E2E8F0",
            "grid.linestyle": "--",
            "grid.alpha": 0.7,
        }
    )

    # -------------------------------------------------------------------------
    # FIGURE 1: Raw WER vs Normalized WER vs Critical Clinical Error Rate (CCER)
    # -------------------------------------------------------------------------
    short_labels = [
        "Whisper-Tiny\n(Auto)",
        "Whisper-Base\n(English-Forced)",
        "Whisper-Base\n(Multi-Auto)",
        "Whisper-Small\n(Unprompted)",
        "Whisper-Small\n(+Clinical Lexicon)",
    ]
    raw_wers = [float(a["mean_raw_wer"]) * 100 for a in overall]
    norm_wers = [float(a["mean_normalized_wer"]) * 100 for a in overall]
    ccers = [float(a["critical_clinical_error_rate"]) * 100 for a in overall]
    sev_scores = [float(a["mean_clinical_severity_score"]) for a in overall]

    x = np.arange(len(short_labels))
    w = 0.26

    fig, ax1 = plt.subplots(figsize=(10.5, 5.2), dpi=220)
    b1 = ax1.bar(x - w, raw_wers, width=w, label="Raw WER % (Script-Sensitive)", color="#94A3B8")
    b2 = ax1.bar(x, norm_wers, width=w, label="Script-Normalized WER % (nWER)", color="#2563EB")
    b3 = ax1.bar(x + w, ccers, width=w, label="Critical Clinical Error Rate % (CCER)", color="#DC2626")

    ax1.set_ylabel("Percentage (%)", fontsize=11, fontweight="bold", color="#0F172A")
    ax1.set_title(
        "Plain WER vs. Critical Clinical Error Rate Across ASR Arms (Locked Test Split, 4 Acoustic Tiers)",
        fontsize=12.5,
        fontweight="bold",
        pad=14,
        color="#0F172A",
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(short_labels, fontsize=9.5, fontweight="bold")
    ax1.set_ylim(0, max(max(raw_wers), max(ccers)) * 1.18)
    ax1.grid(axis="y")
    ax1.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.95, fontsize=9.5)

    for bars in (b1, b2, b3):
        for bar in bars:
            h = bar.get_height()
            ax1.annotate(
                f"{h:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color="#1E293B",
            )

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_wer_vs_critical_clinical_error.png")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE 2: Acoustic Noise & Speaker Overlap Degradation Curves (CSS & SNOMED F1)
    # -------------------------------------------------------------------------
    cond_order = ["clean", "noisy_10db", "noisy_3db", "overlap_10db"]
    cond_titles = ["Clean\nConsult", "Noisy OPD\n(+10 dB SNR)", "Crowded OPD\n(+3 dB SNR)", "Speaker Overlap\n(+10 dB SNR)"]
    palette = {
        "whisper_tiny_auto": ("#64748B", "o", "Whisper-Tiny (Auto)"),
        "whisper_base_en_forced": ("#EA580C", "s", "Whisper-Base (EN-Forced)"),
        "whisper_base_auto": ("#0284C7", "^", "Whisper-Base (Multi-Auto)"),
        "whisper_small_auto": ("#7C3AED", "D", "Whisper-Small (Unprompted)"),
        "whisper_small_clinical_hinglish": ("#059669", "*", "Whisper-Small (+Clinical Hinglish)"),
    }

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=220)
    cx = np.arange(len(cond_order))

    for arm_id, (color, marker, label) in palette.items():
        ys_sev = []
        ys_f1 = []
        for c_name in cond_order:
            rec = next(r for r in by_cell if r["arm_id"] == arm_id and r["acoustic_condition"] == c_name)
            ys_sev.append(float(rec["mean_clinical_severity_score"]))
            ys_f1.append(float(rec["mean_snomed_f1"]) * 100.0)
        lw = 2.6 if "clinical" in arm_id else 1.8
        ms = 9 if marker == "*" else 6.5
        ax_left.plot(cx, ys_sev, marker=marker, color=color, linewidth=lw, markersize=ms, label=label)
        ax_right.plot(cx, ys_f1, marker=marker, color=color, linewidth=lw, markersize=ms, label=label)

    ax_left.set_title("Clinical Severity Score vs. Noise & Overlap\n(Lower = Clinically Safer)", fontsize=10.5, fontweight="bold")
    ax_left.set_xticks(cx)
    ax_left.set_xticklabels(cond_titles, fontsize=9)
    ax_left.set_ylabel("Mean Clinical Severity Score (CSS)", fontsize=10, fontweight="bold")
    ax_left.grid(True)

    ax_right.set_title("Downstream SNOMED CT Concept F1 (%)\nAcross OPD Acoustic Tiers", fontsize=10.5, fontweight="bold")
    ax_right.set_xticks(cx)
    ax_right.set_xticklabels(cond_titles, fontsize=9)
    ax_right.set_ylabel("SNOMED Concept F1 (%)", fontsize=10, fontweight="bold")
    ax_right.set_ylim(0, 95)
    ax_right.grid(True)

    handles, labels = ax_right.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=8.5, frameon=True, facecolor="white", bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.08, 1, 1), pad=1.4)
    fig.savefig(FIG_DIR / "fig2_acoustic_noise_and_overlap_ablation.png", bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE 3: Oracle Linking Ablation & Latency-Safety Pareto Frontier
    # -------------------------------------------------------------------------
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12.4, 5.0), dpi=220)

    modes = ["Unconstrained\nZero-Shot Baseline", "Constrained Hybrid\n(Lexicon + SNOMED Retrieval)"]
    f1_vals = [
        float(oracle["unconstrained_baseline"]["mean_snomed_f1"]) * 100,
        float(oracle["constrained_hybrid"]["mean_snomed_f1"]) * 100,
    ]
    halluc_vals = [
        float(oracle["unconstrained_baseline"]["hallucination_rate_per_consult"]) * 100,
        float(oracle["constrained_hybrid"]["hallucination_rate_per_consult"]) * 100,
    ]
    ccer_oracle = [
        float(oracle["unconstrained_baseline"]["critical_clinical_error_rate_ccer"]) * 100,
        float(oracle["constrained_hybrid"]["critical_clinical_error_rate_ccer"]) * 100,
    ]

    ox = np.arange(2)
    ow = 0.24
    ax_a.bar(ox - ow, f1_vals, width=ow, color="#0D9488", label="SNOMED F1 (%)")
    ax_a.bar(ox, halluc_vals, width=ow, color="#E11D48", label="Consults w/ Hallucinated Code (%)")
    ax_a.bar(ox + ow, ccer_oracle, width=ow, color="#F59E0B", label="Critical Error Rate (%)")
    ax_a.set_xticks(ox)
    ax_a.set_xticklabels(modes, fontsize=9.5, fontweight="bold")
    ax_a.set_ylim(0, 118)
    ax_a.set_ylabel("Percentage (%)", fontsize=10, fontweight="bold")
    ax_a.set_title("Oracle Transcript Ablation:\nConstrained Linking Eliminates Hallucinated Codes", fontsize=10.5, fontweight="bold")
    ax_a.grid(axis="y")
    ax_a.legend(fontsize=8.3, loc="upper right")

    # Panel B: p95 Latency vs Clinical Severity Score (Pareto Tradeoff)
    p95s = [float(a["p95_latency_sec"]) for a in overall]
    colors_p = ["#64748B", "#EA580C", "#0284C7", "#7C3AED", "#059669"]
    offsets = [(6, 6), (6, -13), (-55, -16), (-125, -15), (-50, 10)]
    for idx, a in enumerate(overall):
        ax_b.scatter(p95s[idx], sev_scores[idx], s=155, color=colors_p[idx], zorder=4, edgecolors="#0F172A", linewidth=1.0)
        ax_b.annotate(
            short_labels[idx].replace("\n", " "),
            (p95s[idx], sev_scores[idx]),
            xytext=offsets[idx],
            textcoords="offset points",
            fontsize=8.3,
            fontweight="bold",
            color="#1E293B",
        )
    ax_b.set_xlim(6.5, 22.8)
    ax_b.set_ylim(1.4, 3.82)
    ax_b.set_xlabel("p95 Inference Latency per Consult on Apple M4 (seconds)", fontsize=9.5, fontweight="bold")
    ax_b.set_ylabel("Mean Clinical Severity Score (Lower = Safer)", fontsize=9.5, fontweight="bold")
    ax_b.set_title("Clinical Safety vs. p95 Latency Trade-Off\n($0 Cloud GPU Spend — Local Apple M4)", fontsize=10.5, fontweight="bold")
    ax_b.grid(True)

    fig.tight_layout(pad=1.8)
    fig.savefig(FIG_DIR / "fig3_oracle_ablation_and_latency_pareto.png")
    plt.close(fig)

    print(f"Generated 3 publication figures in {FIG_DIR}")
    print(f"Kannada Oracle SNOMED F1: {kannada['oracle_kannada_mean_snomed_f1']*100:.1f}% | Whisper-Small Kannada F1: {kannada['whisper_small_kannada_mean_snomed_f1']*100:.1f}%")


if __name__ == "__main__":
    main()
