# Pre-Registration Amendment 67: Decomposing the Model's Appraisal Code into the Part Explainable by Human Ratings and the Residual, and Asking Which Carries Emotion

**Created**: 2026-10-06
**Principal investigator policy**: 2026-10-06 "If this works out, turn it into a paper for now, then use a separate route and external advice to fully verify the hypothesis"
**Status**: **New primary line** (following judgement S in Amendment 66). Existing judgements are not changed.
**Activation condition**: No judgement must be made until this file has been committed and pushed. **Never run once.**

---

## BP1. Observation (Revealed During Execution of Amendment 66, 4 Models)

| Model | Full representation | **21 appraisal dimensions** | Top 21 PCs | Random 21 dims p95 | **21 human ratings** | Ratio |
|---|---|---|---|---|---|---|
| OLMo-2-13B | 0.7434 | 0.5709 | 0.6904 | 0.5364 | **0.3230** | **1.77×** |
| OLMo-2-7B | 0.7502 | 0.5847 | 0.6692 | 0.5293 | 0.3230 | **1.81×** |
| Gemma-2-2B | 0.7484 | 0.5749 | 0.6447 | 0.5457 | 0.3230 | **1.78×** |
| Gemma-2-9B | 0.7469 | 0.6130 | 0.6650 | 0.6017 | 0.3230 | **1.90×** |

**Judgement S did not hold** (S2: inferior to top PCs; S3: retention rate 0.77–0.82 < 0.90). **This is reported as-is per the commitments in Amendment 66.**

**However, under the same conditions, the model's 21 appraisal estimates predict emotion labels approximately 1.8 times better than 21 human ratings.** 21 numbers vs. 21 numbers, same target, same classifier family, chance level 0.077.

**The model's appraisal directions were obtained by regressing onto human appraisal ratings.** Despite this, the predictions are better than human ratings, which means **the model's appraisal code carries information that human ratings do not have; it is not a copy of human appraisal concepts.**

## BP2. Question

> **Of the model's appraisal code, is it the part corresponding to human appraisal concepts, or the residual beyond it, that predicts emotion?**

## BP3. Decomposition (Fit on Training Rows Only)

For evaluation rows, let the model's appraisal estimates be $\hat A = \tilde X Q_a$ ($Q_a$ is an orthonormal basis of $\mathrm{span}(V)$, 21 dimensions), and let the human ratings be $Y$ (21 dimensions).

**Using training rows**, regress $\hat A$ onto $Y$ (with intercept, ridge, $\lambda$ selected by inner partition) to obtain coefficients $B$. For evaluation rows,

$$ \hat A^{\text{fit}} = [\mathbf{1}, Y]\,B, \qquad \hat A^{\text{res}} = \hat A - \hat A^{\text{fit}} $$

**The coefficients of $Y$ are not fit on evaluation rows at all.**

## BP4. Estimators and Judgements

The 13-emotion-family macro-F1 is measured with the same classifier (ridge, $\lambda$ selected by inner partition).

| Symbol | Features |
|---|---|
| $F_{\hat A}$ | 21 model appraisal estimates (same as $F_{\text{app}}$ in Amendment 66) |
| $F_{\text{fit}}$ | The part explainable by human ratings $\hat A^{\text{fit}}$ (21 values) |
| **$F_{\text{res}}$** | **Residual $\hat A^{\text{res}}$ (21 values)** |
| $F_{Y}$ | Human ratings $Y$ themselves (21 values; same as $F_{\text{human}}$ in Amendment 66) |

**Judgement R**:
- **R1**: $F_{\text{res}} > F_{\text{fit}}$ (the residual predicts emotion better)
- **R2**: $F_{\text{res}} > F_{Y}$ (the residual predicts better than human ratings themselves)
- **R3 (soundness)**: $\lvert F_{\text{fit}} - F_{Y} \rvert < 0.05$ (the $Y$-derived part should be comparable to $Y$ itself; if it deviates greatly, the decomposition is broken)

**Judgement R is supported when all of R1, R2, and R3 are satisfied for the majority of the 10 models**.

**Quantities also reported** (not used in the judgement):
- The proportion of variance in $\hat A$ accounted for by $\hat A^{\text{fit}}$ (to check whether the residual is merely dominant in variance)
- $R^2$ of regressing $\hat A$ onto $Y$ for each evaluation dimension (how well the model's estimates reproduce human ratings)

## BP5. Claimable Proposition (If R Passes)

> Although the model's appraisal code was obtained by regressing onto human appraisal ratings, **what contributes to predicting emotion categories is not the part explainable by human ratings but the residual beyond it.** That is, what the model uses when constructing emotion is **not the human appraisal concepts themselves.**

**This is a testable partial form of "the concept of emotion is based on other concepts."**

**Limitations to be reported alongside**:
- **What the residual is cannot be determined by this judgement.** Matching against the 16-concept catalogue in Amendment 47 will be done, but if it does not come close to any of them, the result is only "not close to any human concept in this catalogue," and **"not conceptualized by humans" is not written** (Amendment 46 AU0)
- **This is a representational claim, not a causal claim.** Controlling through intervention has not been established under a variance-matched floor (V1″ not held)
- **The appraisal code is inferior to top PCs as a 21-dimensional code** (judgement S, S2 not held for 10/10). "The appraisal code is the best 21-dimensional code" is not written
- The residual is "the part not linearly explainable by human ratings," and **the possibility of nonlinear explanation is not excluded.** This limitation is explicitly stated

## BP6. If It Fails

- **If R1 fails** ($F_{\text{fit}} \ge F_{\text{res}}$): What carries emotion is the part corresponding to human appraisal concepts. **This is a replication of prior work (appraisal theory) and has no novelty.** In that case, Paper 3 is written in the methodological framing of Amendment 64
- **If R3 fails**: The decomposition is not functioning. No judgement is made

## BP7. Commitments

- The non-holding of judgement S (S2, S3) is **reported as-is**. It is not overwritten by judgement R
- The criteria for R1, R2, R3 are not changed after seeing results
- The variance proportion of the residual is reported alongside, and **if it is merely dominant in variance, that is written**
- "The possibility of nonlinear explanation" is stated explicitly as a limitation
- If R fails, the framing reverts to the methodological framing. **The criteria are not loosened to force a pass**
