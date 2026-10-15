"""
mkfig3.py  --  Fig. 3: Null floor distributions and target positions
Reduced from 2x2 to 1x2: single-word readout, two representative models.
  Panel (a): Gemma-2-2B  (largest effect)
  Panel (b): Gemma-2-9B  (smallest effect)

Target: full-column figure*, height <= 200 pt (2.78 in).
figsize (7.16, 2.45): after bbox_inches="tight" ~ 2.5 in = 180 pt  [OK]

Usage:
    python mkfig3.py [--root /path/to/stageC3] [--out /path/to/figures]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# ── Import judge() from final_tables.py ──────────────────────────────────────
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

# ── Constants ─────────────────────────────────────────────────────────────────
B = 4000
COL_NULL   = "#a8a8a8"
COL_THR    = "#333333"
COL_PASS   = "#1f497d"
COL_FAIL   = "#cc6666"
EMOTIONS   = ["anger", "boredom", "disgust", "fear", "guilt", "joy",
              "no-emotion", "pride", "relief", "sadness", "shame",
              "surprise", "trust"]

# Show single-word readout for both models
READOUT = "single"
READOUT_LABEL = "single-word readout"

# Two representative models
MODELS = {
    "gemma-2-2b-it": ("(a)  Gemma-2-2B",
                      "raw_google__gemma-2-2b-it_L20_m50.npz"),
    "gemma-2-9b-it": ("(b)  Gemma-2-9B",
                      "raw_google__gemma-2-9b-it_L32_m50.npz"),
}


def compute_panel_data(npz_path: Path, readout: str, seed: int = 777):
    """Return (null_z, val_z, thr_z) each of shape (C,)."""
    z     = np.load(npz_path)
    tsel  = z[f"emotion|{readout}|tgt_sel"]
    ttest = z[f"emotion|{readout}|tgt_test"]
    A     = z[f"emotion|{readout}|F5"]

    C        = tsel.shape[1]
    K, M, _, _ = A.shape
    rng = np.random.default_rng(seed)

    val  = np.array([ttest[int(np.argmax(tsel[:, e])), e] for e in range(C)])

    null = np.zeros((B, C))
    for e in range(C):
        pick = rng.integers(0, M, size=(B, K))
        fs   = A[np.arange(K)[None, :], pick, 0, e]
        fh   = A[np.arange(K)[None, :], pick, 1, e]
        null[:, e] = fh[np.arange(B), np.argmax(fs, axis=1)]

    h1  = null[: B // 2]
    thr = np.quantile(h1, 0.95, axis=0)
    mu  = h1.mean(0)
    sd  = h1.std(0) + 1e-12

    null_z = (null - mu[None, :]) / sd[None, :]
    val_z  = (val - mu) / sd
    thr_z  = (thr - mu) / sd
    return null_z, val_z, thr_z


def draw_panel(ax, null_z, val_z, thr_z):
    from scipy.stats import gaussian_kde
    C = len(EMOTIONS)
    thr_median = float(np.median(thr_z))

    for e in range(C):
        y     = C - 1 - e
        ndata = null_z[:, e]
        v_obs = float(val_z[e])

        # Horizontal violin (narrow half-width = 0.30 for compact height)
        kde   = gaussian_kde(ndata, bw_method=0.3)
        x_rng = np.linspace(ndata.min() - 0.3, ndata.max() + 0.3, 200)
        dens  = kde(x_rng)
        dens  = dens / dens.max() * 0.30   # half-width 0.30 (was 0.40)

        ax.fill_between(x_rng, y - dens, y + dens,
                        color=COL_NULL, alpha=0.65, linewidth=0, zorder=1)
        ax.plot(x_rng, y - dens, color="#707070", linewidth=0.3, zorder=2)
        ax.plot(x_rng, y + dens, color="#707070", linewidth=0.3, zorder=2)

        # IQR bar
        q25, q75 = np.percentile(ndata, [25, 75])
        ax.plot([q25, q75], [y, y], color="#404040", linewidth=1.5, zorder=3)

        # Observed value
        color = COL_PASS if v_obs > thr_z[e] else COL_FAIL
        ax.scatter(v_obs, y, color=color, s=18, zorder=5,
                   edgecolors="white", linewidths=0.4)

    # Threshold line
    ax.axvline(thr_median, color=COL_THR, linewidth=0.7,
               linestyle="--", zorder=4)

    ax.set_yticks(range(C))
    ax.set_yticklabels([EMOTIONS[C - 1 - e] for e in range(C)], fontsize=6.2)
    ax.set_xlim(-4.5, max(5.0, float(val_z.max()) + 0.8))
    ax.axvline(0, color="#b0b0b0", linewidth=0.4, linestyle="-", zorder=0)
    ax.tick_params(axis="y", length=0, pad=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main(root_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1x2 layout, full column width
    # figsize (7.16, 2.45): compact single-row violin plots
    fig, axes = plt.subplots(
        1, 2, figsize=(7.16, 2.45),
        gridspec_kw={"wspace": 0.45, "left": 0.09, "right": 0.98,
                     "bottom": 0.10, "top": 0.88}
    )

    for col, (mkey, (panel_label, fname)) in enumerate(MODELS.items()):
        ax = axes[col]
        npz_path = root_dir / fname
        null_z, val_z, thr_z = compute_panel_data(npz_path, READOUT)
        draw_panel(ax, null_z, val_z, thr_z)

        ax.set_xlabel("Standardized excess score", labelpad=2, fontsize=7.5)
        if col == 0:
            ax.set_ylabel(READOUT_LABEL, labelpad=3, fontsize=7.5)
        ax.set_title(panel_label, loc="left", fontweight="normal", pad=3,
                     fontsize=7.5)

    # Shared legend (compact, bottom center)
    legend_elements = [
        mpatches.Patch(facecolor=COL_NULL, edgecolor="#707070",
                       label="Null distribution"),
        Line2D([0], [0], color="#404040", linewidth=1.5,
               label="25–75th pctile"),
        Line2D([0], [0], color=COL_THR, linewidth=0.7, linestyle="--",
               label="Null 95th pctile"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COL_PASS,
               markersize=4.5, label="Obs. (above threshold)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COL_FAIL,
               markersize=4.5, label="Obs. (below threshold)"),
    ]
    # Legend placed above axes (below panel titles), outside plot area
    fig.legend(handles=legend_elements, loc="lower center", ncol=5,
               frameon=False, fontsize=6.2, bbox_to_anchor=(0.5, 0.90))

    out_path = out_dir / "fig3_floor_distributions.pdf"
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=
        "data/stageC3")
    parser.add_argument("--out", default=
        "figures")
    args = parser.parse_args()
    main(Path(args.root), Path(args.out))
