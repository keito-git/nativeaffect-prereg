#!/usr/bin/env python3
"""Intensity sweep + residual-axis test on the rebuilt (PAD-free) ICA axes.

DISCOVERY SET ONLY (20 of the 40 E4 stimuli). The confirmation set is not read.

Pre-registration
----------------
03_解析/preregistration/axis_rebuilt_prereg_20260925.md, including Amendment 1
(§10), which was committed before this ran. Predictions R1-R3 and the M1-M3
sanity conditions are fixed there.

The decisive test (§10.3)
-------------------------
An axis whose interventional effect merely restates a human affect dimension is
not evidence for an AI-native axis. So for every axis a we also intervene along

    a_perp = normalise(a - P_S a),    S = span{v_valence, v_arousal, v_dominance}

where the three human directions are regressed from LAST-TOKEN activations (the
same pooling the axes use -- mean-pooling is what broke the positive control).
If a_perp still beats the random and orthogonal floors, the axis's effect is not
reducible to human VAD. If it collapses, the axis was a restatement.

The human-alignment cosines are REPORTED FOR EVERY AXIS but are never used to
select, reorder or exclude axes: selecting on them would define the axes by the
human frame and make the claim tautological (directive of the supervising associate).

No judge LLM is loaded anywhere (PI directive).

Usage
-----
    python3 run_axis_residual_sweep.py --self-check
    python3 run_axis_residual_sweep.py --layers 5 7 10 12
"""

from __future__ import annotations

import argparse
import csv
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
RAND_SEED_OFFSET = 9999      # identical to run_intervention.py:777
N_RAND = 5
N_AXES = 3                   # top-3 by split-half reproducibility (prereg §2)
TOP_K_VOCAB = 100
MAX_LENGTH = 128
PPL_COLLAPSE_RATIO = 3.0     # prereg §6 M3
ALPHAS = (0.01, 0.03, 0.05, 0.10, 0.20)
VAD_PATH = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
ICA_DIR = Path("/path/to/work/results/ica_nopad")
ACT_DIR = Path("/path/to/work/results/activations_nopad")
SPLIT_PATH = Path("/path/to/work/results/axes_nopad/"
                  "axis_rebuilt_split_20260925.json")
VAD_KEYS = ("valence", "arousal", "dominance")


# =========================== statistics ==================================
def bootstrap_ci_mean(values: Sequence[float], n_boot: int = BOOTSTRAP_N,
                      seed: int = BOOTSTRAP_SEED,
                      alpha: float = 0.05) -> tuple[float, float]:
    arr = np.asarray([v for v in values if not math.isnan(v)], dtype=float)
    if arr.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_boot, arr.size))
    m = arr[idx].mean(axis=1)
    lo, hi = np.quantile(m, [alpha / 2.0, 1.0 - alpha / 2.0])
    return (float(lo), float(hi))


def paired_test(a: Sequence[float], b: Sequence[float],
                alternative: str = "greater") -> dict[str, float]:
    pairs = [(x, y) for x, y in zip(a, b)
             if not (math.isnan(x) or math.isnan(y))]
    if len(pairs) < 2:
        return {"n": len(pairs), "mean_diff": float("nan"),
                "std_diff": float("nan"), "wilcoxon_p": float("nan"),
                "ci_lo": float("nan"), "ci_hi": float("nan"),
                "cliffs_delta": float("nan")}
    xa = np.array([p[0] for p in pairs], float)
    xb = np.array([p[1] for p in pairs], float)
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


def bh_fdr(pvals: Sequence[float]) -> list[float]:
    arr = np.asarray(pvals, float)
    ok = ~np.isnan(arr)
    out = np.full(arr.shape, np.nan)
    p = arr[ok]
    if p.size == 0:
        return out.tolist()
    order = np.argsort(p)
    m = p.size
    adj = p[order] * m / (np.arange(m) + 1)
    adj = np.clip(np.minimum.accumulate(adj[::-1])[::-1], 0.0, 1.0)
    r = np.empty(m)
    r[order] = adj
    out[ok] = r
    return out.tolist()


