# Pre-Registration Amendment 73: Registration of E5 (Intervention Efficiency) and a Variance-Dominance Kill Switch as a Condition for Proceeding to E1

**Created**: 2026-10-06
**Occasion**: External advice (2026-10-06)
**Status**: Registration of new judgement E5 that directly verifies H1. The conditions for proceeding to H2 in Amendment 72 are also established.
**Activation condition**: E5 must not be judged until this file has been committed and pushed. **Never run once.**

---

## BV1. The Question

$$\mathrm{Efficiency}(v) = \frac{\text{Target emotional change}}{\text{Global output perturbation}}$$

Since the output perturbation is equalized to $J^\*$, the efficiency equals the target change under $J^\*$. The question is:

> **Under the same output perturbation budget, are human emotion axes and appraisal axes more efficient than variance-matched random directions?**

If not, **human axes are not privileged in terms of intervention efficiency**. This is a direct verification of H1.

## BV2. Families of Directions to Compare (Fixed Before Seeing Results)

| Symbol | Family | Count | Construction |
|---|---|---|---|
| (a) | Emotion category directions | 13 | Ridge regression onto emotion indicator variables |
| (b) | Appraisal dimension directions | 21 | Ridge regression onto crowd-enVENT ratings, single-effect-isolated |
| (c) | Principal component directions | 21 | Top 21 PCs of training-row activations |
| (d) | **Variance-matched random (F4)** | 21 | Permuting PC coordinates of target directions and flipping signs. **Floor** |
| (e) | **Gradient directions** | 13 | **Gradient of target readout with respect to $h$. Positive control** |

All families except (e) have 13–21 directions, and a procedure to cancel the advantage of selection is defined in BV4.

## BV3. Target Readout and Budget

The target is each of the 13 emotion categories. For emotion $e$, the target contrast is the centered indicator vector $t_e \in \mathbb{R}^{13}$. The centered probability change of 13 emotion words $\Delta p$ due to an intervention gives the effect as:

$$S_e(v) = \tfrac12\Big[\tfrac{\langle \Delta p(+\alpha), t_e\rangle}{\lVert \Delta p\rVert}
- \tfrac{\langle \Delta p(-\alpha), t_e\rangle}{\lVert \Delta p\rVert}\Big]$$

Antisymmetrization avoids sign-blindness. $\alpha$ is calibrated direction-by-direction so that the Jensen–Shannon divergence of the next-token distribution equals $J^\* \in \{0.02, 0.05, 0.10\}$.

## BV4. Separation of Selection and Evaluation (Canceling the Advantage of Family Size)

For each target $e$ and each family $F$, the following is performed.

1. On **selection contexts** (half of the stimuli), measure $S_e$ for each direction in family $F$ and select the best direction $v^\*_{F,e}$
2. On **held-out contexts** (the remaining half, unused in selection), measure $S_e$ of $v^\*_{F,e}$ and use this as the efficiency of family $F$

**The same procedure is applied to floor (d).** Because the best of 21 directions is selected and evaluated on held-out data, the same amount of selection-induced upward bias enters the floor as well.

## BV5. Redesigning the Positive Control (Because the Previous Control Did Not Function)

In Amendments 58, 59, and 61, the Warriner valence direction was used as a positive control, but it failed to reach the floor in 3 of 4 models and unmeasurable judgements continued. **It is replaced with a direction that is optimally constructed.**

The gradient of the readout $R_e(h)$ with respect to $h$:

$$g_e = \mathrm{normalise}\big(\nabla_h R_e(h)\big)$$

is used as the positive control. The gradient direction is **the direction that locally moves that readout the most**, so if this does not exceed the floor, it is definitive that the measurement itself is blunt.

**Judgement E5-pre (prerequisite)**: The held-out-context efficiency of $g_e$ exceeds the 95th percentile of floor (d) for the majority of targets. **If it does not, E5 is designated unmeasurable and no negative claim is made.**

