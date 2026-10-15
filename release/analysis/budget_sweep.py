"""Gate I under two intervention budgets, measured on one and the same set of activations.

Amendment 99 CR3 asked whether the conclusion at Gate I depends on the budget J*.
Amendment 104 records that the J*=0.02 half was lost and re-measured; both halves here
come from the rebuilt caches, so the comparison is internal and no published value is joined.
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

import numpy as np

B = 4000
DATA = Path(__file__).resolve().parent / "data"
SHORT = {"Llama-3.2-1B-Instruct": "Llama-3.2-1B", "Llama-3.1-8B-Instruct": "Llama-3.1-8B",
         "OLMo-2-1124-7B-Instruct": "OLMo-2-7B", "OLMo-2-1124-13B-Instruct": "OLMo-2-13B",
         "gemma-2-2b-it": "Gemma-2-2B", "gemma-2-9b-it": "Gemma-2-9B",
         "Ministral-8B-Instruct-2410": "Ministral-8B",
         "Mistral-Nemo-Instruct-2407": "Mistral-Nemo-12B",
         "Phi-3-medium-4k-instruct": "Phi-3-medium"}


def judge(tsel, ttest, A, rng):
    C = tsel.shape[1]
    val = np.array([ttest[int(np.argmax(tsel[:, e])), e] for e in range(C)])
    K, M, _, _ = A.shape
    null = np.zeros((B, C))
    for e in range(C):
        pick = rng.integers(0, M, size=(B, K))
        fs = A[np.arange(K)[None, :], pick, 0, e]
        fh = A[np.arange(K)[None, :], pick, 1, e]
        null[:, e] = fh[np.arange(B), np.argmax(fs, axis=1)]
    h1, h2 = null[: B // 2], null[B // 2:]
    thr = np.quantile(h1, 0.95, axis=0)
    mu, sd = h1.mean(0), h1.std(0) + 1e-12
    z = float(((val - mu) / sd).sum())
    zn = ((h2 - mu[None, :]) / sd[None, :]).sum(1)
    return {"n": int((val > thr).sum()), "C": C,
            "excess": float(np.median((val - mu) / sd)),
            "p_G": float((1 + (zn >= z).sum()) / (1 + len(zn)))}


rows, budgets = {}, set()
for mf in sorted(DATA.glob("meta_*_b0*.json")):
    b = re.search(r"_b(0\.\d+)\.json$", mf.name).group(1)
    meta = json.loads(mf.read_text())
    m = SHORT.get(meta["model"].split("/")[-1], meta["model"].split("/")[-1])
    z = np.load(DATA / mf.name.replace("meta_", "raw_").replace(".json", ".npz"))
    for ro in ("single", "syn"):
        k = f"emotion|{ro}"
        if f"{k}|F5" not in z.files:
            continue
        rows[(m, b, ro)] = judge(z[f"{k}|tgt_sel"], z[f"{k}|tgt_test"], z[f"{k}|F5"],
                                 np.random.default_rng(777))
    rows[(m, b, "_m")] = meta.get("m_f5")
    budgets.add(b)

bs = sorted(budgets, key=float)
models = sorted({k[0] for k in rows})
print(f"=== Gate I, budgets {'  and  '.join('J*='+b for b in bs)} (one set of activations, floor draws  "
      f"{rows[(models[0], bs[0], '_m')]} per target)===")
hdr = "".join(f"{'J*='+b+' single':>18s}{'syn':>14s}" for b in bs)
print(f"{'model':18s}{hdr}")
for m in models:
    line = f"{m:18s}"
    for b in bs:
        for ro in ("single", "syn"):
            r = rows.get((m, b, ro))
            line += f"{(str(r['n'])+'/'+str(r['C'])+f' ({r[chr(101)+chr(120)+chr(99)+chr(101)+chr(115)+chr(115)]:+.2f})'):>18s}" if ro == "single" \
                else f"{(str(r['n'])+'/'+str(r['C'])+f' ({r[chr(101)+chr(120)+chr(99)+chr(101)+chr(115)+chr(115)]:+.2f})'):>14s}"
    print(line)
print()
for b in bs:
    for ro in ("single", "syn"):
        q = [rows[(m, b, ro)] for m in models]
        maj = sum(r["n"] > r["C"] // 2 for r in q)
        print(f"J*={b} {ro:6s}: models with a majority {maj}/{len(q)} / median excess SD "
              f"{np.median([r['excess'] for r in q]):+.2f} / p(G) max "
              f"{max(r['p_G'] for r in q):.4f}")
json.dump({f"{k[0]}|{k[1]}|{k[2]}": v for k, v in rows.items() if k[2] != "_m"},
          open(DATA.parent / "budstats.json", "w"), indent=1, ensure_ascii=False)
