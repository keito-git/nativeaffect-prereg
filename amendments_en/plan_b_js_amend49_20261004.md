# Pre-registration Amendment 49: Reconstituting Paper 3 as a "variance-matched audit of appraisal dimension steering" /
# Replacing the null for E5 with within-skeleton permutation

**Created**: 2026-10-04
**Decision by the principal investigator**: 2026-10-04. (1) Paper 3 is framed as an audit of prior research using VMIC. (2) The null for E5 is reconstructed and re-judged.
**Activation condition**: Neither Part 1 nor Part 2 judgements may be performed until this file has been committed and pushed. The value of the within-skeleton permutation null for E5 has not been computed at the time of creating this file.

---

# Part 1: Variance-matched audit of appraisal dimension steering

## AX1. Subject of the audit (stated fairly)

Tak, Banayeeanzade, Bolourani, Kian, Jia, Gratch (2025) "Mechanistic Interpretability of Emotion Inference in Large Language Models", ACL 2025, arXiv:2502.05489.

**What the study reports** (confirmed from the HTML version of the paper):

- Data: crowd-enVENT (Troiano, Oberländer, Klinger 2023), 6,800 emotion descriptions, 13 emotion categories, 23 self-rated appraisal variables
- Procedure: For each layer and each appraisal dimension, a linear regression $\hat r_a = v_a^\top x + b_a$ is trained, and $v_a$ is taken as the representation of that appraisal dimension
- Isolation of individual effects: $z_a = (I - P_{-a}) v_a$ (projections onto all other appraisal dimensions are removed)
- Intervention: $x \leftarrow x + \beta\, z_a/\lVert z_a \rVert_2$ applied to the hidden state at an intermediate layer
- Effect: change in the emotion label distribution of the output
- Models: Llama 3.2 1B/8B, Gemma 2 2B/9B, OLMo 2 7B/13B, Phi 3.5 mini/Phi 3 medium, Ministral 8B, Mistral 12B — 10 models in total

**Controls placed by the study**: layer specificity (no effect in early or terminal layers), the same procedure on a different task (predicting the first word), prompt robustness, and Appendix B knockout (replacing activations with zero or random activations).

**Controls not placed**: **A within-plane random direction floor with matched variance, applied to the steering itself.** The intervention takes the form of multiplying a unit-norm direction by $\beta$, and **output perturbation magnitude is not equalised across directions.**

**This description is based on the HTML version of the paper.** Until the main PDF and appendix are obtained and rechecked, the paper will not state definitively that "no control exists." **The paper will say "not found within the scope we examined."**

## AX2. Question

> Does the reported finding that intervention on appraisal dimension directions moves emotion output survive under **a within-plane random direction floor with matched variance**?

Paper 2 showed that the phenomenon in which an axis exceeds full-space random directions disappears in 11 of 12 cells when **directions drawn from within the top principal component subspace with matched variance** are used as the floor. Because appraisal dimension directions are obtained by regression against activations, **there is a structural reason for them to align with high-variance directions.** They may therefore be subject to the same confound.

## AX3. Hierarchy of controls (identical to Paper 2; unchanged)

| Floor | How it is drawn |
|---|---|
| F1 Full space | Haar random direction from $\mathbb{R}^d$ |
| F2 Axis-orthogonal | From the subspace orthogonal to all appraisal dimension directions |
| F3 Within-plane | From within the top-$k$ principal component subspace ($k$ is the minimum value containing 90% of $z_a$) |
| **F4 VMIC** | As F3, and additionally **variance is matched to $z_a$** (variance profile in principal component coordinates is matched) |

**The primary floor is F4.** Comparisons using F1 alone will not be reported.

## AX4. Equalising output perturbation

For each direction $v$, $\beta$ is individually calibrated by binary search so that the JS divergence of the next-token distribution (over the union of the top-100 words) reaches the target value $J^\*$. Measurements are taken at 3 points: $J^\* \in \{0.02, 0.05, 0.10\}$.

**Comparisons without equalisation will not be reported.** Without equalisation, the result would only reflect "the direction that hits harder moves more."

## AX5. How to measure effects (without annotators)

