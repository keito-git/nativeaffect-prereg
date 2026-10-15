# Pre-Registration Amendment 3: Reflecting the Results of a Priority Survey Before the Experiment and Downgrading Claims

**Target**: `plan_b_js_prereg_20260926.md` (6f351d5), Amendment 1 (8863f10), Amendment 2 (bb81cb2)
**Created**: 2026-09-26
**Status**: **Before experiment.** Before push
**Source**: `01_調査/採択手法の先行性調査_20260926.md` (a literature check). See the same file for the legend of confirmation status

**The purpose of this amendment is to finalize the upper limit of claims before seeing the results.**
The methods already found to exist are explicitly downgraded here so that there is no room to write "it was novel" after the experiment.

---

## C1. Norm-Preserving Intervention Already Exists. **Do Not Write It as a Proposal**

Regarding the reflection intervention placed as a primary arm in Amendment 1, it has been confirmed that **isometric/rotation-type interventions exist in multiple prior works**. Primary confirmation (◎) by the team from the arXiv abstract pages.

- Angular Steering (arXiv:2510.26243) — rotation within a 2D subspace
- Selective Steering (arXiv:2601.19375) — criticizes the above for actually breaking norm preservation and proposes strict preservation rotation
- Stiefel-Constrained Rotation (arXiv:2608.30986) — Riemannian optimization
- GeoSteer (arXiv:2609.10658) — geodesic optimization

**Decision**:
- **Do not write "we proposed norm-preserving intervention" or "we introduced isometric intervention."** Write it as application of a known method
- **Our difference is only in motivation.** Namely, the motivation that "we use isometric transformation to constructively remove variance confounding because the effect of additive intervention is proportional to the variance along the direction" was not found in any of the works confirmed by the team (the motivation in existing work is sensitivity to layer-norm fluctuation and prevention of distributional shift). **Claim only this difference**
- **Cite all 4 of the above works in Related Work.** Before citing, confirm the motivation in full text and solidify the basis for writing "the motivation is different." **If this cannot be confirmed, do not write "to our knowledge"**

## C2. Jacobian Singular Directions Have Non-Peer-Reviewed Prior Work; Do Not Claim Novelty

Regarding the Jacobian singular directions added as candidates in Amendment 1, **no peer-reviewed prior work was found, but a non-peer-reviewed public post preceded ours.**

- Power Steering (Omar Ayyub, AlignmentForum, 2026-03-13) — uses the right singular vectors of the inter-layer Jacobian. The motivation is "directions in which the network is already sensitive," **which matches ours even on the point that it is independent of data variance**

**Decision**:
- **Cite it.** Treat it as prior work while explicitly noting that it has not been peer-reviewed. **Since it is public, we do not claim novelty while ignoring the prior**
- **Do not write "we proposed using Jacobian directions for steering."** Our use is "placing candidates in the 2D (variance, sensitivity) space to judge whether ICA axes are a byproduct of either," and the claim is **limited to use as a judgment tool**
- Since no arXiv version exists, the citation format must explicitly state the submission URL, author name, and date

## C3. Variance Calibration Control Is Maintained as "Demonstrating Necessity"

Other than Sun et al. (arXiv:2604.03147)'s in-plane control, **no paper with the explicit motivation "a variance-matched control is necessary because the effect of additive intervention is proportional to variance" was found** (within the team's survey scope).

**Decision**: **Maintain the wording "demonstrated that already-used controls are necessary."** Do not write "we proposed a new control." This decision is treated the same as Condition 3 of Paper A (methodology).

## C4. The Contrast with Human Axes for Side Effects Remains at "Independent Possibility" Pending Full-Text Confirmation

Amendment 2's B3-a (attempt the same efficiency improvement with human valence/arousal directions and show that accuracy drops) is **the most important experiment that causally connects our claim with efficiency**.

- E-STEER (arXiv:2604.00005) shows that emotional steering via activation intervention affects reasoning and safety. **However, the contrast "accuracy drops for human emotion axes but not for non-human axes" cannot be confirmed at the abstract level**
- Psychological Steering (arXiv:2510.04484) reports side effects such as joy → decreased factual detection, but **there is no contrast between human and non-human axes** (abstract confirmed)

**Decision**:
- **Complete full-text confirmation of E-STEER before the experiment.** The team has been instructed
- If the full text contains a contrast experiment, **write B3-a as "reproduction of prior work + extension to non-human axes."** Do not write it as independent
- Even if it does not, attach **"to our knowledge."** **Both papers must be cited**
- **In either case, B3-a is executed.** Only the positioning changes

## C5. Residual Effective Rank and Equivalent-Prompt Naming Remain Independent Possibilities

- The method of **counting the effective rank of the residual and reporting it as "the number of independent concepts outside human axes"** was not found within the survey scope
- The method of **naming by the form "this intervention is equivalent to adding ○○ to the prompt"** was also not found. However, research in the reverse direction (reinterpreting prompts as activation interventions) exists (arXiv:2605.03907, arXiv:2606.03093). **Both are cited, and the reversal of direction is explicitly stated**

**Decision**: Write with "to our knowledge." **Cite the above 2 works in Related Work and explicitly state that the direction is reversed.**

## C6. Difficulty-Adaptive Distribution Is Independent (Formulation Is Different)

- ATLAS (arXiv:2601.03093)'s adaptation criterion is **reasoning quality** (evaluation by a lightweight verifier)
- AdaRAS (arXiv:2601.19847)'s adaptation criterion is **correctness** (intervening only on incorrect reasoning)

**Neither is formulated as "distribution of computational resources based on difficulty detection."**

**Decision**: Write it as independent. However, **cite both papers and explicitly state that the adaptation criteria differ.** Do not write "we were the first to perform adaptive steering." **Adaptive steering already exists.**

---

## C7. What Was Finalized Before the Experiment (Summary)

| Adopted proposal | Treatment of novelty |
|---|---|
| Isometric (reflection) intervention | **Already exists.** Claim only the difference in motivation |
| Jacobian singular directions | **Non-peer-reviewed prior work exists.** Limited to use as a judgment tool |
| Variance calibration control | "Demonstration of necessity." Do not write it as a proposal |
| Side-effect contrast with human axes | Pending full-text confirmation. **Attach "to our knowledge"** |
| Residual effective rank | Independent possibility. "To our knowledge" |
| Equivalent-prompt naming | Independent possibility. Cite 2 works in reverse direction |
| Difficulty-adaptive distribution | Independent. **However, adaptive steering itself already exists** |

**Do not write claims stronger than this table after seeing the results.**

## C8. Unfinished Confirmations (Complete Before the Experiment)

1. Full author names of arXiv:2606.06735 (Angle-Norm Decomposition) — confirm before BibTeX entry
2. **Presence or absence of human-axis vs. non-human-axis contrast in the full text of E-STEER (arXiv:2604.00005)** — affects the final judgement of C4
3. Full-text confirmation of motivation in the 4 works of C1 — basis for writing "the motivation is different"
