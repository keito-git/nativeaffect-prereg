"""How many stimuli actually entered each pos-control fit, under each lookup."""
import csv
import json
import re

import numpy as np

vad = {}
for row in csv.DictReader(open(
        "/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv",
        encoding="utf-8")):
    w = row.get("word", "").strip().lower()
    try:
        vad[w] = float(row.get("valence", "").strip())
    except ValueError:
        pass

SUF = ["fully", "fulness", "fulness", "ful", "ness", "ly",
       "ing", "tion", "ed", "er", "est", "s"]


def lk(w):
    if w in vad:
        return vad[w]
    for s in SUF:
        if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
            return vad[w[: -len(s)]]
    return None


def v_strip(t):
    sc = [x for x in (lk(w) for w in re.findall(r"[a-zA-Z']+", t.lower()))
          if x is not None]
    return float(np.mean(sc)) if sc else None


def v_plain(t):
    sc = [vad[w] for w in re.findall(r"[a-z']+", t.lower()) if w in vad]
    return float(np.mean(sc)) if sc else None


st = json.load(open("/path/to/work/code/stimuli/stimuli_e4.json",
                    encoding="utf-8"))[:40]
for name, fn in (("strip (run_intervention.py, main sweep)", v_strip),
                 ("plain (predecessor run_pos_ctrl_pooling_check.py)", v_plain)):
    vals = [fn(s["text"]) for s in st]
    for label, sub in (("first30", vals[:30]), ("all40", vals)):
        keep = [i for i, v in enumerate(sub) if v is not None]
        npos = sum(1 for i in keep if i < 20)
        nneg = len(keep) - npos
        vv = [sub[i] for i in keep]
        print(f"{name:<52} {label:<8} n_fit={len(keep):<3} "
              f"pos={npos:<3} neg={nneg:<3} "
              f"range=[{min(vv):.2f},{max(vv):.2f}] std={np.std(vv):.3f}")
