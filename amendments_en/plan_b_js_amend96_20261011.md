# Pre-Registration Amendment 96: Vocabulary Structure Cannot Equalize Decodability. Equalize from Above Using Activation Clusters.

**Created**: 2026-10-11
**Target**: Structural-match partition control (SP) from Amendment 91 CJ3
**Judgement**: **No partition that enters the acceptance band is obtainable from vocabulary clusters. Report "not obtained" as registered, and newly register a control in which decodability exceeds the emotion partition.**
**Trigger condition**: Do not run the judgement of the new control until this file is committed and pushed.

---

## CO1. Vocabulary Clusters Cannot Reach It (Measured)

Amendment 91 CJ3 registered the use of clusters built from character n-gram TF-IDF, with class sizes matched, accepting only draws in which the probe AUC on the held-out set falls within ±0.05 of the emotion partition.

Measured result on Llama-3.2-1B (layer 12):

| Quantity | Value |
|---|---|
| Median held-out AUC of emotion partition | **0.9546** |
| AUC range of vocabulary cluster candidates (200 evaluated) | **0.5148 to 0.8813** |
| Acceptance band | 0.9046 to 1.0 |
| Partitions accepted | **0** |

**The upper bound of decodability achievable from vocabulary structure is 0.8813, which does not reach the emotion partition's 0.9546.**
A knob for reducing decodability (random reassignment) was prepared, but **there is no means of raising it.**

### This Is a Finding Worth Reporting

> **The human emotion partition is more decodable from the model's activations than any vocabulary-structure partition of the same granularity and class size.** The maximum among 200 candidates is 0.881; the emotion partition is 0.955.

**Report "no partition entered the acceptance band," as committed in Amendment 91 CJ3.
Do not stretch the knob or the acceptance band to force acceptance.**

## CO2. New Control SP-act (Activation Clusters; Equalize Decodability from Above)

### Motivation

If decodability cannot be **equalized**, place a control that **exceeds** it.
If the emotion partition beats a partition that is more decodable than it in terms of intervention effect,
**the explanation "it worked because the partition was predictable" does not hold.**

### Construction (fixed in this amendment; defined before seeing the results)

1. Run $k=13$ k-means in the space of standardized activations $X_{\mathrm{fit}}$ on training rows
2. Match class sizes to the emotion partition (greedy transfer identical to Amendment 91 CJ3)
3. Fit a ridge direction to the indicator variables of the resulting 13-partition using **exactly the same procedure as the emotion family**
4. Measure the probe AUC on the held-out set and confirm it is **at least equal to the emotion partition's AUC**. Draws that fall below are not accepted.
5. Repeat until 30 are accepted (varying the k-means initialization and subspace dimensionality; upper limit 200 trials)

**Affect labels are not used at all.** Only the cluster structure of the activations is used.

### Explicit Statement on Circularity

**Activation clusters are of course more decodable from activations.** That is the intention.
This control is not intended to claim "the emotion partition is the most decodable partition"; it is intended to show **"decodability cannot explain the intervention effect."**
The fact that the control side is advantaged is thus a deliberate feature of the design: it is a **conservative control**.

### Judgement SP-act (fixed before seeing the results)

Does the emotion family exceed the best of 30 activation-cluster families?
**Pass condition**: exceeds over half of 13 targets, and $p_G<0.05$ (for 30 null vectors). Satisfied in **over half of models**.

| Judgement SP-act | What can be written |
|---|---|
| Pass | **Cannot be explained by decodability.** The emotion partition wins even against a partition that is more decodable than it. **The claim of Amendment 90 can be strengthened from "exceeds arbitrary partitions" to "not explained by decodability."** |
| Fail | **The possibility that decodability explains it remains.** Keep the claim of Amendment 90 to "exceeds arbitrary partitions with matched class sizes." **Do not make any stronger claim.** |

**Report as-is even if the result is fail.**

### Also Report

The median and range of AUC for the accepted activation-cluster partitions, the emotion partition's AUC, and the number of rejected trials. **Show numerically that the control side's AUC exceeds the emotion partition.**

## CO3. Do Not Discard the Vocabulary Cluster Results

Vocabulary clusters did not enter the acceptance band, but the **30 most decodable** (top AUC) are measured as **auxiliary controls**. Their AUC is approximately 0.85–0.88, which is lower than the emotion partition but far higher than random partitions (0.51).

**This auxiliary control is not used in the judgement.** It is reported as descriptive information — "does the emotion partition also win against a partition with decodability 0.88?"
**The judgement is made with SP-act.**

## CO4. Execution Order

```
① Currently running LP 100 partitions (11.6 hours)
② SP-act (activation clusters · 9 models · 3.6 hours)
③ Auxiliary measurement of top-30 vocabulary clusters (9 models · 3.6 hours)
```

## CO5. Commitments

- Report that no partition entered the acceptance band with vocabulary clusters, as-is
- Do not relax the acceptance band or the knob
- Show numerically that the control side's AUC in SP-act exceeds the emotion partition
- **If SP-act fails, keep the claim of Amendment 90 to "exceeds arbitrary partitions"**
- Do not use the auxiliary vocabulary cluster measurement in the judgement
- Do not conflate the finding of CO1 that "the emotion partition is the most decodable" with the intervention-effect claim
