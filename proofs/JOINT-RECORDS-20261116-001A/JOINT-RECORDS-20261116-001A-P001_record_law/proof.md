# The w-record law is width-based dynamic programming

Status: Proved (refereed: `JOINT-RECORDS-R1`, confirmed, no fix)

Ticket `JOINT-RECORDS-20261116-001A`, 16 November 2026. Written by Claude; the advisor model was consulted before the freeze and
agreed with the reduction, corrected three statements and proposed the seam table. `seam.py` beside this file computes the table
and checks one implementation of the law. Labels: **known**, **known-with-delta**, **local**. No claim about P versus NP.

## The law

For not-all-equal (NAE) knot patterns, a run of the **w-record law** carries at most w distinctions with their joint record: the
set of joint states, or for counting the vector of counts, allowed by the knots absorbed so far, projected onto the carried
distinctions. Its steps: *absorb* a knot all of whose distinctions are carried; *forget* a carried distinction that no unabsorbed
knot uses (project it out, or sum it out); *combine* two records, joining them on their shared carried distinctions.

## Theorem 1 (the reduction)

The carried sets of a valid run form a tree decomposition of the pattern's primal graph (distinctions adjacent when they share a
knot), and every tree decomposition of width w − 1 gives a valid run. So the least w with which the law decides or counts a pattern
is its treewidth + 1, and its pathwidth + 1 without combining.

*Status: known.* This is bucket elimination, or dynamic programming over a tree decomposition (Freuder 1990; Dechter and Pearl 1989;
Dechter 1999; for counting, Samer and Szeider 2010; the semiring view, Aji and McEliece 2000). Counting changes only the record's
entries (n-bit counts). NAE's global flip makes every record closed under complement, which saves exactly one bit. Bounded treewidth
is decided and counted in logarithmic space (Elberfeld, Jakoby and Tantau 2010); combining in O(log n) parallel stages needs width
about 3 × treewidth (Bodlaender and Hagerup 1998), the width-against-stages trade-off that plays the part the Strahler number played
for forcing.

**Consequences.** On the program's weaves (triangulated surfaces) the width is O(√n), O(√(g n)) with g cycle pairs
(Gilbert, Hutchinson and Tarjan); some weaves, such as stacked triangulations, have width 3. That no algorithm does better is
known only conditionally (under the exponential time hypothesis: Marx 2010; Dalmau and Jonsson for counting). Counting a stage count
on small weaves would only recompute a decomposition, so none is reported.

## Theorem 2 (what a seam must report)

A seam report of s shared distinctions is the projection of a pattern onto them. For NAE patterns the reports are exactly the
relations closed under flipping every value (NAE's polymorphisms are the projections and negation; known). There are 2^(2^(s − 1))
of them: 2, 4, 16, 256 at s = 1, 2, 3, 4 (`seam.py`).

- s = 1: a report says only whether the side is satisfiable. s = 2: it is one of empty, equal, unequal, free. Both are determined
  by their two-place shadows (trivially at s ≤ 2).
- s = 3: 12 of the 16 are determined by their two-place shadows. The 4 that are not are the relations excluding exactly one
  complementary pair: not-all-equal and its three single-flip variants, **all knots** (computed, K1–K3). So pairwise reports first
  fail exactly at the knots.
- s = 4: 50 of the 256 are determined by two-place shadows and 226 by three-place shadows; the four-place not-all-equal is
  determined by neither. The hierarchy never stops: at every s some report is not fixed by its (s − 1)-place shadows.

*Status: known-with-delta* (on two values, determined by two-place shadows = 2-CNF-definable = closed under majority: Montanari;
Baker and Pixley 1975; Jeavons, Cohen and Cooper 1998); the census is local.

## Where joint records escape width (all known)

- **Parity:** records are affine spaces, carried compactly at any width (Gaussian elimination).
- **Counting on drawn knot patterns:** Pfaffians (Kasteleyn; the program's `HANDLE-COUNT-20261106-001`: fixed-parameter tractable in
  the number of handles); Valiant's matchgates are the general form.
- **Deciding on a zero-pair weave:** NAE colourings of a triangulated sphere are twice the perfect matchings of the dual cubic graph,
  and by Petersen's theorem one exists, so the answer is always yes; planar NAE-3SAT is in P (Moret 1988, via Hadlock 1975). This
  escape uses no records at all.

No other gap is known, and under the law as defined none is possible, by Theorem 1.

## The connections

- **The Codex seam finding** (`GUARD-CHOICE-SEPARATION-20261115-001`): separate bit supports on two shared choices miss a
  contradiction, {10} against {00, 01, 11}. That is one-place against two-place reports, in a Horn family with guards. Its pair is
  not closed under flipping every value, so it cannot arise in pure NAE patterns, where a one-distinction report says only
  satisfiable or not. Theorem 2 is the next level of the same hierarchy: two-place against three-place, failing first at the knots.
- **The braid studies:** separate strand records lose what a joint record keeps (110 against 512 distinguishable tables). Here this
  is the separator's joint projection against its shadows.
- **Forcing against satisfiability:** atom (Horn) patterns are decided by local consistency of width 1, which is why joint records
  added nothing in `CARRY-STRANDS-20261116-001`; NAE has unbounded width (Feder and Vardi), which is why they matter here, and why
  their size grows with the seam.

## Check

`python3 -B seam.py`: S1 to S4 as frozen in the pre-registration, and counts of NAE colourings by a record-carrying run equal brute
force on the tetrahedron (6), octahedron (18) and icosahedron (72).

## Referee (16 November 2026)

`JOINT-RECORDS-R1` confirmed both theorems with fresh code (`research/JOINT-RECORDS-20261116-001/referee-R1/`). It added one check,
credited to the referee: every complement-closed relation is the projection of a not-all-equal pattern of knots with distinct
members, found by exhaustive search (all 4 at s = 2 with three hidden distinctions, all 16 at s = 3 with two), which agrees with
not-all-equal's polymorphisms being the projections and negation. It also confirmed the zero-pair correspondence (colourings are
twice the perfect matchings of the dual cubic graph) and the counts 6, 18, 72 three ways.
