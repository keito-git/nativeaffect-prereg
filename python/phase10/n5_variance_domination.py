#!/usr/bin/env python3
"""Addendum 14 N5: can JS be predicted from the projection profile alone?

Registered design (addendum 14 N5, to be run whatever prediction P's verdict is)
--------------------------------------------------------------------------------
1. per layer, draw 1,000 random directions from INSIDE the top-10 PC span
2. for each, record the 10-dim vector of projection lengths onto the top 10 PCs,
   and the JS of the intervention
3. regress JS on the projection lengths alone -- linear AND gradient boosting --
   and report the HOLDOUT R^2
4. a high R^2 is direct evidence that the direction's "meaning" contributes
   nothing to JS

Reporting is fixed in advance: R^2 per layer in a table, the value itself as the
strength of the claim, NO binary verdict from a threshold. The residuals of the
axes and of the human VAD valence direction are reported alongside.

One problem with the registered design, flagged before running
--------------------------------------------------------------
Directions drawn from inside the span all have inside_fraction = 1 by
construction. The axes do not: their inside_fraction is around 0.2-0.3. So a model
fit on the 1,000 draws and applied to an axis is EXTRAPOLATING, and the residual
does not mean "this axis behaves as the variance predicts" -- it partly measures
how badly a model extrapolates outside its training range.

`--draw coverage` therefore draws directions whose inside_fraction spans the
observed range, so the reference directions sit inside the training distribution
and the residual is interpolation. It is an addition to a registered analysis and
its numbers do not count until the coordinator approves it; `--draw in_span`
reproduces the registered design exactly and is the default.

Usage
-----
    python3 n5_variance_domination.py --self-test         # no model, no GPU
    python3 n5_variance_domination.py --layers 11 16 22 27 [--draw coverage]

The JS measurement is injected: this module never defines its own JS. The
verified-equivalent implementation is imported from the existing scripts (see
verify_js_implementations.py: nine copies, all agreeing exactly).
"""

from __future__ import annotations

import os

# Pin the BLAS/OpenMP thread count BEFORE numpy is imported. On this data shape
# (a few hundred rows, ten features) the default thread count costs more in
# oversubscription than it buys: the self-test takes 26.8 s pinned to one thread
# and exceeded 115 s unpinned, and one HistGradientBoosting fit went from 45.6 s
# to 21.0 s at n=400. A caller that has already chosen a value keeps it.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np

N_DRAWS = 1000                 # addendum 14 N5
HOLDOUT_FRAC = 0.30
SEED = 20260926


