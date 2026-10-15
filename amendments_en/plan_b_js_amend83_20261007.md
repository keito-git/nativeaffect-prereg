# Pre-registration Amendment 83: VMIC Was Not Variance-Matched. The Floor Is Corrected and the Partition Leakage Is Also Fixed

**Created**: 2026-10-07
**Occasion**: Point 1 of external review (2026-10-07, 3rd round). Obtained after passing draft v3.
**Judgement**: **The primary result of draft v3 does not use the registered "variance-matched floor." Remeasurement will not be claimed until the floor is corrected and remeasurement is performed.**
**Activation condition**: Remeasurement judgements must not be performed until this file has been committed and pushed.

---

## CB1. Content of the Critique (from the external reviewer)

Given the covariance $\Sigma = U\Lambda U^\top$ of the activations, the variance seen by direction $v$ is

$$v^\top \Sigma v = \sum_i \lambda_i a_i^2, \qquad a = U^\top v.$$

**Permuting the components of $a$ across principal components** gives $\sum_i \lambda_i a_{\pi(i)}^2$, which **does not in general equal the original.** Preserving the multiset $\{a_i^2\}$ is different from preserving $\{\lambda_i a_i^2\}$.

**The critique is correct.** `floor_F4` is:

```python
c = P[:k] @ v
c = rng.permutation(c) * rng.choice([-1.0, 1.0], size=k)
return unit(c @ P[:k])
```

It permutes the coordinates of the top $k$ principal components across components and then **applies unit normalization.** The eigenvalue weights are ignored.

## CB2. Magnitude of the Damage (Llama-3.2-1B-Instruct, layer 12, eigenvalue ratio $\lambda_{\max}/\lambda_{\min} = 2.96\times10^{6}$)

The ratio of the floor's activation variance to the target's activation variance (40 directions each; combined distribution across all directions within the family).

| Family | Floor | Ratio median | Ratio 5% | Ratio 95% | $\max|$ratio$-1|$ |
|---|---|---|---|---|---|
| Emotion category | F4 | **6.899** | 3.696 | 35.218 | 90.3 |
| Raw appraisal dimension | F4 | **2.083** | 0.556 | 12.597 | 26.1 |
| Principal component | F4 | **1.834** | 1.000 | 12.117 | 20.9 |

**The F4 floor is systematically stronger than the target, and moreover the degree of excess differs per family** (6.90 vs. 2.08 vs. 1.83). **Inter-family comparison is contaminated by this mismatch.**

### Correction of the Direction of Bias

When this issue was first audited, the emotion directions were measured as **class centroids** (class mean − overall mean), giving a ratio of 0.35–0.84 (floor **weaker** than the target). However **the emotion directions actually used in stage C are ridge regression directions.** Ridge directions spread their coordinates across all principal components, so the 90% coverage dimension $k$ saturates at the upper limit of 64, and unit normalization after permutation concentrates all the norm in the top-64 principal components (high eigenvalue side). As a result **the ratio exceeds 1.** **The direction of bias depends on how the directions are constructed. The initial 0.35–0.84 does not represent the stage C setting.** In all construction methods, the lack of matching is a common issue.

### The Previously Reported $5.6\times10^{-16}$ Was a Different Quantity

What was reported as "maximum difference in variance profile $5.6\times10^{-16}$" in draft v3 and the amendments was the difference in the multiset $\{a_i^2\}$, **not the difference in variance contributions weighted by eigenvalues.** **The description "the variance profile is exactly matched" is incorrect.**

## CB3. Corrected Floors (Defined in this amendment. Fixed before seeing results)

### F5 (sign flips only, exact eigenvalue matching) — primary floor

For **all components** of the eigen-basis, draw $\tilde a_i = s_i a_i$ with $s_i \in \{-1,+1\}$ independently. Since the principal component positions are not moved, $\lambda_i \tilde a_i^2 = \lambda_i a_i^2$ holds for all $i$, and both $v^\top\Sigma v$ and $\|v\|$ are exactly preserved. **Unit normalization is not applied.** The residual component not spanned by the eigen-basis has its sign flipped while preserving the norm.

**Measured:** Ratio median 1.0000, $\max|$ratio$-1| = 2.9\times10^{-15}$. The absolute cosine of F5 floor directions with targets: emotion median 0.045 (95th percentile 0.127), raw appraisal 0.060 (0.202). **Exactly matched, and nearly orthogonal as directions.**

