# The corner return law on the square torus cut open

Epic `RETURN-LAW-20261110-001` (program foundations, groups `collapse` and `reach`, B138), 2026-11-10. Pre-registered in commit
a5769c7a7, before the proof attempt.

## The question

- **Where it comes from.** `REACH-HALVES-20261110-001` reduced the failure of full reach at a power of two to one even walk count from a
  corner (B137) and computed, beside it, that the corner's return series is 1/(1 + L(w⁴)) at every power of two from 4 to 128, L the
  trace polynomial of GF(2n): the quadrant's Catalan series folded modulo 2n − 1. Its report selected the return law as a theorem (B138)
  as the cheaper route toward the count, and the coordinator gave the go-ahead on 2026-11-10 at 21:58.
- **The question.** Prove the return law, in three steps registered as tickets: the quadrant's Catalan law (A), the invisibility of one
  far wall at even sides (B), and the box's law at every power of two (C); or find a side where one breaks; or state the step that
  resists, checked exactly. Judge whether the method gives a handle on the wall-reaching excursions of the count (B137).

## The question in standard terms

A is the adjacency matrix over GF(2) of the alternating medial digraph of the n × n grid with the outer face's arcs removed; in doubled
coordinates its vertices are the points (X, Y) of [0, 2n − 2]² with X + Y odd. The corner vertex is c = (0, 1) and
r(w) = Σ_k A^k[c, c] w^k. Ticket A: in the quadrant r(w) = C(w⁴), C the Catalan series mod 2. Ticket B: with one far wall removed, the
same at every even n. Ticket C: in the box at n = 2^m ≥ 4, r(w) = 1/(1 + L(w⁴)).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The column decomposition.** With at most one far wall, the corner's return series is the (0, 0) entry of (I − sD − s²f(P))^(−1), s = w², a matrix on the rows alone: P the row path, D its lowering part, f(P) the plain walk's excursion operator. So the quadrant law and the half-strip law are each one identity on a path, (★1D). | proved | A |
| 2 | **The two-sided decomposition.** In the box the same series is one entry of the inverse of a 2(n − 1) × 2(n − 1) block matrix whose blocks, at a power of two, are explicit: the row path is nilpotent, and the column path's first-passage series are quotients of truncated Catalan polynomials. The return law at each power of two is one finite identity. | proved | C |
| 3 | **The return law is proved at every power of two from 4 to 512**, by exact computation: the corner's sequence and the law's both obey linear recurrences of bounded order, and they agree on as many terms as the two orders together. | computed, exact (a proof at each of those sides) | C, stress test |
| 4 | **The looped path.** At n = 2^m, det(I + zP_n^∘) = 1 + L(z) over GF(2), P_n^∘ the path of n sites with a loop at one end. So the law says: read every four steps, the corner of the box returns exactly as the loop end of a looped path of n sites; the quadrant's is the infinite looped half-line. | proved (the restatement); the law computed | C, A |
| 5 | **The reflection through the corner** is a symmetry of the walk; mod 2 only walks whose excursions off X − Y = −1 lie on the bottom side and touch the bottom wall (or the right wall) survive. | proved | A |
| 6 | **The plain quadrant is even.** Without the corner's ban (no north step from column 0) the number of returning walks of each positive length is even; that the ban turns that 1 into C(s²) is (★1D), computed. | proved (the plain walk) | A |
| 7 | **One far wall is invisible at every even side from 2 to 80, not only at powers of two**, and seen first at 4n at every odd side to 79; with the bottom wall removed too it is seen at 4n at every side tested. The strip's four-periodic eigenvector exists exactly at even sides and four more columns act as the identity on its branch. | computed (B1, B2); proved (the eigenvector) | B, stress test |
| 8 | **The integer count.** The corner returns of length 4k in the quadrant are C_k² in number, k ≤ 24: the simple quarter-plane walks with no north step from the y-axis have as many excursions as the diagonal walks. | computed | A |
| 9 | **The box against the quadrant.** At every side 3 to 128 the box's corner series first differs from the quadrant's at time 8n; the four corners obey C_m(w⁴)/(1 + w^(2n−1)ρ) + w^(2n−3)ρ³ at 4 to 128. | computed | C, stress test |
| 10 | **For B137.** The same two-sided decomposition carries the count that decides the failure of full reach (Corollary 10, checked target by target at 4, 5, 6, 8 and 16): the return law needs one entry of the block inverse, the count needs the corner's whole row. | proved | C |
| 11 | **Not proved for every m:** the quadrant law, the half-strip law and the box law each rest on an identity of conclusions 1 and 2. | the gap | A, B, C |

