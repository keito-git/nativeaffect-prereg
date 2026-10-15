# Pre-registration Amendment 45: P1 was not supported. Confirming the execution conditions for P2 (Amendment 38, Stage 1)

**Created**: 2026-10-04
**Target**: Prediction P1 from Amendment 41 / Stage 1 judgement M1 of Amendment 38 (cross-model shared components)
**Activation condition**: The agreement for Stage 1 must not be calculated until this file has been committed and pushed. Obtaining model weights and extracting representations do not involve judgement, so they may be performed before the push.

---

## AT1. Resolution of P1: not supported

P1′ registered in Amendment 43 was executed, and Amendment 44 recorded that the null for E5 was degenerate. A subsequent audit revealed that **the null for E4 also had a defect**. Both are resolved here.

### AT1.1 The null for E4 was dominated by noise in a single direction

| Stimulus set | Layer | Signal norm | Injected noise norm | Ratio | Effective rank of residual pool |
|---|---|---|---|---|---|
| E4 | 0 | 0.17 | 0.16 | 0.93 | **1.0** (all 80) |
| E4 | 11 | 14.53 | 10.24 | 0.71 | **2.2** |
| E4 | 27 | 61.02 | 43.80 | 0.72 | **2.4** |
| E5 | 0 | 0.08 | 0.07 | 0.82 | 57.8 (all 169) |

Because E4 has only 2 sentences per category, the within-category residuals consist of only 40 pairs of $\pm(x_1-x_2)/2$, and because the templates are shared, the direction of the difference is nearly identical across all categories. **The effective rank of the residual pool is 1.0–2.4, which is effectively a single direction.** Because this was added to all 40 rows of the null, the spectrum of the null collapsed (the effective rank of the null for layer 0 was 2.69 against 40 categories).

For variant B, which uses purely independent directions with noise removed, rank90 = 34.00±0.00 and effective rank 34.07–36.14, consistent with the theoretical value. Variant C, which inverts the sign of the residual mean, is identical to variant A, indicating that **the cause is the magnitude of the shared direction, not its sign**.

### AT1.2 The conclusion reverses depending on the statistic

Under the registered null A (a null with matched measurement conditions — this is the correct null):

| Stimulus set | Layer | rank90: observed / null 5th percentile | Effective rank: observed / null 5th percentile |
|---|---|---|---|
| E4 | 11 | 22 / 31.0 **below** | 13.31 / 9.38 **not below** |
| E4 | 16 | 22 / 32.0 **below** | 13.76 / 12.34 **not below** |
| E4 | 22 | 22 / 32.0 **below** | 13.78 / 11.03 **not below** |
| E4 | 27 | 20 / 32.0 **below** | 12.78 / 9.60 **not below** |

**Two statistics that reasonably summarise the same spectrum give opposite answers.** Therefore, for E4 it cannot be said that "the intrinsic dimensionality of the category structure is lower than that of independent categories." The category means in the observation are themselves constructed from 2 samples, and the same single direction is likely contaminating the observations as well (the proximity of the observed effective rank 13.31 to the null A value 11.94 is naturally interpreted this way).

**E4 is insufficiently designed for dimensionality estimation** (2 samples per category, $d$=4096, noise/signal 0.7).

### AT1.3 In E5, compression already exists at layer 0, and computation adds nothing

E5 does not have a low-rank residual pool; in terms of effective rank, the null also has variance (±0.43–0.62).

| Layer | Observed effective rank | Null 5th percentile | Increment from layer 0 |
|---|---|---|---|
| 0 | 25.89 | 33.21 | — |
| 11 | 25.38 | 33.48 | −0.51 |
| 16 | 26.35 | 33.58 | **+0.46** |
| 22 | 27.43 | 33.98 | **+1.54** |
| 27 | 24.45 | 32.55 | −1.44 |

It is clear across all layers that dimensionality is lower than for independent categories. **However, it is equally low at layer 0.** The increments are not uniformly negative, and one layer shows +1.54. In accordance with the intent of the control in Amendment 40 AO2, **only the increment beyond layer 0 is attributable to the model's computation**, and therefore:

