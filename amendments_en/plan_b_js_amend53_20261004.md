# Pre-registration Amendment 53: Three claims stacked on top of the audit — exhaustion, asymmetry, and cross-model transfer

**Created**: 2026-10-04
**PI instruction**: 2026-10-04 "Make findings more interesting than prior work. Show that AI emotion is composed of different concepts, can be generalized, and can even be intervened upon."
**Status**: The audit from amendment 49 is retained as the **methodology and reliability layer**, and the main results are stacked on top of it. Existing judgements V1–V3 and W1 are not changed.
**Activation condition**: X1–X3 must not be judged until this file has been committed and pushed. Stage A (probe reproduction) does not include judgements and is therefore already running.

---

## BB0. What prior work has already shown (cannot be claimed further)

- Evaluation dimensions are linearly encoded inside LLMs (Tak et al. 2025, arXiv:2502.05489)
- Intervening on evaluation dimensions moves the emotional content of outputs as predicted by theory (ibid.). **Confirmed across 10 model families**
- The valence–arousal subspace has a circular geometry, and steering provides monotonic control (Sun et al. 2026, arXiv:2604.03147). **With in-plane random controls**

**Therefore, there is no novelty in merely claiming "emotion is composed of evaluation concepts and can be intervened upon."**
To achieve the PI's goal, it is necessary to show **what prior work has not done**.

## BB1. Three things prior work has not done

| | Question | Why it is absent in prior work |
|---|---|---|
| **X1 Exhaustion** | Is the emotion-category structure **exhausted** by the evaluation subspace? If the evaluation subspace is projected out, does decoding of emotion become impossible? | Prior work shows "evaluation affects emotion," but does not show that **nothing remains in the residual** |
| **X2 Asymmetry** | Intervening on evaluation directions moves emotion, but does **intervening on emotion directions not move evaluation** (with output perturbation magnitude matched)? | Prior work does not compare both directions under matched conditions |
| **X3 Cross-model transfer** | If an evaluation direction estimated on model A is **transferred to model B via anchors and used to intervene**, does B's emotional output move? | Prior work trains probes for each model separately. **Direction transfer is not performed** |

**X3 is the main result.** The strongest form of "can be generalized" is that the same direction works in a different model.

## BB2. X1 Exhaustion (does emotion close as a mixture of evaluation?)

Let the evaluation subspace be $\mathcal{A} = \mathrm{span}\{v_a\}_{a=1}^{21}$.

**Estimator**: Linear decoding accuracy for 13 emotion categories is measured under 3 conditions (cross-validation, macro-F1).

1. Original representation $h$
2. Residual $(I - P_\mathcal{A}) h$ with the evaluation subspace projected out
3. **Random subspace** projected out ($\dim = 21$, 500 runs)

**Judgement X1**: Accuracy in condition 2 drops significantly from condition 1, **and** that drop exceeds the 95th percentile of the drop in condition 3. **Furthermore**, accuracy in condition 2 is indistinguishable from chance (1/13).

**The last requirement is the core of "exhaustion."** A mere drop only shows "evaluation also contributes." **Only when it falls to chance level can one say "emotion is exhausted by evaluation."**

**What can be written if it fails**: Report the components remaining in the residual, and **cross-reference them against the catalogue in amendment 47.** If the residual does not resemble anything in the catalogue, report this as amendment 47 N3.

## BB3. X2 Asymmetry (bidirectional comparison with output perturbation magnitude matched)

The same estimator as amendment 46 H-A, but the difference is that **evaluation dimensions are placed on the upstream-candidate side rather than the human-concept side**.

- $Z$ = evaluation-dimension directions $z_a$ (supervised, Tak et al. procedure)
- $E$ = emotion-category directions $w_e$ (estimated from 13 categories using the same procedure)

$$\mathrm{Asym}(a, e) = \frac{\lvert S_{z_a \to e}\rvert}{\lvert S_{w_e \to a}\rvert}$$

$S_{z_a \to e}$ is the change in emotion readout from intervening on $z_a$, and $S_{w_e \to a}$ is the change in predicted evaluation value from intervening on $w_e$. **JS divergence is matched to $J^*$ in both directions.**

**Judgement X2**: $\mathrm{Asym} > 1$ holds for a majority of the 21×13 cells, **and** for both directions, the F4 (VMIC) floor is exceeded. **If $Z \to E$ does not exceed the floor, the judgement is declared unmeasurable.**

