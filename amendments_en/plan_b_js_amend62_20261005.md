# Pre-Registration Amendment 62: 200 Floor Trials Do Not Rescue the Dimension-Level Judgements. Terminating and Redirecting Resources to the Confirmation Set

**Created**: 2026-10-05
**Target**: Amendment 59 (change to 200 floor trials)
**Judgement**: **Even with 200 floor trials, dimension-level judgements do not pass. The "worsening" predicted in Amendment 59 BH4 occurred.**
**Principal investigator decision**: 2026-10-05. The 200-trial floor is terminated at 2 models, and resources are redirected to the confirmation set (Amendment 60).

---

## BK1. Results with 200 Floor Trials (2 Models)

| Model | Floor trials | Positive control $S$ | Floor p95 | Positive control | Dimension-level pass |
|---|---|---|---|---|---|
| OLMo-2-7B | 40 | +0.2460 | +0.1762 | Exceeded | **3/17** |
| OLMo-2-7B | **200** | +0.2460 | **+0.2430** | Exceeded (narrow margin) | **1/17** |
| Llama-3.2-1B | 40 | +0.1727 | +0.2885 | Not reached | 0/16 |
| Llama-3.2-1B | **200** | +0.1727 | — | Not reached | **5/16** |

**For OLMo-2-7B, the floor p95 rose from +0.1762 to +0.2430, and the number of passes decreased from 3/17 to 1/17.**

**This is as predicted in Amendment 59 BH4** ("possibility of decreased pass count: `self_responsblt` passed by a narrow margin, and if the floor p95 estimate rises it may fail. If it fails, that is reported as-is"). The commitment is kept and reported.

## BK2. Mechanism — The Tail Does Not Shrink with Sample Size

The floor p95 is **the direction-specific variability itself**, not estimation error. Increasing the sample size results in **a more accurate estimate of the tail, and p95 rises** (with 40 samples, the tail was underestimated).

> **The 3/17 passes at 40 floor trials were apparent passes due to underestimation of the tail.**

Therefore, dimension-level judgements do not pass not because of a power problem but because of **the fact that effects are on the same order as the floor tail.** **Increasing precision cannot rescue this.**

## BK3. The Termination Decision

The purpose of 200 floor trials was to confirm "whether dimension-level judgements could be rescued by precision." **OLMo-2-7B's results negated this.** Running the remaining 2 models (Gemma-2-9B and Mistral-Nemo-12B) is expected to reach the same conclusion, requiring approximately 2.5 hours (8990 seconds) per model.

**Terminating and redirecting resources to the 6 confirmation set models (Amendment 60).**

**To be recorded**:
- The 200-trial floor was run for **only 2 models: Llama-3.2-1B and OLMo-2-7B**
- **The 200-trial floor was not run for Gemma-2-9B or Mistral-Nemo-12B.** The fact that they were not run and the reason (above) will be written in the paper
- **The 40-trial results are available for all 4 models.** The dimension-level results will be reported from those, and the 2-model 200-trial results will be shown alongside as "evidence of tail underestimation"

## BK4. The Position of the Aggregate Test Is Confirmed

The reason dimension-level judgements do not pass is that effects are on the same order as the floor tail. **By asking as a family, the comparison target becomes the floor mean rather than the floor tail.** Averaging across 17 dimensions reduces the standard error by approximately 1/4, making comparison with the floor mean (near 0) possible.

**This is not a convenient trick to gain power; it is an estimator suited to the question.** The question "does the family of evaluation dimensions move emotion in the predicted direction?" is a different proposition from whether each dimension individually exceeds the floor tail.

**However, "individual evaluation dimensions control emotion" cannot be written.** The limitation in Amendment 60 BI4 is maintained.

## BK5. Commitments

- The fact of worsening with 200 floor trials is reported. The 40-trial results are not overwritten
- The termination at 2 models and the reason are written
- The aggregate test is not justified as "a manipulation for power." **It is presented as an estimator suited to the question, alongside the reason that dimension-level judgements do not pass (effects are on the same order as the floor tail)**
- The criteria for the confirmation set (Amendment 60 BI3, Amendment 61 BJ4) are not changed
