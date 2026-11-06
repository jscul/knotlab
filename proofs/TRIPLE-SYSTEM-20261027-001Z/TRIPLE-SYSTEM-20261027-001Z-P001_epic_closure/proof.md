# Closure of the triple-system epic

Status: Proved

Epic `TRIPLE-SYSTEM-20261027-001` closed on 2026-10-27.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/TRIPLE-SYSTEM-20261027-001/triple_system.md`. It holds the outcome, the steps, the
  challenged assumptions, the literature, the gaps and the end-of-epic assessment.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Take p odd and N of exponent p and class c < p with an involution. If the Lie triple system 𝔫⁻ is abelian, then on every group with H¹ and H² with F_p coefficients zero the count over ψ is \|Z¹(F_p^ψ)\|^{dim 𝔫⁻}, and every homomorphism lies in exp(𝔫⁻ + [𝔫⁻, 𝔫⁻]) ⋊ ⟨θ⟩. So counting is polynomial on closed 3-manifolds with H₁(M; F_p) = 0, in every class. | Candidate new; folklore risk medium | `TRIPLE-SYSTEM-20261027-001A-P001` |
| 2 | On gadget surgeries the obstruction is the degree-3 Lie part of the cable conjugators on all free −1 classes, exactly, for six nonabelian triple systems of class 3 and 4 at p = 5, 7, 11. Bases and abelian systems never obstruct, and an independent matrix model and group-law count agree. | Experimental support | `TRIPLE-SYSTEM-20261027-001B-E001` (supported) |
| 3 | For graded algebras of class at most 4 (p ≥ 5), a nonabelian triple system makes counting #P-hard on 2-surgeries of knots. With 1: at r = 2, counting is polynomial iff the triple system is abelian. | Candidate new; folklore risk low to medium | `TRIPLE-SYSTEM-20261027-001C-P001` |

## Challenged assumptions

The decision note records three:
- **Higher-layer odd trees add new hard cases.** No: deeper free classes act as further −1 elements.
- **The trivial-character test needs a new argument.** No: the rigid count covers it.
- **Explicit symmetric-power constructions are needed.** No: one-parameter subgroups suffice.

## Remaining gaps

1. Class at least 5.
2. Non-graded algebras.
3. p = 2 and p = 3.
4. r > 2.
5. p-torsion in H₁.
6. Knot exteriors.
7. Cited, not reproved: Bulatov–Grohe, Lazard, Dynkin–Specht–Wever and the previous epic's gadget calculus.
8. No external review.

## Recommendation

**Continue, with a fresh epic: the general coprime dichotomy for every r.**
- **Conjecture:** polynomial iff brackets of nontrivial characters with nontrivial product vanish, both pairs and the triples
  [[𝔫_χ, 𝔫_χ⁻¹], 𝔫_η].
- **Interest:** 2/3.
- **Alternative:** class at least 5 at r = 2.
- **Execution:** deferred to the owner.