def mean_std(v: Sequence[float]) -> tuple[float, float]:
    a = np.asarray([x for x in v if not math.isnan(x)], float)
    if a.size == 0:
        return (float("nan"), float("nan"))
    return (float(a.mean()), float(a.std(ddof=1)) if a.size > 1 else 0.0)


# =========================== Warriner VAD ===============================
def load_vad(path: Path = VAD_PATH) -> dict[str, dict[str, float]]:
    """{word: {valence, arousal, dominance}}."""
    out: dict[str, dict[str, float]] = {}
    if not path.exists():
        print(f"[res] WARNING: VAD file missing: {path}")
        return out
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = row.get("word", row.get("Word", "")).strip().lower()
            if not w:
                continue
            try:
                out[w] = {k: float(row[k].strip()) for k in VAD_KEYS}
            except (KeyError, ValueError, AttributeError):
                continue
    print(f"[res] Loaded {len(out)} VAD entries (V/A/D) from {path}")
    return out


_SUFFIXES = ["fully", "fulness", "fulness", "ful", "ness", "ly",
             "ing", "tion", "ed", "er", "est", "s"]


def stimulus_vad(text: str, vad: dict[str, dict[str, float]]) -> dict | None:
    """Mean V/A/D over matched words. Suffix stripping is essential (2298-word
    list: 'joyful' absent, 'joy' present) -- dropping it silently removes every
    positive stimulus, which is defect D2 from the positive-control work."""
    def look(w: str) -> dict[str, float] | None:
        if w in vad:
            return vad[w]
        for s in _SUFFIXES:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                return vad[w[: -len(s)]]
        return None

    hits = [h for h in (look(w) for w in re.findall(r"[a-zA-Z']+", text.lower()))
            if h is not None]
    if not hits:
        return None
    return {k: float(np.mean([h[k] for h in hits])) for k in VAD_KEYS}


# =========================== hooks / metrics ============================
class Hook:
    """Add alpha*direction at the FINAL token position of one decoder layer."""

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
    """One forward pass -> next-token distribution AND sequence perplexity."""
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
            logits = model(**enc).logits  # (1, T, V)
    finally:
        if h is not None:
            h.remove()

    last = logits[0, -1, :]
    probs = F.softmax(last.float(), dim=-1).cpu().numpy()
    pp = probs[probs > 0]
    idx = np.argsort(probs)[-top_k:]
    lp = np.log(probs[idx] + 1e-45)
    o = np.argsort(idx)

    # sequence perplexity (teacher forcing on the stimulus itself)
    ids = enc["input_ids"][0]
    if ids.shape[0] > 1:
        nll = F.cross_entropy(logits[0, :-1, :].float(), ids[1:],
                              reduction="mean")
        ppl = float(torch.exp(nll).item())
    else:
        ppl = float("nan")

    return {"entropy_nats": float(-np.sum(pp * np.log(pp))),
            "ppl": ppl, "_idx": idx[o], "_logp": lp[o]}


def js_div(m1: dict[str, Any], m2: dict[str, Any]) -> float:
    i1, l1 = m1["_idx"], m1["_logp"]
    i2, l2 = m2["_idx"], m2["_logp"]
    allx = np.union1d(i1, i2)
    p = np.zeros(allx.size)
    q = np.zeros(allx.size)
    a1 = np.searchsorted(i1, allx)
    h1 = (a1 < i1.size) & (i1[np.clip(a1, 0, i1.size - 1)] == allx)
    p[h1] = np.exp(l1[a1[h1]])
    a2 = np.searchsorted(i2, allx)
    h2 = (a2 < i2.size) & (i2[np.clip(a2, 0, i2.size - 1)] == allx)
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


# =========================== geometry ===================================
def human_directions(acts: np.ndarray, scores: dict[str, np.ndarray]
                     ) -> dict[str, np.ndarray]:
    """Unit-norm direction per human dimension: d ∝ X^T z(y). Same recipe and
    pooling as the positive control's last-token variant."""
    out = {}
    for k in VAD_KEYS:
        y = scores[k].astype(np.float64)
        yz = (y - y.mean()) / (y.std() + 1e-8)
        d = acts.astype(np.float64).T @ yz
        n = float(np.linalg.norm(d))
        if n < 1e-12:
            raise RuntimeError(f"human direction {k} is near-zero")
        out[k] = (d / n).astype(np.float32)
    return out


