# Pre-registration Amendment 86: The Readout Is Self-Consistent. Reformulating as a Symmetric 2×2 Design

**Created**: 2026-10-08
**Occasion**: Reconsidering critique 4 (circularity) from the external review led to discovery of a deeper asymmetry
**Judgement**: **The current design is asymmetric as a comparison between families. The comparison between families is not claimed until the symmetric 2×2 has been executed.**
**Activation condition**: Judgements must not be performed until this file has been committed and pushed. **Has never been executed.**

---

## CE1. Location of the Asymmetry

The current design is as follows:

| Direction family | Estimation target | Evaluation readout |
|---|---|---|
| Emotion category | 13 emotion category indicator variables | Next-token probability of **13 emotion words** |
| Appraisal dimension | Continuous values of 21 appraisal dimensions | Next-token probability of **13 emotion words** |

**The emotion family is evaluated with a readout that matches its learning target, and the appraisal family is evaluated with a readout that does not match.** The fact that directions estimated to separate emotion labels move emotion word probabilities carries almost no claim about representations.

> "Emotion axis +3.2 SD, appraisal axis +0.2 SD" — as long as the readout is emotion categories, **this contrast can be explained by the match between the estimation target alone.**

The R-act (behavioral verbs) from amendment 85 breaks the **vocabulary** circularity, but the readout remains **13 emotion categories.** The appraisal family is still required to move "a readout that does not match it." **The asymmetry is not resolved by R-act alone.**

## CE2. Symmetric 2×2 Design

A second readout is prepared, and each family is also evaluated **with a readout that matches its own target.**

| | Readout A (emotion words) | **Readout B (appraisal adjectives, newly added)** |
|---|---|---|
| **Emotion category axis** | Self-consistent | Cross |
| **Appraisal dimension axis** | Cross | **Self-consistent** |

For each cell, the floor is the F5 from amendment 83 (matched per target by exact eigenvalue match), and the statistic is $G$ from amendment 84.

### Specifications of Readout B (Fixed in this amendment)

Frame:

```
Event: {text}

The event was
```

Readout: next-token probability of the following 12 words. Leading token rule from amendment 84 is used; duplication raises an exception.

| Appraisal dimension | Adjective | Appraisal dimension | Adjective |
|---|---|---|---|
| suddenness | sudden | predict_conseq | foreseeable |
| familiarity | familiar | urgency | urgent |
| predict_event | predictable | self_control | controllable |
| pleasantness | pleasant | accept_conseq | acceptable |
| unpleasantness | unpleasant | social_norms | normal |
| goal_relevance | important | chance_responsblt | accidental |

**Excluded 9 dimensions**: `self_responsblt`, `other_responsblt`, `goal_support`, `other_control`, `chance_control`, `standards`, `attention`, `not_consider`, `effort`. **Reason: No single adjective that fits "The event was ___" exists** (responsibility and attention attribution are not adjectives that describe the event). **The exclusions are not changed after seeing results.**

**The direction family uses all 21 dimensions.** The readout having 12 targets and the family having 21 directions are separate matters.

### Validity Check for Readout B (Performed Before the Judgement)

Since appraisal dimensions have continuous values, a stronger check than R-act is available. For each dimension $a$, stimuli from crowd-enVENT are divided into 2 groups by the median of the rating, and **in the unintervened state** it is checked whether the probability of the corresponding adjective is higher in the high-rating group.

**Requiring that the high-rating group is higher for a majority of the 12 dimensions.** If not satisfied, readout B is not used and the fact is recorded. **The adjective table is not rewritten to improve results.**

## CE3. Judgement (Fixed before seeing results)

Judged by $p$ of $G$. Threshold 0.01.

| Emotion axis → A | Appraisal axis → B | What can be written |
|---|---|---|
| Exceeds | **Does not exceed** | **The asymmetry is real.** The emotion category family functions as a causal coordinate system, but the human appraisal dimension family fails **even with a readout that matches itself.** This cannot be explained by the match of the estimation target |
| Exceeds | **Exceeds** | **The contrast between families is not claimed.** Both families move their own readout. The current "only emotion axis exceeds" is an artifact of the choice of readout |
| Does not exceed | Exceeds | Unexpected. Reported as-is |
| Does not exceed | Does not exceed | Suspect the readout design. No claim is made |

**The cross cells (emotion axis → B, appraisal axis → A) are reported as auxiliary.** If the emotion axis moves the appraisal readout in the cross condition, the emotion axis has a broader causal role.

**The comparison between families is claimed only if (i) is obtained.** In the case of (ii), the manuscript's claim is reduced to the standalone fact that "the emotion category axis exceeds the matched floor," and **no claim is made about superiority or inferiority relative to the appraisal dimension.**

## CE4. What This Design Does Not Answer

- The catalog of categories (13 emotions, 21 appraisals) is human-derived in both cases. "Whether this categorization is privileged" is a different question and is not answered by this design
- Both the adjective table and the verb table are **mappings I constructed** and are not independently validated. The CE2 check confirms their validity but does not guarantee correctness. **This is written as a limitation in the main text**
- Readout B has 12 targets, covering only part of the 21 dimensions. Nothing is said about the excluded 9 dimensions

## CE5. Scope and Order of Execution

```
① Validity check for readout B (all 9 models)              ← CE2
② Measurement of readout B (all 9 models, families: emotion and appraisal_raw, floors: F5/F4)
③ 2×2 judgement (CE3)
```

Executed independently from R-act in amendment 85. **Since readout A results are already available, the 2×2 is complete once ② is ready.** Raw measurements are saved to `raw_<tag>_app.npz`.

## CE6. Commitments

- The adjective table and the 9 excluded dimensions are not changed after seeing results
- The validity check in CE2 is performed before the judgement and results are reported
- **In the case of (ii), the contrast between families is not claimed.** The fact that it was an artifact of the readout choice is recorded
- Cross cells are also reported
- The fact that the mappings were constructed by me is stated as a limitation
- **The inter-family contrast currently written in the manuscript — "only the emotion axis exceeds, the appraisal axis does not" — is not claimed until ② and ③ of this amendment are complete**
