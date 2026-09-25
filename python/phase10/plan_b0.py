#!/usr/bin/env python3
"""Plan B, Phase B0: does the selection statistic detect a direction whose
meaning is known?

The positive control is the human valence direction (P2_ridge_std on E1). It
must beat the profile-matched floor on the consistency statistic S in at least
3 of 4 layers at alpha=0.05, or Plan B stops.

Pre-registration: plan_b_prereg_20260926.md, commit fa42c51 (refinements) on
top of 3289513 (design, pushed before any result existed).

Selection set only. No judge, no generation. Results flushed after every cell.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_CVD = os.environ.get("CUDA_VISIBLE_DEVICES")

import numpy as np  # noqa: E402

BASE = Path("/path/to/work/results")
SLUG = "swiss-ai__Apertus-v1_1-1_5B"
ACT = BASE / "activations_nopad" / SLUG
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
VAD = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")

LAYERS = (5, 7, 10, 12)
ALPHAS = (0.03, 0.05, 0.10, 0.20)
A05 = 0.05
PC_K = 50                 # prereg 5: profile basis size
N_PMF = 100               # prereg 12.2: B0 only
N_BINS = 8                # prereg 5: eigenvalue bins for the permutation
VOCAB_M = 512             # prereg 5
BOOT_N, BOOT_SEED = 10_000, 20260925
SPLIT_SEED = 20260926     # fixed by this pre-registration
SEED = 42
MAX_LEN = 128
DEGEN_TOP1, DEGEN_LO, DEGEN_HI = 0.95, 0.5, 2.0
KEYS = ("valence", "arousal", "dominance")
_SUF = ("s", "es", "ed", "ing", "ly")
PREREG_COMMIT = "fa42c5131224afed4d5cdef23f62e59f49b1c3af"

sys.path.insert(0, "/path/to/work/code/phase10")
from consistency_metric import consistency  # noqa: E402


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


def load_vad() -> dict[str, dict[str, float]]:
    import csv
    out: dict[str, dict[str, float]] = {}
    with VAD.open() as fh:
        for r in csv.DictReader(fh):
            try:
                out[r["word"].strip().lower()] = {k: float(r[k]) for k in KEYS}
            except (KeyError, TypeError, ValueError):
                continue
    return out


def stim_vad(t: str, vad: dict) -> dict | None:
    def look(w: str):
        if w in vad:
            return vad[w]
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                return vad[w[: -len(s)]]
        return None
    h = [x for x in (look(w) for w in re.findall(r"[a-zA-Z']+", t.lower()))
         if x is not None]
    return {k: float(np.mean([z[k] for z in h])) for k in KEYS} if h else None


def pmf_draws(d: np.ndarray, PCs: np.ndarray, evals: np.ndarray,
              n: int, rng: np.random.Generator) -> list[np.ndarray]:
    """Directions matching d's squared-projection profile on the PC basis.

    Signs are randomised, coefficients are permuted only among PCs whose
    eigenvalues fall in the same log-spaced bin (so the variance the profile
    implies is preserved), and the residual outside the PC span is randomly
    rotated.
    """
    d = _unit(d)
    coef = PCs @ d                        # (K,)
    resid = d - PCs.T @ coef
    r_norm = float(np.linalg.norm(resid))
    D = d.size
    lo, hi = np.log10(max(evals.min(), 1e-12)), np.log10(evals.max())
    edges = np.linspace(lo, hi, N_BINS + 1)
    binid = np.clip(np.digitize(np.log10(np.maximum(evals, 1e-12)), edges) - 1,
                    0, N_BINS - 1)
    out = []
    for _ in range(n):
        c = coef.copy()
        for b in range(N_BINS):                     # permute within a bin
            idx = np.where(binid == b)[0]
            if idx.size > 1:
                c[idx] = c[rng.permutation(idx)]
        c = c * rng.choice((-1.0, 1.0), size=c.size)   # randomise signs
        v = PCs.T @ c
        if r_norm > 1e-12:                          # random rotation of residual
            g = rng.standard_normal(D)
            g -= PCs.T @ (PCs @ g)
            gn = np.linalg.norm(g)
            if gn > 1e-12:
                v = v + r_norm * (g / gn)
        out.append(_unit(v))
    return out


def bh(pv):
    arr = np.asarray(pv, float)
    ok = ~np.isnan(arr)
    out = np.full(arr.shape, np.nan)
    p = arr[ok]
    if p.size == 0:
        return out.tolist()
    o = np.argsort(p)
    m = p.size
    adj = np.clip(np.minimum.accumulate((p[o] * m / (np.arange(m) + 1))[::-1])[::-1],
                  0, 1)
    r = np.empty(m)
    r[o] = adj
    out[ok] = r
    return out.tolist()


def boot_ci_S(deltas: np.ndarray) -> tuple[float, float]:
    """Bootstrap over stimuli (not pairs), which respects their dependence."""
    rng = np.random.default_rng(BOOT_SEED)
    n = deltas.shape[0]
    vals = []
    for _ in range(1000):                 # 1000 is ample for a CI on a mean cosine
        idx = rng.integers(0, n, size=n)
        if len({int(x) for x in idx}) < 2:
            continue
        vals.append(consistency(deltas[idx]))
    if len(vals) < 2:
        return (float("nan"), float("nan"))
    lo, hi = np.quantile(vals, [0.025, 0.975])
    return float(lo), float(hi)


def env(extra: dict) -> dict:
    def sh(c):
        try:
            return subprocess.run(c, capture_output=True, text=True,
                                  timeout=15).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""
    um = {}
    for ln in sh(["nvidia-smi", "--query-gpu=index,uuid",
                  "--format=csv,noheader"]).splitlines():
        q = [x.strip() for x in ln.split(",")]
        if len(q) == 2:
            um[q[0]] = q[1]
    m = {"generated_utc": datetime.now(timezone.utc).isoformat(),
         "script": Path(__file__).name,
         "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "hostname": platform.node(), "python": sys.version.split()[0],
         "numpy": np.__version__, "CUDA_VISIBLE_DEVICES": _CVD,
         "gpu_uuid_visible_physical": [um.get(i.strip(), "?")
                                       for i in (_CVD or "").split(",") if i.strip()],
         "prereg_commit": PREREG_COMMIT,
         "prereg_file": "plan_b_prereg_20260926.md",
         "phase": "B0", "split_used": "SELECTION only (test set not read)",
         "n_pmf_draws": N_PMF, "pc_k": PC_K, "vocab_m": VOCAB_M,
         "pca_and_direction_rows": "E1 sentences with VAD only",
         "centering": "vocab (per stimulus); stimulus-centring is refused",
         "judge_llm_loaded": False, "generation_used": False,
         "hook_scope": "last_token"}
    try:
        import torch
        m["torch"] = torch.__version__
        m["cuda"] = torch.version.cuda
    except Exception:  # noqa: BLE001
        pass
    m.update(extra)
    return m


def split_heldout() -> tuple[list[int], list[int]]:
    """Category-stratified split of E4 40-79: one template variant per side."""
    e4 = json.loads(E4.read_text())
    cats: dict[str, list[int]] = {}
    for i in range(40, 80):
        cats.setdefault(e4[i]["target_emotion"], []).append(i)
    assert len(cats) == 20 and all(len(v) == 2 for v in cats.values()), \
        "E4 40-79 is not 20 categories x 2 variants"
    rng = np.random.default_rng(SPLIT_SEED)
    sel, tst = [], []
    for c in sorted(cats):
        a, b = cats[c]
        if rng.random() < 0.5:
            a, b = b, a
        sel.append(a)
        tst.append(b)
    assert not (set(sel) & set(tst)) and len(sel) == len(tst) == 20
    return sorted(sel), sorted(tst)


def self_check() -> int:
    ok = True

    def c(n, v):
        nonlocal ok
        print(f"  [{'OK ' if v else 'FAIL'}] {n}")
        ok &= bool(v)
    s, t = split_heldout()
    c("split is 20/20 and disjoint", len(s) == 20 and len(t) == 20
      and not set(s) & set(t))
    c("split covers exactly E4 40-79", sorted(s + t) == list(range(40, 80)))
    e4 = json.loads(E4.read_text())
    c("each side holds all 20 categories",
      len({e4[i]["target_emotion"] for i in s}) == 20
      and len({e4[i]["target_emotion"] for i in t}) == 20)
    rng = np.random.default_rng(0)
    D, K = 64, 10
    A = rng.standard_normal((200, D))
    from sklearn.decomposition import PCA
    pca = PCA(n_components=K, random_state=0).fit(A)
    d = _unit(rng.standard_normal(D))
    draws = pmf_draws(d, pca.components_, pca.explained_variance_, 50, rng)
    prof = np.sort((pca.components_ @ d) ** 2)[::-1]
    c("PMF draws are unit vectors",
      all(abs(np.linalg.norm(v) - 1) < 1e-8 for v in draws))
    c("PMF draws preserve the sorted squared-projection profile",
      all(np.allclose(np.sort((pca.components_ @ v) ** 2)[::-1], prof, atol=1e-8)
          for v in draws))
    c("PMF draws are not the original direction",
      np.mean([abs(float(v @ d)) for v in draws]) < 0.9)
    q = bh([0.001, 0.02, 0.5])
    c("BH monotone", q[0] <= q[1] <= q[2])
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=list(LAYERS))
    ap.add_argument("--alphas", type=float, nargs="+", default=list(ALPHAS))
    ap.add_argument("--n-pmf", type=int, default=N_PMF)
    ap.add_argument("--out-dir", type=Path, default=BASE / "plan_b" / "B0")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        return self_check()
    if self_check() != 0:
        print("REFUSING: self-check failed")
        return 2
    if _CVD is None:
        print("FATAL: CUDA_VISIBLE_DEVICES unset", file=sys.stderr)
        return 4

    import torch
    import torch.nn.functional as F
    from sklearn.decomposition import PCA
    from transformers import AutoModelForCausalLM, AutoTokenizer

    sel_idx, _ = split_heldout()
    e4 = json.loads(E4.read_text())
    texts = [e4[i]["text"] for i in sel_idx]
    vad = load_vad()
    e1 = json.loads(E1.read_text())
    sc = [stim_vad(s["text"], vad) for s in e1]
    keep = [i for i, s in enumerate(sc) if s is not None]
    y = {k: np.array([sc[i][k] for i in keep]) for k in KEYS}
    print(f"selection n={len(texts)}; E1 scored {len(keep)}/{len(e1)}", flush=True)

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True)
    model.eval()
    dec = (model.model.layers if hasattr(model, "model")
           and hasattr(model.model, "layers") else model.transformer.h)
    dev = next(model.parameters()).device
    print("loaded", flush=True)

    class Hook:
        def __init__(self, d, alpha):
            self.delta = torch.tensor(alpha * d, dtype=torch.float16)

        def __call__(self, m, i, o):
            hs = o[0] if isinstance(o, tuple) else o
            z = hs.clone()
            z[:, -1, :] = z[:, -1, :] + self.delta.to(hs.device).to(hs.dtype)
            return (z,) + o[1:] if isinstance(o, tuple) else z

    def logprobs(text, layer, d, alpha):
        enc = {k: v.to(dev) for k, v in
               tok(text, return_tensors="pt", truncation=True,
                   max_length=MAX_LEN).items()}
        h = dec[layer].register_forward_hook(Hook(d, alpha)) if d is not None else None
        try:
            with torch.no_grad():
                lg = model(**enc).logits[0, -1, :]
        finally:
            if h is not None:
                h.remove()
        lp = F.log_softmax(lg.float(), dim=-1).cpu().numpy()
        return lp

    a.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = a.out_dir / f"B0_positive_control_{stamp}.json"
    results: list[dict] = []

    for L in a.layers:
        print(f"\n===== layer {L} =====", flush=True)
        X_all = np.load(ACT / f"layer{L:02d}_seed{SEED:04d}.npz",
                        allow_pickle=True)["arr"].astype(np.float32)
        # the activation file holds all E1 sentences; the VAD targets exist only
        # for `keep`, so both the direction and the PMF basis use that subset,
        # keeping the basis and the direction on the same rows
        assert X_all.shape[0] == len(e1), (X_all.shape, len(e1))
        X1 = X_all[keep]
        assert X1.shape[0] == len(keep) == y["valence"].size
        pos = p2_ridge_std(X1, y["valence"])
        pca = PCA(n_components=PC_K, random_state=SEED).fit(X1.astype(np.float64))
        PCs, evals = pca.components_, pca.explained_variance_
        inside = float(np.sum((PCs @ pos) ** 2))
        print(f"  pos inside top-{PC_K} PC span: {inside:.4f}", flush=True)

        base = [logprobs(t, L, None, 0.0) for t in texts]
        # per-stimulus alpha uses the stimulus's own activation norm
        acts = []
        for t in texts:
            enc = {k: v.to(dev) for k, v in
                   tok(t, return_tensors="pt", truncation=True,
                       max_length=MAX_LEN).items()}
            got = []

            def hk(m, i, o):
                hs = o[0] if isinstance(o, tuple) else o
                got.append(hs.float()[0, -1].detach().cpu().numpy())
            hh = dec[L].register_forward_hook(hk)
            try:
                with torch.no_grad():
                    model(**enc)
            finally:
                hh.remove()
            acts.append(got[0])
        norms = np.linalg.norm(np.stack(acts), axis=1)

        # vocabulary set V: top-M by pooled baseline mass, fixed before any result
        pooled = np.mean([np.exp(b) for b in base], axis=0)
        V = np.sort(np.argsort(pooled)[-VOCAB_M:])

        rng = np.random.default_rng(SPLIT_SEED + L)
        draws = pmf_draws(pos, PCs, evals, a.n_pmf, rng)

        for al in a.alphas:
            def deltas_for(d, sign=1.0):
                out_ = np.empty((len(texts), V.size))
                dg = []
                for i, t in enumerate(texts):
                    lp = logprobs(t, L, sign * d, al * norms[i])
                    out_[i] = lp[V] - base[i][V]
                    pr = np.exp(lp)
                    Hh = float(-np.sum(pr[pr > 0] * np.log(pr[pr > 0])))
                    pb = np.exp(base[i])
                    H0 = float(-np.sum(pb[pb > 0] * np.log(pb[pb > 0])))
                    er = Hh / H0 if H0 > 0 else float("nan")
                    dg.append(1.0 if (pr.max() >= DEGEN_TOP1 or
                                      (not math.isnan(er) and
                                       (er <= DEGEN_LO or er >= DEGEN_HI))) else 0.0)
                return out_, float(np.mean(dg))

            d_pos, degen = deltas_for(pos, 1.0)
            S_pos = consistency(d_pos)
            d_neg, _ = deltas_for(pos, -1.0)
            S_pos_neg = consistency(d_neg)
            ci_lo, ci_hi = boot_ci_S(d_pos)

            S_null = []
            for k, v in enumerate(draws):
                dv, _ = deltas_for(v, 1.0)
                S_null.append(consistency(dv))
                if (k + 1) % 25 == 0:
                    print(f"    L{L} a={al} pmf {k+1}/{len(draws)}", flush=True)
            S_null = np.array(S_null)
            mu, sd = float(S_null.mean()), float(S_null.std(ddof=1))
            p = (1 + int((S_null >= S_pos).sum())) / (1 + S_null.size)
            row = {"layer": L, "alpha_rel": al, "n_stimuli": len(texts),
                   "S_pos": S_pos, "S_pos_neg_polarity": S_pos_neg,
                   "S_pos_ci_lo": ci_lo, "S_pos_ci_hi": ci_hi,
                   "S_pmf_mean": mu, "S_pmf_sd": sd,
                   "S_pmf_min": float(S_null.min()), "S_pmf_max": float(S_null.max()),
                   "E_excess": S_pos - mu,
                   "z": (S_pos - mu) / sd if sd > 0 else float("nan"),
                   "perm_p": p, "degenerate_frac_pos": degen,
                   "pos_inside_pc_span": inside,
                   "_S_pmf": [round(float(x), 10) for x in S_null]}
            results.append(row)
            print(f"  L{L} a={al}: S_pos={S_pos:.4f} pmf={mu:.4f}+-{sd:.4f} "
                  f"E={row['E_excess']:+.4f} z={row['z']:+.2f} p={p:.4f}",
                  flush=True)
            out.write_text(json.dumps(
                {"env": env({"status": "IN_PROGRESS"}), "rows": results},
                indent=2, ensure_ascii=False))

    qs = bh([r["perm_p"] for r in results])
    for r, q in zip(results, qs):
        r["q_bh"] = q
    sig = [r["layer"] for r in results
           if abs(r["alpha_rel"] - A05) < 1e-9 and r["q_bh"] < 0.05
           and r["E_excess"] > 0 and r["degenerate_frac_pos"] < 0.20]
    verdict = {
        "criterion": ">=3 of 4 layers at alpha=0.05 with BH q<0.05 and E>0",
        "bh_family_size": len(results),
        "significant_layers_at_alpha0.05": sorted(set(sig)),
        "n_layers": len(set(sig)), "B0_PASS": bool(len(set(sig)) >= 3),
        "IF_FAIL": ("prereg B section 3: Plan B stops and the recorded conclusion is "
                    "that the consistency statistic does not detect even a "
                    "direction whose meaning is known")}
    out.write_text(json.dumps(
        {"env": env({"status": "COMPLETE"}), "VERDICT": verdict, "rows": results},
        indent=2, ensure_ascii=False))
    print(f"\nB0 VERDICT: {'PASS' if verdict['B0_PASS'] else 'FAIL'} "
          f"({verdict['n_layers']}/4 layers)")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
