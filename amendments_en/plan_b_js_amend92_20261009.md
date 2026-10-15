# Pre-registration Amendment 92: Defining the Judgement Population for Test CE (Before Seeing Measurement Results)

**Created**: 2026-10-09
**Occasion**: When the validity checks for amendment 91 CJ1 were executed, **the pass/fail differed across models.** Amendment 91 wrote "a majority of models," but **had not defined what that population was.** **The measurements for test CE have not yet been judged. This amendment is written before seeing the measurement results.**
**Activation condition**: Test CE must not be judged until this file has been committed and pushed.

---

## CK1. Validity Check Results (Not a Judgement; Used to Determine the Population)

Check 2 from amendment 91 CJ1 (AUC > 0.5 for ≥7/13 categories, and median AUC ≥ 0.65).

| Model | Codebook 1 AUC median | Codebook 2 AUC median | Top-1 match | Judgement |
|---|---|---|---|---|
| gemma-2-9b-it | **0.897** | **0.903** | **13/13** | **Pass** |
| Llama-3.1-8B-Instruct | **0.677** | **0.654** | 6/13 | **Pass** |
| gemma-2-2b-it | 0.588 | 0.595 | 1/13 | Fail |
| OLMo-2-1124-7B-Instruct | 0.562 | 0.552 | 1/13 | Fail |
| Llama-3.2-1B-Instruct | 0.502 | (same) | 1/13 | Fail |
| Remaining 4 models | Measuring | Measuring | — | — |

**Models that fail are outputting the first code in the presented order regardless of stimulus** (codebook 1: uniformly `Q`; codebook 2: uniformly `M`; top-1 match 1/13). **The codebook is not being referenced.** This is a lack of **instruction-following ability**, not a property of emotion representation.

## CK2. Definition of the Judgement Population (Fixed in This Amendment)

> **The judgement for test CE uses as its population only those models that pass the validity check for both codebooks 1 and 2.**
> The pass condition "majority of 13 targets exceeded, and $p_G<0.01$" must be satisfied for **a majority of that population** and **for both codebooks.**

**Rationale**: In models that cannot reference the codebook, the code readout does not track the emotion category at all (top-1 match 1/13). When a readout does not track the target, the fact that the intervention effect is small says nothing about the nature of the direction. **Drawing on the experience of falling into the same trap with readout B (AUC 0.56), uninformative cells are excluded from the population.**

**The following are also made obligatory:**

1. **The size of the population must always be stated explicitly.** Written in the form "of $n$ models, $m$ passed the validity check, of which $k$ passed."
2. **If the population is fewer than 3 models, test CE does not reach a conclusion.** "A population sufficient for judgement was not obtained" is recorded.
3. **Measurements from models that failed are also reported.** The fact of and the reason for exclusion are left in the table and not deleted.
4. **The small population is stated explicitly in the limitations.** The fact that judgement could be made for only a portion of the 9 models is a limitation on the generality of the result.

## CK3. The Population Shrinkage Itself Is a Result

**Only limited models can reference the codebook.** Within the range identified so far, the only model that correctly follows a 13-category codebook (top-1 match 13/13) is gemma-2-9b; Llama-3.1-8B is partial (6/13); the others only return the first code.

**This fact is written in the paper.** Cross-encoding tests of semantic control presuppose **that the model can perform that encoding.** For models that do not meet the presupposition, the test is not valid. **Therefore cross-encoding tests can only be applied to models with sufficient instruction-following ability.** This is a practical constraint when bringing the framework of Gao et al. to other domains, and has value to report.

## CK4. Commitments

- The judgement population is defined as "models that pass the validity check for both codebooks"; not changed after seeing results
- The size of the population ($n$/$m$/$k$) is always stated explicitly
- If the population is fewer than 3 models, no conclusion is reached
- Measurements from failed models and reasons for exclusion are left in the table
- The small population is written in the limitations
- **The fact that only limited models can follow the codebook is itself reported as a result**
