# Pre-Registration Amendment 4: The Premise of B3-a Was the Opposite of Prior Research. Correcting the Direction of the Hypothesis Before the Experiment

**Target**: Amendment 2's B3-a (contrast with human VAD directions), Amendment 3's C4
**Created**: 2026-09-26
**Status**: **Before experiment.** Before push
**Source**: Addendum to `01_調査/採択手法の先行性調査_20260926.md` (team full-text confirmation ○ of E-STEER)

---

## D1. What Was Wrong

In Amendment 2's B3-a, the following expectation was written.

> Human emotion distorts cognition, so it is expected that raising arousal increases speed but causes errors.
> **If Axis X does not drop, the form of the claim becomes "no side effects precisely because it is outside the human framework."**

**This expectation is the opposite of prior research.**

The full text of E-STEER (arXiv:2604.00005) reports that **activation interventions on human VAD directions improve reasoning accuracy** (confirmed in full text by the team, with original text cited).

- At moderate valence states, neutral ratio **average +3.4%**
- Dominance direction, **maximum +14.5%**
- Deterioration at extreme states: excessive activation causes reasoning to terminate early

**That is, it is an inverted U (non-monotonic), and it is not a finding that "emotional interventions deteriorate accuracy."**

**Therefore, the form of the claim "no side effects precisely because it is outside the human framework" does not hold.** Human axes also have improvement (at moderate levels), not side effects.

## D2. How to Replace the Hypothesis

**Claim to abandon**: Intervention on human axes deteriorates accuracy, but our axis does not.

**Replacement claim (fixed before the experiment)**: **Human VAD directions improve accuracy, but they do not come with reduction in computation. Our axis moves the frontier of accuracy and computation itself.**

Factual breakdown forming the basis:
- E-STEER measures **accuracy** but **does not measure token count or computation** (within the range of the team's full-text confirmation)
- Therefore "whether human axes move the accuracy/token frontier" is **unreported**
- **Our comparison target is here**

**Revised B3-a**:
1. For human VAD 3 directions, **sweep the coefficient and measure both accuracy and token count**. Confirm whether the inverted U of E-STEER can be reproduced in our environment (**if it cannot be reproduced, report that it could not be reproduced**)
2. Perform the same measurement for Axis X
3. **Plot the curves of both in the plane of accuracy vs. token count and compare the positions of the frontiers**
4. Judgement: **Does a region exist where the Axis X curve is above (higher accuracy at the same token count, or lower tokens at the same accuracy) all 3 curves of human VAD?**

**Judgement criterion decided in advance**: On one primary benchmark, **the Axis X frontier exceeds all 3 of the human VAD curves over at least one-third of the token count range**. The 95% CI of a paired bootstrap (2000 iterations) does not straddle 0.

**If it fails**: Record "Axis X and our axis cannot be distinguished from human axes on the accuracy/computation frontier." **In that case, the central claim of Amendment 2 (concepts are defined by how computation is distributed) is not supported.** Write it without rephrasing.

## D3. Treatment of E-STEER

- **Must be cited.** As a prior work that showed emotional activation interventions affect reasoning accuracy
- **Correctly describe the inverted U (improvement at moderate levels, deterioration at excessive levels).** Do not write "emotional intervention worsens reasoning." **The original text does not say that**
- Limit our difference to 2 points: (a) **measuring computation**, (b) **using axes that are not human VAD axes**
- The team confirmed in full text that E-STEER only uses VAD axes and **does not have an experimental design comparing different axes**. **Therefore the axis contrast itself is independent. However, attach "to our knowledge"**

## D4. What This Correction Means (Recording Honestly)

**The expectation in the most important experiment set up in Amendment 2 was in the opposite direction from prior research.** The cause was that the claim was based on the common sense that "human emotion distorts cognition," without confirming prior research.
**The team was instructed to do the full-text confirmation before the experiment, and it was discovered before running.** If it had been discovered after running, a manuscript would have existed that wrote "human axes deteriorate" without knowing the inverted U.

**Recurrence prevention**: Before deciding the direction of a hypothesis, confirm at least one prior work that claims that direction. **Do not use common sense as the basis.**

## D5. The Motivational Difference Was Confirmed in Full Text (Finalizing C1 of Amendment 3)

The team confirmed the full texts of the 4 isometric intervention works. The motivations are, in order: coefficient sensitivity to layer-norm fluctuations / distributional shift accumulation in normalization layers / tradeoff between scale and capability preservation / degradation of generation quality due to deviation from representation space.
**The problem awareness that "the effect of additive intervention is confounded with the attribution of large-variance spatial directions" is not present in any of the 4 works.**

**Therefore, the "claim only the motivational difference" of Amendment 3 C1 was confirmed in full text.** This difference is permissible to write.

## D6. Bibliographic Confirmation

The authors of arXiv:2606.06735 are **Georgii Aparin (Huawei Noah's Ark Lab)** and **Tatiana Gaintseva (Queen Mary University of London)**, 2 authors. Confirmed by the team.
