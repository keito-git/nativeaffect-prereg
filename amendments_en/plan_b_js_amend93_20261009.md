# Pre-Registration Amendment 93: Test CE Fails. The Effect Is Bound to Encoding.

**Created**: 2026-10-09
**Target**: Test CE in Amendment 91 CJ1 (re-encoding under the same ontology), and the judgement population from Amendment 92
**Judgement**: **Fail. Among the 5 population models, pass count is 0 across both codebooks.
An effect that satisfies variance-matched, exploration-width-matched, and label-matched conditions does not replicate under a different encoding of the same ontology.**
**Trigger condition**: Do not submit v5 for external peer review until this file is committed and pushed.

---

## CL1. Results (Population 5 models from Amendment 92 · floor F5)

| Model | Codebook | Median AUC | Mode match | Count | Excess SD | $p_G$ | Judgement |
|---|---|---|---|---|---|---|---|
| Mistral-Nemo-12B | 1 | 0.771 | **13/13** | 6/13 | +1.47 | 0.0005 | Fail |
| Mistral-Nemo-12B | 2 | 0.806 | **13/13** | 3/13 | +0.91 | 0.0100 | Fail |
| gemma-2-9b | 1 | 0.897 | **13/13** | 1/13 | +0.98 | 0.0030 | Fail |
| gemma-2-9b | 2 | 0.903 | **13/13** | 1/13 | −0.03 | 0.4703 | Fail |
| OLMo-2-13B | 1 | 0.746 | 11/13 | 2/13 | +0.32 | 0.3823 | Fail |
| OLMo-2-13B | 2 | 0.718 | 10/13 | 1/13 | −0.02 | 0.3029 | Fail |
| Llama-3.1-8B | 1 | 0.677 | 6/13 | **0/13** | +0.52 | 0.2534 | Fail |
| Llama-3.1-8B | 2 | 0.654 | 6/13 | 2/13 | +0.44 | 0.0360 | Fail |
| Ministral-8B | 1 | 0.680 | 5/13 | 2/13 | −0.09 | 0.0045 | Fail |
| Ministral-8B | 2 | 0.662 | 1/13 | 2/13 | +0.29 | 0.0005 | Fail |

**Population median excess SD: +0.38 (range −0.09 to +1.47); median count: 2.0/13 (range 0 to 6).**
Readout A yielded +3.17 SD · 10.5/13.

**The figures for the 4 out-of-population models are also recorded** (Llama-3.2-1B, OLMo-2-7B, Phi-3-medium, and gemma-2-2b all yielded counts of 1–3/13). The reason for exclusion is the inability to retrieve their codebooks; they are not deleted.

## CL2. Cannot Be Explained by Readout Quality

**This is important.** The negative result of readout B could be explained by the low resolution of AUC 0.56.
**Test CE cannot be explained in the same way.**

gemma-2-9b and Mistral-Nemo-12B can **fully retrieve the codebook**
(mode match 13/13, AUC 0.897 and 0.771). Yet the affect direction moves the code readout only slightly (count 1/13 and 6/13, excess SD −0.03 to +1.47).
**The readout is tracking the target, but the intervention does not follow.**

## CL3. What Can Be Written

**A strong effect (+3.17 SD, 9/9 models) that clears a floor with matched variance profiles, exploration width, and partition origin drops to +0.38 SD merely by replacing the output representation with an opaque code while keeping 13 categories intact.**

This reproduces what Gao et al. showed regarding choice identifiers — "following the extraction index" —
**in the affect domain and under a variance-matched floor.**
**This shows that their finding also applies to effects that have passed a strong control.**

## CL4. What Cannot Be Written

- "The affect direction controls nothing." **It does control.** It exceeds both the variance-matched floor and the label-matched partition over affect-word readout (4.2 and 4.7).
- "LLMs have no affect representation." This study does not ask whether representations exist.
- Conclusions about the 4 out-of-population models. The test cannot be constituted because the codebook cannot be retrieved.

## CL5. On Framing (Principal investigator instruction, 2026-10-09)

The principal investigator instructed: "Negative content is fine, but the claims should appear positive."
**The handling of data does not change.** What changes is **the order in which what was established is presented.**

**Content that can be presented positively (all based on measurement)**

1. **We proposed a three-layer control hierarchy and demonstrated its discriminating power.**
   Layer 1 = variance-matched (F5, strict matching with eigenvalues), layer 2 = partition-matched (LP), layer 3 = encoding-matched (CE).
   **The same direction clearly passes layers 1 and 2 and fails at layer 3.**
   The hierarchy is neither vacuous nor uniformly destructive; measurement demonstrates this.
2. **We identified the locus of the affect steering effect.** Rather than "it does not work," this is the localization: **"it lives at the interface of output encoding."**
3. **We quantified the value of human affect labels.** For control over affect-word output, the value is +3.17 SD against the strictly-matched floor; all 30 of 30 cells across all models exceeded the label-matched partition. **The labeling effort is justified within that scope.**
4. **We provided a practical judgement criterion.** For applications where the output is the affect label itself (classification, tagging, moderation), this method is valid. For applications requiring semantic control over full generated text, **verification of encoding invariance is necessary**, and this study provides the test.
5. **The method as F5.** A floor that preserves per-term variance contributions with eigenvalues can be applied post-hoc to existing intervention studies, and it also yields as a by-product the structural fact that no matched floor exists in principal component directions.

**Prohibition**: Do not use the change in presentation order above to conceal negative results.
**The table in CL1, the fail judgements, and the population reduction must be stated explicitly in the abstract and results section.**
When writing "localization of the locus," always write "fell at layer 3" in the same paragraph.

## CL6. Commitments

- Report the fail result of test CE as-is and write it in the abstract
- Keep the figures and exclusion reasons for the 4 out-of-population models in the table
- State explicitly that the failure cannot be explained by readout quality (CL2), and **distinguish it in kind from the negative result of readout B**
- Do not use the positive presentation order (CL5) to conceal negative results
- State the priority of Gao et al. explicitly; limit this study's contribution to "empirical demonstration that their finding also applies to effects that have passed a strong control"
