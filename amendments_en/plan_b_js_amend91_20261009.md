# Pre-registration Amendment 91: Same-Ontology Re-Encoding Test, Structure-Matched Partition Control, and Increasing the Number of Null Draws

**Created**: 2026-10-09
**Occasion**: External review (2026-10-09, 4th round). Obtained after passing draft v4.
**Role**: CJ1 of this amendment is made the precondition for the semantic interpretation of level-3.
**Activation condition**: Judgements must not be performed until this file has been committed and pushed. **Has never been executed.**

---

## CJ1. Same-Ontology Re-Encoding Test (Test CE) — Most Important

### Critique

> What section 4.4 showed is that the emotion direction does not transfer to the **appraisal adjective readout.** Appraisal adjectives are a different conceptual system, and moreover their AUC is only 0.55–0.60. The appropriate test is one that **maintains the same 13 emotion categories but changes only the output representation.**

**The critique is correct.** The current v4 shows only that there is no "cross-ontology transfer," but the title and abstract can be read broadly as "absence of transfer."

### Attribution of Priority

**The method of this test is not our invention.** Gao Zhiwei, Peng Shaowen, Wakamiya Shoko, Aramaki Eiji, "What Does Activation Steering Control? Attribution Across Answer Encodings and Output-Sensitive Subspaces", arXiv:2608.22985, 2026, proposed this as **Cross-Encoding Steering Evaluation.** That paper shows that when the answer identifier is replaced while the intervention is fixed, steering can reflect **following an extraction index** rather than semantic understanding.

**The contribution of this amendment is limited to applying this test to emotion categories and combining it with variance-matched floor, search-width matching, and partition matching.** In the manuscript, the difference is articulated as "Gao et al. control for **output encoding**, while the present study controls for **activation variance, search width, and partition origin**," and **test CE itself is cited as their method.**

### Construction of Test CE (Fixed in this amendment; defined before seeing results)

13 emotion categories are mapped to **opaque single-letter codes**, and the codebook is presented within the prompt. The frame is fixed as follows:

```
Code: anger=Q, boredom=K, disgust=V, fear=Z, guilt=J, joy=X, no-emotion=N,
pride=B, relief=F, sadness=M, shame=G, surprise=W, trust=L

Event: {text}

Answer with the code only. The code is
```

**Codebook 2 (complete transposition — same 13 letters reassigned to all categories):**

```
anger=M, boredom=W, disgust=L, fear=J, guilt=G, joy=Z, no-emotion=V,
pride=K, relief=X, sadness=Q, shame=B, surprise=F, trust=N
```

**No category retains the same letter as in codebook 1.**

Readout: next-token probability of 13 letters. Direction, layer, $J^\ast=0.05$, floor F5, statistics are **not changed at all.** Since the frame differs, $\alpha$ is recalibrated per frame. Token ID duplication raises an exception.

### Validity Checks (Performed Before the Judgement; Not Performed if Not Satisfied)

To avoid repeating the readout B failure (AUC 0.55–0.60 rendering the test uninformative), **thresholds are set before seeing the results.**

1. **Discriminability**: In the unintervened state, the 13-letter probabilities are not degenerate
2. **Mapping validity**: The proportion for which stimuli of the corresponding category give a higher probability for the corresponding code than stimuli of other categories (AUC). **Requiring that ≥7 of 13 categories have AUC > 0.5, and the median AUC ≥ 0.65**
3. **Non-duplication of vocabulary**

**Rationale**: Readout A AUC median was 0.904–0.965; readout B was 0.553–0.597, the latter being uninformative. **0.65 is set in advance as the minimum threshold for the test to have discriminative power.**

**If 2 is not satisfied**: "The model cannot perform the codebook task, so test CE is uninformative" is recorded, and **the judgement is not performed. The codebook is not replaced for a retry.**

### Judgement CE (Fixed before seeing results)

Whether the emotion family exceeds the F5-matched family best using the code readout.
**Pass condition**: Majority of 13 targets exceeded, and $p_G<0.01$. Satisfied for **a majority of models** and **for both codebooks 1 and 2.**

| Judgement CE | What can be written |
|---|---|
| Pass | **Emotion direction control transcends lexical realization.** It transfers to a re-encoding within the same ontology. **"Human-defined emotion partitions induce semantically grounded control beyond their lexical realization"** |
| Fail (validity passes) | **Apparent emotion steering is bound to the output encoding.** Even a strong effect that satisfies variance matching and label matching disappears when encoding changes. **Reported as a negative finding that bears on mechanistic interpretability in general** |
| Validity check fails | Test CE is uninformative. Neither is claimed |

**Reported as-is regardless of which way it goes.**

## CJ2. Weakening the Claim in Section 4.7 (Immediate Correction)

### Critique

> Random partitions differ from the true emotion partition in **decodability itself.** Therefore the explanation could be "because it is a meaningful, predictable partition" rather than "because it is a human emotion partition."

**The critique is correct.** "The specific human emotion partition is effective" in section 4.7 is too strong.

**Correction**: The relevant passages in the main text, abstract, and conclusion are replaced with the following:

