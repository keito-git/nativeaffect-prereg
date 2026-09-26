#!/usr/bin/env python3
"""G1: sensitivity directions from the Jacobian (prereg 1078240, addendum 12).

Per layer and stimulus, the top-10 right singular vectors of the Jacobian of the
next-token logits with respect to the residual stream are found by randomized
subspace iteration using only matrix-vector products; the Jacobian is never
formed (it would be 2.32 GB per stimulus).

Addendum 12 fixes the combination rule:
    M = sum_i V_i V_i^T ,  sensitivity directions = top-10 eigenvectors of M.
Projection matrices are sign-invariant, so v_i and -v_i cannot cancel, and each
stimulus carries equal weight whatever its Jacobian norm.

Checkpointing: each stimulus's V_i is streamed to a memmap as it is computed and
a sidecar records how many are done, so an interrupted layer resumes from where
it stopped. M is rebuilt from the memmap only when every stimulus is present;
the eigendecomposition REFUSES to run on a partial layer.

Two descriptive checks accompany every layer and are never used to judge:
  - the eigenvalue spectrum of M (a flat top-10 means the per-stimulus subspaces
    are near-orthogonal, so a common sensitivity direction does not exist)
  - cosines against the top-10 principal components (near-identity means the
    variance/sensitivity plane is degenerate and the quadrant test is unusable)
"""
from __future__ import annotations
import argparse, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

_CVD = os.environ.get("CUDA_VISIBLE_DEVICES")
MODEL = "Qwen/Qwen3-8B"
LAYERS = (11, 16, 22, 27)
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
SPLIT = Path("/path/to/work/results/plan_b/e1_split_20260926.json")
OUTDIR = Path("/path/to/work/results/plan_b/G1_jacobian")
RANK, OVERSAMPLE, POWER = 10, 10, 2
PC_K = 10
SEED = 20260926
PREREG = "1078240"
ATTN_IMPL = "eager"


_SUF = ("s", "es", "ed", "ing", "ly")
VADCSV = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")


def _load_vad() -> set:
    import csv
    out = set()
    with VADCSV.open() as fh:
        for r in csv.DictReader(fh):
            try:
                float(r["valence"]); out.add(r["word"].strip().lower())
            except (KeyError, TypeError, ValueError):
                continue
    return out


def _has_vad(text: str, vad: set) -> bool:
    """Same lookup rule as the rest of the pipeline, suffix backoff included."""
    import re
    for w in re.findall(r"[a-zA-Z']+", text.lower()):
        if w in vad:
            return True
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[:-len(s)] in vad:
                return True
    return False


def _ops(model, tok, dec, L, enc, dev):
    """Return (vjp, jvp) for J = d(next-token logits)/d(residual stream at L)."""
    import torch

    def _run():
        held = {}

        def hk(m, i, o):
            hs = o[0] if isinstance(o, tuple) else o
            hs.requires_grad_(True)
            hs.retain_grad()
            held["h"] = hs
            return o
        h = dec[L].register_forward_hook(hk)
        try:
            lg = model(**enc).logits[0, -1, :].float()
        finally:
            h.remove()
        return lg, held["h"]

    def vjp(u: np.ndarray) -> np.ndarray:
        lg, h = _run()
        g = torch.autograd.grad(lg, h, grad_outputs=torch.as_tensor(
            u, device=dev, dtype=lg.dtype), retain_graph=False)[0]
        return g[0, -1].float().cpu().numpy().astype(np.float64)

    def jvp(q: np.ndarray) -> np.ndarray:
        """J q by differentiating <J^T v, q> with respect to v."""
        lg, h = _run()
        v = torch.zeros_like(lg, requires_grad=True)
        gh = torch.autograd.grad(lg, h, grad_outputs=v, create_graph=True)[0]
        out = torch.autograd.grad(
            (gh[0, -1] * torch.as_tensor(q, device=dev, dtype=gh.dtype)).sum(), v,
            retain_graph=False)[0]
        return out.float().cpu().numpy().astype(np.float64)
    return vjp, jvp


