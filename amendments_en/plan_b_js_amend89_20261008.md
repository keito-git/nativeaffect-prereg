# Pre-registration Amendment 89: Readout Quality Explains the Order-of-Magnitude Difference. CG5(3) Is Retracted; Label-Consistent Partition Control Is Registered

**Created**: 2026-10-08
**Occasion**: Results of the diagnostic registered in amendment 88 CG6 (AUC for both readouts)
**Judgement**: **"Can be written (3)" in amendment 88 CG5 (the order-of-magnitude difference in the self-consistent readout is not explained by self-consistency alone) is retracted. It is explained by the difference in readout quality.**
**Activation condition**: The control LP must not be executed until this file has been committed and pushed.

---

## CH1. Diagnostic Results (Not Used for Judgement; Reported per the Commitment in CG6)

AUC: the proportion for which stimuli with the corresponding label give a higher probability than stimuli without it. Readout A: stimuli of the corresponding category vs. stimuli of other categories; readout B: high rating vs. low rating.

| Model | Readout A AUC median [range] | Readout B AUC median [range] |
|---|---|---|
| Llama-3.2-1B | **0.943** [0.816–0.978] | 0.559 [0.426–0.718] |
| Llama-3.1-8B | **0.904** [0.819–0.979] | 0.570 [0.467–0.797] |
| OLMo-2-7B | **0.928** [0.778–0.981] | 0.568 [0.441–0.853] |
| OLMo-2-13B | **0.954** [0.811–0.987] | 0.560 [0.417–0.837] |
| Gemma-2-2B | **0.956** [0.869–0.989] | 0.597 [0.482–0.881] |
| Gemma-2-9B | **0.964** [0.879–0.984] | 0.592 [0.449–0.869] |
| Ministral-8B | **0.960** [0.860–0.988] | 0.580 [0.444–0.829] |
| Mistral-Nemo-12B | **0.965** [0.868–0.993] | 0.553 [0.392–0.797] |
| Phi-3-medium | **0.931** [0.846–0.976] | 0.565 [0.422–0.834] |

**Readout A AUC: 0.90–0.97; readout B: 0.55–0.60.** Readout B is barely above chance (0.50).

## CH2. CG5(3) Is Retracted

Amendment 88 CG5 stated the following as "can be written":

> **Can be written (3)**: The effect size in the self-consistent readout differs by an order of magnitude between the two families (emotion +3.17 vs. appraisal +0.39). ...This difference is not explained by self-consistency alone.

**Retracted.** Readout B barely separates its own labels (AUC 0.56). The fact that the intervention effect is small for a readout that does not separate labels **is not evidence that the direction is causally unrelated.** It is a problem of readout resolution.

Amendment 88 CG6 committed: "if the top-1 match rate for readout A is markedly higher than the AUC for readout B, CG5(3)'s order-of-magnitude difference may be explainable by readout quality; this is stated explicitly as a limitation." **This is treated more strongly than the commitment: the claim itself is withdrawn.**

### Only 2 "Can Be Written" Remain

1. When output perturbation is matched using full-vocabulary JSD and a same-size random family best with fully eigenvalue-matched variance profiles is used as the floor, **directions from emotion categories move the emotion word output beyond this floor** (9/9 models, excess SD median +3.17, $p_G \le 0.0005$, 2 readout types consistent)
2. **That advantage does not transfer to the appraisal adjective readout** (+0.03 SD, 0/9)

**The inter-family comparison (emotion vs. appraisal) is not made in the present study due to the dual confounds of readout asymmetry and low resolution of readout B.** No superiority or inferiority is discussed in the manuscript.

## CH3. Registering a Confound-Free Control — Control LP (Label-Consistent Partition Family)

### Question

The remaining "can be written 1" is exposed to the following objection:

> Ridge-regressing onto indicator variables for 13 classes moving the probabilities of the 13 class words — is that not obvious? You don't need human emotion categories; **wouldn't the same thing happen with any 13-way partition?**

This can be tested in a form that is not affected by the readout quality confound. **All that is needed is to compare the human emotion partition with a random partition of the same granularity, using readout A (AUC 0.90–0.97).**

### Construction of Control LP (Fixed in this amendment; defined before seeing results)

1. **Randomly permute** the emotion labels of the training rows across rows, creating **a 13-way partition with the same class sizes as the true classes**
2. Estimate ridge directions for those 13 indicator variables using **exactly the same procedure as for the emotion family** (same training rows, same inner partition, same $\lambda$ candidates)
3. Score the resulting 13 directions as a single family with **the same statistic as the emotion family** (selection in sel contexts, scoring in test contexts, family best)
4. Draw this **30 times**, obtaining the distribution of the family best

**Both the emotion family and the random partition family are measured with the same readout A, the same 13 targets, and the same $J^\*=0.05$.**

### Judgement LP (Fixed before seeing results)

- **Count**: Number of targets for which the emotion family's value exceeds the 95th percentile of the 30 random partition families
- **Continuous statistic**: Taking $\mu_e,\sigma_e$ from the 30 draws and computing $G=\sum_e (S_e-\mu_e)/\sigma_e$, $p_G = (1+\#\{G_{\mathrm{null}} \ge G_{\mathrm{obs}}\})/31$

**Pass condition**: Majority of 13 targets exceeded, and $p_G < 0.05$ (threshold is 0.05 because the resolution with 30 draws is $1/31 = 0.032$; **this relaxation is stated explicitly before the results**). This is satisfied for **a majority of models**.

### Interpretation of Results (Fixed in Advance)

| Judgement LP | What can be written |
|---|---|
| Pass | **The specific partition of human emotion categories is effective.** It is not reproduced by random partitions of the same granularity. **Cannot be explained by vocabulary self-consistency** |
| Fail | "Can be written 1" **is explained by the existence of a 13-way partition alone.** The specificity of human emotion categories cannot be demonstrated. In that case, the affirmative content of the present study is limited to the methodology (floor construction), and this is recorded |

**Reported as-is regardless of pass or fail.**

## CH4. Control LP Is Not Subject to the Readout Quality Confound

The emotion family and the random partition family are compared with **the same readout, the same targets, and the same estimation procedure.** The only difference is **whether the partition is the human emotion or a random one.** Therefore the nature of this comparison differs from the comparison retracted in CH2, and **this comparison holds.**

## CH5. Scope of Execution

**All 9 models.** Floor F5 measurement is already complete, so this control is executed as an additional measurement. Per model: 30 × 13 = 390 measurements (including re-measurement of 13 emotion family directions for 403 total). Raw measurements are saved to `rawLP_<tag>.npz`.

**Independent from level 2 (amendment 77).** LP asks about the origin of the set of axes; L2 asks about the subspace.

## CH6. Commitments

- The retraction of CG5(3) is preserved in the record. Claims that may be explained by readout quality are not retained
- The construction and judgement of control LP are not changed after seeing results. The $p_G$ threshold of 0.05 and its rationale were written first
- If LP fails, the fact that the affirmative content is limited to the methodology is stated explicitly
- The AUC of readout B being 0.55–0.60 is written in the limitations of the main text. **The negative result for readout B is not read as "appraisal dimensions are not causal"**
