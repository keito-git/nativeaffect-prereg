# Pre-registration Amendment 32: The 4th cell of the 2×2 was obtained. Prediction C is "equivalent," not "reversed."

**Target**: Prediction C from Amendment 29 AC3, and Amendment 30 AD1, AD3, AD4
**Created**: 2026-10-03
**Position**: **The judgement in Amendment 30 (AC1 is final; Paper 3 will be written as a methodology paper) is not changed.**
The three changes are: (a) the fact that the 4th cell recorded as unobtainable in Amendment 30 was in fact obtained; (b) characterizing how Prediction C failed; and (c) correcting a counting error in the number of principal component vectors.

---

## AF0. Correction first: "permanently unobtainable" in Amendment 30 is factually incorrect

Amendment 30 AD4 recorded two items as "permanently unobtainable" due to a GPU failure:

1. Experiment A (confirmatory half), layers 22 and 27
2. The 4th cell of the 2×2: "math-derived directions × math stimuli"

Of these, **2 was obtained.** After container reconstruction, `g1_judgement.py` was re-run, and layers 11, 16, and 22 are complete (layer 27 still incomplete at 2 out of 40 cells).

`03_解析/plan_b_qwen3_8b/G1_crossdomain_math_on_math/g1_judgement_result.json`
(`status=IN_PROGRESS`, `layers_completed=[11,16,22]`, generated 2026-10-02T08:27:37Z,
host `emotionnaibu-9d659dc49-q8hlb`)

**1 (Experiment A layers 22 and 27) has still not been obtained.** The confirmatory determination for Experiment A remains at 2 layers (11 and 16).

Amendment 30's description is accurate as a record of the container being unusable at that point, but "permanently" was an overstatement. Do not write equipment-failure forecasts in the form of conclusions.

## AF1. What the 4th cell changed (audit first)

Before interpretation, confirmed that the 4th cell qualifies as an independent cell.
Cross-checked all cells in `G1_crossdomain_emo_on_math` (emo-derived × math stimuli) and `G1_crossdomain_math_on_math` (math-derived × math stimuli) by `_js_axis` value:

| Layer | Matching cells | Differing cells | Floor `_floor_means_per_draw` |
|---|---|---|---|
| 11 | 30 (ica, pc) | 10 (jac) | match |
| 16 | 30 (ica, pc) | 10 (jac) | match |
| 22 | 30 (ica, pc) | 10 (jac) | match |

**This is as designed.** The only variable changed in this comparison is the domain of origin of Jacobian directions; stimulus set, floor, and ICA/PC candidates are all shared. Therefore **the 4th cell is a paired control under identical experimental conditions, and the 2×2 is valid only for the jac family.**
For the ica and pc families, the same directions are measured twice when stimuli are the same, regardless of origin. This limitation will be stated explicitly in the manuscript.

The same cross-check was performed for `G1_judgement` (emo×emo) and `G1_specificity_gsm8k` (math×emo), confirming that ica and pc each have 30 cells matching at layers 11 and 16.

## AF2. 2×2 (jac family, δ_a median, Arm II, registered floor)

| Layer | emo-derived × emo stimuli | emo-derived × math stimuli | math-derived × emo stimuli | math-derived × math stimuli |
|---|---|---|---|---|
| 11 | +0.713 (10/10) | +0.923 (8/10) | +0.790 (8/10) | **+0.993 (10/10)** |
| 16 | +0.678 (10/10) | +0.846 (0/10) | +0.657 (0/10) | **+0.937 (10/10)** |
| 22 | not obtained | +0.909 (7/10) | +1.000 (10/10) | **+0.944 (10/10)** |
| 27 | not obtained | +0.629 (0/10) | +0.755 (7/10) | incomplete (2/40 cells) |

Values in parentheses are pass counts for the registered criterion. Medians use `statistics.median` (rule in Amendment 30 AD0).

## AF3. Judgement on Prediction C: failed, but not reversed

**Prediction C (Amendment 29 AC3)**: diagonal δ_a medians are greater than off-diagonal ones.

Comparison is possible only in layers where all 4 cells are available.

| Layer | Diagonal mean | Off-diagonal mean | Difference |
|---|---|---|---|
| 11 | +0.853 | +0.857 | **−0.003** |
| 16 | +0.808 | +0.752 | **+0.056** |

**Diagonal and off-diagonal are equivalent.** At layer 11 the difference is 0.003; at layer 16, +0.056 with diagonal slightly higher.
Prediction C's claimed "diagonal is larger" does not hold, but the "reversed sign" written in Amendment 30 does not hold either.

**The "moreover the sign is reversed" in Amendment 30 AD1 is withdrawn.** That judgement was made at a time when **only one diagonal cell existed** (emo×emo), so the comparison was only between emo×emo and emo×math. When the other diagonal (math×math) is added, it pushes up the diagonal mean and the difference disappears.
**Diagonal analysis must not be done with only one diagonal cell** — this is the lesson of this case.

**The judgement itself does not change.** The provision of Amendment 29 AC3 states:

> **If this does not hold** (diagonal and off-diagonal are equivalent): The sensitivity structure does not depend on domain.
> The effect is only the general property of output sensitivity, and **the conclusion from AC1 (methodology paper) is final.**

The observed "equivalent" is precisely this branch. **AC1 is final. Paper 3 will be written as a methodology paper. The stimulus set will not be switched to try again.** The conclusion of Amendment 30 AD1 is maintained.

