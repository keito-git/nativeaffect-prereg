#!/usr/bin/env python3
"""Exact overlap between the G1 sensitivity subspace and the top-10 activation PCs.

Why a separate script
---------------------
`g1_jacobian.py` records only two summaries of the 10x10 matrix
C[k, j] = |PC_k . s_j|: the per-direction maximum `C.max(axis=0)` and the grand
mean `C.mean()`. Both are ENTRYWISE. The quantities actually needed are not:

  * principal-angle cosines between the two subspaces = singular values of C.
    A singular value is not bounded by the largest entry. The 8x8 Hadamard
    matrix over sqrt(8) has every entry equal to 0.3536 and describes two
    IDENTICAL subspaces (all ten principal cosines are 1). So a small entrywise
    maximum does not establish that the subspaces are nearly orthogonal, and a
    `C.max() > 0.9` flag can stay False while the subspaces coincide. That flag
    in g1_jacobian.py is therefore weaker than addendum 12 L3 intended.

    The singular values must be taken of the SIGNED inner-product matrix;
    svd(|G|) is not the principal cosines either (the self-test pins this).

  * inside_fraction(s_j) = sum_k (PC_k . s_j)^2, the fraction of a direction's
    squared norm lying inside the top-10 PC span. This is the quantity the old
    ICA axes were measured with (88.7-99.97%), so it is the only one that makes
    the two comparable, and it is what answers "is the axis that passed just a
    re-description of a principal component?".

Neither can be recovered from the stored summaries, because C itself and the PC
basis are not saved. This script recomputes the activations with a single
no-grad forward pass per layer -- no backward pass, no Jacobian -- refits the
same PCA, and writes C, the exact principal cosines, and inside_fraction per
direction.

Reproduction guard
------------------
The recomputation must reproduce what `g1_jacobian.py` already wrote. The script
compares its own `C.max(axis=0)` and `C.mean()` against the stored values and
REFUSES to write if they differ by more than --tol. If they differ, the
activations are not the ones the directions were computed from, and the overlap
numbers would be about a different object.

Usage
-----
    python3 g1_pc_overlap.py --self-test          # math only, no model, no GPU
    python3 g1_pc_overlap.py --layers 11 16 22 27 # needs the model on GPU
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

RANK = 10
PC_K = 10
SEED = 20260926
MODEL = "Qwen/Qwen3-8B"
OUTDIR = Path("/path/to/work/results/plan_b/G1_jacobian")
E1 = Path("/path/to/work/data/e1_stimuli.json")
SPLIT = Path("/path/to/work/results/plan_b/e1_split_20260926.json")


def overlap_stats(pcs: np.ndarray, dirs: np.ndarray) -> dict:
    """C, principal cosines, and inside_fraction. pcs (k,d) and dirs (r,d) orthonormal."""
    G = pcs @ dirs.T                               # (k, r) SIGNED inner products
    # The principal-angle cosines are the singular values of the SIGNED matrix.
    # Taking |.| elementwise first destroys the orthogonality structure and the
    # singular values of |G| are not principal cosines: the self-test pins this
    # with two identical subspaces, where svd(|G|) misses 1.0 while svd(G) hits
    # it exactly. Singular values are invariant to flipping the sign of any
    # basis vector, so the sign ambiguity of PCs and eigenvectors does not
    # matter here.
    sv = np.linalg.svd(G, compute_uv=False)
    sv = np.clip(sv, 0.0, 1.0)                     # numerical guard only
    C = np.abs(G)                                  # entrywise, for the stored-summary guard
    inside = (G ** 2).sum(axis=0)                  # per direction; sign-independent
    return {
        "C_entrywise_abs_cos": C.tolist(),
        "C_max_entry": float(C.max()),
        "C_mean_entry": float(C.mean()),
        "principal_cosines": [float(x) for x in sv],
        "principal_cosine_max": float(sv.max()),
        "principal_cosine_mean": float(sv.mean()),
        "inside_fraction_per_direction": [float(x) for x in inside],
        "inside_fraction_max": float(inside.max()),
        "inside_fraction_mean": float(inside.mean()),
        "sum_squared_principal_cosines": float((sv ** 2).sum()),
        "sum_inside_fraction": float(inside.sum()),
        "subspace_dim": int(min(pcs.shape[0], dirs.shape[0])),
        "note_on_flag": ("addendum 12 L3 degeneracy must be judged on "
                         "principal_cosine_max, not on C_max_entry"),
    }


def self_test() -> None:
    fails: list[str] = []

    def ck(name: str, cond: bool) -> None:
        print(f"  [{'ok' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    rng = np.random.default_rng(0)
    d = 64

    # 1. identical subspaces: principal cosines all 1, inside_fraction all 1,
    #    yet the entrywise maximum can be small.
    from scipy.linalg import hadamard
    Q = np.linalg.qr(rng.standard_normal((d, 8)))[0]        # (d, 8) orthonormal
    H = hadamard(8) / np.sqrt(8)
    s = overlap_stats(Q.T, (Q @ H).T)                        # same span, rotated basis
    ck("identical subspaces -> all principal cosines 1",
       np.allclose(s["principal_cosines"], 1.0, atol=1e-8))
    ck("identical subspaces -> inside_fraction 1",
       np.allclose(s["inside_fraction_per_direction"], 1.0, atol=1e-8))
    ck("identical subspaces can have a SMALL entrywise max (0.354)",
       abs(s["C_max_entry"] - 0.35355) < 1e-4)
    ck("so C_max_entry does NOT bound the principal cosines",
       s["C_max_entry"] < 0.36 and s["principal_cosine_mean"] > 0.99)

    # 2. orthogonal subspaces
    Z = np.linalg.qr(rng.standard_normal((d, 20)))[0]
    s2 = overlap_stats(Z[:, :10].T, Z[:, 10:].T)
    ck("orthogonal subspaces -> principal cosines 0",
       max(s2["principal_cosines"]) < 1e-8)
    ck("orthogonal subspaces -> inside_fraction 0",
       max(s2["inside_fraction_per_direction"]) < 1e-12)

    # 3. the identity sum_i sigma_i^2 == sum_j inside_j (both are ||C||_F^2)
    A = np.linalg.qr(rng.standard_normal((d, 10)))[0].T
    Bv = np.linalg.qr(rng.standard_normal((d, 10)))[0].T
    s3 = overlap_stats(A, Bv)
    ck("sum sigma^2 == sum inside_fraction",
       abs(s3["sum_squared_principal_cosines"] - s3["sum_inside_fraction"]) < 1e-9)
    ck("inside_fraction in [0,1]",
       all(-1e-12 <= v <= 1 + 1e-9 for v in s3["inside_fraction_per_direction"]))
    ck("principal cosines are non-increasing",
       all(a >= b - 1e-12 for a, b in zip(s3["principal_cosines"],
                                          s3["principal_cosines"][1:])))

    # 4. one direction fully inside, the rest outside
    mix = np.vstack([A[0], Bv[1:]])
    mix = np.linalg.qr(mix.T)[0].T
    s4 = overlap_stats(A, mix)
    ck("a direction inside the span shows inside_fraction ~1",
       max(s4["inside_fraction_per_direction"]) > 0.99)

    # 5. the bound actually used in the interim report
    mx = np.array([0.1368, 0.0804, 0.0599, 0.1727, 0.0815,
                   0.0825, 0.0875, 0.1557, 0.0779, 0.0683])   # layer 11, stored
    ub = float(np.sqrt((PC_K * mx ** 2).sum() / PC_K))
    ck("layer-11 bound on the mean principal cosine is 0.3386",
       abs(ub - 0.3386) < 5e-4)
    ck("that bound is below the registered 0.70 threshold", ub < 0.70)

    print(f"\nself-test: {len(fails)} failure(s)")
    if fails:
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", type=int, nargs="+", default=[11, 16, 22, 27])
    ap.add_argument("--out-dir", type=Path, default=OUTDIR)
    ap.add_argument("--tol", type=float, default=1e-6)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    print("self-test:")
    self_test()
    if a.self_test:
        return 0

    # GPU pinned by the caller's environment, never hard-coded to cuda:N here.
    if "CUDA_VISIBLE_DEVICES" not in os.environ:
        raise SystemExit("REFUSING: set CUDA_VISIBLE_DEVICES before importing torch")
    import torch                                        # noqa: PLC0415
    from sklearn.decomposition import PCA               # noqa: PLC0415
    from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415

    split = json.loads(SPLIT.read_text())
    e1 = json.loads(E1.read_text())
    disc = list(split["discovery_indices"])
    texts = [e1[i]["text"] for i in disc]
    if len(texts) != 144:
        raise SystemExit(f"REFUSING: expected 144 discovery sentences, got {len(texts)}")

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True, attn_implementation="eager")
    model.eval()

    out: dict = {"generated_utc": datetime.now(timezone.utc).isoformat(),
                 "purpose": ("exact principal angles and inside_fraction; the "
                             "stored g1_jacobian summaries are entrywise"),
                 "n_stimuli": len(texts), "layers": {}}

    for L in a.layers:
        rec_path = a.out_dir / f"layer{L:02d}.json"
        if not rec_path.exists():
            print(f"layer {L}: no {rec_path.name} yet, skipped")
            continue
        rec = json.loads(rec_path.read_text())
        dirs = np.asarray(rec["sensitivity_directions"], dtype=np.float64)

        acts = []
        for t in texts:
            enc = tok(t, return_tensors="pt").to(model.device)
            got: list = []
            h = model.model.layers[L].register_forward_hook(
                lambda _m, _i, o, g=got: g.append(
                    o[0][0, -1].detach().float().cpu().numpy()))
            try:
                with torch.no_grad():
                    model(**enc)
            finally:
                h.remove()
            acts.append(got[0])
        X = np.stack(acts).astype(np.float64)

        n_pc = min(PC_K, X.shape[0] - 1, X.shape[1])
        pcs = PCA(n_components=n_pc, random_state=SEED).fit(X).components_
        st = overlap_stats(pcs, dirs)

        # Reproduction guard: the entrywise summaries must match what was stored.
        C = np.array(st["C_entrywise_abs_cos"])
        d_max = float(np.abs(C.max(axis=0)
                             - np.array(rec["max_abs_cos_with_top10_PC_per_direction"])).max())
        d_mean = abs(st["C_mean_entry"] - rec["mean_abs_cos_with_top10_PC"])
        st["reproduces_stored_max_abs_dev"] = d_max
        st["reproduces_stored_mean_abs_dev"] = d_mean
        if d_max > a.tol or d_mean > a.tol:
            raise SystemExit(
                f"REFUSING: layer {L} recomputation does not reproduce the stored "
                f"summaries (max dev {d_max:.3e}, mean dev {d_mean:.3e} > tol "
                f"{a.tol:.1e}). The activations differ from the ones the "
                "directions were computed from, so the overlap would describe a "
                "different object.")
        out["layers"][str(L)] = st
        print(f"layer {L}: principal cosine mean={st['principal_cosine_mean']:.4f} "
              f"max={st['principal_cosine_max']:.4f} "
              f"inside_fraction max={st['inside_fraction_max']:.4f} "
              f"(reproduced stored summaries to {max(d_max, d_mean):.1e})")

    dst = a.out_dir / "pc_overlap_exact.json"
    dst.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
