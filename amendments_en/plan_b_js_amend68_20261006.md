# Pre-Registration Amendment 68: Judgement R Is Supported 10/10. Registering Controls That Ask Whether the Residual Is Specific to the Appraisal Subspace

**Created**: 2026-10-06
**Target**: Judgement R in Amendment 67
**Judgement**: **R is supported 10/10.** However, **whether the residual is specific to the appraisal subspace is unverified.**
**Activation condition**: The control judgement must not be made until this file has been committed and pushed. **The controls have never been run once.**

---

## BQ1. Results of Judgement R (10/10 Supported)

| Model | $F_A$ | $F_{\text{fit}}$ | $F_{\text{res}}$ | $F_Y$ | $R^2$ for $A{\sim}Y$ | Variance proportion of fit |
|---|---|---|---|---|---|---|
| Ministral-8B | 0.6275 | 0.3259 | **0.4769** | 0.3230 | 0.492 | 0.484 |
| Phi-3.5-mini | 0.6134 | 0.3257 | **0.4758** | 0.3230 | 0.546 | 0.540 |
| Gemma-2-9B | 0.6130 | 0.3241 | **0.4620** | 0.3230 | 0.492 | 0.485 |
| Phi-3-medium | 0.6118 | 0.3253 | **0.4450** | 0.3230 | 0.563 | 0.568 |
| Mistral-Nemo | 0.5955 | 0.3259 | **0.4427** | 0.3230 | 0.517 | 0.512 |
| Llama-3.2-1B | 0.5803 | 0.3257 | **0.4247** | 0.3230 | 0.442 | 0.435 |
| Llama-3.1-8B | 0.5693 | 0.3249 | **0.4148** | 0.3230 | 0.457 | 0.446 |
| (OLMo-2 7B/13B, Gemma-2-2B also similar shape) | | ≈0.325 | 0.41–0.47 | 0.3230 | | |

**R1, R2, R3 all 10/10.**

**Soundness is particularly strong**: $F_{\text{fit}}$ is 0.3241–0.3259, with a difference from $F_Y = 0.3230$ of **within 0.003**. The part of the model's appraisal code explainable by human ratings **exactly recovers the emotion prediction information of human ratings and no more**. The decomposition is functioning as intended.

**Cannot be explained by variance**: The variance proportion of fit is 0.44–0.57, so **the residual has only about half the variance**, yet its decoding is 1.3–1.5 times higher.

## BQ2. A Missing Control — Is the Residual Specific to the Appraisal Subspace?

**This is what reviewers will invariably ask.** Whether the residual predicts emotion well is

- **(X) A property specific to the appraisal subspace**, or
- **(Y) A property that holds for any 21-dimensional subspace**

In Stage S, the raw decoding of random 21 dimensions was 0.47–0.59, which is close to the appraisal code (0.57–0.63). **(Y) is a practical possibility.**

**If (Y), the primary claim of this result shrinks to "human appraisal self-reports are weak predictors of emotion labels."** That is also worth reporting, but **it is no longer a claim about the model's appraisal code.**

## BQ3. Control Design (Fixed Before Seeing Results)

The same decomposition (regress $Y$ on training rows → fit and res) is applied to **21-dimensional subspaces other than the appraisal subspace**.

| Symbol | Subspace | Role |
|---|---|---|
| $F_{\text{res}}^{\text{app}}$ | Appraisal subspace $\mathrm{span}(V)$ | Primary (already obtained) |
| **$F_{\text{res}}^{\text{rand}}$** | **Random 21 dimensions (200 trials)** | **Primary control** |
| $F_{\text{res}}^{\text{pc}}$ | Top 21 principal components | Secondary control (most information-rich 21-dimensional code) |

**Judgement Q**:

- **Q1**: $F_{\text{res}}^{\text{app}} > F_{\text{res}}^{\text{rand}}$ 95th percentile
- **Q2**: $F_{\text{res}}^{\text{app}} / F_{\text{fit}}^{\text{app}}$ exceeds the 95th percentile of $F_{\text{res}}^{\text{rand}} / F_{\text{fit}}^{\text{rand}}$ (**measured as a ratio**; since raw values depend on the subspace's information content, specificity is measured by "how much the residual exceeds the fit")

**Q holds for the majority of the 10 models if both Q1 and Q2 are satisfied**, and **the residual is specific to the appraisal subspace**.

**Null soundness** (revised Amendment 57 BF2): The random control distribution is non-degenerate.

## BQ4. Claims Depending on Results (Both Written in Advance)

**If Q passes**:

> In the model's appraisal code, the component that carries the prediction of emotion categories is **the component not explained by human appraisal ratings, and this is specific to the appraisal subspace** (does not hold for same-dimensionality random subspaces).

**If Q fails**:

> Of the model's appraisal code, the component explained by human ratings is **informationally equivalent to human ratings themselves** (0.325 vs. 0.323, 10 models), and the unexplained component predicts emotion better. **However, this is a property that holds generally for 21-dimensional subspaces and is not specific to the appraisal code. Therefore, this result shows that human appraisal self-reports are weak predictors of emotion labels, and is not a claim about the properties of the model's appraisal code.**

**If it fails, the claim is written as "shrunk." The criteria are not loosened to force a pass.**

## BQ5. If Q Passes, the Next Step (Only Registered in This Amendment)

The directions in the residual are matched against the **16-concept catalogue in Amendment 47** (judgements N1–N3). **If they do not come close to any, the result is only "not close to any human concept in this catalogue," and "not conceptualized by humans" is not written** (Amendment 46 AU0).

## BQ6. Commitments

- The 10/10 support of judgement R is recorded. It is not overwritten by the control results
- **If Q fails, the shrunk claim in BQ4 is written.** The 10/10 support of R is not used as grounds for expansion
- The criteria for Q1 and Q2 are not changed after seeing results
- The ratio (Q2) is the primary indicator, and passing by raw values alone (Q1) is not written as passing
