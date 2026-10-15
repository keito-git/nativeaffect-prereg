# Pre-registration Amendment 52: F3 already exists. What remains is only F4 and matching of output perturbation magnitude.
# Together with this, the prediction "which directions exceed the floor" is registered

**Created**: 2026-10-04
**Status**: A supplement to amendment 49, Part 1 (variance-matched audit of evaluation-dimension steering). Judgements V1–V3 are not changed.
**Activation condition**: V1–V3 and the prediction W1 of this amendment must not be judged until this file has been committed and pushed. Stage A (probe reproduction) does not include judgements and is therefore already running.

---

## BA1. Re-confirmation of priority (a literature check + our own verification of the full text)

A literature check covered 11 papers, and we verified the full text of the decisive one paper ourselves.
Survey: `05_文献/steering対照条件サーベイ_20261004.md` (466 lines)

**Floor hierarchy coverage status**

| Paper | F1 full-space | F2 axis-orthogonal | F3 in-plane | F4 VMIC |
|---|---|---|---|---|
| Turner et al. 2023 ActAdd (arXiv:2308.10248) | Partial (procedure requires confirmation) | None | None | None |
| Zou et al. 2023 RepE (arXiv:2310.01405) | None | None | None | None |
| Panickssery et al. 2024 CAA (arXiv:2312.06681) | None | None | None | None |
| Li et al. 2023 ITI (arXiv:2306.03341) | Yes (perturbation magnitude not matched) | None | None | None |
| **Tak et al. 2025 (arXiv:2502.05489)** (audit target) | Knockout only | None | None | None |
| **Sun et al. 2026 (arXiv:2604.03147)** | **Yes** | **Yes** | **Yes** | **None** |
| Pres et al. 2024 (arXiv:2410.17245) | Not proposed | — | — | — |
| Braun et al. 2025 (arXiv:2505.22637) | None | None | None | None |
| Bas & Novak 2024 (arXiv:2511.18284) | None | None | None | None |
| Banayeeanzade et al. 2025 (arXiv:2510.04484) | None | None | None | None |
| Gao et al. 2026 (arXiv:2608.22985) | None | None | None | None |

Facts confirmed in the full text (HTML v1) of **Sun, Yan, Lu, Lee, Zhang, Shao (2026) "Valence-Arousal Subspace in LLMs: Circular Emotion Geometry and Multi-Behavioral Control", arXiv:2604.03147**:

- The controls consist of "in-plane, orthogonal-to-plane, completely random orthonormal pairs; 3 seeds each", totaling **9 directions**
- **The procedure for generating in-plane random directions is not explicitly stated in the text** (no description of distribution or norm matching)
- **There is no variance matching** (no description of matching variance profiles in principal-component coordinates)
- Intervention strength uses **the same α for all conditions**. There is no matching on the output-side metric (KL, JS)
- Results: VA axes clearly exceed the controls. "Random directions remain within 2–3pp of baseline across all α" "All nine show similarly flat effects"

**Therefore F3 (in-plane random) is already known.** This is as was previously noted in a literature check at the time of paper 2.
**F4 (variance-matched) and matching of output perturbation magnitude are, within the confirmed scope, not yet implemented.**

## BA2. Novelty remaining in this audit (limited in advance)

1. **Implementing F4 (in-plane random directions with matched variance) as a control for steering**
2. **Comparison with output perturbation magnitude (JS divergence over the top-100-word union) matched across conditions**
3. Applying the above two to **an audit of evaluation-dimension steering (Tak et al. 2025)**
4. **Systematic organization of the floor hierarchy** for emotion and evaluation-dimension steering

**The introduction of F3 will not be claimed as a contribution of this study.** Sun et al. 2026 will be cited.

## BA3. An important tension — our prediction is not trivial

In paper 2, ICA axes were beaten by in-plane random directions in 11 out of 12 cells.
**Sun et al. 2026 reports the opposite result** (VA axes clearly exceed in-plane random).

The difference between the two is considered to lie in **how the directions are constructed**.

| | How direction is constructed | Result relative to in-plane floor |
|---|---|---|
| ICA axes in paper 2 | Unsupervised (selected by activation partition reproducibility) | **Lost** (11/12 cells) |
| VA axes in Sun et al. | Supervised (regression to valence/arousal labels) | **Won** |
| Evaluation dimensions in Tak et al. | **Supervised** (linear regression to evaluation ratings) | **Not yet verified** |

Since the evaluation-dimension directions are supervised, **they are likely to exceed F3.** The real test of the audit is F4.

## BA4. Prediction W1 (registered before seeing results)

> **Supervised directions (obtained by regression to labels associated with the output) exceed F3, whereas unsupervised directions (selected by variance or reproducibility) do not. Since evaluation-dimension directions are supervised, they exceed F3.**
> **Success or failure on F4 is not predicted at the time of this amendment.**

**Judgement W1**: In this audit, (a) evaluation-dimension directions exceed the 95th percentile of F3, and (b) directions selected from ICA/principal components on the same model and same layer do not exceed F3.
**If both are satisfied, W1 is supported.**

**No prediction is made regarding F4.** Whichever way it goes, it will be reported. It is explicitly stated that no prediction is made.

## BA5. Items requiring confirmation (to be resolved before making claims)

The unresolved items raised in a literature check are taken over here.

1. **Full names of all authors of Zou et al. 2023 (RepE).** The survey's BibTeX still has `others`. **This violates the lab convention (full names of all authors, no `et al.`/`others`), and must be resolved before citing.**
2. **The norm-matching procedure in the KL comparison of Turner et al. 2023 ActAdd.** The HTML version is insufficient. Refer to the PDF.
3. **The procedure for generating in-plane random directions in Sun et al. 2026.** Not explicitly stated in the text. **If variance matching turns out to be included, novelty item 1 of this audit disappears.** Either contact the authors, or verify from the code if it is publicly available. **Until resolved, do not assert definitively that "F4 is not yet implemented."**

## BA6. Promises

- The introduction of F3 will not be claimed as a contribution of this study. Sun et al. 2026 will be cited
- The judgement criteria of W1 will not be changed after seeing results
- **It will be explicitly stated that no prior prediction is held for F4, and both pass and fail will be reported**
- Until the 3 items in BA5 are resolved, no definitive statements will be written in the paper regarding those sections
- Zou et al. will not be cited until `others` has been removed from the survey's BibTeX
