#!/usr/bin/env python3
"""Positive control, rebuilt: does the Warriner-valence direction move the
next-token distribution more than the noise floor?

Scope (Nomura, 2026-09-25): positive control ONLY.  No axis sweep is re-run,
no axis search is performed, and NO judge LLM is ever loaded (PI directive:
judges are trained on human emotion frameworks, so using them to validate a
claim about AI-native axes is circular).

Why this rewrite exists
-----------------------
Three defects were found in the previous positive-control code and are fixed
here.  Each is checked by an assertion or reported in the output.

D1  POOLING MISMATCH (the hypothesis under test).
    `run_intervention.compute_positive_control_direction` regresses valence on
    MEAN-POOLED activations (run_intervention.py:492), while the ICA axes and
    the alpha reference norm come from the LAST-TOKEN activation
    (extract_activations.py:77).  Both poolings are measured here.

D2  SILENT FIT-SET COLLAPSE (defect in run_pos_ctrl_pooling_check.py).
    That script used a Warriner lookup without suffix stripping.  The VAD file
    holds only 2298 words, so `joyful`, `elated`, `excited`, ... return None and
    the stimulus is silently dropped from the regression.  Measured: the fit set
    collapsed from 30 to 8 stimuli (first30) and from 40 to 10 (all40), with a
    valence composition unlike the main sweep's.  Its "positive control" was
    therefore a regression on 8-10 stimuli and did NOT reproduce the main
    sweep's direction.  This script uses `stimulus_valence` copied verbatim from
    run_intervention.py (with suffix stripping) and ASSERTS the expected fit-set
    size, aborting rather than silently shrinking.

D3  NOISE FLOOR DEFINED BY A SINGLE RANDOM DRAW.
    `reaggregate_c1_judgefree.py` groups by (k_idx, alpha_rel), so its
    `paired_pos_vs_rand` compared one fixed pos direction against the single
    k_idx-th random direction.  The sign flips with the draw (layer 10,
    alpha=0.01: k=0 gives -4.94e-05 q=0.144, but k=1/3/4 give +2.9e-05/+3.2e-05/
    +3.6e-05 with q=0.009/0.003/0.003).  Here the floor is the MEAN over the 5
    random directions, and the per-draw tests are ALSO reported so the
    draw-sensitivity stays visible.

Conditions
----------
directions
  (a)  pos_lasttoken_first30 : valence regressed on LAST-TOKEN activations, stim 0-29
  (a') pos_lasttoken_all40   : same, all 40 stimuli (valence-balanced: 0-19 positive,
                               20-39 negative, so "first 30" is imbalanced 20/10)
  (b)  pos_meanpool_first30  : valence regressed on MEAN-POOLED activations, stim 0-29
                               (reproduces the main sweep's positive control)
  (c)  rand_0..4             : random unit directions, identical rng series to
                               run_intervention.py:777
                               default_rng(seed + 9999).standard_normal((5, D))
  (d)  ortho_0..4            : Gram-Schmidt orthogonalisation of rand_i against ICA
                               axis i, identical to run_intervention.py:785-791.
                               Axes = split-half-reproducibility top 5, as in the
                               main sweep (axis_selection=split_repro, top_k_axes=5).

hook scope   last_token (MAIN condition) and all_positions (secondary)
alpha        alpha_abs_i = alpha_rel * ||h_i^(last)||, alpha_rel in {0.01, 0.05},
             both polarities
stimuli      40 (stimuli_e4.json, indices 0-39; identical to the main sweep)
metric       Jensen-Shannon divergence of the next-token distribution vs the
             un-intervened baseline (top-100 union, renormalised) + entropy delta
statistics   paired Wilcoxon (one-sided greater, zsplit) + bootstrap 95% CI of the
             mean difference (10k resamples) + Cliff's delta + BH-FDR

Pre-specified decision rule (fixed in
03_解析/preregistration/posctrl_v2_deviation_20260925.md BEFORE this ran)
-----------------------------------------------------------------------
Primary BH family: the MAIN condition (last_token hook) only,
{4 layers} x {2 alpha_rel} x {3 pos variants} = 24 tests of pos vs rand_mean.
A layer's positive control PASSES iff, for at least one alpha_rel,
pos_lasttoken_all40 or pos_lasttoken_first30 has mean_diff > 0 and
q_bh_primary < 0.05.  Layers that fail are not interpreted.

Usage
-----
    python3 run_pos_ctrl_v2.py --self-check
    python3 run_pos_ctrl_v2.py --layers 5 7 10 12 \
        --stimuli /path/to/work/code/stimuli/stimuli_e4.json \
        --output-dir /path/to/work/results/pos_ctrl_v2

Author: 中村 (NativeAffect, paper 2)   Date: 2026-09-25
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

# CUDA_VISIBLE_DEVICES must be set BEFORE torch is imported (lab rule).
# The launcher exports it; never write "cuda:0"/"cuda:1" anywhere.
_CVD = os.environ.get("CUDA_VISIBLE_DEVICES")

import numpy as np  # noqa: E402
from scipy import stats as sp_stats  # noqa: E402

BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 20260925
RAND_SEED_OFFSET = 9999   # identical to run_intervention.py:777
N_CTRL_DIRS = 5           # == top_k_axes of the main sweep (K_AXES=5)
TOP_K_VOCAB = 100         # identical to compute_next_token_metrics default
MAX_LENGTH = 128
VAD_PATH_DEFAULT = Path(
    "/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
ACT_DIR = Path("/path/to/work/results/activations")

POS_VARIANTS = ("pos_lasttoken_first30", "pos_lasttoken_all40",
                "pos_meanpool_first30")
# variants used for the layer-level PASS decision (last-token pooling only)
DECISION_VARIANTS = ("pos_lasttoken_all40", "pos_lasttoken_first30")


# =========================================================================
# statistics
# =========================================================================
def bootstrap_ci_mean(values: Sequence[float], n_boot: int = BOOTSTRAP_N,
                      seed: int = BOOTSTRAP_SEED,
                      alpha: float = 0.05) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean."""
    arr = np.asarray([v for v in values if not math.isnan(v)], dtype=float)
    if arr.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_boot, arr.size))
    means = arr[idx].mean(axis=1)
    lo, hi = np.quantile(means, [alpha / 2.0, 1.0 - alpha / 2.0])
    return (float(lo), float(hi))


