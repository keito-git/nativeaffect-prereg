# Pre-registration Amendment 75: Full Results for E5 — Appraisal Dimension Directions Do Not Exceed the Variance-Matched Floor; Emotion Category Directions and Principal Component Directions Do

**Created**: 2026-10-07
**Targets**: Judgement E5 from amendment 73, provisional record from amendment 74
**Judgement**: **E5-pre passes (all 12 valid cells). E5a fails.**
**The comparison against the floor's own rate is explicitly designated as the reporting statistic.**

---

## BX1. Full Results

The experiment was carried out on 5 models; in 4 models comprising 12 cells, the positive gradient contrast passed. Each entry is the number of targets for which the best-selected direction within the family, evaluated in held-out contexts, exceeded the 95th percentile of the floor.

| Model | $J^\*$ | Emotion axis | Appraisal axis | Principal component | Floor | Gradient | Emotion−Floor | Appraisal−Floor |
|---|---|---|---|---|---|---|---|---|
| OLMo-2-7B | 0.02 | 11/13 | 7/13 | 8/13 | 6/13 | **13/13** | **+5** | +1 |
| OLMo-2-7B | 0.05 | 12/13 | 7/13 | 10/13 | 6/13 | **13/13** | **+6** | +1 |
| OLMo-2-7B | 0.10 | 13/13 | 7/13 | 10/13 | 9/13 | **13/13** | **+4** | −2 |
| Gemma-2-9B | 0.02 | 13/13 | 9/13 | 11/13 | 3/13 | **13/13** | **+10** | +6 |
| Gemma-2-9B | 0.05 | 13/13 | 6/13 | 12/13 | 9/13 | **13/13** | **+4** | −3 |
| Gemma-2-9B | 0.10 | 10/13 | 6/13 | 11/13 | 10/13 | **13/13** | ±0 | −4 |
| Llama-3.1-8B | 0.02 | 13/13 | 7/13 | 9/13 | 9/13 | **13/13** | **+4** | −2 |
| Llama-3.1-8B | 0.05 | 12/13 | 7/13 | 11/13 | 9/13 | **13/13** | **+3** | −2 |
| Llama-3.1-8B | 0.10 | 12/13 | 5/13 | 12/13 | 12/13 | **13/13** | ±0 | −7 |
| Llama-3.2-1B | 0.02 | 12/13 | 3/13 | 7/13 | 3/13 | **13/13** | **+9** | ±0 |
| Llama-3.2-1B | 0.05 | 12/13 | 2/13 | 8/13 | 8/13 | **13/13** | **+4** | −6 |
| Llama-3.2-1B | 0.10 | 12/13 | 3/13 | 9/13 | 5/13 | **13/13** | **+7** | −2 |

### Aggregate (12 cells)

| Family | Cells exceeding floor | Median | Range |
|---|---|---|---|
| **Emotion category axis** | **10/12** | **+4.0** | +0 to +10 |
| Principal component axis | 9/12 | +2.0 | +0 to +8 |
| **Appraisal dimension axis** | **3/12** | **−2.0** | −7 to +6 |

## BX2. Explicit Statement That the Floor's Own Rate Serves as the Reference

The criterion for E5a in amendment 73 BV6 was "whether the number of targets for which the family exceeds the 95th percentile of the floor constitutes a majority."
**However, the floor itself selects from 21 directions and is evaluated on held-out contexts, so upward selection bias allows the floor to reach 3–12/13.**
Therefore the absolute count is meaningless, and **the correct comparison is the difference from the floor's own rate.**

**This comparison does not relax the conclusion; it makes it stricter.** When the difference is taken, the appraisal dimension axis deteriorates further, falling at or below the floor in 9 of 12 cells. **This is in the same direction as the registered criterion's output (E5a fails), and is not a change to a more favorable criterion after seeing the results.**

**The use of the difference from the floor rate as the reporting statistic is fixed by this amendment.** All subsequent E5-series reports will use this difference.

