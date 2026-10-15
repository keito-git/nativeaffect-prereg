# Pre-Registration Amendment 108: Activation-Cluster Control Is Measurable for All 9 Models; 8/9 and 9/9 Pass

**Created**: 2026-10-15
**Target**: Amendment 107 (registration of re-measuring all 9 models with deeper exploration)
**Judgement**: **Measurable: 9/9. Pass: 8/9 for single-token readout; 9/9 for synonym-set readout.**
**Compliance with registration**: Executed after pushing Amendment 107 (`2646e2a` · 2026-10-15 04:3x UTC). Criterion unchanged.

---

## DA1. What Was Executed

As per Amendment 107 CZ2, **only the exploration trial upper limit was changed**. The selection rule (candidate partition held-out AUC ≥ emotion partition held-out AUC), N_PART=30, MIN_ACCEPT=10, judgement criterion, and proposal distribution were not changed.

Exploration does not use the model's forward pass, so it was run with 24 shards in parallel.
**The shard seed divided only the proposal random sequence and was not allowed to affect the 3-fold data split** (during implementation, an error was introduced that also moved the partition, causing the emotion partition's AUC to shift from 0.9772 to 0.9734; this was corrected).
The aggregation method is deterministic (concatenate in ascending shard order, take the first 30).

## DA2. Exploration Results (All 9 Models Reached 30)

| Model | Accepted / Trials | Candidate AUC upper bound (old → new) |
|---|---|---|
| Llama-3.2-1B | 30/615 | 0.9873 → 0.9872 |
| Gemma-2-2B | 30/1503 | 0.9798 → 0.9837 |
| Phi-3-medium | 30/1435 | 0.9828 → 0.9919 |
| OLMo-2-7B | 30/14016 | 0.9819 → 0.9809 |
| Gemma-2-9B | 30/14150 | 0.9803 → 0.9865 |
| **OLMo-2-13B** | 30/13500 | 0.9754 → **0.9802** |
| **Mistral-Nemo-12B** | 30/15000 | 0.9801 → **0.9851** |
| **Llama-3.1-8B** | 30/16500 | 0.9686 → **0.9730** |
| **Ministral-8B** | 30/16500 | 0.9790 → **0.9825** |

**The control is stronger than before** (the upper bound of the candidate decodability has risen). This is not an advantagization.

## DA3. Judgement

| Model | single | syn |
|---|---|---|
| Llama-3.2-1B | 8/13 (+3.05) Pass | 8/13 (+3.45) Pass |
| Llama-3.1-8B | 7/13 (+2.05) Pass | 7/13 (+1.72) Pass |
| OLMo-2-7B | 10/13 (+3.34) Pass | 9/13 (+3.39) Pass |
| OLMo-2-13B | 9/13 (+2.81) Pass | 8/13 (+2.42) Pass |
| Gemma-2-2B | 11/13 (+7.82) Pass | 12/13 (+8.26) Pass |
| Gemma-2-9B | 7/13 (+2.17) Pass | 8/13 (+2.16) Pass |
| Ministral-8B | 8/13 (+2.67) Pass | 7/13 (+2.51) Pass |
| Mistral-Nemo-12B | 8/13 (+2.23) Pass | 8/13 (+2.24) Pass |
| **Phi-3-medium** | **6/13 (+1.18) Fail** | 7/13 (+1.48) Pass |

**Pass: single 8/9 · syn 9/9.** Both readouts satisfy the pre-registered "over half of models."

**The fail is not concealed.** Phi-3-medium falls 1 short of over half on single-token readout.
This model has a candidate AUC upper bound of 0.9919 — the highest of all models — meaning **it fails on the model where the control is strongest.**
This was stated explicitly in the body text with the model name.

## DA4. Differences from the Old Table (Entire Table Replaced)

Even the values of the 5 previously judged models changed (e.g., Llama-3.2-1B 9/13→8/13, Gemma-2-9B 9/13→7/13, Phi-3-medium 7/13→6/13). There are two reasons: **the control became stronger** and **the activations were re-measured using re-extracted activations**. Per the registration in Amendment 107 CZ3, the entire table is replaced and the body text states that it was re-extracted. The old table values are retained in this amendment.

## DA5. Incorporation into Body Text

- Table IV replaced with numbers in all 9 rows (blank rows eliminated)
- "5 of 5 models" → "8 (single) / 9 (syn) of 9 models" updated in Abstract, Results, Discussion, Conclusion, and Figure 1
- Limitation (third point) rewritten from "unmeasurable" to "**exploration cost differs by one order of magnitude across models**"
- Deviation description in Method 3.6: added "**this threshold was in the end never applied even once**"
- Sensitivity analysis from Amendment 106 (counting 4 models as fail, yielding 5/9) removed from body text since its premise is now gone

## DA6. Commitments

- Do not drop Phi-3-medium's fail result
- Do not discard the old table values; retain them in this amendment
- Do not write "all 9 models pass" (single is 8/9)
