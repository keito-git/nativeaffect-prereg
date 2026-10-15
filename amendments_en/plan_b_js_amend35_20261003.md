# Pre-registration Amendment 35: Test whether the residual after removing weight geometry has content-dependent structure

**Created**: 2026-10-03
**Position**: Pre-registration of a new question. The judgement in Amendment 34 (H3 withdrawn) is not changed.
The controls S/W from Amendment 35 are absorbed into this series.
**Launch condition**: The job must not be launched until this file has been committed to git and pushed to remote.

---

## AJ0. Why a new question

Amendment 34's Control R showed that the top 10-dimensional subspace of the layer Jacobian is **nearly the same regardless of what input is given.** Control R from random token sequences agreed with the emotion-derived subspace at 33–141× the null.

This did not negate the principal investigator's hypothesis; it showed that **the measurement instrument was not measuring the hypothesis's target.** The top Jacobian subspace is "where the layer is sensitive" and not "what the model represents."

So the measurement target is changed. **The residual after projecting out Control R's subspace $S_R$** is, by definition, the component that depends on input content. The question is whether this residual has structure.

## AJ1. Exploratory preliminary observation (unregistered; motivation for this amendment)

Let $Q_e, Q_m, Q_r$ be orthonormal bases for the emotion-derived, math-derived, and Control-R-derived sensitivity subspaces respectively, and define the residual by the left singular vectors of $P_x = Q_x - Q_r Q_r^{\top} Q_x$.

| Layer | Energy remaining outside $S_R$ | Residual agreement (emo × math) | Null ratio |
|---|---|---|---|
| 11 | 0.839 | 0.1384 | 56.7× |
| 16 | 0.918 | 0.1020 | 41.8× |
| 22 | 0.835 | 0.0838 | 34.3× |
| 27 | 0.656 | 0.1418 | 58.1× |

**66–92% of the sensitivity subspace remains outside weight geometry, and the residuals agree at 34–58× the null.**

**This must not be treated as evidence of concepts.** Correlated estimation errors alone would produce the same numbers.
The following 2 controls distinguish them.

## AJ2. Control S (split-half reliability)

**Procedure**: randomly split the 144 E1 discovery-half stimuli into 2 halves A/B using category-stratified random splitting (seed 20261003; save the split file first to fix it). Derive 10 sensitivity directions from each of A and B using the same procedure, and measure the agreement $O_{AB}$ of the residuals after removing $S_R$.

**Role**: $O_{AB}$ is the upper bound on "how well independently estimated residuals agree when the content is the same." Used as the reliability baseline.

## AJ3. Control W (a third domain of natural text)

**Procedure**: natural text that is neither emotional nor mathematical (sentences extracted from English Wikipedia body text, length distribution matched to E1, 144 items, seed 20261003). Derive sensitivity directions using the same procedure and take the residual.

**Role**: distinguish whether the "emo × math" agreement comes from structure shared across natural text in general, or structure specific to the content.

## AJ4. Judgement criteria fixed in advance

Measure $O_{AB}$ (split-half), $O_{em}$ (emo × math), and $O_{ew}$ (emo × Wikipedia) all on the residual, and compare by the null-normalized ratio. **Judgement requires 3 or more of 4 layers to be satisfied.**

- **S1**: $O_{AB}$ is **clearly larger** than both $O_{em}$ and $O_{ew}$
  (1.5× or more in ratio). If not satisfied, the shared residual component is not specific to content, and **this series terminates**
- **S2**: $O_{em}$ and $O_{ew}$ are **comparable** (within 1.5× each other). If satisfied, cross-domain agreement is a structure common to natural text in general, not specific to emotion. In this case **this series also terminates**, but "a content-dependent structure shared across natural text exists" is recorded as an independent observation
- **Only if S1 is satisfied and $O_{em}$ is clearly larger than $O_{ew}$**, is there residual structure specific to emotion, and the series proceeds to the next stage

**Both S1 and S2 are termination conditions — this is emphasized.** These controls are placed **to be able to kill the hypothesis**, not to support it.

## AJ5. Next stage (only if S1 is passed; not registered in this amendment)

Whether residual directions actually control the output (floor comparison), and whether they generalize across models, will be registered separately after S1 is passed. **They will not be run before S1 is passed.**

## AJ6. Computational resources and order

Controls S and W are run by simply supplying a stimulus file to `g1_jacobian.py` (approx. 30 min per layer, 4 layers × 3 conditions ≈ 6 hours). The GPU is currently being used by Experiment A (confirmatory half, layers 22 and 27), and **will be launched after Experiment A completes.**

## AJ7. Promises in this amendment

- The job will be launched **only after this file has been committed and pushed**
- Judgement will be performed only by criterion AJ4; criteria will not be changed after seeing results
- If S1 or S2 satisfies the termination condition, **Paper 3 will be written with the methodological proposition of Amendment 32 AF5**