**Prerequisite**: Amendment 49 V3 (positive control) must pass. If it does not pass, X2 will not be judged.

## BB4. X3 Cross-model transfer (main result)

**Procedure**

1. Estimate evaluation direction $z_a^{(A)}$ at layer $L_A$ of model A
2. Take representations $H_A, H_B \in \mathbb{R}^{120 \times d}$ of both models for the common anchor set $\mathcal{S}$ (120 sentences from amendment 45 E1, no emotion words)
3. Solve **orthogonal Procrustes**: $Q = \arg\min_{Q^\top Q = I} \lVert H_A Q - H_B \rVert_F$
4. Normalize the transferred direction $\tilde z_a^{(B)} = Q^\top z_a^{(A)}$
5. Intervene on model B with $\tilde z_a^{(B)}$ and measure the change in B's emotional output

**Controls (mandatory, 4 types)**

| Symbol | Control | What it rules out |
|---|---|---|
| T1 | $z_a^{(B)}$ estimated natively on B | Upper bound for transfer (exceeding this is not required) |
| T2 | **Post-mapping F4 floor** (variance-matched random directions passed through $Q$) | The possibility that the mapping itself creates the effect |
| T3 | **Transfer of a direction estimated with permuted labels** | The possibility that the procedure rather than the evaluation content is responsible |
| T4 | **Transfer with $Q$ replaced by a random orthogonal matrix** | The possibility that $Q$ is genuinely responsible for correspondence |

**Judgement X3**: The effect of the transferred direction $\tilde z_a^{(B)}$ **exceeds the 95th percentile of all three of T2, T3, and T4**. To match paired directionality, **both directions of the model pair** (A→B and B→A) are measured. **The pass rate is reported for all available model pairs.**

**Pass condition**: Satisfied for a majority of all pairs. **If a majority is not reached, report the pairs and their scale and family for which it was satisfied, and write it as "the range over which transfer holds."** Satisfaction across all models is not required.

## BB5. Form of the claims (if everything passes)

> In language models, what humans call emotion categories is **exhausted** by the subspace of more general evaluation concepts (X1). The dependency is **asymmetric**, with evaluation concepts upstream of emotion (X2). The directions are **not model-specific** — a direction estimated on one model can be transferred to another model via common anchors, and the transferred direction controls the emotional output of the target model (X3). These hold under **in-plane random floors with matched variance** and **comparisons with matched output perturbation magnitude**.

**The difference from prior work will be stated explicitly**: Linear encoding of evaluation dimensions and single-model steering are already shown by Tak et al. 2025. The contributions of this study are **exhaustion, asymmetry, and cross-model transfer**, and **the floors that support them**.

## BB6. Possibility of failure (written in advance)

- **X1 is likely to fail.** Requiring emotion categories to fall to chance level is a strong demand. If it fails, the analysis will shift to characterizing the residual components.
- **X3 may fail because Procrustes may not hold.** Amendment 50 found that when topics are matched, agreement of emotion categories across models does not exceed chance. **However, evaluation dimensions are continuous quantities, and this is a different question from category agreement.** The cross-model correlation of evaluation-dimension predictions will be measured first, and **if that correlation is at chance level, X3 will not be run** (to avoid wasting resources).
- **X2 may be unmeasurable if $Z$ and $E$ are matched.** It will be recorded as unmeasurable.

## BB7. Execution order (with kill switches)

1. **Stage A**: Probe reproduction (currently running). If $R^2$ is not comparable to the original paper, the procedure will be revised.
2. **Stage B0**: Cross-model correlation of evaluation-dimension predictions. **If at chance level, X3 is stopped.**
3. **Stage B1**: V1–V3 (audit) + W1
4. **Stage B2**: X1 (exhaustion)
5. **Stage B3**: X2 (asymmetry). Only if V3 passes.
6. **Stage B4**: X3 (cross-model transfer). Only if Stage B0 passes.

**The judgement result of each stage will be recorded before proceeding to the next stage.**

## BB8. Promises

- The criteria for X1–X3 will not be changed after seeing results
- The range already shown by prior work will not be claimed as contributions of this study
- Failed judgements will not be omitted. If X1 fails, that failure will be written
- If X3 is satisfied only for some model pairs, **the claim will be limited to the range of satisfaction**. It will not be generalized to the whole
- If Stage B0 is at chance level, X3 will not be run, and **both the fact that it was not run and the reason will be written**
