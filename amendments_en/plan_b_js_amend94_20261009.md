# Pre-Registration Amendment 94: Add Positive Control and Same-Context Control to Gate III. Correct Terminology and Claim Strength.

**Created**: 2026-10-09
**Occasion**: External peer review (2026-10-09, 5th round). Feedback from passing v5.
**Role**: **Make CM1 and CM2 preconditions for the central claim of encoding-binding.**
**Trigger condition**: Do not run the judgement until this file is committed and pushed. **Not yet executed once.**

---

## CM1. Positive Control (Test PC-code) — Highest Priority

### Feedback

> Gate III is a negative result. A reviewer can ask:
> "Have you confirmed that code output can be moved by activation intervention in that layer at all?"
> **Being able to retrieve the codebook is separate from being able to manipulate code readout at that intervention site and budget.**

**The feedback is correct.** The current v5 does not show that code readout **can be moved** by the intervention.
Without showing this, the explanation "the measurement system was too blunt" cannot be excluded.

### Construction (fixed in this amendment; defined before seeing the results)

Intervene with the gradient direction for code readout at the same layer, the same budget.

$$g_e = \mathrm{normalise}\Big(\nabla_h\Big[\log p(c_e) - \tfrac{1}{13}\sum_j \log p(c_j)\Big]\Big)$$

where $c_e$ is the token currently assigned to category $e$ in the codebook.
The gradient is evaluated over selected contexts and averaged before normalization.
**The floor, statistics, budget, layer, and readout are completely identical to the emotion family**, and the floor generates F5 matched to each $g_e$ (10 null vectors per target).

**This direction is the steepest-ascent direction under the Euclidean metric and is not the optimal direction (natural gradient) under a fixed JSD budget.** It is used as a lower bound.

### Judgement PC-code (fixed before seeing the results)

**The gradient family exceeds the best of the F5-matched family on code readout**
(over half of the 13 targets, and $p_G<0.01$), **in over half of the models in the population**.

| Judgement PC-code | What can be written |
|---|---|
| Pass | **Code readout can be manipulated by intervention.** Therefore the negative result of Gate III cannot be explained by bluntness of the measurement system. **The precondition for the encoding-binding claim is satisfied.** |
| Fail | **Code readout cannot be manipulated at this intervention site and budget.** Gate III is uninformative; **do not claim encoding-binding.** Record that the intervention site or budget needs to be changed. |

**If the result is fail, withdraw the central claim.** This is written here first.

## CM2. Same-Context Control (Test SC) — Highest Priority

### Feedback

> In Gate III, the codebook is added to the prompt.
> **Besides "the encoding changed," the explanation "the codebook in the prompt altered the hidden-state geometry and the original affect direction stopped working" remains.**
> If both affect-word readout and code readout are measured within the same codebook context, the cause can be attributed directly to output encoding itself rather than context shift.

**The feedback is correct.** The current comparison changes both context and readout simultaneously.

### Construction (fixed in this amendment)

Use two frames with an **identical prefix**. The codebook is presented in both.

| Symbol | Frame | Readout |
|---|---|---|
| **SC-code** | `Code: {table}\n\nEvent: {text}\n\nThe code is` | 13 codes |
| **SC-word** | `Code: {table}\n\nEvent: {text}\n\nThe emotion is` | 13 affect words |

The prefix `Code: {table}\n\nEvent: {text}\n\n` is **completely identical**; the only differences are the final cue and the readout vocabulary.

**The direction, layer, floor, and statistics are not changed at all.** The budget is re-calibrated per frame.

### Judgement SC (fixed before seeing the results)

| SC-word | SC-code | What can be written |
|---|---|---|
| Exceeds | **Does not exceed** | **The cause is output encoding.** In the same context, affect words are moved while codes are not. **Context shift cannot explain it. The central claim is established.** |
| Does not exceed | Does not exceed | **The codebook context itself nullifies the affect direction.** The cause is not encoding but context. **Do not claim encoding-binding; report as context-dependence.** |
| Exceeds | Exceeds | The negative result of Gate III stems from a trivial difference between the frames (presence vs. absence of `Answer with the code only.`). **Reconsider.** |
| Does not exceed | Exceeds | Unexpected. Report as-is. |

