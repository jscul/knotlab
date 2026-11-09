# Closure of full reach on the cut-open torus: the proof

Status: Proved

Ticket `FULL-REACH-PROOF-20261108-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/FULL-REACH-PROOF-20261108-001/full_reach_proof.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The cut-open torus walk and its transpose add up to T ⊗ T, the product of two null-boundary path walks (rule 90) on 2n − 1 sites. | new as far as found; proved | A (Theorem 1) |
| 2 | The quarter turn commutes with the walk; the mirror and the diagonal reflection carry it to its transpose, so reach is symmetric under them. | new as far as found; proved | A (Theorem 2) |
| 3 | The walk is the uncut torus's walk with the two cut lines deleted; its walk counts are the torus's corrected through a 2n × 2n cut-line matrix. | known-with-delta (Schur complement); proved | A (Theorem 3) |
| 4 | At powers of two the uncut torus's walk dies after n steps, each cut line carries a circle's Green's function, and the whole spectrum is det R_CC(w), a 2n × 2n polynomial determinant. | new as far as found; proved | A (Theorem 4) |
| 5 | At every side, the characteristic polynomial of two steps on h is an (n − 1) × (n − 1) determinant of Chebyshev polynomials over GF(2). | new as far as found; proved | A (Theorem 5) |
| 6 | When A⁴'s polynomial on a layer is irreducible of full degree, every contact reads every contact; this happens at 3, 5, 7, 11 and at no other side to 24. | new as far as found; proved, the sides computed | A (Proposition 6) |
| 7 | Among sides 3 to 64, every eigenvalue is a (2n − 1)-th root of unity exactly at 4, 8, 16, 32 and 64, with multiplicities k(k + 1)/2 there. | new as far as found; computed, exact | A (checks 9, 10, 12), stress test |
| 8 | Full reach failing exactly at the powers of two from 8 is not proved; the census pattern holds wherever read. | open | the decision note |

## Answer

The theorem is not proved; at powers of two it is reduced to one 2n × 2n determinant on the cut lines, where the spectrum collapses
into GF(2n), exactly at powers of two to side 64.

## Recommendation

**Continue**, selected #1 (the collapse at every power of two), deferred while the tie-law epic runs first. The table is in the decision
note.
