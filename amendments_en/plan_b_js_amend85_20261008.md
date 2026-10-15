# Pre-registration Amendment 85: Specifications of Independent Readout R-act. Breaking the Vocabulary Circularity

**Created**: 2026-10-08
**Occasion**: Critique 4 from external review (2026-10-07, 3rd round). Specifications committed to be fixed "in amendment 84" in amendment 83 CB10.
**Role**: **R-act is made a precondition for level-3 claims.** If the emotion axis does not exceed the floor under R-act, the claim is not made.
**Activation condition**: R-act judgements must not be performed until this file has been committed and pushed. **Has never been executed.**

---

## CD1. The Objection to Be Answered

> The emotion category directions are constructed from emotion category labels, and evaluation is also conducted using the next-token probability of emotion category words. Winning because the same ontology is used on both sides — is that not the explanation?

This is currently the strongest alternative explanation. The synonym-set readout (R-syn) from amendment 82 does not answer it. It is vocabulary from the same 13 categories.

### The Core of the Objection Is the Vocabulary

Emotion directions are estimated to separate 13 category labels in the activation space. The readout uses **the token probability of the word itself.** Therefore a direction that "only raises the logit of the token `anger`" can win without any accompanying claim about representations.

**What must be broken is the vocabulary match.** No emotion word is included in the readout at all.

## CD2. Specifications of R-act (Behavioral Tendency Readout)

### Framework

The prompt frame is changed, and the next-token probability of **13 verbs that contain no emotion word** is used as the readout.

```
Event: {text}

The person's immediate impulse is to
```

**No emotion word appears in this frame.** It is a different pathway from the current frame (`The emotion is`).

### Correspondence table (fixed in this amendment; not changed after seeing results)

| Category | Verb | Category | Verb |
|---|---|---|---|
| anger | fight | pride | boast |
| boredom | yawn | relief | relax |
| disgust | spit | sadness | cry |
| fear | flee | shame | blush |
| guilt | confess | surprise | gasp |
| joy | celebrate | trust | rely |
| no-emotion | continue | | |

**None of the 13 verbs is an emotion category name or a synonym of one.**

### Computation of the Readout

Identical to the current version. The difference vector in the next-token probability before and after intervention is taken for the verb tokens, centered, unit-norm normalized, and made signed. **Statistics are not changed at all.**

Token IDs are obtained using the corrected rule from amendment 84 (the first token with characters remaining when decoded), and **an exception is raised if IDs are duplicated across classes.**

### Calibration

The intervention strength is matched by the same full-vocabulary JSD as the current version. $J^\ast = 0.05$. **Because calibration does not depend on the readout, the same $\alpha$ applies as for R-single and R-syn.** However, because the prompt frame differs, $\alpha$ is recalibrated per frame.

## CD3. Validity Checks (Performed Before the Judgement; R-act Is Not Used If Not Satisfied)

To avoid repeating the failure of readout B (where AUC 0.55–0.60 rendered the test uninformative), **the following are measured before the judgement, and R-act is not used if they are not satisfied.**

1. **Discriminability**: In the unintervened state, the next-token probabilities of 13 verbs are not degenerate (at least 10 distinct values, standard deviation > 0)
2. **Validity of correspondence**: For stimuli in each category of crowd-enVENT, the proportion for which the corresponding verb has the highest probability among the 13 verbs (top-1 match rate) is measured. **Requiring top-1 match in a majority of the 13 categories**
3. **Non-duplication of vocabulary**: Token IDs of the 13 verbs are mutually distinct

**If 2 is not satisfied**: The correspondence table is not functioning. **In that case, R-act is recorded as "the correspondence table does not function" and another independent readout is designed in amendment 86. The correspondence table is not rewritten to improve the results.**

## CD4. Judgement (Fixed before seeing results)

| R-single′ and R-syn | R-act | What can be written |
|---|---|---|
| Emotion axis exceeds the matched family best in a majority of models | **Same** | **Level 3 is claimed. Cannot be explained by vocabulary circularity** |
| Exceeds | Does not exceed | **Level 3 is not claimed.** Reported as a phenomenon limited to the emotion word readout |
| Does not exceed | Exceeds | Reported as-is. Neither conclusion is claimed |
| Does not exceed | Does not exceed | The claims of amendments 80 and 81 are withdrawn |

**The threshold for "majority of models" is the same as in amendments 81 and 83. It is not moved.**

## CD5. Scope of Execution

**All 9 models** (including Phi-3-medium; it is not degenerate per amendment 84 CC1). Families are emotion and appraisal_raw. Floors are F5 (10 directions per target) and F4 (5 directions). Raw measurements are saved to `raw_<tag>_act.npz`.

## CD6. What This Readout Does Not Answer

R-act breaks **vocabulary circularity** but not **the catalog of categories itself**, which is human-derived 13 categories. "Whether this 13-way categorization is privileged" is a different question and is not answered by R-act. **This limitation is stated explicitly in this amendment, and the vocabulary circularity specifically is the objection that is addressed.**

Furthermore, **the correspondence table (emotion → verb) was constructed by me and is not an independently validated mapping.** The top-1 match rate in CD3 is a check of its validity, but does not guarantee the mapping's correctness. **This is written as a limitation in the main text.**

## CD7. Commitments

- The correspondence table is not rewritten after seeing results
- The 3 checks in CD3 are performed before the judgement and the results are reported
- If the top-1 match rate fails to reach a majority, R-act is not used and the fact is recorded
- If the emotion axis does not exceed the floor under R-act, level 3 is not claimed
- The fact that the correspondence table was constructed by me is stated as a limitation
- Raw measurements are saved (amendment 84 CC3)
