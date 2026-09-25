#!/usr/bin/env python3
"""Retest the positive control against the in-plane random floor.

Pre-registration section 29, committed before this ran (prediction in 29.4, and the
rule in 29.3 for telling "the metric lacks resolution" from "the in-plane floor is
simply strong").

The positive control is the stated precondition for interpreting anything, and its
direction lies 58-77 percent inside the top-10 PC span, so its passing at all four
layers against a FULL-space floor is subject to the same confound that sank the axes.

Only the floor changes. Arms per layer:
  pos_lasttoken   Warriner valence regressed from last-token activations (regress_dir)
  pos_meanpool    same but mean-pooled, the older variant, for reference
  inplane_0..4    PRIMARY floor: uniform on the unit sphere of the top-10 PC span
  fullrand_0..4   the historical full-space floor - also the DISCRIMINATOR in 29.3
  ortho_0..2      axis-orthogonal floor

Discovery 20 stimuli only; the confirmation set is not read. No judge, no generation.
Flushed after every alpha.
"""
from __future__ import annotations

import argparse
import csv
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
from typing import Any, Sequence

_CVD = os.environ.get("CUDA_VISIBLE_DEVICES")

import numpy as np  # noqa: E402
from scipy import stats as sp_stats  # noqa: E402

BASE = Path("/path/to/work/results")
SLUG = "swiss-ai__Apertus-v1_1-1_5B"
ACT = BASE / "activations_nopad" / SLUG
ICA = BASE / "ica_nopad" / SLUG
SPLIT = BASE / "axes_nopad" / "axis_rebuilt_split_20260925.json"
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
VADP = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
LAYERS = (5, 7, 10, 12)
ALPHAS = (0.01, 0.03, 0.05, 0.10, 0.20)
PC_K = 10
INPLANE_SEED = 42 + 31337
FULLRAND_SEED = 42 + 9999
N_FLOOR, N_ORTHO, N_AXES = 5, 3, 3
BOOT_N, BOOT_SEED = 10_000, 20260925
TOPK, MAXLEN = 100, 128
DEGEN_TOP1, DEGEN_LO, DEGEN_HI, DEGEN_MAX = 0.95, 0.5, 2.0, 0.20
_SUF = ["fully", "fulness", "fulness", "ful", "ness", "ly",
        "ing", "tion", "ed", "er", "est", "s"]


def boot_ci(v: Sequence[float]) -> tuple[float, float]:
    a = np.asarray([x for x in v if not math.isnan(x)], float)
    if a.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(BOOT_SEED)
    m = a[rng.integers(0, a.size, size=(BOOT_N, a.size))].mean(axis=1)
    lo, hi = np.quantile(m, [0.025, 0.975])
    return (float(lo), float(hi))


def paired(a: Sequence[float], b: Sequence[float]) -> dict[str, float]:
    pr = [(x, y) for x, y in zip(a, b) if not (math.isnan(x) or math.isnan(y))]
    if len(pr) < 2:
        return {"n": len(pr), "mean_diff": float("nan"),
                "wilcoxon_p": float("nan"), "cliffs_delta": float("nan")}
    xa = np.array([p[0] for p in pr], float)
    xb = np.array([p[1] for p in pr], float)
    d = xa - xb
    if np.allclose(d, 0.0):
        p = 1.0
    else:
        try:
            _, p = sp_stats.wilcoxon(xa, xb, alternative="greater",
                                     zero_method="zsplit")
        except ValueError:
            p = float("nan")
    lo, hi = boot_ci(d.tolist())
    return {"n": int(d.size), "mean_diff": float(d.mean()),
            "wilcoxon_p": float(p), "ci_lo": lo, "ci_hi": hi,
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


def ms(v: Sequence[float]) -> float:
    a = np.asarray([x for x in v if not math.isnan(x)], float)
    return float(a.mean()) if a.size else float("nan")


def load_vad() -> dict[str, float]:
    out: dict[str, float] = {}
    with open(VADP, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = row.get("word", "").strip().lower()
            try:
                out[w] = float(row.get("valence", "").strip())
            except (ValueError, AttributeError):
                pass
    return out


def stim_val(t: str, vad: dict[str, float]) -> float | None:
    def look(w: str) -> float | None:
        if w in vad:
            return vad[w]
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                return vad[w[: -len(s)]]
        return None
    h = [x for x in (look(w) for w in re.findall(r"[a-zA-Z']+", t.lower()))
         if x is not None]
    return float(np.mean(h)) if h else None


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
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAXLEN)
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
    idx = np.argsort(pr)[-TOPK:]
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


def cap(model: Any, tok: Any, dec: Any, text: str, layer: int,
        pooling: str = "last") -> np.ndarray:
    import torch
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAXLEN)
    dev = next(model.parameters()).device
    enc = {k: v.to(dev) for k, v in enc.items()}
    got: list[np.ndarray] = []

    def hk(m: Any, i: Any, o: Any) -> None:
        hs = o[0] if isinstance(o, tuple) else o
        hf = hs.float()
        got.append((hf[0, -1] if pooling == "last"
                    else hf.mean(dim=1).squeeze(0)).cpu().numpy())
    h = dec[layer].register_forward_hook(hk)
    try:
        with torch.no_grad():
            model(**enc)
    finally:
        h.remove()
    return got[0]