### Incidental column effect observed (unregistered, descriptive only)

Regardless of origin, **math stimuli have larger δ_a than emotional stimuli** (×emo stimuli n=6 median +0.734, ×math stimuli n=7 median +0.923). However this is confounded with the row effect of origin (emo-derived n=6 median +0.780, math-derived n=7 median +0.937), and the two can only be separated in layers 11 and 16 where all 4 cells are available.
**This is an unregistered observation; no mechanistic explanation is given** (policy of Amendment 22 §V4).

## AF4. Correction: principal components are 80, not 100 (conclusion unchanged)

Amendment 30 AD3 stated "of a total of 100 principal component directions, 0 exceeded the floor."
**This 100 has a double-count.** The pc 20 cells of `G1_judgement` (emo×emo) layers 11 and 16 have `_js_axis` identical to those of `G1_specificity_gsm8k` (math×emo) in the same layers, meaning the same directions were counted twice.

Deduplicating all 4 runs' pc cells by `_js_axis`:

| Selection method | Unique directions | Directions exceeding floor | Rate |
|---|---|---|---|
| Output sensitivity (Jacobian) | 130 | 90 | **69.2%** |
| Activity reproducibility (ICA) | 160 | 4 | **2.5%** |
| Variance magnitude (principal components) | **80** | **0** | **0%** |

**The fact that "not a single principal component exceeds the floor" is unchanged. Only the count changes from 100 to 80.**
In fact this table, with unique counts across runs, is clearer than the layer-by-layer enumeration in Amendment 30. Going forward, when reporting counts, deduplicate across runs by `_js_axis`.

## AF5. Central proposition of Paper 3, confirmed in this amendment

> **What determines whether an intervention works is the selection criterion for the direction, not what it means, nor its variance, nor its domain.**

Based on three pieces of evidence, all using the unique counts re-enumerated in this amendment:

1. **Three-way separation by selection criterion**: output sensitivity 69.2%, activity reproducibility 2.5%, variance magnitude 0%
2. **Independent of semantic content**: math-derived directions work on emotional stimuli as well as or better than emotion-derived ones
   (layer 11: +0.790 vs. +0.713; layer 16: +0.657 vs. +0.678)
3. **Independent of domain**: diagonal and off-diagonal are equivalent (AF3)

## AF6. Remaining items

- **Layer 27 math×math** (2 out of 40 cells). Whether GPU can be used is a decision by the principal investigator. If complete, the 2×2 closes across all 4 layers. Even without it, the AF3 judgement is confirmed in layers 11 and 16 and the conclusion does not change
- Experiment A (confirmatory half), layers 22 and 27 are still not obtained
- **Carving out Paper 2 vs. Paper 3** (to avoid self-salami). Unfinished from Amendment 30 AD5.
  The split "Paper 2: which reference set determines the claim; Paper 3: which selection criterion determines steerability" seems natural, but requires a decision by the principal investigator

---

## AF7. Correction (same day, after the Amendment 32 commit): the 4th cell had completed all 4 layers

The `G1_crossdomain_math_on_math/g1_judgement_result.json` referenced when this amendment was written was
**a snapshot during execution** (`status=IN_PROGRESS`, `layers_completed=[11,16,22]`). Upon checking server log `logs/g1_math_on_math_20261001.log`, **all 4 layers had completed**
(12.53 hours total, `status=COMPLETE`, generated 2026-10-02T14:43:02Z).

The complete version was retrieved, and the in-progress copy was kept as `g1_judgement_result.json.partial_20261002`.

### Correction 1: Layer 27 math×math has been obtained

Correct "layer 27 math×math = incomplete (2/40 cells)" in AF2 as follows:

| Layer | emo-derived × emo stimuli | emo-derived × math stimuli | math-derived × emo stimuli | math-derived × math stimuli |
|---|---|---|---|---|
| 11 | +0.713 (10/10) | +0.923 (8/10) | +0.790 (8/10) | +0.993 (10/10) |
| 16 | +0.678 (10/10) | +0.846 (0/10) | +0.657 (0/10) | +0.937 (10/10) |
| 22 | not obtained | +0.909 (7/10) | +1.000 (10/10) | +0.944 (10/10) |
| 27 | not obtained | +0.629 (0/10) | +0.755 (7/10) | **+0.706 (9/10)** |

**Remove "layer 27 math×math" from the remaining items in AF6.** The only unclosed 2×2 cells are layers 22 and 27 for emo×emo (the not-yet-obtained portion of Experiment A).

### Correction 2: Unique counts re-enumerated

Correct the table in AF4 (40 cells from layer 27 are added):

| Selection method | Unique directions | Directions exceeding floor | Rate |
|---|---|---|---|
| Output sensitivity (Jacobian) | **140** | **99** | **70.7%** |
| Activity reproducibility (ICA) | 160 | 4 | 2.5% |
| Variance magnitude (principal components) | 80 | 0 | **0%** |

**The three-way order and "not a single principal component exceeds the floor" are unchanged.**

### Lesson

**Do not read a running output file as a confirmed value.** `env.status` being `IN_PROGRESS` was written inside the file, but only the `layers_completed` value was checked and the run was judged "incomplete." Going forward, mechanically confirm `env.status == "COMPLETE"` before using a result JSON.
