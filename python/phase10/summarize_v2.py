"""Tables for the stage-1 v2 run, straight from the JSON."""
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text())
env, V = d["env"], d["verdicts"]
K = ("valence", "arousal", "dominance")
print(f"status={env['status']} prereg_commit={env.get('prereg_commit','')[:12]} "
      f"judge={env['judge_llm_loaded']} gen={env.get('generation_used')}")
print(f"BH families: {env.get('bh_family_sizes')}")

print("\n" + "=" * 100)
print("TABLE 1 - TIER VALIDATION (prereg 17.2): does each tier's human direction "
      "generalise?")
print("  rule: holdout |r| > permutation-null p95 AND perm p < 0.05")
print("  synthetic context: 0.794 recoverable / 0.214 noise / 0.191 underdet-noise")
print("=" * 100)
for L in d["layers"]:
    ev = L["direction_estimation_validity"]
    tv = ev["tier_validation"]
    print(f"\n--- layer {L['layer']}")
    for tier, key in (("S1", "S1_vad_on_discovery20"), ("S2", "S2_vad_on_E1_287")):
        print(f"  {tier} (n={tv[tier]['n']}, d={tv[tier]['d']}): "
              f"GENERALISES(all)={tv[tier]['all_vad_generalise']}")
        for k in K:
            e = ev[key][k]
            print(f"     {k:<10} holdout r={e['holdout_r']:+.3f} "
                  f"null_p95={e['perm_null_p95_abs_r']:.3f} "
                  f"null_mean={e['perm_null_mean_abs_r']:.3f} "
                  f"perm_p={e['perm_p_value']:.4f} "
                  f"GEN={e['GENERALISES']}  (in-sample r={e['in_sample_r']:+.3f})")
    s3 = ev["S3_category_dirs_on_heldout40"]
    gen = [c for c in s3 if s3[c]["GENERALISES"]]
    rs = sorted(s3[c]["holdout_r"] for c in s3)
    print(f"  S3 categories (n={tv['S3']['n']}): "
          f"{len(gen)}/{len(s3)} generalise "
          f"(frac={tv['S3']['frac_categories_generalise']:.2f}); "
          f"holdout r min/med/max = {rs[0]:+.3f}/{rs[len(rs)//2]:+.3f}/{rs[-1]:+.3f}")

print("\n" + "=" * 100)
print("TABLE 2 - effective rank per layer (S1 must NOT be summarised as '1')")
print("=" * 100)
print(f"{'layer':<7}{'S1 eff10':<10}{'S1 part':<10}{'S2 eff10':<10}{'S2 part':<10}"
      f"{'S3 dims':<9}{'S3 eff10':<10}{'S3 part':<9}")
for L in d["layers"]:
    s = L["subspaces"]
    print(f"{L['layer']:<7}{s['S1']['eff_rank_10pct']:<10}"
          f"{s['S1']['eff_rank_participation']:<10.2f}"
          f"{s['S2']['eff_rank_10pct']:<10}{s['S2']['eff_rank_participation']:<10.2f}"
          f"{s['S3']['n_dims_supplied']:<9}{s['S3']['eff_rank_10pct']:<10}"
          f"{s['S3']['eff_rank_participation']:<9.2f}")

print("\n" + "=" * 100)
print("TABLE 3 - target/direction cross-check (excess >> 0 = underdetermined)")
print("=" * 100)
for L in d["layers"]:
    ev = L["direction_estimation_validity"]
    row = []
    for nm, lab in (("crosscheck_S1_vad", "S1"), ("crosscheck_S2_vad", "S2"),
                    ("crosscheck_S3_categories", "S3cat")):
        c = ev[nm]
        row.append(f"{lab}: tgt={c['mean_abs_target_corr_offdiag']:.3f} "
                   f"dir={c['mean_abs_direction_cos_offdiag']:.3f} "
                   f"excess={c['collinearity_excess']:+.3f}")
    print(f"  layer {L['layer']}: " + " | ".join(row))

print("\n" + "=" * 100)
print("TABLE 4 - residual norm ratio (how much was actually removed)")
print("=" * 100)
for L in d["layers"]:
    rr = L["residual_norm_ratio"]
    print(f"  layer {L['layer']}: " + "  ".join(
        f"axis{i}=" + "/".join(f"{rr[f'axis{i}_{t}']:.3f}" for t in ("S1","S2","S3"))
        for i in range(3)) + "   (S1/S2/S3)")

print("\n" + "=" * 100)
print("TABLE 5 - S2 residual-axis test at alpha=0.05 (the claim's basis if S2 "
      "validates)")
print("=" * 100)
for L in d["layers"]:
    for r in L["rows"]:
        if r["alpha_rel"] != 0.05:
            continue
        print(f"\n  layer {L['layer']} alpha=0.05  randfloor={r['js_randfloor_mean']:.3e} "
              f"orthofloor={r['js_orthofloor_mean']:.3e}")
        for i in range(3):
            raw_r = r[f"paired_axis{i}_vs_randfloor"]
            raw_o = r[f"paired_axis{i}_vs_orthofloor"]
            s2r = r[f"paired_axis{i}_resid_S2_vs_randfloor"]
            s2o = r[f"paired_axis{i}_resid_S2_vs_orthofloor"]
            print(f"    axis{i}: raw JS={r[f'js_axis{i}_mean']:.3e} "
                  f"q_rand={raw_r['wilcoxon_q_bh']:.4f} d={raw_r['cliffs_delta']:+.2f} "
                  f"q_orth={raw_o['wilcoxon_q_bh']:.4f} || "
                  f"residS2 JS={r[f'js_axis{i}_resid_S2_mean']:.3e} "
                  f"att={r[f'attenuation_axis{i}_S2']:+.3f} "
                  f"q_rand={s2r['wilcoxon_q_bh']:.4f} d={s2r['cliffs_delta']:+.2f} "
                  f"q_orth={s2o['wilcoxon_q_bh']:.4f} "
                  f"degen={r[f'degenerate_frac_axis{i}_resid_S2']:.2f}")

print("\n" + "=" * 100)
print("TABLE 6 - Q4: human valence direction itself (V1 comparable to floor?)")
print("=" * 100)
print(f"  V1 comparable fraction overall = {V['V1_supported_fraction']:.3f}")
for x in V["V1_human_valence_comparable_to_floor"]:
    print(f"    layer {x['layer']} a={x['alpha_rel']:<5} "
          f"JS_val={x['js_human_valence']:.3e} floor={x['js_randfloor']:.3e} "
          f"d={x['mean_diff']:+.3e} q={x['q_bh']:.4f} "
          f"delta={x['cliffs_delta']:+.3f} V1_comparable={x['V1_comparable']}")
print("\n  V2 (valence below axes), alpha=0.05 only:")
for x in V["V2_human_valence_below_axes"]:
    if x["alpha_rel"] == 0.05:
        print(f"    layer {x['layer']} axis{x['axis']}: d={x['mean_diff']:+.3e} "
              f"p={x['p']:.3e} delta={x['cliffs_delta']:+.3f}")

print("\n" + "=" * 100)
print("TABLE 7 - R1 per tier + M3' degeneracy")
print("=" * 100)
for t in ("S1", "S2", "S3"):
    b = V["R1_by_tier"][t]
    print(f"  {t}: supported={b['supported']} cells={b['n_cells_surviving']}")
print(f"  M3' degenerate cells flagged: {len(V['M3prime_degenerate'])}")
for x in V["M3prime_degenerate"][:6]:
    print(f"    {x}")
