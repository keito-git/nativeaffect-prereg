# Pre-Registration Amendment 70: Toward Discovery — Identifying Directions That Carry Emotion Attribution and Describing Them with Human Concepts

**Created**: 2026-10-06
**Principal investigator policy**: 2026-10-06 "No audit paper. Use a separate route to partially show that emotion is based on other concepts"
**Status**: **New primary line**. Existing judgements are not changed.
**Activation condition**: No judgement must be made until this file has been committed and pushed. **Never run once.**

---

## BS1. Changing the Form of the Claim

As recorded in Amendment 69 BR5, four routes failed in the same pattern. All of them took the form of **"X is more special than a control matching variance and information content."** **It was confirmed 4 times that this form does not pass with any control. The form of the claim is changed.**

**"Whether it is special" is not asked. Directions exist. What is asked is "in human terms, what is it?"**

## BS2. Stage 1: Extracting Directions That Carry Emotion Attribution

From the standardized representations $\tilde X$ (training-row statistics), obtain the weight matrix $W \in \mathbb{R}^{d \times 13}$ from a ridge regression of the one-hot vectors for 13 emotion categories ($\lambda$ selected by inner partition).

The left singular vectors $u_1, \dots, u_r$ of the singular value decomposition $W = U \Sigma V^\top$ (in descending order of singular value) are used as **emotion-identification directions**.

**Method for determining dimensionality $r$ (fixed as a rule)**: The minimum $m$ such that the emotion decoding macro-F1 under the top $m$ vectors reaches **95% of the full representation**. $m$ is not changed after seeing results.

## BS3. Stage 2: Matching Against 30 Human Concepts

| Family | Concept | How the direction is constructed |
|---|---|---|
| Appraisal (21) | 21 dimensions of crowd-enVENT | Stage A probe $v_a$ ($R^2$ 0.2–0.65) |
| Norm (3) | valence / arousal / dominance | Regression onto stimulus means of Warriner lexicon (coverage 5900/6600) |
| Event / Social (6) | Expectation violation / agency / certainty (Amendment 56)<br>Temporal perspective / animacy / social presence (this amendment) | Mean of minimum-pair differences |

**Stimuli confirmed in this amendment**: `03_解析/stimuli_general_axis/family_C_pairs_20261006.json`
**sha256**: `41a70861c3ca99f87f4aa2b0116eaf5a80375bfbb6fd55fc7d6d50b4bc9f2f10`

Zero emotion words (96 sentences, machine-verified including derivatives. `affect` and its derivatives are also treated as affect words and excluded). **C2 has the first 3 words in common across all 16 pairs**, with only the animacy of the affected target varying (machine-verified).

### Excluded Concepts and Reasons (Not for Convenience)

| Concept | Reason |
|---|---|
| Concreteness / sensorimotor | **No English lexicon is available** (English norms only have V/A/D. Bonin is French, Repetto is Italian) |
| Controllability / intentionality / goal congruence / norm violation / severity of consequences | **Substantially included in the 21 dimensions of crowd-enVENT** (`self_control`, `other_control`, `chance_control`, `goal_support`, `standards`, `social_norms`, `accept_conseq`). Creating separate minimum pairs would be redundant |

**Changes from the 16-concept catalogue in Amendment 47 are explicitly stated.** The catalogue had 16 concepts, but the appraisal family was replaced with actual data directions in 21 dimensions, and 2 concepts without lexicons were excluded. **This change is made before seeing the results.**

## BS4. Estimators and Judgements

The proximity between emotion-identification direction $u_j$ and concept direction $w_c$ is $\lvert\cos(u_j, w_c)\rvert$.

**Null**:
- Concepts from minimum pairs: Concept directions constructed by randomly flipping the sign of pairs (500 trials)
- Concepts from appraisal/norm: Directions fit after permuting the target variable (500 trials)

**Multiple testing**: **Benjamini–Hochberg FDR 0.05** for $m$ directions × 30 concepts.

**Judgement N1 (adoption of description)**: If at least 1 concept is significant for direction $u_j$ after FDR correction, the top concept is adopted as the description of $u_j$.

**Judgement N3 (no description)**: A direction with no significant concepts is reported as **"not close to any human concept in this catalogue."** **"Not conceptualized by humans" is not written** (Amendment 46 AU0).

**Cross-model**: Run independently for 10 models, and **whether the same concept is assigned to the same direction is reported.** If inconsistent, that is written.

## BS5. Stage 3: Confirmation of Description (Rules from Amendment 38 AM6)

From the descriptions adopted in N1, predictions are formed and confirmed with **newly created stimuli**. For example: if the description of direction $u_1$ is "animacy," **new pairs differing only in animacy** are created, and whether the projection onto $u_1$ follows the predicted ordering is tested.

**Descriptions that fail to pass are discarded and not written in the paper.**

## BS6. The Form of the Claimable Proposition (Fixed in Advance, Regardless of Results)

> Of the $m$ directions that linearly carry the model's emotion attribution, $u_1$ corresponds to ⟨$c_1$⟩, $u_2$ to ⟨$c_2$⟩ (FDR 0.05, consistent in $k$ out of 10 models). **What constitutes the linear structure of emotion attribution is not emotion categories themselves but these concepts.**

**If appraisal concepts match**: This is a replication of prior work (appraisal theory), and **novelty is not claimed** (Tak et al. 2025, Amendment 48). However, **which appraisal dimensions rank highest is new information** and is reported.

**If event/social family matches**: This is a correspondence not explained by the appraisal theory framework, and **novelty can be claimed.** In that case too, only what passed Stage 3 confirmation is adopted.

**If nothing matches**: Reported as N3.

## BS7. Limitations (Written in Advance)

- **This is a claim about linear structure, and does not include what is carried nonlinearly**
- **This is a representational claim, not a causal claim.** Controlling through intervention has not been established in this research series (V1″ confirmation set not held)
- **The catalogue is limited to 30 concepts.** "Not close to any catalogue item" does not mean "unknown concept"
- The method for estimating concept directions differs by family (regression / minimum-pair difference). **This asymmetry is explicitly stated**

## BS8. Commitments

- Judgements are made after this file is pushed
- The non-holding of X1 is corrected as "an error in the question," and **the results of X1 are not hidden**
- The method for determining $m$ (95% of full representation) is not changed after seeing results
- FDR correction is performed; pre-correction significance is not reported
- Directions with no description (N3) are not hidden
- Descriptions that do not pass Stage 3 confirmation are not written in the paper
- If appraisal concepts match, **novelty is not claimed**
- The 2 excluded concepts and the changes from the Amendment 47 catalogue are written as-is
