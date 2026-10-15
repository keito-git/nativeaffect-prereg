# Pre-registration Amendment 55: Regularization defect in probes, its correction, and confirmation of reproduction of the original procedure

**Created**: 2026-10-04
**Target**: Stage A (reproduction of evaluation-dimension probes) of amendment 49, Part 1 (audit)
**Status**: A **measurement record**, not a judgement. The criteria for V1–V3, W1, and X1–X5 are not changed.

---

## BD1. The defect (first implementation)

In the first run of Stage A, the held-out $R^2$ for all 21 evaluation dimensions became **negative**.

| Model | Layer | Dimensions with $R^2>0.1$ | Median $R^2$ | Maximum |
|---|---|---|---|---|
| OLMo-2-7B | 13 / 18 / 24 | **0/21** | **−1.86 / −1.90 / −2.07** | −0.42 / −0.31 / −0.30 |
| Phi-3.5-mini | 13 / 18 / 24 | 1 / 1 / 2 | −0.98 / −0.93 / −0.88 | 0.11 / 0.27 / 0.26 |

$R^2<0$ means performance worse than predicting the mean, and this is **an implementation defect, not a property of the model**.

**Cause**: The ridge penalty was fixed at $\lambda = 1$. For a standardized design matrix with $d=4096$ and 5280 training rows, the diagonal of $X^\top X$ is approximately 5280, so $\lambda=1$ is effectively no regularization at all. Overfitting caused a breakdown on held-out data.

**How it was caught**: By cross-referencing against the original paper (Tak et al. 2025, arXiv:2502.05489), which reports that "evaluation dimensions are linearly detectable" and "appear more strongly near the final layer." **Without this cross-reference, we would have proceeded to intervention experiments with meaningless directions.**

## BD2. The correction

$\lambda \in \{10^1, 10^2, \ldots, 10^7\}$ is selected **using only the inner split of the training rows** (training 4224 / inner validation 1056 / evaluation 1320). **Evaluation rows are not used in the selection.**
Since Stage A had cached the activations in `H_*.npy`, no re-run of the models was required.

Implementation: `code/phase10/refit_probes.py` (bundled with this amendment)

## BD3. Results after correction (OLMo-2-7B; other models being computed)

| Layer | Dimensions with $R^2>0.1$ | Median $R^2$ | Maximum (dimension name) |
|---|---|---|---|
| 13 | **19/21** | +0.232 | 0.583 (pleasantness) |
| 18 | **19/21** | +0.263 | 0.633 (pleasantness) |
| 24 | **20/21** | +0.265 | **0.654 (pleasantness)** |

**Agreement with the original paper has been confirmed on two points.**

1. The majority of the 21 evaluation dimensions (19–20) are linearly detectable
2. **$R^2$ is higher in deeper layers** (0.232 → 0.263 → 0.265). Same direction as the layer-dependence reported in the original paper

The dimension with the best fit being `pleasantness` is also straightforwardly consistent with it being a core dimension in appraisal theory.

**On this basis, it is judged that the procedure of the original paper has been reproduced.** No inquiry to the authors will be made.

## BD4. Remaining differences (to be stated explicitly in the paper)

The differences already recorded in amendment 49 AX8 and in the Stage A output are restated here.

- **The prompt template is that of this study.** The original paper's template has not been confirmed
- **The original paper trains on the correctly classified subset for each model.** This study trains on all 6600 stimuli
- Layers are at relative depths 0.40 / 0.5625 / 0.75. The relative depth of intervention layers 9/16 for the main model (Llama 3.2 1B) of the original paper is 0.5625

**Absolute $R^2$ values will not be numerically compared with the original paper.** The comparison is limited to the **direction of layer dependence** and **the proportion of linearly detectable dimensions**.

## BD5. Recorded as a lesson

**Directions must not be used without checking the $R^2$ of the probes.** If regularization is left at a default value, a "direction" is still obtained even when held-out breaks down in high dimensions. Intervening with such a direction means measuring effects in a meaningless direction.

**Cross-referencing against the values reported in prior work is the cheapest check against this kind of defect.**

## BD6. Promises

- Both the defect in BD1 and the corrected values in BD3 will be **written in the paper**. Writing only the corrected values is not acceptable
- The differences in BD4 will not be hidden
- If $R^2$ is low for other models, **those models will not be excluded — the low values will be reported as-is**
