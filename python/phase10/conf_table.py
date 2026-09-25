#!/usr/bin/env python3
"""Render the C1-C4 adjudication JSON as markdown tables for the report.

Reads only the adjudication output, so every number traces to adjudicate_c.py.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def fmt(x: float | None, sig: int = 3) -> str:
    if x is None:
        return "-"
    if isinstance(x, bool):
        return str(x)
    if x != x:
        return "nan"
    if x == 0:
        return "0"
    return f"{x:.{sig}e}" if abs(x) < 1e-3 or abs(x) >= 1e4 else f"{x:.4f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adj", type=Path, required=True)
    a = ap.parse_args()
    d = json.loads(a.adj.read_text())
    A = 0.05
    print(f"# Confirmation-set adjudication ({d['split_adjudicated']})")
    print(f"\nself-test: {d['self_test']}  |  floor cross-check worst rel diff: "
          f"{d['floor_cross_check_worst_rel_diff']:.3e}")
    print(f"\n**VERDICT**: " + ", ".join(
        f"{k}={'PASS' if v else 'FAIL'}" for k, v in d["SUMMARY"].items()))

    c1 = d["C1"]
    print(f"\n## C1 (in-plane floor > full-space floor)  ->  "
          f"{'PASS' if c1['PASS'] else 'FAIL'}")
    print(f"criterion: {c1['criterion']}")
    print(f"\n| layer | ratio (a=0.05) | mean_diff | Cliff d | BH q | sig |")
    print("|---|---|---|---|---|---|")
    for c in c1["cells"]:
        if abs(c["alpha_rel"] - A) > 1e-9:
            continue
        L = c["layer"]
        print(f"| {L} | {c1['floor_ratios_at_alpha0.05'][str(L)]:.3f} "
              f"| {fmt(c['mean_diff'])} | {fmt(c['cliffs_delta'])} "
              f"| {fmt(c['q'])} | {'yes' if c['significant'] else 'no'} |")
    print(f"\nsignificant layers at a=0.05: {c1['significant_layers']} "
          f"({c1['n_layers_significant_at_alpha0.05']}/4); "
          f"all ratios >= 1.5: {c1['all_ratios_ge_1.5']}")

    c2 = d["C2"]
    print(f"\n## C2 (pos beats full-space but not in-plane)  ->  "
          f"{'PASS' if c2['PASS'] else 'FAIL'}")
    print(f"C2a {'PASS' if c2['C2a']['PASS'] else 'FAIL'} "
          f"(layers {c2['C2a']['significant_layers']}); "
          f"C2b {'PASS' if c2['C2b']['PASS'] else 'FAIL'} "
          f"({c2['C2b']['n_significant_cells']} significant cells, <=1 allowed)")
    print(f"\n| layer | vs full-space: mean_diff | d | q | sig "
          f"| vs in-plane: mean_diff | d | q | sig |")
    print("|---|---|---|---|---|---|---|---|---|")
    for L in (5, 7, 10, 12):
        ca = next((c for c in c2["C2a"]["cells"]
                   if c["layer"] == L and abs(c["alpha_rel"] - A) < 1e-9), None)
        cb = next((c for c in c2["C2b"]["cells"]
                   if c["layer"] == L and abs(c["alpha_rel"] - A) < 1e-9), None)
        if not ca or not cb:
            continue
        print(f"| {L} | {fmt(ca['mean_diff'])} | {fmt(ca['cliffs_delta'])} "
              f"| {fmt(ca['q'])} | {'yes' if ca['significant'] else 'no'} "
              f"| {fmt(cb['mean_diff'])} | {fmt(cb['cliffs_delta'])} "
              f"| {fmt(cb['q'])} | {'yes' if cb['significant'] else 'no'} |")

    c4 = d["C4"]
    print(f"\n## C4 (axes do not beat the in-plane floor)  ->  "
          f"{'PASS' if c4['PASS'] else 'FAIL'}")
    print(f"criterion: {c4['criterion']}  |  family size {c4['family_size']}")
    print(f"\n| layer | axis | mean_diff | Cliff d | BH q | degen | sig |")
    print("|---|---|---|---|---|---|---|")
    for c in c4["cells"]:
        if abs(c["alpha_rel"] - A) > 1e-9:
            continue
        print(f"| {c['layer']} | {c['axis']} | {fmt(c['mean_diff'])} "
              f"| {fmt(c['cliffs_delta'])} | {fmt(c['q'])} "
              f"| {fmt(c['degenerate_frac'])} "
              f"| {'yes' if c['significant'] else 'no'} |")
    print(f"\nsignificant cells at a=0.05: "
          f"{c4['n_significant_cells_at_alpha0.05']}/12 {c4['significant_cells']}")

    c3 = d["C3"]
    print(f"\n## C3 (axis norm inside the human subspace < 5%)  ->  "
          f"{'PASS' if c3['PASS'] else 'FAIL'}")
    print(f"**NOT HELD OUT**: {c3['HELD_OUT_NOTE']}")
    print(f"\nmain ({c3['subspace']}): {c3['n_below_5pct']}/{c3['n_cells']} below 5%")
    print(f"\n| layer | axis0 % | axis1 % | axis2 % |")
    print("|---|---|---|---|")
    for L in (5, 7, 10, 12):
        v = [c["inside_pct"] for c in c3["cells"] if c["layer"] == L]
        if len(v) == 3:
            print(f"| {L} | {v[0]:.4f} | {v[1]:.4f} | {v[2]:.4f} |")
    if "secondary_S3" in c3:
        s = c3["secondary_S3"]
        print(f"\nsecondary S3: {s['n_below_5pct']}/{s['n_cells']} below 5%")
        over = [c for c in s["cells"] if not c["below_threshold"]]
        if over:
            print("exceeding cells: " + ", ".join(
                f"L{c['layer']} axis{c['axis']} {c['inside_pct']:.2f}%" for c in over))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
