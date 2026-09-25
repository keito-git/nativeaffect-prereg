#!/usr/bin/env python3
"""S3 category directions: generalisation, alignment, PC containment, PD2. CPU only.

Consumes the E4 index 40-79 last-token activation cache written by
run_inplane_floor.py, so this never needs the GPU again.

Answers, per layer, for the 20 one-vs-rest emotion-category directions:
  - do they generalise? (train on template_variant 0, score on variant 1, with a
    permutation null on the same activations - prereg 17.2 rule)
  - how much of each ICA axis lies inside the S3 subspace (inside_fraction), with
    a chance baseline from random unit vectors
  - how much of each category direction lies inside the top-10 PC span (the
    mechanism test from 25.3, applied to S3 because S3 is the primary basis)
  - PD2: cosines between estimation procedures for the category directions
    (prereg 21.3 predicted these exceed S2's)

Two estimators, as in section 23.4: P1_cov and P2_ridge_std.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import platform
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
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
LAYERS = (5, 7, 10, 12)
SEED = 42
PERM_SEED = 20260925
N_PERM = 200
N_AXES = 3
PC_K = 10
N_RANDOM = 2000


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


def _r(a: np.ndarray, b: np.ndarray) -> float:
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def validity(X: np.ndarray, y: np.ndarray, fn: Any, tr: np.ndarray,
             n_perm: int) -> dict[str, Any]:
    ho = ~tr
    if tr.sum() < 3 or ho.sum() < 3 or np.std(y[tr]) < 1e-12:
        return {"holdout_r": float("nan"), "perm_p_value": float("nan"),
                "GENERALISES": False, "skipped": "degenerate split"}
    d = fn(X[tr], y[tr])
    r_ho = _r(X[ho].astype(np.float64) @ d, y[ho])
    r_in = _r(X[tr].astype(np.float64) @ d, y[tr])
    prng = np.random.default_rng(PERM_SEED + 101)
    null = []
    for _ in range(n_perm):
        yp = prng.permutation(y)
        if np.std(yp[tr]) < 1e-12:
            continue
        rp = _r(X[ho].astype(np.float64) @ fn(X[tr], yp[tr]), yp[ho])
        if not math.isnan(rp):
            null.append(abs(rp))
    arr = np.asarray(null, float)
    p = float((arr >= abs(r_ho)).mean()) if arr.size >= 10 else float("nan")
    p95 = float(np.quantile(arr, 0.95)) if arr.size >= 10 else float("nan")
    return {"holdout_r": r_ho, "in_sample_r": r_in,
            "perm_null_p95_abs_r": p95, "perm_p_value": p, "perm_n": int(arr.size),
            "GENERALISES": bool((not math.isnan(p)) and p < 0.05
                                and abs(r_ho) > p95)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path,
                    default=ACT / f"e4_heldout40to79_seed{SEED:04d}.npz")
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    ap.add_argument("--out", type=Path,
                    default=BASE / "axes_nopad" / "s3_categories.json")
    a = ap.parse_args()
    if not a.cache.exists():
        print(f"cache missing: {a.cache}\nrun run_inplane_floor.py first "
              f"(it writes this cache)", file=sys.stderr)
        return 2

    from sklearn.decomposition import PCA
    z = np.load(a.cache, allow_pickle=True)
    e4 = json.loads(E4.read_text())
    held = [i for i in range(len(e4)) if i >= 40]
    cats = [e4[i]["target_emotion"] for i in held]
    names = sorted(set(cats))
    tr = np.array([e4[i].get("template_variant", 0) == 0 for i in held], bool)
    Y = {c: np.array([1.0 if hc == c else 0.0 for hc in cats]) for c in names}
    print(f"held-out E4: n={len(held)} categories={len(names)} "
          f"train(variant0)={int(tr.sum())}")
    rng = np.random.default_rng(PERM_SEED)

    rep: dict[str, Any] = {
        "env": {"generated_utc": datetime.now(timezone.utc).isoformat(),
                "script": Path(__file__).name,
                "script_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()).hexdigest(),
                "hostname": platform.node(), "gpu_used": False,
                "cache": str(a.cache), "n_perm": a.n_perm,
                "n_categories": len(names), "n_heldout": len(held),
                "prereg_sections": "17.2 (validity), 21.3 (PD2), 23.4 (P2), 25.3 (PC)",
                "intervention_run": False},
        "layers": {}}

    for L in LAYERS:
        key = f"layer{L:02d}"
        if key not in z:
            print(f"layer {L} not in cache; skipping")
            continue
        Xh = z[key].astype(np.float32)
        X1 = np.load(ACT / f"layer{L:02d}_seed{SEED:04d}.npz",
                     allow_pickle=True)["arr"].astype(np.float32)
        PCs = PCA(n_components=PC_K, random_state=SEED).fit(
            X1.astype(np.float64)).components_

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
        rp = compute_split_reproducibility(
            ACT / f"layer{L:02d}_seed{SEED:04d}.npz", comps, seed=SEED)
        top = comps[np.argsort(-rp)][:N_AXES].astype(np.float64)
        D = Xh.shape[1]

        entry: dict[str, Any] = {}
        for pname, fn in PROC.items():
            dirs = {c: fn(Xh, Y[c]) for c in names}
            val = {c: validity(Xh, Y[c], fn, tr, a.n_perm) for c in names}
            ngen = sum(1 for c in names if val[c]["GENERALISES"])
            rs = sorted(val[c]["holdout_r"] for c in names
                        if not math.isnan(val[c]["holdout_r"]))
            # S3 subspace = the 3 human V/A/D dirs are NOT included here; this is
            # the category block alone, which is what 25.4 asks about
            M = np.stack([dirs[c] for c in names], axis=1)
            sv = np.linalg.svd(M, compute_uv=False)
            Q, _ = np.linalg.qr(M)
            inside = [float(np.sum((Q.T @ top[i]) ** 2)) for i in range(N_AXES)]
            R = rng.standard_normal((N_RANDOM, D))
            R /= np.linalg.norm(R, axis=1, keepdims=True)
            null_in = np.einsum("ij,ij->i", R @ Q, R @ Q)
            p_in = [float((null_in >= o).mean()) for o in inside]
            pc_inside = {c: round(float(np.sum((PCs @ dirs[c]) ** 2)), 4)
                         for c in names}
            entry[pname] = {
                "n_generalising": ngen, "n_total": len(names),
                "frac_generalising": round(ngen / len(names), 3),
                "holdout_r_min_med_max": [round(rs[0], 4),
                                          round(rs[len(rs) // 2], 4),
                                          round(rs[-1], 4)] if rs else None,
                "per_category_validity": val,
                "subspace_eff_rank_10pct": int((sv > 0.10 * sv[0]).sum()),
                "subspace_eff_rank_1pct": int((sv > 0.01 * sv[0]).sum()),
                "subspace_participation": round(float((sv.sum() ** 2)
                                                      / (np.sum(sv ** 2) + 1e-30)), 3),
                "axis_inside_fraction": [round(x, 6) for x in inside],
                "axis_inside_fraction_pct": [round(100 * x, 4) for x in inside],
                "chance_inside_mean": round(float(null_in.mean()), 6),
                "chance_inside_p95": round(float(np.quantile(null_in, .95)), 6),
                "axis_inside_p_vs_chance": p_in,
                "category_dir_inside_top10PC": pc_inside,
                "category_dir_inside_top10PC_median": round(
                    float(np.median(list(pc_inside.values()))), 4),
            }
        # PD2: procedure agreement for the category directions
        pd2 = {}
        for c in names:
            d1 = PROC["P1_cov"](Xh, Y[c])
            d2 = PROC["P2_ridge_std"](Xh, Y[c])
            pd2[c] = round(abs(float(d1 @ d2)), 4)
        entry["PD2_cos_P1_vs_P2_per_category"] = pd2
        entry["PD2_summary"] = {
            "median": round(float(np.median(list(pd2.values()))), 4),
            "min": round(float(np.min(list(pd2.values()))), 4),
            "max": round(float(np.max(list(pd2.values()))), 4)}
        rep["layers"][str(L)] = entry

        print(f"\n=== layer {L}")
        for pname in PROC:
            e = entry[pname]
            print(f"  {pname:<13} generalise={e['n_generalising']}/{e['n_total']} "
                  f"holdout r(min/med/max)={e['holdout_r_min_med_max']} "
                  f"effrank10={e['subspace_eff_rank_10pct']} "
                  f"part={e['subspace_participation']}")
            print(f"     axis inside S3cat span %={e['axis_inside_fraction_pct']} "
                  f"(chance {100*e['chance_inside_mean']:.3f}%, "
                  f"p={[round(p,4) for p in e['axis_inside_p_vs_chance']]})")
            print(f"     category dirs inside top10-PC span (median)="
                  f"{e['category_dir_inside_top10PC_median']}")
        print(f"  PD2 cos(P1,P2) per category: {entry['PD2_summary']}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
