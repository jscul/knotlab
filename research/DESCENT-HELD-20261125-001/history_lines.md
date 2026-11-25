# Proposed history lines: the least-record study and assumption A247

Proposed by `DESCENT-HELD-20261125-001`, 25 November 2026. **Every count here is the drafter's scratch count, to be checked by
the confirming run ([its pre-registration](../DESCENT-HELD-20261125-001A/preregistration.md), P11) before anything is
entered.** The two witness starts below are written out so that the correction stands without either program. The scratch
engine's round equals `lr_core.own_round` of `LOCAL-ROUND-20261123-001A` (names included) on that study's twenty pairs, and it
reproduces the least-record study's sixteen holding runs birth by birth (births by round equal on 16 of 16; no birth with
parents at different parent steps), with that study's stopping reading (a run ends at the first round that changes nothing,
its `pfh_pop.py`, function `p3_lineage`) and its HOLD (SD line 53, coded in
`experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py` line 594).

## What the least-record record says

- [Its result](../LEAST-RECORD-20261124-001A/results.md), lines 12-13: "The one place it fails is the start built so that a
  start knot waits while a knot it meets acts; there five values are enough." Line 30 (P2): the condition "fails on one
  registered start only, the one built to break it". Line 37 (P9, "Fails"): "Under holding every birth's parents still had
  equal generations, in all 16 runs through six rounds". Line 95: on other starts or longer runs under holding, parents of
  unequal generations "may still occur".
- [Its decision](../LEAST-RECORD-20261124-001/decision.md), lines 20-21 and 24.
- The guide, lesson 9.3 (`publication/knotlab/INTUITIONS.md` lines 4319-4330): "on the one start built so ... it fails, and
  five values repair it there."
- A247's challenge: "the stamp fails on the one such start tried, and counting in fives works there".

Each is true of the populations it names. Taken as statements about that study's laws on other starts, they are too narrow.

## The count, defined

- **Starts**: the census of `COPYING-PARTS-20261123-001A` (its `cpcensus.py`): every connected graph of networkx's atlas on 1 to
  5 vertices; a loose count 0 to 3 on each knot with degree plus loose count at least 3 and at least one live knot; each kept
  once up to the graph's automorphisms; one shared distinction per edge; 3,380 starts, **3,348 kept** under parity (every start
  knot passes both methods of the parity test). Under not-all-equal no start knot fails, and the counts over all 3,380 are the
  same (none of the 32 set aside is counted).
- **Laws**: SD's complete round (`research/RING-IN-BALANCE-20261123-001/definitions.md` steps 1-8), two holders, no taking
  rule, RELEASE unless HOLD is named; the least-record study's four laws; the two and three added rules and FLOOR1 with
  waiting; three more waiting laws; the four holding laws of `GUARD-CAP-AND-HOLD-20261124-001`.
- **Bounds and reading**: 8 rounds, or the first round after which the structure has more than 3,000 knots, or the first round
  that changes nothing, or a stall.
- **The count**: a start is counted when some new knot of the run has two parents whose parent steps differ (parent steps:
  0 for a start knot, one more than the greatest of the parents' for a new knot; the least-record study's "generation").
  **Caveat:** the three-valued stamp is wrong somewhere on a counted start only when some birth's parents differ by a number of
  parent steps not divisible by 3; on the census no two parents differ by 3 or more (the greatest difference, child less parent,
  is 3), so there the two are the same.
- **Weighting**: each start counted once (up to isomorphism); the labelled weighting (each numbering of the knots counted
  once) beside it.

## The counts (scratch)

