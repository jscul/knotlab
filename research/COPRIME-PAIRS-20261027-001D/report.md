# Experiment report: interacting pair failures on zero-jump gadgets

Ticket `COPRIME-PAIRS-20261027-001D`: two frozen runs, each after its construction-only check `build_check.py`.
- **E001** (2026-10-27, 6952 s): verdict **refuted**.
  - Contract and code: `experiments/COPRIME-PAIRS-20261027-001D/COPRIME-PAIRS-20261027-001D-E001_interacting_pairs_on_zero_jump_gadgets/`
  - Outputs: `artifacts/COPRIME-PAIRS-20261027-001D/COPRIME-PAIRS-20261027-001D-E001_interacting_pairs_on_zero_jump_gadgets/`
- **E002** (successor, 2026-10-27, 6299 s): verdict **supported**.
  - Contract and code: `experiments/COPRIME-PAIRS-20261027-001D/COPRIME-PAIRS-20261027-001D-E002_interacting_pairs_on_the_solution_variety/`
  - Outputs: `artifacts/COPRIME-PAIRS-20261027-001D/COPRIME-PAIRS-20261027-001D-E002_interacting_pairs_on_the_solution_variety/`

E001 is kept unchanged as negative evidence. E002 tests the claim the theorem actually makes and reproduces E001's failure as a
control.

## What was tested

Interacting pair failures are pair failures of 𝔪_d whose higher layers have components at characters the gadget uses. The claims
under test, for gadget knots at slope d/p built from zero-jump blocks:
- the pinned count is an edge-local integer partition function on the layer-2 variety 𝒱;
- its edge count F(σ_u, σ_v) is maximal on the diagonal and strictly smaller, but positive, across a pair-failing difference;
- so F Fᵀ has rank at least two.

The gadget blocks are summands whose first and last strands carry the meridian value exactly. Each edge has dedicated vertex copies
and one cable_d([A₁₂, A₂₃]) insertion. The single-edge gadget is K₂; the path gadget P₃ has edges e₀ = (0, 1) and e₁ = (1, 2).

| case | algebra | (p, d) | slots | summands | K₂ / P₃ crossings | F_max |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | free class 3 on (1, 1) | (11, 5) | (1, 1, 2) | 8_9, 8_9, 4_1 | 435 / 1491 | 1331 |
| A2 | free class 3 on (1, 2) | (11, 5) | (1, 2, 3) | 8_9, 4_1, 4_1 | 431 / 1483 | 14641 |
| A3 | free class 4 on x (0), y (1) | (11, 5) | (1, 1, 2) | 8_9, 8_9, 4_1 | 435 / 1491 | 14641 |
| A4 | free class 3 on (1, 2, 2) | (5, 4) | (2, 1, 3) | C_1 of T(2,5), C_2 of T(2,5), C_2 of T(2,5) | 394 / 1274 | 15625 |
| A5 | free class 3 on (1, 2) | (5, 4) | (2, 1, 3) | C_1 of T(2,5), C_2 of T(2,5), C_2 of T(2,5) | 394 / 1274 | 625 |

## E001: refuted by an off-variety locality rule

| case | R1 F(σ, σ) | R2 (F(0, D), F(D, 0)) | R3 random F | R4 path locality (random π₁) | R5 minors | holds |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | 1331 | 121, 121 | 11, 121 | 209 path solutions over 3 configurations; e₀ sets equal | all > 0 | yes |
| A2 | 14641 | 121, 121 | 121 | 1089 path solutions over 3 configurations; e₀ sets equal | all > 0 | yes |
| A3 | 14641 | 121, 121 | 11, 121 | 319 path solutions over 3 configurations; e₀ sets equal | all > 0 | yes |
| A4 | 15625 | 1, 1 | 1 | 2 path solutions over 1 configuration; e₀ sets equal | all > 0 | yes |
| A5 | 625 | 1, 1 | 1, 625 | 1257 path solutions over 3 configurations; e₀ sets differ in 1 of 3 configurations | all > 0 | **no** |

- **The failure.** In A5, one of three path configurations had e₀'s path solution set (627 solutions over three
  σ₀) differ from its single-edge set, while e₁'s equation values stayed constant.
- **Why it is not the theorem's claim.** R4 drew e₁'s private data π₁ at random, mostly off e₁'s own solution set. The proof claims
  locality only on 𝒱 (`COPRIME-PAIRS-20261027-001E`, Lemmas 5–6). Off 𝒱, e₁'s insertion has a layer-2 part, and conjugating passed
  strands by it shifts e₀'s blocks at layer 3.
