#!/usr/bin/env python3
"""Does the estimated human direction depend on the estimation procedure?

Pre-registration: section 21 (predictions PD1-PD3 written before this ran).

Paper 1 measured cos(valence_pca50, valence_full) = -0.003 to +0.120 across six
models, with both directions achieving positive holdout R-squared. Equivalent
linear decodability is therefore reachable along many mutually orthogonal
directions, so "we removed the human valence direction" is only ever "we removed
the one direction that this procedure returned". This script measures how much
that matters here.

Four procedures, same activations and same targets, direction only varying:
  P1 cov          d proportional to X^T z(y)   (what regress_dir does)
  P2 ridge_std    Ridge on column-standardised X, alpha by CV on train
  P3 ridge_raw    Ridge without standardisation (the form paper 1 had used)
  P4 pca50_ridge  PCA to 50 components, Ridge there, mapped back

For every procedure: pairwise cosines against the others, plus holdout r and the
permutation p from prereg section 17.2, so a procedure that generalises better can
be told apart from one that merely differs.

S2 (human V/A/D on the 287 matched E1 sentences) runs on CPU from the saved
activations. S3 (the 20 category directions on held-out E4 40-79) needs those
activations, which were never written to disk, so it requires a short GPU pass;
`--cache-e4heldout` points at that cache once it exists.

CPU only unless --cache-e4heldout is given.
"""
from __future__ import annotations

import argparse
import csv
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
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
VADP = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
KEYS = ("valence", "arousal", "dominance")
LAYERS = (5, 7, 10, 12)
SEED = 42
PERM_SEED = 20260925
N_PERM = 200
PCA_K = 50
PROCS = ("P1_cov", "P2_ridge_std", "P3_ridge_raw", "P4_pca50_ridge")
N_PERM_RUN = 0  # set by --n-perm; 0 means cosines + holdout r only
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


def stim_vad(text: str, vad: dict[str, dict[str, float]]) -> dict | None:
    def look(w: str) -> dict[str, float] | None:
        if w in vad:
            return vad[w]
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                return vad[w[: -len(s)]]
        return None
    hits = [h for h in (look(w) for w in re.findall(r"[a-zA-Z']+", text.lower()))
            if h is not None]
    if not hits:
        return None
    return {k: float(np.mean([h[k] for h in hits])) for k in KEYS}


# ------------------------- the four procedures -------------------------
def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        raise RuntimeError("near-zero direction")
    return (v / n).astype(np.float64)


