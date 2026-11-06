# Experiment report: base terms and steering at characters of order d ≥ 3

`COPRIME-DICHOTOMY-20261027-001B-E002`, run once under its frozen contract on 2026-10-27 (227 s).
- **Contract and code:**
  `experiments/COPRIME-DICHOTOMY-20261027-001B/COPRIME-DICHOTOMY-20261027-001B-E002_base_terms_and_steering_at_higher_characters_rerun/`
- **Outputs:**
  `artifacts/COPRIME-DICHOTOMY-20261027-001B/COPRIME-DICHOTOMY-20261027-001B-E002_base_terms_and_steering_at_higher_characters_rerun/`

**Verdict: supported** under the frozen rule. There were no machinery failures and no prediction failures, and all three negative
controls failed to match.

**The first run, `COPRIME-DICHOTOMY-20261027-001B-E001`,** froze the same predictions but crashed in R3 before any verdict.
- The case (p, d) = (11, 5) used 6 copies of the 3-strand 4_1 (13 strands), while cable₅(P4) needs 20.
- Its artifact directory keeps the crash log and an `invalid` result.
- E002 changed only that parameter (11 copies), restored the scoping assertion, and added a construction-only check, `build_check.py`,
  run before the frozen run.

## What was tested

- **The groups.** G = exp(𝔫) ⋊ C_r with sector τ of order d ≥ 3, on S³_{d/p}(K) (and S³_{d/1}(K) in R1).
- **The measurement.** cd_lib's braid model solves the layers and pairs the obstruction layer with (J_t^T s, 0), J_t the Squier
  form.

| Rule | Prediction | Cases | Outcome |
| --- | --- | --- | --- |
| R1 pinning | at slope d/p the exact count of lifting class data on K # K is the square of that on K; at slope d/1 it is not | 6_1 at (p, d) = (5, 4), (7, 3); 3_1 at (7, 6), four-way algebra | 3 / 3 multiplicative at d/p (e.g. 3721 = 61²); 3 / 3 not at d/1 (1929, 7489, 20881) |
| R2 local forms | chiral knots obstruct; negative amphichiral knots and (k,1)-cables of T(2, p) never do | 12 chiral rows; 66 amphichiral rows (4_1, 6_3, 8_9, 8_17, 8_18, p up to 19, three algebras); 56 cable rows (seven (p, d, k), four algebras including a pair-failing one) | as predicted: chiral lift fractions 0.125–0.5; amphichiral and cable all 1 |
| R3 steering | ΔQ = κ_t Σ_j ⟨W_j⁽³⁾(leaves), ℓ_j(s)⟩, κ_t = t⁻² − t⁻¹, d-strand bundles; base Q = 0 | 48 single insertions at d = 3, 4, 5, 6 (seven primes), four-way, F3 and the class-4 algebra (layers 3 and 4) | exact; 80 of 144 components nonzero |
| R4 gadgets | Q = Σ_e κ T(leaves); vertex leaf = X_v − X_u | K₂, P₃, K₃ at (7, 3); P₃ at (13, 4); K₂ at (7, 6), up to 2437 crossings | 10 / 10 exact |

**Machinery checks.** All passed:
- J_t invariance for every letter (n ∈ {3, 6, 10}, every t, p ∈ {5, 7, 11, 13});
- the bundle identity;
- insertions leave the cocycle spaces unchanged;
- (J_t^T 𝟙, 0) annihilates every obstruction;
- the vertex leaf equals X_v − X_u.

**Negative controls.** All failed to match:
- κ = 2 at d = 6;
- forward-order bundle products;
- a twist-knot base.

## What it shows

- At slope d/p there are no cross-summand channels.
- Summands with vanishing local forms exist at every root order: amphichiral at odd orders, cables at even orders.
- The r = 2 steering rule generalizes with κ_t, including the class-4 layer through free layer-2 classes.

## What it does not show

- It proves no theorem; ticket C does.
- Random samples test polynomial identities at random points.
- Prediction and measurement share the colourings and the P4 tensor. R1's exact counts are the independent route.
- There is no class 5, and no p = 2 or 3.
