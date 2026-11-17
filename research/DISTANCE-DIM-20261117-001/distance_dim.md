# Dimension test: does a distance read from the allowed states give an order with nothing skipped, and two independent orders?

Epic `DISTANCE-DIM-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. It takes the first direction of
`DISTANCE-ORDER-20261117-001`. Goals G1 and G16; tests A97 and A98. Referee pending. Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `c04c4a400` at 19:23:49 UTC; the run went from 19:24:00 to 19:26:07
UTC. Proof: [proof.md](../../proofs/DISTANCE-DIM-20261117-001A/DISTANCE-DIM-20261117-001A-P001_order_dimension/proof.md). Code:
[dimlib.py and run.py](../../experiments/DISTANCE-DIM-20261117-001B/DISTANCE-DIM-20261117-001B-E001_dims/). Results:
[results.json](../../artifacts/DISTANCE-DIM-20261117-001B/DISTANCE-DIM-20261117-001B-E001_dims/results.json).

## The answer

**It depends on what 3, 4, 5 are made of (B194).**

**If they are plain implications, yes: the order and its number of independent orders come out of the allowed states exactly
(proved).** In a base of two-place implications, w lies between u and v in the disagreement count exactly when w is in the
order's interval from u to v. The disagreement count is the number of allowed states in which two distinctions differ. So the
states give back the order up to reversal, with no direction used, and with it the order dimension, the number of linear orders
whose intersection it is. The run read these from the states:
- 1 on the chain of twelve;
- 2 on the grids 4 × 4, 6 × 6 and 3 × 7 and on a grid with a corner removed;
- 3 on the three-way grid 3 × 3 × 3 and on the standard example S_3 with a bottom and a top.

A pair's states alone already say whether it is ordered, since one joint pattern never occurs. The route needs chains of three:
on S_3 with nothing above or below, nothing lies between anything, and it reads nothing. The grid is still drawn. The states read
its dimension; they do not choose it.

**If they are knots, exact betweenness gives no order at all, but a nearness order gives levels that grow in two dimensions
(computed).** On the not-all-equal thread, the weave and the chain grid, no distinction lies exactly between two others. The chain
grid is a square grid with one knot and one private distinction on each edge. On it, every assignment of the grid distinctions is
allowed (proved). Read only as nearness, v is a gap neighbour of o when nothing is nearer to both. On that reading the gap graph
has bounded degree:
- 12 on the weave (the six knot-neighbours and six second neighbours of the start's own class);
- 8 at a grid distinction of the chain grid (4 grid neighbours and its 4 private distinctions), and 2 at a private one;
- 3 or 4 on the thread;
- on a binary tree of knots, exactly the knots' own pairs.

Its levels from a start grow:
- quadratically on the weave and the chain grid (balls in two dimensions);
- linearly on the thread;
- exponentially on the tree.

That is a growth dimension, which is a different invariant from an order dimension.

**The two knot bases differ in a second way.** Along an axis, the chain grid's transfer gap tends to Onsager's exact value
1 − log₃ 2 = 0.3691 per step. So its pair counts decay at a fixed rate per step, and τ = −log₃ |1 − 2d/N| grows linearly with
distance. The weave's gap falls like one over the width (0.199, 0.135, 0.102 at widths 6, 9 and 12; gap × width 1.19, 1.22, 1.23),
as at a critical point. There τ grows only logarithmically. The chain grid's counts carry a linear distance along an axis. The
weave's, the program's own space, do not.

| Base | Exact betweenness | Order from the states | Gap degree (order-only) | Levels from a start | Transfer gap |
| --- | --- | --- | --- | --- | --- |
| implication chain, 12 | the intervals | the order up to reversal, dimension 1 | 1–2 (in d) | — | — |
| implication grids 4 × 4, 6 × 6, 3 × 7; corner removed | the intervals | the order up to reversal, dimension 2 | 2–6 | — | — |
| implication 3 × 3 × 3; S_3 with bottom and top | the intervals | the order up to reversal, dimension 3 (realizer verified) | 3–12 | — | — |
| bare S_3 | none | nothing | 4 | — | — |
| NAE thread, n = 30 | none | none | 3–4 | 1, 4, 6, 6, 6, 6, 1 (linear) | — |
| NAE weave, L = 6, 9, 12 | none | none | 12 | 1, 12, 30, 48, 53 at L = 12 (quadratic) | 0.199, 0.135, 0.102: to 0 (critical) |
| NAE chain grid, L = 8, 10, 12 | none | none | 8 and 2 (post hoc at 10, 12; see K3) | 1, 8, 20, 32, 44, … (quadratic) | 0.3764, 0.3719, 0.3702: to 0.3691 |
| knot tree, depth 4 | — | — | the knots' own pairs | 1, 2, 4, 8, 16 (exponential) | — |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| I1 | betweenness = intervals on all eight implication bases | held | 8 of 8 |
| I2 | a missing joint pattern = comparable, on all eight | held | 8 of 8 |
| I3 | comparability from betweenness exact on seven; none on bare S_3 | held | as predicted |
| I4 | order rebuilt up to reversal on seven, not on bare S_3 | held | as predicted |
| I5 | dimension ≤ 2 on the chain and four two-way orders; 3 on 3 × 3 × 3 and S_3 with bottom and top | held | coordinate realizer and one found among 48 linear extensions, both verified |
| K1 | all four joint patterns on every pair: thread, weave, chain grid | held where computed | thread and chain grid in the run; the weave was not computed by the frozen code (an omission), and post hoc its exact rates lie in (0.24, 0.67), so it holds |
| K2 | no strict betweenness on the thread and through the chain grid's starts | held | 0 and 0 |
| K3 | chain grid gap degrees 8 and 2, levels as listed | **failed** at L = 10 and 12 | held at L = 8; at 10 and 12 the run gave 6 and 1, see below |
| K4 | weave levels 1, 12, 23 / 1, 12, 30, 38 / 1, 12, 30, 48, 53 | held | exactly |
| K5 | thread gap degrees and level sizes at most 6 | held | degrees 3, 4; levels 1, 4, 6, 6, 6, 6, 1 |
| K6 | tree: gap graph = co-knot graph; levels 1, 2, 4, 8, 16 | held | exactly |
| K7 | chain-grid gap within 0.01 of 0.3691 at width 12, deviation shrinking | held | 0.3764, 0.3719, 0.3702 |
| K8 | weave gap falls with width; gap(12)/gap(6) < 0.7 | held | 0.514 |

12 of 13 held; K3 failed at two of its three sizes.

**Why K3 failed (post hoc).** A private distinction p on the edge (u, v) is equally near u and v: c(u, p) = c(v, p) exactly, by
symmetry. The gap test is strict, so v does not block u from p. In the run, the two counts were computed from mirror-image entries
of a floating transfer matrix. At L = 10 and 12 they differed in the last bits, so v blocked u from two of its four private
distinctions. That gave degree 6 at a grid start and 1 at a private one, and the levels changed to match. Averaging the counts
over the torus's symmetries makes the ties exact again. The rerun then gives degrees 8 and 2 and exactly the predicted levels at
all three sizes ([posthoc.py](../../experiments/DISTANCE-DIM-20261117-001B/DISTANCE-DIM-20261117-001B-E001_dims/posthoc.py),
[output](../../artifacts/DISTANCE-DIM-20261117-001B/DISTANCE-DIM-20261117-001B-E001_dims/posthoc_symmetric_ties.json)). The frozen
verdict stays failed. The lesson is that an order-only reading meets exact ties, and the advisor flagged this before the freeze.
The fix is exact arithmetic or symmetrised counts, not a tolerance.

## What it means for A97 and A98

- **Under the implication answer to B194, the owner's reading holds exactly on these bases.** One distance read from the allowed
  states, the disagreement count, has an order with nothing skipped: its betweenness is the order's intervals. That order has its
  number of independent orders: 1 on a line, 2 on a grid, 3 on a three-way grid. It is relative and needs no direction.
  - *What it does not cover.* The count is additive along each chain, but its steps are not equal (on 3 × 3, consecutive covers
    count 3 and 6), so it is an order, not a ruler.
  - *Where the grid comes from.* The grid is drawn, so the barrier of `LOGIC-AXIS-20261107-001` stands.
- **Under the knot answer, the order is the nearness order's, and the space is a growth dimension.**
  - The count has no exact betweenness on the thread, the weave and the chain grid.
  - Its nearness order has bounded degree and levels that grow in two dimensions on the weave and the chain grid.
  - Only off the critical point (the chain grid) do the counts also give a linear distance along an axis. On the weave they do not.
- **A97 stays under challenge.** It now has an exact positive case: plain implications, in any number of dimensions drawn. On
  knots it has a nearness-order reading.
- **A98.** Its challenge "order by levels from a start" has been run. Under knots, the levels give bounded degree and two-dimensional
  growth on the weave and the chain grid.

## What the knot picture explained

The owner's "you can't just skip 4 to get to 5" is a statement about three things: 4 lies between 3 and 5. In the disagreement
count, that is a three-place constraint (`DISTANCE-ORDER-20261117-001`).
- **Built from two-place implications,** these constraints are exactly an order's intervals. The states then hold the order and
  its dimension, Dushnik and Miller's.
- **Built from knots,** no three distinctions of the thread, the weave or the chain grid stand in that relation. A knot hides its
  order. What remains is nearness, and nearness gives levels and a growth dimension, as the earlier dimension work found through
  bond distance.

The new point is the weave's criticality. Its states' pair counts fall off slowly enough that they set no scale along an axis. A
knot pattern off its critical point, such as the chain grid, has a scale, and there the counts are a ruler.

Known mathematics, labelled:
- order dimension (Dushnik and Miller; Komm; Gallai; Trotter, Moore and Sumner);
- comparability graphs (Golumbic);
- up-sets and distributive lattices (Birkhoff);
- plane partitions (MacMahon);
- betweenness for symmetric-difference metrics (Glivenko; Pitcher and Smiley);
- the relative neighbourhood graph (Toussaint);
- the Ising correlation length (Onsager);
- the triangular antiferromagnet (Wannier; Stephenson).

The local parts are D1 in this form, the up-to-reversal reading from states, and the measurements on the program's bases.

## Limitations

- The implication grids are drawn, so the states read a dimension and do not choose one.
- The knot bases are read at L ≤ 12. The weave's levels are exact on the tori but reach only five levels. The criticality is read
  from three widths: gap × width is nearly constant, which is the critical signature, not a proof.
- The order-only reading uses τ and a strict gap test. Exact ties need exact arithmetic (K3).
- No outline or roundness was measured (B195, queued separately).
- Pairwise readings only. On parity bases the pairs are blank (`DISTANCE-ORDER-20261117-001A`, statement 4), so they need readings
  beyond pairs, as the earlier bond-distance work used.

## Reproduce

```sh
.venv/bin/python -B proofs/DISTANCE-DIM-20261117-001A/DISTANCE-DIM-20261117-001A-P001_order_dimension/check.py
.venv/bin/python -B experiments/DISTANCE-DIM-20261117-001B/DISTANCE-DIM-20261117-001B-E001_dims/run.py
```

## Advisor

The advisor was consulted twice before the freeze. The first consultation:
- showed that the betweenness route on knots restates the faithful reading;
- predicted that the rates follow straight-line distance along rays, which is B195's question, queued separately;
- warned against rectangles.

The second consultation:
- confirmed D1 and gave the up-to-reversal argument with its hypothesis;
- replaced the S_3 control;
- proved the chain grid's full support;
- said "nothing skipped" cannot fail in the gap graph;
- gave the levels 12k − 4 and Onsager's slope;
- proposed the pair-pattern test and the tree control;
- warned about exact ties, which is what failed K3.

It was not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: order and dimension read from the states | **Status:** Successful (referee pending) | Under implications, the order and its dimension (1, 2, 3) are read exactly from the states (proved, checked). Under knots, no exact order; nearness levels grow in two dimensions on the weave and chain grid. The weave is critical, the chain grid is not. 12 of 13 held |
| Local direction: a distance that is information, order and dimension | Promising | Exact under implications; under knots it splits into nearness levels and, off criticality, a ruler |
| Broader exploration: dimension from logic | Known alternatives | Order dimension, growth dimension and correlation length are classical; reading them from a base's states is the local step |
| Long-term goal: G1 and G16 | G16 capability gained; G1 capability gained | The states give back an order up to reversal and its dimension; the barrier (dimension is drawn) stands |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which three-place knot laws on the weave are off their critical point, so that their counts give a ruler on the program's own space? | 2/3, a state-read ruler on the weave | 3/3: the transfer gaps of the five knot classes at widths 6, 9, 12 | Freeze per-class predictions → stop at the list of critical and off-critical laws | Alternative |
| 2 | Mixed bases: implications and knots together. Does an order survive a knot, and what does the order dimension read then? | 2/3 | 2/3 | Census of small mixed bases with the betweenness route → stop at the first rule | Alternative |
| 3 | Can a law choose its order dimension (the barrier), for example implications grown at open ends? | 3/3 | 1/3 | Look for a growth rule whose up-sets give dimension 2 without a drawn grid → stop at a rule or an obstruction | Alternative |

**Corrections:** none.

**Goals:** a G1 and G16 checkpoint (capability gained for both); no goal changed.

**Assumptions:** A97 stays Under challenge, now with an exact positive case under implications. A98's challenge "levels from a
start" has been run; no new entry.

**Basket:** read; B194 (the owner's question) and B195 (outlines) are related and were left to their own owners.
