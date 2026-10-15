# Pre-registration Amendment 33: The sensitivity subspace is common regardless of domain of origin (exploratory).
# Register this as a new series to test the principal investigator's hypothesis.

**Created**: 2026-10-03
**Position**: §AG is an **unregistered exploratory observation**. §AH is a **pre-registration for a new question** and is separate from the Prediction A/B/C series of Amendments 29–32. The judgement in Amendments 30 and 32 (AC1 is final; the 2×2 series closes) is not changed. **This does not revisit closed questions; it poses a different question.**

---

## AG. Exploratory observation: the sensitivity subspace is independent of domain of origin

### AG1. What was measured

Jacobian-derived sensitivity directions are stored as 10 vectors, 4096-dimensional, per layer.

- Emotion-derived: `sensitivity_directions` in `plan_b_qwen3_8b/G1_jacobian/layer{11,16,22,27}.json`
  (stimuli = E1 discovery half, n=144)
- Math-derived: `plan_b_qwen3_8b/G1_jacobian_gsm8k/layer{11,16,22,27}.json`
  (stimuli = gsm8k_train.jsonl seed=20260928, n=144)

Confirmed that the two are not identical as vectors (`np.array_equal` = False, all layers).

Agreement was measured by **mean squared canonical correlation** `(1/k)Σσ_i²` (σ = canonical correlation). This equals the Frobenius inner product of projection matrices `‖P_A P_B‖_F² / k` and is invariant to the choice of basis.
The null is **200 pairs of random 10-dimensional subspaces in 4096 dimensions**.

### AG2. Results

| Layer | Mean squared canonical correlation | 1st canonical correlation | Null mean | Null p95 | Null ratio |
|---|---|---|---|---|---|
| 11 | 0.1767 | 0.835 | 0.0024 | 0.0030 | **72.7×** |
| 16 | 0.1037 | 0.585 | 0.0024 | 0.0030 | 42.7× |
| 22 | 0.0930 | 0.494 | 0.0024 | 0.0030 | 38.3× |
| 27 | 0.1938 | 0.641 | 0.0024 | 0.0030 | **79.7×** |

Null mean 0.0024 matches the theoretical value k/d = 10/4096 = 0.00244 (confirming the null is correctly constructed).
**All 4 layers: observed values greatly exceed the null p95 (none of the 200 null samples exceeded the observed values).**

Additionally, sensitivity directions are **not variance directions.** Mean |cos| with the top-10 principal components is
0.0329–0.0383 for emotion-derived and 0.0167–0.0222 for math-derived, only slightly above the expected value for a random unit vector √(2/(π·4096)) ≈ 0.0125.

### AG3. What this contributes to the reading of Amendment 32 results

The equivalence of diagonal and off-diagonal in the 2×2 (Amendment 32 AF3) and this observation are **two sides of the same coin.** If the sensitivity subspace is common regardless of domain of origin, it follows naturally that swapping the origin does not change δ_a. The phenomenon called "reversed" in Amendment 30 and corrected to "equivalent" in Amendment 32 has a measurable structural counterpart.

**However, this is an unregistered post-hoc observation and will not be written as a mechanistic claim.** In the manuscript, it will be labeled as exploratory.

## AH. New pre-registration: decompose the principal investigator's hypothesis into four testable propositions

### AH0. Principal investigator's hypothesis (oral statement 2026-10-02)

> LLMs have concepts unknown to humans, and these combine to form emotional concepts.
> Those concepts can generalize across AIs and can be controlled by intervention.

This is decomposed into 4 propositions that can be judged by the measurements of this research group.

| | Proposition | Current evidence | Testability |
|---|---|---|---|
| **H1** | Directions effective for control lie outside the human framework | Sensitivity directions are nearly orthogonal to principal components (AG2). Paper 2 C3 showed overlap of extracted axes with the human VAD subspace is 0.065–1.81% | **Unregistered, measurable** |
| **H2** | They combine to produce emotional effects | None | **Unmeasured; new design needed** |
| **H3** | **Generalizes across AIs** | Within-model, across domains: 38–80× null (AG2). **Across models: not measured** | **Registered in this amendment** |
| **H4** | Can be controlled by intervention | Sensitivity directions: 90 out of a unique 130 exceed the floor (Amendment 32 AF4, 69.2%) | **Already supported** |

