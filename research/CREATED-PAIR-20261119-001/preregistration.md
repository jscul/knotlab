# How does the law create a meet-once collision with other states? Pre-registration

Epic `CREATED-PAIR-20261119-001` (`GROW-SMALL-20261119-001#2` via `TRIPLE-GROWN-20261119-001#1`, the coordinator's go-ahead;
A97, A108, G1), 2026-11-19. Frozen before the full run. The canonical K1–K3 test is unchanged.

## The question

GROW-SMALL found one created pair. Two 7-junction starts with different tables (atlas 448 with loose counts 1, 1, 2, 1, 2, 1,
2; atlas 581 with 0, 2, 1, 2, 1, 2, 1) grow in one round into 12-junction stages with one full table and other allowed states.
The two stages part a round later. The other 86 pairs were carried and stay together. What does a table isometry do to the
created pair, and does the same thing tell created from carried?

## Prior work in the program

`python3 -B scripts/track.py objects "created collision table isometry loose distinctions growing end carried" --until 2026-11-19 --exclude CREATED-PAIR-20261119-001`

- `GROW-SMALL-20261119-001`: the 87 pairs and their origin.
- `UNIQUE-TABLE-20261119-001`: static rivals that differ by moving one distinction.
- `TRIPLE-GROWN-20261119-001`: three-way readings separate all 87.
- `GROWN-PAIR-20261119-001`: reached collisions that persist two rounds (knots sharing two), a relative of the carried ones.

## Design-stage observations (disclosed; seen before the freeze)

- **The created pair.** All 96 table isometries carry 11 of its 12 junctions onto junctions. The 12th is the round's four-way join,
  and its image differs from the other's join by one distinction: it takes one that is shared on the other side, and gives up
  one that is loose there. No isometry carries the loose distinctions onto the loose distinctions. Both members have 10 loose
  distinctions, in twin classes of sizes 1, 2, 2, 2 and 3, so this is not a counting fact (the advisor's E0 check).
- **Two carried pairs** (9 junctions each): some of their isometries carry loose onto loose, and the most junctions kept is 7.

The created side is therefore not fresh evidence. The test below is on the 61 carried pairs not looked at.

## Method

`isos.py` takes the 64 pairs whose members have at most 15 vertices. For each, it enumerates every full-table isometry directly,
with no twin quotient (cap 200,000). For each isometry it records:
- the junctions kept (carried onto junctions);
- whether the loose distinctions are kept;
- whether the growing end is kept: loose onto loose, and every junction holding a loose distinction carried onto a junction;
- whether the last round's junctions are kept;
- as a check, that the states are never carried.
E0 (loose counts and twin-class sizes) is recorded for each pair.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| E3 | Every carried pair (63 of the 64) has an isometry that keeps the loose distinctions (mine 75%, the advisor 70%; at least 55 of 63: advisor 90%) | one has none |
| E3b | Every carried pair has an isometry that keeps the growing end (mine 50%, the advisor 45%) | one has none |
| E0 | In every pair the loose counts and twin-class sizes agree | one differs |

Reported: the fraction of isometries that keep the loose distinctions, where the moved junctions sit, and the last round.

**The account under test.** The law grows on loose distinctions. A collision with an isometry that keeps the growing end is grown
in step one round further. The advisor's lemma is the sufficient direction: if the next table is a function of the table and of
the marked growing end, such an isometry extends to the next round. The created pair's isometries move a distinction across the
growing end, and the next round grows the two members differently. The converse is not a lemma: the created pair itself shows
that growth can bring together two stages with no isometry between them.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **Taken:**
  - the counting check (E0);
  - the growing end as the recorded prediction (E3b);
  - fractions of isometries, not only existence;
  - the sufficient direction stated as a hypothesis about what growth reads;
  - the warning that the created side is one case, already seen.
- **Its bets:** E3 70%, at least 55 of 63 90%, E3b 45%.

## Runs and stop rule

`isos.py` once (seconds); then stop.
