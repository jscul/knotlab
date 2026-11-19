# The eddies in the cluster rule's break shapes

Epic `BREAK-EDDIES-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking
`LOOP-CATALOGUE-20261119-001#1`). Goal G17. **Referee pending. One over-cap start's regrowth is pending (see Record).**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `243a0fd17` at 08:16 UTC after a pilot (disclosed).
- The run went through the shared runner (`BREAK-EDDIES-B1`, `runs/break-eddies`, 122 cases on 3 workers): 120 finished. Two,
  the theta and one eight-knot start, went over the runner's 3.5 GB per case.
- The referee's three six-knot shapes from `LOOP-CATALOGUE-20261119-001`'s R1 were added after the freeze as readouts
  (`BREAK-EDDIES-B2`, `runs/break-eddies-ref`, 9 starts with a 10 GB child; amendment of 08:51 UTC).
- The theta and the other over-cap start were regrown with a 10 GB child (`pilot/theta_groups.py`, post hoc). The theta again went
  over at round 18 (2,258 junctions), with its largest group rising 5, 5, 5, 5, 8, 12 over the last rounds. The other start is
  **pending**.
- Code: [job.py, job_ref.py, merge.py, posthoc.py, stagelib.py, breaklib.py](../../experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/),
  with the pilot in `pilot/`.
- Results: [results.json](../../artifacts/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/results.json) and
  [posthoc.json](../../artifacts/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/posthoc.json).

Words as in `LOOP-CATALOGUE-20261119-001`. A **group of three** is a first-round group of three or more knots: pairwise
candidates with no common neighbour, joined by one junction in round 1. The rule calls it a hyperedge.

## The answer

**In the owner's terms.**
- **The eddies hiding in the break shapes are the same eddies.** Of the 122 self-feeding starts the cluster rule could not read,
  plus the referee's shapes, 118 grow at a rate that is exactly a member of the catalogue's family. That is, the rate solves
  W = 1 for a round-weight W built from the same pieces:
  - y per knot of the loop;
  - (1 + y) per spare or lone hung knot;
  - 1 + y + y² for a hung knot with a spare;
  - 1 + y(1 + y)² for a hung knot with two;
  - 1/(1 − y) for an endless chain.

