"""Exploratory, not pre-registered: is the same emotion category steerable across models,
and does what is easy to decode coincide with what is easy to steer?

Reads the stored Gate I measurements (fifty floor draws) and the per-category readout quality.
No GPU is needed and no number is entered by hand.
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

import numpy as np
import os as _os

B = 4000
ROOT = Path(_os.environ.get("NA_DATA", "data"))
C3 = ROOT / "stageC3"
RO = ROOT / "roauc"
SHORT = {"Llama-3.2-1B-Instruct": "Llama-3.2-1B", "Llama-3.1-8B-Instruct": "Llama-3.1-8B",
         "OLMo-2-1124-7B-Instruct": "OLMo-2-7B", "OLMo-2-1124-13B-Instruct": "OLMo-2-13B",
         "gemma-2-2b-it": "Gemma-2-2B", "gemma-2-9b-it": "Gemma-2-9B",
         "Ministral-8B-Instruct-2410": "Ministral-8B",
         "Mistral-Nemo-Instruct-2407": "Mistral-Nemo-12B",
         "Phi-3-medium-4k-instruct": "Phi-3-medium"}


def per_target(tsel, ttest, A, rng):
    """Standardised excess of every target, and whether it clears its own matched floor."""
    C = tsel.shape[1]
    val = np.array([ttest[int(np.argmax(tsel[:, e])), e] for e in range(C)])
    K, M, _, _ = A.shape
    null = np.zeros((B, C))
    for e in range(C):
        pick = rng.integers(0, M, size=(B, K))
        fs = A[np.arange(K)[None, :], pick, 0, e]
        fh = A[np.arange(K)[None, :], pick, 1, e]
        null[:, e] = fh[np.arange(B), np.argmax(fs, axis=1)]
    h1 = null[: B // 2]
    thr = np.quantile(h1, 0.95, axis=0)
    mu, sd = h1.mean(0), h1.std(0) + 1e-12
    return (val - mu) / sd, val > thr


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def main(readout="single"):
    exc, hit, auc, classes = {}, {}, {}, None
    for mf in sorted(C3.glob("meta_*_m50.json")):
        meta = json.loads(mf.read_text())
        name = meta["model"].split("/")[-1]
        m = SHORT.get(name, name)
        classes = meta["classes"]
        z = np.load(C3 / mf.name.replace("meta_", "raw_").replace(".json", ".npz"))
        k = f"emotion|{readout}"
        e, h = per_target(z[f"{k}|tgt_sel"], z[f"{k}|tgt_test"], z[f"{k}|F5"],
                          np.random.default_rng(777))
        exc[m], hit[m] = e, h
        rf = RO / f"roauc_{mf.name[5:].replace('_m50.json', '')}.json"
        if rf.exists():
            d = json.loads(rf.read_text())
            auc[m] = np.array([d["A"][c] for c in classes])
    models = sorted(exc)
    E = np.array([exc[m] for m in models])          # 9 x 13
    H = np.array([hit[m] for m in models])

    print(f"=== readout {readout} / {len(models)} models x {len(classes)} categories ===")
    print(f"{'category':12s} {'models above floor':>12s} {'median excess SD':>12s} {'median readout AUC':>16s}")
    order = np.argsort(-H.sum(0))
    for i in order:
        a = np.median([auc[m][i] for m in models if m in auc])
        print(f"{classes[i]:12s} {str(int(H[:, i].sum()))+'/'+str(len(models)):>12s} "
              f"{np.median(E[:, i]):+12.2f} {a:16.3f}")
    print(f"\nall categories: above floor {int(H.sum())}/{H.size} cells "
          f"({100*H.sum()/H.size:.0f}%) / median excess SD {np.median(E):+.2f}")
    print(f"range of models above floor across categories {int(H.sum(0).min())}〜{int(H.sum(0).max())}/{len(models)}")

    rs = [spearman(auc[m], exc[m]) for m in models if m in auc]
    print(f"\n=== readout discriminability against steerability (13 categories, Spearman per model)===")
    for m, r in zip([m for m in models if m in auc], rs):
        print(f"{m:18s} rho = {r:+.3f}")
    print(f"median {np.median(rs):+.3f} / range {min(rs):+.3f}〜{max(rs):+.3f} / "
          f"positive sign {sum(r > 0 for r in rs)}/{len(rs)} models")
    json.dump({"readout": readout, "models": models, "classes": classes,
               "hits_per_class": H.sum(0).tolist(),
               "excess_median_per_class": [round(float(x), 3) for x in np.median(E, 0)],
               "auc_median_per_class": [round(float(np.median([auc[m][i] for m in models if m in auc])), 4)
                                        for i in range(len(classes))],
               "spearman_per_model": {m: round(r, 4) for m, r in zip([m for m in models if m in auc], rs)}},
              open(ROOT / "category_wise" / f"catwise_{readout}.json", "w"),
              indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "single"))
