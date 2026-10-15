"""Level 2 of amendment 77: is the subspace privileged, independently of its axes?

Level 3 asks whether the human axes beat matched random axes. A family can fail that and
still span a privileged subspace, because the best combination inside the span can move the
readout more than any single axis does -- max_i S(z_i) < S(sum_i a_i z_i) is ordinary. So the
optimal combination inside each human subspace is measured and compared against the optimal
combination inside subspaces matched to it direction by direction, drawn thirty times as the
preregistration fixed.

The coefficients come from a first-order expansion, whose validity is checked before any
judgement; the combination itself is always measured, never predicted.

Original header follows.

Judgement CMP rebuilt per amendments 82 and 83.

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
RES = Path(_ROOT + "/results/plan_b/stageL2")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261007
N_TRAIN, N_INNER, N_SEL, N_TEST = 2600, 650, 32, 32
N_CALIB, N_SUB, N_LIN = 12, 30, 20
BUDGET_LIN = 0.02
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
    ap.add_argument("--families", default="emotion,appraisal_raw")
    ap.add_argument("--readouts", default="single,syn")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    texts, emo, app = load_rows()
    classes = sorted(set(emo)); n_cls, n = len(classes), len(texts)
    layer = int(a.tag.rpartition("_L")[2])

    # one partition, checked disjoint: amendment 83 CB5
    perm = rng.permutation(n)
    i_fit = perm[:N_TRAIN]
    i_inner = perm[N_TRAIN:N_TRAIN + N_INNER]
    i_sel = perm[N_TRAIN + N_INNER:N_TRAIN + N_INNER + N_SEL]
    i_test = perm[N_TRAIN + N_INNER + N_SEL:N_TRAIN + N_INNER + N_SEL + N_TEST]
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

    _all = {"single": lambda: build([[SYNS[c][0]] for c in classes]),
            "syn": lambda: build([SYNS[c] for c in classes])}
    G = {k: _all[k]() for k in a.readouts.split(",")}
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

    # ---- L2: optimal combination inside the span ------------------------------------
    out = {"model": a.model, "tag": a.tag, "layer": layer, "budget": a.budget, "d": d,
           "split": {k: int(len(v)) for k, v in parts.items()},
           "n_sub": N_SUB, "classes": classes, "readouts": list(G), "results": {}, "ranks": {}}
    arrs = {}

    def ortho(M, tol=1e-8):
        """Orthonormal basis of the span, with the numerical rank reported.

        The thirteen category directions need not be independent -- centroid deviations sum to
        zero under the class proportions -- so the rank is printed rather than assumed.
        """
        U, S, _ = np.linalg.svd(np.asarray(M, dtype=np.float64).T, full_matrices=False)
        r = int((S > tol * S[0]).sum())
        return U[:, :r].T, r

    def basis_profiles(B):
        """S_e for every basis direction: (K, n_cls) on sel and on test."""
        ss, hh = [], []
        for u in B:
            r = measure(ic.unit(u))
            ss.append({nm: r[nm][0] for nm in G}); hh.append({nm: r[nm][1] for nm in G})
        return ss, hh

    def opt_dir(B, prof, nm, e):
        c = np.array([p[nm][e] for p in prof])
        return ic.unit(c @ B)

    for fn, M in fams.items():
        B, rank = ortho(M)
        out["ranks"][fn] = {"K": int(len(M)), "rank": rank}
        print(f"  family {fn}: directions {len(M)}  / rank of their span {rank}"
              + ("  ← linearly dependent" if rank < len(M) else ""), flush=True)

        # first-order validity, amendment 77 BZ2, before any judgement
        keep, a.budget = a.budget, BUDGET_LIN
        alpha_hint[0] = None   # the seeded bracket belongs to the other budget
        sel_prof, _ = basis_profiles(B)
        pred, obs = [], []
        for _ in range(N_LIN):
            c = rng.standard_normal(rank); c /= np.linalg.norm(c)
            r = measure(ic.unit(c @ B))
            for nm in G:
                p = np.array([sel_prof[i][nm] for i in range(rank)])
                pred.append(c @ p); obs.append(r[nm][0])
        pred = np.concatenate([x.ravel() for x in pred])
        obs = np.concatenate([x.ravel() for x in obs])
        corr = float(np.corrcoef(pred, obs)[0, 1])
        a.budget = keep
        alpha_hint[0] = None
        out["results"].setdefault(fn, {})["first_order_corr"] = round(corr, 4)
        out["results"][fn]["first_order_ok"] = bool(corr >= 0.8)
        print(f"    first-order approximation correlation {corr:+.3f} "
              f"({'pass, used for the coefficients' if corr >= 0.8 else 'fail, switching to coordinate descent'})", flush=True)
        use_linear = corr >= 0.8

        def coeffs(Bx, nm, e):
            """Coefficients on the selection contexts: first order, or coordinate descent."""
            pr, _ = CACHE_PROF[id(Bx)]
            if use_linear:
                return np.array([pr[i][nm][e] for i in range(len(Bx))])
            c = np.array([pr[i][nm][e] for i in range(len(Bx))])
            c = c / (np.linalg.norm(c) + 1e-12)
            best = measure(ic.unit(c @ Bx))[nm][0][e]
            for it in range(N_LIN):
                j = it % len(Bx)
                for step in (+0.3, -0.3):
                    t = c.copy(); t[j] += step; t /= np.linalg.norm(t) + 1e-12
                    v = measure(ic.unit(t @ Bx))[nm][0][e]
                    if v > best:
                        best, c = v, t
            return c

        CACHE_PROF = {}
        sel_prof, _ = basis_profiles(B)
        CACHE_PROF[id(B)] = (sel_prof, None)
        obs_val = {nm: np.zeros(n_cls) for nm in G}
        for nm in G:
            for e in range(n_cls):
                c = coeffs(B, nm, e)
                obs_val[nm][e] = measure(ic.unit(c @ B))[nm][1][e]
        print(f"    optimal combination in the human subspace {n_cls}  measureddone", flush=True)

        null = {nm: np.zeros((N_SUB, n_cls)) for nm in G}
        for s in range(N_SUB):
            BR, rr = ortho([floor_F5(ic.unit(u)) for u in B])
            pr, _ = basis_profiles(BR)
            CACHE_PROF[id(BR)] = (pr, None)
            for nm in G:
                for e in range(n_cls):
                    c = coeffs(BR, nm, e)
                    null[nm][s, e] = measure(ic.unit(c @ BR))[nm][1][e]
            print(f"    matched random subspace {s+1}/{N_SUB} (rank {rr})", flush=True)

        for nm in G:
            arrs[f"{fn}|{nm}|obs"] = obs_val[nm]
            arrs[f"{fn}|{nm}|null"] = null[nm]
            q95 = np.quantile(null[nm], 0.95, axis=0)
            mu, sd = null[nm].mean(0), null[nm].std(0) + 1e-12
            cnt = int((obs_val[nm] > q95).sum())
            zo = float(((obs_val[nm] - mu) / sd).sum())
            zn = ((null[nm] - mu[None, :]) / sd[None, :]).sum(1)
            out["results"][fn][nm] = {
                "count_vs_matched_subspace": f"{cnt}/{n_cls}",
                "median_excess_sd": round(float(np.median((obs_val[nm] - mu) / sd)), 3),
                "G_obs": round(zo, 2),
                "p_G": round(float((1 + (zn >= zo).sum()) / (1 + len(zn))), 5),
                "null_sd_min": round(float(null[nm].std(0).min()), 6),
            }
            r = out["results"][fn][nm]
            print(f"  [L2 {nm}] {fn:14s} matched-subspace optimum {r['count_vs_matched_subspace']:>5s} "
                  f"({r['median_excess_sd']:+.2f}SD) G={r['G_obs']:.1f} p={r['p_G']:.4f}",
                  flush=True)

    np.savez_compressed(RES / f"rawL2_{a.tag}.npz", **arrs)
    (RES / f"L2_{a.tag}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    iv.close()
    print("\n=== L2 done ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
