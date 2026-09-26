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
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

RANK = 10

# Paths, seed, model and the activation hook are IMPORTED from g1_jacobian at run
# time, never restated here. A second copy of the stimulus path or of the hook
# would be a second chance to diverge from the file that produced the layers --
# the same defect as the nine copied JS functions. Importing also makes the
# reproduction guard meaningful: it then tests the PCA and the overlap maths,
# not whether two hand-written hooks happen to agree.
# (My first draft did restate them, and had the stimulus path wrong:
#  /path/to/work/data/e1_stimuli.json instead of
#  /path/to/work/code/stimuli/stimuli_e1.json.)
G1_CODE_DIR = Path("/path/to/work/code/phase10")


def variance_along(X: np.ndarray, dirs: np.ndarray, pcs: np.ndarray,
                   evr: np.ndarray) -> dict:
    """Variance of the activations along each direction, in comparable units.

    A direction EXACTLY orthogonal to the top-k PC span cannot have variance
    above lambda_k -- PCA's optimality forbids it -- so exact orthogonality would
    settle the quadrant claim of addendum 1 A2 (low variance, high sensitivity)
    on its own. Our directions are not exactly orthogonal: with inside_fraction f
    the variance only obeys var <= f*lambda_1 + (1-f)*lambda_k, and lambda_1 is
    orders above lambda_k, so a modest f puts it back above lambda_k. The
    variance is therefore measured here rather than inferred from the overlap.
    """
    Xc = X - X.mean(axis=0, keepdims=True)
    n = max(Xc.shape[0] - 1, 1)
    var_dir = (Xc @ dirs.T) ** 2
    var_dir = var_dir.sum(axis=0) / n                   # (r,)
    var_pc = (Xc @ pcs.T) ** 2
    var_pc = var_pc.sum(axis=0) / n                     # (k,)
    total = float((Xc ** 2).sum() / n)
    return {
        "variance_along_direction": [float(v) for v in var_dir],
        "variance_along_top_pcs": [float(v) for v in var_pc],
        "total_variance": total,
        "fraction_of_total_variance_per_direction":
            [float(v / total) for v in var_dir],
        "ratio_to_pc10_variance":
            [float(v / max(var_pc[-1], 1e-30)) for v in var_dir],
        "n_directions_below_pc10_variance":
            int(sum(1 for v in var_dir if v < var_pc[-1])),
        "explained_variance_ratio_top_pcs": [float(v) for v in evr],
        "note": ("a direction below PC10's variance sits in the low-variance "
                 "half of the quadrant plot; above it, it does not, whatever its "
                 "overlap with the PC span"),
    }


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
    n_pc_l11 = 10                      # n_pcs_used as recorded in layer11.json
    ub = float(np.sqrt((n_pc_l11 * mx ** 2).sum() / n_pc_l11))
    ck("layer-11 bound on the mean principal cosine is 0.3386",
       abs(ub - 0.3386) < 5e-4)
    ck("that bound is below the registered 0.70 threshold", ub < 0.70)

    # 6. The true relation, which an earlier version of this test got backwards.
    #    A direction exactly orthogonal to the top-k PC span CANNOT have variance
    #    above lambda_k: if it did, swapping it into the span would raise the
    #    explained variance, contradicting PCA's optimality. So exact
    #    orthogonality does place a direction in the low-variance half. What it
    #    does not do is survive partial overlap: variance along a unit direction
    #    with inside_fraction f obeys var <= f*lambda_1 + (1-f)*lambda_k, and with
    #    lambda_1 >> lambda_k even a modest f lifts it above lambda_k. That is why
    #    the variance is measured rather than inferred.
    k = 3
    Xs = rng.standard_normal((400, d)) * 0.01
    basis = np.linalg.qr(rng.standard_normal((d, d)))[0]
    for j in range(k):
        Xs += np.outer(rng.standard_normal(400) * (10.0 - 3.0 * j), basis[:, j])
    quiet = basis[:, k + 5]
    Xs += np.outer(rng.standard_normal(400) * 1.0, quiet)
    from sklearn.decomposition import PCA as _PCA
    f3 = _PCA(n_components=k, random_state=0).fit(Xs)
    st6 = overlap_stats(f3.components_, quiet[None, :])
    v6 = variance_along(Xs, quiet[None, :], f3.components_, f3.explained_variance_)
    ck("orthogonal to the top PCs => inside_fraction ~ 0",
       st6["inside_fraction_max"] < 1e-3)
    ck("orthogonal to the top PCs => variance at or below PC-k (PCA optimality)",
       v6["ratio_to_pc10_variance"][0] <= 1.0 + 1e-9
       and v6["n_directions_below_pc10_variance"] == 1)

    # partial overlap with the loudest PC lifts it back above lambda_k
    mixed = 0.45 * f3.components_[0] + np.sqrt(1 - 0.45 ** 2) * quiet
    mixed /= np.linalg.norm(mixed)
    st7 = overlap_stats(f3.components_, mixed[None, :])
    v7 = variance_along(Xs, mixed[None, :], f3.components_, f3.explained_variance_)
    ck("partial overlap (f~0.2) lifts the variance back above PC-k",
       0.1 < st7["inside_fraction_max"] < 0.35
       and v7["ratio_to_pc10_variance"][0] > 1.0)
    ck("=> the quadrant claim needs the measured variance, not orthogonality alone",
       v7["n_directions_below_pc10_variance"] == 0)

    print(f"\nself-test: {len(fails)} failure(s)")
    if fails:
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", type=int, nargs="+", default=[11, 16, 22, 27])
    ap.add_argument("--out-dir", type=Path,
                    default=Path("/path/to/work/results/plan_b/G1_jacobian"))
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

    sys.path.insert(0, str(G1_CODE_DIR))
    import g1_jacobian as g1                            # noqa: PLC0415
    print(f"imported {g1.__file__}")
    print(f"  sha256 {hashlib.sha256(Path(g1.__file__).read_bytes()).hexdigest()}")
    MODEL, PC_K, SEED = g1.MODEL, g1.PC_K, g1.SEED

    split = json.loads(g1.SPLIT.read_text())
    if split.get("defined_before_any_G1_judgement") is not True:
        raise SystemExit("REFUSING: the split does not assert that it was defined "
                         "before any G1 judgement")
    e1 = json.loads(g1.E1.read_text())
    disc = list(split["discovery_indices"])
    texts = [e1[i]["text"] for i in disc]
    if len(texts) != 144:
        raise SystemExit(f"REFUSING: expected 144 discovery sentences, got {len(texts)}")

    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True, attn_implementation=g1.ATTN_IMPL)
    model.eval()
    for prm in model.parameters():
        prm.requires_grad_(False)
    dev = next(model.parameters()).device
    dec = model.model.layers

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

        # the SAME activation function that produced the layers
        X = np.stack([g1._act(model, tok, dec, L, t_, dev) for t_ in texts])

        n_pc = min(PC_K, X.shape[0] - 1, X.shape[1])
        fit = PCA(n_components=n_pc, random_state=SEED).fit(X.astype(np.float64))
        pcs = fit.components_
        st = overlap_stats(pcs, dirs)
        st["variance"] = variance_along(X, dirs, pcs, fit.explained_variance_)

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
