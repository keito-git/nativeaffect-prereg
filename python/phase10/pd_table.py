"""Print the procedure-dependence table from the JSON."""
import json
from pathlib import Path

P = ("P1_cov", "P2_ridge_std", "P3_ridge_raw", "P4_pca50_ridge")
d = json.loads(Path("/path/to/work/results/axes_nopad/"
                    "procedure_dependence.json").read_text())
print("layer target      mean|cos|  min    max   | holdout r: P1 / P2 / P3 / P4")
worst = 1.0
for L in sorted(d["layers"], key=int):
    for t, e in d["layers"][L]["S2"]["targets"].items():
        v = e["validity_per_procedure"]
        rs = " / ".join(f"{v[p]['holdout_r']:+.3f}" for p in P)
        print(f"{L:>5} {t:<11} {e['mean_abs_cos_offdiag']:.3f}      "
              f"{e['min_abs_cos_offdiag']:.3f}  {e['max_abs_cos_offdiag']:.3f} | {rs}")
        worst = min(worst, e["min_abs_cos_offdiag"])
print(f"\nworst pairwise |cos| over all S2 targets/layers: {worst:.3f}")

print("\ncos(P1_cov, other procedures)  [P1 is what regress_dir uses]:")
for L in sorted(d["layers"], key=int):
    for t, e in d["layers"][L]["S2"]["targets"].items():
        m = e["abs_cos_matrix"]["P1_cov"]
        print(f"  L{L:<3} {t:<11} P2={m['P2_ridge_std']:.3f} "
              f"P3={m['P3_ridge_raw']:.3f} P4={m['P4_pca50_ridge']:.3f}")

print("\nholdout r by procedure, averaged over layers and targets:")
for p in P:
    vals = [d["layers"][L]["S2"]["targets"][t]["validity_per_procedure"][p]
            ["holdout_r"]
            for L in d["layers"] for t in d["layers"][L]["S2"]["targets"]]
    print(f"  {p:<15} mean={sum(vals)/len(vals):+.3f} "
          f"min={min(vals):+.3f} max={max(vals):+.3f}")
