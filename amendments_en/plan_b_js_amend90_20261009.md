# Pre-registration Amendment 90: Control LP Passes. Level-2 Results Are Also Available

**Created**: 2026-10-09
**Targets**: Control LP (label-consistent partition family) from amendment 89, and level 2 from amendment 77
**Judgement**: **Control LP satisfies the registered criterion. The specific 13-way partition of human emotion categories is effective.
In level 2, the emotion subspace exceeds the matched random subspace in 4/4 models; the appraisal subspace exceeds it in 2/4 models.**
**Activation condition**: The next judgement must not proceed until this file has been committed and pushed.

---

## CI1. Results of Control LP (All 9 Models, Both Readouts)

The emotion family was compared against **the best of 30 families of ridge directions fitted to random 13-way partitions with the same class sizes using the same procedure**, scored with the same readout A, the same 13 targets, and the same $J^\ast=0.05$.

| Model | Single-token readout | Synonym-set readout |
|---|---|---|
| gemma-2-2b | **10/13 (+4.62 SD)** Pass | **10/13 (+4.69)** Pass |
| Llama-3.2-1B | **10/13 (+2.89)** Pass | **10/13 (+2.66)** Pass |
| Mistral-Nemo-12B | **10/13 (+2.57)** Pass | **10/13 (+2.83)** Pass |
| Ministral-8B | **9/13 (+2.01)** Pass | **8/13 (+1.97)** Pass |
| OLMo-2-7B | **8/13 (+2.51)** Pass | **8/13 (+2.32)** Pass |
| gemma-2-9b | **7/13 (+2.59)** Pass | **7/13 (+2.59)** Pass |
| OLMo-2-13B | 6/13 (+1.76) Fail | **7/13 (+1.97)** Pass |
| Phi-3-medium | 6/13 (+1.32) Fail | **7/13 (+1.72)** Pass |
| Llama-3.1-8B | 6/13 (+1.52) Fail | 6/13 (+1.63) Fail |

**$p_G$ is 0.0323 for all 18 cells.** With 30 draws the resolution is the floor, meaning **the emotion family's aggregate statistic exceeded all 30 random partition families.**

### Satisfaction of Registered Criterion

The criterion in amendment 89 CH3 was "majority of 13 targets exceeded, and $p_G<0.05$. Satisfied for a majority of models."

- Single-token readout: **6/9 models pass** (majority satisfied)
- Synonym-set readout: **8/9 models pass** (majority satisfied)

**The "majority of models" condition holds for both readouts. Judgement LP passes.**

### Models Where the Judgement Differs Between Readouts

**OLMo-2-13B and Phi-3-medium fall on the boundary at 6/13 vs. 7/13, and the pass/fail reverses depending on the readout.** Because the threshold for majority is 7, a difference of 1 target flips the pass/fail. **Individual pass/fail is not claimed for these 2 models** (criterion in amendment 77 BZ5). **Llama-3.1-8B fails in both readouts**, and this is independent of the readout.

## CI2. The Objection That Control LP Answers

> Ridge-regressing onto 13-class indicator variables moving the probabilities of those class' words — that is obvious; you don't need human emotion categories.

**Answered.** The random partition families have **the same class sizes, the same training rows, the same inner partition, the same $\lambda$ candidates, the same readout, the same targets, and the same budget** as the emotion family. The only difference is **whether the partition is the human emotion or a random one.** **The human emotion partition produces effects that random partitions of the same granularity do not reproduce.**

**This comparison is not subject to the readout quality confound** (amendment 89 CH4). Both are scored with the same readout.

## CI3. Level-2 Results (4 Discovery-Cohort Models, Both Readouts)

The optimal combination within the subspace was compared against **the optimal combination of 30 random subspaces where each direction is matched using F5.**

| Model | Emotion subspace (rank 13) | Appraisal subspace (rank 21) |
|---|---|---|
| Llama-3.2-1B | 5/13 (+0.85) $p$=**0.032** | 3/13 (+0.67) $p$=**0.032** |
| OLMo-2-7B | 5/13 (+0.55) $p$=**0.032** | 3/13 (+0.64) $p$=**0.032** |
| Llama-3.1-8B | 6/13 (+1.49) $p$=**0.032** | 1/13 (−0.22) $p$=0.161 |
| gemma-2-9b | 4/13 (+1.38) $p$=**0.032** | 3/13 (−0.19) $p$=0.161 |