### F6 (within-near-degenerate-block permutation + sign flip) — auxiliary

Principal components with eigenvalue ratio within $1+\tau$ ($\tau = 0.05$) are grouped into the same block (235 blocks, maximum length 17), permuted within the block, and then sign-flipped. **Measured:** $\max|$ratio$-1| = 7.5\times10^{-3}$, cosine median 0.034.

### F7 (eigenvalue-stratified permutation) — lenient floor for the principal component family

Eigenvalue ranks are divided into $n_b$ equal-count bins, and permutation within bins is performed followed by sign flips. $n_b = 2048$ coincides with F5. **Measured** ($n_b=256$): ratio for emotion — median 1.060 (5–95%: 0.864–1.562).

## CB4. Structural Fact: No Matched Floor Exists for Principal Component Directions

For principal component $u_i$, $a = e_i$, so any direction that preserves $\lambda_j a_j^2$ for all $j$ is restricted to $\pm u_i$. **The F5 floor is the target itself for the principal component family** (measured: $|\cos|$ is 1.0000 for both F5 and F6 against the principal component family).

Therefore:

> **The question "is the principal component basis privileged?" is undefined at the level of exact variance matching. The principal component family is its own matched null.**

**This is not a defect; it is a consequence of the requirement of variance matching. It is reported as a finding in the paper.**

### Consequence: Exact comparison is limited to emotion categories vs. appraisal dimensions

| Family | Testable with F5 (exact)? |
|---|---|
| Emotion category | **Testable** ($|\cos|$ median 0.045) |
| Raw appraisal dimension | **Testable** (0.060) |
| Residualized appraisal dimension | Testable (measurement needed) |
| Principal component | **Not testable** ($|\cos| = 1.0$). Reported as auxiliary using F7/256 lenient floor |

**The primary claim is limited to the contrast between the emotion category axis and the appraisal dimension axis.** Principal components are auxiliary; the reason they cannot be tested at the exact level is written in the main text. This is also the direct contrast for the principal investigator's hypothesis (emotion is a projection of a latent concept).

## CB5. Partition Leakage (Implementation defect, 9th instance)

The stage C implementation draws two independent permutations from the random number generator.

```python
perm = rng.permutation(n); tr, va = perm[1320:1320+3000], perm[:1056]
...
idx = rng.permutation(n); p_sel = ...idx[:32]...; p_held = ...idx[32:64]...
```

These are separate permutations of the same set of $n = 6600$ rows, so overlap occurs. **Measured values:**

| Overlap | Measured |
|---|---|
| sel ∩ tr | **17/32** |
| held ∩ tr | **14/32** |
| sel ∩ va | 5/32 |
| held ∩ va | 7/32 |
| sel ∩ held | 0/32 |

**44% of the held contexts used for scoring were rows used to estimate the directions.** Since emotion category directions are constructed from class labels, **the labels of the held contexts themselves contribute to the direction construction.** This is a circularity that is uniquely advantageous to the emotion family and **is a direct threat to the primary result.**

### Fix: Complete 3-Way Partition

Rows are permuted once and divided into 3 non-overlapping sets.

| Set | Use |
|---|---|
| $D_{\mathrm{train}}$ | Construction of emotion category directions, appraisal dimension probes, principal component bases, eigenvalues, and floor |
| $D_{\mathrm{sel}}$ | Selection of the best direction within the family (same for the floor) |
| $D_{\mathrm{test}}$ | Final scoring |

**Labels and activations of $D_{\mathrm{test}}$ are never used in direction construction.** Mutual exclusivity of the 3 sets is verified at runtime; a violation causes an exception.

## CB6. Matching the Floor to Each Target

The current implementation generates 60 floor directions from **only the first direction of the emotion family, `A_raw[0]`**, and uses the same floor for all families and all targets. This ignores the differences in variance profile across families and directions.

**Fix**: For family $\mathcal{B} = \{v_1,\dots,v_K\}$, a floor is generated **for each $v_i$** separately. One draw of a floor family is $\{\tilde v_1,\dots,\tilde v_K\}$ (where $\tilde v_i$ is matched to $v_i$), and the maximum across this family is taken. The comparison becomes strictly **family vs. matched family.**

## CB7. Global Null Preserving Dependencies Among the 13 Targets

The count "x of 13 targets exceeded the 95th percentile of the floor" cannot be interpreted as a probability because the 13 targets are not independent.

