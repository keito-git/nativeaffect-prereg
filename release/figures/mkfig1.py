"""
mkfig1.py  --  Fig. 1: Three-gate measurement design (methodology figure)
Methodology figure; no experimental data are loaded.
Numbers from task specification only:
  Gate I  : 8/9 models pass, +2.83 SD
  Gate II : 7/9 models pass (100 random splits); 5/5 measurable (act. split)
  Gate III: 0/5 models pass; +2.33 SD -> +0.45 SD; paired diff +1.67 SD

Target output: <= 230 pt tall (IEEEtran full-column, figure*[t])
Design: methodology flow figure with three gate columns.

Vertical zones (header / separator / schematic / separator / verdict / conclusion)
are FIXED and nothing from one zone bleeds into an adjacent zone.

Usage:
    python mkfig1.py [--out /path/to/figures]
"""
from __future__ import annotations
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

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
LGRAY  = "#c0c0c0"
DGRAY  = "#333333"
WHITE  = "#ffffff"
BG     = "#f2f2f2"

# ── Figure canvas ─────────────────────────────────────────────────────────────
# Target: <= 230 pt  =  <= 3.19 in at 72 dpi
FW, FH = 7.16, 3.1


def make_figure():
    fig = plt.figure(figsize=(FW, FH))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FW)
    ax.set_ylim(0, FH)
    ax.axis("off")
    return fig, ax


# ── Drawing helpers ───────────────────────────────────────────────────────────
def box(ax, x, y, w, h, fc=WHITE, ec=GRAY, lw=0.6, zorder=2, rad=0.05):
    p = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={rad}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zorder, clip_on=False)
    ax.add_patch(p)


def arrow(ax, x1, y1, x2, y2, color=DGRAY, lw=0.8, head=0.09, zorder=3):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle=f"->,head_length={head},head_width={head*0.55}",
                    color=color, lw=lw),
                zorder=zorder)


def txt(ax, x, y, s, ha="center", va="center", size=7.5, color=DGRAY,
        weight="normal", style="normal", zorder=5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color,
            fontweight=weight, fontstyle=style, zorder=zorder)


def hline(ax, x1, x2, y, color=LGRAY, lw=0.4, zorder=1):
    ax.plot([x1, x2], [y, y], color=color, lw=lw, zorder=zorder)


def direction_arrow(ax, ox, oy, dx, dy, length=0.20, color=BLUE, lw=1.0):
    norm = np.sqrt(dx**2 + dy**2) + 1e-9
    ex   = ox + dx / norm * length
    ey   = oy + dy / norm * length
    arrow(ax, ox, oy, ex, ey, color=color, lw=lw, head=0.09)


# ── Layout ────────────────────────────────────────────────────────────────────
# Vertical zones (in data-inch coordinates, y=0 at bottom).
# INVARIANT: nothing drawn in zone N extends into zone N-1 (above).

Y_FORM_TOP  = 3.05    # formula bar top
Y_FORM_BOT  = 2.74    # formula bar bottom

Y_GATE_TOP  = 2.70    # gate frame top
Y_NAME_CY   = 2.61    # "Gate I/II/III" bold text center
Y_SUB_CY    = 2.50    # subtitle (floor type) center
Y_QUES_CY   = 2.38    # italic question line center
Y_SEP1      = 2.28    # ═══ header/schematic separator ═══
                       #     nothing from schematic zone
                       #     rises above this line
Y_SCH_TOP   = 2.25    # schematic region top
Y_SCH_BOT   = 0.94    # schematic region bottom
Y_VERD_SEP  = 0.88    # ═══ schematic/verdict separator ═══
Y_GATE_BOT  = 0.50    # gate frame bottom

Y_CONC_TOP  = 0.43    # conclusion box top
Y_CONC_BOT  = 0.04    # conclusion box bottom

# Three gate column x-ranges
COLS = [(0.10, 2.33), (2.43, 4.66), (4.76, 7.06)]


def col_cx(i: int) -> float:
    return (COLS[i][0] + COLS[i][1]) / 2


# ── Formula bar (top, shared measurement) ────────────────────────────────────
def draw_formula_bar(ax):
    """Shared measurement pipeline description across the top."""
    box(ax, 0.08, Y_FORM_BOT, FW - 0.16, Y_FORM_TOP - Y_FORM_BOT,
        fc=BG, ec=LGRAY, lw=0.5, rad=0.04)

    cy = (Y_FORM_TOP + Y_FORM_BOT) / 2
    txt(ax, 0.22, cy + 0.08,
        r"Measurement:  "
        r"$S_e(\mathbf{v}) = \frac{1}{2}[\,R_e(\mathbf{h}+\alpha\mathbf{v})"
        r" - R_e(\mathbf{h}-\alpha\mathbf{v})\,]$",
        ha="left", size=7.5, color=DGRAY)
    txt(ax, 0.22, cy - 0.09,
        r"$\mathbf{h}$: hidden state at $\ell$;  "
        r"$p_0,\,p_\alpha$: next-token dists. before / after steering;  "
        r"$\alpha$ by bisection: $J_S(p_\alpha,\,p_0) = J^{*}= 0.05$ (all vocab.)",
        ha="left", size=6.5, color=GRAY)


