# The eddies in the cluster rule's break shapes

Epic `BREAK-EDDIES-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking
`LOOP-CATALOGUE-20261119-001#1`). Goal G17. **Refereed:** report [R1](referee-R1/report.md), the family claim confirmed with a
**Block** on one reading (the short loops), one Narrowing (the explosive kind) and three corrections that are not blocks, folded in
on 19 November (see Referee). One over-cap start's regrowth is still running (see Record). The headline was also narrowed after the
run, when LOOP-CATALOGUE's part U was read in full (see Part U in full).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `243a0fd17` at 08:16 UTC after a pilot (disclosed).
- The run went through the shared runner (`BREAK-EDDIES-B1`, `runs/break-eddies`, 122 cases on 3 workers): 120 finished. Two,
  the theta and one eight-knot start, went over the runner's 3.5 GB per case.
- The referee's three six-knot shapes from `LOOP-CATALOGUE-20261119-001`'s R1 were added after the freeze as readouts
  (`BREAK-EDDIES-B2`, `runs/break-eddies-ref`, 9 starts with a 10 GB child; amendment of 08:51 UTC).
- The theta and the other over-cap start were regrown with a 10 GB child (`pilot/theta_groups.py`, post hoc). The theta again went
  over at round 18 (2,258 junctions), with its largest group rising 5, 5, 5, 5, 8, 12 over the last rounds. The other start, G-009,
  is still running (`BREAK-EDDIES-B3`). The referee's readout of it reaches round 23 (8, 10, 12, 15, 19, 23, 28, 35, 44, 57, 75, …,
  2,726), with its largest group rising to 8, and finds no recurrence.
- Code: [job.py, job_ref.py, merge.py, posthoc.py, stagelib.py, breaklib.py](../../experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/),
  with the pilot in `pilot/`.
