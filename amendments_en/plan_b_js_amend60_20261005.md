# Pre-Registration Amendment 60: Asking "As a Family" Rather Than Dimension by Dimension —
# Registration of an Aggregate Test and a Discovery/Confirmation Partition

**Created**: 2026-10-05
**Target**: Judgement V1′ in Amendment 58
**Status**: The criteria for V1′ are **not changed**. **An additional estimator is registered.**
**Activation condition**: The aggregate test must not be computed until this file has been committed and pushed.

---

## BI1. The Power Problem Cannot Be Solved by Increasing the Floor Trials

In the 40-trial results (Amendment 59 BH1), the floor SD was 0.077–0.262, which was on the same order as the observed effect of +0.07 to +0.25. Increasing the floor to 200 trials tightens the **estimates of the mean and SD**, but does not shrink the **p95 itself with sample size.** The tail of the distribution is the direction-specific variability itself, not estimation error.

Therefore, the question of "does each evaluation dimension exceed the 95th percentile of its own floor?" is **in principle difficult to pass** given this ratio of effect size to floor spread.

## BI2. Changing the Estimator Without Changing the Question

What this study asks is the following.

> Does an intervention on the appraisal dimension direction move the emotion output **in the direction predicted by human ratings**?

Rather than asking this **dimension by dimension**, this is asked **as a family**. Rather than whether each of the 17 dimensions individually exceeds its floor, the question is whether **the mean signed effect across all 17 dimensions exceeds the mean of the floor**.

Since random directions are unrelated to the contrast vector, the floor's $S$ is distributed around 0 (confirmed to be −0.003 to −0.001 across 3 models in Amendment 59 BH1). Therefore, **if the mean $S$ of the evaluation dimensions is significantly greater than 0, it means the family as a whole is moving in the predicted direction.**

**Estimator $\bar S$**: For adopted evaluation dimensions $a$, $\bar S = \frac{1}{|A|}\sum_a S_a$.

**Null**: In each floor trial, draw the same number of directions and take their mean $S$ (bundling floor trials in groups of $|A|$, 2000 bootstrap samples).

**Judgement V1″**: $\bar S$ exceeds the 95th percentile of the null distribution.

**Soundness**: The mean of the null distribution is within 2 standard errors of 0 (same gate as Amendment 58 BG5). **The positive control condition is maintained**: if the positive control does not exceed the floor for a given model, V1″ is also not judged for that model.

## BI3. Partitioning Discovery and Confirmation

**At the time of this amendment, the dimension-level $S$ values for 4 models are already in hand.** Therefore, applying the aggregate test to these is **exploratory**.

| Category | Models | Treatment |
|---|---|---|
| **Discovery set** | Llama-3.2-1B / OLMo-2-7B / Gemma-2-9B / Mistral-Nemo-12B | **Exploratory**. $\bar S$ is reported but not treated as confirmatory evidence |
| **Confirmation set** | OLMo-2-13B / Gemma-2-2B / Llama-3.1-8B / Phi-3-medium / Phi-3.5-mini / Ministral-8B | **Confirmatory**. Signed readout not yet run. Will be run after this amendment is pushed |

**For the 6 models in the confirmation set, the criteria for V1″ are fixed before seeing the results.**
If the direction seen in the discovery set replicates in the confirmation set, it constitutes confirmatory evidence.

**Pass condition**: V1″ holds for the majority of the 6 confirmation set models **that have the positive control exceeding the floor**. If 2 or fewer models have the positive control exceeding the floor, **this is recorded as unverifiable.**

## BI4. What This Design Can and Cannot Claim

**What can be written if it passes**:

> An intervention on appraisal dimension directions moves the emotion output **as a family** in the direction predicted by human ratings. This holds under a variance-matched in-plane random direction floor. However, **individual evaluation dimensions cannot be separated from the floor** (effect size is on the same order as the floor spread).

**What cannot be written**: Dimension-level claims such as "the `pleasantness` direction controls emotion." Dimension-level judgements did not pass. **This limitation is explicitly stated.**

**What can be written if it fails**: "Under a variance-matched floor, the effect in the predicted direction cannot be detected even for the family as a whole." This is reported as a measurement limitation.

## BI5. Commitments

- The results of V1′ (dimension by dimension) are not overwritten by the aggregate test. **Both are reported**
- The $\bar S$ of the discovery set is **explicitly labeled exploratory**. It is not treated as confirmatory evidence
- The 6 confirmation set models are **run after this amendment is pushed**
- The positive control prerequisite is maintained. Models where it does not hold are not judged
- No dimension-level claims are made
- **No further estimators are added.** The aggregate test is the final arbiter
