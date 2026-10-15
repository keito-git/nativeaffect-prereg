"""
mkfig4.py  --  Fig. 4: Target-level correspondence (Gate III)
5 models x 13 targets = 65 scatter points.
x = standardized excess (word readout), y = standardized excess (code readout).
Right panel: histogram of (word - code) differences.

Target: full-column figure*, height <= 200 pt (2.78 in).
figsize (7.16, 2.5): after bbox_inches="tight" ~ 2.5 in = 180 pt  [OK]
Note: aspect="equal" constrains scatter axes to ~1.9x1.9 in within the panel;
the figure height is bounded by the subplot height, not the axes height.

Usage:
    python mkfig4.py [--root /path/to/stageSC] [--out /path/to/figures]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRATCHPAD = Path("data"
                  "/e3064739-5181-43fd-9b23-e940f47ad402/scratchpad")
sys.path.insert(0, str(SCRATCHPAD))
from final_tables import judge  # noqa: E402

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 7.5,
    "axes.labelsize": 7.5,
    "axes.titlesize": 7.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
})

B = 4000

# 5 models with Gate III data (m50 in stageSC)
MODELS_SC = {
    "OLMo-2-13B":       ("allenai__OLMo-2-1124-13B-Instruct_L30", "s", "#1f497d"),
    "Gemma-2-9B":       ("google__gemma-2-9b-it_L32",             "^", "#1f497d"),
    "Llama-3.1-8B":     ("meta-llama__Llama-3.1-8B-Instruct_L24", "D", "#888888"),
    "Ministral-8B":     ("mistralai__Ministral-8B-Instruct-2410_L27", "o", "#888888"),
    "Mistral-Nemo-12B": ("mistralai__Mistral-Nemo-Instruct-2407_L30", "v", "#c05208"),
}
EMOTIONS = ["anger", "boredom", "disgust", "fear", "guilt", "joy",
            "no-emotion", "pride", "relief", "sadness", "shame",
            "surprise", "trust"]


def compute_excess(npz_path: Path, readout_key: str, seed: int = 777):
    """Per-target standardized excess for one model and readout."""
    z     = np.load(npz_path)
    tsel  = z[f"emotion|{readout_key}|tgt_sel"]
    ttest = z[f"emotion|{readout_key}|tgt_test"]
    A     = z[f"emotion|{readout_key}|F5"]
    C     = tsel.shape[1]
    K, M, _, _ = A.shape
    rng   = np.random.default_rng(seed)

    val  = np.array([ttest[int(np.argmax(tsel[:, e])), e] for e in range(C)])
    null = np.zeros((B, C))
    for e in range(C):
        pick = rng.integers(0, M, size=(B, K))
        fs   = A[np.arange(K)[None, :], pick, 0, e]
        fh   = A[np.arange(K)[None, :], pick, 1, e]
        null[:, e] = fh[np.arange(B), np.argmax(fs, axis=1)]
    h1 = null[: B // 2]
    mu = h1.mean(0)
    sd = h1.std(0) + 1e-12
    return (val - mu) / sd


def main(root_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    word_exc_all = []
    code_exc_all = []
    labels_all   = []
    markers_all  = []
    colors_all   = []

    for mlabel, (tag, marker, color) in MODELS_SC.items():
        word_path = root_dir / f"raw_{tag}_word1_m50.npz"
        code_path = root_dir / f"raw_{tag}_code1_m50.npz"
        if not word_path.exists() or not code_path.exists():
            print(f"  [WARN] Missing: {word_path.name} or {code_path.name}")
            continue
        w_exc = compute_excess(word_path, "word")
        c_exc = compute_excess(code_path, "code")
        word_exc_all.append(w_exc)
        code_exc_all.append(c_exc)
        for _ in range(len(w_exc)):
            labels_all.append(mlabel)
            markers_all.append(marker)
            colors_all.append(color)

    word_exc_flat = np.concatenate(word_exc_all)
    code_exc_flat = np.concatenate(code_exc_all)
    diff          = word_exc_flat - code_exc_flat

    n_total     = len(diff)
    n_word_wins = int((diff > 0).sum())
    print(f"  word > code: {n_word_wins}/{n_total}")

    # ── Layout: scatter (left) + histogram (right), compact height ────────────
    # figsize (7.16, 2.5): target <= 180 pt after bbox_inches="tight"
    # aspect="equal" on scatter: axes will be ~ 1.9x1.9 in within the panel
    fig = plt.figure(figsize=(7.16, 2.5))
    gs  = fig.add_gridspec(1, 2, width_ratios=[2.5, 1.0],
                            left=0.09, right=0.97,
                            bottom=0.15, top=0.93, wspace=0.35)
    ax_sc  = fig.add_subplot(gs[0])
    ax_his = fig.add_subplot(gs[1])

    # ── Scatter ───────────────────────────────────────────────────────────────
    seen = set()
    for w, c, lbl, mk, col in zip(
            word_exc_flat, code_exc_flat, labels_all, markers_all, colors_all):
        kwargs = dict(marker=mk, color=col, s=22, alpha=0.85,
                      linewidths=0.4, edgecolors="white", zorder=3)
        if lbl not in seen:
            kwargs["label"] = lbl
            seen.add(lbl)
        ax_sc.scatter(w, c, **kwargs)

    # Clip axis limits to keep figure compact (outliers beyond ±5.5 SD are rare)
    all_vals = np.concatenate([word_exc_flat, code_exc_flat])
    lim_lo   = max(all_vals.min() - 0.8, -5.5)
    lim_hi   = min(all_vals.max() + 0.8,  8.5)
    diag     = [lim_lo, lim_hi]
    ax_sc.plot(diag, diag, color="#333333", linewidth=0.8, linestyle="--",
               zorder=1, label="$y = x$")

    ax_sc.set_xlabel("Word-readout standardized excess", labelpad=2)
    ax_sc.set_ylabel("Code-readout standardized excess", labelpad=2)
    ax_sc.set_title("(a)  Target-level correspondence (Gate III)",
                    loc="left", pad=3, fontsize=7.5)
    ax_sc.axhline(0, color="#cccccc", linewidth=0.4)
    ax_sc.axvline(0, color="#cccccc", linewidth=0.4)
    ax_sc.set_xlim(lim_lo, lim_hi)
    ax_sc.set_ylim(lim_lo, lim_hi)
    ax_sc.set_aspect("equal", adjustable="box")
    ax_sc.spines["top"].set_visible(False)
    ax_sc.spines["right"].set_visible(False)
    ax_sc.legend(frameon=False, fontsize=6.5, loc="upper left",
                 markerscale=1.1, handletextpad=0.3)
    ax_sc.text(0.97, 0.04,
               f"{n_word_wins}/{n_total} below diagonal\n(word > code)",
               transform=ax_sc.transAxes, ha="right", va="bottom",
               fontsize=6.5, style="italic")

    # ── Histogram of diff = word - code ──────────────────────────────────────
    ax_his.hist(diff, bins=16, color="#1f497d", alpha=0.75,
                edgecolor="white", linewidth=0.4)

    med_diff = float(np.median(diff))
    sd_diff  = float(diff.std())
    thr_line = med_diff + 1.67 * sd_diff

    ax_his.axvline(med_diff, color="#333333", linewidth=0.9,
                   linestyle="-",  label=f"Median ({med_diff:.2f})")
    ax_his.axvline(thr_line, color="#c05208", linewidth=0.9,
                   linestyle="--", label=f"+1.67 SD ({thr_line:.2f})")

    ax_his.set_xlabel("Word $-$ code excess", labelpad=2)
    ax_his.set_ylabel("Count", labelpad=2)
    ax_his.set_title("(b)", loc="left", pad=3)
    ax_his.spines["top"].set_visible(False)
    ax_his.spines["right"].set_visible(False)
    ax_his.legend(frameon=False, fontsize=6.5, loc="upper right")

    out_path = out_dir / "fig4_paired_targets.pdf"
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=
        "data/stageSC")
    parser.add_argument("--out", default=
        "figures")
    args = parser.parse_args()
    main(Path(args.root), Path(args.out))
