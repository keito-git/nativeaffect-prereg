# Pre-registration Amendment 84: "Phi Family Is Degenerate" Was My Bug. The Global Null T Was Also Invalid

**Created**: 2026-10-08
**Occasion**: The duplicate readout token check introduced in amendment 82 excavated another defect
**Judgement**: **The description "Phi-3-medium is degenerate" in amendments 80 and 81 is incorrect. It is retracted. The p-values from the global null T are also invalid and will not be used.**
**Activation condition**: Remeasurement judgements must not be performed until this file has been committed and pushed.

---

## CC1. Implementation Defect 10th Instance: All Classes in Phi-3 Had the Same Token

In amendment 82, the `no-emotion` assignment was corrected and a check was added to raise an exception if token IDs were duplicated across classes. That check fired for Phi-3-medium.

```
Empty class in readout: anger
```

The cause was measured. The number of distinct leading token IDs for the 13 classes was counted for each model.

| Model | Distinct count | Decomposition of `" anger"` |
|---|---|---|
| **Phi-3-medium-4k-instruct** | **1/13** | `[29871, 27343]` = `['', 'anger']` |
| Llama-3.2-1B-Instruct | 13/13 | `[19788]` = `[' anger']` |
| gemma-2-2b-it | 13/13 | `[23790]` = `[' anger']` |
| Mistral-Nemo-Instruct-2407 | 13/13 | `[26202]` = `[' anger']` |

**Phi-3's SentencePiece tokenizer outputs a bare word-boundary fragment (id 29871, decoded as an empty string) before the word.** The old code took `cc[0]`, so **the readout coordinates of all 13 classes became the same token.** If 13 coordinates are identical, the difference vector is constant, and centering ($I - \mathbf{1}\mathbf{1}^\top/13$) makes it **zero.** The observed signature ($|S| \approx 7\times10^{-4}$, all families 0/13, standardized excess $\pm 0.00$) is exactly this.

### Statements That Are Retracted

- "Phi-3-medium is degenerate — excluded from judgement" in amendments 80 and 81
- "The fact that 2 models from the Phi family have the same signature is written in limitations as-is" in amendment 81
- Section 4.6 and the second limitation in section 5.4 of draft v3 ("2 models from the Phi family are unmeasurable")

**All of these are properties of my token extraction error, not the model.** It is highly likely (unconfirmed; will be confirmed) that Phi-3.5-mini's 0/13 across all families in stage E5 was also caused by the same issue.

### Fix

The leading token is changed to "the first token that has characters remaining when decoded."

```python
for form in (" " + w, w):
    for t in tok.encode(form, add_special_tokens=False):
        if tok.decode([t]).strip():
            return int(t)
```

The other 8 models have the leading token as the word itself, so this change does not alter their IDs. **Only Phi-3-medium requires remeasurement, and it will be executed.**

## CC2. Implementation Defect 11th Instance: The Global Null T p-values Were Invalid

The global null introduced in amendment 83 CB7 computed a threshold $q_{0.95,e}$ for each target from draws of the floor family, then built the null distribution of $T = \#\{e : S_e > q_{0.95,e}\}$. In the implementation, **the draws used to compute the threshold and the draws used to count $T$ were the same.**

Since the family best attaches to the "strongest floor direction," the maximum value in the floor family **ties at the same value.** As a result $q_{0.95,e}$ coincides with the observed maximum, and under the strict inequality $>$ nobody can exceed it.

**Measured:** OLMo-2-13B, emotion, F5: `T_null_mean = 0.000`; appraisal: `0.100`. The expected value of the null $T$ under a continuous distribution should be $13 \times 0.05 = 0.65$, but it is nearly 0. Therefore $p_T = P(T_{\mathrm{null}} \ge T_{\mathrm{obs}})$ **becomes an excessively lenient test that is significant even for $T_{\mathrm{obs}} \ge 1$.**

### Statements That Are Retracted

What was reported on 2026-10-07:

> "Not that 'only the emotion axis exceeds the floor and the appraisal axis does not,' but rather 'both exceed, but the emotion axis is overwhelmingly stronger'"

is based on **this invalid p-value. It is retracted.** Whether the appraisal dimension exceeds the global null is not claimed until it is re-measured with a corrected statistic.

### Fix (Fixed in this amendment. Defined before seeing results)

$B = 4000$ floor family draws are generated; **the first 2000 are used to define thresholds and moments, and the latter 2000 for evaluation.**

1. **Count**: $\mathrm{thr}_e = q_{0.95}(\text{first half}_e)$, $T_{\mathrm{obs}} = \#\{e: S_e > \mathrm{thr}_e\}$, $T_{\mathrm{null}}$ computed from the second half. $p_T = (1 + \#\{T_{\mathrm{null}} \ge T_{\mathrm{obs}}\})/(1 + 2000)$
2. **Continuous statistic**: From the first half, $\mu_e, \sigma_e$ are taken and $G = \sum_e (S_e - \mu_e)/\sigma_e$ is computed. $G$ is continuous and does not have the tie problem. $p_G = (1 + \#\{G_{\mathrm{null}} \ge G_{\mathrm{obs}}\})/(1 + 2000)$
3. **Sanity check**: The minimum number of distinct values in the floor distribution and the minimum standard deviation are reported alongside

**$G$ is the primary global statistic.** $T$ is reported alongside for readability, but the fact that it can be affected by ties is stated explicitly.

## CC3. Implementation Defect 12th Instance: Raw Measurements Were Not Saved

The old `stageC3.py` wrote only summary statistics to JSON and did not save per-direction, per-floor measurements. As a result, the fix in CC2 **required rerunning the GPU measurements** (approximately 5 hours).

**Fix**: Measurement and statistics are separated.

- `stageC3.py` measures and saves `raw_<tag>.npz` (arrays over family × readout × {target sel/test, F5, F4}) and `meta_<tag>.json`
- `c3stats.py` computes all statistics from the npz. **Revising statistics does not require GPU**

**Going forward, measurement scripts always save raw measurements.**

## CC4. Scope of Remeasurement

**All 9 models are remeasured.** Measurements are reproducible with the same seed and the same order of random number consumption, but remeasurement is needed because raw data saving is required. Phi-3-medium also incorporates the fix from CC1.

## CC5. Record: The Check Excavated the Defect

The "raise an exception if token IDs are duplicated across classes" check written in amendment 82 was written to fix the `no-emotion` error. That check **excavated a separate, heavier defect (all classes having the same token in Phi-3).** 

**Exception-raising checks catch defects other than the one they were written for.** Something that had been written in the limitations section as "a degenerate model" was my own bug. **Before reporting a property as belonging to the model, suspect the measurement system.**

## CC6. Commitments

- Retract the description "Phi family is degenerate" in amendments 80 and 81 and draft v3; preserve the retraction in the record
- Retract the 2026-10-07 report that "the appraisal axis also exceeds the global null"
- $G$ is the primary global statistic; $T$ is reported alongside only
- Confirm whether the Phi-3.5-mini 0/13 in stage E5 is caused by the same issue and report the result
- Measurement scripts save raw measurements. Statistics revision does not require rerunning measurements
- This is recorded in Appendix B as implementation defect 10th instance (leading token), 11th instance (global null threshold), and 12th instance (raw data not saved)
