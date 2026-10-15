"""Amendment 86 CE2: does the appraisal-adjective readout track the human ratings at all?

Appraisal dimensions are rated on a scale, so the check is stronger than a modal-choice test:
split the stimuli at the median rating of a dimension and ask whether, with no intervention, the
model puts more probability on that dimension's adjective for the highly rated half. A majority
of the twelve must agree, or the readout is not used.
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


RES = Path(_ROOT + "/results/plan_b/appcheck")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261008
N_PER = 60
FRAME = "Event: {text}\n\nThe event was"
APPRAISALS = ["suddenness", "familiarity", "predict_event", "pleasantness", "unpleasantness",
              "goal_relevance", "chance_responsblt", "self_responsblt", "other_responsblt",
              "predict_conseq", "goal_support", "urgency", "self_control", "other_control",
              "chance_control", "accept_conseq", "standards", "social_norms",
              "attention", "not_consider", "effort"]
ADJ = {"suddenness": "sudden", "familiarity": "familiar", "predict_event": "predictable",
       "pleasantness": "pleasant", "unpleasantness": "unpleasant", "goal_relevance": "important",
       "predict_conseq": "foreseeable", "urgency": "urgent", "self_control": "controllable",
       "accept_conseq": "acceptable", "social_norms": "normal", "chance_responsblt": "accidental"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    texts, app = [], []
    for r in csv.DictReader(open(DATA, encoding="utf-8"), delimiter="\t"):
        t = (r.get("generated_text") or "").strip()
        if not t:
            continue
        try:
            vals = [float(r[k]) for k in APPRAISALS]
        except (KeyError, ValueError):
            continue
        texts.append(t); app.append(vals)
    app = np.asarray(app)
    dims = [k for k in APPRAISALS if k in ADJ]

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

    ids = [first_id(ADJ[d]) for d in dims]
    shared = len(ids) - len(set(ids))
    print(f"check 3, token overlap {shared}  ({'pass' if shared == 0 else 'fail'})", flush=True)

    @torch.no_grad()
    def probs(prompts):
        out = []
        for i in range(0, len(prompts), 8):
            b = tok(prompts[i:i + 8], return_tensors="pt", padding=True).to(model.device)
            out.append(torch.softmax(model(**b).logits[:, -1, :].float(), -1).cpu().numpy())
        return np.concatenate(out, 0)

    hits, rows, pool, degenerate = 0, {}, [], []
    for di, d in enumerate(dims):
        col = app[:, APPRAISALS.index(d)]
        # Several dimensions are rated at the floor by most annotators, so a median split can
        # leave one side empty. A tail split is tried next, and a dimension that still cannot be
        # split is recorded as unmeasurable and counted as not agreeing.
        med = float(np.median(col))
        hi = np.flatnonzero(col > med); lo = np.flatnonzero(col < med)
        if len(hi) == 0 or len(lo) == 0:
            q_hi, q_lo = float(np.quantile(col, 0.75)), float(np.quantile(col, 0.25))
            hi = np.flatnonzero(col >= max(q_hi, col.min() + 1e-9))
            lo = np.flatnonzero(col <= q_lo)
        if len(hi) == 0 or len(lo) == 0 or set(col[hi]) == set(col[lo]):
            degenerate.append(d)
            rows[d] = {"adj": ADJ[d], "split_degenerate": True, "match": False,
                       "values": sorted(set(float(x) for x in col))[:6]}
            print(f"  {d:20s} {ADJ[d]:14s} ratings too skewed to split in two (counted as a mismatch)",
                  flush=True)
            continue
        hi = rng.permutation(hi)[:N_PER]; lo = rng.permutation(lo)[:N_PER]
        ph = probs([FRAME.format(text=texts[i]) for i in hi])[:, ids[di]]
        pl = probs([FRAME.format(text=texts[i]) for i in lo])[:, ids[di]]
        pool.append(ph); pool.append(pl)
        # rank-based effect size, so a heavy tail in the probabilities cannot drive it
        auc = float((ph[:, None] > pl[None, :]).mean() + 0.5 * (ph[:, None] == pl[None, :]).mean())
        ok = auc > 0.5
        hits += int(ok)
        rows[d] = {"adj": ADJ[d], "split_degenerate": False, "median": med,
                   "n_hi": int(len(hi)), "n_lo": int(len(lo)),
                   "mean_hi": float(ph.mean()), "mean_lo": float(pl.mean()),
                   "auc": round(auc, 4), "match": bool(ok)}
        print(f"  {d:20s} {ADJ[d]:14s} high ratings {ph.mean():.3e} low ratings {pl.mean():.3e} "
              f"AUC {auc:.3f} {'match' if ok else ''}", flush=True)
    pool = np.concatenate(pool)
    distinct = int(len(np.unique(np.round(pool, 14))))
    print(f"\ncheck 1, discriminability: distinct values {distinct} / sd {pool.std():.3e} "
          f"({'pass' if distinct >= 10 and pool.std() > 0 else 'fail'})", flush=True)
    print(f"check 2, agreement with the ratings {hits}/{len(dims)} "
          f"({'pass' if hits > len(dims) // 2 else 'fail'})", flush=True)
    if degenerate:
        print(f"  dimensions that could not be split {len(degenerate)}: {', '.join(degenerate)}", flush=True)
    json.dump({"model": a.model, "tag": a.tag, "dims": dims, "ids": ids, "shared": shared,
               "degenerate_dims": degenerate,
               "distinct": distinct, "sd": float(pool.std()), "hits": hits, "n_dims": len(dims),
               "validity_ok": bool(shared == 0 and distinct >= 10 and pool.std() > 0
                                   and hits > len(dims) // 2),
               "per_dim": rows},
              open(RES / f"appcheck_{a.tag}.json", "w"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
