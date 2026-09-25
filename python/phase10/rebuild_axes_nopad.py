#!/usr/bin/env python3
"""Rebuild the ICA axes from PAD-free last-token activations, and measure how
much the padding bug moved them.

The bug (Nomura directive, 2026-09-25)
--------------------------------------
`extract_activations.py` tokenises with `padding=True` at `batch_size=8` and then
reads `hs[:, -1, :]`.  The tokeniser pads on the RIGHT
(`AutoTokenizer.from_pretrained('swiss-ai/Apertus-v1.1-1.5B').padding_side ==
'right'`) and the stimuli are not equal length, so for every stimulus that is not
the longest in its batch, index -1 is a PAD position rather than the final
content token.  The ICA axes were estimated from those vectors.

What this script does
---------------------
STAGE 1  Re-extract activations with batch_size=1 and NO padding, so index -1 is
         always the true final content token.  Also reproduce the OLD buggy
         extraction (batch 8, right padding, index -1) in the same process, and
         verify it matches the archived .npz -- this confirms the diagnosis
         rather than assuming it.  Reports, per layer, the per-stimulus cosine
         between the correct and the buggy activation.

STAGE 2  Re-run the ICA sweep on the corrected activations
         (run_ica.run_ica_sweep, k_range 5-20, seed 42 -- identical settings to
         the original `run_ica_c1_p1.sh`).

STAGE 3  Split-half reproducibility on the corrected activations, take the top 5
         axes -- the same selection the main sweep used
         (axis_selection=split_repro, top_k_axes=5).

STAGE 4  DAMAGE ASSESSMENT: match old axes to new axes by |cosine| (ICA has sign
         and permutation ambiguity, so a raw element-wise comparison is
         meaningless) and report the matched |cos| per axis.

Nothing is overwritten.  Corrected activations, corrected ICA and the damage
report all go to NEW directories:
    results/activations_nopad/ , results/ica_nopad/ , results/axes_nopad/

Usage
-----
    python3 rebuild_axes_nopad.py --self-check
    python3 rebuild_axes_nopad.py --layers 5 7 10 12 --stage all

Author: 中村 (NativeAffect, paper 2)   Date: 2026-09-25
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_CVD = os.environ.get("CUDA_VISIBLE_DEVICES")

import numpy as np  # noqa: E402

BASE = Path("/path/to/work/results")
ACT_OLD = BASE / "activations"
ACT_NEW = BASE / "activations_nopad"
ICA_OLD = BASE / "ica"
ICA_NEW = BASE / "ica_nopad"
REPORT_DIR = BASE / "axes_nopad"
STIM_E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
MAX_LENGTH = 128
K_RANGE = (5, 20)          # identical to run_ica_c1_p1.sh
OLD_BATCH_SIZE = 8         # identical to launch_extract.sh (the buggy setting)
TOP_K_AXES = 5             # identical to run_c1_sweep_repro.sh K_AXES


def model_slug(model_id: str) -> str:
    return model_id.replace("/", "__").replace(".", "_")


def env_manifest(extra: dict[str, Any]) -> dict[str, Any]:
    def _sh(cmd: list[str]) -> str:
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=15).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""
    uuid_map = {}
    for line in _sh(["nvidia-smi", "--query-gpu=index,uuid",
                     "--format=csv,noheader"]).splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) == 2:
            uuid_map[parts[0]] = parts[1]
    man: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "hostname": platform.node(),
        "platform": platform.platform(),
        "git_commit": _sh(["git", "rev-parse", "HEAD"])
                      or "NO_GIT_REPO_ON_SERVER (see script_sha256)",
        "CUDA_VISIBLE_DEVICES": _CVD,
        "gpu_uuid_visible_physical": [
            uuid_map.get(i.strip(), "?") for i in (_CVD or "").split(",")
            if i.strip()],
        "k_range": list(K_RANGE),
        "top_k_axes": TOP_K_AXES,
        "judge_llm_loaded": False,
    }
    try:
        import torch
        man["torch"] = torch.__version__
        man["cuda"] = torch.version.cuda
    except Exception:  # noqa: BLE001
        pass
    man.update(extra)
    return man


# =========================================================================
# STAGE 1 -- extraction
# =========================================================================
def get_decoder_layers(model: Any) -> Any:
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        return model.transformer.h
    raise NotImplementedError(type(model).__name__)


def extract_nopad(model: Any, tok: Any, layers: list[int],
                  texts: list[str]) -> dict[int, np.ndarray]:
    """batch_size=1, NO padding -> index -1 is always the final content token."""
    import torch
    dec = get_decoder_layers(model)
    store: dict[int, list[np.ndarray]] = {L: [] for L in layers}

    def mk(L: int):
        def hook(module: Any, inp: Any, out: Any) -> None:
            hs = out[0] if isinstance(out, tuple) else out
            store[L].append(hs[0, -1, :].detach().cpu().float().numpy())
        return hook

    handles = [dec[L].register_forward_hook(mk(L)) for L in layers]
    try:
        device = next(model.parameters()).device
        for i, t in enumerate(texts):
            enc = tok(t, return_tensors="pt", truncation=True,
                      max_length=MAX_LENGTH)
            assert "attention_mask" not in enc or int(
                enc["attention_mask"].sum()) == enc["input_ids"].shape[1], (
                "unpadded batch-of-1 must have a fully-attended mask")
            enc = {k: v.to(device) for k, v in enc.items()}
            with torch.no_grad():
                model(**enc)
            if (i + 1) % 100 == 0:
                print(f"[rebuild]   nopad {i + 1}/{len(texts)}", flush=True)
    finally:
        for h in handles:
            h.remove()
    return {L: np.stack(store[L]).astype(np.float32) for L in layers}


def extract_oldstyle(model: Any, tok: Any, layers: list[int],
                     texts: list[str],
                     batch_size: int = OLD_BATCH_SIZE) -> dict[int, np.ndarray]:
    """Reproduce the BUGGY extraction: padding=True, batch 8, index -1."""
    import torch
    dec = get_decoder_layers(model)
    store: dict[int, list[np.ndarray]] = {L: [] for L in layers}

    def mk(L: int):
        def hook(module: Any, inp: Any, out: Any) -> None:
            hs = out[0] if isinstance(out, tuple) else out
            store[L].append(hs[:, -1, :].detach().cpu().float().numpy())
        return hook

    handles = [dec[L].register_forward_hook(mk(L)) for L in layers]
    try:
        device = next(model.parameters()).device
        for s in range(0, len(texts), batch_size):
            enc = tok(texts[s:s + batch_size], return_tensors="pt",
                      padding=True, truncation=True, max_length=MAX_LENGTH)
            enc = {k: v.to(device) for k, v in enc.items()}
            with torch.no_grad():
                model(**enc)
    finally:
        for h in handles:
            h.remove()
    return {L: np.concatenate(store[L], axis=0).astype(np.float32)
            for L in layers}


def pad_stats(tok: Any, texts: list[str],
              batch_size: int = OLD_BATCH_SIZE) -> dict[str, Any]:
    """How many stimuli had index -1 land on a PAD position under the old code."""
    lens = [len(tok(t)["input_ids"]) for t in texts]
    n_pad_per_stim = []
    for s in range(0, len(texts), batch_size):
        chunk = lens[s:s + batch_size]
        m = max(chunk)
        n_pad_per_stim.extend([m - L for L in chunk])
    n_pad = np.array(n_pad_per_stim)
    return {"padding_side": tok.padding_side,
            "batch_size": batch_size,
            "token_len_min": int(min(lens)), "token_len_max": int(max(lens)),
            "n_stimuli": len(texts),
            "n_stimuli_reading_PAD": int((n_pad > 0).sum()),
            "frac_stimuli_reading_PAD": float((n_pad > 0).mean()),
            "pad_offset_mean": float(n_pad.mean()),
            "pad_offset_max": int(n_pad.max())}


def rowwise_cos(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    a = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    b = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-12)
    return np.sum(a * b, axis=1)


# =========================================================================
# STAGE 4 -- axis matching
# =========================================================================
def match_axes(old: np.ndarray, new: np.ndarray) -> dict[str, Any]:
    """Greedy one-to-one match of old axes to new axes by |cosine|.

    ICA components carry arbitrary sign and order, so only |cos| after matching
    is interpretable.
    """
    C = np.abs(old @ new.T)          # (n_old, n_new)
    Cw = C.copy()
    pairs: list[dict[str, Any]] = []
    for _ in range(min(old.shape[0], new.shape[0])):
        i, j = np.unravel_index(np.argmax(Cw), Cw.shape)
        if not np.isfinite(Cw[i, j]):
            break
        pairs.append({"old_idx": int(i), "new_idx": int(j),
                      "abs_cos": float(C[i, j]),
                      "signed_cos": float(old[i] @ new[j])})
        Cw[i, :] = -np.inf
        Cw[:, j] = -np.inf
    matched = [p["abs_cos"] for p in pairs]
    return {"pairs": sorted(pairs, key=lambda p: p["old_idx"]),
            "matched_abs_cos_mean": float(np.mean(matched)) if matched else float("nan"),
            "matched_abs_cos_min": float(np.min(matched)) if matched else float("nan"),
            "matched_abs_cos_max": float(np.max(matched)) if matched else float("nan"),
            "best_abs_cos_per_old_axis": [float(x) for x in C.max(axis=1)]}


# =========================================================================
def self_check() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if cond else 'FAIL'}] {name}")
        ok &= bool(cond)

    A = np.eye(3, dtype=np.float32)
    chk("match_axes: identical sets -> |cos|=1",
        abs(match_axes(A, A)["matched_abs_cos_mean"] - 1.0) < 1e-6)
    P = A[[2, 0, 1]] * np.array([[1.0], [-1.0], [1.0]], dtype=np.float32)
    m = match_axes(A, P)
    chk("match_axes: permuted+sign-flipped -> |cos|=1",
        abs(m["matched_abs_cos_mean"] - 1.0) < 1e-6)
    chk("match_axes: one-to-one (no new_idx reused)",
        len({p["new_idx"] for p in m["pairs"]}) == 3)
    B = np.array([[1.0, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
    R = np.array([[0.0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=np.float32)
    chk("match_axes handles disjoint bases", match_axes(B, R)["pairs"] != [])
    c = rowwise_cos(np.array([[1.0, 0.0]]), np.array([[2.0, 0.0]]))
    chk("rowwise_cos scale-invariant", abs(c[0] - 1.0) < 1e-6)
    c2 = rowwise_cos(np.array([[1.0, 0.0]]), np.array([[0.0, 5.0]]))
    chk("rowwise_cos orthogonal -> 0", abs(c2[0]) < 1e-6)
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# =========================================================================
def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="swiss-ai/Apertus-v1.1-1.5B")
    ap.add_argument("--layers", type=int, nargs="+", default=[5, 7, 10, 12])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--stimuli", type=Path, default=STIM_E1)
    ap.add_argument("--stage", choices=["extract", "all"], default="all")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        return self_check()
    if _CVD is None:
        print("[rebuild] FATAL: CUDA_VISIBLE_DEVICES not set (lab rule).",
              file=sys.stderr)
        return 4

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_ica import compute_split_reproducibility, load_ica, run_ica_sweep

    slug = model_slug(args.model)
    stim_bytes = args.stimuli.read_bytes()
    stimuli = json.loads(stim_bytes)
    texts = [s["text"] for s in stimuli]
    data_hash = hashlib.sha256(stim_bytes).hexdigest()[:16]
    print(f"[rebuild] {len(texts)} stimuli from {args.stimuli} "
          f"hash={data_hash}", flush=True)

    for d in (ACT_NEW / slug, ICA_NEW / slug, REPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORT_DIR / f"axis_damage_report_{stamp}.json"

    print(f"[rebuild] Loading {args.model} …", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True)
    model.eval()

    ps = pad_stats(tok, texts)
    print(f"[rebuild] PAD stats: {json.dumps(ps)}", flush=True)

    # ---------------- STAGE 1 ----------------
    print("[rebuild] STAGE 1: extracting (nopad, batch=1) …", flush=True)
    acts_new = extract_nopad(model, tok, args.layers, texts)
    print("[rebuild] STAGE 1: reproducing OLD buggy extraction (pad, batch=8) …",
          flush=True)
    acts_oldrepro = extract_oldstyle(model, tok, args.layers, texts)

    stage1: dict[str, Any] = {"pad_stats": ps, "layers": {}}
    for L in args.layers:
        new, oldr = acts_new[L], acts_oldrepro[L]
        assert new.shape == oldr.shape, (new.shape, oldr.shape)
        cos_no = rowwise_cos(new, oldr)
        entry: dict[str, Any] = {
            "shape": list(new.shape),
            "cos_correct_vs_buggy_mean": float(cos_no.mean()),
            "cos_correct_vs_buggy_min": float(cos_no.min()),
            "cos_correct_vs_buggy_median": float(np.median(cos_no)),
            "norm_correct_mean": float(np.linalg.norm(new, axis=1).mean()),
            "norm_buggy_mean": float(np.linalg.norm(oldr, axis=1).mean()),
        }
        # confirm the diagnosis against the ARCHIVED npz
        arch = ACT_OLD / slug / f"layer{L:02d}_seed{args.seed:04d}.npz"
        if arch.exists():
            old_arr = np.load(arch, allow_pickle=True)["arr"].astype(np.float32)
            if old_arr.shape == oldr.shape:
                c = rowwise_cos(old_arr, oldr)
                entry["archived_vs_reproduced_buggy_cos_mean"] = float(c.mean())
                entry["archived_vs_reproduced_buggy_cos_min"] = float(c.min())
                c2 = rowwise_cos(old_arr, new)
                entry["archived_vs_correct_cos_mean"] = float(c2.mean())
                entry["archived_vs_correct_cos_min"] = float(c2.min())
        np.savez_compressed(
            ACT_NEW / slug / f"layer{L:02d}_seed{args.seed:04d}.npz",
            arr=new, manifest=json.dumps(env_manifest({
                "layer": L, "data_hash_stimuli": data_hash,
                "extraction": "batch_size=1, no padding, hs[0,-1,:]",
                "supersedes": str(arch)})))
        stage1["layers"][str(L)] = entry
        print(f"[rebuild] L{L}: cos(correct, buggy) mean="
              f"{entry['cos_correct_vs_buggy_mean']:.4f} "
              f"min={entry['cos_correct_vs_buggy_min']:.4f} | "
              f"archived_vs_reproduced="
              f"{entry.get('archived_vs_reproduced_buggy_cos_mean', float('nan')):.4f}",
              flush=True)

    report = {"env": env_manifest({"data_hash_stimuli": data_hash,
                                   "stage": "1_extraction_done"}),
              "stage1_activations": stage1}
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"[rebuild] wrote {report_path}", flush=True)

    if args.stage == "extract":
        print("[rebuild] stopping after STAGE 1 (--stage extract)")
        return 0

    # free the model: stages 2-4 are CPU/sklearn only
    del model
    torch.cuda.empty_cache()
    print("[rebuild] model released; STAGE 2-4 are CPU-only", flush=True)

    # ---------------- STAGE 2-4 ----------------
    stage24: dict[str, Any] = {}
    for L in args.layers:
        print(f"\n[rebuild] ===== layer {L}: ICA rebuild =====", flush=True)
        acts = acts_new[L]
        best_k, comps, sils, evr = run_ica_sweep(acts, k_range=K_RANGE,
                                                 seed=args.seed)
        comps = np.asarray(comps, dtype=np.float32)
        out = ICA_NEW / slug / f"layer{L:02d}_seed{args.seed:04d}_K{best_k:02d}.json"
        out.write_text(json.dumps({
            "model_id": args.model, "layer": L, "seed": args.seed, "k": best_k,
            "components": comps.tolist(), "silhouettes": sils,
            "explained_variance_ratio": evr,
            "manifest": env_manifest({
                "layer": L, "data_hash_stimuli": data_hash,
                "activations": "activations_nopad (batch=1, no padding)",
                "note": "rebuilt after the right-padding index -1 bug"})}))
        print(f"[rebuild] saved {out}", flush=True)

        new_npz = ACT_NEW / slug / f"layer{L:02d}_seed{args.seed:04d}.npz"
        repro_new = compute_split_reproducibility(new_npz, comps, seed=args.seed)
        order_new = np.argsort(-repro_new)
        new_top = comps[order_new][:TOP_K_AXES]

        old = load_ica(args.model, L, args.seed)
        old_comps = np.asarray(old["components"], dtype=np.float32)
        old_npz = ACT_OLD / slug / f"layer{L:02d}_seed{args.seed:04d}.npz"
        repro_old = compute_split_reproducibility(old_npz, old_comps,
                                                 seed=args.seed)
        order_old = np.argsort(-repro_old)
        old_top = old_comps[order_old][:TOP_K_AXES]

        stage24[str(L)] = {
            "old_k": int(old["k"]), "new_k": int(best_k),
            "old_repro_top5": [float(x) for x in repro_old[order_old][:TOP_K_AXES]],
            "new_repro_top5": [float(x) for x in repro_new[order_new][:TOP_K_AXES]],
            "match_top5_used_by_sweep": match_axes(old_top, new_top),
            "match_full_component_sets": match_axes(old_comps, comps),
            "new_ica_file": str(out),
        }
        mt = stage24[str(L)]["match_top5_used_by_sweep"]
        print(f"[rebuild] L{L} DAMAGE: old_K={old['k']} new_K={best_k} | "
              f"top5 matched |cos| mean={mt['matched_abs_cos_mean']:.4f} "
              f"min={mt['matched_abs_cos_min']:.4f} "
              f"per-old-axis best={[round(x, 3) for x in mt['best_abs_cos_per_old_axis']]}",
              flush=True)

        report["env"] = env_manifest({"data_hash_stimuli": data_hash,
                                      "stage": "in_progress"})
        report["stage24_axis_damage"] = stage24
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    report["env"] = env_manifest({"data_hash_stimuli": data_hash,
                                  "stage": "COMPLETE"})
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n[rebuild] FINAL -> {report_path}")
    print("[rebuild] DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
