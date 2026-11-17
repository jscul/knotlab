# Dimension test: does a distance read from the allowed states give an order with nothing skipped, and two independent orders?

Epic `DISTANCE-DIM-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. It takes the first direction of
`DISTANCE-ORDER-20261117-001`. Goals G1 and G16; tests A97 and A98. Refereed: report [R1](referee-R1/report.md), confirmed with
fixes, no Block, folded in on 17 November (see Referee). Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `c04c4a400` at 19:23:49 UTC; the run went from 19:24:00 to 19:26:07
UTC. Proof: [proof.md](../../proofs/DISTANCE-DIM-20261117-001A/DISTANCE-DIM-20261117-001A-P001_order_dimension/proof.md). Code:
[dimlib.py and run.py](../../experiments/DISTANCE-DIM-20261117-001B/DISTANCE-DIM-20261117-001B-E001_dims/). Results:
[results.json](../../artifacts/DISTANCE-DIM-20261117-001B/DISTANCE-DIM-20261117-001B-E001_dims/results.json).

## The answer

*Rewritten after the referee and the owner's answer to B194 (17 November 2026, see Referee). The owner puts knots first: "The knots
are themselves the smallest form of spatial topology", and "3" exists "with relation to all other numbers, not just neighbors". So
the knot reading comes first below, and the implication reading is what knots would have to build.*

**On knots, no distance read from the allowed states gave an order, let alone two independent orders (computed).**
- **No exact betweenness.** On the not-all-equal thread, the weave and the chain grid, no distinction lies exactly between two
  others in the disagreement count, the number of allowed states in which two distinctions differ. The chain grid is a square
  meeting pattern with one knot and one private distinction on each pair; on it every assignment of the grid distinctions is
  allowed (proved).
- **Nearness gives a graph, not an order.** Read only as nearness, the result depends on the test. Under the relative-neighbourhood
  test (v is a neighbour of o when nothing is nearer to both), a start has 12 neighbours on the weave: its six knot-neighbours and
  six second neighbours of its own class. On the chain grid it has 8 at a grid distinction and 2 at a private one, 3 or 4 on the
  thread, and exactly the knots' own pairs on a binary knot tree. Under the six-nearest test the weave's six neighbours are the
  same-class second neighbours, and the graph splits the weave into its three classes. Under the unit-ball test the degree grows
  with L, so it is not local (the referee's computation).
- **The growth is the meeting pattern's own.** The local graphs' levels grow quadratically on the weave and the chain grid,
  linearly on the thread and exponentially on the tree. The distance faithfully reads how the knots meet in each sample. Nothing
  tested shows it adding or choosing a dimension.
- **Only away from the critical point do the counts give a ruler.** Along an axis, the chain grid's transfer gap tends to Onsager's
  1 − log₃ 2 = 0.3691 per step, so τ = −log₃ |1 − 2d/N| grows linearly with distance. The weave's gap falls like one over the width:
  0.199, 0.135, 0.102 at widths 6, 9, 12, with gap × width 1.19, 1.22, 1.23 approaching the conformal value π√3·x/ln 3 = 1.238 for
  spin dimension x = 1/4. The weave's criticality is known exactly (Stephenson; Blöte and Hilhorst; Nienhuis, Hilhorst and Blöte).
  So on the weave, τ grows only like a logarithm.

**What knots would have to build: an order of plain implications, which the states read back exactly (proved).** In a base of
two-place implications the allowed states are the up-sets of an order. These are the open sets of its Alexandrov topology: the
states are literally a topology, as the owner's "distance is topological" says. Reading the order back is that topology's
specialization order (Alexandrov 1937; Birkhoff's duality), and its dimension follows by Dushnik and Miller.
- **Read from the states.** A pair's states say whether it is ordered, since one joint pattern never occurs. That alone gives the
  comparability, and with it the order dimension: 1 on the chain of twelve, 2 on the grids 4 × 4, 6 × 6, 3 × 7 and a grid with a
  corner removed, 3 on 3 × 3 × 3, on S_3 with a bottom and a top, and on bare S_3.
- **The local part.** In the disagreement count, w lies between u and v exactly when w is in the order's interval from u to v, so
  the order has nothing skipped. This is a folklore-level addition. Through betweenness, bare S_3 reads nothing: it has no chain of
  three.
- **The order is the meeting pattern's own.** These orders are the patterns of implications they were built from, read back. The
  question John's answer raises is whether knots alone can build such an order among their distinctions.

| Base | Exact betweenness | Order from the states | Nearness neighbours (relative-neighbourhood test) | Levels from a start | Transfer gap |
| --- | --- | --- | --- | --- | --- |
| implication chain, 12 | the intervals | the order up to reversal, dimension 1 | 1–2 (in d) | — | — |
| implication grids 4 × 4, 6 × 6, 3 × 7; corner removed | the intervals | the order up to reversal, dimension 2 | 2–6 | — | — |
| implication 3 × 3 × 3; S_3 with bottom and top | the intervals | the order up to reversal, dimension 3 (realizer verified) | 3–12 | — | — |
| bare S_3 | none | nothing through betweenness; its pairs give the order and dimension 3 (referee) | 4 | — | — |
| NAE thread, n = 30 | none | none | 3–4 | 1, 4, 6, 6, 6, 6, 1 (linear) | — |
| NAE weave, L = 6, 9, 12 | none | none | 12 (six-nearest test: 6, splitting the three classes) | 1, 12, 30, 48, 53 at L = 12 (quadratic) | 0.199, 0.135, 0.102: to 0 (critical, known) |
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

- **On knots, the owner's reading is not borne out on these samples.** The disagreement count carries the information
  (`DISTANCE-ORDER-20261117-001`). Read here, it gives no order: no exact betweenness, and nearness graphs whose degree depends on
  the test. Their growth reads each meeting pattern's own (two-way, one-way, branching). Only off the critical point does it give a
  linear ruler along an axis, and the weave is critical. *Scoped after the referee: the first version said the states read "two
  independent orders" under implications and "a two-dimensional growth" under knots without saying that both are the meeting
  pattern's own.*
- **Under implications the states are a topology, and its specialization order is read back exactly** (classical). Under the
  owner's answer, that is what knots would have to build, not the premise's positive case.
- **A97** stays under challenge, with these two facts.
- **A98.** Its challenge "order by levels from a start" has been run. Under the relative-neighbourhood test the levels have bounded
  degree, but other nearness tests give other graphs, and none gives an order.

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

- The implication orders and the knot patterns are given samples; the states read each one's own order or growth, and nothing tested
  adds or chooses a dimension.
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

## Referee

Report [R1](referee-R1/report.md), 17 November 2026, by a background referee thread with fresh code and no Codex: confirmed with
fixes, no Block. D1 to D5 are correct, D3 included. The implication bases recompute exactly. The K3 tie explanation is confirmed:
mirror entries differ by 1.7 to 2.8 × 10⁻¹⁶, and with exactly symmetric correlations the frozen levels hold at L = 8, 10, 12. The
chain grid's float transfer is fine. Folded in the same day, with the owner's answer to B194 (knots first), each item logged in
`docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing.** The summaries said the states read "two independent orders" (implications) and "a two-dimensional growth"
   (knots) without saying that each is the meeting pattern's own. The implication half is the classical round trip: Alexandrov's
   specialization order and Birkhoff's duality, with D1 a folklore-level addition. The knot half reads each pattern's own growth.
   The answer, the meaning for A97, the notebook, A97, the goals line and checkpoint, and the objects rows say so. The answer now
   leads with knots, per the owner.
