"""Stage A of the steering audit: reproduce the appraisal probes of Tak et al. (ACL 2025).

Their procedure, as described in arXiv:2502.05489: fit a linear regression per layer and per
appraisal from hidden states to the self-rated appraisal value, then isolate a single
appraisal with z_a = (I - P_-a) v_a before intervening.

This stage only fits the probes and reports held-out R^2, so nothing here is a verdict. The
intervention and the floor hierarchy come in stage B, after the layer rule is registered.

Deviations from the original are recorded in the output rather than smoothed over: the
prompt template is ours, probes are fit on all vignettes instead of the per-model subset of
correctly classified ones, and four of their ten models are gated.
"""
from __future__ import annotations

import argparse, csv, json, time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DATA = Path("/path/to/work/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv")
OUT = Path("/path/to/work/results/plan_b/audit_stageA")
SEED = 20261004

APPRAISALS = ["suddenness", "familiarity", "predict_event", "pleasantness", "unpleasantness",
              "goal_relevance", "chance_responsblt", "self_responsblt", "other_responsblt",
              "predict_conseq", "goal_support", "urgency", "self_control", "other_control",
              "chance_control", "accept_conseq", "standards", "social_norms",
              "attention", "not_consider", "effort"]
EMOTIONS = ["anger", "boredom", "disgust", "fear", "guilt", "joy", "pride",
            "relief", "sadness", "shame", "surprise", "trust"]
# their primary analysis intervenes at layer 9 of 16 in Llama 3.2 1B
DEPTHS = [0.40, 0.5625, 0.75]
PROMPT = ("Consider the following event description and the emotion of the person who "
          "experienced it.\n\nEvent: {text}\n\nThe emotion is")


def load_rows() -> tuple[list[str], np.ndarray, list[str]]:
    rows = list(csv.DictReader(open(DATA, encoding="utf-8"), delimiter="\t"))
    texts, Y, emo = [], [], []
    for r in rows:
        t = (r.get("generated_text") or "").strip()
        if not t:
            continue
        try:
            y = [float(r[a]) for a in APPRAISALS]
        except (KeyError, ValueError):
            continue
        texts.append(t)
        Y.append(y)
        emo.append(r.get("emotion", ""))
    return texts, np.asarray(Y, dtype=np.float64), emo


@torch.no_grad()
def hidden_at(model, tok, texts, layers, bs=16) -> dict[int, np.ndarray]:
    store = {L: [] for L in layers}
    for i in range(0, len(texts), bs):
        batch = [PROMPT.format(text=t) for t in texts[i:i + bs]]
        enc = tok(batch, return_tensors="pt", padding=True, truncation=True,
                  max_length=256).to(model.device)
        hs = model(**enc, output_hidden_states=True).hidden_states
        # last real token of each sequence, so padding never leaks in
        last = enc["attention_mask"].sum(1) - 1
        for L in layers:
            h = hs[L]
            store[L].append(h[torch.arange(h.shape[0], device=h.device), last].float().cpu().numpy())
        if (i // bs) % 25 == 0:
            print(f"    {i}/{len(texts)}", flush=True)
    return {L: np.concatenate(v) for L, v in store.items()}


def ridge_probe(X: np.ndarray, y: np.ndarray, tr, te, lam=1.0) -> tuple[np.ndarray, float]:
    Xtr, Xte = X[tr], X[te]
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-8
    Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
    ym = y[tr].mean()
    w = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(X.shape[1]), Xtr.T @ (y[tr] - ym))
    pred = Xte @ w + ym
    ss_res = float(((y[te] - pred) ** 2).sum())
    ss_tot = float(((y[te] - y[te].mean()) ** 2).sum())
    return w / (np.linalg.norm(w) + 1e-12), 1.0 - ss_res / max(ss_tot, 1e-12)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    texts, Y, emo = load_rows()
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(texts))
    ntr = int(0.8 * len(texts))
    tr, te = perm[:ntr], perm[ntr:]
    print(f"刺激 {len(texts)} / 評価次元 {Y.shape[1]} / 学習 {len(tr)} 評価 {len(te)}", flush=True)

    meta_path = OUT / "stageA.json"
    res = json.loads(meta_path.read_text()) if meta_path.exists() else {"models": {}}
    res["n_stimuli"] = len(texts)
    res["appraisals"] = APPRAISALS
    res["deviations"] = [
        "プロンプトは本研究のもの。原著のテンプレートは未確認",
        "原著はモデルごとに正しく分類された部分集合で学習。本研究は全刺激で学習",
        "原著10モデル中4モデル（Llama 3.2 1B/3.1 8B, Gemma 2 2B/9B）はゲート付きで未入手",
    ]

    for mid in a.models:
        if mid in res["models"] and res["models"][mid].get("status") == "ok":
            print(f"済 {mid}", flush=True); continue
        t0 = time.time()
        try:
            tok = AutoTokenizer.from_pretrained(mid)
            if tok.pad_token is None:
                tok.pad_token = tok.eos_token
            tok.padding_side = "right"
            model = AutoModelForCausalLM.from_pretrained(
                mid, dtype=torch.float16, device_map="cuda:0", low_cpu_mem_usage=True)
            model.eval()
            n = model.config.num_hidden_layers
            layers = sorted({max(1, min(n, int(round(d * n)))) for d in DEPTHS})
            print(f"  {mid}: 層数{n} -> {layers}", flush=True)
            H = hidden_at(model, tok, texts, layers)
            entry = {"status": "ok", "n_layers": n, "layers": layers,
                     "d": int(H[layers[0]].shape[1]), "r2": {}}
            for L in layers:
                X = H[L]
                V, r2 = [], {}
                for k, name in enumerate(APPRAISALS):
                    w, s = ridge_probe(X, Y[:, k], tr, te)
                    V.append(w); r2[name] = round(s, 4)
                np.save(OUT / f"V_{mid.replace('/', '__')}_L{L}.npy", np.stack(V))
                np.save(OUT / f"H_{mid.replace('/', '__')}_L{L}.npy", X.astype(np.float16))
                entry["r2"][str(L)] = r2
                good = sum(v > 0.1 for v in r2.values())
                print(f"    L{L}: R^2>0.1 の評価次元 {good}/21  中央 "
                      f"{np.median(list(r2.values())):.3f}  最大 {max(r2.values()):.3f}", flush=True)
            entry["seconds"] = time.time() - t0
            res["models"][mid] = entry
            print(f"OK {mid} {time.time()-t0:.0f}s", flush=True)
        except Exception as e:
            res["models"][mid] = {"status": "failed", "error": f"{type(e).__name__}: {e}"[:300]}
            print(f"NG {mid}: {type(e).__name__}: {str(e)[:150]}", flush=True)
        finally:
            try:
                del model
            except Exception:
                pass
            torch.cuda.empty_cache()
            meta_path.write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print("=== 段A 終了 ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
