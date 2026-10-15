# Pre-registration Amendment 22: Transfer the target model from Apertus-1.5B to Qwen3-8B

**Target**: Pre-registration body §1 (target model), §2 G1–G3, §3 G4, Amendment 14 N5
**Created**: a group member / 2026-09-27
**Status**: **Not a single G1 judgement has been run. G4 has not been run. The test set is unopened.**
**Origin**: The prerequisite check for G4 failed on Apertus-1.5B (results in V1 below). Transfer decided by the principal investigator.

---

## V1. Fact: G4 is unmeasurable on Apertus-1.5B

`03_解析/plan_b/g4_precondition.json` (2026-09-26T04:22:24Z, no intervention, GSM8K test 500 questions,
8-shot, greedy, seed 20260926):

| Token budget | 64 | 128 | 256 | 512 |
|---|---|---|---|---|
| Accuracy (%) | 4.6 | 8.6 | 8.8 | 8.8 |

Monotone non-decreasing is satisfied, but **max − min = 4.2 points falls short of the criterion of 5.0** (`PRECONDITION_MET: false`).
The registered failure language is quoted verbatim:
"**G4 cannot be measured on this model: there is no upward curve to shift.**"

**8.8% is the ceiling.** No upward curve exists to shift with intervention.

## V2. Fact: Qwen3-8B satisfies the prerequisite

`03_解析/plan_b/g4_precondition_qwen3_8b.json` (2026-09-26T06:02:15Z, same conditions, batch 16):

| Token budget | 64 | 128 | 256 | 512 |
|---|---|---|---|---|
| Accuracy (%) | 15.4 | 62.6 | 89.0 | 91.0 |

Monotone non-decreasing, **max − min = 75.6 points** (`PRECONDITION_MET: true`).

## V3. Decision: **execute all of G1–G4 and N5 on Qwen3-8B**

**The reason is avoiding confounding.** Deriving axes on Apertus-1.5B and measuring computation reduction on Qwen3-8B would make **the claim "intervention on AI-native axes reduces computation" invalid.** The intervention direction and the target of intervention would come from different models, so observed differences could be explained by inter-model differences rather than the direction's properties.

**Therefore axes will be re-derived from scratch.** Existing Apertus-1.5B results will not be carried over as the basis for Qwen3-8B claims.

### V3.1 Scope of redo

1. Activation extraction (E4 40 stimuli, E1 287 sentences) on Qwen3-8B
2. Axis derivation (both registered estimation procedures P1_cov / P2_ridge_std)
3. **Re-cut the discovery/validation partition.** Since stimuli are identical, **use the same stratification rules and the same seed 20260926**
   (do not change the partitioning rules; changing them would introduce circularity between selection and testing)
4. G1 (Jacobian sensitivity direction construction and 160-cell judgement)
5. G2 / G3
6. G4 (GSM8K, computation reduction)
7. Amendment 14 N5 (1,000 random directions within the top-principal-component subspace, held-out R²)

### V3.2 Layer correspondence

Layer numbers for Qwen3-8B follow the correspondence table in `03_解析/plan_b/layer_mapping_qwen3_8b.json`.
**Apertus layers 5/7/10/12 will not be used as-is.** Correspondence is established by relative depth, and the correspondence table will be included with the results.

### V3.3 Handling of Apertus-1.5B existing results

**They will not be discarded.** The experiments in Paper 2 (the methodology paper) are all complete on Apertus-1.5B, and the claims there (that VMIC is a necessary condition) are unaffected.
**In Paper 3, Apertus results will be positioned as "prior observations on a different model" and will not be used as the basis for claims.**

## V4. On prediction P (restated; no change)

Amendment 14 N2's prediction P failed on Apertus-1.5B (`prediction_p_verdict.json`,
mean of partial-angle cosines 0.109–0.134 across all 4 layers, threshold 0.70).

**Prediction P will not be re-registered for Qwen3-8B.** Re-issuing a prediction that failed once, on a different model, constitutes trying until one hits the target. **We will not write a mechanistic explanation. We will write "why the floor wins remains unresolved."**

However, **the degeneration check (maximum singular value of signed G) will also be performed on Qwen3-8B.** This is not a prediction but a prerequisite confirmation for using the four-quadrant judgement, and it was specified in Amendment 16.

## V5. Items to be reported descriptively (not used in judgement)

On Apertus-1.5B the sensitivity directions were outside the top-10 principal component space (mean 0.109–0.134), whereas the emotion axes of Paper 2 had 88.7–99.97% inside the same subspace. **This contrast will also be measured on Qwen3-8B and reported descriptively.** However **it will not be used in judgement** (to avoid circularity between selection and testing).

## V6. What must be fixed before execution

**Qwen3-8B computation will begin only after this amendment is recorded in git.** No computation has started
(only the prerequisite feasibility checks V1/V2 have been performed, and these are not registered tests but feasibility confirmations.
`purpose: "G4 feasibility precondition; not a pre-registered test"` is stated explicitly in each JSON).
