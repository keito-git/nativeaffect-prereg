"""Judgement CMP rebuilt per amendments 82 and 83.

What changed from stageC_cmp.py, and why:

* The floor is matched on the eigenvalue-weighted variance profile, not on the bare multiset of
  principal coordinates. F5 flips the sign of every coordinate in the eigenbasis, so
  lambda_i * a_i^2 is preserved term by term and the norm needs no renormalisation. The old F4
  is still measured, with fewer draws, so the effect of the floor's construction stays visible.
* Each target gets its own floor draws, so a family is compared against a family matched to it
  direction by direction rather than against draws matched to one arbitrary direction.
* train / selection / test are one partition of the rows, checked disjoint at runtime. The old
  code drew two independent permutations of the same rows, which put 14 of 32 scoring contexts
  inside the rows the directions were fitted on.
* Appraisal probes are refitted here on training rows only, rather than loaded from a cache
  whose own split is not known to be disjoint from the scoring rows.
* Two readouts in one pass: one token per class with no-emotion on " neutral" (it used to be
  " surprise", which is another class), and the synonym sets from amendment 77.
* Besides the per-target counts, the number of targets cleared is compared against its own null
  distribution, which keeps the dependence between the thirteen targets instead of treating the
  count as thirteen independent tests.
"""
from __future__ import annotations

import argparse, csv, json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import intervene_core as ic

import os as _os
_ROOT = _os.environ.get("NA_ROOT", _os.path.join(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__))), "work"))


CACHE = Path(_ROOT + "/results/plan_b/audit_stageA")
RES = Path(_ROOT + "/results/plan_b/stageC3")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261007
N_TRAIN, N_INNER, N_SEL, N_TEST = 2600, 650, 32, 32
N_CALIB, N_BOOT = 12, 2000
M_F5, M_F4 = 10, 5
LAMBDAS = [1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7]
PROMPT = ("Consider the following event description and the emotion of the person who "
          "experienced it.\n\nEvent: {text}\n\nThe emotion is")
APPRAISALS = ["suddenness", "familiarity", "predict_event", "pleasantness", "unpleasantness",
              "goal_relevance", "chance_responsblt", "self_responsblt", "other_responsblt",
              "predict_conseq", "goal_support", "urgency", "self_control", "other_control",
              "chance_control", "accept_conseq", "standards", "social_norms",
              "attention", "not_consider", "effort"]
SYNS = {
    "anger": ["anger", "angry", "furious", "enraged"],
    "boredom": ["boredom", "bored", "dull", "tedious"],
    "disgust": ["disgust", "disgusted", "revolted", "repulsed"],
    "fear": ["fear", "afraid", "frightened", "scared"],
    "guilt": ["guilt", "guilty", "remorseful", "contrite"],
    "joy": ["joy", "happy", "delighted", "cheerful"],
    "no-emotion": ["neutral", "indifferent", "unmoved", "unaffected"],
    "pride": ["pride", "proud", "accomplished", "gratified"],
    "relief": ["relief", "relieved", "reassured", "unburdened"],
    "sadness": ["sadness", "sad", "sorrowful", "downcast"],
    "shame": ["shame", "ashamed", "humiliated", "mortified"],
    "surprise": ["surprise", "surprised", "astonished", "startled"],
    "trust": ["trust", "trusting", "confident", "assured"],
}


def load_rows():
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
    return texts, np.asarray(emo), np.asarray(app, dtype=np.float64)


def make_ridge(Xf, Xi):
    """Ridge directions sharing one decomposition of the training rows.

    The design matrix is the same for every target, so its SVD is taken once; computing it per
    target cost a 2600-by-d decomposition thirty-four times per model.
    """
    U, S, Vt = np.linalg.svd(Xf, full_matrices=False)

    def fit(yf, yi):
        ym = yf.mean()
        best, bw = -np.inf, None
        for lam in LAMBDAS:
            w = Vt.T @ ((S / (S ** 2 + lam)) * (U.T @ (yf - ym)))
            ss = 1.0 - float(((yi - ym - Xi @ w) ** 2).sum()) / max(
                float(((yi - yi.mean()) ** 2).sum()), 1e-12)
            if ss > best:
                best, bw = ss, w
        return ic.unit(bw), float(best)

    return fit


