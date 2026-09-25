#!/usr/bin/env python3
"""Fig. 3: the cells whose axes beat the in-plane floor are the same in both halves.

One figure, one message. Every number is read from the adjudication JSONs; nothing
is typed into the figure. Significance is encoded redundantly (marker + cell
border), never by colour alone, and the diverging map is a ColorBrewer
colourblind-safe one.

Canvas is sized from the printed width: with add_axes([0, 0, 1, 1]) one data unit
equals one inch, so the cell size in inches is set explicitly and the canvas is
kept near a 5.2 in single-column width to keep the shrink factor close to 1.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

LAYERS = (5, 7, 10, 12)
AXES_N = 3
ALPHAS = (0.03, 0.05, 0.10, 0.20)
Q_THRESH = 0.05

# geometry in inches
CW, CH = 0.40, 0.235          # cell width / height
LEFT = 0.78                   # row labels
REPW = 0.26                   # "rep." marker strip
GAP = 0.34                    # gap between the two panels
RIGHT = 0.86                  # colourbar + its label
TOP = 0.50                    # panel titles + alpha header
BOT = 0.66                    # alpha axis label + legend row
FS_TICK, FS_LAB, FS_TITLE = 7.4, 8.0, 8.6


def load_cells(path: Path) -> dict[tuple[int, int, float], dict[str, Any]]:
    d = json.loads(Path(path).read_text())
    out = {}
    for c in d["C4"]["cells"]:
        out[(c["layer"], c["axis"], round(float(c["alpha_rel"]), 3))] = c
    if not out:
        raise SystemExit(f"no C4 cells in {path}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery", type=Path, required=True)
    ap.add_argument("--confirmation", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    disc, conf = load_cells(a.discovery), load_cells(a.confirmation)
    rows = [(L, i) for L in LAYERS for i in range(AXES_N)]
    nr, nc = len(rows), len(ALPHAS)

    # a row "replicates" when it is significant at some alpha in BOTH halves
    def sig_any(cells: dict, key: tuple[int, int]) -> bool:
        return any(cells[(key[0], key[1], round(al, 3))]["significant"]
                   for al in ALPHAS if (key[0], key[1], round(al, 3)) in cells)
    repl = {r: (sig_any(disc, r) and sig_any(conf, r)) for r in rows}

    if a.self_check:
        ok = True
        for name, cells in (("discovery", disc), ("confirmation", conf)):
            n = sum(1 for r in rows if sig_any(cells, r))
            print(f"  [{name}] rows significant at some alpha: {n}")
        print(f"  replicating rows: {[f'L{L} axis{i}' for (L, i) in rows if repl[(L, i)]]}")
        # a significant cell must never have mean_diff <= 0
        for cells in (disc, conf):
            for k, c in cells.items():
                if c["significant"] and c["mean_diff"] <= 0:
                    print(f"  [FAIL] {k} significant with mean_diff<=0")
                    ok = False
        # every cell the figure will draw must exist in both files
        for r in rows:
            for al in ALPHAS:
                for cells in (disc, conf):
                    if (r[0], r[1], round(al, 3)) not in cells:
                        print(f"  [FAIL] missing cell {r} a={al}")
                        ok = False
        print("SELF-CHECK:", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    W = LEFT + REPW + nc * CW + GAP + nc * CW + RIGHT
    H = BOT + nr * CH + TOP
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])      # 1 data unit == 1 inch
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    cmap = plt.get_cmap("RdBu_r")        # ColorBrewer diverging, CVD-safe
    vmax = 1.0                           # Cliff's delta range

    x0 = {"disc": LEFT + REPW, "conf": LEFT + REPW + nc * CW + GAP}
    for panel, cells in (("disc", disc), ("conf", conf)):
        bx = x0[panel]
        for ri, (L, i) in enumerate(rows):
            y = H - TOP - (ri + 1) * CH
            for ci, al in enumerate(ALPHAS):
                c = cells[(L, i, round(al, 3))]
                d = float(c["cliffs_delta"])
                ax.add_patch(Rectangle((bx + ci * CW, y), CW, CH,
                                       facecolor=cmap(0.5 + 0.5 * d / vmax),
                                       edgecolor="0.75", linewidth=0.3))
                if c["significant"]:
                    # redundant coding: heavy border + centre marker, no colour cue
                    ax.add_patch(Rectangle((bx + ci * CW, y), CW, CH,
                                           facecolor="none", edgecolor="black",
                                           linewidth=1.25, zorder=3))
                    ax.plot([bx + ci * CW + CW / 2], [y + CH / 2], marker="o",
                            ms=2.5, mfc="black", mec="white", mew=0.45, zorder=4)
        # column headers
        for ci, al in enumerate(ALPHAS):
            ax.text(bx + ci * CW + CW / 2, H - TOP + 0.05, f"{al:g}",
                    ha="center", va="bottom", fontsize=FS_TICK)
        ax.text(bx + nc * CW / 2, H - TOP + 0.20,
                "Discovery" if panel == "disc" else "Confirmation",
                ha="center", va="bottom", fontsize=FS_TITLE)
        ax.add_patch(Rectangle((bx, H - TOP - nr * CH), nc * CW, nr * CH,
                               facecolor="none", edgecolor="black",
                               linewidth=0.6, zorder=2))
        ax.text(bx + nc * CW / 2, BOT - 0.21, r"$\alpha_{\mathrm{rel}}$",
                ha="center", va="bottom", fontsize=FS_LAB)

    # row labels and the replication strip
    for ri, (L, i) in enumerate(rows):
        y = H - TOP - (ri + 1) * CH
        ax.text(LEFT - 0.07, y + CH / 2, f"L{L}  axis {i}",
                ha="right", va="center", fontsize=FS_TICK)
        if repl[(L, i)]:
            ax.plot([LEFT + REPW / 2], [y + CH / 2], marker="D", ms=3.4,
                    mfc="black", mec="black")
    ax.text(LEFT + REPW / 2, H - TOP + 0.05, "rep.", ha="center", va="bottom",
            fontsize=FS_TICK)
    for ri in range(0, nr, AXES_N):       # layer separators
        yy = H - TOP - ri * CH
        ax.plot([LEFT - 0.02, x0["conf"] + nc * CW], [yy, yy], color="0.55",
                lw=0.5, zorder=5)

    # colourbar
    cbx = x0["conf"] + nc * CW + 0.16
    cbw, cbh = 0.115, nr * CH
    cby = H - TOP - cbh
    grad = [[v] for v in [i / 127 for i in range(128)][::-1]]
    ax.imshow(grad, cmap=cmap, vmin=0, vmax=1, aspect="auto", zorder=1,
              extent=(cbx, cbx + cbw, cby, cby + cbh))
    ax.add_patch(Rectangle((cbx, cby), cbw, cbh, facecolor="none",
                           edgecolor="black", linewidth=0.6, zorder=3))
    for frac, lab in ((0.0, "$-1$"), (0.5, "$0$"), (1.0, "$+1$")):
        ax.text(cbx + cbw + 0.045, cby + frac * cbh, lab, ha="left",
                va="center", fontsize=FS_TICK)
    ax.text(cbx + cbw / 2, cby + cbh + 0.06, "Cliff's $\\delta$", ha="center",
            va="bottom", fontsize=FS_TICK)

    # legend for the redundant significance coding
    ly = 0.06
    ax.add_patch(Rectangle((LEFT + REPW, ly), CW * 0.62, CH * 0.82,
                           facecolor="0.94", edgecolor="black", linewidth=1.25))
    ax.plot([LEFT + REPW + CW * 0.31], [ly + CH * 0.41], marker="o", ms=2.5,
            mfc="black", mec="white", mew=0.45)
    ax.text(LEFT + REPW + CW * 0.72, ly + CH * 0.41,
            "BH $q<0.05$, mean diff $>0$", ha="left", va="center",
            fontsize=FS_TICK)
    ax.plot([x0["conf"] + 0.02], [ly + CH * 0.41], marker="D", ms=3.4,
            mfc="black", mec="black")
    ax.text(x0["conf"] + 0.10, ly + CH * 0.41, "significant in both halves",
            ha="left", va="center", fontsize=FS_TICK)

    a.out.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(a.out.with_suffix("." + ext), dpi=600,
                    bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"canvas {W:.2f} x {H:.2f} in  ->  {a.out.with_suffix('.pdf')}")
    print(f"shrink factor at 371.6pt text width: {371.6 / (W * 72):.3f}")
    print(f"smallest font in print: {FS_TICK * min(1.0, 371.6 / (W * 72)):.2f} pt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
