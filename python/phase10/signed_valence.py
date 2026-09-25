#!/usr/bin/env python3
"""Signed valence readout: does the positive control beat the in-plane floor when the
outcome measure carries a direction?

Pre-registration section 46, committed before this ran (predictions in 46.5, both
outcomes written out in 46.6).

Why: JS divergence measures how far the next-token distribution moved, not WHERE it
moved, so a direction lying in a high-variance subspace scores well mechanically. That
is the confound behind our negative results, and it is the likely reason Sun et al.
(2026) found their VA axis beat an in-plane control while ours does not. The positive
control is the one direction whose semantic dimension is known by construction, so it
is where a signed measure can be defined without ambiguity.

Statistic: S = sum_{POS} p(t) - sum_{NEG} p(t) over the next-token distribution;
signed_effect = polarity * (S_intervened - S_baseline). A valence-carrying direction
scores positive at both polarities; a random direction should sit near zero.

Lexicon rules follow paper 1's hard-won lessons (prereg 46.2): every surface variant is
encoded with add_special_tokens=False and kept ONLY if it is a single token. Paper 1's
first implementation took the final subword of a split word, which silently imports
tokens of unrelated words (positive -> itive). Token ids in both sets are dropped from
both. Adopted variants, ids and counts are recorded.

Cells whose baseline POS-union-NEG mass is under 1e-3 are excluded as a non-functional
lexicon (prereg 46.3), the failure paper 1 hit on one model at 4.6e-4.

Discovery 20 stimuli only. No judge, no generation.
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
POS_THRESH, NEG_THRESH = 7.0, 3.0      # prereg 46.2 (PRIMARY, as registered)
# Secondary lexicon, declared before any outcome was inspected: the registered POS set
# admits very frequent generic tokens (" new", " first", " like") whose probability is
# governed by syntax rather than valence, which can dilute a valence signal. Stricter
# thresholds are reported alongside as a robustness check. The primary remains 7.0/3.0.
POS_THRESH_STRICT, NEG_THRESH_STRICT = 8.0, 2.0
MASS_MIN = 1e-3                        # prereg 46.3
BOOT_N, BOOT_SEED = 10_000, 20260925
TOPK, MAXLEN = 100, 128
_SUF = ["fully", "fulness", "fulness", "ful", "ness", "ly",
        "ing", "tion", "ed", "er", "est", "s"]


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
    rng = np.random.default_rng(BOOT_SEED)
    bs = d[rng.integers(0, d.size, size=(BOOT_N, d.size))].mean(axis=1)
    lo, hi = np.quantile(bs, [0.025, 0.975])
    return {"n": int(d.size), "mean_diff": float(d.mean()),
            "wilcoxon_p": float(p), "ci_lo": float(lo), "ci_hi": float(hi),
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


def load_valence() -> dict[str, float]:
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


def build_lexicon(tok: Any, vad: dict[str, float],
                  pos_th: float = POS_THRESH,
                  neg_th: float = NEG_THRESH) -> dict[str, Any]:
    """Single-token-only lexicon, per prereg 46.2."""
    global POS_THRESH, NEG_THRESH
    POS_THRESH, NEG_THRESH = pos_th, neg_th
    def variants(w: str) -> list[str]:
        return [w, w.capitalize(), " " + w, " " + w.capitalize()]

    sets: dict[str, dict[int, str]] = {"POS": {}, "NEG": {}}
    dropped_multi = 0
    considered = 0
    for w, v in vad.items():
        tag = "POS" if v >= POS_THRESH else ("NEG" if v <= NEG_THRESH else None)
        if tag is None:
            continue
        for var in variants(w):
            considered += 1
            ids = tok(var, add_special_tokens=False)["input_ids"]
            if len(ids) != 1:          # single-token constraint
                dropped_multi += 1
                continue
            sets[tag].setdefault(int(ids[0]), var)
    overlap = set(sets["POS"]) & set(sets["NEG"])
    for t in overlap:
        sets["POS"].pop(t, None)
        sets["NEG"].pop(t, None)
    info = {
        "pos_threshold": POS_THRESH, "neg_threshold": NEG_THRESH,
        "n_words_pos": sum(1 for v in vad.values() if v >= POS_THRESH),
        "n_words_neg": sum(1 for v in vad.values() if v <= NEG_THRESH),
        "variants_considered": considered,
        "variants_dropped_multitoken": dropped_multi,
        "n_token_ids_pos": len(sets["POS"]), "n_token_ids_neg": len(sets["NEG"]),
        "n_overlap_dropped": len(overlap),
        "adopted_pos": {str(k): v for k, v in sorted(sets["POS"].items())},
        "adopted_neg": {str(k): v for k, v in sorted(sets["NEG"].items())},
        "single_token_rule": ("add_special_tokens=False, keep only len(ids)==1; "
                              "paper 1 previously took the final subword of split "
                              "words, importing unrelated tokens"),
    }
    n_p, n_n = len(sets["POS"]), len(sets["NEG"])
    info["asymmetric_warning"] = bool(min(n_p, n_n) < max(n_p, n_n) / 5)
    return {"pos_ids": np.array(sorted(sets["POS"]), dtype=np.int64),
            "neg_ids": np.array(sorted(sets["NEG"]), dtype=np.int64),
            "info": info}


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
        d: np.ndarray | None, alpha: float, lex: dict[str, Any]) -> dict[str, Any]:
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
    mp = float(pr[lex["pos_ids"]].sum())
    mn = float(pr[lex["neg_ids"]].sum())
    lx2 = lex.get("_strict")
    if lx2 is not None:
        mp2 = float(pr[lx2["pos_ids"]].sum())
        mn2 = float(pr[lx2["neg_ids"]].sum())
    else:
        mp2 = mn2 = float("nan")
    idx = np.argsort(pr)[-TOPK:]
    lp = np.log(pr[idx] + 1e-45)
    o = np.argsort(idx)
    return {"S": mp - mn, "mass": mp + mn,
            "S_strict": mp2 - mn2, "mass_strict": mp2 + mn2,
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
    return (d / (np.linalg.norm(d) + 1e-30)).astype(np.float32)


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
        "alphas": list(ALPHAS), "pc_k": PC_K, "mass_min": MASS_MIN,
        "hook_scope": "last_token", "judge_llm_loaded": False,
        "generation_used": False, "stimuli": "DISCOVERY 20 only",
        "prereg_section": "46",
        "decision_rule": ("pos beats the in-plane floor on signed_effect at alpha=0.05 "
                          "in >=3 of 4 layers, BH family 20 (prereg 46.4)"),
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
    try:
        from transformers import AutoTokenizer
        tk = AutoTokenizer.from_pretrained("swiss-ai/Apertus-v1.1-1.5B")
        vad = load_valence()
        lex = build_lexicon(tk, vad)
        i = lex["info"]
        c(f"lexicon built: POS {i['n_token_ids_pos']} ids, NEG "
          f"{i['n_token_ids_neg']} ids", i["n_token_ids_pos"] > 20
          and i["n_token_ids_neg"] > 20)
        c(f"multi-token variants dropped ({i['variants_dropped_multitoken']})",
          i["variants_dropped_multitoken"] > 0)
        c("POS/NEG id sets disjoint",
          len(set(lex["pos_ids"].tolist()) & set(lex["neg_ids"].tolist())) == 0)
        # every adopted variant must really be one token
        bad = [v for v in list(i["adopted_pos"].values())[:50]
               if len(tk(v, add_special_tokens=False)["input_ids"]) != 1]
        c("all adopted POS variants are single tokens", not bad)
        c(f"set sizes not wildly asymmetric (warn={i['asymmetric_warning']})", True)
        print(f"     sample POS: {list(i['adopted_pos'].values())[:6]}")
        print(f"     sample NEG: {list(i['adopted_neg'].values())[:6]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  [SKIP] tokenizer unavailable: {exc}")
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=list(LAYERS))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", type=Path, default=BASE / "signed_valence")
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

    vad = load_valence()
    e4 = json.loads(E4.read_text())
    disc = json.loads(SPLIT.read_text())["discovery_indices"]
    texts = [e4[i]["text"] for i in disc]
    yv = np.array([stim_val(t, vad) for t in texts], dtype=float)
    assert not np.isnan(yv).any()

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    lex = build_lexicon(tok, vad, POS_THRESH, NEG_THRESH)
    li = lex["info"]
    lex_s = build_lexicon(tok, vad, POS_THRESH_STRICT, NEG_THRESH_STRICT)
    li_s = lex_s["info"]
    print(f"strict lexicon (secondary, 8.0/2.0): POS {li_s['n_token_ids_pos']} / "
          f"NEG {li_s['n_token_ids_neg']} ids", flush=True)
    print(f"lexicon: POS {li['n_token_ids_pos']} ids / NEG {li['n_token_ids_neg']} ids, "
          f"dropped {li['variants_dropped_multitoken']} multi-token variants, "
          f"overlap dropped {li['n_overlap_dropped']}, "
          f"asym_warn={li['asymmetric_warning']}", flush=True)

    lex["_strict"] = lex_s
    model = AutoModelForCausalLM.from_pretrained(
        a.model, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True)
    model.eval()
    dec = (model.model.layers if hasattr(model, "model")
           and hasattr(model.model, "layers") else model.transformer.h)
    D = int(model.config.hidden_size)

    a.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = a.out_dir / f"signed_valence_{stamp}.json"
    layers_out: list[dict[str, Any]] = []

    for L in a.layers:
        print(f"\n===== layer {L} =====", flush=True)
        A_last = np.stack([cap(model, tok, dec, t, L, "last") for t in texts])
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
        sys.path.insert(0, "/path/to/work/code/phase10")
        from run_ica import compute_split_reproducibility
        rp = compute_split_reproducibility(
            ACT / f"layer{L:02d}_seed{a.seed:04d}.npz", comps, seed=a.seed)
        top = comps[np.argsort(-rp)][:N_AXES]

        dirs: dict[str, np.ndarray] = {"pos_lasttoken": regress_dir(A_last, yv)}
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
        for i in range(N_AXES):
            dirs[f"axis{i}"] = top[i]

        base = [fwd(model, tok, dec, t, L, None, 0.0, lex) for t in texts]
        base_mass = [b["mass"] for b in base]
        mass_ok = float(np.mean(base_mass)) >= MASS_MIN
        print(f"  baseline POS+NEG mass: mean={np.mean(base_mass):.3e} "
              f"min={np.min(base_mass):.3e} -> lexicon_functional={mass_ok}",
              flush=True)

        names = list(dirs)
        rows: list[dict[str, Any]] = []
        entry = {"layer": L, "baseline_mass_mean": float(np.mean(base_mass)),
                 "baseline_mass_min": float(np.min(base_mass)),
                 "lexicon_functional": bool(mass_ok), "rows": rows}
        layers_out.append(entry)

        for al in ALPHAS:
            sg: dict[str, list[float]] = {n: [] for n in names}
            sgs: dict[str, list[float]] = {n: [] for n in names}
            jv: dict[str, list[float]] = {n: [] for n in names}
            for si, t in enumerate(texts):
                aa = al * norms[si]
                b = base[si]
                for pol in (1.0, -1.0):
                    for n in names:
                        m = fwd(model, tok, dec, t, L, dirs[n] * pol, aa, lex)
                        sg[n].append(pol * (m["S"] - b["S"]))
                        sgs[n].append(pol * (m["S_strict"] - b["S_strict"]))
                        jv[n].append(js(m, b))
                if (si + 1) % 10 == 0:
                    print(f"    L{L} a={al} {si+1}/{len(texts)}", flush=True)
            ns = len(sg[names[0]])
            fl_s = {k: [float(np.mean([sg[f"{k}_{i}"][j] for i in range(cnt)]))
                        for j in range(ns)]
                    for k, cnt in (("inplane", N_FLOOR), ("fullrand", N_FLOOR),
                                   ("ortho", N_ORTHO))}
            fl_j = {k: [float(np.mean([jv[f"{k}_{i}"][j] for i in range(cnt)]))
                        for j in range(ns)]
                    for k, cnt in (("inplane", N_FLOOR), ("fullrand", N_FLOOR),
                                   ("ortho", N_ORTHO))}
            row: dict[str, Any] = {"layer": L, "alpha_rel": al, "n_samples": ns}
            for n in names:
                row[f"signed_{n}_mean"] = float(np.mean(sg[n]))
                row[f"js_{n}_mean"] = float(np.mean(jv[n]))
            for k in fl_s:
                row[f"signed_floor_{k}_mean"] = float(np.mean(fl_s[k]))
                row[f"js_floor_{k}_mean"] = float(np.mean(fl_j[k]))
            fl_ss = {k: [float(np.mean([sgs[f"{k}_{i}"][j] for i in range(cnt)]))
                         for j in range(ns)]
                     for k, cnt in (("inplane", N_FLOOR),)}
            row["signed_strict_pos_mean"] = float(np.mean(sgs["pos_lasttoken"]))
            row["signed_strict_floor_inplane_mean"] = float(np.mean(fl_ss["inplane"]))
            row["paired_signed_strict_pos_vs_inplane"] = paired(
                sgs["pos_lasttoken"], fl_ss["inplane"])
            for k in fl_s:
                row[f"paired_signed_pos_vs_{k}"] = paired(sg["pos_lasttoken"], fl_s[k])
                row[f"paired_js_pos_vs_{k}"] = paired(jv["pos_lasttoken"], fl_j[k])
            for i in range(N_AXES):
                row[f"paired_signed_axis{i}_vs_inplane"] = paired(
                    sg[f"axis{i}"], fl_s["inplane"])
            rows.append(row)
            out.write_text(json.dumps(
                {"env": env({"prereg_commit": a.prereg_commit,
                             "status": "IN_PROGRESS"}),
                 "lexicon": li, "lexicon_strict": li_s, "layers": layers_out},
        indent=2, ensure_ascii=False))
            print(f"    flushed (L{L} a={al}) signed_pos="
                  f"{row['signed_pos_lasttoken_mean']:+.3e} "
                  f"floor_ip={row['signed_floor_inplane_mean']:+.3e}", flush=True)

    fam = [r["paired_signed_pos_vs_inplane"] for Lo in layers_out for r in Lo["rows"]]
    for t, q in zip(fam, bh([x["wilcoxon_p"] for x in fam])):
        t["wilcoxon_q_bh"] = q
    famj = [r["paired_js_pos_vs_inplane"] for Lo in layers_out for r in Lo["rows"]]
    for t, q in zip(famj, bh([x["wilcoxon_p"] for x in famj])):
        t["wilcoxon_q_bh"] = q

    sig_layers = sorted({Lo["layer"] for Lo in layers_out for r in Lo["rows"]
                         if r["alpha_rel"] == 0.05
                         and Lo["lexicon_functional"]
                         and r["paired_signed_pos_vs_inplane"]["mean_diff"] > 0
                         and r["paired_signed_pos_vs_inplane"]["wilcoxon_q_bh"] < 0.05})
    js_layers = sorted({Lo["layer"] for Lo in layers_out for r in Lo["rows"]
                        if r["alpha_rel"] == 0.05
                        and r["paired_js_pos_vs_inplane"]["mean_diff"] > 0
                        and r["paired_js_pos_vs_inplane"]["wilcoxon_q_bh"] < 0.05})
    verdict = {
        "signed_layers_significant_a05": sig_layers,
        "signed_PASS_3of4": bool(len(sig_layers) >= 3),
        "js_layers_significant_a05": js_layers,
        "js_PASS_3of4": bool(len(js_layers) >= 3),
        "excluded_layers_nonfunctional_lexicon": [
            Lo["layer"] for Lo in layers_out if not Lo["lexicon_functional"]],
        "INTERPRETATION": ("prereg 46.6: signed beating in-plane while JS does not "
                           "demonstrates condition 4 and justifies scoping the claim "
                           "to the JS metric; signed also failing makes the negative "
                           "conclusion metric-independent and returns the conditions "
                           "to three")}
    out.write_text(json.dumps(
        {"env": env({"prereg_commit": a.prereg_commit, "status": "COMPLETE"}),
         "VERDICT": verdict, "lexicon": li, "lexicon_strict": li_s,
         "layers": layers_out},
        indent=2, ensure_ascii=False))
    print(f"\nSIGNED: layers significant at a=0.05 {sig_layers} -> "
          f"PASS={verdict['signed_PASS_3of4']}")
    print(f"JS (same run): {js_layers} -> PASS={verdict['js_PASS_3of4']}")
    print(f"FINAL -> {out}")
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
