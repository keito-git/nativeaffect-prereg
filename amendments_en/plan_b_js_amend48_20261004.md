# Pre-registration Amendment 48: M1 passed on the main evaluation set but has no statistical power on E5.
# Additionally, the matching for Family B has been pre-empted by prior research

**Created**: 2026-10-04
**Target**: Judgement M1 of Amendment 38 Stage 1 (conditions in Amendment 45); human concept list Family B from Amendment 47
**Judgement**: **M1 is satisfied on the main evaluation set (E2+E3). However, this is a pass on 4 of the 5 registered models.** **E5 has high null values and no statistical power.**

---

## AW1. Results of M1 (main evaluation set E2+E3; judgement target)

| Model pair | After surface removal | Raw |
|---|---|---|
| Qwen3-8B vs granite-4.2-3b | +0.8548 | +0.8661 |
| Qwen3-8B vs llm-jp-4-8b-base | +0.8421 | +0.8444 |
| Qwen3-8B vs Mistral-7B-v0.3 | +0.7794 | +0.7740 |
| llm-jp-4-8b-base vs granite-4.2-3b | +0.8612 | +0.8597 |
| llm-jp-4-8b-base vs Mistral-7B-v0.3 | +0.8129 | +0.8232 |
| granite-4.2-3b vs Mistral-7B-v0.3 | +0.7731 | +0.7625 |

Null N1 (permutation of stimulus rows, 200 repetitions): mean +0.4745, SD **0.0417**, p95 +0.5336. The null soundness gate (Amendment 45 AT2.5) is **passed** (SD is non-zero and at least 1/10 of the difference from the observation).

**Minimum agreement in main series +0.7731 > p95 +0.5336 → M1 satisfied.**

## AW2. 2 of the 5 registered models could not be extracted

| Model | Outcome | Reason |
|---|---|---|
| `google/gemma-4-E2B-it` (main series) | **Failed** | `AttributeError: 'list' object has no attribute 'keys'` (cannot be read with `AutoModelForCausalLM`) |
| `swiss-ai/Apertus-v1.1-1.5B` (supplementary series) | Failed | `RuntimeError: expected mat1 and mat2 to have the same dtype, float != Half` |

**Accordingly, M1 was satisfied with 4 models (6 pairs) rather than the 5 registered models.** Amendment 45 AT2.1 permits the exclusion of models that cannot be read, but **the fact that this is not a pass on 5 models will be explicitly stated in the paper.** `gemma-4-E2B-it` will be retried with the appropriate auto class, and if successful, the pair count will be updated from 6 to 10 for re-judgement. The outcome of the retry will be recorded regardless of success or failure.

Because only SmolLM2-1.7B succeeded in the supplementary series, **scale-dependence cannot be examined at this time.**

## AW3. No statistical power on E5 (critical limitation)

| | Minimum agreement (after surface removal) | Null mean | Null p95 |
|---|---|---|---|
| Main evaluation E2+E3 | +0.7731 | +0.4745 | +0.5336 |
| Supplementary evaluation E5 | +0.8502 | **+0.8483** | **+0.9155** |

**On E5, the null mean reaches +0.8483, and the minimum observed agreement of +0.8502 does not exceed p95.**

Mechanism: Because E5 is a grid of stimuli sharing skeletons, rows are close to each other. Permuting rows barely changes the relative representation profiles, so the null is high. **Permutation null is not appropriate for E5.**

**Implication**: M1 was satisfied on the topically diverse E2+E3, and **the possibility that the agreement is due to topical structure cannot be excluded.** In E5, where topics are controlled, agreement cannot be distinguished from chance.

This limitation will be explicitly stated in the paper. **"There is a shared representation about content across models" will not be written.** The writable claim is limited to: "In a topically diverse stimulus set, there is agreement not explained by sentence form."

## AW4. Prior art check (fulfilling the obligation of Amendment 47 AV6)

The matching with Family B (appraisal dimensions) **has already been published.**

| Reference | Content |
|---|---|
| Tak, Banayeeanzade, Bolourani, Kian, Jia, Gratch (2025), ACL 2025, arXiv:2502.05489 "Mechanistic Interpretability of Emotion Inference in Large Language Models" | Reports that appraisal theory dimensions are **linearly encoded** in LLM internals, and that **causal intervention on those dimensions moves output emotion as theory predicts**, across **multiple model families and scales** |
| Choi, Weber (2026), arXiv:2604.07382 "Latent Structure of Affective Representations in Large Language Models" | Reports via geometric analysis that latent affective representations align with the psychological valence–arousal model |
| Sofroniew, Kauvar, Saunders et al. (2026), arXiv:2604.07729 "Emotion Concepts and their Function in a Large Language Model" | Reports that "functional emotions" in Claude Sonnet 4.5 **causally influence** output |

**Pre-empted scope**:
- "Appraisal dimensions are linearly represented" — Tak et al. 2025
- "Intervention on appraisal dimensions moves emotion" — Tak et al. 2025 (**the majority of the intent of Amendment 46 H-A**)
- "Emotion representations align with valence–arousal" — Choi & Weber 2026

**Therefore, if the components match Family B (appraisal dimensions), those results have no novelty.** Per the promise in Amendment 47 AV6, novelty will not be claimed.

**Scope not pre-empted (what remains in this research)**:
1. **Discovery of components without using human labels.** Prior research probes human-defined appraisal dimensions. This research extracts components from cross-model agreement and **asks where they fall in human concepts.** Only if Amendment 47 N3 (components not close to any concept) results does this become novel.
2. **Identification of shared components in a model-independent coordinate system** (relative representation). Prior research measures separately per model.
3. **Auditing with variance-matched floor (VMIC).** Paper 2 showed that the apparent effect of steering over full-space random directions disappears in 11 of 12 cells when using directions drawn from within a variance-matched subspace. **Whether the intervention results of Tak et al. survive under VMIC has not been tested.**

## AW5. Promises

- M1 will not be claimed as a novelty (already stated in Amendment 46 AU3)
- The fact that M1 was satisfied on 4 models will be explicitly stated
- **The fact that there was no statistical power on E5 will not be concealed.** The inappropriateness of the permutation null for E5 will be written
- If components match Family B, Tak et al. 2025 will be cited and **reported as a replication**
- The outcome of the retry of `gemma-4-E2B-it` will be recorded regardless of success or failure
- **The main text of Tak et al. 2025 has not been obtained.** Until it is obtained and the scope of claims is confirmed, the specific description of "what was pre-empted" will not be written in the paper
