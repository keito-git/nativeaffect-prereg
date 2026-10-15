# Pre-Registration Amendment 99: Additional Experiments for TAFFC Submission — Different Encoding Vocabulary and Multiple Budgets

**Created**: 2026-10-13
**Occasion**: Priority A and B from external peer review (6th round). Submission target decided as IEEE TAFFC (a decision by the principal investigator, 2026-10-13).
**Role**: Establishing the generality of Gate III (whether it depends on the encoding vocabulary) and ruling out the contingency of budget $J^\ast=0.05$.
**Trigger condition**: Do not run the judgement until this file is committed and pushed. **Not yet executed once.**

---

## CR1. Premise: The Activation Cache Was Re-extracted

The activation cache for 9 models lost to a GPU failure was re-extracted in a new container.
**The stimulus corpus was also not included in the backup and was re-acquired**
(`https://www.romanklinger.de/data-sets/crowd-enVent2023.zip`, 6,600 rows · 13 emotions, matching the original).

**It is not guaranteed that the re-extraction is identical to the original.** The extraction script was lost; it was rewritten with the same specification (last token position of the layer, fp16, left-aligned padding, maximum length 256).
**Therefore, values from the additional experiments are not directly linked or compared to previously reported values.**
**Only comparisons that are self-contained within the additional experiments are made** (e.g., encoding vocabulary A vs. encoding vocabulary B measured on the same re-extracted activations).
**The numbers in previously reported tables are not replaced.**

## CR2. Test CE-2 (Different Encoding Vocabulary)

### Question

> Is the attenuation in Gate III a phenomenon specific to the particular encoding of single-character alphabets?

### Construction (fixed in this amendment)

Replace the codebook vocabulary with **digits**. The frame and procedure are identical to codebooks 1 and 2.

```
anger=7, boredom=3, disgust=9, fear=1, guilt=5, joy=8, no-emotion=0,
pride=2, relief=6, sadness=4, shame=... (only 10 single-digit digits available)
```

**Single-digit digits number only 10 for 13 categories.** Therefore two-digit numbers are not used;
instead **10 digits + 3 symbols** are used.

```
anger=7, boredom=3, disgust=9, fear=1, guilt=5, joy=8, no-emotion=0,
pride=2, relief=6, sadness=4, shame=#, surprise=@, trust=+
```

**Codebook 4 (complete transpose)** is also created. No category retains the same symbol.

### Validity check (performed before judgement; same threshold as Amendment 91 CJ1)

At least 7 of 13 categories with AUC > 0.5, and median AUC ≥ 0.65.
**Only models that pass both codebooks are included in the judgement population** (Amendment 92 CK2).

**Digits and symbols may not tokenize to single tokens depending on the tokenizer.**
Apply the rule from Amendment 84 (the first token from which the character can be recovered when decoded); **if token IDs are duplicated across classes, abort.**

### Judgement CE-2 (fixed before seeing the results)

| Result | What can be written |
|---|---|
| Attenuation analogous to alphabets | **Not dependent on encoding vocabulary.** The generality of Gate III's conclusion increases. |
| No attenuation (exceeds floor) | **Was a phenomenon specific to alphabets.** Limit Gate III's conclusion to "when re-encoding to single-character alphabets." |
| Validity check fails | Uninformative. No judgement. |

**Measure alphabets (codebook 1) and digit-symbols (codebook 3) side by side on the same re-extracted activations.** This circumvents the constraint of CR1.

## CR3. Multiple Budgets (Test BUD)

### Question

> Is the conclusion from a single budget $J^\ast = 0.05$ an artifact of the choice of budget?

### Construction

At $J^\ast \in \{0.02, 0.05, 0.10\}$, measure **Gate I (emotion family vs. variance-matched floor) and Gate III
(affect-word readout vs. code readout, same prefix)**.
The floor, statistics, partition, and readout are not changed. Null vectors are F5, 10 per target
(suppressed due to 3 budgets × multiple cells; **state that the count is suppressed**).

**Target**: judgement population 5 models (Llama-3.1-8B, gemma-2-9b, OLMo-2-13B, Ministral-8B,
Mistral-Nemo-12B).

### Judgement BUD (fixed before seeing the results)

| Result | What can be written |
|---|---|
| Gate I pass and Gate III affect-word/code difference same sign across all 3 budgets | **Not budget-dependent.** Not a contingency of $J^\ast=0.05$. |
| Sign changes across budgets | **Budget-dependent.** Limit the conclusion to $J^\ast=0.05$ and report the form of the dependence. |

**Report all values for all budgets.** Do not select favorable budgets.

## CR4. What Is Not Executed

**A different affect dataset is not executed.** An external reviewer indicated it would be effective for TAFFC, but acquisition, label-matching, and re-running all gates would require more than 10 hours and **does not contribute to the central claim (encoding-binding)**.
**State in the limitations that "only a single dataset" is used; execute if required during peer review.**

For the same reason, layer-by-layer analysis, extension to non-affect domains, and Base vs. Instruct are not executed.
**These are written as future work items targeting NMI/JMLR.**

## CR5. Commitments

- **Do not replace the numbers in previously reported tables with values obtained from re-extracted activations.** Additional experiments are limited to comparisons self-contained within them.
- State in the limitations of the body text that it is not guaranteed the re-extraction is identical to the original
- Do not move the validity check threshold after seeing the results
- Do not replace codebooks 3 and 4 after seeing the results
- Report all values for all budgets and do not select favorable budgets
- Write in the body text that a different dataset, layer analysis, and non-affect domains are not executed, and the reasons