# ── Gate column frames and headers ────────────────────────────────────────────
GATE_HEADERS = [
    ("Gate I",   "Direction floor",
     r"Does $\tilde{\mathbf{v}}$ with same $\lambda_i a_i^2$ pass?"),
    ("Gate II",  "Partition floor",
     "Does any 13-class split pass?"),
    ("Gate III", "Encoding floor",
     "Does word-to-code swap attenuate?"),
]


def draw_gate_frame_header(ax, col_idx: int):
    x0, x1 = COLS[col_idx]
    cx = col_cx(col_idx)
    # Outer frame
    box(ax, x0, Y_GATE_BOT, x1 - x0, Y_GATE_TOP - Y_GATE_BOT,
        fc=WHITE, ec=LGRAY, lw=0.7, rad=0.07)
    gname, glabel, gq = GATE_HEADERS[col_idx]
    # Gate name (bold)
    txt(ax, cx, Y_NAME_CY, gname,
        size=8.0, weight="bold", color=DGRAY)
    # Floor type subtitle — well above Y_SEP1
    txt(ax, cx, Y_SUB_CY, glabel,
        size=7.0, color=BLUE if col_idx < 2 else ORANGE)
    # Italic question — still above Y_SEP1=2.28
    txt(ax, cx, Y_QUES_CY, gq,
        size=6.2, color=DGRAY, style="italic")
    # Separator lines
    hline(ax, x0 + 0.06, x1 - 0.06, Y_SEP1,  color=LGRAY)
    hline(ax, x0 + 0.06, x1 - 0.06, Y_VERD_SEP, color=LGRAY)


# ── Mini bar chart (eigenvalue-weighted variance profile) ─────────────────────
def mini_bars(ax, cx, cy, vals, colors, width=0.11, bar_w=0.026):
    """Draw a small horizontal bar chart centred at (cx, cy)."""
    n  = len(vals)
    xs = np.linspace(cx - width / 2 + bar_w / 2,
                     cx + width / 2 - bar_w / 2, n)
    bh     = 0.15   # max bar height in data units
    base_y = cy - bh / 2
    for xi, v, c in zip(xs, vals, colors):
        h = v * bh
        rect = mpatches.Rectangle((xi - bar_w / 2, base_y), bar_w, h,
                                   facecolor=c, edgecolor="none", zorder=4)
        ax.add_patch(rect)
    ax.plot([cx - width / 2, cx + width / 2], [base_y, base_y],
            color=DGRAY, lw=0.5, zorder=3)


# ── Gate I schematic ──────────────────────────────────────────────────────────
# All y-coords < Y_SCH_TOP = 2.25
def draw_gate1_schematic(ax, cx: float):
    """Direction floor: two arrows + identical bar profiles."""
    x0, x1 = COLS[0]

    G1_ROW_T = 2.07    # Target row center  (bar top: 2.07+0.075=2.145 < 2.25)
    G1_ROW_C = 1.52    # Floor row center
    G1_MID_Y = (G1_ROW_T + G1_ROW_C) / 2   # 1.795

    # Row labels at LEFT — do NOT place labels above bars
    txt(ax, x0 + 0.18, G1_ROW_T, r"Target  $\mathbf{v}$",
        size=6.5, color=BLUE, ha="left")
    txt(ax, x0 + 0.18, G1_ROW_C, r"Floor  $\tilde{\mathbf{v}}$",
        size=6.5, color=GRAY, ha="left")

    # Direction arrows (small, centered in mid-left area)
    arrow_ox = cx - 0.08
    direction_arrow(ax, arrow_ox, G1_ROW_T - 0.05,  0.55, 1.0,
                    length=0.18, color=BLUE)
    direction_arrow(ax, arrow_ox, G1_ROW_C - 0.05, -0.55, 1.0,
                    length=0.18, color=GRAY)

    # Sign flip annotation between arrow rows
    txt(ax, arrow_ox + 0.04, G1_MID_Y,
        r"$\mathbf{s} = \pm 1$",
        size=5.8, color=DGRAY, style="italic")

    # Identical bar profiles (no above-bar labels; equality shown by same bars)
    bar_vals = [0.45, 0.88, 0.65, 1.00, 0.55, 0.70, 0.38]
    bar_cx   = cx + 0.44
    mini_bars(ax, bar_cx, G1_ROW_T, bar_vals,
              colors=[BLUE if i % 2 == 0 else LGRAY for i in range(len(bar_vals))])
    mini_bars(ax, bar_cx, G1_ROW_C, bar_vals,
              colors=[GRAY if i % 2 == 0 else LGRAY for i in range(len(bar_vals))])

    # Construction formula notes (below row centers, well inside schematic zone)
    txt(ax, cx, 1.24,
        r"$\tilde{\mathbf{v}} = Q^\top(\mathbf{s}\odot Q\mathbf{v})$;  "
        r"$\lambda_i\tilde{a}_i^2 = \lambda_i a_i^2$"
        r"  (max dev: $2.4\!\times\!10^{-7}$)",
        size=5.8, color=DGRAY, style="italic")
    txt(ax, cx, 1.10,
        r"For $\mathbf{v} = \mathbf{u}_i$ (PC dir.): floor $\equiv$ target,"
        r"  $|\cos|=1.0$",
        size=5.8, color=DGRAY, style="italic")


