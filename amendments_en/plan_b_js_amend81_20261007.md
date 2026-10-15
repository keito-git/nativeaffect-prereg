# Pre-registration Amendment 81: Results of the Confirmation Cohort. In 8 of 9 Models, Only the Emotion Category Axis Exceeds the Family Best of the Variance-Matched Floor

**Created**: 2026-10-07
**Target**: Confirmation cohort for judgement CMP registered in amendment 80
**Judgement**: **Executed as registered; results recorded as-is. In 4 models of the confirmation cohort (excluding 1 degenerate model), the emotion category axis exceeded the majority of targets, consistent with the discovery cohort.**
**Activation condition**: Draft v3 writing must not proceed until this file has been committed and pushed.

---

## BZ1. What Was Registered (Commitments in Amendments 80 BY/CC7)

1. The confirmation cohort results are **reported as-is, regardless of whether they satisfy the majority or not**
2. Degenerate models (where the scale $S$ collapses and no family exceeds the individual floor p95 on any target) are **excluded from the judgement population on grounds of failing E5-pre, and this fact is recorded**
3. The statistic fixed in amendment 80 — family best vs. family best (selection on sel contexts, scoring on held-out, floor F4 measured 60 times, maximum of K resampled bootstrap) — is not changed

All were fixed before execution and are not changed in this amendment.

## BZ2. What Was Executed

`code/phase10/stageC_cmp.py` (identical code, no differences from the discovery cohort) was applied to 5 models via `code/scripts/go_stageC_conf.sh`.

Confirmation cohort: Gemma-2-2B-it / OLMo-2-13B-Instruct / Ministral-8B-Instruct-2410 /
Phi-3-medium-4k-instruct / Mistral-Nemo-Instruct-2407

Completion: 2026-10-07 12:09:30 UTC. All 5 models ran to completion.

## BZ3. Judgement for the Degenerate Model (Application of Commitment 2)

**Phi-3-medium-4k-instruct is degenerate.** The standardized excess for all families is 0.00 SD, and no family exceeds the individual floor p95 on even 1 target (0/13). `appraisal_raw` shows 8/13, but the excess is +0.00 SD, which is degeneracy where the family best and the floor family best are tied at the same value.

**Excluded from the judgement population on grounds of failing E5-pre, as registered; the fact of exclusion is preserved in this amendment.**
Phi-3.5-mini from the same family was also degenerate with 0/13 across all families including the gradient ($|S| \approx 0.0007$). The fact that 2 models from the Phi family have the same signature is **written in the limitations as-is.**

## BZ4. Results (8 Models Excluding the Degenerate One)

The floor is "the best of the variance-matched integrated cohort (VMIC) of the same size." Values are the number of targets exceeded / 13 and the median standardized excess.

| Model | Cohort | Emotion category | Raw appraisal dimension | Principal component |
|---|---|---|---|---|
| Llama-3.2-1B-Instruct | Discovery | **11/13 (+2.95)** | 6/13 (+0.41) | 4/13 (+0.61) |
| Llama-3.1-8B-Instruct | Discovery | **11/13 (+2.75)** | 3/13 (−0.48) | 6/13 (+0.91) |
| OLMo-2-7B-Instruct | Discovery | **10/13 (+3.33)** | 3/13 (+0.27) | 6/13 (+0.79) |
| gemma-2-9b-it | Discovery | **7/13 (+2.01)** | 1/13 (−1.01) | 5/13 (+0.30) |
| gemma-2-2b-it | Confirmation | **13/13 (+7.98)** | 1/13 (−0.96) | 6/13 (+0.48) |
| Mistral-Nemo-Instruct-2407 | Confirmation | **12/13 (+2.97)** | 3/13 (−0.50) | 4/13 (+0.63) |
| OLMo-2-13B-Instruct | Confirmation | **9/13 (+2.24)** | 4/13 (+0.18) | 4/13 (+0.43) |
| Ministral-8B-Instruct-2410 | Confirmation | **8/13 (+1.43)** | 0/13 (−0.83) | 5/13 (+1.01) |
| Phi-3-medium-4k-instruct | Confirmation | Degenerate — excluded from judgement | — | — |

### Aggregate by Cohort

| Family | Discovery (4 models) | Confirmation (4 models) | Total (8 models) |
|---|---|---|---|
| Emotion category | Majority **4/4**, median 10.5/13, **+2.85 SD** | Majority **4/4**, median 10.5/13, **+2.61 SD** | Majority **8/8**, median 10.5/13, **+2.85 SD** |
| Raw appraisal dimension | 0/4, median 3.0/13, −0.11 SD | 0/4, median 2.0/13, −0.67 SD | 0/8, median 3.0/13, −0.49 SD |
| Principal component | 0/4, median 5.5/13, +0.70 SD | 0/4, median 4.5/13, +0.56 SD | 0/8, median 5.0/13, +0.62 SD |
| Residualized appraisal dimension | 0/4, median 0.5/13, −0.62 SD | 0/4, median 0.5/13, −0.82 SD | 0/8, median 0.5/13, −0.62 SD |

The ordering is preserved even in the K=13-adjusted subsample (thinning the larger families 200 times to 13 directions: emotion median 10.5/13, +3.07 SD; raw appraisal 3.0/13, −0.03 SD; principal component 5.0/13, +0.84 SD). **Family size cannot explain it.**

## BZ5. What Can and Cannot Be Said

**Can be said (L3, basis privilege)**: Under interventions with matched output perturbation, **directions corresponding to human emotion categories move the target readout more strongly than the best of a family of random directions with fully matched variance profiles.** This was observed in the discovery cohort of 4 models and **reproduced in the confirmation cohort of 4 models using the statistics registered in advance.** Majority was exceeded in 8/8 models.

**Cannot be said:**

1. **L2 (subspace privilege) has not been executed.** The question of whether the subspace spanned by appraisal dimensions is privileged requires the procedure of amendment 77 (optimal linear combination within the subspace vs. size-matched random subspace), which has not been executed. The present result addresses **basis privilege only**
2. **Appraisal theory is not negated.** The fact that raw appraisal dimensions do not exceed the family floor is evidence that "appraisal dimensions are not the computational basis of LLMs," not evidence that "appraisal theory does not explain LLM emotion representation." L2 has not been executed, so the explanatory power as a subspace is unverified
3. **The core of AAPH (the principal investigator's hypothesis) has not been supported.** If "emotion categories are projections of a latent concept Z," the candidates for Z (appraisal dimensions, principal components) should move the readout at least as strongly as emotion categories. The observation is the opposite: **emotion categories themselves are the strongest.** After withdrawing $k \ll |E|$ in amendment 72, the present result shows that **the projection direction is opposite to the hypothesis**
4. Two models from the Phi family are degenerate and cannot be judged

## BZ6. Preserving the History of Amendments 78 and 79

In the course of reaching this judgement, the E5 conclusion was retracted once in amendment 78, and that retraction was withdrawn in amendment 79. **Both are preserved in the record, and the history is written in the methodology section of draft v3.** The cause of the retraction was not residualization, JSD, or partition, but **the comparison target**, and the factor decomposition confirmed that the family best vs. family best statistic (the E5 statistic) was the correct quantity.

## BZ7. What Can Proceed Next (Commitments)

1. Draft v3 is written **limited to basis privilege (L3).** L2 not being executed is stated explicitly
2. L2 is executed using the procedure of amendment 77. **Draft v3 is frozen before the results come in**
3. The rotation test for L3 (105 directions within the subspace) is also executed alongside
4. The 2 degenerate models are written in the limitations section, with the exclusion criterion cited verbatim from the pre-registration
