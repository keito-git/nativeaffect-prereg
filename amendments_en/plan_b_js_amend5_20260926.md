# Pre-Registration Amendment 5: Finalizing G4 Benchmarks as GSM8K and MATH (AIME Will Not Be Used)

**Target**: `plan_b_js_prereg_20260926.md` §2 G4, Amendment 2 B3, Amendment 4 D2
**Created**: 2026-09-26
**Status**: **Before experiment.** Before push
**Source**: `01_調査/ベンチマークのライセンス確認_20260926.md` (team, primary confirmation)

---

## E1. Finalizing the Benchmarks to 2

**The original pre-registration only said "one primary benchmark." This is finalized here before running.**

| Dataset | License | Basis | Decision |
|---|---|---|---|
| **GSM8K** (`openai/gsm8k`) | MIT (Copyright (c) 2021 OpenAI) | Double confirmation: LICENSE document of GitHub `openai/grade-school-math` + HF card | **Use as primary benchmark** |
| **MATH** (`hendrycks/competition_math`) | MIT (Copyright (c) Dan Hendrycks, 2021) | Double confirmation: LICENSE document of GitHub `hendrycks/math` + HF metadata | **Use as secondary benchmark** |
| **AIME** | **Unknown (gray area)** | The copyright of the problems belongs to the Mathematical Association of America. The Apache 2.0 etc. displayed on each dataset on HF **is attached by the dataset creator and is not a display by a party with authority to license the reuse of MAA's copyrighted works** | **Will not be used** |

## E2. Decision Not to Use AIME (a decision by the group)

**There are 2 reasons.**

1. **There is no scientific return for the legal risk.** What G4 requires is "a curve where accuracy increases as the token budget increases," and **with GSM8K (elementary arithmetic, 1,319 problems) and MATH (competition mathematics, 12,500 problems, 5 difficulty levels), there is sufficient width of difficulty.** Adding AIME does not change the conclusions about the shape of the curve
2. **We assume code disclosure.** Including material whose redistribution permission is unknown means that problems will materialize at the time of disclosure. **It is cheaper not to use it than to realize at the time of submission**

**No prior inquiry to MAA will be made.** The benefit does not justify the waiting time. **If AIME is needed in the future, inquire at that time.**

## E3. Constraints Added to How Claims Are Written

- **When writing "effective on hard problems," the basis is limited to the upper difficulty tier of MATH.** Since AIME was not used, do not write extrapolation to the very top of competition-level
- **State as a limitation**: "Evaluation is limited to GSM8K and MATH. More difficult benchmarks such as AIME were not used because the ownership of the problem copyrights was unconfirmed"
- **Primary benchmark = GSM8K.** The judgement criterion of Amendment 4 D2 (Axis X frontier exceeds all 3 human VAD curves over at least one-third of the token count range) **is judged using GSM8K**. MATH is treated as a **sensitivity analysis**. **Do not shift the primary judgement to MATH afterward**

## E4. Handling of Data

- **GSM8K**: MIT, so bundling is possible. **Bundle the copyright notice and MIT text together**
- **MATH**: MIT, but at 12,500 items it is large, so **only the link and acquisition script are published** (not bundled)
- Acquisition via HuggingFace datasets. **No API key is used**

## E5. Citations (Author names confirmed in full by the team)

- GSM8K: Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, Christopher Hesse, John Schulman (2021), arXiv:2110.14168
- MATH: Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric Tang, Dawn Song, Jacob Steinhardt (2021), arXiv:2103.03874

**Write all authors without `et al.`**

## E6. Preconditions for G4 Execution (Re-stated; Unchanged)

**Confirm in advance that the baseline curve for the chosen model without intervention is not flat.** On GSM8K 500 problems, token budgets at 4 points (64 / 128 / 256 / 512), accuracy increases monotonically, and **the difference between the minimum and maximum budget is 5 or more points**.
**If not satisfied, G4 is unmeasurable for that model**, stop and report. Model changes are decided by the group.
