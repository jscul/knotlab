# Joint records where they can matter: pre-registration

Epic `JOINT-RECORDS-20261116-001` (takes `CARRY-STRANDS-20261116-001#1`; goal G3), 16 November 2026. Frozen before the one
computation it contains. The canonical K1–K3 test is unchanged.

## The question and the stop rule

Carrying joint records of up to w distinctions through not-all-equal satisfiability and counting, where a joint record can hold
more than separate ones (unlike forcing, `CARRY-STRANDS-20261116-001`). The coordinator's stop rule: define the law, and stop as
soon as it reduces to known width-based dynamic programming or shows a gap.

**The w-record law.** A run carries at most w distinctions with their joint record (the set of allowed joint states, or for
counting the vector of counts, of the knots absorbed so far, projected onto the carried distinctions). Steps: absorb a knot all of
whose distinctions are carried; forget a carried distinction that no unabsorbed knot uses (projecting it out, or summing it out);
combine two records (join on shared carried distinctions). Phases combine records in a balanced way.

**Finding before any computation (advisor, confirming my reading).** The carried sets of a valid run form a tree decomposition of
the pattern's primal graph and every tree decomposition gives a run, so the least working w is treewidth + 1 (pathwidth + 1 without
combining): the law is bucket elimination, dynamic programming over a tree decomposition (Freuder 1990; Dechter and Pearl 1989;
Dechter 1999; for counting, Samer and Szeider 2010; the semiring view, Aji and McEliece 2000). No stage count on small weaves can
differ from the decomposition's, so none is run (it would test a tautology). By the stop rule the study closes on the proof, plus
the one table below.

## Prior work in the program

`python3 -B scripts/track.py objects "joint report two shared choices seam" --until 2026-11-16 --exclude JOINT-RECORDS-20261116-001`

`python3 -B scripts/track.py objects "treewidth pathwidth dynamic programming knot patterns counting" --until 2026-11-16 --exclude JOINT-RECORDS-20261116-001`

`python3 -B scripts/track.py objects "Pfaffian counting planar drawn knot pattern not-all-equal" --until 2026-11-16 --exclude JOINT-RECORDS-20261116-001`

- `TWO-CHOICE-IMPLICATIONS-20261115-001`: a relative (exact two-port reports for positive implications: 13 binary reports). That is
  the Horn seam; this study's seam is not-all-equal's.
- `GUARD-CHOICE-SEPARATION-20261115-001`: a relative, the Codex seam finding (separate bit supports on two shared choices miss a
  contradiction: {10} against {00, 01, 11}). That pair is not closed under flipping every value, so it cannot arise in pure
  not-all-equal patterns; this study gives the not-all-equal seam hierarchy instead.
- `SWAPPED-ROUTE-GROUPING-20261115-001`: unrelated (branch orders of the route family).
- `RANDOM-FATES-20261112-001`: unrelated (bonds in growth; matched on general words).
- `SHORT-DESC-20261112-001`: unrelated (fates of short-description patterns).
- `SUBST-NEST-20261112-001`: unrelated (distinction substitution).
- `NEST-READ-20261112-001`: unrelated (self-nested patterns).
- The program's counting results on drawn knot patterns (`HANDLE-COUNT-20261106-001`: counting fixed-parameter tractable in the
  number of handles through Pfaffians) are the known escape from width that this study cites.

## The one computation and its expected values (frozen)

Every seam report of s shared distinctions in a not-all-equal pattern is closed under flipping every value, and every such
relation is one (not-all-equal's polymorphisms are the projections and negation). `seam.py` lists the complement-closed relations
on s = 1, 2, 3, 4 distinctions and counts those determined by their two-place shadows, and, at s = 4, by their three-place shadows.
It also counts not-all-equal colourings of the tetrahedron, octahedron and icosahedron by a record-carrying run, against brute
force, as a check of an implementation of the law.

| # | Expected (advisor's hand count where given) | Fails when |
| --- | --- | --- |
| S1 | complement-closed relations: 2, 4, 16, 256 at s = 1, 2, 3, 4 (2^(2^(s−1))) | any differs |
| S2 | determined by two-place shadows: 2, 4, 12 at s = 1, 2, 3; the 4 failures at s = 3 are not-all-equal and its three single-flip variants, all knots | any differs |
| S3 | at s = 4, some relation is not determined by its three-place shadows (the four-place not-all-equal) | none found |
| S4 | colourings by a record-carrying run equal brute force: 6 (tetrahedron), 18 (octahedron), 72 (icosahedron) | any differs |
