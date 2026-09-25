#!/usr/bin/env python3
"""CPU-only conditioning diagnostic for the human-affect subspace variants.

No GPU, no model: it reuses the already-extracted PAD-free E1 activations
(results/activations_nopad/.../layerNN_seed0042.npz, 300 x 2048) and the Warriner
norms.

Why this exists
---------------
Nomura's caution: enlarging the human subspace mechanically drives every axis's
residual towards zero, so "how many dimensions were added" is not the right
figure -- the effective rank and the residual norm ratio are. This script
measures those BEFORE any GPU time is spent, so we can tell whether the stricter
secondary test is informative or vacuous.

It also documents a degeneracy that rules out one candidate design: the
discovery set holds exactly ONE stimulus per emotion category (20 categories,
20 items), so one-vs-rest category directions fitted there span the entire row
space of the discovery activations and would remove essentially everything.

Variants compared, per layer:
  S1  V/A/D fitted on the 20 discovery E4 stimuli   (the pre-registered primary)
  S2  V/A/D fitted on the 300 E1 sentences          (same 3 dims, better conditioned)

For each: singular spectrum, effective rank at several tolerances, and the
residual norm ratio ||a - P a|| / ||a|| of each of the layer's top-3 axes.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

import numpy as np

BASE = Path("/path/to/work/results")
SLUG = "swiss-ai__Apertus-v1_1-1_5B"
ACT = BASE / "activations_nopad" / SLUG
ICA = BASE / "ica_nopad" / SLUG
SPLIT = BASE / "axes_nopad" / "axis_rebuilt_split_20260925.json"
E1 = Path("/path/to/work/code/stimuli/stimuli_e1.json")
E4 = Path("/path/to/work/code/stimuli/stimuli_e4.json")
VADP = Path("/path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv")
KEYS = ("valence", "arousal", "dominance")
LAYERS = (5, 7, 10, 12)
SEED = 42
N_AXES = 3
_SUF = ["fully", "fulness", "fulness", "ful", "ness", "ly",
        "ing", "tion", "ed", "er", "est", "s"]


def load_vad() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    with open(VADP, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = row.get("word", "").strip().lower()
            if not w:
                continue
            try:
                out[w] = {k: float(row[k].strip()) for k in KEYS}
            except (KeyError, ValueError, AttributeError):
                continue
    return out


def stim_vad(text: str, vad: dict[str, dict[str, float]]) -> dict | None:
    def look(w: str) -> dict[str, float] | None:
        if w in vad:
            return vad[w]
        for s in _SUF:
            if w.endswith(s) and len(w) - len(s) >= 3 and w[: -len(s)] in vad:
                return vad[w[: -len(s)]]
        return None
    hits = [h for h in (look(w) for w in re.findall(r"[a-zA-Z']+", text.lower()))
            if h is not None]
    if not hits:
        return None
    return {k: float(np.mean([h[k] for h in hits])) for k in KEYS}


def dirs_from(acts: np.ndarray, sc: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    out = {}
    for k in KEYS:
        y = sc[k].astype(np.float64)
        yz = (y - y.mean()) / (y.std() + 1e-8)
        d = acts.astype(np.float64).T @ yz
        out[k] = (d / np.linalg.norm(d)).astype(np.float32)
    return out


def spectrum(hd: dict[str, np.ndarray]) -> dict[str, Any]:
    M = np.stack([hd[k] for k in KEYS], axis=1).astype(np.float64)
    sv = np.linalg.svd(M, compute_uv=False)
    Q, _ = np.linalg.qr(M)
    return {"singular_values": [round(float(x), 4) for x in sv],
            "eff_rank_1pct": int((sv > 0.01 * sv[0]).sum()),
            "eff_rank_10pct": int((sv > 0.10 * sv[0]).sum()),
            "eff_rank_participation": round(
                float((sv.sum() ** 2) / (np.sum(sv ** 2) + 1e-30)), 3),
            "pairwise_cos": {f"{a}-{b}": round(float(hd[a] @ hd[b]), 4)
                             for i, a in enumerate(KEYS) for b in KEYS[i + 1:]},
            "_Q": Q.astype(np.float32)}


def resid_ratio(a: np.ndarray, Q: np.ndarray) -> float:
    a64, Q64 = a.astype(np.float64), Q.astype(np.float64)
    r = a64 - Q64 @ (Q64.T @ a64)
    return float(np.linalg.norm(r) / (np.linalg.norm(a64) + 1e-12))


def main() -> None:
    vad = load_vad()
    print(f"VAD entries: {len(vad)}")

    e1 = json.loads(E1.read_text())
    e4 = json.loads(E4.read_text())
    split = json.loads(SPLIT.read_text())
    disc = split["discovery_indices"]

    # ---- degeneracy check that rules out one candidate design ----
    disc_cats = [e4[i]["target_emotion"] for i in disc]
    print("\n--- why one-vs-rest category directions CANNOT be fitted on the "
          "discovery set ---")
    print(f"discovery stimuli: {len(disc)}, distinct categories: "
          f"{len(set(disc_cats))}, items per category: "
          f"{sorted({disc_cats.count(c) for c in set(disc_cats)})}")
    print("=> exactly 1 item per category. One-vs-rest indicator vectors for 20 "
          "categories over 20 samples span R^20, i.e. the FULL row space of the "
          "discovery activations, so the resulting 'human subspace' would remove "
          "essentially every component of any direction fitted from those same "
          "activations. Such a test is vacuous by construction.")
    held = [i for i in range(len(e4)) if i >= 40]
    held_cats = [e4[i]["target_emotion"] for i in held]
    print(f"\nheld-out E4 indices 40-79: {len(held)} stimuli, "
          f"{len(set(held_cats))} categories, "
          f"{sorted({held_cats.count(c) for c in set(held_cats)})} items/category")
    print("=> these are used by NO intervention experiment and are NOT the "
          "confirmation set, so they are the clean place to fit category "
          "directions (needs a small GPU pass: 40 stimuli x 4 layers).")

    # ---- E1-based vs discovery-based V/A/D ----
    sc_e1_raw = [stim_vad(s["text"], vad) for s in e1]
    keep = [i for i, s in enumerate(sc_e1_raw) if s is not None]
    print(f"\nE1: {len(keep)}/{len(e1)} sentences have Warriner matches")
    sc_e1 = {k: np.array([sc_e1_raw[i][k] for i in keep]) for k in KEYS}


    report: dict[str, Any] = {"note": __doc__.strip().splitlines()[0],
                             "degeneracy": {
                                 "discovery_items_per_category": 1,
                                 "discovery_n_categories": len(set(disc_cats)),
                                 "verdict": ("one-vs-rest on the discovery set is "
                                             "vacuous; fit categories on E4 40-79"),
                                 "heldout_e4_indices": held,
                                 "heldout_n_categories": len(set(held_cats))},
                             "layers": {}}

    for L in LAYERS:
        npz = ACT / f"layer{L:02d}_seed{SEED:04d}.npz"
        X = np.load(npz, allow_pickle=True)["arr"].astype(np.float32)
        assert X.shape[0] == len(e1), X.shape
        hd_e1 = dirs_from(X[keep], sc_e1)
        sp_e1 = spectrum(hd_e1)

        # axes (top-3 by split-half reproducibility), same rule as the sweep
        import glob
        files = sorted(glob.glob(str(ICA / f"layer{L:02d}_seed{SEED:04d}_K*.json")))
        best, bs = None, -2.0
        for fp in files:
            dd = json.loads(Path(fp).read_text())
            s_ = max(dd.get("silhouettes") or [-1.0])
            if s_ > bs:
                bs, best = s_, dd
        comps = np.array(best["components"], dtype=np.float32)
        import sys
        sys.path.insert(0, "/path/to/work/code/phase10")
        from run_ica import compute_split_reproducibility
        rep = compute_split_reproducibility(npz, comps, seed=SEED)
        order = np.argsort(-rep)
        top = comps[order][:N_AXES]

        ent = {"S2_vad_on_E1_300": {
            k: v for k, v in sp_e1.items() if k != "_Q"}}
        ent["S2_vad_on_E1_300"]["residual_norm_ratio_top3"] = [
            round(resid_ratio(top[i], sp_e1["_Q"]), 4) for i in range(N_AXES)]
        ent["S2_vad_on_E1_300"]["abs_cos_max_vad_top3"] = [
            round(max(abs(float(top[i] @ hd_e1[k])) for k in KEYS), 4)
            for i in range(N_AXES)]

        # S1 (the pre-registered primary: V/A/D on the 20 discovery E4 stimuli)
        # is read from the completed sweep output rather than recomputed, because
        # its activations come from E4 and are not on disk.
        sweep = sorted((BASE / "axis_residual").glob(
            "axis_residual_discovery_*.json"))
        if sweep:
            sw = json.loads(sweep[-1].read_text())
            for Ls in sw["layers"]:
                if Ls["layer"] == L:
                    q = Ls["human_vad_subspace"]
                    sv = np.asarray(q["singular_values"], dtype=float)
                    ent["S1_vad_on_discovery_20_PREREGISTERED"] = {
                        "singular_values": [round(float(x), 4) for x in sv],
                        "eff_rank_1pct": int((sv > 0.01 * sv[0]).sum()),
                        "eff_rank_10pct": int((sv > 0.10 * sv[0]).sum()),
                        "eff_rank_participation": round(
                            float((sv.sum() ** 2) / (np.sum(sv ** 2) + 1e-30)), 3),
                        "pairwise_cos": q["pairwise_cos"],
                        "residual_norm_ratio_top3": [
                            round(Ls["residual_norm_ratio"][f"axis{i}"], 4)
                            for i in range(N_AXES)],
                        "abs_cos_max_vad_top3": [
                            round(Ls["alignment_spectrum_ALL_axes"][i]
                                  ["abs_cos_max_vad"], 4) for i in range(N_AXES)],
                        "source_file": sweep[-1].name}
                    break
        report["layers"][str(L)] = ent
        print(f"\n=== layer {L} (ICA K={best['k']}, top3 repro="
              f"{[round(float(rep[order][i]),3) for i in range(N_AXES)]})")
        e = ent["S2_vad_on_E1_300"]
        print(f"  S2 V/A/D on E1(300): sv={e['singular_values']} "
              f"eff_rank(1%)={e['eff_rank_1pct']} "
              f"eff_rank(10%)={e['eff_rank_10pct']} "
              f"participation={e['eff_rank_participation']}")
        print(f"     pairwise cos: {e['pairwise_cos']}")
        print(f"     residual norm ratio (top3): {e['residual_norm_ratio_top3']}")
        print(f"     max|cos| vs VAD  (top3): {e['abs_cos_max_vad_top3']}")

    out = BASE / "axes_nopad" / "preflight_subspace_conditioning.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
