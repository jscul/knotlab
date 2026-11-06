# Closure of the soft-crossings-to-hardness epic

Status: Proved

Ticket `SOFT-CROSS-20261031-001Z`, 2026-10-31. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes
no new claim. The decision note is `research/SOFT-CROSS-20261031-001/soft_crossings_to_hardness.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The cube minus an edge, unsigned, counts 3 whatever its two attachments see (a dead cap); a line with one capped leg acts by M = [[1, 2], [2, 1]] = 3P₊ − P₋. | new gadget (elementary) | A-P001, Lemmas 1, 4 |
| 2 | k junctions of two twisted truncated-octahedron pages in series, with capped plumbing, are crossover-type with straight entries σ₁Λ^{k−1}, Λ = (810000, 7506, −22518, −432), whose valuations at 5, 139 and 3 separate count vectors. | new (exact) | A-P001, Lemmas 2–3 |
| 3 | Counting colourings of cubic bipartite signed systems Turing-reduces to counting on cubic bipartite Pfaffian graphs under signings (planar hosts with trisum junctions of twisted pages); K₃,₃ recovered from four Pfaffian instances. | new (no overlap found) | A-P001, Theorem 5, Corollary 6 |
| 4 | Counting 2-colourings of 3-regular 3-uniform hypergraphs is #P-complete: merge paths of capped lines act by (3M)^k, and #col(G_k) = 2^{D/3} 9^{kD} p_Φ((−1/3)^k) with p_Φ(1) = #Φ. | known (Fan–Cai 2020, Holant([0,1,1,0] \| =3)); independent replay | B-P001, Theorem 3 |
| 5 | Counting colourings of cubic bipartite Pfaffian graphs under signings is #P-hard; the instances have three twisted branches at every junction, while the knot's class and unbranched twists count in polynomial time. | new (no overlap found; folklore risk moderate) | B-P001, Theorem 4, Corollary 5 |
| 6 | The composition runs end to end: two formulas recovered exactly through 44 certified Pfaffian, non-planar instances with branched twists at all 176 junctions. | finite check | C-P001 |

## Recommendation

**Continue**, as a fresh epic: counting on Pfaffian triple systems without signs (2/3).
- **The plan.** Remove the signs by long edges interpolated at t = −1. Then classify unsigned Pfaffian triple systems by how their own
  Pfaffian class twists.
- **Status.** Deferred to the owner. The decision note has the full assessment.
