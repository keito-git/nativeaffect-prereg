"""C1/C2 seed stability from the five floor-seed runs."""
import glob
import json
from pathlib import Path

files = sorted(glob.glob("/path/to/work/results/pos_ctrl_inplane_seeds/"
                         "pos_ctrl_inplane_floorseed*.json"))
print(f"{len(files)} seed runs\n")
print("=== C2 (conjunction) per seed ===")
for f in files:
    d = json.loads(Path(f).read_text())
    V = d["VERDICT"]
    sd = d["env"].get("floor_seed_arg")
    print(f"  seed {sd}: C2a pos>fullrand = {V['pos_beats_fullrand']} "
          f"({len(V['pos_beats_fullrand_cells'])} cells) | "
          f"C2b pos NOT> inplane = {not V['pos_beats_inplane']} "
          f"({len(V['pos_beats_inplane_cells'])} cells) | "
          f"reading={V['DISCRIMINATOR_READING'][:1]}")

print("\n=== C1 part (b): floor ratio inplane/fullrand at each alpha ===")
print("   (criterion: ratio >= 1.5 in ALL 4 layers at alpha=0.05)")
for f in files:
    d = json.loads(Path(f).read_text())
    sd = d["env"].get("floor_seed_arg")
    print(f"\n  seed {sd}")
    for L in d["layers"]:
        r05 = [r for r in L["rows"] if r["alpha_rel"] == 0.05][0]
        ratio05 = r05["js_floor_inplane_mean"] / r05["js_floor_fullrand_mean"]
        alls = " ".join(
            f"a{r['alpha_rel']}={r['js_floor_inplane_mean']/r['js_floor_fullrand_mean']:.2f}"
            for r in L["rows"])
        flag = "OK" if ratio05 >= 1.5 else "FAIL"
        print(f"    L{L['layer']:<3} a=0.05 ratio={ratio05:.2f} [{flag}] | all: {alls}")

print("\n=== C1 part (b) summary: min ratio at alpha=0.05 over layers, per seed ===")
allpass = True
for f in files:
    d = json.loads(Path(f).read_text())
    sd = d["env"].get("floor_seed_arg")
    mins = min((r["js_floor_inplane_mean"] / r["js_floor_fullrand_mean"])
               for L in d["layers"] for r in L["rows"] if r["alpha_rel"] == 0.05)
    ok = mins >= 1.5
    allpass &= ok
    print(f"  seed {sd}: min ratio = {mins:.2f} -> {'PASS' if ok else 'FAIL'}")
print(f"\nC1 part (b) passes all seeds: {allpass}")
print("\nNOTE: C1 part (a), the paired Wilcoxon between the two floors, is NOT")
print("computable from these files: only floor MEANS were stored, not per-sample")
print("values. The script has to be extended before the confirmation run.")
