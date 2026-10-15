# Pre-Registration Amendment 74: Results of E5 — The Positive Control Passes for the First Time, and E5a Does Not Hold.
# Emotion Category Axes Are Efficient; Appraisal Axes Cannot Be Distinguished from the Floor

**Created**: 2026-10-06
**Target**: Judgement E5 in Amendment 73
**Judgement**: **E5-pre holds. E5a does not hold.** As per the commitment in Amendment 73 BV6, H1 is revised for intervention efficiency.
**Run**: Llama-3.2-1B (L12). Extension to other models is underway.

---

## BW1. Results (Llama-3.2-1B, $d$=2048, 3 Budgets)

The number of targets for which the held-out-context efficiency exceeds the 95th percentile of the floor is shown. The floor values themselves are those of the best direction selected from 21 on selection contexts and evaluated on held-out contexts, containing selection-induced upward bias.

| Family | $J^\*$=0.02 | 0.05 | 0.10 |
|---|---|---|---|
| **e Gradient directions (positive control)** | **13/13** | **13/13** | **13/13** |
| **a Emotion category directions** | **12/13** | **12/13** | **12/13** |
| c Principal component directions | 7/13 | 8/13 | 9/13 |
| d Variance-matched random (floor, own selection best) | 3/13 | 8/13 | 5/13 |
| **b Appraisal dimension directions** | **3/13** | **2/13** | **3/13** |

## BW2. E5-pre Passed for the First Time

**The gradient directions are 13/13 across all 3 budgets.** This is the **first judgement in this research series where the positive control clearly passed**.

In Amendments 58, 59, and 61, the Warriner valence direction was used as a positive control and failed to reach the floor in 3 of 4 models, with unmeasurable judgements continuing. **The cause was not the bluntness of the readout but the choice of the positive control.** A direction obtained by regressing onto valence norms is not optimal for moving the emotion category output. Because the gradient direction is constructionally the one that moves that readout the most, the prerequisite was resolved.

**This correction is explicitly stated in the paper.** The previous unmeasurable judgements were not limitations of the measurement system but design defects in the control.

## BW3. E5a Does Not Hold

Amendment 73 BV6 registered the following.

> **E5a**: The held-out efficiency of human axis families (a) and (b) does **not exceed** the 95th percentile of floor (d) for the majority of targets.

**Because emotion category directions exceeded the floor in 12/13, E5a does not hold.** **As committed, H1 is revised for intervention efficiency.** That is:

> **Human emotion category axes are privileged in terms of intervention efficiency.** **On the other hand, human appraisal dimension axes cannot be distinguished from the variance-matched floor.**

**Only the convenient side is not written.** H1 is not unconditionally maintained.

## BW4. Negating Circularity (Premise for the Claim)

The emotion category direction $w_e$ is a ridge regression from activations to predict human labels, and the gradient direction $g_e$ is the direction that most increases the output probability of the same emotion word. If the model is accurate, both may align, so the possibility that family (a)'s efficiency is merely a paraphrase of family (e) was verified.

| | Value |
|---|---|
| Chance level $\lvert\cos\rvert$ ($d$=2048) | 0.0221 |
| **$w_e$ with the corresponding $g_e$** | **Median 0.1526** (min 0.0216, max 0.1761) |
| $w_e$ with a non-corresponding $g_{e'}$ | Median 0.0168 |
| Appraisal dimension → gradient (maximum from 21) | Median 0.0819 |
| PC → gradient (maximum from 21) | Median 0.1595 |

**$\lvert\cos\rvert = 0.15$ is far from 1, and family (a) is not a paraphrase of the gradient.** On the other hand, since the corresponding pair is approximately 9 times the non-corresponding pair, $w_e$ has a direction specific to that emotion.

**The asymmetry of the comparison is explicitly stated.** The values for appraisal dimensions and PCs are the maximum from 21 directions, a counting method more advantageous than the 1-to-1 correspondence of emotion directions. Even so, PCs remain at 0.1595 and floor exceedance is 7–9/13. **Gradient alignment alone cannot explain the ordering of efficiency.**

## BW5. Relationship to Prior Work

| | Prior work | This result |
|---|---|---|
| Intervention on appraisal dimensions | The emotion of the output moves as expected theoretically (Tak, Banayeeanzade, Bolourani, Kian, Jia, Gratch, Findings of ACL 2025) | **When output perturbation is equalized and a variance-matched floor is placed, does not exceed the floor** |
| Emotion category directions | Not verified as a target | **Exceeds the floor** |

**The causal path from appraisal to emotion assumed by appraisal theory is not supported under this measurement.** On the other hand, **emotion categories themselves have coordinates directly connected to the output.**

**Not written as a denial of prior work.** Written as **the identification of boundary conditions**: it was an observation dependent on the strength of the control.Appendix B's final accounts table shows, alongside, the consistent observation of this research series that things pass under a full-space floor and do not pass under a variance-matched floor.

## BW6. A Single Model Is Not Conclusive

**This result is from Llama-3.2-1B only.** An additional 5 models (OLMo-2-7B, Gemma-2-9B, Mistral-Nemo-12B, Phi-3.5-mini, Llama-3.1-8B) are being run.

**The judgement criteria remain unchanged from Amendment 73.** If the ordering changes with additional models, **it is reported as model-dependent, as-is.**

## BW7. Hypothesis Update (Revising H1 from Amendment 72)

H1 from Amendment 72 is replaced with the following.

> **H1′**: Of the human emotional description frameworks, **appraisal dimensions are** not privileged computational units in the model's interior. **Emotion category axes are privileged in terms of intervention efficiency.**

**This divergence itself is a result.** The wholesale claim "human concepts are not privileged" does not hold; **it is necessary to separately state which human concepts are privileged and which are not.**

H2 and H3 are maintained as unverified. However, **the motivation for H2 changes.** If emotion category axes are efficient, the motivation for searching for model-native computational modes is no longer "because human axes do not work," but becomes **"whether coordinates more efficient than emotion category axes exist."**

## BW8. Commitments

- The non-holding of E5a is recorded as-is, and H1 is revised. H1 is not unconditionally maintained
- The fact that the previous positive control failures were design defects in the control is explicitly stated
- The asymmetry of the comparison used in negating circularity is explicitly stated
- If the ordering changes with additional models, it is reported as model-dependent
- Prior work is not written as a denial; it is written as the identification of boundary conditions
- **H2's motivation is not written as "because human axes do not work"**
