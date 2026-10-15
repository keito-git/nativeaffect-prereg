# Pre-registration Amendment 38: Identify representation components shared across models via relative representations
# and measure their relationship to human emotion dimensions

**Created**: 2026-10-03
**Position**: Pre-registration of a new main series, separate from the current series (Amendments 29–34 2×2, Amendment 36 V/A/D residual, Amendment 37 signed readout). All existing judgements remain unchanged.
**Launch condition**: The job must not be launched until this file has been committed and pushed to remote.

---

## AM0. Repositioning the question (principal investigator instruction 2026-10-03)

This research group has repeatedly asked "are emotion directions special?" and has repeatedly been negated.

- Emotion-derived directions work on math stimuli as well as or better (Amendment 32 AF3)
- Per-direction stimulus profiles are uncorrelated with stimuli's valence (today's observation, same as null across all families and all layers)
- What works is the layer's sensitivity structure, not input content (Amendment 34)
- 0 out of 80 principal-component directions exceed the floor (Amendment 32 AF4)

**These can be read as evidence that the framing "emotion" does not cut the model's representation space at its natural joint.** This series establishes that reading as a claim and tests it.

> **There exist common components in the representations of diverse language models. They are not human emotion dimensions.
> What humans call "emotion" is constituted as a mixture of these.**

## AM1. Technical key (how to make cross-model comparison work)

Dimensions and bases differ per model, so directions cannot be compared directly. **Relative representations** are used.

For a fixed anchor stimulus set $A$, represent stimulus $s$ in model $m$ as:

$$R_m[s,a] = \cos\big(h_m(s),\, h_m(a)\big),\quad a \in A$$

$R_m$ is a matrix of the same shape $|S| \times |A|$ for all models, and model-specific bases disappear.
Decomposing in this space yields components that are model-independent by construction.

**Anchor set and evaluation set must always be separate** (to prevent overfitting to anchors).
Anchors are selected from general sentences that do not contain emotional words and are not selected for emotional content.

## AM2. Stage 1: Does cross-model agreement exist? (first kill switch)

**Procedure**: For 5 models (Qwen3-8B / llm-jp-4-8b-base / gemma-4-E2B-it / granite-4.2-3b /
Dense_1b_130B; V/A/D directions already obtained in Paper 1), construct $R_m$.
Layer is selected from within the normalized depth range 0.45–0.75 for each model and **fixed to 1 layer per model** before measuring agreement (layers will not be selected post-hoc).

**Estimand**: per model-pair agreement of $R_m$ (matrix correlation, and principal angles of top principal components).

**Null and controls**:
- **Null N1**: matrix with shuffled model labels
- **Control N2 (required)**: $\hat{R}$ predicted from **surface statistics** of stimuli alone (token length, mean word frequency, punctuation count, topic cluster). If agreement does not exceed this, the common component is surface-level rather than content, and **this series terminates**

**Criterion M1**: Cross-model agreement exceeds Null N1, **and** also exceeds the null in the residual after removing the variance explained by surface statistics. **If not satisfied, this series terminates.**

## AM3. Stage 2: Are the agreement components human emotion dimensions?

Executed only if Stage 1 is passed. Decompose the agreement space into $r$ components ($r$ is **pre-determined by BIC**; will not be changed after seeing results).

**Criterion M2**: For each component $C_i$, the correspondence with human V/A/D axes and each of 20 emotion category contrasts is low, **and** the reconstruction of emotion categories is better than a V/A/D basis of the same rank $r$.

**Controls**: V/A/D basis of the same rank, and a random basis of the same rank.
**The V/A/D basis shows degeneration in today's observation** (valence and dominance have $|\cos|=0.76$–$0.80$ across all 4 layers, within-same-axis cross-layer agreement 0.10–0.45). Therefore **beating V/A/D is not strong evidence.**
A random basis and **a same-rank basis from 20 categories unrelated to emotion (topic classification)** are the primary controls.

## AM4. Stage 3: Is emotion a mixture?

**Criterion M3**: Each emotion category requires $k \geq 2$ components rather than corresponding to a single component, and also **5 held-out categories** can be reconstructed without using them in learning (cross-validation).

Due to a criticism that 20 categories can trivially be reconstructed in $r$ dimensions,
**$r < 10$ and reconstruction on held-out categories are both required.** To close off the trivial success path, cross-validation with falsely assigned dummy categories is used as a control.

## AM5. Stage 4: Can it be controlled by intervention?

Project the components back to each model's activation space via anchors and intervene.

**Criterion M4**: Intervention in the component direction, compared against content-free directions with equalized output perturbation magnitude (Haar random directions within the sensitivity subspace), moves emotional expression more. Measurement uses the signed readout of Amendment 37.

## AM6. Stage 5: Characterization discipline and naming rules

**A description given to a component is adopted only when predictions are drawn from it and confirmed on independently created novel stimuli. Descriptions that fail are discarded and not written in the paper.**

Naming takes the form of a prediction, not an interpretation. Example: if the description "component $X$ represents the speaker's departure from expectation" is proposed, create new stimulus pairs differing only in degree of departure, and test whether $X$'s response follows the predicted order.

## AM7. Scope of claims (limited in advance)

What can be claimed if all stages are passed:

> Language models have common representation components **not explained by existing human emotion description frameworks (V/A/D and emotion vocabulary categories)**, and what humans call "emotion" is constituted as a mixture of these.

**We will not write "not conceptualized by humans."** Checking against the full universe of human concepts is impossible; what can be shown is only "not explained by the human emotion description frameworks used in this study." Substantiveness is given by concretely describing the component properties and verifying them with the discipline of AM6.

## AM8. Promises

- The job will be launched **only after this file has been committed and pushed**
- $r$, layers, and anchor set will be confirmed **before seeing the results** and added to this file
- Judgement will be performed only by M1–M4; criteria will not be changed after seeing results
- If terminated at Stage 1, Paper 3 will be written with the methodological proposition of Amendment 32 AF5
