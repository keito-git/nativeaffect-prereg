# Pre-Registration Amendment 100: Re-Extracted Activations Reproduced the Previously Reported Values for Codebook 1 — Relaxing One Point of the CR5 Commitment

**Created**: 2026-10-14
**Target**: Amendments 99 CR1 and CR5 (provision for the lack of guarantee that re-extraction is identical to the original)
**Type**: **Post-hoc observation and an explicit relaxation of a commitment.** The judgement of codebooks 3 and 4 is not made here.
**Trigger condition**: Do not write this observation in the manuscript until this file is committed and pushed.

---

## CS1. What Happened

Stage 0 of Amendment 99 (re-measurement of codebook 1; population 5 models × 2 readouts; 10 null vectors per target) was completed at 2026-10-14 02:27 UTC. The values are as follows.

| Model | Affect-word readout | Code readout |
|---|---|---|
| Llama-3.1-8B | 10/13 (+3.19) | 2/13 (+0.62) |
| Gemma-2-9B | 6/13 (+1.53) | 4/13 (+0.59) |
| Mistral-Nemo-12B | 11/13 (+2.82) | 6/13 (+1.55) |
| OLMo-2-13B | 9/13 (+2.46) | 3/13 (+1.30) |
| Ministral-8B | 9/13 (+2.74) | 2/13 (+0.02) |

**All 10 cells' counts and excess SDs matched the previously reported values to 2 decimal places.**
That is, the re-extraction of the lost activation cache had, to the extent of the measurement outputs, restored the original.

## CS2. Why This Is a Problem

Amendments 99 CR1 and CR5 committed to the following.

> Do not replace the numbers in previously reported tables with values obtained from re-extracted activations. Additional experiments are limited to comparisons self-contained within them.

This commitment is a **protective commitment**. Its purpose was to preemptively block the room to mix old and new values and interpret them favorably, since identity was not guaranteed. The match in CS1 is itself a comparison of the type that commitment addresses (comparing new and old).

## CS3. Decision (a decision by the principal investigator, 2026-10-14)

**Relax one point of the commitment only. Replacement is still not performed.**

- **Do not replace the numbers in previously reported tables.** Tables II–V in the body text remain as the original measurements (CR5 maintained).
- **The judgement of codebooks 3 and 4 is performed as an internal comparison on the same re-extracted activations** (CR1 maintained).
- **The match in CS1 may be written in the body text as a post-hoc confirmation that was not pre-registered.**
  When writing it, the following 3 points must be written together: (a) that it is post-hoc, (b) that it was not pre-registered, and (c) that it is not used as evidence for any claim in this paper.

**Reason for relaxation**: The only basis for keeping it private is "a procedure I imposed on myself"; the content to be written is factual; and for readers (reviewers) it is information that informs their assessment of reproducibility. If the post-hoc nature is stated explicitly, it does not constitute misleading. **Suppressing information whose benefit from suppression lies only with the authors does not serve the purpose of pre-registration (eliminating favorable selection).**

## CS4. Confirmation That the Match Is Not Coincidental

The match occurred in all 10 cells, for both counts (integers) and excess SDs (2 decimal places).
**This is not a coincidental match; it may be treated as an identical computation on identical inputs.**
However, this amendment does **not** treat this match as proof of identity of the extraction pipeline.
Only the fact that the outputs matched is recorded.

## CS5. What Is Not Done in This Amendment

- Judgement of codebooks 3 and 4 (validity check not yet executed; **perform the check before making the judgement**)
- Judgement of the budget sweep (stages 2 and 3 not yet complete)
- Replacement of previously reported tables (not done, as per CR5)

## CS6. Commitments

- When writing CS1 in the body text, do not omit the 3 points of CS3 (post-hoc, not pre-registered, not used as evidence for any claim)
- Do not move the validity check threshold for codebooks 3 and 4 (at least 7/13 with AUC>0.5, and median 0.65 or above) after seeing the results
- Models that fail the validity check are removed from the judgement population, and **their numbers and reasons are reported without deletion**
