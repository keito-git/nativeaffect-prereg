# Pre-Registration Amendment 14: Registering a Prediction About the "Mechanism" by Which the Floor Wins, Before Seeing the G1 Numbers

**Target**: Amendment 12 L3 (descriptive checks), pre-registration main body §2 G1
**Created**: 2026-09-26
**Status**: **G1 running. Not a single value—sensitivity directions, cosines with principal components, or judgement statistics—has been seen**
**Origin**: First-ranked proposals (Proposals 1 and 2) from 50 divergent proposals. **The adopted proposals have not had their priority confirmed. The team will be consulted**

---

## N1. Why Write Before Seeing the Results

**In Amendment 12 L3, the following descriptive check was mandated.**

> **Report the cosine between sensitivity directions and the top 10 principal components.** If the sensitivity directions almost coincide with the top principal components, the (variance, sensitivity) plane is degenerate and cannot be used for judgement.

**This check was written as a warning for judgement. However, the same observation is the explanation of the mechanism behind all previous negative results.**

**If that interpretation is written after seeing the results, it cannot be distinguished from post hoc rationalization. Therefore it is registered in advance as a prediction.**

## N2. The Prediction Being Registered

**Prediction P**: At each layer, the Jacobian sensitivity directions (the top 10 eigenvectors of $M$ from Amendment 12) **greatly overlap with the subspace spanned by the top 10 principal components of activations**.

**Quantitative expression of the prediction (fixed before execution)**: The **mean cosine of the principal angles between the 10 sensitivity directions and the 10 top principal components is 0.70 or above**.

## N3. What Can Be Said If the Prediction Is Correct (Explanation of the Mechanism)

The change in output logits is locally approximated as $\Delta \text{logits} \approx J v$ (where $J$ is the Jacobian from layer to logits).

**If the top singular directions of $J$ almost coincide with the top principal component directions**, by matching the projection lengths of direction $v$ onto each principal component with those of the axis, **the distribution of $\|Jv\|$ becomes nearly independent of rotation within the principal components of $v$.**

**That is, it follows geometrically that "no direction can exceed a floor with matched variance profile."** This simultaneously explains all of the following.

- The axes losing to the in-plane floor in 11 out of 12 cells
- **Even the human valence direction, with known semantic content, losing in all 20 cells**
- Principal components themselves (PC1–PC5) producing effects equal to or greater than the axes
- The conclusion remaining the same even when the metric is changed to S (if $\|Jv\|$ does not depend on the direction, the same holds for any readout)

**How to write**: Not "our axis was weak," but **"under this readout and form of intervention, the semantic content of a direction cannot in principle be identified."** **Write it as a positive claim, close to a proof of absence.**

## N4. If the Prediction Fails (Mean Cosine of Principal Angles < 0.70)

**The mechanistic explanation does not hold.** In that case:

- **(Variance, sensitivity) plane is not degenerate, so four-quadrant judgement can be used** (the original intended use of Amendment 12 L3)
- **Do not write the mechanistic explanation.** Write "the reason the floor wins is unexplained." **Do not search for another explanation afterward and fit it in**
- **The measurement in N5 is executed regardless of whether the prediction holds** (below)

## N5. Also Executed: Variance Dominance Rule (Proposal 1)

**Independent of whether the prediction holds, the following is measured. This is a separate analysis from the G1 judgement.**

1. At each layer, draw **1,000 random directions from within the top principal component subspace**
2. For each direction, record the **vector of projection lengths onto the top 10 principal components** (10-dimensional) and **JS**
3. Fit a **regression predicting JS from projection lengths alone** (both linear and gradient boosting), and report the **held-out coefficient of determination $R^2$**
4. **If $R^2$ is high, it is direct evidence that the "meaning" of a direction does not contribute to JS**

**Form of reporting decided in advance**: Report $R^2$ in a table by layer. **No binary judgement by threshold.** Report the value of $R^2$ itself as the strength of the claim.
**Also report how far the JS of axes and the human valence direction deviate from the predictions of this regression (residuals).** If the residuals are nearly zero, those directions also behave "as predicted by variance."

**Computation cost**: 1,000 directions × 4 layers × 1 JS computation at 0.0094 seconds (converted from the team's empirical measurement of 0.94 seconds/20 stimuli × both polarities) ≈ **about 10 minutes**. No generation involved.

## N6. This Is Not a Rescue of G1

**Stated explicitly.**

- **If G1 fails, G1 fails.** Record the conclusion text of the pre-registration as-is (main body §2 G1)
- **N2–N5 have value independent of whether G1 passes or fails.** Execute and report regardless
- **Do not use "the $R^2$ of N5 is high" in the form "therefore the failure of G1 is not our fault."** It is a mechanistic explanation, not an excuse
- **N3's claim can only be written if Prediction P holds**

## N7. Prior Art Confirmation (Complete Before Execution)

**The following will be checked with the team. If prior art exists, write it as "empirical demonstration of a known argument" and do not present it as our own proposal.**

1. **Research that quantitatively shows "the effect size of activation steering is mostly determined by the variance profile of the direction"**
2. **The argument that "because the top singular directions of the Jacobian coincide with the principal components of activations, directions cannot be identified under a variance-matched control" (local-linear non-identifiability)**
3. **Research that predicts the intervention effect by regression from projection lengths**

**In particular, 2 must be confirmed without fail if we are placing it at the core of our claim.** The background exists of Amendment 3 finding 4 existing works when equal-length intervention was found to already exist.
