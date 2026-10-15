"""
mkfig5.py  --  Fig. S1 (supplementary): Effect size across control conditions
(a) Gate I: m10 vs m50 null directions (slope chart, 9 models)
(b) Gate I: 32-row vs 256-row scoring context (slope chart, 9 models)
(c) Gate II: 30-split vs 100-split (slope chart, 9 models)

Target: supplementary full-column, height <= 250 pt (3.47 in).
figsize (7.16, 3.4) is already within range.

Usage:
    python mkfig5.py [--root /path/to/analysis_root] [--out /path/to/figures]
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SCRATCHPAD = Path("data")
sys.path.insert(0, str(SCRATCHPAD))
from final_tables import judge, SHORT, ORDER  # noqa: E402

# ── Style ────────────────────────────────────────────────────────────────────
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

B    = 4000
READOUT = "single"   # focus on single for Fig. 5


def compute_excess_from_npz(npz_path: Path, readout: str = "single",
                             seed: int = 777) -> float:
    """Median standardized excess across 13 targets (scalar)."""
    z     = np.load(npz_path)
    tsel  = z[f"emotion|{readout}|tgt_sel"]
    ttest = z[f"emotion|{readout}|tgt_test"]
    A     = z[f"emotion|{readout}|F5"]
    C     = tsel.shape[1]
    K, M, _, _ = A.shape
    rng   = np.random.default_rng(seed)

    val = np.array([ttest[int(np.argmax(tsel[:, e])), e] for e in range(C)])
    null = np.zeros((B, C))
    for e in range(C):
        pick = rng.integers(0, M, size=(B, K))
        fs   = A[np.arange(K)[None, :], pick, 0, e]
        fh   = A[np.arange(K)[None, :], pick, 1, e]
        null[:, e] = fh[np.arange(B), np.argmax(fs, axis=1)]
    h1   = null[: B // 2]
    mu   = h1.mean(0)
    sd   = h1.std(0) + 1e-12
    return float(np.median((val - mu) / sd))


# ── Collect data ──────────────────────────────────────────────────────────────
def collect_gatei(c3_dir: Path):
    """Gate I: {model: (excess_m10, excess_m50)}"""
    data = {}
    for f in sorted(c3_dir.glob("meta_*_m50.json")):
        m = re.fullmatch(r"meta_(.+?)_L\d+_m50\.json", f.name)
        if not m:
            continue
        meta  = json.loads(f.read_text())
        mname = SHORT.get(meta["model"].split("/")[-1], meta["model"])
        tag   = f.name.replace("meta_", "").replace("_m50.json", "")
        npz50 = c3_dir / f"raw_{tag}_m50.npz"
        npz10 = c3_dir / f"raw_{tag}.npz"
        if not (npz10.exists() and npz50.exists()):
            continue
        e10 = compute_excess_from_npz(npz10, READOUT)
        e50 = compute_excess_from_npz(npz50, READOUT)
        data[mname] = (e10, e50)
    return data


def collect_bigtest(c3_dir: Path):
    """Gate I: {model: (excess_m10_32rows, excess_m10_256rows)}"""
    data = {}
    for f in sorted(c3_dir.glob("meta_*_bigtest.json")):
        # skip _m3_bigtest variants
        if "_m3_" in f.name:
            continue
        m = re.fullmatch(r"meta_(.+?)_L\d+_bigtest\.json", f.name)
        if not m:
            continue
        meta  = json.loads(f.read_text())
        mname = SHORT.get(meta["model"].split("/")[-1], meta["model"])
        tag   = f.name.replace("meta_", "").replace("_bigtest.json", "")
        npz_b  = c3_dir / f"raw_{tag}_bigtest.npz"
        npz_32 = c3_dir / f"raw_{tag}.npz"
        if not (npz_32.exists() and npz_b.exists()):
            continue
        e32  = compute_excess_from_npz(npz_32, READOUT)
        e256 = compute_excess_from_npz(npz_b,  READOUT)
        data[mname] = (e32, e256)
    return data


def collect_lp(lp_dir: Path):
    """Gate II: {model: (excess_30, excess_100)}"""
    data = {}
    for f in sorted(lp_dir.glob("LP_*.json")):
        if "_p100" in f.name:
            continue
        d     = json.loads(f.read_text())
        mname = SHORT.get(d["model"].split("/")[-1], d["model"])
        tag   = f.name.replace("LP_", "").replace(".json", "")
        f100  = lp_dir / f"LP_{tag}_p100.json"
        if not f100.exists():
            continue
        e30  = d["results"][READOUT]["median_excess_sd"]
        e100 = json.loads(f100.read_text())["results"][READOUT]["median_excess_sd"]
        data[mname] = (e30, e100)
    return data


# ── Slope chart helper ────────────────────────────────────────────────────────
def _series_color(mname: str, col_a: str, col_b: str) -> str:
    """Alternate two colors to distinguish crossing lines."""
    idx = ORDER.index(mname) if mname in ORDER else 0
    return col_a if idx % 2 == 0 else col_b


def _nudge_labels(models, y_vals, min_gap=0.18):
    """Nudge labels to avoid vertical overlap; returns adjusted y positions."""
    pairs = sorted(zip(y_vals, models))
    adjusted = list(pairs)
    changed = True
    for _ in range(50):
        changed = False
        for i in range(1, len(adjusted)):
            if adjusted[i][0] - adjusted[i-1][0] < min_gap:
                mid = (adjusted[i][0] + adjusted[i-1][0]) / 2
                adjusted[i-1] = (mid - min_gap / 2, adjusted[i-1][1])
                adjusted[i]   = (mid + min_gap / 2, adjusted[i][1])
                changed = True
        if not changed:
            break
    return {m: y for y, m in adjusted}


def draw_slope(ax, data: dict, label_left: str, label_right: str,
               col_a: str = "#1f497d", col_b: str = "#888888"):
    """Draw a slope chart from data = {model: (val_left, val_right)}."""
    x = [0, 1]
    models_present = [m for m in ORDER if m in data]

    for mname in models_present:
        y1, y2 = data[mname]
        c = _series_color(mname, col_a, col_b)
        ax.plot(x, [y1, y2], color=c, linewidth=1.0, alpha=0.85, zorder=2)
        ax.scatter([0], [y1], color=c, s=20, zorder=3, linewidths=0.3,
                   edgecolors="white")
        ax.scatter([1], [y2], color=c, s=20, zorder=3, linewidths=0.3,
                   edgecolors="white")

    # Labels on the right – nudge to avoid overlap
    right_y = [data[m][1] for m in models_present]
    nudged  = _nudge_labels(models_present, right_y)
    for mname in models_present:
        y2_nudged = nudged[mname]
        y2_orig   = data[mname][1]
        c = _series_color(mname, col_a, col_b)
        # Small connector line if nudged
        if abs(y2_nudged - y2_orig) > 0.01:
            ax.plot([1.02, 1.025], [y2_orig, y2_nudged],
                    color=c, linewidth=0.4, alpha=0.6)
        ax.text(1.03, y2_nudged, mname, fontsize=6.5, va="center", color=c)

    ax.set_xticks([0, 1])
    ax.set_xticklabels([label_left, label_right], fontsize=8)
    ax.set_xlim(-0.1, 1.35)
    ax.set_ylabel("Median standardized excess (single)", labelpad=3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhline(0, color="#cccccc", linewidth=0.5)


def main(root_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    c3_dir = root_dir / "stageC3"
    lp_dir = root_dir / "stageLP"

    data_a = collect_gatei(c3_dir)
    data_b = collect_bigtest(c3_dir)
    data_c = collect_lp(lp_dir)

    print("Gate I m10 vs m50 models:", sorted(data_a.keys()))
    print("Gate I 32 vs 256 models: ", sorted(data_b.keys()))
    print("Gate II 30 vs 100 models:", sorted(data_c.keys()))

    # figsize (7.16, 3.2): supplementary full-column, ~ 230 pt after tight
    fig, axes = plt.subplots(1, 3, figsize=(7.16, 3.2),
                              gridspec_kw={"wspace": 0.50, "left": 0.08,
                                           "right": 0.84, "bottom": 0.12,
                                           "top": 0.92})

    # ── (a) Gate I: m10 vs m50 ────────────────────────────────────────────────
    draw_slope(axes[0], data_a, "10 nulls", "50 nulls")
    axes[0].set_title("(a)  Gate I: null set size", loc="left", pad=4)

    # ── (b) Gate I: 32 vs 256 scoring rows ───────────────────────────────────
    draw_slope(axes[1], data_b, "32 rows", "256 rows")
    axes[1].set_title("(b)  Gate I: scoring rows", loc="left", pad=4)

    # ── (c) Gate II: 30 vs 100 splits ────────────────────────────────────────
    draw_slope(axes[2], data_c, "30 splits", "100 splits")
    axes[2].set_title("(c)  Gate II: split count", loc="left", pad=4)

    # Supplementary figure: save to supp/figs/
    out_path = out_dir / "fig5_control_strength.pdf"
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    print(f"Saved: {out_path}")
    # Also save to supp/figs/ if it exists
    supp_dir = out_dir.parent / "supp" / "figs"
    if supp_dir.exists():
        supp_path = supp_dir / "fig5_control_strength.pdf"
        fig.savefig(supp_path, bbox_inches="tight", dpi=300)
        print(f"Also saved: {supp_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=
        "data")
    parser.add_argument("--out", default=
        "figures")
    args = parser.parse_args()
    main(Path(args.root), Path(args.out))
