# Pre-Registration Amendment 58: V3 (Positive Control) Failed. V1 is Unmeasurable.
# Identifying the Non-Specificity of the Readout and Registering a Signed Readout

**Created**: 2026-10-05
**Target**: Judgements V1, V2, V3 in Amendment 49, Prediction W1 in Amendment 52
**Judgement**: **V3 did not hold. Therefore, the failure of V1 is not claimed (unmeasurable).**
**Activation condition**: The signed-readout judgement must not be performed until this file has been committed and pushed.

---

## BG1. Observed Values (First Model, Deepest Layer of OLMo-2-7B Series)

Changes in the emotion readout after equalizing the output perturbation budget (JS divergence over the union of the top-100 vocabulary items).

| Budget $J^\*$ | F1 Full space | F2 Axis-orthogonal | **F3 In-plane** | **F4 VMIC** | Evaluation dims exceeding F4 | Positive control | PCs exceeding F3 |
|---|---|---|---|---|---|---|---|
| 0.02 | — | — | — | — | **1/17** | **0.01713 ≤ F4** | 1/5 |
| 0.05 | p95 0.0877 | p95 0.0923 | **p95 0.1902** | **p95 0.1806** | **2/17** | **0.07525 ≤ F4** | 1/5 |
| 0.10 | p95 0.1639 | p95 0.1790 | **p95 0.4057** | **p95 0.3389** | **1/17** | **0.14022 ≤ F4** | 0/5 |

## BG2. What the Hierarchy of Floors Showed (This Is Reported as a Result)

**The floors of F3 and F4 are approximately twice those of F1 and F2.** At $J^\*=0.05$, F1 p95 is 0.0877, whereas F3 is 0.1902 and F4 is 0.1806. At $J^\*=0.10$, F1 is 0.1639 vs. F3 is 0.4057.

> **Even after equalizing the output perturbation budget, a random direction drawn from within the dominant-variance subspace moves the emotion readout approximately twice as much as a random direction drawn from the full space.**

This is a confirmation, in a different measurement system, of the confound reported in Paper 2. **A design that uses only the full-space floor and claims "the direction is special" misses this factor of two.**

## BG3. However, V1 Cannot Be Judged Because V3 Failed

Amendment 49 AX6 registered the following.

> **Judgement V3 (positive control, prerequisite)**: The Warriner valence direction moves E1 and E2 under F4. **If it does not move them, this constitutes insufficient measurement resolution, and failure of V1 is not claimed.**

**The positive control did not exceed F4 in any of the three budgets.** Therefore:

- **V1 is unmeasurable.** One must **not write** "appraisal dimension steering does not exceed the variance-matched floor"
- **W1 is also unmeasurable.** The observation that the principal components (unsupervised) did not exceed F3 (1/5, 1/5, 0/5) was made, but since **the supervised direction also did not exceed it**, the condition (a) of Prediction W1 in Amendment 52 BA4 does not hold

**Prediction W1 in Amendment 52 BA4 was not supported.** However, this is unmeasurable, not unsupported.

## BG4. Diagnosis of the Cause — The Readout Is Non-Specific

The emotion readout was defined as the **JS divergence of the next-token probability distribution over 13 emotion words**. This is an indicator of **magnitude** and does not observe **direction**.

Even after equalizing the output perturbation budget at $J^\*$, perturbation along a dominant-variance direction moves the probabilities of the 13 words **in either direction**. Therefore, even a random direction yields large values, resulting in high floors. **The reason the positive control does not reach the floor is that the floor cannot measure "moving an emotion."**

**This is a recurrence of what was learned in Paper 2.** In Amendment 37, the sign-blind problem was pointed out and a signed readout measuring the antisymmetric component was introduced. **In this audit, the system had reverted to a magnitude indicator.**

## BG5. Registration of a Signed Readout (Defined Before Seeing the Results)

**Predictions are constructed from human ratings only.** No model is used.

Using crowd-enVENT ratings, for evaluation dimension $a$, define the **human-side contrast vector** over the 13 emotion categories as

$$ c_a[e] = \mathrm{corr}\big(Y_a,\ \mathbb{1}[\text{emotion} = e]\big),\qquad \lVert c_a \rVert = 1 $$

(measuring from human data which emotion tends to appear when the appraisal rating is high).

For the probability change across 13 words $\Delta p \in \mathbb{R}^{13}$ (centered to sum to 0) induced by an intervention, define the **signed effect** as

$$ S_a = \frac{\langle \Delta p,\ c_a \rangle}{\lVert \Delta p \rVert} $$

$S_a \in [-1, 1]$, and **it becomes positive only when the movement is in the direction predicted by theory.** Magnitude alone does not make it positive.

**Judgement V1′**: $S_a$ for an intervention on evaluation dimension $a$ exceeds the 95th percentile of the $S_a$ distribution under the F4 floor. **Since random directions are unrelated to $c_a$, the floor's $S_a$ should be distributed around 0.** This is used as a null validity check (if the mean of the floor's $S_a$ deviates significantly from 0, $c_a$ itself is confounded, and no judgement is made).

**Judgement V3′ (prerequisite)**: For the Warriner valence direction, $c_{\text{valence}}$ is constructed similarly from the correlation between Warriner valence and the 13 emotions, and $S$ exceeds the F4 floor. **If it does not exceed it, the result remains unmeasurable.**

**Antisymmetrization**: Following Amendment 37, $S$ takes the form $\tfrac12[S(+\alpha v) - S(-\alpha v)]$.

## BG6. The Magnitude-Based Results Are Not Discarded

The values in BG1 **are reported as-is.** They are not discarded in favor of reporting only the signed version.

**Proposition to report**:

> Under the design of measuring the **magnitude** of the emotion readout after equalizing the output perturbation budget, appraisal dimension directions cannot be distinguished from the variance-matched floor (1–2 out of 17 dimensions). Since the positive control also does not reach the floor, **this design cannot measure a specific effect on emotion.** **Direction rather than magnitude must be measured.**

This is a methodological finding and constitutes **a critique of the readout design in steering research.**

## BG7. Commitments

- The failure of V3 is recorded, and **the failure of V1 is not claimed**
- W1 is recorded as unmeasurable, and is written as **neither supported nor unsupported**
- The magnitude-indicator values in BG1 are **reported as-is**. They are not overwritten with the signed version
- $c_a$ is constructed **from human ratings only**. It is not constructed from model output
- The fact that floor $S_a$ is centered around 0 is confirmed before making any judgement
- If V3′ fails, **the result remains unmeasurable.** A third redesign is not performed; the limitation is written in the paper
