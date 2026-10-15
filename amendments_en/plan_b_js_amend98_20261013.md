# Pre-Registration Amendment 98: SP-act Passes. Decodability Cannot Explain the Intervention Effect.

**Created**: 2026-10-13
**Target**: Control SP-act (activation-cluster partition) from Amendments 96 CO2 and 97
**Judgement**: **5/5 measurable models pass (both readouts). Decodability cannot explain it.
However, 4 models are unmeasurable, and that bias is also reported.**
**Trigger condition**: Do not submit v6 for external peer review until this file is committed and pushed.

---

## CQ1. Results (Rules from Amendment 97 CP3 · 2000-trial exploration)

The control used activation-cluster partitions; only those with **held-out AUC at least equal to the emotion partition's** were accepted.
Models with fewer than 10 accepted partitions were excluded as unmeasurable (Amendment 97 CP3).

| Model | Emotion partition AUC | Accepted | Trials | Candidate AUC upper bound | single | syn |
|---|---|---|---|---|---|---|
| Gemma-2-2B | 0.9684 | 30 | 84 | 0.9798 | **11/13 (+6.25)** | **12/13 (+6.08)** |
| Llama-3.2-1B | 0.9546 | 30 | 38 | 0.9873 | **9/13 (+3.16)** | **9/13 (+2.88)** |
| OLMo-2-7B | 0.9718 | 30 | 1460 | 0.9819 | **9/13 (+3.05)** | **9/13 (+3.21)** |
| Gemma-2-9B | 0.9726 | 30 | 1087 | 0.9803 | **9/13 (+1.85)** | **9/13 (+1.67)** |
| Phi-3-medium | 0.9729 | 30 | 175 | 0.9828 | **7/13 (+1.57)** | **7/13 (+1.63)** |
| OLMo-2-13B | 0.9724 | **5** | 2000 | 0.9754 | Unmeasurable | Unmeasurable |
| Llama-3.1-8B | 0.9652 | **4** | 2000 | 0.9686 | Unmeasurable | Unmeasurable |
| Ministral-8B | 0.9775 | **3** | 2000 | 0.9790 | Unmeasurable | Unmeasurable |
| Mistral-Nemo-12B | 0.9772 | **2** | 2000 | 0.9801 | Unmeasurable | Unmeasurable |

**Measurable: 5/9 models. single: 5/5 pass; syn: 5/5 pass.**
Median excess SD: single +3.05, syn +2.88. $p_G$ is 0.032 (lower bound for 30 null vectors) for all cells.

## CQ2. What Can Be Said

The control partitions are **more decodable than the emotion partition** (candidate upper bound 0.9686–0.9873 vs. emotion 0.9546–0.9775).
This is guaranteed by the selection rule. **Yet the emotion partition beats the control in terms of intervention effect.**

> **The explanation "it worked because the partition was predictable" does not hold.**

The claim of Amendment 90 can be strengthened as follows.

| Before | From this amendment onward |
|---|---|
| Human-defined emotion partition exceeds **arbitrary** partitions with matched class sizes | Human-defined emotion partition also exceeds partitions whose **decodability is at least equal to the emotion partition's**. **Not explained by decodability.** |

**However, do not yet write "special among all alternative partitions."** What was tested is 2 families: random partitions (Amendment 90) and activation-cluster partitions (this amendment).

## CQ3. Be Honest About the 4 Unmeasurable Models

**The 4 models reached only 2–5 accepted partitions even after 2000 trials.** The reason is, as described in CP2, that the decodability of the emotion partition is close to the upper bound reachable by activation clusters.
The null variance collapses, the standardized excess diverges, and $p_G$ is fixed at 0.5, making the statistic undefined.

**State the bias explicitly.** The emotion partition AUC of the 4 unmeasurable models is 0.9652, 0.9724, 0.9772, and 0.9775, which **is skewed toward the higher end compared to the measurable 5 models' range of 0.9546–0.9729.**
In other words, **models for which the emotion partition is especially decodable cannot obtain a control that exceeds it and therefore cannot be tested.**
This is a limitation on the generalizability of the results; **I do not deny the possibility that the models that were testable were "relatively easy to test."**

## CQ4. Report the Two "Unconstructable" Results Together

| Control | Result | Implication |
|---|---|---|
| Vocabulary-structure clusters (Amendment 96 CO1) | **Unconstructable** (upper bound 0.881 vs. emotion 0.955) | The emotion partition has decodability unreachable from vocabulary structure |
| Activation clusters (this amendment) | Constructable in 5 models; **difficult to construct** in 4 | The emotion partition is close to the upper bound of activation clusters |

**These are descriptions of the position of the emotion partition's decodability, not intervention-effect claims.**
**Do not conflate them** (commitment in Amendment 96 CO5).

## CQ5. Final State of All Gates

| Gate / control | Null | Result |
|---|---|---|
| **I Variance-matched** | F5 50 vectors | **Pass**. Effect size is at most 0.9 SD lower than with 10 vectors (10 vectors overestimates) |
| **II Partition-matched (random)** | 100 partitions | **Pass**. Pass 7/9 (single) · 8/9 (syn). $p_G$ 0.0099 for all 18 cells |
| **II' Partition-matched (activation clusters)** | 30 partitions | **Pass**. 5/5 measurable models |
| **III Encoding transfer** | F5 50 vectors | **Fail**. 0 pass among 5 population models |
| III Positive control (gradient) | F5 10 vectors | **Pass** 5/5 · +5.95 · 13/13 |
| III Same-context control | F5 10/50 vectors | Affect words +2.74 vs. codes +0.61 (identical prefix) |
| Held-out covariance · null space | — | Ratio 0.985–1.011 on held-out rows; null-space proportion 0.000000 |
| 256-row scoring context | F5 10 vectors | Measured (tabulation in v6) |
| Action-verb readout | — | **Fail on validity check**. Reported as a control that fell out |

## CQ6. Commitments

- Keep the acceptance count, trial count, and candidate AUC upper bound for the 4 unmeasurable models in the table
- **State explicitly that the unmeasurable models are skewed toward the higher side of emotion partition AUC**
- Do not write "special among all alternative partitions"; state explicitly the 2 families tested
- Do not conflate descriptions of decodability position with intervention-effect claims
- Do not sell $p_G = 0.032$ as a rigorous probability (lower bound for 30 null vectors)