def top_right_singular(vjp, jvp, d: int, V: int, rng) -> np.ndarray:
    """Randomized subspace iteration; only mat-vecs, never the matrix.

    QR does not order its columns by singular value, so the first RANK columns
    of Q are an arbitrary basis of the k-dimensional subspace rather than the
    leading directions. A closing Rayleigh-Ritz step (SVD of J Q inside that
    subspace) is what actually selects the top RANK.
    """
    def unit(x: np.ndarray) -> np.ndarray:
        """Rescale between mat-vecs. The model runs in fp16, so the magnitudes
        compound across power iterations and overflow; scaling each column does
        not change the subspace that QR then orthonormalises."""
        n = float(np.linalg.norm(x))
        if not np.isfinite(n) or n == 0.0:
            raise FloatingPointError(f"non-finite or zero mat-vec (norm={n})")
        return x / n

    k = RANK + OVERSAMPLE
    Y = np.stack([unit(vjp(rng.standard_normal(V))) for _ in range(k)], axis=1)
    Q, _ = np.linalg.qr(Y)
    for _ in range(POWER):
        Y = np.stack([unit(vjp(unit(jvp(Q[:, j])))) for j in range(Q.shape[1])],
                     axis=1)
        Q, _ = np.linalg.qr(Y)
    # the closing projection must NOT be column-normalised: its singular values
    # are what order the directions
    C = np.stack([jvp(Q[:, j]) for j in range(Q.shape[1])], axis=1)   # V x k
    if not np.isfinite(C).all():
        raise FloatingPointError("non-finite projection C; cannot select the top "
                                 f"{RANK} ({np.isnan(C).sum()} nan, "
                                 f"{np.isinf(C).sum()} inf)")
    _, _, Wt = np.linalg.svd(C, full_matrices=False)
    return np.ascontiguousarray(Q @ Wt.T[:, :RANK])


def matvecs_per_stimulus() -> dict:
    """Exact mat-vec budget, so the cost estimate matches the implementation."""
    k = RANK + OVERSAMPLE
    return {"initial_vjp": k, "power_vjp": POWER * k, "power_jvp": POWER * k,
            "rayleigh_ritz_jvp": k, "total": k + 2 * POWER * k + k}


def _act(model, tok, dec, L, text, dev):
    import torch
    enc = {k: v.to(dev) for k, v in tok(text, return_tensors="pt").items()}
    got = []
    h = dec[L].register_forward_hook(
        lambda m, i, o: got.append((o[0] if isinstance(o, tuple) else o)
                                   .float()[0, -1].detach().cpu().numpy()))
    try:
        with torch.no_grad():
            model(**enc)
    finally:
        h.remove()
    return got[0]


