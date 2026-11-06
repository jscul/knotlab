# Closure of the signed-subdivision epic

Status: Proved

Ticket `SIGNED-SUBDIVISION-20261029-001Z`, 2026-10-29. A ledger: one line per conclusion, with its novelty label and evidence. No
new claim. The decision note is `research/SIGNED-SUBDIVISION-20261029-001/signed_subdivision.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On the triangular-lattice torus, edge sign gauges (laws on all triangles) and corner sign gauges with product one (laws on up triangles) leave every fine and coarse sum unchanged; the 135,440 signed versions of the 122 rule shapes fall into 944 gauge orbits. | elementary | A-P001, Lemma 1 |
| 2 | With weights ±1, no rule shape outside the 22 counted-exact (affine) ones becomes exact, or even exact on allowed states, under shared subdivision at scale 2 (coarse sides 2–4) or 3 (sides 2–3). At scale 2 every sign pattern of the 22 keeps its allowed states, but only 28 of their 80 orbits keep their weights (always the unsigned law); at scale 3 six of the eight orbits of each twisted not-all-equal pair do. | no overlap found | A-P001, Theorem 2 |
| 3 | Every nonzero real weighting is gauge-equivalent to a sign class times one to four free positive magnitudes; positive weights have the counted supports and add no exact or support-exact shape. | elementary | B-P001, Lemma 1, Theorem 2 |
| 4 | Sign-parity obstruction: if every fine extension of a coarse-forbidden assignment uses each tuple equally often modulo 2, no real weighting cancels it. This rules out 54 of the 100 non-affine shapes at scale 2 and 34 shapes at scale 3, for every real weighting; one coherent witness per sign class adds nothing. | elementary obstruction; census new | B-P001, Theorem 3 |
| 5 | On the 22 affine shapes the exact real weightings are exactly the gauge images of the exact ±1 classes (scale 2, coarse sides 2–6; scale 3, sides 2–4). Smaller tori admit spurious exact weights: 2^(1/9) and 2^(−1/3) (parity on up triangles, sides 2–4), the golden ratio (twisted pairs, scale 3) and the reciprocal tribonacci constant (twisted pairs, scale 2) on the coarse 2-torus; larger tori remove them. | no overlap found | B-P001, Theorem 4 |
| 6 | The atoms excluding 000 or 111, with weights constant on Hamming classes, have no exact weighting on the coarse 2-torus at scale 2. | exact computation | B-P001, Theorem 5 |
| 7 | A multistart search over the gauge slice (magnitudes between 1/100 and 100), on every shape, sign class and both scales, found no exact weighting of any open shape; at scale 2 none reached a 2-torus candidate. The confirmatory reading failed its power check (2 of the 28 exact classes at scale 2 were missed by the joint stage), so it is not drawn; post hoc, the single scale-3 candidate is a degenerate cancellation point that fails on the 3-torus. | experiment, closed null (exploratory reading only) | C-E001 |

## Recommendation

**Continue**, as a fresh epic: signed not-all-equal on the level-k Sierpinski gaskets (3/3). Scoping (not evidence) finds the
law (−1)^((a⊕b)(a⊕c)) − [a = b = c] exact on every level from 2 to 11. These gaskets are finitely ramified spaces whose dimension
log(k(k+1)/2)/log k tends to 2, while the plane is excluded by this epic. The recommendation is deferred to the owner. See the decision note for the full assessment.
