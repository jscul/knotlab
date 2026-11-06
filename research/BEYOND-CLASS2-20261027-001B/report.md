# Experiment report: the four-way Massey form on gadget surgeries

`BEYOND-CLASS2-20261027-001B-E001`, run once under its frozen contract on 2026-10-27.
- Contract and code: `experiments/BEYOND-CLASS2-20261027-001B/BEYOND-CLASS2-20261027-001B-E001_four_way_massey_form_on_gadget_surgeries/`
- Outputs: `artifacts/BEYOND-CLASS2-20261027-001B/BEYOND-CLASS2-20261027-001B-E001_four_way_massey_form_on_gadget_surgeries/`
  (result.json, rows.json, run_log.txt)

**Verdict: supported** under the frozen rule, in one run of 2,264 s. There were no machinery failures and no prediction failures, and all negative controls failed to match.

## What was tested

- **The group.** G_p = U₄(F_p) ⋊ ⟨diag(1, −1, 1, −1)⟩ on 2-surgeries of closed braids (H₁ = Z/2).
- **The form.** Q(c; s) = ⟨o(c), (J^T s, 0)⟩, the layer-3 obstruction read through the J-duality of the Fox-colouring transport.
- **The predictions.** All were fixed before the run. The constant κ = 2 was read off in scoping, at p = 5 on P4 only.

| Rule | Prediction | Fixtures | Outcome |
| --- | --- | --- | --- |
| R0 base | Q = 0 on sums of 4_1, 5_2 and T(2, p) | 9 full tables (level model), 6 sampled sums at p = 5, 7, 11, 13 | 15 / 15 |
| R1 steering | each insertion adds 2 Σ_j Λ_j(c) ℓ_j(s) (Magnus tensor of the conjugators, bundle functionals at the insertion level) | 17 fixtures: P4 and P4B = [[A23, A34], A12], levels and offsets, sums of 4_1, 5_2, T(2, 5), T(2, 7), T(2, 11), T(2, 13), mixed and doubled insertions, an under-dragged and a shifted insertion; 64 samples each | 17 / 17 exact |
| R1, level model | change of the full table = −2 × rule | P4 (6, 0) and P4B (0, 0) on 4_1 x4, 256 entries each | 2 / 2 exact |
| R2 gadget | Q = 2 Σ_e T(X_v − X_u; privates), leaves in closed form | K2, P3, digon, K3, K1,3, C4 at p = 5, 7, 11 (120 to 788 crossings, up to 28 summands); 64 samples each | 18 / 18 exact; closed-form leaves 18 / 18 |
| R3 counts | sector 1 = p^(N+4) p^(3N) on bases; sector 0 = 1 | ticket A's direct layered count (BCH group, Wirtinger presentation) | 4 / 4: S³₂(4_1) and S³₂(T(2,5)) give 390625 = 5⁸; S³₂(T(2,5)#T(2,5)) gives 244140625 = 5¹²; sector 0 of S³₂(4_1) gives 1 |
| R4 lifting | a class triple lifts exactly when Q(c; .) = 0, with p^(N+1) completions | 40 triples on 4_1 x4 + P4 (10 with c_y = 0, 10 with c_x = 0, 20 random) | 40 / 40 (20 lift) |

**Negative controls.** All five failed to match, as required:
- X1, one edge dropped (K3 at p = 5);
- X2, bundles 0 and 2 swapped (P3 at p = 5);
- X3, a random tensor;
- X4, κ = 1;
- X5, no insertion predicted as inserted.

**Machinery.** All checks passed:
- J-invariance, every letter, n ≤ 10, four primes;
- the bundle identity;
- the cable acting by bundle substitution, conjugators in γ₃F₄, and cable transport = I, for P4 and P4B;
- dimensions and left kernels on every fixture.

## Observations

- **κ = 2 held without change** at p = 7, 11 and 13, for the second braid P4B, and under the level model's opposite convention
  (−2). It was never refit.
- **One mixed fixture gives Q ≡ 0**, both predicted and measured: 4_1 x4 with P4 at (0, 0) and P4B at (8, 1). The two tensors
  cancel on those leaves, although each insertion alone is nonzero.
- **Dragged insertions.** The under-dragged strand changes colour, and the rule used the transported colour; the shifted
  insertion was handled the same way. Both match. This supports the proof's reading of Corollary 4.5 for dragged insertions in
  general, not only the over-dragging used by the gadget.
- **Independence.** Four routes agree:
  - the closed-braid matrix model (bm.py);
  - the level-presentation model (lp.py, with ticket A's Fox calculus);
  - the BCH group of ticket A on cp_lib's Wirtinger presentations (direct_count);
  - the predictions, from the Milnor–Magnus tensors and colour transport.

  The measurement and the prediction share only the layer-1 colourings.

## Limits

- Sampled identities are checked at 64 points per fixture. The full tables are exact but small.
- The gadget sizes test the construction, not every graph. The general realization is the proof in ticket C, §§4–5.
- The direct counts are small (bases with N ≤ 2).
