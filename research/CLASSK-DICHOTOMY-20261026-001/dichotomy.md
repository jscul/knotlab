# A dichotomy for class-(K) groups with bounded first homology

Epic `CLASSK-DICHOTOMY-20261026-001`, closed 2026-10-27.

## The question

**The assignment.** It was relayed by a peer session on the owner's behalf, after the pattern-1 checkpoint succeeded:

> Please resume the general class-(K) theorem from the successful PATTERN1-CHECKPOINT-20261026-001 and lane A, in the proposed
> odd-prime split scope (r divides p-1) for closed manifolds with bounded first homology … Pursue the proof and its remaining
> obligations using your scientific judgment, and report the result and any precise unresolved gaps … Use mathematical completion or
> a substantive obstruction to determine the stopping point.

The owner also asked that no time-based checkpoints be used.

**The intuition targeted.** This is the complexity side of the 2-versus-3 thesis. Is the easy/hard line, for every coprime
class-2-by-cyclic group, exactly "a commutator joining three nontrivial characters", a genuinely three-way interaction?

**The evidence:**
- [Class-(K) counts on gadget surgeries are positive sums of sector partition functions](../../proofs/CLASSK-DICHOTOMY-20261026-001A/CLASSK-DICHOTOMY-20261026-001A-P001_gadget_counts_are_positive_sums_of_sector_partition_functions/proof.md)
  (A, proof);
- [Sector counts on explicit gadget surgeries, all three patterns](../CLASSK-DICHOTOMY-20261026-001B/report.md) (B, experiment,
  supported);
