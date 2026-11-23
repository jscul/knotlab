# The operator test as a yes-or-no reading of growth: pre-registration

Ticket `REVIEW-LEADS-20261123-001A` of epic `REVIEW-LEADS-20261123-001` (takes B310; G1, with G18 and G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Sonnet sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged.

## The question

The six-rule study classified closed parity patterns by whether a signed operator reading with no ordinary state exists. That test can be read on every stage of a growing structure, where it needs no scale and no fitted exponent. Two questions: does the reading say more than the number of independent loops, and does ordinary growth keep passing longer than a rewiring with the same births? A third: which closed parts met in growth admit the signed reading.

## In standard terms

The object is the bipartite incidence graph of knots and distinctions. The test is planarity: a planar graph is one that can be drawn without crossings, equivalently one with no K5 or K3,3 minor (Kuratowski 1930, Wagner 1937). For a closed arrangement of parity constraints with every variable in two constraints, a quantum (operator) solution with no classical assignment exists for some choice of signs exactly when the graph is not planar (Arkhipov 2012). For stages with loose distinctions, not-all-equal knots or more than two holders the theorem says nothing and the test is only a reading of shape. Quantities: first failing parent step, loop (cycle) rank, and bounds on the skewness (fewest edges whose removal gives a planar graph).

## Prior work in the program

`python3 -B scripts/track.py objects "sharing pattern operator test first failing stage of growth" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "planar graph Kuratowski minor of the knot-distinction incidence graph" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "labelled trees with extra meetings grown by ordinary growth" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`FOUR-READINGS-20261120-001` — a relative: it classified 173 closed patterns by the operator test; this study reads the same test on every stage of growth and uses its classification as the code gate.
`MERGE-BURST-20261119-001` — same population in part (explosive starts); it read them by blocks, not by this test.
`ERASURE-AND-CLOSING-SIGNS-20261121-001` — a relative: it counted closed parts that admit the reversed sign in drawn trees and explosive draws; this study adds open stages, first failing steps and a rewired comparison.
`NAE-METRIC-20261118-001` — unrelated object (bond distance as a metric).
`JOINT-BRAID-READS-20261114-001` — unrelated object.
`FIRST-KNOT-20261118-001` — same population in part (starts grown by the cubic rule); it measured growth, not this test.
`TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001` — same population in part (trees with two extra meetings); it measured whole closure, not this test on open stages.
`INFLUENCE-CONE-20261120-001` — unrelated object (edit influence); shares the tree weighting.
`THREE-READERS-AND-GROWTH-20261120-001` — unrelated object; shares the tree weightings.

Seen before this freeze, by the thread's own abstract checks of 2026-11-23 (`docs/prompts/missed_leads_checks/`, private): the benchmark constructions (cubic passes to depth 3 and fails at depth 4; pinwheel and polygonal control pass; bounded-bond fails from a 28-knot window). No recorded source or fresh draw has been read.

## Prior work outside the program

Kuratowski (1930) and Wagner (1937) for the test; Arkhipov (2012) for the operator reading; MacLane (1937) for the equivalent statement that the allowed changes have a generating set using each distinction at most twice. Not found: the test read along a growth law of this kind.

## Settled by construction (stated, not tested)

Failing is monotone in the parent step, since growth only adds knots and distinctions. A stage with loop rank below 4 passes. A start with only one-parent births never fails. Under even signs the all-zero word is allowed, so 'admits' always means: for some choice of one odd knot.

## What is supplied

The reading itself; the populations, weightings, seeds and horizons; the rewired comparison; the removal bounds. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Pattern of a stage.** One node per knot and one per distinction; a link when the knot holds the distinction.
- **T.** A stage passes when that pattern is planar (`networkx.check_planarity`), and fails otherwise.
- **Loop rank.** Links minus nodes plus connected parts.
- **First failing step** of a start: the least parent step whose stage fails, within the horizon.
- **Removal bounds.** Lower: over connected parts with K ≥ 3 knots, max(0, P − (3K − 6)) with P the number of distinct pairs of knots that share a distinction. Upper: remove one shared distinction lying on the forbidden sub-pattern the routine returns, repeat until the stage passes, count removals.
- **Growth kind** within the horizon: stalled; bounded (births per step never above the largest of the first four steps); growing (otherwise). The share of one-parent births is recorded beside it.
- **Rewired comparison.** Replay the start's ordinary history. At each parent step keep the number of births and each birth's number of parents and of fresh distinctions, and draw each birth's parents uniformly without replacement from the knots that still hold a loose distinction at that step. If fewer are available the birth takes fewer and the shortfall is recorded. Eight replicas per start, seeds 2026112310 to 2026112317.
- **Closed parity part.** A connected part with no loose distinction in which every knot is a parity knot. It admits when, for some single odd knot, commuting two-valued operators satisfy every knot and no assignment does.
- **Populations.** P1, the four constructions of the shape benchmark: cubic to depth 6 or 20,000 knots, pinwheel to depth 5, polygonal control to depth 8, bounded-bond windows 1 to 4. P2, recorded sources under both laws to 16 parent steps or 20,000 knots: the seven-knot source, the nine-knot drawn source, the 21-knot structure with two clocks, the five-founder clock, and the three archived explosive starts. P3, fresh draws with seed 2026112301: sizes four to eight with equal weight, a uniform labelled tree at each size, each knot filled to three places and given one more loose distinction with chance 1/4, in four arms with 0, 1, 2 and 3 uniform extra meetings, 256 draws per arm per law, grown 12 parent steps or to 5,000 knots, stalls kept in every denominator.
- **Knot-side check.** On five small parity structures (two split three-place knots; the five-knot closure of the closing-sign study; three closed parts met in P3 with at most 14 distinctions), compare the chance of every change-answer word under the recorded counting rule with the chance from drawing a uniform set of knots and reading each distinction as the parity of its drawn holders.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates. On the 173 recorded simple sharing patterns the code's fail verdict equals the recorded admit verdict (115 admit). The planarity routine agrees with a brute-force minor search on every pattern of at most six knots. A mutant that unlinks the second holder of every shared distinction passes everything. The knot-side check agrees on all five structures. | any fails |
| P1 | Replication of what was seen before the freeze: cubic passes to depth 3 and fails from depth 4; pinwheel and polygonal control pass at every depth; bounded-bond fails from window 2. | any differs |
| P2 | T is not a function of loop rank: some two reached stages have equal loop rank, one passing and one failing. The least loop rank of a failing reached stage is reported per population and law. | no such pair exists |
| P3 | Ordinary growth keeps passing at least as long as its rewiring: among P3 starts in which the start or any of its eight rewirings fails within the horizon, the start's first failing step is no earlier than the median of its rewirings' in at least three quarters. | the share is below 3/4 |
| P4 | Every closed parity part met in P2 and P3 admits exactly when it fails T. | one disagrees |

## Runs and stop rule

One census script per population writes one JSON line per stage. The study stops when the three populations and the checks are done. It reports the smallest failing reached stage under each law, whether any start of bounded kind fails, the cross-table of growth kind against T, the comparison with the rewiring, and the benchmark. Every run stays under ten minutes and under 12 GB; a longer run is not started, the partial result is reported instead. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the six designs cold before this freeze (`research/REVIEW-LEADS-20261123-001/advisor/`, question and answer kept). Its strongest objection here and the change made: T mostly tracks loop count, the theorem covers only closed two-holder parity parts with free signs, and the first predictions were false by reasoning (one-parent births can more than double and never fail). Changes: loop rank is reported beside T, a rewired comparison with the same births and parent-group sizes was added, the sign quantifier is stated, the lower bound counts distinct pairs of knots, and the predictions about growth kind were replaced by P2 and P3.
