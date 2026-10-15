"""Amendment 88 CG6: readout A and readout B on one comparable scale.

The effect sizes in the two self-matched cells differ by an order of magnitude, but the two
readouts were validated with different measures -- modal agreement for the emotion words, an
AUC against the ratings for the appraisal adjectives. Neither says how sharply a readout
separates the thing it is supposed to track. This computes, for both, the probability that a
stimulus carrying the label ranks above one that does not, on the readout coordinate for that
label. Diagnostic only; it enters no judgement.
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


RES = Path(_ROOT + "/results/plan_b/roauc")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261008
N_PER = 60
FRAME_A = ("Consider the following event description and the emotion of the person who "
           "experienced it.\n\nEvent: {text}\n\nThe emotion is")
FRAME_B = "Event: {text}\n\nThe event was"
WORDS_A = {"anger": "anger", "boredom": "boredom", "disgust": "disgust", "fear": "fear",
           "guilt": "guilt", "joy": "joy", "no-emotion": "neutral", "pride": "pride",
           "relief": "relief", "sadness": "sadness", "shame": "shame", "surprise": "surprise",
           "trust": "trust"}
APPRAISALS = ["suddenness", "familiarity", "predict_event", "pleasantness", "unpleasantness",
              "goal_relevance", "chance_responsblt", "self_responsblt", "other_responsblt",
              "predict_conseq", "goal_support", "urgency", "self_control", "other_control",
              "chance_control", "accept_conseq", "standards", "social_norms",
              "attention", "not_consider", "effort"]
WORDS_B = {"suddenness": "sudden", "familiarity": "familiar", "predict_event": "predictable",
           "pleasantness": "pleasant", "unpleasantness": "unpleasant",
           "goal_relevance": "important", "predict_conseq": "foreseeable", "urgency": "urgent",
           "self_control": "controllable", "accept_conseq": "acceptable",
           "social_norms": "normal", "chance_responsblt": "accidental"}


def auc(pos, neg):
    pos, neg = np.asarray(pos)[:, None], np.asarray(neg)[None, :]
    return float((pos > neg).mean() + 0.5 * (pos == neg).mean())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    texts, emo, app = [], [], []
    for r in csv.DictReader(open(DATA, encoding="utf-8"), delimiter="\t"):
        t = (r.get("generated_text") or "").strip()
        if not t:
            continue
        try:
            vals = [float(r[k]) for k in APPRAISALS]
        except (KeyError, ValueError):
            continue
        texts.append(t); emo.append((r.get("emotion") or "").strip()); app.append(vals)
    emo = np.asarray(emo); app = np.asarray(app)

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

    @torch.no_grad()
    def probs(prompts, ids):
        out = []
        for i in range(0, len(prompts), 8):
            b = tok(prompts[i:i + 8], return_tensors="pt", padding=True).to(model.device)
            p = torch.softmax(model(**b).logits[:, -1, :].float(), -1).cpu().numpy()
            out.append(p[:, ids])
        return np.concatenate(out, 0)

    rep = {}
    # readout A: in-category stimuli against out-of-category stimuli
    cls = sorted(set(emo) & set(WORDS_A))
    ids_a = [first_id(WORDS_A[c]) for c in cls]
    aucs_a = {}
    for ci, c in enumerate(cls):
        inc = rng.permutation(np.flatnonzero(emo == c))[:N_PER]
        out = rng.permutation(np.flatnonzero(emo != c))[:N_PER]
        pi = probs([FRAME_A.format(text=texts[i]) for i in inc], ids_a)[:, ci]
        po = probs([FRAME_A.format(text=texts[i]) for i in out], ids_a)[:, ci]
        aucs_a[c] = round(auc(pi, po), 4)
        print(f"  A {c:12s} AUC {aucs_a[c]:.3f}", flush=True)
    rep["A"] = aucs_a

    # readout B: highly rated stimuli against the rest, with the tail split as a fallback
    dims = [k for k in APPRAISALS if k in WORDS_B]
    ids_b = [first_id(WORDS_B[d]) for d in dims]
    aucs_b, skipped = {}, []
    for di, d in enumerate(dims):
        col = app[:, APPRAISALS.index(d)]
        med = float(np.median(col))
        hi = np.flatnonzero(col > med); lo = np.flatnonzero(col < med)
        if len(hi) == 0 or len(lo) == 0:
            hi = np.flatnonzero(col >= float(np.quantile(col, 0.75)))
            lo = np.flatnonzero(col <= float(np.quantile(col, 0.25)))
        if len(hi) == 0 or len(lo) == 0:
            skipped.append(d); print(f"  B {d:20s} cannot be split", flush=True); continue
        hi = rng.permutation(hi)[:N_PER]; lo = rng.permutation(lo)[:N_PER]
        ph = probs([FRAME_B.format(text=texts[i]) for i in hi], ids_b)[:, di]
        pl = probs([FRAME_B.format(text=texts[i]) for i in lo], ids_b)[:, di]
        aucs_b[d] = round(auc(ph, pl), 4)
        print(f"  B {d:20s} AUC {aucs_b[d]:.3f}", flush=True)
    rep["B"] = aucs_b
    rep["B_skipped"] = skipped

    va = list(aucs_a.values()); vb = list(aucs_b.values())
    print(f"\nreadout A AUC median {np.median(va):.3f} range {min(va):.3f}-{max(va):.3f} (n={len(va)})",
          flush=True)
    print(f"readout B AUC median {np.median(vb):.3f} range {min(vb):.3f}-{max(vb):.3f} (n={len(vb)})",
          flush=True)
    rep.update(model=a.model, tag=a.tag,
               A_median=float(np.median(va)), B_median=float(np.median(vb)))
    json.dump(rep, open(RES / f"roauc_{a.tag}.json", "w"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
