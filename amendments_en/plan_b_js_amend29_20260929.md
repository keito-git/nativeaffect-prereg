# Pre-registration Amendment 29: Prediction B failed. Register a 2×2 cross-domain design.

**Target**: Judgement on Prediction B from Amendment 26 Z4, and the follow-up Experiment C (cross-domain)
**Created**: a group member / 2026-09-29
**Status**: Experiment B has **layer 11 confirmed; layers 16, 22, and 27 are running**. Experiment C has not been executed.

---

## AC1. Prediction B failed

**Prediction B (Amendment 26 Z4)**: GSM8K-derived sensitivity directions are weaker on emotional stimuli than emotion-derived ones.

**Measured results (layer 11, E1 validation set 143 stimuli, Arm II, fp32, registered floor)**

| Direction origin | Passes registered criterion | δ_a min / med / max |
|---|---|---|
| **Emotion-derived** (E1 discovery half 144 items) | **10/10** | +0.371 / **+0.804** / +1.000 |
| **GSM8K-derived** (math problem texts 144 items) | **8/10** | −0.133 / **+0.832** / +1.000 |

δ_a for 10 GSM8K-derived vectors: +1.000 / +0.692 / +1.000 / +0.510 / +0.748 / +0.944 / +0.986 / +0.832 /
**−0.133 (p=0.3465, fail)** / **+0.161 (p=0.0693, fail)**

**The median is higher for GSM8K-derived than emotion-derived (+0.832 vs. +0.804).** Pass count is 8/10 vs. 10/10, only marginally fewer.

**Apply the clause registered in Amendment 26 Z4 for "if equal or higher"**:
> **The effect is not specific to emotion. It is the general fact that "high-output-sensitivity directions move the output," and Paper 3 cannot be written as an emotion paper. Rewrite it as a methodology paper.**

**The stimulus set will not be switched to try again** (stated explicitly in Amendment 26 Z4).

## AC2. Findings that survive

**Principal components, regardless of the origin of the direction, do not exceed the floor.**

| How the direction is selected | Emotion-derived | GSM8K-derived |
|---|---|---|
| Output sensitivity (Jacobian) | 10/10 | **8/10** |
| Activity reproducibility (ICA) | 1/20 | 1/20 |
| **Variance magnitude (principal components)** | **0/10** | **0/10** |

**What is established**: **the selection criterion is decisive, and the domain of the stimuli used for selection is not essential.**
Selecting by variance magnitude does not exceed the floor. Selecting by activity reproducibility does not either. Exceeding the floor happens only when selected by output sensitivity.

**This directly addresses the confound that Paper 2 identified (high-variance directions work because they are high-variance).**
**However, it is not evidence that the effect is specific to emotion.**

## AC3. Experiment C: 2×2 cross-domain design (asking whether domain specificity exists)

**AC1 only shows "both exceed the floor."**
**"Does each work stronger in its domain of origin?" has not been measured.** This is a different question, and
**if it holds, it would mean the model has domain-specific sensitivity structure** (a weak version of the principal investigator's vision, but substantive).

### Design (4 cells; 2 already obtained)

| | Emotional stimuli (E1 validation set 143) | Non-emotional stimuli (GSM8K 143) |
|---|---|---|
| **Emotion-derived directions** | **Already obtained** 10/10, med +0.804 | **Not yet obtained** |
| **GSM8K-derived directions** | **Already obtained** 8/10, med +0.832 | **Not yet obtained** |

**Execute the 2 not-yet-obtained cells.** Floor, JS, Arm II, fp32, PMF 100 draws are identical to the existing runs.
GSM8K test stimuli are **143 items different from the 144 used in construction**
(`gsm8k_train.jsonl`, seed 20260929, extracted after excluding the 144 construction items).

Estimated duration: 10 × 4 layers × 100 floors × 143 stimuli × 2 cells ≈ **11.6 hours**

### Prediction C (fixed before seeing data)
**The diagonal δ_a medians (origin and test domain match) are greater than the off-diagonal ones.**
That is, `emo×emo > emo×math` and `math×math > math×emo`.

- **If this holds**: **The sensitivity structure is domain-specific.** The claim "AI has different sensitivity directions for each domain" becomes possible. **Emotion can be treated as one instance**
- **If this does not hold** (diagonal and off-diagonal are equivalent): **The sensitivity structure does not depend on domain.**
  The effect is only the general property of output sensitivity, and **the conclusion from AC1 (methodology paper) is final**
- **If only one side holds**: report as asymmetric and specify which domain is the special one

**Prediction C being wrong is entirely possible. If wrong, write that.**

## AC4. Execution order
1. Remaining 3 layers of Experiment B (layers 16, 22, 27) — running now, approx. 5 hours
2. The 2 not-yet-obtained cells of Experiment C — approx. 11.6 hours
3. Remaining 2 layers of Experiment A (validation set, layers 22, 27) — approx. 11 hours

**GPU will be used in order 1→2→3.** Sync to local upon completion of each stage
(a server was inaccessible on 2026-09-29, so results will not be left on the server only).