# ── Gate II schematic ─────────────────────────────────────────────────────────
# Row labels placed at LEFT; boxes placed to the right.
# box_h = 0.18; box tops < Y_SCH_TOP = 2.25
def draw_gate2_schematic(ax, cx: float):
    """Partition floor: same direction, different 13-class splits."""
    x0, x1 = COLS[1]

    BOX_H    = 0.18
    C        = 13
    LABEL_W  = 0.46    # horizontal space reserved for left label
    BOX_XSTART = x0 + LABEL_W
    BOX_XEND   = x1 - 0.04
    total_box_w = BOX_XEND - BOX_XSTART
    box_w       = total_box_w / C
    GAP         = 0.003

    # Row centers: top boxes at 2.10 (top 2.10+0.09=2.19 < 2.25)
    # spacing 0.44 in between centers ensures no overlap with notes at 1.04/0.97
    rows = [
        (2.10, "Target",    BLUE,   False),
        (1.66, "Ctrl (i)",  GRAY,   True),
        (1.22, "Ctrl (ii)", GRAY,   True),
    ]

    colors_base = [BLUE, BLUE, LGRAY, BLUE, LGRAY,
                   ORANGE, LGRAY, ORANGE, LGRAY, BLUE,
                   LGRAY, ORANGE, BLUE]
    rng   = np.random.default_rng(42)
    shuf1 = rng.permutation(C)
    shuf2 = rng.permutation(C)
    cluster_colors = [GRAY if i < 8 else LGRAY for i in range(C)]

    row_orders = [list(range(C)), list(shuf1), list(shuf2)]
    row_fc     = [colors_base, colors_base, cluster_colors]

    for row_idx, (row_cy, label, lcolor, _shuf) in enumerate(rows):
        # Label at LEFT (vertically centered with box)
        txt(ax, x0 + 0.04, row_cy, label,
            size=6.0, color=lcolor, ha="left", va="center")
        # Colored boxes
        row_y = row_cy - BOX_H / 2
        for pos in range(C):
            orig = row_orders[row_idx][pos]
            fc   = row_fc[row_idx][orig]
            xi   = BOX_XSTART + pos * box_w
            rect = mpatches.Rectangle(
                (xi, row_y), box_w - GAP, BOX_H,
                facecolor=fc, edgecolor=WHITE, lw=0.3, zorder=4)
            ax.add_patch(rect)

    # Annotation notes (inside schematic zone)
    txt(ax, cx, 1.03,
        "Ctrl (i): 100 random relabellings",
        size=5.8, color=DGRAY, style="italic")
    txt(ax, cx, 0.97,
        "Ctrl (ii): activation-cluster grouping",
        size=5.8, color=DGRAY, style="italic")


