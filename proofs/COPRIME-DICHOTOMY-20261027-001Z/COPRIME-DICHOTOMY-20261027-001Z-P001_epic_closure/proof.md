# Closure of the coprime-dichotomy epic

Status: Proved

Epic `COPRIME-DICHOTOMY-20261027-001` closed on 2026-10-27.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/COPRIME-DICHOTOMY-20261027-001/coprime_dichotomy.md`. It holds the outcome, the steps, the
  challenged assumptions, the literature, the gaps and the end-of-epic assessment.
- **The consolidated, corrected presentation** for independent review is `presentation.md` in
  `COPRIME-DICHOTOMY-20261027-001D-P001`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For p odd, N of exponent p and class c < p, and C_r acting with r \| p − 1: (P2_d) holds iff the C_d action collapses to an involution θ_d that is an automorphism. With (P3_d), the count over a sector of order d is Π_{α≢0} \|Z¹(F_p^{αψ})\|^{dim 𝔤_α}, every homomorphism lies in a class-2 subgroup, the criterion passes to divisors, and no grading is needed. So counting is polynomial with boundedly many sectors. | Candidate new; folklore risk medium | `COPRIME-DICHOTOMY-20261027-001A-P001` |
| 2 | At characters of order d ≥ 3: slope d/p removes cross-summand channels (exact counts multiplicative, unlike slope d/1). Local Massey forms vanish on negative amphichiral knots and on (k,1)-cables of T(2, p), while chiral knots obstruct. The steering rule with κ_t = t⁻² − t⁻¹ and d-strand bundles is exact on 48 insertions and 10 gadgets. | Experimental support | `COPRIME-DICHOTOMY-20261027-001B-E002` (supported; E001 crashed before a verdict and is kept as invalid) |
| 3 | For graded 𝔫 of class at most 4 and p ≥ 5: under (P2_d) only near triples can fail. If (P2_d) holds and (P3_d) fails, counting on S³_{d/p}(K) is #P-hard, at every sector order d. | Candidate new; folklore risk medium | `COPRIME-DICHOTOMY-20261027-001C-P001` |
| 4 | Consolidated presentation. Theorem A; hardness for class 2, for triples under pairs, and for the cross-layer pair. Corollary C: the dichotomy for graded class ≤ 4, open only for pair failures in classes 3 and 4. Incorporated: the reversed Artin identity, the sector-count assumption, the per-group anchor lemma and the interpretation boundary. Frozen predecessors are unchanged. | Consolidation | `COPRIME-DICHOTOMY-20261027-001D-P001` |

## Challenged assumptions

The decision note records five:
- **Channels at r > 2 are intrinsic.** No: slope d/p removes them.
- **Local terms are unavoidable.** No: summand choice removes them.
- **Amphichiral summands suffice everywhere.** No: they reach square roots only, and cables cover even orders.
- **Far triples are a separate case.** No: Jacobi kills them under (P2_d).
- **The r = 2 machinery is special to t = −1.** No: J_t and κ_t generalize it.

## Remaining gaps

1. Pair failures in classes 3 and 4 (the residual family of Corollary C).
2. Class at least 5.
3. Non-graded algebras; p = 2 and p = 3; p-torsion in H₁; unbounded sectors; knot exteriors beyond class (K).
4. Cited, not reproved: Bulatov–Grohe via Cai–Chen–Lu, Lemma I, Lazard, Schur–Zassenhaus, Schubert, the satellite formula,
   universal coefficients over Λ, and the clasper results behind the class-(K) route.
5. No external review of the new results (A at every r; C for d ≥ 3).

## Recommendation

**Continue, with a fresh epic: pair failures in classes 3 and 4.**
- **First discriminator.** The inert reduction, and a non-inert example: free class 3 on (a, a) at d = 4 or 5.
- **Interest:** 2/3.
- **Alternative:** class at least 5.
- **Execution:** deferred to the owner.
