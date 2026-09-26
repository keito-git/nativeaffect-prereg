#!/usr/bin/env python3
"""Define the discovery/confirmation split of E1 (addendum 13).

E1 had no split: axis_rebuilt_split_20260925.json splits E4's 40 intervention
stimuli. Candidate directions must come from the discovery half only, so the
split has to exist before any candidate is computed.

Stratified by tertile of Warriner valence, because the judgement statistic is a
change in the output distribution and valence is the stimulus property that
moves it most; an unstratified draw could put extreme valence on one side and
make a group difference reflect the stimuli rather than the directions.

CPU only. No judgement statistic is computed here.
"""
from __future__ import annotations
import csv, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
VADCSV = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
OUT = Path("/path/to/work/results/plan_b/e1_split_20260926.json")
SEED = 20260926
_SUF = ("s", "es", "ed", "ing", "ly")


def load_vad() -> dict:
    out = {}
    with VADCSV.open() as fh:
        for r in csv.DictReader(fh):
            try:
                out[r["word"].strip().lower()] = float(r["valence"])
            except (KeyError, TypeError, ValueError):
                continue
    return out


def sent_valence(text: str, vad: dict):
    hits = []
    for w in re.findall(r"[a-zA-Z']+", text.lower()):
        if w in vad:
            hits.append(vad[w]); continue
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                hits.append(vad[w[: -len(s)]]); break
    return float(np.mean(hits)) if hits else None


def main() -> int:
    e1 = json.loads(E1.read_text())
    vad = load_vad()
    scored = [(i, s.get("id", f"e1_{i:04d}"), sent_valence(s["text"], vad))
              for i, s in enumerate(e1)]
    keep = [(i, sid, v) for i, sid, v in scored if v is not None]
    assert len(keep) == 287, f"expected 287 scored sentences, got {len(keep)}"
    vals = np.array([v for _, _, v in keep])
    q33, q67 = np.quantile(vals, [1/3, 2/3])
    strata = {"low": [], "mid": [], "high": []}
    for (i, sid, v) in keep:
        k = "low" if v <= q33 else ("mid" if v <= q67 else "high")
        strata[k].append((i, sid, v))

    rng = np.random.default_rng(SEED)
    disc, conf, per = [], [], {}
    for k in ("low", "mid", "high"):          # fixed order for reproducibility
        rows = sorted(strata[k], key=lambda t: t[0])
        idx = rng.permutation(len(rows))
        # remainder to discovery, as the addendum specifies
        n_disc = int(np.ceil(len(rows) / 2))
        d = [rows[j] for j in idx[:n_disc]]
        c = [rows[j] for j in idx[n_disc:]]
        disc += d; conf += c
        per[k] = {"n": len(rows), "discovery": len(d), "confirmation": len(c),
                  "valence_min": float(min(v for *_, v in rows)),
                  "valence_max": float(max(v for *_, v in rows))}
    disc.sort(key=lambda t: t[0]); conf.sort(key=lambda t: t[0])
    dv = np.array([v for *_, v in disc]); cv = np.array([v for *_, v in conf])
    rec = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "created_by": "Nakamura (experiment, team Nomura)",
        "addendum": "13", "prereg_commit": "2013dae",
        "defined_before_any_G1_judgement": True,
        "purpose": ("E1 had no split; axis_rebuilt_split_20260925.json splits E4. "
                    "Candidate directions are computed from the discovery half "
                    "only, so this must exist first."),
        "population": "E1 sentences with a Warriner valence score",
        "n_total_file": len(e1), "n_scored": len(keep),
        "stimuli_file": str(E1),
        "stimuli_sha256": hashlib.sha256(E1.read_bytes()).hexdigest(),
        "vad_file_sha256": hashlib.sha256(VADCSV.read_bytes()).hexdigest(),
        "seed": SEED, "rng": "numpy.random.default_rng",
        "stratification": {"variable": "sentence-level Warriner valence "
                                       "(mean over matched words)",
                           "tertile_q33": float(q33), "tertile_q67": float(q67),
                           "per_stratum": per},
        "allocation_rule": ("50/50 within each stratum; an odd stratum sends the "
                            "remainder to discovery"),
        "n_discovery": len(disc), "n_confirmation": len(conf),
        "balance_check": {
            "discovery_valence_mean": float(dv.mean()),
            "confirmation_valence_mean": float(cv.mean()),
            "abs_mean_difference": float(abs(dv.mean() - cv.mean())),
            "discovery_valence_sd": float(dv.std(ddof=1)),
            "confirmation_valence_sd": float(cv.std(ddof=1))},
        "discovery_indices": [i for i, _, _ in disc],
        "confirmation_indices": [i for i, _, _ in conf],
        "discovery_ids": [s for _, s, _ in disc],
        "confirmation_ids": [s for _, s, _ in conf],
        "USAGE_RULE": ("Candidate directions (ICA, principal components, "
                       "Jacobian sensitivity) and the PMF basis are computed "
                       "from the discovery indices only. The confirmation half "
                       "is not read until G1's verdict is fixed."),
    }
    assert not (set(rec["discovery_indices"]) & set(rec["confirmation_indices"]))
    assert len(rec["discovery_indices"]) + len(rec["confirmation_indices"]) == 287
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    print(f"scored {len(keep)}/{len(e1)}")
    print(f"tertiles: q33={q33:.4f}  q67={q67:.4f}")
    for k, v in per.items():
        print(f"  {k:<5} n={v['n']:>3}  disc={v['discovery']:>3} "
              f"conf={v['confirmation']:>3}  valence {v['valence_min']:.2f}-"
              f"{v['valence_max']:.2f}")
    print(f"TOTAL discovery={len(disc)}  confirmation={len(conf)}")
    print(f"valence mean: discovery={dv.mean():.4f}  confirmation={cv.mean():.4f} "
          f"(diff {abs(dv.mean()-cv.mean()):.4f})")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
