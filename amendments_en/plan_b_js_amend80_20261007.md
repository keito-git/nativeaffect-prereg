# Pre-registration Amendment 80: Results of Judgement CMP — Only the Emotion Category Axis Exceeds the Same-Size Random Family Across All Discovery-Cohort Models

**Created**: 2026-10-07
**Target**: Judgement CMP from amendment 79
**Judgement**: **In all 4 models of the discovery cohort, only the emotion category axis exceeded the best of the same-size variance-matched random family on a majority of targets.** The appraisal dimension axis and the principal component axis do not exceed it.
**The confirmation cohort of 5 models is currently running, and their results have not been obtained as of the time this amendment was written.**

---

## CC1. Results (4 discovery-cohort models, $J^\*=0.05$, full-vocabulary JSD)

| Model | Family | Best of random family | K=13 adjusted | Individual floor p95 |
|---|---|---|---|---|
| Llama-3.2-1B | **Emotion** | **11/13 (+2.95SD)** | 11/13 (+3.25) | 13/13 |
| | Raw appraisal | 6/13 (+0.41) | 6/13 (+0.74) | 9/13 |
| | Principal component | 4/13 (+0.61) | 4/13 (+0.82) | 9/13 |
| | Residualized appraisal | 0/13 (−0.70) | 0/13 (−0.19) | 6/13 |
| OLMo-2-7B | **Emotion** | **10/13 (+3.33SD)** | 10/13 (+3.35) | 13/13 |
| | Raw appraisal | 3/13 (+0.27) | 3/13 (+0.71) | 8/13 |
| | Principal component | 6/13 (+0.79) | 6/13 (+1.01) | 10/13 |
| | Residualized appraisal | 1/13 (+0.07) | 1/13 (+0.41) | 8/13 |
| Gemma-2-9B | **Emotion** | **7/13 (+2.01SD)** | 7/13 (+2.08) | 9/13 |
| | **Raw appraisal** | **1/13 (−1.01)** | 1/13 (−0.62) | 2/13 |
| | Principal component | 5/13 (+0.30) | 5/13 (+0.66) | 7/13 |
| | Residualized appraisal | 0/13 (−1.03) | 0/13 (−0.58) | 2/13 |
| Llama-3.1-8B | **Emotion** | **11/13 (+2.75SD)** | 11/13 (+3.06) | 13/13 |
| | Raw appraisal | 3/13 (−0.48) | 3/13 (+0.00) | 7/13 |
| | Principal component | 6/13 (+0.91) | 6/13 (+1.24) | 10/13 |
| | Residualized appraisal | 1/13 (−0.53) | 1/13 (−0.09) | 4/13 |

### Aggregate (models as the unit of replication)

| Family | Models with majority | Median targets exceeded | Median standardized excess | K=13 adjusted |
|---|---|---|---|---|
| **Emotion category** | **4/4** | **10.5/13** | **+2.85 SD** | 10.5/13 (+3.15SD) |
| Principal component | **0/4** | 5.5/13 | +0.70 SD | 5.5/13 (+0.91SD) |
| Raw appraisal dimension | **0/4** | 3.0/13 | **−0.11 SD** | 3.0/13 (+0.36SD) |
| Residualized appraisal dimension | **0/4** | 0.5/13 | **−0.62 SD** | 0.5/13 (−0.14SD) |

## CC2. Primary Result

> **When output perturbation is matched using full-vocabulary JSD and the comparison is against the best of same-size variance-matched random families, only the emotion category axis exceeds the floor**
> (all 4 models with a majority, median standardized excess $+2.85$ SD).
> **The raw appraisal dimension axis does not exceed it** (0/4 models, median $-0.11$ SD),
> **and the principal component axis does not either** (0/4, $+0.70$ SD). **The ordering is unchanged even when family size is matched.**

## CC3. Resolution of Concerns

| Concern (external advice) | Resolution |
|---|---|
| Could residualization be the cause? | **Even raw directions: 0/4 models, median $-0.11$ SD.** Residualization makes it worse, but even raw directions do not pass |
| Could the emotion axis advantage be due to high variance? | **Principal component axis: 0/4 models, $+0.70$ SD.** Clearly separated from the emotion axis's $+2.85$ SD |
| Confound of family size | **Even when matched to K=13: 10.5 vs. 5.5 vs. 3.0.** Ordering invariant |
| Were only individual appraisal axes examined? | This judgement is still about **basis privilege (L3)**. **L2 (subspace privilege) has not been executed** |

## CC4. The Design of the Comparison Target Determines the Conclusion

**Given the same measurements, changing the comparison target changes the conclusion.**

| Comparison target | Raw appraisal | Principal component | Emotion |
|---|---|---|---|
| **Best of same-size random family** (correct) | **1–6/13** | **4–6/13** | **7–11/13** |
| 95th percentile of individual floor (lenient) | 2–9/13 | 7–10/13 | 9–13/13 |

**With the lenient comparison, even the appraisal axis and principal component axis reach majority in some models.** This is because the selection advantage of "choosing the best from K directions" is given to the family but not to the floor. **Both are reported in the paper alongside each other, with the effect of the design made explicit.**

**This is a methodological finding that is not limited to emotion research.** Studies making claims at the level of families must give the same size of selection to the contrast as well.

## CC5. In Gemma-2-9B, the Appraisal Axis Falls Below the Floor

Raw appraisal directions: 1/13, $-1.01$ SD; residualized: 0/13, $-1.03$ SD. **This goes beyond "no special power" to being inferior to variance-matched random directions.**

**Not over-interpreted.** A negative standardized excess means the best of the family falls below the mean of the best of random families, but **no particular meaning is assigned to the fact of being negative.** It is a single-model observation.

## CC6. What Has Not Been Executed

- **L2 (subspace privilege) has not been executed.** This judgement concerns the basis, and **"appraisal representations are not causal" cannot be written** (amendment 76 BY2)
- **The confirmation cohort of 5 models is currently running and the results have not been seen**
- Only one budget, $J^\* = 0.05$, has been used. Of the 3 budgets registered in amendment 73, 2 remain unexecuted
- Only the single-token readout of 13 emotion words has been used. The synonym-set readout in amendment 77 BZ5 has not been executed

## CC7. Commitments

- The confirmation cohort results are reported as-is regardless of whether they satisfy the majority or not
- The comparison against the individual floor p95 is reported alongside; **the fact that they pass with the lenient comparison is not concealed**
- The negative standardized excess for Gemma-2-9B is not over-interpreted
- **The fact that L2 has not been executed is stated explicitly; the basis results are not written as subspace results**
- The fact that only one budget and one readout type have been used is written in the limitations
- The history of the amendment 78 retraction and the amendment 79 retraction of the retraction is left in the paper as a record
