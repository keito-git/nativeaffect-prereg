#!/usr/bin/env python3
"""Fix the discovery / confirmation split of the E4 stimuli BEFORE any analysis.

Pre-registration: 03_解析/preregistration/axis_rebuilt_prereg_20260925.md §4-1.
Stratified by emotion polarity and by emotion category (2 items per category in
E4 indices 0-39), one item of each category to each side, so both sides hold
10 positive + 10 negative and every category appears on both sides.

Deterministic: seed 20260925. Writes the assignment table and its sha256.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

STIM = Path("/path/to/work/code/stimuli/stimuli_e4.json")
OUT = Path("/path/to/work/results/axes_nopad/axis_rebuilt_split_20260925.json")
SEED = 20260925

stim = json.loads(STIM.read_text())[:40]
assert len(stim) == 40, len(stim)

# E4 layout (run_c1_sweep_repro.sh): indices 0-19 positive, 20-39 negative,
# two consecutive items per emotion category.
cats: dict[str, list[int]] = {}
for i, s in enumerate(stim):
    # id form: e4_<category>_<n>
    cat = s["id"].rsplit("_", 1)[0]
    cats.setdefault(cat, []).append(i)
assert all(len(v) == 2 for v in cats.values()), {k: v for k, v in cats.items()
                                                 if len(v) != 2}
assert len(cats) == 20, len(cats)

rng = np.random.default_rng(SEED)
discovery: list[int] = []
confirmation: list[int] = []
for cat in sorted(cats):
    a, b = cats[cat]
    if rng.random() < 0.5:
        discovery.append(a)
        confirmation.append(b)
    else:
        discovery.append(b)
        confirmation.append(a)

discovery.sort()
confirmation.sort()
assert len(discovery) == len(confirmation) == 20
assert set(discovery) & set(confirmation) == set()
assert set(discovery) | set(confirmation) == set(range(40))
n_pos_d = sum(1 for i in discovery if i < 20)
n_pos_c = sum(1 for i in confirmation if i < 20)
assert n_pos_d == n_pos_c == 10, (n_pos_d, n_pos_c)

payload = {
    "created_utc": "2026-09-25",
    "created_by": "experiment lead",
    "prereg": ("03_解析/preregistration/axis_rebuilt_prereg_20260925.md "
               "§4-1 and §10"),
    "seed": SEED,
    "stimuli_file": str(STIM),
    "stimuli_sha256": hashlib.sha256(STIM.read_bytes()).hexdigest(),
    "rule": ("stratified by emotion category (2 items each in E4 0-39): one item "
             "of every category to each side, so each side has 10 positive "
             "(idx<20) and 10 negative (idx>=20) stimuli"),
    "discovery_indices": discovery,
    "confirmation_indices": confirmation,
    "discovery_ids": [stim[i]["id"] for i in discovery],
    "confirmation_ids": [stim[i]["id"] for i in confirmation],
    "n_positive_discovery": n_pos_d,
    "n_positive_confirmation": n_pos_c,
    "USAGE_RULE": ("The confirmation side must NOT be looked at until the "
                   "description hypotheses are appended to the pre-registration "
                   "with a timestamp. Discovery-side numbers are never cited as "
                   "confirmatory evidence."),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
print(f"wrote {OUT}")
print(f"split sha256: {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
print(f"discovery   : {discovery}")
print(f"confirmation: {confirmation}")
