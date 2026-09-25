#!/usr/bin/env python3
"""In-plane random floor (primary), PC-direction arms, and the E4 held-out cache.

Pre-registration section 26, committed before this ran (predictions 26.4 recorded).

The confound: every random floor so far came from the full 2048-dim space, while
the ICA axes sit 88.7-99.97 percent inside the top-10 PC span, which a random
2048-dim direction overlaps by only 10/2048 = 0.49 percent in expectation. So the
existing results may only show that a high-variance direction beats a random one.
The decisive control is a random direction drawn from WITHIN the span (Sun et al.'s
in-plane random).

Arms per layer:
  axis0..2              top-3 ICA axes by split-half reproducibility
  inplane_0..4          PRIMARY floor: uniform on the unit sphere of the top-10 PC span
  inplanevar_0..4       secondary: same span, coefficients scaled by PC sd
  pc_0..4               PC1..PC5 themselves, as intervention directions
  fullrand_0..4         the old full-space floor, kept for comparison

Primary criterion (26.3): an axis beats the in-plane floor at some alpha >= 0.03
with BH q < 0.05, mean_diff > 0 and degenerate_frac < 0.20. Failing that, the
recorded conclusion is that the effect is explained by high-variance directionality.

Also caches the E4 index 40-79 last-token activations to disk so the S3 category
work never needs the GPU again.

Discovery set only. No judge, no generation. Results flushed after every alpha.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

_CVD = os.environ.get("CUDA_VISIBLE_DEVICES")

import numpy as np  # noqa: E402
from scipy import stats as sp_stats  # noqa: E402

BASE = Path("/path/to/work/results")
SLUG = "swiss-ai__Apertus-v1_1-1_5B"
ACT = BASE / "activations_nopad" / SLUG
ICA = BASE / "ica_nopad" / SLUG
SPLIT = BASE / "axes_nopad" / "axis_rebuilt_split_20260925.json"
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
LAYERS = (5, 7, 10, 12)
ALPHAS = (0.01, 0.03, 0.05, 0.10, 0.20)
N_AXES = 3
N_FLOOR = 5
N_PC_ARMS = 5
PC_K = 10                 # FIXED by prereg 26.2
INPLANE_SEED = 42 + 31337  # FIXED by prereg 26.2
FULLRAND_SEED = 42 + 9999  # the historical floor
BOOT_N = 10_000
BOOT_SEED = 20260925
TOP_K_VOCAB = 100
MAX_LEN = 128
DEGEN_TOP1, DEGEN_LO, DEGEN_HI, DEGEN_MAX = 0.95, 0.5, 2.0, 0.20


def boot_ci(v: Sequence[float]) -> tuple[float, float]:
    a = np.asarray([x for x in v if not math.isnan(x)], float)
    if a.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(BOOT_SEED)
    m = a[rng.integers(0, a.size, size=(BOOT_N, a.size))].mean(axis=1)
    lo, hi = np.quantile(m, [0.025, 0.975])
    return (float(lo), float(hi))


def paired(a: Sequence[float], b: Sequence[float],
           alt: str = "greater") -> dict[str, float]:
    pr = [(x, y) for x, y in zip(a, b) if not (math.isnan(x) or math.isnan(y))]
    if len(pr) < 2:
        return {"n": len(pr), "mean_diff": float("nan"),
                "wilcoxon_p": float("nan"), "cliffs_delta": float("nan"),
                "ci_lo": float("nan"), "ci_hi": float("nan")}
    xa = np.array([p[0] for p in pr], float)
    xb = np.array([p[1] for p in pr], float)
    d = xa - xb
    if np.allclose(d, 0.0):
        p = 1.0
    else:
        try:
            _, p = sp_stats.wilcoxon(xa, xb, alternative=alt, zero_method="zsplit")
        except ValueError:
            p = float("nan")
    lo, hi = boot_ci(d.tolist())
    return {"n": int(d.size), "mean_diff": float(d.mean()),
            "std_diff": float(d.std(ddof=1)), "wilcoxon_p": float(p),
            "ci_lo": lo, "ci_hi": hi,
            "cliffs_delta": float((d > 0).mean() - (d < 0).mean())}


def bh(pv: Sequence[float]) -> list[float]:
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


def ms(v: Sequence[float]) -> tuple[float, float]:
    a = np.asarray([x for x in v if not math.isnan(x)], float)
    if a.size == 0:
        return (float("nan"), float("nan"))
    return (float(a.mean()), float(a.std(ddof=1)) if a.size > 1 else 0.0)


class Hook:
    def __init__(self, d: np.ndarray, alpha: float) -> None:
        import torch
        self.delta = torch.tensor(alpha * d, dtype=torch.float16)

    def __call__(self, m: Any, i: tuple, o: Any) -> Any:
        hs = o[0] if isinstance(o, tuple) else o
        dd = self.delta.to(hs.device).to(hs.dtype)
        z = hs.clone()
        z[:, -1, :] = z[:, -1, :] + dd
        return (z,) + o[1:] if isinstance(o, tuple) else z


def fwd(model: Any, tok: Any, dec: Any, text: str, layer: int,
        d: np.ndarray | None, alpha: float) -> dict[str, Any]:
    import torch
    import torch.nn.functional as F
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAX_LEN)
    dev = next(model.parameters()).device
    enc = {k: v.to(dev) for k, v in enc.items()}
    h = dec[layer].register_forward_hook(Hook(d, alpha)) if d is not None else None
    try:
        with torch.no_grad():
            lg = model(**enc).logits[0, -1, :]
    finally:
        if h is not None:
            h.remove()
    pr = F.softmax(lg.float(), dim=-1).cpu().numpy()
    pp = pr[pr > 0]
    idx = np.argsort(pr)[-TOP_K_VOCAB:]
    lp = np.log(pr[idx] + 1e-45)
    o = np.argsort(idx)
    return {"H": float(-np.sum(pp * np.log(pp))), "top1": float(pr.max()),
            "_i": idx[o], "_l": lp[o]}


def js(a: dict[str, Any], b: dict[str, Any]) -> float:
    i1, l1, i2, l2 = a["_i"], a["_l"], b["_i"], b["_l"]
    ax = np.union1d(i1, i2)
    p = np.zeros(ax.size)
    q = np.zeros(ax.size)
    s1 = np.searchsorted(i1, ax)
    h1 = (s1 < i1.size) & (i1[np.clip(s1, 0, i1.size - 1)] == ax)
    p[h1] = np.exp(l1[s1[h1]])
    s2 = np.searchsorted(i2, ax)
    h2 = (s2 < i2.size) & (i2[np.clip(s2, 0, i2.size - 1)] == ax)
    q[h2] = np.exp(l2[s2[h2]])
    p /= (p.sum() + 1e-45)
    q /= (q.sum() + 1e-45)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / (m + 1e-45) + 1e-45))
                 + 0.5 * np.sum(q * np.log(q / (m + 1e-45) + 1e-45)))


def cap(model: Any, tok: Any, dec: Any, text: str, layer: int) -> np.ndarray:
    import torch
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAX_LEN)
    dev = next(model.parameters()).device
    enc = {k: v.to(dev) for k, v in enc.items()}
    got: list[np.ndarray] = []

    def hk(m: Any, i: Any, o: Any) -> None:
        hs = o[0] if isinstance(o, tuple) else o
        got.append(hs.float()[0, -1].cpu().numpy())
    h = dec[layer].register_forward_hook(hk)
    try:
        with torch.no_grad():
            model(**enc)
    finally:
        h.remove()
    return got[0]


def env(extra: dict[str, Any]) -> dict[str, Any]:
    def sh(c: list[str]) -> str:
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
    m: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "hostname": platform.node(), "python": sys.version.split()[0],
        "numpy": np.__version__, "CUDA_VISIBLE_DEVICES": _CVD,
        "gpu_uuid_visible_physical": [um.get(i.strip(), "?")
                                      for i in (_CVD or "").split(",") if i.strip()],
        "pc_k_FIXED": PC_K, "inplane_seed": INPLANE_SEED,
        "fullrand_seed": FULLRAND_SEED, "alphas": list(ALPHAS),
        "hook_scope": "last_token", "judge_llm_loaded": False,
        "generation_used": False, "split_set": "DISCOVERY ONLY",
        "primary_criterion": ("axis beats in_plane_random at some alpha>=0.03 with "
                              "BH q<0.05, mean_diff>0, degenerate_frac<0.20 "
                              "(prereg 26.3)"),
        "prereg_section": "26",
    }
    try:
        import torch
        m["torch"] = torch.__version__
        m["cuda"] = torch.version.cuda
    except Exception:  # noqa: BLE001
        pass
    m.update(extra)
    return m


def self_check() -> int:
    ok = True

    def c(n: str, v: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if v else 'FAIL'}] {n}")
        ok &= bool(v)

    r = paired([2.0] * 20, [1.0] * 20)
    c("paired shift", abs(r["mean_diff"] - 1) < 1e-12 and r["cliffs_delta"] == 1.0)
    q = bh([0.001, 0.02, 0.5])
    c("bh monotone", q[0] <= q[1] <= q[2])
    m1 = {"_i": np.array([1, 2, 3]), "_l": np.log([.2, .3, .5])}
    c("JS(self)=0", abs(js(m1, m1)) < 1e-12)
    c("JS(disjoint)=ln2", abs(js(m1, {"_i": np.array([7, 8]),
                                      "_l": np.log([.5, .5])}) - math.log(2)) < 1e-9)
    # in-plane directions must lie inside the span, and full-space ones must not
    rg = np.random.default_rng(0)
    Xf = rg.standard_normal((100, 64))
    from sklearn.decomposition import PCA
    pc = PCA(n_components=10, random_state=0).fit(Xf).components_
    co = rg.standard_normal((5, 10))
    ip = co @ pc
    ip /= np.linalg.norm(ip, axis=1, keepdims=True)
    inside = [float(np.sum((pc @ v) ** 2)) for v in ip]
    c(f"in-plane dirs lie inside the span (min={min(inside):.4f})",
      min(inside) > 0.999)
    fr = rg.standard_normal((5, 64))
    fr /= np.linalg.norm(fr, axis=1, keepdims=True)
    ins_f = [float(np.sum((pc @ v) ** 2)) for v in fr]
    c(f"full-space dirs mostly outside the span (max={max(ins_f):.3f})",
      max(ins_f) < 0.6)
    c("in-plane inside-fraction exceeds full-space",
      min(inside) > max(ins_f))
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=list(LAYERS))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", type=Path, default=BASE / "inplane_floor")
    ap.add_argument("--prereg-commit", default="")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        return self_check()
    if _CVD is None:
        print("FATAL: CUDA_VISIBLE_DEVICES unset", file=sys.stderr)
        return 4

    import torch
    from sklearn.decomposition import PCA
    from transformers import AutoModelForCausalLM, AutoTokenizer
    sys.path.insert(0, "/path/to/work/code/phase10")
    from run_ica import compute_split_reproducibility

    disc = json.loads(SPLIT.read_text())["discovery_indices"]
    e4 = json.loads(E4.read_text())
    texts = [e4[i]["text"] for i in disc]
    held_idx = [i for i in range(len(e4)) if i >= 40]
    held_texts = [e4[i]["text"] for i in held_idx]

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True)
    model.eval()
    dec = (model.model.layers if hasattr(model, "model")
           and hasattr(model.model, "layers") else model.transformer.h)
    D = int(model.config.hidden_size)
    print(f"loaded, D={D}", flush=True)

    a.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = a.out_dir / f"inplane_floor_discovery_{stamp}.json"
    cache_path = ACT / f"e4_heldout40to79_seed{a.seed:04d}.npz"
    cache: dict[str, np.ndarray] = {}
    layers_out: list[dict[str, Any]] = []

    for L in a.layers:
        print(f"\n===== layer {L} =====", flush=True)
        acts_d = np.stack([cap(model, tok, dec, t, L) for t in texts])
        norms = np.linalg.norm(acts_d, axis=1)
        # task 1: cache the held-out E4 activations for the S3 work (CPU later)
        cache[f"layer{L:02d}"] = np.stack(
            [cap(model, tok, dec, t, L) for t in held_texts]).astype(np.float32)

        X1 = np.load(ACT / f"layer{L:02d}_seed{a.seed:04d}.npz",
                     allow_pickle=True)["arr"].astype(np.float32)
        pca = PCA(n_components=PC_K, random_state=a.seed).fit(X1.astype(np.float64))
        PCs = pca.components_
        pcsd = np.sqrt(pca.explained_variance_)

        files = sorted(glob.glob(str(ICA / f"layer{L:02d}_seed{a.seed:04d}_K*.json")))
        best, bs = None, -2.0
        for fp in files:
            dd = json.loads(Path(fp).read_text())
            s_ = max(dd.get("silhouettes") or [-1.0])
            if s_ > bs:
                bs, best = s_, dd
        comps = np.array(best["components"], dtype=np.float32)
        rp = compute_split_reproducibility(
            ACT / f"layer{L:02d}_seed{a.seed:04d}.npz", comps, seed=a.seed)
        top = comps[np.argsort(-rp)][:N_AXES]

        dirs: dict[str, np.ndarray] = {f"axis{i}": top[i] for i in range(N_AXES)}
        rg = np.random.default_rng(INPLANE_SEED)
        co = rg.standard_normal((N_FLOOR, PC_K))
        ip = co @ PCs
        for i in range(N_FLOOR):
            dirs[f"inplane_{i}"] = (ip[i] / np.linalg.norm(ip[i])).astype(np.float32)
        co2 = rg.standard_normal((N_FLOOR, PC_K)) * pcsd[None, :]
        ipv = co2 @ PCs
        for i in range(N_FLOOR):
            dirs[f"inplanevar_{i}"] = (ipv[i] / np.linalg.norm(ipv[i])).astype(np.float32)
        for i in range(N_PC_ARMS):
            dirs[f"pc_{i}"] = (PCs[i] / np.linalg.norm(PCs[i])).astype(np.float32)
        rg2 = np.random.default_rng(FULLRAND_SEED)
        fr = rg2.standard_normal((N_FLOOR, D))
        for i in range(N_FLOOR):
            dirs[f"fullrand_{i}"] = (fr[i] / np.linalg.norm(fr[i])).astype(np.float32)

        insidef = {n: float(np.sum((PCs @ dirs[n].astype(np.float64)) ** 2))
                   for n in dirs}
        print("  inside top-10 PC span: "
              + f"axes={[round(insidef[f'axis{i}'],4) for i in range(N_AXES)]} "
              + f"inplane={round(float(np.mean([insidef[f'inplane_{i}'] for i in range(N_FLOOR)])),4)} "
              + f"fullrand={round(float(np.mean([insidef[f'fullrand_{i}'] for i in range(N_FLOOR)])),4)}",
              flush=True)
        for n, v in dirs.items():
            assert abs(float(np.linalg.norm(v)) - 1) < 1e-4, n

        base = [fwd(model, tok, dec, t, L, None, 0.0) for t in texts]
        names = list(dirs)
        rows: list[dict[str, Any]] = []
        entry: dict[str, Any] = {
            "layer": L, "axis_split_repro_top3": [float(x) for x in
                                                  np.sort(rp)[::-1][:N_AXES]],
            "axis_ica_k": int(best["k"]), "hidden_dim": D,
            "pca_explained_variance_ratio_top10": [
                round(float(x), 4) for x in pca.explained_variance_ratio_],
            "inside_top10_pc_span": {n: round(insidef[n], 6) for n in dirs},
            "alphas_completed": [], "rows": rows}
        layers_out.append(entry)

        for al in ALPHAS:
            jsv: dict[str, list[float]] = {n: [] for n in names}
            dg: dict[str, list[float]] = {n: [] for n in names}
            for si, t in enumerate(texts):
                aa = al * norms[si]
                b = base[si]
                for pol in (1.0, -1.0):
                    for n in names:
                        m = fwd(model, tok, dec, t, L, dirs[n] * pol, aa)
                        jsv[n].append(js(m, b))
                        er = m["H"] / b["H"] if b["H"] > 0 else float("nan")
                        dg[n].append(1.0 if (m["top1"] >= DEGEN_TOP1 or
                                             (not math.isnan(er) and
                                              (er <= DEGEN_LO or er >= DEGEN_HI)))
                                     else 0.0)
                if (si + 1) % 10 == 0:
                    print(f"    L{L} a={al} {si+1}/{len(texts)}", flush=True)
            ns = len(jsv[names[0]])
            floors = {
                "inplane": [float(np.mean([jsv[f"inplane_{i}"][j]
                                           for i in range(N_FLOOR)]))
                            for j in range(ns)],
                "inplanevar": [float(np.mean([jsv[f"inplanevar_{i}"][j]
                                              for i in range(N_FLOOR)]))
                               for j in range(ns)],
                "fullrand": [float(np.mean([jsv[f"fullrand_{i}"][j]
                                            for i in range(N_FLOOR)]))
                             for j in range(ns)],
                "pc": [float(np.mean([jsv[f"pc_{i}"][j]
                                      for i in range(N_PC_ARMS)]))
                       for j in range(ns)]}
            row: dict[str, Any] = {"layer": L, "alpha_rel": al, "n_samples": ns}
            for n in names:
                row[f"js_{n}_mean"] = ms(jsv[n])[0]
                row[f"degenerate_frac_{n}"] = float(np.mean(dg[n]))
            for fn_, fv in floors.items():
                row[f"js_floor_{fn_}_mean"] = ms(fv)[0]
            for i in range(N_AXES):
                for fn_, fv in floors.items():
                    row[f"paired_axis{i}_vs_{fn_}"] = paired(jsv[f"axis{i}"], fv)
            for i in range(N_PC_ARMS):
                row[f"paired_pc{i}_vs_inplane"] = paired(jsv[f"pc_{i}"],
                                                         floors["inplane"])
                row[f"paired_pc{i}_vs_fullrand"] = paired(jsv[f"pc_{i}"],
                                                          floors["fullrand"])
            rows.append(row)
            entry["alphas_completed"].append(al)
            out.write_text(json.dumps(
                {"env": env({"prereg_commit": a.prereg_commit,
                             "status": "IN_PROGRESS", "partial_layer": L,
                             "partial_alphas": entry["alphas_completed"]}),
                 "layers": layers_out}, indent=2, ensure_ascii=False))
            print(f"    flushed (L{L} a={al})", flush=True)
        print(f"  layer {L} done", flush=True)

    np.savez_compressed(cache_path, **cache)
    print(f"\ncached E4 held-out activations -> {cache_path}", flush=True)

    # BH over the primary family: axis vs in-plane, 4 layers x 3 axes x 5 alphas
    fam: list[dict[str, Any]] = []
    for Lo in layers_out:
        for r in Lo["rows"]:
            for i in range(N_AXES):
                fam.append(r[f"paired_axis{i}_vs_inplane"])
    for t, q in zip(fam, bh([x["wilcoxon_p"] for x in fam])):
        t["wilcoxon_q_bh"] = q
    for Lo in layers_out:
        for r in Lo["rows"]:
            for i in range(N_AXES):
                for fn_ in ("inplanevar", "fullrand", "pc"):
                    k = f"paired_axis{i}_vs_{fn_}"
                    r[k]["wilcoxon_q_bh_sameFamilySize"] = r[k]["wilcoxon_p"]

    verdict: list[dict[str, Any]] = []
    for Lo in layers_out:
        for i in range(N_AXES):
            cells = []
            for r in Lo["rows"]:
                if r["alpha_rel"] < 0.03:
                    continue
                t = r[f"paired_axis{i}_vs_inplane"]
                if (t["mean_diff"] > 0 and t["wilcoxon_q_bh"] < 0.05
                        and r[f"degenerate_frac_axis{i}"] < DEGEN_MAX):
                    cells.append({"alpha_rel": r["alpha_rel"],
                                  "cliffs_delta": t["cliffs_delta"],
                                  "q": t["wilcoxon_q_bh"]})
            verdict.append({"layer": Lo["layer"], "axis": i,
                            "beats_inplane": bool(cells), "cells": cells})
    n_pass = sum(1 for v in verdict if v["beats_inplane"])
    final = {"env": env({"prereg_commit": a.prereg_commit, "status": "COMPLETE",
                         "primary_bh_family_size": len(fam)}),
             "PRIMARY_VERDICT": {
                 "n_axis_cells_beating_inplane": n_pass,
                 "n_axis_cells_total": len(verdict),
                 "criterion_met": bool(n_pass > 0),
                 "per_axis": verdict,
                 "NOTE": ("prereg 26.3: failing this means the effect is explained "
                          "by high-variance directionality")},
             "layers": layers_out}
    out.write_text(json.dumps(final, indent=2, ensure_ascii=False))
    print(f"\nPRIMARY: {n_pass}/{len(verdict)} axis-cells beat the in-plane floor")
    print(f"FINAL -> {out}")
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
