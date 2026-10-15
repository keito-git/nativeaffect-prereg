# Pre-Registration Amendment 16: The Reasoning in Amendment 15 Had an Invalid Step. The Conclusion Is Unchanged

**Target**: Amendment 15 O1, Reason 1 (the reasoning used to judge Prediction P)
**Created**: 2026-09-26
**Status**: Layers 11 and 16 of G1 are complete. **Judgement statistics have not been computed**
**Origin**: A team member constructed a counterexample and pointed out an error in the group's reasoning (pre-registration §23, commit `423efd5`)

---

## P1. The Invalid Reasoning

In Amendment 15 O1, the following was written.

> **Empirical measurement for layer 11**: `max_abs_cos_with_top10_PC = 0.1727`. **Since the maximum is 0.17, the mean is 0.17 or below.**

**This does not hold.**

What is stored is a per-**element** summary of the 10×10 matrix $C[k,j] = |PC_k \cdot s_j|$.
**The "principal angle cosines" stated by Prediction P are the singular values of the signed inner-product matrix $G = \mathrm{PC}^\top S$, not the elements of $C$.**

**The maximum element value does not bound the singular values.** A team member constructed a counterexample numerically.

> **An 8th-order Hadamard matrix divided by $\sqrt{8}$ has all elements equal to 0.3536, but the two subspaces are completely identical** (all principal angle cosines are 1.0000). For a 4th-order matrix, all elements are 0.5000 with the same result.

**Therefore "because the elements are small, the subspaces are nearly orthogonal" cannot be said.**

## P2. Valid Reasoning (Path Shown by the Team)

Via the Frobenius norm.

$$\mathrm{inside\_fraction}(s_j) = \sum_k (PC_k \cdot s_j)^2 \le n_{pc} \cdot \max_j^2, \qquad \sum_j \mathrm{inside\_fraction}_j = \|C\|_F^2 = \sum_i \sigma_i^2$$

By Cauchy–Schwarz, $\mathrm{mean}(\sigma) \le \sqrt{\|C\|_F^2 / n_{pc}}$.

| Layer | Element max of $C$ | Upper bound of $\|C\|_F^2$ | **Upper bound of mean principal angle cosine** | Registered threshold |
|---|---|---|---|---|
| 11 | 0.1727 | 1.1463 | **0.3386** | 0.70 |
| 16 | 0.1228 | 0.8645 | **0.2940** | 0.70 |

**Both layers have strict upper bounds far below the threshold. Prediction P cannot hold for layers 11 and 16.**

**The conclusion of Amendment 15 (not writing the mechanistic explanation) is unchanged.** Only the path of reasoning changes.

## P3. The "Good News" Side Is Also Not Established (For the Same Reason)

The group stated in the Amendment 15 report "**(variance, sensitivity) 2 axes are standing independently / four-quadrant judgement can be used**," but **this is also not established.**

From $\sigma_{\max}^2 \le \sum \sigma_i^2$:

- **Layer 11**: $\sigma_{\max} \le 1.070$. Against an upper bound of 1, **nothing is excluded**. **The possibility that one direction of the sensitivity subspace is completely contained in the principal component space cannot be ruled out**
- **Layer 16**: $\sigma_{\max} \le 0.930$. Complete containment is excluded, but the margin is small

**The upper bound denies "mean ≥ 0.70" but does not establish "nearly orthogonal."** Both are in the same position. **Neither will be written until the exact value of $\sigma_{\max}$ is measured.**

## P4. The Safety Valve of Amendment 12 L3 Was Not Functioning

The degeneracy detection in `g1_jacobian.py` is `bool(cos.max() > 0.9)`, which is also **per element**.
**In the Hadamard example of P1, the element maximum is 0.354 so this flag stays False, but the two planes are identical.**

**Therefore this flag cannot detect "degeneracy of the (variance, sensitivity) plane" as required by Amendment 12 L3.** It was not used for judgement, but **it was not functioning as a safety valve.**

**Degeneracy judgement will use `principal_cosine_max` (the maximum singular value of $G$).** Per-element quantities will not be used.

## P5. Variance Is Measured Empirically, Not Inferred

The group stated "sensitivity directions are nearly orthogonal to the top 10 principal components = the model is sensitive in directions with small variance."

**When exactly orthogonal, this reasoning is correct** (a team member tried to construct a counterexample and could not, and this was confirmed via an argument from PCA optimality: if the variance of a direction orthogonal to the top k principal component space exceeds $\lambda_k$, swapping would increase explained variance, a contradiction).

**However it does not hold for partial overlap.** The variance of a unit direction with inside fraction $f$ only guarantees $\mathrm{var} \le f\lambda_1 + (1-f)\lambda_k$, and since $\lambda_1 \gg \lambda_k$, **even at $f \approx 0.2$ it can exceed $\lambda_k$** (confirmed numerically by a team member).

**Therefore variance will be measured empirically, not inferred.** Output the actual variance of each direction, its ratio to $\lambda_1 \ldots \lambda_{10}$, and the number of directions falling below $\lambda_{10}$.

## P6. Record the Inside Fraction (Supplementing Amendment 12 L3)

**The `inside_fraction` (fraction of containment in the top 10 principal component space) of each axis that passes selection must always be recorded.**

**This is the same quantity measured for the old model's ICA axes** (88.7–99.97%). **The same quantity is needed for comparison.**
**Reporting per-element maxima was the error.**

**"The candidate basis is not a paraphrase of principal components" and "axes that pass selection are not close to principal components" are different claims.** The latter is shown by inside fraction.

## P7. Record

**The group used a per-element summary of a matrix as an upper bound for the principal angles of subspaces.** This is invalid as linear algebra.
**A team member showed it by constructing a counterexample (Hadamard).** "The type of error where what was thought to be an upper bound is not an upper bound" is settled by one counterexample.

**The conclusion was unchanged only by coincidence.** The correct upper bound via Frobenius happened to be below the threshold. **If the upper bound had been 0.9, the group would have concluded "failed" via an invalid argument.**

**Lesson**: When discussing the overlap of subspaces, **do not use per-element quantities (maximum, mean) as substitutes for principal angles.** Principal angles are the singular values of G. Related: the same family as ⑧ of [[feedback_measurement_audit_before_interpretation]] (do not assume the order of linear algebra library outputs).
