# Why how the knots meet changes the number of orders: pre-registration

Epic `MEET-ORDERS-20261118-001` (`KNOT-CAP-20261117-001#2`; goals G1 and G16; tests A97), 18 November 2026, by Claude, on the
coordinator's pick. Frozen before the run; the exploration that shaped it is disclosed below. The canonical K1–K3 test is
unchanged.

## The question

Presentations of the same line by betweenness knots have the same allowed states, yet under the knot-local fewest-states rule
KF3 (`STATE-RULES-20261117-001`, `KNOT-CAP-20261117-001`) they can grow different numbers of orders. For the line of five (the
one-order base on five distinctions, the inherited name) with its shared distinction at an end against in the middle, two orders
come at n = 7 with probability 5/12 against 11/18 (exact, refereed). The six-starts agree exactly through n = 9. What is it about
how the knots meet that the states do not carry, and that changes how many orders grow? The study asks for an invariant of the
knots' overlaps that predicts the distribution of the number of orders, a proof where one can be had, the untested placement
(next to an end), and whether the six-starts' agreement has the same cause.

## Words used here

To be entered in the glossary of `publication/knotlab/INTUITIONS.md` in this commit, chosen with the advisor (below).
- **Step of the line.** The consecutive pair (k − 1, k) of the line, k = 1 to n − 1, with the cut state that separates
  distinctions 0 to k − 1 from the rest; a knot B(a, c, b) of a presentation has c between a and b, and its **steps** are the
  line's steps from a to b.
- **Halves of a knot.** Its steps from a to c and from c to b.
- **Within; step-disjoint.** A knot lies **within** a half of another when all its steps are steps of that half; two knots are
  **step-disjoint** when they share no step, which in a presentation is the same as neither lying within the other (the advisor
  proposed "separate", which the glossary already uses in its everyday sense in the entry Hub).
