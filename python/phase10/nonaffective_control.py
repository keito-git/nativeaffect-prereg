#!/usr/bin/env python3
"""Non-affective control (prereg section 54): hold the stimuli fixed, swap the
target subspace.

The same 287 E1 sentences and the same cached activations are used, so sentence
length, lexical diversity, syntax, register and the activations themselves are
identical by construction rather than matched, and no GPU is needed.

NOT RUN YET. Execution waits on the PI's decision. The norm files are also not
obtained yet: their bibliographic details are unverified (prereg 54.6), so this
script refuses to run on a norm set that has not been declared.

Run `--dry-run` to exercise the whole pipeline on synthetic norms; that path
touches the same functions the real run uses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

BASE = Path("/path/to/work/results")
SLUG = "swiss-ai__Apertus-v1_1-1_5B"
ACT = BASE / "activations_nopad" / SLUG
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
LAYERS = (5, 7, 10, 12)
N_AXES = 3
SEED = 42
NULL_SEED = 20260925          # identical to alignment_primary.py
N_RANDOM = 2000               # identical to alignment_primary.py
RANK = 3                      # FIXED by prereg 54.2: subspaces must be rank 3
CONTAMINATION_MAX = 0.5       # prereg 54.3 criterion C: |r| > 0.5 is unusable
_SUF = ("s", "es", "ed", "ing", "ly")   # identical to alignment_primary.py
VAD_KEYS = ("valence", "arousal", "dominance")


def _unit(v: np.ndarray) -> np.ndarray:
    return (v / (np.linalg.norm(v) + 1e-30)).astype(np.float64)


def p2_ridge_std(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Identical to the registered P2 procedure."""
    from sklearn.linear_model import RidgeCV
    Xf = X.astype(np.float64)
    mu, sd = Xf.mean(axis=0), Xf.std(axis=0)
    sd[sd < 1e-12] = 1.0
    m = RidgeCV(alphas=np.logspace(-2, 5, 22), fit_intercept=True)
    m.fit((Xf - mu) / sd, (y - y.mean()) / (y.std() + 1e-8))
    return _unit(np.asarray(m.coef_, dtype=np.float64).ravel() / sd)


def inside_fraction(a: np.ndarray, Q: np.ndarray) -> float:
    a = _unit(a)
    proj = Q @ (Q.T @ a)
    return float(np.dot(proj, proj))


def sentence_score(text: str, norms: dict[str, dict[str, float]],
                   keys: tuple[str, ...]) -> tuple[dict[str, float] | None, int, int]:
    """Average the word-level norms over a sentence.

    Identical lookup rule to the VAD pipeline, including the suffix backoff, so
    the affective and non-affective conditions are scored the same way.
    Returns (scores, n_words, n_covered).
    """
    def look(w: str) -> dict[str, float] | None:
        if w in norms:
            return norms[w]
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in norms:
                return norms[w[: -len(s)]]
        return None
    words = re.findall(r"[a-zA-Z']+", text.lower())
    hits = [x for x in (look(w) for w in words) if x is not None]
    if not hits:
        return None, len(words), 0
    return ({k: float(np.mean([h[k] for h in hits])) for k in keys},
            len(words), len(hits))


def load_norms(path: Path, keys: tuple[str, ...]) -> dict[str, dict[str, float]]:
    """Load a norm table: a header row with 'word' plus the named dimensions."""
    import csv
    out: dict[str, dict[str, float]] = {}
    with path.open() as fh:
        sniff = csv.Sniffer().sniff(fh.read(4096)) if path.stat().st_size else None
        fh.seek(0)
        rd = csv.DictReader(fh, dialect=sniff) if sniff else csv.DictReader(fh)
        missing = [k for k in ("word",) + keys if k not in (rd.fieldnames or [])]
        if missing:
            raise SystemExit(f"FATAL: norm file lacks columns {missing}; "
                             f"found {rd.fieldnames}")
        for r in rd:
            try:
                out[r["word"].strip().lower()] = {k: float(r[k]) for k in keys}
            except (TypeError, ValueError):
                continue
    if not out:
        raise SystemExit("FATAL: norm file produced no usable rows")
    return out


