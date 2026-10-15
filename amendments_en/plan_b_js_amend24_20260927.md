# Pre-registration Amendment 24: Register a "measurement resolution gate" to be passed before the G1 judgement is executed

**Target**: Pre-registration body §2 G1 (conditions for executing the judgement)
**Created**: a group member / 2026-09-27
**Status**: **The G1 judgement (160 cells) has not been executed.** The measurement for the gate defined in this amendment (v3, registered floor) **is currently running; floor statistics and judgement values have not yet been output** (the confirmation time and the extent already seen are noted in X5 below).

---

## X1. Why the gate is necessary

The G1 judgement requires 160 cells, approximately 70.7 hours (fp32, 6.912M forwards × 36.2 ms measured). **If the effect size falls below the measurement resolution, even investing 70.7 hours will yield rankings determined by numerical error.** This amendment registers that resolution will be confirmed before execution, and execution will not proceed if it is not met.

## X2. Origin of the resolution baseline value 1.183e-3 bits

`03_解析/plan_b/G1_judgement/batch_equivalence_20260927.json` (2026-09-27).
**The maximum absolute difference in JS when only the batch size was changed (batch=1 vs. batch=N)** was 1.183e-3 bits.

**This is not run-to-run variability.** Repeated runs at batch=1 are bit-identical (`g1_audit_ab.py` Audit A, max|run1−run2| = 0). 1.183e-3 is **"how much the value moves when choosing a numerically equivalent implementation"** and is used as a scale for **whether a different implementation would reproduce the result**.

## X3. Gate (fixed before execution; will not be changed after seeing results)

For **2 directions in layer 11 (`get_candidate_dirs`'s `ica[0]` and `jac[0]`) × 2 arms = 4 cells**, measure the following using **the registered PMF floor (`g1.pmf_draws`, §5), 100 draws**.

### Gate 1: Effect size vs. implementation difference
For each cell, count `n_within = #{ k : |JS(floor_k) − JS(axis)| < 1.183e-3 }`.

- **`n_within` ≥ 50 for a cell** → **that cell is judged unmeasurable.** The 160-cell run for that arm will not proceed
- **`n_within` < 50** → that arm satisfies the resolution requirement

### Gate 2: Rank stability across precision levels
For the same axis and same 10 floor draws, measure with fp16 and fp32, and count
`swaps = #{ k : (JS(floor_k) > JS(axis)) differs between fp16 and fp32 }`.

- **swaps = 0** → rankings do not depend on implementation
- **swaps 1–2** → grey zone. **Execution is allowed, but ranking instability must be stated explicitly in the manuscript**
- **swaps ≥ 3** → **conclusion is implementation-dependent. That arm will not be executed**

### Precision to be used upon execution
**Execute in fp32.** fp32 at 36.2 ms/pass is essentially the same cost as fp16 (fp16 effective 35 ms), and **there is no reason to choose fp16 when one can eliminate one source of implementation dependence without sacrificing speed.**
Repeated fp32 runs are confirmed to be bit-identical (v2 probe, max_abs = 0).

## X4. How to report an arm that fails the gate

**Write "fell below the resolution of the measurement instrument," not "was not measured."**
Report the measured `n_within` and `swaps` values from this amendment, and **make no positive or negative claims about that arm.**
**Do not use the resolution failure to retain only arms that are favorable** (the same gate is applied to both arms).

## X5. Disclosure of numbers already seen

**To show that this gate was not constructed post-hoc, all numbers seen at this point are disclosed.**

**(a) First audit conducted with unregistered floor** (`g1_audit_20260927_1001.json`, 2026-09-27T10:01Z):
`g1_audit_ab.py` used `pmf_draws_inline` (**matched to X's variance profile and made orthogonal to d**),
which is **not the registered `g1.pmf_draws` (matched to d's own projection profile, orthogonality not imposed).**
Therefore **the δ, n_above, and VERDICT for these 4 cells are not the values of the registered test.**

**Nevertheless, the numbers seen are recorded** (same intent as Amendment 23: nothing is hidden):

| Cell | Arm | Axis | n_within/100 | n_above/100 | δ |
|---|---|---|---|---|---|
| ica_0 | I | 4.53e-04 | 100 | 86 | −0.050 |
| ica_0 | II | 3.42e-03 | 6 | 99 | −0.326 |
| jac_0 | I | 7.75e-04 | 100 | **0** | **+0.202** |
| jac_0 | II | 3.26e-03 | 8 | 100 | −0.413 |

**It is explicitly recorded that `jac_0` Arm I satisfied the registered threshold δ ≥ +0.20.**
**That same cell simultaneously had `n_within = 100/100`, meaning it was a cell that failed the resolution requirement.**
**Seeing this combination was the motivation for writing this amendment.** The motivation is not hidden.

**(b) fp16/fp32 rank comparison (unregistered floor, Audit B ICA configuration)**: `swaps = 2/10`.

**(c) What has been seen so far for v3 (registered floor, production candidate directions)**:
Only `ica_0` Arm I fp16 **axis** JS mean = 4.571933e-04 bits.
**Floor statistics, n_within, n_above, δ, and swaps are all not yet output**
(log confirmed as of 2026-09-27T10:47:56Z; the relevant lines do not exist).

**The gate numbers in this amendment were fixed before seeing these values for v3.**

## X6. Incidental recorded facts (not used in judgement)

The production ICA direction (n=20, seed=42) and the Audit B ICA direction (n=40, seed=20260926) have
**L2 distance 1.405 (essentially orthogonal for unit vectors)**, yet
**the axis JS means differ by only 0.9%: 4.5329e-04 vs. 4.5719e-04.**

**This is the observation that nearly orthogonal directions produce output changes of the same magnitude, which is consistent with weak directional specificity.**
**However, it will not be used in this amendment's judgement** (it is merely a comparison of 2 points, not a measurement target).
