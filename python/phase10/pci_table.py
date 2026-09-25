"""Positive-control in-plane retest tables, from the JSON."""
import glob
import json
from pathlib import Path

f = sorted(glob.glob("/path/to/work/results/pos_ctrl_inplane/"
                     "pos_ctrl_inplane_*.json"))[-1]
d = json.loads(Path(f).read_text())
V = d["VERDICT"]
print(f"source: {Path(f).name}  status={d['env']['status']}")
print(f"prereg_commit={d['env'].get('prereg_commit','')[:12]}  "
      f"stimuli={d['env']['stimuli']}")
print(f"\npos beats in-plane : {V['pos_beats_inplane']} "
      f"({len(V['pos_beats_inplane_cells'])} cells)")
print(f"pos beats full-space: {V['pos_beats_fullrand']} "
      f"({len(V['pos_beats_fullrand_cells'])} cells)")
print(f"DISCRIMINATOR      : {V['DISCRIMINATOR_READING']}")

print("\n=== pos direction containment in the top-10 PC span (exact, E4) ===")
for L in d["layers"]:
    ins = L["inside_top10_pc_span"]
    ip = sum(ins[f"inplane_{i}"] for i in range(5)) / 5
    fr = sum(ins[f"fullrand_{i}"] for i in range(5)) / 5
    print(f"  layer {L['layer']:<3} pos_lasttoken={ins['pos_lasttoken']:.4f} "
          f"pos_meanpool={ins['pos_meanpool']:.4f} "
          f"inplane={ip:.4f} fullrand={fr:.4f}")

print("\n=== alpha=0.05: pos_lasttoken against each floor ===")
for x in V["alpha_0.05_detail"]:
    print(f"  layer {x['layer']:<3} vs in-plane  d={x['vs_inplane_delta']:+.2f} "
          f"q={x['vs_inplane_q']:.4f}   |   vs full-space "
          f"d={x['vs_fullrand_delta']:+.2f} q={x['vs_fullrand_q']:.4f}")

print("\n=== per alpha, all layers: JS of pos vs the two floors ===")
for L in d["layers"]:
    print(f"\n  layer {L['layer']}")
    for r in L["rows"]:
        ip = r["paired_pos_lasttoken_vs_inplane"]
        fr = r["paired_pos_lasttoken_vs_fullrand"]
        print(f"    a={r['alpha_rel']:<5} JS_pos={r['js_pos_lasttoken_mean']:.3e} "
              f"floor_ip={r['js_floor_inplane_mean']:.3e} "
              f"floor_fr={r['js_floor_fullrand_mean']:.3e} | "
              f"vs_ip d={ip['cliffs_delta']:+.2f} q={ip.get('wilcoxon_q_bh', float('nan')):.4f} | "
              f"vs_fr d={fr['cliffs_delta']:+.2f} q={fr.get('wilcoxon_q_bh', float('nan')):.4f}")

print("\n=== cells where pos beat the full-space floor (the discriminator) ===")
for c in V["pos_beats_fullrand_cells"]:
    print(f"  layer {c['layer']:<3} a={c['alpha_rel']:<5} d={c['cliffs_delta']:+.2f} "
          f"q={c['q']:.4f}")