def draw_in_span(pcs: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """Uniform on the unit sphere of the top-k PC span. inside_fraction == 1."""
    c = rng.standard_normal((n, pcs.shape[0]))
    c /= np.linalg.norm(c, axis=1, keepdims=True)
    return c @ pcs


def draw_coverage(pcs: np.ndarray, n: int, rng: np.random.Generator,
                  f_lo: float, f_hi: float) -> np.ndarray:
    """Directions whose inside_fraction is spread over [f_lo, f_hi].

    d = sqrt(f) * u_in + sqrt(1-f) * u_out, with u_in inside the span and u_out in
    its orthogonal complement, so inside_fraction(d) = f exactly.
    """
    k, dim = pcs.shape
    f = rng.uniform(f_lo, f_hi, size=n)
    u_in = draw_in_span(pcs, n, rng)
    g = rng.standard_normal((n, dim))
    g -= (g @ pcs.T) @ pcs                       # project out the span
    g /= np.linalg.norm(g, axis=1, keepdims=True)
    d = np.sqrt(f)[:, None] * u_in + np.sqrt(1.0 - f)[:, None] * g
    return d / np.linalg.norm(d, axis=1, keepdims=True)


def features(dirs: np.ndarray, pcs: np.ndarray, with_norm: bool) -> np.ndarray:
    """Projection lengths onto each PC; optionally the inside_fraction as well.

    Absolute values: the registered feature is the projection LENGTH, so sign --
    which is where the direction's meaning lives -- is deliberately withheld from
    the model. That is the point of the analysis.
    """
    proj = np.abs(dirs @ pcs.T)
    if not with_norm:
        return proj
    inside = (proj ** 2).sum(axis=1, keepdims=True)
    return np.hstack([proj, inside])


def fit_and_score(X: np.ndarray, y: np.ndarray, seed: int) -> dict:
    """Holdout R^2 for a linear model and for gradient boosting."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import RidgeCV
    from sklearn.metrics import r2_score
    from sklearn.model_selection import train_test_split

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=HOLDOUT_FRAC,
                                          random_state=seed)
    out = {}
    models = {}
    for name, mk in (("linear", lambda: RidgeCV(alphas=np.logspace(-4, 4, 25))),
                     ("gradient_boosting",
                      lambda: HistGradientBoostingRegressor(random_state=seed))):
        m = mk().fit(Xtr, ytr)
        out[f"{name}_holdout_r2"] = float(r2_score(yte, m.predict(Xte)))
        out[f"{name}_insample_r2"] = float(r2_score(ytr, m.predict(Xtr)))
        models[name] = m
    # The claim N5 tests is whether the profile CAN predict JS. A weaker learner
    # failing is not evidence that it cannot, so the reported predictability is the
    # better of the two estimators. Measured on a target that is exactly linear in
    # the features, gradient boosting reaches only ~0.84 holdout R^2 at n=200 while
    # the linear model reaches 1.0000 -- reading the boosting number as the answer
    # would understate predictability and wrongly credit the direction's meaning.
    out["profile_predictability_holdout_r2"] = max(
        out["linear_holdout_r2"], out["gradient_boosting_holdout_r2"])
    out["why_the_max"] = (
        "N5 asks whether the projection profile suffices to predict JS. The better "
        "estimator answers that; the weaker one bounds nothing. Both are reported."
    )
    out["n_train"], out["n_holdout"] = int(len(ytr)), int(len(yte))
    out["y_mean"], out["y_sd"] = float(y.mean()), float(y.std())
    out["note"] = ("holdout R^2 is the reported quantity; in-sample R^2 is "
                   "included only so the gap is visible")
    return out, models


def residuals_for(refs: dict[str, np.ndarray], pcs: np.ndarray, models: dict,
                  with_norm: bool, js_of: Callable[[np.ndarray], float],
                  train_inside: np.ndarray) -> dict:
    """JS minus the model's prediction, with an out-of-distribution flag."""
    lo, hi = float(train_inside.min()), float(train_inside.max())
    out = {}
    for name, d in refs.items():
        d = d / np.linalg.norm(d)
        X = features(d[None, :], pcs, with_norm)
        inside = float((np.abs(d @ pcs.T) ** 2).sum())
        row = {"inside_fraction": inside,
               "js_measured": float(js_of(d)),
               "training_inside_fraction_range": [lo, hi],
               "outside_training_range": bool(inside < lo - 1e-9 or inside > hi + 1e-9)}
        for mname, m in models.items():
            pred = float(m.predict(X)[0])
            row[f"{mname}_predicted"] = pred
            row[f"{mname}_residual"] = row["js_measured"] - pred
        if row["outside_training_range"]:
            row["interpretation_refused"] = (
                "inside_fraction lies outside the range the model was fit on, so "
                "the residual mixes the effect of interest with extrapolation "
                "error and is not interpreted")
        out[name] = row
    return out


def analyse_layer(pcs: np.ndarray, js_of: Callable[[np.ndarray], float],
                  refs: dict[str, np.ndarray], rng: np.random.Generator,
                  draw: str, n: int = N_DRAWS) -> dict:
    with_norm = draw == "coverage"
    if draw == "in_span":
        dirs = draw_in_span(pcs, n, rng)
    elif draw == "coverage":
        ins = [float((np.abs((v / np.linalg.norm(v)) @ pcs.T) ** 2).sum())
               for v in refs.values()] or [1.0]
        lo = max(min(ins) * 0.5, 1e-3)
        dirs = draw_coverage(pcs, n, rng, lo, 1.0)
    else:
        raise ValueError(f"unknown draw mode {draw!r}")
    X = features(dirs, pcs, with_norm)
    y = np.array([js_of(d) for d in dirs], dtype=np.float64)
    scores, models = fit_and_score(X, y, SEED)
    inside = (np.abs(dirs @ pcs.T) ** 2).sum(axis=1)
    rec = {"draw_mode": draw, "n_draws": int(n),
           "features": ("projection lengths onto the top-10 PCs"
                        + (" plus inside_fraction" if with_norm else "")),
           "inside_fraction_of_draws": {"min": float(inside.min()),
                                        "max": float(inside.max()),
                                        "mean": float(inside.mean())},
           **scores,
           "references": residuals_for(refs, pcs, models, with_norm, js_of, inside),
           "no_binary_verdict": ("addendum 14 N5 fixes the reporting: the R^2 "
                                 "value itself is the strength of the claim. No "
                                 "threshold is applied.")}
    if draw == "coverage":
        rec["approval_required"] = (
            "coverage draw is an addition to the registered design; its numbers "
            "do not count until approved by the coordinator")
    return rec


def self_test() -> None:
    fails: list[str] = []

    def ck(name: str, cond: bool) -> None:
        print(f"  [{'ok' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    rng = np.random.default_rng(0)
    dim, k = 128, 10
    pcs = np.linalg.qr(rng.standard_normal((dim, k)))[0].T

    d0 = draw_in_span(pcs, 50, rng)
    ins0 = (np.abs(d0 @ pcs.T) ** 2).sum(axis=1)
    ck("in_span draws are unit vectors", np.allclose(np.linalg.norm(d0, axis=1), 1))
    ck("in_span draws have inside_fraction 1", np.allclose(ins0, 1.0, atol=1e-10))

    dc = draw_coverage(pcs, 400, rng, 0.05, 1.0)
    insc = (np.abs(dc @ pcs.T) ** 2).sum(axis=1)
    ck("coverage draws are unit vectors", np.allclose(np.linalg.norm(dc, axis=1), 1))
    ck("coverage draws span the requested inside_fraction range",
       insc.min() < 0.15 and insc.max() > 0.9)

    # JS that depends ONLY on the projection lengths -> holdout R^2 near 1
    w = rng.uniform(0.5, 2.0, size=k)

    def js_profile(d):
        return float(np.abs(d @ pcs.T) @ w)

    r = analyse_layer(pcs, js_profile, {}, np.random.default_rng(1), "in_span", n=400)
    ck("JS determined by the profile -> holdout R^2 near 1 (linear)",
       r["linear_holdout_r2"] > 0.99)
    ck("JS determined by the profile -> boosting recovers most of it",
       r["gradient_boosting_holdout_r2"] > 0.70)
    ck("boosting UNDERSTATES a target that is exactly linear in the features",
       r["gradient_boosting_holdout_r2"] < r["linear_holdout_r2"])
    ck("so the reported predictability takes the better estimator",
       abs(r["profile_predictability_holdout_r2"] - r["linear_holdout_r2"]) < 1e-12)

    # JS that depends on the SIGNS -> the profile cannot predict it
    def js_signed(d):
        c = d @ pcs.T
        return float(c @ w)                       # sign matters, |c| does not suffice

    r2 = analyse_layer(pcs, js_signed, {}, np.random.default_rng(1), "in_span", n=400)
    ck("JS determined by sign (meaning) -> holdout R^2 is low",
       r2["profile_predictability_holdout_r2"] < 0.5)
    ck("the two cases are distinguishable, so the analysis can fail",
       r["profile_predictability_holdout_r2"]
       - r2["profile_predictability_holdout_r2"] > 0.6)

    # pure noise -> holdout R^2 near or below 0 while in-sample is higher
    r3 = analyse_layer(pcs, lambda d: float(rng.standard_normal()), {},
                       np.random.default_rng(2), "in_span", n=400)
    ck("noise -> holdout R^2 at or below 0 for BOTH estimators",
       r3["profile_predictability_holdout_r2"] < 0.1)
    ck("in-sample exceeds holdout on noise, and both are reported",
       r3["gradient_boosting_insample_r2"] > r3["gradient_boosting_holdout_r2"])

    # an out-of-span reference under the registered draw must be flagged
    ref = 0.45 * pcs[0] + np.sqrt(1 - 0.45 ** 2) * np.linalg.qr(
        rng.standard_normal((dim, 1)))[0][:, 0]
    r4 = analyse_layer(pcs, js_profile, {"axis": ref}, np.random.default_rng(3),
                       "in_span", n=300)
    ck("a reference outside the training range is flagged",
       r4["references"]["axis"]["outside_training_range"])
    ck("and its residual is explicitly not interpreted",
       "interpretation_refused" in r4["references"]["axis"])

    r5 = analyse_layer(pcs, js_profile, {"axis": ref}, np.random.default_rng(3),
                       "coverage", n=400)
    ck("the coverage draw brings it inside the training range",
       not r5["references"]["axis"]["outside_training_range"])
    ck("coverage is marked as needing approval", "approval_required" in r5)
    ck("no threshold verdict is emitted in either mode",
       "no_binary_verdict" in r4 and "no_binary_verdict" in r5
       and not any("pass" in str(v).lower() for v in (r4.get("verdict"),
                                                      r5.get("verdict"))))

    print(f"\nself-test: {len(fails)} failure(s)")
    if fails:
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", type=int, nargs="+", default=[11, 16, 22, 27])
    ap.add_argument("--draw", choices=("in_span", "coverage"), default="in_span")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    print("self-test:")
    self_test()
    if a.self_test:
        return 0

    raise SystemExit(
        "The JS measurement adapter is not wired yet. It must import the verified "
        "JS implementation and the intervention path from the existing scripts "
        "rather than define new ones, and it needs the GPU. Not started without "
        "the coordinator's go-ahead.")


if __name__ == "__main__":
    raise SystemExit(main())