**(ii): Rewrite the central claim from "encoding-binding" to "context-dependence."** This is written here first.

## CM3. Scope of Execution

**Judgement population: 5 models** (Llama-3.1-8B, Ministral-8B, Mistral-Nemo-12B, OLMo-2-13B, gemma-2-9b).
The 4 out-of-population models are excluded because their codebooks cannot be retrieved; this is recorded.

- CM2 (SC-code, SC-word): both codebooks
- CM1 (PC-code): codebook 1 only (a positive control does not need 2 codebooks)

Save raw measurements to `raw_<tag>_sc<N>.npz` and `raw_<tag>_pc1.npz`.

## CM4. Terminology Change (Feedback point 5)

"Layer 1 / layer 2 / layer 3" is confusable with Transformer layers (layer 12, layer 24, etc.).

> **Gate I (variance-matched) / Gate II (partition-matched) / Gate III (encoding transfer)**
> *Control Gate I / II / III*

Unify throughout: body text, tables, and abstract.

## CM5. Reduce Claim Strength (Feedback points 3 and 4)

### Weaken "bears category identity"

Gate II compares against random partitions, and **random partitions have lower decodability than the true emotion partition**.
We acknowledge this ourselves. Therefore "the direction bears category identity" is too strong.

**Replace the single-sentence claim with the following.**

> **A steering effect specific to the human emotion partition exists, but that effect does not transfer across encodings.**
> *Emotion steering is specific to the human emotion partition, yet remains bound to its
> output encoding.*

**Also change "what the direction bears is the identity of the category" in the Discussion to "the effect is specific to the human emotion partition."**

### Revise "the three layers are empirically independent"

"Independent" is readable as statistical independence. What was shown is

$$\text{Gate I pass} \wedge \text{Gate II pass} \nRightarrow \text{Gate III pass}$$

**Change to: "The three gates are empirically non-redundant and do not imply one another."**

### Tone down the selling of $p_G$

The floor for Gate I uses 10 null vectors per direction; 4000 bootstraps do not mean 4000 independent directions.
**Do not treat $p_G = 0.0005$ as a rigorous Monte Carlo probability; instead write "the bootstrap-tail estimate reached its numerical lower bound."**

### Condition the PC result

Add **"under the per-term variance-matching criterion of this study"** explicitly to "no strictly-matched floor exists in principal component directions."

## CM6. Number of Null Vectors and Scoring Context (Feedback point 6)

Execute the increase registered in Amendment 91 CJ4 (F5 to 50 null vectors, LP to 150 partitions).
In addition, **draw 256 fresh rows from unused data as scoring context and re-evaluate once**
(Amendment 91 CJ6). **Apply with the procedure frozen; do not redraw the partition.**

## CM7. Handling of Appendices in the Submission Version (Feedback)

**In the external-review version, keep Appendices A and B at their current length.**
**In the submission version, consolidate "deviations from pre-registration, implementation corrections, and re-run analyses" into a concise audit table, and place the full history in the repository.** This preserves transparency while maintaining focus.
**It is a move, not a deletion.** State the location of the full history in the body text of the submission version.

## CM8. Execution Order

```
① Text revisions for CM4 and CM5 (immediate)
② CM1 (positive control) + CM2 (same-context control)   ← Highest priority; proceed to submission after this passes
③ CM6 (number of null vectors · 256-row scoring context)
④ Structural-match partition control (Amendment 91 CJ3)
```

**Do not produce the submission version until ② is complete.**

## CM9. Commitments

- If CM1 fails, withdraw the encoding-binding central claim
- If CM2 yields case (ii), rewrite the central claim to "context-dependence"
- Do not change the judgement criteria, frames, or gradient definition after seeing the results
- Weaken the single-sentence claim to "specific to the human emotion partition"
- Change "independent" to "non-redundant; do not imply one another"
- Do not sell $p_G$ as a rigorous probability
- When consolidating appendices into an audit table for the submission version, treat it as a **move, not a deletion**, and state the location
