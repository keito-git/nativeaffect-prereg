#!/usr/bin/env python3
"""Alignment as the primary measurement, with a chance baseline and a mechanism test.

Prereg section 25. CPU only: no model, no hook, no intervention.

Three things the supervising associate made mandatory:

1. The headline number is the FRACTION OF AXIS NORM INSIDE the human subspace,
   1 - (residual norm ratio)^2, which is directly interpretable, rather than
   max|cos|.

2. A chance baseline. A random unit vector in 2048 dimensions still has a small
   overlap with any 3-D subspace: the expectation of the inside-fraction is r/d,
   i.e. 3/2048 = 0.146%. So the observed values must be tested against random
   directions drawn in the same space and scored with the same statistic, to say
   whether the axes are "slightly aligned but overwhelmingly outside" or
   "indistinguishable from chance".

3. A mechanism test for the trade-off (directions overlapping the axes do not
   generalise; directions that generalise do not overlap). Candidate mechanism:
   P1_cov is underdetermined and is pulled towards the dominant covariance
   structure of the activations, and the ICA axes come from those same
   activations, so the overlap may be nothing more than both being pulled onto
   the leading principal components. Measured by the alignment of each direction
   with the top PCs.
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

BASE = Path("/path/to/work/results")
SLUG = "swiss-ai__Apertus-v1_1-1_5B"
ACT = BASE / "activations_nopad" / SLUG
ICA = BASE / "ica_nopad" / SLUG
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
VADP = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
KEYS = ("valence", "arousal", "dominance")
LAYERS = (5, 7, 10, 12)
SEED = 42
N_RANDOM = 2000
N_AXES = 3
N_PC = 10
_SUF = ["fully", "fulness", "fulness", "ful", "ness", "ly",
        "ing", "tion", "ed", "er", "est", "s"]


def load_vad() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    with open(VADP, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = row.get("word", "").strip().lower()
            if not w:
                continue
            try:
                out[w] = {k: float(row[k].strip()) for k in KEYS}
            except (KeyError, ValueError, AttributeError):
                continue
    return out


def stim_vad(t: str, vad: dict[str, dict[str, float]]) -> dict | None:
    def look(w: str) -> dict[str, float] | None:
        if w in vad:
            return vad[w]
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                return vad[w[: -len(s)]]
        return None
    h = [x for x in (look(w) for w in re.findall(r"[a-zA-Z']+", t.lower()))
         if x is not None]
    return ({k: float(np.mean([z[k] for z in h])) for k in KEYS}) if h else None


def _unit(v: np.ndarray) -> np.ndarray:
    return (v / (np.linalg.norm(v) + 1e-30)).astype(np.float64)


def p1_cov(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    yz = (y - y.mean()) / (y.std() + 1e-8)
    return _unit(X.astype(np.float64).T @ yz)


def p2_ridge_std(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    from sklearn.linear_model import RidgeCV
    Xf = X.astype(np.float64)
    mu, sd = Xf.mean(axis=0), Xf.std(axis=0)
    sd[sd < 1e-12] = 1.0
    m = RidgeCV(alphas=np.logspace(-2, 5, 22), fit_intercept=True)
    m.fit((Xf - mu) / sd, (y - y.mean()) / (y.std() + 1e-8))
    return _unit(np.asarray(m.coef_, dtype=np.float64).ravel() / sd)


PROC = {"P1_cov": p1_cov, "P2_ridge_std": p2_ridge_std}


def inside_fraction(a: np.ndarray, Q: np.ndarray) -> float:
    """Fraction of a unit vector's squared norm lying inside span(Q)."""
    a = _unit(a)
    proj = Q @ (Q.T @ a)
    return float(np.dot(proj, proj))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=BASE / "axes_nopad" / "alignment_primary.json")
    a = ap.parse_args()

    from sklearn.decomposition import PCA
    vad = load_vad()
    e1 = json.loads(E1.read_text())
    sc = [stim_vad(s["text"], vad) for s in e1]
    keep = [i for i, s in enumerate(sc) if s is not None]
    y = {k: np.array([sc[i][k] for i in keep]) for k in KEYS}
    rng = np.random.default_rng(20260925)

    rep: dict[str, Any] = {
        "env": {"generated_utc": datetime.now(timezone.utc).isoformat(),
                "script": Path(__file__).name,
                "script_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()).hexdigest(),
                "hostname": platform.node(), "gpu_used": False,
                "intervention_run": False, "n_random_baseline": N_RANDOM,
                "prereg_section": "25",
                "headline_statistic": "inside_fraction = 1 - (residual norm ratio)^2",
                "chance_expectation_note": ("for a random unit vector and a rank-r "
                                            "subspace in d dims the expected "
                                            "inside_fraction is r/d = 3/2048 = "
                                            "0.001465")},
        "layers": {}}

    for L in LAYERS:
        npz = ACT / f"layer{L:02d}_seed{SEED:04d}.npz"
        Xall = np.load(npz, allow_pickle=True)["arr"].astype(np.float32)
        X = Xall[keep]
        D = X.shape[1]

        files = sorted(glob.glob(str(ICA / f"layer{L:02d}_seed{SEED:04d}_K*.json")))
        best, bs = None, -2.0
        for fp in files:
            dd = json.loads(Path(fp).read_text())
            s_ = max(dd.get("silhouettes") or [-1.0])
            if s_ > bs:
                bs, best = s_, dd
        comps = np.array(best["components"], dtype=np.float32)
        sys.path.insert(0, "/path/to/work/code/phase10")
        from run_ica import compute_split_reproducibility
        rp = compute_split_reproducibility(npz, comps, seed=SEED)
        top = comps[np.argsort(-rp)][:N_AXES].astype(np.float64)

        # principal components of the same activations (mechanism test)
        pca = PCA(n_components=N_PC, random_state=SEED).fit(X.astype(np.float64))
        PCs = pca.components_
        evr = [round(float(x), 4) for x in pca.explained_variance_ratio_]

        entry: dict[str, Any] = {"pca_explained_variance_ratio_top10": evr}
        for pname, fn in PROC.items():
            dirs = {k: fn(X, y[k]) for k in KEYS}
            M = np.stack([dirs[k] for k in KEYS], axis=1)
            Q, _ = np.linalg.qr(M)

            obs = [inside_fraction(top[i], Q) for i in range(N_AXES)]
            mx = [max(abs(float(top[i] @ dirs[k])) for k in KEYS)
                  for i in range(N_AXES)]
            # chance baseline: random unit vectors scored the same way
            R = rng.standard_normal((N_RANDOM, D))
            R /= np.linalg.norm(R, axis=1, keepdims=True)
            null_inside = np.einsum("ij,ij->i", R @ Q, R @ Q)
            null_max = np.max(np.abs(R @ M), axis=1)
            p_inside = [float((null_inside >= o).mean()) for o in obs]
            p_max = [float((null_max >= m).mean()) for m in mx]

            # mechanism: alignment of the human directions with the top PCs
            pc_align = {k: [round(abs(float(dirs[k] @ PCs[j])), 4)
                            for j in range(N_PC)] for k in KEYS}
            pc_max = {k: round(max(pc_align[k]), 4) for k in KEYS}
            pc_inside10 = {k: round(float(np.sum(
                (PCs @ dirs[k]) ** 2)), 4) for k in KEYS}
            axis_pc_inside10 = [round(float(np.sum((PCs @ top[i]) ** 2)), 4)
                                for i in range(N_AXES)]

            entry[pname] = {
                "inside_fraction_per_axis": [round(o, 6) for o in obs],
                "inside_fraction_pct_per_axis": [round(100 * o, 4) for o in obs],
                "max_abs_cos_per_axis": [round(m, 4) for m in mx],
                "chance": {
                    "null_inside_mean": round(float(null_inside.mean()), 6),
                    "null_inside_p95": round(float(np.quantile(null_inside, .95)), 6),
                    "null_max_abs_cos_mean": round(float(null_max.mean()), 4),
                    "null_max_abs_cos_p95": round(float(np.quantile(null_max, .95)), 4),
                    "p_inside_per_axis": p_inside,
                    "p_max_abs_cos_per_axis": p_max,
                    "n_axes_above_chance_p05": int(sum(1 for p in p_inside
                                                       if p < 0.05))},
                "mechanism_pc_alignment": {
                    "human_dir_max_abs_cos_with_top10_PCs": pc_max,
                    "human_dir_inside_fraction_of_top10_PC_space": pc_inside10,
                    "axis_inside_fraction_of_top10_PC_space": axis_pc_inside10},
            }
        rep["layers"][str(L)] = entry

        print(f"\n=== layer {L}  (PC1-10 explain {sum(evr):.3f} of variance)")
        for pname in PROC:
            e = entry[pname]
            print(f"  {pname:<13} inside%={e['inside_fraction_pct_per_axis']} "
                  f"max|cos|={e['max_abs_cos_per_axis']}")
            c = e["chance"]
            print(f"     chance: inside mean={100*c['null_inside_mean']:.4f}% "
                  f"p95={100*c['null_inside_p95']:.4f}% | "
                  f"p_inside={[round(p,4) for p in c['p_inside_per_axis']]} "
                  f"above_chance={c['n_axes_above_chance_p05']}/3")
            m = e["mechanism_pc_alignment"]
            print(f"     PC-align: human dir inside top10-PC space="
                  f"{m['human_dir_inside_fraction_of_top10_PC_space']} "
                  f"(axes: {m['axis_inside_fraction_of_top10_PC_space']})")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
