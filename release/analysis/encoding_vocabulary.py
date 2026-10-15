"""Amendment 100: the second encoding vocabulary, and the reproduction check on codebook 1.

Reads the stageSC2 archives and reports, per model and codebook,
  - the count of targets cleared and the median standardised excess, for both readouts,
  - the paired standardised-excess difference over matched targets (word minus code),
and compares codebook 1 against the values already published for it.

No GPU is needed and no number is entered by hand.
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

import numpy as np

B = 4000
SHORT = {"Llama-3.1-8B-Instruct": "Llama-3.1-8B", "gemma-2-9b-it": "Gemma-2-9B",
         "Mistral-Nemo-Instruct-2407": "Mistral-Nemo-12B",
         "OLMo-2-1124-13B-Instruct": "OLMo-2-13B",
         "Ministral-8B-Instruct-2410": "Ministral-8B"}
CB_NAME = {"1": "table 1, single letters", "2": "table 2, derangement", "3": "table 3, digits and symbols", "4": "table 4, its derangement"}


def per_target(tsel, ttest, A, rng):
    """Return the standardised excess of every target, and the pass count."""
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
    z = (val - mu) / sd
    g = float(z.sum())
    zn = ((h2 - mu[None, :]) / sd[None, :]).sum(1)
    return {"z": z, "n": int((val > thr).sum()), "C": C,
            "excess": float(np.median(z)), "G": g,
            "p_G": float((1 + (zn >= g).sum()) / (1 + len(zn)))}


def load(root: Path):
    rows = {}
    for mf in sorted(root.glob("meta_*.json")):
        m2 = re.search(r"meta_(.+?)_(word|code)(\d)(_grad)?\.json$", mf.name)
        if not m2:
            continue
        npz = root / mf.name.replace("meta_", "raw_").replace(".json", ".npz")
        if not npz.exists():
            continue
        meta = json.loads(mf.read_text())
        name = meta["model"].split("/")[-1]
        m = SHORT.get(name, name)
        cue, cb, fam = m2.group(2), m2.group(3), "grad" if m2.group(4) else "emotion"
        z = np.load(npz)
        key = f"{fam}|{cue}"
        rows[(m, cb, fam, cue)] = per_target(z[f"{key}|tgt_sel"], z[f"{key}|tgt_test"],
                                             z[f"{key}|F5"], np.random.default_rng(777))
        rows[(m, cb, fam, cue)]["budget"] = meta.get("budget", meta.get("J_star"))
    return rows


def published(path: Path):
    """Parse the published codebook-1 values out of the generated table file."""
    out = {}
    block = path.read_text().split("### Fifty floor draws, codebook 1")[-1]
    for line in block.split("\n"):
        c = [x.strip().replace("**", "") for x in line.strip().strip("|").split("|")]
        if len(c) != 3 or c[0] in ("Model", "") or set(c[1]) <= set("-: "):
            continue
        def parse(s):
            m = re.match(r"(\d+)/(\d+) \(([-+0-9.]+)\)", s)
            return (int(m.group(1)), float(m.group(3))) if m else None
        w, k = parse(c[1]), parse(c[2])
        if w and k:
            out[c[0]] = {"word": w, "code": k}
    return out


def main(root, pub=None):
    rows = load(Path(root))
    if not rows:
        print("nothing to analyse")
        return 1
    models = sorted({k[0] for k in rows})
    cbs = sorted({k[1] for k in rows})

    print(f"{'model':18s} {'codebook':>12s} | {'emotion words':>16s} | {'codes':>16s} | {'paired difference':>8s}")
    paired = {}
    for cb in cbs:
        for m in models:
            w = rows.get((m, cb, "emotion", "word"))
            c = rows.get((m, cb, "emotion", "code"))
            if not (w and c):
                continue
            d = w["z"] - c["z"]
            paired.setdefault(cb, []).append((m, d))
            f = lambda r: f"{r['n']:>2d}/{r['C']} ({r['excess']:+.2f})"
            print(f"{m:18s} {CB_NAME.get(cb, cb):>12s} | {f(w):>16s} | {f(c):>16s} "
                  f"| {np.median(d):+8.2f}")
    print()
    for cb, lst in paired.items():
        alld = np.concatenate([d for _, d in lst])
        med = [float(np.median(d)) for _, d in lst]
        print(f"{CB_NAME.get(cb, cb)}: median paired difference {np.median(med):+.2f} SD "
              f"(per model {min(med):+.2f}〜{max(med):+.2f}) / "
              f"targets where words exceed codes {int((alld > 0).sum())}/{len(alld)}")

    # Amendment 99 CR1: codebooks are compared on one and the same set of activations.
    if "1" in cbs:
        print("\n=== code vocabularies compared on one and the same set of activations (amendment 99 CR1)===")
        print(f"{'model':18s} " + " ".join(f"{CB_NAME.get(c, c):>14s}" for c in cbs))
        for m in models:
            cells = []
            for c in cbs:
                r = rows.get((m, c, "emotion", "code"))
                cells.append("—".rjust(14) if r is None
                             else f"{r['n']:>2d}/{r['C']} ({r['excess']:+.2f})".rjust(14))
            print(f"{m:18s} " + " ".join(cells))

    if pub and "1" in cbs:
        P = published(Path(pub))
        print("\n=== reference only: codebook 1 against the published values; by amendment 99 CR1 this")
        print("    comparison supports no claim and replaces no published number===")
        print(f"{'model':18s} {'count new/old':>14s} {'excess SD new/old':>18s}")
        for m in models:
            w = rows.get((m, "1", "emotion", "word")); c = rows.get((m, "1", "emotion", "code"))
            if not (w and c) or m not in P:
                continue
            pw, pc = P[m]["word"], P[m]["code"]
            print(f"{m:18s} word {w['n']:>2d}/{pw[0]:<2d} code {c['n']:>2d}/{pc[0]:<2d}  "
                  f"word {w['excess']:+.2f}/{pw[1]:+.2f}  code {c['excess']:+.2f}/{pc[1]:+.2f}")
    json.dump({f"{k[0]}|{k[1]}|{k[2]}|{k[3]}":
               {a: (b if not isinstance(b, np.ndarray) else [round(float(x), 4) for x in b])
                for a, b in v.items()} for k, v in rows.items()},
              open(Path(root) / "amend100.json", "w"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else ".",
                          sys.argv[2] if len(sys.argv) > 2 else None))
