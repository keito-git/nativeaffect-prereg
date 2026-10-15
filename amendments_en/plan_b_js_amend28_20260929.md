# Pre-registration Amendment 28: Record the validation-set replication and swap the execution order

**Target**: Intermediate results of Experiment A (validation-set replication) from Amendment 26, and the execution order of Experiments A and B
**Created**: a group member / 2026-09-29
**Status**: Experiment A **stopped after completing layers 11 and 16 (80 cells)**. Layers 22 and 27 are not executed
(checkpoint exists; can be resumed at any time). **Experiment B has not been executed.**

---

## AB1. Experiment A results (layers 11 and 16, validation set 143 stimuli)

`03_解析/plan_b/G1_judgement/g1_confirm_partial_L11L16_20260929.json`

| Layer | jac (10) | ica (20) | pc (10) | jac δ_a min / med / max |
|---|---|---|---|---|
| 11 | **10/10** | 1/20 | **0/10** | +0.371 / +0.804 / +1.000 |
| 16 | **10/10** | 0/20 | **0/10** | +0.427 / +0.692 / +1.000 |

Comparison with the discovery half (`g1_judgement_discovery_20260928.json`):

| Layer | Discovery jac | Validation jac | Discovery pc | Validation pc |
|---|---|---|---|---|
| 11 | 10/10 | **10/10** | 0/10 | **0/10** |
| 16 | 10/10 | **10/10** | 0/10 | **0/10** |

**Prediction A (Amendment 26 Z3) was satisfied at layers 11 and 16.**

**δ_a has not degraded** (across 10 vectors at layer 11, the difference from the discovery half ranges from −0.100 to +0.107, mean +0.021).

### Implication
**The Jacobian directions were constructed from the discovery-half 144 stimuli, but they also exceed the floor on 143 stimuli never used in construction.** The circularity concern described in Amendment 26 Z2 ("testing on the same stimuli is close to definitional") **has been resolved for layers 11 and 16.**

**However, layers 22 and 27 are not yet executed, so "in all 4 layers" cannot be written.**
**The current description is limited to "replicated in layers 11 and 16."**

## AB2. Swap in execution order (decision by the principal investigator, 2026-09-29)

**Experiment A is stopped at the completion of layer 16, and Experiment B will be executed first.**

**Reason**: The remaining 2 layers of Experiment A require approximately 11 hours, whereas **with jac 10/10 and pc 0/10 holding for 2 consecutive layers, the likelihood that the remaining 2 layers would reverse the conclusion is small.** By contrast, **the result of Experiment B determines how Paper 3 will be written (as an emotion paper or a methodology paper).** The information gain per unit of time is different.

**The group member recommended this and the principal investigator approved.** Experiment A will be resumed after Experiment B.

### Disclosure
**This order change was decided after seeing the layer 11 and 16 results.** All numbers seen are fully listed in AB1.
**The remaining 2 layers were not stopped because the results were unfavorable** — layers 11 and 16 both satisfied Prediction A, and the reason for stopping was the priority of information gain. **Layers 22 and 27 will be executed later and all results will be reported.**

## AB3. Conditions for Experiment B (unchanged from Amendment 26 Z4; restated)

- Non-emotional stimuli: **144 GSM8K train problem texts** (`data/raw/benchmarks/gsm8k_train.jsonl`, seed 20260928)
- Run `g1_jacobian.py` on 144 GSM8K items to obtain 10 sensitivity directions per layer for 4 layers
- Test: **E1 validation half 143 items**, Arm II, fp32, registered floor `g1.pmf_draws`, PMF 100 draws
- **Prediction B**: GSM8K-derived sensitivity directions are weaker on emotional stimuli than jac(E1)
  (fewer layers satisfying the registered criterion, or δ_a systematically smaller)

**The comparison target is the validation-set values in AB1 (layer 11: med +0.804 / layer 16: med +0.692).**
**These two medians are fixed as the baseline before executing Experiment B.**

- **If GSM8K-derived δ_a medians are clearly lower** (compared by the same layer) → **the effect depends on emotional content**
- **If equal or higher** → **not specific to emotion. Rewrite Paper 3 as a methodology paper**
- **If Prediction B is wrong, write that. The stimulus set will not be switched to try again.**