def paired_test(a: Sequence[float], b: Sequence[float],
                alternative: str = "greater") -> dict[str, float]:
    """Paired Wilcoxon + bootstrap CI + Cliff's delta on the paired differences."""
    pairs = [(x, y) for x, y in zip(a, b)
             if not (math.isnan(x) or math.isnan(y))]
    if len(pairs) < 2:
        return {"n": len(pairs), "mean_diff": float("nan"),
                "std_diff": float("nan"), "wilcoxon_p": float("nan"),
                "ci_lo": float("nan"), "ci_hi": float("nan"),
                "cliffs_delta": float("nan")}
    xa = np.array([p[0] for p in pairs], dtype=float)
    xb = np.array([p[1] for p in pairs], dtype=float)
    diff = xa - xb
    if np.allclose(diff, 0.0):
        w_p = 1.0
    else:
        try:
            _, w_p = sp_stats.wilcoxon(xa, xb, alternative=alternative,
                                       zero_method="zsplit")
        except ValueError:
            w_p = float("nan")
    lo, hi = bootstrap_ci_mean(diff.tolist())
    return {"n": int(diff.size), "mean_diff": float(diff.mean()),
            "std_diff": float(diff.std(ddof=1)), "wilcoxon_p": float(w_p),
            "ci_lo": lo, "ci_hi": hi,
            "cliffs_delta": float((diff > 0).mean() - (diff < 0).mean())}