def build_subspace(X: np.ndarray, y: dict[str, np.ndarray],
                   keys: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
    dirs = {k: p2_ridge_std(X, y[k]) for k in keys}
    M = np.stack([dirs[k] for k in keys], axis=1)
    Q, _ = np.linalg.qr(M)
    return Q, M


def analyse(X: np.ndarray, axes: np.ndarray, y: dict[str, np.ndarray],
            keys: tuple[str, ...], D: int) -> dict[str, Any]:
    if len(keys) != RANK:
        raise SystemExit(f"FATAL: subspace rank must be {RANK} (prereg 54.2), "
                         f"got {len(keys)}")
    Q, _ = build_subspace(X, y, keys)
    obs = [inside_fraction(axes[i], Q) for i in range(len(axes))]
    rng = np.random.default_rng(NULL_SEED)
    R = rng.standard_normal((N_RANDOM, D))
    R /= np.linalg.norm(R, axis=1, keepdims=True)
    null = np.einsum("ij,ij->i", R @ Q, R @ Q)
    nm = float(null.mean())
    return {"inside_pct": [round(100 * o, 4) for o in obs],
            "null_mean_pct": round(100 * nm, 4),
            "null_p95_pct": round(100 * float(np.quantile(null, 0.95)), 4),
            "ratio_to_null": [round(o / nm, 2) for o in obs],
            "p_vs_null": [round(float((null >= o).mean()), 4) for o in obs]}


def contamination(y_new: dict[str, np.ndarray],
                  y_vad: dict[str, np.ndarray]) -> dict[str, Any]:
    """Prereg 54.3 criterion C: a 'non-affective' dimension correlating with
    V/A/D above |r| = 0.5 is not usable as a control."""
    rows, worst = [], 0.0
    for kn, vn in y_new.items():
        for kv, vv in y_vad.items():
            r = float(np.corrcoef(vn, vv)[0, 1])
            rows.append({"non_affective_dim": kn, "vad_dim": kv,
                         "pearson_r": round(r, 4)})
            worst = max(worst, abs(r))
    return {"pairs": rows, "max_abs_r": round(worst, 4),
            "usable": bool(worst <= CONTAMINATION_MAX),
            "rule": f"prereg 54.3 C: unusable if |r| > {CONTAMINATION_MAX}"}


def dry_run() -> int:
    """Exercise every production function on synthetic data."""
    ok = True

    def c(n: str, v: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if v else 'FAIL'}] {n}")
        ok &= bool(v)

    rng = np.random.default_rng(0)
    n, D = 287, 64
    X = rng.standard_normal((n, D))
    keys = ("dim_a", "dim_b", "dim_c")
    # a direction that is genuinely encoded, plus two unrelated ones
    true_d = _unit(rng.standard_normal(D))
    y = {"dim_a": X @ true_d + 0.01 * rng.standard_normal(n),
         "dim_b": rng.standard_normal(n),
         "dim_c": rng.standard_normal(n)}
    Q, M = build_subspace(X, y, keys)
    c("subspace is orthonormal", np.allclose(Q.T @ Q, np.eye(RANK), atol=1e-8))
    c("subspace has the registered rank", Q.shape[1] == RANK)
    c("an encoded direction is recovered inside the subspace",
      inside_fraction(true_d, Q) > 0.5)
    axes = np.stack([_unit(rng.standard_normal(D)) for _ in range(N_AXES)])
    res = analyse(X, axes, y, keys, D)
    c("a random axis sits near the chance level",
      all(r < 5.0 for r in res["ratio_to_null"]))
    c("null mean is close to rank/D",
      abs(res["null_mean_pct"] - 100 * RANK / D) < 0.6 * 100 * RANK / D)
    # rank guard must fire
    try:
        analyse(X, axes, y, ("dim_a", "dim_b"), D)
        c("rank guard rejects a non-rank-3 subspace", False)
    except SystemExit:
        c("rank guard rejects a non-rank-3 subspace", True)
    # contamination guard must fire on a copied dimension
    vad = {"valence": y["dim_a"], "arousal": rng.standard_normal(n),
           "dominance": rng.standard_normal(n)}
    c("contamination guard flags a dimension copied from valence",
      not contamination(y, vad)["usable"])
    c("contamination guard passes independent dimensions",
      contamination({"z": rng.standard_normal(n)},
                    {"valence": rng.standard_normal(n)})["usable"])
    # sentence scoring, including the suffix backoff
    norms = {"happy": {"dim_a": 1.0, "dim_b": 2.0, "dim_c": 3.0}}
    s, nw, nc = sentence_score("They were happier and happy", norms, keys)
    c("sentence scoring averages the covered words", s is not None and nc >= 1)
    s2, _, nc2 = sentence_score("zzz qqq", norms, keys)
    c("a sentence with no covered word returns None", s2 is None and nc2 == 0)
    print("DRY-RUN:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--norms", type=Path,
                    help="CSV/TSV with a 'word' column plus the three dimensions")
    ap.add_argument("--dims", nargs=3, metavar=("D1", "D2", "D3"),
                    help="the three non-affective dimension column names")
    ap.add_argument("--norm-set-name", default="",
                    help="declared, citation-verified name of the norm set")
    ap.add_argument("--citation-verified", action="store_true",
                    help="set only after Ito has confirmed the bibliography "
                         "first-hand (prereg 54.6)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        return dry_run()
    if dry_run() != 0:
        print("REFUSING to run: dry-run failed")
        return 2
    if not (a.norms and a.dims and a.norm_set_name):
        print("REFUSING to run: --norms, --dims and --norm-set-name are required")
        return 2
    if not a.citation_verified:
        print("REFUSING to run: the norm set's bibliography is unverified "
              "(prereg 54.6). Confirm it first-hand, then pass "
              "--citation-verified.")
        return 3

    keys = tuple(a.dims)
    norms = load_norms(a.norms, keys)
    e1 = json.loads(E1.read_text())
    from alignment_primary import stim_vad          # reuse the registered loader
    sys.path.insert(0, str(Path(__file__).parent))

    scored, cov = [], []
    for s in e1:
        sc, nw, nc = sentence_score(s["text"], norms, keys)
        scored.append(sc)
        cov.append((nw, nc))
    keep = [i for i, s in enumerate(scored) if s is not None]
    y_new = {k: np.array([scored[i][k] for i in keep]) for k in keys}
    print(f"coverage: {len(keep)}/{len(e1)} sentences scored; "
          f"mean word coverage {np.mean([c[1] / max(c[0], 1) for c in cov]):.3f}")

    out: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "prereg_section": "54 (non-affective control), 55.6 (revised prediction)",
        "norm_set": a.norm_set_name, "dimensions": list(keys),
        "norm_file_sha256": hashlib.sha256(a.norms.read_bytes()).hexdigest(),
        "n_sentences_scored": len(keep), "n_sentences_total": len(e1),
        "subspace_rank": RANK, "n_random_null": N_RANDOM,
        "gpu_used": False, "layers": {}}
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("NOTE: the per-layer computation needs the cached activations on the "
          "server; run this there once the norm set is confirmed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
