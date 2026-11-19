# How does the law create a meet-once collision with other states?

Epic `CREATED-PAIR-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `GROW-SMALL-20261119-001#2`.
Assumptions A97, A108; goal G1. **Referee pending.**

**Record.** Pre-registration, frozen before the run (commit `2f1b5c396`): [preregistration.md](preregistration.md). Code:
[isos.py](../../experiments/CREATED-PAIR-20261119-001A/CREATED-PAIR-20261119-001A-E001_isos/isos.py). Result:
[isos.json](../../artifacts/CREATED-PAIR-20261119-001A/CREATED-PAIR-20261119-001A-E001_isos/isos.json).

## The answer

**In the owner's terms.**
- **What the round does.** Call the two starts A and B. Every renaming that matches the two grown tables (there are 96) does the
  same thing:
  - It keeps 11 of the 12 junctions.
  - It swaps the roles of two junctions. One of A's starting knots plays the part of a junction that B gains only in the round,
    and one of A's new junctions plays the part of one of B's starting knots. That is why the starts differ while the grown stages
    agree: each start lacks one junction the other has, and the round supplies it.
  - The 12th junction is the round's four-way join. On the two sides it differs by one distinction. A's join holds the distinction
    that is loose in B, and B's join holds one that A leaves loose.
- **Why the allowed states differ.** The two joins are different equations, and no renaming makes them agree (the weight counts
  differ).
- **Why the pair parts at once.** The law grows on loose distinctions. No matching renaming carries A's loose distinctions onto B's
  (0 of 96), so the next round grows the two from different places and their tables part.
- **How carried pairs differ.** In all 63 small carried pairs, some matching renaming keeps the loose distinctions; in fact 23,436
  of their 23,496 renamings do. Their difference sits inside, two junctions away from the growing ends, so the law grows both alike.
  That is why all of them stay together a round further, and on full tables, by GROW-SMALL's referee.
- **The created pair's difference is one move.** It is the move of UNIQUE-TABLE's static rivals: a junction trades one distinction
  for another and keeps every bond size. The move made here falls on the growing end, and that is why it does not last.

| 64 small pairs (both members at most 15 vertices) | Carried (63) | Created (1) |
| --- | ---: | ---: |
| Table isometries (all, no twin quotient) | 23,496 | 96 |
| … keeping the loose distinctions | 23,436 (every pair has some) | 0 |
| … keeping the growing end (loose kept, and every junction holding one kept) | in 57 of 63 pairs | 0 |
| Most junctions kept | all but two, in every pair | all but one (the join) |
| Loose counts and loose twin classes equal | 63 | 1 |
| An isometry carrying the states | 0 | 0 |

| # | Prediction | Verdict |
| --- | --- | --- |
| E0 | Loose counts and twin classes agree in every pair | **held** (64 of 64): "no isometry keeps the loose distinctions" is not a counting fact |
| E3 | Every carried pair has an isometry keeping the loose distinctions | **held** (63 of 63; 99.7% of all their isometries) |
| E3b | Every carried pair has an isometry keeping the growing end | **failed** (57 of 63; the 6 others are the smallest, 9 junctions, where the moved junctions hold loose distinctions) |

## How it was done

`isos.py` enumerated every isometry of the two full tables, computed by bonds, for each of GROW-SMALL's 64 pairs small enough. It
used VF2 on the edge-coloured complete graphs, so isometries that break twin classes were included. For each isometry it checked
the junctions kept, the loose distinctions and the growing end. As a control, it checked that none carries the equation space. A
short follow-up after the run (`junction_maps.py`, [junction_maps.json](../../artifacts/CREATED-PAIR-20261119-001A/CREATED-PAIR-20261119-001A-E001_isos/junction_maps.json))
recorded which junctions each isometry exchanges. There are two junction maps, with 48 isometries each: both
maps send A's start knot {0, 1, 8} to B's round-1 pair junction {11, 14, 21}, and A's round-1 junction {9, 12, 15, 21} to B's
start knot {2, 5, 8, 17}.

## Known results, and what this adds

Known:
- UNIQUE-TABLE's static rivals, which differ by one moved distinction;
- GROWN-PAIR's and GROW-SMALL's carried pairs, which persist;
- GROW-SMALL's created pair, which parts;
- A108: the law reads junctions, not only states.

What this adds: the mechanism of the one created pair. A table isometry exchanges a start knot with a new junction and moves one
distinction of the join across the growing end. And a contrast that holds on all 64 small pairs: carried pairs keep their loose
distinctions under some isometry, and the created one does not.

