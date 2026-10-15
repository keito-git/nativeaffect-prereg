"""
mkfig2.py  --  Fig. 2: Floor construction for Gate I
Two panels (horizontal layout):
  (a) Eigenvalue-weighted variance profile is preserved exactly (only signs differ).
      Illustrative bar chart; annotation "exact to 2.4e-07".
  (b) For a principal component direction, the only variance-preserving
      directions are +/-u_i, so the floor collapses onto the target itself.

Target: 1-column figure, <= 230 pt tall (3.19 in).
Layout: (1 x 2) horizontal to keep height compact.

Conceptual figure; no experimental data are loaded.

Usage:
    python mkfig2.py [--out /path/to/figures]
"""
from __future__ import annotations
import argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

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

BLUE   = "#1f497d"
ORANGE = "#c05208"
GRAY   = "#888888"
LGRAY  = "#bbbbbb"
DGRAY  = "#333333"


# ── (a) Bar chart panel ───────────────────────────────────────────────────────
def draw_panel_a(ax):
    """Eigenvalue-weighted variance profile identical for target and floor."""
    rng = np.random.default_rng(7)
    d   = 8   # number of components shown

    lambdas = np.array([3.2, 2.1, 1.6, 1.0, 0.8, 0.55, 0.38, 0.22])
    a_raw   = rng.uniform(0.3, 1.0, size=d)
    a_raw  /= np.linalg.norm(a_raw)
    a       = a_raw

    lam_a2  = lambdas * a**2

    rng2    = np.random.default_rng(99)
    signs   = rng2.choice([-1, 1], size=d)
    a_tilde = a * signs
    lam_a2t = lambdas * a_tilde**2   # identical to lam_a2 by construction

    x     = np.arange(d)
    bar_w = 0.32

    ax.bar(x - bar_w / 2, lam_a2,  width=bar_w, color=BLUE,
           label=r"Target $\;\lambda_i a_i^2$",
           edgecolor="white", linewidth=0.3, zorder=3)
    ax.bar(x + bar_w / 2, lam_a2t, width=bar_w, color=LGRAY,
           label=r"Floor $\;\lambda_i \tilde{a}_i^2$",
           edgecolor="white", linewidth=0.3, zorder=3)

    sign_str = [f"$({'+' if s > 0 else '-'})$" for s in signs]
    ax.set_xticks(x)
    ax.set_xticklabels(sign_str, fontsize=6.5)
    ax.set_xlabel(r"Comp. $i$  (sign of $\tilde{a}_i$ rel. $a_i$)", labelpad=2)
    ax.set_ylabel(r"$\lambda_i a_i^{\,2}$", labelpad=2)
    ax.set_title("(a)  Variance profile preserved",
                 loc="left", pad=3, fontsize=7.5)

    ax.legend(frameon=False, fontsize=6.5, loc="upper right",
              handlelength=1.0, handletextpad=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, lam_a2.max() * 1.45)

    ax.text(0.02, 0.97,
            r"Max deviation: $2.4\times10^{-7}$",
            transform=ax.transAxes, va="top", ha="left",
            fontsize=6.2, color=DGRAY, style="italic")
    ax.text(0.02, 0.83,
            r"$\tilde{\mathbf{v}} = Q^{\!\top}(\mathbf{s}\odot Q\mathbf{v})$",
            transform=ax.transAxes, va="top", ha="left",
            fontsize=7.0, color=DGRAY)


# ── (b) PC-direction panel ─────────────────────────────────────────────────────
def draw_panel_b(ax):
    """When target = u_i, only ±u_i preserves variance -> floor ≡ target."""
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.25, 1.9)
    ax.axis("off")
    ax.set_title("(b)  No non-trivial floor",
                 loc="left", pad=3, fontsize=7.5)

    # Axis cross
    ax.annotate("", xy=(1.3, 0), xytext=(-1.3, 0),
                arrowprops=dict(arrowstyle="->,head_length=0.07,head_width=0.045",
                                color=LGRAY, lw=0.7))
    ax.annotate("", xy=(0, 1.7), xytext=(0, -0.08),
                arrowprops=dict(arrowstyle="->,head_length=0.07,head_width=0.045",
                                color=LGRAY, lw=0.7))
    ax.text(1.35, 0, r"$u_j$", ha="left", va="center", fontsize=7, color=LGRAY)
    ax.text(0, 1.76, r"$u_i$", ha="center", va="bottom", fontsize=7, color=LGRAY)

    # Target: +u_i (blue)
    ax.annotate("", xy=(0, 1.30), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->,head_length=0.11,head_width=0.065",
                                color=BLUE, lw=1.8))
    ax.text(0.09, 1.15, r"$\mathbf{v} = \mathbf{u}_i$",
            ha="left", va="center", fontsize=7.5, color=BLUE, fontweight="bold")

    # Floor: -u_i (orange)
    ax.annotate("", xy=(0, -0.08), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->,head_length=0.11,head_width=0.065",
                                color=ORANGE, lw=1.8))
    ax.text(0.09, -0.12, r"$-\mathbf{u}_i$",
            ha="left", va="top", fontsize=7.5, color=ORANGE)

    # Any other direction fails (dashed gray)
    dx, dy = 0.9, 0.7
    nm = np.sqrt(dx**2 + dy**2)
    dx_n, dy_n = dx / nm * 1.15, dy / nm * 1.15
    ax.annotate("", xy=(dx_n, dy_n), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->,head_length=0.09,head_width=0.055",
                                color=GRAY, lw=1.0, linestyle="dashed"))
    ax.text(dx_n + 0.07, dy_n + 0.04, r"$\tilde{\mathbf{v}}$?",
            ha="left", va="bottom", fontsize=7, color=GRAY)
    ax.text(dx_n * 0.52 + 0.07, dy_n * 0.52 + 0.04, r"$\times$",
            ha="center", va="center", fontsize=10, color=ORANGE, fontweight="bold")

    ax.text(0, -0.20,
            r"Only $\pm\mathbf{u}_i$ preserve $\lambda_i a_i^2$"
            "\n"
            r"$\Rightarrow$ floor $\equiv$ target  ($|\cos|=1.0000$)",
            ha="center", va="top", fontsize=6.5, color=DGRAY,
            linespacing=1.4)


# ── Main ──────────────────────────────────────────────────────────────────────
def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1-column figure, horizontal layout (1 x 2)
    # Target: 1-col width = 3.5 in, height <= 230 pt = 3.19 in
    # figsize (3.5, 2.9): after bbox_inches="tight" ~ 2.8 in = 202 pt  [OK]
    fig = plt.figure(figsize=(3.5, 2.9))
    gs  = GridSpec(1, 2, figure=fig,
                   wspace=0.42, left=0.12, right=0.98,
                   bottom=0.11, top=0.96)

    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    draw_panel_a(ax_a)
    draw_panel_b(ax_b)

    out_path = out_dir / "fig2_floor_construction.pdf"
    # pad_inches=0.04 to keep width <= 252 pt (1 column)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.04, dpi=300)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=
        "figures")
    args = parser.parse_args()
    main(Path(args.out))
