# Pre-Registration Amendment 2: Identifying a Concept by "How It Distributes Computation" (Integration of G4 and G5)

**Target**: `plan_b_js_prereg_20260926.md` (commit 6f351d5), Amendment 1 (commit 8863f10)
**Created**: 2026-09-26
**Status**: **Before experiment.** Do not execute until pushed to git
**Origin**: Adopted from the second round of divergent proposals. **Prior art not yet confirmed. Inquiry to the team is ongoing. If prior art exists, write it as "application of a known method"**

---

## B0. Rewriting the Central Claim (Most Important)

**Old**: Demonstrate uniqueness with G3 (cannot be spanned by human VAD), and demonstrate applied value with G4 (computation reduction). **Sell the two separately.**

**New**: **What a concept is, is defined by how it distributes computation.**

Reason: G3 remains in negative form (cannot be explained by human axes), and G4 is already established (demonstrated by 5 groups). **Selling the two separately makes the first half weak and the second half not new.**

However, candidates such as "uncertainty state," "attention distribution," "distance to the end," and "saturation of repetition" are, directly, **computational distribution mechanisms** called "difficulty detection," "concentration," "budget awareness," and "loop suppression."
**Naming and efficiency are two sides of the same thing.**

**Therefore the claim becomes**: An internal state exists that cannot be named in human emotion vocabulary, and **it controls the distribution of computational resources**.
Intervening on this state produces a combination of efficiency and accuracy that cannot be obtained by intervening on human VAD directions.

**This rewriting does not change the gates and judgement criteria of G1–G4.** It is a change in what is written as the claim.

---

## B1. Concretizing the Procedure for G5 (Description)

Without this amendment, G5 was vague, consisting only of "clustering tokens." The following replaces it.

**B1-a. Linearly decomposing Δ by vocabulary features (no manual annotation)**
Attach feature columns unrelated to human emotion to the full vocabulary: POS, function/content word, word length, log-rank of corpus frequency, tense marker, person, negation, hedge, number/symbol, script type (other languages/code), whether already present in context.
Apply Ridge regression to Δ (log-probability change in the vocabulary dimension) on these, and **use the signed combination of the top contributing features as the axis description**.
**Perform the same regression for human VAD directions and report the distance of the coefficient profiles.** This becomes the affirmative form of "what is different."

**B1-b. Counting the effective rank of the residual after removing human axis components**
Form the Δ of many contexts into a matrix, project out the components explained by human VAD directions, and examine the singular value spectrum of the residual.
**Report the effective rank k as "the number of independent concepts outside human axes."**
State a **count**, not names. Even if naming fails, it can be written as a structural discovery.

**B1-c. Searching for equivalent input transformations**
For candidate prompt transformations (context length, noise insertion, speaker attributes, repetition, ambiguization, instruction strength, output format, language switch, length instruction, etc., 30 types), measure the cosine between the Δ_prompt produced by each transformation and the Δ of the intervention.
**The nearest input operation becomes the "name that does not pass through emotion words" for that concept.** Verify the validity of this procedure with the human valence direction (it should agree with adding emotion words).

**B1-d. Taking the common core across models**
Follow the same procedure for multiple independently trained models and evaluate the intersection of the top Δ tokens using a hypergeometric test.
**If the intersection exceeds chance and the overlap with the human VAD Δ is small, then a model-independent structure that cannot be reduced to human axes exists.**

**All of these are exploratory.** Hypotheses formed here are tested on independent data in a separate pre-registration.

---

## B2. Enumerating Candidate States in Advance and Assigning a Correlation Test to Each

Rather than searching vaguely for "concepts not in humans," **list candidates in advance and eliminate them**. Each candidate is tested by the correlation between pre-intervention axis activation and observed quantities (no intervention needed; forward only; cheap).

| Candidate | Operational definition | Test |
|---|---|---|
| Uncertainty state | Pre-encodes the spread of the next-token distribution | Axis activation × next-token entropy at that position |
| Attention distribution | Concentration and reach distance of attention | Attention entropy and mean distance before and after intervention |
| Sequence predictability | Whether the context currently being read is predictable | Axis activation × actual surprisal measured by a separate model |
| Distance to the end | Remaining length until EOS | Axis activation × actual remaining length on completed generation sequences |
| Modeling the other | Reading user attributes | Linear probe on prompt sets with varied attributes |
| Saturation of repetition | Re-occurrence probability of already-appearing n-grams | Repetition rate before and after intervention |
| Self-reference | Meta-utterance mode | Δ of self-referential vocabulary |

**Fill in the same table for human VAD directions.** Human emotion has no counterpart to "how many words until the end."
**If a correlation appears for the axis but not for the human direction, that is the affirmative answer.**

---

## B3. Changing the Comparison Design for G4 from "Reduction Amount" to "Qualitative Difference"

Exceeding the reduction rate of the existing 5 methods is difficult. **Change to a design that can win without exceeding it.**

**B3-a (Most Important): Contrast with human VAD directions**
**Attempt the same efficiency improvement with human valence/arousal directions and show that accuracy drops.**
Human emotion distorts cognition, so it is expected that raising arousal increases speed but causes errors.
**If Axis X does not drop, the form of the claim becomes "no side effects precisely because it is outside the human framework."**
This is not a competition against the existing 5 methods, but **the only experiment that directly connects our claim (outside the human framework) with efficiency causally.**

**B3-b: Orthogonality and additivity with existing brevity directions**
Reproduce the "brevity" direction used by existing methods in our environment and measure the cosine with Axis X.
**If the reduction rate is additive when both are intervened simultaneously, that is direct evidence that different axes are being reduced.**
Furthermore, classify the deleted content by function using rules (apologies, hedges, repetitions, intermediate calculations, verification, paraphrase) and **show that even at the same reduction rate, the content is different.**

**B3-c: Distribution rather than uniform reduction**
If the pre-intervention activation of Axis X predicts problem difficulty, **change the intervention strength according to the activation.** Total tokens decrease, and accuracy on hard problems does not drop.
Existing methods are uniform shortening at fixed strength, so this is a qualitatively different claim.

**B3-d: Adding one more way to measure computation**
The primary metric is "number of tokens to reach the same accuracy" (as in the original pre-registration).
**As a secondary metric, add "total tokens per correct answer"** (including those spent on incorrect answers and retries).
If intervention reduces incorrect answers, this metric improves even if the mean length is the same. **Do not replace the primary metric; report them together.**

---

## B4. Preserving Proposals That Were Not Adopted

Of the 80 divergent proposals in the second round, only the above were adopted. All proposals are saved in `00_研究計画/発散_概念の名指しと計算量削減_80案_20260926.md`.
**Refer to them as next steps if G1 fails and if no difference appears between human directions and others in B3-a.**

In particular, the following are recorded as strong next steps.
- The family measuring by attention readout volume (KV reference volume) and speculative decoding acceptance rate (leaving the token-count arena)
- The family making the intervention cost zero by self-distilling outputs under intervention
- The degree to which the answer can be read from intermediate layers (reduction in layer count)

---

## Execution Order

**The review response for Paper 1 is the top priority.** This amendment is executed after that.
Of this amendment, **the correlation tests of B2 and B1-a and B1-b can be run on existing data without intervention, so they may proceed first.**
