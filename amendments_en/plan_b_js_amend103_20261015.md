# Pre-Registration Amendment 103: Correction of Metric Name in Amendment 102; Ruled Out the Stimuli-Count Explanation

**Created**: 2026-10-15
**Target**: Amendment 102 (exploratory category-level analysis)
**Type**: **Correction of a name and a supplementary confirmation that was not pre-registered.** The judgement criteria, population, and numbers are not changed in any way.

---

## CV1. Correction: The AUC Used in the Correlation Is "Readout Discriminability," Not "Decodability from Hidden States"

Amendment 102 CU1 wrote "readout AUC" correctly, but **the manuscript body had described the same quantity as "decodability" and "linear recoverability."** This is an error.

What `roauc.py` (Amendment 88 CG6) computes is **the probability that a stimulus bearing the given label ranks above a stimulus not bearing it, on the readout coordinates of the next-token probability**. It is not the held-out AUC of a linear probe over hidden states. The original script also states "Diagnostic only; it enters no judgement."

**Corrected description**: readout discriminability.
Words that can be read as linear decodability from hidden states (decodability / linear recoverability) have been removed from the body text.

**Why not replace with the true metric**: Producing per-category true probe AUC requires hidden states, but what is on hand is the re-extracted version; per Amendment 99 CR1, it **cannot be paired with the previously reported measurement values (excess SD)**. Therefore the metric is not replaced; the name is corrected.

## CV2. Stimuli Count Does Not Explain Category Differences (Supplementary Confirmation; Not Pre-Registered)

The large variation in floor exceedance across categories (2/9–9/9) could be explained by the argument "the direction estimate is simply more stable for categories with more stimuli."

By the extraction conditions used in the body text: **11 categories have 550 rows; only guilt and shame have 275 rows.**
**Yet guilt and shame, despite having the same count, show floor exceedance of 4/9 and 8/9 — opposite extremes.**
No correlation computation is even necessary: stimuli count cannot explain the category differences.

This is a property of the corpus, not of the analysis of results, and is independent of the re-extracted activations; it does not conflict with CR1.

## CV3. Withdrawal of Overstatements

The manuscript had used the following 2 expressions regarding the results of Amendment 102, which were rolled back to the level the data actually supports.

| Withdrawn expression | Corrected version |
|---|---|
| Steerability is a property of the category **as much as** of the model | Steerability **varies substantially across** emotion categories as well as across models |
| Readout discriminability and causal steerability are **close to unrelated** | ... show **little rank association here** |

"As much as" can be read as comparing the variance of category effects to that of model effects, but that comparison was not made. "Close to unrelated" can be read as demonstrating independence, but what was shown is a weak rank correlation with a median of +0.08.

## CV4. Commitments

- Do not call readout discriminability "decodability from hidden states"
- If true probe AUC is wanted, first re-measure excess SD on the same activations, then pair them
- Report the fact that the stimuli-count explanation was ruled out, together with the explanations that were not ruled out
