"""Amendment 91 CJ5: does the F5 matching hold on a covariance estimated from unseen rows?

F5 preserves lambda_i a_i^2 term by term on the empirical covariance of the fitting rows. Where
the hidden dimension exceeds the sample, that covariance has a null space, and the component of
a direction that lives there is treated as carrying no variance. On unseen data it may. So the
ratio is recomputed against a covariance estimated from rows the fit never saw, and the share of
each direction's norm that lies in the fitted null space is reported. CPU only; no judgement.
"""
from __future__ import annotations

import argparse, csv, json
from pathlib import Path

import numpy as np

import os as _os
_ROOT = _os.environ.get("NA_ROOT", _os.path.join(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__))), "work"))


CACHE = Path(_ROOT + "/results/plan_b/audit_stageA")
RES = Path(_ROOT + "/results/plan_b/vmatch")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261007
N_TRAIN, N_INNER, N_SEL, N_TEST = 2600, 650, 32, 32
LAMBDAS = [1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7]
M_F5 = 20
APPRAISALS = ["suddenness", "familiarity", "predict_event", "pleasantness", "unpleasantness",
              "goal_relevance", "chance_responsblt", "self_responsblt", "other_responsblt",
              "predict_conseq", "goal_support", "urgency", "self_control", "other_control",
              "chance_control", "accept_conseq", "standards", "social_norms",
              "attention", "not_consider", "effort"]


def unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    texts, emo, app = [], [], []
    for r in csv.DictReader(open(DATA, encoding="utf-8"), delimiter="\t"):
        t = (r.get("generated_text") or "").strip()
        if not t:
            continue
        try:
            vals = [float(r[k]) for k in APPRAISALS]
        except (KeyError, ValueError):
            continue
        texts.append(t); emo.append((r.get("emotion") or "").strip()); app.append(vals)
    emo = np.asarray(emo); app = np.asarray(app); n = len(texts)
    classes = sorted(set(emo))

    # the same partition the measurement used
    perm = rng.permutation(n)
    i_fit = perm[:N_TRAIN]; i_inner = perm[N_TRAIN:N_TRAIN + N_INNER]
    i_train = np.concatenate([i_fit, i_inner])
    i_unseen = perm[N_TRAIN + N_INNER:]

    X = np.load(CACHE / f"H_{a.tag}.npy").astype(np.float64)
    mu, sd = X[i_train].mean(0), X[i_train].std(0) + 1e-8
    Xs = (X - mu) / sd
    d = Xs.shape[1]

    Xc = Xs[i_train] - Xs[i_train].mean(0)
    _, Sv, Vt = np.linalg.svd(Xc, full_matrices=False)
    lam_fit = (Sv ** 2) / (len(i_train) - 1)
    Q = Vt.astype(np.float32)
    rank = int((Sv > 1e-10 * Sv[0]).sum())

    Xu = Xs[i_unseen] - Xs[i_unseen].mean(0)
    print(f"tag={a.tag} d={d} eigenbasis {Q.shape[0]} effective rank {rank} "
          f"unseen rows {len(i_unseen)}", flush=True)

    def var_fit(v):
        c = (Q @ v.astype(np.float32)).astype(np.float64)
        return float((lam_fit * c ** 2).sum())

    def var_unseen(v):
        z = Xu @ v
        return float((z ** 2).sum() / (len(i_unseen) - 1))

    def null_share(v):
        v32 = v.astype(np.float32)
        res = v32 - Q.T @ (Q @ v32)
        return float((res ** 2).sum() / max((v32 ** 2).sum(), 1e-30))

    def floor_F5(v):
        v32 = v.astype(np.float32)
        c = Q @ v32
        res = v32 - Q.T @ c
        rn = float(np.linalg.norm(res))
        c = c * rng.choice(np.float32([-1.0, 1.0]), size=len(c))
        out = Q.T @ c
        if rn > 1e-8:
            r = rng.standard_normal(d).astype(np.float32)
            r = r - Q.T @ (Q @ r)
            out = out + r * (rn / (float(np.linalg.norm(r)) + 1e-12))
        return out.astype(np.float64)

    def ridge(Xf, Xi, yf, yi):
        U, S, Vh = np.linalg.svd(Xf, full_matrices=False)
        ym = yf.mean(); best, bw = -np.inf, None
        for lm in LAMBDAS:
            w = Vh.T @ ((S / (S ** 2 + lm)) * (U.T @ (yf - ym)))
            ss = 1.0 - float(((yi - ym - Xi @ w) ** 2).sum()) / max(
                float(((yi - yi.mean()) ** 2).sum()), 1e-12)
            if ss > best:
                best, bw = ss, w
        return unit(bw)

    Xf, Xi = Xs[i_fit], Xs[i_inner]
    U, S2, Vh = np.linalg.svd(Xf, full_matrices=False)

    def fit(y):
        ym = y[i_fit].mean(); best, bw = -np.inf, None
        for lm in LAMBDAS:
            w = Vh.T @ ((S2 / (S2 ** 2 + lm)) * (U.T @ (y[i_fit] - ym)))
            ss = 1.0 - float(((y[i_inner] - ym - Xi @ w) ** 2).sum()) / max(
                float(((y[i_inner] - y[i_inner].mean()) ** 2).sum()), 1e-12)
            if ss > best:
                best, bw = ss, w
        return unit(bw)

    fams = {"emotion": np.stack([fit((emo == c).astype(np.float64)) for c in classes]),
            "appraisal_raw": np.stack([fit(app[:, j]) for j in range(len(APPRAISALS))])}

    out = {"tag": a.tag, "d": d, "rank": rank, "n_unseen": int(len(i_unseen)),
           "m_f5": M_F5, "families": {}}
    for fn, M in fams.items():
        rf, ru, ns = [], [], []
        for v in M:
            v = unit(v)
            ns.append(null_share(v))
            tf, tu = var_fit(v), var_unseen(v)
            for _ in range(M_F5):
                f = floor_F5(v)
                rf.append(var_fit(f) / max(tf, 1e-30))
                ru.append(var_unseen(f) / max(tu, 1e-30))
        rf, ru, ns = np.asarray(rf), np.asarray(ru), np.asarray(ns)
        out["families"][fn] = {
            "fit_ratio_median": round(float(np.median(rf)), 6),
            "fit_ratio_maxdev": round(float(np.max(np.abs(rf - 1))), 8),
            "unseen_ratio_median": round(float(np.median(ru)), 4),
            "unseen_ratio_q05": round(float(np.quantile(ru, 0.05)), 4),
            "unseen_ratio_q95": round(float(np.quantile(ru, 0.95)), 4),
            "unseen_ratio_maxdev": round(float(np.max(np.abs(ru - 1))), 4),
            "null_share_median": round(float(np.median(ns)), 6),
            "null_share_max": round(float(np.max(ns)), 6),
        }
        r = out["families"][fn]
        print(f"  {fn:14s} fit ratio {r['fit_ratio_median']:.6f}"
              f"(max deviation {r['fit_ratio_maxdev']:.2e}) | "
              f"unseen ratio median {r['unseen_ratio_median']:.4f} "
              f"[{r['unseen_ratio_q05']:.4f}, {r['unseen_ratio_q95']:.4f}] | "
              f"null-space share median {r['null_share_median']:.6f} max {r['null_share_max']:.6f}",
              flush=True)
    (RES / f"vmatch_{a.tag}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