**H3 is the crux of the entire hypothesis.** It has been shown to be domain-independent within a model, but the claim of "across AIs" requires evidence spanning multiple models. The following is pre-registered as the main experiment.

### AH1. Experiment X (H3): cross-model agreement of sensitivity subspaces

**Target models**: In addition to Qwen3-8B (already obtained), **2 models from different families.** Selection criteria are the same as for the floor-comparison experiments in Paper 2: "no overlap in family, layer count, or parameter count." Candidates will be confirmed later and added to this file before jobs are launched.

**Procedure**: For each model and each normalized depth, obtain sensitivity directions as the top-10 eigenvectors of `M = Σ_i V_i V_iᵀ` from the same E1 discovery stimuli (same procedure as existing `g1_jacobian`).

**Cross-model comparison faces the dimension-mismatch problem.** This experiment uses **two dimension-independent quantities** for comparison:

1. **Overlap with principal components** `mean |cos|` (with the top-10 principal components of each model).
   Report the ratio against the dimension-normalized null √(2/(πd))
2. **Floor-exceed rate** (same definition as Amendment 32 AF4) measured for the 3 selection-criterion families

**Judgement criteria fixed in advance (support conditions for H3)**:

- **X1**: Across all 3 models, the floor-exceed rate follows the order **output sensitivity > activity reproducibility > variance magnitude**
- **X2**: Across all 3 models, the floor-exceed rate of variance magnitude (principal components) is **0%**
- **X3**: Across all 3 models, `mean |cos| / √(2/(πd))` for sensitivity directions and top-10 principal components is **below 3.0**
  (= "sensitivity directions are not variance directions" holds regardless of model)

**X1 and X2 both satisfied → H3 supported.** X3 is reported as supplementary evidence for H1.
**If either is violated, report "the effect of selection criterion is model-dependent" and conclude that H3 is not supported.**

### AH2. Essential control: rule out the weight-geometry explanation

The agreement in AG2 might be a property of **the layer's weight geometry rather than the learned conceptual structure.**
If the top singular directions of the layer Jacobian are dominated by the weight matrix regardless of input, then the same subspace would emerge regardless of which stimuli were used. **If this confound cannot be ruled out, neither AG2 nor H3 carries meaning.**

**Control R (sensitivity directions from meaningless stimuli)**: tokens drawn uniformly from the vocabulary (length distribution matched to E1) as stimuli, using the same procedure to construct sensitivity directions.

- **If the agreement between Control R and the emotion-derived subspace is comparable to that between math-derived and emotion-derived, the agreement in AG2 is a property of weight geometry that does not depend on stimulus content, not evidence of concepts.** In that case, AG2 will be rewritten as "top Jacobian directions are a property of the layer," and H3 will be withdrawn
- **If Control R's agreement is significantly lower**, the agreement depends on stimulus content and the conceptual interpretation remains

Judgement uses three-way comparison with a common null (random 10-dimensional subspaces).
**Control R will be run before Experiment X.** If Control R negates the hypothesis, there is no reason to run X.

### AH3. Execution order and termination conditions

1. **Control R** (Qwen3-8B, 4 layers, lightweight GPU) → if negated, terminate all subsequent runs; Paper 3 will be written with only the methodological propositions of Amendment 32 AF5
2. **Layer 27 math×math** (2/40 cells incomplete) → close the 2×2 across all 4 layers
3. **Experiment X** (2 models × 4 depths)

GPU use was approved by the principal investigator on 2026-10-03.

### AH4. Carving out Paper 2 vs. Paper 3 (decision by the principal investigator, 2026-10-03)

- **Paper 2**: Which reference set determines the claim?
- **Paper 3**: Which selection criterion determines steerability?

Paper 3 answers the question left in the Discussion of Paper 2 — "does selecting by output sensitivity make one exceed the floor?" — with Paper 3 citing Paper 2 to connect them. The same experiment will not be reported twice.
