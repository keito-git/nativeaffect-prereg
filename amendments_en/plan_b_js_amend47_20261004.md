# Pre-registration Amendment 47: Characterising components by proximity to human concepts — fixing the list of reference concepts in advance

**Created**: 2026-10-04
**Status**: A **supplement** to Amendment 38 Stage 5 (AM6 naming discipline) and Amendment 46 (operational definition of higher-orderness). The existing judgements M1–M4 and H-A–H-C are not changed.
**Activation condition**: The matching of components with human concepts must not be performed until this file has been committed and pushed. The results of Stage 1 (M1) have not been obtained at the time of creating this file.

---

## AV0. Additional request from the principal investigator (2026-10-04)

> What humans call emotion is, for AI, a fusion of different concepts. It would be good to be able to make that claim. **It would be even better if we could go further and say: those concepts, in human terms, are close to this and that.**

The claim that "humans have not conceptualised" it was removed from the goals in Amendment 46 AU0. This amendment instead establishes a procedure to **actively characterise components by their proximity to human concepts**.

**This is a stronger result than claiming the unknown.** A description of the form "component $Z_1$ is close, in human concepts, to \<expectation violation\> and \<agency\>, and is not close to \<valence\>" is verifiable and gives substantive content to the reader.

## AV1. The problem to be solved: concept names must not be assigned to obtained components opportunistically

Stating "this looks like expectation violation" after obtaining a component is a post-hoc interpretation and does not constitute evidence. **The list of human concepts to be matched must be fixed before the components are seen.**

## AV2. List of human concepts (16 items; confirmed in this file, no additions thereafter)

Each concept is operationalised using **minimal pairs** (pairs of stimuli differing only in the concept in question). Human annotation is not used.

### Family A: Psycholinguistic norms (using existing public norms; only those already on hand)

| # | Concept | Source (file on hand) |
|---|---|---|
| A1 | valence | `warriner_2013_en_vad.csv` |
| A2 | arousal | same |
| A3 | dominance | same |
| A4 | concreteness | `norare/fr/Bonin-2018-Concreteness.csv` and others |
| A5 | sensorimotor | `norare/it/Repetto-2023-Sensorimotor.csv` |

**A1–A3 are the human emotion frameworks themselves that this research uses as a reference.** They are included in the list in order to show that components are not close to these (Amendment 38 M2).

### Family B: Concepts corresponding to appraisal dimensions

These correspond to dimensions of appraisal theory, but **this research does not aim to test appraisal theory.** They are used as a list of concepts that humans possess.

| # | Concept | How to construct minimal pairs |
|---|---|---|
| B1 | deviation from expectation | change only the degree of deviation (shared with Amendment 46 Q1) |
| B2 | attribution of agency | swap the agent (shared with Amendment 46 Q2) |
| B3 | degree of certainty | change only the modal auxiliary (shared with Amendment 46 Q3) |
| B4 | controllability | change only whether the subject can alter the outcome |
| B5 | intentionality | change only whether the act is deliberate or accidental |
| B6 | goal congruence | change only whether the act helps or hinders an explicitly stated goal |
| B7 | norm violation | change only whether the act is socially permissible |
| B8 | severity of outcome | change only the magnitude of the consequence |

### Family C: Events and social structure

| # | Concept | How to construct minimal pairs |
|---|---|---|
| C1 | temporal perspective | change only whether it has already happened or is about to happen |
| C2 | animacy | change only whether the affected object is a person or a thing |
| C3 | social presence | change only whether the subject is alone or others are present |

**The list is fixed at 16 items (A5+B8+C3). No additions or deletions will be made after seeing the results.**

## AV3. Estimator for matching

Let $z_i^{(m)}$ denote the direction recovered into the activation space of each model via the anchor for component $Z_i$. For concept $c$, given the set of minimal pairs $\{(s^+_k, s^-_k)\}$, the concept direction is estimated as

$$ u_c^{(m)} = \mathrm{normalise}\Big(\frac{1}{K}\sum_k \big[h_m(s^+_k) - h_m(s^-_k)\big]\Big) $$

**Proximity** is defined as $|\cos(z_i^{(m)}, u_c^{(m)})|$ averaged across models.

**Null**: A concept direction constructed by randomly flipping the $\pm$ labels of the minimal pairs (500 repetitions). **Multiple testing**: Corrected for **Benjamini–Hochberg FDR 0.05** across 16 concepts × number of components.

**Handling of norm families (A1–A5)**: Because norms are word-level, the norm value averaged over the words in the stimulus is used as the stimulus score, and $u_c$ is the regression direction onto the score. **The coverage rate of the norms will be reported, and concepts with coverage below 50% will be excluded from matching** (the fact of exclusion will be written).

## AV4. Judgement

**Judgement N1 (adoption of description)**: For component $Z_i$, if at least 1 concept is significant after FDR correction, **the combination of top concepts** is adopted as the description of $Z_i$.

**Judgement N2 (confirmation; AM6 discipline)**: A prediction is derived from the adopted description and confirmed using **newly created stimuli made independently**. If the description is "Z_i is close to expectation violation and agency," **a new set of pairs differing only in degree of expectation violation** and **a new set of pairs differing only in agency** are created, and the responsiveness of $Z_i$ is tested for conformity with the predicted ordering. **Descriptions that fail are discarded and not written in the paper.**

**Judgement N3 (reporting of no-description)**: A component for which no concept is significant after FDR correction is **reported as "not close to any human concept in this list."** This will not be concealed. The limitation that the list is restricted to 16 items will be explicitly stated.

## AV5. Form of claims that can be made

For components that pass N1+N2, the writable sentence takes the following form:

> What humans call emotion categories is constructed as a mixture of components shared across models. Those components are close, in human concepts, to \<$c_1$\> and \<$c_2$\>, and **are not close to the emotion frameworks used in this research (valence, arousal, dominance, and emotion vocabulary categories).**

**"Humans have not conceptualised it" will not be written** (Amendment 46 AU0). For N3 components, the statement will go no further than "not close to any concept in this list," and **it will not be written that they are unknown concepts.**

## AV6. Prior art check (mandatory before making claims)

It is likely that prior research exists addressing the appearance of appraisal dimension structure in language model representations. **Before writing "first" or "novel," verify by full-text search.** The novelty language will not be used until verification is complete.

- Research reporting that appraisal theory dimensions appear linearly in LLM internal representations
- Research reconstructing emotion categories as a mixture of appraisal dimensions
- Research applying relative representation to identify cross-model components in emotion

**Prior work by the authors must also be checked** (Paper 1, Paper 2, the TAC submission on referent-controlled readout).

**Smith & Ellsworth (1985) Table 1 has not been verified in the original text** (noted following a literature check). When citing it, do not write a specific list of appraisal dimensions in the main text until the original is obtained and confirmed.

## AV7. Promises

- Matching will be performed after this file is pushed
- The 16-item list is fixed and will not be changed after seeing the results
- When minimal pair stimuli are created, their hash will be appended to this file
- Only descriptions that pass N2 confirmation will be adopted. Failed descriptions will not be written
- N3 (components that are not close to any concept) will be reported without concealment
- Novelty will not be claimed until prior art has been confirmed
