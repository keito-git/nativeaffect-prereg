# Pre-registration Amendment 20: Full-text confirmation of Braun et al. Claim ② is independent. Two prior studies conflict with each other.

**Target**: Amendment 14 N7 (obligation to confirm priority), Amendment 15 O2 (judgement on claim ②)
**Created**: a group member / 2026-09-26
**Status**: **G1 judgement statistics have not been computed**
**Source**: Full PDF of arXiv:2505.22637 (obtained and read directly by the group member)

---

## T1. Bibliographic information

**Joschka Braun, Carsten Eickhoff, David Krueger, Seyed Ali Bahrainian, Dmitrii Krasheninnikov (2025). Understanding (Un)Reliability of Steering Vectors in Language Models.** arXiv:2505.22637. **Presented at the ICLR 2025 Workshop on Foundation Models in the Wild.**

**The peer review standard is workshop level.** It is not a main-conference paper. When citing in Related Work, this must be stated explicitly.

## T2. Their quantity (from the original text)

$$d' = \frac{\mu_+ - \mu_-}{\sqrt{\tfrac{1}{2}(\sigma_+^2 + \sigma_-^2)}}$$

> where $\mu_+$ and $\mu_-$ are the means of the positive and negative activations **projected onto the difference-of-means line**, and $\sigma_+^2$ and $\sigma_-^2$ are their respective **variances along this line**. A higher $d'$ indicates better separation.

Claim:

> Both directional agreement, as measured by cosine similarity and separability of activations, as measured by the discriminability index $d'$, are correlated with each other and are both **predictive of a larger steering effect size** and lower fraction of anti-steerable samples.

## T3. Judgement: claim ② is **independent** (confirmed after reading the full text)

**These are different quantities.**

| | Braun et al. | Our claim ② |
|---|---|---|
| What is measured | **How well two classes of activations separate along a single direction (the difference-of-means line)** | **Where the steering direction lies in the covariance eigenbasis** |
| Meaning of variance | **Within-class variance** (variance of each class after projection) | **Covariance eigenstructure of the activation cloud** (projection lengths onto the top-10 principal components) |
| Dimension | **1-dimensional** (a single difference-of-means line) | **10-dimensional** (vector of projection lengths onto the top-10 principal components) |
| Direction of claim | High $d'$ → larger effect (forward direction) | Can projection lengths predict JS? (**predictability itself**) |
| Held-out $R^2$ | **Not reported** | Will be reported |

**Therefore claim ② is independent.** The judgement in Amendment 15 O2 is corroborated by the full-text confirmation.

**However, citation is necessary.** It will be placed in Related Work as a precedent for the concern that "the magnitude of a steering effect may be explainable by geometric quantities rather than the semantic content of a direction." **We will not write "we were the first to point this out."**

## T4. Finding: two prior studies conflict with each other

**Braun et al. (ICLR 2025 Workshop)**: Class separability $d'$ **predicts** the steering effect.

**CRH (Gao et al., ICML 2026)**: Separability estimates **do not always correlate well** with actual steering outcomes.

> "these estimates do not always correlate well with actual steering outcomes"

**The two studies make contradictory claims about the same family of quantities (Fisher-type class separation).** A literature check had identified CRH's separability as "Fisher-type between-class distance $d'$," and the full-text confirmation now establishes that this is the same quantity as Braun et al.'s $d'$.

**This conflict is favorable to us. We fix the wording.**

> Concerning whether class separability predicts steerability, prior studies are not in agreement (Braun et al. 2025 report that it does, Gao et al. 2026 report that it does not). **What the present study measures is a third quantity—the position of a direction in the covariance eigenstructure—and it belongs to neither side of this conflict.**

**Constraints against overclaiming**:
- **We will not judge which is correct.** The two studies differ in model, behavior, and outcome measure
- **We will not write "prior studies are confused."** We will go only as far as "not in agreement"
- **We will not write that our quantity is superior.** We will write that it is a different quantity

## T5. Completing the obligations of Amendment 14 N7

N7 required confirmation on 3 points. **All are complete.**

| Inquiry item | Judgement | Basis |
|---|---|---|
| ① "Unidentifiability from the alignment of J's top singular directions with principal components" | **Partial overlap** (the first half was previously known) | Amendment 15 O1 (full text of Gao et al. 2608.22985) |
| ② Quantifying effect size from variance profiles | **Independent** (confirmed after full-text reading) | This amendment |
| ③ Studies in general where effects are explained by geometric quantities | **Independent** (related work exists in the vicinity) | Amendment 15 O2 + this amendment |

**① will not be claimed** (withdrawn in Amendment 15; the prediction P also missed). **② and ③ will be written with "to the best of our knowledge."**
