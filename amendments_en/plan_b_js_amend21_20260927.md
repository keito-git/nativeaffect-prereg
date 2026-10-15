# Pre-registration Amendment 21: Finalize how Cliff's δ is constructed from 100 floor draws

**Target**: Pre-registration body §2 G1 ("Cliff's δ ≥ +0.20")
**Created**: a group member / 2026-09-27
**Status**: **Not a single G1 judgement statistic exists. The GPU has not started due to a fault.**
**Origin**: During implementation, a group member disclosed that the registered text does not specify how δ is aggregated.

---

## U1. Specification gap

§2 G1 states "one-sided permutation p < 0.05 (BH-corrected q < 0.05) and **Cliff's δ ≥ +0.20**."
**However, it does not specify how δ pairs "an axis vs. 100 floor draws."** At least three approaches exist.

- **(a)** For each stimulus, take the **mean** of the 100 floor draws, then compute paired δ over 144 pairs
- **(b)** **Pool** the 144 axis values and 144×100 floor values and compute unpaired δ
- **(c)** Compute δ for each individual floor draw, then take the **median** of 100 δ values

## U2. Decision: adopt (a). Align with existing practice

**This is the same aggregation as done for the in-plane floor in `pos_ctrl_inplane.py:429`.**

**Reason**: This is structurally equivalent to the α issue (Amendment 18 R1) and the fp16 issue (Amendment 19 S2). **C1, C2, and C4 were computed using (a), and the threshold δ ≥ +0.20 was implicitly set on top of this practice.** Changing the aggregation changes the meaning of the threshold. **Comparability between measurements takes priority.**

**The one-sided permutation p is as registered: $(1+\#\{{\rm floor} \ge {\rm axis}\})/101$.** p cannot be 0, and with 100 draws q < 0.05 is reachable (impossible with 20 draws). This was fixed by self-checking.

## U3. However, (a) inflates δ. Visualization is mandatory

**(a) averages the 100 floor draws, so the spread of the comparison target shrinks by a factor of $\sqrt{100}=10$.**

**As a result, the stimulus-wise signs align and δ approaches +1 even when the axis only marginally exceeds the floor mean.** This makes |δ| larger than (b) or (c) — i.e., **non-conservative relative to the condition "δ ≥ +0.20."**

**Obligations**:

1. **State in the same location as the results that the δ is relative to the floor mean.** It is not "the proportion of times the axis exceeds a single random draw"
2. **Also report (c) alongside** (compute δ for each individual floor draw and report the median and quartiles of 100 values). **No additional GPU computation is required. It can be computed from the same data**
3. **If (a) and (c) diverge, report the divergence.** Judgement uses (a) only, but **cells where (c) is small will be described as "exceeds the floor mean, but superiority over individual random directions is limited"**

**Reason for imposing 3**: **If G1 passes, the magnitude of δ will be cited as evidence that "the effect is large."** If it is not recorded that (a)'s δ is structurally large, it will be misread.

**The judgement itself uses (a).** It will not be switched to (c) after seeing the results.

## U4. Also confirmed: the mirror arm uses one polarity

**A group member showed that mirror reflection is invariant to the sign of $d$.**

$$x - 2(x\cdot(-d))(-d) = x - 2(x\cdot d)d$$

**Therefore it is not necessary to measure ± both polarities in the mirror arm.** Fixed by self-checking.

- Addition arm: 144 stimuli × 2 polarities
- **Mirror arm: 144 stimuli × 1**

**This is a cost reduction, not a design change.** The object being measured is the same. **The previous estimate of 60.76 hours counted the mirror arm as 2 polarities in error; the correct figure is 45.6 hours.**

## U5. Record: `script_sha256` was already the existing project standard

**Existing ICA result JSONs record `manifest.script` and `manifest.script_sha256`** (`rebuild_axes_nopad.py` / `e67608bf...`).

**This means the absence of a script hash in the G1 Jacobian-stage output was not an added requirement but a regression from the existing standard.** This was the cause of the hash-mismatch incident (Amendments 15 and 16).

**Rule**: **When writing a new script, check what the existing output of the same type records.** Do not fall below the existing standard.

## U6. ICA uses the existing implementation via import

Call `run_ica.run_ica_sweep` with `k_range=(20,20)` and `seed=42`.

**This code has a record of a corrected bug in the whitening scale restoration** (multiply `sqrt(explained_variance)` by `ica.mixing_` (the mixing matrix), not `ica.components_` (the separation matrix); corrected 2026-09-24).

**Do not rewrite it.** The group member's judgement "rewriting it would almost certainly have introduced errors" is correct. **This is the same family of problems as the 9 JS functions and the `g1_pc_overlap` stimulus path error.**