- **Labelling.** Which distinction stands at which place of the line, read up to reversal (the line of five has 60).
- **The ends' knot.** The knot holding both ends, whose steps are all the line's.
- **Bracketing.** Which knot lies directly within which half of which, starting from the ends' knot (the literature's
  bracketing, or rooted binary tree; drawn as a triangulation of a polygon rooted at a marked side). The **bare bracketing**
  forgets which half: which knot lies directly within which (the literature's unlabelled rooted binary tree).
- **Same way, other way.** For knots χ within ν within π, χ lies in ν **the same way** when it sits in ν at the same end as ν
  sits in π, and **the other way** otherwise.
- **Odd set.** While no new distinction has added a state, every new distinction takes, in each state, the parity of an odd set of the
  line's distinctions; that set is its odd set. The fill of a triple a < c < b is the parity of a, c and b.

## In standard terms

Betweenness constraints on Boolean variables; the base read as a split system on the distinctions; the number of orders is the
lattice dimension (Eppstein 2005). Presentations of a path by betweenness triples; their structure as polygon triangulations and
binary trees (Catalan numbers); KF3 as a Markov chain on (allowed states, co-knotted pairs).

## Prior work in the program

`python3 -B scripts/track.py objects "how knots meet changes the number of orders grown from the same states knot-local fewest states" --until 2026-11-18 --exclude MEET-ORDERS-20261118-001`

`python3 -B scripts/track.py objects "lattice dimension of split systems grown by betweenness extensions polygon triangulations rooted binary trees" --until 2026-11-18 --exclude MEET-ORDERS-20261118-001`

`python3 -B scripts/track.py objects "presentations of a line of five or six distinctions by betweenness knots fan non-fan end middle" --until 2026-11-18 --exclude MEET-ORDERS-20261118-001`

- `STATE-RULES-20261117-001`: same object. KF3 itself, the C(n, 3) zero-cost fills of a line (S4, used here), and the six-starts'
  equal number of orders (narrowed by `KNOT-CAP`). This study explains when the knots change the number of orders.
- `KNOT-CAP-20261117-001`: same object and population (the five-starts and six-starts); the finding this study explains. Its
  referee counted the 300 labelled presentations of the line of five and named the untested placement.
- `KNOT-ORDER-20261117-001`: a relative: single knots that keep a line, and outward growth needing a hub. It does not study
  presentations or KF3.
- `DISTANCE-ORDER-20261117-001`: a relative: betweenness as the constraint "no state a = b ≠ c", and order read from
  disagreement counts on knot trees. Used for the definition only.
- `CUBE-DOUBLING-20261118-001`: a relative: the cheapest states-only growth reaches the cube at every doubling; no knot reading.
- `OVERLAP-READ-20261111-001`: unrelated (not-all-equal patterns read back faithfully).
- Also returned and unrelated: `OLD-CORE-20261112-001`, `TWO-ENDS-20261117-001`, `DISTANCE-DIM-20261117-001`,
  `FOLD-20261112-001`, `GROWTH-LAW-20261107-001`, `PINWHEEL-ROUND-20261107-001`, `HUB-SURVIVORS-20261029-001`.

## Prior work outside the program

- Triangulations of a convex polygon, bracketings and binary trees are counted by Catalan numbers (classical). Two searches found
  no statement that the fewest-knot betweenness presentations of a path are the triangulations; the advisor knows none.
- The nearest analogue is phylogenetics: minimal sets of rooted triples that define a binary tree (Steel; Grünewald, Steel and
  Swenson), to be checked before any novelty claim. Re-bracketing a knot with its parent is a rotation (Sleator, Tarjan and
  Thurston; the Tamari lattice).
- The second-step formula is specific to KF3 and, as far as the advisor and searches show, new.

## Exploration before this freeze (disclosed)

Run in the scratchpad with this study's engine, which reproduces every exact value of KNOT-CAP's referee:
- the three five-start placements to n = 10: next to an end equals the end exactly at n = 7 (5/12) and 8 (173/6552) and differs
  at n = 9 (163213/181890072 against 1810423/995045688); the middle differs from n = 7;
- every presentation of the line of six to n = 10 and of five to n = 9, grouped by bare bracketing (the basis of Q2 to Q4);
- Theorem 1's formula against exact counts on all 193 presentations with n0 = 5 to 8 (no mismatch);
- the per-first-knot split of the five-start chains and the labelled counts of the six-presentations (the basis of Q8).

## Ticket A: the proof (written before this freeze)

`proofs/MEET-ORDERS-20261118-001A/MEET-ORDERS-20261118-001A-P001_second_fill/proof.md`.
- **Lemma 0.** The fewest-knot presentations of a line of n are exactly its bracketings, n − 2 knots, Catalan(n − 2) per
  labelling (proved both ways).
- **Lemma A.** KF3's first new distinction fills one knot of the presentation, uniformly, one knot set each.
- **Lemma C.** On a line with fills of triples, two orders exactly when some fill exists and no fill's middle lies strictly
  between the ends of another fill without being its middle; otherwise three or more.
- **Lemma B.** After the first fill at κ, KF3's options are: the fill of each other knot (one knot set each), and for each knot
  ν sharing a pair with κ, two knot sets, the fills of the two triples that join the distinction of κ outside the shared pair
  with that of ν. Proof by a compression lemma and the finite check of ticket B (every presentation with at most 11
  distinctions).
- **Theorem 1.** P(two orders after the second new distinction) = (1/(n − 2)) Σ_κ [s(κ) + 2 p(κ) + c(κ)] / [(n − 3) +
  2 (p(κ) + c(κ))], with s(κ) the knots step-disjoint from κ, p(κ) = 1 when κ lies directly within a knot, and c(κ) the knots
  directly within κ. It depends only on the bare bracketing.

Settled by construction (stated, not tested): mirror images give identical distributions (renaming i ↦ n − 1 − i); KF3 reads the
knots only through which pairs share a knot.

## Ticket B: computations

Code: `melib.py`, `job.py`, `checks.py` and `merge.py` in
`experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/`, written fresh and checked against the exact
values of KNOT-CAP's referee (who shares no code with KNOT-CAP). 15 gate checks pass before this freeze.

Cases (`job.py`):
- **M1.** Lemma B's finite check: every bracketing with n0 = 4 to 11 (6,916), every first knot.
- **P5.** Lemma 0 by exhaustion: one knot per interior distinction, n0 = 5 to 9.
- **C.** Exact KF3 distributions of the number of orders from every presentation up to mirror: n0 = 5 to n0 + 5, n0 = 6, 7, 8
  and 9 to n0 + 4.
- **X.** Labelled runs: n0 = 5 and 6 to n0 + 4, n0 = 7 to n0 + 3; per level the labelled bases, the mass by largest odd set, and
  Lemma C's criterion against the measured number of orders.

## Predictions (frozen; advisor's probabilities from its first consultation)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | The 15 gate checks pass (engine against the referee's exact values, pruned against brute-force moves, the canonical form against networkx isomorphism, labelled against canonical runs, Catalan counts, the formula and two mutants) | any fails |
| Q1 | For every presentation with n0 = 4 to 11 and every first knot, the second step's options are exactly Lemma B's (counts, odd sets, verdicts) and the exact two-order chance equals Theorem 1 (advisor 93%) | one exception |
| Q2 | At n0 + 3 the distribution of the number of orders depends only on the bare bracketing, for every presentation with n0 = 7, 8 and 9 (advisor 85%) | two presentations with the same bare bracketing differ |
| Q3 | At n0 + 3 different bare bracketings give different distributions, n0 = 7, 8 and 9 (advisor 88%) | a tie |
| Q4 | At n0 + 4 every two presentations that are not mirror images give different distributions, n0 = 7 and 8 (advisor 75%; n0 = 9 reported with no prediction: the advisor expects ties once chains are long) | a tie |
| Q5 | The fewest-knot presentations are exactly the bracketings, n0 = 5 to 9 (advisor 98%; proved in A) | otherwise |
| Q6 | The chain (each knot directly within the next) is the unique bare bracketing with the least two-order chance after the second new distinction, n0 = 5 to 13 | otherwise |
| Q7 | Lemma C's criterion agrees with the measured number of orders on every labelled base whose new distinctions are all fills of triples | one disagreement |
| Q8 | The labelled base counts and the mass by largest odd set at every level depend only on which knots share a pair (the knots' pair-sharing tree, unrooted; the literature's dual tree), and different trees differ somewhere, for n0 = 6 to n0 + 4 and n0 = 7 to n0 + 3 | otherwise |

**What would count against the account.** Q1 failing would break the proof. Q2 failing would mean the order of the bracketing
enters at the third new distinction, so the six-starts' agreement through n = 9 would not follow from their bare bracketings
alone. Q8 failing would mean the rooting changes how many ways growth continues, not only which ways keep two orders.

**The headline, stated before running.** What the states do not carry is the bracketing: which knot lies within which half of
which, from the ends' knot. A fill makes a knot's halves cross; a second fill keeps two orders only when its knot is step-disjoint
from the first, or extends the first through the knot it lies within (two ways out of two) or through a knot within it (one of
two). End and next to an end are both chains; the middle is the ends' knot holding one knot in each half; hence 5/12 against 11/18.
The bare bracketing decides the number of orders through the third new distinction; same way against other way enters at the
fourth, which is where next to an end parts from the end (n = 9) and the two six-starts part (n = 10).

## Runs and stop rule

The shared runner (`scripts/longrun.py`), 634 cases, 12 workers, 2 GB per case (the heaviest measured case: 28 s and 124 MB),
expected under half an hour of wall time, registered as long run MEET-ORDERS-B1. Then `merge.py` and the read-out. The study
stops after the read-out, A97's status, the decision note, the referee hand-off and the report.

**Advisor.** Consulted twice before this freeze. The first consultation found a hole in the pull-back of the compression proof
(a knot set classified in a small presentation must use all three pairs of a knot of the big one; now checked), gave the
agreement-form proof of Lemma 0's converse, the parity form (odd sets), the two-order criterion (Lemma C), the probabilities
above, the restatement of Q4 as finite-size, the literature pointers, and the words. The second was asked about Q8 and the
third-step blindness (see the note).
