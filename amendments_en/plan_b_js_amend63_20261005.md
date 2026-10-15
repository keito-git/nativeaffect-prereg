# Pre-Registration Amendment 63: The Appraisal Readout in X2 Is Circular. Replacing It with an Output-Side Readout

**Created**: 2026-10-05
**Target**: Judgement X2 (asymmetry) in Amendment 53 BB3
**Judgement**: **The registered X2 is circular and will not be run. Replacing it with an output-side readout.**
**Activation condition**: X2′ must not be run until this file has been committed and pushed. X2 has never been run, so this is not a change made after seeing results.

---

## BL1. The Registered X2 Is Circular

Amendment 53 BB3 registered the following.

$$\mathrm{Asym}(a, e) = \frac{\lvert S_{z_a \to e}\rvert}{\lvert S_{w_e \to a}\rvert}$$

> $S_{w_e \to a}$ is the change in **the predicted value of appraisal $a$** due to an intervention on $w_e$.

**This is circular.** The predicted value of appraisal $a$ is a linear probe $\hat r_a = v_a^\top h + b_a$ applied to the hidden state $h$. An intervention is $h \leftarrow h + \alpha w_e$, so

$$\hat r_a(h + \alpha w_e) - \hat r_a(h) = \alpha\, v_a^\top w_e$$

**This does not depend on the stimulus or on the model's computation; it is a deterministic quantity determined solely by $\alpha$ and the inner product.** This does not measure the effect of an intervention; it merely measures **the geometric relationship between two directions**.

For the same reason, the $S_{z_a \to e}$ side is also circular if the emotion readout is a hidden-state probe. **The emotion readout in this study uses the output side (next-token probabilities of 13 emotion words), so that side is not circular.**

**Even if asymmetry were found, it could arise from "the asymmetric normalization of the inner product between $v_a$ and $w_e$."** Therefore, the registered X2 is not run.

## BL2. Replacement: Reading Appraisal on the Output Side As Well

**The appraisal readout is replaced from hidden-state probes to output-side question answering.**

For each evaluation dimension, a **binary question** is prepared, and the ratio of the next-token probabilities of `yes` / `no` is used as the readout.

$$ R_a(h) = \log \frac{p(\text{yes})}{p(\text{no})} \quad\text{(for a question asking about the given evaluation dimension)} $$

The effect of an intervention follows the antisymmetric component per Amendment 37.

$$ S_{v \to a} = \tfrac12\big[R_a(h + \alpha v) - R_a(h - \alpha v)\big] $$

**This is an output-side quantity and is not determined solely by the inner product with the intervened direction.**

### Question Texts (21 items, fixed in this amendment)

| Evaluation dimension | Question |
|---|---|
| suddenness | Did this happen suddenly? |
| familiarity | Had this person been in this kind of situation before? |
| predict_event | Could this event have been predicted? |
| pleasantness | Was this pleasant for the person? |
| unpleasantness | Was this unpleasant for the person? |
| goal_relevance | Did this matter to the person's goals? |
| chance_responsblt | Was this caused by chance? |
| self_responsblt | Was the person responsible for this? |
| other_responsblt | Was someone else responsible for this? |
| predict_conseq | Could the consequences have been predicted? |
| goal_support | Did this help the person's goals? |
| urgency | Did this require immediate action? |
| self_control | Could the person control this? |
| other_control | Could someone else control this? |
| chance_control | Was this outside anyone's control? |
| accept_conseq | Could the person accept the consequences? |
| standards | Did this violate the person's own standards? |
| social_norms | Did this violate social norms? |
| attention | Did the person attend to this closely? |
| not_consider | Did the person try not to think about this? |
| effort | Did this require effort from the person? |

The question texts are placed after the stimulus (the description from crowd-enVENT). **The question texts are not changed after seeing the results.**

## BL3. Judgement X2′

$$ \mathrm{Asym}(a, e) = \frac{S_{z_a \to e}}{S_{w_e \to a}} $$

However, **both sides use output-side readouts**, and **both have output perturbation equalized to $J^\*$.**

- $S_{z_a \to e}$: Signed effect of an intervention on appraisal direction $z_a$ in the direction of emotion contrast $c_a$ (same as $S$ in Amendment 58)
- $S_{w_e \to a}$: Signed change in the log-odds of the appraisal question due to an intervention on emotion direction $w_e$

**Judgement X2′**: Judged as a family (aligned with the policy in Amendment 60). Comparing $\overline{S_{Z \to E}}$ and $\overline{S_{E \to Z}}$ each against the F4 floor:

- **(a)** $\overline{S_{Z \to E}}$ **exceeds** the 95th percentile of the F4 floor
- **(b)** $\overline{S_{E \to Z}}$ **does not exceed** the 95th percentile of the F4 floor

**If both (a) and (b) hold, asymmetry is supported.**

**Prerequisite**: The (b)-side readout is confirmed to be functional. **As a positive control for the appraisal question**, it is confirmed that the log-odds moves for stimulus pairs that directly ask about the given evaluation dimension (minimum pairs from Q1–Q3 in Amendment 56). **If it does not move, the non-holding of (b) is not claimed** (asymmetric treatment same as V3 in Amendment 49).

## BL4. Limitations That Remain in This Design (Written in Advance)

- **The output-side readout depends on the question text.** Changing the question text could change the results. **The limitation that only one set of question texts was used is written**
- **(b) not exceeding does not mean "there is no effect."** It only means it cannot be detected. **"Emotion directions do not move appraisal" is not written; instead, "cannot be detected under a variance-matched floor" is written**
- Emotion direction $w_e$ is a regression onto indicator variables for 13 categories, and $R^2$ may be low. **$R^2$ is reported, and if it is low, it is not used in interpreting (b)**

## BL5. Commitments

- The registered X2 (hidden-state probe) is **not run**. The fact that it was circular is written in the paper
- The 21 question texts are fixed in this amendment and are not changed after seeing results
- If the prerequisite for (b) fails, asymmetry is not claimed
- "Does not move" is not written; "cannot be detected" is written
