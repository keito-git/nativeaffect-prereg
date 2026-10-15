# Pre-Registration Amendment 7: MATH Will Not Be Used. Evaluation Will Use GSM8K Only

**Target**: Changing the decision of Amendment 5 (`b472ce9`) E1
**Created**: 2026-09-26
**Status**: **Before experiment** (MATH measurements have never been executed. Only the GSM8K precondition check is running)
**Source**: `01_調査/ベンチマークのライセンス確認_20260926.md` (team, primary confirmation ◎)

---

## G1. Facts That Have Come to Light

**The MATH dataset has received a DMCA takedown notice.** The team confirmed at first hand from the HuggingFace official takedown notices repository (`huggingface-legal/takedown-notices/blob/main/2025/2025-01-02-AoPS.md`).

- **Notifying party**: Art of Problem Solving (AoPS) Incorporated
- **Notice date**: January 2, 2025
- **Claim**: More than **10,000 of the 12,500 problems** match the original content of AoPS's Alcumus platform with a similarity of 95 or above. **Both the problem text and the solutions** are asserted to be AoPS's copyrighted works
- **Original text**: "The MATH dataset contains both proprietary problems written by our team for usage in our Alcumus learning platform, as well as all of our proprietary solutions entirely written by our team."
- **Target**: `hendrycks/competition_math` **and derivative datasets** (explicitly demanded)
- **Result**: `hendrycks/competition_math` has been deleted. **This is the cause of the `DatasetNotFoundError` encountered by the team**

**Timeline**: DMCA was on January 2, 2025, and the `hendrycks/math` README was updated to point to `qwedsacf` on September 6, 2025 (committed by `hendrycks`). **The README update is after the DMCA, but it does not resolve AoPS's copyright claim.**

**Scope of MIT license**: The MIT attached by Hendrycks applies to **the parts he has rights over (code, etc.)**. **AoPS claims rights over the problem texts and solutions themselves.** The two are compatible. **Therefore, "it says MIT" does not mean that reuse of the content is permitted.**

## G2. Decision: MATH Will Not Be Used

**Evaluation will use GSM8K only.** Neither the `EleutherAI` version nor any copy of MATH including the `qwedsacf` version will be used.

**Reasons**:
1. **The design is valid.** The primary judgement was already finalized as GSM8K in Amendment 5, and MATH was only a sensitivity analysis. **Not a single claim is lost**
2. **We will publish our code and data paths.** Using content that is subject to a valid DMCA notice means that problems will materialize at the time of publication
3. **Consistency with the decision to drop AIME.** AIME was dropped because "the location of rights is unknown." **MATH has an actual takedown notice.** Dropping AIME while using MATH is not consistent

## G3. Alternative for Sensitivity Analysis

**No new datasets will be added.** Instead, **stratify GSM8K internally by difficulty for the sensitivity analysis.**

- Stratification criterion = **the number of calculation steps in the reference answer of each problem** (GSM8K answers explicitly show calculations with `<<...>>`, so they can be counted mechanically)
- **Divide into 3 quantiles by step count, and perform the same measurement as the primary judgement for the top quantile as "hard problems"**
- **This allows asking "is it effective on hard problems?" without bringing in new data**

**Replace the description of Amendment 5 E3**: When writing "effective on hard problems," the basis is limited to **the top step-count quantile of GSM8K**. **Do not mention MATH or AIME (since they were not used).**

**Write in the main text as a limitation**:
> Evaluation is limited to GSM8K. More difficult mathematics benchmarks were not used because the problem texts are subject to third-party rights claims (MATH: valid DMCA notice present) or the location of rights could not be confirmed (AIME). The effect of difficulty is examined by stratification using calculation step count within GSM8K.

## G4. Handling of Already-Acquired Data

**Will not delete.** By lab rules, deletion of data files requires explicit permission from the principal investigator.

- Move both the `EleutherAI` version (in `benchmarks/_unused_license_unclear/`) and the `qwedsacf` version to **`benchmarks/_dmca_do_not_use/`**, naming the directory so that the prohibition on use is clear
- **Place a `README_DO_NOT_USE.txt` in the same directory with the takedown notice URL, notice date, and notifying party**
- **Whether to delete or not is for the principal investigator to decide.** The group will not delete

## G5. Record

**This decision was made before the experiment.** MATH measurements have never been executed.
**Record the background of nearly being satisfied with "it said MIT"**: The team acquired it using `license: mit` on the HF card as the basis, and a re-examination began when the team found `_LICENSE = ""  # TODO: Add the licence for the dataset here if you can find it` in the load script of the `EleutherAI` version, in the course of which the DMCA was discovered.
**License tags are not primary information.** Look at all three: the LICENSE document itself, the rights holder, and third-party rights claims.
