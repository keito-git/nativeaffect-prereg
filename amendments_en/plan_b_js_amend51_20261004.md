# Pre-registration Amendment 51: The G1 judgement (Arm II, 160 cells) is terminated

**Created**: 2026-10-04
**Decision by the principal investigator**: 2026-10-04 "If G1 is meaningless, it is fine to terminate it."
**Judgement**: **Terminate. Will not re-run.**

---

## AZ1. Background

The G1 judgement (Arm II, fp32, 160 cells) was running on the old container `emotionnaibu-9d659dc49-q8hlb` when it stopped due to loss of GPU device permissions (`99_記録/GPU障害_管理者向け報告_20261004.md`). The container was deleted on 2026-10-04, and **the run was lost.**

## AZ2. State of progress at the time of loss (based on preserved data)

- `jac`: 99 out of 140 cells passed (70.7%)
- `ica` and `pc` did not reach full-layer completion
- Confirmed values for the number of completed cells and per-layer p, q, δ_a, δ_c are not available

**These numbers will not be used in the paper.** Not all 160 cells are complete, and `build_numbers.py` is designed to reject incomplete layers (`CELLS_PER_LAYER = 40`).

## AZ3. Reason for termination

Paper 3 has been converted to the **variance-matched audit of evaluation-dimension steering** by the decision of the principal investigator (amendment 49). The G1 judgement belongs to the old main series (causality of AI-native axes) and **will not be used in the main results of the audit.**

Furthermore, in amendment 50, it was confirmed that when topics are matched, the agreement of emotion categories across models does not exceed chance. The premise supporting the old main series is weak.

Re-running would require approximately 4 hours of GPU time, competing for resources with Stage A and Stage B of the audit.

## AZ4. Description in the paper

The interruption of the G1 judgement will not be hidden. **"It was interrupted due to a GPU failure, and was not re-run" will be written.**
Partial results (jac 70.7%) will not be cited as evidence.

## AZ5. What has been preserved

`03_解析/_server_backup_20261004_gpu障害/` (241MB, all items verified)

- 8 right singular basis vectors of the Jacobian (`np.load` verified, orthogonality error ≤3.0×10⁻⁷)
- 3 direction vectors from `G1_judgement`
- Result JSON, logs, code, stimuli

**If re-running becomes necessary, reconstruction can be done from here.** It will not be deleted.
