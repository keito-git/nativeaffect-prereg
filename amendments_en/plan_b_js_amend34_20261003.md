# Pre-registration Amendment 34: Control R negated H3. Experiment X is cancelled; Paper 3 will be written as a methodology paper.

**Target**: Amendment 33 AH1–AH3 (principal investigator hypothesis H3 and Experiment X)
**Created**: 2026-10-03
**Judgement**: **H3 is withdrawn. Experiment X will not be run.** The termination condition in Amendment 33 AH3 was triggered.

---

## AI1. What was measured (as in Amendment 33 AH2)

**Control R**: Token sequences drawn uniformly from the vocabulary. Length distribution was matched to E1 discovery half (E1 min/med/max = 4/17/37 tokens; Control R = 4/18/41). Special tokens and added vocabulary excluded. Seed 20261003. 144 stimuli.

`g1_jacobian.py` was supplied with these via `--stimuli-file`, obtaining 10 sensitivity directions per layer for layers 11, 16, 22, and 27 using exactly the same procedure as emotion-derived and math-derived (self-check PASS, 12.1 hours, approx. 30 min per layer).

**Pre-specified judgement rule (Amendment 33 AH2)**:

> If the agreement between Control R and the emotion-derived subspace is comparable to that between math-derived and emotion-derived, then the agreement in AG2 is a property of weight geometry that does not depend on stimulus content. In that case, AG2 will be rewritten as "top Jacobian directions are a property of the layer," and H3 will be withdrawn.

## AI2. Results: Control R agrees as well as or better than math-derived

Mean squared canonical correlation. Null: random 10-dimensional subspaces, n=500 (mean 0.0024, p95 0.0030, matches theoretical value 10/4096 = 0.00244).

| Layer | emo × math | emo × Control R | math × Control R | Null ratio (emo×math) | Null ratio (emo×R) |
|---|---|---|---|---|---|
| 11 | 0.1767 | 0.1611 | 0.0724 | 72.5× | 66.1× |
| 16 | 0.1037 | 0.0818 | 0.0098 | 42.5× | 33.5× |
| 22 | 0.0930 | **0.1653** | 0.0243 | 38.2× | **67.8×** |
| 27 | 0.1938 | **0.3436** | 0.0809 | 79.5× | **140.9×** |
| Mean | 0.1418 | **0.1880** | | | |

**Control R exceeds the null p95 greatly in all 4 layers (33–141×).**
**Moreover the mean exceeds math-derived (0.1880 vs. 0.1418, ratio 0.75).** At layers 22 and 27, Control R's agreement is clearly higher.

### Confirming no degeneration (before accepting the result)

If Control R's subspace is degenerate, the comparison is meaningless; confirmed first.
`flat_spectrum_warning` and `degenerate_plane_warning` are **False for all layers and all origins.**
Eigenvalue ratio w10/w1 for Control R is 0.2883–0.4020, comparable to emotion-derived 0.2481–0.3717 and math-derived 0.2104–0.2880. **Control R is a valid comparison target; the result is not an artifact of degeneration.**

## AI3. Judgement: H3 is withdrawn

**Sensitivity directions constructed from random token sequences agree with those from emotional sentences at tens to hundreds of times the null.** Since this occurs with stimuli carrying no content, the "domain-independent agreement" observed in Amendment 33 AG2 is **a property of the layer's weight geometry, not a property of stimulus content.**

As registered, rewrite as follows:

- **Reading of Amendment 33 AG2**: "sensitivity subspace is common regardless of domain of origin" →
  **"the top singular subspace of the layer Jacobian is a property of the layer that barely depends on input content"**
- **H3 (concepts that generalize across AIs)**: **Withdrawn.** It has been shown to be domain-independent within a model, but that invariance is explained by weight geometry. Extending to across models would face the same confound and would not constitute evidence for the hypothesis
- **Experiment X (cross-model agreement of sensitivity subspaces)**: **Will not be run.** Following the termination condition of Amendment 33 AH3.

## AI4. Current status of the principal investigator's hypothesis (updating the table in Amendment 33 AH0)

| | Proposition | Judgement |
|---|---|---|
| **H1** | Directions effective for control lie outside the human framework | **Partially supported.** Sensitivity directions are nearly orthogonal to the top-10 principal components (mean\|cos\| 0.017–0.038, random expected value 0.0125). However "outside the human framework" can only be claimed to the extent of "not variance directions" |
| **H2** | Combine to produce emotional effects | **Unmeasured.** No design for it |
| **H3** | Generalizes across AIs | **Withdrawn** (this amendment) |
| **H4** | Can be controlled by intervention | **Supported.** 99 out of a unique 140 exceed the floor (70.7%) |

**The hypothesis as a whole is not supported.** H4 holds, but H4 alone is close to the tautological claim "high-output-sensitivity directions move the output," and with H3 dropped, the pillar supporting the interpretation "those are AI-native concepts" is gone.

## AI5. The positive value of this negation

This control provides the reason why the 2×2 in Amendment 32 AF3 showed "diagonal and off-diagonal equivalent."

**If the top directions of the layer Jacobian barely depend on input content, it is natural that swapping the domain of origin does not change δ_a.** The domain effect failing to appear in the 2×2 was not a design failure or power shortage; it was because the quantity being measured is a quantity that does not depend on domain.

This does not weaken the methodological proposition of Paper 3; it **provides mechanistic underpinning.**

> Selecting directions by output sensitivity exceeds the floor not because those directions carry semantic content, but because
> **they are directions along which the layer is sensitive regardless of input.**

Combined with the fact that 0 out of 80 principal-component directions exceed the floor (Amendment 32 AF4), the claim of Paper 3 is confirmed in the following form:

> **What determines steerability is not what a direction means, but whether the way of selecting the direction picks up the layer's sensitivity structure.** Variance (principal components) does not. Activity reproducibility (ICA) barely does.
> Output sensitivity (Jacobian) does. And what it picks up is not meaning or domain but a property of the layer.

## AI6. Policy going forward

- **Paper 3 will be written with the methodological proposition of Amendment 32 AF5.** It will not be written as a proof of the principal investigator's hypothesis
- **Experiment X will not be run.** GPU is best used next on Experiment A layers 22 and 27 (emo×emo, closing the 2×2 across 4 layers). Requires a decision by the principal investigator
- H2 (combination) cannot be measured with the current research group's design. A new pre-registration is needed if it is taken up as a separate study
- **Control R results will be included in the main text of Paper 3.** "Top Jacobian directions are a property of the layer" is an independent observation of value, and simultaneously it precisely locates the limitations of this study

## AI7. For the record

**This control was registered and run after a result supporting the hypothesis had appeared, specifically in order to refute that result.**
The 38–80× agreement in Amendment 33 AG2, seen without a control, would have appeared as strong evidence for H3.
Without the registered order of running Control R first (Amendment 33 AH3), the same confound would have been reached after investing days of GPU on the cross-model experiment.
