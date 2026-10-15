# Pre-Registration Amendment 72: Updating the Hypothesis to Three Levels — Retracting Fixed $Z_i$, Moving Toward Context-Conditioning and Coarse-Graining

**Created**: 2026-10-06
**Occasion**: External advice (2026-10-06)
**Status**: **Update of the primary hypothesis.** Replaces the AAPH from Amendment 41. Existing judgement results are not changed.
**Activation condition**: No judgement concerning H2 or H3 must be made until this file has been committed and pushed.

---

## BU1. Which Elements of the Amendment 41 Hypothesis Were Not Supported

Amendment 41 set the following as the primary hypothesis.

$$u_e \approx \sum_{i=1}^{k} a_{ei} Z_i, \qquad k \ll |E|$$

Here $\{Z_i\}$ are fixed global latent axes that are neither emotion categories nor human emotional dimensions.

**Identifying which elements were not supported.**

| Element | Verification | Result |
|---|---|---|
| $k \ll \|E\|$ (compression to few dimensions) | P1, P1′ | **Not held**. Low-dimensionality was already present at layer 0; no contribution from computation |
| Fixed global $Z_i$ | M1, M1′ | **Not held**. When topics are matched, cross-model agreement does not exceed chance |
| Emotion can be controlled by intervening on $Z_i$ | V1–V1″ | **Did not replicate in confirmation set** |
| $Z_i$ are not human emotional dimensions | N1, N3 | **Consistent with the negative side being observed**. Emotion-attribution directions do not align with the 30 human concepts of the catalogue to the same degree as content-sharing concept pairs |

**That is, the negative side is supported, and the form of the construction (fixed, few, global) was not supported.**

## BU2. Updated Hypothesis

$$\boxed{\;u_e(x,m) \approx \sum_{i=1}^{K} a_{ei}(x,m)\, Z_i(x,m)\;}$$

**Emotion is not formed by fixed latent axes, but is a context $x$ and model $m$ dependent set of multiple model-native computational modes, projected from the human side.**

### Change 1: Retracting $k \ll |E|$

**$|Z| > |E|$ is acceptable.** The possibility that human emotion categories are the coarser side is admitted.

Therefore, this study **does not write "AI has higher-order emotions than humans."** Instead,

> **Human emotion categories are a lossy coarse-graining of the model's internal emotion-related computation**

is written. The former contains anthropomorphism and is also unverifiable, but the latter is a proposition that can be handled within the framework of causal abstraction.

### Change 2: Making Context-Conditioning a Premise

$Z_i$ can depend on $x$. **The non-holding of M1′ is a prediction under this update.** When topics are matched, the disappearance of geometric agreement can be read as due to emotion representations being context-conditioned.

### Change 3: Asking Functional Universality Rather Than Geometric Universality

It is acceptable that $Z_i^{(A)} \not\approx Z_i^{(B)}$ across models. What is asked is the agreement of effect fingerprints:

$$\Phi(Z_i^{(A)}) \approx \Phi(Z_j^{(B)})$$

**Even if the coordinates of activation space are not shared, the possibility that the models have latent variables with the same computational role** is verified.

## BU3. Three-Level Hypothesis

| Level | Hypothesis | Current status |
|---|---|---|
| **H1** | Human emotion and appraisal axes are **not privileged computational units** in the model's internal computation | **Supported** (aggregate of M1′, X1, V1″, S, Q, N) |
| **H2** | Emotional behavior is organized by **model-native causal factors** distinct from human categories | **Unverified** |
| **H3** | Human emotion categories are the **context-dependent projection** of those factors | **Unverified** |

**The paper is not closed on H1 alone. The goal is to show at least one instance of H2.**

## BU4. Elevation of the Primary Message

Until now, the results of 5 routes were listed as individual negative results. **These are integrated into a single proposition.**

> **decodability $\neq$ computational identity**
>
> Human emotion and appraisal concepts are useful for reading the behavior of language models. However, the fact that they are linearly decodable and move when intervened upon **does not constitute evidence that those concepts themselves are implemented as computational units in the model's interior.**

**The observation that 5 routes broke down for the same reason is the most important material for this proposition.** This is presented not in the discussion section but as the claim.

## BU5. Definition of Model-Native Causal Factors (Not Making Semantic Interpretability a Condition)

$Z_i$ is defined by the following 5 conditions. **Human interpretability is not included as a condition.**

| Condition | Content |
|---|---|
| Stability | The same mode appears when stimuli are resampled |
| Causal efficacy | Intervention moves the output and exceeds the variance-matched floor |
| Behavioral consistency | Shows a consistent pattern of effects for multiple output readouts |
| Non-redundancy | Can be distinguished from other modes by effect fingerprint |
| Held-out transfer | Shows the same pattern of effects for unknown prompts |

**Stated as a declaration**: Semantic interpretability is not a criterion for identification. **However, this stance itself is a proposal by Xeno-Interpretability and is not claimed as a contribution of this study** (Amendment 71 BT3).

**$Z_i$ is not called a "concept."** The designation is **computational mode**. The correspondence with human concepts is a separate matter asked after identification.

## BU6. What Can Be Written If It Fails

- **If H2 fails**: "Under a variance-matched floor, stable causal modes that organize emotional behavior could not be identified." **Written within the scope of H1**
- **If the fingerprint space is variance-dominated**: H2 is not performed due to the kill switch in Amendment 73. That fact and the reason are written

## BU7. Commitments

- The elements of the Amendment 41 hypothesis that were not supported are shown in the table of BU1 in the paper. They are not hidden
- The fact that $k \ll |E|$ was retracted is written. It is not written as if it passed without being retracted
- "AI has higher-order emotions than humans" is not written. It is written as coarse-graining
- $Z_i$ is not called "concept"; it is called "computational mode"
- The stance of not making semantic interpretation an identification criterion is attributed to Xeno-Interpretability
- If the paper is closed only on H1, the fact that H2 and H3 are unverified is stated
