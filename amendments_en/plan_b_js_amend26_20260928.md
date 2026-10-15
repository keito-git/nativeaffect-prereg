# Pre-registration Amendment 26: Record G1 results and register Experiment A (validation-set replication) and Experiment B (emotion specificity control)

**Target**: Completion report of the G1 judgement, and the next-stage Experiment A (validation-set replication) and Experiment B (emotion specificity control)
**Created**: a group member / 2026-09-28
**Status**: **Experiments A and B are both unexecuted. The 143-stimulus validation set has not been opened.** This amendment fixes the predictions and judgement rules for both experiments before looking at the data.

---

## Z1. G1 results (final)

`03_解析/plan_b/G1_judgement/g1_judgement_result.json` (completed 2026-09-28T13:47Z, 1.47 MB)
Arm II (mirror) only, fp32, E1 discovery half 144 stimuli, PMF 100 draws, registered floor `g1.pmf_draws`.

Number of cells satisfying the registered criterion (BH q < 0.05 **and** Cliff's δ_a ≥ +0.20):

| Layer | jac (10) | ica (20) | pc (10) |
|---|---|---|---|
| 11 | **10/10** | 0/20 | 0/10 |
| 16 | **10/10** | 1/20 | 0/10 |
| 22 | **10/10** | 0/20 | 0/10 |
| 27 | **9/10** | 1/20 | 0/10 |
| **Total** | **39/40** | **2/80** | **0/40** |

Script judgement text:
`G1 PASS (arm_II): out of 4 layers, arm_I has 0 and arm_II has 4 with ≥1 axis meeting q<0.05 AND δ≥0.2.`

**"`arm_I has 0`" means "could not be measured," not "no effect was found"** (Amendment 25 Y2: the addition arm did not pass the resolution gate and was not executed). **The manuscript must not conflate these two.**

**The heaviest number is `pc 0/40`.** Principal components are by definition the highest-variance directions, and not a single one exceeds the floor, whereas the output-sensitivity-selected directions go 39/40. **"High variance therefore effective" is ruled out as an explanation.**

## Z2. What still cannot be claimed (why these two experiments are needed)

**Jacobian directions were constructed to maximize output sensitivity on the E1 discovery half of 144 stimuli.** Testing "does it produce large output movement" on the same stimuli is close to circular. **What has been established so far is only "output sensitivity can be separated from variance structure"; nothing at all has been shown about specificity to emotion.**

## Z3. Experiment A: replication in the validation set (breaking the circularity)

**The directions will not be changed.** Use the `sensitivity_directions` from `layer{11,16,22,27}.json` (already constructed on the discovery half) as-is, and **replace only the stimuli with 143 E1 validation-set items.**

- All 40 candidates (jac 10 / ica 20 / pc 10). **ica and pc will not be dropped**
  (dropping them would constitute "retaining only the favorable family")
- Arm II only, fp32, PMF 100 draws, registered floor. Judgement rules identical to G1
- **ica and pc will be re-estimated from validation-set activations** (not carried over from the discovery half). Only jac uses the fixed values constructed on the discovery half. **This asymmetry is intentional and will be stated explicitly in the report**
- Estimated duration: 40 × 4 layers × 100 floors × 143 stimuli × 1 pass = 2,288,000 passes × 36.2 ms ≈ **23.0 hours**

### Prediction A (fixed before seeing the data)
**jac satisfies the registered criterion in at least 1 axis in all 4 layers in the validation set.**

- **If satisfied**: the effect generalizes to stimuli not used in construction. **Circularity is broken**
- **If not satisfied**: the G1 result is limited to the stimuli used in construction.
  **Write "discovery-half-only finding" and make no generalization claim**
- **If partial** (1–3 layers): report as layer-dependent, specifying which layers it holds for

## Z4. Experiment B: emotion specificity control (the core of the principal investigator's vision)

**Question: is this effect specific to emotion, or merely the general fact that "high-output-sensitivity directions move the output"?**

**The current design cannot distinguish these two.** To distinguish them, **Jacobian sensitivity directions will be constructed from non-emotional text and tested on the same emotional stimuli.**

- Non-emotional stimuli: **144 GSM8K train problem texts** (`data/raw/benchmarks/gsm8k_train.jsonl`, extracted with fixed seed 20260928). **E3 will not be used** — `children` ("happily") and `social` ("can't believe they cancelled my favourite show") are emotional, making them unsuitable as controls
- Procedure: run `g1_jacobian.py` on 144 GSM8K items to obtain 10 sensitivity directions per layer for 4 layers
- Test: **E1 validation half 143 items** (same stimuli and same floor construction as Experiment A), Arm II, fp32
- Estimated duration: Jacobian construction ≈ **2.1 hours** + judgement 10 × 4 layers × 100 × 143 = 572,000 passes ≈ **5.8 hours**
  = **approx. 8 hours total**

### Prediction B (fixed before seeing the data)
**GSM8K-derived sensitivity directions are weaker on emotional stimuli than jac(E1)**
(fewer layers satisfying the registered criterion, or δ_a systematically smaller).

- **If Prediction B is correct**: the effect depends on emotional content. **Supports the principal investigator's vision (AI-native emotion concepts)**
- **If Prediction B is wrong and GSM8K-derived directions work equally well**: **the effect is not specific to emotion.**
  It is the general fact that "high-output-sensitivity directions move the output," and
  **Paper 3 cannot be written as an emotion paper.** It will be rewritten as a methodological finding
- **If intermediate**: report the δ_a difference as effect size and make no definitive conclusion in either direction

**Prediction B being wrong is entirely possible. If wrong, write that.**
**The stimulus set will not be switched to try again** (one attempt with GSM8K, then done).

## Z5. Execution order and fixed items
1. Experiment A (23.0 hours)
2. Experiment B (8 hours)

**The judgement rules, predictions, stimulus sets, and seeds for both experiments are fixed in this amendment.**
**Thresholds and stimuli will not be changed after execution.** Result files will be written to
`g1_confirm_result.json` / `g1_specificity_gsm8k_result.json`.
