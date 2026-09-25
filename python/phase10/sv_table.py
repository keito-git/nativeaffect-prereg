"""Signed valence readout tables, from the JSON."""
import glob
import json
from pathlib import Path

f = sorted(glob.glob("/path/to/work/results/signed_valence/"
                     "signed_valence_*.json"))[-1]
d = json.loads(Path(f).read_text())
V, L1, L2 = d["VERDICT"], d["lexicon"], d["lexicon_strict"]
print(f"source: {Path(f).name}  status={d['env']['status']}")
print(f"lexicon primary: POS {L1['n_token_ids_pos']} / NEG {L1['n_token_ids_neg']} ids "
      f"(thresh {L1['pos_threshold']}/{L1['neg_threshold']}), "
      f"dropped {L1['variants_dropped_multitoken']} multitoken")
print(f"lexicon strict : POS {L2['n_token_ids_pos']} / NEG {L2['n_token_ids_neg']} ids "
      f"(thresh {L2['pos_threshold']}/{L2['neg_threshold']})")
print(f"\nVERDICT signed: layers {V['signed_layers_significant_a05']} "
      f"PASS(3of4)={V['signed_PASS_3of4']}")
print(f"VERDICT js    : layers {V['js_layers_significant_a05']} "
      f"PASS(3of4)={V['js_PASS_3of4']}")
print(f"excluded (non-functional lexicon): "
      f"{V['excluded_layers_nonfunctional_lexicon']}")

print("\n=== per layer / alpha: signed effect, pos vs in-plane floor ===")
for Lo in d["layers"]:
    print(f"\n  layer {Lo['layer']}  baseline mass {Lo['baseline_mass_mean']:.3e} "
          f"functional={Lo['lexicon_functional']}")
    for r in Lo["rows"]:
        s = r["paired_signed_pos_vs_inplane"]
        j = r["paired_js_pos_vs_inplane"]
        st = r["paired_signed_strict_pos_vs_inplane"]
        print(f"    a={r['alpha_rel']:<5} "
              f"signed pos={r['signed_pos_lasttoken_mean']:+.3e} "
              f"floor={r['signed_floor_inplane_mean']:+.3e} "
              f"d={s['cliffs_delta']:+.2f} q={s.get('wilcoxon_q_bh', float('nan')):.4f}"
              f" | strict d={st['cliffs_delta']:+.2f} p={st['wilcoxon_p']:.4f}"
              f" | JS d={j['cliffs_delta']:+.2f} "
              f"q={j.get('wilcoxon_q_bh', float('nan')):.4f}")

print("\n=== does the signed metric separate pos from the floor better than JS? ===")
print("  (Cliff's delta at alpha=0.05, signed vs JS, per layer)")
for Lo in d["layers"]:
    r = [x for x in Lo["rows"] if x["alpha_rel"] == 0.05][0]
    print(f"  layer {Lo['layer']:<3} signed d={r['paired_signed_pos_vs_inplane']['cliffs_delta']:+.2f} "
          f"vs JS d={r['paired_js_pos_vs_inplane']['cliffs_delta']:+.2f}")

print("\n=== axes on the signed metric (alpha=0.05) ===")
for Lo in d["layers"]:
    r = [x for x in Lo["rows"] if x["alpha_rel"] == 0.05][0]
    s = " ".join(f"axis{i}:d={r[f'paired_signed_axis{i}_vs_inplane']['cliffs_delta']:+.2f}"
                 for i in range(3))
    print(f"  layer {Lo['layer']:<3} {s}")
