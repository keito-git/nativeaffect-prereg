# Pre-Registration Amendment 66: Shifting from Necessity to Sufficiency —
# Is the Appraisal Readout a Sufficient Bottleneck for Emotion?

**Created**: 2026-10-06
**Principal investigator instruction**: 2026-10-06 "Show, at least partially and from a different angle, that the concept of emotion is based on other concepts."
**Status**: **New primary line**. Existing judgements (X1, V1″, X2″, X4) are not changed.
**Activation condition**: No judgement must be made until this file has been committed and pushed. **Never run once.** The estimator, control, and criteria are fixed in this file.

---

## BO1. X1 Was Asking the Wrong Question

X1 (Amendment 53 BB2) measured the following.

> When the appraisal subspace $\mathcal{A}$ (21 dimensions) is **projected out**, does the decoding accuracy for emotion families drop to chance level?

**It did not drop in all 10 models** (the decrease was at most 0.0053, and in 4 models it increased).

**This is to be expected.** Removing 21 dimensions from $d=4096$ leaves the representation nearly intact, and **the removal is a test of necessity**. What is needed to support the claim "emotion is based on appraisal" is **sufficiency**, not necessity.

**The non-holding of X1 was an error in the question, not a falsification of the hypothesis.** This correction is explicitly stated in the paper.

## BO2. The New Question — Sufficiency

> **Can the model's own 21 appraisal readout values predict emotion families as well as the 4096-dimensional representation?**

If they can, **emotion families in the model are a (low-dimensional) function of appraisal concepts.** This is a testable form of "the concept of emotion is based on other concepts."

## BO3. Estimators

The appraisal probe $v_a$ fit on training rows (Stage A, $\lambda$ selected by inner partition) is used. **On evaluation rows, only 21 values — the probe outputs $\hat r_a = v_a^\top \tilde h$ ($\tilde h$ is the representation standardized by training-row statistics) — are used as features.**

The 13-emotion-family classification is measured by macro-F1 (same classifier, ridge, $\lambda$ selected by inner partition).

| Symbol | Features | Status |
|---|---|---|
| $F_{\text{full}}$ | Standardized representation $\tilde h$ (4096 dimensions) | Reference upper bound |
| **$F_{\text{app}}$** | **21 appraisal probe outputs** | **Primary estimator** |
| $F_{\text{rand}}$ | Random linear projections of $\tilde h$ (21 projections, 500 trials) | Control with matched dimensionality |
| **$F_{\text{pc}}$** | **Top 21 principal components** | **Control with matched dimensionality and variance (primary control)** |
| $F_{\text{human}}$ | 21 human ratings | Reference for the human side (not a control) |

**$F_{\text{pc}}$ is the primary control.** Random projections include directions with small variance and are lenient. **The top 21 principal components are the linear code with the most information in the same dimensionality, and it is required that the appraisal readout be comparable to them.** This is the representational version of VMIC from Paper 2.

## BO4. Judgements

- **S1**: $F_{\text{app}} > F_{\text{rand}}$ 95th percentile
- **S2**: $F_{\text{app}} \ge F_{\text{pc}}$ (primary control; **not inferior to the top 21 principal components**)
- **S3**: $F_{\text{app}} \ge 0.90 \times F_{\text{full}}$ (sufficiency; 90% or more is retained in 21 dimensions)

**Judgement S**: All of S1, S2, and S3 are satisfied for the **majority of the 10 models**.

**Null soundness** (revised gate from Amendment 57 BF2): The distribution of $F_{\text{rand}}$ is non-degenerate (SD > 0, interquartile range > 0, at least 10 distinct values). **If not satisfied, no judgement is made.**

## BO5. Minimum Count — How Many Concepts Are Sufficient?

Performed only if S holds.

**Forward greedy selection using only training rows** (evaluation rows are not seen at all). Report the minimum number of evaluation dimensions $k^\*$ at which $0.90 \times F_{\text{full}}$ is reached, and the **order in which dimensions are selected**. Evaluation is done on evaluation rows.

**Whether $k^\*$ and the selected concepts are consistent across 10 models is reported.** If consistent, one can write "emotion families are a function of $k^\*$ appraisal concepts." If inconsistent, one writes "different sets of concepts constitute them in different models." **Either outcome is reported.**

## BO6. Claimable Proposition (If S Passes)

> The model's own appraisal readout **in 21 dimensions** retains 90% or more of the predictability of emotion families that the **4096-dimensional representation** possesses, and is not inferior to a same-dimensionality top-principal-component code. That is, in the model, **emotion families are a low-dimensional function of appraisal concepts**.

**Limitations to be reported alongside**:
- **This is a representational claim, not a causal claim.** Showing that emotion can be controlled through intervention requires a separate step, and in this research series this has not been established under a variance-matched floor (V1″ not held)
- **The appraisal concepts themselves are a framework defined by humans** (the 21 dimensions of crowd-enVENT). This is not "a concept not conceptualized by humans"
- The information about emotion families is **not inside** the appraisal subspace (X1). **What is sufficient is the appraisal readout; it is not that the appraisal subspace contains emotion** — this distinction is written clearly

## BO7. How This Claim Differs from Prior Work

- Tak et al. 2025 (Findings of ACL 2025) showed that appraisal dimensions are **linearly decodable** and that **emotion moves when intervened upon**. They did not show **that the appraisal readout is a sufficient bottleneck for emotion**
- Choi & Weber 2026 showed that emotional representations are consistent with valence–arousal. They did not perform **a comparison of the predictability between 21-dimensional appraisal codes and the full representation**
- **The design of placing top principal components as a control with the same dimensionality has not been found in prior work reviewed**

**Priority is re-confirmed before execution** (obligation from Amendment 47 AV6).

## BO8. Commitments

- The file is pushed before making any judgements
- The non-holding of X1 is corrected as "an error in the question," and **the results of X1 are not hidden**
- $F_{\text{pc}}$ (top 21 principal components) is used as the primary control. **The result is not written as if passing only through random projections**
- The threshold 0.90 in S3 is not changed after seeing results
- The fact that this is a representational claim, not a causal claim, is explicitly stated
- If $k^\*$ is inconsistent across 10 models, that is reported as-is
