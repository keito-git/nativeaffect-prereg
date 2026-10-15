# Pre-registration Amendment 23: Correct three errors in Amendment 22 (model attribution, disclosure of computations already performed)

**Target**: Amendment 22 (`cd92d48`, 2026-09-27 16:22:40 +0900), §V3.1 / §V4 / §V5 / §V6
**Created**: a group member / 2026-09-27
**Nature**: **Self-reported correction. Amendment 22 was pushed while containing factual errors.**
**Origin**: A monitoring script failed on `layer11.json`; reading the JSON contents during investigation revealed that the premises of Amendment 22 were incorrect.

---

## W1. What was wrong

**Amendment 22 stated that the G1 sensitivity directions and the prediction P test were performed on Apertus-1.5B. This is incorrect.**

`/path/to/work/code/phase10/g1_jacobian.py:32` has `MODEL = "Qwen/Qwen3-8B"`, and
`G1_jacobian/layer{11,16,22,27}.json` all have `d = 4096` (the hidden dim of Qwen3-8B).
**Apertus-v1.1-1.5B has a hidden dim of 2048, which cannot be 4096.**

| Target | Actual model | Generation time (UTC) |
|---|---|---|
| G1 sensitivity directions layer11 | **Qwen/Qwen3-8B** | 2026-09-26T11:30:26Z |
| G1 sensitivity directions layer16 | Qwen/Qwen3-8B | 2026-09-26T11:49:46Z |
| G1 sensitivity directions layer22 | Qwen/Qwen3-8B | 2026-09-26T12:06:00Z |
| G1 sensitivity directions layer27 | Qwen/Qwen3-8B | 2026-09-26T12:19:31Z |
| `prediction_p_verdict.json` | Derived from the above 4 layers = **Qwen3-8B** | 2026-09-26T13:22:39Z |

Consistency check: `prediction_p_verdict.json`'s layer11 `C_mean_entry = 0.0377840929706246` **exactly matches** `layer11.json`'s `mean_abs_cos_with_top10_PC`. They originate from the same computation.

## W2. Correction 1 (§V4): **Prediction P failed on Qwen3-8B**

The statement "prediction P failed on Apertus-1.5B" in Amendment 22 §V4 is withdrawn.
**Prediction P was tested on Qwen3-8B from the beginning, and failed there** (mean of partial-angle cosines 0.1087–0.1340 across 4 layers, threshold 0.70).

**The conclusion does not change.** The policy of not re-registering prediction P (Amendment 22 §V4) is maintained as-is.
In fact, **since it already failed on the target model, there was no room to re-register on a different model from the start.**

## W3. Correction 2 (§V5): **That contrast is not a controlled comparison**

Amendment 22 §V5 stated "on Apertus-1.5B sensitivity directions were outside the top-10 principal component space (mean cosine 0.109–0.134), whereas emotion axes in Paper 2 had 88.7–99.97% inside." **The two are from different models.**

- Sensitivity directions (outside, mean cosine 0.109–0.134): **Qwen3-8B**
- Emotion axes in Paper 2 (88.7–99.97% inside): **Apertus-1.5B**

**Therefore this contrast is precisely the inter-model confounding that Amendment 22 §V3 itself prohibited.**
**It will not be used in claims or descriptions.** To present this contrast, **emotion axes must be derived on Qwen3-8B** and compared within the same model (this is already required by §V3.1).

## W4. Correction 3 (§V6): **Computations had already been performed. "No computation has started" is incorrect.**

Amendment 22 §V6 stated "no computation has started." **This is incorrect.**

**The G1 candidate construction (computation of sensitivity directions) was completed on Qwen3-8B approximately 20 hours before the Amendment 22 commit (2026-09-27 16:22 JST), specifically between 2026-09-26 20:30 and 21:19 JST.**

**However, the G1 judgement (160 cells) has never been run.** The confirmatory status of the research depends on the judgement, and the judgement will be executed after this amendment. **The fact that candidate construction preceded registration is recorded here, and the claim is limited to "registration exists before the judgement." Regarding candidate construction, it will be explicitly stated in the report that "it was performed before pre-registration."**

**Why the error was made**: The JSON's `d` (hidden dim) was not read; instead, the inference was made from the fact that two files `g4_precondition.json` (Apertus) and `g4_precondition_qwen3_8b.json` exist that "the G1 series must be on the Apertus side." **A pre-registration was written based on inference.** Going forward, model attribution will be confirmed from **the `d` inside the file and the `MODEL` constant in the script**.

## W5. Correction 4 (§V3.1): Narrow the scope of the redo

**Since G1 sensitivity directions already exist on Qwen3-8B, they will not be recomputed** (it would be merely a repetition of the same computation, and changing the random seed would constitute redoing the selection).

The redo items in §V3.1 are replaced with the following:

1. **G1 sensitivity directions: will not be recomputed** (use existing results on Qwen3-8B; the 4 files in W1)
2. G1 judgement (160 cells): **not yet executed; will be executed after this amendment**
3. Activation extraction and axis derivation (P1_cov / P2_ridge_std): execute on Qwen3-8B (not yet done)
4. G2 / G3 / G4 / Amendment 14 N5: execute on Qwen3-8B (not yet done)

**On the partition**: `e1_split_20260926.json` is a partition over stimuli and does not depend on the model. As `layer11.json`'s `split_group: "discovery"` shows, sensitivity directions were constructed using only the discovery half. **Applying the same rules and the same seed produces the same partition, so this partition file will be used as-is** (the phrase "re-cut" in Amendment 22 §V3.1 meant this; it does not mean creating a different partition).

## W6. Audits A and B will be conducted as planned

`g1_audit_ab.py` failed on `layer11.json` because it assumed the key name `directions`.
**The correct key is `sensitivity_directions`** (shape (10, 4096), L2 norm of each row = 1.0).
Fix and re-run. **The judgement criteria remain unchanged from those fixed before the amendment**
(if 50 or more of the 100 floor draws are within 1.183e-3 bits of the axis, the metric is judged unmeasurable).
