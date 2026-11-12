# What the law reads on travelling bases: pre-registration

Epic `TRAVEL-READ-20261112-001` (`COMMON-FOLD-20261112-001` direction 1; G1 with G17, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead. Committed before the registered run. The canonical K1–K3 test is unchanged. The advisor
model was consulted on the design before freezing (what it changed is listed below).

## Words

The glossary's and `COMMON-FOLD-20261112-001`'s: knot kind, travels along a shift, a travelling base, tied along a shift, bond, bond
distance, unlengthened shift, along-count, across-count, heddle. In this record:

- **Frame.** For a travelling shift t, t' = t divided by the greatest common divisor of its entries, and u the shortest vector with
  det(t', u) = 1; a distinction a t' + b u has along-count a and across-count b.
- **Rank.** The rank of the set of directions (t reduced to t') along which some certified pattern travels: 1 when all are parallel
  (labelled rank ≥ 1 below: one direction found), 2 when two are independent.
- **Window bond.** A set refuted in some pattern on a finite window (sound) none of whose proper parts is refuted in that window in any
  pattern. It is **certified** when every proper part is also carried in every pattern by a doubly periodic state. A window bond is a
  bond up to the window: "not refuted in the window" is not a certificate.
- **Cross profile.** On a rank-1 base, b(α, y): the least size of a window bond holding the origin and the distinction α along and y
  across, with the rest of it in one cross-section (the origin's along-count) or in two.

## The question

On the travelling bases of the COMMON-FOLD census (random periodic bases where a bounded set decides distinctions arbitrarily far
along a shift), what does the law read? On base 16 it reads no length along the shift and one dimension across, bond distance growing
by one per two across-counts. Is that typical? How many bases have a second unlengthened shift, and what do those read?

## The question in standard terms

For random periodic 3-uniform hypergraphs on ℤ² under proper 2-colouring that have a finite pattern forcing its own translate:
the rank of the set of such translation directions; and the least size of minimal non-shattered sets (up to a window) containing the
origin and a far vertex, as a function of the transverse offset.

## Prior work (bounded search, with the advisor's list, to verify)

Expansive subdynamics and directions of determinism (Boyle and Lind 1997; Guillon, Kari and Zinoviadis; Cyr and Kra; Kari and
Szabados on Nivat's conjecture); Ledrappier's shift and algebraic actions, deterministic in many directions with sparse bounded
relations (Kitchens and Schmidt; Einsiedler, Lind, Miles and Ward); stable directions in bootstrap percolation, where a finite set's
closure is infinite along a line or a cone (Bollobás, Smith and Uzzell), the closest analogue of rank 1 against rank 2; extender sets
and topological strong spatial mixing (Ormes and Pavlov; Briceño). None found that gives the typical cross profile in random families.

## What is settled by definition or by proof (checks)

- Bond distance is bounded along every travelling direction (COMMON-FOLD's lemma). A pattern travels if and only if its complement
  does; t travels implies every positive multiple does, so directions are reduced to t' before the rank.
- d(0, v) = d(0, −v), so a profile is read at a fixed sign of the along-count; both signs of y are informative.
- If one certified pattern travels along two independent shifts ("common pattern"), translation and complement symmetry give ±p on
  A + m t₁ + n t₂ for all m, n ≥ 0, so bond distance is bounded on that cone and its mirror.
- **The control.** Base 16 must reproduce its theorem: one cross-section b(10, y) = 4, 5, 5, 6, 6 for y = 2 to 6 and none for
  y = −3 to −6 (Theorems L, C, D of `ACROSS-FOLD-20261112-001`), b(14, 3) = 5, and with two cross-sections the referee's bonds of 5
  at y = −3, −4. Checked before freezing: it does (the bonds at y = 5, 6 and downward are window bonds, not torus-certified: doubly
  periodic states cannot carry two of the sixteen patterns of a heddle part, so certification needs states that repeat along no
  step).

## Disclosed before freezing

A pilot on the travelling bases of the census's unregistered seeds 900 to 939 at r = 4, 5 (about 25 bases), with the frozen code:
- **Rank.** Two independent travelling directions in 16 of 28 travelling bases at r = 3 to 6 (a first pilot), and in about half at
  r = 4, 5; two bases travel along all ten shifts.
- **Rank-1 profiles differ from base 16.** Of 7 rank-1 bases, 5 had b(10, y) = 4 at every y from −6 to 6 (bounded across: no growth),
  and 2 had 4 to 5 with at most one step; none grew like base 16. Some of these bonds are torus-certified (for example a set of three
  at across-counts 0, −2, 1 reaching across-count 6), others are window bonds only.
- **Rank-2 rings.** Window bonds of 2 to 5 to most targets on the rings of radius 3 and 6, the radius-6 values no larger than the
  radius-3 ones; a few targets unreached by sets of at most four in the 3 × 3 box.
So the pilot suggests that base 16's one dimension across is rare among travelling bases, and that most read zero dimensions in the
measured range. The predictions test this on the registered bases.

## The census (frozen in `experiments/TRAVEL-READ-20261112-001A/`)

Samples: every base classed "travels" at r = 3 to 6 in `artifacts/COMMON-FOLD-20261112-001A/.../main.json` (sha256 pinned in the
contract): 33, 55, 53 and 28 bases. Parts: `dirs` (all), `cross` (rank 1), `rings` (rank 2), `control`; each base in its own
process, written as it finishes, capped at 1,200 s and recorded as dropped beyond it.

**Predictions.**
- **T1, rank.** Among travelling bases at r = 4 and 5 together, rank 2 is at least 40% (Wilson lower bound at least 30%), and at least
  20% have rank 1.
- **T2, flat across.** A rank-1 base is **flat** when, in one cross-section, b(10, ±6) − b(10, ±2) ≤ 1 in every direction where both
  are defined and at least one direction is defined to ±6; a **line** when the difference is at least 2 in some direction (base 16:
  2 upward); else **open**. Among decided rank-1 bases, at least half are flat and at most 20% are lines.
- **T3, along does not matter.** b(14, ±3) = b(10, ±3) wherever both are defined, in at least 90% of the cases.
- **T4, rank 2 reads zero dimensions.** For at least two thirds of rank-2 bases, at least 80% of the ring-6 targets are reached and the
  largest b reached on ring 6 is at most the largest on ring 3.
- **Validity.** The control holds; at most 20% of bases dropped.

**Failure criteria.** T1 fails if rank 2 is below 40% (or its lower bound below 30%) at r = 4, 5; T2 fails if fewer than half of the
decided rank-1 bases are flat, or more than 20% are lines (then base 16's line would be common, against the pilot); T3 fails below
90%; T4 fails below two thirds. Each failure is reported as such.

## Decision rules

- **T1 to T4 hold:** on typical travelling bases the law reads zero dimensions (bond distance bounded along and across, within the
  measured range), base 16's line being a rare case; the middle regime's geometry is mostly collapsed, not one-dimensional.
- **T2 fails with many lines:** base 16's one dimension across is common among rank-1 bases.
- Every claim of boundedness is within the measured range (|y| ≤ 6, α ≤ 14, rings to radius 6) and at window level; certified shares
  are reported.

## Changed by the advisor's critique

Exhaustive enumeration in the strip instead of a beam over travelling sets (which bounded reach, not bond distance, and could force
the slope it measured); two along depths (α = 10, 14); "rank ≥ 1" labelling; directions reduced to primitive vectors; the common
pattern noted as settled; rings and quadrants for rank 2; failure criteria per base and overall.

## Overlap with the other line

Base 16's control shows that freeness near a travelling set needs states repeating along no step (doubly periodic states miss two of
sixteen patterns); the corner-knot line found that corner-shaped knots unlock only through such states. The two may meet here.

## Stop rule and runtime

One registered run of each part (about 10 minutes on 6 workers in the pilot's timing); hand-off to the referee thread; report.
Registered in `docs/LONG_RUNNING.md`, run under `systemd-run --user -p MemoryMax=16G -p MemorySwapMax=0`, each base saved as it
finishes.

## Workspace assumptions

- **Relied on.** A64, A67, A71, A74, A76.
