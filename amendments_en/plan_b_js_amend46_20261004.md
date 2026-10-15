# Pre-registration Amendment 46: Operationally defining "higher-order" — causal asymmetry, emotion non-exclusivity, and compositionality

**Created**: 2026-10-04
**Status**: A **supplement** to Amendment 38 (cross-model shared components), Stages 2–4. M1–M4 are not changed.
**Activation condition**: The judgements of H-A / H-B must not be performed until this file has been committed and pushed. The results of Stage 1 (M1) have not been obtained at the time of creating this file.

---

## AU0. Confirmation of the principal investigator's goal (2026-10-04)

> **It would be desirable to show that AI captures emotion using a different, higher-order concept.**
> Whether humans know that concept or not does not matter.

The form of the claim follows Amendment 38 AM7 unchanged.

> Language models possess common representational components not explained by the human emotion description frameworks used in this research (V/A/D and emotion vocabulary categories), and what humans call emotions is constructed as a mixture of those components.

**Proving that "humans have not conceptualised" it is removed from the goals of this research.** It is impossible to verify against the entirety of human concepts, and the limitation stated in Amendment 38 AM7 is preserved. Instead, **higher-orderness itself is measured**.

## AU1. Problem: "higher-order" is not yet a testable predicate

"The component is higher-order than emotion" is, as stated, not a falsifiable proposition. **The route via dimensionality count is already closed** (Amendment 45 AT1: P1 was not supported. In E5, the low dimensionality is explained by lexical statistics at layer 0, and there is no contribution from computation).

Therefore, higher-orderness is defined **not by smallness of dimension, but by the direction and scope of dependency**.

## AU2. Operational definitions of higher-orderness (3 senses; each tested independently)

### H-A Causal asymmetry (strongest sense)

Let $Z$ be the direction of the shared component and $E$ be the human emotion direction (the Warriner valence direction obtained in Paper 1, and the contrast directions of emotion categories).

- An intervention on $Z$ moves the emotion readout
- An intervention on $E$ does not move the projection onto $Z$

**If emotion is primary, the dependency is symmetric or in the opposite direction.** If it is asymmetric, $Z$ is upstream.

**Estimator**: Using the signed readout from Amendment 37, $S(v) = \tfrac12[R(h+\alpha v) - R(h-\alpha v)]$,

$$\mathrm{Asym} = \frac{|S_{Z \to E}|}{|S_{E \to Z}|}$$

**Equalising output perturbation**: The $\alpha$ for each direction is individually calibrated so that the JS divergence of the next-token distribution (over the union of the top-100 words) reaches the target value ($\mathrm{JS}=0.05$) before comparing. Without equalization, the result would only reflect "the direction that hits harder moves more."

**Control (mandatory; lesson from Paper 2)**: For both $Z$ and $E$, place **VMIC** (within-plane random directions with matched variance). Random directions from the full space are not used.

**Judgement H-A**: $\mathrm{Asym}$ significantly exceeds 1, and the effect of $Z \to E$ exceeds the VMIC floor. This is required in **at least 3 of 4 layers**.

**Prerequisite (H-A will be judged as unmeasurable if this does not pass)**: As a positive control, an intervention on the Warriner valence direction moves the emotion readout above the VMIC floor. If it does not, the readout resolution is insufficient, and **the non-satisfaction of H-A will not be claimed.** (Because in Paper 2 the positive control lost to the within-plane floor, this must always be confirmed first.)

### H-B Non-exclusivity to emotion

If it is a higher-order concept, it should **not be exclusive to emotion**. If the same component governs judgements other than emotion, that component is more general than emotion.

**Non-emotion probes (fixed to 3 before seeing results)**:

| Symbol | Probe | Measurement method |
|---|---|---|
| Q1 | Deviation from expectation (degree of expectation violation) | Next-token JS on stimulus pairs that differ only in degree of deviation |
| Q2 | Attribution of agency (who caused it) | Next-token JS on stimulus pairs with the agent swapped |
| Q3 | Degree of certainty (assertion vs. hedge) | Next-token JS on stimulus pairs differing only in modal auxiliary |

All are constructed with stimuli **containing no emotion words**, and no annotators are used (no human annotation).

**Judgement H-B**: Each component $Z_i$ has an effect exceeding the VMIC floor on at least 1 of Q1–Q3, **and** the set of components does not partition into "components that load only on emotion probes" and "components that load only on non-emotion probes" (if it does partition, an emotion-exclusive component exists and the higher-orderness claim is weakened).

Whether partition occurs is judged by comparing the modularity of bipartite clustering on the component × probe effect matrix against **a null of random assignment**.

### H-C Compositionality

As stated in Amendment 38 M3. Each emotion category does not correspond to a single component but requires $k \geq 2$ components, and the **5 held-out categories** can be reconstructed without using them in learning. $r < 10$ is mandatory.

## AU3. Hierarchy of claims (what can be written depending on how far judgements pass)

| Judgements passed | What can be written |
|---|---|
| M1 only | There is a shared representation across models not explained by sentence form (**already known; no novelty**) |
| M1+M2 | The shared components are not the human V/A/D and emotion category axes themselves |
| +H-C | Human emotion categories are constructed as a mixture of shared components |
| +H-B | The shared components are not exclusive to emotion and also govern more general judgements |
| **+H-A** | **The shared components are upstream of emotion readout (the dependency is asymmetric)** |

**Only when H-A passes will the paper write "AI captures emotion using a higher-order concept."** If it does not pass, the paper will remain within the scope of H-B and H-C — "emotion can be described as a mixture of shared components" — and **the words upstream and higher-order will not be used**.

## AU4. Points likely to fail under this definition (written in advance)

- **H-A cannot be measured if $Z$ and $E$ are aligned.** In the observations from Paper 2, the axes were 88.7–99.97% contained within the top-10 principal component space. If $Z$ is similar, the separation of $Z$ and $E$ itself may not hold. In this case, record as **unmeasurable**.
- **Equalising output perturbation may cause the effect to disappear.** In Paper 2, the floor ratio for C1 was 1.795–2.429, whereas C2b was 0/16. If the same occurs, H-A is not satisfied.
- **H-B becomes meaningless if the components are "too general."** A component that moves every probe may simply be a direction that strongly affects output. For this reason, a VMIC floor is placed on each probe.

## AU5. Promises

- H-A / H-B will be judged after this file is pushed
- Probes Q1–Q3 and the 5 held-out categories are fixed **before seeing the results**, and hashes will be appended to this file when the stimuli are created
- If the prerequisite condition for H-A (positive control) does not pass, **the non-satisfaction of H-A will not be claimed**
- The words higher-order and upstream are used only when H-A passes. They will not be used if it does not pass
- The fact that M1 is an already-known result will be explicitly stated in the paper, and **M1 will not be claimed as a novelty**