> **Human-defined emotion partitions exceed arbitrary partitions with matched class sizes.**

**"Emotion is more special than any alternative partition" is not written.**

## CJ3. Structure-Matched Partition Control (Control SP)

To eliminate the confound of CJ2, **a partition with matched decodability** is added.

**Construction**: Stimuli are clustered into 13 clusters using lexical features (TF-IDF of character n-grams), **adjusted to the same class sizes as the emotion partition.** Additionally, a conditional-permutation condition that **replaces emotion labels within clusters** (preserving surface lexical correlations) is also created. **Only draws are accepted where the probe AUC on the held set falls within ±0.05 of that for the emotion partition.**

**Judgement SP**: Majority of targets for which the emotion family exceeds the control SP family best, and $p_G<0.05$ (30 draws). Satisfied for **a majority of models.**

**If fail**: "What is effective is not being the emotion partition, but being a predictable partition" is recorded, and the claim in section 4.7 is weakened further.

## CJ4. Increasing the Number of Null Draws

### Critique

> F5 has only 10 draws per direction, and even with 4000 bootstrap iterations, only 10 independent directions are used. The number $p_G=0.0005$ does not directly observe the tail to that extent. LP also has 30 draws with $p_{\min}=0.032$.

**The critique is correct.** The following increases are made:

| Target | Current | After change | Rationale |
|---|---|---|---|
| F5 (emotion family) | 10 draws/direction | **50 draws/direction** | Sign patterns are $2^d$ and can be drawn independently |
| F5 (appraisal family) | 10 draws/direction | 10 draws (unchanged) | Allocation of computation. **Stated explicitly that it is not changed** |
| Control LP | 30 partitions | **150 partitions** | $p_{\min} = 1/151 = 0.0066$ |

**Independent samples are used directly to construct the null family, not bootstrap.** **The increase in numbers only raises the resolution of the null; statistics and judgement criteria are not changed.** **If the results with the increased numbers differ from those with 10 draws / 30 partitions, both are reported.**

## CJ5. Matched-Covariance Verification and Null-Space Energy

### Critique

> For models where the number of hidden dimensions exceeds the number of samples in $D_{\mathrm{fit}}+D_{\mathrm{inner}}$, the empirical covariance has a null space. The null-space component is replaced by a random direction of the same norm, but **this does not guarantee variance 0 in unknown test contexts either.**

**The critique is correct.** The following are reported (not used for judgement; they are diagnostics):

1. $\dfrac{\tilde v^\top \Sigma_{\mathrm{test}} \tilde v}{v^\top \Sigma_{\mathrm{test}} v}$ (where $\Sigma_{\mathrm{test}}$ is estimated from the activations in the scoring contexts)
2. $\dfrac{\|v_{\mathrm{null}}\|^2}{\|v\|^2}$ (the fraction of the direction that falls in the training null space)

**The description in the main text is changed to "exactly matched with respect to the empirical fit-covariance."** The unconditional "exactly matched" is not written.

## CJ6. Robustness of Scoring Contexts

### Critique

> $D_{\mathrm{sel}}=32$ and $D_{\mathrm{test}}=32$ are small.

**Response**: **While completely freezing the procedure up to v4**, a **new $D_{\mathrm{test}'}$ (256 rows) is drawn once from unused rows and the results are re-evaluated.** The partition is not redrawn (partition is not changed after seeing results). **Bootstrap confidence intervals for the scoring contexts** are also reported alongside.

## CJ7. Title and Abstract Correction (Immediate)

**Title** is changed to:

> **Variance-Matched Controls Reveal Readout-Specific Steering by Human-Defined Emotion Partitions in Large Language Models**

**"Absence of transfer" is removed from the title.** Because an independent emotion category readout has not been achieved, this is too broad.

**The "consistent across 2 readout types" in the abstract is changed to:**

> **Consistent across 2 emotion-word encodings within the same ontology (single token and synonym set), and not consistent with the appraisal adjective readout outside the ontology.**

## CJ8. Execution Order

```
① CJ2, CJ7 text corrections (immediate; no measurement needed)
② Validity check for test CE → judgement (all 9 models, both codebooks)  ← Highest priority
③ CJ5 diagnostics (CPU only)
④ CJ4 number increase (F5 emotion family 50 draws, LP 150 partitions)
⑤ Control SP
⑥ Re-evaluation with larger scoring context from CJ6
```

**Draft v5 will not be submitted to external review until ② is complete.**

## CJ9. Commitments

- The method of test CE is cited as the contribution of Gao et al.; our contribution is limited to the application and the combination of controls
- The threshold for the validity check (7/13 and median 0.65) is not moved after seeing results
- The codebook is not replaced for a retry
- If test CE fails, **it is claimed as a negative finding as-is**
- The claim in section 4.7 is limited to "exceeds arbitrary partitions with matched class sizes"
- If the results with increased numbers differ from the original, both are reported
- "Exactly matched" is changed to "exactly matched with respect to the empirical fit-covariance"
- Pres et al.'s evaluation framework (arXiv:2410.17245, NeurIPS 2024 Workshop) is added to related work