## BX3. Primary Finding

> **When output perturbation is matched and a variance-matched in-plane floor is placed, the appraisal dimension directions that prior work has reported as causal levers do not exceed the floor**
> (median −2 targets, 3/12 cells). **Emotion category directions do exceed it**
> (median +4, 10/12), **and principal component directions also exceed it** (median +2, 9/12).
> **The gradient direction exceeds 13/13 in all 12 valid cells.**

**This is not a null result.** It is a **finding about ordering**: the appraisal dimension — treated by the field as a causal mechanism — fails, whereas simpler coordinates succeed.

**The fact that principal components exceed the floor is also reported.** Part of the emotion axis efficiency is explained by being a high-variance direction with structure. The emotion axis exceeds this; the **asymmetry whereby only the appraisal axis fails to reach the floor** is the core of the result.

## BX4. The 2 Excluded Models and Reasons

| Model | Event | Treatment |
|---|---|---|
| Phi-3.5-mini | 0/13 across all families and all budgets. **Gradient also 0/13** | **Reported as degenerate.** The readout does not respond. Does not satisfy E5-pre and is excluded from the judgement count |
| Mistral-Nemo-12B | **CUDA OOM.** Failed to allocate 2.50 GiB for the gradient backpropagation. Only 2.18 GiB of 94.97 GiB was free | **Reported as not executed.** Caused by the load of computing gradients of a 12B model in fp32. Retry is possible with `expandable_segments` and a smaller batch |

**Both are explicitly stated in the paper.** Phi's degeneracy is a result; Mistral-Nemo is an unexecuted case. **The fact that it could not be executed is not concealed.**

## BX5. Relationship to Prior Work

| Prior work | Report | Present result |
|---|---|---|
| Reichman, Avsian, Heck (ICLR 2026, arXiv:2510.22042) | Low-dimensional emotion manifold. Stable across 8 datasets and 5 languages. Manipulable with a trained steering module | **Consistent.** Emotion category directions exceed the floor |
| Maheswaran, Desarkar (EACL 2026) | Shared emotion representation in later layers. Emotion direction vectors exchangeable across datasets | Exchangeability not verified in the present study |
| Tak, Banayeeanzade, Bolourani, Kian, Jia, Gratch (Findings of ACL 2025) | Appraisal dimensions are linearly encoded; intervention moves output affect as predicted by theory | **Does not replicate under the variance-matched floor** |

**Not framed as a negation.** Framed as **identification of a boundary condition**: the effect was contingent on the strength of the contrast. Reichman et al.'s steering is a trained module and not a single direction, so **direct comparison with the direction-based intervention in the present study is explicitly noted as not applicable.**

## BX6. Current Status of Hypotheses (Update of Amendments 72 and 74)

> **H1′**: Among human emotion description frameworks, **the appraisal dimension is not privileged in intervention efficiency.**
> **The emotion category axis is privileged.** However, because principal component directions also exceed the floor,
> the advantage of the emotion category axis partially includes "being a high-variance direction with structure."

**H1 is not maintained as a monolithic claim.** The statement separately addresses which human concepts are privileged and which are not.

**The question of H2 has become clearer.** Rather than "searching for another coordinate because the human axis fails," the question is
**"whether there exists a coordinate that exceeds both the emotion category axis and the principal component axis."** This is carried out only if the E1-gate in amendment 73 BV7 is satisfied.

## BX7. Commitments

- The table of 12 cells is included in the paper as-is. Cells that did not exceed the floor are not omitted
- The difference from the floor rate is used as the reporting statistic; claims are not based on absolute counts alone
- The fact that principal components exceed the floor is stated explicitly; the advantage of the emotion axis is not overstated
- Phi's degeneracy and Mistral-Nemo's non-execution are stated explicitly
- Tak et al. are not framed as negated; they are framed as identification of a boundary condition
- The fact that Reichman et al.'s steering is a trained module and cannot be directly compared is stated
