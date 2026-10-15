# Pre-Registration Amendment 17: Finalizing the Sampling Method and Reporting Rules for the Estimator in N5, Before Seeing the Real Data

**Target**: Amendment 14 N5 (variance dominance rule measurement)
**Created**: 2026-09-26
**Status**: **N5 has not been executed. Not a single real-data value has been seen.** GPU server is stopped
**Origin**: A team member pointed out 2 flaws in the registered design **before seeing real data** during implementation of N5 (calibration on synthetic data, `03_解析/plan_b/n5_estimator_calibration.json`)

---

## Q1. Flaw 1: With the Registered Sampling Method, Axis Residuals Are Extrapolation

Amendment 14 N5 specified:

> At each layer, draw **1,000 random directions from within the top principal component subspace**

**Drawing from inside means inside_fraction is structurally 1.0 for all of them.** However, **the axes' inside_fraction is around 0.2–0.3**.

**Therefore, applying the regression fitted on 1,000 directions to the axes constitutes extrapolation, and the residuals partially measure "how much the model deviates outside the training range" rather than "whether the axes behave as predicted by variance."**

**This is a flaw in the design I registered.**

### Decision

**The main analysis remains as registered, drawing from `in_span` (1,000 from inside the subspace), unchanged.** This answers the question "does the projection profile predict JS for directions inside the dominant variance subspace?" It is a self-contained question.

**In addition, execute the `coverage` sampling method.** By $d = \sqrt{f}\,u_{in} + \sqrt{1-f}\,u_{out}$, inside_fraction can be set exactly to $f$, **allowing coverage of the observed inside_fraction range.**

**Residuals of axes and the human valence direction are interpreted only against the `coverage` results.** Against `in_span` results, **residuals are not interpreted.**

**When reporting axis residuals from `in_span`, state "this residual contains extrapolation because the reference directions' inside_fraction is outside the training range, so it is not interpreted."** Use the flag implemented by the team (refuse interpretation if outside training range) as-is.

**Both results are reported.** The better one is not chosen.

## Q2. Flaw 2: Failure of a Weak Estimator Gets Misread as "Contribution of Meaning"

A team member calibrated the estimators on a **strictly linear function** (reachable $R^2 = 1$).

| n | Linear model | Gradient boosting | Shortfall |
|---|---|---|---|
| 200 | 1.0000 | 0.8426 | 0.1574 |
| 400 | 1.0000 | 0.8485 | 0.1515 |
| **1,000 (registered value)** | **1.0000** | **0.9197** | **0.0803** |

**Even at the registered sample size, gradient boosting only achieves 0.92 for a strictly predictable target.** Reading that number as the answer means **misattributing the estimator's error of 0.08 to "the contribution of the direction's meaning."**

**Also confirmed in the reverse direction**: For a target determined by sign (= meaning), the reported value at n=1,000 is **−0.0019**. **When meaning matters, it correctly yields something close to 0.**

### Decision

**Report value = the better (maximum) of linear and gradient boosting.**

**Reason**: What N5 asks is "**can** JS be predicted from the projection profile?" **A weak estimator's failure is not evidence of "it cannot."** To estimate the reachable predictability, taking the maximum of the estimators tried is the correct operationalization.

**However, 3 conditions are imposed.**

1. **Always report both values together.** Do not write only the maximum
2. **Attach the team's calibration table (above table) to the report.** So that readers can see the ceiling of each estimator at n=1,000
3. **Explicitly state the asymmetry.** Taking the maximum is a **conservative estimate of the upper side for predictability**, but is **non-conservative for the claim "meaning has no effect."** **Write this asymmetry in the main text**

**Reason for imposing condition 3**: Since the mechanistic explanation was withdrawn in Amendment 15, **the $R^2$ of N5 is reported as "a measurement value with no explanation given."** Since there is no claim in either direction, taking the maximum does not become self-serving. **However, if this value is cited in the future to make some claim, if the asymmetry is not recorded it will be misused.**

## Q3. Also Finalizing

- **N5 is executed at primary α only** (about 1.04 hours). The 4 α values would strain the budget
- **The JS implementation is imported from the one for which a team member proved agreement across 9 versions.** Not written fresh (see Q4)
- **No binary judgement by threshold is set for $R^2$.** Report the values themselves (as per Amendment 14 N5)

## Q4. Record: There Were 9 JS Implementations, and They Had Been Compared Against Each Other

**A team member discovered that 9 scripts each independently defined next-token JS** (3 types of function names, 2 types of key spellings, 4 variants as sources). **And results from different scripts had been compared against each other.**

**All 9 were extracted and run on the same input, confirming maximum difference 0.000e+00.** Also matched an analytic anchor (0 for identical distributions, $\ln 2 = 0.693147180560$ for mutually exclusive distributions). `top_k = 100` and `max_len = 128` are also identical across all 9.

**Therefore cross-script comparisons in the past (B0, E1 diagnostics, C1–C4) are valid on this axis.**

**If even 2 of them had differed, the comparisons between B0, E1 diagnostics, and C1–C4 would not have been comparisons.** That they look the same is not proof.

**Future rule**: **Do not duplicate a function that computes the same quantity.** If a duplicate already exists, **confirm numerical agreement on the same input before using it in a comparison.**

## Q5. Record: Running Only Some Layers Over Again Loses Shared Conditions

Patched by a team member in §25 (commit `457bc05`).

**Layers 11 and 16 were generated by `g1_jacobian.py` (sha256 `febe1971...`). If layers 22 and 27 are computed again with a file with one diagnostic line added, the 4 layers appear to be "4 layers from one run" while having lost shared conditions.** This is the type of error of reporting conditional results as unconditional results.

**Countermeasure**: Do not edit `g1_jacobian.py`. Place the exact principal angle computation in a separate file. `verify_g1_code_identity.py` exits with code 1 on sha256 mismatch and **displays "re-run all 4 layers with the new file, not just 2 layers."**