> **P1 (that the intrinsic dimensionality of emotion categories is lower than that of independent categories, and that this is brought about by the model's computation) was not supported.**

The low dimensionality observed in E5 **is explained by the lexical statistics at layer 0**.

### AT1.4 For the record

- The 4/4 pass for E4 by `rank90` registered in Amendment 43 will **not be cited as a result**
- The judgement for E5 by effective rank registered in Amendment 44 will also **not be counted as a pass, because it does not pass the layer-0 control**
- The negation of P1 is not the negation of AAPH as a whole. P1 is an auxiliary proposition; the core is P2 (the existence of components shared across models)

## AT2. Confirming the execution conditions for P2 (Amendment 38, Stage 1)

Amendment 38 AM8 promises: "Confirm the model, layer, and anchor set before seeing the results, and append them to this file." These are confirmed below.

### AT2.1 Models (5 models in the main series)

Of the 5 models listed in Amendment 38, `Dense_1b_130B` **does not exist in HuggingFace**. As a replacement, `mistralai/Mistral-7B-v0.3` will be used. The family does not overlap, there is no gate, and it is included in the target set of Paper 1. **This substitution is not concealed.**

| # | Model | Family | Number of layers | Selected layer (depth 0.6) |
|---|---|---|---|---|
| 1 | `Qwen/Qwen3-8B` | Qwen | 36 | 22 |
| 2 | `llm-jp/llm-jp-4-8b-base` | LLM-jp | 32 | 19 |
| 3 | `google/gemma-4-E2B-it` | Gemma | obtained from config | nearest to depth 0.6 |
| 4 | `ibm-granite/granite-4.2-3b` | Granite | 40 | 24 |
| 5 | `mistralai/Mistral-7B-v0.3` | Mistral | 32 | 19 |

**Layer selection rule (fixed)**: $L = \mathrm{round}(0.6 \times n_{\text{layers}})$. The midpoint of the range 0.45–0.75 from Amendment 38 AM2. **Only one layer per model is used; the layer is not selected post-hoc.** For `gemma-4-E2B-it`, the `num_hidden_layers` in `config.json` is nested, so it is read from `text_config`. **If this cannot be read, that model will be excluded, and the fact of exclusion will be reported.**

### AT2.2 Extension (2 models in the supplementary series; not used for judgement)

`swiss-ai/Apertus-v1.1-1.5B` and `HuggingFaceTB/SmolLM2-1.7B` will also be measured using the same procedure, and **the full pairwise agreement matrix will be reported**. This extends the family count to 7 across the 1.5B–8B range in order to examine scale dependence. **The judgement of M1 is made on the main series of 5 models only.** The supplementary series is reported as description.

### AT2.3 Anchors and evaluation sets

- **Anchors**: 120 sentences drawn from E1 by permutation with `seed=20261003` (the default of `stage1_relative_rep.py`, unchanged). E1 consists of general sentences containing no emotion words, and were not selected based on emotional content.
- **Main evaluation set**: E2 + E3 (the default of `stage1_relative_rep.py`). M1 is judged on this set.
- **Supplementary evaluation set**: E5 (skeleton × category grid; no emotion words). **The same procedure will be applied and reported, but it will not be used for the judgement of M1.** E5 is closer to the question of AAPH, but the evaluation set registered in Amendment 38 for the judgement is E2+E3, and the evaluation set must not be selected after seeing the results.

The anchors and evaluation sets are disjoint by construction.

### AT2.4 Judgement (as in Amendment 38 AM2; unchanged)

**M1**: For **all pairs** among the 5 main-series models, the agreement in the residuals after removing the portion explained by surface statistics exceeds the 95th percentile of null N1 (permutation of stimulus rows, 200 repetitions).
**If not satisfied, this series is terminated and Paper 3 will be written using the methodological proposition in Amendment 32 AF5.**

Surface statistics are `surface_features` (token count, word count, mean word length, punctuation count, capitalisation rate, mean and standard deviation of token IDs), fit on the evaluation stimuli only.

### AT2.5 Confirming the soundness of the null first (discipline introduced in Amendment 44 AS4)

**Confirm that the standard deviation of null N1 is not 0, and if the standard deviation is less than 1/10 of the difference between the observation and the null, record M1 as unmeasurable.** The reason for this gate is that for P1, the degenerate null was not noticed and a pass was nearly reported. From this point forward, this gate is applied to all judgements.

## AT3. Promises

- Agreement will be calculated after this file is pushed. Extraction alone may proceed beforehand
- Model, layer, anchor, and evaluation set are fixed in this file and will not be changed after seeing the results
- The substitution of `Dense_1b_130B` and any excluded models will be written in the paper
- If M1 is not satisfied, this series is terminated. The criterion will not be relaxed
- **The fact that P1 was not supported will be explicitly stated in the paper.** Even if P2 passes, the claim that "the intrinsic dimensionality is low" will not be made
