"""Print the positive-control tables straight from the run's JSON.

Every number printed here is read from the JSON produced by run_pos_ctrl_v2.py.
Nothing is recomputed or typed by hand.

Usage: python3 summarize_pos_ctrl_v2.py <path-to-pos_ctrl_v2_*.json>
"""
import json
import sys
from pathlib import Path

PV = ("pos_lasttoken_all40", "pos_lasttoken_first30", "pos_meanpool_first30")
SHORT = {"pos_lasttoken_all40": "(a') last/all40",
         "pos_lasttoken_first30": "(a)  last/first30",
         "pos_meanpool_first30": "(b)  meanpool/first30"}

path = Path(sys.argv[1])
d = json.loads(path.read_text())
env = d["env"]
print(f"source          : {path}")
print(f"status          : {env.get('status')}")
print(f"generated_utc   : {env.get('generated_utc')}")
print(f"script_sha256   : {env.get('script_sha256', '')[:16]}…")
print(f"torch/cuda      : {env.get('torch')} / {env.get('cuda')}")
print(f"hostname        : {env.get('hostname')}")
print(f"CVD             : {env.get('CUDA_VISIBLE_DEVICES')}  "
      f"visible uuid: {env.get('gpu_uuid_visible_physical')}")
print(f"judge_llm_loaded: {env.get('judge_llm_loaded')}")
print(f"data_hash       : {env.get('data_hash_stimuli')}")
print(f"BH primary m    : {env.get('primary_bh_family_size')}")
print(f"git_commit      : {env.get('git_commit')}")

print("\n" + "=" * 100)
print("TABLE 1 — layer-level verdict (MAIN condition: last-token hook; "
      "primary BH family)")
print("=" * 100)
print("{:<6}{:<7}{:<19}{:<19}{:<22}".format(
    "layer", "PASS", "(a) last/first30", "(a2) last/all40",
    "(b) meanpool/first30"))
for L in d["layers"]:
    v = L.get("positive_control_verdict")
    if v is None:
        print(f"{L['layer']:<6}(verdict pending — run still IN_PROGRESS)")
        continue
    print(f"{L['layer']:<6}{str(v['LAYER_POSITIVE_CONTROL_PASSES']):<7}"
          f"{str(v['pos_lasttoken_first30']['main_last_token_hook']):<19}"
          f"{str(v['pos_lasttoken_all40']['main_last_token_hook']):<19}"
          f"{str(v['pos_meanpool_first30']['main_last_token_hook']):<22}")

print("\n" + "=" * 118)
print("TABLE 2 — pos vs random floor (mean of 5 random dirs), per layer x alpha "
      "x variant. n=80 = 40 stimuli x 2 polarities")
print("=" * 118)
for L in d["layers"]:
    print(f"\n--- layer {L['layer']}  "
          f"||h_last||={L['last_token_norm_mean']:.1f}"
          f"(sd {L['last_token_norm_std']:.1f})  "
          f"[prereg-v5 meanpool ref {L['meanpool_norm_mean_PREREG_V5_REFERENCE']:.1f}]"
          f"  axis repro top5={[round(x, 3) for x in L['axis_split_repro_top5']]}")
    for scope in ("last_token", "all_positions"):
        tag = "MAIN " if scope == "last_token" else "sec. "
        for r in L["rows"]:
            if r["hook_scope"] != scope:
                continue
            print(f"  {tag}a={r['alpha_rel']:<5} (a_abs≈{r['alpha_abs_mean']:.2f})"
                  f"  JS_randfloor={r['js_randfloor_mean']:.3e}"
                  f"  JS_orthofloor={r['js_orthofloor_mean']:.3e}")
            for pv in PV:
                t = r[f"paired_{pv}_vs_randfloor"]
                o = r[f"paired_{pv}_vs_orthofloor"]
                q = t.get("wilcoxon_q_bh_primary")
                qs = f"{q:.4f}" if isinstance(q, float) else "  -   "
                ql = t.get("wilcoxon_q_bh_within_layer")
                qls = f"{ql:.4f}" if isinstance(ql, float) else "  -   "
                print(f"      {SHORT[pv]:<24} JS={r[f'js_{pv}_mean']:.3e} "
                      f"ratio={r[f'ratio_{pv}_over_randfloor']:.3f} "
                      f"d={t['mean_diff']:+.3e} "
                      f"CI[{t['ci_lo']:+.2e},{t['ci_hi']:+.2e}] "
                      f"delta={t['cliffs_delta']:+.3f} "
                      f"p={t['wilcoxon_p']:.2e} q_prim={qs} "
                      f"q_lay={qls} | "
                      f"vs_ortho d={o['mean_diff']:+.3e} "
                      f"delta={o['cliffs_delta']:+.3f} "
                      f"| beat {r[f'n_rand_draws_beaten_p05_{pv}']}/5 rand, "
                      f"{r[f'n_ortho_draws_beaten_p05_{pv}']}/5 ortho draws")

print("\n" + "=" * 100)
print("TABLE 3 — direction geometry: cos(pos direction, ICA axis i)")
print("=" * 100)
for L in d["layers"]:
    print(f"  layer {L['layer']}")
    for pv, cs in L["cos_pos_vs_axes"].items():
        print(f"    {pv:<24} " + " ".join(f"{c:+.3f}" for c in cs)
              + f"   max|cos|={max(abs(c) for c in cs):.3f}")

print("\n" + "=" * 100)
print("TABLE 4 — positive-control fit sets (D2 guard)")
print("=" * 100)
for L in d["layers"]:
    for pv, fi in L["pos_fit_info"].items():
        print(f"  layer {L['layer']:<3} {pv:<24} n_fit={fi['n_fit']:<3} "
              f"pooling={fi['pooling']:<9} "
              f"valence {fi['valence_min']:.2f}-{fi['valence_max']:.2f} "
              f"(sd {fi['valence_std']:.3f}) "
              f"n_pos_in_fit={fi['n_pos_stimuli_in_fit']} "
              f"dropped={fi['dropped_indices']}")

print("\n" + "=" * 100)
print("TABLE 5 — pooling contrast: JS(last-token pos) vs JS(meanpool pos), "
      "same stimuli 0-29, two-sided")
print("=" * 100)
for L in d["layers"]:
    for r in L["rows"]:
        t = r["paired_lasttoken_vs_meanpool_first30"]
        print(f"  layer {L['layer']:<3} {r['hook_scope']:<14} a={r['alpha_rel']:<5} "
              f"d={t['mean_diff']:+.3e} CI[{t['ci_lo']:+.2e},{t['ci_hi']:+.2e}] "
              f"delta={t['cliffs_delta']:+.3f} p={t['wilcoxon_p']:.3e}")
