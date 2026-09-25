"""S3 category results table, from the JSON."""
import json
from pathlib import Path

d = json.loads(Path("/path/to/work/results/axes_nopad/"
                    "s3_categories.json").read_text())
print(f"n_categories={d['env']['n_categories']} n_heldout={d['env']['n_heldout']} "
      f"n_perm={d['env']['n_perm']} gpu_used={d['env']['gpu_used']}")

print("\n=== generalisation + subspace rank ===")
print(f"{'layer':<6}{'proc':<14}{'gen':<8}{'holdout r min/med/max':<26}"
      f"{'effrank10':<11}{'particip.':<10}")
for L in sorted(d["layers"], key=int):
    for p in ("P1_cov", "P2_ridge_std"):
        e = d["layers"][L][p]
        print(f"{L:<6}{p:<14}{e['n_generalising']}/{e['n_total']:<6}"
              f"{str(e['holdout_r_min_med_max']):<26}"
              f"{e['subspace_eff_rank_10pct']:<11}{e['subspace_participation']:<10}")

print("\n=== how much of each ICA axis lies inside the CATEGORY subspace ===")
for L in sorted(d["layers"], key=int):
    for p in ("P1_cov", "P2_ridge_std"):
        e = d["layers"][L][p]
        print(f"  L{L:<3} {p:<14} inside%={e['axis_inside_fraction_pct']} "
              f"chance={100*e['chance_inside_mean']:.3f}% "
              f"p={[round(x,4) for x in e['axis_inside_p_vs_chance']]}")

print("\n=== mechanism: category dirs inside the top-10 PC span (median) ===")
for L in sorted(d["layers"], key=int):
    row = " ".join(f"{p}={d['layers'][L][p]['category_dir_inside_top10PC_median']}"
                   for p in ("P1_cov", "P2_ridge_std"))
    print(f"  L{L:<3} {row}")

print("\n=== PD2: procedure dependence of the category directions ===")
print("  (prereg 21.3 predicted these would EXCEED S2's; S2's cos(P1,P2) was "
      "0.733-0.847)")
for L in sorted(d["layers"], key=int):
    s = d["layers"][L]["PD2_summary"]
    print(f"  L{L:<3} cos(P1,P2) median={s['median']} min={s['min']} max={s['max']}")
