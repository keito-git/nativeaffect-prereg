# Pre-Registration Amendment 15: Withdrawing the Mechanistic Explanation of Amendment 14. Half Was Already Known; Half Was Refuted by Our Own Data

**Target**: Amendment 14 (mechanistic prediction and claim)
**Created**: 2026-09-26
**Status**: Layer 11 of G1's 4 layers is complete. **Judgement statistics have not been computed**
**Source**: (1) Descriptive check for layer 11 (`03_解析/plan_b/G1_jacobian/layer11.json`), (2) Full-text confirmation by the team (`01_調査/追記14の主張の先行性調査_20260926.md`)

---

## O1. Withdrawing

**The mechanistic explanation described in Amendment 14 N3 will not be written.** There are 2 reasons, and **either one alone is sufficient to preclude writing it.**

### Reason 1: Prediction P Failed (Our Own Data)

The prediction registered **before seeing results** in Amendment 14 N2.

> **Prediction P**: Sensitivity directions greatly overlap with the subspace spanned by the top 10 principal components. **Mean cosine of principal angles is 0.70 or above.**

**Empirical measurement for layer 11**: `max_abs_cos_with_top10_PC = 0.1727`. **Since the maximum is 0.17, the mean is 0.17 or below. Far below 0.70.**

**The prediction failed.** Per the rule of Amendment 14 N4, the mechanistic explanation will not be written. **Do not write "partially supported."**

**The values for the remaining 3 layers will also be collected and recorded, but since the layer 11 value is far from the threshold, the conclusion is not expected to be overturned.** If it is overturned, it will be recorded at that time.

### Reason 2: The First Half of the Mechanism Was Already Known (Full-Text Confirmation by the Team)

**arXiv:2608.22985 (Gao et al., What Does Activation Steering Control?) has already shown that it constructs an output-sensitive subspace from the Jacobian of logit differences and that this subspace carries almost all of the effect.**

Original text (confirmed in full by the team):

> "g_{x,a,b} = ∇_{h_{ℓ,p_pre}(x)}[z(o_a)−z(o_b)]"
> "The validation-selected projection contains **15.4% of the direction's squared L2 energy** but retains **96.3% [95.8, 96.7]** of its extraction-index effect"

**That is, "the top singular structure of $J$ determines the effect" has been shown by prior work.** The only part we could have claimed as new was the connection "that coincides with the principal components of activations," but **by Reason 1, that connection does not hold in our data.**

**Therefore the mechanistic explanation of Amendment 14 is preceded in its first half and refuted in its second half. Nothing remains.**

## O2. What Remains

**Condition 3 remains.** That is, the claim that **"directions cannot be identified under a control with matched projection lengths."**

- arXiv:2608.22985 uses **covariance-matched random controls (controls with matched norms)**, but **has not reached the design of randomizing directions while keeping the projection-length vector onto each principal component fixed** (confirmed in full text by the team)
- Therefore **Condition 3 remains independent**. This is the content already claimed in Paper 2 (methodology paper), and **nothing new has been added**

**Claims ② (regressing effect size from variance profile) and ③ (effect is explained by geometric quantities) remain independent.** However, **②③ are the targets to be confirmed in the N5 measurement of Amendment 14 and cannot be stated as claims in advance.** Decide what can be said after seeing the $R^2$ values.

## O3. How to Write (Confirmed)

- **Write "the reason the floor wins is unexplained."** As per Amendment 14 N4
- **Cite arXiv:2608.22985 and explicitly state the relationship.** Make clear in the main text that we do not claim "the top singular structure of $J$ determines the effect"
- **Do not search for another mechanism and fit it in.** Presenting a third explanation after Reasons 1 and 2 have come to light is the same act prohibited by Amendment 14 N4
- **Do not rewrite Amendment 14's file.** The record itself of registering a prediction and having it fail has value

## O4. The N5 Measurement Will Be Executed (Decision Unchanged)

**The variance dominance rule measurement (1,000 random directions from the top principal component subspace, regression of 10-dimensional projection lengths to JS for held-out $R^2$) will be executed as planned.**

**Reason**: Amendment 14 N6 stated "N2–N5 have value independent of whether G1 passes or fails." **Even after the mechanistic explanation is withdrawn, the measurement value of $R^2$ itself can be reported.**
**However, if $R^2$ is high, do not write "therefore the mechanism is this."** Report it as a measurement value and **do not provide an explanation.**

## O5. What Should Be Recorded

**Amendment 14 was withdrawn within one hour because a prediction had been registered with specific numbers before seeing the results.**
**If the mechanistic explanation had been written first and the numbers seen afterward, the value 0.17 might have been written as "partly consistent."**

**And the prior art confirmation also judged at the abstract level "independent." It was only after reading the full text that "the top singular structure of $J$ determines the effect" was found to be already known.**
**When establishing the core of a claim, read at least one nearest paper in full text.** This is the second instance of the same type of event today (first instance: isometric intervention found in 4 existing works).
