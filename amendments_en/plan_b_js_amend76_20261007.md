# Pre-registration Amendment 76: Correction and Three-Level Framework — Decodability, Subspace Privilege, and Basis Privilege

**Created**: 2026-10-07
**Occasion**: External advice (2026-10-07, 2nd round)
**Role**: **Correction of errors in the draft and three-level decomposition of the judgement framework.** Existing judgement results are not changed.
**Activation condition**: L2 and L3 judgements must not be performed until this file has been committed and pushed.

---

## BY1. Correction — The Gradient Direction Is Not "Constructively Optimal"

In sections 3.5 and 5.3 of external-review draft v2, the gradient direction of the target readout was described as **"constructively optimal"** and **"the direction that locally moves that readout most."** **This is incorrect.**

With the Euclidean norm fixed, the gradient is the steepest ascent direction. However, **the present study fixes the JSD budget.** Under small perturbations,

$$\mathrm{JSD} \approx \tfrac12\,\Delta h^\top F\, \Delta h$$

introduces an output-side metric, so **the direction that maximizes efficiency under fixed JSD is in general $v^\* \propto F^{-1} g$ (the natural gradient direction), not the raw gradient $g$.**

**Correction**: The description of the gradient direction is weakened to **"the direction of steepest ascent under the Euclidean metric."** **The expressions "constructively optimal" and "moves most" are not used.**

**Its function as a positive contrast is preserved.** The fact that the gradient direction exceeds the floor shows that the readout responds to the intervention, thereby serving as a precondition. **However it is not used as an upper-bound claim.**

**Addition (if capacity permits)**: The Fisher-preconditioned gradient $F^{-1}g$ is measured as a **theoretically motivated upper-bound contrast.** $F$ is the softmax covariance of the next-token distribution, approximated via the Jacobian from the intervention layer to the output layer. The method of approximation will be stated explicitly if this is carried out.

## BY2. Three-Level Framework

The previous judgement was a single question: "does a direction exceed the floor?" **This is decomposed into three levels.**

| Level | Question | Contrast |
|---|---|---|
| **L1 Decodability** | Can that concept be linearly read out from internal representations? | — |
| **L2 Subspace privilege** | Is the subspace spanned by that family of concepts causally more effective than a **variance-matched random subspace of the same dimension**? | Random subspace |
| **L3 Basis privilege** | Within that subspace, are the individual axes named by humans **more special than an arbitrary rotated basis**? | **Random rotation within the same subspace** |

**The existing E5 results concern L3.** "The appraisal dimension axis does not exceed the floor" means only **"the human-defined appraisal basis is not privileged"** — it does not mean **"appraisal representations are not causal."**

The possibility remains that a direction rotated within the appraisal subspace,

$$z = \textstyle\sum_a \beta_a v_a,$$

is the true causal coordinate. **This possibility has not been excluded.**

## BY3. Limitation of Claims (Correction of Section 5.2 in Draft)

Draft v2 stated: "Appraisal theory assumes a causal path from appraisal to emotion. The present result does not support this path."
**This is too strong.**

**What can be negated is limited to the following hypothesis:**

> **Individual psychological appraisal dimensions are implemented in LLMs as independent linear causal levers.**

**Appraisal theory itself is not negated.** The possibilities of nonlinear implementation, combinations of multiple appraisals, and implementation in a different basis remain. **This limitation is stated explicitly in the main text.**

## BY4. Correction of Asymmetry in the Comparison

In draft v2, emotion category directions were learned from emotion labels and appraisal dimension directions were learned from appraisal labels, while **evaluation was conducted using the output change on 13 emotion words.** This is advantageous for the emotion directions.

**Response 1 — Adding an independent readout**: In addition to the 13 emotion words, a readout using **a synonym set for each emotion** is added. For example, joy uses `joy, happy, delighted, cheerful`.
**The synonym sets are fixed in this amendment and will not be changed after seeing results.**

**Response 2 — Adding raw appraisal directions**: The appraisal dimension directions in draft v2 were single-effect-isolated versions with projection onto other appraisal dimensions removed. **To exclude the possibility that the residualization degraded the effect, raw appraisal directions are also added to the family.**

