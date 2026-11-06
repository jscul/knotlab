# Closure of the coprime-pairs epic

Status: Proved

Epic `COPRIME-PAIRS-20261027-001` closed on 2026-10-27.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/COPRIME-PAIRS-20261027-001/coprime_pairs.md`. It holds the outcome, the steps, the challenged
  assumptions, the literature, the gaps and the end-of-epic assessment.
- **The corrected presentation** of the predecessor's results is `presentation.md` in `COPRIME-PAIRS-20261027-001B-P001`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The triple-hardness proof, reissued after an independent AI review: the literal Fox matrix t⁻¹(Bur_t − I), the integer cable exponent, the actual edge weights, and "(P2) supplies a compatible parity automorphism"; pinned coordinates and reading strands expanded; precise references. | Correction | `COPRIME-PAIRS-20261027-001A-P001` |
| 2 | The corrected presentation of the coprime dichotomy, with every review recorded as an independent AI review with finite V2 checks. | Consolidation | `COPRIME-PAIRS-20261027-001B-P001` |
| 3 | On closed 3-manifolds without F_p-homology, maps over a sector of order d land in exp(𝔪_d) ⋊ C_d, where 𝔪_d is the ideal of the nonzero characters. Hardness transfers from any quotient with a pinned surgery family whose knots avoid the kernel's characters, with the total count recovered by Lemma I. Decides 153 residual census algebras. | Candidate new; folklore risk high (Theorem 1) and medium (transfer) | `COPRIME-PAIRS-20261027-001C-P001` |
| 4 | Gadget behaviour on five interacting algebras: maximal diagonal, deficient pair-failing differences, vanishing vertex pairings, path locality on the solution variety. E001 was refuted by an off-variety locality rule; the successor reproduces that failure as a control. | Experimental support | `COPRIME-PAIRS-20261027-001D-E002` (supported; E001 refuted and kept) |
| 5 | Interacting pair failures with a clean edge are #P-hard: zero-jump gadget knots, locality on the layer-2 variety, the Brunnian rank lemma, subdivision. A character-0 refinement adds 5 algebras (55 in all). The open algebras are classified by their failing conditions, and (K) and (V₃) are shown to be real vertex couplings. | Candidate new; folklore risk medium | `COPRIME-PAIRS-20261027-001E-P001` |
| 6 | When an edge fails only the vertex-root condition, its vertex equations are a conserved flow. If the flow vanishes off the diagonal and is bilinear on it, the Fourier dual has non-negative weights and the count is #P-hard. Decides 8 more algebras; 113 of 850 census algebras stay open. | Candidate new; folklore risk medium | `COPRIME-PAIRS-20261027-001F-P001` |

## Challenged assumptions

The decision note records these:
- **Higher layers at the gadget characters break the class-(K) route.** Only when their couplings are non-local.
- **Pair failures need parity for the steering to be clean.** No: on the layer-2 variety the pair steering is central.
- **The class-2 quotient must carry the hard pair.** Not after the trivial-character reduction.
- **An edge count is local if its equations ignore distant data.** Only on the joint solution variety, which is all the count needs.
- **Vertex conservation laws block the spin-system reduction.** Not when the flow lives on the diagonal and is bilinear there.

## Remaining gaps

1. The 113 open census algebras: (B₀); (B₁′)/(B₂′) at nonzero characters; vertex-root flows where (F0) or (F1) fails; class-4
   couplings (K), the largest family (26 algebras fail only that); and one cross-layer algebra (free class 4 on (a, −a) at order 3).
2. Class at least 5; non-graded algebras; p = 2, 3; knot exteriors at d ≥ 3; unbounded sectors.
3. The census covers free algebras on at most three generators with d ≤ 12.
4. Cited, not reproved: Bulatov–Grohe via Cai–Chen–Lu, Lemma I, the predecessor's summand and steering lemmas.
5. No human or external review of the phase-2 results.

## Recommendation

**Continue, with a fresh epic: class-4 locality and flows.**
- **First discriminator.** Path locality on the full solution variety for free class 4 on (a, a) at d = 5.
- **Interest:** 2/3.
- **Alternative:** class at least 5.
- **Execution:** deferred to the owner.
