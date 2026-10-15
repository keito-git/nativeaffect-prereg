# Pre-registration Amendment 25: Record the gate results and execute the mirror arm only

**Target**: Application of the gate from Amendment 24 (X3) and the scope of G1 judgement execution
**Created**: a group member / 2026-09-27
**Status**: **The G1 judgement (160 cells) has not been executed.** This amendment records the results of applying the Amendment 24 gate to actual measurements and determines the scope of execution accordingly.

---

## Y1. Gate measurement (registered floor, registered JS, production candidate directions)

`03_解析/plan_b/G1_judgement/g1_remeasure_v3_20260927_1228.json`
(completed 2026-09-27T12:28Z, layer 11, 144 stimuli = E1 discovery half, PMF 100 draws)

- Floor: `g1.pmf_draws` (registered in §5)
- JS: `g1.js_from_dists` (top-100 union, re-normalized)
- Candidate directions: `g1.get_candidate_dirs` (production; ICA via `run_ica_sweep` n=20 seed=42)

| Direction | Arm | Axis | Floor min / med / max | Floor ≥ axis | p | Within resolution | Judgement |
|---|---|---|---|---|---|---|---|
| ica[0] | I addition | 4.09e-04 | 4.04e-04 / 5.10e-04 / 6.25e-04 | 99/100 | 0.9901 | **100/100** | **unmeasurable** |
| ica[0] | II mirror | 2.84e-02 | 1.19e-02 / 1.07e-01 / 5.37e-01 | 93/100 | 0.9307 | 2/100 | measurable |
| jac[0] | I addition | 7.43e-04 | 3.08e-04 / 3.52e-04 / 4.18e-04 | 0/100 | 0.0099 | **100/100** | **unmeasurable** |
| jac[0] | II mirror | 3.28e-03 | 4.40e-04 / 7.87e-04 / 1.74e-03 | **0/100** | **0.0099** | **0/100** | measurable |

**`n_within` and `n_above` are identical between fp16 and fp32 for all cells.** `swaps` is 0 for both jac arms and ica mirror; ica addition alone has 2 (but that cell is already unmeasurable). **The choice of precision does not change the conclusion.**

## Y2. Applying Gate 1: **the addition arm will not be executed**

**Both directions have `n_within = 100/100` (criterion: 50). Per Amendment 24 X3, the addition arm is unmeasurable.**

**This did not resolve even in fp32, so the cause is not numerical precision but that the effect of the addition intervention itself is buried in the implementation-difference band (1.183e-3 bits).**

**Per Amendment 24 X4, this will be described as "fell below the resolution of the measurement instrument," reporting the measured values above. No positive or negative claim will be made about that arm.**

**It is explicitly recorded that `jac[0]` addition had p = 0.0099 (exceeding all 100 floor draws).**
**Because it does not satisfy the resolution requirement, it will not be used, but the fact of having seen it is not hidden** (same intent as Amendment 24 X5).

## Y3. Applying Gate 2: **the mirror arm will be executed**

`ica[0]` mirror `n_within = 2/100`, `jac[0]` mirror `n_within = 0/100`, `swaps = 0` for both.
**Both Gates 1 and 2 are passed.**

### Y3.1 Execution details
- **Arm: II (mirror) only**
- **Precision: fp32** (36.2 ms/pass, essentially same cost as fp16; registered in Amendment 24 X3)
- Estimated duration: **23.2 hours** (100 floors × 144 stimuli × 1 pass × 160 cells = 2,304,000 passes × 36.2 ms)

### Y3.2 Required fix before execution
**Save per-stimulus floor values (100 × 144).**
The current gate measurement saved only `floor_means` (100 per-draw stimulus means), which makes **the Amendment 21 (a) Cliff's δ (paired δ over 144 pairs after averaging 100 floor draws per stimulus) impossible to compute.**

**The registered criterion is "one-sided permutation p (BH q) < 0.05 **and** δ ≥ +0.20."**
**If δ cannot be produced, the registered criterion cannot be assessed.** Values must be saved in the production run.

### Y3.3 The validation set must not be opened
**The E1 validation half (143 stimuli) will not be used in this execution.** The judgement is performed on the discovery half (144 stimuli). Since `jac` directions were constructed using the discovery half, **all results of this execution are discovery-side findings.**
**A follow-up in the validation half is separate; it will be registered after seeing the results of this execution.**

## Y4. What can and cannot be claimed at this point

**Can claim (discovery side, 2 cells)**:
- Against the registered floor, `jac[0]` mirror has one-sided permutation p = 0.0099
- The same cell satisfies the resolution requirement (all 100 floor draws are outside the implementation-difference band)
- As a comparison, `ica[0]` mirror falls below 93/100 floor draws (p = 0.9307)

**Cannot claim**:
- **Satisfaction of the registered criterion** (δ not yet computed)
- **Generalization** (layer 11, candidate 0, discovery half only; 160 cells not executed)
- **Causal or mechanistic explanation** (per Amendment 22 §V4 / Amendment 23 W2, mechanistic explanations will not be written)

## Y5. Incidental record
The production ICA direction and Audit B ICA direction have L2 distance 1.405 (essentially orthogonal), yet
the axis JS means for the addition arm were 4.5719e-04 vs. 4.5329e-04 (0.9% difference). **Not used in judgement.**
