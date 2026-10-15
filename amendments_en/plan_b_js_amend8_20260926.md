# Pre-Registration Amendment 8: G4 Will Be Measured on All GSM8K Test Problems. Sampling Is Abandoned

**Target**: Amendment 2 B3, Amendment 4 D2, Amendment 7 G3
**Created**: 2026-09-26
**Status**: **Before experiment** (G4 judgement measurements have not been executed. Only the precondition check is running)
**Origin**: A team member pointed out before execution that "the statistical power for the top difficulty quantile is insufficient"

---

## H1. Problem Identified

In Amendment 7, the sensitivity analysis was decided to be "the top quantile of the three quantiles by calculation step count in GSM8K." After a team member finalized the boundaries before the experiment (`03_解析/plan_b/gsm8k_difficulty_strata.json`):

- Step count is an integer, so the three quantiles do not divide evenly. **For test 1,319 problems: low 440 / mid 654 / high 225**
- With the design of measuring G4 on a 500-problem subset, **the top quantile would include only about 85 problems**
- If baseline accuracy is around 15%, **there would be about 13 correct answers**, with little prospect of detecting an effect

## H2. Decision: Abandon Sampling. **Measure on All 1,319 GSM8K Test Problems**

**The design of a 500-problem subset is abandoned entirely.** The problem disappears with this.

1. **The top quantile of 225 problems is automatically included in full.** Additional computation is zero. There is no need to decide on a sampling method
2. **No seed for sampling is needed.** Decoding is greedy, so the seed for 500-problem sampling was the only random source. **Using all problems eliminates the random source and also eliminates variability from subset selection**
3. **The n for the primary judgement increases from 500 to 1,319**

**The "3 seeds" written in Amendment 2 is abandoned.** With greedy and all problems, there is nothing to average over. **If an arm involving stochastic sampling (such as self-consistency) is added later, seeds will be restored for that arm alone and recorded at that time.**

**Execution time**: Generation time is proportional to budget, and all 1,319 problems at 256 tokens takes about 33 minutes (empirical measurements by the team). With 4 budget points (64/128/256/512), about 2 hours per condition. **Proportional to the number of conditions.**

## H3. Stratified Tests Are Done with a Paired Design

**The team's estimate "about 34 correct answers, so detection is not possible" assumes an unpaired comparison. Our comparison is paired** (with and without intervention for the same problem).

- **Stratified judgement uses McNemar's test** (looking at the number of problems where correctness changed with intervention). **The relevant quantity is not the number of correct answers but the number of discordant pairs**
- The effect size is expressed as a 95% CI from **a paired bootstrap** (resampling problems, 2000 iterations)
- **If judgement is not possible due to too few discordant pairs with n=225, record "unmeasurable."** Do not relax the criterion

**Statistical power is still limited.** Difficulty stratification results are reported as an **exploratory sensitivity analysis** and **not used in the primary judgement** (the primary judgement uses all 1,319 problems).

## H4. Finalizing the Conditions (Arms)

List the conditions to be measured in G4 before the experiment. **Do not add to them afterward.**

1. No intervention (baseline curve)
2. Axis X (cells that passed G3)
3. Human valence direction
4. Human arousal direction
5. Human dominance direction

**Conditions 3–5 are the core of Amendment 4 D2** (whether human VAD improves accuracy, whether that comes with reduction in computation).
Re-implementation of the existing 5 methods (Amendment 6 F4) will be executed **only after the above 5 conditions have been measured, with a separate time estimate and after obtaining approval from the principal investigator.**

## H5. Record

**This decision was made before seeing the results.** The 500-problem subset measurements were never seen (the precondition check is a feasibility check for intervention-free execution, not a G4 judgement).
**A design was made simpler by a team member pointing out the power problem before the experiment.** Abandoning sampling is better than choosing a sampling method.
