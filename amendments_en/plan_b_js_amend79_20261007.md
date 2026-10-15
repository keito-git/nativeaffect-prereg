# Pre-registration Amendment 79: The Retraction in Amendment 78 Was Premature. The Difference in Comparison Target Is the Cause; the E5 Statistic Is the Correct One for Claims About the Family

**Created**: 2026-10-07
**Targets**: The retraction in amendment 78, E5 conclusion from amendment 75
**Judgement**: **The statement "the E5 conclusion does not replicate" in amendment 78 is corrected.** The failure to replicate occurs **only when the comparison target is relaxed.**
**Activation condition**: Recalculation judgements must not be performed until this file has been committed and pushed.

---

## CB1. Diagnostic Results (Llama-3.2-1B, $J^\*=0.05$, 8 conditions)

| Condition | Appraisal F1 | Appraisal F4 | Emotion F4 | Principal component F4 |
|---|---|---|---|---|
| Raw / full vocabulary / with separation ★ | 10/13 (+2.11) | **10/13 (+2.51)** | 13/13 (+3.65) | 12/13 (+2.01) |
| Raw / full vocabulary / without separation | 10/13 (+2.11) | 10/13 (+2.57) | 13/13 (+3.65) | 12/13 (+2.08) |
| Raw / top-100 / with separation | 11/13 (+2.18) | 10/13 (+2.55) | 13/13 (+3.75) | 13/13 (+2.08) |
| Raw / top-100 / without separation | 11/13 (+2.18) | 10/13 (+2.59) | 13/13 (+3.75) | 13/13 (+2.11) |
| Residualized / full vocabulary / with separation ★ | 7/13 (+1.69) | **8/13 (+1.80)** | 13/13 (+3.65) | 12/13 (+2.01) |
| Residualized / full vocabulary / without separation | 8/13 (+1.90) | 8/13 (+2.00) | 13/13 (+3.65) | 12/13 (+2.08) |
| Residualized / top-100 / with separation | 7/13 (+1.67) | 7/13 (+1.50) | 13/13 (+3.75) | 13/13 (+2.08) |
| Residualized / top-100 / without separation | 8/13 (+1.75) | 7/13 (+2.08) | 13/13 (+3.75) | 13/13 (+2.11) |

**The only factor that matters is residualization.** Raw: 10/13, $+2.5$ SD; residualized: 7–8/13, $+1.8$ SD. **The JSD vocabulary range and selection separation have almost no effect.**

**The floor hierarchy is flat.** The pass count barely changes between F1 and F4. The "approximately twice" of amendments 73 and 75 **does not replicate in the present measurement.**

## CB2. The Retraction in Amendment 78 Was Premature

Amendment 78 stated "the E5 conclusion does not replicate." **This is corrected.**

The absolute counts for E5 and stage D are **consistent.**

| | Appraisal (residualized) | Emotion |
|---|---|---|
| E5 (amendment 75) | 2–7/13 | 10–13/13 |
| Stage D (present measurement) | 7–8/13 | 13/13 |

**What differs is the comparison target.**

| | Comparison target for the appraisal axis |
|---|---|
| **E5** | **Best of 21 selected from the floor family** (strict) |
| Stage D | 95th percentile of the distribution of individual floor directions (lenient) |

In E5, the selected best of the floor itself reached 3–12/13, exceeding the appraisal axis's 2–7/13, so the difference became negative. **Stage D does not give selection to the floor, so only the family side receives the selection advantage.**

## CB3. The E5 Comparison Is the Correct One for Claims About the Family

As long as the question is "**is this family of concepts causally more effective than a random family of the same size?**," **the same selection advantage must be given to both the family and the floor.**

The stage D comparison gives selection to the family but uses the distribution of individual directions for the floor. **Therefore stage D is lenient, and the E5 statistic is the correctly designed quantity.**

**The judgement in amendment 75 BX2 to use the difference from the floor rate as the reporting statistic was correct.** Questioning this in amendment 78 was an error.

## CB4. Recalculation with the Correct Comparison (Following Procedure of Amendment 77 BZ3)

From $N_{\text{floor}} = 40$ measured floor values, $K$ are resampled with replacement and the maximum is taken; this operation is repeated 2000 times, constructing **the distribution of "best of a random family."** $K$ is matched to the number of directions in the family being compared.

**Judgement CMP**: The number of targets for which the effect of the selected best direction from the family, evaluated on held-out contexts, exceeds the 95th percentile of the distribution of the best of a random family constitutes a majority.

**This judgement is applied to all four families: raw appraisal directions, residualized appraisal directions, emotion directions, and principal component directions.** Because the number of directions differs per family, **the resampling count from the floor is matched to each family** (appraisal: 21, emotion: 13, principal component: 21).

**The same comparison is also recalculated for F1 and F4 to address the floor hierarchy.**

## CB5. Interpretation of Results (Fixed in Advance)

| Raw appraisal directions | Residualized appraisal directions | What can be written |
|---|---|---|
| Does not exceed | Does not exceed | **The E5 conclusion is reinstated.** The appraisal axis cannot be distinguished from a random family |
| **Exceeds** | **Does not exceed** | **The conclusion differs depending on whether residualization is applied.** Neither is chosen; an analysis of what residualization is removing is written |
| Exceeds | Exceeds | **The E5 conclusion was incorrect.** The appraisal axis exceeds a random family |
| Does not exceed | Exceeds | Unexpected. Reported as-is |

**The same comparison is applied to the emotion directions and principal component directions, and the ordering is reported.**

## CB6. On the Floor Hierarchy

Amendments 73 and 75 reported "even with output perturbation matched, F3 and F4 floors are approximately twice F1." **This does not replicate in stage D.**

**Identifiable points of difference**

| | Amendments 73 and 75 | Stage D |
|---|---|---|
| Readout | **Magnitude** of JS divergence in the distribution of 13 emotion words | **Signed projection** onto a human-defined contrast |
| Evaluation of floor | Distribution of individual directions | Same |
| Direction family | Residualized appraisal directions | Both raw and residualized |

**The "twice" was observed with the magnitude readout.** It is flat with the signed readout. **This difference is identified and reported.** The C1 of Paper 2 is a measurement under a different readout, different stimuli, and different axes, and **does not directly contradict the present measurement**, but **the fact that the floor hierarchy changes depending on the readout is written in the paper.**

## CB7. Commitments

- The fact that the retraction in amendment 78 was premature is preserved in the record. **The retraction of the retraction is not concealed**
- The fact that the E5 statistic is the correctly designed quantity for claims about the family is stated explicitly
- The fact that stage D's comparison is lenient is stated; stage D numbers are not deleted
- All four cases of CB5 are reported regardless of which occurs
- The fact that the "twice" was observed with the magnitude readout and is flat with the signed readout is reported
- The fact that the finding does not contradict Paper 2 is confirmed, and the readout dependence is written
- **External review submission is withheld until this recalculation is completed**
