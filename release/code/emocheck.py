"""Amendment 88 CG6: how good is readout A itself? A diagnostic, not a judgement.

Readout B carries a validity check against the human ratings, readout A carried none, so the
gap in effect size between the two self-matched cells cannot be read without knowing how well
each readout tracks its own labels. This runs the same modal-agreement check on the thirteen
emotion words. Its result never enters a judgement.

Original header follows.

Amendment 85 CD3: the three validity checks on the action-verb readout, before any judgement.

1 distinctness -- the thirteen verb probabilities must not be degenerate without intervention
2 mapping -- for stimuli of a category, the category's own verb should be the most likely of the
  thirteen; a majority of categories must agree, or the mapping is not working and R-act is not
  used
3 no shared tokens between classes
"""
from __future__ import annotations

import argparse, csv, json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import os as _os
_ROOT = _os.environ.get("NA_ROOT", _os.path.join(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__))), "work"))


RES = Path(_ROOT + "/results/plan_b/emocheck")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261008
N_PER = 20
FRAME = ("Consider the following event description and the emotion of the person who "
         "experienced it.\n\nEvent: {text}\n\nThe emotion is")
# The single-token readout of amendment 82: the class word itself, with neutral for no-emotion.
VERBS = {"anger": "anger", "boredom": "boredom", "disgust": "disgust", "fear": "fear",
         "guilt": "guilt", "joy": "joy", "no-emotion": "neutral", "pride": "pride",
         "relief": "relief", "sadness": "sadness", "shame": "shame", "surprise": "surprise",
         "trust": "trust"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    texts, emo = [], []
    for r in csv.DictReader(open(DATA, encoding="utf-8"), delimiter="\t"):
        t = (r.get("generated_text") or "").strip()
        if not t:
            continue
        texts.append(t); emo.append((r.get("emotion") or "").strip())
    emo = np.asarray(emo)
    classes = sorted(set(emo) & set(VERBS))

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.float16, device_map="cuda:0", low_cpu_mem_usage=True)
    model.eval()

    def first_id(w):
        for form in (" " + w, w):
            for t in tok.encode(form, add_special_tokens=False):
                if tok.decode([t]).strip():
                    return int(t)
        raise SystemExit(f"cannot tokenise word: {w}")

    ids = [first_id(VERBS[c]) for c in classes]
    shared = len(ids) - len(set(ids))
    print(f"overlap {shared}  "
          f"({'pass' if shared == 0 else 'fail'})", flush=True)
    if shared:
        dup = sorted({i for i in ids if ids.count(i) > 1})
        print(f"  duplicate ids {dup} / word "
              f"{[VERBS[c] for c, i in zip(classes, ids) if i in dup]}", flush=True)

    @torch.no_grad()
    def probs(prompts):
        out = []
        for i in range(0, len(prompts), 8):
            b = tok(prompts[i:i + 8], return_tensors="pt", padding=True).to(model.device)
            lg = model(**b).logits[:, -1, :].float()
            out.append(torch.softmax(lg, dim=-1).cpu().numpy())
        return np.concatenate(out, 0)

    hits, rows = 0, {}
    allp = []
    for ci, c in enumerate(classes):
        idx = np.flatnonzero(emo == c)
        idx = rng.permutation(idx)[:N_PER]
        p = probs([FRAME.format(text=texts[i]) for i in idx])
        pv = p[:, ids]
        allp.append(pv)
        modal = int(np.argmax(pv.mean(0)))
        ok = modal == ci
        hits += int(ok)
        rows[c] = {"verb": VERBS[c], "modal_verb": VERBS[classes[modal]],
                   "match": bool(ok), "n": int(len(idx)),
                   "own_rank": int(1 + (pv.mean(0) > pv.mean(0)[ci]).sum())}
        print(f"  {c:12s} own word {VERBS[c]:10s} modal {VERBS[classes[modal]]:10s} "
              f"rank {rows[c]['own_rank']:2d}/13 {'match' if ok else ''}", flush=True)
    allp = np.concatenate(allp, 0)
    distinct = int(len(np.unique(np.round(allp, 12))))
    sd = float(allp.std())
    print(f"\ncheck 1, discriminability: distinct values {distinct} / sd {sd:.3e} "
          f"({'pass' if distinct >= 10 and sd > 0 else 'fail'})", flush=True)
    print(f"check 2, modal match {hits}/{len(classes)} "
          f"({'pass' if hits > len(classes) // 2 else 'fail'})", flush=True)
    json.dump({"model": a.model, "tag": a.tag, "classes": classes, "ids": ids,
               "shared": shared, "distinct": distinct, "sd": sd,
               "modal_hits": hits, "n_classes": len(classes),
               "validity_ok": bool(shared == 0 and distinct >= 10 and sd > 0
                                   and hits > len(classes) // 2),
               "per_class": rows},
              open(RES / f"actcheck_{a.tag}.json", "w"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
