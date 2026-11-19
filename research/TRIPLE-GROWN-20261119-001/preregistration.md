# Do three-way readings separate the reached and static meet-once collisions? Pre-registration

Epic `TRIPLE-GROWN-20261119-001` (`GROW-SMALL-20261119-001#1`, the coordinator's go-ahead; A97, G1), 2026-11-19. Frozen before
the run. The canonical K1–K3 test is unchanged.

## The question

THREE-WAY found that pair plus three-way readings separate every collision with other states known then. Since then:
- PARENT-RULE found 472 static meet-once groups with one table and other states (1,034 pairs, 6 and 7 junctions);
- GROW-SMALL found 87 reached meet-once pairs (9 to 17 junctions): 86 carried from those static pairs, and 1 created.

Do three-way readings separate all of them?

## Prior work in the program

`python3 -B scripts/track.py objects "three-way readings separate reached meet-once collisions static groups" --until 2026-11-19 --exclude TRIPLE-GROWN-20261119-001`

- `THREE-WAY-20261119-001`: the readings and the test.
- `GROW-SMALL-20261119-001`: the 87 reached pairs.
- `PARENT-RULE-20261119-001`: the 472 static groups.

## Method

`triples.py` takes every two members in different state groups.
- **Readings.** When both members have at most 15 vertices, the readings come from every bond (exact): 1,034 static and 64
  reached pairs. Otherwise both members are read from every bond of at most 9 distinctions, with readings above 8 and "none"
  pooled together: 23 reached pairs.
- **The test** (THREE-WAY's): the pair table as an edge-coloured complete graph with Weisfeiler–Leman colours, with every triple
  that has a reading attached as a vertex labelled by it. Is there an isomorphism between the two graphs?
  - With pooled readings, separation is exact, but agreement is undecided.
- **Also reported:** the rank of the three-distinction bonds against the rank of the equation space. That rank check is the
  advisor's test of whether separation is automatic; a smoke test shows it is not here (ranks 2 to 6 against 6 to 9).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| T1 | All 1,034 static pairs separated (my bet 90%, the advisor's 97%) | a pair agrees on both |
| T2 | All 87 reached pairs separated, none undecided (my bet 90%, the advisor's 95%); the created pair reported separately | a pair agrees on both, or one stays undecided |

All pairs are run; the count and pattern of any agreements is the result. If a pair agrees on both:
- compare its two full bond sets up to renaming;
- if they are isomorphic, no reading of any arity separates them;
- if not, the smallest bond in one and not the other gives the arity needed;
- confirm by a second code path and an invariant of the states.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **Its warning.** It warned that separation could be automatic if three-way readings at 2 found every junction. That holds only
  when junctions have three distinctions, and here they do not: the rank check is reported.
- **Taken:**
  - one reading regime per pair;
  - "none" and "above 8" pooled together;
  - distinct colours for triple vertices;
  - the created pair reported apart;
  - run everything rather than stop at the first agreement;
  - its procedure for an agreement.

## Runs and stop rule

`triples.py` once (minutes, under a 16 GB cap); then stop.