- Results: [results.json](../../artifacts/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/results.json),
  [posthoc.json](../../artifacts/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/posthoc.json) (W from the rate,
  superseded) and [posthoc_full.json](../../artifacts/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/posthoc_full.json)
  (W from every factor of the counts' recurrence, `posthoc_full.py`, after the referee).

Words as in `LOOP-CATALOGUE-20261119-001`. A **group of three** is a first-round group of three or more knots: pairwise
candidates with no common neighbour, joined by one junction in round 1. The rule calls it a hyperedge.

## The answer

**In the owner's terms.**
- **The break-shape eddies read here are the same eddies.** Of the 122 self-feeding starts the cluster rule could not read in
  part U's first 440 starts (the cheap ones; see Part U in full), 116 grow at a rate that is exactly a member of the catalogue's
  family, and so do 2 of the referee's 9 shapes. That is, the rate solves W = 1 for a round-weight W built from the same pieces:
  - y per knot of the loop;
  - (1 + y) per spare or lone hung knot;
  - 1 + y + y² for a hung knot with a spare;
  - 1 + y(1 + y)² for a hung knot with two;
  - 1/(1 − y) for an endless chain.

W is read from every factor of the counts' minimal recurrence, not from the rate (corrected after referee R1, `posthoc_full.py`).
The rate alone does not fix W: eight members of the family share the plastic number, and two share the rate of y³(1 + y).

| Round-weight W | Starts | Rate |
| --- | --- | --- |
| y^2 (1 + y) | 10 | 1.3247 (the plastic number) |
| y^3 (1 + y) | 2 | 1.2207 |
| y^4 (1 + y) | 8 (incl. the referee's two triangles joined once) | 1.1673 |
| y^4 (1 + y)^2 | 15 | 1.3247 |
| y^5 (1 + y) | 9 | 1.1347 |
| y^5 (1 + y)^2 | 23 | 1.2628 |
| y^5 (1 + y)^3 | 29 | 1.3854 |
| y^5 (1 + y)(1 + y + y²) | 8 | 1.3247 |
| y^5 / (1 − y) | 1 | 1.3247 |
| y^5 (1 + y)/(1 − y) | 5 | 1.4196 |
| y^5 (1 + y + y²) | 1 | 1.2032 |
| y^5 (1 + y(1 + y)²) | 1 | 1.2825 |
| y^6 (1 + y)^2 | 4 | 1.2207 |
| two loops, no single W | 2 | 1.3247 |

The first version's table, read from the rate, had 36 starts at y^2 (1 + y) and 6 at y^3 (1 + y). Those are now 10 and 2, the rest
spread over y^4 (1 + y)^2, y^5 (1 + y)(1 + y + y²), y^5 / (1 − y), y^6 (1 + y)^2 and two starts with two loops.

- **Corrected (Block on this reading, referee R1): short loops are not shown.** No ring of knots makes a loop shorter than four
  steps. Three knots in a ring are joined in one go, four make a pair with two common neighbours, six make two groups of three.
  - The first version said loops of two and three steps (W = y^2 (1 + y), y^3 (1 + y)) are the commonest here, and that all 70
    rational starts with such a loop hold a group of three, so groups of three make the short loops. It read W from the rate.
  - Read from every factor of the counts' recurrence, only 12 starts are consistent with a loop of three steps or fewer. Even there
    the counts do not show one: a loop of four with two spares, with a factor the counts cancel, fits them too.
  - All 12 hold a first-round group of three (B6, 12 of 12). Whether groups of three make loops shorter than a ring's is open.
- **Why the rule can't see them, even later.** The growth continued from any stage is the growth of that stage taken as a start,
  so the rule can be applied at any stage. At the stages after 0 to 3 rounds, none of the 120 starts is inside its scope and free
  of its known breaks. The groups of three reproduce themselves every round, so restarting the rule later does not recover the
  loop.
- **So does one extended rule cover them? In what they do, yes; in finding them, not yet.** Their counts are the catalogue's,
  piece for piece. What is missing is the rule's map: it would have to include the junctions of the first round as points, and to
  take in the case it now excludes, a group of three that shares two knots with another block. (That case is not a loop of length
  two: `JUNCTION-MAP-20261119-001`.) "Junctions as valid sets" is the right picture for building that map. It is not built here.
- **A second, different kind: explosive starts.** Two triangles joined twice, the three-regular six-knot graph (the referee's
  shapes), the eight-knot G-121 and, by its last rounds, the theta grow in leaps: 22, 38, 127, 720, or 80, 32, 31, 465, 4,495,
  31,465.
  - In the last round or two reached before memory ran out, their largest groups jump (13, then 60; 33, then 178; 36, then 382 in
    G-121).
  - That is not "groups grow without bound" (Narrowing, referee R1). In F-04 and F-05 the largest group falls back from 66 to 2, 3,
    4, 5 while the counts leap.
  - This is not a loop with a fixed rate. These need a different object, one that follows the growth's groups, not a round-weight.
- **A third, undecided: three fast starts** at eight knots double every round (32,385, 61,165, 116,108, 221,417), with groups
  staying near 8 to 10. No recurrence fits within reach. They may be two-loop eddies (algebraic), which none of the catalogue's
  entries to eight knots was.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| B1 | pilot recurrences persist | **held** | 26 of 26, to 41 to 60 rounds |
| B2 | W nonnegative integers, W(1) ≥ 2 | failed as scored | 93 of 116; the 23 others read W from the irreducible factor with the largest root, which drops x^2 + x + 1 (x^7 − (1 + x)^2 = (x^2 + x + 1)(x^5 − x^4 + x^2 − x − 1)). The counts cancel it in only 6 of the 23; in 17 it is in their minimal recurrence and the reader dropped it (referee R1). Read from every factor, all 116, plus the referee's 2, are members (post hoc) |
| B3 | readout: largest group in rational starts | — | 9 to 14 at round 40, growing slowly |
| B4 | explosive starts' groups exceed rational ones' | failed | measured on 2 of the 4 (the others went over the cap): one exceeds, one stays at 8. The referee's explosive shapes reach 60 and 178, and the theta's regrowth rises to 12 by round 18 (readouts) |
| B5 | theta: no recurrence of order ≤ 8 | not decided | over the cap in the frozen run, and again at 10 GB (18 rounds, too few to decide) |
| B6 | loops of ≤ 3 steps need a group of three | **held** as scored, on a misread W | 70 of 70 as scored; of those 70, 58 have loops of four or more steps when W is read from every factor (28 of them five). On the 12 consistent with three or fewer, 12 of 12 (referee R1, post hoc) |
| B7 | more open places never lengthen the loop | failed as scored | 74 of 89 pairs. The 15 failures were the misread W: read from every factor, all 86 comparable pairs hold (referee R1, post hoc) |
| B8 | no later stage inside the rule and break-free | **held** | 0 of 120 |

3 of 7 held as scored (B3 is a readout). B2 and B7 hold once W is read correctly (post hoc), and B6 holds on its true population.
B5 could not be decided within memory.

## Known results, and what this adds

- **Known.** As in `LOOP-CATALOGUE-20261119-001`: transfer matrices and rational series; the trinomials x^(L+1) − x − 1; the plastic
  number (the real root of x^3 = x + 1, the smallest Pisot number).
- **What this adds.**
  - The cluster rule's break shapes hide no new kind of steady eddy. Every rational one has a rate of the family, and its W is a
    member built from the catalogue's pieces, three of them new to the table: y^4 (1 + y)^2, y^5 (1 + y)(1 + y + y²) and
    y^6 (1 + y)^2.
  - The rate does not fix W. Every factor of the counts' minimal recurrence other than x − 1 divides 1 − W, and that reads it.
  - A separate explosive kind exists, in which the counts leap and the groups jump in the last rounds reached.
  - Restarting the rule at a later stage does not recover either kind.

## Limitations

- **Rational means a recurrence found** by Berlekamp–Massey with twice its order to spare, holding to the horizon (41 to 60 rounds,
  or 300,000 junctions). W is the smallest member of the family that every factor of the minimal recurrence divides, read after
  the referee (`posthoc_full.py`, which reproduces the referee's table). For 12 starts that member is not the only one consistent
  with the counts.
- **The explosive class** is read on 7 starts of the referee's shapes, each stopped by memory after 9 to 14 rounds, on G-121, and on
  the theta to 18 rounds. G-009 is still running.
- **The population** is LOOP-CATALOGUE's part U main run (122 exponential starts), not the 1,080 read afterwards, and the
  referee's 9.

## Part U in full

Added on 19 November, after `LOOP-CATALOGUE-B4` read the rest of part U. Logged as a **Narrowing** (completeness) in
`docs/CORRECTIONS.md`.
- **This population was the cheap part.** The 122 came from the 11 shards of part U that fitted the runner's memory. The other
  1,080 starts hold 170 more exponential starts, not grown here, and 626 that went over their child's 3 GB or 90 s. 624 of those
  were still rising, by a median factor of 2.6 in their last round, and 574 have overlapping groups of three.
- **So the headline holds on this population only.** Whether most eddies in the break shapes are the catalogue's, or the explosive
  kind, is open. Direction #2 (the explosive kind) now has 624 starts to begin from.

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread, with its own growth engine and
its own exact Berlekamp–Massey. No study code was run.
- **Confirmed.**
  - All 131 starts regrown: counts and largest groups equal to the study's on every common round of the 129 both reached.
  - 118 rational starts (116 of the 122, and 2 of the 9), with the study's dominant factors in all 118 and every rate a rate of
    the family.
  - The identity behind B2's reading, and its uniqueness for the 23.
  - Growth from a stage is growth of that stage taken as a start: exact by the engine's structure, and 369 of 369 tests (s = 1, 2,
    3; 8 rounds each). The same check serves `JUNCTION-MAP-20261119-001`'s gate G.
- **Folded in the same day**, logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`. Before folding, `posthoc_full.py` read
  W from every factor of the minimal recurrence with its own exact Berlekamp–Massey. It reproduced the referee's table, B6's 12 of 12
  and B7's 86 of 86 exactly.
  - **Block, on the short-loop reading.** "Loops of two and three steps are the commonest" and "70 of 70" read W from the rate. The
    corrected table is in The answer. Loops of three steps or fewer are consistent with 12 starts and shown for none.
  - **Narrowing, the explosive kind.** "Their largest group grows without bound" rested on the last round or two before memory ran
    out. F-04 and F-05's groups fall back to 2 to 5 while their counts leap. G-121 is of this kind and is now named.
  - **Not blocks.** B7 holds on all 86 pairs once W is read correctly. B2's "a factor the counts cancel" fits 6 of the 23; in 17
    the reader dropped it. "118 of 122" is 116 of the 122 plus 2 of the referee's 9.
- **Not rechecked by the referee.** B8, and the three fast eight-knot starts beyond rounds 13 to 15 (they agree there, with no
  recurrence found).

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It reported its own session as unreliable and gave no rule.
- **What held.** The loop runs through first-round junctions, not the knots (consistent with B8, and with B6 on its 12). "Open
  places never lengthen the loop" (B7) holds on all 86 pairs once W is read from every factor; the 15 failures first scored were my
  misread W, not the advisor's.
- **What failed.** "Groups stay bounded in rational starts" failed already in the smoke run. "Groups merge without bound" in the
  explosive kind is not what F-04 and F-05 show (referee R1). Its claims that the theta's groups are not maximal, and that round-1
  counts miss the groups, were wrong.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the eddies in the break shapes | **Status:** Partially successful (3 of 7 held as scored; B2 and B7 post hoc; corrected after referee R1) | 118 rational, all in the catalogue's family once W is read from every factor; short loops not shown (12 starts consistent, all with a group of three); an explosive kind whose counts leap; three fast starts undecided |
| Local direction: extending the cluster rule | Continue | What they do is the catalogue's; the rule's map must take in first-round junctions and the excluded overlap |
| Broader exploration: what the cheapest growth builds | Known alternatives | Steady eddies (round-weights) and explosive starts (growing groups) |
| Long-term goal: G17 | Capability gained | The rare kinds named: steady eddies of the family, and explosive growth (the short loops, as first claimed, withdrawn) |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The map with first-round junctions as points: find the loop and its entries in the stage-1 structure, admitting a group of three that shares two knots with a block as a loop of length two | 3/3 — closes the cluster rule's out-of-scope class and its second break | 2/3 — 118 starts with known W to test against | build it on the 36 starts with W = y^2 (1 + y) (10 after the referee's reading) → stop when it predicts their W, or at a start where it cannot | Taken by `JUNCTION-MAP-20261119-001` |
| 2 | The explosive kind: group sizes over rounds, and whether the count has any fixed rate | 2/3 — a different object, possibly faster than any exponential | 2/3 — memory is the limit | follow the largest group with exhausted junctions kept as counters (the advisor's suggestion) → stop at a growth law for the group sizes | Alternative · deferred |
| 3 | A growth that reads only the allowed states (A108) | 3/3 | 2/3 | as in NAE-GROWTH | Alternative · deferred |

## Final report as sent (2026-11-19 10:54 UTC)

**Outcome:** The self-feeding loops hidden where the cluster rule breaks are the same eddies as the catalogue's. Of 122 such starts, 118 grow at a rate that is exactly a member of the catalogue's family, built from the same pieces. That includes the referee's six-knot eddy (W = y⁴(1 + y)). What's new is loops of two and three steps, which no ring makes; every one of them (70 of 70) needs a group of three knots joined at once in the first round. Separately, an explosive kind exists in which the groups keep growing and no fixed rate fits. 3 of 7 frozen predictions held as scored, and 1 more once read correctly. Closed, referee pending.

- **The family, where the rule breaks.**
  - y²(1 + y) is the commonest (36 starts), at the plastic number 1.3247. Then y³(1 + y), y⁴(1 + y), y⁵(1 + y)^k for k = 1 to 3, and three with hung knots or a chain.
  - All 118 rates match a member of the family to 10⁻⁶.
- **Why the rule can't see them.** The loop runs through first-round junctions, not through the knots alone. Restarting the rule at any later stage doesn't help either: 0 of 120 stages fall inside its scope, because the groups of three reproduce every round.
- **So, one extended rule or a new object?** In what they do, one rule covers them: the same round-weights. To find them, the rule's map has to include first-round junctions as points. It also has to admit the case it now excludes, a group of three sharing two knots with another block, which is a loop of length two. "Junctions as valid sets" is the picture for building that map; I haven't built it yet.
- **The explosive kind needs a different object.** Two triangles joined twice and the three-regular six-knot graph grow in leaps (e.g. 465, 4,495, 31,465), and their largest group climbs from 13 to 60 and from 33 to 178. The theta starts the same way by round 18 (groups 5 → 12). It is not a loop with a rate.
- **Undecided:** three eight-knot starts double every round with groups near 8 to 10. No recurrence fits within reach, so they may be two-loop eddies.
- **Real failures:** one more open place can lengthen the loop (15 of 89 pairs). The explosive test reached only 2 of 4 starts within memory, and one of the two failed it.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the eddies in the break shapes | **Status:** Partially successful (3 of 7 held as scored; 1 more post hoc) | 118 rational, all in the catalogue's family, with loops of two and three steps made by groups of three; an explosive kind; three undecided |
| Local direction: extending the cluster rule | Continue | What they do is the catalogue's; the rule's map must take in first-round junctions and its excluded overlap |
| Broader exploration: what the cheapest growth builds | Known alternatives | Steady eddies (round-weights) and explosive starts (growing groups) |
| Long-term goal: G17 | Capability gained | The rare kinds named and measured |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The map with first-round junctions as points, admitting the excluded overlap as a loop of length two | 3/3 — closes the rule's out-of-scope class and its second break | 2/3 — 118 starts with known W to test against | build it on the 36 starts with W = y²(1 + y) → stop when it predicts their W, or at a start where it can't | Selected · awaiting go-ahead |
| 2 | The explosive kind: group sizes over rounds, and whether the count has any fixed rate | 2/3 | 2/3 — memory is the limit | follow the largest group with exhausted junctions as counters → stop at a law for the group sizes | Alternative · deferred |
| 3 | A growth that reads only the allowed states (A108) | 3/3 | 2/3 | as in NAE-GROWTH | Alternative · deferred |

**Corrections:** none for this study. Separately, I folded in the LOOP-CATALOGUE referee's Narrowing: part U wasn't every start the rule can't decide, and a six-knot eddy sat outside both lists. It's logged in docs/CORRECTIONS.md (c3c6829de), and that eddy is now measured here. The catalogue's scorer slips were fixed in a logged amendment, beside the frozen verdicts. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A109 history line: few in kind holds for the steady eddies, while the explosive kind keeps it under challenge. **Basket:** `LOOP-CATALOGUE-20261119-001#1` taken. **Advisor:** Fable 5.2, before the freeze. It reported its own session as unreliable and gave no rule. It was right that the loop runs through first-round junctions and that explosive starts have merging groups. It was wrong that groups stay bounded, and that more open places never lengthen the loop.

**Referee hand-off.** The decision note is `research/BREAK-EDDIES-20261119-001/break_eddies.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check:
- the Berlekamp–Massey reading and the post hoc family match (posthoc.py), especially the cancelled factor in the 23 starts with W = y⁵(1 + y)²;
- stagelib's claim that growth from a stage equals growth of that stage taken as a start;
- the explosive readouts (memory-limited).
