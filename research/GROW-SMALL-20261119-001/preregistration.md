# Does the law, grown from every small arrangement, ever make a meet-once collision with other states? Pre-registration

Epic `GROW-SMALL-20261119-001` (`PARENT-RULE-20261119-001#1`, the coordinator's go-ahead; A97, G1), 2026-11-19. Frozen before
the runs. The canonical K1–K3 test is unchanged.

## The question

PARENT-RULE showed that backed pairs, which the law keeps at every size, do not keep the allowed states: 242 static meet-once pairs
of 6 and 7 junctions share a table with other states and are backed on both sides. What protects the census's reached stages
must then be the law's exact joins and counts. But only 85 small arrangements are themselves one round of the law, too few to
test. So take every one of PARENT-RULE's 503,039 legal meet-once arrangements of at most 7 junctions as a start. Grow each one and
two complete rounds of the census's law. Every resulting stage still meets once. Among all of them, is there a pair of
non-isomorphic stages with isomorphic full bond-distance tables and other allowed states?

## Prior work in the program

`python3 -B scripts/track.py objects "grow every small arrangement one and two rounds meet-once collision other states self-grown" --until 2026-11-19 --exclude GROW-SMALL-20261119-001`

- `PARENT-RULE-20261119-001`: the 503,039 starts, backed pairs, and the self-grown test (the direct predecessor).
- `MEET-ONCE-20261119-001`: the same question on the census's reached stages, and the pairing reused here.
- `GROWN-PAIR-20261119-001`: reached collisions to 14 junctions.
Also `TOUCH-CENSUS-20261118-001`, whose starts (at most five knots) these starts include and extend.

## Method

- **The run** (`job.py`, on the shared runner).
  - Each start is grown by complete rounds, cheapest counts, elimination over GF(2), rounds 1 and 2. A stall ends a start.
  - For every stage it records:
    - round, junctions, distinctions, and the largest number of distinctions any two junctions share;
    - a Weisfeiler–Leman hash of its table, read exactly to 8 and pooled beyond (exact_table_v2);
    - whether some pair reads beyond 8;
    - a hash of the arrangement;
    - its **self-grown depth**: peel, regrow one round, compare; repeat while it gives the arrangement back; at most 4.
  - Every 500th start is also grown from a relabelled copy.
- **The pairing** (`pairs_grow.py`): one global pool over all stages, of any start and round. It runs MEET-ONCE's amended pairing
  unchanged (`pairs_meet2.examine`):
  - exact arrangement classes, with every provenance;
  - candidate groups, by exact isomorphism of the tables read to 8;
  - states first: a junction-graph isomorphism, else every isomorphism of those tables on twin classes, tested by rank (cap
    5,000). Every renaming that carries one equation space onto the other keeps every table, so an exhausted search is an exact
    "other";
  - classes with other states escalated to tables read to 12, 16, … and the full table, under a 1,800 s alarm.
- **The control and the targeted test** (`targeted.py`), both suggested by the advisor:
  - **C0:** PARENT-RULE's 472 static other-states groups, run through the same pairing as stages;
  - **T:** every member of those groups grown one and two rounds and paired again.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G1 | No pair of non-isomorphic stages (rounds 1 and 2, all starts) with isomorphic full tables and other states; it holds only if none is undecided (my bet 75%, the advisor's 80%) | one exists; with undecided ones it is reported as not decided |
| G2 | Power: at least 100 same-states collision groups among the stages (else G1 is reported as weak) | fewer |
| C0 | Control: all 472 static groups come back as collisions with other states, none undecided | any missed |
| K | Controls: every stage meets once; every stage of round r has self-grown depth ≥ r; relabelled copies grow isomorphically | any exception |

Reported without a prediction:
- G1 by self-grown depth cells, (1, 1), (1, ≥ 2) and (≥ 2, ≥ 2), since the round index depends on the start;
- T's tallies;
- stages by start size;
- stalls;
- stages with a pair beyond 8.

If G1 fails, the pair is checked outside the pipeline:
- full tables by bonds (PARENT-RULE's `plib`) with an explicit renaming checked entry by entry;
- non-isomorphism, by a second encoding;
- other states, by an invariant (rank and low-weight word counts);
- regrowth from relabelled starts;
- a third round.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

Taken:
- the targeted test T and the positive control C0;
- undecided groups block G1;
- one global pool across starts and rounds;
- the relabelled-start control;
- stalls and stages by start size;
- a power floor (G2);
- meeting once checked over all pairs of junctions;
- the beyond-8 log;
- scoring by self-grown depth;
- the check protocol for a failure.

Answered rather than taken: its worry that "a renaming need not be a table isomorphism". Every renaming that carries the
equation spaces keeps the table, since the table is read from the equation space, so the exhausted search is exact. The twin
classes are invariant: permutations inside one keep both equation spaces (PARENT-RULE's `plib` notes).

Its bet: G1 holds overall 80%; fails only at depth 1, 14%; fails with a depth-2 stage, 6%. It expects any failure among
round-1 stages of 10 to 14 junctions whose starts are themselves such a pair.

## Runs and stop rule

`job.py` (113 cases, 8 workers, 16G cap), then `pairs_grow.py` and `targeted.py`. One run each; then stop.
