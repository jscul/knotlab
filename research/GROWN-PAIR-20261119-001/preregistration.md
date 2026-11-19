# Do two arrangements the cheapest growth reaches share a bond-distance table with different states? Pre-registration

Epic `GROWN-PAIR-20261119-001` (`UNIQUE-TABLE-20261119-001#1`, the coordinator's go-ahead; A97, G1), 2026-11-19. Code by the
thread; frozen before the run. The canonical K1–K3 test is unchanged.

## The question

`UNIQUE-TABLE-20261119-001` found, on 6 symmetry-free census stages, a second arrangement with the same exact table and other
allowed states, legal as a static arrangement but not shown reachable (five stall at once). Here both arrangements must be reached:
two census stages, each a stage of the cheapest complete-round growth from its own start, whose exact tables agree up to a renaming
of distinctions while the arrangements are not isomorphic.

## Two notions, kept apart

- **Legal as a static arrangement** (UNIQUE-TABLE's bound): every distinction in one or two junctions, junctions of at least three
  distinctions, no two sharing two, no junction at a cut vertex.
- **Reached by growth** (this study): a stage, round 1 to 8, of the census's growth from one of its 26,441 starts under the cheapest
  counts in complete rounds. A start (round 0) is not reached by growth; pairs are reported as start–start, start–grown and
  grown–grown, and only grown–grown answers the question. Codex's serial mixed law is not run here (not cheap enough tonight); its
  own census and the referee's to width 31 are the place to repeat this.

## In standard terms

Graphs G1, G2 on labelled edge sets of the same size; their smallest-bond tables T1, T2; is there a bijection of edges carrying T1
to T2 while G1 and G2 are not isomorphic? And does some such bijection carry the cut space of G1 onto that of G2 (same states up to
renaming) or none (other states)?

## Prior work in the program

`python3 -B scripts/track.py objects "two grown arrangements share a bond-distance table up to renaming reachable census stages" --until 2026-11-19 --exclude GROWN-PAIR-20261119-001`

- `CENSUS-READ-20261118-001`: the census stages and their exact tables (same population).
- `UNIQUE-TABLE-20261119-001`: the static version (same object; rivals not required to be reached).
- `NAE-GROWTH-20261119-001`: a relative under the not-all-equal law (whether tables say who joins whom); not this law.

`python3 -B scripts/track.py objects "canonical form of a distance table isomorphism of weighted complete graphs census" --until 2026-11-19 --exclude GROWN-PAIR-20261119-001`

- `OVERLAP-READ-20261111-001`: unrelated (minimal knot configurations forcing a tied pair).
- `CENSUS-READ-20261118-001` and `FRESH-COUNT-20261118-001`: as above.

Codex's `VARIABLE-OUTPUT-READER-20261118-001` line (`-001K`, `-001L`, `-001N`): reached histories under the serial mixed law with
one table and different states or menus; the comparison for this question under complete rounds.

## Method

`job.py` (shared runner): every census stage of at most 14 junctions (rounds 0 to 8, stopping at a stall or a close): its exact full
table, a Weisfeiler–Leman hash of the table (complete graph on distinctions, edges labelled by distance, four rounds; an isomorphism
invariant, so equal tables up to renaming share a bucket) and of the arrangement. `pairs.py`: arrangements deduplicated by exact
isomorphism (provenances kept); within a bucket every two arrangement classes tested for exact table isomorphism (VF2, nodes
coloured by their sorted rows); for each pair, whether some table isomorphism carries one's circuits (equation space) onto the
other's (states agree, renaming only, no value flips), decided by one isomorphism test of the table with circuits attached; for
grown–grown pairs, two rounds of growth from each, compared. The cheapest growth reads only the junctions (shown in
`RING-READ-20261118-001`), so isomorphic arrangements grow alike and deduplication loses nothing.

## Predictions (frozen)

The advisor's guesses are given beside mine.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | No arrangement class carries two tables (the table is a function of the arrangement) | one does |
| P1 | At least one non-isomorphic pair with isomorphic tables, of any provenance (advisor: about 70%) | none |
| P2 | At least one grown–grown pair (advisor: about 30% with no table symmetry) | none |
| P3 | No grown–grown pair in which junctions meet at most once on both sides (advisor: about 35% that one exists) | one exists |
| P4 | Every grown–grown pair found grows differently within two rounds (joins, sizes or grown tables differ) | a pair grows alike |
| P5 | Among grown–grown pairs, at least one has other states (no table isomorphism carries one equation space to the other) | all agree, or no pair |

## Runs and stop rule

One run of `job.py` (265 shards of 100 arrangements, 10 workers, about two minutes) and `pairs.py`. If P2 fails, one widening is
declared now: the same run at up to 20 junctions, with full exact tables where they finish within the case limit. Then stop.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage` names
claude-fable-5-2). Taken: deterministic hashing with fixed iterations; VF2 seeded with row colours; the check that one arrangement
never carries two tables; deduplication with provenance; starts reported apart and only grown–grown counted as the answer; results
by size; "states agree" stated existentially over all table isomorphisms and decided by one combined isomorphism test; renaming
only, no value flips. Its guesses are in the table.
