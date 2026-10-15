# Pre-Registration Amendment 1: Addition of Isometric Intervention and Change to Direction Search Space (Plan B, JS Version)

**Target**: `plan_b_js_prereg_20260926.md` (commit 6f351d5)
**Created**: 2026-09-26
**Status**: **Before experiment.** Do not execute until this amendment is committed and pushed to git
**Origin**: 6 proposals adopted from 46 divergent proposals. **The adopted proposals have not yet had their priority confirmed. Inquiry to the team is ongoing. If prior work exists, write them as "application of a known method" and do not present them as our own proposals**

---

## A1. Adding One More Form of Intervention (the Most Important Change)

**Re-recognition of the problem**: In the additive intervention x ← x + αd, the change received downstream is coupled with "the variance already existing along that direction."
The PMF floor is a **patch that addresses this confound post hoc**, but the mechanism itself remains.

**Change**: Measure the following two as **co-equal primary arms**.

- **Arm I (additive)**: x ← x + αd. α is the residual-norm ratio {0.5, 1.0, 2.0, 4.0}, primary judgement at 1.0 (as in the original pre-registration)
- **Arm II (reflection, isometric)**: x ← x − 2(x·d)d. **An orthogonal transformation that preserves the norm and does not change any component other than d**. Has no coefficient, so no choice of dosage is required

**Why isometric intervention is effective against confounding**: Reflection is an orthogonal transformation, so it preserves the covariance structure of the activation set.
The pathway "large variance direction, therefore large addition" does not exist. The magnitude of change is determined by "the projection value already present along that direction," and that can be drawn from the same distribution for a random direction too.

**Effect on judgement**: The passing condition of G1 is set to **be satisfiable by either Arm I or Arm II**. The results of both arms must always be reported together.
**If Arm I passes and Arm II does not, that is evidence that "the effect depends on the magnitude of the additive intervention," and it should be written as such.** Do not report only the arm that is convenient.

**Additional description (not used for judgement)**: Report whether the ranking of axes is reversed between Arm I and Arm II. If reversed, this becomes a methodological finding showing that the conclusions of existing studies using additive interventions depend on the form of intervention.

---

## A2. Expanding the Search Space for Candidate Directions (Adding One Criterion Independent of Variance)

**Change**: **Add** the following to the candidate axis population of §2 G1 (the existing ICA rank20 and PC1–PC10 are retained).

- **Sensitivity directions**: The top singular vectors (top 10) of the Jacobian from the residuals of layer L to the output logits. **Directions to which the model is sensitive**, defined independently of the variance of the data
- **Plot each candidate direction in 2D (variance, sensitivity) space as a figure**. The target is the **low-variance, high-sensitivity** quadrant

**Why include them**: If ICA axes exist only in "high-variance, high-sensitivity," then the axes are a byproduct of variance.
**If low-variance, high-sensitivity directions exist and exceed the floor, they cannot be explained by variance.** Either way, the matter is settled with one figure.

**Computation**: Forward + backward only. No generation needed. A few hundred prompts suffice.

---

## A3. Drawing a Calibration Curve from Variance to Effect, and Reporting the Excess (Generalization of PMF)

**Change**: At each layer, measure JS for **300 random directions sampled by stratification across the full variance spectrum**, and obtain a calibration curve via **nonparametric regression (isotonic regression) of variance vs. JS**.
The effect of an axis is reported additionally as the **excess (residual)** from this curve.

**Position**: **The judgement remains as the PMF floor** (the original pre-registration is not changed). The calibration curve is **a descriptive addition**.
PMF "compares against directions with the same variance profile"; the calibration curve "subtracts the effect predicted from variance." **Both are reported, and it is examined whether the conclusions agree.**

---

## A4. Sharpening the Operational Definition of G3 (Decomposed into 3 Conditions)

**Change**: The judgement of §2 G3 is changed to a form that reports the status of the following 3 conditions **in addition to** R²_reduce < 0.50.

1. **Output is natural**: The decrease in log-probability of continuation after intervention is within a pre-specified threshold for each arm (for the additive arm at coefficient 1.0, decrease ≤ 0.30 nat; for the reflection arm, ≤ 0.30 nat)
2. **Does not rely on human emotion vocabulary**: The next-token distribution restricted to human emotion words remains **flat** after intervention (the KL relative to the neutral condition is smaller than the KL at the time of human valence direction intervention)
3. **Still deviates from neutral**: The full-vocabulary JS exceeds the floor (= condition of G1)

**The primary judgement remains R²_reduce.** The 3 conditions are **reported simultaneously**, and if any axis satisfies all 3, it is described as a **"state that systematically moves outputs but cannot be named in human vocabulary."**

**Rationale**: A small R²_reduce alone does not distinguish from a random direction (in high dimensions, any two directions are nearly orthogonal). **By requiring the conjunction of the 3 conditions, random directions fail on condition 1.**

---

## A5. Vocabulary-Level Coherence of Changed Tokens (No Additional Forward Pass Needed; Can Be Executed Immediately)

**Change**: From existing intervention results, compute the **mean pairwise cosine of the unembedding vectors of the top 50 tokens whose probability increased**, and compare across axes, PCs, and the floor.

**Position**: **Descriptive analysis for Paper A (methodology paper)**. Not included in the judgement of Plan B. **Involves no new computation, so it may be executed first as a re-analysis of existing data.**
JS only sees "how much it changed." Even at the same JS, if coherence differs, that is a difference in content. **If this metric distinguishes axes from the floor, it becomes a critique of our own design, which uses JS as the primary metric.**

---

## A6. Identifying the Nature of Layer 5 Axis 2 (Exploratory; Not a Gate)

For the **sole surviving case** (passed α=0.05 in both the discovery and confirmation groups with δ increasing from +0.25 to +0.55), the following are performed.

1. Collect the top and bottom 500 tokens/contexts each in a large corpus where the projection of layer 5 axis 2 is extreme, and cluster them
2. Report the overlap with emotion word dictionaries, syntactic roles, and correlations with frequency, word length, and concreteness
3. Change the extraction setting (ICA rank 10/30/50, whitened ICA, sparse dictionary) to **check whether a direction with cosine 0.8 or above reappears**
4. Report the asymmetry of effects for +α and −α, and the shape of the dose-response curve (threshold, saturation, non-monotonicity)

**This is exploratory, and hypotheses obtained here are not presented as claims as-is.** If a hypothesis is formed, a separate pre-registration will be written and tested on independent data.
**Reason for execution**: If the nature of the sole surviving case is understood, other designs change from guesswork to hypothesis testing.

---

## Regarding Proposals That Were Not Adopted

Of the 46 divergent proposals, 6 were adopted. **Proposals that were not adopted were not negated; they are saved in full in `00_研究計画/` as candidates to revisit if G1 fails.**
In particular, the following 3 families were judged to be strong next steps if G1 fails.

- The family representing concepts as **subspaces, circuits, attention patterns, or temporal structures** rather than directions
- The family using CCA to search for directions **shared across independently trained multiple models but not aligned with human probes**
- The family using directions that only move emotional outputs in **machine-specific contexts** (code, system prompts, refusal contexts) as the operational definition of "AI-native"

---

## Execution Order (Principle: Do Not Change)

**The review response for Paper 1 (additional analysis of layer 0) is the top priority.** The amendments here are executed after that.
Only A5, which involves no new computation as a re-analysis of existing data, may proceed first.
