# Pre-Registration Amendment 57: Results of Stage B0, a Defect in the Registered Gate Formula,
# and the Confound That "Prediction Agreement" Does Not Indicate Shared Representations

**Created**: 2026-10-05
**Target**: The null validity gate in Amendment 45 AT2.5, Stage B0 in Amendment 53 BB7
**Judgement**: **Stage B0 is unmeasurable under the registered formula. This is a formula defect; the null is sound.**
**Additionally, the estimator in Stage B0 is confounded and does not constitute evidence of shared representations.**
**Activation condition**: The revised Stage B0′ must not be judged until this file has been committed and pushed.

---

## BF1. Observed Values for Stage B0 (10 models, 45 pairs, 1320 evaluation rows)

Probe predictions were generated at the deepest layer of each model, and correlations were averaged across model pairs for each of the 21 evaluation dimensions.

| | Value |
|---|---|
| Minimum agreement (minimum across 45 pairs) | **+0.8838** |
| Maximum agreement | +0.9481 (Ministral-8B vs Mistral-Nemo-12B) |
| Null (row permutation, 500 trials) | Mean **−0.0001**, SD **0.0131**, p95 **+0.0215** |

The observed minimum is approximately **67 SD** from the null mean.

## BF2. The Registered Gate Formula Produced an Incorrect Judgement

Amendment 45 AT2.5 registered the following.

> The null standard deviation is non-zero, and **the standard deviation is at least 1/10 of the difference between the observed and null values**.

Applying this formula, the SD 0.0131 is less than 1/10 (0.0884) of the difference 0.8839, so the formula returns **"unmeasurable."**

**This is a formula defect.** The intent of the gate, as stated in Amendment 44 AS2, was to detect the condition that **"a null with no variance leaves a test uncalibrated."** In this case, the null is distributed normally with a mean of approximately 0 and SD 0.0131, and is **not degenerate.** The formula had been misread such that an extremely large effect would be interpreted as an unsound null.

**This is recorded as-is.** The output of the registered formula is "unmeasurable."

**Revised gate (defined in this amendment, applied hereafter)**:

> The null is judged to be **non-degenerate** by the following: (i) SD > 0, (ii) interquartile range of the null > 0, (iii) at least 10 distinct values in the null. **The ratio against the difference from the observed value is not used.** The effect size is also reported in **null SD units**.

The revised gate still captures the case where degeneracy was missed in P1 (Amendment 44: null mean and 5th percentile were completely identical across all layers, SD ≈ 0). **Past judgements are not retroactively rewritten.**

## BF3. A More Serious Problem — Prediction Agreement Does Not Indicate Shared Representations

Stage B0 measures the correlation of **probe predictions** from each model. However, the probes of every model were **trained against the same ground truth $Y$ (crowd-enVENT ratings).**

Therefore, the correlation between the predictions of two models can be **explained entirely by both approximating $Y$ well.** This does not constitute evidence of shared internal representations.

The null using row permutation does not eliminate this confound. **This is a design defect in Stage B0.**

**Revised estimator (Stage B0′)**: Remove $Y$ by partial regression. For evaluation rows, from the prediction $\hat r^{(m)}_a$ of model $m$ at evaluation dimension $a$, take the **residual after removing the component explained by the true rating $Y_a$**:

$$\tilde r^{(m)}_a = \hat r^{(m)}_a - \beta_a^{(m)} Y_a - c_a^{(m)}$$

**Judgement B0′**: The residual agreement exceeds the 95th percentile of the null (row permutation, 500 trials). The revised gate is applied.

**If the residual agreement is at chance level, one cannot write that "there are shared representations of appraisal across models."** What can be said in that case is only that "every model predicts the same human ratings well."

## BF4. The Decision of Whether to Perform X3 (Cross-Model Transfer)

Stage B0 is a kill switch whose purpose was to determine **"whether it is worth investing GPU resources in transfer."**

- Agreement exceeds +0.88 across all 45 pairs, and **probes are capturing the same signal**
- Therefore, the prerequisite for attempting transfer is judged to be satisfied, and X3 is performed
- However, **Stage B0 is not cited as evidence that there are shared representations across models.** The claim of shared representations will follow the results of Stage B0′

**The judgement of X3 itself remains unchanged from Amendment 53 BB4.** X3 is judged by whether the transfer direction exceeds the floors of T2, T3, and T4, and does not depend on the values of Stage B0.

## BF5. Comparison with Amendment 50 (An Important Asymmetry)

| Level | Stimulus | Agreement | Null | Result |
|---|---|---|---|---|
| Emotion family (relative representation) | E5 (topic fixed) | +0.8502 | +0.8619±0.0276 | **Does not exceed chance** (Amendment 50) |
| Evaluation dimension (probe predictions) | crowd-enVENT | +0.8838 | −0.0001±0.0131 | Greatly exceeds (this amendment, but with confound from BF3) |

**These two must not be directly compared, because the levels of the null are entirely different.** The null in Amendment 50 reaches +0.86 through within-skeleton permutation, while the null here is 0 under row permutation. **When the nulls differ, the numbers are not comparable.**

**Once the results of Stage B0′ are available, the comparison will be rewritten using nulls of the same nature.** Until then, one must not write "agreement holds for appraisal but not for emotion families."

## BF6. Commitments

- The output of the registered formula (unmeasurable) is reported as-is and is not overwritten with the revised version
- The revised gate is applied **only to judgements after this amendment**
- Stage B0 is not cited as evidence of shared representations
- If Stage B0′ is at chance level, one must not write that "there are shared representations of appraisal across models"
- The comparison in BF5 is not performed until the nulls are made comparable
