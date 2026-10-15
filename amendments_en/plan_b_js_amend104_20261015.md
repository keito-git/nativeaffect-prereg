# Pre-Registration Amendment 104: Gate I Budget Sweep Lost One Budget (Filename Collision)

**Created**: 2026-10-15
**Target**: Amendment 99 CR3 (Test BUD · multiple budgets)
**Type**: **Record of a loss.** The judgement criteria, population, and body-text numbers are not changed in any way.
**Impact on body text**: None (the budget sweep was not incorporated into the body text).

---

## CW1. What Happened

Amendment 99 CR3 registered measurement at $J^\ast \in \{0.02, 0.05, 0.10\}$ for Gates I and III.
The additional experiments were fully completed at 2026-10-14 17:33 UTC, but **the Gate I output filenames (`stageC3.py`) did not include the budget**.

```
raw_{tag}{tail}.npz        # tail encodes only the null-vector count and scoring set
```

As a result, the $J^\ast=0.02$ output for the same model was overwritten by the $J^\ast=0.10$ output,
and **the raw data for $J^\ast=0.02$ was lost for all 9 models.** Only $J^\ast=0.10$ remains.

The Gate III side (`stageSC2.py`) includes `_b0.02` / `_b0.1` in the name, so **both are intact** (20 vectors each).

## CW2. No Impact on Body Text

- **The main results of the body text ($J^\ast=0.05$) are backed up in a separate directory and are intact.** The overwriting occurred only in the budget-sweep directory in the new container.
- The budget sweep was not incorporated into the body text (from the beginning of Amendment 99, it was "record only").
- Therefore **there are no numbers that need to be replaced or retracted**.

## CW3. Relation to the Commitments

CR3 committed to "report values for all budgets; do not select favorable budgets."
**Reporting Gate I budget-dependence with only one budget on hand would violate this commitment.**
Therefore the two options currently available are, and **reporting only $J^\ast=0.10$ is not done**:

1. Re-measure $J^\ast=0.02$ and report both (9 models · approximately 2 hours · GPU currently free)
2. Do not report Gate I budget sweep (Gate III side has both budgets, so reporting that is possible)

**The decision is deferred to the principal investigator.** This does not affect the completeness of the body text, so it is not a reason to delay submission.

## CW4. Prevention

Added the budget to the output names of `stageC3.py` (for the default $J^\ast=0.05$, the conventional name is retained without conflicting with existing artifacts). The 18 remaining $J^\ast=0.10$ files were also backed up under names with `_b0.1` before being overwritten.

**Lesson**: Always encode swept parameters in the output name.
`stageSC2.py` did this; `stageC3.py` did not, and when the same sweep was run through two pathways, only one was corrupted. **Before a sweep, verify that the output name encodes that axis.**
Related: the same failure mode as the defect in Amendment 84 where raw measurement values were not saved.

## CW5. Commitments

- Do not write the result for $J^\ast=0.10$ only as evidence for budget-dependence in the body text
- If re-measured, report both budgets side by side
