# Pre-registration Amendment 82: Defect in Readout Tokens (no-emotion Was Assigned to surprise) and Execution of the Synonym-Set Readout

**Created**: 2026-10-07
**Occasion**: Self-audit before submitting draft v3 to external review. Re-read the stage C code
**Judgement**: **The results of amendments 80 and 81 contain a defect. Draft v3 will not be submitted to external review until the corrected version has been executed.**
**Activation condition**: The corrected version must not be executed until this file has been committed and pushed.

---

## CA1. Content of the Defect (Implementation defect, 7th instance)

In the readout token construction for stage C (as well as stages B1s, B3, D, E5, and L), the following line appears:

```python
w = "surprise" if c == "no-emotion" else c
```

Among the 13 classes, `no-emotion` is not a single word, so the intent was to substitute an alternative word, but **the word substituted is `surprise`, which already exists as a separate class.** As a result, the token ID array `ids` for the readout **contains the same ID twice.**

### Consequences

1. **2 of the 13 targets (no-emotion and surprise) have the same readout by construction.** For any direction, $S_{\text{no-emotion}} = S_{\text{surprise}}$ holds
2. Therefore the count "exceeded $x$ out of 13 targets" is a count against **effectively 12 distinct targets**, not 13 independent ones
3. The `no-emotion` target is not measuring no-emotion; **it is measuring surprise**
4. The centering of the 13 coordinates ($T = I - \mathbf{1}\mathbf{1}^\top/13$) contains duplicate coordinates, so the centered values are also affected by the duplication

**This defect affects all results in amendments 80 and 81.** Because it affects all 9 models and all 4 families in common, the direction in which it systematically distorts the inter-family ordering cannot be identified, but **the fact that the denominator of the count and the meaning of the no-emotion target are incorrect** is certain.

### Inconsistency with Amendment 77 BZ5

Amendment 77 BZ5 registered `neutral, indifferent, unmoved, unaffected` as the `no-emotion` entry in the synonym-set readout (R-syn). This correct assignment is implemented in `stageL_prep.py`, but **had not been reflected in the single-token pathway** (line 138 of the same file also uses `surprise`). **The registered vocabulary and the implementation were inconsistent.**

## CA2. Second Problem: Only One Readout Type Has Been Used

Amendment 77 BZ8 contains the following commitment:

> If the conclusions from the two readout types do not agree, **neither conclusion is claimed**

Amendment 80 recorded the single-readout status as a limitation, but **no exemption from this commitment was registered.** Therefore the commitment remains in force. **Submitting draft v3's claims to external review without having executed R-syn violates this commitment.**

## CA3. Specifications of the Corrected Version (Fixed in this amendment. Defined before seeing results)

### Readout R-single′ (corrected version, single token)

The word substituted for `no-emotion` is changed to **`neutral`**. The other 12 classes are unchanged. Duplicate IDs are checked at runtime and an exception is raised if any are found.

### Readout R-syn (synonym set; uses the vocabulary registered in amendment 77 BZ5 exactly as registered)

The **sum of probabilities** of the 4 registered words for each class is taken. The leading token ID of each word is used, and **if an ID is duplicated across classes, that ID is removed from the set for that class.** If removal leaves any class with 0 words, an exception is raised.

```
anger: anger, angry, furious, enraged
boredom: boredom, bored, dull, tedious
disgust: disgust, disgusted, revolted, repulsed
fear: fear, afraid, frightened, scared
guilt: guilt, guilty, remorseful, contrite
joy: joy, happy, delighted, cheerful
no-emotion: neutral, indifferent, unmoved, unaffected
pride: pride, proud, accomplished, gratified
relief: relief, relieved, reassured, unburdened
sadness: sadness, sad, sorrowful, downcast
shame: shame, ashamed, humiliated, mortified
surprise: surprise, surprised, astonished, startled
trust: trust, trusting, confident, assured
```

### Statistics

**The family best vs. family best statistic fixed in amendment 80 is not changed at all.** Only the readout is changed. Floor F4 measured $N=60$ times, bootstrap the maximum of K resampled draws 2000 times, selection on sel contexts, scoring on held-out contexts, signed readout, $J^\ast = 0.05$. The K=13 adjusted subsample of 200 draws is also reported alongside.

### Scope

**All 9 models** (4 discovery cohort, 5 confirmation cohort) are measured with **both** R-single′ and R-syn. The criterion for degeneracy judgement (no family exceeds the individual direction floor p95 on even 1 target) is unchanged.

## CA4. Judgement (Fixed before seeing results)

| R-single′ | R-syn | What can be written |
|---|---|---|
| Emotion category exceeds the floor family best in a majority of models | Same | **The claim is made.** The result is independent of the readout |
| Exceeds | Does not exceed | **Neither conclusion is claimed** (amendment 77 BZ8). Readout dependence is reported |
| Does not exceed | Exceeds | Same. Neither conclusion is claimed |
| Does not exceed | Does not exceed | **The results of amendments 80 and 81 are recorded as having been obtained with a defective readout, and the claims are withdrawn** |

"Majority of models" refers to: among non-degenerate models, a majority satisfies "exceeds a majority of 13 targets." **The same threshold as amendment 81 is used and not moved.**

## CA5. Treatment of Amendments 80 and 81

**They are not withdrawn. They are preserved as a record.** The fact that the numbers in amendments 80 and 81 were obtained with a defective readout is made explicit in this amendment, and the results are **reported alongside** the corrected version. If any differences arise, those differences themselves are reported as "the effect of readout token construction on the conclusion."

**Draft v3 is frozen and will not be submitted to external review.** Draft v4, reflecting the corrected version's results, will be the external review version.

## CA6. Error in Draft v3 Description (Corrected Alongside)

Section 3.3 of draft v3 describes the readout as "the projection of the output change onto a human-derived contrast vector $c_e$ defined for each emotion category $e$," and $c_e$ as "constructed from the correlation between indicator variables and occurrence of each vocabulary item." **This is not the stage C implementation.** The stage C implementation takes the change vector in the next-token probability over 13 emotion words, centers it, and normalizes it to unit norm, taking the $e$-th component. **This is rewritten in v4 to match the implementation.**

## CA7. Commitments

- The corrected version's results are reported as-is regardless of whether they are consistent with amendments 80 and 81
- If the conclusions from the two readout types do not agree, **neither conclusion is claimed**
- Duplicate token ID checking is performed at runtime; an exception is raised if any are found
- Amendments 80 and 81 are not deleted; they are preserved with a note that they contain the defect
- This defect is recorded in Appendix B (record of implementation defects) as the 7th instance
- Draft v3 will not be submitted to external review until the corrected version's results are available
