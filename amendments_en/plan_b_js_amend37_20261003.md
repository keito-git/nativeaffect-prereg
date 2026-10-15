# Pre-registration Amendment 37: Measure the direction of movement using a signed readout, and test whether a direction moves the output "in which direction"

**Created**: 2026-10-03
**Position**: Pre-registration of a new measurement. Amendment 34 (H3 withdrawn) and Amendment 36 (V/A/D residual series) are not changed.
**Launch condition**: The job must not be launched until this file has been committed and pushed to remote.

---

## AL0. Why measure this

The output metric used to date is the JS divergence of the next-token distribution, which **does not distinguish sign.** "How much did it move" can be measured, but "in which direction did it move" cannot.

Today's observation found that the per-stimulus profile of each direction is uncorrelated with the stimuli's valence (all families, all layers: same as null, mean |r| 0.050–0.089 vs. null mean 0.071, p95 0.165). However this is a negation about **input-side content**, and says nothing about **output-side direction.**

If a direction carries valence, $+\alpha v$ and $-\alpha v$ should move the output **in opposite directions.** JS treats both as "moved a lot" and returns the same value. **There remains the possibility that all past nulls are an artifact of the instrument's resolution.** This experiment directly tests that.

## AL1. The quantity to measure

From vocabulary norms (Warriner), take the words existing as single tokens in the model vocabulary with highest valence as $\mathrm{POS}$ and lowest valence as $\mathrm{NEG}$ ($n$ words each; $n$ is determined from vocabulary coverage at implementation time and **fixed in this file before seeing the results**).

Define the signed readout at stimulus $h$ as:

$$R(h) = \frac{1}{|\mathrm{POS}|}\sum_{w \in \mathrm{POS}} \log p(w \mid h)
       - \frac{1}{|\mathrm{NEG}|}\sum_{w \in \mathrm{NEG}} \log p(w \mid h)$$

Define the **antisymmetric effect** of direction $v$ as:

$$S(v) = \tfrac{1}{2}\big[ R(h + \alpha v) - R(h - \alpha v) \big]$$

averaged over stimuli. $S(v)$ becomes large when $v$ carries valence, and scatters around 0 for a direction without content. It is handled with sign, not as $|S(v)|$, and the asymmetry between $+v$ and $-v$ itself is the quantity.

## AL2. Equalize output perturbation magnitude (response to a criticism that gains differ between families)

Since gains differ between families, equating $\alpha$ would make comparison meaningless. **Equalize the output perturbation magnitude.**
However since the equalization method is not uniquely determined, **execute 2 ways and claim only when conclusions agree.**

- **Budget 1**: equalize to a common value of the L2 norm of all logits $\|\Delta \mathrm{logit}\|_2$
- **Budget 2**: equalize to the L2 norm restricted to the $\mathrm{POS} \cup \mathrm{NEG}$ dimensions

Budget 2 privileges content dimensions a priori and is circular alone. **Budget 1 is primary; Budget 2 is a sensitivity analysis.**

To confirm the effective range of the linear approximation, measure the range in which $\|\Delta \mathrm{logit}\|$ is proportional to $\alpha$ for each family and each layer, and **use only $\alpha$ within that range.**

## AL3. Controls

- **Control H (required)**: Haar random directions within the sensitivity subspace $S$. Injected with the same budget.
  Carries no content but has the same gain.
  Note: today's confirmation that $|\cos|$ between $S$-internal random directions and human V/A/D directions is nearly the same as for random directions in the full space (ratio 0.79–1.60) suggests Control H is functional
- **Control L (required)**: Label permutation. Randomly permute the $\mathrm{POS}/\mathrm{NEG}$ labels and recompute $S(v)$ to construct a null distribution (500 permutations)
- **Control F**: Random directions in the full space (same population as existing floors)

## AL4. Judgement criteria fixed in advance

**3 or more of 4 layers** must be satisfied.

- **B1**: The median $|S(v)|$ of the output sensitivity family **exceeds the 95th percentile of Control H**.
  If not, "content is not detected even with the signed readout," and
  **the causal/control clause of the hypothesis is closed. Paper 3 will be written with the methodological proposition of Amendment 32 AF5**
- **B2**: If B1 is satisfied, the **sign of $S(v)$ is consistent across stimuli**
  (sign agreement rate across stimuli passes a binomial test at $p<0.05$). If not consistent,
  there is an average directionality but it is stimulus-dependent, and **the claim is weakened**
- **B3**: B1's conclusion agrees between Budget 1 and Budget 2. If not,
  **report "depends on the equalization method" and make no claim from either conclusion**

**Even if termination occurs at B1, that fact reinforces the central proposition of Paper 3** (direct evidence for the claim that what works is gain, not content).

## AL5. Promises in this amendment

- The job will be launched only after this file has been committed and pushed
- The count $n$ of $\mathrm{POS}/\mathrm{NEG}$ words will be confirmed and added to this file **before seeing the results**
- Judgement will be performed only by B1–B3; criteria will not be changed after seeing results
- Report the measured effective range of the linear approximation together with the $\alpha$ used for judgement