## Limitations

- One created pair; the explanation is of it, not a theorem on creation.
- The sufficient direction (an isometry keeping the growing end extends a round) is the advisor's lemma under the hypothesis that
  the next table depends only on the table and the marked growing end. It is not proved here. The 6 carried pairs that fail E3b
  still persist, so keeping the loose distinctions, not the whole growing end, is what the data follow.
- 23 of GROW-SMALL's pairs (round 2, larger than 15 vertices) were not analysed.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)). Its counting check (E0)
rules out the trivial reading. It predicted that E3b would suffer from small-stage crowding, and it did: 57 of 63, against its 45%
bet that all would pass. It bet 70% on E3, which held. It noted that only the sufficient direction can be a lemma, since the
created pair shows that growth can bring together two stages with no isometry between them.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: how the created pair arises | **Status:** Successful | An exchange of a start knot with a new junction, and one distinction of the join moved across the growing end; no isometry keeps the loose distinctions, unlike every carried pair |
| Local direction: what reading of a base is complete | Continue | The growing end is what the law reads and the table does not mark |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | UNIQUE-TABLE's move, placed on the growing end |
| Long-term goal: G1 with A97 | Capability gained | A mechanism for when the law makes, and when it keeps, an ambiguity of the distances |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the sufficient direction: an isometry keeping the loose distinctions (and what else the round reads) extends one round | 3/3: turns "carried pairs persist" into a theorem | 2/3: the round's inputs are known (live junctions, candidates, counts) | state what the round reads, prove it is kept, check on the 86 → stop at a proof or a counterexample | Proposed |
| 2 | How often creation happens: starts of 8 junctions, three rounds, sampled | 2/3 | 2/3 | as recorded | Alternative · deferred |
| 3 | A pair agreeing on pair and three-way readings with other states (static, 8 junctions) | 2/3 | 2/3 | as recorded | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this study, status
unchanged.

## Final report as sent (2026-11-19 14:44 UTC)

**Outcome:** the created pair is explained, and the explanation also tells it apart from every carried pair. Closed, referee pending.

- **What the round does.** Call the two starts A and B. Every renaming that matches the grown tables (96 of them) keeps 11 of the 12 junctions. It also swaps the roles of two junctions: one of A's starting knots plays the part of a junction B only gains in the round, and the other way round. That is why the starts differ but the grown stages agree. The 12th junction is the round's four-way join, which differs by one distinction: on one side it takes a distinction that the other side leaves loose.
- **Why it parts next round.** The law grows on loose distinctions, and no matching renaming keeps them (0 of 96). So the next round grows the two from different places.
- **Why carried pairs stay together.** Every one of the 63 small carried pairs has matching renamings that keep the loose distinctions (23,436 of 23,496 do). Their difference sits away from where the law grows.
- **The same move as before.** The difference is UNIQUE-TABLE's static-rival move (a junction trades one distinction), here placed on the growing end. In short, the law makes the ambiguity only when the move lands where it grows next, and then undoes it at once.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: how the created pair arises | **Status:** Successful | A swap of a start knot with a new junction, and one join distinction moved across the growing end; no isometry keeps the loose distinctions, unlike every carried pair |
| Local direction: what reading of a base is complete | Continue | The growing end is what the law reads and the table does not mark |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | UNIQUE-TABLE's move, on the growing end |
| Long-term goal: G1 with A97 | Capability gained | A mechanism for when the law makes, and when it keeps, an ambiguity of the distances |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove that an isometry keeping what the round reads extends one round | 3/3 | 2/3 | state the round's inputs, prove they're kept, check on the 86 → a proof or a counterexample | Proposed |
| 2 | How often creation happens (8-junction starts, three rounds) | 2/3 | 2/3 | as recorded | Alternative · deferred |
| 3 | A pair agreeing on pair and three-way readings (static, 8 junctions) | 2/3 | 2/3 | as recorded | Alternative · deferred |

**Corrections:** one since my last report. TRIPLE-GROWN: counts of readings separate every pair (not 1,000 and 73), and its quoted ranks were wrong; Not a block. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. Its counting check ruled out the trivial reading. It predicted that the growing-end test would fail on small pairs, and it failed on 6 of 63.

Referee hand-off: the decision note is `research/CREATED-PAIR-20261119-001/created_pair.md`. Check most closely the isometry enumeration in `isos.py` (no twin quotient) and the junction maps in `junction_maps.py`.
