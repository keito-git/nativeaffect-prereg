# Pre-Registration Amendment 18: α Is the Per-Stimulus Norm Ratio. N5 Is Measured for Both Arms

**Target**: Pre-registration main body §4 (intervention strength), Amendment 1 A1, Amendment 14 N5, Amendment 17
**Created**: 2026-09-26
**Status**: **G1 judgement has not been executed** (only the Jacobian phase = construction of candidate directions is complete). N5 not yet executed
**Origin**: A team member pointed out during N5 implementation a discrepancy between the registered text and the existing implementation, and that the arm for N5 was unspecified

---

## R1. Finalizing the Meaning of α: **Per-Stimulus Norm Ratio**

**The registered text was ambiguous.** Amendment 1 A1 wrote "α is the **residual-norm mean ratio**," and the pre-registration main body §4 wrote "the ratio relative to the mean residual norm at that layer and that stimulus." **It is not clear what "mean" modifies.**

**Confirmed: per-stimulus norm ratio.**

$$\alpha_{abs,i} = \alpha_{rel} \cdot \|h_i^{(last)}\|$$

**This is a clarification, not a change.** Three reasons are given.

1. **All existing measurements use this.** `plan_b0.py` injects using per-stimulus norms, and **B0, E1 diagnostics, and C1–C4 were all measured under this definition.** If N5 uses a different definition, comparison with existing results is impossible
2. **The Methodology §3.D of Paper 2 (methodology paper) explicitly states this equation with subscript $i$.** The manuscript already describes it as per-stimulus
3. **Per-stimulus is more in line with the design intent.** Activation norms differ by orders of magnitude across stimuli, so adding the same absolute quantity to all stimuli causes excessive perturbation for stimuli with small norms

**My phrasing "residual-norm mean ratio" was imprecise.** Recorded as such.

**Implementation note (pointed out by the team)**: The existing `Hook` applies `alpha * d` as an **absolute coefficient**. **Calling it as-is with α=1.0 results in injection of absolute coefficient 1.0, not a norm ratio.** Explicitly scale per-stimulus on the N5 side.

## R2. N5 Is Measured for **Both Arms**

Amendment 14 N5 did not specify the arm. Amendment 17's "primary α only" was phrasing that assumed Arm I (additive), and **the limitation does not apply to Arm II (reflection), which has no coefficient.**

**Confirmed: execute N5 for both Arm I (α=1.0) and Arm II (reflection).** Cost is about 2.1 hours.

**Reason**: The G1 judgement is "**satisfiable by either Arm I or Arm II**" (Amendment 1 A1). **If N5 is measured for only one arm, a situation may arise where the regression does not exist for the arm that passed.** This is exactly the point raised by the team member.

**Reporting**: Report $R^2$ separately for each arm. **Do not produce a single combined value for both arms.**

## R3. Finalizing the Execution Order (Important)

**Reading the team member's report, the group noticed that the order was reversed.**

**The Jacobian phase being complete is the "construction of candidate directions," not the G1 judgement.** The G1 judgement (whether the candidate axes' JS exceeds the PMF floor, both arms) **has not yet been computed even once.**

**Confirming the order.**

1. **G1 judgement** (candidate axes' JS vs. PMF floor, both arms). **This is the gate.** Cost is about 0.31 hours for 60 candidates (from the team's empirical measurement of 0.94 seconds/direction/layer)
2. **G2 if G1 passes** (open confirmation group of 143 sentences)
3. **G3**
4. **N5** (both arms, about 2.1 hours)
5. **G4** (only if G1–G3 pass, about 2.5 hours)

**N5 will not be run before the G1 judgement.** Two reasons.

- **G1 is a cheap (0.31-hour) gate.** Running the 2.1-hour N5 first is wasteful as an ordering
- **N5 has value independent of whether G1 passes or fails (Amendment 14 N6), but that means "also report it if it fails," not "run it first"**

**GPU budget**: Against the approved 5 hours, approximately 1.2 hours have been used in the Jacobian phase. G1 judgement 0.31 + N5 2.1 = approximately 3.6 hours. **If G4 becomes necessary, the total will be 6.1 hours, exceeding the budget, so the principal investigator will be consulted for additional approval at that point.**

## R4. Record: A Team Member Counted Transferred Files and Found the Error

The first rsync of `Vi.npy` **transferred 0 bytes due to an error in the glob syntax, but appeared to exit with code 0 due to `tail`.**
**The team member noticed by counting the number of files.** If it had been left as "transfer appeared to succeed," a hole in preservation would have remained.

**Rule**: Verify transfer and copy success **by file count and byte count, not by exit code.**
This is the same type as "commit success does not mean the intended files are included" (addendum to [[feedback_preregistration_timestamp]]).

## R5. Record: What Could Be Said for the First Time with the Exact Computation

**Principal angle cosine mean 0.1087–0.1340, maximum 0.2428–0.3096** (4 layers).

- **Prediction P failed** (threshold 0.70). Confirmed with exact values
- **The plane is not degenerate** (the maximum is far from 1). **Four-quadrant judgement can be used**
- **However, the latter does not follow from Prediction P having failed.** The upper bound for layer 11 was $\sigma_{\max} \le 1.070$, which excluded nothing. **It follows from directly measuring the maximum singular value**

**Inside fraction (comparison on the same scale)**: Old ICA axes **88.7–99.97%** vs. Jacobian sensitivity directions **3.0–4.9%**. **At opposite ends of the same scale.**

**Candidates exist in the targeted quadrant**: All 40 directions are below the variance of PC10 (the largest is only 17.7% of PC10), and the variance carried by each direction is 0.3% or less of total variance. **This is empirical measurement, not inference.**
