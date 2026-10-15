# Pre-Registration Amendment 71: Confirmation of Two Prior Work Items, Correction of Venue, and Limiting the Positioning of Novelty

**Created**: 2026-10-06
**Occasion**: External advice (2026-10-06)
**Status**: Record of priority and limitation of novelty claims. Existing judgements are not changed.

---

## BT1. Correction of Venue

In Amendments 48, 52, 64, 69, etc., the audit target was recorded as "Tak et al. 2025, **ACL 2025**." **The correct venue is Findings of ACL 2025** (ACL Anthology `2025.findings-acl.679`). This is not the main conference. **This notation is used hereafter, and the existing mistaken records are corrected by this amendment.**

The error occurred because the main conference was inferred from the description on the arXiv abstract page. The practice of **confirming the publication category by the Anthology identifier** is adopted going forward.

## BT2. Prior Work Confirmed

### Xeno-Interpretability (arXiv:2609.20408, 2026)

Authors: F. Pierucci, M. Bracale Syrnikov, M. Prandi, M. Galisai, F. Giarrusso, P. Bisconti. Submitted 17 September 2026, arXiv (cs.CL). **Full names of all authors have not been confirmed**; this will be resolved before citation.

Claim: There may exist internal structures in LLMs that cannot be sufficiently described by human concepts. Proposes to **separate identification from semantic interpretation**, arguing that as long as something can be "reproducibly localized, geometrically characterized, and causally manipulated," it does not need to be expressible in human terms. **The type is a position paper and presents no experiments.**

### Characterizing Model-Native Skills (arXiv:2604.17614, COLM 2026)

Authors: Feiyang Kang, Mahavir Dabas, Myeongseob Ko, Ruoxi Jia.

Extracts orthogonal bases from series-level activations and **selects useful directions via lightweight surrogate interventions**. Improves Pass@1 on MATH by up to 20% and AMC by up to 41% with data selection, **surpassing selection based on skills characterized by humans**. In inference-time steering, improves Pass@8 on MATH by up to 4.8%, an intervention that cannot be performed with human-characterized skills. Safety alignment also exhibited more sample-efficient coverage with model-native skills.

## BT3. Scope That Has Been Preempted (Not Claimed as Contributions of This Study)

1. **The very idea of "identifying AI-native representations without depending on human concepts"** — Xeno-Interpretability
2. **The form of the claim "model-native axes outperform human-defined axes"** — demonstrated by Kang et al. for reasoning and safety
3. The methodological stance of separating identification from semantic interpretation — same as above

**The framework constructed in Amendments 46, 47, 54, and 70 overlaps with these.** **"The idea of AI-native concepts" is not written as a contribution of this study.**

## BT4. Remaining Novelty (Limited to 3 Points)

| # | Content | Basis |
|---|---|---|
| 1 | **Targeting emotion** | The domain where the assumption of human ontology is strongest. Verifying that human axes are not privileged as computational units in this domain. Kang et al.'s target is reasoning and safety, not emotion |
| 2 | **The source of discovery is intervention responses** | Kang et al. take orthogonal bases from activations and use surrogate interventions for selection. This study decomposes the intervention response matrix itself |
| 3 | **Variance-matched floor and output perturbation equalization** | Neither prior work has these controls. These are tools established in the methodological paper of this research series |

**Novelty is not claimed beyond these 3 points.** The general claim "there exist representations that cannot be described by human concepts" is attributed to Xeno-Interpretability.

## BT5. Related Work on Emotional Representations (Pending Confirmation)

The following, cited by external advice, **are unconfirmed at the time of this amendment**. **They are not cited and not used as grounds for claims until confirmed.**

- Emotions Where Art Thou (ICLR 2026): Reported to show a low-dimensional emotion manifold, cross-domain consistency, and steerability
- A Unified View on Emotion Representation in Large Language Models (EACL 2026, `2026.eacl-long.165`): Reported to show a common emotion representation exchangeable across datasets. Also mentioned in a literature check, but the main text is unconfirmed

**If these report "a low-dimensional universal emotion subspace exists," the problem formulation of this study directly confronts them.** Since this directly concerns the framing of the introduction, **obtaining and confirming the main text is included as the next task.**

## BT6. Commitments

- Tak et al. is expressed as Findings of ACL 2025, and the fact that the existing mistaken records were corrected is retained in the paper
- The 3 items in BT3 are not claimed as contributions of this study
- Xeno-Interpretability and Kang et al. are explicitly cited in the introduction and related work, with the difference limited to the 3 points in BT4
- The 2 papers in BT5 are not cited until their main texts are obtained and confirmed
- The full names of all authors of Xeno-Interpretability are confirmed before citation
