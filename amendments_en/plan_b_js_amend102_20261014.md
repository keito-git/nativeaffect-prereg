# Pre-Registration Amendment 102: Category-Level Analysis Is Exploratory (Not Pre-Registered)

**Created**: 2026-10-14
**Type**: **Record of an exploratory analysis that was not pre-registered.** The judgement criteria are not changed in any way.
**Occasion**: Suggestions ② and ③ from external peer review (9th round). Obtainable by re-computation from existing measurements only.

---

## CU1. What Was Computed

The **per-target** values from Gate I (50 null vectors · 9 models · single and syn readouts of readout A) were aggregated across categories. No new measurements were made.

1. Number of models (out of 9) exceeding the matched floor, for each of 13 categories
2. Median excess SD per category
3. Rank correlation between "readout AUC" and "excess SD" per category (Spearman, per model)

## CU2. Results

- Number of models exceeding the floor varies substantially across categories (**2–9/9**), and the ranking is consistent across both readouts.
  surprise and trust yield 9/9; fear 3/9; no-emotion 2/9 (median excess SD −0.16)
- 83/117 (single) and 85/117 (syn) cells in total exceed the floor
- **Rank correlation between readout AUC and excess SD is near zero**: median +0.077 (single, range −0.236 to +0.434, positive sign in 7/9 models) / median +0.143 (syn, positive sign in 6/9 models)

## CU3. Position (Strictly Observed)

- **Not pre-registered.** State "exploratory" in the body text; do not present as a hypothesis test.
- **No p-values are attached.** 13 categories are not independent within a single model, and 9 models also have serial dependence.
- **The judgement population, thresholds, and criteria are not changed in any way.** The judgements of Gates I–III remain as in Amendments 98 and 101.
- The category-level results reinforce but do **not replace** the central claim of this paper (encoding-binding).

## CU4. Why It Is Worth Reporting

The central claim of this paper — that linear decodability and causal steerability are different — has so far been shown only at the encoding level. **That the two are also barely associated at the category level** supports the same conclusion from an independent angle. This includes the direction that fear (easily decodable) is hard to steer while surprise (hard to decode) is easy to steer.

## CU5. Commitments

- Do not drop the exploratory label from the body text
- Do not select only the readout with a favorable-looking sign for the correlation (report both single and syn)
- Do not form a post-hoc hypothesis from category-level results and test it on the same data
