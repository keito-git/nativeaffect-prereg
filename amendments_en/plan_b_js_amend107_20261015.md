# Pre-Registration Amendment 107: Re-Measure Activation-Cluster Control for All 9 Models — Deeper Exploration, Eliminate Blank Rows in Table

**Created**: 2026-10-15
**Target**: Amendments 96, 97, 98 (control SP-act) / Amendment 99 CR5 (commitment not to replace previously reported tables)
**Type**: **Registration before execution.** Do not make the judgement until this file is committed and pushed.
**Trigger condition**: Not yet executed. The judgement criteria and selection rule are not changed.

---

## CZ1. Motivation

The activation-cluster control SP-act was unmeasurable for 4 of 9 models, leaving 4 blank rows in the body-text table (Amendment 98). The concern raised by the principal investigator: "having blanks for unmeasurable models in the table is a problem." **The purpose is to eliminate the blanks; the purpose is not to make the results more favorable.**

The cause of unmeasurability is the cutoff of exploration. The margin left by the selection rule (candidate partition AUC upper bound − emotion partition AUC) is +0.0015 to +0.0034 for the 4 unmeasurable models and +0.0077 to +0.0327 for the 5 measurable models (Amendment 106 CY3). With an acceptance rate of 0.10–0.25%, only 2–5 partitions can be accepted in 2000 trials. **The rule is not too strict; the trials are insufficient.**

## CZ2. What Is Changed (Only One Thing)

**Raise the exploration trial upper limit MAX_TRIES from 2000.** Explore until the target acceptance count N_PART=30 is reached; if not reached, mark unmeasurable per the rule of Amendment 97 CP3 (MIN_ACCEPT=10).

**What is not changed**: selection rule (candidate held-out AUC ≥ emotion partition held-out AUC) / N_PART=30 / MIN_ACCEPT=10 / judgement criterion (over half of targets exceed the 95th percentile; in over half of models) / partition, readout, budget, statistics, and handling of random seeds.

**Deepening the exploration is in the direction of strengthening the control.** More accepted partitions raises the best-of-family floor, which disadvantages the emotion family. It is not an advantagization.

## CZ3. Replace the Previously Reported Table (Partial Release of CR5)

**Re-measuring only the 4 models cannot be placed in the same table.** The 5 already-judged rows were measured on the original lost activations, and Amendment 99 CR1 prohibits placing them alongside re-extracted values. Therefore **all 9 models are re-measured on the same re-extracted activations, and the table is replaced entirely.**

The commitment "do not replace previously reported table numbers" from CR5 is **released for this one table only.** Reasons:

1. The replacement covers **the entire table**; it does not selectively swap favorable rows. The "favorable selective replacement mixing old and new" that CR5 aimed to prevent does not occur.
2. The re-extracted activations have reproduced the previously reported values to 2 decimal places across all 10 cells of codebook 1 and Gate III (Amendment 100 CS1).
3. If not replaced, the blanks remain and **readers can only be told "was unmeasurable."** Producing a result by making it measurable carries more information.

**State in the body text that this table was re-measured on re-extracted activations.**

## CZ4. What Must Be Decided Before Seeing the Results (Most Important)

**Report the results as they come out.** The following is established in advance.

| Possible result | What to write |
|---|---|
| All 9 models measurable, over half pass | The SP-act control holds for all models. Gate II's secondary control achieves its complete form. |
| Measurable but some or all **fail** | **Report as-is.** Write the pass count honestly and limit Gate II's claim to "holds for all models against random partitions; for decodability-equalized control, N/9." |
| Some models still do not reach 10 even with deeper exploration | Those models remain unmeasurable; state the trial count and accepted count. |

**Do not revert to the original table on the grounds that "blanks were better."**
Reverting is selecting the presentation after seeing the results, which is the operation this paper has consistently avoided throughout Gates I–III.

**If the judgement turns negative, weaken the claim in the body text.** Specifically, rewrite "partitions constructed to be more decodable than the emotion partition" in the Discussion to reflect the actual number of passing models. Do likewise for the corresponding passage in the Abstract.

## CZ5. Judgement Statement Decided in Advance

- Report the pass count $k$ and the measurable model count $n$ in the table; write "$k/n$" as-is in the body text
- Write "passed the SP-act control" only when $k > n/2$
- When $n < 9$, do not drop the trial count, accepted count, and candidate AUC upper bound for unmeasurable models

## CZ6. Commitments

- Change nothing other than the exploration trial upper limit
- Do not change N_PART, MIN_ACCEPT, the judgement criterion, or the presentation method after seeing the results
- Do not rewrite fail as "unmeasurable"
- Do not discard the old table (original activations) values; retain them together with a note stating the table was replaced