## Answer

The return law is not proved for every power of two, but it is now proved at each power of two from 4 to 512 and reduced to one finite
identity per side. Cutting the corner's walks at the columns where its moves are restricted (column 0, where it cannot step north, and in
the box also the last column, where it cannot step south) turns the two-dimensional count into a matrix on the rows alone, with explicit
entries at a power of two (conclusions 1, 2). An exact finite check settles each side, and the stress test went to 512 (conclusion 3). The
law has a one-dimensional reading: every four steps, the corner returns as the loop end of a looped path of n sites, whose determinant is
1 + L(z) exactly at powers of two (conclusion 4). The quadrant and half-strip laws reduce to one identity on a path, computed and
unproved; one far wall is invisible at every even side computed (2 to 80), wider than the powers of two (conclusion 7). The planned reflection proof
does not land: the reflection through the corner is a symmetry (conclusion 5) but leaves surviving walks without a closed form. For B137,
the same decomposition carries the full-reach count, so the count and the law are now statements about one block matrix.

## Reading

**Interpretation, not a theorem.**
- **Why the trace of GF(2n).** At a power of two the row path of n − 1 sites is nilpotent over GF(2) (rule 90 on 2^m − 1 sites), and
  the looped path of n sites has determinant 1 + L(z). The trace polynomial enters through these two Chebyshev facts; nothing in the
  proof so far uses the field GF(2n) itself.