def regress_dir(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    yz = (y - y.mean()) / (y.std() + 1e-8)
    d = X.astype(np.float64).T @ yz
    n = float(np.linalg.norm(d))
    if n < 1e-12:
        raise RuntimeError("near-zero")
    return (d / n).astype(np.float32)


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
        "hostname": platform.node(), "CUDA_VISIBLE_DEVICES": _CVD,
        "gpu_uuid_visible_physical": [um.get(i.strip(), "?")
                                      for i in (_CVD or "").split(",") if i.strip()],
        "pc_k_FIXED": PC_K, "inplane_seed": INPLANE_SEED,
        "fullrand_seed": FULLRAND_SEED, "alphas": list(ALPHAS),
        "hook_scope": "last_token", "judge_llm_loaded": False,
        "generation_used": False,
        "stimuli": "DISCOVERY 20 only (confirmation not read)",
        "note_vs_original": ("the original positive control used all 40 E4 stimuli, "
                             "so JS magnitudes are not directly comparable; what is "
                             "comparable is pos against each floor within this run"),
        "discriminator_rule": ("prereg 29.3: if pos fails against in-plane but beats "
                              "full-space, the metric resolves pos from random and "
                              "the in-plane floor is simply strong (reading b); if "
                              "pos also fails against full-space, the metric lacks "
                              "resolution (reading a)"),
        "prereg_section": "29",
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
    vad = load_vad()
    if vad and SPLIT.exists():
        e4 = json.loads(E4.read_text())
        disc = json.loads(SPLIT.read_text())["discovery_indices"]
        vals = [stim_val(e4[i]["text"], vad) for i in disc]
        c(f"all {len(disc)} discovery stimuli have valence",
          all(v is not None for v in vals))
        v = np.array([x for x in vals if x is not None])
        c("valence separates polarity on the discovery set",
          v[:10].mean() > v[10:].mean())
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=list(LAYERS))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", type=Path, default=BASE / "pos_ctrl_inplane")
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

    vad = load_vad()
    e4 = json.loads(E4.read_text())
    disc = json.loads(SPLIT.read_text())["discovery_indices"]
    texts = [e4[i]["text"] for i in disc]
    yv = np.array([stim_val(t, vad) for t in texts], dtype=float)
    assert not np.isnan(yv).any(), "a discovery stimulus has no valence"
    print(f"discovery n={len(texts)}, valence range {yv.min():.2f}-{yv.max():.2f}")

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

    a.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = a.out_dir / f"pos_ctrl_inplane_{stamp}.json"
    layers_out: list[dict[str, Any]] = []

    for L in a.layers:
        print(f"\n===== layer {L} =====", flush=True)
        A_last = np.stack([cap(model, tok, dec, t, L, "last") for t in texts])
        A_mean = np.stack([cap(model, tok, dec, t, L, "meanpool") for t in texts])
        norms = np.linalg.norm(A_last, axis=1)

        X1 = np.load(ACT / f"layer{L:02d}_seed{a.seed:04d}.npz",
                     allow_pickle=True)["arr"].astype(np.float32)
        PCs = PCA(n_components=PC_K, random_state=a.seed).fit(
            X1.astype(np.float64)).components_

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

        dirs: dict[str, np.ndarray] = {
            "pos_lasttoken": regress_dir(A_last, yv),
            "pos_meanpool": regress_dir(A_mean, yv)}
        rg = np.random.default_rng(INPLANE_SEED)
        ip = rg.standard_normal((N_FLOOR, PC_K)) @ PCs
        for i in range(N_FLOOR):
            dirs[f"inplane_{i}"] = (ip[i] / np.linalg.norm(ip[i])).astype(np.float32)
        rg2 = np.random.default_rng(FULLRAND_SEED)
        fr = rg2.standard_normal((N_FLOOR, D))
        for i in range(N_FLOOR):
            dirs[f"fullrand_{i}"] = (fr[i] / np.linalg.norm(fr[i])).astype(np.float32)
        for i in range(N_ORTHO):
            v = fr[i].copy()
            v -= top[i] * float(np.dot(v, top[i]))
            dirs[f"ortho_{i}"] = (v / np.linalg.norm(v)).astype(np.float32)

        inside = {n: float(np.sum((PCs @ dirs[n].astype(np.float64)) ** 2))
                  for n in dirs}
        print(f"  inside top-10 PC span: pos_lasttoken={inside['pos_lasttoken']:.4f} "
              f"pos_meanpool={inside['pos_meanpool']:.4f} "
              f"inplane={np.mean([inside[f'inplane_{i}'] for i in range(N_FLOOR)]):.4f} "
              f"fullrand={np.mean([inside[f'fullrand_{i}'] for i in range(N_FLOOR)]):.4f}",
              flush=True)
        for n, v in dirs.items():
            assert abs(float(np.linalg.norm(v)) - 1) < 1e-4, n

        base = [fwd(model, tok, dec, t, L, None, 0.0) for t in texts]
        names = list(dirs)
        rows: list[dict[str, Any]] = []
        entry = {"layer": L, "inside_top10_pc_span": {n: round(inside[n], 6)
                                                     for n in dirs},
                 "n_pos_fit": len(texts), "alphas_completed": [], "rows": rows}
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
                "fullrand": [float(np.mean([jsv[f"fullrand_{i}"][j]
                                            for i in range(N_FLOOR)]))
                             for j in range(ns)],
                "ortho": [float(np.mean([jsv[f"ortho_{i}"][j]
                                         for i in range(N_ORTHO)]))
                          for j in range(ns)]}
            row: dict[str, Any] = {"layer": L, "alpha_rel": al, "n_samples": ns}
            for n in names:
                row[f"js_{n}_mean"] = ms(jsv[n])
                row[f"degenerate_frac_{n}"] = float(np.mean(dg[n]))
            for fn_, fv in floors.items():
                row[f"js_floor_{fn_}_mean"] = ms(fv)
            for pn in ("pos_lasttoken", "pos_meanpool"):
                for fn_, fv in floors.items():
                    row[f"paired_{pn}_vs_{fn_}"] = paired(jsv[pn], fv)
            rows.append(row)
            entry["alphas_completed"].append(al)
            out.write_text(json.dumps(
                {"env": env({"prereg_commit": a.prereg_commit,
                             "status": "IN_PROGRESS", "partial_layer": L}),
                 "layers": layers_out}, indent=2, ensure_ascii=False))
            print(f"    flushed (L{L} a={al})", flush=True)

    # BH within the primary family: pos_lasttoken vs inplane, 4 layers x 5 alphas
    fam = [r["paired_pos_lasttoken_vs_inplane"] for Lo in layers_out
           for r in Lo["rows"]]
    for t, q in zip(fam, bh([x["wilcoxon_p"] for x in fam])):
        t["wilcoxon_q_bh"] = q
    famf = [r["paired_pos_lasttoken_vs_fullrand"] for Lo in layers_out
            for r in Lo["rows"]]
    for t, q in zip(famf, bh([x["wilcoxon_p"] for x in famf])):
        t["wilcoxon_q_bh"] = q

    def passes(key: str) -> list[dict[str, Any]]:
        got = []
        for Lo in layers_out:
            for r in Lo["rows"]:
                if r["alpha_rel"] < 0.03:
                    continue
                t = r[key]
                if (t["mean_diff"] > 0 and t.get("wilcoxon_q_bh", 1) < 0.05
                        and r["degenerate_frac_pos_lasttoken"] < DEGEN_MAX):
                    got.append({"layer": Lo["layer"], "alpha_rel": r["alpha_rel"],
                                "cliffs_delta": t["cliffs_delta"],
                                "q": t["wilcoxon_q_bh"]})
        return got

    ip_pass = passes("paired_pos_lasttoken_vs_inplane")
    fr_pass = passes("paired_pos_lasttoken_vs_fullrand")
    a05 = [{"layer": Lo["layer"],
            "vs_inplane_delta": r["paired_pos_lasttoken_vs_inplane"]["cliffs_delta"],
            "vs_inplane_q": r["paired_pos_lasttoken_vs_inplane"].get("wilcoxon_q_bh"),
            "vs_fullrand_delta": r["paired_pos_lasttoken_vs_fullrand"]["cliffs_delta"],
            "vs_fullrand_q": r["paired_pos_lasttoken_vs_fullrand"].get("wilcoxon_q_bh")}
           for Lo in layers_out for r in Lo["rows"] if r["alpha_rel"] == 0.05]
    reading = ("b_inplane_floor_is_strong_metric_has_resolution" if fr_pass
               else "a_metric_lacks_resolution")
    verdict = {"pos_beats_inplane_cells": ip_pass,
               "pos_beats_inplane": bool(ip_pass),
               "pos_beats_fullrand_cells": fr_pass,
               "pos_beats_fullrand": bool(fr_pass),
               "alpha_0.05_detail": a05,
               "DISCRIMINATOR_READING": reading,
               "RULE": ("prereg 29.3: pos beating in-plane confirms the axes' loss "
                        "is meaningful; pos failing in-plane but beating full-space "
                        "is reading b, so the negative conclusion stands; pos "
                        "failing both is reading a and the framing must be rebuilt")}
    out.write_text(json.dumps(
        {"env": env({"prereg_commit": a.prereg_commit, "status": "COMPLETE"}),
         "VERDICT": verdict, "layers": layers_out}, indent=2, ensure_ascii=False))
    print(f"\npos beats in-plane: {bool(ip_pass)} ({len(ip_pass)} cells)")
    print(f"pos beats full-space: {bool(fr_pass)} ({len(fr_pass)} cells)")
    print(f"DISCRIMINATOR: {reading}")
    print(f"FINAL -> {out}")
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
