# Pre-Registration Amendment 61: Discovery Set Results for the Aggregate Test (Positive) and
# Clarification That the Role of the Positive Control Is Asymmetric

**Created**: 2026-10-05
**Target**: Judgement V1″ in Amendment 60, Prerequisite V3′ in Amendment 58
**Judgement**: **$\bar S$ exceeded the null p95 in the discovery set (exploratory). Confirmation will be done with the 6 confirmation set models.**
**Principal investigator policy (2026-10-05)**: Do not make negative results the main axis; place discovery and intervention as the primary results.
**Activation condition**: Claims based on the reading in BJ3 must not be written in the paper until this file has been committed and pushed. Execution of the confirmation set is already underway as registered in Amendment 60 (pushed `7517e80`).

---

## BJ1. Discovery Set Results (Exploratory, as per the partition in Amendment 60 BI3)

$\bar S$ is the mean of the signed effects across adopted evaluation dimensions. The null is the distribution of the mean drawn one from each dimension's floor distribution (2000 trials). $J^\*=0.05$.

| Model | Floor trials | $\bar S$ | Between-dimension SD | Null mean | Null SD | Null p95 | **Effect** |
|---|---|---|---|---|---|---|---|
| Mistral-Nemo-12B | 40 | **+0.0952** | 0.1168 | −0.0045 | 0.0335 | +0.0512 | **+2.98 SD** |
| Llama-3.2-1B | 200 | **+0.1079** | 0.1468 | +0.0023 | 0.0374 | +0.0642 | **+2.83 SD** |

**Both have $\bar S >$ null p95.** The signs are aligned, and the movement is **in the direction predicted by human ratings**.

**This is exploratory.** The dimension-level values for the 4 discovery set models were in hand before this amendment was created.

## BJ2. The Aggregate Values for the Remaining 2 Models Are Not Yet Computed at the Time of This Amendment

The aggregate values for OLMo-2-7B and Gemma-2-9B were not included in this round of computation due to a filename issue (the 40-trial outputs were saved without the `_nf` suffix). **The computation will be corrected and all 4 models will be reported.** Only the 2 convenient models will not be shown.

## BJ3. The Role of the Positive Control Is Asymmetric (Clarification)

The current output is "unmeasurable (positive control did not reach the floor)." This follows the letter of the implementation in Amendment 58 BG5. **However, the logical role of the positive control is asymmetric.**

The wording when V3 was introduced in Amendment 49 AX6 was:

> If it does not move them, **this constitutes insufficient measurement resolution, and failure of V1 is not claimed.**

**The positive control is a condition that protects the claim that "there is no effect."** It is a safeguard against interpreting the non-appearance of an effect when measured with a blunt instrument as "there is no effect."

**If an effect is seen even when measured with a blunt instrument, that effect cannot be explained by the bluntness of the instrument.** Therefore, the positive control is not a necessary condition for a positive claim.

**However, Amendment 58 wrote "if it does not exceed, the result is unmeasurable."** By its letter, the result is unmeasurable. **The letter is not conveniently reinterpreted.** The following procedure is taken.

1. **The output of the registered letter (unmeasurable) is recorded as-is**
2. **The asymmetry is clarified in this amendment and applied to subsequent judgements**:
   - If the positive control does not exceed the floor, **a negative result ($\bar S \le$ p95) is unmeasurable**
   - **A positive result ($\bar S >$ p95) is judged.** However, **the status of the positive control is always reported alongside**
3. **Confirmation is done with the confirmation set.** The 6 confirmation set models were registered in Amendment 60, and the clarification of asymmetry in this amendment is also **performed before seeing the confirmation set results**

## BJ4. Confirmation Set (Unchanged from Amendment 60 BI3)

OLMo-2-13B / Gemma-2-2B / Llama-3.1-8B / Phi-3-medium / Phi-3.5-mini / Ministral-8B

**Pass condition**: $\bar S >$ null p95 for the majority of the 6 models. The condition "majority of models that have the positive control exceeding the floor" from Amendment 60 BI3 **is not applied to positive results** due to the asymmetry in BJ3. The status of the positive control is reported in a table for all models.

## BJ5. The Form of the Claim (If the Confirmation Set Passes)

> In language models, an intervention on appraisal concept directions moves the emotion output **as a family** in the direction predicted by human ratings. This holds under output perturbation equalization and a variance-matched in-plane floor, across 10 models and 5 families.

**Limitations to be reported alongside**:
- **Individual evaluation dimensions cannot be separated from the floor** (effect size is on the same order as the floor spread). "The `pleasantness` direction controls emotion" is not written
- The information about emotion families is not exhausted in the appraisal subspace (X1, not held for 10 models)
- When topics are matched, there is no agreement in emotion families across models (M1′)

**The claim holds even with these limitations stated.** "Appraisal concepts move emotion" and "emotion is exhausted by appraisal concepts" are different propositions.

## BJ6. Commitments

- The discovery set results are **explicitly labeled exploratory**
- The 2 models in BJ2 are added to the computation, and **all 4 models are reported**
- The output of the registered letter (unmeasurable) is retained in the record
- If the confirmation set is negative, **negative is written**. The asymmetry in BJ3 is not used to evade negatives
- No dimension-level claims are made
- The non-holding of X1 and M1′ is reported alongside. Inconvenient results are not omitted
