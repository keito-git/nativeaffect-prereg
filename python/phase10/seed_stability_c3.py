#!/usr/bin/env python3
"""C3 seed stability: refit ICA for seeds 42-46 on CPU and measure inside_fraction.

Pre-registration 37.2. CPU only - the PAD-free activations are cached, so the axes
can be refitted without the GPU. No intervention is run here.

Per seed and layer:
  - refit ICA on the cached activations (same k_range and selection rule as the
    original pipeline), pick top-3 axes by split-half reproducibility
  - build the human subspaces with P2_ridge_std: S2 primary (V/A/D on the 287
    matched E1 sentences) and S3 secondary (20 one-vs-rest category directions on
    the held-out E4 40-79 activations)
  - report inside_fraction = 1 - (residual norm ratio)^2 for each axis against both,
    with the chance level, and whether the C3 criterion (>=10 of 12 cells under
    5 percent) holds within that seed

Note on what varies with seed: the activations are fixed, so the human directions are
fixed too. What changes is the ICA solution, hence the axes. That is exactly the
quantity C3 depends on.
"""
from __future__ import annotations

import argparse
import csv
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
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
VADP = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
HELD_CACHE = ACT / "e4_heldout40to79_seed0042.npz"
KEYS = ("valence", "arousal", "dominance")
LAYERS = (5, 7, 10, 12)
SEEDS = (42, 43, 44, 45, 46)
K_RANGE = (5, 20)
N_AXES = 3
THRESH_PCT = 5.0      # prereg 37 / 38.1
MIN_CELLS = 10        # of 12
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


