# Closure of the simplex-gaskets epic

Status: Proved

Ticket `SIMPLEX-GASKETS-20261029-001Z`, 2026-10-29. This is a ledger: one line per conclusion, with its novelty label and evidence.
It makes no new claim. The decision note is `research/SIMPLEX-GASKETS-20261029-001/simplex_gaskets.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For every dimension d, level k and complex y, the standing wave w^(y) = (−1)^(x₀) U_(E−1)(y/2) reproduces itself on the level-k Sierpinski d-simplex with factor λ_(d,k)(y). At y = 2 cos θ the wave is (−1)^(x₀) sin(θE)/sin θ, with E = Σ(−1)^(xᵢ). The proof locks the phase sectors along the d edges from the base corner and uses an odd global flip. | no overlap found | A-P001, Theorem 2 |
| 2 | λ_(d,k) is a monic integer polynomial in y = 2 cos θ, of degree d(#T − 1), with λ(2) = 2^N. The reason: the limit law 1 + Σ s₀sᵢ has as its only even edge sets the empty set and the d axis paths. At level 2, λ = y^d (y² − 2)^(d(d−1)/2). Hence there are finitely many exceptional angles, none at θ = jπ/q with q an odd prime power, and the Legendre factor is ≡ (−1)^N (mod 3). | no overlap found | A-P001, Theorem 3, Lemma 4, Corollary 5 |
| 3 | For d ≥ 2 and sin 2θ ≠ 0, the support of w_θ is a knot (K1–K3) exactly when d is odd, or θ = jπ/q with q odd and q ≤ d + 1. So the Legendre law (−1)^(x₀)(E \| 3) is an exact knot in every dimension, and in odd d there is a continuum of exact knots. They build finitely ramified towers of similarity dimension log C(k+d−1, d)/log k, increasing to d. | criterion elementary; geometry classical | A-P001, Proposition 6, Corollary 7 |
| 4 | The cosine wave (−1)^(x₀) cos(θE) reproduces itself exactly when the number of simplices is odd; otherwise its corner relation is the sine wave. The parity twist exchanges the two families in even d and maps sine waves to sine waves in odd d. In d = 2 this is the period-4 family of `SIGNED-GASKETS-20261029-001B`. | no overlap found | B-P001, Theorem 1 |
| 5 | Both waves fail at θ = π/4 at every even level in every dimension d ≥ 2, through phase frustration along the edges between non-base corners. In the factors computed (d = 2, k ≤ 8; d = 3, k ≤ 5; d = 4, k ≤ 3), the only rational exceptional angles are π/2 and π/4; all others are irrational multiples of π. | no overlap found | B-P001, Theorem 2, Proposition 6 |
| 6 | Even parity is exact exactly at powers of 2 in every dimension, and odd parity there only in even dimension (Lucas). Complement, and at odd k the non-base flip, preserve exactness. | classical / elementary | B-P001, Lemma 3, Theorem 4 |
| 7 | Of the laws f(x₀, ones among the other corners) with weights in {−1, 0, 1}, 75 of 3,280 are exact on some Sierpinski tetrahedron of level 2 to 5, and 75 of 29,524 on some four-simplex of level 2 or 3; 13 and 8 of them are knots. The families account for all but 6 and 2 sporadic knots. The knots exact at every computed level are exactly standing waves. | census new | B-P001, Theorem 5 |

## Recommendation

**Continue**, as a fresh epic: interference in three dimensions (2/3).
- **The action.** A census of signed bit laws on the edges of ordered triangulations under the 2–3 and 1–4 moves.
- **The question.** Do signs let bits see more of a three-manifold than mod-2 cohomology, and does anything beyond twisted
  Dijkgraaf–Witten appear?
- **Status.** Deferred to the owner. The decision note has the full assessment and the alternatives.
