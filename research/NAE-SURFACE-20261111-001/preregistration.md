# Does a faithful reading supply the surface? Pre-registration

Epic `NAE-SURFACE-20261111-001` (sub-goal B145, G1, question 9; program topology, group spacing), 2026-11-11, at the coordinator's
go-ahead after `KNOTS-ALONE-20261111-001`. Frozen before any run on the family below. Under challenge: A64 (counting how knots meet
at a distinction names no face), with A63 behind it. The canonical K1–K3 test is unchanged.

## The question

`KNOTS-ALONE-20261111-001` found that the not-all-equal law (NAE, weights {1, 2} on every knot) reads almost every flat surface of
knots alone faithfully, but the surface condition was given with the law. Its biased sample at V ≤ 12 found faithful non-surface
worlds only at d = 3. If no d-regular world that is not a surface is read faithfully at d ≥ 4, the surface count is a consequence of
reading the knots natively; one faithful non-surface world shows that it is an input.

## Definitions (frozen; as in `KNOTS-ALONE-20261111-001`)

- **World.** A finite set of distinctions with a set of three-element subsets (knots); connected; simple (no repeated knot);
  d-regular (every distinction in exactly d knots); read up to isomorphism.
- **Non-surface.** Not a closed triangulated surface: some co-knotted pair lies in one knot, or in three or more, or every pair
  lies in two but some link is more than one cycle (a pinched link). Each faithful non-surface world is reported with its defects.
- **Faithful.** Under NAE: some allowed state, no frozen distinction, no tie (every pair takes all four value pairs), and the
  three-place bonds (triples with free pairs that do not take all eight patterns) exactly the world's knots. Computed by the frozen
  `read_law_sat` of `KNOTS-ALONE-20261111-001A-E001`, whose hash is checked against that epic's contract before use.

## Settled before the run

Nothing that decides a prediction. By definition a faithful world's knots are recovered from its allowed states, so its complex is
read natively; whether that complex is a surface is the open question. No local configuration is known to force a tie or an extra
three-place bond under NAE: a pair in three knots forces its third distinctions to the other value when the pair is equal, and the pair
to differ when two of them differ, which fixes no pattern on three distinctions by itself; and a pinched link gives the
four-element bonds that surfaces have too.

## Families (frozen)

- **F0, exhaustive.** Every connected simple d-regular world on 6 distinctions, d = 4, 5, 6, 7 (all subsets of the 20 triples,
  isomorphism by all 720 relabellings).
- **F1, a random sample.** For d = 4 to 7 and every V from 13 to 30 with 3 | dV, 40 connected simple d-regular worlds by the frozen
  generator `random_regular_worlds_sat` (SAT with random phases), seed 20261112 + 100 d + V, surfaces removed. Biased; for existence.
- **F2, swaps of faithful flat tori.** Every lattice torus with 24 to 48 distinctions of edge-width at least 5 that NAE reads
  faithfully; from each, worlds made by k = 1, 2, 4 degree-preserving swaps (two disjoint knots {a, b, c}, {x, y, z} become
  {a, b, z}, {x, y, c}), two replicates each, seed 20261113 + 1000 n + 10 k + replicate; connected non-surface worlds kept. d = 6
  only, since no other degree has large faithful surfaces.
- **Coverage.** The code builds F0's and F1's cells from this list and checks at the end that every registered cell ran (the lesson
  of `KNOTS-ALONE-20261111-001`, whose frozen code dropped two cells through an unregistered filter). A cell with no worlds is
  reported as such.

## Predictions (frozen)

- **P1.** Some swap world in F2 is read faithfully: d = 6 worlds with a local defect and long loops elsewhere keep NAE's faithful
  reading. *Fails* if none is.
- **P2.** For each d = 4 to 7, F1 has a faithful non-surface world (sparse worlds at 13 to 30 distinctions behave like long-loop
  surfaces). *Fails* for a d with none found, which a sample reports as not found, not as an absence.
- **P3.** No world on 6 distinctions is read faithfully at d = 4 to 7 (small worlds are dense). *Fails* if one is.

## Decision rules

- **Any faithful non-surface world (P1 or P2).** B145 is answered no: reading the knots faithfully does not supply the surface
  count, which is an input. A64's challenge then reads the count as given with the law; the defects NAE tolerates are reported; the
  stop condition is reached.
- **None in range.** A local lemma is attempted: that each defect type, in every d-regular world with d ≥ 4, forces a tie or an extra
  three-place bond; it is refereed before any claim. Until proved, the absence is computed only.

## Disclosed before freezing

- Controls outside the family ran: d = 3 random worlds on 9 distinctions (one faithful, with pairs in one knot) and swaps of a
  12-distinction torus (neither faithful). The coverage check reports false in control mode, where no registered cell runs, so it
  can fail. The enumerator gives one 3-regular world on 5 distinctions (the complement of a 5-cycle), as it should.
- No world of F0, F1 or F2 was read before freezing.
- Prior work, a bounded search: hypergraph reconstruction from colourings appears in a contextuality setting (arXiv 2105.08520);
  weak 2-colourings of pseudomanifolds and polychromatic colourings of triangulations concern existence and balance, not recovery
  of the complex. No overlap found; not a novelty claim.
- Expected runtime: under an hour; registered in `docs/LONG_RUNNING.md`, run under `systemd-run --user -p MemoryMax=16G -p
  MemorySwapMax=0`.

## Stop rule

One run. A faithful non-surface world in range ends the epic; otherwise one local-lemma attempt with a referee pass. Then report and
hold for a go-ahead.
