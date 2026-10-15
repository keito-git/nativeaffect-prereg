# Pre-registration Amendment 87: R-act Failed the Validity Check. It Is Not Used. The Precondition for the Independent Readout Is Moved to the Cross Cell of Readout B

**Created**: 2026-10-08
**Target**: Behavioral verb readout R-act registered in amendment 85
**Judgement**: **R-act fails check 2 of CD3. Not used. The correspondence table is not rewritten.**
**Activation condition**: The readout B judgement must not be performed until this file has been committed and pushed.

---

## CF1. Check Results (5 Models Executed; All Failed)

Amendment 85 CD3 imposed 3 checks. Check 1 (discriminability) and check 3 (non-duplication of vocabulary) passed for all models. **Check 2 (top-1 match rate ≥ majority of 13 categories) failed for all models.**

| Model | Top-1 match | Judgement |
|---|---|---|
| Llama-3.2-1B-Instruct | 6/13 | Failed |
| OLMo-2-1124-7B-Instruct | 6/13 | Failed |
| Llama-3.1-8B-Instruct | 6/13 | Failed |
| gemma-2-9b-it | 4/13 | Failed |
| gemma-2-2b-it | 5/13 | Failed |

The requirement was "majority," i.e., 7/13 or more. **The maximum was 6/13, falling 1 short.** The remaining 4 models were not measured and the check was stopped (since R-act will not be used per the specification, GPU should not be expended).

## CF2. Where It Broke Down

Breakdown by category (number of matches across 5 models, and median rank of the self-verb among 13 verbs).

| Category | Match | Self-verb rank | Verb most often at top-1 |
|---|---|---|---|
| fear | 5/5 | 1/13 | flee (5/5) |
| joy | 5/5 | 1/13 | celebrate (5/5) |
| sadness | 5/5 | 1/13 | cry (5/5) |
| anger | 4/5 | 1/13 | fight (4/5) |
| guilt | 3/5 | 1/13 | confess (3/5) |
| no-emotion | 3/5 | 1/13 | continue (3/5) |
| trust | 1/5 | 4/13 | **celebrate (3/5)** |
| disgust | 1/5 | 7/13 | spit (1/5) |
| **pride** | **0/5** | 3/13 | **celebrate (5/5)** |
| **relief** | **0/5** | 2/13 | **celebrate (5/5)** |
| **surprise** | **0/5** | 9/13 | **celebrate (4/5)** |
| **shame** | **0/5** | 6/13 | confess (3/5) |
| **boredom** | **0/5** | 8/13 | flee (2/5) |

**Number of times each verb was at top-1**: celebrate 24, flee 13, confess 7, cry 7, fight 6.

**`celebrate` dominates top-1 in 24 out of 13 slots.** Positive emotions (joy, pride, relief, trust) are absorbed into the same verb and not discriminated. The verb vocabulary **carries only positive/negative polarity and does not have the resolution for categories.**

**This is a failure of design, not a property of the model.** The frame "The person's immediate impulse is to" strongly constrains the polarity of the behavior, leaving no category-specific residue.

## CF3. The Correspondence Table Is Not Rewritten

Amendment 85 CD7 stated "the correspondence table is not rewritten after seeing results." **This is honored.** There is a prospect that replacing `celebrate` with a different word for pride/relief/trust would pass the check, but **that would be a change after seeing the results and is not performed.**

R-act is recorded as "**an attempt to design an independent readout that breaks vocabulary circularity, but the correspondence table did not have category resolution and it failed the validity check.**" This is stated explicitly as a tested but failed control in the limitations section and appendix of the paper.

## CF4. The Precondition for the Independent Readout Is Moved

Amendment 85 had made R-act the precondition for level-3 claims. Since R-act cannot be used, **the precondition is moved to the cross cell of readout B from amendment 86. Fixed before seeing results.**

### New Precondition (Precondition IND)

In readout B (appraisal adjectives, frame `The event was`, 12 adjectives), **the emotion category axis exceeds the matched family best** ($p_G < 0.01$ in a majority of models).

**Rationale**: The emotion category axis is estimated from 13 emotion category labels. The vocabulary of readout B (sudden, pleasant, urgent, ...) **never appears in those estimation targets.** Therefore if the emotion axis moves readout B, it cannot be explained by "only raising the logit of `anger`."

**If precondition IND is not satisfied, level-3 claims are not made.** The phenomenon is reported as being limited to the emotion word readout.

### The Judgement Table of Amendment 86 CE3 Remains Valid

The cross cell (emotion axis → B) was auxiliary in amendment 86, but **by this amendment it is elevated to the precondition.** The judgement for the self-consistent cell (appraisal axis → B) is unchanged from amendment 86 CE3.

## CF5. Also Recorded: An Independent Emotion Readout Has Not Been Achieved

Readout B is **appraisal** vocabulary and **is not an independent emotion category readout.** A readout that measures emotion categories decomposed into 13 classes without using emotion vocabulary has not been achieved in the present study.

Candidates (not implemented in this amendment; recorded as future directions):

- Free generation after intervention is evaluated by a classifier or NLI trained on a separate corpus (consistent with the policy of not using manual annotations)
- The change in log-probability for a set of descriptive sentences containing no emotion words

**"Replicated with an independent readout" can be claimed only for the cross cell of readout B; the present study has not achieved independent measurement of emotion categories.** This is stated explicitly as a limitation.

## CF6. Commitments

- The R-act failure is reported as-is, and it is left in the paper as a tested but failed control
- The correspondence table is not rewritten. A retry with different words is not performed
- Precondition IND is placed in the cross cell of readout B; level 3 is not claimed if it is not satisfied
- The fact that an independent emotion category readout has not been achieved is written in limitations
- The check for the 4 models whose measurement was halted is recorded as not executed