**Response 3 — Replication of prior procedure**: The procedure of Tak et al. is applied as-is, and **the positive result is first shown to replicate under a whole-space floor.** The floor is then replaced with a variance-matched one. This excludes the interpretation that "the effect disappeared due to implementation changes."

## BY5. Correction of Output Perturbation Definition

Draft v2 called the JSD on the union of the top-100 tokens "global output perturbation." **This label is too strong.**

**Response**: JSD is computed for top-100, top-500, and the full vocabulary, and **the correlations are reported.** If the correlation exceeds 0.99, top-100 continues to be used and this fact is recorded. If not, **the full-vocabulary JSD is used instead.**

## BY6. Correction of the Unit of Replication

Draft v2 presented the results as "12 cells from 4 models × 3 budgets." **The 3 budgets are repeated measurements on the same model and do not constitute 12 independent replications.**

**Response**: **Models are reported as the unit of replication.** Consistency across budgets is shown as within-model auxiliary information. The expression "12 cells" is not used in the primary results.

## BY7. Comparison of Emotion Axis and Principal Component Axis

In draft v2, the emotion axis was 10/12, median $+4$, and the principal component axis was 9/12, median $+2$. **This difference is insufficient to conclude that "the emotion axis is more special than high-variance structure in general."**

**Response 1**: The emotion axis and the principal component axis are compared in a **paired comparison.** Pairs are formed by the same model, same budget, and same target.

**Response 2**: **F4 is brought to the fore as "a contrast that breaks only the semantic arrangement of emotions."** F4 preserves the multiset of principal coordinate magnitudes while breaking only the assignment and signs. The fact that the emotion axis exceeds F4 means that **what matters is the arrangement of coordinates, not the variance profile.**

**Response 3**: The scope of the claim is limited. Instead of writing "the emotion axis is privileged," it is written that **"the emotion axis is privileged over the variance-matched contrast."**

## BY8. Correction of Reporting Statistic

Draft v2 used the difference in the number of floor exceedances as the reporting statistic, but this was **a judgement made after looking at the absolute count per family.** The draft's conclusion stated that "all criteria were registered before execution," which **appears contradictory.**

**Response — Shift to continuous quantities and re-registration**: To avoid threshold dependence, the following two are used as the **primary reporting statistics:**

1. **Percentile rank in the null distribution** $q(v) = \hat F_{\text{null}}\big(S(v)\big)$
2. **Standardized excess** $E(v) = \dfrac{S(v) - \mu_{\text{null}}}{\sigma_{\text{null}}}$

Both are defined per direction and contain no threshold. **Bootstrap confidence intervals are reported alongside.**

**The difference in floor exceedance counts is reported as auxiliary.** It is not discarded.

## BY9. Confirmation Cohort

The 4 models on which E5 has already been executed constitute the **discovery and statistic-development cohort.** **The 5 models not yet executed are designated as the pre-registered confirmation cohort.**

| Cohort | Models |
|---|---|
| Discovery / statistic development | OLMo-2-7B / Gemma-2-9B / Llama-3.1-8B / Llama-3.2-1B |
| **Confirmation (results not yet seen)** | **OLMo-2-13B / Gemma-2-2B / Phi-3-medium / Ministral-8B / Mistral-Nemo-12B** |

**The results of the confirmation cohort are not examined before this amendment and amendment 77 are pushed.** Phi-3-medium belongs to the same family as Phi-3.5-mini and may be degenerate; **if degenerate, it is excluded from the judgement count on grounds of failing E5-pre, and this fact is reported.**

## BY10. Commitments

- The gradient direction is not written as "constructively optimal." It is written as the direction of steepest ascent under the Euclidean metric
- L3 results are not written as L2 results. "Appraisal representations are not causal" is not written
- The negated hypothesis is limited to "individual psychological appraisal dimensions are implemented as independent linear causal levers"
- Raw appraisal directions and single-effect-isolated directions are **both reported**
- The positive result under a whole-space floor is **first replicated using the prior procedure**
- Correlations by JSD vocabulary range are reported
- Models are reported as the unit of replication. 12 cells are not treated as independent replications
- The privilege of the emotion axis is qualified as "over the variance-matched contrast"
- Continuous statistics are primary; the difference in floor exceedance counts is auxiliary and reported alongside
- **The results of the confirmation cohort are not examined before pushing**
