# Is the knots' nesting a distance?: pre-registration

Epic `MEET-DIST-20261118-001` (sub-goal B198, `MEET-TWIST-20261118-001#1`; goal G16; tests A97), 18 November 2026, by Claude, on
the coordinator's go-ahead. Frozen before the run. The canonical K1–K3 test is unchanged.

## The question

The owner's founding premise (A97) is that distance is the only form of information. Presentations of one line by the fewest
betweenness knots differ only in how their knots nest (the bracketing), and their states, hence their disagreement counts, are
identical: before any growth the nesting is information the distances do not carry. Under KF3 the nesting decides how many orders
grow (`MEET-ORDERS-20261118-001`), and the growth's law does not depend on where the line's ends sit (`MEET-TWIST-20261118-001`).
So the grown bases differ. How much of the nesting do the grown disagreement counts reveal, after how many new distinctions, in law
and from one grown base?

## In standard terms

For each presentation P, the law μ_{P,k} of the isomorphism class of the pair (N, disagreement table) of the base after k steps of
KF3. In law: is P ↦ μ_{P,k} injective on bare bracketings (unlabelled rooted binary trees), and on presentations up to mirror? Per
sample: the Bayes probability of recovering the bare bracketing (and the presentation) from one draw of μ_{P,k}, P uniform over the
labelled presentations of one labelling of the line.

## Prior work in the program

`python3 -B scripts/track.py objects "disagreement counts of grown bases reveal how knots nest, presentations of a line" --until 2026-11-18 --exclude MEET-DIST-20261118-001`

`python3 -B scripts/track.py objects "distance is the only form of information, table of disagreement counts determines the base" --until 2026-11-18 --exclude MEET-DIST-20261118-001`

- `DISTANCE-ORDER-20261117-001`: the result used (statement 3(a): the table with N determines these bases), and order read from
  disagreement counts (a relative).
- `DISTANCE-INFO-20261117-001`: same premise (A97) tested on not-all-equal bases: the disagreement count determined every base
  tested through six; a relative, on other bases and with no growth.
- `MEET-GROW-20261118-001` and `MEET-ORDERS-20261118-001`: same population and rule; their findings are the premise here.

## Settled by construction (stated, not tested)

- At k = 0 every presentation has the same table (the line's), so nothing is revealed.
- The grown bases are defined by complement-closed constraints on at most three distinctions, so the table with N determines the
  allowed states (`DISTANCE-ORDER-20261117-001`, statement 3(a)): "what the grown distances reveal" equals "what the grown states
  reveal". Gate G2 checks it on every reached base of five and six to n0 + 3.
- Mirror images have the same laws.
- **The advisor's literal test, settled by hand.** Two fill points' disagreement count is not a function of how far apart their
  knots are in the nesting: for the knots (0,1,2) and (0,2,3) of the end placement it is 4, for (0,1,2) and (0,2,4) of the middle
  placement 6, though each pair shares a pair of distinctions. The count measures steps along the line between the distinctions
  the two triples do not share (the odd-set difference), not steps between knots.

## Ticket B: computations

Code: `job.py`, `checks.py` and `merge.py` with `melib.py` (MEET-ORDERS-20261118-001B's engine, unchanged) in
`experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/`. 4 gate checks pass (the engine's hash; table classes
equal state classes on five and six to n0 + 3; renaming invariance; the hand count at five, k = 1: the bare bracketing named with
chance 13/15 and the presentation 11/15 under the stated prior).

Cases: every presentation up to mirror of lines of 5, 6, 7 (to k = 4) and 8, 9 (to k = 3): 315 cases.

## Predictions (frozen)

Exploration before the freeze (disclosed): the smoke test on the line of five gave, for the bare bracketing, information fractions
0.63, 0.60 and 0.39 at k = 1, 2, 3 (falling), naming chances 13/15, 8/9 and 776/945, a bag-of-knots null that names it with
certainty at k = 2 and 3, and a multiset ablation at chance (4/5) from k = 2. The predictions for six to nine are informed by this.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | The 4 gate checks pass | any fails |
| D1 | In law, from k = 1, every two presentations with different bare bracketings have different table laws (n0 = 5 to 9; the advisor: about 0.8, expecting a first failure at 10, not run) | a pair equal at some k ≥ 1 |
| D2 | In law, from k = 2, every two presentations that are not mirror images have different table laws (the advisor: about 0.85; ties at k = 1 are expected from mirrored self-mirror regions, counted not predicted) | a pair equal at some k ≥ 2 |
| D3 | Per sample, the share of the bare bracketing's information a grown table carries (mutual information over entropy, under the prior) is largest at k = 1 or 2 and smaller at the last k, for every n0 (the trace fades in single samples) | it is largest at the last k for some n0 |
| D4 | KF3's grown table carries less information about the bare bracketing than the bag-of-knots null (k distinct knots revealed as fills, no growth) at every k ≥ 2 where the null exists | KF3 carries at least as much at some such k |
| D5 | From k = 2, the unlabelled multiset of table entries (with N) carries less information about the bare bracketing than the full table, for every n0 | not less at some k ≥ 2 |

Reported with no prediction: the naming chances (bare bracketing, presentation, from the number of orders, from the multiset,
null), the k = 1 ties, and the information about the presentation.

## Runs and stop rule

The shared runner, 315 cases, 12 workers at 1 GB, registered as MEET-DIST-B1; expected under half an hour. Then `merge.py` and the
read-out; the study stops after the read-out, A97's status, the decision note, the referee hand-off and the report.

**Advisor.** Consulted once before the freeze. It reproduced the hand count at five by a bag-of-knots model, found that D2 as
first written (from k = 1) is false at six (a mirrored self-mirror region gives equal k = 1 laws), put D1 at about 0.8 with an
expected failure at 10, judged the original rising-chance and threshold predictions unlikely, and argued that this design tests
memory of the presentation rather than nesting as a distance. Its sharper tests became the null (D4), the multiset ablation (D5)
and the literal test settled by hand above; the information fraction replaces the naming chance as the headline reading, since the
prior is dominated by chains.
