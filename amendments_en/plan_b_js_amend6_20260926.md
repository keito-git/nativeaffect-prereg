# Pre-Registration Amendment 6: Finalizing the Definition of "Token Count" (Budget or Self-Termination Length)

**Target**: `plan_b_js_prereg_20260926.md` §2 G4, Amendment 2 B3-d, Amendment 4 D2, Amendment 5 E3
**Created**: 2026-09-26
**Status**: **Before experiment** (only the precondition check for G4 is running. Primary judgement not yet executed)
**Origin**: Empirical observations by the team

---

## F1. Observed Facts

During the G4 precondition check (Apertus-v1.1-1.5B, GSM8K, 8-shot CoT, greedy), **`mean_generated_tokens` matched the token budget exactly** (64.0 at budget 64, 512.0 at budget 512).

**Cause**: The base model does not output EOS after the answer and always generates up to the limit.

## F2. Why This Can Become a Problem

The reduction reported by the existing 5 methods (ASC, ALS, Reflection Steering, ATLAS, PID) is **the length at which the model terminates generation by itself** (shortening of CoT, suppression of reflection).
**In a model that always generates up to the limit, that mechanism cannot in principle appear.** Therefore, using "token count" without definition means **comparing our measurements against the reported values of existing methods as if they were the same thing when they are not.**

## F3. Decision (Fixed Before the Experiment)

**The "token count" in the primary metric of G4 is the budget given by `max_new_tokens`.** Not the self-termination length.

- **Primary judgement**: Frontier of accuracy vs. **budget**. That is, the same coordinates as the test-time compute scaling curve of Snell et al. (arXiv:2408.03314). **State the reason for using these coordinates in the main text**
- **Secondary metric** (the "total tokens per correct answer" of Amendment 2 B3-d) is also **calculated on a budget basis**. Include the budget spent on incorrect answers and retries
- **What to record**: Always output the agreement or disagreement between `mean_generated_tokens` and the budget for each setting. **When moving to a model where they do not match, start reporting self-termination length as well**

## F4. How to Compare Against the Existing 5 Methods (Re-confirming Amendments 3 and 4)

**Do not directly compare the reported values of existing methods against our numbers.** This was already decided in Amendment 3, but the reason has been concretized in this amendment. **The coordinates are different.**

- **Re-implement the 5 methods in our environment and measure them under the same protocol (same model, same budget grid, same exemplars, greedy)**
- **If the re-implementation does not reproduce the reported values of the original paper, report that they were not reproduced.** Speculation about the cause may be written, but **do not state it definitively**
- **The condition for writing "outperformed existing methods" is limited to outperforming our own re-implementation values**. Do not write that we outperformed the numbers in the original papers

## F5. Implications for Model Selection

**G4 is valid with the base model.** Because the primary judgement measures the frontier in budget coordinates.
However, **write the following limitation in the main text**.

> The model used for evaluation does not self-terminate generation; therefore, the token count reported is the budget given, not the result of the model answering briefly of its own accord. In a model that self-terminates, an intervention may produce additional reduction through faster termination, and the present study does not measure that.

**No change to the instruct model will be made.** There are 2 reasons. (a) The primary judgement is valid in budget coordinates. (b) Changing the model means that the axis extraction of `axis_rebuilt_split_20260925.json` has to be redone, and the model would not be aligned between G1–G3 and G4. **Having them aligned is more important.**

**This decision was fixed before seeing the results.** After seeing unsatisfactory results in G4, we will not move to an instruct model and re-measure.
