# Referee report MEET-ONCE-001-R1 (own growth, own tables read to distance 8, own states test)

**Verdict: confirmed, with one small count to correct. No Block.**
- **The 2,698 are the whole population, not a sample.**
  - The study grew every one of the census's 26,441 starts: all 265 shards ran, and the census is TOUCH-CENSUS's list of start
    arrangements of at most five knots.
  - The referee regrew all of them with its own engine and kept every stage of rounds 1 to 8 with 15 to 40 junctions in which no
    two junctions share two distinctions. It found the same 2,698 stages: the same start and round each, the same keys and the same
    junction counts. These form 2,692 non-isomorphic arrangements.
- **The 102 groups reproduce exactly, from the referee's own tables.** The referee read each table to distance 8 with its own bond
  enumeration (Section 2). On the 509 stages of at most 18 junctions, these tables equal its full shore table entry by entry. Its
  grouping gives 102 groups, 101 of two and 1 of three, and each of the study's 102 lies inside one of them.
- **Same states, exactly, in every group.** Each of the 103 tests was decided by an explicit carrier:
  - 88 by a junction-graph isomorphism;
  - 15 by the referee's exact search over renamings that keep the distance-8 table, with every star's image checked against the
    other span.
  None was undecided.
- **The split adds up: 83 + 5 + 15 = 103 tests in 102 groups.** The group of three (20, 21 and 20 junctions) holds two tests, one of
  a closed stage against an open one and one with the outside exchanged. The kinds match the study's exactly.
- **The states test, and "no full table needed", are sound.**
  - Every renaming that carries one equation space onto the other keeps the full table, and so the table read to 8.
  - So same states implies isomorphic full tables, and no full table is needed for a same-states pair.
  - Every full-table collision lies inside a group of the distance-8 table.
  - "Other states" would have needed a complete enumeration, but no group needed it.
- **One size past it holds again.** The referee repeated the whole pipeline on every meet-once grown stage of 14 to 50 junctions
  (3,503 stages), which also catches groups that straddle the bounds. It found 113 groups: the same 102, 9 more at 41 to 50 junctions,
  and 2 that straddle 14 and 15. All 113 keep the states.
- **The count to correct: 19 should be 20.** The Limitations' "without them, 19 groups remain" subtracts the 83 closed-and-open
  pairs as if each were its own group. The group of three keeps two open arrangements of 20 junctions when its closed one is
  removed. So 20 groups remain (102 − 82). M2 holds either way.
- **The wording is mostly guarded.** The size bound is stated in the answer, the table and Known results. A few sentences read as a
  law (points 2 to 4 below).

## 1. The population (`job_meetonce.py` from GROWN-PAIR-R1 with `--param lo=15 --param hi=40 --param notable=1`; `referee_meet.json`)

| Check | Result |
| --- | --- |
| Census starts | 26,441 (TOUCH-CENSUS's arrangements of at most five knots, the census's sorted order) |
| Study's shards | 265 of 265 ok (100 starts each; index range 1 to 26,415 among the stages kept) |
| Meet-once grown stages, rounds 1 to 8, 15 to 40 junctions: referee / study | **2,698 / 2,698** |
| Same set of (start, round); same start key; same junction count on every stage | yes; yes; yes |
| Non-isomorphic arrangements | 2,692 |

- **The engine.** The referee's is its own: complete rounds, the fewest counts, GF(2) implication (FRESH-COUNT-R1 and FIRST-KNOT-R1).
- **The study's** is CENSUS-READ's census job.
- **They agree stage for stage.** So the population is every such stage the law reaches from the census's starts, not a sample of
  them.

## 2. Tables read to distance 8 (`referee_meet.py`, `job_meet_tables.py`)

**The referee's bond enumeration, independent of `exact_table_v2`:**
- **The junction graph.** Junctions are vertices; the outside vertex o is added when something is loose. Each distinction is an
  edge.
- **Bonds of at most nine distinctions.** Each bond has a side S that avoids a root (o, or junction 0 when closed). S is grown as a
  connected set from its least vertex; at each step one free neighbour is either added or held out.
- **Pruning.** A branch is cut when the maximum flow from S to the held-out set exceeds nine.
- **The leaves.** At a leaf every neighbour of S is held out, so the cut is exactly the edges leaving S. It is kept when it has at
  most nine edges and the rest of the graph is connected.
- **The table.** It holds each pair's least bond of at most nine; larger pairs are pooled.

| Check | Result |
| --- | --- |
| Stages | 2,698 (slowest 2.7 s) |
| Equal to the referee's full shore table at entries of at most nine (stages of at most 18 junctions) | **509 of 509** |

## 3. Groups and states (`job_meet_groups.py`)

