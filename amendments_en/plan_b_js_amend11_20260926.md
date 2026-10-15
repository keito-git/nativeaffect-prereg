# Pre-Registration Amendment 11: With the Model Change, Layer Selection and Axis Extraction Must Be Redone

**Target**: Amendment 10 (model change), pre-registration main body §4 (layers = 5, 7, 10, 12)
**Created**: 2026-09-26
**Status**: **G1 not yet executed**
**Origin**: Amendment 10 changed the G4 model, but **how to handle layer selection and axis extraction had been omitted**

---

## K1. Omission in Amendment 10

Amendment 10 stated "since G1 has not been executed, all of G1–G4 can be run on the same model." **This consequence had not been stated explicitly.**

**Saying that all of Plan B will be redone with Qwen3-8B means redoing the axis extraction from scratch.**

- The pre-registration main body fixed the layers as **5, 7, 10, 12**. **These were selected for Apertus-v1.1-1.5B (d=2048)**
- **Qwen3-8B has 36 layers and d=4096** (empirically measured by the team). **Layers 5, 7, 10, 12 in a 36-layer model are extremely biased toward the shallow side**
- The axes (ICA components) and the PMF floor basis **must be extracted fresh for each model**

**G4 will not be run alone with the new model.** G4 measures interventions on axes selected in G1, so **G4 measurements are meaningless if the axes come from a different model.**

## K2. Layer Selection (Fixed Before the Experiment)

**Preserve relative depth.** Do not arbitrarily select new layers.

1. **Empirically measure the total number of layers N in Apertus-v1.1-1.5B** (read from the configuration file; do not estimate)
2. Calculate the relative depths of the old 4 layers as **5/N, 7/N, 10/N, 12/N**
3. **For Qwen3-8B (36 layers), select the layers closest to those 4 relative depths**
4. **Record the correspondence table of selected layer numbers and relative depths in a JSON file before executing G1**

**Since this rule is written first, even if the resulting layers are inconvenient, they will not be changed.**

**Basis for using relative depth**: In Paper 1 (AffectGeometry), the peak depth of linear decodability fluctuated across models, and **across 38 models, aligning by relative depth reduced inter-model variance**. This follows the finding that relative depth, not absolute layer number, is the comparable coordinate.

## K3. Redoing the Axis Extraction

- **Re-extract ICA components (rank 20) from the activations of Qwen3-8B.** Use seed 20260926 and record it
- **Include the top 10 principal components (PC1–PC10) among the candidates** (as in Amendment 1 A2)
- **Also compute Jacobian singular directions with Qwen3-8B** (Amendment 1 A2)
- **Also build the PMF floor basis from the activations of Qwen3-8B**
- **The discovery/confirmation partition is defined on the stimulus side, and `axis_rebuilt_split_20260925.json` is used as-is.** The stimulus set (E1) is not changed, so no re-partitioning is needed

## K4. Treatment of Old Model Results

- **Results obtained with Apertus-v1.1-1.5B (C1–C4, B0, E1 diagnostics, G4 precondition failure) are final results of Paper A (methodology paper). They are not retracted or remade**
- **The model description of Paper A will not be changed**
- **Plan B (G1–G4) will be executed as a separate study with Qwen3-8B.** The fact that the model differs between Paper A and Plan B will be explicitly stated in the Plan B manuscript
- **If Plan B results are obtained, whether the conclusions of Paper A (the reality of variance confounding and the fact that directions with known semantic content lose to the floor) also hold in Qwen3-8B will be separately confirmed by performing measurements corresponding to C1 and C2.** Do not extrapolate the 1.5B findings to 8B in writing

## K5. Execution Time (Updated with Empirical Measurements)

Empirical measurements by the team (16.2× with batch 16, Qwen3-8B):

- Precondition (500 problems × 4 budgets): **about 0.19 hours**
- All 1,319 problems × 4 budgets: **about 0.49 hours/condition**
- **5 conditions: about 2.5 hours**

The concern in Amendment 10 J4 of "exceeding 18 hours" has been resolved. **The judgment to place implementation before design compromise was effective.**
However, **the computation for axis extraction and floor construction in G1–G3, and the computation for performing those with 8B and 4096 dimensions, will be estimated separately.** The 2.5 hours of G4 is not the full picture.

## K6. Caution About Ceiling Effects (Record That Does Not Change the Judgement)

In smoke (32 problems), accuracy at budget 256 reached **78.12%**. **The baseline is high, so the room for improvement with intervention is small on the upper side.**

**Since the primary judgement is "token count to reach the same accuracy," ceiling effects do not invalidate the primary judgement** (examining whether the same 78% can be reached with fewer tokens).
**However, if budgets 256 and 512 saturate at the same level, the upper 2 points carry no information.** In that case, **record it as such. The budget grid will not be changed.**
