# Pre-registration Amendment 78: The E5 Conclusion Has Reversed. Identifying the Cause Using All 4 Conditions

**Created**: 2026-10-07
**Targets**: E5 conclusion from amendment 75, central claim of external-review draft v2
**Judgement**: **The E5 conclusion "appraisal dimension directions do not exceed the variance-matched floor" does not replicate.**
**The central claim of draft v2 is retracted.**
**Activation condition**: The diagnostics judgement must not be performed until this file has been committed and pushed.

---

## CA1. Reversed Observation (Llama-3.2-1B, $J^\*=0.05$, full-vocabulary JSD)

| Family | F1 whole-space | F2 axis-orthogonal | F3 in-plane | **F4 variance-matched** |
|---|---|---|---|---|
| **Raw appraisal directions** | 11/13 (+2.21SD) | 12/13 (+2.44) | 10/13 (+2.36) | **11/13 (+2.07SD)** |
| Residualized appraisal directions | 9/13 (+1.88) | 10/13 (+1.88) | 8/13 (+1.87) | 7/13 (+1.60) |
| Emotion category directions | 13/13 (+3.79) | 13/13 (+3.37) | 13/13 (+3.08) | **13/13 (+3.07SD)** |
| Principal component directions | 12/13 (+2.47) | 12/13 (+2.42) | 11/13 (+2.02) | **12/13 (+2.12SD)** |

**Raw appraisal directions exceed F4** (11/13, +2.07 SD). In E5 from amendment 75, the number of cells in which appraisal dimension directions exceeded the floor was 3 out of 12. **The conclusion has reversed.**

**Furthermore, the floor hierarchy is nearly flat.** The pass count barely changes from F1 to F4. The observation reported in amendments 73 and 75 that "even with output perturbation matched, the F3 and F4 floors are approximately twice F1" **does not replicate in the present procedure.**

## CA2. Claims That Are Retracted

The central claim of external-review draft v2 is retracted.

> ~~When output perturbation is matched and a variance-matched in-plane floor is placed, the appraisal dimension directions that prior work has reported as causal levers do not exceed the floor~~

**This claim is not used.** Draft v2 will not be submitted to external review.

The "primary finding" in amendment 75 BX3 is likewise retracted. **The fact of the retraction is preserved in the record, and the E5 numbers are not deleted.**

## CA3. Differences Between E5 and the Present Measurement (4 Conditions)

| # | Condition | E5 (amendment 75) | Present measurement |
|---|---|---|---|
| ① | Appraisal direction | **Single-effect-isolated (residualized)** | **Raw directions** |
| ② | JSD vocabulary range | **Union of top-100 tokens** | **Full vocabulary** |
| ③ | Selection and evaluation | **Select best on selection contexts, evaluate on held-out** | **Maximum of family on held-out set** |
| ④ | Reporting statistic | Difference in floor exceedance count from floor's own rate | Floor exceedance count and standardized excess |

**As long as the condition responsible for the reversal is not identified, neither result can be trusted.**

In judgement REP from amendment 77 BZ4, the raw direction yielded 12/13 under F1, while the residualized direction yielded 6/13. **Condition ① is likely the primary cause**, but ③ also has an effect because taking the family maximum uniformly raises all families.

## CA4. Diagnostic Design

**Treating ①②③ as binary and always reporting both for ④**, $2^3 = 8$ conditions are measured exhaustively.

| Factor | Levels |
|---|---|
| ① Appraisal direction | Raw / Residualized |
| ② JSD | Full vocabulary / Top-100 |
| ③ Selection | With separation / Without separation |

**For each condition, the number of targets for which the raw or residualized appraisal direction exceeds F4, and the median standardized excess, are reported.**

**Judgement DIAG**: Among the 8 conditions, **does any condition exist in which the appraisal direction does not exceed F4?**

- If it exists, **that condition is identified, and the fact that the E5 conclusion depends on it is stated explicitly.** Then, **which condition is appropriate is judged on independent grounds.** It is not chosen based on which result is more favorable
- If it does not exist, **the conclusion is that the E5 conclusion was incorrect, and only the retraction is recorded**

**Validity judgement criteria (fixed before seeing results)**

| Condition | Valid level | Rationale |
|---|---|---|
| ① Appraisal direction | **Raw** | The prior procedure performs residualization before intervention, but the residualization in the present study is orthogonalization against all other 20 dimensions, which is identical to $z_a = (I-P_{-a})v_a$ in the prior work. **Therefore both are reported; neither is declared valid** |
| ② JSD | **Full vocabulary** | Already decided by the criterion in amendment 76 BY5 (full vocabulary if correlation < 0.99) |
| ③ Selection | **With separation** | To cancel the advantage arising from family size. Registered in amendment 73 BV4 |

**② and ③ are decided before seeing the results. ① is reported both ways.**

Therefore **the valid conditions are the 2 conditions "raw or residualized × full vocabulary × with separation."** **These 2 conditions are the primary results; the remaining 6 are reported as sensitivity analyses.**

## CA5. Re-verification of the Floor Hierarchy

The fact that the floor hierarchy was flat is also a target of the diagnostic. **For each condition, the difference in standardized excess between F1 and F4 is reported.** The specific condition under which the "F3 and F4 are approximately twice F1" of amendments 73 and 75 held is identified.

## CA6. What Can Be Written in Each Case

- **If the appraisal direction exceeds F4 under the valid 2 conditions**: "Human appraisal axes exceed the variance-matched floor." **This is consistent with prior work, not in conflict with it.** Only the ordering (emotion > principal component ≈ appraisal) is reported
- **If the appraisal direction does not exceed F4 under the valid 2 conditions**: The conclusion of amendment 75 is reinstated. However **the entire history of the reversal and re-reversal is recorded**
- **If the conclusion differs depending on the level of ①**: "The conclusion changes depending on whether residualization is applied" is reported, and **neither is chosen.** An analysis of what the residualization is removing is placed in the limitations

## CA7. Commitments

- The central claim of draft v2 is retracted, and **the fact of the retraction is preserved in the record**
- E5 numbers are not deleted. The full history of the reversal is written
- The validity judgement criteria were fixed **before seeing the results** (table in CA4). The levels are not chosen based on the results
- All results for all 8 conditions are reported. The 6 non-primary conditions are not hidden
- The fact that the floor hierarchy was flat is also reported
- **External review submission is withheld until this diagnostic is completed**
