# Pre-registration Amendment 42: NLI agreement rate will not be used as a pass condition for stimuli. Both E4 and E5 will be analyzed.

**Created**: 2026-10-04
**Target**: Validity check of stimulus set E5 (stimulus specification of Amendment 38, promise of dual reporting of E4/E5 in Amendment 40)
**Judgement**: **NLI agreement rate is reported as a descriptor and is not used as a pass condition.**

---

## AQ1. What was measured

E5 (no emotion words, 28 skeletons, 169 sentences) and E4 (direct emotion word writing, 80 sentences) were evaluated as argmax agreement rate across all 40 categories using an independent NLI model. Four hypothesis templates were tried.

| Template | E4 | E5 |
|---|---|---|
| A `This situation involves someone feeling {}.` | **75%** | **11%** |
| D `This is about {}.` | 61% | 9% |
| C `She feels {}.` | 52% | 5% |
| B `The person in this situation is {}.` | 24% | 7% |

Chance level 2.5% (40 categories). Model: bart-large-mnli.
In the initial 3-model comparison (deberta / bart / roberta), within-skeleton judgements agreed at 27–33%.

## AQ2. Result of disaggregation

Three causes for the low agreement rate were hypothesized; two were ruled out.

1. **Not a procedural problem.** E4 achieves 75% with template A. Since sentences containing emotion words are correctly matched, the implementation of the test is functioning.
2. **Not a template problem.** Four templates were tried and A was the best in all conditions. Even for the same E4, results varied by a factor of 3 (24%–75%) across templates, so **had we tried only one template and concluded that "the stimuli are too weak," that conclusion would have been wrong**.
3. **What remains is the evocative power of the stimuli.** E5 reaches only 11% (4.4 times chance) even with the best template.

## AQ3. Decision: will not be used as a pass condition

**The NLI agreement rate will not be used as a pass condition for E5.** The reason is circularity.

NLI models are trained on human emotion categories. Using this as a gate for stimuli means **adopting only stimuli that are readable within the human framework**. The main hypothesis of this research series (Amendment 41, AAPH) is that "human emotion categories are merely a projection of AI-native latent axes," and making readability in the human framework a requirement for stimuli **contradicts the direction of the hypothesis**.

Furthermore, trying to increase the NLI agreement rate of E5 would mean making the situational descriptions more explicit, moving closer to what the red-team review pointed out as "merely measuring scenario-level statistics." **Only the position within the trade-off changes; the problem does not disappear.**

## AQ4. What will be done instead

- **The NLI agreement rate will be reported as a descriptor in the main text.** E4 75% / E5 11% (best template, chance 2.5%) will be written as-is. We will not conceal this.
- **All analyses will be performed on both E4 and E5, and both will be reported** (as promised in Amendment 40 AO6).
- **The essential question is "does the structure visible in E4 also appear in E5?"** If it does, the structure does not depend on surface emotion words. If it does not, what was visible in E4 was a property of emotion words. **Either outcome can be reported.**

## AQ5. What will be stated as a limitation

**There is no independent means of guaranteeing the validity of the stimuli.** Human annotation is not available in this research series, and NLI relies on the human framework. Therefore this study cannot prove that "E5 evokes the intended emotions."

What can be said is only the following:

> E5 is a stimulus set that contains no emotion words and controls topics across categories.
> The readout agreement rate by the NLI model is 11% for E5 against 75% for E4,
> and **the readability within the human emotion framework is substantially inferior.**
> This study performs the same analysis on both sets and reports the agreement of results.

This limitation will be stated explicitly in the Limitations section of the paper.

## AQ6. Promises

- We will not report only whichever of E4 and E5 gives better results.
- We will not retroactively change the NLI agreement rate to a pass condition.
- If E5 is rewritten to increase the agreement rate, **the fact of the rewrite and its reason will be recorded**, and the results of the old version will also be reported alongside.
