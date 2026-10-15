# Pre-Registration Amendment 13: E1 Had No Discovery/Confirmation Partition. Defining It Before the Judgement

**Target**: Pre-registration main body §3 (partition), §2 G1 (discovery group only), §2 G2 (whether reproduction occurs in confirmation group)
**Created**: 2026-09-26
**Status**: **Jacobian computation for G1 halted in order to write this. Not a single judgement statistic has been computed**
**Origin**: A team member checked the contents of the partition file and reported that **it was defined on E4, not on E1**. The group noticed this issue from that report

---

## M1. A Design Error by the Group

The pre-registration main body §3 stated:

> - **Primary stimuli = E1 (natural sentences, 287 items). Use all items.**
> - Partition: Use the existing discovery/confirmation partition `axis_rebuilt_split_20260925.json` **as-is. Do not re-partition.**

**These two lines are incompatible.** The contents of `axis_rebuilt_split_20260925.json` are as follows (confirmed by the team).

- `stimuli_file: stimuli_e4.json`
- Stratification rule: Stratified by emotion category for E4 items 0–39
- discovery n=20 / confirmation n=20 / union=40, index range 0-39

**That is, the existing partition is defined on E4 (40 intervention stimuli), and no partition exists for E1.**

**Yet G1 judges using "the discovery group only," and G2 asks "whether reproduction occurs in the confirmation group." If E1 has no partition, neither G1 nor G2 can be executed.**

**The error was writing in §3 that E4 is "only for sensitivity analysis; will not be used for claims," while also saying that only E4's partition would be borrowed for G1 and G2.**

## M2. Decision: Define a Partition for E1. Before Computing the Judgement

**The rule in §3 "do not re-partition" means not re-creating an existing partition. Newly defining a partition that does not exist is not re-partitioning.** On top of that, fix the rules in advance to prevent arbitrariness.

**Partition rules (fixed before seeing a single result)**:

1. **Target = 287 sentences of E1 that have VAD scores**
2. **Stratification = three quantiles (low, mid, high) of valence obtained from Warriner norms**. Random assignment within each stratum
3. **Ratio = 50/50.** Fractional remainder goes to the discovery group (143 / 144)
4. **Seed = 20260926**, using `numpy.random.default_rng`, **extracted IDs recorded in JSON**
5. **Output = `03_解析/plan_b/e1_split_20260926.json`.** Explicitly state `defined_before_any_G1_judgement: true`

**Reason for stratifying by valence**: Because the quantity used for judgement is the change in output distribution, and valence is the axis among the emotional properties of the stimuli that most strongly affects outputs. **Without stratification, extreme valence may be concentrated in one group, causing inter-group comparison to reflect differences in stimulus properties.**

## M3. Candidate Direction Computation Is Also Limited to the Discovery Group (Important)

**This is the substantive reason for the halt.**

**ICA components, top 10 principal components, and Jacobian sensitivity directions are all computed exclusively from the activations of the discovery group (143 sentences).**

- If computed from all 287 sentences, **confirmation group data enters into the selection of candidates.** The purpose of the discovery/confirmation partition is lost
- **The PMF floor basis is also built from the discovery group**
- **G1 judgement is performed in the discovery group.** The confirmation group is opened in G2, and it is checked whether the cells that passed G1 reproduce

**The Jacobian computation currently running targets all 287 sentences and must therefore be halted and remade using the discovery group of 143 sentences.** Since not a single judgement statistic has been computed, **this does not constitute opening the data.**

**Cost decreases**: 287 → 143 means Jacobians take about 1.43 hours instead of 2.87 hours.

## M4. Treatment of the Existing E4 Partition

**The E4 partition (discovery 20 / confirmation 20) is left as-is. It will not be remade.**
E4 is specified as sensitivity analysis only in §3, and **that partition will be used when performing the sensitivity analysis.**
**The handling of E4 already used in B0 and E1 diagnostics will not be changed.** The results of Paper 2 (methodology paper) will also not be changed.

## M5. Record

**This error was found because a team member actually opened the partition file and reported its contents.** The group wrote "use the existing partition as-is" without confirming what the existing partition was defined on.
**Lesson**: When writing "use the existing X as-is," **confirm what that existing X is by the file contents.** Do not infer the name and role.

**Also record**: The group stated to a team member "300 items processed means 13 are in neither group," but **this was an error** (since E1 has no partition, they are not in any group to begin with). The conclusion of taking 287 is based solely on the description of pre-registration §3.
