# Pre-registration Amendment 36: Test whether the residual after removing human V/A/D has structure (direct test of the principal investigator's hypothesis)

**Created**: 2026-10-03
**Position**: Pre-registration of a new question. Amendment 34 (H3 withdrawn) and Amendment 35 (residual controls) are not changed. Controls S/W from Amendment 35 are absorbed into this series.
**Launch condition**: The job must not be launched until this file has been committed and pushed to remote.

---

## AK0. Why the measurement target is changed

The principal investigator's hypothesis is: "Concepts unknown to humans combine to form emotional concepts; those concepts generalize across AIs and can be controlled by intervention."

What was measured in Amendments 29–34 was "whether sensitivity subspaces agree across domains." **This is not the statement of the hypothesis.** Control R (Amendment 34) confirmed that this proxy indicator is dominated by the layer's weight geometry, establishing that it is also unsuitable as a proxy indicator.

The direct form of the hypothesis is as follows. **Paper 1 showed that 38 models share emotion geometry and measured the coefficient of determination against human valence/arousal/dominance. What the hypothesis says is that the major portion of the shared structure is not human axes.** Therefore what should be measured is:

> **Whether the residual after removing the human V/A/D subspace has reproducible structure.
> And whether that residual is shared across models.**

## AK1. Why this series is stronger than past series

1. **A positive control is built in.** Since Paper 1 actually produced V/A/D coefficients of determination, when a result of "no structure in the residual" appears, it cannot be confused with instrument failure
2. **Human axes are explicitly defined.** "Outside the human framework" has an operational definition: "the orthogonal complement of the 3-dimensional subspace spanned by V/A/D," not vague phrasing
3. **Existing assets can be used.** V/A/D directions (4096-dimensional) for 5 models are saved in `direction_pca50/vectors/`, and the extraction pipeline also exists

## AK2. First fix the unit problem (Stage 0)

The saved V/A/D was estimated from **layer 21, standardized activations** (`pipeline: preprocess_layer(standardized, clip ±5SD) -> PCA-50`). The Jacobian directions in Paper 3 are from **layers 11/16/22/27, raw residual stream.**

**Taking cosines directly between these two is meaningless.** Standardization stretches the space anisotropically, so orthogonality in the standardized space does not agree with orthogonality in the raw space.

**Stage 0**: Recompute V/A/D directions using the same layer, same preprocessing (raw residual stream, final token position, no padding) as Paper 3. Estimation uses the same standardized ridge regression as Paper 2, with published vocabulary norms as target variables. **No cosines will be reported until Stage 0 is complete.**

## AK3. Stage 1: Residual reliability (the largest gate)

Let $H$ be the 3-dimensional subspace spanned by V/A/D, and $Q$ the sensitivity subspace (or primary activation subspace). Write the residual as $Q^{\perp H}$.

**Procedure**: Category-stratified random 2-split A/B of the 144 E1 discovery-half stimuli (seed 20261003; save split first). Independently estimate residual subspaces from A and B, and measure their agreement $O_{AB}$ by mean squared canonical correlation. Null: random subspaces of the same dimension.

**Judgement criteria fixed in advance (require 3 or more of 4 layers to be satisfied)**

- **K1**: Energy retained by the residual is **10% or more** of the total. If below this, the human axes nearly explain everything, and **this series terminates**
- **K2**: $O_{AB}$ is **5× or more** the null. If below this, the residual is estimation error, and **this series terminates**
- **K3**: K1 and K2 still hold after removing the Control-R-derived subspace. If not, the residual is weight geometry, and **this series terminates**

**If any of K1–K3 triggers termination, Paper 3 will be written with the methodological proposition of Amendment 32 AF5.**

## AK4. Stage 2: Causal effectiveness of residual directions

Executed only if Stage 1 is passed. Take directions from the residual subspace and intervene against the same floor as Paper 3 (variance-matched in-plane control), and measure whether they exceed the floor.

- **K4**: The floor-exceed rate of residual directions significantly exceeds that of the same number of random directions. If below, the residual is an epiphenomenon, and this series terminates

## AK5. Stage 3: Cross-model sharing

Executed only if Stage 2 is passed. Estimate residual subspaces for the 5 models in Paper 1 (Qwen3-8B / llm-jp-4-8b-base / gemma-4-E2B-it / granite-4.2-3b / Dense_1b_130B) and measure cross-model agreement. Since dimensions differ, compare by null-normalized ratios within each model.

- **K5**: Cross-model agreement is **5× or more** the null, and this holds even after removing the Control-R-derived subspace

**Only if K5 is satisfied** will we state: "Language models share emotion representation structure that is not explained by the human axes."

## AK6. Limitations stated in advance

- V/A/D is one of multiple human frameworks for describing emotion. Being outside V/A/D does not mean "unknown to humans." **What this study can claim is only "not explained by V/A/D"**
- "Combine to form emotional concepts" (the 2nd element of the principal investigator's hypothesis) cannot be measured by this design. A separate design is needed
- The residual by definition includes estimation error. K2 and K3 are placed to exclude this, but they are not perfect

## AK7. Promises in this amendment

- The job will be launched **only after this file has been committed and pushed**
- Judgement will be performed only by K1–K5; criteria will not be changed after seeing results
- No cosines will be reported until Stage 0 is complete
