# Pre-Registration Amendment 12: Rule for Aggregating Per-Stimulus Singular Vectors into a Single Set of Sensitivity Directions

**Target**: Amendment 1 A2 (adding Jacobian singular directions as candidates)
**Created**: 2026-09-26
**Status**: **G1 not yet executed. Jacobian computation also not yet executed**
**Origin**: In the process of examining empirical cost measurements by the team (VJP × 1 = 0.0680 seconds, top 10 = 114,800 VJPs = 2.17 hours), the group noticed a specification omission

---

## L1. Specification Omission

Amendment 1 A2 stated that "the **top singular vectors (top 10) of the Jacobian**" would be added as candidate directions.
**However, it was not specified how to aggregate them into a single set after computing them per stimulus.**

Since the output logits differ by stimulus, the Jacobian $J_i = \partial \text{logits}_i / \partial h_i$ is **separate for each stimulus $i$**.
287 stimuli × 4 layers produce 287 sets of top 10 vectors. **Whether to average them, concatenate and re-SVD, or take a majority vote changes the resulting 10 vectors.**

**If left unspecified before execution, the aggregation method could be chosen after seeing the results.**

## L2. Decision: Use Eigenvectors of the Sum of Projection Matrices

For each layer, determine the sensitivity directions by the following procedure.

1. For stimulus $i$, obtain the top 10 right singular vectors by randomized SVD. Denote the matrix with these as columns as $V_i \in \mathbb{R}^{4096 \times 10}$
2. **Form the sum of projection matrices**: $M = \sum_{i=1}^{287} V_i V_i^{\top} \in \mathbb{R}^{4096 \times 4096}$
3. **Take the top 10 eigenvectors of $M$ as the "sensitivity directions"**

**Three reasons for this choice are given.**

- **Sign ambiguity is structurally eliminated.** Singular vectors have indefinite sign, so averaging or concatenating causes $v_i$ and $-v_i$ to cancel each other out. **$V_i V_i^{\top}$ does not depend on sign**, so no post-processing to align signs is needed. Introducing post-processing would introduce a different arbitrariness, namely the choice of alignment method
- **Stimuli are treated with equal weight.** Each stimulus holds one vote as a 10-dimensional subspace. It is not pulled by stimuli with large Jacobian norms
- **Computation is negligible.** Eigendecomposition of a $4096 \times 4096$ symmetric matrix takes seconds on CPU. **Negligible compared to the 2.17-hour VJP**

## L3. Descriptive Checks to Be Reported (Not Used for Judgement)

- **Report the eigenvalue spectrum of $M$.** What fraction of the total does the top 10 eigenvalues account for? **If the eigenvalues are flat, the sensitivity subspaces of each stimulus are nearly orthogonal to each other, meaning that the concept of "common sensitivity direction" itself does not hold.** If that is the case, write it as such
- **Report the cosine between the obtained sensitivity directions and the top 10 principal components.** This confirms whether the goal of Amendment 1 A2 (placing variance and sensitivity as two independent axes) is achieved. **If the sensitivity directions almost coincide with the top principal components, the (variance, sensitivity) plane is degenerate and cannot be used for judgement.** If that is the case, write it as such

**The latter is already promised in Amendment 1 A2, but is fixed here as a concrete quantity.**

## L4. What Will Not Be Changed

- **The number of top 10 vectors will not be changed**
- **The randomized SVD oversampling of 10 and power iterations of 2 will not be changed** (the central cost estimate is based on this)
- **The exact version will be executed.** The proposal to substitute with gradient of a scalar output function was **not adopted** because the empirical measurements showed the exact version takes 2.17 hours. Being cheap is not a reason to change the procedure

## L5. Record

**This rule was written before the Jacobian was computed even once.** Even if the resulting 10 vectors are inconvenient, they will not be changed.
**If the 2 checks in L3 produce the conclusion "cannot be used for judgement," that will be reported as a result, and the four-quadrant judgement using (variance, sensitivity) will be withdrawn.** Trying other aggregation methods to search for usable results will not be done.
