# When a local reader's view settles, from the start alone: what stands

Epic `SETTLE-BOUND-20261126-001` (the coordinator's go-ahead on the selected direction of `LOOK-ALIKE-20261126-001`;
goals G17 with G1; register entry A283 bears on it), closed 26 November 2026. A check by the thread, not registered:
computed; referee pending. [The note, with the frozen bound, the expectations and the results](README.md)

## What stands

1. **The largest block does not bound the settling round.** The bound frozen on starts of up to four knots, a start's
   view settling by M + 5 rounds without parents and M + 7 with them (M the larger of the largest set of live start
   knots sharing a neighbour and the largest fresh count of a round-1 birth), fails on 41 of 1,556 five-knot starts of a
   dimension and on 6 of 387 held-out six-knot starts (a seeded sample of 1,000 of the census's 82,656) under
   not-all-equal, and on 11 and 2 under parity, by up to three rounds.
2. **Most late starts narrow to one knot first.** In 30 of the 41 and 4 of the 6, the counts fall to a single birth a
   round and the growth then goes on as a lone knot does; the view settles a few rounds after. The narrowing can come
   late in a start with no large block.
3. **The pair rule holds wherever the views settle by the cut.** With each start's bound as its cut, every missed pair
   in all four runs includes a start that settles past its bound.

**Not established.** A bound on the settling round from the start alone; whether the round of the last merge bounds it
(the note's link); starts of seven knots or more.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the settling round bounded by the start's largest block | **Status:** Refuted (the stop met at a miss) | 41 five-knot and 6 held-out six-knot starts settle past it, in both knot laws |
| Local direction — a bound from the start alone | Continue, narrowly | The late starts narrow to one knot first; the round of that merge is the candidate |
| Broader exploration — what a local reader keeps of a start | Searching | The pair rule holds wherever views settle by the cut |
| Long-term goal — G17 Typical and rare meeting patterns, with G1 | Obstruction learned | The settling round is not a function of the largest block; it follows the whole growth's merging |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The round of the last merge as the settling bound | 2/3 — a bound from the start's meeting pattern | 3/3 — the map of joins is in the record | Compute from the map of joins the round at which every live member lies in one cluster; compare with settling on the 47 late starts → a bound, or none | Selected · not started |
| 2 | Late views from the start alone | 3/3 — "logically small" made static | 2/3 — the late kinds look like chain tips and block bursts | Predict each late view from endless chains and blocks → every view, or a miss | Alternative · deferred |
| 3 | Rings of one proved rate | 2/3 | 3/3 | The look-alike referee's ring pairs, extended | Alternative · deferred |

1. Cheap, and it either gives the bound or says settling has no simple start-alone bound.
2. Still the stronger question.
3. Unchanged from the look-alike study.

**Corrections:** none.
**Goals:** checkpoint row added (G17, G1; obstruction learned); no goal changed.
**Assumptions:** none added; the bound was a prediction, now refuted, not an assumption.
**Scaffolds:** the readings (A283), the settling definition and its least round 3, the census weighting and the seeded
sample. Swapped: the knot law (parity), four, five and six knots. What survived: the pair rule wherever views settle
by the cut; what failed in every swap: the bound.
**Advisor:** not consulted before the freeze, again a slip against the standing practice; the referee is the check.
