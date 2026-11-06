# Closure of the signed-gaskets epic

Status: Proved

Ticket `SIGNED-GASKETS-20261029-001Z`, 2026-10-29. A ledger: one line per conclusion, with its novelty label and evidence. No new
claim. The decision note is `research/SIGNED-GASKETS-20261029-001/signed_gaskets.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Signed not-all-equal, w(a, b, c) = (−1)^((a⊕b)(a⊕c)) − [a=b=c], equals (−1)^a times the Legendre symbol of a+b+c modulo 3, the standing wave (−1)^a sin(πE/3)/sin(π/3) of two sixth-root phases, and the multiplication of the Eisenstein field in the basis of primitive sixth roots. | elementary | A-P001, Lemma 1 |
| 2 | On the level-k Sierpinski gasket (copies on the k(k+1)/2 up triangles of a k-subdivided triangle), the corner relation of signed not-all-equal is λ_k w for every k ≥ 1, with λ_k an integer congruent to (−1)^⌊k/2⌋ modulo 3, hence nonzero; the proof splits each copy into two phase sectors locked along the gasket's edges, with an odd global flip, and reduces modulo 3 to even edge sets of a grid. | no overlap found | A-P001, Theorems 2–3 |
| 3 | The same identity holds for every (−1)^a sin(θE)/sin θ (sin θ ≠ 0); only θ ≡ ±π/3 gives a knot; so signed not-all-equal builds exact towers of every level k, of similarity dimension log(k(k+1)/2)/log k, whose corner relation's support is a knot (K1–K3). | no overlap found | A-P001, Theorem 2, Corollary 4 |
| 4 | Among the 1,168 signed three-bit laws, 68 are exact on some level-k gasket with 2 ≤ k ≤ 12: 26 in families proved for every k (rotations of signed not-all-equal at every k; their relabelings by position parity at odd k; (−1)^a [NAE] at k ≡ 1, 2 mod 4, with nonzero factor checked to k = 22; its relabelings at k ≡ 1 mod 4; unsigned parity at powers of 2 by Lucas's theorem), and 42 sporadic (30 three-excluded laws at k = 3 only, 12 not-all-equal laws at k = 5 only). | census new; parity classical | B-P001 |

## Recommendation

**Continue**, as a fresh epic: the standing-wave law in every dimension (3/3). The sector proof does not use the dimension. Scoping
(not evidence) finds the four-place law (−1)^a sin(θE)/sin θ exact on the level-2 and level-3 Sierpinski tetrahedra at four angles.
There it vanishes exactly on the tuples with two ones, so every member is a knot (knotlab: minimum width 4). The recommendation is
deferred to the owner. See the decision note for the full assessment.