def vad_basis(hd: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, Any]]:
    """Orthonormal basis Q (D,r) of span{v,a,d} via QR, plus rank diagnostics."""
    M = np.stack([hd[k] for k in VAD_KEYS], axis=1).astype(np.float64)  # (D,3)
    sv = np.linalg.svd(M, compute_uv=False)
    Q, _ = np.linalg.qr(M)
    info = {"singular_values": [float(x) for x in sv],
            "rank_tol_1e-6": int((sv > 1e-6 * sv[0]).sum()),
            "pairwise_cos": {f"{a}_{b}": float(hd[a] @ hd[b])
                             for i, a in enumerate(VAD_KEYS)
                             for b in VAD_KEYS[i + 1:]}}
    return Q.astype(np.float32), info


def residualise(a: np.ndarray, Q: np.ndarray) -> tuple[np.ndarray, float]:
    """a_perp = normalise(a - Q Q^T a); also return ‖a-P a‖/‖a‖."""
    a64 = a.astype(np.float64)
    Q64 = Q.astype(np.float64)
    r = a64 - Q64 @ (Q64.T @ a64)
    ratio = float(np.linalg.norm(r) / (np.linalg.norm(a64) + 1e-12))
    n = float(np.linalg.norm(r))
    if n < 1e-12:
        raise RuntimeError("axis lies entirely in the human VAD subspace")
    return (r / n).astype(np.float32), ratio


# =========================== manifest ===================================
def env_manifest(extra: dict[str, Any]) -> dict[str, Any]:
    def sh(c: list[str]) -> str:
        try:
            return subprocess.run(c, capture_output=True, text=True,
                                  timeout=15).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""
    umap = {}
    for line in sh(["nvidia-smi", "--query-gpu=index,uuid",
                    "--format=csv,noheader"]).splitlines():
        p = [x.strip() for x in line.split(",")]
        if len(p) == 2:
            umap[p[0]] = p[1]
    man: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version.split()[0], "numpy": np.__version__,
        "hostname": platform.node(), "platform": platform.platform(),
        "git_commit_server": sh(["git", "rev-parse", "HEAD"])
                             or "NO_GIT_REPO_ON_SERVER (see script_sha256)",
        "CUDA_VISIBLE_DEVICES": _CVD,
        "gpu_uuid_visible_physical": [umap.get(i.strip(), "?")
                                      for i in (_CVD or "").split(",")
                                      if i.strip()],
        "bootstrap_n": BOOTSTRAP_N, "bootstrap_seed": BOOTSTRAP_SEED,
        "alphas_rel": list(ALPHAS), "n_axes": N_AXES, "n_rand": N_RAND,
        "hook_scope": "last_token (main condition)",
        "judge_llm_loaded": False,
        "ppl_collapse_ratio": PPL_COLLAPSE_RATIO,
        "split_set": "DISCOVERY ONLY (confirmation set untouched)",
    }
    try:
        import torch
        man["torch"] = torch.__version__
        man["cuda"] = torch.version.cuda
    except Exception:  # noqa: BLE001
        pass
    man.update(extra)
    return man