def bh_fdr(pvals: Sequence[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values; NaN in -> NaN out."""
    arr = np.asarray(pvals, dtype=float)
    ok = ~np.isnan(arr)
    out = np.full(arr.shape, np.nan)
    p = arr[ok]
    if p.size == 0:
        return out.tolist()
    order = np.argsort(p)
    m = p.size
    adj = p[order] * m / (np.arange(m) + 1)
    adj = np.clip(np.minimum.accumulate(adj[::-1])[::-1], 0.0, 1.0)
    restored = np.empty(m)
    restored[order] = adj
    out[ok] = restored
    return out.tolist()


def mean_std(values: Sequence[float]) -> tuple[float, float]:
    arr = np.asarray([v for v in values if not math.isnan(v)], dtype=float)
    if arr.size == 0:
        return (float("nan"), float("nan"))
    return (float(arr.mean()),
            float(arr.std(ddof=1)) if arr.size > 1 else 0.0)


# =========================================================================
# Warriner valence -- copied VERBATIM from run_intervention.py (398-446)
# so that pos_meanpool_first30 reproduces the main sweep's direction exactly.
# =========================================================================
def load_warriner(vad_path: Path = VAD_PATH_DEFAULT) -> dict[str, float]:
    vad: dict[str, float] = {}
    if not vad_path.exists():
        print(f"[pos2] WARNING: VAD file not found: {vad_path}")
        return vad
    with open(vad_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            word = row.get("word", row.get("Word", "")).strip().lower()
            val_str = row.get("valence", row.get("V.Mean.Sum", "")).strip()
            try:
                vad[word] = float(val_str)
            except (ValueError, KeyError):
                pass
    print(f"[pos2] Loaded {len(vad)} VAD entries from {vad_path}")
    return vad


def stimulus_valence(text: str, vad: dict[str, float]) -> float | None:
    """Mean Warriner valence (1-9) of the words in `text`; None if no match.

    Suffix stripping is ESSENTIAL: the VAD file has only 2298 words, so
    'joyful' is absent while 'joy' is present.  Dropping the stripping silently
    removes every positive stimulus from the fit (defect D2).
    """
    _SUFFIXES = ["fully", "fulness", "fulness", "ful", "ness", "ly",
                 "ing", "tion", "ed", "er", "est", "s"]

    def _lookup(w: str) -> float | None:
        if w in vad:
            return vad[w]
        for suf in _SUFFIXES:
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                stem = w[: -len(suf)]
                if stem in vad:
                    return vad[stem]
        return None

    words = re.findall(r"[a-zA-Z']+", text.lower())
    scores = [s for s in (_lookup(w) for w in words) if s is not None]
    if not scores:
        return None
    return float(np.mean(scores))


# =========================================================================
# hooks
# =========================================================================
class InterventionHook:
    """Add alpha * direction to the hidden state at one decoder layer.

    scope='all_positions' reproduces run_intervention._InterventionHook.
    scope='last_token'    adds the delta only at the final sequence position.
    """

    def __init__(self, direction: np.ndarray, alpha: float,
                 scope: str = "last_token") -> None:
        import torch
        if scope not in ("last_token", "all_positions"):
            raise ValueError(f"bad scope: {scope}")
        self.scope = scope
        self.delta = torch.tensor(alpha * direction, dtype=torch.float16)

    def __call__(self, module: Any, inputs: tuple, output: Any) -> Any:
        hs = output[0] if isinstance(output, tuple) else output
        delta = self.delta.to(hs.device).to(hs.dtype)
        if self.scope == "all_positions":
            hs_mod = hs + delta.unsqueeze(0).unsqueeze(0)
        else:
            hs_mod = hs.clone()
            hs_mod[:, -1, :] = hs_mod[:, -1, :] + delta
        if isinstance(output, tuple):
            return (hs_mod,) + output[1:]
        return hs_mod


# =========================================================================
# next-token metrics / JS  (same maths as run_intervention.py)
# =========================================================================
def next_token_metrics(model: Any, tok: Any, decoder_layers: Any, text: str,
                       layer: int, direction: np.ndarray | None, alpha: float,
                       scope: str = "last_token",
                       top_k: int = TOP_K_VOCAB) -> dict[str, Any]:
    import torch
    import torch.nn.functional as F

    # batch of 1, no padding -> position -1 is the true final content token
    enc = tok(text, return_tensors="pt", truncation=True,
              max_length=MAX_LENGTH)
    device = next(model.parameters()).device
    enc = {k: v.to(device) for k, v in enc.items()}

    handle = None
    if direction is not None:
        handle = decoder_layers[layer].register_forward_hook(
            InterventionHook(direction, alpha, scope))
    try:
        with torch.no_grad():
            logits = model(**enc).logits[0, -1, :]
    finally:
        if handle is not None:
            handle.remove()

    probs = F.softmax(logits.float(), dim=-1).cpu().numpy()
    p_pos = probs[probs > 0]
    idx_raw = np.argsort(probs)[-top_k:]
    logp_raw = np.log(probs[idx_raw] + 1e-45)
    order = np.argsort(idx_raw)
    return {"entropy_nats": float(-np.sum(p_pos * np.log(p_pos))),
            "top1_prob": float(probs.max()),
            "_idx": idx_raw[order], "_logp": logp_raw[order]}


def js_divergence(m1: dict[str, Any], m2: dict[str, Any]) -> float:
    """JS divergence over the union of the two top-k supports, renormalised."""
    idx1, lp1 = m1["_idx"], m1["_logp"]
    idx2, lp2 = m2["_idx"], m2["_logp"]
    all_idx = np.union1d(idx1, idx2)
    p = np.zeros(all_idx.size)
    q = np.zeros(all_idx.size)
    pos1 = np.searchsorted(idx1, all_idx)
    hit1 = (pos1 < idx1.size) & (idx1[np.clip(pos1, 0, idx1.size - 1)] == all_idx)
    p[hit1] = np.exp(lp1[pos1[hit1]])
    pos2 = np.searchsorted(idx2, all_idx)
    hit2 = (pos2 < idx2.size) & (idx2[np.clip(pos2, 0, idx2.size - 1)] == all_idx)
    q[hit2] = np.exp(lp2[pos2[hit2]])
    p /= (p.sum() + 1e-45)
    q /= (q.sum() + 1e-45)
    m = 0.5 * (p + q)
    kl_pm = np.sum(p * np.log(p / (m + 1e-45) + 1e-45))
    kl_qm = np.sum(q * np.log(q / (m + 1e-45) + 1e-45))
    return float(0.5 * kl_pm + 0.5 * kl_qm)


# =========================================================================
# activation capture / direction fitting
# =========================================================================
def capture_activation(model: Any, tok: Any, decoder_layers: Any, text: str,
                       layer: int, pooling: str) -> np.ndarray:
    """Hidden state at `layer`, pooled as requested.

    pooling='last'     -> final token position    (D,)
    pooling='meanpool' -> mean over token positions (D,)

    Batch of 1 and no padding, so 'last' is the true final content token.
    """
    import torch
    if pooling not in ("last", "meanpool"):
        raise ValueError(pooling)
    enc = tok(text, return_tensors="pt", truncation=True,
              max_length=MAX_LENGTH)
    device = next(model.parameters()).device
    enc = {k: v.to(device) for k, v in enc.items()}
    got: list[np.ndarray] = []

    def _hook(module: Any, inp: Any, out: Any) -> None:
        hs = out[0] if isinstance(out, tuple) else out
        hf = hs.float()
        got.append((hf[0, -1] if pooling == "last"
                    else hf.mean(dim=1).squeeze(0)).cpu().numpy())

    h = decoder_layers[layer].register_forward_hook(_hook)
    try:
        with torch.no_grad():
            model(**enc)
    finally:
        h.remove()
    return got[0]


def valence_direction(model: Any, tok: Any, decoder_layers: Any,
                      texts: Sequence[str], layer: int, pooling: str,
                      vad: dict[str, float],
                      expect_n_fit: int) -> tuple[np.ndarray, dict[str, Any]]:
    """Unit-norm valence direction (direction ∝ X.T @ y, y z-scored).

    Aborts if the fit set is not exactly `expect_n_fit` stimuli: a silent
    shrink of this set is defect D2 and must never pass unnoticed.
    """
    acts: list[np.ndarray] = []
    vals: list[float] = []
    dropped: list[int] = []
    for i, t in enumerate(texts):
        v = stimulus_valence(t, vad)
        if v is None:
            dropped.append(i)
            continue
        acts.append(capture_activation(model, tok, decoder_layers, t, layer,
                                       pooling))
        vals.append(v)
    if len(acts) != expect_n_fit:
        raise RuntimeError(
            f"fit-set size {len(acts)} != expected {expect_n_fit} "
            f"(pooling={pooling}, dropped indices={dropped}). "
            "Refusing to fit a silently-shrunken positive control (defect D2).")
    X = np.stack(acts).astype(np.float64)
    y = np.asarray(vals, dtype=np.float64)
    y_z = (y - y.mean()) / (y.std() + 1e-8)
    d = X.T @ y_z
    n = float(np.linalg.norm(d))
    if n < 1e-12:
        raise RuntimeError("valence direction is near-zero")
    info = {"n_fit": len(acts), "pooling": pooling,
            "valence_mean": float(y.mean()), "valence_std": float(y.std()),
            "valence_min": float(y.min()), "valence_max": float(y.max()),
            "n_pos_stimuli_in_fit": int(sum(1 for i, _ in enumerate(texts)
                                            if i < 20 and i not in dropped)),
            "dropped_indices": dropped}
    return (d / n).astype(np.float32), info


def load_axes_top5(model_id: str, layer: int, seed: int,
                   n_axes: int) -> tuple[np.ndarray, list[float]]:
    """Top-`n_axes` ICA axes by split-half reproducibility.

    Identical code path to the main sweep (axis_selection=split_repro,
    top_k_axes=5): run_intervention.py:736-763.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_ica import compute_split_reproducibility, load_ica, model_slug

    data = load_ica(model_id, layer, seed)
    comps = np.array(data["components"], dtype=np.float32)   # (K, D)
    act_path = (ACT_DIR / model_slug(model_id)
                / f"layer{layer:02d}_seed{seed:04d}.npz")
    if not act_path.exists():
        raise FileNotFoundError(act_path)
    scores = compute_split_reproducibility(act_path, comps, seed=seed)
    order = np.argsort(-scores)
    comps = comps[order][:n_axes]
    return comps, [float(x) for x in scores[order][:n_axes]]


# =========================================================================
def env_manifest(extra: dict[str, Any]) -> dict[str, Any]:
    def _sh(cmd: list[str]) -> str:
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=15).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""

    # physical uuid of the VISIBLE device(s) only (nvidia-smi ignores CVD)
    uuid_all = _sh(["nvidia-smi", "--query-gpu=index,uuid",
                    "--format=csv,noheader"]).splitlines()
    uuid_map = {}
    for line in uuid_all:
        parts = [x.strip() for x in line.split(",")]
        if len(parts) == 2:
            uuid_map[parts[0]] = parts[1]
    visible = [uuid_map.get(i.strip(), "?")
               for i in (_CVD or "").split(",") if i.strip() != ""]

    man: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(
            Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "hostname": platform.node(),
        "platform": platform.platform(),
        "git_commit": _sh(["git", "rev-parse", "HEAD"]) or
                      "NO_GIT_REPO_ON_SERVER (see script_sha256)",
        "CUDA_VISIBLE_DEVICES": _CVD,
        "gpu_uuid_visible_physical": visible,
        "gpu_uuid_all_on_host": uuid_map,
        "bootstrap_n": BOOTSTRAP_N,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "top_k_vocab": TOP_K_VOCAB,
        "max_length": MAX_LENGTH,
        "judge_llm_loaded": False,
        "known_upstream_caveat": (
            "extract_activations.py uses padding=True (padding_side='right') "
            "with batch_size=8 and then takes hs[:, -1, :]. E4/E1 stimuli are "
            "not equal length (E4: 9-13 tokens), so for every stimulus that is "
            "not the longest in its batch that index is a PAD position, not the "
            "final content token. The ICA axes -- and therefore the ortho_* "
            "directions used here as condition (d) -- inherit this. NOT fixed "
            "by this script; reported to PI."),
    }
    try:
        import torch
        man["torch"] = torch.__version__
        man["cuda"] = torch.version.cuda
        man["cuda_available"] = bool(torch.cuda.is_available())
        man["device_count_visible"] = int(torch.cuda.device_count())
    except Exception:  # noqa: BLE001
        pass
    man.update(extra)
    return man


# =========================================================================
def self_check() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if cond else 'FAIL'}] {name}")
        ok &= bool(cond)

    r = paired_test([2.0] * 30, [1.0] * 30)
    chk("paired_test constant shift",
        abs(r["mean_diff"] - 1.0) < 1e-12 and r["cliffs_delta"] == 1.0)
    chk("paired_test identical -> p=1",
        paired_test([1.0] * 20, [1.0] * 20)["wilcoxon_p"] == 1.0)
    q = bh_fdr([0.001, 0.02, 0.5])
    chk("bh_fdr monotone", q[0] <= q[1] <= q[2])
    chk("bh_fdr NaN preserved", math.isnan(bh_fdr([0.01, float("nan")])[1]))

    m1 = {"_idx": np.array([1, 2, 3]), "_logp": np.log([0.2, 0.3, 0.5])}
    chk("JS(identical)=0", abs(js_divergence(m1, m1)) < 1e-12)
    m3 = {"_idx": np.array([7, 8]), "_logp": np.log([0.5, 0.5])}
    chk("JS(disjoint)=ln2", abs(js_divergence(m1, m3) - math.log(2)) < 1e-9)

    # D2 guard: the fit set must be 30/40 under the stripping lookup
    vad = load_warriner()
    if vad:
        stim = json.loads(Path(
            "/path/to/work/code/stimuli/stimuli_e4.json"
        ).read_text())[:40]
        vals = [stimulus_valence(s["text"], vad) for s in stim]
        n30 = sum(1 for v in vals[:30] if v is not None)
        n40 = sum(1 for v in vals if v is not None)
        chk(f"D2 guard: fit set first30={n30} (expect 30)", n30 == 30)
        chk(f"D2 guard: fit set all40={n40} (expect 40)", n40 == 40)
        pos = np.mean([v for v in vals[:20]])
        neg = np.mean([v for v in vals[20:]])
        chk(f"valence separates polarity (pos {pos:.2f} > neg {neg:.2f})",
            pos > neg)
        # the no-stripping lookup is what collapsed: demonstrate it here
        plain = [None if not [w for w in re.findall(r"[a-z']+", s["text"].lower())
                              if w in vad] else 1 for s in stim]
        chk("no-stripping lookup would collapse the fit set (<=10)",
            sum(1 for p in plain if p is not None) <= 10)
    else:
        print("  [SKIP] VAD file unavailable")

    # rand direction series must match run_intervention.py:777 exactly
    rng = np.random.default_rng(42 + RAND_SEED_OFFSET)
    rd = rng.standard_normal((N_CTRL_DIRS, 8)).astype(np.float32)
    rng2 = np.random.default_rng(42 + 9999)
    chk("rand rng series reproducible",
        np.allclose(rd, rng2.standard_normal((N_CTRL_DIRS, 8)).astype(np.float32)))

    # Gram-Schmidt: ortho must be orthogonal to its axis and unit-norm
    ax = np.zeros(8, dtype=np.float32); ax[0] = 1.0
    v = rd[0].copy()
    v -= ax * float(np.dot(v, ax))
    v /= np.linalg.norm(v) + 1e-12
    chk("ortho dir is orthogonal to axis", abs(float(np.dot(v, ax))) < 1e-6)
    chk("ortho dir is unit norm", abs(float(np.linalg.norm(v)) - 1.0) < 1e-6)

    try:
        import torch

        class _D:
            pass

        d = np.zeros(4, dtype=np.float32); d[0] = 1.0
        hs = torch.zeros(1, 3, 4)
        o_last = InterventionHook(d, 2.0, "last_token")(_D(), (), hs)
        o_all = InterventionHook(d, 2.0, "all_positions")(_D(), (), hs)
        chk("last_token hook touches only the final position",
            float(o_last[0, 0, 0]) == 0.0 and float(o_last[0, 2, 0]) == 2.0)
        chk("all_positions hook touches every position",
            float(o_all[0, 0, 0]) == 2.0 and float(o_all[0, 2, 0]) == 2.0)
        chk("hook does not mutate the input tensor in place",
            float(hs[0, 2, 0]) == 0.0)
    except ImportError:
        print("  [SKIP] torch unavailable for hook checks")

    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# =========================================================================
