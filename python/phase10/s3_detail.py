"""S3 residual results at alpha=0.05 and the R1-per-tier summary."""
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text())
V = d["verdicts"]
print("R1 per tier:")
for t in ("S1", "S2", "S3"):
    b = V["R1_by_tier"][t]
    print(f"  {t}: supported={b['supported']} cells={b['n_cells_surviving']}")
print(f"M3' degenerate cells: {len(V['M3prime_degenerate'])}")

print("\nS3 residual-axis test, alpha=0.05 (S3 = VAD + 20 category dirs, "
      "eff rank 22):")
for L in d["layers"]:
    for r in L["rows"]:
        if r["alpha_rel"] != 0.05:
            continue
        print(f"  layer {L['layer']}:")
        for i in range(3):
            s = r[f"paired_axis{i}_resid_S3_vs_randfloor"]
            o = r[f"paired_axis{i}_resid_S3_vs_orthofloor"]
            print(f"    axis{i}: residS3 JS={r[f'js_axis{i}_resid_S3_mean']:.3e} "
                  f"att={r[f'attenuation_axis{i}_S3']:+.3f} "
                  f"norm_ratio={r[f'residual_norm_ratio_axis{i}_S3']:.3f} "
                  f"q_rand={s['wilcoxon_q_bh']:.4f} d={s['cliffs_delta']:+.2f} "
                  f"q_orth={o['wilcoxon_q_bh']:.4f} "
                  f"degen={r[f'degenerate_frac_axis{i}_resid_S3']:.2f}")

print("\nS3 cells surviving (per tier list), layer/axis/alpha:")
cells = V["R1_by_tier"]["S3"]["cells"]
by = {}
for c in cells:
    by.setdefault((c["layer"], c["axis"]), []).append(c["alpha_rel"])
for k in sorted(by):
    print(f"  layer {k[0]} axis{k[1]}: alphas {sorted(by[k])}")
