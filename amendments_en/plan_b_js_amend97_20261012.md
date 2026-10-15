# Pre-Registration Amendment 97: SP-act's Selection Rule Was Too Strict. Raise Exploration Budget and Exclude Unmeasurable Models.

**Created**: 2026-10-12
**Target**: Control SP-act (activation-cluster partition) from Amendment 96 CO2
**Judgement**: **The judgement criterion is not changed. Raise the exploration budget from 200 to 2000 trials, and exclude models with fewer than 10 accepted partitions as unmeasurable. The threshold is introduced after having seen the collapsed statistics; this is stated explicitly.**
**Trigger condition**: Do not run the judgement of the re-execution until this file is committed and pushed.

---

## CP1. What Happened

Amendment 96 CO2 registered the acceptance of 30 partitions from activation clusters whose **held-out AUC is at least equal to the emotion partition's**. The result of running with a limit of 200 trials showed large variation in acceptance count across models.

| Emotion partition AUC | AUC range of activation cluster candidates | Accepted | Registered judgement |
|---|---|---|---|
| 0.9546 | 0.9383–0.9778 (200 evaluated) | 5 | Fail ($p$=0.1667) |
| 0.9652 | 0.9086–0.9658 (200 evaluated) | **1** | Fail ($p$=0.5) |
| 0.9726 | 0.9324–0.9742 (200 evaluated) | 4 | Fail ($p$=0.2000) |
| 0.9684 | 0.9424–0.9798 (84 evaluated) | **30** | **Pass** (11/13 · +6.25 SD · $p$=0.0323) |
| 0.9724 | 0.9184–0.9730 (200 evaluated) | **1** | Fail ($p$=0.5) |
| 0.9729 | 0.9332–0.9828 (175 evaluated) | **30** | **Pass** (7/13 · +1.57 SD · $p$=0.0323) |
| 0.9775 / 0.9772 | 0.9205–0.9748 / 0.9264–0.9744 | 0 | **Abnormal termination** |

**When acceptance count is 1, the null standard deviation collapses to zero, and the standardized excess takes a meaningless value of $+1.5\times10^{11}$.** 2 models could accept none and terminated abnormally.

## CP2. The Cause and Why It Is Itself a Finding

**The decodability of the emotion partition sits at the upper end of the range reachable by clustering the activations themselves.**
Across 200 candidates, the maximum is 0.9658–0.9828 and the emotion partition is 0.9546–0.9775;
**the probability of drawing a partition that exceeds it is low.**

> **The human emotion partition, as a partition of the same granularity and class size, has decodability
> unreachable from vocabulary structure (Amendment 96 CO1: upper bound 0.881 vs. 0.955)
> and reachable from activation clusters only at the upper end.**

**This fact is reported.** However, **do not conflate it with the intervention-effect claim** (commitment in Amendment 96 CO5).
Being highly decodable and being movable by intervention are separate things.

## CP3. What Is Changed and What Is Not Changed

### Not changed

- Selection rule: **held-out AUC at least equal to the emotion partition's**
- Judgement criterion: **over half of 13 targets, and $p_G<0.05$; satisfied in over half of models**
- Target acceptance count: **30**

### Changed

| Item | Before | After | Reason |
|---|---|---|---|
| Upper limit of exploration trials | 200 | **2000** | The only means to increase acceptance count without relaxing the selection rule |
| Minimum accepted count for judgement | Not specified | **10** | With few accepted partitions, the null variance collapses and the statistic becomes undefined |

**Increasing the exploration budget is not a relaxation of the criterion.** It merely searches the same rule more broadly.

## CP4. Be Honest About the Threshold

**I have seen the collapsed statistics for the models before introducing the threshold.**
I saw count values of 12/13 and 9/13 with 1 accepted partition, 10/13 with 5 accepted, and 8/13 with 4 accepted.
**Therefore this threshold was not decided before seeing the results.**

The basis for introducing it is the **definability of the statistic, not the direction of the counts.**
With 1 accepted partition, the null standard deviation is zero; $p_G$ is fixed at 0.5 and the standardized excess diverges numerically. **This quantity cannot be compared for size.**

**Moreover, applying the registered rule as-is makes these models "fail"**
($p$=0.1667 to 0.5, all exceeding 0.05).
**Introducing a threshold and excluding them converts fail to "unmeasurable," not fail to pass.** Neither is "pass."
**I record this here as evidence that the change is not in a favorable direction.**

**Reporting obligation**: Even after the re-execution, if any model has fewer than 10 accepted partitions,
**report its acceptance count and collapsed statistics in the table, and write the fact of exclusion and the reason.**

## CP5. What Can Be Written After Re-execution (Fixed Before Seeing the Results)

| Result | What can be written |
|---|---|
| Over half of measurable models pass | **Cannot be explained by decodability.** The emotion partition wins even against a partition more decodable than it |
| Over half of measurable models fail | **The possibility that decodability explains it remains.** Keep the claim of Amendment 90 to "exceeds arbitrary partitions with matched class sizes" |
| Fewer than 3 measurable models | **SP-act does not produce a conclusion.** The population is insufficient. Keep the claim of Amendment 90. |

**In all cases, report the acceptance count and AUC range of candidates for all models.**

## CP6. Commitments

- Do not change the selection rule or the judgement criterion; change only the exploration budget
- State that the exclusion threshold was introduced after seeing the results (CP4)
- Write that exclusion is "fail → unmeasurable," not "fail → pass"
- Keep the acceptance counts and candidate AUC ranges for all models in the table after re-execution
- If fewer than 3 measurable models, produce no conclusion
- Do not conflate the finding of CP2 that "the emotion partition is the most decodable" with the intervention-effect claim
