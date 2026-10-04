"""Stage B0 from preregistration amendment 53 BB7: the kill switch before spending GPU on X3.

X3 maps an appraisal direction estimated in one model into another model and asks whether it
still steers. That is only worth running if the two models agree about the appraisals in the
first place. Amendment 50 already found no cross-model agreement at the emotion-category
level, so this checks the continuous appraisal predictions instead, which is a different
question.

Agreement is measured on the held-out rows only, between each model's probe predictions, and
compared against a null that permutes the rows. Nothing here intervenes on a model.
"""
from __future__ import annotations

import csv, json
from itertools import combinations
from pathlib import Path

import numpy as np

OUT = Path("/path/to/work/results/plan_b/audit_stageA")
DATA = Path("/path/to/work/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
SEED = 20261004
N_NULL = 500
APPRAISALS = ["suddenness", "familiarity", "predict_event", "pleasantness", "unpleasantness",
              "goal_relevance", "chance_responsblt", "self_responsblt", "other_responsblt",
              "predict_conseq", "goal_support", "urgency", "self_control", "other_control",
              "chance_control", "accept_conseq", "standards", "social_norms",
              "attention", "not_consider", "effort"]


def load_Y() -> np.ndarray:
    Y = []
    for r in csv.DictReader(open(DATA, encoding="utf-8"), delimiter="\t"):
        if not (r.get("generated_text") or "").strip():
            continue
        try:
            Y.append([float(r[k]) for k in APPRAISALS])
        except (KeyError, ValueError):
            continue
    return np.asarray(Y, dtype=np.float64)


def main() -> int:
    Y = load_Y()
    n = len(Y)
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(n)
    ntr = int(0.8 * n)
    tr_all, te = perm[:ntr], perm[ntr:]
    nva = int(0.2 * len(tr_all))
    tr = tr_all[nva:]

    fit = json.loads((OUT / "stageA_refit.json").read_text())
    # one layer per model: the deepest fitted layer, fixed by rule, not by result
    by_model: dict[str, str] = {}
    for tag in fit:
        model, _, layer = tag.rpartition("_L")
        if model not in by_model or int(layer) > int(by_model[model].rpartition("_L")[2]):
            by_model[model] = tag
    print(f"モデル {len(by_model)}: " + ", ".join(sorted(by_model)), flush=True)

    # each model's held-out appraisal predictions, 21 columns
    P = {}
    for model, tag in sorted(by_model.items()):
        V = np.load(OUT / f"Vfit_{tag}.npy")
        X = np.load(OUT / f"H_{tag}.npy").astype(np.float64)
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
        P[model] = ((X[te] - mu) / sd) @ V.T
        print(f"  {model}: 予測 {P[model].shape}", flush=True)

    ids = sorted(P)
    def agree(M):
        out = {}
        for i, j in combinations(ids, 2):
            # per-appraisal correlation across held-out stimuli, averaged over appraisals
            cs = [float(np.corrcoef(M[i][:, k], M[j][:, k])[0, 1]) for k in range(len(APPRAISALS))]
            out[f"{i} vs {j}"] = float(np.nanmean(cs))
        return out

    obs = agree(P)
    null = []
    for _ in range(N_NULL):
        Pp = {k: v[rng.permutation(v.shape[0])] for k, v in P.items()}
        null += list(agree(Pp).values())
    null = np.asarray(null)
    nm, ns, p95 = float(np.nanmean(null)), float(np.nanstd(null)), float(np.nanquantile(null, 0.95))

    omin = min(obs.values())
    gap = omin - nm
    gate = ns > 0 and ns >= abs(gap) / 10.0
    verdict = ("判定不能（帰無の分散が小さすぎる）" if not gate
               else ("PASS（X3 を実施してよい）" if omin > p95 else "FAIL（X3 を実施しない）"))

    for k in sorted(obs):
        print(f"  {k:70s} {obs[k]:+.4f}", flush=True)
    print(f"\n帰無 平均{nm:+.4f} SD {ns:.4f} p95 {p95:+.4f}  健全性 {'OK' if gate else '不足'}", flush=True)
    print(f"最小一致 {omin:+.4f} -> 段B0 {verdict}", flush=True)

    (OUT / "stageB0.json").write_text(json.dumps({
        "prereg": "amendment 53 BB7 stage B0", "models": ids, "n_heldout": int(len(te)),
        "agreement": {k: round(v, 4) for k, v in sorted(obs.items())},
        "min_agreement": omin, "null_mean": nm, "null_sd": ns, "null_p95": p95,
        "null_health_ok": gate, "verdict": verdict,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