**Added statistic:** Generate the floor family 2000 times; for each draw compute
$T_{\mathrm{null}} = \#\{e : S_e > q_{0.95,e}\}$ to obtain the null distribution of $T$. Report $P(T_{\mathrm{null}} \ge T_{\mathrm{obs}})$ for the observed $T_{\mathrm{obs}}$. The correlations among the 13 targets are preserved as-is.

**Aggregation across models**: Rather than treating 8 models as independent replications, **bootstrap with clusters defined by 5 families (Llama, OLMo, Gemma, Mistral, Phi).** Llama 1B/8B and OLMo 7B/13B are not independent follow-up studies.

## CB8. Correction of Terminology (Critique 2)

13 category directions from centroid construction satisfy $\sum_e p_e(\mu_e - \mu) = 0$, making them **linearly dependent** with rank at most 12. Even in ridge construction, the rank of the space spanned by 13 directions may be 12 or less. In either case, **the word "basis" is inaccurate.**

- "Basis privilege" → **"Axis privilege"**
- Title's *Privileged Emotion-Category Bases* → ***Privileged Emotion-Category Axes***
- **The fact that the 13 directions are linearly dependent with rank at most 12** is stated explicitly in the main text

**Level numbers and contents are not changed.** Only the terminology is corrected to be mathematically accurate.

## CB9. Logical Error in Section 5.1 (Critique 3)

Section 5.1 of draft v3 states: "The candidates for the latent concept should move the readout at least as strongly. The observation is the opposite, and the direction of projection is opposite to the hypothesis."

**This does not hold.** Given $v_{\text{joy}} = \sum_i a_i z_i$,

$$\max_i S(z_i) < S\Big(\sum_i a_i z_i\Big)$$

can occur normally. Even if individual $z_i$ are weak, their linear combination being strong is not a contradiction. And judging that is precisely level 2, which **has not been executed.**

**Fix**: Delete the relevant paragraph and replace it with the following:

> The present result does not negate the structure that "emotion categories are projections of appraisal axes." What is shown is that **individual human-named appraisal axes do not exhibit axis privilege, while emotion category axes do.** Whether the subspace spanned by appraisal axes is privileged is a level-2 question that is not verified in this paper.

## CB10. Independent Readout (Critique 4) — Elevated to Precondition for Level-3 Claims

The strongest alternative explanation is circularity. The emotion category directions are constructed from emotion category labels, and evaluation is also conducted using the readout of emotion category words. **The same ontology is used on both sides.** The synonym-set readout (R-syn) from amendment 82 does not answer this. It is vocabulary from the same 13 categories.

**Added readout R-ind**: Free generation is obtained after intervention, and the full output is evaluated by an **independent rater that does not directly use the 13 category names.** The implementation is **fixed before seeing results in amendment 84.**

**If the emotion axis does not exceed the floor under R-ind, level-3 claims are not made.**

## CB11. Execution Order

```
① Verification of corrected floors F5, F6, F7                    ← This amendment CB3, CB4 (already executed)
② Implementation of complete 3-way partition and runtime check    ← CB5
③ Implementation of per-target matched floor families              ← CB6
④ Global null T and family-cluster bootstrap                      ← CB7
⑤ Remeasurement of all 9 models (readouts as per amendment 82's 2 types)
⑥ Fix specifications of independent readout R-ind in amendment 84 and execute
```

**The paper is not submitted to external review until ⑤ and ⑥ are complete.**

## CB12. Commitments

- Remeasurement results are reported as-is regardless of whether they are consistent with amendments 80 and 81
- **If the floor construction changes the conclusion, the fact that it changed is reported as a primary result**
- Old F4 results are not deleted; they are reported alongside as a floor that does not achieve variance matching
- Mutual exclusivity of the 3-way partition is verified at runtime; a violation causes an exception
- The reason the principal component family cannot be tested at the exact level is written in the main text; claims are limited to emotion vs. appraisal
- Terminology is unified to "axis privilege"; the linear dependence of the 13 directions is written in the main text
- The relevant paragraph in section 5.1 is deleted. Claims that cannot be made without level 2 are not made
- The independent readout is elevated to a precondition for level-3 claims
- This is recorded in Appendix B as implementation defect 8th instance (floor variance matching) and 9th instance (partition leakage)
- **The correction of the direction of bias (CB2) is preserved in the record. The initial numbers measured with class centroids do not represent the stage C setting**
