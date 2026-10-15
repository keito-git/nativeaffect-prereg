# Pre-registration Amendment 54: The causal power of emotion directions is carried solely by their component onto general axes (non-identifiability)

**Created**: 2026-10-04
**PI instruction**: 2026-10-04 "I want a surprising finding, such as that what was thought to be AI emotion is actually a constituent of a different concept."
**Status**: Adds **the central claim** on top of amendment 53 (X1–X3). Existing judgements are not changed.
**Activation condition**: X4 and X5 must not be judged until this file has been committed and pushed.

---

## BC0. Formulating the PI's "surprising finding" as a proposition

> **What was thought to be AI emotion is a constituent of a different concept.**

Converted into a testable form, this becomes:

> **The causal power of emotion directions is carried solely by their component onto more general axes, and there is no causal power in the residual unique to emotion.**

If this holds, **"emotion" is not an independently identifiable entity in the model — it is a projection of general axes.**
In the direction the PI describes as "constituent," the claim is that **emotion is merely being read as a constituent of general axes**.

## BC1. Prior work of this group must be confirmed first (anti-salami check)

**Paper 1 (AffectGeometry, under submission to IEEE TAC) already reports that the valence direction is not identifiable in decoding.** Orthogonal directions with cos≈0 yield the same decoding performance (`project_affectgeometry_direction_nonidentifiability`).

**The claim of this amendment is an extension of that, and is not identical.** The difference is stated explicitly.

| | Paper 1 | This amendment X4 |
|---|---|---|
| Target | **Decoding** (performance of linear probes) | **Causality** (effect of intervention) |
| Claim | Valence direction is not identifiable in decoding | The **causal power** of emotion directions is carried solely by their component onto general axes |
| Control | Orthogonal directions | **F4 (variance-matched in-plane) + matching of output perturbation magnitude** |

Paper 1 will be cited, and the paper will say: **"We extend the non-identifiability of decoding to the non-identifiability of causality."**

## BC2. External prior work must also be confirmed

**Sun et al. 2026 (arXiv:2604.03147) reports that the valence–arousal subspace also controls refusal and sycophancy** (as stated in the title: "Multi-Behavioral Control").

**Therefore, "emotion axes also move non-emotional behaviors" is already known.** This will not be claimed as a contribution of this study.

**What is not known is the reverse.** "There is no power in the component unique to emotion" — that is, **the emotion axis cannot be identified separately from general axes**. Sun et al. does not perform decomposition and lacks a variance-matched floor, so this claim has not been tested.

## BC3. Definition of the general axes $\mathcal{G}$ (fixed before seeing results)

$\mathcal{G}$ spans the following 3 families of directions. **Emotion-category directions are not included.**

| Family | Directions | How constructed |
|---|---|---|
| G-a | 21 evaluation dimensions | Linear regression to crowd-enVENT ratings (Tak et al. procedure) |
| G-b | Non-emotion probes Q1–Q3 | Expectation deviation, agency, certainty from amendment 46 (minimal-pair difference) |
| G-c | 2 non-emotional behaviors | Refusal and sycophancy (behaviors used by Sun et al. Difference of contrastive stimulus pairs) |

$\dim \mathcal{G} = 21 + 3 + 2 = 26$. **This construction will not be changed after seeing results.**

## BC4. Decomposition and judgement (X4)

Decompose the direction $w_e$ of emotion category $e$ (13 categories, estimated using the same procedure):

$$ w_e = \underbrace{P_\mathcal{G}\, w_e}_{\text{general-axis component}} \;+\; \underbrace{(I - P_\mathcal{G})\, w_e}_{\text{emotion-specific residual}} $$

For both components, intervene with **output perturbation magnitude (JS divergence over the top-100-word union) matched to $J^*$**, and measure the change in emotion readout.

**Judgement X4**:

- **(a)** The effect of the general-axis component $P_\mathcal{G} w_e$ **exceeds the 95th percentile of the F4 floor**
- **(b)** The effect of the emotion-specific residual $(I-P_\mathcal{G}) w_e$ **does not exceed the F4 floor**
- **(c)** As the floor for the residual, **random directions drawn with matched variance from within the residual subspace** are used (because if the residual is low-dimensional, a full-space floor would be too lenient)

**X4 is supported if (a) and (b) both hold for a majority of 13 categories × models × layers.**

**Prerequisite**: $w_e$ itself must exceed the F4 floor. If it does not, the judgement is declared **unmeasurable**, and neither success nor failure of X4 will be claimed. **(This is mandatory given the history in paper 2 where the positive control was beaten by the in-plane floor.)**

**If the residual dimension is close to 0** ($\lVert (I-P_\mathcal{G}) w_e \rVert / \lVert w_e \rVert < 0.1$), **this fact itself will be reported as a result.** It would mean that emotion directions lie almost entirely within $\mathcal{G}$.

## BC5. Layer-0 control (X5)

The layer-0 control from amendment 40 is applied to this series as well. **Paper 1 reports that subspace separation already exists at layer 0, and in amendment 45 AT1.3, the low dimensionality of E5 was already present at layer 0.**

**Judgement X5**: Estimate the emotion direction $w_e$ at layer 0 (mean pooling) and compare the overlap $\lVert P_\mathcal{G} w_e \rVert / \lVert w_e \rVert$ between layer 0 and layer $L$.

- If the overlap is already large at layer 0, **the non-identifiability is a property of lexical statistics**
- If the overlap increases at layer $L$, **the model's computation is drawing emotion into the general axes**

**Either result will be reported.** The former would mean "emotion is a projection of lexical geometry," and the latter would mean "computation turns emotion into a component of general axes" — **changing the attribution of the claim**.

## BC6. The claim if everything passes

> In language models, what is measured as emotion is **not an independently identifiable entity.** The causal power of emotion directions is carried solely by their component onto the general axes spanned by evaluation, non-emotional judgement, and non-emotional behavior; and there is no detectable causal effect, under a variance-matched floor, in the residual unique to emotion. That is, **emotion is merely being read as a projection of general axes.**

**Difference from prior work**: Linear encoding of evaluation dimensions and single-model steering are already shown by Tak et al. 2025. The control of non-emotional behaviors by emotion axes is already shown by Sun et al. 2026. Non-identifiability in decoding is already shown by paper 1. **The contribution of this study is to show causal non-identifiability under a variance-matched floor and with matched output perturbation magnitude.**

## BC7. Cases of failure (written in advance)

- **If (b) fails** (the residual also has power): emotion is not exhausted by the general axes. **Cross-reference the residual against the 16-concept catalogue of amendment 47 and report what it resembles.** This too is a result.
- **If the prerequisite fails**: Declare unmeasurable. Report as a problem of measurement resolution.
- **If the residual is approximately 0**: (b) holds trivially. **Trivial satisfaction will not be treated as support.** Since $\mathcal{G}$ has dimension 26 and $d$ is in the thousands, it is not the case that the residual vanishes by chance, but **the residual norm ratio when $\mathcal{G}$ is replaced by 26 random directions will be reported as a control**.

## BC8. Promises

- The construction of $\mathcal{G}$ (G-a/G-b/G-c, 26 directions in total) will not be changed after seeing results
- The range shown by paper 1, Tak et al. 2025, and Sun et al. 2026 will not be claimed as contributions of this study
- If the prerequisite fails, failure of X4 will not be claimed
- If the residual is approximately 0, the control using 26 random directions will be reported alongside
- In X5, whichever way it turns out, **the attribution (lexical vs. computation) will be written correctly**
