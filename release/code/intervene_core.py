"""Shared intervention machinery for the steering audit (amendments 49, 52, 53, 54).

Two things here are what the audited work does not do.

First, every direction is calibrated to the same output perturbation before its effect is
read: alpha is bisected until the Jensen-Shannon divergence of the full next-token
distribution, over the union of the top 100 tokens, hits a target budget. Comparing a unit
vector scaled by a shared beta instead lets a direction win by being effectively larger.

Second, the floors form a hierarchy. F4 (VMIC) draws a direction inside the dominant-variance
subspace whose coordinates in the principal basis are a permutation of the target's own
coordinates with random signs, so the variance profile is preserved exactly while the
direction is randomised. A full-space Haar floor (F1) cannot distinguish content from
variance, which is the confound paper 2 found.
"""
from __future__ import annotations

import numpy as np
import torch

EMOTIONS = ["anger", "boredom", "disgust", "fear", "guilt", "joy", "pride",
            "relief", "sadness", "shame", "surprise", "trust"]


def js(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log(a[mask] / np.maximum(b[mask], 1e-30))).sum())
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def js_top_union(p_full: np.ndarray, q_full: np.ndarray, k: int = 100) -> float:
    """JS restricted to the union of each distribution's top-k tokens, renormalised."""
    idx = np.union1d(np.argpartition(-p_full, k)[:k], np.argpartition(-q_full, k)[:k])
    p, q = p_full[idx], q_full[idx]
    return js(p / p.sum(), q / q.sum())


class Intervener:
    """Adds alpha * v to one layer's output at the final prompt position."""

    def __init__(self, model, tok, layer: int, emotion_ids: list[int]):
        self.model, self.tok, self.layer = model, tok, layer
        self.emotion_ids = emotion_ids
        self._vec = None
        self._handle = None
        block = self._blocks()[layer - 1] if layer > 0 else None
        if block is None:
            raise ValueError("intervention at layer 0 is undefined")
        self._handle = block.register_forward_hook(self._hook)

    def _blocks(self):
        m = self.model
        for path in ("model.layers", "model.model.layers", "transformer.h", "model.decoder.layers"):
            obj = m
            try:
                for part in path.split("."):
                    obj = getattr(obj, part)
                return obj
            except AttributeError:
                continue
        raise RuntimeError("could not find the list of layers")

    def _hook(self, module, args, output):
        if self._vec is None:
            return output
        hs = output[0] if isinstance(output, tuple) else output
        hs[:, -1, :] = hs[:, -1, :] + self._vec.to(hs.dtype)
        return (hs,) + tuple(output[1:]) if isinstance(output, tuple) else hs

    def close(self):
        if self._handle is not None:
            self._handle.remove()

    @torch.no_grad()
    def next_token_probs(self, prompts: list[str], vec=None, bs: int = 16) -> np.ndarray:
        self._vec = None if vec is None else torch.as_tensor(vec, device=self.model.device)
        out = []
        for i in range(0, len(prompts), bs):
            enc = self.tok(prompts[i:i + bs], return_tensors="pt", padding=True,
                           truncation=True, max_length=256).to(self.model.device)
            logits = self.model(**enc).logits[:, -1, :].float()
            out.append(torch.softmax(logits, -1).cpu().numpy())
        self._vec = None
        return np.concatenate(out)

    def perturbation(self, prompts, base: np.ndarray, v: np.ndarray, alpha: float) -> float:
        """Mean JS of the full next-token distribution at this alpha."""
        q = self.next_token_probs(prompts, v * alpha)
        return float(np.mean([js_top_union(base[i], q[i]) for i in range(len(prompts))]))

    def calibrate(self, prompts, base, v, target: float,
                  lo: float = 1e-3, hi: float = 1e3, steps: int = 6) -> float:
        """Bisect alpha so the output perturbation equals the registered budget."""
        for _ in range(8):
            if self.perturbation(prompts, base, v, hi) >= target:
                break
            hi *= 4
        for _ in range(steps):
            mid = float(np.sqrt(lo * hi))
            if self.perturbation(prompts, base, v, mid) < target:
                lo = mid
            else:
                hi = mid
        return float(np.sqrt(lo * hi))

    def emotion_effect(self, prompts, base: np.ndarray, v: np.ndarray, alpha: float) -> float:
        """JS between the renormalised 13-way emotion-label distributions."""
        q = self.next_token_probs(prompts, v * alpha)
        ids = self.emotion_ids
        eff = []
        for i in range(len(prompts)):
            p = base[i, ids]; r = q[i, ids]
            eff.append(js(p / max(p.sum(), 1e-30), r / max(r.sum(), 1e-30)))
        return float(np.mean(eff))


def emotion_token_ids(tok) -> list[int]:
    """One leading-space token per emotion word, so the readout is a fixed vocabulary."""
    ids = []
    for w in EMOTIONS:
        cand = tok.encode(" " + w, add_special_tokens=False) or tok.encode(w, add_special_tokens=False)
        ids.append(int(cand[0]))
    return ids


# ---- floors -----------------------------------------------------------------

def pc_basis(X: np.ndarray, k: int) -> np.ndarray:
    """Top-k principal directions of the (already centred) activation matrix."""
    Xc = X - X.mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Vt[:k]


def k_for_coverage(v: np.ndarray, P: np.ndarray, frac: float = 0.90) -> int:
    c = P @ v
    cum = np.cumsum(c ** 2) / max(float((v ** 2).sum()), 1e-30)
    idx = int(np.searchsorted(cum, frac) + 1)
    return min(idx, P.shape[0])


def unit(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) + 1e-12)


def floor_F1(d: int, rng) -> np.ndarray:
    return unit(rng.standard_normal(d))


def floor_F2(d: int, Z: np.ndarray, rng) -> np.ndarray:
    """Haar in the orthogonal complement of all target directions."""
    q, _ = np.linalg.qr(Z.T)
    g = rng.standard_normal(d)
    return unit(g - q @ (q.T @ g))


def floor_F3(P: np.ndarray, k: int, rng) -> np.ndarray:
    """Haar inside the top-k principal subspace."""
    return unit(rng.standard_normal(k) @ P[:k])


def floor_F4(v: np.ndarray, P: np.ndarray, k: int, rng) -> np.ndarray:
    """VMIC: the target's own principal coordinates, permuted and sign-flipped."""
    c = P[:k] @ v
    c = rng.permutation(c) * rng.choice([-1.0, 1.0], size=k)
    return unit(c @ P[:k])
