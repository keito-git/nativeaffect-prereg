# Pre-Registration Amendment 69: Judgement Q Is 3/10. The Superiority of the Residual Is Not Specific to the Appraisal Subspace

**Created**: 2026-10-06
**Target**: Judgement Q in Amendment 68
**Judgement**: **3/10. Not specific (general to 21-dimensional subspaces).**
The "shrunk claim" written in advance in Amendment 68 BQ4 is adopted as-is.
**Principal investigator policy (2026-10-06)**: The audit paper is not created. This amendment is retained as a research record.

---

## BR1. Results

| Model | Appraisal: fit / res / ratio | Top 21 PCs: res / ratio | Random: res(p95) / ratio(p95) | Judgement |
|---|---|---|---|---|
| OLMo-2-13B | 0.3257 / 0.4371 / 1.342 | 0.6194 / **1.902** | 0.3897(0.4276) / 1.201(1.321) | PASS |
| OLMo-2-7B | 0.3253 / 0.4457 / 1.370 | 0.5760 / **1.768** | 0.3783(0.4128) / 1.165(1.281) | PASS |
| Llama-3.1-8B | 0.3249 / 0.4148 / 1.277 | 0.4848 / **1.488** | 0.3684(0.4004) / 1.136(1.238) | PASS |
| Gemma-2-2B | 0.3257 / 0.4168 / 1.280 | 0.5356 / 1.643 | 0.3908(0.4250) / 1.207(1.322) | FAIL |
| Gemma-2-9B | 0.3241 / 0.4620 / 1.425 | 0.6039 / 1.860 | 0.4543(0.4883) / 1.401(1.505) | FAIL |
| Llama-3.2-1B | 0.3257 / 0.4247 / 1.304 | 0.4839 / 1.481 | 0.3924(0.4304) / 1.208(1.324) | FAIL |
| Phi-3-medium | 0.3253 / 0.4450 / 1.368 | 0.6055 / 1.846 | 0.4185(0.4507) / 1.290(1.399) | FAIL |
| Phi-3.5-mini | 0.3257 / 0.4758 / 1.461 | 0.6155 / 1.886 | 0.4549(0.4956) / 1.401(1.538) | FAIL |
| Ministral-8B | 0.3259 / 0.4769 / 1.463 | 0.6520 / **1.994** | 0.4860(0.5230) / 1.499(1.608) | FAIL |
| Mistral-Nemo | 0.3259 / 0.4427 / 1.358 | 0.6342 / **1.940** | 0.4779(0.5110) / 1.472(1.574) | FAIL |

**Judgement Q: 3/10. Does not reach majority.**

**What is decisive is the top 21 principal components.** The ratio is 1.481–1.994, **exceeding the appraisal subspace's 1.277–1.463 in all 10 models.** The phenomenon "the residual predicts emotion better than the human-explained part" is **not concentrated in the appraisal subspace but is stronger in variance-dominant subspaces**.

## BR2. The Adopted Claim (Shrunk Version from Amendment 68 BQ4, As-Is)

> Of the model's appraisal code, the component explained by human ratings is **informationally equivalent to human ratings themselves** ($F_{\text{fit}}$ 0.3241–0.3259 vs. $F_Y$ 0.3230, 10 models), and the unexplained component predicts emotion better. **However, this is a property that holds generally for 21-dimensional subspaces and is not specific to the appraisal code. Therefore, this result shows that human appraisal self-reports are weak predictors of emotion labels, and is not a claim about the properties of the model's appraisal code.**

**The 10/10 support of judgement R is not used as grounds for expansion** (commitment in Amendment 68 BQ6).

## BR3. Robust Facts That Are Not Affected by Controls

1. **$F_{\text{fit}} \approx F_Y$ (difference within 0.003, 10 models).** This is proof that the decomposition is functioning as intended, and **the model's evaluation probes exactly recover the emotion prediction information of human ratings in that component, and no more**
2. **The emotion label prediction of human 21 appraisal ratings is macro-F1 0.3230** (13 categories, chance 0.077). **The 21 dimensions of appraisal theory only weakly determine emotion labels**
3. **The appraisal subspace is inferior to top PCs as a 21-dimensional code** (judgement S, S2 not held for 10/10)
4. **Even after projecting out the appraisal subspace, emotion decoding does not drop** (X1, 10 models)

## BR4. Final Accounts of the Entire Line

| Judgement | Content | Result |
|---|---|---|
| M1 (E2+E3) | Cross-model agreement (after surface-level control) | Held (4 models). Explainable by topic |
| M1′ (E5, topic fixed) | Same, under within-skeleton-permutation null | **Not held** |
| X1 | Removal of appraisal subspace (necessity) | **Not held 10/10**. Error in the question (Amendment 66) |
| V1, W1 | Steering with magnitude readout | **Unmeasurable** (positive control not reached) |
| V1′ | Signed, dimension by dimension | **Unmeasurable** (on the same order as floor tail, Amendment 62) |
| V1″ | Aggregate, discovery set | Positive 4/4 (+2.2 to +3.1 SD, exploratory) |
| **V1″** | **Aggregate, confirmation set** | **1/5. Not held** |
| X2′ | Asymmetry | **Withdrawn** (prerequisite not implemented, Amendment 65) |
| S | Sufficiency of appraisal code | **Not held 0/10** |
| R | Decomposition into human-explained part and residual | Supported 10/10 |
| **Q** | **Specificity of residual** | **Not held 3/10** |

**The only positive result remaining is R. Because Q failed, the interpretation of R shrinks to BR2.**

## BR5. Four Routes Failed in the Same Pattern

| Route | Form of claim | How it failed |
|---|---|---|
| P1 | Low intrinsic dimensionality | Already present at layer 0. No contribution from computation |
| M1/M1′ | Shared across models | When topics are matched, agreement does not exceed chance |
| V1 series | Steering is specific | Disappears with variance-matched floor / does not replicate in confirmation set |
| S/R/Q | Appraisal code is sufficient / residual is specific | Inferior to top PCs / same in random subspaces |

**Commonly, "when a control matching variance or information content is placed, the claim does not hold."** The form of the claim is consistently "X is more special than a control," and **it has been confirmed 4 times that this form does not hold.** The next route must **change the form of the claim**.

## BR6. Commitments

- The 3/10 of Q is recorded as-is; only the 3 passing models are not shown
- **The fact that the top PCs ratio exceeded the appraisal subspace in all models is explicitly stated**
- The shrunk claim in BR2 is adopted; the 10/10 support of R is not used for expansion
- The final accounts table in BR4 is retained as a research record
