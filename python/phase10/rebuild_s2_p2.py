#!/usr/bin/env python3
"""Rebuild the S2 human subspace with P2_ridge_std and characterise it (CPU only).

Pre-registration section 23: the direction estimator changes from P1_cov to
P2_ridge_std because P1_cov was the worst-generalising of the four procedures
(holdout r +0.159 against +0.230). The change can only make the residual test
stricter, since a better estimate of the human structure is being removed.
The residual-test procedure itself is unchanged.

This step does not run any intervention. It produces, per layer, for BOTH
estimators side by side:
  - the subspace's singular spectrum, effective rank and participation ratio
  - holdout r and the permutation null per human dimension (prereg 17.2 rule)
  - cos between the P1 and P2 subspaces (principal angles)
  - the residual norm ratio of each of the top-3 axes under each estimator

Nothing here reveals a residual EFFECT: no model, no hook, no JS.
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import math
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
PERM_SEED = 20260925
N_PERM = 200
N_AXES = 3
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
    hits = [h for h in (look(w) for w in re.findall(r"[a-zA-Z']+", t.lower()))
            if h is not None]
    return ({k: float(np.mean([h[k] for h in hits])) for k in KEYS}
            if hits else None)


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        raise RuntimeError("near-zero direction")
    return (v / n).astype(np.float64)


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


def validity(X: np.ndarray, y: np.ndarray, fn: Any, n_perm: int) -> dict[str, Any]:
    n = X.shape[0]
    idx = np.random.default_rng(PERM_SEED).permutation(n)
    tr = np.zeros(n, dtype=bool)
    tr[idx[: n // 2]] = True
    ho = ~tr
    d = fn(X[tr], y[tr])
    r_ho = _r(X[ho].astype(np.float64) @ d, y[ho])
    r_in = _r(X[tr].astype(np.float64) @ d, y[tr])
    prng = np.random.default_rng(PERM_SEED + 101)
    null = []
    for _ in range(n_perm):
        yp = prng.permutation(y)
        rp = _r(X[ho].astype(np.float64) @ fn(X[tr], yp[tr]), yp[ho])
        if not math.isnan(rp):
            null.append(abs(rp))
    arr = np.asarray(null, float)
    p = float((arr >= abs(r_ho)).mean()) if arr.size >= 10 else float("nan")
    p95 = float(np.quantile(arr, 0.95)) if arr.size >= 10 else float("nan")
    return {"holdout_r": r_ho, "in_sample_r": r_in, "perm_n": int(arr.size),
            "perm_null_p95_abs_r": p95, "perm_p_value": p,
            "GENERALISES": bool((not math.isnan(p)) and p < 0.05
                                and abs(r_ho) > p95)}


def subspace(M: np.ndarray) -> dict[str, Any]:
    sv = np.linalg.svd(M.astype(np.float64), compute_uv=False)
    Q, _ = np.linalg.qr(M.astype(np.float64))
    return {"n_dims": int(M.shape[1]),
            "singular_values": [round(float(x), 4) for x in sv],
            "eff_rank_10pct": int((sv > 0.10 * sv[0]).sum()),
            "eff_rank_1pct": int((sv > 0.01 * sv[0]).sum()),
            "participation": round(float((sv.sum() ** 2)
                                         / (np.sum(sv ** 2) + 1e-30)), 3),
            "_Q": Q}


def resid_ratio(a: np.ndarray, Q: np.ndarray) -> float:
    a = a.astype(np.float64)
    r = a - Q @ (Q.T @ a)
    return float(np.linalg.norm(r) / (np.linalg.norm(a) + 1e-12))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    ap.add_argument("--out", type=Path,
                    default=BASE / "axes_nopad" / "s2_subspace_p1_vs_p2.json")
    a = ap.parse_args()

    vad = load_vad()
    e1 = json.loads(E1.read_text())
    sc = [stim_vad(s["text"], vad) for s in e1]
    keep = [i for i, s in enumerate(sc) if s is not None]
    y = {k: np.array([sc[i][k] for i in keep]) for k in KEYS}
    print(f"E1 matched {len(keep)}/{len(e1)}  (n_perm={a.n_perm})")

    rep: dict[str, Any] = {
        "env": {"generated_utc": datetime.now(timezone.utc).isoformat(),
                "script": Path(__file__).name,
                "script_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()).hexdigest(),
                "hostname": platform.node(), "gpu_used": False,
                "numpy": np.__version__, "python": sys.version.split()[0],
                "prereg_section": "23 (estimator change to P2_ridge_std)",
                "intervention_run": False,
                "NOTE": ("no model, hook or JS here: this characterises the "
                         "subspace only and cannot reveal a residual effect")},
        "layers": {}}

    for L in LAYERS:
        X = np.load(ACT / f"layer{L:02d}_seed{SEED:04d}.npz",
                    allow_pickle=True)["arr"].astype(np.float32)[keep]
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
        top = comps[np.argsort(-rp)][:N_AXES]

        entry: dict[str, Any] = {}
        Qs: dict[str, np.ndarray] = {}
        for pname, fn in PROC.items():
            dirs = {k: fn(X, y[k]) for k in KEYS}
            sp = subspace(np.stack([dirs[k] for k in KEYS], axis=1))
            Qs[pname] = sp["_Q"]
            val = {k: validity(X, y[k], fn, a.n_perm) for k in KEYS}
            entry[pname] = {
                "subspace": {k: v for k, v in sp.items() if k != "_Q"},
                "pairwise_cos": {f"{x}-{z}": round(float(dirs[x] @ dirs[z]), 4)
                                 for i, x in enumerate(KEYS) for z in KEYS[i + 1:]},
                "validity": val,
                "all_generalise": all(val[k]["GENERALISES"] for k in KEYS),
                "residual_norm_ratio_top3": [
                    round(resid_ratio(top[i], sp["_Q"]), 4) for i in range(N_AXES)],
                "abs_cos_axis_vs_dirs": [
                    {k: round(abs(float(top[i] @ dirs[k])), 4) for k in KEYS}
                    for i in range(N_AXES)],
            }
        # principal angles between the two 3-D subspaces
        s_ = np.linalg.svd(Qs["P1_cov"].T @ Qs["P2_ridge_std"], compute_uv=False)
        entry["subspace_agreement_P1_vs_P2"] = {
            "principal_cosines": [round(float(x), 4) for x in s_],
            "mean_principal_cos": round(float(np.mean(s_)), 4),
            "min_principal_cos": round(float(np.min(s_)), 4)}
        rep["layers"][str(L)] = entry

        e1r, e2r = entry["P1_cov"], entry["P2_ridge_std"]
        print(f"\n=== layer {L}")
        print(f"  P1_cov       eff10={e1r['subspace']['eff_rank_10pct']} "
              f"part={e1r['subspace']['participation']} "
              f"generalise_all={e1r['all_generalise']} "
              f"holdout r={[round(e1r['validity'][k]['holdout_r'],3) for k in KEYS]} "
              f"resid_ratio={e1r['residual_norm_ratio_top3']}")
        print(f"  P2_ridge_std eff10={e2r['subspace']['eff_rank_10pct']} "
              f"part={e2r['subspace']['participation']} "
              f"generalise_all={e2r['all_generalise']} "
              f"holdout r={[round(e2r['validity'][k]['holdout_r'],3) for k in KEYS]} "
              f"resid_ratio={e2r['residual_norm_ratio_top3']}")
        print(f"  P1 vs P2 subspace principal cos="
              f"{entry['subspace_agreement_P1_vs_P2']['principal_cosines']}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
