# Pre-registration Amendment 44: P1′ passes for E4; E5 is unjudgeable because the null is degenerate.

**Created**: 2026-10-04
**Target**: Prediction P1′ (dimensionality test using independent category null N′) of Amendment 43
**Judgement**: **E4 passes. E5 satisfies the registered criterion numerically but is not counted as evidence because the null is degenerate.**
**Activation condition**: No judgement using an alternative statistic for E5 shall be performed unless this file has been committed and pushed beforehand.

---

## AS1. Execution results (recorded as-is)

Qwen3-8B, layer 0 is mean pooling (Amendment 40 AO7), layers 11/16/22/27 are final token. Null N′: 500 iterations.

### E4 (direct emotion word writing, 80 sentences, 40 categories): **4/4 layers pass**

| Layer | rank90 | Null mean | Null 5th pct | Below | Increment from layer 0 | Increment null 5th pct | Below |
|---|---|---|---|---|---|---|---|
| 0 | 33 | 25.56 | 24.0 | No | — | — | — |
| 11 | 22 | 31.98 | 31.0 | Yes | −11 | +4.0 | Yes |
| 16 | 22 | 32.74 | 32.0 | Yes | −11 | +5.0 | Yes |
| 22 | 22 | 32.02 | 32.0 | Yes | −11 | +4.0 | Yes |
| 27 | 20 | 32.10 | 32.0 | Yes | −13 | +4.0 | Yes |

**At layer 0, the null is not exceeded (33 vs. 5th percentile 24). Compression first appears at layer 11 and beyond.**
Where 40 categories with independent directions would require approximately 32 dimensions, the actual requirement is 22–20 dimensions.

### E5 (no emotion words, 169 sentences, 40 categories, 28 skeletons): **Numerically 3/4 pass. Not adopted.**

| Layer | rank90 | Null mean | Null 5th pct | Increment | Increment null 5th pct |
|---|---|---|---|---|---|
| 0 | 30 | **33.00** | **33.0** | — | — |
| 11 | 29 | **33.00** | **33.0** | −1 | **+0.0** |
| 16 | 29 | **33.00** | **33.0** | −1 | **+0.0** |
| 22 | 30 | **33.00** | **33.0** | +0 | **+0.0** |
| 27 | 29 | **33.00** | **33.0** | −1 | **+0.0** |

## AS2. Why E5 is not adopted

**The null mean and 5th percentile are completely identical at all layers. The variance of the null is nearly zero.**

With a null that has no variance, we can determine whether the observed value exceeds or falls below it, but **we cannot judge whether that difference is within the range of chance**. The p-value takes only 0 or 1. This is not a test.

Furthermore, the increment null 5th percentile is +0.0 at all layers. Therefore "the increment falls below the null" means in substance **"the rank decreased by even 1 dimension from layer 0"**, and the null eliminates nothing. The 3/4 pass for E5 derives from rank90 decreasing by 1 at layers 11, 16, and 27.

**Mechanism**: `rank90` returns a deterministic value for 40 equal-norm orthogonal vectors. Since the norms of E5's category means are nearly uniform, the null's 40 vectors become nearly equal-norm orthogonal each time, and rank90 always becomes 33. For E4, the null mean at layer 0 moved to 25.56, indicating that the null was functioning. **The same null functions for one stimulus set and does not for another.**

This falls under the **null no-op** type identified in "audit the measurement before interpreting." It must not be passed simply because it satisfies the registered criterion.

## AS3. What is claimed and what is not

**Claimed (E4)**: At layer 0, the means of 40 categories require 33 dimensions, indistinguishable from independent directions; but at layers 11 and beyond, they are compressed to 22–20 dimensions. **This compression is not explained by word identity; it is produced by the model's contextual computation.** This is consistent with the form of projection described in Amendment 41's P1.

**Not claimed (E5)**: Whether the same compression occurs for stimuli that do not contain emotion words. **Unjudgeable at the present time.**

Therefore what can currently be said is only: **"For stimuli where emotion words are written out, the categorical structure is lower-dimensional than independent directions, and that is produced by computation rather than vocabulary"**, and **"emotion categories in general are projections of a low-dimensional latent axis" cannot be said**.

## AS4. Registering an alternative statistic for E5

`rank90` takes only integer values for 40 categories and lacks resolution. **Replacing it with a continuous quantity.**

**Statistic ER (effective rank)**: For the singular values $s_i$ of the category mean matrix,

$$\mathrm{ER} = \left(\sum_i s_i^2\right)^2 \Big/ \sum_i s_i^4$$

This is the participation ratio of eigenvalues; it returns $k$ for $k$ equal-norm orthogonal vectors, but **responds to continuous changes in the singular value distribution**. The construction of null N′ remains unchanged from Amendment 43.

**Judgement P1″**: The observed ER falls below the 5th percentile of null N′, **and** the increment $\mathrm{ER}(L) - \mathrm{ER}(0)$ falls below the 5th percentile of the same increment under the null. Passing requires **3 or more out of 4 layers**.

**Confirm null soundness first**: Confirm that the standard deviation of the null ER is not 0, and **if the standard deviation is less than 1/10 of the difference between the observed and null, record it as unjudgeable for this statistic as well.** Do not pass judgement without confirming that the null is functioning.

## AS5. Disclosure: computation of ER values began before this file was created

Immediately after noticing that the null for E5 was degenerate, **we began computing the null distribution of ER on hand in order to isolate the cause**. Therefore we may know the value of ER at the time of writing this amendment.

**This sequence of events will not be concealed. The ER analysis for E5 will be reported as exploratory and will not be treated as confirmatory evidence.** Confirmation will be performed by one of the following:

- **Replication in other models** (P2). The judgement criterion is fixed in this file and will have been pushed before the execution of each model.
- **Split validation of E5**. The 28 skeletons are divided in half, and we check whether the direction found in one half is replicated in the other.

## AS6. Promises

- **Both the pass for E4 and the unjudgeable for E5 will be reported as-is.** We will not select only one.
- We will not change the null for E5 in the direction of relaxing the criterion because "its variance is small."
- If the null is also degenerate for ER, **E5 will be written in the paper as unjudgeable as-is**.
- The 3/4 pass of E5 under `rank90` registered in Amendment 43 will **not be cited as an achievement**.
