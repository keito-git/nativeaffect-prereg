# Pre-registration Amendment 50: M1′ is not satisfied. When topics are controlled, cross-model agreement on emotion categories does not exceed chance

**Created**: 2026-10-04
**Target**: Judgement M1′ from Amendment 49 Part 2 (E5; within-skeleton permutation null)
**Judgement**: **Not satisfied.** The criterion is not changed.

---

## AY1. Results

E5 (169 stimuli, 28 skeletons, 6–7 stimuli per skeleton), agreement in residuals after removing surface statistics. Null: permutation of category assignments only within each fixed skeleton (500 repetitions).

| Model pair | Agreement |
|---|---|
| granite-4.2-3b vs SmolLM2-1.7B | +0.9278 |
| llm-jp-4-8b-base vs SmolLM2-1.7B | +0.9031 |
| llm-jp-4-8b-base vs granite-4.2-3b | +0.8907 |
| Qwen3-8B vs granite-4.2-3b | +0.8771 |
| Qwen3-8B vs llm-jp-4-8b-base | +0.8755 |
| Qwen3-8B vs SmolLM2-1.7B | +0.8627 |
| llm-jp-4-8b-base vs Mistral-7B-v0.3 | +0.8599 |
| granite-4.2-3b vs Mistral-7B-v0.3 | +0.8564 |
| Qwen3-8B vs Mistral-7B-v0.3 | +0.8502 |
| Mistral-7B-v0.3 vs SmolLM2-1.7B | +0.8379 |

**Null (within-skeleton permutation): mean +0.8619, SD 0.0276, p95 +0.9211. Soundness gate passed.**

**Minimum agreement in main series +0.8502 < p95 +0.9211 → M1′ not satisfied.** The minimum observed value **is even below the null mean** (+0.8502 vs. +0.8619).

## AY2. Interpretation

The null fixes the skeletons and destroys only the category assignments. This judgement therefore asks **"do models agree on category structure?"**

> **When topics (skeletons) are controlled, cross-model agreement does not exceed chance on the structure of emotion categories.**

The satisfaction of M1 recorded in Amendment 48 (E2+E3, minimum +0.7731 vs. p95 +0.5336) was **agreement on a topically diverse stimulus set, and combined with this result, it is natural to interpret that agreement as being due to topical structure.**

**The null is sound** (SD 0.0276, which is sufficient relative to the difference from the observation of 0.012). This is not unmeasurable due to degeneracy; **the agreement is absent.**

## AY3. Implications

- The main series of Amendment 38 (cross-model shared components → mixture of human emotions) **cannot assume cross-model universality at the level of emotion categories.** The grounds for proceeding to Stage 2 and beyond are weak
- Amendment 38 AM8 promises: "If the series terminates at Stage 1, Paper 3 will be written using the methodological proposition in Amendment 32 AF5." **M1 was satisfied on E2+E3 but not on E5, and for the portion concerning emotion, Stage 1 has not been passed**
- Because of the decision by the principal investigator (2026-10-04), Paper 3 has already been redirected to the **variance-matched audit of appraisal dimension steering**. This result retrospectively supports that decision

## AY4. Both are reported

- **M1 satisfied (E2+E3; old null)**
- **M1 not satisfied (E5; old null. However, treated as unmeasurable because the null was degenerate)**
- **M1′ not satisfied (E5; within-skeleton permutation null. Null is sound)**

All three will be written in the paper. Results will not be cherry-picked.

## AY5. Promises

- The criterion for M1′ will not be changed post-hoc
- "There is a shared representation about emotion across models" will not be written
- The possibility that the satisfaction of M1 is explained by topical structure will be explicitly stated
- Stages 2–4 (M2–M4) and H-A–H-C will be treated as a **supplementary series with the audit as the main series**, and will not be presented as the main result
