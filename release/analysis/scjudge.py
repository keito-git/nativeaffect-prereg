"""Amendment 94: the same-context control (CM2) and the gradient positive control (CM1)."""
import glob, json, re, sys
from pathlib import Path
import numpy as np

B = 4000
SHORT = {"Llama-3.1-8B-Instruct": "Llama-3.1-8B", "gemma-2-9b-it": "Gemma-2-9B",
         "Mistral-Nemo-Instruct-2407": "Mistral-Nemo-12B",
         "OLMo-2-1124-13B-Instruct": "OLMo-2-13B",
         "Ministral-8B-Instruct-2410": "Ministral-8B"}


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
    cnt = int((val > thr).sum())
    z = float(((val - mu) / sd).sum())
    zn = ((h2 - mu[None, :]) / sd[None, :]).sum(1)
    p = float((1 + (zn >= z).sum()) / (1 + len(zn)))
    return {"count": f"{cnt}/{C}", "n": cnt, "excess": round(float(np.median((val - mu) / sd)), 3),
            "G": round(z, 2), "p_G": round(p, 5), "pass": bool(cnt > C // 2 and p < 0.01)}


def main(root):
    root = Path(root)
    rows = {}
    for mf in sorted(root.glob("meta_*.json")):
        m2 = re.search(r"meta_(.+?)_(word|code)(\d)(_grad)?\.json$", mf.name)
        meta = json.loads(mf.read_text())
        m = SHORT.get(meta["model"].split("/")[-1], meta["model"].split("/")[-1])
        cue, cb, gr = m2.group(2), m2.group(3), bool(m2.group(4))
        z = np.load(root / mf.name.replace("meta_", "raw_").replace(".json", ".npz"))
        fam = "grad" if gr else "emotion"
        key = f"{fam}|{cue}"
        rows[(m, cb, fam, cue)] = judge(z[f"{key}|tgt_sel"], z[f"{key}|tgt_test"],
                                        z[f"{key}|F5"], np.random.default_rng(777))
    models = sorted({k[0] for k in rows})

    print("=== CM2 same-context control（identical prefix; only the cue and the readout vocabulary differ）===")
    print(f"{'model':20s} {'cb':>2s} | {'emotion wordsreadout':>22s} | {'codesreadout':>22s}")
    for m in models:
        for cb in ("1", "2"):
            w = rows.get((m, cb, "emotion", "word")); c = rows.get((m, cb, "emotion", "code"))
            if not (w and c):
                continue
            f = lambda r: f"{r['count']:>5s}({r['excess']:+.2f}) p={r['p_G']:.4f}"
            print(f"{m:20s} {cb:>2s} | {f(w):>22s} | {f(c):>22s}")
    print()
    print("=== CM1 positive control (gradient for the code readout, codebook 1) ===")
    print(f"{'model':20s} | {'gradient family':>22s} | {'emotion family (same)':>22s}")
    for m in models:
        g = rows.get((m, "1", "grad", "code")); c = rows.get((m, "1", "emotion", "code"))
        if not g:
            continue
        f = lambda r: "—" if r is None else f"{r['count']:>5s}({r['excess']:+.2f}) p={r['p_G']:.4f}"
        print(f"{m:20s} | {f(g):>22s} | {f(c):>22s}")
    print()
    for label, sel in (("emotion-word readout (same context)", lambda m, cb: rows.get((m, cb, "emotion", "word"))),
                       ("code readout (same context)", lambda m, cb: rows.get((m, cb, "emotion", "code"))),
                       ("gradient (positive control)", lambda m, cb: rows.get((m, cb, "grad", "code")) if cb == "1" else None)):
        q = [r for m in models for cb in ("1", "2") if (r := sel(m, cb))]
        if not q:
            continue
        ok = sum(r["pass"] for r in q)
        print(f"{label:26s} pass {ok}/{len(q)} cells / median excess SD "
              f"{np.median([r['excess'] for r in q]):+.2f} / count median "
              f"{np.median([r['n'] for r in q]):.1f}/13")
    json.dump({f"{k[0]}|{k[1]}|{k[2]}|{k[3]}": v for k, v in rows.items()},
              open(root / "scjudge.json", "w"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