| Round-weight W | Starts | Rate |
| --- | --- | --- |
| y^2 (1 + y) | 36 | 1.3247 (the plastic number) |
| y^3 (1 + y) | 6 | 1.2207 |
| y^4 (1 + y) | 8 (incl. the referee's two triangles joined once) | 1.1673 |
| y^5 (1 + y) | 9 | 1.1347 |
| y^5 (1 + y)^2 | 23 | 1.2628 |
| y^5 (1 + y)^3 | 29 | 1.3854 |
| y^5 (1 + y)/(1 − y) | 5 | 1.4196 |
| y^5 (1 + y + y²) | 1 | 1.2032 |
| y^5 (1 + y(1 + y)²) | 1 | 1.2825 |

- **What is new: loops of two and three steps.** No ring of knots makes a loop shorter than four steps. Three knots in a ring are
  joined in one go, four make a pair with two common neighbours, six make two groups of three. Here loops of two and three steps
  (W = y^2 (1 + y), y^3 (1 + y)) are the commonest. Every one of the 70 rational starts with a loop of three steps or fewer holds a
  group of three. So **groups of three are what make the short loops**: the loop runs through first-round junctions, not through
  the knots alone.
- **Why the rule can't see them, even later.** The growth continued from any stage is the growth of that stage taken as a start,
  so the rule can be applied at any stage. At the stages after 0 to 3 rounds, none of the 120 starts is inside its scope and free
  of its known breaks. The groups of three reproduce themselves every round, so restarting the rule later does not recover the
  loop.
- **So does one extended rule cover them? In what they do, yes; in finding them, not yet.** Their counts are the catalogue's,
  piece for piece. What is missing is the rule's map: it would have to include the junctions of the first round as points, and to
  take in the case it now excludes, a group of three that shares two knots with another block, which is a loop of length two.
  "Junctions as valid sets" is the right picture for building that map. It is not built here.
- **A second, different kind: explosive starts.** Two triangles joined twice, the three-regular six-knot graph (the referee's
  shapes) and, by its last rounds, the theta grow in leaps: 22, 38, 127, 720, or 80, 32, 31, 465, 4,495, 31,465. Their largest group
  grows without bound (13, then 60; 33, then 178). This is not a loop with a fixed rate: groups keep merging, as the advisor
  predicted. These need a different object, one that follows group sizes, not a round-weight.
- **A third, undecided: three fast starts** at eight knots double every round (32,385, 61,165, 116,108, 221,417), with groups
  staying near 8 to 10. No recurrence fits within reach. They may be two-loop eddies (algebraic), which none of the catalogue's
  entries to eight knots was.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| B1 | pilot recurrences persist | **held** | 26 of 26, to 41 to 60 rounds |
| B2 | W nonnegative integers, W(1) ≥ 2 | failed as scored | 93 of 116; the 23 others read W from the irreducible factor, which drops a factor the counts cancel (x^7 − (1 + x)^2 = (x^2 + x + 1)(x^5 − x^4 + x^2 − x − 1)); matched against the family, all 116, plus the referee's 2, are members (post hoc) |
| B3 | readout: largest group in rational starts | — | 9 to 14 at round 40, growing slowly |
| B4 | explosive starts' groups exceed rational ones' | failed | measured on 2 of the 4 (the others went over the cap): one exceeds, one stays at 8. The referee's explosive shapes reach 60 and 178, and the theta's regrowth rises to 12 by round 18 (readouts) |
| B5 | theta: no recurrence of order ≤ 8 | not decided | over the cap in the frozen run, and again at 10 GB (18 rounds, too few to decide) |
| B6 | loops of ≤ 3 steps need a group of three | **held** | 70 of 70 |
| B7 | more open places never lengthen the loop | failed | 74 of 89 pairs; in 15, one more open place gives a longer loop |
| B8 | no later stage inside the rule and break-free | **held** | 0 of 120 |

3 of 7 held as scored (B3 is a readout); B2 holds once read correctly (post hoc); B5 could not be decided within memory.

## Known results, and what this adds

- **Known.** As in `LOOP-CATALOGUE-20261119-001`: transfer matrices and rational series; the trinomials x^(L+1) − x − 1; the plastic
  number (the real root of x^3 = x + 1, the smallest Pisot number).
- **What this adds.**
  - The cluster rule's break shapes hide no new kind of steady eddy, only shorter loops made by groups of three.
  - A separate explosive kind exists, in which groups grow without bound.
  - Restarting the rule at a later stage does not recover either kind.

## Limitations

- **Rational means a recurrence found** by Berlekamp–Massey with twice its order to spare, holding to the horizon (41 to 60 rounds,
  or 300,000 junctions). The family match is to 10^(−6) in the rate, and it was done after the read-out.
- **The explosive class** is read on 7 starts of the referee's shapes, each stopped by memory after 9 to 14 rounds, and on the theta
  to 18 rounds. One eight-knot start is pending.
- **The population** is LOOP-CATALOGUE's part U main run (122 exponential starts), not its pending 1,080, and the referee's 9.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It reported its own session as unreliable and gave no rule.
- **What held.** The loop runs through first-round junctions, not the knots (consistent with B6 and B8). The explosive kind is
  groups merging without bound, seen in the referee's shapes.
- **What failed.** "Groups stay bounded in rational starts" failed already in the smoke run. "Open places never lengthen the loop"
  (B7) failed in 15 of 89 pairs. Its claims that the theta's groups are not maximal, and that round-1 counts miss the groups, were
  wrong.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the eddies in the break shapes | **Status:** Partially successful (3 of 7 held as scored; B2 post hoc) | 118 rational, all in the catalogue's family, with loops of two and three steps made by groups of three; an explosive kind with unbounded groups; three fast starts undecided |
| Local direction: extending the cluster rule | Continue | What they do is the catalogue's; the rule's map must take in first-round junctions and the excluded overlap |
| Broader exploration: what the cheapest growth builds | Known alternatives | Steady eddies (round-weights) and explosive starts (growing groups) |
| Long-term goal: G17 | Capability gained | The rare kinds named: short loops through groups of three, and explosive growth |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The map with first-round junctions as points: find the loop and its entries in the stage-1 structure, admitting a group of three that shares two knots with a block as a loop of length two | 3/3 — closes the cluster rule's out-of-scope class and its second break | 2/3 — 118 starts with known W to test against | build it on the 36 starts with W = y^2 (1 + y) → stop when it predicts their W, or at a start where it cannot | Selected · awaiting go-ahead |
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
