# Pre-registration Amendment 40: Remove vocabulary bias not by elimination but by measurement and subtraction — use layer 0 as a vocabulary baseline

**Target**: Amendment 38 (main series of cross-model common components) and the analysis specification for stimulus set E5
**Created**: 2026-10-04
**Status**: Does not change the judgements M1–M4 of Amendment 38. This is a supplement that **adds one control term to the analysis**.
**Activation condition**: No analysis using E5 shall be treated as a confirmed value unless this file has been committed and pushed beforehand.

---

## AO0. The problem to be solved

Stimulus E4 is a template with only one emotion word replaced, and it cannot answer the criticism that "we are only measuring the token representation of an emotion word." E5 was redesigned with situational descriptions that exclude emotion words, but a red-team review (conducted 2026-10-03) pointed out the following:

> LLMs are also sensitive to the cultural narrative patterns in the training corpus. **The level of abstraction merely rose one step from words to scenarios; the structure of the problem is the same.**

E5 was redesigned as a grid of scenario skeletons × categories (fixing the skeleton and varying only the ending), with the word-count range within a skeleton compressed to 1.3 words and the average non-shared words in the ending compressed to 7.2 words. **Even so, the vocabulary difference is not zero.**

**The policy of this amendment: do not try to eliminate the vocabulary difference; measure it and subtract it.**

## AO1. Use layer 0 as the vocabulary baseline

The **layer 0 (output of the embedding layer) of the same model** is used as the control.

| | Has | Does not have |
|---|---|---|
| Layer 0 | Word identity, token representation, position | Transformer's contextual computation |
| Layer $L$ | Word identity + **contextual computation** | — |

Because it is the same model, same tokenizer, and same space, the comparison is perfectly aligned, with no need to bring in an external embedding.

**Claims are stated incrementally.**

> Only the part of the categorical structure observed at layer $L$ that exceeds what is already observed at layer 0 is the structure contributed by the model's contextual computation.

## AO2. Why this control is essential

**Paper 1 reports that "subspace separation already exists at layer 0."** That is, a substantial portion of the emotional structure is explained by word identity alone. To report the categorical structure of layer $L$ without subtracting layer 0 is equivalent to reporting vocabulary statistics as properties of internal representations.

This control is therefore not supplementary but **essential**. Conversely, the claims in prior work that does not include this control cannot be distinguished from vocabulary statistics.

## AO3. Estimator and judgement

We write the strength of categorical structure as $\mathrm{CS}(\ell)$, defined by comparing categories within a skeleton (differences between skeletons are removed as fixed effects).

$$\mathrm{CS}(\ell) = \frac{\text{Mean inter-category distance within skeleton}}{\text{Mean intra-category distance within skeleton}}$$

Distance is cosine distance after standardization.

The **increment** is defined as $\Delta \mathrm{CS}(L) = \mathrm{CS}(L) - \mathrm{CS}(0)$.

- **L1**: $\Delta \mathrm{CS}(L) > 0$, and exceeds the 95th percentile of the **null** with random category assignment (label permutation within skeleton, 500 iterations). If it does not, the categorical structure of layer $L$ is explained by the vocabulary structure of layer 0, and **no further claims based on E5 will be made**.
- **L2**: If L1 is satisfied, all subsequent analyses in Amendment 38 (identification of components, correspondence with the human framework, cross-model sharing) are performed **on the residual representations with layer 0 subtracted**.

## AO4. Apply the same control to E4

The same analysis is applied to E4 (direct emotion word writing). The predictions are as follows, and are written **in advance**.

- In E4, $\mathrm{CS}(0)$ is large (emotion words themselves are present at layer 0).
- In E5, $\mathrm{CS}(0)$ is small (no emotion words).
- **If $\Delta \mathrm{CS}(L)$ is comparable for both**, the structure contributed by the model's computation does not depend on whether emotion words are present, which empirically validates the E5 design.
- **If $\Delta \mathrm{CS}(L)$ is small only for E5**, there is a possibility that the E5 stimuli are too weak, and we return to the stimulus design.

This comparison is made **without knowing the results at the time of this amendment**. We report whichever way it goes.

## AO5. Remaining limitations (to be stated explicitly in the paper)

Layer 0 controls for word identity but **does not control for prior probabilities at the scenario level**. The pattern "negative result after treatment → joy narrative" can exist across both the vocabulary representations at layer 0 and the computation at layer $L$.

Therefore, what this study can claim is only **"not explained by word-level vocabulary statistics"**, and not **"we are measuring the content itself."** Following the recommendation in the red-team review, this limitation will be stated explicitly in the Limitations section.

## AO6. Promises

- No analysis result using E5 will be treated as a confirmed value unless this file has been committed and pushed beforehand.
- The definition of $\mathrm{CS}$ and the construction of the null will be fixed in this file and will not be changed after seeing the results.
- Both E4 and E5 will be reported; only one will not be selected for reporting.

---

## AO7. Correction (2026-10-04 — identified while running P1)

**"Layer 0 carries word identity," as stated in AO1, does not hold for the final-token readout.**

In the first run of P1, `rank90` for layer 0 of E4 became NaN. The cause is not an implementation error but a property of the readout position.

All 80 sentences of E4 end with `...about this situation.` or similar, and **the final token is the same for all stimuli**. Layer 0 is the embedding layer, so the representation at the final token position is the embedding of the period itself, which **carries no information about the sentence**. The contrast between categories becomes exactly zero, all singular values become 0, and NaN arises.

E5 does not become exactly zero because the endings differ, but it is still **only the embedding of the last one word**, and does not function as a vocabulary baseline.

### Correction content

**Change the layer 0 representation from the final token to the mean of all token embeddings (mean pooling).** This is a bag-of-words in the model's own space, which retains word identity while not including Transformer computation. This is what AO1 intended as the control.

The readout of layers $L$ (11/16/22/27) remains the final token as before. This is the position where the intervention acts, and it is aligned with other measurements in this series of studies.

### Handling the different readout positions

Since layer 0 and layer $L$ use different readout positions, the increment $\mathrm{CS}(L) - \mathrm{CS}(0)$ does not separate "contribution of computation" from "difference in readout position." **This limitation will be stated explicitly in the paper.**

As a supplementary measure, the same quantity will be measured for layer $L$ using mean-pooled representations as well, providing a position-matched comparison. If the conclusions do not agree between the two, **neither conclusion will be claimed**.

### Lesson

**Before using a baseline, confirm not only what it does not contain, but also what it does contain.** We confirmed at design time that layer 0 does not contain computation, but **did not confirm that it actually retains word identity**. We noticed because NaN appeared, but in a case like E5 where a non-zero value appears, a meaningless number could have been reported as though it were meaningful.
