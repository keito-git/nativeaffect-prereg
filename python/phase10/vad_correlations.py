#!/usr/bin/env python3
"""Measure V/A/D correlations directly in the norms file we actually use.

CPU only, no model, no GPU.

Why: the claim "the subspace degeneracy reflects a valence-dominance correlation
in the norms" must be shown from the data in hand, not asserted from memory of
the literature. Two levels matter:

  word level     - the correlation among the 2298 entries of the norms file
  sentence level - the correlation among the AVERAGED scores that are actually
                   used as regression targets, computed separately for the 20
                   discovery E4 stimuli and for the 287 matched E1 sentences

The sentence level is the one that governs the subspace: if the targets
y_valence and y_dominance are nearly collinear over a stimulus set, the two
regressed directions must be nearly collinear too.

No claim about what any publication reports is made here; only measured values.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats as sp

VADP = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
SPLIT = Path("/path/to/work/results/axes_nopad/"
             "axis_rebuilt_split_20260925.json")
OUT = Path("/path/to/work/results/axes_nopad/vad_correlations.json")
KEYS = ("valence", "arousal", "dominance")
_SUF = ["fully", "fulness", "fulness", "ful", "ness", "ly",
        "ing", "tion", "ed", "er", "est", "s"]

rows = list(csv.DictReader(open(VADP, encoding="utf-8")))
vad: dict[str, dict[str, float]] = {}
for r in rows:
    w = r.get("word", "").strip().lower()
    if not w:
        continue
    try:
        vad[w] = {k: float(r[k].strip()) for k in KEYS}
    except (KeyError, ValueError, AttributeError):
        continue

W = {k: np.array([vad[w][k] for w in vad]) for k in KEYS}


def pair_stats(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    pr, pp = sp.pearsonr(x, y)
    sr, sp_ = sp.spearmanr(x, y)
    return {"n": int(x.size), "pearson_r": round(float(pr), 4),
            "pearson_p": float(pp), "spearman_rho": round(float(sr), 4),
            "spearman_p": float(sp_)}


def look(w: str) -> dict[str, float] | None:
    if w in vad:
        return vad[w]
    for s in _SUF:
        if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
            return vad[w[: -len(s)]]
    return None


def sent_scores(texts: list[str]) -> tuple[dict[str, np.ndarray], int, int]:
    out: list[dict[str, float]] = []
    for t in texts:
        hits = [h for h in (look(w) for w in re.findall(r"[a-zA-Z']+", t.lower()))
                if h is not None]
        if hits:
            out.append({k: float(np.mean([h[k] for h in hits])) for k in KEYS})
    return ({k: np.array([o[k] for o in out]) for k in KEYS}, len(out), len(texts))


report: dict[str, Any] = {
    "norms_file": str(VADP),
    "norms_sha256": __import__("hashlib").sha256(VADP.read_bytes()).hexdigest(),
    "n_entries": len(vad),
    "columns_present": sorted(rows[0].keys()) if rows else [],
    "IMPORTANT": ("this file holds 2298 entries, a SUBSET of the full Warriner "
                  "et al. norm list; correlations below describe THIS file only "
                  "and no published value is asserted here"),
    "word_level": {f"{a}-{b}": pair_stats(W[a], W[b])
                   for i, a in enumerate(KEYS) for b in KEYS[i + 1:]},
}

e1 = json.loads(E1.read_text())
e4 = json.loads(E4.read_text())
disc = json.loads(SPLIT.read_text())["discovery_indices"]

for name, texts in (("sentence_level_E1_300", [s["text"] for s in e1]),
                    ("sentence_level_E4_discovery_20",
                     [e4[i]["text"] for i in disc]),
                    ("sentence_level_E4_heldout_40to79",
                     [e4[i]["text"] for i in range(40, len(e4))])):
    sc, n_ok, n_all = sent_scores(list(texts))
    report[name] = {"n_matched": n_ok, "n_total": n_all,
                    **{f"{a}-{b}": pair_stats(sc[a], sc[b])
                       for i, a in enumerate(KEYS) for b in KEYS[i + 1:]}}

wl = report["word_level"]["valence-dominance"]["pearson_r"]
s_e1 = report["sentence_level_E1_300"]["valence-dominance"]["pearson_r"]
s_d = report["sentence_level_E4_discovery_20"]["valence-dominance"]["pearson_r"]
report["interpretation_check"] = {
    "observed_subspace_cos_V_D_S1_discovery": [0.984, 0.978, 0.989, 0.984],
    "observed_subspace_cos_V_D_S2_E1": [0.7916, 0.7939, 0.8331, 0.8549],
    "word_level_r_V_D": wl,
    "sentence_level_r_V_D_E1": s_e1,
    "sentence_level_r_V_D_discovery": s_d,
    "question": ("does the target-level V-D correlation explain the direction "
                 "collinearity, and is the discovery set more collinear than E1?"),
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False))

print(f"norms file: {VADP}  entries={len(vad)}")
print("\n--- WORD level (this file's 2298 entries) ---")
for k, v in report["word_level"].items():
    print(f"  {k:<22} pearson r={v['pearson_r']:+.4f} "
          f"spearman rho={v['spearman_rho']:+.4f}  (n={v['n']})")
for name in ("sentence_level_E1_300", "sentence_level_E4_discovery_20",
             "sentence_level_E4_heldout_40to79"):
    d = report[name]
    print(f"\n--- SENTENCE level: {name} "
          f"(matched {d['n_matched']}/{d['n_total']}) ---")
    for k in [f"{a}-{b}" for i, a in enumerate(KEYS) for b in KEYS[i + 1:]]:
        v = d[k]
        print(f"  {k:<22} pearson r={v['pearson_r']:+.4f} "
              f"spearman rho={v['spearman_rho']:+.4f}")
print(f"\nwrote {OUT}")
