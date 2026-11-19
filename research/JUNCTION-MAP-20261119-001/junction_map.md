# A map that sees loops through first-round junctions

Epic `JUNCTION-MAP-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking `BREAK-EDDIES-20261119-001#1`).
Goal G17. **Referee pending.** Its wording about short loops was corrected on 19 November, when `BREAK-EDDIES-20261119-001`'s
referee withdrew them (see the note there); the predictions and verdicts are unchanged.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `552910bd8` at 11:13 UTC after a pilot (disclosed).
- The run went through the shared runner (`JUNCTION-MAP-B1`, `runs/junction-map`, 94 cases), all ok.
- Code: [maplib.py, mergelib.py, job.py, merge.py](../../experiments/JUNCTION-MAP-20261119-001B/JUNCTION-MAP-20261119-001B-E001_map/),
  with the pilot in `pilot/`.
- Results: [results.json](../../artifacts/JUNCTION-MAP-20261119-001B/JUNCTION-MAP-20261119-001B-E001_map/results.json).

**Words.**
- The **stage** after s rounds is the growth's presentation then, taken as a start: its junctions are the points, and the live ones
  are the last round's.
- The **junction map** is the cluster rule's candidate map of that start, with the rule's one scope cut lifted: a first-round group
  of three that shares two knots with another block is kept, so that the two make a loop of length two.
- The **overlap** is that case.

## The answer

**In the owner's terms.**
- **The stop rule's second case: the map cannot.** Read with first-round junctions as points, and the excluded overlap as a loop of
  length two, the map gets the next round right and the one after wrong. That held on all 36 starts then read as W = y²(1 + y) in
  the pilot (10 of them are, by `BREAK-EDDIES-20261119-001`'s corrected reading).
  Frozen on 94 fresh starts, it held in every one of 261 stages with the overlap, and in none was it wrong earlier or later.
- **Why it fails.** A group of three that shares two knots with a block is not a loop of length two. When the growth goes round it
  a second time it reaches the same junction again, where the unrolled map counts a new one on every lap. This is the same mistake
  as the rule's first break, one junction where the map sees two.
- **Where it works, it is exact.** At every one of the 14 stages free of the overlap and of the rule's breaks, the junction map
  equals the growth for all 8 rounds compared. The controls were two touching knots, a chain of three, and the rings' first stage.
- **The overlap is not peculiar to the break shapes.** It appears two rounds into the ordinary rings of the catalogue, where the
  rule read from the original knots stays exact. So a later stage is not a valid start for the rule. The knot-level map already
  accounts for these overlaps, and the break-shape eddies' loops must be found there.
- **The same overlap read at the knot level also fails.** With the cut lifted on the original start, the map differs from the
  growth by round 2 on all 82 rational break-shape starts tested. Read as an ordinary merged block instead, it differs at round 1.
- **So a different object is needed.** The counts are rational, with the catalogue's round-weights (`BREAK-EDDIES-20261119-001`),
  so a finite description exists: a transfer between kinds of junction. It is not a count of clusters on any candidate map tried
  here.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | the stage presentation grown 8 rounds equals the continued growth | **held** | 282 of 282 stages |
| J1 | where the stage holds the overlap, the map is right at round s + 1 and wrong at s + 2 | **held** | 261 of 261 |
| J2 | where the stage is clean, the map is exact | **held** | 14 of 14 |
| J3 | the knot-level cut-lifted map is wrong by round 2 on every rational break-shape start | **held** | 82 of 82 |

4 of 4 held. Seven further stages hold the rule's first break, a merged block with a missing pair; they are reported but not scored.

## Why it holds

- **The stage gate.** In complete rounds, a new junction's parents are the last round's junctions, and the policy reads only the
  present presentation (`FRESH-COUNT-20261118-001`). So the growth from a stage is the growth of that stage taken as a start. G
  checks this on 282 stages.
- **One round right, then wrong.** At round s + 1 the map's clusters of two points are exactly the stage's candidate pairs and
  groups. From round s + 2 the unrolled 2-cycle offers a second lift of the same pair of junctions, which the growth does not make.
  This is argued from the counts, not proved. The identification is the one the advisor could not make exact.

## Known results, and what this adds

- **Known.** The cluster rule and its cover (`CLUSTER-ALL-20261119-001`, `RING-PAIR-20261119-001`; lattice animals, Fisher and Essam
  1961). The rational counts of the break shapes (`BREAK-EDDIES-20261119-001`).
- **What this adds.** The obvious extension, a later stage with the overlap admitted as a short loop, fails in a fixed way that the
  overlap alone predicts. A later stage is not a valid start for the rule, even for ordinary rings. So the break shapes' eddies need
  an object other than clusters on a candidate map.

## Limitations

- The failure is shown for the overlap read as a loop of length two, and as a merged simplex. Another reading of the same overlap is
  not excluded.
- The population is BREAK-EDDIES' rational starts and the catalogue. The explosive kind is not tested here.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **The answer is unreliable.** The advisor had no tools, yet it described files and runs that do not exist (`eddies.py`,
  `/tmp/jm_adv/`).
