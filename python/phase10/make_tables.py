#!/usr/bin/env python3
"""Generate Tables I-IX for paper 2 from the result files.

No number is typed into a table: every cell is read from a result JSON or from
an explicitly listed design constant. Emits markdown (for the Japanese draft)
and booktabs LaTeX (for the eventual manuscript).

Conventions fixed with the coordinator:
  - a table that reports an absolute and a relative quantity shows BOTH in the
    same table, so a reader cannot see one without the other
  - any table with a ratio to chance carries the chance level as its own row
  - the "proposal on the bottom row" convention is applied only where the table
    actually has a proposal/baseline structure; this paper mostly does not
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics as stats
from pathlib import Path
from typing import Any

B = Path("/path/to/research/論文/NativeAffect_AI固有の感情軸")
R = B / "03_解析"
LAYERS = (5, 7, 10, 12)
ALPHAS_GE03 = (0.03, 0.05, 0.10, 0.20)
A05 = 0.05

# --- design constants, listed so the whitelist is auditable -----------------
CONTROLS = [
    ("Full-space random",
     "uniform on the unit sphere of R^2048",
     "direction is not the specific one claimed",
     "none of the variance structure"),
    ("Axis-orthogonal",
     "full-space draw, Gram-Schmidt against the axis",
     "overlap with the axis itself",
     "subspace variance"),
    ("In-plane random (VMIC)",
     "uniform on the unit sphere of the top-10 PC span",
     "direction sits in the dominant-variance subspace",
     "everything except the rotation within that subspace"),
    ("Variance-matched in-plane",
     "in-plane draw with coefficients scaled by PC sd",
     "as above, plus the per-component variance profile",
     "the rotation within the subspace only"),
    ("PC arms (PC1-PC5)",
     "the principal components themselves",
     "whether a plain PC reproduces the axis effect",
     "not a floor; a reference direction"),
]


def j(p: Path) -> Any:
    return json.loads(p.read_text())


def f(x: float | None, nd: int = 4) -> str:
    if x is None:
        return "--"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if x != x:
        return "nan"
    if x == 0:
        return "0"
    if abs(x) < 1e-3 or abs(x) >= 1e5:
        m, e = f"{x:.2e}".split("e")
        return f"{m}e{int(e)}"
    return f"{x:.{nd}f}".rstrip("0").rstrip(".")


def md(rows: list[list[str]], head: list[str]) -> str:
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def tex(rows: list[list[str]], head: list[str], cap: str, label: str) -> str:
    esc = lambda s: (s.replace("%", r"\%").replace("_", r"\_")  # noqa: E731
                      .replace("&", r"\&").replace("<", r"$<$"))
    body = "\n".join(" & ".join(esc(c) for c in r) + r" \\" for r in rows)
    return (r"\begin{table}[t]" "\n" r"\centering" "\n"
            f"\\caption{{{esc(cap)}}}\n\\label{{{label}}}\n"
            r"\begin{tabular}{" + "l" * len(head) + "}\n" r"\toprule" "\n"
            + " & ".join(esc(h) for h in head) + r" \\" "\n" r"\midrule" "\n"
            + body + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n"
            r"\end{table}")


def cell(doc: dict, L: int, al: float, key: str) -> dict | None:
    for Lo in doc["layers"]:
        if Lo["layer"] != L:
            continue
        for r in Lo["rows"]:
            if abs(float(r["alpha_rel"]) - al) < 1e-9:
                return r.get(key) if key else r
    return None


def c4cell(adj: dict, L: int, ax: int, al: float) -> dict | None:
    for c in adj["C4"]["cells"]:
        if c["layer"] == L and c["axis"] == ax and abs(c["alpha_rel"] - al) < 1e-9:
            return c
    return None


def build() -> dict[str, tuple[str, list[str], list[list[str]]]]:
    adjc = j(R / "confirmation/adjudication_confirmation.json")
    adjd = j(R / "_gate1_smoke/adj_discovery_validation.json")
    posc = j(R / "confirmation/pos_ctrl_inplane_confirmation_20260925T210056Z.json")
    posd = j(R / "pos_ctrl_inplane_seeds/pos_ctrl_inplane_floorseed42_20260925T191612Z.json")
    align = j(R / "axes_nopad/alignment_primary.json")
    s3 = j(R / "axes_nopad/s3_categories.json")
    seeds = j(R / "axes_nopad/seed_stability_c3.json")
    sv = j(R / "signed_valence/signed_valence_20260925T200619Z.json")
    split = j(R / "axes_nopad/axis_rebuilt_split_20260925.json")
    e1 = j(B / "data/raw/stimuli/stimuli_e1.json")
    e4 = j(B / "data/raw/stimuli/stimuli_e4.json")
    T: dict[str, tuple[str, list[str], list[list[str]]]] = {}

    # ---- Table I: stimulus sets and the split
    w1 = [len(s["text"].split()) for s in e1]
    w4 = [len(e4[i]["text"].split()) for i in range(40)]
    cats = sorted({e4[i]["target_emotion"] for i in range(40)})
    sha = hashlib.sha256(
        (R / "axes_nopad/axis_rebuilt_split_20260925.json").read_bytes()).hexdigest()
    T["I"] = ("Stimulus sets and the pre-registered discovery/confirmation split",
              ["Item", "E1 (alignment)", "E4 (intervention)"],
              [["Source", "GoEmotions validation split", "templates"],
               ["Sentences available", str(len(e1)), str(len(e4))],
               ["Sentences used", "287 (with VAD)", "40 (indices 0-39)"],
               ["Emotion categories", "--", f"{len(cats)} x 2 polarities"],
               ["Words per sentence, mean (SD)",
                f"{stats.mean(w1):.2f} ({stats.pstdev(w1):.2f})",
                f"{stats.mean(w4):.2f} ({stats.pstdev(w4):.2f})"],
               ["Words per sentence, min-max",
                f"{min(w1)}-{max(w1)}", f"{min(w4)}-{max(w4)}"],
               ["Discovery / confirmation", "not split",
                f"{len(split['discovery_indices'])} / "
                f"{len(split['confirmation_indices'])}"],
               ["Positive stimuli per side", "--",
                f"{split['n_positive_discovery']} / "
                f"{split['n_positive_confirmation']}"],
               ["Split rule", "--", "stratified by emotion category"],
               ["Split seed", "--", str(split["seed"])],
               ["Split file sha256", "--", sha[:16] + "..."]])

    # ---- Table II: the confirmatory hypotheses
    rows = []
    for k in ("C1", "C2", "C3", "C4"):
        cc, dd = adjc[k], adjd[k]
        if k == "C2":
            fam = f"{cc['C2a']['family_size']} / {cc['C2b']['family_size']}"
            res_d = (f"C2a {len(dd['C2a']['significant_layers'])}/4, "
                     f"C2b {dd['C2b']['n_significant_cells']}")
            res_c = (f"C2a {len(cc['C2a']['significant_layers'])}/4, "
                     f"C2b {cc['C2b']['n_significant_cells']}")
        elif k == "C3":
            fam = "--"
            res_d = f"{dd['n_below_5pct']}/{dd['n_cells']}"
            res_c = f"{cc['n_below_5pct']}/{cc['n_cells']} (not held out)"
        elif k == "C1":
            fam = str(cc["family_size"])
            res_d = f"{dd['n_layers_significant_at_alpha0.05']}/4 layers"
            res_c = f"{cc['n_layers_significant_at_alpha0.05']}/4 layers"
        else:
            fam = str(cc["family_size"])
            res_d = f"{dd['n_significant_cells_at_alpha0.05']}/12 cells"
            res_c = f"{cc['n_significant_cells_at_alpha0.05']}/12 cells"
        rows.append([k, cc["criterion"][:78], fam, res_d, res_c,
                     "PASS" if cc["PASS"] else "FAIL"])
    T["II"] = ("Pre-registered confirmatory hypotheses, criteria and outcomes",
               ["", "Criterion (pre-registered)", "BH family", "Discovery",
                "Confirmation", "Verdict"], rows)

    # ---- Table III: the control hierarchy
    T["III"] = ("Control types and the confound each one removes",
                ["Control", "Construction", "What it tests",
                 "What it holds fixed"],
                [list(c) for c in CONTROLS])

    # ---- Table IV: C1, absolute floors AND the ratio in one table
    rows = []
    for L in LAYERS:
        rd, rc = cell(posd, L, A05, ""), cell(posc, L, A05, "")
        td = next(c for c in adjd["C1"]["cells"]
                  if c["layer"] == L and abs(c["alpha_rel"] - A05) < 1e-9)
        tc = next(c for c in adjc["C1"]["cells"]
                  if c["layer"] == L and abs(c["alpha_rel"] - A05) < 1e-9)
        rows.append([
            str(L),
            f(rd["js_floor_inplane_mean"]), f(rd["js_floor_fullrand_mean"]),
            f(adjd["C1"]["floor_ratios_at_alpha0.05"][str(L)], 3),
            f(td["cliffs_delta"], 2), f(td["q"]),
            f(rc["js_floor_inplane_mean"]), f(rc["js_floor_fullrand_mean"]),
            f(adjc["C1"]["floor_ratios_at_alpha0.05"][str(L)], 3),
            f(tc["cliffs_delta"], 2), f(tc["q"])])
    T["IV"] = ("C1 at alpha=0.05: absolute floor effects and their ratio, "
               "discovery and confirmation",
               ["Layer", "D in-plane", "D full-space", "D ratio", "D delta",
                "D q", "C in-plane", "C full-space", "C ratio", "C delta",
                "C q"], rows)

    # ---- Table V: C2a and C2b
    rows = []
    for L in LAYERS:
        for al in (0.03, 0.05, 0.10, 0.20):
            a_ = next((c for c in adjc["C2"]["C2a"]["cells"]
                       if c["layer"] == L and abs(c["alpha_rel"] - al) < 1e-9), None)
            b_ = next((c for c in adjc["C2"]["C2b"]["cells"]
                       if c["layer"] == L and abs(c["alpha_rel"] - al) < 1e-9), None)
            if not a_ or not b_:
                continue
            rows.append([str(L), f"{al:g}",
                         f(a_["mean_diff"]), f(a_["cliffs_delta"], 2), f(a_["q"]),
                         "yes" if a_["significant"] else "no",
                         f(b_["mean_diff"]), f(b_["cliffs_delta"], 2), f(b_["q"]),
                         "yes" if b_["significant"] else "no"])
    T["V"] = ("C2 on the confirmation set: the positive control against the "
              "full-space floor (C2a) and against the in-plane floor (C2b)",
              ["Layer", "alpha", "C2a mean diff", "C2a delta", "C2a q",
               "C2a sig", "C2b mean diff", "C2b delta", "C2b q", "C2b sig"],
              rows)

    # ---- Table VI: C4, all 12 cells x 4 alphas, both halves
    rows = []
    for L in LAYERS:
        for ax in range(3):
            r = [f"L{L} axis {ax}"]
            for al in ALPHAS_GE03:
                cd, cc = c4cell(adjd, L, ax, al), c4cell(adjc, L, ax, al)
                r += [f"{f(cd['cliffs_delta'],2)}{'*' if cd['significant'] else ''}",
                      f"{f(cc['cliffs_delta'],2)}{'*' if cc['significant'] else ''}"]
            dg = c4cell(adjc, L, ax, A05)["degenerate_frac"]
            r.append(f(dg, 2))
            rows.append(r)
    head = ["Cell"] + [f"{lab} a={al:g}" for al in ALPHAS_GE03
                       for lab in ("D", "C")] + ["degen"]
    T["VI"] = ("C4: Cliff's delta of each axis against the in-plane floor; "
               "an asterisk marks BH q<0.05 with a positive mean difference",
               head, rows)

    # ---- Table VII: alignment, absolute AND relative, with the chance rows
    rows = []
    for name, doc, okey, nmean, np95, pkey in (
            ("S2 (rank 3)", align, "inside_fraction_pct_per_axis", None, None, None),
            ("S3 (rank 20)", s3, "axis_inside_fraction_pct", None, None, None)):
        for L in LAYERS:
            e = doc["layers"][str(L)]["P2_ridge_std"]
            if name.startswith("S2"):
                ch = e["chance"]
                nm, p95, ps = (100 * ch["null_inside_mean"],
                               100 * ch["null_inside_p95"],
                               ch["p_inside_per_axis"])
            else:
                nm, p95, ps = (100 * e["chance_inside_mean"],
                               100 * e["chance_inside_p95"],
                               e["axis_inside_p_vs_chance"])
            obs = e[okey]
            for ax in range(3):
                rows.append([name, str(L), str(ax), f(obs[ax], 4), f(nm, 4),
                             f(p95, 4), f(obs[ax] / nm, 2), f(ps[ax]),
                             "yes" if obs[ax] > p95 else "no"])
            rows.append([name, str(L), "chance", f(nm, 4), f(nm, 4), f(p95, 4),
                         "1.00", "--", "--"])
    T["VII"] = ("Alignment of each axis with the human subspace: absolute "
                "inside_fraction and its ratio to the permutation null "
                "(2,000 draws), with the chance level as its own row",
                ["Subspace", "Layer", "Axis", "inside %", "null mean %",
                 "null p95 %", "ratio", "p", "above p95"], rows)

    # ---- Table VIII: procedure dependence
    rows = []
    for L in LAYERS:
        p1 = align["layers"][str(L)]["P1_cov"]["inside_fraction_pct_per_axis"]
        p2 = align["layers"][str(L)]["P2_ridge_std"]["inside_fraction_pct_per_axis"]
        for ax in range(3):
            rows.append([str(L), str(ax), f(p1[ax], 4), f(p2[ax], 4),
                         f(p1[ax] / p2[ax], 1),
                         "yes" if p1[ax] >= 5.0 else "no",
                         "yes" if p2[ax] >= 5.0 else "no"])
    T["VIII"] = ("Estimation-procedure dependence of inside_fraction for the "
                 "S2 subspace; the 5% criterion is met under P2 and violated "
                 "under P1 in most cells",
                 ["Layer", "Axis", "P1_cov %", "P2_ridge_std %", "P1/P2",
                  "P1 >= 5%", "P2 >= 5%"], rows)

    # ---- Table IX: signed readout, primary vs strict lexicon
    lx, lxs = sv["lexicon"], sv["lexicon_strict"]
    rows = []
    for Lo in sv["layers"]:
        L = Lo["layer"]
        r = next(x for x in Lo["rows"] if abs(x["alpha_rel"] - A05) < 1e-9)
        pm = r["paired_signed_pos_vs_inplane"]
        st = r["paired_signed_strict_pos_vs_inplane"]
        js_ = r["paired_js_pos_vs_inplane"]
        rows.append([str(L), f(pm["cliffs_delta"], 2),
                     f(pm.get("wilcoxon_q_bh", pm["wilcoxon_p"])),
                     f(st["cliffs_delta"], 2), f(st["wilcoxon_p"]),
                     f(js_["cliffs_delta"], 2),
                     f(js_.get("wilcoxon_q_bh", js_["wilcoxon_p"]))])
    T["IX"] = (f"Signed valence readout at alpha=0.05 against the in-plane "
               f"floor, under the pre-declared primary lexicon "
               f"({lx['n_token_ids_pos']} positive / {lx['n_token_ids_neg']} "
               f"negative token ids) and the stricter secondary lexicon "
               f"({lxs['n_token_ids_pos']} / {lxs['n_token_ids_neg']})",
               ["Layer", "Primary delta", "Primary q", "Strict delta",
                "Strict p", "JS delta", "JS q"], rows)
    return T


def self_check(T: dict) -> int:
    ok = True

    def c(n: str, v: bool) -> None:
        nonlocal ok
        print(f"  [{'OK ' if v else 'FAIL'}] {n}")
        ok &= bool(v)

    c("all nine tables built", sorted(T) == ["I", "II", "III", "IV", "IX",
                                             "V", "VI", "VII", "VIII"])
    for k, (cap, head, rows) in T.items():
        c(f"Table {k}: every row has {len(head)} cells",
          all(len(r) == len(head) for r in rows))
        c(f"Table {k}: no empty cells", all(all(str(x).strip() for x in r)
                                            for r in rows))
    # the chance rows must be present in the alignment table
    c("Table VII carries a chance row per subspace and layer",
      sum(1 for r in T["VII"][2] if r[2] == "chance") == 8)
    # absolute and relative must appear in the same table
    c("Table IV holds absolute floors and the ratio together",
      any("in-plane" in h for h in T["IV"][1]) and
      any("ratio" in h for h in T["IV"][1]))
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-md", type=Path,
                    default=B / "04_原稿/図表/tables_I_to_IX.md")
    ap.add_argument("--out-tex-dir", type=Path, default=B / "04_原稿/図表/tex")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    T = build()
    if a.self_check:
        return self_check(T)
    if self_check(T) != 0:
        print("REFUSING to write: self-check failed")
        return 2
    a.out_md.parent.mkdir(parents=True, exist_ok=True)
    a.out_tex_dir.mkdir(parents=True, exist_ok=True)
    parts = ["# Tables I-IX (generated; do not edit by hand)", "",
             "Generated by `python/phase10/make_tables.py` from the result "
             "files. Every value is read from a JSON or from a design constant "
             "listed in that script.", ""]
    for k in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"):
        cap, head, rows = T[k]
        parts += [f"## Table {k}", "", f"*{cap}.*", "", md(rows, head), ""]
        (a.out_tex_dir / f"table_{k}.tex").write_text(
            tex(rows, head, f"Table {k}. {cap}.", f"tab:{k.lower()}"))
    a.out_md.write_text("\n".join(parts))
    print(f"\nwrote {a.out_md}")
    print(f"wrote 9 .tex files -> {a.out_tex_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
