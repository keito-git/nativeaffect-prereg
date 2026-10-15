# Pre-Registration Amendment 65: The Output "Asymmetry Supported" in X2′ Is Not Adopted.
# The Registered Prerequisite Was Not Implemented, and the Floor for (b) Is Inflated

**Created**: 2026-10-06
**Target**: Judgement X2′ in Amendment 63
**Judgement**: **X2′ is unmeasurable. The output "asymmetry supported" is not adopted.**
**Activation condition**: The revised X2″ must not be judged until this file has been committed and pushed.

---

## BN1. The Output (Recorded As-Is)

Llama-3.2-1B, L12, $J^\*=0.05$, 60 floor trials.

| | Estimator | Floor | Floor p95 | Exceeded floor? |
|---|---|---|---|---|
| **(a) Appraisal → emotion** | $\bar S = +0.1101$ | −0.0099±0.0570 | +0.0910 | **Exceeded** |
| **(b) Emotion → appraisal** | $\lvert\bar S\rvert = +0.3276$ | **+0.4591±0.3502** | **+0.9489** | Did not exceed |

The script output "asymmetry supported." **This judgement is not adopted.** There are two reasons.

## BN2. Reason 1 — The Registered Prerequisite Was Not Implemented

Amendment 63 BL3 registered the following.

> **Prerequisite**: The readout on the (b) side is confirmed to be functional. As a positive control for the appraisal question, it is confirmed that the log-odds moves for stimulus pairs that directly ask about the given evaluation dimension (minimum pairs from Q1–Q3 in Amendment 56). **If it does not move, the non-holding of (b) is not claimed.**

**This confirmation was not implemented in the code.** Therefore, it cannot be determined whether (b)'s "did not exceed the floor" is due to the bluntness of the readout. **This is a judgement that does not satisfy the registered prerequisite.**

## BN3. Reason 2 — The Absolute Value Comparison Inflates the Floor

The implementation used $\lvert \bar S \rvert$ for the target side and the distribution of $\lvert \text{floor} \rvert$ for the floor side. **Taking the absolute value causes the floor mean to become $\mathbb{E}\lvert \text{noise} \rvert$, deviating greatly from 0.** Floor mean +0.4591 and SD 0.3502 illustrate this.

**The target value +0.3276 for (b) is below the floor mean +0.4591.** This means "did not exceed the floor" signifies that **random directions move it more**. This is not the absence of an effect but a manifestation of **the readout being highly sensitive to random directions**.

**(a)-side's same problem (a magnitude readout has a floor higher than the effect) is recurring on the (b) side.** The pattern diagnosed in Amendment 58 and placed at the center of primary results in Amendment 64 is repeating on the appraisal-side readout.

## BN4. This Is the Fourth Implementation Defect; It Is Recorded

| No. | Defect | Amendment |
|---|---|---|
| 1 | The null validity gate incorrectly judged "a large effect means the null is unsound" | 57 |
| 2 | A magnitude indicator was used for the emotion readout, causing sign-blindness (recurrence of a type already resolved in Amendment 37) | 58 |
| 3 | The zero-centering gate was significance-based and became stricter as sample size increased | 59 |
| 4 | **The registered prerequisite was not implemented, and absolute value comparison inflated the floor** | **This amendment** |

**All were detected and recorded independently, but each could have been prevented at the design stage.** **Going forward, before any judgement is output, a step of mechanically checking "does the registered prerequisite exist in the code?" is taken.**

## BN5. Revised X2″

**The readout for (b) is changed to a directional quantity.** The change in log-odds of the appraisal question is matched against **the direction predicted by human ratings**.

For each evaluation dimension $a$, the **predicted sign** is constructed from the relationship between crowd-enVENT rating $Y_a$ and emotion category $e$: $\sigma(e, a) = \mathrm{sign}\big(\mathrm{corr}(Y_a, \mathbb{1}[\text{emotion}=e])\big)$ (the sign of the contrast vector $c_a$ in Amendment 58).

If an intervention on emotion direction $w_e$ moves the log-odds of appraisal $a$, **its sign should be consistent with $\sigma(e, a)$.** Therefore,

$$ T_{e} = \frac{1}{|A|}\sum_{a \in A} \sigma(e, a)\, S_{w_e \to a} $$

is used as the estimator. **Since random directions are unrelated to $\sigma$, the floor of $T$ should be zero-centered.** This is the same logic as the (a)-side design.

**Judgement X2″**:
- **(a)** $\bar S_{Z \to E}$ exceeds the 95th percentile of the F4 floor
- **(b)** $\bar T_{E \to Z}$ **does not exceed** the 95th percentile of the F4 floor
- **Prerequisite (i)**: The floor of (b) is zero-centered (|mean| < 2 SE). **If not satisfied, (b) is not judged**
- **Prerequisite (ii)**: The log-odds of the appraisal question moves for the Q1–Q3 minimum pairs in Amendment 56 (the pair difference exceeds the null). **If not satisfied, non-holding of (b) is not claimed**

**(a) and (b) and prerequisites (i)(ii) all holding supports asymmetry.**

## BN6. Commitments

- The output "asymmetry supported" is **not adopted**. The record is kept in this amendment
- Prerequisites (i)(ii) are **implemented in the code before** making any judgement
- Absolute value comparison is not used. **Directional quantities are used for comparison**
- A step of checking "whether registered prerequisites are in the code" is taken before judgement
- If prerequisites fail even for X2″, **asymmetry is not claimed**
