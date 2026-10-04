"""Refit the appraisal probes with a selected ridge penalty.

The first pass fixed lambda = 1, which against a 4096-dimensional standardised design with
5280 training rows is effectively no regularisation: held-out R^2 came out between -0.9 and
-2.1, i.e. worse than predicting the mean. That is a defect in our probe, not a property of
the models - Tak et al. report appraisals as linearly detectable, so a replication that
cannot fit at all has not reproduced their procedure.

Activations were cached by stage A, so this refits from disk without re-running any model.
Lambda is chosen on an inner split of the training rows only, never on the test rows.
"""
from __future__ import annotations

import argparse, json
from pathlib import Path

import numpy as np

OUT = Path("/path/to/work/results/plan_b/audit_stageA")
SEED = 20261004
LAMBDAS = [1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7]
APPRAISALS = ["suddenness", "familiarity", "predict_event", "pleasantness", "unpleasantness",
              "goal_relevance", "chance_responsblt", "self_responsblt", "other_responsblt",
              "predict_conseq", "goal_support", "urgency", "self_control", "other_control",
              "chance_control", "accept_conseq", "standards", "social_norms",
              "attention", "not_consider", "effort"]


def fit_eval(U, S, Vt, ytr, Xva, yva, lam):
    """Ridge from a cached SVD of the standardised training design."""
    d = S / (S ** 2 + lam)
    w = Vt.T @ (d * (U.T @ ytr))
    pred = Xva @ w
    ss_res = float(((yva - pred) ** 2).sum())
    ss_tot = float(((yva - yva.mean()) ** 2).sum())
    return w, 1.0 - ss_res / max(ss_tot, 1e-12)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(Path("/path/to/work/data/raw/crowd_envent/"
                                              "corpus/crowd-enVent_generation.tsv")))
    a = ap.parse_args()
    import csv
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8"), delimiter="\t"))
    Y, keep = [], []
    for i, r in enumerate(rows):
        if not (r.get("generated_text") or "").strip():
            continue
        try:
            Y.append([float(r[k]) for k in APPRAISALS])
        except (KeyError, ValueError):
            continue
        keep.append(i)
    Y = np.asarray(Y, dtype=np.float64)
    n = len(Y)
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(n)
    ntr = int(0.8 * n)
    tr_all, te = perm[:ntr], perm[ntr:]
    nva = int(0.2 * len(tr_all))
    va, tr = tr_all[:nva], tr_all[nva:]
    print(f"刺激 {n} / 学習 {len(tr)} 検証 {len(va)} 評価 {len(te)}", flush=True)

    res = {}
    for hp in sorted(OUT.glob("H_*_L*.npy")):
        tag = hp.stem[2:]
        X = np.load(hp).astype(np.float64)
        if X.shape[0] != n:
            print(f"skip {tag}: 行数 {X.shape[0]} != {n}"); continue
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
        Xs = (X - mu) / sd
        U, S, Vt = np.linalg.svd(Xs[tr], full_matrices=False)
        entry, V = {}, []
        for k, name in enumerate(APPRAISALS):
            ym = Y[tr, k].mean()
            best = max(((fit_eval(U, S, Vt, Y[tr, k] - ym, Xs[va], Y[va, k] - ym, L), L)
                        for L in LAMBDAS), key=lambda t: t[0][1])
            (w, _), lam = best
            pred = Xs[te] @ w + ym
            ss_res = float(((Y[te, k] - pred) ** 2).sum())
            ss_tot = float(((Y[te, k] - Y[te, k].mean()) ** 2).sum())
            r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
            entry[name] = {"r2_test": round(r2, 4), "lambda": lam}
            V.append(w / (np.linalg.norm(w) + 1e-12))
        np.save(OUT / f"Vfit_{tag}.npy", np.stack(V))
        vals = [v["r2_test"] for v in entry.values()]
        res[tag] = entry
        print(f"{tag}: R^2>0.1 {sum(v > 0.1 for v in vals)}/21  中央 {np.median(vals):.3f}  "
              f"最大 {max(vals):.3f} ({max(entry, key=lambda k: entry[k]['r2_test'])})", flush=True)
    (OUT / "stageA_refit.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print("=== 再当てはめ終了 ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
