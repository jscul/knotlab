# Soft crossings to hardness

Epic `SOFT-CROSS-20261031-001`, 2026-10-31.

## The question

- **The owner's request (2026-10-31).** "Yes, please continue." This approved the recommendation of `TWIST-COUNT-20261030-001`:
  - sharpen the soft crossing by repeating it and interpolating;
  - then reduce from counting on general cubic signed systems.
- **The aim.** Make the counting boundary two-sided: polynomial on Seymour's bound and along unbranched twists, #P-hard where twists branch,
  with the knot's sign class as the dividing line.
- **Intuitions targeted:**
  - the two/three boundary as emergence, in counting;
  - interference: signs that cancel.

**The evidence:**
- [A soft crossing interpolates to a sharp one](../../proofs/SOFT-CROSS-20261031-001A/SOFT-CROSS-20261031-001A-P001_a_soft_crossing_interpolates_to_a_sharp_one/proof.md)
  (A, proof with exact computations);
- [Counting under branched twists is #P-hard](../../proofs/SOFT-CROSS-20261031-001B/SOFT-CROSS-20261031-001B-P001_counting_under_branched_twists_is_sharp_p_hard/proof.md)
  (B, proof with exact computations);
- [End to end: formulas counted through certified Pfaffian instances](../../proofs/SOFT-CROSS-20261031-001C/SOFT-CROSS-20261031-001C-P001_end_to_end_through_certified_pfaffian_instances/proof.md)
  (C, finite check).

## Outcome in one paragraph

**The boundary is two-sided. On the knot's own graphs, which are Pfaffian, counting colourings is polynomial under the knot's sign class
and under every twist that does not branch, and #P-hard in general. Every junction of the hard instances is twisted on all three
branches.**
- **The soft crossing sharpens (A, proved).**
  - Repeated k times with capped plumbing, the junction of two twisted truncated-octahedron pages keeps zero turning entries.
  - Its four crossing states grow by 810000, 7506, −22518 and −432 per step. The primes 5, 139 and 3 separate them, so interpolation
    yields an exact crossover.
  - With dead caps (the cube minus an edge, whose count is always 3) and long edges, every cubic bipartite signed system's count is read off
    from counts of Pfaffian instances.
- **The source is hard (B; known).** Counting 2-colourings of 3-regular 3-uniform hypergraphs is #P-complete.
  - This is Fan and Cai's Holant([0, 1, 1, 0] | =3).
  - It is replayed here from #NAE-3SAT by merge paths of capped lines acting by (3M)^k, with absorbers through dead caps.
- **Hence #P-hardness on Pfaffian graphs under signings (B, proved).** The instances are planar hosts with trisum junctions of twisted
  pages.
- **End to end (C).** Two formulas were recovered exactly through 44 certified Pfaffian, non-planar instances, with three twisted branches
  at every one of 176 junctions.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemmas 1–4 | Dead cap; snakes, crossover-type with straight entries σ₁Λ^{k−1}; lattice condition (5, 139, 3); long edges 9^k P₊ + (−3)^k P₋. |
| A, Theorem 5 | Universality: counting on cubic bipartite signed systems Turing-reduces to counting on cubic bipartite Pfaffian graphs under signings. |
| A, Corollary 6 | K₃,₃ (never Pfaffian) counted from four Pfaffian instances, three signings. |
| B, Lemmas 1–2, Theorem 3 | Merge paths and absorbers; #col(G_k) = 2^{D/3} 9^{kD} p_Φ((−1/3)^k), p_Φ(1) = #Φ (known result, Fan–Cai 2020; independent replay). |
| B, Theorem 4, Corollary 5 | #P-hard on Pfaffian graphs under signings; with the knot's class and unbranched twists polynomial, a two-sided boundary. |
| C | The composition run end to end on two formulas, 44 certified instances. |

## Reading

- **Two twisted branches pass, three are hard.** At a trisum square, two twisted sides act as a similitude of the knot's angle when the third
  carries the knot's signs (`TWIST-COUNT`). When all three are twisted, the square becomes a soft crossing, and soft crossings compose into
  every cubic counting problem.
  - The two/three boundary reappears here as a boundary in how twists meet.
- **The hardness is interference.** The soft crossing exists because signs cancel the turning paths exactly. Repetition then lets four
  incommensurable growth rates separate the crossing states. The graph stays Pfaffian throughout, and its perfect matchings count in
  polynomial time.
- **The knot's sign class is the easy vacuum.** With the knot's own signs, counting is a determinant per piece (`SEYMOUR-COUNT`). Twists
  that run along paths stay easy; branching twists make counting universal.
- **Provenance.**
  - Interpolation and crossover simulation are standard (Valiant; Vadhan; Dyer, Goldberg and Jerrum; Cai, Lu and Xia).
  - The source hardness is Fan and Cai's (2020), found during this epic's literature check, and is replayed rather than claimed.
  - New, with no overlap found: the dead cap, the snake with its lattice condition, universality inside Pfaffian graphs, and the two-sided
    boundary on the knot's graphs.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — soft crossings to hardness | **Status:** Successful | The soft crossing sharpens inside Pfaffian graphs. Counting under signings is #P-hard there (source known, replayed), and the composition runs end to end. |
| Local direction — counting under twisted signs on the knot's graphs | Practically exhausted for the worst case | Both sides are proved: polynomial for the knot's class and unbranched twists, #P-hard in general with branched twists. What remains is refinement: no signs, parameters, approximation. |
| Broader exploration — counting on and near Seymour's bound | Known alternatives | Mapped: the bound (determinants), unbranched twists (matchgates), branched twists (#P-hard). Unmapped: unsigned Pfaffian triple systems, approximate counting, deficiency ≥ 1. |
| Long-term goal — the two/three boundary in counting | Capability gained | A two-sided boundary on the knot's own graphs. Two twisted branches pass and three are hard. The knot's sign class is the easy vacuum. |
| Next recommendation — counting on Pfaffian triple systems without signs | **Next step:** Continue, as a fresh epic. Remove the signs: replace each negated edge of this epic's hard instances by an unsigned long edge and interpolate at t = −1, where P₊ + tP₋ becomes negation. Classify unsigned Pfaffian triple systems by how their own Pfaffian class twists: none (the knot's spaces), unbranched (polynomial by `TWIST-COUNT` with σ = ∅), branched (hard in general). | It would state the boundary for plain hypergraphs, the program's native objects, with no signs supplied. Counting is easy on the knot's spaces and along their unbranched twists, and #P-hard on Pfaffian triple systems in general. |
| Interest — that recommendation | **2/3 — Promising** | The sign removal is a one-parameter interpolation, and the Pfaffian certificates of this epic should survive long edges inside planar pieces. Main uncertainties: whether the result is routine to Holant specialists (folklore risk moderate), and whether natural unsigned families with unbranched twists exist beyond the knot's spaces. |
| Execution — that next action | Deferred to the owner (fresh epic) | First discriminator: K₃,₃'s signed instances from ticket A made unsigned, counted for L + 1 lengths, interpolated at t = −1 and certified Pfaffian. Stop if a long edge breaks the certificate, or if the unsigned instances fall outside Pfaffian triple systems. |

**Recommendation.** **Continue**, as a fresh epic: counting on Pfaffian triple systems without signs (2/3). Two alternatives were
considered.
- **Approximate counting under twisted signs (1/3).** Exact counting is now settled. Approximation at degree 3 and size 3 lies between the
  known algorithmic and hardness thresholds for hypergraph colourings, but its tie to the knot is weak.
- **A write-up of the counting arc (1/3).** The arc runs Seymour's bound, then unbranched twists, then branched twists. It is coherent, but its
  source hardness is known, and the unsigned statement would make it stronger.
