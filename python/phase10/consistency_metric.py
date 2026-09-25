#!/usr/bin/env python3
"""The Plan B selection statistic S: consistency of the output shift across stimuli.

Centring is over the VOCABULARY dimension, per stimulus. Centring over the
stimulus dimension is refused, because the consistent component IS the mean over
stimuli: removing it leaves residuals that sum to zero, whose pairwise inner
products are then negative by construction, so the statistic would measure the
opposite of what it is for. That failure is verified numerically below.
"""
from __future__ import annotations

import numpy as np


def consistency(deltas: np.ndarray, centering: str = "vocab") -> float:
    """Mean pairwise cosine of the per-stimulus output-shift vectors.

    deltas: (n_stimuli, n_vocab) array of log p(+alpha d) - log p(baseline).
    centering: 'vocab' (per stimulus, over the vocabulary) or 'none'.
    """
    D = np.asarray(deltas, dtype=np.float64)
    if D.ndim != 2 or D.shape[0] < 2:
        raise ValueError("deltas must be (n_stimuli >= 2, n_vocab)")
    if centering == "vocab":
        D = D - D.mean(axis=1, keepdims=True)
    elif centering == "stimulus":
        raise ValueError(
            "centering='stimulus' is refused: the consistent component is the "
            "mean over stimuli, so removing it makes the statistic structurally "
            "negative and non-discriminating (prereg B section 2.2)")
    elif centering != "none":
        raise ValueError(f"unknown centering {centering!r}")
    nrm = np.linalg.norm(D, axis=1, keepdims=True)
    nrm[nrm < 1e-30] = 1.0
    U = D / nrm
    G = U @ U.T
    n = G.shape[0]
    iu = np.triu_indices(n, k=1)
    return float(G[iu].mean())


def _stimulus_centred(deltas: np.ndarray) -> float:
    """The refused variant, implemented ONLY so the self-test can show it fails."""
    D = np.asarray(deltas, dtype=np.float64)
    D = D - D.mean(axis=1, keepdims=True)
    D = D - D.mean(axis=0, keepdims=True)          # the mistake
    nrm = np.linalg.norm(D, axis=1, keepdims=True)
    nrm[nrm < 1e-30] = 1.0
    U = D / nrm
    iu = np.triu_indices(U.shape[0], k=1)
    return float((U @ U.T)[iu].mean())


def _synthetic(n: int, V: int, shared: float, seed: int) -> np.ndarray:
    """A consistent shift of weight `shared` plus per-stimulus idiosyncratic noise."""
    rng = np.random.default_rng(seed)
    common = rng.standard_normal(V)
    common -= common.mean()
    common /= np.linalg.norm(common)
    out = np.empty((n, V))
    for i in range(n):
        idio = rng.standard_normal(V)
        idio -= idio.mean()
        idio /= np.linalg.norm(idio)
        scale = rng.uniform(0.5, 2.0)              # per-stimulus magnitude varies
        offset = rng.uniform(-3, 3)                # per-stimulus constant offset
        out[i] = scale * (shared * common + (1 - shared) * idio) + offset
    return out


def self_test() -> int:
    ok = True

    def c(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if cond else 'FAIL'}] {name}")
        ok &= bool(cond)

    n, V = 20, 512
    hi = _synthetic(n, V, shared=0.9, seed=1)
    lo = _synthetic(n, V, shared=0.0, seed=2)
    s_hi, s_lo = consistency(hi), consistency(lo)
    c(f"a consistent direction scores high (S={s_hi:.3f})", s_hi > 0.5)
    c(f"an inconsistent direction scores near zero (S={s_lo:.3f})", abs(s_lo) < 0.15)
    c("consistent beats inconsistent", s_hi > s_lo + 0.4)

    # S must be monotone in the shared fraction
    ss = [consistency(_synthetic(n, V, shared=f, seed=3)) for f in
          (0.0, 0.25, 0.5, 0.75, 1.0)]
    c(f"S increases with the shared fraction ({[round(x,2) for x in ss]})",
      all(ss[i] < ss[i + 1] for i in range(len(ss) - 1)))

    # per-stimulus constant offsets must not matter (softmax shift invariance)
    off = hi + np.random.default_rng(4).uniform(-50, 50, size=(n, 1))
    c("S is invariant to per-stimulus constant offsets",
      abs(consistency(off) - s_hi) < 1e-9)

    # the refused centring destroys the signal
    w_hi, w_lo = _stimulus_centred(hi), _stimulus_centred(lo)
    c(f"stimulus-centring makes the consistent case negative (S={w_hi:.3f})",
      w_hi < 0)
    c(f"stimulus-centring cannot separate consistent from inconsistent "
      f"({w_hi:.3f} vs {w_lo:.3f})", abs(w_hi - w_lo) < 0.1)
    c("stimulus-centring is refused by the production function",
      _refuses(hi))

    # scale invariance: multiplying one stimulus's shift must not change S
    sc = hi.copy(); sc[0] *= 7.0
    c("S is invariant to per-stimulus scale",
      abs(consistency(sc) - s_hi) < 1e-9)
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _refuses(d: np.ndarray) -> bool:
    try:
        consistency(d, centering="stimulus")
        return False
    except ValueError:
        return True


if __name__ == "__main__":
    raise SystemExit(self_test())
