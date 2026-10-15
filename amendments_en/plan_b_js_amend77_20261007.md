# Pre-registration Amendment 77: Judgement Procedures for L2 and L3 — Optimal In-Subspace Combination and Random Rotation

**Created**: 2026-10-07
**Occasion**: External advice (2026-10-07, 2nd round)
**Role**: Specific procedures and judgement criteria for L2 and L3 of the three-level framework introduced in amendment 76.
**Activation condition**: L2 and L3 judgements must not be performed until this file has been committed and pushed. **Neither has been executed even once.**

---

## BZ1. Target Subspaces

| Symbol | Subspace | Dimension | Directions that span it |
|---|---|---|---|
| $U_E$ | Emotion category subspace | 13 | Ridge regression directions onto 13 emotion category indicator variables |
| $U_A$ | Appraisal dimension subspace | 21 | Ridge regression directions onto 21 appraisal dimensions of crowd-enVENT (**raw directions**) |
| $U_P$ | Principal component subspace | 21 | Top-21 principal components of the activations from the training rows |
| $U_R$ | **Variance-matched random subspace** | 13 or 21 | The space spanned by replacing each direction of the corresponding human subspace with F4 |

**$U_A$ is spanned by raw directions.** Single-effect-isolated directions are handled separately as a distinct family under L3.

## BZ2. L2 — Subspace Privilege

### Estimator

Let $u_1,\dots,u_K$ be an orthonormal basis of subspace $U$. For target $e$, measure the effect $S_e(u_i)$ of each basis direction using **only selection contexts**, and define

$$v^{\text{opt}}_{U,e} = \mathrm{normalise}\Big(\textstyle\sum_{i=1}^{K} S_e(u_i)\, u_i\Big)$$

as the **optimal in-subspace combination.** Under the first-order approximation $S_e(\sum c_i u_i) \approx \sum c_i S_e(u_i)$, this is the coefficient that maximizes the effect subject to $\sum c_i^2 = 1$.

**$v^{\text{opt}}$ is measured directly on held-out contexts.** The coefficients are obtained by the approximation, but **the effect is measured directly, not approximated.**

### Validity check for the first-order approximation (performed before the judgement)

At the minimum budget $J^\* = 0.02$, for 20 randomly chosen coefficient vectors $c$, the correlation between the measured value of $S_e(\sum c_i u_i)$ and the predicted value $\sum c_i S_e(u_i)$ is measured.

**If the correlation falls below 0.8, the first-order approximation is not used; instead, the coefficients are directly searched** (coordinate descent on selection contexts, 20 iterations). **Which was used is reported.**

### Judgement L2

**Judgement L2**: The number of targets for which the standardized excess $E$ of $v^{\text{opt}}_{U_A,e}$ exceeds the 95th percentile of the distribution of standardized excesses for $v^{\text{opt}}_{U_R,e}$ constitutes a majority. $U_R$ is drawn 30 times.

**The same judgement is applied to $U_E$.**

**Interpretation of results (fixed in advance)**

| L2 for $U_A$ | What can be written |
|---|---|
| Exceeds | **The appraisal subspace is causally effective.** It is meaningful to ask about basis privilege in L3 |
| Does not exceed | The appraisal subspace itself cannot be distinguished from a variance-matched random subspace. **In this case, the L3 result is read as "neither the basis nor the subspace is privileged"** |

## BZ3. L3 — Basis Privilege

### Estimator

From the unit sphere of subspace $U$, **105 directions are drawn at random**, and the effect of each is measured on held-out contexts. From these, $K$ directions are resampled with replacement ($K=13$ for $U_E$, $K=21$ for $U_A$) and the maximum is taken; this operation is repeated 2000 times, constructing **the distribution of "best of a random basis."**

**This construction reduces the number of measurements to 1/4 compared to directly measuring 20 sets of bases.** The distribution of the maximum is approximated by resampling with replacement. **The fact that it is an approximation is stated explicitly.**

### Judgement L3

**Judgement L3**: The number of targets for which the effect of the best direction in the human basis exceeds the 95th percentile of the distribution of the best of a random basis constitutes a majority.

**The judgement is made for both $U_E$ and $U_A$.**

**Interpretation of results (fixed in advance)**

| | $U_E$ | $U_A$ | What can be written |
|---|---|---|---|
| (i) | Exceeds | Exceeds | Both the human emotion basis and the appraisal basis are privileged coordinates |
| (ii) | **Exceeds** | **Does not exceed** | **Human emotion categories are privileged coordinates, but the human appraisal coordinate system is not** |
| (iii) | Does not exceed | Does not exceed | Neither human basis is privileged. Only the subspace is what matters |
| (iv) | Does not exceed | Exceeds | Unexpected. Reported as-is |

