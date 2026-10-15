# Pre-registration Amendment 19: Finalize the accuracy, batching, and family definition for the G1 judgement. The family will not be reduced.

**Target**: Pre-registration body §2 G1, §4 (numerical precision), §7 (family for multiple comparisons)
**Created**: a group member / 2026-09-26
**Status**: **Not a single G1 judgement statistic has been computed**
**Origin**: A cost estimate error was corrected (0.31 hours → 15.19 hours), and four decisions were requested.

---

## S1. The population of candidate axes will **not** be reduced (160 cells)

§2 G1 specifies candidates as "ICA rank20 + PC1–PC10," and Amendment 1 A2 **added** Jacobian directions. **Therefore the registered family is 4 layers × (ICA20 + PC10 + Jacobian10) = 160 cells.**

**We will not reduce to 40 cells (Jacobian directions only) to fit the budget. The reason is decisive.**

**We have already descriptively measured that Jacobian directions lie in the "low-variance, high-sensitivity" quadrant** (containment rate 3.0–4.9%, all 40 directions falling below PC10 variance). **Deciding "only Jacobian directions go to judgement" after that is selecting the family after seeing which candidates look favorable.**

**The rationale for including ICA and PC is stated in §2 G1 itself.**

> **If an "axis" is merely a redescription of a PC, that should show up in the selection result.**

**Given that containment rates came out as ICA 88.7–99.97% vs. Jacobian 3.0–4.9%, subjecting them to the same judgement as the same family produces the strongest evidence.** Reduction would eliminate this comparison.

**Cost (10× batching, both arms): approx. 6.08 hours. With 3.8 hours remaining in budget, it does not fit. The principal investigator will be consulted about additional GPU time. If approval is not obtained, G1 will not be executed.**

**The family will not be reduced and then executed.**

## S2. Numerical precision is **fp16** (to match existing measurements)

§4 stated "**bf16 not used (fp32)**." All existing JS measurements use **fp16** (`pos_ctrl_inplane.py:337`).

**Decision: fp16.** Three reasons.

1. **This does not contradict the registered text.** "bf16 not used" is satisfied
2. **All existing measurements (B0, E1 diagnostics, C1–C4) use fp16.** Switching to fp32 would make **G1 results incomparable with existing results**
3. **This is structurally equivalent to the α issue (Amendment 18 R1).** Comparability between measurements takes priority over the parenthetical specification in the registered text

**The "(fp32)" parenthetical was inaccurate. It is preserved here as a record.**

## S3. Batching is approved, with conditions

**Without batching, it does not fit the budget.** Since a 16.2× speedup was actually measured in G4, 10× is conservative.

**Condition: Before producing a single judgement number, verify equivalence with batch 1 on a subset.** This follows the same reproducibility-assurance form as `g1_pc_overlap`. **Left-aligned padding changes numerical values, so the full run will not be executed without confirming equivalence.**

**If equivalence fails, batching will not be used.** In that case the budget will need to be reconsidered.

## S4. Confirm and finalize the handling of α

- **Judgement uses primary α = 1.0 only**
- The remaining 3 levels (0.5, 2.0, 4.0) are **dose-response description and are not part of the judgement**
- **The family is 4 layers × number of candidate axes. α is not included in the family**

**The S-version family was "4 layers × 4 α = 16," but in the JS version α is not included in the family.** This is because Amendment 1 A1 fixed "primary judgement 1.0." **This difference is recorded here.**

## S5 (important). Decide in advance what can be claimed if G1 passes

**A group member, when recording a prediction, wrote a self-adverse caveat. This is hereby elevated to pre-registration.**

> **G1 selects and tests on the same 144 sentences. The floor draws are not selected. There is a bias toward passing directions, and no one has estimated its magnitude.**

**Fixed statement**:

- **A G1 pass shows that "selection by output sensitivity is not vacuous." Nothing more**
- **We will not write "causal specificity" or "intervention on AI-native concepts manipulates behavior"**
- **The claim rests on G2 (replication in the validation set).** The claim will not be established on G1 alone
- **The fact that selection and testing use the same stimulus set will be stated in the same location as the results**

**Reason for fixing this before the judgement**: If G1 passes, **there will be a temptation to read the pass as "selection worked."** The upper limit is set before that temptation arises.

**It is also recorded that the group member's prediction (G1 85%) is higher than the principal investigator's (45%).** The reason is "the selection criterion and the outcome measure are two views of the same thing, and the PMF floor preserves the variance profile but not the output leverage." **If this reasoning is correct, G1 will pass. And when it passes, the upper limit in S5 will be needed.**

## S6. Confirmation of settled matters (responses to a group member's inquiry)

| Item | Registered text | Decision |
|---|---|---|
| Layers | 5,7,10,12 | **11,16,22,27** (Amendment 11) |
| Stimuli / partition | E1 all 287 / old split | **E1 discovery half 144** / `e1_split_20260926.json` (Amendment 13) |
| PMF draw count | — | **100** (§5) |
| α definition | "mean residual norm ratio" | **per-stimulus norm ratio** (Amendment 18) |
| Arms | addition only | **addition + mirror, 2 arms** (Amendment 1 A1) |
| Precision | "(fp32)" | **fp16** (this amendment S2) |
| Family | 4 layers × 3 axes × 4 α = 48 | **4 layers × number of candidate axes; α not included in family** (this amendment S4) |

**All correct.**

## S7. Record: the structure of the cost estimate error

**The figure of 0.31 hours was for 20 stimuli with zero PMF floor draws counted.** The group member self-recorded that "the figure was stated without specifying what it included."

**And that figure was used as the basis for placing G1 before N5** (Amendment 18 R3). **The ordering decision itself was correct, but the figure used as justification was in error.**

**Rule**: **When a cost estimate is used as the basis for a decision, explicitly state what the figure includes and excludes.** Write the stimulus count, number of controls, arms, α levels, and batch width.
