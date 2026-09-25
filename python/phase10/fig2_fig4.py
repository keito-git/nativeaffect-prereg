#!/usr/bin/env python3
"""Fig. 2 (floor effects against alpha) and Fig. 4 (seed stability).

Both read result JSONs; no number is written into either figure. Series are
distinguished by marker and line style as well as colour, so neither figure
depends on colour being seen. Canvas widths are chosen so the printed shrink
factor stays near 1 at a 371.6 pt text width.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

B = Path("/path/to/research/論文/NativeAffect_AI固有の感情軸")
R = B / "03_解析"
LAYERS = (5, 7, 10, 12)
ALPHAS = (0.01, 0.03, 0.05, 0.10, 0.20)
FS = 8.6   # smallest derived size stays >= 7 pt in print
# Okabe-Ito, colour-blind safe; each series also gets its own marker and dash
SERIES = [
    ("js_floor_inplane_mean", "In-plane floor", "#0072B2", "o", "-"),
    ("js_floor_fullrand_mean", "Full-space floor", "#D55E00", "s", "--"),
    ("js_axis0_mean", "Axis 0", "#009E73", "^", "-."),
    ("js_axis1_mean", "Axis 1", "#CC79A7", "v", ":"),
    ("js_axis2_mean", "Axis 2", "#56B4E9", "D", (0, (3, 1, 1, 1))),
]


def row(doc: dict, L: int, al: float) -> dict | None:
    for Lo in doc["layers"]:
        if Lo["layer"] == L:
            for r in Lo["rows"]:
                if abs(float(r["alpha_rel"]) - al) < 1e-9:
                    return r
    return None


def fig2(out: Path) -> None:
    d = json.loads((R / "confirmation/inplane_floor_confirmation_20260925T210454Z.json")
                   .read_text())
    W, H = 5.1, 4.1
    fig = plt.figure(figsize=(W, H))
    for k, L in enumerate(LAYERS):
        ax = fig.add_subplot(2, 2, k + 1)
        for key, lab, col, mk, ls in SERIES:
            ys = [row(d, L, a)[key] for a in ALPHAS]
            ax.plot(ALPHAS, ys, color=col, marker=mk, linestyle=ls, ms=3.2,
                    lw=1.0, label=lab, markerfacecolor="none", markeredgewidth=0.9)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"Layer {L}", fontsize=FS + 0.6, pad=3)
        ax.tick_params(labelsize=FS - 0.6, length=2.5, pad=1.5)
        ax.grid(True, which="major", lw=0.3, alpha=0.4)
        if k >= 2:
            ax.set_xlabel(r"$\alpha_{\mathrm{rel}}$", fontsize=FS)
        if k % 2 == 0:
            ax.set_ylabel("next-token JS", fontsize=FS)
    h, lab = fig.axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=5, fontsize=FS - 0.8,
               frameon=False, bbox_to_anchor=(0.5, -0.015), handlelength=2.4,
               columnspacing=1.1, handletextpad=0.5)
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(out.with_suffix("." + ext), dpi=600, bbox_inches="tight",
                    pad_inches=0.02)
    plt.close(fig)
    print(f"Fig.2 canvas {W:.2f}x{H:.2f} in; shrink {371.6/(W*72):.3f}; "
          f"min font in print {(FS-0.8)*min(1.0,371.6/(W*72)):.2f} pt -> {out}")


def fig4(out: Path) -> None:
    d = json.loads((R / "axes_nopad/seed_stability_c3.json").read_text())
    seeds = sorted(d["seeds"], key=int)
    W, H = 5.1, 2.7
    fig = plt.figure(figsize=(W, H))
    cols = {5: "#0072B2", 7: "#D55E00", 10: "#009E73", 12: "#CC79A7"}
    mks = {5: "o", 7: "s", 10: "^", 12: "D"}
    for pi, (key, name) in enumerate((("inside_pct_S2", "S2 (rank 3)"),
                                      ("inside_pct_S3", "S3 (rank 20)"))):
        ax = fig.add_subplot(1, 2, pi + 1)
        for si, s in enumerate(seeds):
            for L in LAYERS:
                vals = d["seeds"][s]["layers"][str(L)][key]
                xs = [si + (list(LAYERS).index(L) - 1.5) * 0.13] * len(vals)
                ax.plot(xs, vals, linestyle="none", marker=mks[L], ms=3.0,
                        markerfacecolor="none", markeredgecolor=cols[L],
                        markeredgewidth=0.9,
                        label=f"Layer {L}" if (si == 0 and pi == 0) else None)
        ax.axhline(5.0, color="black", lw=0.8, ls="--")
        ax.text(-0.42, 5.0, "5% criterion", fontsize=FS - 1.2,
                ha="left", va="bottom")
        ax.set_xticks(range(len(seeds)))
        ax.set_xticklabels(seeds, fontsize=FS - 0.6)
        ax.set_xlabel("ICA seed", fontsize=FS)
        ax.set_title(name, fontsize=FS + 0.6, pad=3)
        ax.tick_params(labelsize=FS - 0.6, length=2.5, pad=1.5)
        ax.grid(True, axis="y", lw=0.3, alpha=0.4)
        if pi == 0:
            ax.set_ylabel("inside_fraction (%)", fontsize=FS)
    h, lab = fig.axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=4, fontsize=FS - 0.8,
               frameon=False, bbox_to_anchor=(0.5, -0.03), columnspacing=1.2,
               handletextpad=0.4)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(out.with_suffix("." + ext), dpi=600, bbox_inches="tight",
                    pad_inches=0.02)
    plt.close(fig)
    print(f"Fig.4 canvas {W:.2f}x{H:.2f} in; shrink {371.6/(W*72):.3f}; "
          f"min font in print {(FS-1.2)*min(1.0,371.6/(W*72)):.2f} pt -> {out}")


def self_check() -> int:
    ok = True

    def c(n: str, v: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if v else 'FAIL'}] {n}")
        ok &= bool(v)
    d = json.loads((R / "confirmation/inplane_floor_confirmation_20260925T210454Z.json")
                   .read_text())
    c("Fig.2: every layer/alpha cell exists",
      all(row(d, L, a) is not None for L in LAYERS for a in ALPHAS))
    c("Fig.2: every plotted key is present",
      all(k in row(d, L, a) for k, *_ in SERIES for L in LAYERS for a in ALPHAS))
    c("Fig.2: JS values are positive (log axis is valid)",
      all(row(d, L, a)[k] > 0 for k, *_ in SERIES for L in LAYERS for a in ALPHAS))
    c("Fig.2: the in-plane floor exceeds the full-space floor at every cell",
      all(row(d, L, a)["js_floor_inplane_mean"]
          > row(d, L, a)["js_floor_fullrand_mean"] for L in LAYERS for a in ALPHAS))
    s = json.loads((R / "axes_nopad/seed_stability_c3.json").read_text())
    c("Fig.4: five seeds, four layers, three axes each",
      all(len(s["seeds"][k]["layers"][str(L)][q]) == 3
          for k in s["seeds"] for L in LAYERS
          for q in ("inside_pct_S2", "inside_pct_S3")) and len(s["seeds"]) == 5)
    c("Fig.4: the only S2 value above 5% is seed 46",
      [k for k in s["seeds"]
       if any(v > 5.0 for L in LAYERS
              for v in s["seeds"][k]["layers"][str(L)]["inside_pct_S2"])] == ["46"])
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=B / "04_原稿/図表")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        return self_check()
    if self_check() != 0:
        print("REFUSING to draw: self-check failed")
        return 2
    a.out_dir.mkdir(parents=True, exist_ok=True)
    fig2(a.out_dir / "fig2_floor_vs_alpha")
    fig4(a.out_dir / "fig4_seed_stability")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
