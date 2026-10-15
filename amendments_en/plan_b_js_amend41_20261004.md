# Pre-registration Amendment 41: Formulating the Artificial Affect Projection Hypothesis (AAPH) as the main hypothesis of this research series

**Created**: 2026-10-04
**Proposed by**: The principal investigator
**Status**: Rewrites the main series of Amendment 38 in a clearer hypothesis form. Does not change the existing judgements in Amendments 29–40.
**Activation condition**: No job based on this hypothesis shall be launched unless this file has been committed and pushed beforehand.

---

## AP0. Hypothesis

> **Anger, fear, joy, sadness and other human emotions as such do not exist inside a language model.**
> There exist latent computational concepts $Z_1,\dots,Z_k$, and human emotion categories are
> **secondary phenomena** — projections of multiple directions in that AI-native latent space.

Formally, the representation $u_e$ of emotion category $e$ can be written as

$$u_e \approx \sum_{i=1}^{k} a_{ei} Z_i, \qquad k \ll |E|$$

where $\{Z_i\}$ are neither emotion categories nor human emotion dimensions.

Candidate examples of $Z_i$ suggested by the principal investigator: how strongly the situation demands a state change; how predictable the world is judged to be; whether the agent should approach or avoid the target; whether causation is attributed to the self or to the outside world; how controllable the future state is judged to be.

## AP1. The direction of inquiry is the reverse of prior work

The majority of prior work proceeds in the direction **human emotion concept → search for it inside the LLM**. Zou et al.'s representation engineering extracts directions using principal components and performs interventions~[1]; Sun et al. extract the valence–arousal subspace using principal components and validate it with 9 controls~[2]. Both **take the human emotion framework as given and ask whether it exists inside the model**.

This study reverses that direction.

> **AI-native representation → human emotions are merely one projection of it**

[1] Zou, A. et al. "Representation Engineering: A Top-Down Approach to AI Transparency."
    arXiv:2310.01405, 2023.
[2] Sun, L. et al. "Valence-Arousal Subspace in LLMs." arXiv:2604.03147, 2026.

## AP2. Existing negative results are predictions of this hypothesis

**This is the primary reason for adopting this hypothesis.** The negative results this research series has obtained so far were individually "failures to demonstrate emotion specificity," but under AAPH they all become **predictions**.

| Existing observation | Old reading | **Reading under AAPH** |
|---|---|---|
| Emotion-derived directions move mathematical stimuli equally or more (Amendment 32 AF3) | No domain specificity = failure | **$Z_i$ are domain-general, so this is expected** |
| Stimulus profiles of directions are uncorrelated with valence (same as null) | No content selectivity = failure | **Valence is a projection, not a basis** |
| Even signed readout falls below the content-free control (Amendment 39, 0/4 layers) | Content not detected = failure | **The component along the human axis is small** |
| Estimation of human V/A/D degenerates (valence and dominance are parallel) | Measurement deficiency | **A sign that the human axes are not the model's basis** |

**A single hypothesis simultaneously explains four independently obtained negative results.** This is an indicator of the strength of the hypothesis, and the fact that it is not post-hoc rationalization is guaranteed by the fact that each observation was obtained under pre-registration **before** the formulation of this hypothesis.

## AP3. Testable predictions and the controls that would kill them

### P1: Intrinsic dimensionality is small

**Prediction**: The intrinsic dimensionality $k$ of the representations of 40 emotion categories is substantially smaller than $|E|=40$.
**Estimator**: The number of dimensions explaining 90% of the variance, from the singular value spectrum of the category means $\{u_e\}$.
**Null**: Random category assignment with the same count and dimensionality (label permutation within skeleton, 500 iterations).
**Killing control**: If the same $k$ is obtained at layer 0 (vocabulary baseline, Amendment 40), the low dimensionality is a property of vocabulary statistics and not of computation. **P1 is not established if the reduction in $k$ does not exceed layer 0.**

### P2: The axes are not the human framework

**Prediction**: The recovered $\{Z_i\}$ do not correspond to individual emotion categories or to human V/A/D.
**Estimator**: The maximum absolute cosine between each $Z_i$ and (a) the contrast of each category, (b) each V/A/D axis, and (c) appraisal dimensions (6 dimensions of Smith & Ellsworth 1985).
**Killing control**: If a V/A/D basis or appraisal-dimension basis of the same rank provides an equivalent reconstruction as $\{Z_i\}$, they cannot be called AI-native. **P2 is not established if it cannot beat any of the three human frameworks.**

**Note**: Appraisal dimensions are a human theory. If $Z_i$ match appraisal dimensions, the claim that "humans have not named them" does not hold. In that case, the claim will be rewritten to: **"The model internalizes not phenomenological emotion categories but cognitive appraisal processes that are not specific to emotion"** (a proposal from the group, Amendment 38). This is not weakening the claim but refining it.

### P3: The axes are domain-general (reuse of existing results as a prediction)

**Prediction**: The same $\{Z_i\}$ also vary for non-emotion domain stimuli (mathematics, grammar).
**This has already been observed in Amendment 32 AF3.** Under this hypothesis, this is a success, not a failure.
**Killing control**: If the cross-domain variation is explained by the vocabulary statistics of layer 0, it is meaningless.

### P4: Emotion categories can be reconstructed by combination

**Prediction**: Each category is represented as a combination of $k' \geq 2$ $Z_i$'s, and **held-out categories not used in training** can also be reconstructed.
**Killing control**: If the same cross-validation passes for randomly assigned fake categories, the reconstruction is a trivial property of dimensionality (red-team attack 5). **Both $k < 10$ and success on held-out categories are required.**

### P5: The axes reappear across models

**Prediction**: The same type of $\{Z_i\}$ is obtained across multiple models.
**Procedure**: Create a common coordinate system using the relative representations (anchor similarity profiles) of Amendment 38.
**Killing control**: If the agreement disappears in the residual after removing surface statistics, the sharing is sharing of sentence form (M1).

## AP4. Scope of possible claims (limited in advance)

If all predictions pass, what can be claimed is only the following:

> The emotion category representations of language models are described as **projections of domain-general axes far fewer in number than the number of categories**, and those axes are **not explained by the human emotion frameworks used in this study (emotion categories, V/A/D, appraisal dimensions)**.

**We will not write "not conceptualized by humans."** It is impossible to compare against all human concepts. What can be shown is only "not explained by the frameworks used in this study"; the substantive content will be given by describing the properties of $Z_i$ concretely and establishing and testing predictions from that description with new stimuli (Amendment 38 AM6).

## AP5. Name

**Artificial Affect Projection Hypothesis (AAPH)** is adopted as the name of the main hypothesis of this research series. It will be used as the central claim of Paper 3.

## AP6. Relationship to existing series

- The methodological proposition of Amendment 32 AF5 (the selection criterion determines the feasibility of intervention) is **maintained**. It is the content of Paper 3 in the event that AAPH does not hold, and if it does hold, it functions as corroborating evidence for AAPH.
- H3 from Amendment 34 (cross-model generalization of the sensitivity subspace), which was withdrawn, **will not be revived**. As control R demonstrated, that was weight geometry and not $Z_i$.
- The layer 0 baseline of Amendment 40 is **applied to all of P1–P4**.

## AP7. Promises

- No job based on AAPH will be launched unless this file has been committed and pushed beforehand.
- The criterion for determining $k$, the method of selecting held-out categories, and the source of the appraisal dimensions will be confirmed **before seeing the results** and registered in a subsequent amendment.
- If any of P1–P5 is not established, that fact will be recorded and claims will be limited to that scope.