- **Its checkable claims are false.** The W = y²(1 + y) starts do approach the plastic number, with three-round mean ratios of 1.324
  to 1.327. The stage presentation does equal the continued growth, 282 of 282.
- **One usable point.** It asked for a gate on the stage presentation, which is G.
- **Kept as a direction.** It suggested that in the stage the loop of length two is a ring of four (two junctions and two knots,
  joined by two-knot places).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the junction map | **Status:** Successful (4 of 4 held; the stop rule's second case) | The map cannot predict the break-shape eddies' loops, and it fails exactly where the overlap stands, with the mechanism named |
| Local direction: extending the cluster rule to the break shapes | Practically exhausted | Excluding, unrolling and merging the overlap all fail, at the stage level and at the knot level |
| Broader exploration: what the cheapest growth builds | Known alternatives | The steady eddies' counts are rational, so a transfer between kinds of junction should describe them |
| Long-term goal: G17 | Obstruction learned | Clusters on a candidate map cannot carry the break shapes' loops |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A transfer between kinds of junction: classify the junctions of a W = y²(1 + y) start by their local pattern (parents, fresh count, demand, and their parents' kinds) and look for a finite set of kinds whose counts follow a fixed matrix | 3/3 — the finite object the break shapes need, read from the growth | 2/3 — the counts and the growth are at hand | refine the kinds on the 36 starts → stop at a finite matrix whose root is the plastic number on all 36, or at kinds that never settle | Selected · awaiting go-ahead |
| 2 | A growth that reads only the allowed states (A108) | 3/3 | 2/3 | as in NAE-GROWTH | Alternative · deferred |
| 3 | The explosive kind (BREAK-EDDIES #2) | 2/3 | 2/3 | as there | Alternative · deferred |

## Final report as sent (2026-11-19 11:16 UTC)

**Outcome:** The stop rule's second case. A map with first-round junctions as points cannot predict the short loops in the break shapes, and it fails for a reason the frozen test pins down exactly. It reads the rule's excluded overlap (a group of three sharing two knots with another block) as a loop of length two, but that isn't a loop: going round it a second time reaches the same junction, where the map counts a new one on every lap. So the map gets the next round right and the one after wrong at every stage holding the overlap (261 of 261), and is exact at every stage free of it (14 of 14). 4 of 4 frozen predictions held. Closed, referee pending.

- **The overlap is everywhere, not only in break shapes.** It appears two rounds into the catalogue's ordinary rings too, where the rule read from the original knots stays exact. So a later stage isn't a valid start for the rule.
- **The other readings fail too.** Admitting the overlap at the knot level fails by round 2 on all 82 rational break-shape starts. Merging it into an ordinary block fails at round 1.
- **What's needed instead.** The break-shape counts are rational with the catalogue's round-weights (last study), so a finite description exists. It should be a transfer between kinds of junction, not a count of clusters on a candidate map.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the junction map | **Status:** Successful (4 of 4 held; the stop rule's second case) | It cannot predict the short loops, and it fails exactly where the overlap stands, with the mechanism named |
| Local direction: extending the cluster rule to the break shapes | Practically exhausted | Excluding, unrolling and merging the overlap all fail, at the stage level and the knot level |
| Broader exploration: what the cheapest growth builds | Known alternatives | Rational counts, so a transfer between kinds of junction should describe them |
| Long-term goal: G17 | Obstruction learned | Clusters on a candidate map cannot carry these loops |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A transfer between kinds of junction, read from the growth on the 36 starts with W = y²(1 + y) | 3/3 — the finite object the break shapes need | 2/3 — counts and growth at hand | refine junction kinds (parents, fresh count, demand, parents' kinds) → stop at a finite matrix with root the plastic number on all 36, or kinds that never settle | Selected · awaiting go-ahead |
| 2 | A growth that reads only the allowed states (A108) | 3/3 | 2/3 | as in NAE-GROWTH | Alternative · deferred |
| 3 | The explosive kind | 2/3 | 2/3 | as in BREAK-EDDIES | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (obstruction learned). **Assumptions:** none new. **Basket:** `BREAK-EDDIES-20261119-001#1` taken. **Advisor:** Fable 5.2, before the freeze. Its answer was unreliable: with no tools, it described files and runs that don't exist, and its two checkable claims were false (I checked both). Its one usable point was to gate the stage presentation first, and gate G does that: 282 of 282.

**Referee hand-off.** The decision note is `research/JUNCTION-MAP-20261119-001/junction_map.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check:
- the stage gate's argument (growth from a stage equals growth of that stage taken as a start);
- that maplib's lifted cut is the reading the go-ahead meant;
- the one-round-right, next-round-wrong mechanism on one small start by hand.