2. **Narrowing.** Degree 12 belongs to the relative-neighbourhood test. The six-nearest test gives the six same-class second
   neighbours and splits the weave into its three classes, and the unit-ball test's degree grows with L (17, 32, 36). No
   order-only reading gives an order.
3. **Not a block.** The weave's criticality is known exactly (Stephenson; Blöte and Hilhorst; Nienhuis, Hilhorst and Blöte), and
   the measured gap × width approaches the conformal 1.238 (x = 1/4). It is cited now instead of resting on three widths.
4. **Not a block.** Bare S_3: "nothing" holds only for the betweenness route. Its pairs give the order and dimension 3, since D2
   reads comparability with no hypothesis, and dimension depends only on comparability.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: order and dimension read from the states | **Status:** Successful (refereed, confirmed with fixes) | On knots, no order: no exact betweenness, and nearness graphs that depend on the test and grow as each meeting pattern does; only off criticality a ruler, and the weave is critical. Under implications the states are a topology whose specialization order and dimension are read back (classical; D1 folklore level). 12 of 13 held |
| Local direction: a distance that is information, order and dimension | Promising | Knots first (the owner's answer): can knots alone build an order among their distinctions, as implications have one |
| Broader exploration: dimension from logic | Known alternatives | Order dimension, growth dimension and correlation length are classical; reading them from a base's states is the local step |
| Long-term goal: G1 and G16 | G16 capability gained; G1 no demonstrated advance | G16: the states give back an implication pattern's order. G1: on knots the distance reads each meeting pattern's own growth and adds no order |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which three-place knot laws on the weave are off their critical point, so that their counts give a ruler on the program's own space? | 2/3, a state-read ruler on the weave | 3/3: the transfer gaps of the five knot classes at widths 6, 9, 12 | Freeze per-class predictions → stop at the list of critical and off-critical laws | Taken by `WEAVE-LAWS-20261117-001` (coordinator's go-ahead) |
| 2 | Mixed bases: implications and knots together. Does an order survive a knot, and what does the order dimension read then? | 2/3 | 2/3 | Census of small mixed bases with the betweenness route → stop at the first rule | Alternative |
| 3 | Can knots alone build an order among their distinctions, as implications have one (sharpened by the owner's answer: knots first)? For example through distinctions that knots force or settle | 3/3 | 1/3 | Look for knot patterns whose forced or settled distinctions carry exact betweenness → stop at a pattern or an obstruction | Alternative |

**Corrections:** none at the close; after the referee, two Narrowings and two Not a block entries, logged.

**Goals:** a G1 and G16 checkpoint (G16 capability gained, G1 no demonstrated advance; corrected after the referee from capability gained for both); no goal changed.

**Assumptions:** A97 stays Under challenge, now with an exact positive case under implications. A98's challenge "levels from a
start" has been run; no new entry.

**Basket:** read; B194 (the owner's question) and B195 (outlines) are related and were left to their own owners.
