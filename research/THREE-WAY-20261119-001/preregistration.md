# Do three-way readings complete the bond-distance table? Pre-registration

Epic `THREE-WAY-20261119-001` (`UNIQUE-TABLE-20261119-001#2` and `GROWN-PAIR-20261119-001#1`, the coordinator's go-ahead; A97,
G1), 2026-11-19. Frozen before `triples.py` runs. The canonical K1–K3 test is unchanged.

## The question

A three-way reading is the smallest circuit holding three given distinctions, less one (the reading `VARIABLE-OUTPUT-READER-20261118-001E`
used at width 32). Both it and the pair table are functions of the allowed states. Add it to the pair table: on UNIQUE-TABLE's 527
symmetry-free stages, are the 6 different-states rivals separated, and do the 21 undecided stages decide? And does it separate
GROWN-PAIR's 152 reached groups with one table and other states?

## Settled by construction (stated, not tested)

A rival with the same allowed states as the truth has the same three-way readings, so the 72 same-states rivals of UNIQUE-TABLE, and
GROWN-PAIR's 4,474 same-states groups, are never separated by three-way readings or by any reading of the allowed states; only the
growth law, which reads the junctions, can tell them apart (A108).

## Prior work in the program

`python3 -B scripts/track.py objects "three-way readings smallest circuit holding three distinctions complete table" --until 2026-11-19 --exclude THREE-WAY-20261119-001`

- `UNIQUE-TABLE-20261119-001` and `GROWN-PAIR-20261119-001`: the same populations; this study adds the triple readings.
- `RING-READ-20261118-001`: the ring, read from pair distances alone (a relative).
Also `VARIABLE-OUTPUT-READER-20261118-001E` (three-way readings separate a width-32 pair under the other law).

## Method

`triples.py`: (six) triple readings of the truth and of each of the 11 rivals on the same names; (undecided) forcing with pairs and
triples (a triple at reading d lies in a circuit of d + 1 distinctions whose pairs and triples are all at most d; a unique one is
forced; a pair candidate holding a triple read above its size less one is dropped), then the one-missing search requiring both
readings to match, and the same-equation rivals within the bound as before; (grown) one isomorphism test per group of the pair table
with every triple attached as a vertex labelled by its reading.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| T1 | All 11 different-states rivals of the 6 stages differ from the truth in some three-way reading | one does not |
| T2 | On the 21 undecided stages, forcing with triples reaches the true equations on at least half, and no stage yields a code other than the truth's matching both readings | fewer, or such a code |
| T3 | Three-way readings separate every one of the 152 reached groups (no pair-table isomorphism also carries the triples) | some group is not separated |

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)). It confirmed the
settled-by-construction point and that forcing with triples is sound when candidates range over all (d + 1)-sets and readings are
exact; taken: its extra filter (a candidate may not sit inside a forced circuit either), and "none" as its own reading. It would bet
on the 11 and not on all 152: a circuit reading sees supports only, and differences may first show at four or more distinctions; so
T3 is the prediction it expects to fail. "States" here are equation spaces (no signs), as in the predecessors.

## Runs and stop rule

One run (minutes), then the readout; the study stops and goes on to B205.
