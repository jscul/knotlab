# Does the meeting pattern grow on its own?: pre-registration

Epic `MEET-GROW-20261118-001` (`MEET-ORDERS-20261118-001#1`; goals G16 and G1; tests A97), 18 November 2026, by Claude, on the
coordinator's go-ahead. Frozen before the run; the exploration that shaped it is disclosed below. The canonical K1–K3 test is
unchanged. Words as in `MEET-ORDERS-20261118-001` and the glossary (bracketing, bare bracketing, halves, odd set).

## The question

`MEET-ORDERS-20261118-001` found that under KF3 the number of orders depends on how the knots' meeting pattern sits along the
line (the bracketing), and, post hoc, that the labelled base counts and odd-set weights follow the meeting pattern itself (the
knots as sets of distinctions, the line ignored). KF3 reads the knots only through the co-knotted pairs. So: is the growth of the
co-knotted pairs carried exactly, label for label, from one presentation to another by an isomorphism of their meeting pattern,
at every new distinction, even though the states differ and the numbers of orders differ? If so, how the knots meet grows by
itself under KF3, and the states only decide how many orders the grown pattern carries.

## In standard terms

Two presentations P, P′ of the path's threshold split system by betweenness triples (polygon triangulations with different marked
sides) whose triple systems are isomorphic by φ. KF3 is a Markov chain on (allowed states, co-knotted pairs); the claim is that the
law of the co-knotted pair graph process from P, relabelled by φ, equals its law from P′ at every time.

## Prior work in the program

`python3 -B scripts/track.py objects "pair graph grown by KF3 from presentations with the same meeting pattern" --until 2026-11-18 --exclude MEET-GROW-20261118-001`

`python3 -B scripts/track.py objects "isomorphism of hypergraphs carrying a Markov growth of co-knotted pairs, polygon triangulations rotated" --until 2026-11-18 --exclude MEET-GROW-20261118-001`

`python3 -B scripts/track.py objects "presentations of a line by betweenness knots, bracketings, meeting pattern" --until 2026-11-18 --exclude MEET-GROW-20261118-001`

- `MEET-ORDERS-20261118-001`: same object and population; this study's source (its Theorem 1, its census, and the post hoc
  meeting-pattern reading this study freezes and extends).
- `STATE-RULES-20261117-001`: KF3 itself and the six-starts (a relative).
- `OVERLAP-READ-20261111-001`: unrelated (not-all-equal patterns read back).
- `RULER-FLAT-20261111-001` and `PERIODIC-READ-20261111-001`: unrelated (six-regular weaves; returned by the word
  "isomorphism").

## Prior work outside the program

None found for this growth rule. The advisor reads the presentations of one meeting pattern as one triangulation with different
marked sides, and suggests the mechanism of a twist: moving the marked side past a distinction v with neighbours u, w substitutes
the parity u ⊕ v ⊕ w for v, a bijection on states that keeps the co-knotted pairs and the state count but not the number of orders.

## Exploration before this freeze (disclosed)

In the scratchpad, with this study's code: for every pair of presentations with the same meeting pattern, the labelled pair-graph
distribution is carried by some meeting-pattern isomorphism at every level for five to n0 + 4 (10 pairs) and for six to n0 + 3
(31 pairs); the joint distribution with each state's option profile is carried for five and six to n0 + 2. Within one presentation
the same pair graph is reached with different state sets whose options differ (510 pair graphs for five to n0 + 3), so the
correspondence is not one of pair graphs alone.

## Settled by construction (stated, not tested)

- Mirror images are carried (renaming i ↦ n − 1 − i).
- At the first two new distinctions the claim follows from `MEET-ORDERS-20261118-001`'s Lemmas A and B: the options are the fills
  of the knots and two re-bracketing fills per knot sharing a pair, each adding the same new pairs whichever the line.
- Different meeting patterns start from different pair graphs, since the pair graph of a bracketing determines its knots.

## Ticket B: computations

Code: `job.py`, `checks.py`, `merge.py` and `melib.py` (MEET-ORDERS-20261118-001B's engine, copied unchanged, same sha256) in
`experiments/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph/`. 6 gate checks pass before this freeze (the engine's
hash; mirror images carried; three meeting patterns for six; a digest mutant; digests against a brute-force comparison through
every isomorphism on all ten pairs of five; renaming invariance).

Cases: labelled KF3 from every presentation up to mirror: five to n0 + 5 (3), six to n0 + 4 (7), seven to n0 + 4 (22), eight to
n0 + 4 (66), nine to n0 + 3 (217); 315 cases. Six to n0 + 5 was planned and dropped before the freeze: a smoke test showed the
five-start cases to n0 + 5 need over 3.5 GB each, and six to n0 + 5 holds roughly thirty times more labelled bases.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | The 6 gate checks pass | any fails |
| P1 | For every two presentations with the same meeting pattern, one meeting-pattern isomorphism carries one's labelled pair-graph distribution onto the other's at every level, for all five sizes and depths (advisor: about 85%; if it fails, first at depth, six at n0 + 4 or + 5; six is run to + 4) | one pair not carried at one level |
| P2 | Two different meeting patterns have different pair-graph distributions up to renaming at every level to n0 + 3 | equal at some level |
| P3 | The labelled base counts at every level depend only on the meeting pattern | otherwise |
| P4 | The joint distribution of the pair graph with each state's option profile (cost and new pairs of each option) is carried, to n0 + 3 below each case's depth (advisor's discriminator: carried means a state-by-state correspondence, the twist; not carried means averaging) | one pair not carried |

**What would count against the account.** P1 failing means the line's placement changes how the pairs grow, so the two layers
are not separate. P4 failing with P1 holding means the agreement is an average over states, not a correspondence.

**The headline, stated before running.** Under KF3 the meeting pattern grows on its own: its co-knotted pairs grow with the same
law, label for label, whichever way the pattern sits along the line, and only the number of orders depends on the placement.

## Runs and stop rule

The shared runner in two launches: the three five-start cases to n0 + 5 (3 workers, 5 GB each; long run MEET-GROW-B1) and the
other 312 (8 workers, 1.5 GB each; MEET-GROW-B2); expected under an hour. Then `merge.py` and the read-out. The study stops after the
read-out, A97's status, the decision note, the referee hand-off and the report.

**Advisor.** Consulted once before this freeze: P1's probability and where it would fail, the twist mechanism, the discriminator
that became P4, the point that the start already separates meeting patterns (P2 is therefore read from the first new distinction
on), and the name "middle-blind" for the property (not adopted; the note says "the meeting pattern grows on its own").