**What can be written under (ii)**

> **Computation corresponding to appraisal exists, but is not implemented in the human appraisal coordinate system.** On the other hand, human emotion categories are privileged coordinates.

**What can be written under (iii)**

> Neither the human emotion nor human appraisal bases are privileged. **What is privileged is the subspace; which axes within it are taken is arbitrary.**

**All cases are reported.** (ii) is the most interesting, but the criteria are not moved in order to obtain it.

## BZ4. Replication of the Prior Procedure (Performed Before L2 and L3)

The procedure of Tak et al. is applied as-is. That is, for raw appraisal dimension directions, single-effect isolation $z_a = (I - P_{-a}) v_a$ is performed, and intervention is applied by **multiplying a common coefficient by the unit-norm directions**, and compared against **the whole-space floor (F1).**

**Judgement REP**: Under this design, the number of targets for which appraisal dimension directions exceed the F1 floor constitutes a majority.

**If satisfied**: The phenomenon from prior work is recorded as replicated, and then the floor is replaced with F4. **The interpretation that "the effect disappeared due to implementation changes" can be excluded.**

**If not satisfied**: The failure to replicate is recorded, and **no claim about the strength of the floor is made.** Until the difference in procedure is identified, the results from L2 and L3 are not used in comparison with prior work.

## BZ5. Readout

Following amendment 76 BY4, two types are used.

| Symbol | Readout |
|---|---|
| R-single | Next-token probability of 13 emotion words (as before) |
| **R-syn** | **Sum of probabilities for the synonym set of each emotion** |

The synonym sets are **fixed in this amendment.**

```
anger: anger, angry, furious, enraged
boredom: boredom, bored, dull, tedious
disgust: disgust, disgusted, revolted, repulsed
fear: fear, afraid, frightened, scared
guilt: guilt, guilty, remorseful, contrite
joy: joy, happy, delighted, cheerful
no-emotion: neutral, indifferent, unmoved, unaffected
pride: pride, proud, accomplished, gratified
relief: relief, relieved, reassured, unburdened
sadness: sadness, sad, sorrowful, downcast
shame: shame, ashamed, humiliated, mortified
surprise: surprise, surprised, astonished, startled
trust: trust, trusting, confident, assured
```

**Judgements are made using both readouts; if the conclusions do not agree, neither conclusion is claimed.**

## BZ6. Reporting Statistics (Following Amendment 76 BY8)

The primary statistics are, per direction:

1. **Percentile rank in the null distribution** $q(v) = \hat F_{\text{null}}(S(v))$
2. **Standardized excess** $E(v) = (S(v) - \mu_{\text{null}})/\sigma_{\text{null}})$

**Bootstrap 95% confidence intervals are reported alongside.** The difference in floor exceedance counts is reported as auxiliary.

**Models are the unit of replication.** Consistency across budgets is shown as within-model auxiliary information.

## BZ7. Execution Order and Cohorts

```
① Correlation check by JSD vocabulary range (amendment 76 BY5)
② Validity check for the first-order approximation (BZ2)
③ Judgement REP (replication of prior work, BZ4)
④ L2 (subspace privilege)
⑤ L3 (basis privilege)
⑥ Paired comparison of emotion axis and principal component axis (amendment 76 BY7)
```

Steps ①–⑥ are executed on the **discovery and statistic-development cohort** (OLMo-2-7B / Gemma-2-9B / Llama-3.1-8B / Llama-3.2-1B), and steps ③–⑥ are re-executed on the **confirmation cohort** (OLMo-2-13B / Gemma-2-2B / Phi-3-medium / Ministral-8B / Mistral-Nemo-12B).

**The confirmation cohort results are not examined before this amendment is pushed.**

## BZ8. Commitments

- The validity of the first-order approximation is verified before the judgement; if not satisfied, direct search is used. **Which was used is written**
- The fact that the distribution of the best of a random basis is an approximation by resampling is stated explicitly
- All four cases of BZ3 are reported. The criteria are not moved
- If judgement REP is not satisfied, no claim about the strength of the floor is made
- If the conclusions from the two readouts do not agree, **neither conclusion is claimed**
- The confirmation cohort results are not examined before pushing
- Raw appraisal directions and single-effect-isolated directions are both reported
