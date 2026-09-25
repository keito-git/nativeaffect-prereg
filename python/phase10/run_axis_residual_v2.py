#!/usr/bin/env python3
"""Residual-axis test v2: degeneracy guard, 3-tier human subspace, valence arm.

Implements Amendment 2 (prereg §12), which was committed before this ran.
DISCOVERY SET ONLY. The confirmation set is never read by this script.

What is new versus run_axis_residual_sweep.py
---------------------------------------------
Q2 (§12.1) The perplexity ratio is structurally insensitive to a last-token-only
    intervention, so it measured nothing and sat at 1.00. It is still emitted as
    a reference value but NEVER used for a decision. The degeneracy guard M3' now
    reads the intervened position itself: top1_prob and entropy_ratio.
    A sample is degenerate if top1_prob >= 0.95 or entropy_ratio <= 0.5 or
    entropy_ratio >= 2.0; a cell needs degenerate_frac < 0.20.

Q3 (§12.2) Three human subspaces, all reported, S1 remaining the primary:
      S1  V/A/D regressed on the 20 discovery E4 stimuli   (pre-registered)
      S2  V/A/D regressed on the 300 E1 sentences          (same 3 dims,
          effective rank 3 instead of 1 -- no dimensions added)
      S3  S2 plus 20 one-vs-rest emotion-category directions fitted on the
          held-out E4 indices 40-79 (used by no intervention experiment and not
          the confirmation set)
    Category directions are NOT fitted on the discovery set: it holds exactly one
    stimulus per category, so its one-vs-rest indicators span the full row space
    of those activations and the test would be vacuous by construction.
    Effective rank and per-axis residual norm ratio are mandatory outputs for
    every tier, because enlarging the subspace mechanically drives residuals to
    zero and would manufacture a "restatement" verdict.

Q4 (§12.3) The human valence direction is injected as its own arm at exactly the
    same per-stimulus ratio as the axes, to test directly whether it is weak
    (V1: comparable to the random floor, q>=0.05 and |Cliff's delta|<0.33) and
    weaker than the axes (V2). Arousal and dominance arms are added as
    descriptive companions so no metric is selectively withheld.

No judge LLM is loaded (PI directive). No generation (stage 1).
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

BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 20260925
RAND_SEED_OFFSET = 9999
N_RAND = 5
N_AXES = 3
TOP_K_VOCAB = 100
MAX_LENGTH = 128
ALPHAS = (0.01, 0.03, 0.05, 0.10, 0.20)
PPL_REF_ONLY = 3.0
DEGEN_TOP1 = 0.95
DEGEN_ENT_LO = 0.5
DEGEN_ENT_HI = 2.0
DEGEN_FRAC_MAX = 0.20
CLIFF_COMPARABLE = 0.33
KEYS = ("valence", "arousal", "dominance")
BASE = Path("/path/to/work/results")
VAD_PATH = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
ICA_DIR = BASE / "ica_nopad"
ACT_DIR = BASE / "activations_nopad"
SPLIT_PATH = BASE / "axes_nopad" / "axis_rebuilt_split_20260925.json"
E1_PATH = Path("/path/to/work/code/stimuli/stimuli_e1.json")
TIERS = ("S1", "S2", "S3")
_SUF = ["fully", "fulness", "fulness", "ful", "ness", "ly",
        "ing", "tion", "ed", "er", "est", "s"]


# ============================ statistics =================================
def bootstrap_ci_mean(v: Sequence[float], n_boot: int = BOOTSTRAP_N,
                      seed: int = BOOTSTRAP_SEED,
                      alpha: float = 0.05) -> tuple[float, float]:
    a = np.asarray([x for x in v if not math.isnan(x)], float)
    if a.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    m = a[rng.integers(0, a.size, size=(n_boot, a.size))].mean(axis=1)
    lo, hi = np.quantile(m, [alpha / 2.0, 1.0 - alpha / 2.0])
    return (float(lo), float(hi))


def paired_test(a: Sequence[float], b: Sequence[float],
                alternative: str = "greater") -> dict[str, float]:
    pr = [(x, y) for x, y in zip(a, b)
          if not (math.isnan(x) or math.isnan(y))]
    if len(pr) < 2:
        return {"n": len(pr), "mean_diff": float("nan"), "std_diff": float("nan"),
                "wilcoxon_p": float("nan"), "ci_lo": float("nan"),
                "ci_hi": float("nan"), "cliffs_delta": float("nan")}
    xa = np.array([p[0] for p in pr], float)
    xb = np.array([p[1] for p in pr], float)
    d = xa - xb
    if np.allclose(d, 0.0):
        p = 1.0
    else:
        try:
            _, p = sp_stats.wilcoxon(xa, xb, alternative=alternative,
                                     zero_method="zsplit")
        except ValueError:
            p = float("nan")
    lo, hi = bootstrap_ci_mean(d.tolist())
    return {"n": int(d.size), "mean_diff": float(d.mean()),
            "std_diff": float(d.std(ddof=1)), "wilcoxon_p": float(p),
            "ci_lo": lo, "ci_hi": hi,
            "cliffs_delta": float((d > 0).mean() - (d < 0).mean())}


def bh_fdr(pv: Sequence[float]) -> list[float]:
    arr = np.asarray(pv, float)
    ok = ~np.isnan(arr)
    out = np.full(arr.shape, np.nan)
    p = arr[ok]
    if p.size == 0:
        return out.tolist()
    o = np.argsort(p)
    m = p.size
    adj = p[o] * m / (np.arange(m) + 1)
    adj = np.clip(np.minimum.accumulate(adj[::-1])[::-1], 0.0, 1.0)
    r = np.empty(m)
    r[o] = adj
    out[ok] = r
    return out.tolist()


def mean_std(v: Sequence[float]) -> tuple[float, float]:
    a = np.asarray([x for x in v if not math.isnan(x)], float)
    if a.size == 0:
        return (float("nan"), float("nan"))
    return (float(a.mean()), float(a.std(ddof=1)) if a.size > 1 else 0.0)


# ============================ Warriner ===================================
def load_vad(path: Path = VAD_PATH) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = row.get("word", "").strip().lower()
            if not w:
                continue
            try:
                out[w] = {k: float(row[k].strip()) for k in KEYS}
            except (KeyError, ValueError, AttributeError):
                continue
    return out


def stimulus_vad(text: str, vad: dict[str, dict[str, float]]) -> dict | None:
    """Suffix stripping is essential (2298-word list: 'joyful' absent, 'joy'
    present). Dropping it silently removes every positive stimulus."""
    def look(w: str) -> dict[str, float] | None:
        if w in vad:
            return vad[w]
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                return vad[w[: -len(s)]]
        return None
    hits = [h for h in (look(w) for w in re.findall(r"[a-zA-Z']+", text.lower()))
            if h is not None]
    if not hits:
        return None
    return {k: float(np.mean([h[k] for h in hits])) for k in KEYS}


# ============================ hooks / metrics ============================
class Hook:
    def __init__(self, direction: np.ndarray, alpha: float) -> None:
        import torch
        self.delta = torch.tensor(alpha * direction, dtype=torch.float16)

    def __call__(self, module: Any, inputs: tuple, output: Any) -> Any:
        hs = output[0] if isinstance(output, tuple) else output
        d = self.delta.to(hs.device).to(hs.dtype)
        m = hs.clone()
        m[:, -1, :] = m[:, -1, :] + d
        return (m,) + output[1:] if isinstance(output, tuple) else m


def forward_metrics(model: Any, tok: Any, dec: Any, text: str, layer: int,
                    direction: np.ndarray | None, alpha: float,
                    top_k: int = TOP_K_VOCAB) -> dict[str, Any]:
    import torch
    import torch.nn.functional as F
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAX_LENGTH)
    dev = next(model.parameters()).device
    enc = {k: v.to(dev) for k, v in enc.items()}
    h = None
    if direction is not None:
        h = dec[layer].register_forward_hook(Hook(direction, alpha))
    try:
        with torch.no_grad():
            logits = model(**enc).logits
    finally:
        if h is not None:
            h.remove()
    probs = F.softmax(logits[0, -1, :].float(), dim=-1).cpu().numpy()
    pp = probs[probs > 0]
    idx = np.argsort(probs)[-top_k:]
    lp = np.log(probs[idx] + 1e-45)
    o = np.argsort(idx)
    ids = enc["input_ids"][0]
    if ids.shape[0] > 1:
        nll = F.cross_entropy(logits[0, :-1, :].float(), ids[1:], reduction="mean")
        ppl = float(torch.exp(nll).item())
    else:
        ppl = float("nan")
    return {"entropy_nats": float(-np.sum(pp * np.log(pp))),
            "top1_prob": float(probs.max()),
            "ppl_REFERENCE_ONLY_structurally_insensitive": ppl,
            "_idx": idx[o], "_logp": lp[o]}


def js_div(m1: dict[str, Any], m2: dict[str, Any]) -> float:
    i1, l1, i2, l2 = m1["_idx"], m1["_logp"], m2["_idx"], m2["_logp"]
    ax = np.union1d(i1, i2)
    p = np.zeros(ax.size)
    q = np.zeros(ax.size)
    a1 = np.searchsorted(i1, ax)
    h1 = (a1 < i1.size) & (i1[np.clip(a1, 0, i1.size - 1)] == ax)
    p[h1] = np.exp(l1[a1[h1]])
    a2 = np.searchsorted(i2, ax)
    h2 = (a2 < i2.size) & (i2[np.clip(a2, 0, i2.size - 1)] == ax)
    q[h2] = np.exp(l2[a2[h2]])
    p /= (p.sum() + 1e-45)
    q /= (q.sum() + 1e-45)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / (m + 1e-45) + 1e-45))
                 + 0.5 * np.sum(q * np.log(q / (m + 1e-45) + 1e-45)))


def capture_last(model: Any, tok: Any, dec: Any, text: str,
                 layer: int) -> np.ndarray:
    import torch
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAX_LENGTH)
    dev = next(model.parameters()).device
    enc = {k: v.to(dev) for k, v in enc.items()}
    got: list[np.ndarray] = []

    def hk(module: Any, i: Any, o: Any) -> None:
        hs = o[0] if isinstance(o, tuple) else o
        got.append(hs.float()[0, -1].cpu().numpy())
    h = dec[layer].register_forward_hook(hk)
    try:
        with torch.no_grad():
            model(**enc)
    finally:
        h.remove()
    return got[0]


# ============================ geometry ===================================
def regress_dir(acts: np.ndarray, y: np.ndarray) -> np.ndarray:
    yz = (y.astype(np.float64) - y.mean()) / (y.std() + 1e-8)
    d = acts.astype(np.float64).T @ yz
    n = float(np.linalg.norm(d))
    if n < 1e-12:
        raise RuntimeError("regression direction is near-zero")
    return (d / n).astype(np.float32)


def subspace(mat: np.ndarray) -> dict[str, Any]:
    """Orthonormal basis + effective-rank diagnostics for a (D, r) matrix."""
    M = mat.astype(np.float64)
    sv = np.linalg.svd(M, compute_uv=False)
    Q, _ = np.linalg.qr(M)
    keep = sv > 1e-10 * max(sv[0], 1e-30)
    Q = Q[:, : int(keep.sum())] if keep.sum() < Q.shape[1] else Q
    return {"n_dims_supplied": int(mat.shape[1]),
            "singular_values": [float(x) for x in sv],
            "eff_rank_1pct": int((sv > 0.01 * sv[0]).sum()),
            "eff_rank_10pct": int((sv > 0.10 * sv[0]).sum()),
            "eff_rank_participation": float((sv.sum() ** 2)
                                            / (np.sum(sv ** 2) + 1e-30)),
            "_Q": Q.astype(np.float32)}


def residualise(a: np.ndarray, Q: np.ndarray) -> tuple[np.ndarray, float]:
    a64, Q64 = a.astype(np.float64), Q.astype(np.float64)
    r = a64 - Q64 @ (Q64.T @ a64)
    ratio = float(np.linalg.norm(r) / (np.linalg.norm(a64) + 1e-12))
    n = float(np.linalg.norm(r))
    if n < 1e-12:
        raise RuntimeError("axis lies entirely inside the human subspace")
    return (r / n).astype(np.float32), ratio


def env_manifest(extra: dict[str, Any]) -> dict[str, Any]:
    def sh(c: list[str]) -> str:
        try:
            return subprocess.run(c, capture_output=True, text=True,
                                  timeout=15).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""
    um = {}
    for ln in sh(["nvidia-smi", "--query-gpu=index,uuid",
                  "--format=csv,noheader"]).splitlines():
        p = [x.strip() for x in ln.split(",")]
        if len(p) == 2:
            um[p[0]] = p[1]
    man: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version.split()[0], "numpy": np.__version__,
        "hostname": platform.node(), "platform": platform.platform(),
        "CUDA_VISIBLE_DEVICES": _CVD,
        "gpu_uuid_visible_physical": [um.get(i.strip(), "?")
                                      for i in (_CVD or "").split(",") if i.strip()],
        "bootstrap_n": BOOTSTRAP_N, "bootstrap_seed": BOOTSTRAP_SEED,
        "alphas_rel": list(ALPHAS), "n_axes": N_AXES, "n_rand": N_RAND,
        "hook_scope": "last_token", "judge_llm_loaded": False,
        "generation_used": False,
        "degeneracy_rule": (f"top1_prob>={DEGEN_TOP1} or entropy_ratio<="
                            f"{DEGEN_ENT_LO} or entropy_ratio>={DEGEN_ENT_HI}; "
                            f"cell needs degenerate_frac<{DEGEN_FRAC_MAX}"),
        "ppl_note": ("ppl is emitted for reference only: a last-token-only "
                     "intervention cannot change a teacher-forced loss that "
                     "excludes the intervened position, so it is pinned at 1.00 "
                     "and supports no claim (prereg §11.3)"),
        "split_set": "DISCOVERY ONLY (confirmation untouched)",
        "tiers": {"S1": "V/A/D on 20 discovery E4 stimuli (PRE-REGISTERED PRIMARY)",
                  "S2": "V/A/D on 300 E1 sentences (3 dims, eff rank 3)",
                  "S3": "S2 + 20 one-vs-rest category dirs on held-out E4 40-79"},
    }
    try:
        import torch
        man["torch"] = torch.__version__
        man["cuda"] = torch.version.cuda
    except Exception:  # noqa: BLE001
        pass
    man.update(extra)
    return man


# ============================ self-check =================================
def self_check() -> int:
    ok = True

    def chk(n: str, c: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if c else 'FAIL'}] {n}")
        ok &= bool(c)

    r = paired_test([2.0] * 20, [1.0] * 20)
    chk("paired_test shift", abs(r["mean_diff"] - 1) < 1e-12
        and r["cliffs_delta"] == 1.0)
    chk("bh monotone", (lambda q: q[0] <= q[1] <= q[2])(bh_fdr([.001, .02, .5])))
    m1 = {"_idx": np.array([1, 2, 3]), "_logp": np.log([.2, .3, .5])}
    chk("JS(self)=0", abs(js_div(m1, m1)) < 1e-12)
    chk("JS(disjoint)=ln2", abs(js_div(
        m1, {"_idx": np.array([7, 8]), "_logp": np.log([.5, .5])})
        - math.log(2)) < 1e-9)

    rng = np.random.default_rng(0)
    # independent dirs -> eff rank 3; near-duplicate dirs -> eff rank 1
    M = rng.standard_normal((64, 3))
    M /= np.linalg.norm(M, axis=0, keepdims=True)
    s = subspace(M.astype(np.float32))
    chk("subspace: independent dirs eff_rank_10pct==3", s["eff_rank_10pct"] == 3)
    v = rng.standard_normal(64)
    v /= np.linalg.norm(v)
    Mdup = np.stack([v, v + 1e-3 * rng.standard_normal(64),
                     v + 1e-3 * rng.standard_normal(64)], axis=1)
    Mdup /= np.linalg.norm(Mdup, axis=0, keepdims=True)
    sd = subspace(Mdup.astype(np.float32))
    chk("subspace: near-duplicate dirs eff_rank_10pct==1",
        sd["eff_rank_10pct"] == 1)
    chk("subspace: participation ratio orders the two",
        sd["eff_rank_participation"] < s["eff_rank_participation"])
    chk("subspace basis orthonormal",
        np.allclose(s["_Q"].T.astype(np.float64) @ s["_Q"].astype(np.float64),
                    np.eye(s["_Q"].shape[1]), atol=1e-5))
    a = rng.standard_normal(64).astype(np.float32)
    a /= np.linalg.norm(a)
    ap, rr = residualise(a, s["_Q"])
    chk("residual unit norm", abs(np.linalg.norm(ap) - 1) < 1e-5)
    chk("residual orthogonal to basis",
        float(np.abs(s["_Q"].T.astype(np.float64) @ ap.astype(np.float64)).max())
        < 1e-4)
    chk("residual ratio in (0,1]", 0 < rr <= 1 + 1e-6)
    inside = s["_Q"][:, 0] * 0.7 + s["_Q"][:, 1] * 0.7
    inside /= np.linalg.norm(inside)
    chk("axis inside subspace -> ratio ~0", residualise(inside, s["_Q"])[1] < 1e-3)
    # a larger subspace must never RAISE the residual ratio
    big = subspace(np.concatenate(
        [M, rng.standard_normal((64, 5))], axis=1).astype(np.float32))
    chk("larger subspace never increases residual ratio",
        residualise(a, big["_Q"])[1] <= rr + 1e-6)

    # degeneracy rule
    def degen(t1: float, er: float) -> bool:
        return t1 >= DEGEN_TOP1 or er <= DEGEN_ENT_LO or er >= DEGEN_ENT_HI
    chk("degeneracy: collapsed top1 flagged", degen(0.97, 1.0))
    chk("degeneracy: entropy collapse flagged", degen(0.2, 0.4))
    chk("degeneracy: entropy blowup flagged", degen(0.2, 2.5))
    chk("degeneracy: normal sample not flagged", not degen(0.3, 1.1))

    vad = load_vad()
    if vad and SPLIT_PATH.exists():
        e4 = json.loads(Path("/path/to/work/code/stimuli/"
                             "stimuli_e4.json").read_text())
        disc = json.loads(SPLIT_PATH.read_text())["discovery_indices"]
        got = [stimulus_vad(e4[i]["text"], vad) for i in disc]
        chk("all discovery stimuli have VAD", all(g is not None for g in got))
        held = [i for i in range(len(e4)) if i >= 40]
        cats = [e4[i]["target_emotion"] for i in held]
        chk("held-out E4 40-79 has >=2 items per category",
            min(cats.count(c) for c in set(cats)) >= 2)
        dcats = [e4[i]["target_emotion"] for i in disc]
        chk("discovery has 1 item per category (why S3 is not fitted there)",
            max(dcats.count(c) for c in set(dcats)) == 1)
        e1 = json.loads(E1_PATH.read_text())
        n1 = sum(1 for s in e1 if stimulus_vad(s["text"], vad) is not None)
        chk(f"E1 usable for S2 ({n1}/{len(e1)} matched)", n1 >= 250)
    else:
        print("  [SKIP] VAD or split file unavailable")

    try:
        import torch

        class D:
            pass
        d = np.zeros(4, dtype=np.float32)
        d[0] = 1.0
        hs = torch.zeros(1, 3, 4)
        o = Hook(d, 2.0)(D(), (), hs)
        chk("hook only final position",
            float(o[0, 0, 0]) == 0.0 and float(o[0, 2, 0]) == 2.0)
        chk("hook does not mutate input", float(hs[0, 2, 0]) == 0.0)
    except ImportError:
        print("  [SKIP] torch unavailable")

    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ============================ main =======================================
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=[5, 7, 10, 12])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--stimuli", type=Path,
                    default=Path("/path/to/work/code/stimuli/stimuli_e4.json"))
    ap.add_argument("--output-dir", type=Path, default=BASE / "axis_residual_v2")
    ap.add_argument("--prereg-commit", default="")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        return self_check()
    if _CVD is None:
        print("[v2] FATAL: CUDA_VISIBLE_DEVICES unset (lab rule)", file=sys.stderr)
        return 4

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_ica import compute_split_reproducibility, model_slug

    split = json.loads(SPLIT_PATH.read_text())
    disc = split["discovery_indices"]
    e4 = json.loads(args.stimuli.read_bytes())
    stim = [e4[i] for i in disc]
    texts = [s["text"] for s in stim]
    held_idx = [i for i in range(len(e4)) if i >= 40]
    held_texts = [e4[i]["text"] for i in held_idx]
    held_cats = [e4[i]["target_emotion"] for i in held_idx]
    cat_names = sorted(set(held_cats))

    vad = load_vad()
    assert vad, "no VAD"
    sc_d = [stimulus_vad(t, vad) for t in texts]
    assert all(s is not None for s in sc_d), "discovery stimulus without VAD"
    y_disc = {k: np.array([s[k] for s in sc_d]) for k in KEYS}

    e1 = json.loads(E1_PATH.read_text())
    sc1 = [stimulus_vad(s["text"], vad) for s in e1]
    keep1 = [i for i, s in enumerate(sc1) if s is not None]
    y_e1 = {k: np.array([sc1[i][k] for i in keep1]) for k in KEYS}
    print(f"[v2] discovery n={len(texts)}  E1 matched={len(keep1)}/{len(e1)}  "
          f"held-out E4={len(held_idx)} in {len(cat_names)} categories", flush=True)

    slug = model_slug(args.model)
    print(f"[v2] Loading {args.model} …", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True)
    model.eval()
    dec = (model.model.layers if hasattr(model, "model")
           and hasattr(model.model, "layers") else model.transformer.h)
    D = int(model.config.hidden_size)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = args.output_dir / f"axis_residual_v2_discovery_{stamp}.json"
    layers_out: list[dict[str, Any]] = []

    for layer in args.layers:
        print(f"\n[v2] ===== layer {layer} =====", flush=True)
        acts_d = np.stack([capture_last(model, tok, dec, t, layer) for t in texts])
        norms = np.linalg.norm(acts_d, axis=1)
        acts_h = np.stack([capture_last(model, tok, dec, t, layer)
                           for t in held_texts])
        X1 = np.load(ACT_DIR / slug / f"layer{layer:02d}_seed{args.seed:04d}.npz",
                     allow_pickle=True)["arr"].astype(np.float32)[keep1]

        hd_S1 = {k: regress_dir(acts_d, y_disc[k]) for k in KEYS}
        hd_S2 = {k: regress_dir(X1, y_e1[k]) for k in KEYS}
        cat_dirs = {c: regress_dir(
            acts_h, np.array([1.0 if hc == c else 0.0 for hc in held_cats]))
            for c in cat_names}

        sub = {
            "S1": subspace(np.stack([hd_S1[k] for k in KEYS], axis=1)),
            "S2": subspace(np.stack([hd_S2[k] for k in KEYS], axis=1)),
            "S3": subspace(np.stack([hd_S2[k] for k in KEYS]
                                    + [cat_dirs[c] for c in cat_names], axis=1)),
        }
        for t in TIERS:
            s = sub[t]
            print(f"[v2] {t}: dims={s['n_dims_supplied']} "
                  f"eff_rank(10%)={s['eff_rank_10pct']} "
                  f"eff_rank(1%)={s['eff_rank_1pct']} "
                  f"participation={s['eff_rank_participation']:.2f}", flush=True)

        files = sorted(glob.glob(str(ICA_DIR / slug
                                    / f"layer{layer:02d}_seed{args.seed:04d}_K*.json")))
        assert files
        best, bs = None, -2.0
        for fp in files:
            dd = json.loads(Path(fp).read_text())
            s_ = max(dd.get("silhouettes") or [-1.0])
            if s_ > bs:
                bs, best, best_fp = s_, dd, fp
        comps_all = np.array(best["components"], dtype=np.float32)
        npz = ACT_DIR / slug / f"layer{layer:02d}_seed{args.seed:04d}.npz"
        rep_all = compute_split_reproducibility(npz, comps_all, seed=args.seed)
        order = np.argsort(-rep_all)
        comps = comps_all[order][:N_AXES]
        repro = [float(x) for x in rep_all[order][:N_AXES]]

        spectrum = [{"axis_rank": int(r), "ica_index": int(order[r]),
                     "split_repro": float(rep_all[order[r]]),
                     **{f"abs_cos_{k}_S1": abs(float(comps_all[order[r]] @ hd_S1[k]))
                        for k in KEYS},
                     **{f"abs_cos_{k}_S2": abs(float(comps_all[order[r]] @ hd_S2[k]))
                        for k in KEYS},
                     "abs_cos_max_vad_S1": max(
                         abs(float(comps_all[order[r]] @ hd_S1[k])) for k in KEYS),
                     "abs_cos_max_vad_S2": max(
                         abs(float(comps_all[order[r]] @ hd_S2[k])) for k in KEYS),
                     "abs_cos_max_category": max(
                         abs(float(comps_all[order[r]] @ cat_dirs[c]))
                         for c in cat_names)}
                    for r in range(len(order))]

        dirs: dict[str, np.ndarray] = {}
        rr: dict[str, float] = {}
        for i in range(N_AXES):
            dirs[f"axis{i}"] = comps[i]
            for t in TIERS:
                ap_, ratio = residualise(comps[i], sub[t]["_Q"])
                dirs[f"axis{i}_resid_{t}"] = ap_
                rr[f"axis{i}_{t}"] = ratio
        for k in KEYS:                      # Q4 arms
            dirs[f"human_{k}"] = hd_S2[k]
        rng = np.random.default_rng(args.seed + RAND_SEED_OFFSET)
        rd = rng.standard_normal((N_RAND, D)).astype(np.float32)
        for i in range(N_RAND):
            rd[i] /= np.linalg.norm(rd[i]) + 1e-12
            dirs[f"rand{i}"] = rd[i]
        for i in range(N_AXES):
            v = rd[i].copy()
            v -= comps[i] * float(np.dot(v, comps[i]))
            dirs[f"ortho{i}"] = v / (float(np.linalg.norm(v)) + 1e-12)

        for n, d_ in dirs.items():
            assert abs(float(np.linalg.norm(d_)) - 1.0) < 1e-4, n
        for i in range(N_AXES):
            for t in TIERS:
                assert float(np.abs(
                    sub[t]["_Q"].T.astype(np.float64)
                    @ dirs[f"axis{i}_resid_{t}"].astype(np.float64)).max()) < 1e-3

        print(f"[v2] repro={[round(x,3) for x in repro]}  residual ratios: "
              + "  ".join(f"axis{i}:" + "/".join(f"{rr[f'axis{i}_{t}']:.3f}"
                                                 for t in TIERS)
                          for i in range(N_AXES)) + "  (S1/S2/S3)", flush=True)

        if args.dry_run:
            print(json.dumps({"spectrum_top3": spectrum[:3],
                              "residual_ratio": rr,
                              "eff_ranks": {t: {k: sub[t][k] for k in sub[t]
                                                if k != "_Q"} for t in TIERS}},
                             indent=2))
            return 0

        base = [forward_metrics(model, tok, dec, t, layer, None, 0.0)
                for t in texts]
        names = list(dirs)
        # Register the layer entry BEFORE the alpha loop and flush after EVERY
        # alpha, so a job that dies mid-layer keeps everything already measured.
        rows: list[dict[str, Any]] = []
        layer_entry: dict[str, Any] = {
            "layer": layer, "model_id": args.model, "seed": args.seed,
            "hidden_dim": D, "axis_source_file": best_fp,
            "axis_ica_k": int(best["k"]), "axis_split_repro_top3": repro,
            "discovery_indices": disc,
            "heldout_category_indices": held_idx,
            "category_names": cat_names,
            "n_e1_matched": len(keep1),
            "last_token_norm_mean": float(norms.mean()),
            "subspaces": {t: {k: v for k, v in sub[t].items() if k != "_Q"}
                          for t in TIERS},
            "human_dir_pairwise_cos_S1": {
                f"{a}-{b}": float(hd_S1[a] @ hd_S1[b])
                for i, a in enumerate(KEYS) for b in KEYS[i + 1:]},
            "human_dir_pairwise_cos_S2": {
                f"{a}-{b}": float(hd_S2[a] @ hd_S2[b])
                for i, a in enumerate(KEYS) for b in KEYS[i + 1:]},
            "alignment_spectrum_ALL_axes": spectrum,
            "residual_norm_ratio": rr,
            "alphas_completed": [],
            "rows": rows,
        }
        layers_out.append(layer_entry)
        for a_rel in ALPHAS:
            js: dict[str, list[float]] = {n: [] for n in names}
            ent_ratio: dict[str, list[float]] = {n: [] for n in names}
            top1: dict[str, list[float]] = {n: [] for n in names}
            pplr: dict[str, list[float]] = {n: [] for n in names}
            degen: dict[str, list[float]] = {n: [] for n in names}
            for si, t in enumerate(texts):
                a_abs = a_rel * norms[si]
                b = base[si]
                for pol in (1.0, -1.0):
                    for n in names:
                        m = forward_metrics(model, tok, dec, t, layer,
                                            dirs[n] * pol, a_abs)
                        js[n].append(js_div(m, b))
                        er = (m["entropy_nats"] / b["entropy_nats"]
                              if b["entropy_nats"] > 0 else float("nan"))
                        ent_ratio[n].append(er)
                        top1[n].append(m["top1_prob"])
                        pr = m["ppl_REFERENCE_ONLY_structurally_insensitive"]
                        pb = b["ppl_REFERENCE_ONLY_structurally_insensitive"]
                        pplr[n].append(pr / pb if pb and pb > 0 else float("nan"))
                        degen[n].append(1.0 if (
                            m["top1_prob"] >= DEGEN_TOP1
                            or (not math.isnan(er) and (er <= DEGEN_ENT_LO
                                                        or er >= DEGEN_ENT_HI))
                        ) else 0.0)
                if (si + 1) % 10 == 0:
                    print(f"[v2]   L{layer} a={a_rel} {si+1}/{len(texts)}",
                          flush=True)
            ns = len(js[names[0]])
            randfloor = [float(np.mean([js[f"rand{i}"][j] for i in range(N_RAND)]))
                         for j in range(ns)]
            orthofloor = [float(np.mean([js[f"ortho{i}"][j] for i in range(N_AXES)]))
                          for j in range(ns)]
            row: dict[str, Any] = {"layer": layer, "alpha_rel": a_rel,
                                   "n_samples": ns,
                                   "alpha_abs_mean": float(a_rel * norms.mean())}
            for n in names:
                row[f"js_{n}_mean"], row[f"js_{n}_std"] = mean_std(js[n])
                row[f"entropy_ratio_{n}_mean"] = mean_std(ent_ratio[n])[0]
                row[f"top1_{n}_mean"] = mean_std(top1[n])[0]
                row[f"degenerate_frac_{n}"] = float(np.mean(degen[n]))
                row[f"ppl_ratio_REF_{n}_mean"] = mean_std(pplr[n])[0]
            row["js_randfloor_mean"] = mean_std(randfloor)[0]
            row["js_orthofloor_mean"] = mean_std(orthofloor)[0]
            for i in range(N_AXES):
                tags = [f"axis{i}"] + [f"axis{i}_resid_{t}" for t in TIERS]
                for tg in tags:
                    row[f"paired_{tg}_vs_randfloor"] = paired_test(js[tg], randfloor)
                    row[f"paired_{tg}_vs_orthofloor"] = paired_test(js[tg], orthofloor)
                for t in TIERS:
                    row[f"paired_axis{i}_vs_resid_{t}"] = paired_test(
                        js[f"axis{i}"], js[f"axis{i}_resid_{t}"],
                        alternative="two-sided")
                    ja = row[f"js_axis{i}_mean"]
                    jr = row[f"js_axis{i}_resid_{t}_mean"]
                    row[f"attenuation_axis{i}_{t}"] = (1.0 - jr / ja if ja > 0
                                                      else float("nan"))
                    row[f"residual_norm_ratio_axis{i}_{t}"] = rr[f"axis{i}_{t}"]
            # Q4: V1 human valence vs random floor (two-sided), V2 vs axes
            for k in KEYS:
                row[f"paired_human_{k}_vs_randfloor_TWOSIDED"] = paired_test(
                    js[f"human_{k}"], randfloor, alternative="two-sided")
                row[f"paired_human_{k}_vs_orthofloor_TWOSIDED"] = paired_test(
                    js[f"human_{k}"], orthofloor, alternative="two-sided")
            for i in range(N_AXES):
                row[f"paired_human_valence_vs_axis{i}_LESS"] = paired_test(
                    js["human_valence"], js[f"axis{i}"], alternative="less")
            rows.append(row)
            layer_entry["alphas_completed"].append(a_rel)
            out_path.write_text(json.dumps(
                {"env": env_manifest({
                    "prereg_commit": args.prereg_commit,
                    "split_sha256": hashlib.sha256(
                        SPLIT_PATH.read_bytes()).hexdigest(),
                    "layers_complete": [L["layer"] for L in layers_out
                                        if len(L["rows"]) == len(ALPHAS)],
                    "partial_layer": layer,
                    "partial_alphas_done": layer_entry["alphas_completed"],
                    "status": "IN_PROGRESS"}),
                 "layers": layers_out}, indent=2, ensure_ascii=False))
            print(f"[v2] flushed {out_path.name} (layer {layer}, "
                  f"alpha {a_rel} done)", flush=True)

        print(f"[v2] layer {layer} complete -> {out_path}", flush=True)

    # ---- BH families: one per (tier, floor) plus the raw axes ----
    fams: dict[str, list[dict[str, Any]]] = {}
    for L in layers_out:
        for r in L["rows"]:
            for i in range(N_AXES):
                fams.setdefault("raw_vs_rand", []).append(
                    r[f"paired_axis{i}_vs_randfloor"])
                fams.setdefault("raw_vs_ortho", []).append(
                    r[f"paired_axis{i}_vs_orthofloor"])
                for t in TIERS:
                    fams.setdefault(f"resid_{t}_vs_rand", []).append(
                        r[f"paired_axis{i}_resid_{t}_vs_randfloor"])
                    fams.setdefault(f"resid_{t}_vs_ortho", []).append(
                        r[f"paired_axis{i}_resid_{t}_vs_orthofloor"])
            for k in KEYS:
                fams.setdefault("human_vs_rand_twosided", []).append(
                    r[f"paired_human_{k}_vs_randfloor_TWOSIDED"])
    sizes = {}
    for f, ts in fams.items():
        for t_, q in zip(ts, bh_fdr([x["wilcoxon_p"] for x in ts])):
            t_["wilcoxon_q_bh"] = q
        sizes[f] = len(ts)
    print(f"[v2] BH family sizes: {sizes}")

    # ---- verdicts ----
    V: dict[str, Any] = {"R1_by_tier": {}, "V1_human_valence_comparable_to_floor": [],
                         "V2_human_valence_below_axes": [], "M3prime_degenerate": []}
    for t in TIERS:
        surv = []
        for L in layers_out:
            for i in range(N_AXES):
                for r in L["rows"]:
                    ar = r[f"paired_axis{i}_vs_randfloor"]
                    ao = r[f"paired_axis{i}_vs_orthofloor"]
                    sr = r[f"paired_axis{i}_resid_{t}_vs_randfloor"]
                    so = r[f"paired_axis{i}_resid_{t}_vs_orthofloor"]
                    dg = r[f"degenerate_frac_axis{i}_resid_{t}"]
                    if (ar["mean_diff"] > 0 and ar["wilcoxon_q_bh"] < 0.05
                            and ao["mean_diff"] > 0 and ao["wilcoxon_q_bh"] < 0.05
                            and sr["mean_diff"] > 0 and sr["wilcoxon_q_bh"] < 0.05
                            and so["mean_diff"] > 0 and so["wilcoxon_q_bh"] < 0.05
                            and dg < DEGEN_FRAC_MAX):
                        surv.append({
                            "layer": L["layer"], "axis": i,
                            "alpha_rel": r["alpha_rel"],
                            "residual_norm_ratio": r[
                                f"residual_norm_ratio_axis{i}_{t}"],
                            "attenuation": r[f"attenuation_axis{i}_{t}"],
                            "degenerate_frac": dg,
                            "resid_delta_vs_rand": sr["cliffs_delta"]})
        V["R1_by_tier"][t] = {
            "n_cells_surviving": len(surv), "supported": bool(surv),
            "cells": surv,
            "NOTE": ("a cell only counts when the residual norm ratio shows that "
                     "something was actually removed; report the ratio alongside")}
    for L in layers_out:
        for r in L["rows"]:
            hv = r["paired_human_valence_vs_randfloor_TWOSIDED"]
            V["V1_human_valence_comparable_to_floor"].append({
                "layer": L["layer"], "alpha_rel": r["alpha_rel"],
                "js_human_valence": r["js_human_valence_mean"],
                "js_randfloor": r["js_randfloor_mean"],
                "mean_diff": hv["mean_diff"], "q_bh": hv["wilcoxon_q_bh"],
                "cliffs_delta": hv["cliffs_delta"],
                "V1_comparable": bool(hv["wilcoxon_q_bh"] >= 0.05
                                      and abs(hv["cliffs_delta"])
                                      < CLIFF_COMPARABLE)})
            for i in range(N_AXES):
                t_ = r[f"paired_human_valence_vs_axis{i}_LESS"]
                V["V2_human_valence_below_axes"].append({
                    "layer": L["layer"], "axis": i, "alpha_rel": r["alpha_rel"],
                    "mean_diff": t_["mean_diff"], "p": t_["wilcoxon_p"],
                    "cliffs_delta": t_["cliffs_delta"]})
            for n in ("axis0", "axis1", "axis2", "human_valence"):
                if r[f"degenerate_frac_{n}"] >= DEGEN_FRAC_MAX:
                    V["M3prime_degenerate"].append({
                        "layer": L["layer"], "alpha_rel": r["alpha_rel"],
                        "direction": n, "degenerate_frac": r[f"degenerate_frac_{n}"]})
    V["V1_supported_fraction"] = float(np.mean(
        [1.0 if x["V1_comparable"] else 0.0
         for x in V["V1_human_valence_comparable_to_floor"]]))

    out_path.write_text(json.dumps(
        {"env": env_manifest({"prereg_commit": args.prereg_commit,
                              "split_sha256": hashlib.sha256(
                                  SPLIT_PATH.read_bytes()).hexdigest(),
                              "bh_family_sizes": sizes,
                              "layers_complete": [L["layer"] for L in layers_out],
                              "status": "COMPLETE"}),
         "verdicts": V, "layers": layers_out}, indent=2, ensure_ascii=False))
    for t in TIERS:
        print(f"[v2] R1 {t}: supported={V['R1_by_tier'][t]['supported']} "
              f"cells={V['R1_by_tier'][t]['n_cells_surviving']}")
    print(f"[v2] V1 comparable fraction = {V['V1_supported_fraction']:.3f}")
    print(f"[v2] FINAL -> {out_path}")
    print("[v2] DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