- **The corner as one particle.** The looped path is an n-state operator with exactly the corner's return series, the candidate that
  B59 asked for, and it is a quotient of the corner's orbit, not a subspace of it. Wherever the law holds, the corner's A⁴-cyclic space
  modulo the vectors that the corner never sees along their orbit is a minimal realization of the corner's sequence, so by the
  uniqueness of minimal realizations it is similar to the looped path; and since (P_n^∘)^(2n−1) = I at a power of two, a copy inside the
  orbit would force e_c A^(4(2n−1)) = e_c, which fails at 16 to 128 (the orbit's period is 2^(⌊m/2⌋+1)(2n − 1)). No explicit description
  of the quotient map is known.
- **Even, not powers of two.** The far wall's invisibility is computed at every even side to 80, not only at powers of two; what is
  special about powers of two is the folding in the box, which needs both far walls.

## Stress test

`stress_test.py` (one process, run under systemd with a 16 GB memory cap) tested the computed claims one size past their checked
ranges: C1 exactly at 512; B1 at the even sides 66 to 80 below w^3200 and B2 at the odd sides 65 to 79; A1 below w^8000; C3 at every
side 65 to 128; the four-corner formula at 128 below w^2000; Theorem 7 at 13 to 16. Results are in `stress_test.json` and
`stress_test_log.txt`. **Passed, every part, in 65 s.** The ranges above are the ones the conclusions quote.

## Literature and provenance

What the prior-work check found for the return law, for the coordinator's novelty mark:
- **1/(1 + trace polynomial).** No source found that gives a lattice walk's return series as 1/(1 + L(w⁴)), or that states
  det(I + zP_(2^m)^∘) = 1 + z + z² + z⁴ + ⋯ + z^(2^m) over GF(2). The ingredients are classical: Chebyshev polynomials and continuants
  over GF(2) and the nilpotency of rule 90 on 2^m − 1 sites (Martin, Odlyzko and Wolfram 1984; Sutner's σ-automata); the looped path's
  characteristic polynomial U_n − U_(n−1) (loop weight +1), whose roots are −2cos(2πj/(2n + 1)), j = 1, …, n, a product of minimal
  polynomials of −(ζ + ζ⁻¹) for roots of unity of order dividing 2n + 1; the trace and linearized polynomials of a finite field (Lidl and
  Niederreiter, chapters 2 and 3). The identity follows from these in a few lines, so it
  may be folklore in that literature; we did not find it.
- **The Catalan folding.** Nothing found on a return series equal to the Catalan series mod 2 (odd exactly at 2^j − 1) or to that series
  folded modulo 2n − 1. The parity of Catalan numbers is classical, and the integer count C_k² in the quadrant equals the classical count of
  diagonal walks (a product of two Dyck paths); the simple walk's own excursions are C_k C_(k+1) (Guy, Krattenthaler and Sagan 1992).
  Walks with boundary-dependent steps are studied as walks with interacting boundaries (Beaton, Owczarek and Rechnitzer, arXiv
  1807.08853), but this rule, no north step from the y-axis, and its count C_k² were not found.
- **Classification.** New as far as found, with the looped-path identity likely elementary to specialists. Not a priority claim.
- **Searches.** Bounded web searches on 2026-11-10: quadrant walks with Catalan-squared excursions; Catalan numbers mod 2 and the
  trace polynomial; Manhattan-lattice and alternating diagonal walks; Chebyshev polynomials over GF(2) and looped paths; boundary-modified
  quarter-plane models.

## Explorations (not claims)

- **Algebraic guessing.** `guess_algebraic.py` looked for an algebraic relation Σ_d c_d(s, x) A^d = 0 over GF(2) for the quadrant's
  boundary series on the h contacts (bottom row A, left column B), with degrees up to (D, ds, dx) = (4, 8, 4): none exists in that range,
  so no algebraic closed form of that size exists.
- **The kernel method.** On the h contacts the quadrant's kernel is xy + s(x + y)(1 + xy), symmetric in x and y, with group of order four;
  the boundary term s(x + y)A(x) is not of the form that the orbit sum eliminates, and the kernel curve has genus one.
- **Doubling.** M² on the v-grid is the half-scale walk with loops on the axes and an attached plain quadrant (ticket A, computed);
  eliminating the attached quadrant leaves a second identity on the half-line, of the same kind as (★1D).
- **The box's corner row.** In 𝒦_n^(−1) at 4, 8, 16 the corner's row is not paired the way the quadrant's is (entry 2k = t₀ · entry
  2k − 1); its first two entries on the last column's rows equal its last two on the first column's.

## Referee pass

An independent referee, a separate session given the files and not the conclusions, read the three proofs and their checks on
2026-11-10 before publication and recomputed with its own code: Theorem 3 over the integers against the walk itself (half-strips 2 to 5
and the quadrant, to s^16), Theorem 7 (sides 2 to 6, to s^20), Proposition 9 by direct determinants at 2 to 16, the box law exactly at
4 to 32 by determinants and at 4 to 512 with its own walk, the half-strip law at 2 to 12, C3 to 24 and the orbit periods. Verdicts: every
statement marked proved is correct, the three Obstructed statuses match the frozen criteria, and ticket C's proofs at each side from 4 to
512 stand. It found one false inference: ticket C's "What resists" said a chain on which A⁴ acts as the looped path would live in a
proper subspace of the corner's orbit, but (P_n^∘)^(2n−1) = I, so no such invariant chain exists at 16 to 128; the looped path is a
quotient of the orbit (uniqueness of minimal realizations). It also found checks weaker than their labels (ticket C's check of the
B137 count compared only the sum of the two targets; the integer checks ran against the v-grid rather than the walk itself), computed
claims without checks (the failures of the doubling relation, "other rows do not", the kernel equation and its consequences, the
survivor counts), an equivalence asserted without proof (the doubled identity), a missing citation (the second half-strip in ticket A's
corollary), and overclaims and wording (ticket A's novelty sentence on Catalan walks, ticket B's "explains", this note's "proved" on
(★1D), "every even side" and "ruled out", the looped path's polynomial and its sign, a Lidl–Niederreiter chapter, ticket B's "corner
contact" with no bottom wall, stale run times and theorem numbers in the library). All were fixed before the first commit of the
results: the passage and this note's Reading rewritten; the B137 check made target by target and the integer checks run against the
walk A itself; checks added for the doubling failures (first at w^16, w^64, w^96, w^128), the pairing to k ≤ 8 and where it fails, the
kernel equation with its factorisation and the reflection D, and the survivor counts; the kernel equation, the doubling equivalence and
Corollary 10 proved in the text; the statements narrowed. None of them touched the reductions or the computed laws.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the corner return law (B138) | **Status:** Partially successful | Proved at every power of two from 4 to 512 and reduced to one finite identity per side; not proved for every m |
| Local direction — column decompositions | Continue | The count of B137 and the law of B138 are now entries of one block matrix |
| Broader exploration — the collapse line's spectral route (G5) | Known alternatives | The looped path, a quotient of the corner's orbit, is B59's candidate operator; the spectral route stays parked |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | The power-of-two effect at the corner is a looped path of n sites, exact at every power of two to 512 |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained), no goal change; B138 taken; backlog B140 and B141 added.
**Assumptions:** none added.
**Basket:** B137 (3/3, 1/3), B74 (3/3, 1/3), B66 (2/3, 3/3); none taken, because #1 (B140) is the concrete route into B137 and waits
for the coordinator's go-ahead.

- **What the attempt leaves open.** The identities (★1D) on paths and the block identity of ticket C for every m, the integer count C_k²,
  and an explicit form of the quotient map from the corner's orbit onto the looped path.
- **What it keeps.** The decompositions apply to any count from the corner, so they carry over to B137.

**Next step:** Continue — selected: #1, awaiting the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The corner's row of the block inverse (B140, toward B137) | 3/3 — Barrier | 2/3 — Testable | Compute det 𝒦_n and the corner's row of 𝒦_n^(−1) exactly at 4 to 64 and look for a closed form in the truncated Catalan polynomials → a closed form that proves both laws for every m, or no pattern | Selected · awaiting go-ahead |
| 2 | The quadrant law as a theorem: one identity on the half-line (B141) | 2/3 — Substantial | 1/3 — Stated | Use the pairing of the corner's row and column (entry 2k = t₀ · entry 2k − 1) as an ansatz in the kernel equation → a proof of A1 and B1, or the ansatz fails | Alternative · deferred |
| 3 | An explicit quotient map onto the looped path (B59) | 3/3 — Barrier | 1/3 — Stated | Describe at 8 and 16 the corner's A⁴-orbit modulo the vectors the corner never sees → the single particle as an explicit map, or no description | Alternative · deferred |
| 4 | A short-time certificate for the other half (B139) | 2/3 — Substantial | 1/3 — Stated | Odd counts within 6.4n for every contact and ring, sides to 40 → a rule, or sides with none | Alternative · deferred |

1. **The corner's row.** Payoff 3: the count that decides the failing half of full reach (B137) and the return law (B138) both become
   finite sums over that row, so a closed form proved for every m settles both. Concreteness 2: the matrices are explicit and small
   (2(n − 1) square), the row is computable exactly, and its corner entry is the clean 1/(1 + L(s²)); whether the other entries have a
   closed form is the uncertainty. Connection to G5: the corner is where the power-of-two effect is simplest. Bound: one epic.
2. **The quadrant law.** Payoff 2: the first proof of a Catalan return law for this walk, likely carrying the half-strip law. Concreteness
   1: one identity on a path, but no method, and no algebraic relation of degree at most 4 exists for the boundary series.
3. **The looped path as a particle.** Payoff 3: one n-state object behind the corner's returns (B59). Concreteness 1: the quotient map
   exists wherever the law holds (uniqueness of minimal realizations), but nothing describes it, and it is not a subspace of the orbit.
4. **The other half.** Payoff 2 and concreteness 1, unchanged from `REACH-HALVES-20261110-001`.

**Recommendation.** Continue with #1 once the coordinator gives the go-ahead.
