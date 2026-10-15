# Pre-registration Amendment 27: Record the cross-layer shared subspace and fix the operating rules for exploration

**Target**: Operating rules for the exploratory stage, and registration of the new candidate "cross-layer shared direction"
**Created**: a group member / 2026-09-28
**Status**: Experiment A (validation-set replication) is running. **Not a single validation-set test has completed.**
All analyses in this amendment used **only sensitivity directions constructed from the discovery half**, and the validation set has not been touched.

---

## AA1. Principal investigator instruction (2026-09-28): "There must be a concept that can be generalized. Keep going until you find it."

**Exploration continues. However, operating rules are fixed to avoid spending down the validation set.**

| Data | How to use |
|---|---|
| **Discovery half, 144 stimuli** | **May be explored freely. No upper limit on number of trials** |
| **Validation half, 143 stimuli** | **Once only, after narrowing down to one best candidate** |
| **Record of trials** | **All variants tried on the discovery half are recorded in this amendment series.** The manuscript will write "N variants were tried on the discovery half; the most promising one was tested on the validation half" |

**Reason**: If each variant is tested on the validation half, it ceases to be held-out data.
**If 20 variants were tried and the 20th passed, that is simply hitting on the 20th try.**
**Freedom of exploration and strength of claims can only coexist through this separation.**

## AA2. Discovery-half exploration #1: eigenvalue rank does not predict effect

From `g1_judgement_discovery_20260928.json` and `G1_jacobian/layer*.json` (no GPU needed).

| Layer | Spearman (eigenvalue rank, δ_a) | δ_a max | δ_a min |
|---|---|---|---|
| 11 | **+0.042** | jac_4 (+1.000) | **jac_0 (+0.264)** |
| 16 | +0.321 | jac_7 (+1.000) | jac_5 (+0.444) |
| 22 | +0.224 | jac_1 (+1.000) | jac_4 (+0.292) |
| 27 | +0.164 | jac_2 (+1.000) | jac_4 (+0.181) |

Eigenvalues span 4× (42→10.4 at layer 11), yet **effect barely follows rank.
Across all 4 layers, jac_0 (the first eigenvector) is not the strongest, and at layer 11 it is the weakest.**

**Implication**: it is not the case that "the single direction with maximum sensitivity" is special. **The target to search for may be a subspace rather than a single axis.**

## AA3. Discovery-half exploration #2: **the sensitivity subspaces across 4 layers share a common structure** (primary finding)

Principal subspace cosines between the subspaces spanned by 10 unit-norm vectors per layer.
Random control: 200 pairs of random orthogonal subspaces of the same shape (seed 20260928).

| Layer pair | Mean cosine | Random mean | z |
|---|---|---|---|
| L11–L16 | **0.526** | 0.0415 | **+169** |
| L22–L27 | **0.580** | 0.0415 | **+188** |
| L16–L22 | **0.471** | 0.0415 | **+150** |
| L11–L22 | 0.315 | 0.0415 | +95 |
| L16–L27 | 0.297 | 0.0415 | +89 |
| L11–L27 | 0.241 | 0.0415 | +70 |

The random control mean is 0.0415 (p95 = 0.0467); observed values are 0.241–0.580. **All 6 pairs greatly exceed the p95.**

**Adjacent layers are more similar, and similarity decreases with distance** (L11–L16: 0.526 → L11–L27: 0.241).
**The picture is a shared subspace that rotates gradually along depth.**

### Direction common to all 4 layers
Top eigenvalues of the projection sum `M = Σ_L V_L V_Lᵀ` (maximum 4.0 = completely contained in all 4 layers):
`3.125, 2.609, 2.577, 2.377, 2.373, 2.230, 2.137, 1.860, 1.587, 1.497`

Containment rate `|V_L v|²` of the 1st eigenvector in each layer's subspace:
L11 = 0.780 / L16 = 0.853 / L22 = 0.812 / L27 = 0.680 (eigenvalue 3.125 / 4 = 78%)

## AA4. Registering a new candidate: test the "cross-layer shared direction" as an intervention direction

**Candidate**: the 1st eigenvector `v` of `M` above (sign is arbitrary; for the mirror arm, sign-invariance holds, so there is no issue).

**Procedure**: test `v` as `d` across 4 layers using the registered floor `g1.pmf_draws`, registered JS, Arm II, fp32.
**Use discovery-half 144 stimuli** (exploratory stage). Estimated: 1 vector × 4 layers × 100 floors × 144 stimuli ≈ **35 minutes**.

### Prediction (fixed before seeing data)
**The δ_a of `v` exceeds the median δ_a of the 10 jac vectors in the same layer.**

- **If it exceeds**: the shared component across layers is more effective than the layer-specific components.
  **`v` becomes the top candidate to bring to the validation set**
- **If it does not exceed**: the shared structure exists but does not carry the intervention effect.
  **`v` will be eliminated as a candidate.** Record "a shared subspace exists but is not the carrier of the effect"
- **In either case, this test is on the discovery half and will not be used for generalization claims**

## AA5. Exploration candidates not yet executed (record only; predictions will be added when executed)
- Extracting components stable across stimuli (current Jacobian is a simple sum of per-stimulus subspaces)
- Separating components shared versus specific across emotion categories (the 40 categories of E4)
- Intervention on the subspace itself (rotation within the space spanned by 10 vectors)

**All of these will be performed on the discovery half. The validation half follows the rule in AA1.**