def finish_layer(L: int, out_dir: Path, n: int, d: int, X: np.ndarray) -> dict:
    """Build M from the stored V_i and eigendecompose. Partial layers refused."""
    prog = json.loads((out_dir / f"layer{L:02d}_progress.json").read_text())
    if prog["n_done"] != n:
        raise SystemExit(f"REFUSING: layer {L} has {prog['n_done']}/{n} stimuli. "
                         "The eigendecomposition is not run on a partial layer.")
    from sklearn.decomposition import PCA
    Vi = np.lib.format.open_memmap(out_dir / f"layer{L:02d}_Vi.npy", mode="r")
    M = np.zeros((d, d), dtype=np.float64)
    for i in range(n):                      # accumulated, never all held at once
        A = np.asarray(Vi[i], dtype=np.float64)
        M += A @ A.T
    w, Vec = np.linalg.eigh(M)
    o = np.argsort(w)[::-1]
    w, S = w[o], Vec[:, o][:, :RANK]
    # PC_K components need at least PC_K samples; only a small smoke hits this
    n_pc = min(PC_K, X.shape[0] - 1, X.shape[1])
    PCs = PCA(n_components=n_pc, random_state=SEED).fit(
        X.astype(np.float64)).components_
    cos = np.abs(PCs @ S)
    return {"prereg_commit": PREREG, "addendum": "12", "layer": L,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "n_stimuli": n, "d": d, "rank": RANK,
            "pca_and_direction_rows": "E1 discovery half only (addendum 13)",
            "split_file": str(SPLIT), "split_group": "discovery",
            "combination_rule": "M = sum_i V_i V_i^T; top eigenvectors of M",
            "why_this_rule": ("projection matrices are sign invariant, so v and "
                              "-v cannot cancel, and stimuli are equally weighted"),
            "jacobian_formed_explicitly": False,
            "attn_implementation": ATTN_IMPL,
            "matvecs_per_stimulus": matvecs_per_stimulus(),
            "eigenvalues_top20": [float(x) for x in w[:20]],
            "eigenvalue_ratio_w10_over_w1": float(w[RANK - 1] / max(w[0], 1e-30)),
            "eigenvalue_ratio_w11_over_w1": float(w[RANK] / max(w[0], 1e-30)),
            "flat_spectrum_warning": bool(w[RANK] / max(w[0], 1e-30) > 0.8),
            "max_abs_cos_with_top10_PC_per_direction":
                [float(x) for x in cos.max(axis=0)],
            "mean_abs_cos_with_top10_PC": float(cos.mean()),
            "n_pcs_used": int(n_pc),
            "degenerate_plane_warning": bool(cos.max() > 0.9),
            "sensitivity_directions": S.T.tolist()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", type=int, nargs="+", default=list(LAYERS))
    ap.add_argument("--n-stimuli", type=int, default=None)
    ap.add_argument("--out-dir", type=Path, default=OUTDIR)
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        return self_check()
    if self_check() != 0:
        print("REFUSING: self-check failed"); return 2
    if _CVD is None:
        print("FATAL: CUDA_VISIBLE_DEVICES unset", file=sys.stderr); return 4

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    a.out_dir.mkdir(parents=True, exist_ok=True)
    # Addendum 13: candidate directions and the PMF basis come from the
    # DISCOVERY half of E1 only. Computing them from all 287 would put
    # confirmation data into the selection.
    e1 = json.loads(E1.read_text())
    split = json.loads(SPLIT.read_text())
    assert split.get("defined_before_any_G1_judgement") is True
    disc = list(split["discovery_indices"])
    texts = [e1[i]["text"] for i in disc]
    if a.n_stimuli:
        texts = texts[:a.n_stimuli]
    n = len(texts)
    if not a.n_stimuli and n != 144:
        raise SystemExit(f"REFUSING: expected the {len(disc)} discovery "
                         f"sentences of the E1 split (addendum 13), got {n}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    # eager attention: flash attention has no double-backward, which the JVP in
    # the power iteration needs (RuntimeError: derivative for
    # aten::_scaled_dot_product_flash_attention_backward is not implemented)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map="auto",
        low_cpu_mem_usage=True, attn_implementation="eager")
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dev = next(model.parameters()).device
    dec = model.model.layers
    d = int(model.config.hidden_size)
    V = int(model.config.vocab_size)
    print(f"{n} stimuli, layers {a.layers}, d={d}, vocab={V}", flush=True)

    for L in a.layers:
        done_file = a.out_dir / f"layer{L:02d}.json"
        if done_file.exists():
            print(f"layer {L}: already finished, skipping", flush=True)
            continue
        vif = a.out_dir / f"layer{L:02d}_Vi.npy"
        pf = a.out_dir / f"layer{L:02d}_progress.json"
        if vif.exists() and pf.exists():
            Vi = np.lib.format.open_memmap(vif, mode="r+")
            start = int(json.loads(pf.read_text())["n_done"])
            print(f"layer {L}: resuming at stimulus {start}/{n}", flush=True)
        else:
            Vi = np.lib.format.open_memmap(vif, mode="w+", dtype=np.float32,
                                           shape=(n, d, RANK))
            start = 0
            pf.write_text(json.dumps({"n_done": 0, "n_total": n, "layer": L}))
        t0 = time.time()
        rng = np.random.default_rng(SEED + L + 1000 * start)
        for si in range(start, n):
            enc = {k: v.to(dev) for k, v in
                   tok(texts[si], return_tensors="pt").items()}
            vjp, jvp = _ops(model, tok, dec, L, enc, dev)
            Vi[si] = top_right_singular(vjp, jvp, d, V, rng).astype(np.float32)
            Vi.flush()                                  # durable before progress
            pf.write_text(json.dumps({"n_done": si + 1, "n_total": n, "layer": L}))
            if (si + 1) % 10 == 0:
                el = time.time() - t0
                print(f"  L{L}: {si+1}/{n}  {el:.0f}s  "
                      f"eta {el/(si+1-start)*(n-si-1):.0f}s", flush=True)
        X = np.stack([_act(model, tok, dec, L, t_, dev) for t_ in texts])
        rec = finish_layer(L, a.out_dir, n, d, X)
        rec["seconds"] = round(time.time() - t0, 1)
        done_file.write_text(json.dumps(rec, indent=2))
        print(f"layer {L} done: w10/w1={rec['eigenvalue_ratio_w10_over_w1']:.4f} "
              f"w11/w1={rec['eigenvalue_ratio_w11_over_w1']:.4f} "
              f"maxcosPC={max(rec['max_abs_cos_with_top10_PC_per_direction']):.4f}",
              flush=True)
    return 0


def self_check() -> int:
    ok = True

    def c(n, v):
        nonlocal ok
        print(f"  [{'OK ' if v else 'FAIL'}] {n}")
        ok &= bool(v)
    rng = np.random.default_rng(0)
    d, r = 64, 3
    Vs = [np.linalg.qr(rng.standard_normal((d, r)))[0] for _ in range(5)]
    M1 = sum(V @ V.T for V in Vs)

    def flip(V):
        return V * rng.choice((-1.0, 1.0), size=V.shape[1])
    M2 = sum((lambda W: W @ W.T)(flip(V)) for V in Vs)
    c("sum V V^T is invariant to per-column sign flips", np.allclose(M1, M2, atol=1e-10))
    m1 = np.mean([V[:, 0] for V in Vs], axis=0)
    m2 = np.mean([V[:, 0] * s for V, s in zip(Vs, rng.choice((-1.0, 1.0), 5))], axis=0)
    c("plain averaging IS affected by sign flips (why the rule is needed)",
      not np.allclose(m1, m2, atol=1e-8))
    base = np.linalg.qr(rng.standard_normal((d, r)))[0]
    Msh = sum((base + .05 * rng.standard_normal((d, r))) @
              (base + .05 * rng.standard_normal((d, r))).T for _ in range(20))
    w = np.sort(np.linalg.eigvalsh(Msh))[::-1]
    Mor = sum(np.linalg.qr(rng.standard_normal((d, r)))[0] @
              np.linalg.qr(rng.standard_normal((d, r)))[0].T for _ in range(20))
    wo = np.sort(np.abs(np.linalg.eigvalsh(Mor)))[::-1]
    c(f"shared subspace -> steep spectrum (w[r]/w[0]={w[r]/w[0]:.3f})", w[r]/w[0] < 0.2)
    c(f"orthogonal subspaces -> flatter ({wo[r]/wo[0]:.3f})", wo[r]/wo[0] > w[r]/w[0])

    # the mat-vec routine must recover the true right singular vectors
    Vv, dd = 200, 40
    J = rng.standard_normal((Vv, dd))
    U, s, Wt = np.linalg.svd(J, full_matrices=False)
    s[:] = np.linspace(10, 1, len(s)) ** 2          # a clear spectrum
    J = (U * s) @ Wt
    got = top_right_singular(lambda u: J.T @ u, lambda q: J @ q, dd, Vv,
                             np.random.default_rng(1))
    true = Wt[:RANK].T
    sub = np.abs(np.linalg.svd(got.T @ true, compute_uv=False))
    c(f"randomized routine recovers the true top-{RANK} right singular subspace "
      f"(min principal cosine {sub.min():.4f})", sub.min() > 0.99)
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
