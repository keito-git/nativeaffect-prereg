"""Control SP-act of amendment 96: match decodability from above, not from the side.\n\nLexical clustering cannot reach the emotion partition's decodability -- two hundred candidates\nper model topped out near 0.88 against the emotion partition's 0.95 -- so a band-matched\ncomparison is unobtainable there. Clustering the activations themselves overshoots instead,\nand a comparison partition is used only if its held-out probe quality is at least the emotion\npartition's. The comparison is therefore deliberately favoured: if the emotion partition still\nwins on intervention, decodability cannot be what is doing the work. The emotion labels never\nenter the construction.\n\nOriginal header follows.\n\nControl SP of amendment 91 CJ3: is it the emotion partition, or any predictable partition?

Control LP compared the emotion partition against random relabellings, which the emotion
partition beats. But a random relabelling is also far less predictable from the text than the
emotion labels are, so "it is the emotion partition" and "it is a predictable partition" are
not separated by that comparison. Here the comparison partitions come from clustering the
stimuli on their own character n-grams -- lexical structure, not model activations -- at the
same class sizes, and a draw is used only if its held-out probe quality lands within a fixed
band of the emotion partition's. The achieved band is reported, as is the number of draws
rejected.

Original header follows.

Control LP of amendment 89: is it the human emotion partition, or any partition of that grain?

A direction fitted to separate thirteen classes will move a thirteen-way readout over those
same classes, whatever the classes are. So the emotion family is compared not against random
directions but against families fitted the identical way to random partitions of the training
stimuli with the identical class sizes. Everything -- readout, targets, budget, estimator,
selection and scoring contexts -- is held fixed; only the provenance of the labels differs,
which is why the readout-quality confound of amendment 89 cannot reach this comparison.

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
RES = Path(_ROOT + "/results/plan_b/stageSPact")
DATA = Path(_ROOT + "/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261007
N_TRAIN, N_INNER, N_SEL, N_TEST = 2600, 650, 32, 32
N_CALIB, N_BOOT = 12, 2000
N_PART = 30
AUC_BAND = 0.05
MIN_ACCEPT = 10   # amendment 97 CP3: below this the null variance collapses
MAX_TRIES = 2000   # amendment 97 CP3: wider search, same rule
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
    ap.add_argument("--max-tries", type=int, default=None)
    ap.add_argument("--search-only", action="store_true")
    ap.add_argument("--labels", default=None)
    ap.add_argument("--shard", default=None)
    ap.add_argument("--n-part", type=int, default=None, dest="n_part",
                    help="comparison partitions; amendments 91 CJ4 / 91 CJ3")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    global N_PART, MAX_TRIES
    if a.max_tries:
        MAX_TRIES = a.max_tries
    if a.n_part:
        N_PART = a.n_part

    tail = f"_p{N_PART}" if N_PART != 30 else ""
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
    V, r2 = [], []
    for c in classes:
        y = (emo == c).astype(np.float64)
        w, sc = ridge(y[i_fit], y[i_inner]); V.append(w); r2.append(sc)
    E = np.stack(V)
    sizes = np.array([int((emo[i_train] == c).sum()) for c in classes])
    print(f"  emotion directions {len(E)}  inner R2 median {np.median(r2):+.3f} / "
          f"class sizes {sizes.min()}-{sizes.max()}", flush=True)

    def probe_auc(y_all):
        """Median held-out AUC of ridge probes for a partition, on the inner rows."""
        aucs = []
        for ci in range(len(classes)):
            w, _ = ridge(y_all[ci][i_fit], y_all[ci][i_inner])
            sc_ = Xs[i_inner] @ w
            pos, neg = sc_[y_all[ci][i_inner] > 0], sc_[y_all[ci][i_inner] == 0]
            if len(pos) == 0 or len(neg) == 0:
                return None, None
            aucs.append(float((pos[:, None] > neg[None, :]).mean()
                              + 0.5 * (pos[:, None] == neg[None, :]).mean()))
        return float(np.median(aucs)), aucs

    def onehot(lab):
        y = np.zeros((len(classes), len(texts)))
        for ci in range(len(classes)):
            y[ci, i_train] = (lab == ci).astype(np.float64)
        return y

    # lexical features of the stimuli: the model's activations play no part here
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.cluster import KMeans
    FEAT = {}

    def lexical_space(ngram, dims, seed):
        key = (ngram, dims)
        if key not in FEAT:
            tv = TfidfVectorizer(analyzer="char_wb", ngram_range=ngram, min_df=3,
                                 max_features=60000, sublinear_tf=True)
            M_ = tv.fit_transform([texts[i] for i in i_train])
            FEAT[key] = TruncatedSVD(n_components=dims, random_state=0).fit_transform(M_)
        return FEAT[key]

    def size_match(lab, sizes, rng):
        """Move members between clusters until the class sizes match the emotion partition."""
        lab = lab.copy()
        for _ in range(60):
            cnt = np.array([(lab == ci).sum() for ci in range(len(classes))])
            d_ = cnt - sizes
            if not d_.any():
                break
            over = int(np.argmax(d_)); under = int(np.argmin(d_))
            if d_[over] <= 0 or d_[under] >= 0:
                break
            idx = np.flatnonzero(lab == over)
            take = rng.permutation(idx)[:min(int(d_[over]), int(-d_[under]))]
            lab[take] = under
        return lab

    def activation_partition(rng):
        """A size-matched partition from k-means on the training activations."""
        dims = int(rng.choice([16, 32, 64, 128]))
        Z = Xs[i_train][:, :0]  # placeholder, replaced below
        key = ("act", dims)
        if key not in FEAT:
            Xc_ = Xs[i_train] - Xs[i_train].mean(0)
            FEAT[key] = TruncatedSVD(n_components=dims, random_state=0).fit_transform(Xc_)
        Z = FEAT[key]
        km = KMeans(n_clusters=len(classes), n_init=3,
                    random_state=int(rng.integers(0, 10 ** 6))).fit(Z)
        return size_match(km.labels_.astype(int), sizes, rng), dims

    def structured_partition(rng):
        """A size-matched partition of the training rows from lexical clusters.

        Pure clusters are usually more decodable from activations than the emotion labels are,
        so a fraction of rows is reassigned at random to tune the decodability downwards. The
        knob never touches the emotion labels, so the comparison partitions stay independent of
        the thing being tested.
        """
        ngram = (2, 4) if rng.random() < 0.5 else (3, 5)
        dims = int(rng.choice([30, 60, 120]))
        Z = lexical_space(ngram, dims, 0)
        km = KMeans(n_clusters=len(classes), n_init=3,
                    random_state=int(rng.integers(0, 10 ** 6))).fit(Z)
        lab = km.labels_.astype(int)
        noise = float(rng.choice([0.0, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8]))
        if noise > 0:
            pick = rng.permutation(len(lab))[: int(noise * len(lab))]
            lab[pick] = rng.integers(0, len(classes), size=len(pick))
        return size_match(lab, sizes, rng), ngram, dims, noise

    def partition_family():
        """Thirteen directions fitted to a random relabelling with the same class sizes."""
        lab = np.empty(len(i_train), dtype=int)
        order = rng.permutation(len(i_train))
        at = 0
        for ci, sz in enumerate(sizes):
            lab[order[at:at + sz]] = ci
            at += sz
        if at < len(i_train):
            lab[order[at:]] = rng.integers(0, len(classes), size=len(i_train) - at)
        y_all = np.zeros((len(classes), len(texts)))
        for ci in range(len(classes)):
            y_all[ci, i_train] = (lab == ci).astype(np.float64)
        out = []
        for ci in range(len(classes)):
            w, _ = ridge(y_all[ci][i_fit], y_all[ci][i_inner])
            out.append(w)
        return np.stack(out)

    if a.search_only:
        # Amendment 107: the search needs activations and probes only, never a forward pass.
        # The acceptance rule and the proposal call the same functions as the main path.
        emo_auc0, _ = probe_auc(onehot(np.array([classes.index(c) for c in emo[i_train]])))
        print(f"  emotion partition held-out AUC median {emo_auc0:.4f}", flush=True)
        rng_s = np.random.default_rng(SEED + (int(a.shard) if a.shard else 0))
        acc_lab, acc_auc, seen, tried0 = [], [], [], 0
        while len(acc_lab) < N_PART and tried0 < MAX_TRIES:
            tried0 += 1
            lab0, dims0 = activation_partition(rng_s)
            au0, _ = probe_auc(onehot(lab0))
            if au0 is None:
                continue
            seen.append(round(au0, 4))
            if au0 >= emo_auc0:
                acc_lab.append(lab0.astype(np.int16)); acc_auc.append(round(au0, 4))
                print(f"  accepted {len(acc_lab)}/{N_PART} (AUC {au0:.4f}, tried {tried0})", flush=True)
        outp = RES / f"search_{a.tag}{'_' + a.shard if getattr(a, 'shard', None) else ''}.npz"
        RES.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(outp, labels=np.array(acc_lab, dtype=np.int16) if acc_lab
                            else np.zeros((0, len(emo[i_train])), dtype=np.int16),
                            aucs=np.array(acc_auc), seen=np.array(seen),
                            tried=np.array([tried0]), emo_auc=np.array([emo_auc0]))
        print(f"  search only, done: accepted {len(acc_lab)} / tried {tried0} -> {outp.name}", flush=True)
        return 0

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

    # ---- measurement ---------------------------------------------------------------
    def family_profiles(M):
        ss, hh = [], []
        for v in M:
            r = measure(ic.unit(v))
            ss.append({nm: r[nm][0] for nm in G}); hh.append({nm: r[nm][1] for nm in G})
        return ss, hh

    es, eh = family_profiles(E)
    print("  emotion family measured", flush=True)
    # the emotion partition's own probe quality sets the band the comparisons must land in
    emo_auc, _ = probe_auc(onehot(np.array([classes.index(c) for c in emo[i_train]])))
    print(f"  emotion partition held-out AUC median {emo_auc:.4f}"
          f" (the control must reach at least this)", flush=True)

    accepted, tried, aucs_acc, specs, seen_auc = [], 0, [], [], []
    if a.labels:
        # Amendment 107: load the partitions found by the parallel search; the directions are rebuilt from the labels deterministically.
        z0 = np.load(a.labels)
        for lab0, au0 in zip(z0["labels"], z0["aucs"]):
            y0 = onehot(lab0.astype(int))
            accepted.append(np.stack([ridge(y0[ci][i_fit], y0[ci][i_inner])[0]
                                      for ci in range(len(classes))]))
            aucs_acc.append(float(au0)); specs.append({"auc": float(au0)})
        tried = int(z0["tried"][0]); seen_auc = [float(x) for x in z0["seen"]]
        print(f"  loaded stored accepted partitions: {len(accepted)}  (tried {tried})", flush=True)
    while len(accepted) < N_PART and tried < MAX_TRIES and not a.labels:
        tried += 1
        lab, dims = activation_partition(rng)
        y_all = onehot(lab)
        au, _ = probe_auc(y_all)
        if au is None:
            continue
        seen_auc.append(round(au, 4))
        if au >= emo_auc:
            V2 = []
            for ci in range(n_cls):
                w, _ = ridge(y_all[ci][i_fit], y_all[ci][i_inner])
                V2.append(w)
            accepted.append(np.stack(V2)); aucs_acc.append(au)
            specs.append({"dims": dims, "auc": round(au, 4)})
            print(f"  accepted {len(accepted)}/{N_PART} (AUC {au:.4f}, tried {tried})", flush=True)
    if seen_auc:
        print(f"  candidate partition AUC range {min(seen_auc):.4f}-{max(seen_auc):.4f}"
              f" ({len(seen_auc)} evaluated)", flush=True)
    if len(accepted) < N_PART:
        print(f"  warning: {tried} tries yielded only {len(accepted)} accepted", flush=True)
    if len(accepted) < MIN_ACCEPT:
        # Amendment 97 CP4: with too few comparison partitions the null has no spread, so the
        # standardised excess diverges and the p-value pins at 0.5. The model is recorded as
        # unmeasurable rather than judged; the accepted count and the candidate range are kept.
        (RES / f"SPact_{a.tag}.json").write_text(json.dumps(
            {"model": a.model, "tag": a.tag, "layer": layer,
             "emotion_probe_auc": round(emo_auc, 4), "n_part": len(accepted),
             "n_tried": tried, "min_accept": MIN_ACCEPT,
             "candidate_auc_seen": seen_auc, "accepted_specs": specs,
             "measurable": False,
             "reason": "accepted partitions below MIN_ACCEPT; null variance degenerate"},
            indent=2, ensure_ascii=False))
        print(f"  unmeasurable: accepted {len(accepted)}  < {MIN_ACCEPT} 。"
              f"candidate AUC {min(seen_auc):.4f}-{max(seen_auc):.4f} ({len(seen_auc)} evaluated)",
              flush=True)
        iv.close()
        return 0

    null = {nm: np.zeros((len(accepted), n_cls)) for nm in G}
    for s_i, M2 in enumerate(accepted):
        ps, ph = family_profiles(M2)
        for nm in G:
            sel_m = np.stack([p[nm] for p in ps]); hel_m = np.stack([p[nm] for p in ph])
            for e in range(n_cls):
                null[nm][s_i, e] = float(hel_m[int(np.argmax(sel_m[:, e])), e])
        print(f"  structure-matched partition family {s_i+1}/{len(accepted)}", flush=True)

    out = {"model": a.model, "tag": a.tag, "layer": layer, "budget": a.budget, "d": d,
           "split": {k: int(len(v)) for k, v in parts.items()},
           "n_part": len(accepted), "n_tried": tried, "rule": "auc >= emotion",
           "min_accept": MIN_ACCEPT, "measurable": True,
           "emotion_probe_auc": round(emo_auc, 4),
           "accepted_auc_median": round(float(np.median(aucs_acc)), 4),
           "accepted_auc_range": [round(min(aucs_acc), 4), round(max(aucs_acc), 4)],
           "accepted_specs": specs, "candidate_auc_seen": seen_auc,
           "classes": classes, "class_sizes": sizes.tolist(),
           "inner_r2_median": round(float(np.median(r2)), 4), "results": {}}
    arrs = {}
    for nm in G:
        sel_e = np.stack([p[nm] for p in es]); hel_e = np.stack([p[nm] for p in eh])
        obs = np.array([float(hel_e[int(np.argmax(sel_e[:, e])), e]) for e in range(n_cls)])
        arrs[f"{nm}|obs"] = obs
        arrs[f"{nm}|null"] = null[nm]
        arrs[f"{nm}|emotion_sel"] = sel_e
        arrs[f"{nm}|emotion_test"] = hel_e
        q95 = np.quantile(null[nm], 0.95, axis=0)
        mu, sd = null[nm].mean(0), null[nm].std(0) + 1e-12
        cnt = int((obs > q95).sum())
        zo = float(((obs - mu) / sd).sum())
        zn = ((null[nm] - mu[None, :]) / sd[None, :]).sum(1)
        p_g = float((1 + (zn >= zo).sum()) / (1 + len(zn)))
        out["results"][nm] = {
            "count_vs_activation_partitions": f"{cnt}/{n_cls}",
            "median_excess_sd": round(float(np.median((obs - mu) / sd)), 3),
            "G_obs": round(zo, 2), "p_G": round(p_g, 5),
            "pass": bool(cnt > n_cls // 2 and p_g < 0.05),
            "null_sd_min": round(float(null[nm].std(0).min()), 6),
        }
        r = out["results"][nm]
        print(f"  [SPact {nm}] comparison partitions {len(accepted)} against "
              f"{r['count_vs_activation_partitions']} "
              f"({r['median_excess_sd']:+.2f}SD) G={r['G_obs']:.1f} p={r['p_G']:.4f} "
              f"{'pass' if r['pass'] else 'fail'}", flush=True)
    np.savez_compressed(RES / f"rawSPact_{a.tag}.npz", **arrs)
    (RES / f"SPact_{a.tag}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    iv.close()
    print("\n=== stage C3 done ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
