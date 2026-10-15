# Pre-Registration Amendment 59: Results of the Signed Readout (Floor at 40 Trials) and Disclosure of the Decision to Increase the Floor to 200 Trials

**Created**: 2026-10-05
**Target**: Judgements V1′ and V3′ in Amendment 58
**Judgement**: **V3′ holds. V1′ is unmeasurable because some dimensions have a non-zero-centered floor.**
**Change**: The number of floor trials is increased from 40 to 200. **This change was made after seeing the results, and that fact is disclosed.**
**Activation condition**: The judgement with 200 floor trials must not be performed until this file has been committed and pushed.

---

## BH1. Results with 40 Floor Trials (OLMo-2-7B, Deepest Layer L24, $J^\*=0.05$)

**V3′ (positive control) held.**

| | $S$ | Floor mean | Floor p95 | Judgement |
|---|---|---|---|---|
| **Positive control (Warriner valence)** | **+0.2460** | **−0.0012** | +0.1762 | **Exceeded** |

**The floor mean landed at −0.0012, virtually at 0.** This shows that the diagnosis in Amendment 58 BG4 was correct (a magnitude indicator is sign-blind and direction must be measured). **This measurement system is capable of measuring specific effects on emotion.**

Results for evaluation dimensions (17 dimensions):

| Evaluation dimension | $S$ | Floor mean | Floor SD | Floor p95 | Judgement |
|---|---|---|---|---|---|
| not_consider | +0.3146 | −0.0275 | 0.1541 | +0.2639 | Exceeded |
| chance_control | +0.2817 | −0.0259 | 0.2615 | +0.3586 | Not reached |
| social_norms | +0.1928 | +0.0110 | 0.1156 | +0.1836 | Exceeded |
| pleasantness | +0.1903 | +0.0089 | 0.1288 | +0.2086 | **Not reached (by a small margin)** |
| unpleasantness | +0.1688 | +0.0127 | 0.1418 | +0.2370 | Not reached |
| self_responsblt | +0.1621 | −0.0354 | 0.1244 | +0.1527 | Exceeded |
| other_responsblt | +0.0772 | **−0.0360** | 0.0770 | +0.1156 | **Floor not zero-centered** |
| (Other 10 dimensions have $S$ within ±0.12 or negative) | | | | | Not reached |

**Pass 3/17. However, because the floor of `other_responsblt` deviated significantly from 0, the clause in Amendment 58 BG5 designates this as unmeasurable.** The figure of 3/17 passed is not cited as a result.

## BH2. Insufficient Estimation Precision of the Floor

**The floor standard deviation is 0.077–0.262, which is on the same order as the observed effect size (+0.16 to +0.19).** With 40 trials, the estimate of the p95 is coarse and cannot separate a real effect from noise.

The fact that `pleasantness` $S=+0.1903$ does not reach p95 $+0.2086$ is likely because the p95 is estimated from 40 samples under floor SD 0.1288.

For the same reason, the floor mean of `other_responsblt` deviating from 0 may also be **coincidence due to insufficient sample size** (floor SD 0.0770, standard error 0.0122, observed mean −0.0360 is approximately 2.9 SE).

## BH3. Change: Increasing the Floor to 200 Trials

**Reason**: The floor SD is on the same order as the effect size, and 40 samples provide insufficient estimation precision for both the p95 and the floor mean. With 200 trials, the standard error is reduced by approximately 1/2.2.

**This is a change made after seeing the results.** The decision was made after observing the result of 3/17 passed and unmeasurable with 40 trials. **That ordering is not hidden.**

**Measures to preserve fairness**:

1. **The 40-trial results (BH1) are included in the paper as-is.** They are not replaced by the 200-trial results
2. **The judgement criteria ($S$ exceeds floor p95, floor is zero-centered, positive control exceeds floor) are not changed at all**
3. If the 200-trial results are worse than the 40-trial results, they are still reported
4. Nothing other than the number of floor trials is changed ($J^\*$, the $R^2$ threshold for adopting evaluation dimensions, the number of stimuli, the antisymmetrization method)

**Principal investigator approval**: 2026-10-05. Approval was obtained after explaining the reason for the increase and the fact that it is result-dependent.

## BH4. What Could Change With This Change (Written in Advance)

- **Possibility of increased pass count**: `pleasantness` (+0.1903 vs. p95 +0.2086) and `unpleasantness` (+0.1688 vs. +0.2370) may pass if the floor estimate tightens
- **Possibility that the unmeasurable status is resolved**: If the floor mean of `other_responsblt` moves closer to 0, a judgement can be made
- **Possibility of decreased pass count**: `self_responsblt` (+0.1621 vs. p95 +0.1527) passed by a narrow margin, and if the floor p95 estimate moves up it may fail. **If it fails, that is reported as-is**

**Either outcome is reported.** If the 200-trial result is worse, that is written as worse.

## BH5. Commitments

- The 40-trial results are retained in the paper. They are not overwritten by the 200-trial results
- The judgement criteria are not changed. Nothing other than the number of floor trials is changed
- If the 200-trial results are worse, they are still reported
- The floor trials are not increased further. **A third change is not performed**
