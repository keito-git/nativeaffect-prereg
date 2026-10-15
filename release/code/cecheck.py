"""Amendment 91 CJ1: can the model do the codebook task at all, before anything is judged?

Readout B failed because it separated its own labels at AUC 0.56, which made a null result
uninformative. The bar here is fixed in advance: at least seven of thirteen categories above
chance, and a median AUC of 0.65 or better. Below that the cross-encoding test is declared
uninformative and no judgement is made; the codebook is not swapped for a better one.
"""
from __future__ import annotations

import argparse, csv, json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RES = Path(_ROOT + "/results/plan_b/cecheck")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261009
N_PER = 60
MIN_HITS, MIN_MEDIAN = 7, 0.65
PROMPT = "Code: {codebook}\n\nEvent: {text}\n\nAnswer with the code only. The code is"
CODE1 = {"anger": "Q", "boredom": "K", "disgust": "V", "fear": "Z", "guilt": "J", "joy": "X",
         "no-emotion": "N", "pride": "B", "relief": "F", "sadness": "M", "shame": "G",
         "surprise": "W", "trust": "L"}
CODE2 = {"anger": "M", "boredom": "W", "disgust": "L", "fear": "J", "guilt": "G", "joy": "Z",
         "no-emotion": "V", "pride": "K", "relief": "X", "sadness": "Q", "shame": "B",
         "surprise": "F", "trust": "N"}
# Amendment 99 CR2, the second code vocabulary; the tables are imported from the measurement script so the two cannot diverge
from stageSC2 import CODE3, CODE4  # noqa: E402

import os as _os
_ROOT = _os.environ.get("NA_ROOT", _os.path.join(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__))), "work"))



def auc(pos, neg):
    pos, neg = np.asarray(pos)[:, None], np.asarray(neg)[None, :]
    return float((pos > neg).mean() + 0.5 * (pos == neg).mean())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--codebook", choices=("1", "2", "3", "4"), required=True)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    CODE = {"1": CODE1, "2": CODE2, "3": CODE3, "4": CODE4}[a.codebook]

    texts, emo = [], []
    for r in csv.DictReader(open(DATA, encoding="utf-8"), delimiter="\t"):
        t = (r.get("generated_text") or "").strip()
        if not t:
            continue
        texts.append(t); emo.append((r.get("emotion") or "").strip())
    emo = np.asarray(emo)
    classes = sorted(set(emo) & set(CODE))

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

    ids = [first_id(CODE[c]) for c in classes]
    shared = len(ids) - len(set(ids))
    print(f"check 3, token overlap {shared} ({'pass' if shared == 0 else 'fail'})", flush=True)
    if shared:
        json.dump({"model": a.model, "tag": a.tag, "codebook": a.codebook, "shared": shared,
                   "validity_ok": False, "reason": "token_collision"},
                  open(RES / f"cecheck_{a.tag}_ce{a.codebook}.json", "w"), indent=1)
        return 1

    cb = ", ".join(f"{c}={CODE[c]}" for c in classes)

    @torch.no_grad()
    def probs(prompts):
        out = []
        for i in range(0, len(prompts), 8):
            b = tok(prompts[i:i + 8], return_tensors="pt", padding=True).to(model.device)
            p = torch.softmax(model(**b).logits[:, -1, :].float(), -1).cpu().numpy()
            out.append(p[:, ids])
        return np.concatenate(out, 0)

    rows, aucs, pool = {}, {}, []
    for ci, c in enumerate(classes):
        inc = rng.permutation(np.flatnonzero(emo == c))[:N_PER]
        oth = rng.permutation(np.flatnonzero(emo != c))[:N_PER]
        pi = probs([PROMPT.format(codebook=cb, text=texts[i]) for i in inc])
        po = probs([PROMPT.format(codebook=cb, text=texts[i]) for i in oth])
        pool.append(pi); pool.append(po)
        aucs[c] = round(auc(pi[:, ci], po[:, ci]), 4)
        modal = int(np.argmax(pi.mean(0)))
        rows[c] = {"code": CODE[c], "auc": aucs[c], "modal_code": CODE[classes[modal]],
                   "modal_match": bool(modal == ci)}
        print(f"  {c:12s} code {CODE[c]} AUC {aucs[c]:.3f} "
              f"modal {CODE[classes[modal]]}{' match' if modal == ci else ''}", flush=True)
    pool = np.concatenate(pool)
    va = list(aucs.values())
    hits = sum(x > 0.5 for x in va)
    med = float(np.median(va))
    distinct = int(len(np.unique(np.round(pool, 14))))
    ok1 = distinct >= 10 and pool.std() > 0
    ok2 = hits >= MIN_HITS and med >= MIN_MEDIAN
    print(f"\ncheck 1, discriminability: distinct values {distinct} sd {pool.std():.3e} "
          f"({'pass' if ok1 else 'fail'})", flush=True)
    print(f"check 2, the mapping works: AUC>0.5  in  {hits}/{len(va)} (requires {MIN_HITS}), "
          f"median {med:.3f} (requires {MIN_MEDIAN})({'pass' if ok2 else 'fail'})", flush=True)
    print(f"  AUC range {min(va):.3f}-{max(va):.3f} / modal match "
          f"{sum(r['modal_match'] for r in rows.values())}/{len(rows)}", flush=True)
    json.dump({"model": a.model, "tag": a.tag, "codebook": a.codebook, "classes": classes,
               "ids": ids, "shared": shared, "distinct": distinct, "sd": float(pool.std()),
               "auc_hits": hits, "auc_median": med, "auc_min": min(va), "auc_max": max(va),
               "modal_hits": sum(r["modal_match"] for r in rows.values()),
               "validity_ok": bool(ok1 and ok2), "per_class": rows},
              open(RES / f"cecheck_{a.tag}_ce{a.codebook}.json", "w"), indent=1,
              ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