def p2_ridge_std(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    from sklearn.linear_model import RidgeCV
    Xf = X.astype(np.float64)
    mu, sd = Xf.mean(axis=0), Xf.std(axis=0)
    sd[sd < 1e-12] = 1.0
    m = RidgeCV(alphas=np.logspace(-2, 5, 22), fit_intercept=True)
    m.fit((Xf - mu) / sd, (y - y.mean()) / (y.std() + 1e-8))
    return _unit(np.asarray(m.coef_, dtype=np.float64).ravel() / sd)


def inside_pct(a: np.ndarray, Q: np.ndarray) -> float:
    a = _unit(a)
    p = Q @ (Q.T @ a)
    return 100.0 * float(np.dot(p, p))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--out", type=Path,
                    default=BASE / "axes_nopad" / "seed_stability_c3.json")
    a = ap.parse_args()

    sys.path.insert(0, "/path/to/work/code/phase10")
    from run_ica import compute_split_reproducibility, run_ica_sweep

    vad = load_vad()
    e1 = json.loads(E1.read_text())
    sc = [stim_vad(s["text"], vad) for s in e1]
    keep = [i for i, s in enumerate(sc) if s is not None]
    y_e1 = {k: np.array([sc[i][k] for i in keep]) for k in KEYS}

    e4 = json.loads(E4.read_text())
    held = [i for i in range(len(e4)) if i >= 40]
    cats = [e4[i]["target_emotion"] for i in held]
    names = sorted(set(cats))
    Yc = {c: np.array([1.0 if hc == c else 0.0 for hc in cats]) for c in names}
    zheld = np.load(HELD_CACHE, allow_pickle=True)

    rep: dict[str, Any] = {
        "env": {"generated_utc": datetime.now(timezone.utc).isoformat(),
                "script": Path(__file__).name,
                "script_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()).hexdigest(),
                "hostname": platform.node(), "gpu_used": False,
                "intervention_run": False, "seeds": a.seeds,
                "threshold_pct": THRESH_PCT, "min_cells": MIN_CELLS,
                "prereg": "37.2 (seed stability of C3), 38.1 (single 5% threshold)",
                "note": ("activations are fixed, so the human directions are fixed; "
                         "what varies with seed is the ICA solution and hence the "
                         "axes, which is what C3 depends on")},
        "seeds": {}}

    # human subspaces are seed-independent: build once per layer
    human: dict[int, dict[str, Any]] = {}
    for L in LAYERS:
        X1 = np.load(ACT / f"layer{L:02d}_seed0042.npz",
                     allow_pickle=True)["arr"].astype(np.float32)[keep]
        d2 = {k: p2_ridge_std(X1, y_e1[k]) for k in KEYS}
        Q2, _ = np.linalg.qr(np.stack([d2[k] for k in KEYS], axis=1))
        Xh = zheld[f"layer{L:02d}"].astype(np.float32)
        d3 = {c: p2_ridge_std(Xh, Yc[c]) for c in names}
        Q3, _ = np.linalg.qr(np.stack([d3[c] for c in names], axis=1))
        human[L] = {"Q_S2": Q2, "Q_S3": Q3,
                    "chance_S2_pct": 100.0 * Q2.shape[1] / X1.shape[1],
                    "chance_S3_pct": 100.0 * Q3.shape[1] / X1.shape[1]}
        print(f"layer {L}: S2 rank={Q2.shape[1]} (chance "
              f"{human[L]['chance_S2_pct']:.3f}%) "
              f"S3 rank={Q3.shape[1]} (chance {human[L]['chance_S3_pct']:.3f}%)",
              flush=True)

    for sd in a.seeds:
        print(f"\n===== seed {sd} =====", flush=True)
        per_layer: dict[str, Any] = {}
        s2_cells: list[float] = []
        s3_cells: list[float] = []
        for L in LAYERS:
            npz = ACT / f"layer{L:02d}_seed0042.npz"
            acts = np.load(npz, allow_pickle=True)["arr"].astype(np.float32)
            bk, comps, sil, _evr = run_ica_sweep(acts, k_range=K_RANGE, seed=sd)
            comps = np.asarray(comps, dtype=np.float32)
            rp = compute_split_reproducibility(npz, comps, seed=sd)
            order = np.argsort(-rp)
            top = comps[order][:N_AXES].astype(np.float64)
            s2 = [inside_pct(top[i], human[L]["Q_S2"]) for i in range(N_AXES)]
            s3 = [inside_pct(top[i], human[L]["Q_S3"]) for i in range(N_AXES)]
            s2_cells += s2
            s3_cells += s3
            per_layer[str(L)] = {
                "ica_k": int(bk),
                "repro_top3": [round(float(rp[order][i]), 4) for i in range(N_AXES)],
                "inside_pct_S2": [round(x, 4) for x in s2],
                "inside_pct_S3": [round(x, 4) for x in s3]}
            print(f"  L{L:<3} K={bk} repro={per_layer[str(L)]['repro_top3']} "
                  f"S2 inside%={[round(x,3) for x in s2]} "
                  f"S3 inside%={[round(x,3) for x in s3]}", flush=True)
        n2 = sum(1 for x in s2_cells if x < THRESH_PCT)
        n3 = sum(1 for x in s3_cells if x < THRESH_PCT)
        rep["seeds"][str(sd)] = {
            "layers": per_layer,
            "S2_cells_under_threshold": n2, "S2_total": len(s2_cells),
            "S3_cells_under_threshold": n3, "S3_total": len(s3_cells),
            "C3_primary_pass": bool(n2 >= MIN_CELLS),
            "C3_secondary_pass": bool(n3 >= MIN_CELLS),
            "S2_max_pct": round(max(s2_cells), 4),
            "S3_max_pct": round(max(s3_cells), 4)}
        print(f"  seed {sd}: S2 {n2}/{len(s2_cells)} under {THRESH_PCT}% "
              f"(max {max(s2_cells):.3f}%) -> pass={n2 >= MIN_CELLS} | "
              f"S3 {n3}/{len(s3_cells)} (max {max(s3_cells):.3f}%) -> "
              f"pass={n3 >= MIN_CELLS}", flush=True)

    allp2 = [rep["seeds"][str(s)]["C3_primary_pass"] for s in a.seeds]
    allp3 = [rep["seeds"][str(s)]["C3_secondary_pass"] for s in a.seeds]
    rep["summary"] = {
        "C3_primary_pass_all_seeds": bool(all(allp2)),
        "C3_secondary_pass_all_seeds": bool(all(allp3)),
        "S2_max_over_seeds": round(max(rep["seeds"][str(s)]["S2_max_pct"]
                                       for s in a.seeds), 4),
        "S3_max_over_seeds": round(max(rep["seeds"][str(s)]["S3_max_pct"]
                                       for s in a.seeds), 4),
        "per_seed_primary": dict(zip(map(str, a.seeds), allp2)),
        "per_seed_secondary": dict(zip(map(str, a.seeds), allp3))}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    print(f"\nC3 primary passes all seeds : {all(allp2)}")
    print(f"C3 secondary passes all seeds: {all(allp3)}")
    print(f"max inside% over seeds: S2={rep['summary']['S2_max_over_seeds']} "
          f"S3={rep['summary']['S3_max_over_seeds']}")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
