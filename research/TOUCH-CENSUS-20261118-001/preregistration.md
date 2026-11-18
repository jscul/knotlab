# Which dimensions does the cheapest growth give across arrangements of touching knots? Pre-registration

Epic `TOUCH-CENSUS-20261118-001` (the coordinator's go-ahead on `FIRST-KNOT-20261118-001#3`; goals G2, G17 and G1), 2026-11-18.
Lemmas (ticket A) written before the census; census code (ticket B) written and gated before this freeze; launched by the thread
with the shared runner after it. The canonical K1–K3 test is unchanged.

## The question

Under the parity law, the cubic study's joining rule and the fewest counts, `FIRST-KNOT-20261118-001` found that two touching knots
grow two-dimensionally and that m mutually touching knots of m + 1 places grow m-dimensionally. Nothing chooses how first knots are
arranged (the owner's no-choice direction, lesson 7.3), so ask what is typical: over every small arrangement of touching knots,
which dimensions occur, how often, and does one rule predict every dimension?

## In standard terms

Every connected multigraph on at most five vertices with vertex weights 3 to 5 and degree at most the weight (vertices: parity
constraints of that arity; edges: shared variables; loose variables: weight − degree), up to isomorphism (26,441 classes: 3, 22,
154, 1,760 and 24,502 on one to five vertices); grown by upward closure under the least count rule; the growth exponent of the
number of constraints per round.

## What is given

The parity law, the joining rule, the fewest counts (`FRESH-COUNT-20261118-001`), the arrangement (round 0). Nothing is read but
the current pattern.

## The rule (frozen; found after `FIRST-KNOT-20261118-001`'s read-out, its general form frozen here)

A birth is an offshoot of demand 1 whose parent is not itself an offshoot of demand 1; its partner is its unique candidate; births of
one round with a common partner form a class (two sibling births, each the other's partner, form one class of two). **The dimension
of the fewest growth is the largest class ever formed; 1 if the growth runs forever without a birth; 0 if it closes.** The advisor
proposed the split and the birthless exception (a ring of five four-place knots regrowing as pair-groups).

## Measurement

Up to 30 rounds or 6,000 junctions (cut at a round's end); dimension 0 if closed; otherwise k + 1 for the least k such that the k-th
differences of junctions per round are constant and nonzero over the last seven rounds; an unsettled case is rerun to 45 rounds or
25,000 junctions. The rule is computed from the births, separately from the measurement. Weights: uniform over distinct
arrangements, and by labelled count (knots labelled, places not: n!/|automorphisms|); every share reported per number of knots.
"Typical" is said only of what holds under both weights and within each number of knots.

## Prior work in the program

Searches (`--until 2026-11-18 --exclude TOUCH-CENSUS-20261118-001`):

`python3 -B scripts/track.py objects "dimension of cheapest growth of touching knot arrangements" --until 2026-11-18 --exclude TOUCH-CENSUS-20261118-001`
`python3 -B scripts/track.py objects "arrangements of touching parity knots typical rare" --until 2026-11-18 --exclude TOUCH-CENSUS-20261118-001`
`python3 -B scripts/track.py objects "fewest counts chains of offshoots" --until 2026-11-18 --exclude TOUCH-CENSUS-20261118-001`

- `FIRST-KNOT-20261118-001`, `FRESH-COUNT-20261118-001` — the predecessors: the same growth on two-knot starts and one seed; this
  study takes all small arrangements.
- `ROW-ARRANGE-20261118-001`, `COUNT-BALLS-20261118-001`, `CUBE-DOUBLING-20261118-001` — relatives on betweenness bases (readings of
  the number of orders; ball growth; the cheapest growth's orders); not this population.
- `WEAVE-MIX-20261117-001`, `WEAVE-PAIR-20261118-001` — arrangements of not-all-equal knot classes on a weave; unrelated object.
- `KNOT-SWITCH-20261118-001`, `MEET-ORDERS-20261118-001` — betweenness growth; unrelated.
- `LOGIC-AXIS-20261107-001`, `LOGIC-CIRCLE-20261107-001`, `EXACT-TOWERS-20261029-001`, `OPEN-END-GROWTH-20261107-001`,
  `SIMPLEX-GASKETS-20261029-001`, `SIGNED-SUBDIVISION-20261029-001`, `CHAIN-TRANSFER-20261106-001`, `SPLICE-TREE-20261102-001`,
  `BRACE-TREE-20261105-001`, `BOND-CHAIN-20261108-001`, `KNOT-COMPETITION-20261019-001`, `DISTANCE-20261108-001`,
  `KNOT-COUPLING-20261031-001`, `JUNCTION-READ-20261106-001` — unrelated objects or populations.

## Prior work outside the program

Enumeration of small multigraphs up to isomorphism; the median-graph and event-structure picture cited in the predecessors. No
census of growth exponents over arrangements is known to the thread.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Three gate checks pass (`checks.py`): the canonical form counts the arrangements of up to three knots as brute-force isomorphism does (179 classes, 787 labelled); the measured dimension and the rule are 0, 2, 1, 3 and 4 on five known starts; a round-1 stall is recorded | any fails |
| P1a | Every settled arrangement that grows without a birth has dimension 1 | one does not |
| P1b | Every settled arrangement with a birth has dimension equal to its largest class | one does not |
| P2 | Among settled growing arrangements, 2 is the most common dimension; dimension 3 or more occurs in under 2% of all arrangements, both by distinct count and by labelled count | either fails |
| P3 | No settled dimension above 4, no unsettled case left after the rerun, and exactly one arrangement of dimension 4 (four mutually touching five-place knots) | any fails |
| P4 | Every stall is in round 1 (Lemma 1) | a later stall |
| P5 | The stall share rises with the number of knots from two to five and exceeds 40% at five; among settled growing arrangements the share of dimension 2 rises and that of dimension 1 falls from two to five knots | any part fails |
| P6 | No distinction has one value in every allowed state, in any arrangement | one does |

**Exploration disclosed.** A pilot on 300 random arrangements of at most four knots (the same growth code, an earlier dimension
reader without the rerun): closed 69, stall 50, dimension 1 in 37, 2 in 141, 3 in 2, 4 in 1; the unsplit rule matched every settled
case. The census code's first shard was run once to time it (41 arrangements: closed 17, stall 12, dimension 1 in 6, 2 in 5, 4 in 1).

## Runs and stop rule

`job.py` through the shared runner: 265 shards of 100 arrangements, 8 workers, 2G per case, a 3,600-second case timeout; expected
15 to 40 minutes, registered in the long-running index. `merge.py` scores G and P1 to P6. Stop: one run, its read-out, referee
hand-off, report.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It proposed splitting the rule into its parts, a likely counterexample to
"nothing grows without a birth" (a ring of five four-place knots, outside the pilot's four knots), the rerun of unsettled cases,
computing the rule separately from the measurement, the tighter 2% bound, the exact count of dimension 4, the stall-share
prediction, both weightings reported per number of knots, and that the cutoffs of five knots and five places belong in the
assumptions register. It also suggested freezing "no birth after round 2"; the thread did not, since a relay starts births later
(`FIRST-KNOT-20261118-001` Theorem 3).
