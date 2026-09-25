#!/usr/bin/env python3
"""Mechanically adjudicate the confirmatory hypotheses C1-C4 (prereg section 37).

Every criterion is read from the pre-registration and applied to the JSON that
the runners produced. No number is typed by hand.

BH is recomputed here rather than reused from the runners, because the runners'
families differ from the families section 37 fixes (the runners include
alpha=0.01, which section 37 excludes from C2b/C4).

--self-test drives THESE SAME functions with synthetic inputs, including inputs
that must NOT pass, so a criterion that silently always passes is caught.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np

LAYERS = (5, 7, 10, 12)
ALPHAS = (0.01, 0.03, 0.05, 0.10, 0.20)
ALPHAS_GE03 = (0.03, 0.05, 0.10, 0.20)
ALPHA_PRIMARY = 0.05
N_AXES = 3
DEGEN_MAX = 0.20          # prereg M3'
Q_THRESH = 0.05
C1_RATIO_MIN = 1.5        # prereg 37 C1
C3_PCT_THRESH = 5.0       # prereg 37 C3
C3_MIN_CELLS = 10         # of 12
C2B_MAX_CELLS = 1
C4_MAX_CELLS = 2
MIN_LAYERS_SIG = 3        # of 4, at alpha=0.05


def bh(pv: Sequence[float]) -> list[float]:
    arr = np.asarray(pv, float)
    ok = ~np.isnan(arr)
    out = np.full(arr.shape, np.nan)
    p = arr[ok]
    if p.size == 0:
        return out.tolist()
    o = np.argsort(p)
    m = p.size
    adj = np.clip(np.minimum.accumulate((p[o] * m / (np.arange(m) + 1))[::-1])[::-1],
                  0, 1)
    r = np.empty(m)
    r[o] = adj
    out[ok] = r
    return out.tolist()


def rows_of(doc: dict, layer: int) -> list[dict]:
    for Lo in doc["layers"]:
        if Lo["layer"] == layer:
            return Lo["rows"]
    return []


def cell(doc: dict, layer: int, alpha: float) -> dict | None:
    for r in rows_of(doc, layer):
        if abs(float(r["alpha_rel"]) - alpha) < 1e-9:
            return r
    return None


def _mean_degen(row: dict, prefix: str, n: int) -> float:
    """Mean degeneracy fraction over the n arms that make up a floor."""
    v = [row[f"degenerate_frac_{prefix}_{i}"] for i in range(n)
         if f"degenerate_frac_{prefix}_{i}" in row]
    return float(np.mean(v)) if v else float("nan")


def _sig(test: dict, q: float, degen: float) -> bool:
    """A cell counts as a rejection only with q<0.05 AND mean_diff>0 AND a
    non-degenerate output distribution. mean_diff<=0 can never be a rejection."""
    md = test.get("mean_diff", float("nan"))
    if math.isnan(md) or md <= 0:
        return False
    if math.isnan(q) or q >= Q_THRESH:
        return False
    if not math.isnan(degen) and degen >= DEGEN_MAX:
        return False
    return True


def _family(doc: dict, key: str, alphas: Sequence[float],
            degen_fn: Any) -> dict[tuple, dict]:
    """Collect a BH family over (layer, alpha) and attach q."""
    keys, tests, degens = [], [], []
    for L in LAYERS:
        for al in alphas:
            r = cell(doc, L, al)
            if r is None or key not in r:
                continue
            keys.append((L, al))
            tests.append(r[key])
            degens.append(degen_fn(r))
    qs = bh([t.get("wilcoxon_p", float("nan")) for t in tests])
    return {k: {"test": t, "q": q, "degen": d}
            for k, t, q, d in zip(keys, tests, qs, degens)}


def judge_c1(pos: dict) -> dict:
    """C1: the in-plane floor's effect exceeds the full-space floor's."""
    fam = _family(pos, "paired_floor_inplane_vs_fullrand", ALPHAS,
                  lambda r: max(_mean_degen(r, "inplane", 5),
                                _mean_degen(r, "fullrand", 5)))
    sig_layers, ratios, per_cell = [], {}, []
    for (L, al), e in sorted(fam.items()):
        s = _sig(e["test"], e["q"], e["degen"])
        per_cell.append({"layer": L, "alpha_rel": al, "q": e["q"],
                         "mean_diff": e["test"]["mean_diff"],
                         "cliffs_delta": e["test"].get("cliffs_delta"),
                         "degenerate_frac": e["degen"], "significant": s})
        if abs(al - ALPHA_PRIMARY) < 1e-9:
            if s:
                sig_layers.append(L)
            r = cell(pos, L, al)
            fr = r["js_floor_fullrand_mean"]
            ratios[L] = (r["js_floor_inplane_mean"] / fr if fr > 0
                         else float("nan"))
    n_sig = len(sig_layers)
    ratio_ok = (len(ratios) == len(LAYERS)
                and all(not math.isnan(v) and v >= C1_RATIO_MIN
                        for v in ratios.values()))
    return {"name": "C1", "family_size": len(fam),
            "n_layers_significant_at_alpha0.05": n_sig,
            "significant_layers": sig_layers,
            "floor_ratios_at_alpha0.05": ratios,
            "all_ratios_ge_1.5": ratio_ok,
            "criterion": (f">={MIN_LAYERS_SIG}/4 layers with BH q<0.05 and "
                          f"mean_diff>0 at alpha=0.05, AND all 4 ratios >= "
                          f"{C1_RATIO_MIN}"),
            "PASS": bool(n_sig >= MIN_LAYERS_SIG and ratio_ok),
            "cells": per_cell}


def judge_c2(pos: dict) -> dict:
    """C2: conjunction of C2a (pos beats full-space) and C2b (pos does not
    beat in-plane)."""
    dg = lambda r: r.get("degenerate_frac_pos_lasttoken", float("nan"))  # noqa: E731
    fam_a = _family(pos, "paired_pos_lasttoken_vs_fullrand", ALPHAS, dg)
    sig_layers_a, cells_a = [], []
    for (L, al), e in sorted(fam_a.items()):
        s = _sig(e["test"], e["q"], e["degen"])
        cells_a.append({"layer": L, "alpha_rel": al, "q": e["q"],
                        "mean_diff": e["test"]["mean_diff"],
                        "cliffs_delta": e["test"].get("cliffs_delta"),
                        "significant": s})
        if abs(al - ALPHA_PRIMARY) < 1e-9 and s:
            sig_layers_a.append(L)
    a_pass = len(sig_layers_a) >= MIN_LAYERS_SIG

    fam_b = _family(pos, "paired_pos_lasttoken_vs_inplane", ALPHAS_GE03, dg)
    sig_b, cells_b = [], []
    for (L, al), e in sorted(fam_b.items()):
        s = _sig(e["test"], e["q"], e["degen"])
        cells_b.append({"layer": L, "alpha_rel": al, "q": e["q"],
                        "mean_diff": e["test"]["mean_diff"],
                        "cliffs_delta": e["test"].get("cliffs_delta"),
                        "significant": s})
        if s:
            sig_b.append({"layer": L, "alpha_rel": al})
    b_pass = len(sig_b) <= C2B_MAX_CELLS
    return {"name": "C2", "C2a": {"family_size": len(fam_a),
                                  "significant_layers": sig_layers_a,
                                  "n": len(sig_layers_a), "PASS": bool(a_pass),
                                  "cells": cells_a},
            "C2b": {"family_size": len(fam_b), "n_significant_cells": len(sig_b),
                    "significant_cells": sig_b, "PASS": bool(b_pass),
                    "cells": cells_b},
            "criterion": ("C2a: >=3/4 layers at alpha=0.05; C2b: <=1 cell over "
                          "the 16 cells with alpha>=0.03. CONJUNCTION"),
            "PASS": bool(a_pass and b_pass)}


def judge_c4(floor: dict) -> dict:
    """C4: the axes do not beat the in-plane floor."""
    keys, tests, degens = [], [], []
    for L in LAYERS:
        for i in range(N_AXES):
            for al in ALPHAS_GE03:
                r = cell(floor, L, al)
                if r is None:
                    continue
                k = f"paired_axis{i}_vs_inplane"
                if k not in r:
                    continue
                keys.append((L, i, al))
                tests.append(r[k])
                degens.append(r.get(f"degenerate_frac_axis{i}", float("nan")))
    qs = bh([t.get("wilcoxon_p", float("nan")) for t in tests])
    sig, cells = [], []
    for (L, i, al), t, q, d in zip(keys, tests, qs, degens):
        s = _sig(t, q, d)
        cells.append({"layer": L, "axis": i, "alpha_rel": al, "q": q,
                      "mean_diff": t["mean_diff"],
                      "cliffs_delta": t.get("cliffs_delta"),
                      "degenerate_frac": d, "significant": s})
        if abs(al - ALPHA_PRIMARY) < 1e-9 and s:
            sig.append({"layer": L, "axis": i})
    return {"name": "C4", "family_size": len(tests),
            "n_significant_cells_at_alpha0.05": len(sig),
            "significant_cells": sig,
            "criterion": (f"<={C4_MAX_CELLS} of the 12 cells at alpha=0.05 with "
                          "BH q<0.05 and mean_diff>0"),
            "PASS": bool(len(sig) <= C4_MAX_CELLS),
            "NOTE": ("this confirms indistinguishability from the in-plane floor, "
                     "not the absence of an effect"),
            "cells": cells}


def judge_c3(align: dict, s3: dict | None) -> dict:
    """C3: the axes' norm inside the human emotion subspace is below 5 percent.

    NOT held out by the stimulus split: this quantity is computed from the E1
    sentences and the ICA axes, neither of which depends on the E4 split. Its
    value is therefore fixed by the discovery computation.
    """
    main = []
    layers = align["layers"]
    for Lk in sorted(layers, key=lambda x: int(x)):
        e = layers[Lk].get("P2_ridge_std")
        if not e:
            continue
        for i, v in enumerate(e["inside_fraction_pct_per_axis"]):
            main.append({"layer": int(Lk), "axis": i, "inside_pct": float(v),
                         "below_threshold": bool(float(v) < C3_PCT_THRESH)})
    n_below = sum(1 for m in main if m["below_threshold"])
    out = {"name": "C3", "subspace": "S2 via P2_ridge_std",
           "n_cells": len(main), "n_below_5pct": n_below,
           "criterion": f">={C3_MIN_CELLS} of 12 cells with inside_fraction < "
                        f"{C3_PCT_THRESH}%",
           "PASS": bool(len(main) == 12 and n_below >= C3_MIN_CELLS),
           "HELD_OUT": False,
           "HELD_OUT_NOTE": ("C3 does not read the E4 stimulus split; it is "
                             "computed from E1 sentences and the ICA axes, so "
                             "the confirmation value equals the discovery value "
                             "and C3 carries no out-of-sample information"),
           "cells": main}
    if s3:
        sec = []
        for Lk in sorted(s3.get("layers", {}), key=lambda x: int(x)):
            # S3 stores the same statistic under a different key name
            v = (s3["layers"][Lk].get("P2_ridge_std", {})
                 .get("axis_inside_fraction_pct"))
            if v:
                for i, x in enumerate(v):
                    sec.append({"layer": int(Lk), "axis": i,
                                "inside_pct": float(x),
                                "below_threshold": bool(float(x) < C3_PCT_THRESH)})
        if sec:
            out["secondary_S3"] = {
                "n_cells": len(sec),
                "n_below_5pct": sum(1 for s in sec if s["below_threshold"]),
                "cells": sec}
    return out


# ---------------------------------------------------------------- self-test

def _mk_pos(layer_specs: dict, ratio: dict, alphas=ALPHAS) -> dict:
    """Build a pos-runner-shaped doc. layer_specs[L] = dict of per-key
    (p, mean_diff) for 'c1', 'c2a', 'c2b'; applied at every alpha."""
    layers = []
    for L, sp in layer_specs.items():
        rows = []
        for al in alphas:
            fr = 1.0e-4
            rows.append({
                "layer": L, "alpha_rel": al, "n_samples": 40,
                "js_floor_inplane_mean": fr * ratio[L],
                "js_floor_fullrand_mean": fr,
                "degenerate_frac_pos_lasttoken": sp.get("degen", 0.0),
                **{f"degenerate_frac_inplane_{i}": sp.get("degen", 0.0)
                   for i in range(5)},
                **{f"degenerate_frac_fullrand_{i}": 0.0 for i in range(5)},
                "paired_floor_inplane_vs_fullrand": {
                    "wilcoxon_p": sp["c1"][0], "mean_diff": sp["c1"][1],
                    "cliffs_delta": 1.0, "n": 40},
                "paired_pos_lasttoken_vs_fullrand": {
                    "wilcoxon_p": sp["c2a"][0], "mean_diff": sp["c2a"][1],
                    "cliffs_delta": 1.0, "n": 40},
                "paired_pos_lasttoken_vs_inplane": {
                    "wilcoxon_p": sp["c2b"][0], "mean_diff": sp["c2b"][1],
                    "cliffs_delta": -1.0, "n": 40},
            })
        layers.append({"layer": L, "rows": rows})
    return {"layers": layers}


def _mk_floor(n_sig_cells: int, degen: float = 0.0) -> dict:
    """Floor-runner-shaped doc where exactly n_sig_cells of the 12 alpha=0.05
    cells are strongly significant with a positive mean_diff."""
    layers, made = [], 0
    for L in LAYERS:
        rows = []
        for al in ALPHAS_GE03:
            r: dict[str, Any] = {"layer": L, "alpha_rel": al, "n_samples": 40}
            for i in range(N_AXES):
                hit = (abs(al - ALPHA_PRIMARY) < 1e-9 and made < n_sig_cells)
                if hit:
                    made += 1
                r[f"paired_axis{i}_vs_inplane"] = {
                    "wilcoxon_p": 1e-9 if hit else 0.9,
                    "mean_diff": 1e-4 if hit else -1e-5,
                    "cliffs_delta": 0.5 if hit else -0.5, "n": 40}
                r[f"degenerate_frac_axis{i}"] = degen
            rows.append(r)
        layers.append({"layer": L, "rows": rows})
    return {"layers": layers}


def _mk_align(pcts: list[float]) -> dict:
    layers = {}
    for j, L in enumerate(LAYERS):
        layers[str(L)] = {"P2_ridge_std": {
            "inside_fraction_pct_per_axis": pcts[3 * j:3 * j + 3]}}
    return {"layers": layers}


def self_test() -> int:
    ok = True

    def c(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if cond else 'FAIL'}] {name}")
        ok &= bool(cond)

    GOOD = {"c1": (1e-9, 1e-4), "c2a": (1e-9, 1e-4), "c2b": (0.9, -1e-5)}
    r2 = {L: 2.0 for L in LAYERS}

    # --- C1
    c("C1 passes when all 4 layers are significant and all ratios >= 1.5",
      judge_c1(_mk_pos({L: GOOD for L in LAYERS}, r2))["PASS"])
    bad_ratio = dict(r2); bad_ratio[10] = 1.2
    c("C1 FAILS on a ratio below 1.5 even with 4/4 significant",
      not judge_c1(_mk_pos({L: GOOD for L in LAYERS}, bad_ratio))["PASS"])
    two = {L: (GOOD if L in (5, 7) else
               {"c1": (0.9, 1e-6), "c2a": GOOD["c2a"], "c2b": GOOD["c2b"]})
           for L in LAYERS}
    c("C1 FAILS with only 2/4 layers significant",
      not judge_c1(_mk_pos(two, r2))["PASS"])
    # the sign trap: a tiny p with a NEGATIVE mean_diff must never count
    flip = {L: ({"c1": (1e-30, -1e-4), "c2a": GOOD["c2a"], "c2b": GOOD["c2b"]}
                if L in (10, 12) else GOOD) for L in LAYERS}
    j = judge_c1(_mk_pos(flip, r2))
    c("C1: p~0 with mean_diff<0 is NOT counted as a rejection (sign trap)",
      j["n_layers_significant_at_alpha0.05"] == 2 and not j["PASS"])
    dg = {L: dict(GOOD, degen=0.5) for L in LAYERS}
    c("C1 FAILS when every cell is degenerate (degenerate_frac >= 0.20)",
      not judge_c1(_mk_pos(dg, r2))["PASS"])

    # --- C2 conjunction
    c("C2 passes when C2a holds and C2b has 0 cells",
      judge_c2(_mk_pos({L: GOOD for L in LAYERS}, r2))["PASS"])
    b3 = {L: (dict(GOOD, c2b=(1e-9, 1e-4)) if L in (5, 7, 10) else GOOD)
          for L in LAYERS}
    j2 = judge_c2(_mk_pos(b3, r2))
    c("C2 FAILS when C2b has more than 1 significant cell (conjunction)",
      j2["C2a"]["PASS"] and not j2["C2b"]["PASS"] and not j2["PASS"])
    a0 = {L: dict(GOOD, c2a=(0.9, -1e-6)) for L in LAYERS}
    j3 = judge_c2(_mk_pos(a0, r2))
    c("C2 FAILS when C2a fails even though C2b holds",
      not j3["C2a"]["PASS"] and j3["C2b"]["PASS"] and not j3["PASS"])

    # --- C4
    c("C4 passes with 2 significant cells", judge_c4(_mk_floor(2))["PASS"])
    c("C4 FAILS with 5 significant cells", not judge_c4(_mk_floor(5))["PASS"])
    c("C4 counts exactly the injected number of cells",
      judge_c4(_mk_floor(3))["n_significant_cells_at_alpha0.05"] == 3)
    c("C4 family size is 48 as pre-registered",
      judge_c4(_mk_floor(0))["family_size"] == 48)
    c("C4: degenerate cells are excluded from the count",
      judge_c4(_mk_floor(5, degen=0.5))["n_significant_cells_at_alpha0.05"] == 0)

    # --- C3
    c("C3 passes at 12/12 below 5%", judge_c3(_mk_align([1.0] * 12), None)["PASS"])
    c("C3 passes at 10/12 below 5%",
      judge_c3(_mk_align([1.0] * 10 + [9.0, 9.0]), None)["PASS"])
    c("C3 FAILS at 9/12 below 5%",
      not judge_c3(_mk_align([1.0] * 9 + [9.0] * 3), None)["PASS"])
    c("C3 treats exactly 5.0% as NOT below threshold",
      judge_c3(_mk_align([5.0] * 12), None)["n_below_5pct"] == 0)
    c("C3 is flagged as not held out",
      judge_c3(_mk_align([1.0] * 12), None)["HELD_OUT"] is False)
    s3syn = {"layers": {str(L): {"P2_ridge_std": {
        "axis_inside_fraction_pct": [1.0, 2.0, 9.0]}} for L in LAYERS}}
    j3s = judge_c3(_mk_align([1.0] * 12), s3syn)["secondary_S3"]
    c("C3 secondary S3 is read and counted separately",
      j3s["n_cells"] == 12 and j3s["n_below_5pct"] == 8)

    # --- BH sanity
    q = bh([0.001, 0.02, 0.5])
    c("BH monotone and >= p", q[0] <= q[1] <= q[2] and q[0] >= 0.001)
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pos-json", type=Path)
    ap.add_argument("--floor-json", type=Path)
    ap.add_argument("--align-json", type=Path)
    ap.add_argument("--s3-json", type=Path)
    ap.add_argument("--split", default="confirmation")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--prereg-commit", default="")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if self_test() != 0:
        print("REFUSING to adjudicate: self-test failed")
        return 2
    pos = json.loads(a.pos_json.read_text())
    floor = json.loads(a.floor_json.read_text())
    align = json.loads(a.align_json.read_text())
    s3 = json.loads(a.s3_json.read_text()) if a.s3_json else None

    # cross-check: both runners drew the same floors, so their floor means must agree
    xchk = []
    for L in LAYERS:
        for al in ALPHAS:
            rp, rf = cell(pos, L, al), cell(floor, L, al)
            if rp and rf:
                for k in ("js_floor_inplane_mean", "js_floor_fullrand_mean"):
                    xchk.append({"layer": L, "alpha_rel": al, "key": k,
                                 "pos": rp[k], "floor": rf[k],
                                 "rel_diff": abs(rp[k] - rf[k])
                                 / max(abs(rp[k]), 1e-300)})
    worst = max((x["rel_diff"] for x in xchk), default=float("nan"))

    res = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "split_adjudicated": a.split,
        "prereg_commit": a.prereg_commit,
        "prereg_section": "37 (with the 38 supplements)",
        "inputs": {"pos": str(a.pos_json), "floor": str(a.floor_json),
                   "align": str(a.align_json),
                   "s3": str(a.s3_json) if a.s3_json else None},
        "input_sha256": {
            "pos": hashlib.sha256(a.pos_json.read_bytes()).hexdigest(),
            "floor": hashlib.sha256(a.floor_json.read_bytes()).hexdigest()},
        "floor_cross_check_worst_rel_diff": worst,
        "self_test": "PASS",
        "C1": judge_c1(pos), "C2": judge_c2(pos),
        "C3": judge_c3(align, s3), "C4": judge_c4(floor),
    }
    res["SUMMARY"] = {k: res[k]["PASS"] for k in ("C1", "C2", "C3", "C4")}
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print(json.dumps(res["SUMMARY"], indent=2))
    print(f"C1 ratios: {res['C1']['floor_ratios_at_alpha0.05']}")
    print(f"C1 sig layers: {res['C1']['significant_layers']}")
    print(f"C2a sig layers: {res['C2']['C2a']['significant_layers']}  "
          f"C2b sig cells: {res['C2']['C2b']['n_significant_cells']}")
    print(f"C3 below 5%: {res['C3']['n_below_5pct']}/{res['C3']['n_cells']} "
          f"(held out: {res['C3']['HELD_OUT']})")
    print(f"C4 sig cells: {res['C4']['n_significant_cells_at_alpha0.05']}/12")
    print(f"floor cross-check worst rel diff: {worst:.3e}")
    if a.out:
        print(f"-> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
