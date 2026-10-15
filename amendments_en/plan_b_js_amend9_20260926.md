# Pre-Registration Amendment 9: The CRH (ICML 2026) Control Is Norm-Matched, Not Variance-Matched

**Target**: Amendment 3 C3 (treatment of novelty for the variance calibration control), framing of Condition 3
**Created**: 2026-09-26
**Status**: **Before experiment**
**Source**: Full-text PDF of arXiv:2605.01844v2 (read directly from Appendix K.2 by the group)

---

## I1. Background

During a literature check, **Cylindrical Representation Hypothesis (CRH, arXiv:2605.01844, ICML 2026 accepted)** was raised as potentially partially overlapping with Condition 3.
The point of contention was the control design of **Appendix K.2 "Probing on a Random Cylinder."** Since ar5iv and arXiv HTML both cut off at Appendix E, the group obtained the PDF and read it directly (the first download had broken xrefs and a second fetch was needed).

## I2. Actual Content of the K.2 Control (From the Original Text)

> "**Setup.** We run a matched null control on Gemma-2B-IT at layer 9. We use the same probing objective and **the same norm budget** as the main probe. The only change is that we replace the PCA-derived cylinder directions with **random directions**."

> "**Result.** The optimized directions produce stronger axis and phase structure, while the random directions produce a much flatter landscape. … Therefore, **only semantically meaningful direction and normal plane can produce structured loss landscapes**."

Numerical values (Table 4, Gemma-2B-IT layer 9): mean loss 38.72 vs. 39.80, loss standard deviation 3.43 vs. 1.16, axis-direction range 6.05 vs. 1.59, phase-direction range 0.51 vs. 0.07.

## I3. Judgement: Condition 3 Has Not Been Pre-Empted

**The CRH control is "random directions with matched norm budget."** The paper **does not state that the random directions are drawn from the same subspace or the same variance profile as the optimized directions.**

**And the conclusion is "only semantically meaningful directions and normal planes produce structured loss landscapes." This is exactly the type of reasoning our Condition 3 states "cannot be reached without a variance-matched control."**

**Therefore CRH does not pre-empt Condition 3. Rather, it is an instance of the practice that Condition 3 points out.** The framing of Amendment 3 C3 "demonstrated that already-used controls are necessary" can be maintained, and **one more instance has been added.**

## I4. Three Constraints on How to Write (Preventing Overclaiming)

1. **Do not assert "they drew from the full space."** The original text only writes "random directions" and does not explicitly state what space they were drawn from. **What can be written is limited to "the random directions are matched only in norm budget, and no statement is made about matching subspace or variance profile"**
2. **Explicitly state that the outcome metrics are different.** CRH examines **the structure of the loss landscape**, while we examine **changes in output distributions**. The settings are not the same, so **we do not claim that the specific conclusions of CRH are wrong**
3. **It is an ICML 2026 accepted paper.** Do not treat it critically; **cite it in the form "the same problem appears in the most recent peer-reviewed research," as corroborating evidence for the necessity of Condition 3**

## I5. What Was Also Confirmed (Update to Amendment 3)

- **The mechanism is independent.** CRH explicitly states that separability-based and variance-based metrics do not predict steering outcomes well ("separability estimates…do not always correlate well with actual steering outcomes"). **Our variance-proportionality claim is incompatible with CRH and is an independent contribution**
- **The qualitative phenomenon (where along the direction within the representation subspace matters for the result) is preceded by CRH.** **Cite it here and do not write "we showed this"**
- **The only precedent for in-plane control is Sun et al. (arXiv:2604.03147).** CRH does not use in-plane control

## I6. Record

**This confirmation was completed before the experiment.** The conservative decision written in Amendment 3 C3, "maintain as a demonstration of necessity," was confirmed by full-text reading.
**Because the HTML version was cut off partway through, judgement was held until the PDF was obtained.** Record that the judgement was not made from aggregated HTML or secondary information.