| Law | Counted (of 3,348) | Labelled share | Greatest difference 2 / 3 | Fives right on |
| --- | --- | --- | --- | --- |
| RATION-3, waiting (the least-record study's law) | **510** | 19.3% | 501 / 9 | 501 |
| CAP-3, waiting (the two added rules) | 510 | 19.3% | 502 / 8 | 502 |
| CAP-3, waiting, FILLERS (the three added rules) | 510 | 19.3% | 502 / 8 | 502 |
| FLOOR1, waiting | 223 | 7.9% | 222 / 1 | 222 |
| ORD, ONE-FEWER, RATION-4, each with waiting | 155, 351, 400 | 5.8%, 12.9%, 15.1% | 155/0, 346/5, 377/23 | not run |
| CAP-3 and RATION-3 with waiting, HOLD | 48, 48 | 1.5%, 1.5% | 44/4, 48/0 | not run |
| FLOOR1 retiring, HOLD; FLOOR1 offshoots, HOLD | 369, 462 | about 12.8%, 16.4% | —, 417/45 | not run |
| FLOOR1 offshoots; FLOOR1 retiring; ORD with STALL (the study's three other laws) | 0 | 0 | — | — |

"Fives right on" counts the starts on which the stamp written as parent steps counted in fives, read "a parent is one or two
less, counted in fives", is right at every place: exactly the starts whose greatest difference is 2. So 1,727 of the 1,753
counted runs under the four waiting bases (510 + 510 + 510 + 223); the other 26 have a parent three parent steps above a
child. The first draft's "1,225 of 1,243" left out the three added rules. Under FLOOR1 retiring with HOLD the count is 368 if
a run ends at the first round with no birth (a retiring round can bar without births).

- **By size** under the study's law: 21 of 197 four-knot starts and 489 of 3,128 five-knot starts; none of three knots or fewer.
- **The study's condition** (a start knot waits in a round in which a start knot it meets is a parent) fails on 1,474 starts
  under each RELEASE waiting law, every counted start among them. Under holding without waiting it never fails, and 369 and
  462 starts are counted: there P1's condition holds and the parents still differ. P1 is a statement under RELEASE.
- **Six knots** (a seeded sample of 3,000 of the 82,372 kept, `random.Random('DESCENT-HELD-20261125-001|six|v2')`): counted
  on 493, 493, 493 and 184 under the four waiting bases.

## The two witnesses (each grown by hand from SD's round; knots numbered start knots first, then new knots in the order of `lr_core.own_round`)

- **W1, the study's waiting law** (RATION-3, CANCEL-WAIT): stars `[[0,1,2],[0,3,5],[1,3,4,6],[2,4,7,8]]` (census start 133;
  four knots, nine distinctions; the smallest counted start by knots, then distinctions). Round 1: knots 1 and 2 are short and
  wait; knot 3 makes offshoots 4 and 5. Round 2: knot 2 waits again; knot 1 makes offshoot 7 (parent steps 1); 4 and 5 join as
  knot 6 and make offshoots 8 to 11. Round 3: new knot 12 is a join of knot 2, a start knot (parent steps 0), and knot 7 (parent
  steps 1). The three-valued stamp gives knot 12 the value 2 and knot 2 the value 0, and the rule takes the place between them
  the wrong way from both sides: knot 12 does not take knot 2 for a parent, and knot 2 takes knot 12 for one.
- **W2, holding with no knot waiting** (FLOOR1, CANCEL-OFFSHOOT, HOLD): stars `[[0,4,5],[1,2,6],[1,3,7,8],[0,2,3]]` (census
  start 64; four knots, nine distinctions; the smallest counted start under holding). Round 1: knots 0 and 2 join as knot 4;
  knot 1 makes offshoot 5; knot 0 keeps a loose place under HOLD for its cancelled group. Round 2: knot 2 makes offshoot 6, 4
  makes 7, 5 makes 8. Round 3: new knot 9 is a join of knot 0, a start knot (parent steps 0), and knot 7 (parent steps 2). No
  knot waits. (Under FLOOR1 retiring with HOLD, census start 62, stars `[[0,4,5],[1,2,6],[1,3,7],[0,2,3,8,9]]`, reaches such a
  birth at round 2: new knot 5 joins knot 0, parent steps 0, and knot 4, parent steps 1.)

## Proposed history lines

**On `LEAST-RECORD-20261124-001` (its result and decision):**

> 2026-11-25 · Narrowed, not a block (proposed by `DESCENT-HELD-20261125-001`; scratch counts, to be confirmed by its run).
> The corrected sentence: "On the twenty registered pairs it fails only on the start built so that a start knot waits while a
> knot it meets acts, and five values are enough there. On the census of 3,348 starts of up to five knots (each once up to
> isomorphism, 8 rounds or 3,000 knots) the three-valued stamp is wrong somewhere on 510 under the fixed three with waiting and
> on none under the other three laws; five values are enough on 501 of the 510, and no fixed number is known to be enough." P1,
> P2 and the table of costs stand on their populations; the narrowing is of what the sentence says of that law on other
> starts. P9 stays "Fails"; its stated limit is met off the registered runs: 48, 48, 369 and 462 of 3,348 census starts (368 for
> the third if a run ends at the first round with no birth). Under holding without waiting P1's condition holds and parents
> still differ: P1 is a statement under RELEASE. Witnesses: stars `[[0,1,2],[0,3,5],[1,3,4,6],[2,4,7,8]]` under the fixed three
> with waiting (round 3, a join of a start knot at parent steps 0 and a knot at 1) and `[[0,4,5],[1,2,6],[1,3,7,8],[0,2,3]]`
> under FLOOR1 with offshoots and holding (round 3, a start knot at 0 and a knot at 2).

**On A247, history:**

> 2026-11-25 · `DESCENT-HELD-20261125-001` (scratch counts, to be confirmed): the stamp's failure is not one built start. Under
> the waiting law of the study that adopted it, parents at different parent steps occur on 510 of 3,348 census starts of up to
> five knots (each once up to isomorphism; 19% with each numbering of the knots counted once), from round 2, smallest witness
> `[[0,1,2],[0,3,5],[1,3,4,6],[2,4,7,8]]`; under that study's three other laws on none; under its four holding laws on 48, 48,
> 369 and 462. Counting in fives is right on 1,727 of 1,753 such runs under the four waiting laws tried; a greatest difference of
> three parent steps occurs, so no fixed count is known to be enough. The same study writes the stamp in barred distinctions with
> no birth changed (its note, argument 2), from a start supplied flat. Status unchanged.

**For the thread:** whether lesson 9.3's sentence and the least-record summary on knotlab need a Narrowing entry in the
correction log once the run reproduces the counts. The drafter's reading: a Narrowing (the published sentence names the only
failure; the census has 510 under that law), not a Block (the stamp's result on its registered population stands).
