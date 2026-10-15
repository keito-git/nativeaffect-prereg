"""Judgement for test CE, with the two codebooks kept apart and the population of amendment 92.

Only models that passed the validity check on both codebooks are judged; the rest are reported
with their numbers and the reason they are excluded, not deleted.
"""
from __future__ import annotations

import glob, json, re, sys
from pathlib import Path

import numpy as np

B = 4000
MIN_POP = 3


def family_max_null(A, rng, b=B):
    K, M, _, C = A.shape
    out = np.zeros((b, C))
    for e in range(C):
        pick = rng.integers(0, M, size=(b, K))
        fs = A[np.arange(K)[None, :], pick, 0, e]
        fh = A[np.arange(K)[None, :], pick, 1, e]
        out[:, e] = fh[np.arange(b), np.argmax(fs, axis=1)]
    return out


def judge(tsel, ttest, A, rng):
    C = tsel.shape[1]
    val = np.array([ttest[int(np.argmax(tsel[:, e])), e] for e in range(C)])
    null = family_max_null(A, rng)
    h1, h2 = null[: B // 2], null[B // 2:]
    thr = np.quantile(h1, 0.95, axis=0)
    mu, sd = h1.mean(0), h1.std(0) + 1e-12
    cnt = int((val > thr).sum())
    z_obs = float(((val - mu) / sd).sum())
    z_null = ((h2 - mu[None, :]) / sd[None, :]).sum(1)
    p_g = float((1 + (z_null >= z_obs).sum()) / (1 + len(z_null)))
    return {"count": f"{cnt}/{C}", "n_pass": cnt, "n_cls": C,
            "excess": round(float(np.median((val - mu) / sd)), 3),
            "G": round(z_obs, 2), "p_G": round(p_g, 5),
            "pass": bool(cnt > C // 2 and p_g < 0.01)}


def main(root):
    root = Path(root)
    chk = {}
    for f in glob.glob(str(root / "cecheck" / "*.json")):
        d = json.loads(Path(f).read_text())
        chk[(d["model"].split("/")[-1], d["codebook"])] = d
    models = sorted({m for m, _ in chk})
    pop = [m for m in models if all(chk.get((m, c), {}).get("validity_ok") for c in ("1", "2"))]

    rows = {}
    for mf in sorted(root.glob("meta_*_ce*.json")):
        cb = re.search(r"_ce(\d)\.json$", mf.name).group(1)
        meta = json.loads(mf.read_text())
        m = meta["model"].split("/")[-1]
        z = np.load(root / mf.name.replace("meta_", "raw_").replace(".json", ".npz"))
        rng = np.random.default_rng(777)
        rows[(m, cb)] = judge(z["emotion|code|tgt_sel"], z["emotion|code|tgt_test"],
                              z["emotion|code|F5"], rng)

    print(f"judgement population (valid on both codebooks): {len(pop)}/{len(models)} models")
    print(f"  {', '.join(pop)}\n")
    print(f"{'model':28s} {'in pop':>6s} {'cb':>2s} {'AUC median':>7s} {'modal':>6s} "
          f"{'count':>6s} {'excess SD':>7s} {'p(G)':>8s} verdict")
    for m in models:
        inpop = "○" if m in pop else "×"
        for cb in ("1", "2"):
            r = rows.get((m, cb)); c = chk.get((m, cb), {})
            if r is None:
                continue
            print(f"{m:28s} {inpop:>6s} {cb:>2s} {c.get('auc_median', 0):7.3f} "
                  f"{str(c.get('modal_hits'))+'/13':>6s} {r['count']:>6s} "
                  f"{r['excess']:+7.2f} {r['p_G']:8.5f} "
                  f"{'pass' if r['pass'] else 'fail'}"
                  f"{'' if m in pop else '（outside the population）'}")
    print()
    if len(pop) < MIN_POP:
        print(f"the population is {MIN_POP} models, below the minimum, so test CE yields no conclusion (amendment 92 CK2)。")
        return 0
    for cb in ("1", "2"):
        ok = [m for m in pop if rows[(m, cb)]["pass"]]
        print(f"codebook{cb}: pass {len(ok)} of {len(pop)} models "
              f"→ {'a majority' if len(ok) > len(pop)//2 else 'short of a majority'}"
              f"{'（' + ', '.join(ok) + '）' if ok else ''}")
    both = all(len([m for m in pop if rows[(m, cb)]["pass"]]) > len(pop)//2 for cb in ("1","2"))
    print(f"\n**verdict CE: {'pass' if both else 'fail'}** (criterion of amendment 91 CJ1)")
    ex = [rows[(m, cb)]["excess"] for m in pop for cb in ("1", "2")]
    cn = [rows[(m, cb)]["n_pass"] for m in pop for cb in ("1", "2")]
    print(f"population median excess SD {np.median(ex):+.2f} range {min(ex):+.2f}〜{max(ex):+.2f} / "
          f"count median {np.median(cn):.1f}/13 range {min(cn)}〜{max(cn)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