- [With a hard pair, class-(K) counting is #P-hard with H₁ = Z/r: the dichotomy](../../proofs/CLASSK-DICHOTOMY-20261026-001C/CLASSK-DICHOTOMY-20261026-001C-P001_with_a_hard_pair_class_k_counting_is_sharp_p_hard_the_dichotomy/proof.md)
  (C, proof).

## Outcome

**The dichotomy is proved.** Take p odd, r | p − 1, and G = N ⋊ C_r of class (K).
- **Closed 3-manifolds with |H₁| ≤ C.** Counting homomorphisms π₁M → G is:
  - polynomial if no subgroup G_d = N ⋊ C_d with d | r and d ≤ C has a hard pair (`COPRIME-CLASS2-20261026-001C`);
  - #P-hard under Turing reductions otherwise, already on d-surgeries of knots (C).
- **C ≥ r.** The criterion is simply whether G has a hard pair: (χ, χ′) with χ, χ′ and χχ′ nontrivial and κ_{χ,χ′} ≠ 0.

**Knot groups follow too**, also when commutators involve the trivial character. This closes the gap that lane A and the note left
open.
- So Rowell's Conjecture 3.2(b) fails for every class-(K) group with a hard pair over odd prime fields, unless every #P function is
  computable in polynomial time.
- The note had this only for the Heisenberg family, S₄ and UT₃(F₄) ⋊ C₃.

**How it works.**
- **The count.** On the gadget surgeries, the count is a positive sum over the meridian characters ψ^k of partition functions. Each
  multiplies over disjoint unions, and the k-th is the ψ¹ term of the group with the action raised to the k-th power.
- **The weight.** A Fourier step turns the slot conditions into a positive, even, translation-invariant weight. It has rank one
  exactly when its three pairings vanish, and a hard pair makes the ψ¹ weight nonconstant.
- **Isolation.** A fixed anchor graph and a Vandermonde solve over disjoint unions isolate the hard term. Bulatov–Grohe does the rest.
- **Realization.** The construction of `COPRIME-CLASS2-20261026-001D` §3 never used the group. It was built and measured for all
  three character patterns at two primes.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| The count on gadget manifolds | A positive sum of r sector partition functions, with weight W = \|K₂\| \|K₃\| p^{−rank} on U = B₁ ⊕ A₂₃*. Constant iff the three pairings vanish, rank ≥ 2 otherwise. A hard pair makes W₁ nonconstant | Proved (A). Checked three ways on 1,274 group, pattern, sector and graph cases; 7 known values; 170 hard pairs; 934 negative controls; the count formula against independent lifting counts |
| Sector isolation | Lane A proposed Goldberg–Grohe–Jerrum–Thurley Lemma 6.4, which needs integer vertex weights. Replaced by an anchor graph and a Vandermonde solve over disjoint unions, which needs only multiplicativity and positivity | Proved (C). Exact recovery on four groups, including one with two equivalent hard sectors |
| Realization, all three patterns | 8 surgeries (589–5,324 crossings) at (7, 6) and (5, 4). 108 group-by-fixture comparisons, every sector, closed and knot, all equal to frozen predictions. Leaves pure, H₁ = Z/r | Supported (B) |
| Knot groups with trivial-character commutators | The u-pairing ⟨u ⌣ v ⌣ w⟩ is unchanged by moves (leaves have linking number 0) and block-diagonal over summands. So the knot count is a positive sum of multiplicative (k, β) terms, and the anchor argument still applies | Proved (C). Measured: ψ¹ gives 211 on the knot group against 133 closed; on K₂ ⊔ K₂ knot counts are sums over β of squares, not squares |
| Small homology bounds | Hardness needs a subgroup C_d with d ≤ C carrying a hard pair. Free class 2 on (ζ, ζ², ζ³) at p = 7 is #P-hard exactly for C ≥ 6 | Proved (C) |
| Process | Two session restarts killed the frozen run (logs kept). It was relaunched unchanged as a systemd user unit and finished in 3,058 s. Two trial checks hit the memory limit and were bounded | Recorded |

## Challenged assumptions

- **"Sector isolation needs GGJT Lemma 6.4"** (lane A). Not needed. Anchor isolation avoids its integer-vertex-weight hypothesis.
- **"Knot groups need κ_{1,σ} = 0"** (lane A's gap 3). Not needed. The trivial-character coupling splits into multiplicative pieces
  indexed by β.
- **"The Heisenberg Potts gadgets are the mechanism."** They are special cases. Bulatov–Grohe on the general weight covers every
  class-(K) group.
- **"Hardness holds for every bound on |H₁|."** Refined. It needs a cyclic subgroup of order at most the bound that still sees a
  hard pair.

## Literature and novelty

- **Bulatov–Grohe (2005).** The dichotomy for non-negative symmetric partition functions, in the statement of Cai–Chen–Lu,
  Theorem 2.1. Its hardness side is for multigraphs without loops.
- **Samperton–Weiß (arXiv:2602.02885v2).** Class 2 nilpotent with bounded H²(M; Z(G)).
- **Galindo (arXiv:2605.06984).** Unbounded homology.
- **Kuperberg–Samperton (2018) and Rowell (2009).** The solvable case is open there.
- **Matei–Suciu (2005).** The counting method.
- **Searches.** Those of this epic and the earlier epics found no statement of a bounded-homology dichotomy for semidirect products
  with coprime action.
- **Novelty.** Candidate new, with folklore risk medium. The ingredients are standard (Bulatov–Grohe, clasper realization,
  interpolation over disjoint unions). The contribution is the complete criterion and the knot-group case.

## Precise remaining gaps

1. **p = 2.** The diagonal terms are not κ-terms, and lane A's Bockstein criterion is untested here. UT₃(F₄) ⋊ C₃ is covered
   separately, by `CORRECTIONS-20261026-001D`.
2. **Extension fields** (r ∤ p − 1). Characters live on Frobenius orbits.
3. **Groups outside class (K).** This includes class ≥ 3, non-central layers and non-cyclic tops. See the next step.
4. **Cited, not reproved.** Bulatov–Grohe; the Y-graph = six-component-link model (Habiro, Garoufalidis–Goussarov–Polyak);
   Massuyeau's lemma through `COPRIME-CLASS2-20261026-001B`.
5. **Approximate counting** (Rowell's part (a)) is not addressed. The interpolation is not approximation-preserving.
6. **No external review.**

## Assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the class-(K) dichotomy (p odd, r \| p − 1) | **Status:** Successful | Proved for closed manifolds with bounded H₁ (refined by subgroup orders) and for knot groups. Realization supported on 8 surgeries. Gaps 1–6 above. |
| Local direction: coprime class-2 counting with bounded homology | Practically complete at odd split primes | The hard-pair criterion is exact for class (K). What remains is p = 2, extension fields, or leaving class 2. |
| Broader exploration: complexity of counting into solvable groups with bounded homology | Known alternatives | Beyond class 2 (below); p = 2 and extension fields; approximate counting (#BIS-hard only for UT₃(F₄) ⋊ C₃ so far); converting the result into the Rowell note. |
| Long-term goal: the complexity side of the 2-versus-3 thesis | Capability gained | For a whole class of groups the boundary is exactly "pairwise or bounded" against "three nontrivial characters". This is a complexity theorem, not a native-emergence result. |
| Next recommendation: beyond class 2 | **Next step:** Continue, with a fresh epic testing whether the criterion extends past class 2. **First discriminator** (expected hard): a class-3 group whose class-2 quotient has no hard pair. N is free class 3 of exponent p on x (trivial character) and y (character α). Its cross-layer bracket [y, [x, y]] joins α, α and α². With H₁ = Z/r the x-cocycle vanishes, the class-2 lift is a free α-cocycle, and the class-3 obstruction is its cup product with the y-cocycle. That is the Heisenberg pattern-2 count, so the class-2 quotient does not decide hardness; a "graded" hard pair (between any two layers) is needed. **Second discriminator** (open): no graded hard pair, but x and y have inverse characters α and α⁻¹, so [x, y] is trivial, and [[x, y], w] has character γ. Then the obstruction is a triple Massey product ⟨c_x, c_y, c_w⟩ tested against V_{γ⁻¹}: a four-way form on characters α, α⁻¹, γ, γ⁻¹. | If the four-way form is hard, the boundary is "any irreducible interaction of three or more", not a graded hard pair. If it is easy, the graded criterion stands. Either outcome decides the right general statement. Stop on a proof of the class-3 criterion or on a counterexample. Alternative: fold this dichotomy into the Rowell note (conversion, 2/3); sharing remains the owner's call. |
| Interest: beyond class 2 | **2/3: Promising** | The first discriminator has a sketched reduction to a proved case. The second is a sharp open question about four-way interactions. The main uncertainty: whether Massey forms can be steered freely on knot surgeries, and what the polynomial side looks like past class 2. |
| Execution | Deferred to the owner | This epic's assignment was the class-(K) theorem and its gaps. A new direction is the owner's decision. |