def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=[5, 7, 10, 12])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--alphas-rel", type=float, nargs="+", default=[0.01, 0.05])
    ap.add_argument("--n-stim", type=int, default=40)
    ap.add_argument("--n-pos-fit", type=int, default=30)
    ap.add_argument("--n-ctrl-dirs", type=int, default=N_CTRL_DIRS)
    ap.add_argument("--stimuli", type=Path)
    ap.add_argument("--vad-path", type=Path, default=VAD_PATH_DEFAULT)
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="build directions and exit before the sweep")
    args = ap.parse_args()

    if args.self_check:
        return self_check()
    if args.stimuli is None or args.output_dir is None:
        ap.error("--stimuli and --output-dir are required")
    if _CVD is None:
        print("[pos2] FATAL: CUDA_VISIBLE_DEVICES is not set (lab GPU rule). "
              "Export it in the launcher.", file=sys.stderr)
        return 4

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    stim_bytes = args.stimuli.read_bytes()
    stimuli = json.loads(stim_bytes)[: args.n_stim]
    texts = [s["text"] for s in stimuli]
    ids = [s["id"] for s in stimuli]
    data_hash = hashlib.sha256(stim_bytes).hexdigest()[:16]
    print(f"[pos2] {len(texts)} stimuli, data_hash={data_hash}")

    vad = load_warriner(args.vad_path)
    if not vad:
        print("[pos2] FATAL: no VAD data", file=sys.stderr)
        return 3

    print(f"[pos2] Loading {args.model} …", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True)
    model.eval()
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        decoder_layers = model.model.layers
    elif hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        decoder_layers = model.transformer.h
    else:
        raise NotImplementedError(type(model).__name__)
    D = int(model.config.hidden_size)
    print(f"[pos2] hidden_dim={D}, n_layers={len(decoder_layers)}", flush=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = args.output_dir / f"pos_ctrl_v2_{stamp}.json"
    all_layers: list[dict[str, Any]] = []
    K = args.n_ctrl_dirs

    for layer in args.layers:
        print(f"\n[pos2] ===== layer {layer} =====", flush=True)

        # ---- alpha reference: per-stimulus LAST-TOKEN norm -------------
        norms = np.array([float(np.linalg.norm(capture_activation(
            model, tok, decoder_layers, t, layer, "last"))) for t in texts])
        meanpool_norms = np.array([float(np.linalg.norm(capture_activation(
            model, tok, decoder_layers, t, layer, "meanpool"))) for t in texts])
        print(f"[pos2] last-token norm: mean={norms.mean():.2f} "
              f"std={norms.std():.2f} | meanpool norm mean="
              f"{meanpool_norms.mean():.2f} (prereg-v5 reference)", flush=True)

        # ---- directions -----------------------------------------------
        dirs: dict[str, np.ndarray] = {}
        fit_info: dict[str, Any] = {}
        d, info = valence_direction(model, tok, decoder_layers,
                                    texts[: args.n_pos_fit], layer, "last",
                                    vad, expect_n_fit=args.n_pos_fit)
        dirs["pos_lasttoken_first30"] = d
        fit_info["pos_lasttoken_first30"] = info
        d, info = valence_direction(model, tok, decoder_layers, texts, layer,
                                    "last", vad, expect_n_fit=len(texts))
        dirs["pos_lasttoken_all40"] = d
        fit_info["pos_lasttoken_all40"] = info
        d, info = valence_direction(model, tok, decoder_layers,
                                    texts[: args.n_pos_fit], layer, "meanpool",
                                    vad, expect_n_fit=args.n_pos_fit)
        dirs["pos_meanpool_first30"] = d
        fit_info["pos_meanpool_first30"] = info

        # (c) random: identical rng series to run_intervention.py:777
        rng = np.random.default_rng(args.seed + RAND_SEED_OFFSET)
        rand_dirs = rng.standard_normal((K, D)).astype(np.float32)
        for i in range(K):
            rand_dirs[i] /= np.linalg.norm(rand_dirs[i]) + 1e-12

        # (d) axis-orthogonal: identical Gram-Schmidt to run_intervention.py:785
        axes, repro = load_axes_top5(args.model, layer, args.seed, K)
        assert axes.shape == (K, D), f"axes shape {axes.shape} != {(K, D)}"
        ortho_dirs = np.zeros_like(axes)
        for i in range(K):
            v = rand_dirs[i].copy()
            v -= axes[i] * float(np.dot(v, axes[i]))
            ortho_dirs[i] = v / (float(np.linalg.norm(v)) + 1e-12)
        print(f"[pos2] axes: split-half repro top{K} = "
              f"{[round(x, 4) for x in repro]}", flush=True)

        for name, dd in dirs.items():
            assert abs(float(np.linalg.norm(dd)) - 1.0) < 1e-4, name
        for i in range(K):
            assert abs(float(np.linalg.norm(rand_dirs[i])) - 1.0) < 1e-4
            assert abs(float(np.linalg.norm(ortho_dirs[i])) - 1.0) < 1e-4
            assert abs(float(np.dot(ortho_dirs[i], axes[i]))) < 1e-3

        all_dirs: dict[str, np.ndarray] = dict(dirs)
        for i in range(K):
            all_dirs[f"rand_{i}"] = rand_dirs[i]
            all_dirs[f"ortho_{i}"] = ortho_dirs[i]
        names = list(all_dirs)

        cos_report = {a: {b: float(np.dot(all_dirs[a], all_dirs[b]))
                          for b in names} for a in names}
        cos_pos_axis = {a: [float(np.dot(dirs[a], axes[i])) for i in range(K)]
                        for a in dirs}

        if args.dry_run:
            print("[pos2] DRY-RUN: directions built, stopping before sweep.")
            print(json.dumps({"fit_info": fit_info,
                              "cos_pos_axis": cos_pos_axis}, indent=2))
            return 0

        baselines = [next_token_metrics(model, tok, decoder_layers, t, layer,
                                        None, 0.0) for t in texts]

        layer_rows: list[dict[str, Any]] = []
        for scope in ("last_token", "all_positions"):
            for a_rel in args.alphas_rel:
                js: dict[str, list[float]] = {n: [] for n in names}
                ent: dict[str, list[float]] = {n: [] for n in names}
                for s_idx, text in enumerate(texts):
                    a_abs = a_rel * norms[s_idx]
                    for pol in (1.0, -1.0):
                        for n in names:
                            m = next_token_metrics(
                                model, tok, decoder_layers, text, layer,
                                all_dirs[n] * pol, a_abs, scope)
                            js[n].append(js_divergence(m, baselines[s_idx]))
                            ent[n].append(m["entropy_nats"]
                                          - baselines[s_idx]["entropy_nats"])
                    if (s_idx + 1) % 10 == 0:
                        print(f"[pos2]   L{layer} {scope} a={a_rel} "
                              f"{s_idx + 1}/{len(texts)}", flush=True)

                n_samples = len(js[names[0]])
                # aggregate floors: per-sample mean over the K control dirs
                rand_mean = [float(np.mean([js[f"rand_{i}"][j]
                                            for i in range(K)]))
                             for j in range(n_samples)]
                ortho_mean = [float(np.mean([js[f"ortho_{i}"][j]
                                             for i in range(K)]))
                              for j in range(n_samples)]

                row: dict[str, Any] = {
                    "layer": layer, "hook_scope": scope, "alpha_rel": a_rel,
                    "condition": "main" if scope == "last_token" else "secondary",
                    "n_samples": n_samples,
                    "alpha_abs_mean": float(a_rel * norms.mean()),
                }
                for n in names:
                    m_, s_ = mean_std(js[n])
                    row[f"js_{n}_mean"] = m_
                    row[f"js_{n}_std"] = s_
                # aggregate noise floors get their own explicit key names so
                # that no f-string can collide with a per-direction key
                for fname, series in (("randfloor", rand_mean),
                                      ("orthofloor", ortho_mean)):
                    m_, s_ = mean_std(series)
                    row[f"js_{fname}_mean"] = m_
                    row[f"js_{fname}_std"] = s_
                for n in names:
                    em, es = mean_std(ent[n])
                    row[f"entropy_delta_{n}_mean"] = em
                    row[f"entropy_delta_{n}_std"] = es

                # ---- contrasts -------------------------------------------
                for pv in POS_VARIANTS:
                    row[f"paired_{pv}_vs_randfloor"] = paired_test(
                        js[pv], rand_mean)
                    row[f"paired_{pv}_vs_orthofloor"] = paired_test(
                        js[pv], ortho_mean)
                    per_rand = [paired_test(js[pv], js[f"rand_{i}"])
                                for i in range(K)]
                    per_orth = [paired_test(js[pv], js[f"ortho_{i}"])
                                for i in range(K)]
                    row[f"per_rand_{pv}"] = per_rand
                    row[f"per_ortho_{pv}"] = per_orth
                    row[f"n_rand_draws_beaten_p05_{pv}"] = int(sum(
                        1 for t in per_rand
                        if t["mean_diff"] > 0 and t["wilcoxon_p"] < 0.05))
                    row[f"n_ortho_draws_beaten_p05_{pv}"] = int(sum(
                        1 for t in per_orth
                        if t["mean_diff"] > 0 and t["wilcoxon_p"] < 0.05))
                    row[f"ratio_{pv}_over_randfloor"] = (
                        row[f"js_{pv}_mean"] / row["js_randfloor_mean"]
                        if row["js_randfloor_mean"] > 0 else float("nan"))
                # pooling contrast: does last-token pooling beat mean-pooling?
                row["paired_lasttoken_vs_meanpool_first30"] = paired_test(
                    js["pos_lasttoken_first30"], js["pos_meanpool_first30"],
                    alternative="two-sided")
                layer_rows.append(row)

        # within-layer BH (m = n rows), for comparability with the old analysis
        for pv in POS_VARIANTS:
            key = f"paired_{pv}_vs_randfloor"
            for r, q in zip(layer_rows,
                            bh_fdr([r[key]["wilcoxon_p"] for r in layer_rows])):
                r[key]["wilcoxon_q_bh_within_layer"] = q

        all_layers.append({
            "layer": layer, "model_id": args.model, "seed": args.seed,
            "stimulus_ids": ids, "n_pos_fit": args.n_pos_fit,
            "hidden_dim": D, "n_ctrl_dirs": K,
            "alpha_reference": "per_stimulus_last_token_norm",
            "last_token_norm_mean": float(norms.mean()),
            "last_token_norm_std": float(norms.std()),
            "meanpool_norm_mean_PREREG_V5_REFERENCE": float(meanpool_norms.mean()),
            "axis_split_repro_top5": repro,
            "pos_fit_info": fit_info,
            "direction_cosines": cos_report,
            "cos_pos_vs_axes": cos_pos_axis,
            "rows": layer_rows,
        })

        # incremental write: one layer done -> on disk immediately
        out_path.write_text(json.dumps(
            {"env": env_manifest({
                "data_hash_stimuli": data_hash,
                "alphas_rel": args.alphas_rel,
                "n_ctrl_dirs": K,
                "rand_rng": f"default_rng({args.seed}+{RAND_SEED_OFFSET})"
                            ".standard_normal((K, D)), rows unit-normalised",
                "decision_rule": (
                    "PRIMARY BH family = main condition (last_token hook) only, "
                    "{layers} x {alpha_rel} x {3 pos variants} tests of "
                    "pos vs rand_mean. A layer PASSES iff some alpha_rel has "
                    "mean_diff>0 and q_bh_primary<0.05 for "
                    "pos_lasttoken_all40 or pos_lasttoken_first30."),
                "prereg_deviation_record": (
                    "03_解析/preregistration/posctrl_v2_deviation_20260925.md"),
                "layers_complete": [L["layer"] for L in all_layers],
                "status": "IN_PROGRESS"}),
             "layers": all_layers}, indent=2, ensure_ascii=False))
        print(f"[pos2] wrote {out_path} (layers so far: "
              f"{[L['layer'] for L in all_layers]})", flush=True)

    # ---- PRIMARY BH family across all layers (main condition only) -----
    primary: list[tuple[dict[str, Any], str]] = []
    for L in all_layers:
        for r in L["rows"]:
            if r["condition"] != "main":
                continue
            for pv in POS_VARIANTS:
                primary.append((r[f"paired_{pv}_vs_randfloor"], pv))
    qs = bh_fdr([t[0]["wilcoxon_p"] for t in primary])
    for (t, _), q in zip(primary, qs):
        t["wilcoxon_q_bh_primary"] = q
    print(f"[pos2] primary BH family size m={len(primary)}")

    # ---- verdicts -------------------------------------------------------
    for L in all_layers:
        def passes(cond: str, pv: str) -> bool:
            return any(
                r[f"paired_{pv}_vs_randfloor"]["mean_diff"] > 0
                and r[f"paired_{pv}_vs_randfloor"].get(
                    "wilcoxon_q_bh_primary" if cond == "main"
                    else "wilcoxon_q_bh_within_layer", float("nan")) < 0.05
                for r in L["rows"] if r["condition"] == cond)

        verdict = {pv: {"main_last_token_hook": passes("main", pv),
                        "secondary_all_positions_hook": passes("secondary", pv)}
                   for pv in POS_VARIANTS}
        verdict["LAYER_POSITIVE_CONTROL_PASSES"] = any(
            verdict[pv]["main_last_token_hook"] for pv in DECISION_VARIANTS)
        L["positive_control_verdict"] = verdict
        print(f"[pos2] layer {L['layer']}: PASS="
              f"{verdict['LAYER_POSITIVE_CONTROL_PASSES']} | "
              + " ".join(f"{pv}:{verdict[pv]['main_last_token_hook']}"
                         for pv in POS_VARIANTS), flush=True)

    out_path.write_text(json.dumps(
        {"env": env_manifest({
            "data_hash_stimuli": data_hash,
            "alphas_rel": args.alphas_rel,
            "n_ctrl_dirs": K,
            "rand_rng": f"default_rng({args.seed}+{RAND_SEED_OFFSET})"
                        ".standard_normal((K, D)), rows unit-normalised",
            "primary_bh_family_size": len(primary),
            "decision_rule": (
                "PRIMARY BH family = main condition (last_token hook) only, "
                "{layers} x {alpha_rel} x {3 pos variants} tests of "
                "pos vs rand_mean. A layer PASSES iff some alpha_rel has "
                "mean_diff>0 and q_bh_primary<0.05 for pos_lasttoken_all40 or "
                "pos_lasttoken_first30."),
            "prereg_deviation_record": (
                "03_解析/preregistration/posctrl_v2_deviation_20260925.md"),
            "layers_complete": [L["layer"] for L in all_layers],
            "status": "COMPLETE"}),
         "layers": all_layers}, indent=2, ensure_ascii=False))
    print(f"\n[pos2] FINAL -> {out_path}")
    print("[pos2] DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