The method:
- **Deduplication.** Arrangements in each invariant bucket were deduplicated by exact isomorphism.
- **Grouping.** They were grouped by exact isomorphism (VF2, edge labels) of the labelled graph of entries of at most nine.
- **The states test,** run against each state group's first member:
  - **a junction-graph isomorphism,** with o a plain vertex and edge multiplicities kept. It carries one cut space onto the other.
  - **Otherwise `same_states`.** This is a search over renamings of the distinctions:
    - each candidate must have the same sorted row of the distance-8 table, and every entry assigned so far must agree;
    - distinctions held by the same junctions are taken in increasing order;
    - a branch is pruned as soon as an assigned star's image leaves the other span.

    It is exact, and its cap was never reached.

| | Count |
| --- | ---: |
| Groups (two / three arrangements) | **102** (101 / 1) |
| … one state group (same states) | **102** |
| … other states / undecided | **0 / 0** |
| Tests: a closed stage and an open one of one junction fewer, by junction-graph isomorphism | **83** |
| Tests: same junction count, junction graphs isomorphic (outside exchanged) | **5** |
| Tests: same junction count, other junction graphs, by the search | **15** |
| The study's 102 groups each inside one of the referee's | 102 of 102 |

**On the states test in `pairs_meet2.py`** (the owner's hand-off):
- **A junction-graph isomorphism** fixes the cut space, so its "same" is sound.
- **The twin-class lift** is sound. Distinctions with the same holders are parallel edges, and permuting them keeps the span. Its
  check is that the mapped stars and the other stars together have the other arrangement's rank, and so do the mapped stars alone.
  That is equality of spans.
- **"Other"** would need the full enumeration (cap 5,000), and no test reached it. Every "same" came from the first quotient
  renaming tried, as the note says.

## 4. One size past (`--param lo=14 --param hi=50`, then the same two jobs)

| | Count |
| --- | ---: |
| Meet-once grown stages, 14 to 50 junctions | 3,503 (156 at 14; 41 to 50: 56, 53, 38, 100, 89, 67, 77, 65, 47, 57) |
| Groups | 113 (112 of two, 1 of three) |
| … wholly within 15 to 40 / 41 to 50 / straddling 14 and 15 | 102 / **9** / **2** |
| … same states | **113 of 113** (tests: 93 closed and open, 5 outside exchanged, 16 other graphs; none undecided) |

So no meet-once reached collision with other states appears to 50 junctions. Groups across the study's two bounds were checked as
well: none straddles 40 and 41, and both that straddle 14 and 15 keep the states.

## 5. The six static pairs

UNIQUE-TABLE's six:
- **Size and meeting.** They have 7 (pop-0308) or 8 junctions, and in every one the truth and the rival both meet once (from
  `verify_rivals.json`).
- **Reachability.** UNIQUE-TABLE-R1 showed that no rival is reached, from any start after any number of rounds, nor under the
  serial law at the same width. Each truth is reached at round 1 of its census start.
- **So** "the law never builds them" is right for the rivals; the truths are built (point 4).

## Corrections and wording points for the owner (listed, not folded in)

1. **"Without them, 19 groups remain" should be 20** (Limitations). The group of three loses its closed member and keeps two open
   arrangements of 20 junctions, so 102 − 82 = 20 groups remain. M2 holds either way. **Not a block.**
2. **"Reached collisions with other states need knots that share two distinctions"** (the answer) and **"Other-states collisions need
   knots sharing two"** (the final report) read as a law. Statically the six meet-once pairs have other states. For reached stages
   it is computed: none where junctions meet once to 40 junctions (and, by this referee, 50). It should say so. **Not a block.**
3. **"Where junctions meet once, reached stages lose nothing of the states to their distances; statically they do"** (the position
   table, and the final report's row) carries no size bound. It should say "to 40 junctions, computed". "GROWN-PAIR's finding is not
   a size effect" likewise holds to 40, and the Limitations' "This is a property of what the law reaches" is best written "observed
   (computed) on what the law reaches". **Not a block.**
4. **"None of them is reachable"** (the six static pairs): the rivals are not, but each truth is a census stage of round 1. Say "the
   law never builds the rivals". **Not a block.**

## How the work was split

- **The referee:**
  - read `meet_once.md`, the pre-registration and Amendment 1, `job.py`, `pairs_meet2.py`, `check_full.py`, and `exact_table_v2.py`
    (for the meaning of H only);
  - wrote `referee_meet.py` (junction graph, bond enumeration with a flow bound, distance-8 table, invariant, junction-graph
    isomorphism, exact states search), `job_meet_tables.py`, `job_meet_groups.py` and `meet_readout.py`;
  - extended its GROWN-PAIR-R1 `job_meetonce.py` (`notable`), on its FRESH-COUNT-R1, FIRST-KNOT-R1 and CENSUS-READ-R1 code.
- **Read as data:** the census keys; the study's stage results (start, round, key, junctions), its groups' provenance and tests
  (`meet_pairs2.json`); UNIQUE-TABLE's `verify_rivals.json`.
- **No study code was run.**
- **Where it ran.** Every computation ran under `scripts/longrun.py` within the 16 GB cap, with a 2 GB limit per case (peak 664 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