# ── Gate III schematic ────────────────────────────────────────────────────────
# Row labels placed at LEFT; swap arrow between label and boxes.
# box_h = 0.19; box tops < Y_SCH_TOP = 2.25
def draw_gate3_schematic(ax, cx: float):
    """Encoding floor: emotion words -> opaque codes, 13 categories unchanged."""
    x0, x1 = COLS[2]

    BOX_H    = 0.19
    LABEL_W  = 0.43    # space for left label ("Words:" / "Codes:")
    ARR_W    = 0.22    # space for swap arrow column
    BOX_XSTART = x0 + LABEL_W + ARR_W
    BOX_XEND   = x1 - 0.04
    total_box_w = BOX_XEND - BOX_XSTART

    words = ["anger", "joy", "fear", "...", "trust"]
    codes = [r"$X_1$", r"$X_2$", r"$X_3$", "...", r"$X_{13}$"]
    W     = len(words)
    GAP   = 0.025
    box_w = (total_box_w - (W - 1) * GAP) / W
    x_start = BOX_XSTART

    # Row centers (box tops < 2.25)
    G3_W = 1.90   # Words row center (box top: 1.90+0.095=1.995 < 2.25)
    G3_C = 1.52   # Codes row center

    # Left labels
    txt(ax, x0 + 0.04, G3_W, "Words:", size=6.0, color=BLUE, ha="left")
    txt(ax, x0 + 0.04, G3_C, "Codes:", size=6.0, color=GRAY, ha="left")

    # Swap arrow (between label column and box column)
    arr_x  = x0 + LABEL_W + ARR_W / 2   # center of arrow column
    arr_x -= 0.04
    arrow(ax, arr_x, G3_W - BOX_H / 2 - 0.01,
              arr_x, G3_C + BOX_H / 2 + 0.01,
          color=ORANGE, lw=0.9, head=0.08)
    txt(ax, arr_x, (G3_W + G3_C) / 2 - 0.03,
        "surface\nform\nonly",
        size=5.2, color=ORANGE, ha="center")

    # Boxes
    for i, (w, c) in enumerate(zip(words, codes)):
        xi = x_start + i * (box_w + GAP)
        # Word box
        ax.add_patch(mpatches.FancyBboxPatch(
            (xi, G3_W - BOX_H / 2), box_w, BOX_H,
            boxstyle="round,pad=0,rounding_size=0.03",
            facecolor="#dce6f0", edgecolor=BLUE, lw=0.5, zorder=4))
        txt(ax, xi + box_w / 2, G3_W, w,
            size=5.5, color=BLUE,
            weight="bold" if w != "..." else "normal")
        # Code box
        ax.add_patch(mpatches.FancyBboxPatch(
            (xi, G3_C - BOX_H / 2), box_w, BOX_H,
            boxstyle="round,pad=0,rounding_size=0.03",
            facecolor="#ebebeb", edgecolor=GRAY, lw=0.5, zorder=4))
        txt(ax, xi + box_w / 2, G3_C, c,
            size=5.5, color=GRAY)

    # Note
    txt(ax, cx, 1.20,
        "13 categories unchanged; only surface form replaced",
        size=5.8, color=DGRAY, style="italic")


# ── Verdict annotations (compact, three lines, no border box) ─────────────────
VERDICTS = [
    # (gate_idx, lines, color)
    (0, ["8 / 9 models pass",
         r"median $+2.83$ SD",
         None], BLUE),
    (1, ["7 / 9 models pass",
         "(100 random splits)",
         r"5 / 5 measurable (act. split)"], BLUE),
    (2, [r"0 / 5 models pass",
         r"$+2.33$ SD $\to$ $+0.45$ SD",
         r"paired diff $+1.67$ SD"], ORANGE),
]

# Verdict line y-centers (3-line layout; unused line for Gate I is None)
_VERD_L1  = 0.79
_VERD_L2  = 0.67
_VERD_L3  = 0.55


def draw_verdicts(ax):
    line_ys = [_VERD_L1, _VERD_L2, _VERD_L3]
    for col_idx, lines, color in VERDICTS:
        cx  = col_cx(col_idx)
        x0  = COLS[col_idx][0]
        # Small filled circle at left margin of verdict zone
        cy0 = _VERD_L1 + 0.02
        fc  = BLUE if color == BLUE else ORANGE
        ax.scatter([x0 + 0.16], [cy0], s=12, color=fc,
                   zorder=5, linewidths=0)
        # Text lines
        for i, (line, ly) in enumerate(zip(lines, line_ys)):
            if line is None:
                continue
            txt(ax, x0 + 0.28, ly, line,
                ha="left", size=6.2, color=DGRAY)


# ── Conclusion bar (bottom) ───────────────────────────────────────────────────
def draw_conclusion(ax):
    box(ax, 0.10, Y_CONC_BOT, FW - 0.20, Y_CONC_TOP - Y_CONC_BOT,
        fc=BG, ec=LGRAY, lw=0.5, rad=0.05)
    mid_x = FW / 2
    mid_y = (Y_CONC_TOP + Y_CONC_BOT) / 2
    txt(ax, mid_x, mid_y,
        r"Specific steering $\nRightarrow$ encoding-invariant semantic control",
        size=8.0, color=DGRAY, weight="bold")


# ── Main ──────────────────────────────────────────────────────────────────────
def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = make_figure()

    draw_formula_bar(ax)

    cxs = [col_cx(i) for i in range(3)]
    for i in range(3):
        draw_gate_frame_header(ax, i)

    draw_gate1_schematic(ax, cxs[0])
    draw_gate2_schematic(ax, cxs[1])
    draw_gate3_schematic(ax, cxs[2])
    draw_verdicts(ax)
    draw_conclusion(ax)

    out_path = out_dir / "fig1_three_gates.pdf"
    # pad_inches=0.04 keeps height < 230 pt after tight clipping
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.04, dpi=300)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=
        "figures")
    args = parser.parse_args()
    main(Path(args.out))
