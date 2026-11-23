# Does repeated release need a failing pattern? Pre-registration

Ticket `REVIEW-LEADS-20261123-001G` of epic `REVIEW-LEADS-20261123-001` (follow-up to ticket A, B310; G17 with G1), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged.

## The question

Ticket A found that all seven recorded structures that keep producing fail the operator test by their second step, while 247 of 280 funded fresh draws per law pass it for twelve steps. Is failing the test tied to being a source, a start that releases separate lasting families for ever, or only to growing?

## In standard terms

Whether the bipartite incidence graph of a growing structure that emits infinitely many persistent components must become non-planar, and whether non-planarity arrives sooner (at fewer vertices) for such structures than for other growing ones. A birth with one parent adds a pendant piece and cannot destroy planarity; a birth with several parents destroys it exactly when its parents do not lie around one common region of any drawing.

## Prior work in the program

`python3 -B scripts/track.py objects "repeated release sources and the operator test first failing stage" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "planar incidence graph of structures that emit families indefinitely" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "single edits of the seven-knot source and demand-supplied draws on nine to twelve knots" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`TWO-READERS-ONE-SURVIVING-SIGN-20261121-001` — unrelated object.
`TWO-CHOICE-IMPLICATIONS-20261115-001` — unrelated object.
`READ-ORIGIN-20261120-001` — unrelated object.
`READS-HOLDERS-SOURCES-20261120-001` — same population and the source of every verdict used here: it proved which single edits and which draws release repeatedly; it did not read this test.
`EARLIER-EVENT-AND-LATER-BIRTH-20261122-001` — unrelated object.
`EARN-BUDGET-20261117-001` — unrelated object.
`FORBIDDING-JOIN-20261120-001` — a relative: the seven-knot source under rival grants; not this test.

`REVIEW-LEADS-20261123-001A` (this epic, closed today) — the source of the question: every recorded source fails by step 2; fresh draws mostly pass. Seen there before this freeze: the first failing steps of the seven-knot source (1), the nine-knot drawn source (1) and the 21-knot structure (2). No edit of the seven-knot source and no demand-supplied draw has been read.

## Prior work outside the program

Kuratowski (1930) for the test. Not found: non-planarity as a condition for emitting persistent components under a growth law.

## Settled by construction (stated, not tested)

Failing is monotone in the step. The birth that first makes a stage fail has two or more parents. A start that stalls at once passes.

## What is supplied

The reading; the two populations and their recorded verdicts, which are not recomputed; the horizon; the bars that decide between the two readings of the result. Each is a scaffold.

## Definitions (frozen)

- **Test, pattern, first failing step, growth kind.** As in ticket A, with its code.
- **Q1.** The 53 uniform single edits of the seven-knot source of the reads-holders-sources study, part C, with its recorded verdicts: 16 proved to release repeatedly, 33 proved not to, 4 undecided.
- **Q2.** That study's draws with supply sized to fund the first joins, sizes nine to twelve: 96 with two extra meetings and 96 with three, with its recorded verdicts: 5 proved to release repeatedly, the rest not certified.
- **Horizon.** 12 parent steps or 5,000 knots, under both laws.
- **Per start.** Growth kind; first failing step; the number of knots at the first failing stage; the number of parents of the birth whose addition first makes the stage fail (found by adding that step's births one at a time in the engine's order); for Q1, whether the first failing stage's forbidden sub-pattern uses only knots that the unedited source also has at that step.
- **Independent sources.** The 16 edits of Q1 are edits of one structure and count as one family. With the five draws of Q2 that is six.
- **Reading of the result, fixed now.** Among starts of growing kind in Q1 and Q2 that are not proved sources: if at least 90% fail within the horizon, the test tracks growth and no argument is attempted. If at most 50% fail while every proved source fails, the test separates sources from other growing starts and the thread attempts an argument. In between, both numbers are reported and no argument is attempted.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: ticket A's code reproduces its recorded first failing steps for the seven-knot and nine-knot sources; the recorded verdict counts (16, 33, 4; 5 of 192) are recovered from the earlier study's files. | any fails |
| P1 | Every proved source in Q1 and Q2 fails within the horizon. | a proved source passes at every stage: a candidate counterexample |
| P2 | Among starts of growing kind in Q1, proved sources first fail at a number of knots whose median is no larger than that of the starts proved not to be sources. | the median is larger |
| P3 | Among starts of growing kind in Q1 and Q2 that are not proved sources, at most half fail within the horizon. | more than half fail |

## Runs and stop rule

One script recovers the two populations with their verdicts; one reads the test along each start's growth. Every run stays under ten minutes and under 12 GB. The study stops when both populations are read. It reports the cross-table of verdict against test by growth kind, the knots at first failure, the parents of the breaking birth, and which of the three readings above applies. Nothing is tuned after values are seen; deviations go in `deviations.md`. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed this design cold before the freeze (`research/REVIEW-LEADS-20261123-001/advisor/question_g.md`, `answer_g.json`). Its strongest objection: the test may read growth and not source-hood, since a start that keeps growing soon has a birth whose parents do not lie around one region; the sample of sources is about six and not 21; "by step 3" was fitted to the seven records; and "passing implies not a source" is only the contrapositive of P1. Changes: a comparison matched on growth kind with its reading fixed in advance, knots at first failure in place of the step, the breaking birth and its parents recorded, the inherited sub-pattern checked for Q1, the independent count stated, and the fitted step bound dropped.
