# Pre-Registration Amendment 105: Conclusions Are Unchanged Across Budgets (Test BUD · Judgement with 2 Budgets)

**Created**: 2026-10-15
**Target**: Amendment 99 CR3 (Test BUD) / Amendment 104 (loss of $J^\ast=0.02$)
**Judgement**: **For both Gate I and Gate III, the conclusion does not change even when the budget is varied by a factor of 5.
However, this is a judgement based on 2 budgets, not 3.** The reason is written in CX3.

---

## CX1. What Was Measured

$J^\ast=0.02$ lost in Amendment 104 was re-measured (9 models · 2026-10-15 00:54–02:35 UTC),
and placed alongside the remaining $J^\ast=0.10$. **Both use re-extracted activations and 10 null vectors per target**; the comparison is self-contained within the additional experiments (Amendment 99 CR1).

## CX2. Results

### Gate I (Emotion family vs. variance-matched floor)

| Budget | Models satisfying over half | Median excess SD (single/syn) | Max p(G) |
|---|---|---|---|
| $J^\ast=0.02$ | **9/9** | +2.92 / +2.78 | 0.0005 |
| $J^\ast=0.10$ | **8/9** | +2.88 / +2.82 | 0.0005 |

The only model that falls below over half at the larger budget is Gemma-2-9B, which passes 10/13 and 11/13 at the smaller budget.

### Gate III (Affect-word readout vs. code readout · codebook 1)

| Budget | Median pairwise difference | All models positive | Models where code readout meets count criterion |
|---|---|---|---|
| $J^\ast=0.02$ | **+1.79 SD** | Yes (5/5) | **0/5** |
| $J^\ast=0.10$ | **+2.33 SD** | Yes (5/5) | **0/5** |

**The judgement condition of Amendment 99 CR3 — "same sign for the affect-word/code difference across all budgets" — is satisfied for both budgets.**

## CX3. Explicit Statement That This Is Not 3 Budgets

CR3 registered measurement at 3 points: $\{0.02, 0.05, 0.10\}$. $J^\ast=0.05$ is the main result of the body text, but **it was measured on the original activations, and per Amendment 99 CR1, cannot be placed alongside the re-extracted values.**
Re-measuring $J^\ast=0.05$ on the re-extracted activations would yield 3 points, but this is not done in this amendment.

Therefore the claim is limited to **"the conclusion does not change across 2 budgets (a 5-fold range)";
"passed all 3 budgets" is not written.**

## CX4. Incorporation into Body Text

- Changed the limitation "single layer and single budget" to **"single layer"**, and added: the budget was varied, the conclusion does not change across both gates, **and the values were obtained on re-extracted activations and are not combined with the body-text numbers**.
- All numbers are tabulated in Supplementary S9 (code-generated; no hand-entry).

## CX5. Commitments

- Do not write "passed all 3 budgets"
- Do not select favorable budgets; include all models' values for both budgets
- Do not mix values obtained from re-extracted activations into the body-text tables