# =========================== self-check =================================
def self_check() -> int:
    ok = True

    def chk(n: str, c: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if c else 'FAIL'}] {n}")
        ok &= bool(c)

    r = paired_test([2.0] * 20, [1.0] * 20)
    chk("paired_test shift", abs(r["mean_diff"] - 1) < 1e-12
        and r["cliffs_delta"] == 1.0)
    q = bh_fdr([0.001, 0.02, 0.5])
    chk("bh monotone", q[0] <= q[1] <= q[2])
    m1 = {"_idx": np.array([1, 2, 3]), "_logp": np.log([0.2, 0.3, 0.5])}
    chk("JS(self)=0", abs(js_div(m1, m1)) < 1e-12)
    chk("JS(disjoint)=ln2", abs(js_div(
        m1, {"_idx": np.array([7, 8]), "_logp": np.log([0.5, 0.5])})
        - math.log(2)) < 1e-9)

    # residualisation: a_perp must be orthogonal to all three human directions
    rng = np.random.default_rng(0)
    hd = {k: rng.standard_normal(64).astype(np.float32) for k in VAD_KEYS}
    for k in hd:
        hd[k] /= np.linalg.norm(hd[k])
    Q, info = vad_basis(hd)
    chk("VAD basis is orthonormal",
        np.allclose(Q.T.astype(np.float64) @ Q.astype(np.float64),
                    np.eye(Q.shape[1]), atol=1e-5))
    chk("VAD basis rank 3 for independent dirs", info["rank_tol_1e-6"] == 3)
    a = rng.standard_normal(64).astype(np.float32)
    a /= np.linalg.norm(a)
    ap, ratio = residualise(a, Q)
    chk("residual is unit norm", abs(np.linalg.norm(ap) - 1) < 1e-5)
    chk("residual ⟂ every human direction",
        all(abs(float(ap @ hd[k])) < 1e-4 for k in VAD_KEYS))
    chk("residual norm ratio in (0,1]", 0 < ratio <= 1.0 + 1e-6)
    # an axis already inside the subspace must residualise to ~nothing
    inside = hd["valence"] * 0.6 + hd["arousal"] * 0.8
    inside = inside / np.linalg.norm(inside)
    _, ratio_in = residualise(inside, Q)
    chk("axis inside subspace -> tiny residual ratio", ratio_in < 1e-3)
    # projection idempotence
    P = Q.astype(np.float64) @ Q.astype(np.float64).T
    chk("projector idempotent", np.allclose(P @ P, P, atol=1e-6))

    vad = load_vad()
    if vad:
        stim = json.loads(Path("/path/to/work/code/stimuli/"
                               "stimuli_e4.json").read_text())[:40]
        sp = json.loads(SPLIT_PATH.read_text()) if SPLIT_PATH.exists() else None
        if sp:
            disc = sp["discovery_indices"]
            got = [stimulus_vad(stim[i]["text"], vad) for i in disc]
            chk(f"D2 guard: all {len(disc)} discovery stimuli have VAD",
                all(g is not None for g in got))
            v = np.array([g["valence"] for g in got if g])
            chk("discovery valence separates polarity",
                v[:10].mean() > v[10:].mean())
        else:
            print("  [SKIP] split file not found")
    else:
        print("  [SKIP] VAD file unavailable")

    try:
        import torch

        class D:
            pass
        d = np.zeros(4, dtype=np.float32)
        d[0] = 1.0
        hs = torch.zeros(1, 3, 4)
        o = Hook(d, 2.0)(D(), (), hs)
        chk("hook touches only final position",
            float(o[0, 0, 0]) == 0.0 and float(o[0, 2, 0]) == 2.0)
        chk("hook does not mutate input", float(hs[0, 2, 0]) == 0.0)
    except ImportError:
        print("  [SKIP] torch unavailable")

    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# =========================== main =======================================
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=[5, 7, 10, 12])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--stimuli", type=Path,
                    default=Path("/path/to/work/code/stimuli/stimuli_e4.json"))
    ap.add_argument("--output-dir", type=Path,
                    default=Path("/path/to/work/results/axis_residual"))
    ap.add_argument("--prereg-commit", default="")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        return self_check()
    if _CVD is None:
        print("[res] FATAL: CUDA_VISIBLE_DEVICES unset (lab rule)", file=sys.stderr)
        return 4

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_ica import compute_split_reproducibility, model_slug

    split = json.loads(SPLIT_PATH.read_text())
    disc = split["discovery_indices"]
    all_stim = json.loads(args.stimuli.read_bytes())[:40]
    stim = [all_stim[i] for i in disc]
    texts = [s["text"] for s in stim]
    print(f"[res] DISCOVERY set: {len(texts)} stimuli "
          f"(split sha {hashlib.sha256(SPLIT_PATH.read_bytes()).hexdigest()[:16]})")

    vad = load_vad()
    if not vad:
        return 3
    sc_raw = [stimulus_vad(t, vad) for t in texts]
    assert all(s is not None for s in sc_raw), "a discovery stimulus has no VAD"
    scores = {k: np.array([s[k] for s in sc_raw]) for k in VAD_KEYS}

    slug = model_slug(args.model)
    print(f"[res] Loading {args.model} …", flush=True)
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
    out_path = args.output_dir / f"axis_residual_discovery_{stamp}.json"
    layers_out: list[dict[str, Any]] = []

    for layer in args.layers:
        print(f"\n[res] ===== layer {layer} =====", flush=True)
        acts = np.stack([capture_last(model, tok, dec, t, layer) for t in texts])
        norms = np.linalg.norm(acts, axis=1)

        hd = human_directions(acts, scores)
        Q, qinfo = vad_basis(hd)

        # all rebuilt axes for this layer
        import glob as _g
        files = sorted(_g.glob(str(ICA_DIR / slug
                                   / f"layer{layer:02d}_seed{args.seed:04d}_K*.json")))
        assert files, f"no ICA file for layer {layer} in {ICA_DIR}"
        best, best_sil, best_fp = None, -2.0, ""
        for fp in files:
            dd = json.loads(Path(fp).read_text())
            s_ = max(dd.get("silhouettes") or [-1.0])
            if s_ > best_sil:
                best_sil, best, best_fp = s_, dd, fp
        comps_all = np.array(best["components"], dtype=np.float32)
        npz = ACT_DIR / slug / f"layer{layer:02d}_seed{args.seed:04d}.npz"
        repro_all = compute_split_reproducibility(npz, comps_all, seed=args.seed)
        order = np.argsort(-repro_all)
        comps = comps_all[order][:N_AXES]
        repro = [float(x) for x in repro_all[order][:N_AXES]]

        # (i) alignment spectrum for EVERY axis -- reported, never used to select
        spectrum = [{"axis_rank": int(r), "ica_index": int(order[r]),
                     "split_repro": float(repro_all[order[r]]),
                     **{f"abs_cos_{k}": abs(float(comps_all[order[r]] @ hd[k]))
                        for k in VAD_KEYS},
                     "abs_cos_max_vad": max(
                         abs(float(comps_all[order[r]] @ hd[k]))
                         for k in VAD_KEYS)}
                    for r in range(len(order))]

        dirs: dict[str, np.ndarray] = {}
        res_ratio: dict[str, float] = {}
        for i in range(N_AXES):
            dirs[f"axis{i}"] = comps[i]
            ap_, rr = residualise(comps[i], Q)
            dirs[f"axis{i}_resid"] = ap_
            res_ratio[f"axis{i}"] = rr

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
            for k in VAD_KEYS:
                assert abs(float(dirs[f"axis{i}_resid"] @ hd[k])) < 1e-3, (i, k)

        print(f"[res] axes repro={[round(x,4) for x in repro]} | "
              f"residual norm ratio={{{', '.join(f'axis{i}:{res_ratio[f0]:.3f}' for i, f0 in enumerate([f'axis{j}' for j in range(N_AXES)]))}}}",
              flush=True)
        print(f"[res] max|cos| vs VAD per top-{N_AXES} axis: "
              f"{[round(spectrum[i]['abs_cos_max_vad'], 3) for i in range(N_AXES)]}",
              flush=True)

        if args.dry_run:
            print(json.dumps({"spectrum": spectrum[:6], "qinfo": qinfo,
                              "res_ratio": res_ratio}, indent=2))
            return 0

        base = [forward_metrics(model, tok, dec, t, layer, None, 0.0)
                for t in texts]
        names = list(dirs)
        rows: list[dict[str, Any]] = []
        for a_rel in ALPHAS:
            js: dict[str, list[float]] = {n: [] for n in names}
            ppl: dict[str, list[float]] = {n: [] for n in names}
            ent: dict[str, list[float]] = {n: [] for n in names}
            for si, t in enumerate(texts):
                a_abs = a_rel * norms[si]
                for pol in (1.0, -1.0):
                    for n in names:
                        m = forward_metrics(model, tok, dec, t, layer,
                                            dirs[n] * pol, a_abs)
                        js[n].append(js_div(m, base[si]))
                        ent[n].append(m["entropy_nats"]
                                      - base[si]["entropy_nats"])
                        ppl[n].append(m["ppl"] / base[si]["ppl"]
                                      if base[si]["ppl"] > 0 else float("nan"))
                if (si + 1) % 10 == 0:
                    print(f"[res]   L{layer} a={a_rel} {si+1}/{len(texts)}",
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
                mm, ss = mean_std(js[n])
                row[f"js_{n}_mean"], row[f"js_{n}_std"] = mm, ss
                row[f"ppl_ratio_{n}_mean"] = mean_std(ppl[n])[0]
                row[f"entropy_delta_{n}_mean"] = mean_std(ent[n])[0]
                row[f"ppl_collapse_frac_{n}"] = float(np.mean(
                    [1.0 if (not math.isnan(x)) and x > PPL_COLLAPSE_RATIO else 0.0
                     for x in ppl[n]]))
            row["js_randfloor_mean"] = mean_std(randfloor)[0]
            row["js_orthofloor_mean"] = mean_std(orthofloor)[0]
            for i in range(N_AXES):
                for tag in (f"axis{i}", f"axis{i}_resid"):
                    row[f"paired_{tag}_vs_randfloor"] = paired_test(js[tag], randfloor)
                    row[f"paired_{tag}_vs_orthofloor"] = paired_test(js[tag], orthofloor)
                row[f"paired_axis{i}_vs_resid"] = paired_test(
                    js[f"axis{i}"], js[f"axis{i}_resid"], alternative="two-sided")
                jm_a = row[f"js_axis{i}_mean"]
                jm_r = row[f"js_axis{i}_resid_mean"]
                row[f"attenuation_axis{i}"] = (1.0 - jm_r / jm_a
                                               if jm_a > 0 else float("nan"))
                row[f"residual_norm_ratio_axis{i}"] = res_ratio[f"axis{i}"]
            rows.append(row)

        layers_out.append({
            "layer": layer, "model_id": args.model, "seed": args.seed,
            "hidden_dim": D, "axis_source_file": best_fp,
            "axis_ica_k": int(best["k"]),
            "axis_split_repro_top3": repro,
            "discovery_indices": disc,
            "discovery_ids": [s["id"] for s in stim],
            "last_token_norm_mean": float(norms.mean()),
            "human_vad_subspace": qinfo,
            "human_vad_fit_n": len(texts),
            "alignment_spectrum_ALL_axes": spectrum,
            "residual_norm_ratio": res_ratio,
            "rows": rows,
        })
        out_path.write_text(json.dumps(
            {"env": env_manifest({"prereg_commit": args.prereg_commit,
                                  "split_sha256": hashlib.sha256(
                                      SPLIT_PATH.read_bytes()).hexdigest(),
                                  "layers_complete": [L["layer"] for L in layers_out],
                                  "status": "IN_PROGRESS"}),
             "layers": layers_out}, indent=2, ensure_ascii=False))
        print(f"[res] wrote {out_path}", flush=True)

    # ---- BH families (prereg §5 / §10.4) ----
    fams: dict[str, list[dict[str, Any]]] = {"A_axis_vs_rand": [],
                                             "B_axis_vs_ortho": [],
                                             "R_resid_vs_rand": [],
                                             "R_resid_vs_ortho": []}
    for L in layers_out:
        for r in L["rows"]:
            for i in range(N_AXES):
                fams["A_axis_vs_rand"].append(r[f"paired_axis{i}_vs_randfloor"])
                fams["B_axis_vs_ortho"].append(r[f"paired_axis{i}_vs_orthofloor"])
                fams["R_resid_vs_rand"].append(r[f"paired_axis{i}_resid_vs_randfloor"])
                fams["R_resid_vs_ortho"].append(r[f"paired_axis{i}_resid_vs_orthofloor"])
    fam_sizes = {}
    for fam, tests in fams.items():
        for t, q in zip(tests, bh_fdr([t["wilcoxon_p"] for t in tests])):
            t["wilcoxon_q_bh"] = q
        fam_sizes[fam] = len(tests)
    print(f"[res] BH family sizes: {fam_sizes}")

    # ---- M1 monotonicity + R1/R2/R3 verdicts ----
    verdicts: dict[str, Any] = {"R1_axes_surviving_residualisation": [],
                                "M1_monotonicity": [], "R3_spearman": None}
    att_pairs: list[tuple[float, float]] = []
    for L in layers_out:
        al = [r["alpha_rel"] for r in L["rows"]]
        for i in range(N_AXES):
            jm = [r[f"js_axis{i}_mean"] for r in L["rows"]]
            rho, pv = sp_stats.spearmanr(al, jm)
            verdicts["M1_monotonicity"].append(
                {"layer": L["layer"], "axis": i, "spearman_rho": float(rho),
                 "p": float(pv), "M1_pass": bool(rho >= 0.80)})
            surv = []
            for r in L["rows"]:
                a_r = r[f"paired_axis{i}_vs_randfloor"]
                a_o = r[f"paired_axis{i}_vs_orthofloor"]
                s_r = r[f"paired_axis{i}_resid_vs_randfloor"]
                s_o = r[f"paired_axis{i}_resid_vs_orthofloor"]
                ppl_ok = r[f"ppl_ratio_axis{i}_resid_mean"] < PPL_COLLAPSE_RATIO
                raw_ok = (a_r["mean_diff"] > 0 and a_r["wilcoxon_q_bh"] < 0.05
                          and a_o["mean_diff"] > 0 and a_o["wilcoxon_q_bh"] < 0.05)
                res_ok = (s_r["mean_diff"] > 0 and s_r["wilcoxon_q_bh"] < 0.05
                          and s_o["mean_diff"] > 0 and s_o["wilcoxon_q_bh"] < 0.05)
                if raw_ok and res_ok and ppl_ok:
                    surv.append({"alpha_rel": r["alpha_rel"],
                                 "attenuation": r[f"attenuation_axis{i}"],
                                 "resid_vs_rand_delta": s_r["cliffs_delta"],
                                 "resid_q_rand": s_r["wilcoxon_q_bh"],
                                 "resid_q_ortho": s_o["wilcoxon_q_bh"],
                                 "ppl_ratio_resid": r[f"ppl_ratio_axis{i}_resid_mean"]})
                if r["alpha_rel"] == 0.05:
                    att_pairs.append((L["alignment_spectrum_ALL_axes"][i]
                                      ["abs_cos_max_vad"],
                                      r[f"attenuation_axis{i}"]))
            if surv:
                verdicts["R1_axes_surviving_residualisation"].append(
                    {"layer": L["layer"], "axis": i,
                     "split_repro": L["axis_split_repro_top3"][i],
                     "abs_cos_max_vad": L["alignment_spectrum_ALL_axes"][i]
                                        ["abs_cos_max_vad"],
                     "residual_norm_ratio": L["residual_norm_ratio"][f"axis{i}"],
                     "alphas_passing": surv})
    if len(att_pairs) >= 3:
        xs = [p[0] for p in att_pairs]
        ys = [p[1] for p in att_pairs]
        rho, pv = sp_stats.spearmanr(xs, ys)
        verdicts["R3_spearman"] = {
            "note": ("R3 predicted rho > 0: axes more aligned with human VAD "
                     "should attenuate more. alpha_rel=0.05, all layers pooled."),
            "n": len(att_pairs), "spearman_rho": float(rho), "p": float(pv),
            "R3_supported": bool(rho > 0 and pv < 0.05)}
    verdicts["R1_supported"] = bool(verdicts["R1_axes_surviving_residualisation"])

    out_path.write_text(json.dumps(
        {"env": env_manifest({"prereg_commit": args.prereg_commit,
                              "split_sha256": hashlib.sha256(
                                  SPLIT_PATH.read_bytes()).hexdigest(),
                              "bh_family_sizes": fam_sizes,
                              "layers_complete": [L["layer"] for L in layers_out],
                              "status": "COMPLETE"}),
         "verdicts": verdicts, "layers": layers_out}, indent=2,
        ensure_ascii=False))
    print(f"\n[res] R1 supported: {verdicts['R1_supported']} "
          f"({len(verdicts['R1_axes_surviving_residualisation'])} axis-cells)")
    print(f"[res] FINAL -> {out_path}")
    print("[res] DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
