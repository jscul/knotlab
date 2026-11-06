# Closure of the class-(K) dichotomy epic

Status: Proved

Epic `CLASSK-DICHOTOMY-20261026-001` closed on 2026-10-27.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/CLASSK-DICHOTOMY-20261026-001/dichotomy.md`. It holds the outcome, the steps, the challenged
  assumptions, the literature, the precise gaps and the end-of-epic assessment.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Take p odd, r \| p − 1 and any class-(K) group. On r-surgeries whose triple product is a gadget tensor (three slot patterns), the count is a positive sum over k ∈ Z/r of multiplicative partition functions. Their weights W_k = \|K₂\| \|K₃\| p^{−rank} are positive and even, and have rank one exactly when the three pairings vanish. A hard pair makes W₁ nonconstant; without one, every W_k is constant. | Bookkeeping over standard tools. Folklore risk medium | `CLASSK-DICHOTOMY-20261026-001A-P001` |
| 2 | The projector construction realizes the gadget tensors of all three patterns at (7, 6) and (5, 4). Across 8 surgeries and 108 group-by-fixture comparisons, every sector count equals its frozen prediction, on closed surgeries and knot exteriors. | Experimental support for the realization step | `CLASSK-DICHOTOMY-20261026-001B-E001` (supported) |
| 3 | With a hard pair, counting into a class-(K) group is #P-hard (Turing) on r-surgeries of knots (H₁ = Z/r). The steps are anchor isolation over disjoint unions, then Bulatov–Grohe. With `COPRIME-CLASS2-20261026-001C`, this is a dichotomy for closed 3-manifolds with \|H₁\| ≤ C: polynomial iff no G_d (d \| r, d ≤ C) has a hard pair. | Candidate new. Folklore risk medium | `CLASSK-DICHOTOMY-20261026-001C-P001` Theorem C, Corollary D |
| 4 | The same dichotomy holds for knot groups, including commutators with the trivial character: the u-pairing is unchanged by the moves and block-diagonal, so the count splits into multiplicative (k, β) terms. So Rowell's Conjecture 3.2(b) fails for every class-(K) group with a hard pair over odd prime fields, unless every #P function is polynomial-time computable. | Candidate new. External confirmation needed | `CLASSK-DICHOTOMY-20261026-001C-P001` Corollary E; `CLASSK-DICHOTOMY-20261026-001B-E001` |

## Challenged assumptions

The decision note records four:
- **Sector isolation needs GGJT Lemma 6.4.** Replaced by anchor isolation.
- **Knot groups need κ_{1,σ} = 0.** Not needed.
- **The Heisenberg Potts gadgets are the mechanism.** They are special cases of the Bulatov–Grohe weight.
- **Hardness holds for every bound on |H₁|.** Refined by the orders of the subgroups.

## Remaining gaps

1. p = 2.
2. Extension fields.
3. Groups outside class (K).
4. Cited, not reproved: Bulatov–Grohe and the clasper calculus.
5. Approximate counting.
6. No external review.

## Recommendation

**Continue, with a fresh epic beyond class 2.**
- **First discriminator** (expected hard): a class-3 group with no class-2 hard pair but a cross-layer hard pair, which reduces to the
  Heisenberg pattern-2 count.
- **Second discriminator** (open): a four-way triple-Massey interaction on characters α, α⁻¹, γ, γ⁻¹ with no graded hard pair.
- **Interest:** 2/3.
- **Alternative:** fold the dichotomy into the Rowell note (2/3).
- **Execution:** deferred to the owner.