def js(p, q):
    m = 0.5 * (p + q)
    def kl(x, y):
        mk = x > 0
        return float((x[mk] * np.log(x[mk] / np.maximum(y[mk], 1e-30))).sum())
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--budget", type=float, default=0.05)
    ap.add_argument("--m-f5", type=int, default=None, dest="m_f5",
                    help="unique F5 draws per target; amendment 94 CM6 raises this from 10")
    ap.add_argument("--m-f4", type=int, default=None, dest="m_f4")
    ap.add_argument("--big-test", action="store_true",
                    help="score on 256 unused rows drawn after the original test block, "
                         "with the rest of the procedure frozen (amendment 91 CJ6)")
    ap.add_argument("--families", default="emotion,appraisal_raw")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    global M_F5, M_F4
    if a.m_f5:
        M_F5 = a.m_f5
    if a.m_f4 is not None:
        M_F4 = a.m_f4

    tail = (f"_m{M_F5}" if M_F5 != 10 else "") + ("_bigtest" if a.big_test else "")

    if abs(float(a.budget) - 0.05) > 1e-12:

        tail += f"_b{a.budget}"
    texts, emo, app = load_rows()
    classes = sorted(set(emo)); n_cls, n = len(classes), len(texts)
    layer = int(a.tag.rpartition("_L")[2])

    # one partition, checked disjoint: amendment 83 CB5
    perm = rng.permutation(n)
    i_fit = perm[:N_TRAIN]
    i_inner = perm[N_TRAIN:N_TRAIN + N_INNER]
    i_sel = perm[N_TRAIN + N_INNER:N_TRAIN + N_INNER + N_SEL]
    _t0 = N_TRAIN + N_INNER + N_SEL
    if a.big_test:
        # frozen protocol, fresh rows: the 256 immediately after the original test block
        i_test = perm[_t0 + N_TEST:_t0 + N_TEST + 256]
    else:
        i_test = perm[_t0:_t0 + N_TEST]
    parts = {"fit": i_fit, "inner": i_inner, "sel": i_sel, "test": i_test}
    for k1 in parts:
        for k2 in parts:
            if k1 < k2 and set(parts[k1]) & set(parts[k2]):
                raise SystemExit(f"splits overlap: {k1} ∩ {k2}")
    i_train = np.concatenate([i_fit, i_inner])
    print(f"layer L{layer} / split fit={len(i_fit)} inner={len(i_inner)} "
          f"sel={len(i_sel)} test={len(i_test)} / disjointness checked", flush=True)

    X = np.load(CACHE / f"H_{a.tag}.npy").astype(np.float64)
    mu, sd = X[i_train].mean(0), X[i_train].std(0) + 1e-8
    Xs = (X - mu) / sd
    d = Xs.shape[1]

    # eigenbasis of the training activations only
    Xc = Xs[i_train] - Xs[i_train].mean(0)
    _, Sv, Vt = np.linalg.svd(Xc, full_matrices=False)
    lam = ((Sv ** 2) / (len(i_train) - 1)).astype(np.float64)
    Q = Vt.astype(np.float32)
    del Xc, Vt
    P = Q[:64].astype(np.float64)
    print(f"  d={d} eigenbasis {Q.shape[0]}  eigenvalue ratio {lam[0]/max(lam[-1],1e-30):.2e}", flush=True)

    def act_var(v):
        c = (Q @ v.astype(np.float32)).astype(np.float64)
        return float((lam * c ** 2).sum())

    def floor_F5(v):
        """Sign flips in the eigenbasis; the null-space part is redrawn at the same norm."""
        v32 = v.astype(np.float32)
        c = Q @ v32
        res = v32 - Q.T @ c
        rn = float(np.linalg.norm(res))
        c = c * rng.choice(np.float32([-1.0, 1.0]), size=len(c))
        out = Q.T @ c
        if rn > 1e-8:
            r = rng.standard_normal(d).astype(np.float32)
            r = r - Q.T @ (Q @ r)
            out = out + r * (rn / (float(np.linalg.norm(r)) + 1e-12))
        return out.astype(np.float64)

    def floor_F4(v):
        return ic.floor_F4(v, P, ic.k_for_coverage(v, P), rng)

    # directions, fitted on training rows only
    Xf, Xi = Xs[i_fit], Xs[i_inner]
    ridge = make_ridge(Xf, Xi)
    fams = {}
    want = set(a.families.split(","))
    if "emotion" in want:
        V, r2 = [], []
        for c in classes:
            y = (emo == c).astype(np.float64)
            w, s = ridge(y[i_fit], y[i_inner]); V.append(w); r2.append(s)
        fams["emotion"] = np.stack(V)
        print(f"  emotion directions {len(V)}  inner R2 median {np.median(r2):+.3f}", flush=True)
    if "appraisal_raw" in want:
        V, r2 = [], []
        for j in range(len(APPRAISALS)):
            w, s = ridge(app[i_fit, j], app[i_inner, j]); V.append(w); r2.append(s)
        A_raw = np.stack(V)
        fams["appraisal_raw"] = A_raw
        print(f"  appraisal directions {len(V)}  inner R2 median {np.median(r2):+.3f} "
              f"R2>0.1  in  {sum(x > 0.1 for x in r2)}/{len(r2)}", flush=True)
    if "appraisal_iso" in want:
        V = []
        for i in range(len(A_raw)):
            others = np.stack([A_raw[j] for j in range(len(A_raw)) if j != i])
            q, _ = np.linalg.qr(others.T)
            V.append(ic.unit(A_raw[i] - q @ (q.T @ A_raw[i])))
        fams["appraisal_iso"] = np.stack(V)
    if "pc" in want:
        fams["pc"] = np.stack([ic.unit(P[i]) for i in range(len(APPRAISALS))])

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.float16, device_map="cuda:0", low_cpu_mem_usage=True)
    model.eval()

    def first_id(w):
        """First token that carries characters.

        A SentencePiece tokenizer can emit a bare word-boundary piece before the word, and
        Phi-3 does: " anger" starts with id 29871, which decodes to nothing and is the same for
        every class. Taking cc[0] therefore gave all thirteen classes one identical readout
        coordinate, which centring then sent to zero -- the "degenerate model" of amendments 80
        and 81 was this, not the model.
        """
        for form in (" " + w, w):
            for t in tok.encode(form, add_special_tokens=False):
                if tok.decode([t]).strip():
                    return int(t)
        raise SystemExit(f"cannot tokenise word: {w}")

    def build(words):
        raw = [[first_id(w) for w in ws] for ws in words]
        owner = {}
        for gi, g in enumerate(raw):
            for t in dict.fromkeys(g):
                owner.setdefault(t, set()).add(gi)
        shared = sorted({t for t, gs in owner.items() if len(gs) > 1})
        groups = [[t for t in dict.fromkeys(g) if t not in shared] for g in raw]
        for c, g in zip(classes, groups):
            if not g:
                raise SystemExit(f"empty readout for class: {c}")
        return groups, shared

    G = {"single": build([[SYNS[c][0]] for c in classes]),
         "syn": build([SYNS[c] for c in classes])}
    for nm, (groups, shared) in G.items():
        print(f"  readout {nm}: " + " ".join(f"{c}={len(g)}" for c, g in zip(classes, groups))
              + f" / shared removed {len(shared)}", flush=True)
    ids = sorted({t for groups, _ in G.values() for g in groups for t in g})
    iv = ic.Intervener(model, tok, layer, ids)

    p_sel = [PROMPT.format(text=texts[i]) for i in i_sel]
    p_test = [PROMPT.format(text=texts[i]) for i in i_test]
    p_cal = p_sel[:N_CALIB]
    base_sel = iv.next_token_probs(p_sel)
    base_test = iv.next_token_probs(p_test)
    base_cal = base_sel[:N_CALIB]
    T = np.eye(n_cls) - 1.0 / n_cls
    alpha_hint = [None]

    def calib(v):
        def pert(al):
            q = iv.next_token_probs(p_cal, v * al)
            return float(np.mean([js(base_cal[i], q[i]) for i in range(len(p_cal))]))
        # seeded from the previous direction's alpha, then bisected to the same tolerance
        if alpha_hint[0] is None:
            lo, hi = 1e-3, 1e3
        else:
            lo, hi = alpha_hint[0] / 8.0, alpha_hint[0] * 8.0
            for _ in range(6):
                if pert(lo) < a.budget:
                    break
                lo /= 8.0
            for _ in range(6):
                if pert(hi) >= a.budget:
                    break
                hi *= 8.0
        for _ in range(8):
            if pert(hi) >= a.budget:
                break
            hi *= 4
        for _ in range(6):
            mid = float(np.sqrt(lo * hi))
            if pert(mid) < a.budget:
                lo = mid
            else:
                hi = mid
        al = float(np.sqrt(lo * hi))
        alpha_hint[0] = al
        return al

    def measure(v):
        al = calib(v)
        out = {nm: [] for nm in G}
        for prompts, base in ((p_sel, base_sel), (p_test, base_test)):
            acc = {nm: [] for nm in G}
            for s in (+1.0, -1.0):
                q = iv.next_token_probs(prompts, v * (s * al))
                rr = {nm: [] for nm in G}
                for i in range(len(prompts)):
                    for nm, (groups, _) in G.items():
                        dp = np.array([float(q[i, g].sum() - base[i, g].sum()) for g in groups])
                        dp = dp - dp.mean(); nr = np.linalg.norm(dp)
                        rr[nm].append(np.zeros(n_cls) if nr < 1e-12 else (T @ dp) / nr)
                for nm in G:
                    acc[nm].append(np.mean(rr[nm], axis=0))
            for nm in G:
                out[nm].append(0.5 * (acc[nm][0] - acc[nm][1]))
        return {nm: (out[nm][0], out[nm][1]) for nm in G}

    # ---- measurement ----------------------------------------------------------------
    data = {}   # family -> readout -> ("tgt"|"F5"|"F4") -> array
    vr = {}     # family -> variance-ratio diagnostics
    for fn, M in fams.items():
        tg = {nm: ([], []) for nm in G}
        fl = {("F5", nm): [] for nm in G}
        fl.update({("F4", nm): [] for nm in G})
        ratios = {"F5": [], "F4": []}
        for ti, v in enumerate(M):
            v = ic.unit(v)
            tv = act_var(v)
            r = measure(v)
            for nm in G:
                tg[nm][0].append(r[nm][0]); tg[nm][1].append(r[nm][1])
            for kind, mm, fgen in (("F5", M_F5, floor_F5), ("F4", M_F4, floor_F4)):
                rows = {nm: [] for nm in G}
                for _ in range(mm):
                    f = fgen(v)
                    ratios[kind].append(act_var(f) / max(tv, 1e-30))
                    rf = measure(ic.unit(f) if kind == "F4" else f)
                    for nm in G:
                        rows[nm].append((rf[nm][0], rf[nm][1]))
                for nm in G:
                    fl[(kind, nm)].append(rows[nm])
            print(f"    {fn} {ti+1}/{len(M)} done", flush=True)
        # floor profiles as plain arrays, indexed (target, draw, sel/test, class)
        data[fn] = {}
        for nm in G:
            entry = {"tgt": (np.stack(tg[nm][0]), np.stack(tg[nm][1]))}
            for kind, mm in (("F5", M_F5), ("F4", M_F4)):
                arr = np.zeros((len(M), mm, 2, n_cls))
                for ti, row in enumerate(fl[(kind, nm)]):
                    for mi, (sp, hp) in enumerate(row):
                        arr[ti, mi, 0] = sp; arr[ti, mi, 1] = hp
                entry[kind] = arr
            data[fn][nm] = entry
        vr[fn] = {k: [float(np.median(v)), float(np.quantile(v, .05)),
                      float(np.quantile(v, .95)), float(np.max(np.abs(np.array(v) - 1)))]
                  for k, v in ratios.items() if v}
        print(f"  family {fn}: targets {len(M)}  / floor F5 {M_F5}/targets F4 {M_F4}/targets", flush=True)

    # ---- save the raw measurements -------------------------------------------------
    # Statistics are computed by c3stats.py from this file, so a statistic can be revised
    # without spending the GPU again. The earlier version stored only summaries, and a defect
    # in the global-count null could not be fixed without remeasuring.
    arrs, meta = {}, {}
    for fn in fams:
        for ro in G:
            e = data[fn][ro]
            arrs[f"{fn}|{ro}|tgt_sel"] = e["tgt"][0]
            arrs[f"{fn}|{ro}|tgt_test"] = e["tgt"][1]
            arrs[f"{fn}|{ro}|F5"] = e["F5"]
            arrs[f"{fn}|{ro}|F4"] = e["F4"]
    meta = {"model": a.model, "tag": a.tag, "layer": layer, "budget": a.budget, "d": d,
            "split": {k: [int(x) for x in v] for k, v in parts.items()},
            "m_f5": M_F5, "m_f4": M_F4, "big_test": bool(a.big_test), "classes": classes,
            "families": list(fams), "readouts": list(G),
            "variance_ratio": vr,
            "readout_ids": {nm: {c: [int(t) for t in g]
                                 for c, g in zip(classes, G[nm][0])} for nm in G},
            "shared_tokens_dropped": {nm: [int(t) for t in G[nm][1]] for nm in G}}
    np.savez_compressed(RES / f"raw_{a.tag}{tail}.npz", **arrs)
    (RES / f"meta_{a.tag}{tail}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    for fn in fams:
        for ro in G:
            ts, th = data[fn][ro]["tgt"]
            f5 = data[fn][ro]["F5"]
            best = [float(th[int(np.argmax(ts[:, e])), e]) for e in range(n_cls)]
            fmax = [float(np.quantile(f5[:, :, 1, e].ravel(), 0.95)) for e in range(n_cls)]
            print(f"  [preview {ro}] {fn:14s} above the per-target floor p95 "
                  f"{sum(b > m for b, m in zip(best, fmax))}/{n_cls}", flush=True)
    print(f"  raw data saved: raw_{a.tag}{tail}.npz", flush=True)
    iv.close()
    print("\n=== stage C3 done ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