- **Everything else held.** R1, R2, R3 and R5 held in all five algebras, and R4 held in A1–A4. Machinery checks passed. The controls
  behaved as required: the cumulative design broke locality (X1), and with no dual slot there was no deficit (X2).

## Diagnostics after E001 (post hoc, other seeds; not evidence)

- **A5.** With π₁ on e₁'s single-edge solution set, e₀'s path sets equalled the single-edge sets in 36 of 36 comparisons. Off that
  set they differed in 7 of 24.
- **A1.** On the variety, the zero-jump design differed in 0 of 12 comparisons, and e₁'s equations vanished on every e₀ solution.
  The cumulative design differed in 12 of 12.

## E002: locality on the solution variety

R4 now draws π₁ from e₁'s single-edge solution set at (σ₁, σ₂). It then requires three things:
- e₀'s path solution set equals the single-edge set at (σ₀, σ₁);
- e₁'s equations vanish on every e₀ solution;
- vertex pairings vanish.

R1–R3 and R5 are unchanged. Seeds are fresh.

| case | R1 F(σ, σ) | R2 (F(0, D), F(D, 0)) | R3 random F | R4 on the variety | R5 minors | holds |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | 1331 | 121, 121 | 11 | 66 path solutions, 6 comparisons; differing sets 0, nonzero e₁ equations 0, nonzero vertex pairings 0 | all > 0 | yes |
| A2 | 14641 | 121, 121 | 121 | 726 path solutions, 6 comparisons; differing sets 0, nonzero e₁ equations 0, nonzero vertex pairings 0 | all > 0 | yes |
| A3 | 14641 | 121, 121 | 11, 121 | 1386 path solutions, 6 comparisons; differing sets 0, nonzero e₁ equations 0, nonzero vertex pairings 0 | all > 0 | yes |
| A4 | 15625 | 1, 1 | 1 | 2 path solutions, 2 comparisons; differing sets 0, nonzero e₁ equations 0, nonzero vertex pairings 0 | all > 0 | yes |
| A5 | 625 | 1, 1 | 1, 625 | 636 path solutions, 12 comparisons; differing sets 0, nonzero e₁ equations 0, nonzero vertex pairings 0 | all > 0 | yes |

**Controls** (a match would make the run invalid):
- **X1 (cumulative design, A1, same on-variety protocol).** Some e₀ set must differ. Observed: 6 of 6 comparisons differ.
  Not matched, as required.
- **X2 (no dual slot, A1).** The dual slot gets the type ±1, so no block carries duals at ±2. No deficit may appear. Observed:
  F(0, D) = 14641, F(0, D) = 14641, F(0, D) = 14641 against F_max = 14641. Not matched, as required.
- **X3 (A5, π₁ off its solution set).** Some e₀ set must differ, reproducing E001's failure. Observed: 11 of 24 comparisons
  differ, in 6 of 8 configurations. Not matched, as required.

Machinery failures: 0. Failed cases: none.

## What the numbers say

- **Locality lives on the variety.** On it, the path gadget's edge equations agree with the single edge in every comparison of
  every algebra. Off it they need not (E001, X3), exactly as the proof's Lemmas 5–6 predict.
- **Higher layers change the weights, not the rank.** In A1, F takes the values 11, 121 and 1331. The diagonal stays at F_max, and
  every pair-failing difference stays strictly below it.
- **The cumulative design breaks locality; the zero-jump design restores it.** Removing the dual slot removes the deficit, so the
  rank comes from the pair bracket read by the dual slot, not from the gadget geometry.

## What it does not show

- Locality is tested on one graph shape (a path of two edges) at sampled configurations; the general argument is the proof
  `COPRIME-PAIRS-20261027-001E`.
- The on-variety restriction was adopted after E001. It is the theorem's stated claim, not a loosening fitted to the data, and X3
  tests the distinction itself.
- The five algebras all satisfy the clean-edge conditions.
- **A correction to both contracts' red-team notes.** They say that, in scoping, free class 4 on (1, 1) at d = 5 had vanishing
  vertex pairings on single-edge solutions. That held only at random vertex pairs, where solutions are rare. At the diagonal its
  vertex equations are nonzero at 396 of 400 random points (`COPRIME-PAIRS-20261027-001E`, check 6), so that algebra's edges do
  couple through its vertices. Neither run uses it.
