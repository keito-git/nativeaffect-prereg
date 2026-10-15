# Pre-Registration Amendment 10: Changing the G4 Model. Failure of the Precondition Is a Measurability Problem

**Target**: Amendment 6 F5 (decision not to change the model), Amendment 8 H2 (full-problem measurement)
**Created**: 2026-09-26
**Status**: **G1 not yet executed. No measurements involving intervention have ever been performed**
**Source**: `03_解析/plan_b/g4_precondition.json` (Apertus-v1.1-1.5B, GSM8K test 500 problems, no intervention)

---

## J1. Precondition Result: Fail

| Budget | Accuracy | Increment |
|---|---|---|
| 64 | 4.60% | — |
| 128 | 8.60% | **+4.00** |
| 256 | 8.80% | +0.20 |
| 512 | 8.80% | **±0.00** |

- Monotone non-decreasing: satisfied
- **Maximum − minimum = 4.20 points. Does not reach the criterion of 5.0 (`MIN_GAIN_POINTS = 5.0`, fixed in code before execution), so it fails**

**4.20 is close to 5.0, but something that does not satisfy the criterion does not satisfy the criterion. Do not write "substantially satisfied."**

**The curve saturates at 128 tokens.** Only the 64→128 interval moves; additional tokens beyond 128 are not being converted to accuracy.

## J2. Why the Model Is Being Changed. This Is Not a Post Hoc Rescue

Amendment 6 F5 fixed "the model will not be changed" and "we will not move to an instruct model and re-measure if G4 produces unsatisfactory results." **This decision is being changed. The reason is stated explicitly.**

**What Amendment 6 prohibited was "changing the model when the judgement result of G4 was unsatisfactory."** The reason for the current change is not the judgement result.

1. **G1 has not been executed.** Neither axis selection nor intervention has ever been measured. **We have not seen a single result involving intervention**
2. **The precondition is a measurability gate, not a judgement.** The premise of Amendment 6 F5 "the primary judgement is valid because it measures the frontier in budget coordinates" itself collapses **because there is no slope in the frontier above 128 tokens**
3. **The content of the failure is not "there is no effect."** It is the factual measurement that "the curve does not exist above 128 tokens as a target to shift upward." **It says nothing about the effect of the intervention**

**Therefore, this is not relaxing a condition to fit the result of an experiment, but replacing a device that cannot measure with one that can.**

**However, the boundary beyond which this change becomes indistinguishable from post hoc rescue is made explicit.**

> **Changing the model after G1 has been executed will not be done.** Model changes after seeing any of the G1–G4 judgement results are not permitted under this amendment.

## J3. Decision

**Execute all of Plan B (G1–G4) with a more capable instruct model.**

**Since G1 has not been executed, all of G1–G4 can be run on the same model.** The problem that Amendment 6 F5 was concerned about—"the model is not aligned between G1–G3 and G4"—does not arise.

**Model requirements (fixed before the experiment)**:
1. **Must satisfy the same criterion for the precondition on GSM8K (monotone non-decreasing and maximum − minimum ≥ 5.0 points)**
2. Must run under the constraints of 1 GPU and 8 GiB host RAM
3. **Forward hooks to the residual stream must function.** Avoid models with inter-layer KV sharing where edits do not propagate (Gemma-4-E2B-it was structurally unmeasurable in Paper 1)
4. In local HF cache, with minimal additional download required

**First candidate = Qwen/Qwen3-8B** (post-trained, on the 38-model registry, in local cache, used in layer 0 analysis).

**Procedure**: Re-run the precondition on the candidate model **with the same criterion and the same budget grid (64/128/256/512)**. **If the criterion is not satisfied, that model is not used either.** Candidates are changed until a satisfying model is found. **The criterion is not changed.**

## J4. Revised Computational Resource Estimate (Correcting the Estimate in Amendment 8)

**Empirical measurement**: For Apertus-1.5B, 500 problems × 4 budgets = **85 minutes** (batch=1, greedy). Amendment 8 estimated "about 2 hours per condition for all 1,319 problems," but **converting from the empirical measurement gives about 3.7 hours/condition**, **a 1.85-fold underestimate.**

Since an 8B model requires more time in proportion to the parameter count, **running all 1,319 problems × 4 budgets × 5 conditions with batch=1 is not realistic.**

**Approach (examine in this order)**:
1. **Implement batching first.** The current batch=1 is conservative, and the team estimates several-fold shortening is feasible. **Solve with implementation before compromising the design**
2. After batching, **measure empirically** and obtain execution time
3. **Only if still not manageable, reduce the number of stimuli or budget grid points.** In that case, **record it as an addition to this amendment before reducing, and state the reason**

**Long-time GPU occupation requires approval from the principal investigator before starting.** Consult when the estimate is available.

## J5. Record

- **The precondition failure is kept as a record.** It is the factual measurement that Apertus-1.5B does not convert additional tokens beyond 128 to accuracy on GSM8K
- **Paper A (methodology paper) is based on the Apertus-1.5B results and is not affected by this amendment.** Do not change the model description of Paper A
- **Plan B (G1–G4) will be executed as a separate study with Qwen3-8B.** Explicitly state in the Plan B manuscript that the model differs from Paper A
- **If Plan B results are obtained, whether the conclusions of Paper A (the reality of variance confounding and the fact that directions with known semantic content lose to the floor) also hold in Qwen3-8B will be verified by performing measurements corresponding to C1 and C2 separately.** Do not extrapolate the 1.5B findings to 8B in writing

**The option of shifting the grid to the lower side (16/32/64/128) is not taken.** It would mean selecting a grid that satisfies the criterion after seeing the results. A team member's own decision not to push this option was correct.
