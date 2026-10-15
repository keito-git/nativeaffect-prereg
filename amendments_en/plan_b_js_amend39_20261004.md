# Pre-registration Amendment 39: Experiment B (signed readout) failed at all layers.
# The explanation "the metric was sign-blind" is closed.

**Target**: Amendment 37 (Experiment B, judgements B1–B3)
**Created**: 2026-10-04
**Judgement**: **B1 not established. The causal and control clauses of the hypothesis are closed.**

---

## AN1. What was measured

The previous output metric (JS divergence of the next-token distribution) does not distinguish sign.
Because it returns the same value for $+\alpha v$ and $-\alpha v$, even if a direction carries valence, all we could say was that it "moved a lot." **The possibility that all previous null results were due to insufficient resolution of the metric** had remained open.

Experiment B measured the antisymmetric effect $S(v) = \frac{1}{2}[R(h+\alpha v) - R(h-\alpha v)]$ against the signed valence readout

$$R(h) = \frac{1}{|\mathrm{POS}|}\sum_{w \in \mathrm{POS}} \log p(w \mid h)
       - \frac{1}{|\mathrm{NEG}|}\sum_{w \in \mathrm{NEG}} \log p(w \mid h)$$

If a direction carries content, $+v$ and $-v$ move in opposite directions, so $S(v)$ comes out large.

The vocabulary was the top and bottom 200 single-token words by valence according to the Warriner criterion.
**0 overlapping words; finalized before seeing results** (as promised in Amendment 37 AL5).

## AN2. Control

**Haar random directions within the sensitivity subspace $S$** ($N=30$). Since they are drawn from the same subspace, they **have the same gain and carry no content**. As stated in Amendment 37 AL3, it was confirmed in advance that the $|\cos|$ between random directions within $S$ and the human V/A/D directions is approximately the same as that for random directions in the full space (ratio 0.79–1.60), verifying that it functions as a control.

## AN3. Results: fell below the control at all layers

| Layer | Median $|S|$ of jac | 95th percentile of Haar in $S$ | Judgement |
|---|---|---|---|
| 11 | 0.0055 | 0.0152 | **FAIL** |
| 16 | 0.0176 | 0.0355 | **FAIL** |
| 22 | 0.0246 | 0.0691 | **FAIL** |

The confirmed value for layer 27 was not obtained due to a server connection failure, but **the registered criterion requiring 3 or more out of 4 layers cannot be met once 3 layers have failed**. The overall FAIL is confirmed.

**The direction selected by output sensitivity does not move valence more than a content-free direction with the same gain. In fact, it falls below it.**

## AN4. Judgement and its consequences

The provision of Amendment 37 AL4 is applied.

> **B1**: The median of $|S(v)|$ for the output-sensitivity family exceeds the 95th percentile of control H.
> If it does not, "content is not detected even with signed readout" is concluded, and
> **the causal and control clauses of the hypothesis are closed.**

**As registered, the causal and control clauses are closed.**

The following is thereby confirmed.

- **"The previous null results were because JS was sign-blind" does not hold.** Content was not detected even with a metric that distinguishes sign; it actually fell below the content-free control.
- The reading that the floor-exceeding rate of 70.7% (Amendment 32 AF4) is a **measurement of the magnitude of output change (gain)** and not of content is corroborated by an independent metric.

## AN5. Implications of this result for the new main series (Amendment 38)

**This is support, not negation.**

The claim of Amendment 38 is that "the carving called emotion does not cut the model's representation space at its natural joints." Valence is a **human axis**, and as long as we measure along a human axis, the directions that work in the model carry nothing — this is exactly the prediction of Amendment 38, and the FAIL of B becomes its **direct evidence**.

Under the old framework (is an emotion direction special?), this was "yet another failure," but under the new framework it is the first piece of evidence. The meaning of the same observation is reversed depending on how the question is framed.

## AN6. Remaining items

- Obtain the confirmed value for layer 27 and append it to this amendment (the judgement will not change).
- Back up the result file of Experiment B, `results/plan_b/expB_signed/expB_signed.json`, locally.
