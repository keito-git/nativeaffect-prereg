#!/usr/bin/env python3
"""Adjudicate prediction P of addendum 14 N2 mechanically.

Registered prediction (before any result was seen)
--------------------------------------------------
P: the sensitivity directions overlap substantially with the span of the top 10
   activation principal components -- the MEAN of the principal-angle cosines is
   at least 0.70.

What may be used to decide it
-----------------------------
The stored per-layer summaries are entrywise (`C.max(axis=0)`, `C.mean()`), and
an entrywise maximum does not bound a principal angle: the 8x8 Hadamard matrix
over sqrt(8) has every entry 0.3536 with the two subspaces identical. The only
sound route from the stored summaries is an upper bound:

    inside_j = sum_k (PC_k . s_j)^2 <= n_pc * max_k |PC_k . s_j|^2
    sum_j inside_j = ||C||_F^2 = sum_i sigma_i^2
    mean(sigma) <= sqrt(mean(sigma^2)) = sqrt(||C||_F^2 / n_pc)

So a layer whose bound is below 0.70 cannot satisfy P. A layer whose bound is at
or above 0.70 is NOT thereby a layer that satisfies P -- the bound is one-sided,
and such a layer is reported INDETERMINATE and must be settled by the exact
computation in g1_pc_overlap.py. This script prefers the exact value whenever
`pc_overlap_exact.json` supplies one.

The verdict wording is fixed by addendum 14 N4 and is emitted verbatim. "Partly
supported" is not an available outcome.

Usage
-----
    python3 adjudicate_prediction_p.py --self-test
    python3 adjudicate_prediction_p.py --dir <G1_jacobian dir>
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

THRESHOLD = 0.70                      # registered in addendum 14 N2
LAYERS = (11, 16, 22, 27)             # registered in addendum 11
DEFAULT_DIR = Path("/path/to/research/論文/"
                   "NativeAffect_AI固有の感情軸/03_解析/plan_b/G1_jacobian")

# Addendum 14 N4, quoted from plan_b_js_amend14_20260926.md. Not paraphrased.
N4_VERBATIM = (
    "**機構の説明は成立しない。** その場合:\n\n"
    "- **(分散, 感度) の平面は退化していないので、四象限による判定は使える**"
    "（追記12 L3 の本来の想定）\n"
    "- **機構の説明は書かない。** 「床が勝つ理由は未解明」と書く。"
    "**別の説明を後から探して当てはめることはしない**\n"
    "- **N5 の測定は、予測の当否にかかわらず実行する**（下記）"
)

# N4's FIRST bullet does not follow, and addendum 16 has already replaced the
# test it relies on. P is about the MEAN of the principal cosines; degeneracy of
# the (variance, sensitivity) plane is about the MAXIMUM. A configuration with one
# principal cosine equal to 1 and the other nine near 0 has a mean of 0.1 -- P
# fails -- while one sensitivity direction lies entirely inside the PC span, which
# is precisely the degeneracy L3 was guarding against. So "P failed" does not
# license "the plane is not degenerate, the quadrant judgement is usable".
# Addendum 16 fixes the degeneracy test on the largest singular value of the
# SIGNED matrix G, so that bullet is superseded rather than applied.
N4_BULLET1_SUPERSEDED = (
    "追記14 N4 の第1項（予測Pが外れたので平面は退化しておらず四象限判定が使える）は"
    "適用しない。予測P は部分角コサインの**平均**についての予測であり、退化は"
    "**最大**についての性質である。1本が完全に含まれ残り9本がほぼ直交する配置は"
    "平均 0.1 で予測P を外すが、それはまさに L3 が警戒した退化そのものである。"
    "追記16 により、退化の判定は符号付き G の最大特異値で行う。"
)

# N5 stands regardless of the verdict, by its own terms.
N5_OBLIGATION = (
    "追記14 N5（上位主成分部分空間内から無作為方向1,000本・射影長ベクトルから JS を"
    "予測する回帰・ホールドアウト R² を層ごとに表で報告・閾値による二値判定はしない・"
    "軸と人間 valence 方向の残差も併記）は、予測の当否にかかわらず実行する。"
)

def bound_from_summaries(rec: dict) -> tuple[float, float]:
    """Upper bound on the mean principal cosine, and on ||C||_F^2."""
    mx = np.asarray(rec["max_abs_cos_with_top10_PC_per_direction"], dtype=np.float64)
    n_pc = int(rec["n_pcs_used"])
    f2_ub = float((n_pc * mx ** 2).sum())
    return math.sqrt(f2_ub / n_pc), f2_ub


def adjudicate(d: Path, layers=LAYERS) -> dict:
    exact_path = d / "pc_overlap_exact.json"
    exact = {}
    if exact_path.exists():
        exact = json.loads(exact_path.read_text()).get("layers", {})

    per_layer, missing = [], []
    for L in layers:
        p = d / f"layer{L:02d}.json"
        if not p.exists():
            missing.append(L)
            continue
        rec = json.loads(p.read_text())
        ub, f2 = bound_from_summaries(rec)
        row = {
            "layer": L,
            "n_stimuli": rec["n_stimuli"],
            "C_max_entry": float(max(rec["max_abs_cos_with_top10_PC_per_direction"])),
            "C_mean_entry": rec["mean_abs_cos_with_top10_PC"],
            "frobenius_sq_upper_bound": f2,
            "mean_principal_cosine_upper_bound": ub,
            "source": "upper bound from the stored entrywise summaries",
        }
        if str(L) in exact:
            row["mean_principal_cosine_exact"] = exact[str(L)]["principal_cosine_mean"]
            row["max_principal_cosine_exact"] = exact[str(L)]["principal_cosine_max"]
            row["source"] = "exact, from pc_overlap_exact.json"
            row["value_used"] = row["mean_principal_cosine_exact"]
        else:
            row["value_used"] = ub
        if row["source"].startswith("exact"):
            row["layer_verdict"] = ("P holds at this layer"
                                    if row["value_used"] >= THRESHOLD
                                    else "P fails at this layer")
        else:
            row["layer_verdict"] = ("P fails at this layer"
                                    if ub < THRESHOLD else "INDETERMINATE")
        per_layer.append(row)

    verdicts = [r["layer_verdict"] for r in per_layer]
    if missing:
        overall = f"NOT YET ADJUDICABLE: layers {missing} are not present"
        conclusion = None
    elif any(v == "INDETERMINATE" for v in verdicts):
        overall = ("NOT YET ADJUDICABLE: at least one layer's one-sided bound does "
                   "not decide it; run g1_pc_overlap.py for the exact value")
        conclusion = None
    elif all(v == "P fails at this layer" for v in verdicts):
        overall = "予測P は外れた"
        conclusion = N4_VERBATIM
    elif all(v == "P holds at this layer" for v in verdicts):
        overall = "予測P は成立した"
        conclusion = None
    else:
        n_hold = sum(1 for v in verdicts if v == "P holds at this layer")
        overall = (f"予測P は外れた（{n_hold}/{len(verdicts)} 層でのみ成立。"
                   "全層での成立を予測していたので、外れたとして扱う）")
        conclusion = N4_VERBATIM

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "prediction": ("addendum 14 N2: mean of the principal-angle cosines "
                       "between the sensitivity directions and the top-10 "
                       "activation PC span is at least 0.70"),
        "registered_before_results": True,
        "threshold": THRESHOLD,
        "why_a_bound_is_admissible": (
            "the stored summaries are entrywise; an entrywise maximum does not "
            "bound a principal angle (8x8 Hadamard/sqrt(8): every entry 0.3536, "
            "subspaces identical), but sum_i sigma_i^2 = ||C||_F^2 <= n_pc * "
            "sum_j max_j^2 gives a one-sided bound via Cauchy-Schwarz"
        ),
        "bound_is_one_sided": (
            "a bound below the threshold refutes P at that layer; a bound at or "
            "above it decides nothing and is reported INDETERMINATE"
        ),
        "per_layer": per_layer,
        "overall_verdict": overall,
        "registered_conclusion_verbatim": conclusion,
        "n4_bullet1_not_applied": N4_BULLET1_SUPERSEDED if conclusion else None,
        "n5_still_required": N5_OBLIGATION,
        "wording_rule": ("addendum 14 N4: record that the prediction FAILED. "
                         "'partly supported' is not an available outcome."),
    }


def self_test() -> None:
    fails: list[str] = []

    def ck(name: str, cond: bool) -> None:
        print(f"  [{'ok' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    import tempfile

    def write(d: Path, L: int, maxes: list[float]) -> None:
        (d / f"layer{L:02d}.json").write_text(json.dumps({
            "n_stimuli": 144, "n_pcs_used": 10,
            "max_abs_cos_with_top10_PC_per_direction": maxes,
            "mean_abs_cos_with_top10_PC": float(np.mean(maxes) / 2)}))

    small = [0.1] * 10                      # bound = sqrt(0.1) = 0.316
    big = [0.9] * 10                        # bound = sqrt(8.1) > 1, indeterminate

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for L in LAYERS:
            write(d, L, small)
        r = adjudicate(d)
        ck("all four layers below threshold -> P failed",
           r["overall_verdict"] == "予測P は外れた")
        ck("the verbatim conclusion is emitted",
           r["registered_conclusion_verbatim"] == N4_VERBATIM)
        ck("the conclusion never says 部分的に支持",
           "部分的" not in r["registered_conclusion_verbatim"])
        ck("the emitted text is addendum 14 N4 verbatim",
           r["registered_conclusion_verbatim"] == N4_VERBATIM)
        ck("N4's first bullet is explicitly NOT applied",
           r["n4_bullet1_not_applied"] is not None
           and "最大特異値" in r["n4_bullet1_not_applied"])
        ck("N5 is carried as an obligation regardless of the verdict",
           r["n5_still_required"] is not None)
        ck("bound computed from the summaries, not hand-typed",
           abs(r["per_layer"][0]["mean_principal_cosine_upper_bound"]
               - math.sqrt(0.1)) < 1e-12)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for L in LAYERS[:3]:
            write(d, L, small)
        r = adjudicate(d)
        ck("a missing layer blocks adjudication",
           r["overall_verdict"].startswith("NOT YET ADJUDICABLE")
           and r["registered_conclusion_verbatim"] is None)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for L in LAYERS:
            write(d, L, small)
        write(d, 27, big)
        r = adjudicate(d)
        ck("a bound above the threshold is INDETERMINATE, not 'P holds'",
           r["overall_verdict"].startswith("NOT YET ADJUDICABLE"))
        ck("and it does NOT emit a conclusion",
           r["registered_conclusion_verbatim"] is None)

        # the exact file settles that layer
        (d / "pc_overlap_exact.json").write_text(json.dumps({"layers": {
            "27": {"principal_cosine_mean": 0.12, "principal_cosine_max": 0.4}}}))
        r2 = adjudicate(d)
        ck("the exact value is preferred over the bound when available",
           r2["per_layer"][-1]["source"].startswith("exact"))
        ck("with the exact value the verdict resolves to failed",
           r2["overall_verdict"] == "予測P は外れた")

        (d / "pc_overlap_exact.json").write_text(json.dumps({"layers": {
            "27": {"principal_cosine_mean": 0.85, "principal_cosine_max": 0.9}}}))
        r3 = adjudicate(d)
        ck("one layer holding while three fail is still recorded as failed",
           r3["overall_verdict"].startswith("予測P は外れた")
           and r3["registered_conclusion_verbatim"] == N4_VERBATIM)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for L in LAYERS:
            write(d, L, small)
        (d / "pc_overlap_exact.json").write_text(json.dumps({"layers": {
            str(L): {"principal_cosine_mean": 0.9, "principal_cosine_max": 0.95}
            for L in LAYERS}}))
        r = adjudicate(d)
        ck("P holding everywhere is reportable and emits no failure text",
           r["overall_verdict"] == "予測P は成立した"
           and r["registered_conclusion_verbatim"] is None)

    print(f"\nself-test: {len(fails)} failure(s)")
    if fails:
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--write", action="store_true",
                    help="write prediction_p_verdict.json into --dir")
    a = ap.parse_args()

    print("self-test:")
    self_test()
    if a.self_test:
        return 0

    r = adjudicate(a.dir)
    for row in r["per_layer"]:
        print(f"  layer {row['layer']:>2}: bound {row['mean_principal_cosine_upper_bound']:.4f}"
              f"  ({row['source']})  -> {row['layer_verdict']}")
    print(f"\noverall: {r['overall_verdict']}")
    if r["registered_conclusion_verbatim"]:
        print(f"conclusion (verbatim): {r['registered_conclusion_verbatim']}")
    if a.write:
        p = a.dir / "prediction_p_verdict.json"
        p.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