**This prerequisite is stricter than the previous ones and carries more information.** If the gradient does not exceed the floor, it is understood that the readout design itself needs to be reconsidered.

## BV6. Judgement E5

**Judged only if E5-pre is satisfied.**

- **E5a (verification of H1)**: The held-out efficiency of human axis families (a) and (b) does **not exceed** the 95th percentile of floor (d) for the majority of targets. If they do not exceed, **human axes are not privileged in terms of intervention efficiency**
- **E5b (description)**: The held-out efficiency of all 5 families is reported in a table for each target $e$. **Whether PCs (c) outperform human axes (a)(b) is explicitly stated**

**If E5a does not hold** (human axes exceed the floor), **H1 is partially revised.** In that case, "human axes are privileged in terms of intervention efficiency" is written alongside the negative results from other routes. **Only the convenient side is not written.**

**Null soundness** (revised gate from Amendment 57 BF2): The floor distribution is non-degenerate.

## BV7. Condition for Proceeding to E1 (Discovery of Causal Modes) — Variance-Dominance Kill Switch

H2 in Amendment 72 is verified by discovering computational modes from intervention responses. **However, there is a danger that the decomposition of the intervention response space is dominated by variance.**

In the empirical measurements of this research series, even after equalizing the output perturbation, **the F3/F4 floor was approximately twice the F1 floor**. This indicates the possibility that **any direction within the dominant-variance subspace has a similarly large effect**. In that case, decomposing the effect fingerprints $\Phi(v_1),\dots,\Phi(v_N)$ would merely **extract the principal component subspace again**, resulting in the same outcome as the fifth route.

**Judgement E1-gate (condition for running E1, fixed before seeing results)**:

The effect fingerprint of direction $v$ is defined as:

$$\Phi(v) = \big[\, S_f(v) \,\big]_{f \in \mathcal{F}}$$

for a fixed set of readouts $\mathcal{F}$. **The readout set $\mathcal{F}$ is fixed in this amendment**: 13 emotion category contrasts, certainty, agency, and predictability, for a total of 16 components. Certainty, agency, and predictability use the log-odds of the binary questions from Amendment 63. **$\mathcal{F}$ is not changed after seeing results.**

Construct the fingerprint set $\{\Phi(r_j)\}$ of variance-matched random directions and the fingerprint set $\{\Phi(p_j)\}$ of principal component directions.

- **E1-gate**: The effective rank of the subspace occupied by the fingerprints of variance-matched random directions is **below 70%** of the effective rank of the subspace occupied by the fingerprints of all directions
- **If it does not fall below, "the fingerprint space is variance-dominated" is recorded and E1 is not run**

**Reason**: If the fingerprints of random directions alone span most of the fingerprint space, the modes obtained from decomposition reflect the variance structure rather than the content of the directions. In that case, verifying H2 with this design is not possible.

## BV8. What Can Be Written If It Fails (Fixed in Advance)

- **If E5-pre fails**: "Even the optimally constructed gradient directions do not exceed the variance-matched floor. Comparing intervention efficiency is not possible with this readout design." Reported as a limitation of the measurement design
- **If E5a fails** (human axes exceed the floor): "Human axes exceed the floor in terms of intervention efficiency" is written, and **H1 is revised for intervention efficiency**
- **If E1-gate fails**: "The effect fingerprint space is dominated by variance, and mode discovery from intervention responses cannot be established with this design." H2 is not run and the paper is closed within the scope of H1

## BV9. Commitments

- E5 is judged after this file is pushed
- The composition and count of families (a)–(e) are not changed after seeing results
- The separation of selection and evaluation is also applied to floor (d). Only the floor is not given a selection advantage
- If E5-pre is not satisfied, no negative claim is made
- **If E5a fails, that is also reported. H1 is not unconditionally maintained**
- The 16 components of readout set $\mathcal{F}$ are not changed after seeing results
- **If E1-gate fails, E1 is not run.** The seventh same-pattern failure is not repeated