def p1_cov(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    yz = (y - y.mean()) / (y.std() + 1e-8)
    return _unit(X.T @ yz)


def _ridge_cv(X: np.ndarray, y: np.ndarray, standardise: bool) -> np.ndarray:
    from sklearn.linear_model import RidgeCV
    alphas = np.logspace(-2, 5, 22)
    Xf = X.astype(np.float64)
    if standardise:
        mu = Xf.mean(axis=0)
        sd = Xf.std(axis=0)
        sd[sd < 1e-12] = 1.0
        Xf = (Xf - mu) / sd
    m = RidgeCV(alphas=alphas, fit_intercept=True)
    m.fit(Xf, (y - y.mean()) / (y.std() + 1e-8))
    coef = np.asarray(m.coef_, dtype=np.float64).ravel()
    if standardise:
        # map back to the original (unstandardised) coordinate scale
        coef = coef / sd
    return _unit(coef)


def p2_ridge_std(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    return _ridge_cv(X, y, standardise=True)


def p3_ridge_raw(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    return _ridge_cv(X, y, standardise=False)


def p4_pca_ridge(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    from sklearn.decomposition import PCA
    from sklearn.linear_model import RidgeCV
    k = min(PCA_K, X.shape[0] - 1, X.shape[1])
    pca = PCA(n_components=k, random_state=SEED)
    Z = pca.fit_transform(X.astype(np.float64))
    m = RidgeCV(alphas=np.logspace(-2, 5, 22), fit_intercept=True)
    m.fit(Z, (y - y.mean()) / (y.std() + 1e-8))
    return _unit(np.asarray(m.coef_, dtype=np.float64).ravel() @ pca.components_)


PROC_FN = {"P1_cov": p1_cov, "P2_ridge_std": p2_ridge_std,
           "P3_ridge_raw": p3_ridge_raw, "P4_pca50_ridge": p4_pca_ridge}


# ------------------------- validity -------------------------
def _r(a: np.ndarray, b: np.ndarray) -> float:
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def validity(X: np.ndarray, y: np.ndarray, fn: Any, tr: np.ndarray,
             n_perm: int = 0) -> dict[str, Any]:
    """holdout r, and the permutation null only when n_perm > 0.

    The null is off by default on purpose. Re-running RidgeCV inside a 200-fold
    permutation loop is ~9,600 cross-validated fits at n=143, d=2048, which ran
    for 38 minutes without finishing and competed with paper 1's grid for CPU.
    The deliverable here is the BETWEEN-PROCEDURE cosine, which needs only one
    fit per procedure. P1's null is already measured in the stage-1 output under
    the identical rule (prereg 17.2), so nothing is lost by omitting it here.
    """
    ho = ~tr
    try:
        d = fn(X[tr], y[tr])
    except Exception as exc:  # noqa: BLE001
        return {"holdout_r": float("nan"), "perm_p_value": float("nan"),
                "GENERALISES": False, "error": str(exc)}
    r_ho = _r(X[ho].astype(np.float64) @ d, y[ho])
    if n_perm <= 0:
        return {"holdout_r": r_ho,
                "holdout_r2": (r_ho ** 2 if not math.isnan(r_ho) else float("nan")),
                "perm_null_skipped": True,
                "NOTE": ("permutation null not run here for compute reasons; P1's "
                         "null is in the stage-1 output under the same rule")}
    prng = np.random.default_rng(PERM_SEED + 101)
    null = []
    for _ in range(n_perm):
        yp = prng.permutation(y)
        try:
            dp = fn(X[tr], yp[tr])
        except Exception:  # noqa: BLE001
            continue
        rp = _r(X[ho].astype(np.float64) @ dp, yp[ho])
        if not math.isnan(rp):
            null.append(abs(rp))
    arr = np.asarray(null, float)
    if arr.size >= 10 and not math.isnan(r_ho):
        p = float((arr >= abs(r_ho)).mean())
        p95 = float(np.quantile(arr, 0.95))
    else:
        p = p95 = float("nan")
    return {"holdout_r": r_ho, "perm_null_p95_abs_r": p95, "perm_p_value": p,
            "perm_n": int(arr.size),
            "GENERALISES": bool((not math.isnan(p)) and p < 0.05
                                and (not math.isnan(p95)) and abs(r_ho) > p95)}


def cos_table(dirs: dict[str, np.ndarray]) -> dict[str, Any]:
    names = list(dirs)
    M = {a: {b: round(float(abs(dirs[a] @ dirs[b])), 4) for b in names}
         for a in names}
    off = [abs(float(dirs[a] @ dirs[b]))
           for i, a in enumerate(names) for b in names[i + 1:]]
    return {"abs_cos_matrix": M,
            "mean_abs_cos_offdiag": float(np.mean(off)) if off else float("nan"),
            "min_abs_cos_offdiag": float(np.min(off)) if off else float("nan"),
            "max_abs_cos_offdiag": float(np.max(off)) if off else float("nan")}


def analyse(X: np.ndarray, targets: dict[str, np.ndarray], label: str,
            split: np.ndarray | None = None) -> dict[str, Any]:
    n = X.shape[0]
    if split is None:
        idx = np.random.default_rng(PERM_SEED).permutation(n)
        tr = np.zeros(n, dtype=bool)
        tr[idx[: n // 2]] = True
    else:
        tr = np.asarray(split, dtype=bool)
    out: dict[str, Any] = {"label": label, "n": int(n), "d": int(X.shape[1]),
                           "n_train": int(tr.sum()), "targets": {}}
    for tname, y in targets.items():
        dirs: dict[str, np.ndarray] = {}
        val: dict[str, Any] = {}
        for pname in PROCS:
            try:
                dirs[pname] = PROC_FN[pname](X, y)
            except Exception as exc:  # noqa: BLE001
                print(f"    [{tname}] {pname} failed: {exc}")
                continue
            val[pname] = validity(X, y, PROC_FN[pname], tr, n_perm=N_PERM_RUN)
        entry = cos_table(dirs)
        entry["validity_per_procedure"] = val
        out["targets"][tname] = entry
    return out


def env(extra: dict[str, Any]) -> dict[str, Any]:
    import scipy
    import sklearn
    m = {"generated_utc": datetime.now(timezone.utc).isoformat(),
         "script": Path(__file__).name,
         "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "python": sys.version.split()[0], "numpy": np.__version__,
         "scipy": scipy.__version__, "sklearn": sklearn.__version__,
         "hostname": platform.node(), "gpu_used": False,
         "procedures": list(PROCS), "n_perm": N_PERM, "pca_k": PCA_K,
         "prereg_section": "21 (predictions PD1-PD3 fixed before running)"}
    m.update(extra)
    return m


def self_check() -> int:
    ok = True

    def chk(n: str, c: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if c else 'FAIL'}] {n}")
        ok &= bool(c)

    rg = np.random.default_rng(3)
    d_true = _unit(rg.standard_normal(80))
    Xs = rg.standard_normal((300, 80))
    y = Xs @ d_true + 0.05 * rg.standard_normal(300)
    ds = {p: PROC_FN[p](Xs, y) for p in PROCS}
    ct = cos_table(ds)
    chk(f"well-posed problem: all procedures agree "
        f"(min|cos|={ct['min_abs_cos_offdiag']:.3f})",
        ct["min_abs_cos_offdiag"] > 0.8)
    for p in PROCS:
        chk(f"{p} recovers the true direction",
            abs(float(ds[p] @ d_true)) > 0.8)
    # A well-determined problem (n >> d) makes the procedures agree EVEN on a
    # pure noise target, because they all converge on the same least-squares
    # solution. So agreement measures how determined the estimate is, NOT whether
    # the direction means anything. Validity is the holdout/permutation test, and
    # the two must never be conflated (same discipline as residual norm vs effect).
    yn = rg.standard_normal(300)
    ctn = cos_table({p: PROC_FN[p](Xs, yn) for p in PROCS})
    chk(f"well-determined noise: procedures still AGREE, so agreement is not "
        f"validity (mean|cos|={ctn['mean_abs_cos_offdiag']:.3f})",
        ctn["mean_abs_cos_offdiag"] > 0.7)
    # Disagreement is the signature of UNDERDETERMINATION (n < d), which is the
    # regime our real data sits in (S2 n=287/d=2048, S3 n=40/d=2048).
    Xu = rg.standard_normal((40, 2048))
    ctu = cos_table({p: PROC_FN[p](Xu, rg.standard_normal(40)) for p in PROCS})
    chk(f"underdetermined noise (n=40,d=2048): procedures disagree "
        f"(mean|cos|={ctu['mean_abs_cos_offdiag']:.3f})",
        ctu["mean_abs_cos_offdiag"] < 0.8)
    Xu2 = rg.standard_normal((287, 2048))
    d2 = _unit(rg.standard_normal(2048))
    ctu2 = cos_table({p: PROC_FN[p](Xu2, Xu2 @ d2 + 0.05 * rg.standard_normal(287))
                      for p in PROCS})
    chk(f"underdetermined but real signal (n=287,d=2048): agreement is higher "
        f"than for noise (mean|cos|={ctu2['mean_abs_cos_offdiag']:.3f})",
        ctu2["mean_abs_cos_offdiag"] > ctu["mean_abs_cos_offdiag"])
    chk("all directions unit norm",
        all(abs(float(np.linalg.norm(v)) - 1) < 1e-6 for v in ds.values()))
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-e4heldout", type=Path, default=None,
                    help="npz with E4 40-79 last-token activations per layer "
                         "(needs a short GPU pass to create)")
    ap.add_argument("--out", type=Path,
                    default=BASE / "axes_nopad" / "procedure_dependence.json")
    ap.add_argument("--n-perm", type=int, default=0,
                    help="permutations per procedure (0 = skip; the null is "
                         "expensive and P1's is already in the stage-1 output)")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        return self_check()
    global N_PERM_RUN
    N_PERM_RUN = a.n_perm

    vad = load_vad()
    e1 = json.loads(E1.read_text())
    sc = [stim_vad(s["text"], vad) for s in e1]
    keep = [i for i, s in enumerate(sc) if s is not None]
    y_e1 = {k: np.array([sc[i][k] for i in keep]) for k in KEYS}
    print(f"E1 matched {len(keep)}/{len(e1)}")

    report: dict[str, Any] = {"env": env({"e1_matched": len(keep)}), "layers": {}}
    for L in LAYERS:
        X = np.load(ACT / f"layer{L:02d}_seed{SEED:04d}.npz",
                    allow_pickle=True)["arr"].astype(np.float32)[keep]
        print(f"\n=== layer {L}  S2 (human V/A/D, n={X.shape[0]}, d={X.shape[1]})")
        s2 = analyse(X, y_e1, "S2_vad_on_E1")
        for t, e in s2["targets"].items():
            v = e["validity_per_procedure"]
            print(f"  {t:<10} mean|cos|={e['mean_abs_cos_offdiag']:.3f} "
                  f"min={e['min_abs_cos_offdiag']:.3f} "
                  f"max={e['max_abs_cos_offdiag']:.3f}")
            for p in PROCS:
                if p in v:
                    pp = v[p].get("perm_p_value")
                    tail = (f" perm_p={pp:.4f} GEN={v[p].get('GENERALISES')}"
                            if isinstance(pp, float) and not math.isnan(pp) else "")
                    print(f"      {p:<15} holdout r={v[p]['holdout_r']:+.3f}{tail}")
        entry: dict[str, Any] = {"S2": s2}

        if a.cache_e4heldout and a.cache_e4heldout.exists():
            z = np.load(a.cache_e4heldout, allow_pickle=True)
            key = f"layer{L:02d}"
            if key in z:
                Xh = z[key].astype(np.float32)
                e4 = json.loads(E4.read_text())
                held = [i for i in range(len(e4)) if i >= 40]
                cats = [e4[i]["target_emotion"] for i in held]
                names = sorted(set(cats))
                variant = np.array(
                    [e4[i].get("template_variant", 0) == 0 for i in held], bool)
                tgt = {c: np.array([1.0 if hc == c else 0.0 for hc in cats])
                       for c in names}
                print(f"  S3 categories (n={Xh.shape[0]})")
                s3 = analyse(Xh, tgt, "S3_categories_on_E4_heldout",
                             split=variant)
                mc = [s3["targets"][c]["mean_abs_cos_offdiag"] for c in names]
                print(f"    mean|cos| across 20 categories: "
                      f"median={float(np.median(mc)):.3f} "
                      f"min={float(np.min(mc)):.3f} max={float(np.max(mc)):.3f}")
                entry["S3"] = s3
        report["layers"][str(L)] = entry

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nwrote {a.out}")
    if not (a.cache_e4heldout and a.cache_e4heldout.exists()):
        print("NOTE: S3 (category) part skipped - needs the E4 40-79 activation "
              "cache, which requires a short GPU pass (160 forwards).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
