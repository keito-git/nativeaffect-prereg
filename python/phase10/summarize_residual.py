"""Print the residual-axis test tables straight from the run's JSON."""
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text())
env, V = d["env"], d["verdicts"]
print(f"status={env['status']}  prereg_commit={env.get('prereg_commit','')[:12]}")
print(f"split_sha256={env.get('split_sha256','')[:16]}  "
      f"script_sha256={env.get('script_sha256','')[:16]}")
print(f"judge_llm_loaded={env['judge_llm_loaded']}  alphas={env['alphas_rel']}")
print(f"BH family sizes={env.get('bh_family_sizes')}")
print(f"set={env.get('split_set')}")

print("\n" + "=" * 104)
print("TABLE A - human-VAD alignment spectrum, ALL axes (reported, NEVER used to "
      "select/reorder/exclude)")
print("=" * 104)
for L in d["layers"]:
    q = L["human_vad_subspace"]
    print(f"\nlayer {L['layer']}  K={L['axis_ica_k']}  "
          f"VAD subspace singular values="
          f"{[round(x,3) for x in q['singular_values']]}  rank={q['rank_tol_1e-6']}")
    print(f"  human dir pairwise cos: "
          + "  ".join(f"{k}={v:+.3f}" for k, v in q["pairwise_cos"].items()))
    print(f"  {'rank':<5}{'ica':<5}{'repro':<8}{'|cos|V':<8}{'|cos|A':<8}"
          f"{'|cos|D':<8}{'max':<7}")
    for s in L["alignment_spectrum_ALL_axes"]:
        mark = " <- top3" if s["axis_rank"] < 3 else ""
        print(f"  {s['axis_rank']:<5}{s['ica_index']:<5}{s['split_repro']:<8.3f}"
              f"{s['abs_cos_valence']:<8.3f}{s['abs_cos_arousal']:<8.3f}"
              f"{s['abs_cos_dominance']:<8.3f}{s['abs_cos_max_vad']:<7.3f}{mark}")

print("\n" + "=" * 118)
print("TABLE B - raw axis vs residual axis (human VAD subspace removed). "
      "n=40 = 20 discovery stimuli x 2 polarities")
print("=" * 118)
for L in d["layers"]:
    print(f"\n--- layer {L['layer']}  repro(top3)="
          f"{[round(x,3) for x in L['axis_split_repro_top3']]}")
    for i in range(3):
        rr = L["residual_norm_ratio"][f"axis{i}"]
        cs = L["alignment_spectrum_ALL_axes"][i]["abs_cos_max_vad"]
        print(f"  axis{i}  max|cos|VAD={cs:.3f}  residual_norm_ratio={rr:.3f}")
        for r in L["rows"]:
            ar = r[f"paired_axis{i}_vs_randfloor"]
            ao = r[f"paired_axis{i}_vs_orthofloor"]
            sr = r[f"paired_axis{i}_resid_vs_randfloor"]
            so = r[f"paired_axis{i}_resid_vs_orthofloor"]
            att = r[f"attenuation_axis{i}"]
            print(f"    a={r['alpha_rel']:<5} JS_raw={r[f'js_axis{i}_mean']:.3e} "
                  f"JS_res={r[f'js_axis{i}_resid_mean']:.3e} att={att:+.3f} | "
                  f"raw:q_rand={ar['wilcoxon_q_bh']:.4f} d={ar['cliffs_delta']:+.2f} "
                  f"q_orth={ao['wilcoxon_q_bh']:.4f} | "
                  f"res:q_rand={sr['wilcoxon_q_bh']:.4f} d={sr['cliffs_delta']:+.2f} "
                  f"q_orth={so['wilcoxon_q_bh']:.4f} | "
                  f"pplR_res={r[f'ppl_ratio_axis{i}_resid_mean']:.2f}")

print("\n" + "=" * 104)
print("TABLE C - R1: axis-cells whose effect SURVIVES removal of the human VAD "
      "subspace (prereg 10.4)")
print("=" * 104)
print(f"R1_supported = {V['R1_supported']}  "
      f"({len(V['R1_axes_surviving_residualisation'])} axis-cells)")
for e in V["R1_axes_surviving_residualisation"]:
    al = ", ".join(f"a={c['alpha_rel']} (att={c['attenuation']:+.3f}, "
                   f"d={c['resid_vs_rand_delta']:+.2f}, "
                   f"pplR={c['ppl_ratio_resid']:.2f})"
                   for c in e["alphas_passing"])
    print(f"  layer {e['layer']} axis{e['axis']}: repro={e['split_repro']:.3f} "
          f"max|cos|VAD={e['abs_cos_max_vad']:.3f} "
          f"res_ratio={e['residual_norm_ratio']:.3f}")
    print(f"      passing: {al}")

print("\n" + "=" * 104)
print("TABLE D - M1 monotonicity of JS in alpha (Spearman, prereg 6)")
print("=" * 104)
for m in V["M1_monotonicity"]:
    print(f"  layer {m['layer']} axis{m['axis']}: rho={m['spearman_rho']:+.3f} "
          f"p={m['p']:.4f} M1_pass={m['M1_pass']}")

print("\n" + "=" * 104)
print("TABLE E - R3 (alignment vs attenuation)")
print("=" * 104)
print(f"  {json.dumps(V['R3_spearman'], ensure_ascii=False)}")