The $p$ judgement was consistent across both readouts. The first-order approximation correlation was +0.905–+0.954, passing for all cells (coefficients taken from linear expansion, effect always measured directly). **Rank: emotion 13/13, appraisal 21/21; neither is linearly dependent.**

### Fail Under the Registered Count Criterion

The judgement L2 in amendment 77 BZ2 was "majority of targets for which the 95th percentile is exceeded." The observations are 4–6/13 (emotion) and 1–3/13 (appraisal), **neither reaching majority. Fail.**

**With 30 draws, the 95th percentile is effectively the "maximum of 30 draws," and requiring exceeding all 30 draws on a majority of 13 targets is a stringent criterion. The criterion is not moved.** The aggregate statistic $G$ is reported as auxiliary.

### From the Perspective of $G$

**The emotion subspace exceeds all 30 draws in 4/4 models. The appraisal subspace does so in only 2/4 models** (in Llama-3.1-8B and gemma-2-9b, $p$=0.161 and the excess SD is negative).

## CI4. Current Consequences for the Principal Investigator's Hypothesis (AAPH)

The hypothesis was: "Emotion categories as such do not exist inside LLMs; there is a latent computational concept $Z$, and human emotion categories are projections of it."

**Points partially consistent**: Appraisal dimensions, as individual named axes, do not exceed the matched floor (+0.18 SD), but **as the subspace they span**, exceed the matched random subspace in 2/4 models. The fact that results differ between the axis and the subspace is itself consistent with the picture that "the space spanned, not the named axes, is what carries it."

**Points inconsistent**: **The emotion subspace is consistently stronger** (4/4 vs. 2/4). The hypothesis requires the latent concept side to be at least as effective as the emotion categories; the observation is the opposite. Furthermore, control LP shows that **the specific partition of human emotion categories is effective.** This does not support the picture that emotion categories are secondary projections.

**Therefore the core of AAPH remains unsupported.** Following the withdrawal of $k \ll |E|$ in amendment 72 and the recording in amendment 81 that the projection direction is opposite to the hypothesis, the present amendment reaches the same conclusion. **This judgement is recorded and the criteria are not moved to fit the hypothesis.**

## CI5. Claims the Present Study Can Make (Updating Amendments 88 CG5 and 89 CH2)

**Can be written (1)**: When output perturbation is matched using full-vocabulary JSD and a same-size random family best with fully eigenvalue-matched variance profiles is used as the floor, **directions estimated from human emotion categories move the emotion word output beyond this floor** (9/9 models, excess SD median +3.17, $p_G \le 0.0005$, 2 readout types consistent).

**Can be written (2, new)**: This effect **is not explained by the mere existence of a 13-way partition.** Against 30 random partition families of the same granularity and same procedure, the emotion family's aggregate statistic exceeds all 30 in all 9 models and both readouts ($p_G=0.032$), and the count criterion is satisfied for a majority of models. **The specific partition of human emotion categories is effective.**

**Can be written (3)**: **That advantage does not transfer across readouts.** Scoring the same directions using the appraisal adjective readout drops to +0.03 SD (0/9). Therefore **axis privilege is not generally claimed.**

**Can be written (4, new)**: At the subspace level, the emotion subspace exceeds the matched random subspace in 4/4 models and the appraisal subspace does so in 2/4 models ($G$). **However both fail under the registered count criterion**, and the stringency of the criterion with 30 draws is stated explicitly.

**Cannot be written**: That the emotion category axis is generally a privileged coordinate (due to 3). That appraisal theory does not explain LLM emotion representation (due to readout B AUC 0.55–0.60 and 2/4 models passing $G$ for level 2). Comparing effect sizes between the two families (due to readout quality difference).

## CI6. Commitments

- The pass of judgement LP is reported with both the count criterion and the number of models stated explicitly
- The individual pass/fail of the 2 boundary models (OLMo-2-13B and Phi-3-medium) is not claimed
- **The fact that Llama-3.1-8B fails in both readouts is not concealed**
- Level 2 is first written as failing the registered count criterion, with $G$ reported alongside as auxiliary
- The judgement that the core of AAPH is unsupported is recorded and the criteria are not moved
- The distinction in CI5 — "4 things that can be written" and "3 things that cannot be written" — is not collapsed in the manuscript
