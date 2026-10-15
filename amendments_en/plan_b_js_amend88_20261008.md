# Pre-registration Amendment 88: Results of the Symmetric 2×2. Precondition IND Is Not Satisfied; Level 3 Is Not Claimed

**Created**: 2026-10-08
**Targets**: 2×2 judgement of amendment 86 CE3, and precondition IND from amendment 87 CF4
**Judgement**: **The emotion axis advantage is limited to readout A (emotion words). It does not exceed the matched floor under readout B (appraisal adjectives).
Therefore precondition IND is not satisfied, and level-3 (axis privilege) is not claimed.**
**Activation condition**: The next judgement must not proceed until this file has been committed and pushed.

---

## CG1. Validity Check for Readout B (Amendment 86 CE2) — Pass

The modified check was executed on all 9 models. Check 1 (discriminability) and check 3 (non-duplication of vocabulary) passed for all models. **Check 2 (concordance with ratings) passed for all models at 9–10/12** (requirement was ≥7/12).

AUC examples (Llama-3.2-1B): unpleasantness 0.811, suddenness 0.718, pleasantness 0.653, goal_relevance 0.559 were concordant. familiarity 0.477, predict_event 0.480 were not concordant.

**Readout B is used.**

## CG2. 2×2 Results (Floor F5, 9 Models, Series Clusters)

Excess SD is the median; brackets are the 5-series cluster bootstrap 95% CI.

| Direction family | Readout | Majority of models | Excess SD median [95% CI] | p(G)<0.01 |
|---|---|---|---|---|
| **Emotion category** | **A (emotion words, self-consistent)** | **9/9** | **+3.17 [+2.20, +3.39]** | **9/9** (all 0.0005) |
| Emotion category | B (appraisal adjectives, cross) | 0/9 | **+0.03 [−0.07, +0.15]** | **0/9** (max 0.795) |
| Raw appraisal dimension | A (emotion words, cross) | 0/9 | +0.18 [−0.09, +0.29] | 0/9 (max 0.858) |
| Raw appraisal dimension | **B (appraisal adjectives, self-consistent)** | 0/9 | **+0.39 [+0.16, +0.59]** | **3/9** (max 0.861) |

## CG3. Precondition IND Is Not Satisfied

Amendment 87 CF4 specified the following as the precondition:

> In readout B, the emotion category axis exceeds the matched family best ($p_G < 0.01$ in a majority of models).

**The measured value is 0/9 models, excess SD +0.03. Not satisfied.**

**Therefore level-3 (axis privilege) is not claimed.** This is consistent with the registration.

**The advantage of the emotion axis is limited to the readout whose vocabulary matches the estimation target.** The explanation of vocabulary and ontological self-consistency cannot be excluded.

## CG4. Relationship to the Judgement Table of Amendment 86 CE3

In the CE3 table, "emotion axis → A exceeds, appraisal axis → B does not exceed" corresponds to (i) "the asymmetry is real." **This row holds formally, but per CG3, it is not used for level-3 claims.**

There is no contradiction. CE3 is the condition for the **inter-family contrast**, and CF4 is the precondition for the claim of **axis privilege**; the latter is not satisfied. **Therefore what the present study can write is limited to the inter-family contrast, and "the emotion category axis is a privileged coordinate" is not written.**

## CG5. What Can Be Written (Confirmed in This Amendment)

**Can be written (1)**: When output perturbation (full-vocabulary JSD, $J^\*=0.05$) is matched and a same-size random family best with fully eigenvalue-matched variance profiles is used as the floor, **directions estimated from human emotion categories move the model's emotion word output beyond this floor.** 9/9 models, excess SD median +3.17, $p_G \le 0.0005$, 2 readout types consistent.

**Can be written (2)**: **Directions estimated from human appraisal dimensions do not exceed the same floor** (0/9, +0.18 SD). **Even against a readout B that matches their own vocabulary, they do not exceed the floor in a majority of models** (0/9, +0.39 SD, $p_G<0.01$ in 3/9).

**Can be written (3)**: **The effect size in the self-consistent readout differs by an order of magnitude between the two families** (emotion +3.17 vs. appraisal +0.39). Both families are estimated with the same procedure (ridge in the inner partition) and scored with their respective readouts. **This difference is not explained by self-consistency alone.**

**Cannot be written (1)**: That the emotion category axis is privileged **in general.** It does not transfer to readout B (+0.03 SD, 0/9).

**Cannot be written (2)**: That appraisal theory does not explain LLM emotion representation. Level 2 has not been executed, and the resolution of readout B is also limited (AUC 0.55–0.81).

## CG6. Adding a Diagnostic (Not Used for Judgement)

The comparison in CG5(3) is exposed to the possibility that the quality of the readout differs between the two families. Readout B has a validity check (AUC), but **readout A has no corresponding quality indicator.**

**Added diagnostic (defined before seeing results)**: For readout A, for stimuli in each emotion category of crowd-enVENT, **in the unintervened state**, the proportion for which the self-word has the highest probability among 13 words (top-1 match rate) and the rank of the self-word for each stimulus are measured. This is identical to the check imposed on R-act.

**This diagnostic is not used for the judgement.** It is reported as material for reading the effect-size comparison in CG5(3). **If the top-1 match rate for readout A is markedly higher than the AUC for readout B, the order-of-magnitude difference in CG5(3) may be explainable by the difference in readout quality; this is stated explicitly as a limitation.**

## CG7. What to Execute Next

```
① Quality diagnostic for readout A (CG6; all 9 models)
② L2 (subspace privilege, amendment 77) — direct test of the principal investigator's hypothesis. Not yet executed
```

**The results of L2 do not change the judgement of this amendment.** L2 is a different question about the subspace.

## CG8. Commitments

- The non-satisfaction of precondition IND is reported as-is, and level 3 is not claimed
- Both the formal satisfaction of CE3 (i) and the non-claiming of level 3 are written
- The distinction in CG5 — "3 things that can be written" and "2 things that cannot be written" — is not collapsed in the manuscript
- The CG6 diagnostic is not used for the judgement. If readout quality difference may explain the order-of-magnitude difference, it is written as such
- The fact that the emotion axis advantage is localized to readout A is written in the **results** section, not in the limitations
