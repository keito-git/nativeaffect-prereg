# Pre-Registration Amendment 101: Second Encoding Vocabulary Is Undecidable — Only 2 Models Pass the Validity Check

**Created**: 2026-10-14
**Target**: Amendment 99 CR2 (Test CE-2 · codebook 3 = digits and symbols / codebook 4 = its transpose)
**Judgement**: **No judgement is made.** Only 2/5 models passed the validity check for both codebooks, which does not reach the minimum population of 3 registered in Amendment 92 CK2.
**Order**: This amendment is written, committed, and pushed **at a point when the statistics for codebooks 3 and 4 have not yet been computed even once.** This is to leave no room to move the population or threshold after seeing the numbers.

---

## CT1. Validity Check Results (Same Threshold as Amendment 91 CJ1: at least 7/13 with AUC>0.5, and median AUC ≥ 0.65)

| Model | Codebook | AUC>0.5 | Median AUC | Mode match | Judgement |
|---|---|---|---|---|---|
| Gemma-2-9B | 3 | 12/13 | 0.703 | 3/13 | Pass |
| Gemma-2-9B | 4 | 13/13 | 0.787 | 3/13 | Pass |
| Mistral-Nemo-12B | 3 | 13/13 | 0.727 | 1/13 | Pass |
| Mistral-Nemo-12B | 4 | 13/13 | 0.733 | 3/13 | Pass |
| Llama-3.1-8B | 3 | 11/13 | 0.607 | 1/13 | **Fail** (median) |
| Llama-3.1-8B | 4 | 10/13 | 0.564 | 2/13 | **Fail** (median) |
| Ministral-8B | 3 | 12/13 | 0.546 | 2/13 | **Fail** (median) |
| Ministral-8B | 4 | 9/13 | 0.598 | 1/13 | **Fail** (median) |
| OLMo-2-13B | 3 | 10/13 | 0.574 | 1/13 | **Fail** (median) |
| OLMo-2-13B | 4 | 13/13 | 0.568 | 2/13 | **Fail** (median) |

**Pass on both codebooks = 2 models (Gemma-2-9B and Mistral-Nemo-12B).**

## CT2. Judgement

Under the rule of Amendment 92 CK2, **when the population is fewer than 3 models, test CE produces no conclusion.**
The population is 2, so **test CE-2 is not judged.**

**The threshold is not lowered.** "Median 0.65" was set in advance in Amendment 91, in response to the failure of readout B (in which a negative result became uninformative at AUC 0.56).
**The median of the 4 models that now fail ranges from 0.546 to 0.607 — exactly the same band as readout B.** Moving the threshold here would defeat the very purpose of Amendment 91.

## CT3. What Can Still Be Written (These Are Results)

1. **Codebooks using digits and symbols are harder to execute than codebooks using single-character letters.**
   For codebooks 1 and 2, all 5 of 5 models passed the validity check; for codebooks 3 and 4, only 2 did.
2. **Even in the 2 models that passed, execution quality drops substantially.** Mode match was 13/13 for both Gemma-2-9B and Mistral-Nemo-12B with codebook 1, but is only 1/13–3/13 for codebooks 3 and 4.
   AUC exceeds the criterion, but the most frequent prediction is almost never correct.
3. **Therefore the generality of Gate III's conclusion could not be confirmed by extension to a different vocabulary.**
   The limitation "only one type of re-encoding" **does not diminish**. The reason it does not diminish is not "because it was not measured" but "because readout is not executable"; this is worth recording.

## CT4. What to Write in the Body Text

- That a second encoding vocabulary (digits and symbols) was pre-registered and measured
- That only 2 of 5 models passed the validity check for both codebooks, **failing to reach the minimum population registered in advance, so no judgement is made**
- That the numbers for failing models (median AUC and mode match) are **shown without deletion**
- That the limitation "only one type of re-encoding" has not been resolved

**What must not be written**: "Attenuation also reproduced with a different vocabulary" or "not dependent on encoding vocabulary."
Since no judgement was made, neither can be written.

## CT5. Handling of Statistics for Codebooks 3 and 4

Since the population is insufficient, they are not used in the judgement, but **descriptive statistics are computed and recorded**
(consistent with the commitment in Amendment 100 CS6: "report numbers and reasons without deletion").
**The computation is performed after this amendment is pushed.** They are not presented in the body text as judgements.

## CT6. Commitments

- Do not change the threshold, minimum population, or codebooks after seeing the results
- Do not read "undecidable" as "attenuation reproduced"
- Do not drop the numbers for the 4 failing models
