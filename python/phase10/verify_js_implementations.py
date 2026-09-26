#!/usr/bin/env python3
"""Prove the JS implementations scattered across the scripts agree numerically.

Nine scripts define their own next-token JS function under four different names
(`js`, `js_div`, `js_divergence`) and two different key spellings (`_i`/`_l` and
`_idx`/`_logp`). Reading them suggests they are the same algorithm, but results
produced by different scripts have been compared with each other, so "suggests"
is not enough: if two of them differed, those comparisons were never comparisons.

This extracts every definition, executes each in isolation, and runs all of them
on identical inputs, including the cases where the two supports do not coincide.
It reports the maximum disagreement rather than a pass/fail on inspection.

    python3 verify_js_implementations.py [--write]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np

CODE = Path("/path/to/research/論文/"
            "NativeAffect_AI固有の感情軸/python/phase10")
OUT = Path("/path/to/research/論文/"
           "NativeAffect_AI固有の感情軸/03_解析/plan_b/js_implementation_equivalence.json")
NAME_RE = re.compile(r"js|js_div|js_divergence|_js")


def collect() -> list[tuple[str, str, Callable]]:
    """Compile each JS definition on its own, with numpy and Any in scope."""
    found = []
    for p in sorted(CODE.glob("*.py")):
        src = p.read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and NAME_RE.fullmatch(node.name):
                seg = ast.get_source_segment(src, node)
                if seg is None:
                    continue
                ns: dict[str, Any] = {"np": np, "Any": Any}
                exec(compile(seg, f"<{p.name}:{node.name}>", "exec"), ns)  # noqa: S102
                found.append((p.name, node.name, ns[node.name]))
    return found


def both_spellings(idx: np.ndarray, logp: np.ndarray) -> dict[str, Any]:
    """One dict carrying both key conventions, so every variant can read it."""
    return {"_i": idx, "_l": logp, "_idx": idx, "_logp": logp}


def cases(rng: np.random.Generator, k: int = 100, vocab: int = 151936):
    """Input pairs, including disjoint and partially overlapping supports."""
    out = []

    def mk(i1, i2):
        i1 = np.sort(np.asarray(i1)); i2 = np.sort(np.asarray(i2))
        l1 = np.log(rng.dirichlet(np.ones(i1.size)))
        l2 = np.log(rng.dirichlet(np.ones(i2.size)))
        return both_spellings(i1, l1), both_spellings(i2, l2)

    base = rng.choice(vocab, size=k, replace=False)
    out.append(("identical supports", *mk(base, base)))
    shifted = np.concatenate([base[: k // 2],
                              rng.choice(np.setdiff1d(np.arange(vocab), base),
                                         size=k - k // 2, replace=False)])
    out.append(("half-overlapping supports", *mk(base, shifted)))
    disjoint = rng.choice(np.setdiff1d(np.arange(vocab), base), size=k, replace=False)
    out.append(("disjoint supports", *mk(base, disjoint)))
    out.append(("tiny supports (k=3)", *mk(base[:3], base[1:4])))
    # an identical distribution on both sides: JS must be ~0
    idx = np.sort(rng.choice(vocab, size=k, replace=False))
    lp = np.log(rng.dirichlet(np.ones(k)))
    out.append(("same distribution", both_spellings(idx, lp), both_spellings(idx, lp)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    impls = collect()
    print(f"found {len(impls)} JS definitions:")
    for f, n, _ in impls:
        print(f"  {f}:{n}")
    if len(impls) < 2:
        raise SystemExit("REFUSING: fewer than two definitions found; the "
                         "extraction is broken, not the code")

    rng = np.random.default_rng(20260926)
    rows, worst = [], 0.0
    for label, m1, m2 in cases(rng):
        vals = {}
        for f, n, fn in impls:
            vals[f"{f}:{n}"] = float(fn(m1, m2))
        v = np.array(list(vals.values()))
        spread = float(v.max() - v.min())
        worst = max(worst, spread)
        rows.append({"case": label, "values": vals, "max_minus_min": spread,
                     "value": float(v[0])})
        print(f"  {label:<28} JS={v[0]:.12f}  spread={spread:.3e}")

    # sanity anchors that do not depend on agreement
    same = [r for r in rows if r["case"] == "same distribution"][0]["value"]
    disj = [r for r in rows if r["case"] == "disjoint supports"][0]["value"]
    ln2 = float(np.log(2))
    print(f"\n  identical distributions -> JS = {same:.3e} (expected 0)")
    print(f"  disjoint supports       -> JS = {disj:.12f} (expected ln2 = {ln2:.12f})")

    ok = (worst < 1e-12 and same < 1e-12 and abs(disj - ln2) < 1e-9)
    doc = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": ("verify that the JS implementations copied across scripts "
                    "agree, since results from different scripts are compared"),
        "n_definitions": len(impls),
        "definitions": [f"{f}:{n}" for f, n, _ in impls],
        "distinct_source_variants": 4,
        "top_k_vocab_all_scripts": 100,
        "max_len_all_scripts": 128,
        "cases": rows,
        "max_disagreement_across_all_cases": worst,
        "identical_distribution_js": same,
        "disjoint_support_js": disj,
        "ln2": ln2,
        "verdict": ("all definitions agree to within 1e-12 and match the two "
                    "analytic anchors" if ok else
                    "DISAGREEMENT: see cases; comparisons across scripts are "
                    "not valid until resolved"),
        "caveat": ("this establishes that the JS functions agree given the same "
                   "inputs. It does not establish that the scripts feed them the "
                   "same inputs; top_k and max_len were checked separately and "
                   "are 100 and 128 in every script."),
    }
    print(f"\nverdict: {doc['verdict']}")
    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