The study in question examines changes in the emotion label distribution of the output. Because this research follows a policy of **not using annotators**, the following 2 measures are used in combination.

- **E1 (label probability)**: The next-token probability of each of the 13 emotion words is obtained, and the change in distribution before and after intervention is measured by Jensen–Shannon divergence. The vocabulary is fixed to the 13 categories of crowd-enVENT.
- **E2 (signed readout)**: $S(v) = \tfrac12[R(h+\alpha v) - R(h-\alpha v)]$ from Amendment 37. The antisymmetric component is used to avoid sign-blindness.

**If the two measures do not agree on the conclusion, neither conclusion is claimed.**

## AX6. Judgement

**Judgement V1 (main judgement)**: The effect of appraisal dimension direction $z_a$ exceeds the 95th percentile of F4 (VMIC). The pass rate per cell is reported for each combination of 23 appraisal dimensions × model × layer × $J^\*$.

**Judgement V2 (floor hierarchy)**: How the pass rate changes as the floor is made stricter in the sequence F1 → F2 → F3 → F4 is reported. **If a cell passes under F1 but fails under F4, the reported effect is explained by variance confound.**

**Judgement V3 (positive control; prerequisite)**: The Warriner valence direction moves E1 and E2 above the F4 floor. **If it does not, measurement resolution is insufficient, and the non-satisfaction of V1 will not be claimed.** (Because in Paper 2 the positive control lost to the within-plane floor, this is required.)

The **null soundness gate** (Amendment 45 AT2.5) is applied to all judgements.

## AX7. What can be written regardless of outcome (written in advance)

- **If V1 fails**: "The reported effect of appraisal dimension steering cannot be distinguished from random directions under a variance-matched within-plane floor." **Written as the identification of a boundary condition, not a refutation.** The contributions of the study (that appraisal dimensions can be linearly decoded, their localisation to layers) are not negated.
- **If V1 passes**: "Appraisal dimension steering survives under the strictest floor." This is a replication of the study in question, and **the novelty of this research lies in the introduction of the floor**, which will be explicitly stated.
- **If V3 fails**: Reported as unmeasurable and improvement of the measurement method is noted as a future task.

## AX8. Models and availability

Among the 10 models in the study in question, some may not be obtainable (`meta-llama/Llama-3.1-8B` has been confirmed as gated=manual). **Only models that can be obtained will be used, and models that could not be obtained will be explicitly stated.** No substitutes will be created (because auditing the same model is the key point).

The availability of crowd-enVENT will be confirmed first, and **if it cannot be obtained, this audit will not be conducted.** No substitution with self-created stimuli will be made (because auditing the same data is the key point).

---

# Part 2: Replacing the null for E5 with within-skeleton permutation

## AX9. Why the replacement is made

As recorded in Amendment 48 AW3, on E5 the permutation null for stimulus rows reached a mean of +0.8483, and the minimum observed agreement of +0.8502 did not exceed p95 +0.9155. **Because E5 is a grid with shared skeletons, rows are close to each other, and a permutation that crosses skeletons barely changes the relative representation profiles.**

This is a design flaw in the null and **does not mean that agreement is absent in E5**.

## AX10. New null (defined before seeing results)

**Null N1′ (within-skeleton permutation)**: The skeleton is fixed, and **only the category assignment within the same skeleton is permuted** (500 repetitions). The difference between skeletons is fixed; only the category structure is destroyed.

**Judgement M1′**: For all pairs in the main series, the agreement in the residuals after removing the portion explained by surface statistics exceeds the 95th percentile of null N1′.

**Null soundness gate**: The standard deviation of N1′ is non-zero and is at least 1/10 of the difference from the observation. If not satisfied, **it will be recorded as unmeasurable** and no further claims about E5 will be made.

## AX11. Promises

- M1′ will be calculated after this file is pushed
- The unit of permutation will not be changed after seeing the results
- If M1′ is unmeasurable, it will be written that "a null with statistical power could not be constructed" for E5
- The non-satisfaction recorded in Amendment 48 for E5 (old null) **will also be reported**. It will not be concealed by the replacement
- **Until the main PDF and appendix of the study in question are obtained and confirmed, the absence of a control will not be stated definitively**
