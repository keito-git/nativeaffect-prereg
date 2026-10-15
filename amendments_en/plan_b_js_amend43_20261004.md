# Pre-registration Amendment 43: The null for P1 was in the wrong direction. Recording as unjudgeable and registering the correct null.

**Created**: 2026-10-04
**Target**: Prediction P1 (intrinsic dimensionality) of Amendment 41
**Judgement**: **Registered P1 is unjudgeable. The criterion is not changed; a new null is registered separately.**
**Activation condition**: No judgement using the new null shall be performed unless this file has been committed and pushed beforehand.

---

## AR1. What happened

P1 of Amendment 41 registered the following:

> **Estimator**: The number of dimensions explaining 90% of the variance, from the singular value spectrum of the category means $\{u_e\}$.
> **Null**: Random category assignment with the same count and dimensionality (label permutation within skeleton, 500 iterations).

Upon execution, it was found that **the direction of the null is the reverse of the design intent**.

When labels are permuted within a skeleton, each "category" mean becomes the mean of randomly selected stimuli. Random means resemble one another and converge toward the overall mean. Therefore **the category mean matrix under the null has low rank**.

The observed value (true category assignment) has structure, so its rank comes out **higher** than the null. The judgement "observed < 5th percentile of null" is **structurally impossible** with this design.

## AR2. Measured values (not used for judgement)

Qwen3-8B, E4 (direct emotion word writing, 40 categories, 80 sentences).

| Layer | rank90 | Null mean | Null 5th pct | Registered judgement |
|---|---|---|---|---|
| 0 (mean pooling) | 33 | 12.3 | 10.0 | Not established |
| 11 | 22 | 20.6 | 19.0 | Not established |
| 16 | 22 | 21.8 | 21.0 | Not established |
| 22 | 22 | 21.2 | 20.0 | Not established |
| 27 | 20 | 18.4 | 17.0 | Not established |

**Under the registered criterion, the result is not established at all layers. This judgement is recorded as-is.**

However, **looking at the observed values alone without the null, there is a reduction of 11–13 dimensions from 33 at layer 0 to 20–22 at layers 11–27**. The embeddings of 40 emotion words are nearly orthogonal, so 33 dimensions are required at layer 0, but passing through contextual computation compresses them to nearly half. This is consistent with the form of projection described by AAPH, but **we do not claim this at present because there is no appropriate null**.

## AR3. The correct null for the question

The question of P1 is "is the dimensionality lower **than when 40 categories each have an independent direction**?" Therefore the null must be not something that destroys the category structure, but **the case where categories each have independent directions**.

**Null N' (independent category null)**: While preserving the observed within-category covariance, generate 40 category means as **mutually independent directions**. Specifically:

1. Estimate the within-category residual covariance $\Sigma_w$ from the observed data.
2. Draw 40 mean vectors independently from an isotropic distribution on $\mathbb{R}^d$, matching the norm distribution of the observed category means.
3. For each category, generate the same number of samples as observed from $\Sigma_w$ and add them.
4. Compute rank90 of the resulting matrix. Repeat 500 times.

**Judgement P1'**: The observed rank90 falls **below** the 5th percentile of null N'. Additionally, rank90 is measured with the same null at layer 0, and it is also required that the **increment rank90(L) − rank90(0) is negative and falls below the 5th percentile of the same increment under the null** (layer 0 control of Amendment 40).

Passing is defined as meeting these conditions in **3 or more out of 4 layers**.

## AR4. Not discarding the permutation null

The permutation null cannot be used for the judgement of P1, but it is **valid for a different question**.

> "Does a categorical structure exist?"

This should be measured not by rank but by the **ratio of inter-category to intra-category distance** ($\mathrm{CS}$ of Amendment 40), for which the permutation null is the correct null. The two were confused with each other.

**Statistics and nulls must be designed as a pair.** Deciding only one and repurposing the other can produce a test in the wrong direction, as in this case.

## AR5. As a record

This case is an **example of pre-registration preventing a criterion from being moved for the convenience of results**. The measured values (layer 0: 33 → layer 11: 22) look favorable to the hypothesis, but under the registered criterion they are not established, and that fact is recorded first. Rewriting the criterion retrospectively to "observed < layer 0" would make it appear to pass, but that would be changing the criterion after seeing the results, and will not be done.

The new null N' is defined in this amendment **before seeing the results** and will be executed after push.

## AR6. Promises

- The failure of the registered P1 will be reported as-is. It will not be concealed by substitution.
- The definition of null N' will be fixed in this file and will not be changed after execution.
- If P1' is not established, it will be recorded that AAPH's P1 was not supported.
