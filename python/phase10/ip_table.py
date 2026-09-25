"""In-plane floor result tables, straight from the JSON."""
import glob
import json
from pathlib import Path

f = sorted(glob.glob("/path/to/work/results/inplane_floor/"
                     "inplane_floor_discovery_*.json"))[-1]
d = json.loads(Path(f).read_text())
V = d["PRIMARY_VERDICT"]
print(f"source: {Path(f).name}")
print(f"status={d['env']['status']} prereg_commit={d['env'].get('prereg_commit','')[:12]}")
print(f"PRIMARY: {V['n_axis_cells_beating_inplane']}/{V['n_axis_cells_total']} "
      f"axis-cells beat the in-plane floor; criterion_met={V['criterion_met']}")

print("\n=== per axis-cell (prereg 26.3: alpha>=0.03, BH q<0.05, degen<0.20) ===")
for v in V["per_axis"]:
    al = ", ".join(f"a={c['alpha_rel']}(d={c['cliffs_delta']:+.2f},q={c['q']:.4f})"
                   for c in v["cells"])
    print(f"  L{v['layer']:<3} axis{v['axis']}  beats={str(v['beats_inplane']):<5} "
          f"{al}")

print("\n=== floors and axis JS at alpha=0.05, with the margin against each floor ===")
for L in d["layers"]:
    for r in L["rows"]:
        if r["alpha_rel"] != 0.05:
            continue
        print(f"\n  layer {L['layer']}  floors: inplane={r['js_floor_inplane_mean']:.3e} "
              f"inplanevar={r['js_floor_inplanevar_mean']:.3e} "
              f"fullrand={r['js_floor_fullrand_mean']:.3e} "
              f"pc={r['js_floor_pc_mean']:.3e}")
        for i in range(3):
            ip = r[f"paired_axis{i}_vs_inplane"]
            fr = r[f"paired_axis{i}_vs_fullrand"]
            iv = r[f"paired_axis{i}_vs_inplanevar"]
            pc = r[f"paired_axis{i}_vs_pc"]
            print(f"    axis{i} JS={r[f'js_axis{i}_mean']:.3e} | "
                  f"vs inplane d={ip['cliffs_delta']:+.2f} q={ip['wilcoxon_q_bh']:.4f} | "
                  f"vs fullrand d={fr['cliffs_delta']:+.2f} | "
                  f"vs inplanevar d={iv['cliffs_delta']:+.2f} | "
                  f"vs pc d={pc['cliffs_delta']:+.2f}")

print("\n=== do the PCs themselves act like the axes? (alpha=0.05) ===")
for L in d["layers"]:
    for r in L["rows"]:
        if r["alpha_rel"] != 0.05:
            continue
        s = " ".join(f"pc{i}:d={r[f'paired_pc{i}_vs_fullrand']['cliffs_delta']:+.2f}"
                     for i in range(5))
        print(f"  layer {L['layer']} PC vs fullrand: {s}")
        s2 = " ".join(f"pc{i}:d={r[f'paired_pc{i}_vs_inplane']['cliffs_delta']:+.2f}"
                      for i in range(5))
        print(f"  layer {L['layer']} PC vs inplane : {s2}")

print("\n=== containment check (floor construction) ===")
for L in d["layers"]:
    ins = L["inside_top10_pc_span"]
    ax = [round(ins[f"axis{i}"], 4) for i in range(3)]
    ip = round(sum(ins[f"inplane_{i}"] for i in range(5)) / 5, 4)
    fr = round(sum(ins[f"fullrand_{i}"] for i in range(5)) / 5, 4)
    print(f"  layer {L['layer']}: axes={ax} inplane={ip} fullrand={fr} "
          f"(chance 10/2048={10/2048:.5f})")
