# Pre-Registration Amendment 95: Results of Positive Control and Same-Context Control. Encoding-Binding Established; "No Transfer" Is an Overstatement.

**Created**: 2026-10-10
**Target**: Amendment 94 CM1 (positive control) and CM2 (same-context control)
**Judgement**: **CM1 pass (5/5 cells). CM2 yields branch (i). The cause is output encoding, not the measurement system's bluntness and not context shift.
However, transfer is not "absent" but "strongly attenuated." The wording of the claim is revised.**
**Trigger condition**: Do not produce the submission version until this file is committed and pushed.

---

## CN1. Positive Control (CM1) — Pass

The gradient direction for code readout was applied via intervention at the same layer, the same budget, the same floor, and the same statistics.

| Model | Gradient family | Emotion family (same conditions) |
|---|---|---|
| Mistral-Nemo-12B | **13/13 (+7.76)** $p$=0.0005 | 6/13 (+1.55) |
| Llama-3.1-8B | **13/13 (+6.39)** $p$=0.0005 | 2/13 (+0.62) |
| OLMo-2-13B | **13/13 (+5.95)** $p$=0.0005 | 3/13 (+1.30) |
| gemma-2-9b | **13/13 (+4.97)** $p$=0.0005 | 4/13 (+0.59) |
| Ministral-8B | **13/13 (+4.92)** $p$=0.0005 | 2/13 (+0.02) |

**5/5 cells pass. Median excess SD: +5.95; median count: 13.0/13.**
No non-finite gradients occurred; gradient norms ranged from 3.0×10¹ to 9.1×10¹.

**Code readout can be manipulated at this intervention site and at this budget.**
Therefore the negative result of Gate III **cannot be explained by bluntness of the measurement system.**
The precondition in Amendment 94 CM1 is satisfied.

## CN2. Same-Context Control (CM2) — Branch (i)

The prefix `Code: {table}\n\nEvent: {text}\n\n` was made **completely identical**;
only the final cue and the readout vocabulary were changed.

| Model | Codebook | Affect-word readout | Code readout |
|---|---|---|---|
| Mistral-Nemo-12B | 1 | **11/13 (+2.82)** Pass | 6/13 (+1.55) Fail |
| Mistral-Nemo-12B | 2 | **11/13 (+2.82)** Pass | 4/13 (+0.99) Fail |
| Llama-3.1-8B | 1 | **10/13 (+3.19)** Pass | 2/13 (+0.62) Fail |
| Llama-3.1-8B | 2 | **10/13 (+2.75)** Pass | 2/13 (+0.10) Fail |
| OLMo-2-13B | 2 | **10/13 (+2.84)** Pass | 3/13 (+0.65) Fail |
| OLMo-2-13B | 1 | **9/13 (+2.46)** Pass | 3/13 (+1.30) Fail |
| Ministral-8B | 1 | **9/13 (+2.74)** Pass | 2/13 (+0.02) Fail |
| Ministral-8B | 2 | **9/13 (+2.62)** Pass | 2/13 (+0.35) Fail |
| gemma-2-9b | 1 | 6/13 (+1.53) Fail | 4/13 (+0.59) Fail |
| gemma-2-9b | 2 | 6/13 (+1.58) Fail | 2/13 (+0.46) Fail |

**Affect-word readout: pass 8/10 cells, median excess SD +2.74, median count 9.5/13.**
**Code readout: pass 0/10 cells, median excess SD +0.61, median count 2.5/13.**

**Within the same context, the affect direction moves affect words strongly and moves codes barely at all.**
Therefore the cause is **not a change in hidden-state geometry caused by placing the codebook in the prompt, but output encoding itself.** This corresponds to branch (i) of Amendment 94 CM2.

### State the exception for gemma-2-9b explicitly

**For gemma-2-9b, affect-word readout also fails to meet the count criterion** (6/13; over half requires 7).
Since the count was 7/13 in the context without a codebook, **codebook context does reduce the effect on affect words somewhat.**
However, $p_G$ is 0.0005 (lower bound) and excess SD is +1.53, which is **2.6 times the code readout in the same context (+0.59).**
**The contribution of context is not denied. Context reduces the effect, but the gap due to encoding is larger.**

## CN3. "Does Not Transfer" Is an Overstatement. Revise.

**$p_G$ falls below 0.01 in 7 of the 10 code-readout cells**
(Mistral-Nemo both codebooks, Ministral both codebooks, OLMo-2-13B both codebooks, gemma-2-9b codebook 1).
At the level of aggregate statistics, **some models do exceed the floor on code readout.**
They simply fail to meet the count criterion.

**Therefore "does not transfer across encoding" is inaccurate.** The accurate statement is:

> **Transfer is strongly attenuated.** In the same context, excess SD is +2.74 for affect words versus +0.61 for codes
> (**approximately 1/4.5**); the count criterion (over half of 13 targets) is met in 0 of 10 cells.
> The gradient direction reaches 13/13 · +5.95 in the same cells.

**From this amendment onward, do not write "does not transfer"; write "strongly attenuated" or "largely bound to encoding."**

### Single-sentence claim (final)

> **A steering effect specific to the human emotion partition exists, but its effect is largely bound
> to the output encoding and transfers only weakly to a re-encoding of the same categories.**
>
> *Emotion steering is specific to the human emotion partition, yet its effect is largely bound
> to the output encoding and transfers only weakly to a re-encoding of the same categories.*

## CN4. Alternative Explanations That Were Ruled Out

| Alternative explanation | Basis for ruling out |
|---|---|
| Measurement system is blunt | Gradient direction reaches 13/13 · +5.95 in the same cells (CN1) |
| Codebook context nullified the affect direction | In the same context, affect words yield 9.5/13 · +2.74 (CN2) |
| Readout does not track categories | Population is limited to models that can retrieve the codebook (Amendment 92). gemma-2-9b and Mistral-Nemo have mode match 13/13 |
| Floor variance is not matched | Per-term matching with eigenvalues; deviation in fit covariance 2.4e-07; median 0.99 on held-out rows; null-space proportion 0 (Amendment 91 CJ5) |
| Passing 13 partitions is sufficient | All 30 random partitions of the same granularity exceeded across all 9 models (Amendment 90) |
| Due to effect size | Gates I with 9/9 models (Amendments 81, 90) |

**An effect that ruled out 6 alternative explanations in sequence drops to 1/4.5 when the encoding is changed.** This is the core of this study.

## CN5. Commitments

- **Do not write "does not transfer." Write "strongly attenuated."**
- Write in the body text that $p_G$ falls below 0.01 in 7/10 cells of code readout
- State explicitly that gemma-2-9b also fails to meet the count criterion for affect-word readout, and **do not deny the contribution of context**
- Reiterate that the gradient is steepest-ascent under the Euclidean metric and is not the natural gradient
- Include the CN4 table in the body text, explicitly stating what was and was not ruled out
