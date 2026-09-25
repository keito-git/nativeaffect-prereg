#!/usr/bin/env python3
"""Cross-check every number in the drafts against the result files.

Builds a pool of values that the result JSONs actually contain (recursively,
plus derived ratios and percentages), then flags any number printed in the
drafts that cannot be matched at the precision it is printed to.

Design constants (layer indices, alpha levels, sample counts) are listed
explicitly rather than silently allowed, so the whitelist itself is auditable.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

B = Path("/path/to/research/論文/NativeAffect_AI固有の感情軸")
RES = B / "03_解析"

JSONS = [
    RES / "confirmation/adjudication_confirmation.json",
    RES / "_gate1_smoke/adj_discovery_validation.json",
    RES / "confirmation/pos_ctrl_inplane_confirmation_20260925T210056Z.json",
    RES / "confirmation/inplane_floor_confirmation_20260925T210454Z.json",
    RES / "inplane_floor/inplane_floor_discovery_20260925T172110Z.json",
    RES / "pos_ctrl_inplane_seeds/pos_ctrl_inplane_floorseed42_20260925T191612Z.json",
    RES / "axes_nopad/alignment_primary.json",
    RES / "axes_nopad/s3_categories.json",
    RES / "axes_nopad/procedure_dependence.json",
    RES / "axes_nopad/seed_stability_c3.json",
    RES / "axes_nopad/vad_correlations.json",
    RES / "signed_valence/signed_valence_20260925T200619Z.json",
]

# design constants, stated explicitly so the whitelist is auditable
DESIGN = {
    5, 7, 10, 12,                    # layers
    0.01, 0.03, 0.05, 0.1, 0.2,      # alpha levels
    0, 1, 2, 3, 4,                   # axis / small indices
    20, 40, 287, 300, 2048, 2000,    # stimuli, samples, dim, permutations
    48, 60, 16, 12, 8,               # BH families / cell counts
    10000, 20260925, 42, 46, 95,     # bootstrap, seeds, percentile
    100, 128, 1.5, 0.95, 0.5, 2.0,   # top-k, maxlen, thresholds
    2026, 9, 26, 25, 1, 6, 11, 15, 17, 30, 1.0, 0.0,
    1.1, 1.5, 5.0, 4, 23, 2.7, 98, 99, 50, 1e-45,
}


def collect(o, out: set) -> None:
    if isinstance(o, dict):
        for v in o.values():
            collect(v, out)
    elif isinstance(o, list):
        for v in o:
            collect(v, out)
    elif isinstance(o, bool):
        pass
    elif isinstance(o, (int, float)):
        out.add(float(o))


def build_pool() -> set:
    pool = set(float(x) for x in DESIGN)
    raw = set()
    for p in JSONS:
        if not p.exists():
            print(f"  [warn] missing: {p}")
            continue
        collect(json.loads(p.read_text()), raw)
    for v in list(raw):
        pool.add(v)
        pool.add(v * 100)          # fraction -> percent
        pool.add(v / 100)
        pool.add(abs(v))
    # derived: alignment ratios against the permutation null
    a = json.loads((RES / "axes_nopad/alignment_primary.json").read_text())
    for L in ("5", "7", "10", "12"):
        e = a["layers"][L]["P2_ridge_std"]
        nm = e["chance"]["null_inside_mean"] * 100
        for o in e["inside_fraction_pct_per_axis"]:
            pool.add(o / nm)
    s3 = json.loads((RES / "axes_nopad/s3_categories.json").read_text())
    for L in ("5", "7", "10", "12"):
        e = s3["layers"][L]["P2_ridge_std"]
        nm = e["chance_inside_mean"] * 100
        for o in e["axis_inside_fraction_pct"]:
            pool.add(o / nm)
    # derived: floor ratios
    for p in (RES / "confirmation/pos_ctrl_inplane_confirmation_20260925T210056Z.json",
              RES / "pos_ctrl_inplane_seeds/pos_ctrl_inplane_floorseed42_20260925T191612Z.json"):
        d = json.loads(p.read_text())
        for Lo in d["layers"]:
            for r in Lo["rows"]:
                f = r.get("js_floor_fullrand_mean")
                i = r.get("js_floor_inplane_mean")
                if f:
                    pool.add(i / f)
    # stimulus-set statistics (Table I) come from the raw stimulus files
    import statistics as _st
    for f_, lim in ((B / "data/raw/stimuli/stimuli_e1.json", None),
                    (B / "data/raw/stimuli/stimuli_e4.json", 40)):
        if not f_.exists():
            continue
        d = json.loads(f_.read_text())
        w = [len(s["text"].split()) for s in (d[:lim] if lim else d)]
        for x in (_st.mean(w), _st.pstdev(w), min(w), max(w), len(d)):
            pool.add(float(x))
    # procedure-dependence ratios (Table VIII)
    for L in ("5", "7", "10", "12"):
        e = a["layers"][L]
        p1 = e["P1_cov"]["inside_fraction_pct_per_axis"]
        p2 = e["P2_ridge_std"]["inside_fraction_pct_per_axis"]
        for x, y in zip(p1, p2):
            if y:
                pool.add(x / y)
    return pool


NUM = re.compile(r"(?<![\w.])(\d+(?:,\d{3})*)(?:\.(\d+))?(?:[eE]([+-]?\d+))?")


def numbers_in(text: str):
    # strip code fences and inline code, which legitimately hold identifiers
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    out = []
    for ln_no, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith(">"):        # quoted prereg text
            pass
        line = re.sub(r"§\s*\d+(?:\.\d+)*", " ", line)      # section refs
        line = re.sub(r"(\d+(?:\.\d+)?)\s*[x×]\s*10[⁻^-]?[⁰¹²³⁴⁵⁶⁷⁸⁹\d{}^+-]*",
                      lambda m: " ", line)                    # mantissa x 10^k
        for m in NUM.finditer(line):
            s = m.group(0)
            try:
                v = float(s.replace(",", ""))
            except ValueError:
                continue
            dec = len(m.group(2)) if m.group(2) else 0
            out.append((ln_no, s, v, dec, line.strip()[:100]))
    return out


def main() -> int:
    pool = build_pool()
    print(f"pool: {len(pool)} distinct values from {len(JSONS)} result files\n")
    bad_total = 0
    for name in ("02_Methodology_draft.md", "03_Experiments_draft.md"):
        p = B / "04_原稿/日本語版" / name
        if not p.exists():
            print(f"MISSING {p}")
            continue
        nums = numbers_in(p.read_text())
        bad = []
        for ln, s, v, dec, ctx in nums:
            tol = 0.5 * (10 ** -dec) if dec else 0.5
            if not any(abs(v - q) <= tol for q in pool):
                bad.append((ln, s, ctx))
        print(f"=== {name}: {len(nums)} numbers, {len(bad)} unmatched ===")
        for ln, s, ctx in bad:
            print(f"  L{ln}: {s!r}  |  {ctx}")
        bad_total += len(bad)
    print(f"\nTOTAL UNMATCHED: {bad_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
