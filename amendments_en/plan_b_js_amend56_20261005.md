# Pre-registration Amendment 56: Finalizing stimuli for general axes G-b and G-c (hash record) / Word-count control for G-c

**Created**: 2026-10-05
**Target**: General axes $\mathcal{G}$ (G-b, G-c) in amendment 54 BC3, non-emotion probes Q1–Q3 in amendment 46
**Status**: Finalization of stimuli and clarification of estimation procedure. **The criteria for judgements X4 and X5 are not changed.**
**Activation condition**: X4 and X5 must not be judged until this file has been committed and pushed.

---

## BE1. Finalization of stimuli

`03_解析/stimuli_general_axis/general_axis_pairs_20261005.json`

**sha256**: `9d6e2cde1559f53708b91bd8f750f326f4f3f8d2444afe1c9c8a1f6d3565d703`

| Concept | Family | Pairs | What was varied |
|---|---|---|---|
| Q1 Expectation deviation | G-b | 16 | Only the magnitude of deviation from expectation |
| Q2 Agency attribution | G-b | 16 | Only the agent (self / other, device, rule) |
| Q3 Certainty | G-b | 16 | Only modal auxiliaries (will / might, etc.) |
| C1 Refusal | G-c | 16 | Requests that should be answered / requests that should be declined |
| C2 Sycophancy | G-c | 16 | Neutral questions / requests to agree with an incorrect assertion |

Concept direction: $u_c = \mathrm{normalise}\big(\frac{1}{K}\sum_k [h(s^+_k) - h(s^-_k)]\big)$ (amendment 47 AV3).

**$\dim \mathcal{G} = 21 + 3 + 2 = 26$** (unchanged from amendment 54 BC3).

## BE2. Absence of emotion words was verified mechanically

All 160 sentences were checked against the 13 emotion categories, the 40 emotion words used in this study's stimuli group, general affect words (`feel/felt/feeling/emotion/emotional/mood/affect/affective/sentiment` and their derivatives with `-s/-ed/-ing/-ly/-ness`). **0 occurrences of contamination.**

**This check is mandatory.** In a study showing that general axes are upstream of emotion, using emotion words in the estimation of general axes would be circular. Since `felt` was overlooked once during the creation of E5, this is done mechanically rather than by visual inspection.

## BE3. Word-count confound in G-c, and its control (clarification of procedure)

Within-pair word-count difference (median / maximum):

| Concept | Median | Maximum |
|---|---|---|
| Q3 Certainty | **1.0** | 2 |
| Q2 Agency | 1.5 | 4 |
| Q1 Expectation deviation | 2.0 | 4 |
| **C1 Refusal** | **5.0** | 7 |
| **C2 Sycophancy** | **4.0** | 8 |

**G-c (refusal and sycophancy) does not have matched word counts.** Requests that should be declined versus requests that should be answered, and neutral questions versus requests to agree with an incorrect assertion, are inherently different in length due to the nature of the concepts.

**Control**: For the 2 directions in G-c, the variance explained by the surface statistics in amendment 49 AX1 (token count, word count, mean word length, punctuation count, capitalization rate, and mean and standard deviation of token IDs) is **removed before direction estimation**. Specifically, a regression is performed on the set of minimal-pair difference vectors $\{h(s^+_k) - h(s^-_k)\}$ with the surface-statistic differences of the same pairs as explanatory variables, the residuals are taken, and their mean is normalized to obtain $u_c$.

**This is not applied to G-a or G-b** (the within-pair word-count difference is a median of 1.0–2.0 words, and the same procedure is not mixed in). **This asymmetric treatment will be stated explicitly in the paper.**

## BE4. Limitations to be stated explicitly

- **Word-count control removes the word-count confound but does not remove the content difference.** Requests that should be declined also differ in content. Therefore, the direction carried by C1 may represent "content requiring refusal" rather than "refusal."
- **The 2 directions in G-c constitute 2 out of 26 dimensions of $\mathcal{G}$.** If the results of X4 depend on G-c, **X4 using only the 24 dimensions excluding G-c will also be reported alongside.**
- There is no independent means to validate the construct validity of Q1–Q3 and C1–C2 (human annotation is not used). The limitation that **it cannot be proven that the concepts are being manipulated as intended** will be written in the limitations section.

## BE5. Promises

- X4 and X5 will be judged after this file is pushed
- Stimuli will not be rewritten after seeing results. If they are rewritten, results from the old version will also be reported alongside
- The dimensional composition of $\mathcal{G}$ (21+3+2) will not be changed
- **X4 using the 24 dimensions excluding G-c will always be reported alongside**
- The limitations in BE4 will be written in the paper
