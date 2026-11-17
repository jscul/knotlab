# Dimension test: does a distance read from the allowed states give an order with nothing skipped, and two independent orders? Pre-registration

Epic `DISTANCE-DIM-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. It takes `DISTANCE-ORDER-20261117-001`'s
first direction. Goals G1 and G16; tests A97 and A98. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

The owner asked whether the new direction reopens the program's earlier work on dimensions ("dimensions like x and y with rules").
The coordinator's brief: on patterns with cycles, is there a distance read from the allowed states alone from which an order with
no skipping comes out, and then two independent orders? The owner's words: "Distance is topological, so it will have some
starting point, then go off outward from there ... there isn't really any such thing as "direction". Everything is just
"relative", but it's also topological, so if you're at 3 on the number line, you can't just skip 4 to get to 5, so there is an
order."

Whether his 3, 4, 5 is a chain of plain implications (an order before any knot) or a chain of knots is open (B194, a question for
the owner). The test is built to read under either answer.

**What the earlier dimension work read.** It read bond distance, an ordering distance: steps apart plus one on the weave, with
balls growing like r²; t − s + 1 on the knot thread; taxicab-like on Tseitin and gauge grids (`RULER-20261111-001`,
`RULER-FLAT-20261111-001`, `LOGIC-AXIS-20261107-001`; proved). Its barrier is that the grid is drawn: no law chose its own
dimension. Today's tests show that the information is carried by the disagreement count (`DISTANCE-ORDER-20261117-001`). This
test asks what that count, read from the states, gives as order and dimension.

## Ticket A: the proof (written before this freeze)

`proofs/DISTANCE-DIM-20261117-001A/DISTANCE-DIM-20261117-001A-P001_order_dimension/proof.md`, checked by its `check.py`.
- **D1.** On a base that allows exactly the up-sets of a finite poset, w lies between u and v in the disagreement count iff w is in
  their interval.
- **D2.** Two distinctions are comparable iff one joint pattern of their values never occurs. Under not-all-equal with no tie, all
  four occur for every pair.
- **D3.** Suppose every comparable pair lies in a chain of three. Then the betweenness triples give the comparability graph. If the
  poset is also connected, they give the order up to reversal. So the order dimension (Dushnik–Miller), which is the same for an
  order and its reverse, is read from the states.
- **D4.** On the not-all-equal chain grid, every assignment of the grid distinctions extends to an allowed state. So no three of
  them are in exact betweenness.
- **D5.** The chain grid is the Ising model with tanh K = −1/3, above its critical point. Its transfer gap along an axis is
  ln(3/2), that is 1 − log₃ 2 ≈ 0.3691 in log base 3 (Onsager).

## Ticket B: definitions

- **Disagreement count** d(u, v), the number of allowed states in which u and v differ; N, the number of allowed states;
  τ = −log₃ |1 − 2d/N|.
- **Strict betweenness.** w lies between u and v when d(u, v) = d(u, w) + d(w, v), with both parts positive. For the chain grid's
  floating counts, this holds within 10⁻⁹.
- **Pair patterns.** For each pair, which of 00, 01, 10 and 11 occur.
- **Comparability from betweenness.** The pairs that occur together in a strict betweenness triple.
- **Order dimension.** "At most two" means the incomparability graph is a comparability graph (Dushnik–Miller), tested by
  Golumbic's implication classes. "Three" means that test fails and an explicit realizer of three linear extensions is verified:
  the coordinate orders on the three-way grid, or a search among the linear extensions of the eight-element crown.
- **The order-only reading** (A98's untried "levels from a starting point"):
  - v is a gap neighbour of o when no w has τ(o, w) < τ(o, v) and τ(w, v) < τ(o, v), with strict inequalities (the literature's
    relative neighbourhood graph, Toussaint 1980);
  - the levels from a start are the breadth-first layers of the gap graph.
  - By definition nothing is skipped along gap edges, and the gap graph is connected, so that part cannot fail. What can fail is
    the gap degree (does it stay bounded) and the level sizes (how do they grow).
- **Transfer gap per row.** log₃(λ₀/|λ₁|), with λ₁ the largest modulus below the top one. The top modulus's multiplicity is reported.

Two different invariants appear. On the implication side "2" is an order dimension: two linear orders whose intersection is the
order. On the knot side, "quadratic" is a growth exponent of the gap graph's balls. A growth exponent is not an order dimension.

## Bases

| Side | Base | Size | Method |
| --- | --- | --- | --- |
| implication | chain | 12 elements | exact, up-sets |
| implication | grids | 4 × 4, 6 × 6, 3 × 7 | exact |
| implication | grid with a corner removed (a non-grid order of dimension 2) | 5 × 5 less 2 × 2 | exact |
| implication | three-way grid | 3 × 3 × 3 (980 states, MacMahon) | exact |
| implication | the standard example S_3 with a bottom and a top (dimension 3) | 8 elements | exact |
| implication | bare S_3 (height two: the route reads nothing) | 6 elements | exact |
| knot | not-all-equal thread | n = 30 | exact |
| knot | the six-regular weave W(L) | L = 6, 9, 12 | exact (frontier programme; transfer matrices modulo primes) |
| knot | the not-all-equal chain grid: a square grid on a torus, each edge one knot with a private distinction | L = 8, 10, 12 | row transfer, floating (agrees with exact counts to 2 × 10⁻¹⁶ at L = 3 and 6) |
| knot | control: a binary tree of knots, depth 4 | 31 distinctions | exact |

## Predictions (frozen; checked with the advisor)

| # | Prediction | Fails when |
| --- | --- | --- |
| I1 | On all eight implication bases, the strict betweenness triples are exactly the interval triples (D1) | any differs (a bug) |
| I2 | On all eight, the pairs with a missing joint pattern are exactly the comparable pairs (D2) | any differs |
| I3 | Comparability from betweenness is exact on the seven bases with chains of three; bare S_3 has no betweenness triple | otherwise |
| I4 | The order is rebuilt up to reversal from betweenness on the seven, and not on bare S_3 | otherwise |
| I5 | Dimension read from the states: at most two on the chain and the four two-way orders (the chain's comparability graph is complete, so its dimension is 1); three on the three-way grid and on S_3 with bottom and top, the two-test failing and a realizer of three verified | otherwise |
| K1 | On the thread, the weave (L = 6, 9, 12) and the chain grid (L = 8, 10, 12), every pair of distinctions shows all four joint patterns | some pair misses one |
| K2 | No strict betweenness among the thread's distinctions, nor through the chain grid's three kinds of start (grid, horizontal private, vertical private) | any triple |
| K3 | Chain grid: a grid start has 8 gap neighbours (its 4 grid neighbours and its 4 private distinctions), a private start has 2 (its ends), no other degree occurs; the levels from a grid start are those of that graph on the torus: L = 8: 1, 8, 20, 32, 42, 40, 28, 16, 5; L = 10: 1, 8, 20, 32, 44, 54, 52, 40, 28, …; L = 12: 1, 8, 20, 32, 44, 56, 66, 64, 52, … (on the endless grid 12k − 4, balls quadratic) | any degree or level differs |
| K4 | Weave: the levels from a start are those of the twelve-neighbour graph (six knot-neighbours, six second neighbours of the start's class) on the torus: L = 6: 1, 12, 23; L = 9: 1, 12, 30, 38; L = 12: 1, 12, 30, 48, 53 (endless: 18k − 6 from k = 2, balls quadratic). The twelve neighbours are the referee's finding at these sizes, so only the levels are new | any level differs |
| K5 | Thread: every gap degree is at most 6, and the level sizes from the middle stay at most 6 (balls linear) | otherwise |
| K6 | Knot tree: the gap graph is the co-knot graph, and the levels from the root are 1, 2, 4, 8, 16 (exponential) | otherwise |
| K7 | Transfer gap of the chain grid at widths 8, 10, 12 lies within 0.01 of 0.3691 at width 12, with its distance from 0.3691 shrinking as the width grows | otherwise |
| K8 | Transfer gap of the weave falls with width (6, 9, 12), and gap(12)/gap(6) is below 0.7, as at a critical point | otherwise |

**Exploratory, no prediction:**
- the gap degrees of the implication bases in d and in τ (a common yardstick across both answers);
- the thread's exact gap degrees and levels.

**What each outcome would mean, stated before running.**
- **I1 to I5 hold.** Under the implication answer, an order with nothing skipped and its number of independent orders are read
  exactly from the states, through the disagreement count's betweenness: 1 on a chain, 2 on a grid, 3 on a three-way grid. The
  grid is still drawn (the barrier stands), and the dimension is an order dimension.
- **K1 and K2 hold.** Under the knot answer, exact betweenness reads no order at all on the thread, the weave and the chain grid.
- **K3, K4 and K6 hold.** The order-only reading gives bounded-degree local graphs. Their balls grow quadratically on the weave
  and the chain grid, and exponentially on the tree control. That is a growth dimension, read from the states, of a local order
  that is not exactly the pattern's own (the weave adds six second neighbours, and the chain grid joins each grid distinction to
  its private ones).
- **K7 and K8 hold.** The states' pair counts give a linear ruler along an axis on the chain grid (off-critical) and only a
  logarithmic one on the weave (critical). That is a second sense in which the two knot bases differ.
- **Any of I1–I4 fails.** That is a bug, since D1 to D3 are proved. **K3 or K4 fails.** The gap graph is not the predicted one,
  and the failing level says where.

## Prior work in the program

`python3 -B scripts/track.py objects "order dimension betweenness implications up-sets poset" --until 2026-11-17 --exclude DISTANCE-DIM-20261117-001`

`python3 -B scripts/track.py objects "dimension read from allowed states ball growth" --until 2026-11-17 --exclude DISTANCE-DIM-20261117-001`

- `DISTANCE-ORDER-20261117-001` and its referee: the predecessor (betweenness is a three-place constraint; the order-only reading
  on the weave; A98).
- `LOGIC-AXIS-20261107-001`, `RULER-20261111-001`, `RULER-FLAT-20261111-001`: dimension read through bond distance on drawn grids
  and weaves.
- `DISTANCE-INFO-20261117-001`: bond distance and steps apart do not carry the base.
- `BOND-BALLS-20261111-001`: a relative (bond balls on faithfully read infinite two-shift bases: growth read through bond distance,
  where this test reads it through the disagreement count's gap graph).
- `OVERLAP-READ-20261111-001`: a relative (the law reads pair counts of knots; faithful reading of overlapping bases).
- `ONE-RELAY-PADDING-20261115-001`: unrelated (guard supports from shared implication pads; matched on "implication").

## Prior work outside the program

- **Order dimension:** Dushnik and Miller 1941; Komm 1948; Gallai 1967; Trotter, Moore and Sumner 1976; Trotter's book; Yannakakis
  1982 for NP-completeness.
- **Comparability graphs:** Golumbic 1977 and his book.
- **Up-sets and distributive lattices:** Birkhoff. Plane partitions: MacMahon.
- **Betweenness:** for metrics, Menger; in lattices and orders, Glivenko 1936, Pitcher and Smiley 1942, Altwegg 1950 and Sholander
  1952, from the advisor's memory and to be checked.
- **The relative neighbourhood graph:** Toussaint 1980.
- **Ising correlation length above the critical point:** Onsager 1944.
- **The zero-temperature triangular antiferromagnet:** Wannier 1950; Stephenson 1964 and 1970.

## Runs and stop rule

One script, `run.py`, one process, expected under twenty minutes. The study stops after its read-out, followed by A97 and A98
status, the decision note, the referee hand-off and the report.

The advisor model (`claude -p --model claude-fable-5-2`) was consulted twice before this freeze. It:
- confirmed D1 and its corollaries, and gave the up-to-reversal argument and the hypothesis it needs;
- showed that S_3 alone reads nothing, and supplied the replacement controls;
- showed that the knot side's exact betweenness is decided by proof (full support), and that "nothing skipped" in the gap graph
  cannot fail;
- gave the chain grid's level sequence 12k − 4 and the exact Onsager slope;
- warned that rectangles and short tori cannot show a slope, so the transfer gap is used instead;
- proposed the pair-pattern test and the tree control.
